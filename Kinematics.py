import numpy as np
import matplotlib.pyplot as plt
import math
import pdb

#import firefish

dt = 1
duration = 100

times = np.linspace(0,duration,num=duration/dt+1)
posits = np.zeros([times.shape[0],3],float) # x,y,z - 3 DoF postion
# x,y,z are the position of the rocket in global coordinates
# x',y',z' are the body fixed coordinates of the rocket
angles = np.zeros([times.shape[0],3],float) # theta, psi, roll  - 3 DoF rotation
# Theta is defined as the angle down from the vertical (z) axis - the angle between z and z'
# Psi is defined as the rotation around the vertical (z) axis
# Roll is defined as the rotation around the z' axis 

# To begin with model rocket as a cylinder
Initial_Mass = 100
Radius = 0.3
Height = 2
gravityacc = 9.81 # m/s^2

t, mass = 10, Initial_Mass
vel = np.zeros(3,float) # start at the origin with zero velocity
rot = np.zeros(3,float)

for ii, t in enumerate(times):
	if ii > 0:
		dt = t - times[ii-1]

		if t <= 50: 
			Thrust = 2000.0
			print Thrust
		else: Thrust = 0.0

		angles[ii,:] = angles[ii-1,:]
		posits[ii,:] = posits[ii-1,:]

		## Mass integration ------------------------------------------
		
		mdot = 0.1 # kg / s 	

		mass0 = mass*1
		mass -= mdot
		timestepmass = 0.5*(mass + mass0)
	
		# Moments of inertia from geometry + engine mass
		Ixx = (timestepmass/12.0)*( 3*Radius**2 + Height**2 )
		Iyy = (timestepmass/12.0)*( 3*Radius**2 + Height**2 )
		Izz = timestepmass*Radius**2 / 2.0
		MoI = np.array([Ixx,Iyy,Izz])

		# Forces and moments from CFD solution - in body coordinates
		moments = np.array([0.0, 0.0, 0.0])  # Nm = kg m^2 / s^2
		rotdotbody = moments/MoI

		theta = angles[ii,0]
		rotmat = 	np.array([	[np.cos(theta), 0, np.sin(theta)],
								[0, 1, 0],
								[-1*np.sin(theta), 0, np.cos(theta)] ])
		
		rotdotglobal = np.dot(rotmat,rotdotbody) 

		## Moments integration ------------------------------------------
		
		# Rotation integration from angular acceleration
		rot0 = rot*1
		rot += rotdotglobal*dt 
		angles[ii,:] += 0.5*(rot0 + rot)*dt	

		## Forces integration ------------------------------------------
		forces = np.array([2.0, 0.0, Thrust])  # Nm = kg m / s^2
		#pdb.set_trace()		
		vdotbody = forces/timestepmass
	
		vdotglobal = np.dot(rotmat,vdotbody)
		vdotglobal[-1] += -gravityacc

		# Convert forces from body to global

		# Velocity integration from acceleration
		vel0 = vel*1 # *1 to avoid copying variable reference
		vel += vdotglobal*dt
		posits[ii,:] += 0.5*(vel + vel0)*dt

plt.figure()
plt.scatter(times[:],posits[:,0])
plt.xlabel('Time')
plt.ylabel('x')
plt.figure()
plt.scatter(times[:],posits[:,1])
plt.xlabel('Time')
plt.ylabel('y')
plt.figure()
plt.scatter(times[:],posits[:,2])
plt.xlabel('Time')
plt.ylabel('z')
plt.show()


	




