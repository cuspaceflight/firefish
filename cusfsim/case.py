"""
This module allows the building and manipulating OpenFOAM case directories.

OpenFOAM files are mapped into Python objects using the following conventions:

  * Dictionaries map to python :py:class:`dict`.
  * Keyword data entries map to :py:class:`tuple` when the number of data
    entries is greater than one. Otherwise the single data entry is the
    keyword's value.
  * Lists are mapped to Python :py:class:`list`.
  * Dimension are represented via the :py:class:`~.Dimension` type.

"""
import contextlib
import enum
import os

import PyFoam.Basics.DataStructures as PFDataStructs
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.ParsedParameterFile import (
    ParsedParameterFile, WriteParameterFile
)

## EXCEPTIONS

class CaseException(Exception):
    """Base class for exceptions raised by cusfsim.case module."""

class CaseDoesNotExist(CaseException):
    """A case directory did not exist when we expected it to."""

class CaseToolRunFailed(CaseException):
    """There was a failure running a tool on a case directory."""

## ENUMERATIONS

def _sys_path(p):
    return os.path.join('system', p)

def _constant_path(p):
    return os.path.join('constant', p)

class FileName(enum.Enum):
    """An enumeration of well known OpenFOAM file locations."""

    #: controlDict
    CONTROL                     = _sys_path('controlDict')

    #: blockMeshDict
    BLOCK_MESH                  = _sys_path('blockMeshDict')

    #: fvSolution
    FV_SOLUTION                 = _sys_path('fvSolution')

    #: fvSchemes
    FV_SCHEMES                  = _sys_path('fvSchemes')

    #: transportProperties
    TRANSPORT_PROPERTIES        = _constant_path('transportProperties')
    
    #: thermoPhysicalProperties
    THERMOPHYSICAL_PROPERTIES   = _constant_path('thermophysicalProperties')
    
    #: turbulence Properties
    TURBULENCE_PROPERTIES       = _constant_path('turbulenceProperties')

class Dimension(PFDataStructs.Dimension):
    """Represents a value's dimensions in OpenFOAM cases.

    >>> d = Dimension(0, 1, -2, 0, 0, 0, 0)
    >>> str(d) # PyFOAM data file representation
    '[ 0 1 -2 0 0 0 0 ]'
    >>> d.unit
    'ms^-2'
    >>> repr(d)
    'cusfsim.case.Dimension(0, 1, -2, 0, 0, 0, 0)'

    It supports indexing and the sequence property

    >>> d[2]
    -2
    >>> [v+1 for v in d]
    [1, 2, -1, 1, 1, 1, 1]
    >>> d[0] = 2
    >>> d.unit
    'kg^2ms^-2'

    """

    _SI_UNIT_NAMES = ['kg', 'm', 's', 'K', 'mol', 'A', 'cd']

    @property
    def unit(self):
        combined = []
        for unit, value in zip(Dimension._SI_UNIT_NAMES, self):
            if value == 0:
                continue
            combined.append(unit)
            if value != 1:
                combined.append('^{}'.format(value))
        return ''.join(combined)

    def __repr__(self):
        return ''.join([
            str(self.__class__.__module__), '.',
            str(self.__class__.__name__), '(',
            ', '.join([str(v) for v in self]), ')'
        ])

# Monkey-patch PyFOAM to ensure our Dimension type is returned from parsing
# functions. This is not terribly elegant to say the least and isn't documented
# but cusfsim tries very hard to hide PyFOAM's API from the user.
def _monkey_patch_pyfoam():
    from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator
    from PyFoam.RunDictionary import ParsedParameterFile
    PFDataStructs.Dimension = Dimension
    FoamFileGenerator.Dimension = Dimension
    FoamFileGenerator.primitiveTypes.extend([Dimension])
    ParsedParameterFile.Dimension = Dimension
_monkey_patch_pyfoam()

class FileClass(enum.Enum):
    """Well known OpenFOAM dictionary classes."""

    #: A parameter dictionary
    DICTIONARY = "dictionary"

    #: A 3D scalar field
    SCALAR_FIELD_3D = "volScalarField"

    #: A 3D vector field
    VECTOR_FIELD_3D = "volVectorField"

## PUBLIC CLASSES AND FUNCTIONS

def read_data_file(path):
    """Read and parse an OpenFOAM dict into a Python dictionary.

    Args:
        path (str): path to the OpenFOAM dict on disk

    Returns:
        A dict representing a Python transliteration of the dict.

    Raises:
        IOError: the path could not be read from
    """
    return ParsedParameterFile(path).content


