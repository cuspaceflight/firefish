.. This file is read by doc/examples.rst and inserted into the documentation. It
   lives here so that it is more clearly associated with
   openfoam_supersonic_wedge.py. Note that file paths are, however, relative to
   the doc/ directory.

Kinematics Example
-----------------------

The :download:`kinematics_example.py <../examples/kinematics_example.py>` script
uses the new *firefish.kinematics* framework to implement the kinematics example in :download:`kinematics_basis.py <../examples/kinematics_basis.py>`

We firstly define a class that inherits from *firefish.kinematics.KinematicBody*. We want to model a cylindrical rocket
whose principal moments of inertia vary as the rocket burns its motor. In order to vary the prinicpal moments of inertia
automatically during the timestepping routine we must overload the *update_moi()* function.

.. literalinclude:: ../examples/kinematics_example.py
    :pyobject: CylinderRocket
    
In the main function we now undergo the time stepping routine. For each time step we must pass the forces acting on the rocket
along with the torques to the routine. These forces and torques must be given in the body coordinate system. The example here burns
the motor for fifty seconds and then lets it coast

.. literalinclude:: ../examples/kinematics_example.py
    :pyobject: main