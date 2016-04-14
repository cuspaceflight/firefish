"""
Test OpenFOAM case handling.

"""
import os

import pytest

import firefish.geometry
from firefish.case import (
    Case, CaseDoesNotExist, Dimension, FileName, FileName, read_data_file,
    CaseToolRunFailed, CaseAlreadyExists, StandardFluid,
    write_standard_thermophysical_properties
)

@pytest.fixture
def tmpcase(tmpdir):
    """An empty Case instance which has been created in a temporary directory.

    """
    from firefish.case import Case
    case_dir = tmpdir.join('temp_case')
    return Case(case_dir.strpath)

@pytest.fixture
def unit_sphere_geometry(geomdir):
    """An stl.mesh.Mesh representing the unit sphere."""
    stl_path = os.path.join(geomdir, 'unit_sphere.stl')
    return firefish.geometry.stl_load(stl_path)

def _read_foam_dict(path):
    """Read foam dict file at path and return content."""
    return ParsedParameterFile(path).content

def test_case_must_exist(tmpdir):
    """If create is False, the case directory must exist."""
    case_dir = tmpdir.join('does_not_exist')
    assert not case_dir.check()
    with pytest.raises(CaseDoesNotExist):
        Case(case_dir.strpath, create=False)

def test_case_created(tmpdir):
    """If create is True, the case directory is created."""
    case_dir = tmpdir.join('does_not_exist')
    assert not case_dir.check()
    Case(case_dir.strpath)
    assert case_dir.check()

def test_write_control_dict(tmpcase):
    """Writing to a mutable control dict should be reflected on disk."""
    with tmpcase.mutable_data_file(FileName.CONTROL) as control:
        control['testing'] = 'oneTwoThree'
    dict_path = os.path.join(tmpcase.root_dir_path, 'system', 'controlDict')
    assert os.path.isfile(dict_path)
    content = read_data_file(dict_path)
    assert 'testing' in content
    assert content['testing'] == 'oneTwoThree'

def test_read_data_file_needs_file(tmpdir):
    """Reading a non-existent dictionary file raises."""
    pn = tmpdir.join('noSuchDict').strpath
    assert not os.path.isfile(pn)
    with pytest.raises(IOError):
        read_data_file(pn)

def test_dimension_type_preserved(tmpcase):
    dims = Dimension(1, 2, 3, 4, 5, 6, 7)
    with tmpcase.mutable_data_file('test') as d:
        d['foo'] = dims
    d = tmpcase.read_data_file('test')
    assert d['foo'] == dims
    print(type(d['foo']))
    assert isinstance(d['foo'], Dimension)

def test_run_tool(tmpcase):
    """Simple invocation of run_tool succeeds."""
    tmpcase.run_tool('foamInfoExec')

def test_run_tool_needs_tool_to_exist(tmpcase):
    """Simple invocation of run_tool fails for a non-existent tool."""
    with pytest.raises(OSError):
        tmpcase.run_tool('thatsNoTool')

def test_run_tool_needs_tool_to_succeed(tmpcase):
    """Trying to run a tool which fails raises an error."""
    # Running blockMesh with no blockMeshDict fails
    with pytest.raises(CaseToolRunFailed):
        tmpcase.run_tool('blockMesh')

def test_add_tri_surface(tmpcase, unit_sphere_geometry):
    assert not os.path.isfile(os.path.join(
        tmpcase.root_dir_path, 'constant', 'triSurface', 'surface.stl'
    ))
    tmpcase.add_tri_surface('surface', unit_sphere_geometry)
    assert os.path.isfile(os.path.join(
        tmpcase.root_dir_path, 'constant', 'triSurface', 'surface.stl'
    ))

def test_add_tri_surface_does_not_clobber(tmpcase, unit_sphere_geometry):
    tmpcase.add_tri_surface('surface', unit_sphere_geometry)
    with pytest.raises(CaseAlreadyExists):
        tmpcase.add_tri_surface('surface', unit_sphere_geometry)

def test_add_tri_surface_will_clobber_if_asked(tmpcase, unit_sphere_geometry):
    tmpcase.add_tri_surface('surface', unit_sphere_geometry)
    tmpcase.add_tri_surface('surface', unit_sphere_geometry,
                            clobber_existing=True)

def test_dimensionless_air(tmpcase):
    """Tests dimensionless air writes to a file"""
    write_standard_thermophysical_properties(tmpcase, StandardFluid.DIMENSIONLESS_AIR)
    dict_path = os.path.join(tmpcase.root_dir_path, 'constant', 'thermophysicalProperties')
    assert os.path.isfile(dict_path)


def test_dimensionless_air(tmpcase):
    """Tests dimensionless air writes to a file"""
    write_standard_thermophysical_properties(tmpcase, StandardFluid.AIR)
    dict_path = os.path.join(tmpcase.root_dir_path, 'constant', 'thermophysicalProperties')
    assert os.path.isfile(dict_path)
