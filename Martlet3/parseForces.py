#!/usr/bin/python                                                                                                                                                                                                                     
import numpy
import matplotlib
import re

from matplotlib import pyplot as plt

#Current Input
#1.000000e+00    ((1.460676e+04 -1.948520e+02 9.535164e+02) (2.508036e-02 -6.720399e-05 -3.082446e-04) (0.000000e+00 0.000000e+00 0.000000e+00)) ((1.140514e+04 1.153182e+05 -1.730316e+05) (-3.153913e-03 1.658614e-01 -2.916495e-01\
#) (0.000000e+00 0.000000e+00 0.000000e+00)                                                                                                                                                                                            

forceRegex=r"([0-9.Ee\-+]+)\s+\(+([0-9.Ee\-+]+)\s([0-9.Ee\-+]+)\s([0-9.Ee\-+]+)+\)+\s+\(+([0-9.Ee\-+]+)"

#scale to real forces, negative to get positive numbers
rhoNorm = 1.4
rhoReal = 1.13
vNorm = 1.1 
vReal = 345
scaling = -(rhoReal/rhoNorm) * (vReal/vNorm)**2

#setup arrays
t = []
fpx = []; fpy = []; fpz = []; #Pressure
fpx1 = []; fpy1 = []; fpz1 = []; #Pressure                                                                                                                                                                                                                                                                                                                                                                                              
fvx = []; fvy = []; fvz = []; #Viscous                                                                                                                                                                                                
fpox = []; fpoy = []; fpoz=[];#Porous                                                                                                                                                                                                 
mpx = []; mpy = []; mpz = []; #Moment Pressure                                                                                                                                                                                        
mvx = []; mvy = []; mvz = []; #Moment Viscous                                                                                                                                                                                         
mpox= []; mpoy = [];mpoz = [];#Moment Porous                                                                                                                                                                                          

#read the .dat files
pipefileDart=open('../Martlet3/separationResults/postProcessing/forces1/0.095/forces.dat','r')
pipefileCore=open('../Martlet3/separationResults/postProcessing/forces2/0.095/forces.dat','r')

linesDart = pipefileDart.readlines()
linesCore = pipefileCore.readlines()

#iterate through to match to the forceRegex pattern
lth=len(linesDart);print(lth)

for i in xrange(0, lth, lth/200):
	match=re.search(forceRegex, linesDart[i])
	if match:
		t.append(float(match.group(1)))
		fpx.append(float(match.group(2)))
		fpy.append(float(match.group(3)))
		fpz.append(float(match.group(4)))

	match1=re.search(forceRegex, linesCore[i])
	if match1:
		fpx1.append(float(match1.group(2)))
		fpy1.append(float(match1.group(3)))
		fpz1.append(float(match1.group(4)))

#scale the arrays, find the separation force
fpy = [x * scaling for x in fpy]
fpy1 = [x * scaling for x in fpy1]
sep = numpy.subtract(fpy1, fpy)

#plot the forces
plt.figure()
plt.xlabel('Simulation time (sec)')
plt.ylabel('Drag force (N)')
plt.plot(t, fpy,'g', label = "Fin")
plt.plot(t, fpy1,'b', label = "Core")
plt.plot(t, sep, 'c', label = "Separation Force")
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
output = "separation-force.pdf"
plt.savefig(output, format='PDF')