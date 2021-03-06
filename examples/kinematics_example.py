"""
Example to demonstrate the kinematics classes

>>> abs(main()-27670)<1
True
"""

from firefish.kinematics import (
    KinematicBody, KinematicSimulation)

class CylinderRocket(KinematicBody):
    """A rocket that is a cylinder with  evenly distributed mass"""
    def update_moi(self):
        radius = 0.3
        height = 2
       
        Ixx = (self.mass/12.0)*(3*radius**2 + height**2)
        Iyy = (self.mass/12.0)*(3*radius**2 + height**2)
        Izz = self.mass*radius**2 / 2.0
        
        self.MoI = [Ixx,Iyy,Izz]
        
pos = []
        
def main():
    """Run through the simulation with a 50s motor burn"""
    initialMass = 100
    initialInertias = [0, 0, 0]
    rocket = CylinderRocket(initialMass,initialInertias)
    dt =1; duration = 100; gravity = 9.81;
    simulation = KinematicSimulation(rocket,gravity,duration,dt)
    while simulation.tIndex*dt <= duration:

        thrust = 0

        if simulation.tIndex*dt <= 50:
            thrust = 2000.0

        forces = [2.0, 0.0, thrust]
        torques = [0.0, 0.0, 0.0]
        mdot = 0.1

        i = simulation.tIndex
       
        simulation.time_step(forces,torques,mdot)
    
    return simulation.posits[100,2] #z position
    
if __name__ == '__main__':
    main()