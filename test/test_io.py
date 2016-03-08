import firefish.io as cio
import os
import pytest

@pytest.fixture
def engine1(iodir):
    engine_path = os.path.join(iodir, 'engine_1.rse')
    return cio.rse_load(engine_path)[0]

def assert_nearly_equal(a, b, tolerance=1e-3):
    assert abs(a-b) < tolerance

def test_single_load(iodir):
    engine_path = os.path.join(iodir, 'engine_1.rse')
    engines = cio.rse_load(engine_path)
    assert len(engines) == 1

def test_engine_has_code(engine1):
    assert engine1.code == "614-I100-RL_LB-17A"

def test_engine_has_manufacturer(engine1):
    assert engine1.manufacturer == "CTI"

def test_engine_has_comments(engine1):
    assert engine1.comments == "Pro-54-2G Red Lightning Long Burn"

def test_engine_has_data(engine1):
    assert engine1.data is not None

def test_engine_times_correct(engine1):
    times = engine1.data['time']
    assert times.size == 22
    assert_nearly_equal(times.iloc[0], 0)
    assert_nearly_equal(times.iloc[-1], 8.993)

def test_engine_forces_correct(engine1):
    times = engine1.data['force']
    assert times.size == 22
    assert_nearly_equal(times.iloc[1], 269.267)
    assert_nearly_equal(times.iloc[-2], 0.95)

def test_engine_masses_correct(engine1):
    times = engine1.data['mass']
    assert times.size == 22
    assert_nearly_equal(times.iloc[0], 350.1)
    assert_nearly_equal(times.iloc[-2], 0.0681854)

