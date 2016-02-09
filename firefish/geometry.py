"""
This module deals with the loading, saving and manipulation of geometry.

Most manipulation functions deal with instances of :py:class:`stl.mesh.Mesh`. 
See the `numpy-stl documentation`_ for more information.

.. _numpy-stl documentation: http://numpy-stl.readthedocs.org/en/latest/stl.html#module-stl.mesh

"""
import numpy as np
import stl.mesh as mesh
import enum

from firefish.case import (
    Case, FileName)

class GeometryFormat(enum.Enum):
    """An enumeration of different geometry formats"""
    STL = 1

class MeshQualitySettings(object):
    """Controls the mesh quality settings associated with the gometry"""
    def __init__(self):
        """Fills it with default values"""
        self.maxNonOrtho = 65
        self.maxBoundarySkewness = 20
        self.maxInternalSkewness = 4
        self.maxConcave = 80
        self.minFlatness = 0.5
        self.minVol = 1e-13
        self.minArea = -1
        self.minTwist = 0.05
        self.minDeterminant = 0.001
        self.minFaceWeight = 0.05
        self.minVolRatio = 0.01
        self.minTriangleTwist = -1
        self.nSmoothScale = 4
        self.errorReduction = 0.75
        self.minTetQuality = 1e-9

    def write_settings(self, case):
        """Writes the quality settings to a separate dict that can be included"""
        quality_settings_dict = {
            'maxNonOrtho' : self.maxNonOrtho,
            'maxBoundarySkewness' : self.maxBoundarySkewness,
            'maxInternalSkewness' : self.maxInternalSkewness,
            'maxConcave' : self.maxConcave,
            'minFlatness' : self.minFlatness,
            'minVol' : self.minVol,
            'minArea' : self.minArea,
            'minTwist' : self.minTwist,
            'minDeterminant' : self.minDeterminant,
            'minFaceWeight' : self.minFaceWeight,
            'minVolRatio' : self.minVolRatio,
            'minTriangleTwist' : self.minTriangleTwist,
            'nSmoothScale' : self.nSmoothScale,
            'errorReduction' : self.errorReduction,
            'minTetQuality' : self.minTetQuality}
        with case.mutable_data_file(FileName.MESH_QUALITY_SETTINGS) as d:
            d.update(quality_settings_dict)


class Geometry(object):
    """Encapsulates a lot of desired geometry functionality"""

    def __init__(self, geomType, path, name, case):
        """Initialises settings and loads the geometry into memory"""
        self.geomType = geomType
        self.geomPath = path
        self.saved = False    #Flag to check whether this has been written or not
        self.case = case
        self.name = name
        self.filename = '{}.stl'.format(self.name)

        if geomType == GeometryFormat.STL:
            self.geom = load(path)

        self.meshSettings = MeshQualitySettings() # we create a default set of mesh quality settings

    def translate(self, delta):
        """Scales geometry by delta"""
        if self.geomType == GeometryFormat.STL:
            self.geom = translate(self.geom, delta)

    def scale(self, factor):
        """Scales geometry by factor"""
        if self.geomType == GeometryFormat.STL:
            self.geom = scale(self.geom,factor)

    def extract_features(self):
        """Extracts features from geometry using the surfaceFeatureExtract tool"""
        #This is used by mesh generation but could be used elsewhere so is kept in this class
        if self.saved==False:
            self.case.add_tri_surface(self.name,self.geom)

        surface_extract_dict = {
            '{}.stl'.format(self.name) : { 'extractionMethod' : 'extractFromSurface',
                                           'extractFromSurfaceCoeffs' : { 'includedAngle' : 180,
                                                                          'geometricTestOnly' : True },
                                           'writeObj' : 'yes'}
        }

        with self.case.mutable_data_file(FileName.SURFACE_FEATURE_EXTRACT) as d:
            d.update(surface_extract_dict)

        self.case.run_tool('surfaceFeatureExtract')

def _erase_attr(o, attr):
    """Delete the attribute *attr* from *o* but only if present."""
    if hasattr(o, attr):
        delattr(o, attr)

def load(path):
    """Convenience function to load a :py:class:`stl.mesh.Mesh` from disk.

    .. note::

        The :py:meth:`save` method on :py:class:`stl.mesh.Mesh` may be used to
        write geometry to disk.

    Args:
        path (str): pathname to STL file

    Returns:
        an new instance of :py:class:`stl.mesh.Mesh`
    """
    return mesh.Mesh.from_file(path)

def bounds(geom):
    """Compute the bounding box of the geometry.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        A pair giving the minimum and maximum X, Y and Z co-ordinates as
        three-dimensional array-likes.

    """
    return geom.min_, geom.max_

def geometric_centre(geom):
    """Compute the centre of the bounding box.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        An array like giving the X, Y and Z co-ordinates of the centre.

    """
    return 0.5 * (geom.max_ + geom.min_)

def copy(geom):
    """Copy a geometry.

    Use this function sparingly. Geometry can be quite heavyweight as data
    structures go.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        A deep copy of the geometry.

    """
    return mesh.Mesh(geom.data, calculate_normals=False, name=geom.name)

def translate(geom, delta):
    """Translate a geometry along some vector.

    This function modifies the passed geometry.

    Args:
        geom (stl.mesh.Mesh): STL geometry
        delta (array like): 3-vector giving translation in X, Y and Z

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    cx, cy, cz = np.atleast_1d(delta)
    geom.x += cx
    geom.y += cy
    geom.z += cz

    # Delete cached minimum and maximum values. Other cached values are
    # unaffected. (This sort of magic is why we write wrappers!)
    _erase_attr(geom, '_min')
    _erase_attr(geom, '_max')

    return geom

def recentre(geom):
    """Centre a geometry such that its bounding box is centred on the origin.

    This function modifies the passed geometry.

    Equivalent to::

        translate(geom, -geometric_centre(geom))

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    return translate(geom, -geometric_centre(geom))

def scale(geom, factor):
    """Scale geometry by a fixed factor.

    This function modifies the passed geometry. If the scale factor is a single
    scalar it is applied to each axis. If it is a 3-vector then the elements
    specify the scaling along the X, Y and Z axes.

    Args:
        geom (stl.mesh.Mesh): STL geometry
        factor (scalar or array like): scale factor to apply

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    factor = np.atleast_1d(factor)
    if factor.shape == (1,):
        factor = np.ones(3) * factor[0]
    sx, sy, sz = factor

    geom.x *= sx
    geom.y *= sy
    geom.z *= sz

    # Delete cached minimum, maximum and area values. Other cached values are
    # unaffected. (This sort of magic is why we write wrappers!)
    _erase_attr(geom, '_min')
    _erase_attr(geom, '_max')
    _erase_attr(geom, '_areas')

    return geom
