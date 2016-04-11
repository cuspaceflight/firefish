import firefish.kinematics as kine
import pytest

@pytest.fixture
def kilogram_point_mass():
    return kine.KinematicBody(1, [0, 0, 0])


def test_kinematics_vert():
    dur = 10
    dt = 0.1
    g = 10
    F = [0,0,20]
    sim = kine.KinematicSimulation(kilogram_point_mass(), g, dur, dt)
    while sim.tIndex*dt <= dur:
        sim.time_step(F, [0, 0, 0], 0)
    zPos = sim.posits[int(dur/dt), 2]
    calcZPos = 0.5*10*dur**2
    distTol = 1
    assert(abs(zPos-calcZPos)<distTol)

def test_kinematics_mass():
    dur = 10
    dt = 0.1
    g = 10
    sim = kine.KinematicSimulation(kilogram_point_mass(),g,dur,dt)
    sim.time_step([0,0,0],[0,0,0],1)
    massTol = 0.01
    assert(abs(sim.body.mass-(1.0-1.0*dt))<massTol)
