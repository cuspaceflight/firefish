#!/usr/bin/python                                                                                                                                                                                                                     
import pylab
import numpy
import matplotlib
import re

#Current Input
#1.000000e+00    ((1.460676e+04 -1.948520e+02 9.535164e+02) (2.508036e-02 -6.720399e-05 -3.082446e-04) (0.000000e+00 0.000000e+00 0.000000e+00)) ((1.140514e+04 1.153182e+05 -1.730316e+05) (-3.153913e-03 1.658614e-01 -2.916495e-01\
#) (0.000000e+00 0.000000e+00 0.000000e+00)                                                                                                                                                                                            

forceRegex=r"([0-9.Ee\-+]+)\s+\(+([0-9.Ee\-+]+)\s([0-9.Ee\-+]+)\s([0-9.Ee\-+]+)+\)+\s+\(+([0-9.Ee\-+]+)"

#change this to use real forces, negative to get positive numbers
scaling = -10000

t = []
fpx = []; fpy = []; fpz = []; #Pressure                                                                                                                                                                                               
fvx = []; fvy = []; fvz = []; #Viscous                                                                                                                                                                                                
fpox = []; fpoy = []; fpoz=[];#Porous                                                                                                                                                                                                 
mpx = []; mpy = []; mpz = []; #Moment Pressure                                                                                                                                                                                        
mvx = []; mvy = []; mvz = []; #Moment Viscous                                                                                                                                                                                         
mpox= []; mpoy = [];mpoz = [];#Moment Porous                                                                                                                                                                                          

pipefile=open('separation/M1p1_1206/forces1/forces_0.03502.dat','r')

lines = pipefile.readlines()

lth=len(lines);print(lth)

for i in xrange(0, lth, lth/100):
	
	match=re.search(forceRegex, lines[i])

	if match:
		t.append(float(match.group(1)))
		fpx.append(float(match.group(2)))
		fpy.append(float(match.group(3)))
		fpz.append(float(match.group(4)))
#       fvx.append(float(match.group(5)))
#       fvy.append(float(match.group(6)))
#       fvz.append(float(match.group(7)))
#       fpox.append(float(match.group(8)))
#       fpoy.append(float(match.group(9)))
#       fpoz.append(float(match.group(10)))
#       mpx.append(float(match.group(11)))
#       mpy.append(float(match.group(12)))
#       mpz.append(float(match.group(13)))
#       mvx.append(float(match.group(14)))
#       mvy.append(float(match.group(15)))
#       mvz.append(float(match.group(16)))
#       mpox.append(float(match.group(17)))
#       mpoy.append(float(match.group(18)))
#       mpoz.append(float(match.group(19)))

pylab.xlabel('time (sec)')
pylab.ylabel('force (N)')
pylab.grid(True)

#title('Example of using python to parse the force/moment tuples')                                                                                                                                                                    
pylab.plot(t,fpy,'o-')
pylab.show()