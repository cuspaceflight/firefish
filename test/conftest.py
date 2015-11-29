import os
import pytest

@pytest.fixture
def datadir():
    """A directory containing test data."""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def geomdir(datadir):
    """Geometry data directory."""
    return os.path.join(datadir, 'geometry')
