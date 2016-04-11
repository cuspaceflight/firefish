"""
This module deals with kinematic models used in rocket simulation
"""
import numpy as np


class KinematicBody(object):
    """Encapsulates information about the kinematic body"""

    def __init__(self, mass, inertias):
        """
        Initialises the kinematic body
        Args:
            mass (float): the mass of the body
            inertias ([float,float,float]): Principal moments of inertia in form [Ixx,Iyy,Izz]
        """
        self.mass = mass
        self.MoI = inertias
        self.vel = np.zeros(3, float)
        self.rot = np.zeros(3, float)

    def update_moi(self):
        """
        We update moments of inertias.
        Any class inheriting KinematicBody must overload this if it has non-constant
        moments of inertia
        """

class KinematicSimulation(object):
    """
    Encapsulates all the simulation logic and time stepping
    """
    def __init__(self, body, gravity, duration, dt):
        """
        Initialises the simulation
        Args:
            body (firefish.kinematics.KinematicBody): the kinematic body to simulate
            gravity (float): accelaration due to gravity in ms^-2
            duration (float): duration of the simulation in s
            dt (float): time step of the simulation in s
        """
        self.g = gravity
        self.body = body
        self.times = np.linspace(0, duration, num=duration/dt + 1)
        # pylint: disable=no-member
        self.posits = np.zeros([self.times.shape[0], 3]) #x,y,z position
        self.angles = np.zeros([self.times.shape[0], 3])
        self.dt = dt
        self.tIndex = 1 #means we have t=0 as being on the pad
    def time_step(self, forces, torques, mdot):
        """
        Performs a single time step

        Args:
            forces ([float]): A list of the forces on the body in N in the form [Fx,Fy,Fz]
            torques ([float]): A lst of the moments acting on the body in Nm in the
                form [Mxx,Myy,Mzz]
            modt (float): Mass flow rate of the motor. i.e. 0.1 implies the motor is
                ejection 0.1 kgs^-1
        """
        #we update our positon and attitude so that we start from the previous point
        self.posits[self.tIndex, :] = self.posits[self.tIndex-1, :]
        self.angles[self.tIndex, :] = self.angles[self.tIndex-1, :]

        #We update the bodies mass by half a time step ( as this is the mass used during
        #timestepping)
        self.body.mass -= mdot*0.5*self.dt

        self.body.update_moi() #we update the moments of inertiat based on the timestep mass

        moments = np.array(torques)
        moi = np.array(self.body.MoI)

        rotdotbody = moments/moi

        theta = self.angles[self.tIndex, 0]
        rotmat = np.array([[np.cos(theta), 0, np.sin(theta)],
                           [0, 1, 0],
                           [-1*np.sin(theta), 0, np.cos(theta)]])
        rotdotglobal = np.dot(rotmat, rotdotbody)

        rot0 = self.body.rot*1
        self.body.rot += rotdotglobal*self.dt

        self.angles[self.tIndex, :] += 0.5*(rot0 + self.body.rot)*self.dt

        bodyForces = np.array(forces) #in Newtons
        vdotbody = bodyForces/self.body.mass

        vdotglobal = np.dot(rotmat, vdotbody)
        vdotglobal[2] += -self.g

        vel0 = self.body.vel*1
        self.body.vel += vdotglobal*self.dt

        self.posits[self.tIndex, :] += 0.5*(self.body.vel+vel0)*self.dt

        #We correct the mass
        self.body.mass -= mdot*0.5*self.dt

        #we update the time index
        self.tIndex += 1
