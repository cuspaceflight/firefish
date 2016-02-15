import os

import numpy as np
import pytest

import firefish.geometry as geom

# Set this to be comparable to the tolerance at which we generate surfaces in
# the test geometry.
TOLERANCE=2e-2

@pytest.fixture
def unit_sphere(geomdir):
    """An stl.mesh.Mesh representing the unit sphere."""
    stl_path = os.path.join(geomdir, 'unit_sphere.stl')
    return geom.load(stl_path)

@pytest.fixture
def off_centre_unit_sphere(geomdir, tmpdir):
    """An stl.mesh.Mesh representing the unit sphere off centre."""
    stl_path = os.path.join(geomdir, 'unit_sphere.stl')
    g = geom.stl_load(stl_path)
    g.x += 0.1
    g.y += 0.2
    g.z -= 0.3

    # We save and re-load the geometry to make sure it's as if we loaded from
    # disk in the first place.
    tmp_stl = os.path.join(tmpdir.strpath, 'temp.stl')
    g.save(tmp_stl)
    return geom.stl_load(tmp_stl)

def test_load_stl(geomdir):
    stl_path = os.path.join(geomdir, 'unit_sphere.stl')
    assert os.path.isfile(stl_path)
    g = geom.stl_load(stl_path)
    assert g is not None

def test_bounds(unit_sphere):
    min_, max_ = geom.stl_bounds(unit_sphere)
    assert np.all(np.abs(min_ - np.array([-1, -1, -1])) < TOLERANCE)
    assert np.all(np.abs(max_ - np.array([1, 1, 1])) < TOLERANCE)

def test_geometric_center(unit_sphere):
    c = geom.stl_geometric_centre(unit_sphere)
    assert np.all(np.abs(c) < TOLERANCE)

def test_copy(unit_sphere):
    sphere_copy = geom.stl_copy(unit_sphere)
    assert sphere_copy is not unit_sphere
    assert np.all(sphere_copy.data == unit_sphere.data)

def test_recentre(off_centre_unit_sphere):
    c = geom.stl_geometric_centre(off_centre_unit_sphere)
    assert not np.all(np.abs(c) < TOLERANCE)
    geom.stl_recentre(off_centre_unit_sphere)
    c = geom.stl_geometric_centre(off_centre_unit_sphere)
    assert np.all(np.abs(c) < TOLERANCE)

def test_translate(unit_sphere):
    geom.stl_translate(unit_sphere, (-1,-2,3))
    c = geom.stl_geometric_centre(unit_sphere)
    assert np.all(np.abs(c - np.array([-1,-2,3])) < TOLERANCE)

def test_uniform_scale(unit_sphere):
    geom.stl_scale(unit_sphere, 2)
    min_, max_ = geom.stl_bounds(unit_sphere)
    assert np.all(np.abs(min_ - np.array([-2, -2, -2])) < 2*TOLERANCE)
    assert np.all(np.abs(max_ - np.array([2, 2, 2])) < 2*TOLERANCE)

def test_non_uniform_scale(unit_sphere):
    geom.stl_scale(unit_sphere, (0.5, 2, 3))
    min_, max_ = geom.stl_bounds(unit_sphere)
    assert np.all(np.abs(min_ - np.array([-0.5, -2, -3])) < 3*TOLERANCE)
    assert np.all(np.abs(max_ - np.array([0.5, 2, 3])) < 3*TOLERANCE)