class Case(object):
    """Object representing an OpenFOAM case on disk.

    Attributes:
        root_dir_path: path to case directory
    """

    def __init__(self, root_dir_path, create=True):
        """Initialises an OpenFOAM case from an on-disk path.

        The case directory may optionally be created if it does not exist. If
        create is False, a CaseDoesNotExist exception will be raised.

        Args:
            root_dir_path (str): Path to the OpenFOAM case.
            create (bool): Create the case if it doesn't exist.

        """
        # ensure directory exists if asked
        if create:
            os.makedirs(root_dir_path)

        # check directory exists
        if not os.path.isdir(root_dir_path):
            raise CaseDoesNotExist(
                'Is not a directory: {}'.format(root_dir_path)
            )

        # set attributes
        self.root_dir_path = root_dir_path

    def mutable_data_file(self, path,
                     create_class=FileClass.DICTIONARY, create=True):
        """A context manager representing a dict. Changes to the dict are
        written back to disk.

        Args:
            path (str or FileName): relative path to dictionary
            create_class (str or FileClass): specify the class of created files
            create (bool): create file if it does not exist

        >>> case = getfixture('tmpcase')
        >>> with case.mutable_data_file('system/blockMeshDict') as d:
        ...     d['boundary'] = { 'foo': { 'type': 'empty' } }
        >>> case.read_data_file('system/blockMeshDict')['boundary']['foo']
        {'type': 'empty'}

        >>> case = getfixture('tmpcase')
        >>> items = { 'application': 'simpleFoam', 'description': 'mycase' }
        >>> with case.mutable_data_file(FileName.CONTROL) as d:
        ...     d.update(items)
        >>> control = case.read_data_file(FileName.CONTROL)
        >>> control['application']
        'simpleFoam'
        >>> control['description']
        'mycase'

        """
        return _mutable_data_file_manager(
            self._get_rel_path(_to_dict_path(path)),
            create_class=create_class, create=create
        )

    def read_data_file(self, path):
        """Read the contents of the control dictionary.

        Args:
            path (str or FileName): relative path to dictionary

        Raises:
            IOError: the control dictionary could not be opened

        """
        return read_data_file(self._get_rel_path(_to_dict_path(path)))

    def run_tool(self, tool_name):
        """Run an OpenFOAM tool on the case.

        It is assumed that the tool accepts the standard "-case" argument.

        Args:
            tool_name (str): name of tool to run (e.g. "icoFoam")

        Raises:
            CaseToolRunFailed: if the tool exits with an error
        """
        logname = 'log.{}'.format(tool_name)
        runner = BasicRunner(
            [tool_name, '-case', self.root_dir_path],
            silent=True, logname=logname
        )
        runner.start()
        if not runner.runOK():
            raise CaseToolRunFailed('Tool "{}" failed'.format(tool_name))

    def _get_rel_path(self, path):
        """Return path relative to root directory."""
        return os.path.join(self.root_dir_path, path)

## PRIVATE CLASSES AND FUNCTIONS

@contextlib.contextmanager
def _mutable_data_file_manager(path, create_class=FileClass.DICTIONARY, 
                               create=True):
    """Context manager for mutating an OpenFOAM dict.

    If the dictionary is created, create_class is used to specify the class of
    the created dictionary.

    >>> dict_path = getfixture('tmpdir').join('tmpDict').strpath
    >>> with _mutable_data_file_manager(dict_path, create=True) as d:
    ...     d['test'] = 'foo'
    >>> read_data_file(dict_path)['test']
    'foo'

    Args:
        path (str): path to OpenFOAM dict
        create_class (str or FileClass): specify the class of created files
        create (bool): create file if it does not exist

    Returns:
        A context manager which reads (or optionally creates) an OpenFOAM dict
        file, returns a Python representation. When the context is left, the
        content is written back to disk.

    """
    if create and not os.path.isfile(path):
        dir_path = os.path.dirname(path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        try:
            create_class = create_class.value
        except AttributeError:
            create_class = create_class

        foam_file = WriteParameterFile(path, className=create_class)
    else:
        foam_file = ParsedParameterFile(path)
    yield foam_file.content
    foam_file.writeFile()

def _to_dict_path(path_or_dict_name):
    try:
        return path_or_dict_name.value
    except AttributeError:
        return path_or_dict_name
