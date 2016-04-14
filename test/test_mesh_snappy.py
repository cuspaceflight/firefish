import os

import numpy as np
import pytest

import firefish.geometry as geom
import firefish.meshsnappy as snappy

@pytest.fixture
def tmpcase(tmpdir):
    """An empty Case instance which has been created in a temporary directory.

    """
    from firefish.case import Case
    case_dir = tmpdir.join('temp_case')
    return Case(case_dir.strpath)

def test_snappy_dict(tmpcase,tmpdir,geomdir):
    stl_path = os.path.join(geomdir, 'unit_sphere.stl')
    geometry = geom.Geometry(geom.GeometryFormat.STL,stl_path,'sphere',tmpcase)
    snap = snappy.SnappyHexMesh([geometry],4,tmpcase)
    snap.write_snappy_dict()
    assert os.path.isfile(os.path.join(
        tmpcase.root_dir_path, 'system','snappyHexMeshDict'
    ))
