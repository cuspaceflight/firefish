"""
This module deals with kinematic models used in rocket simulation
"""
import numpy as np
import matplotlib.pyplot as plt
import math

import enum

class KinematicBody(object):
    def __init__(self,mass,inertias):
        self.mass = mass
        self.MoI = inertias
        self.vel = np.zeros(3,float)
        self.rot = np.zeros(3,float)
        
    def update_moi(self):
        '''We update moments of inertias. This should be overloaded by inherting classes'''
        
class KinematicSimulation(object):
    def __init__(self,body,gravity,duration,dt):
        self.g = gravity
        self.body = body
        self.times = np.linspace(0,duration,num=duration/dt + 1)
        self.posits = np.zeros([self.times.shape[0],3],float) #x,y,z position
        self.angles = np.zeros([self.times.shape[0],3],float)
        self.dt = dt
        self.tIndex = 1 #means we have t=0 as being on the pad
    def time_step(self,forces,torques,mdot):
        #we update our positon and attitude so that we start from the previous point
        self.posits[self.tIndex,:] = self.posits[self.tIndex-1,:]
        self.angles[self.tIndex,:] = self.angles[self.tIndex-1,:]
        
        #We update the bodies mass by half a time step ( as this is the mass used during timestepping)
        self.body.mass -= mdot*0.5*self.dt
        
        self.body.update_moi() #we update the moments of inertiat based on the timestep mass
        
        moments = np.array(torques)
        moi     = np.array(self.body.MoI)
        
        rotdotbody = moments/moi
        
        theta = self.angles[self.tIndex,0]
        rotmat = np.array([ [np.cos(theta), 0, np.sin(theta)],
                            [0, 1, 0],
                            [-1*np.sin(theta), 0, np.cos(theta)]])
        rotdotglobal = np.dot(rotmat,rotdotbody)
        
        rot0 = self.body.rot*1
        self.body.rot +=rotdotglobal*self.dt
        
        self.angles[self.tIndex,:] += 0.5*(rot0 + self.body.rot)*self.dt
        
        bodyForces = np.array(forces) #in Newtons
        vdotbody = bodyForces/self.body.mass
        
        vdotglobal = np.dot(rotmat,vdotbody)
        vdotglobal[2] += -self.g
        
        print('vdotglobal:')
        
        print(vdotglobal)
        
        vel0 = self.body.vel*1
        self.body.vel += vdotglobal*self.dt
        
        print('vel')
        
        
        print(self.body.vel)
        
        print('vel0')
        print(vel0)
        
        self.posits[self.tIndex,:] += 0.5*(self.body.vel+vel0)*self.dt
        print('dt is %f'%(self.dt))
        print('pos')
        
        print(self.posits[self.tIndex,:])
        
        #We correct the mass
        self.body.mass -=mdot*0.5*self.dt
        
        #we update the time index
        self.tIndex+=1
        
        
        
        
        
        
        
        
        
        
        
        
