"""Configuration for pytest.

Put any global scope fixtures in this file. Fixtures defined in this file are
available to doctest tests via the "getfixture" function.

"""
import pytest

@pytest.fixture
def tmpcase(tmpdir):
    """An empty Case instance which has been created in a temporary directory.

    """
    from firefish.case import Case
    case_dir = tmpdir.join('temp_case')
    return Case(case_dir.strpath)

