"""
Test OpenFOAM case handling.

"""
import os

import pytest

from cusfsim.case import (
    Case, CaseDoesNotExist, Dimension, FileName, FileName, read_data_file,
    CaseToolRunFailed
)

@pytest.fixture
def tmpcase(tmpdir):
    """An empty Case instance which has been created in a temporary directory.

    """
    from cusfsim.case import Case
    case_dir = tmpdir.join('temp_case')
    return Case(case_dir.strpath)

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
    """Simple incovation of run_tool succeeds."""
    tmpcase.run_tool('foamInfoExec')

def test_run_tool_needs_tool_to_succeed(tmpcase):
    """Trying to run a tool which fails raises an error."""
    # Running blockMesh with no blockMeshDict fails
    with pytest.raises(CaseToolRunFailed):
        tmpcase.run_tool('blockMesh')
