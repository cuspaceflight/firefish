.. This file is read by doc/examples.rst and inserted into the documentation. It
   lives here so that it is more clearly associated with
   openfoam_supersonic_wedge.py. Note that file paths are, however, relative to
   the doc/ directory.

Supersonic flow over wedge
----------------------

The :download:`openfoam_supersonic_wedge.py <../examples/openfoam_supersonic_wedge.py>`
script provides an example of setting up a compressible flow solver in OpenFoam.


As in :download:`openfoam_cavity_tutorial.py <../examples/openfoam_cavity_tutorial.py>`
we set up the OpenFOAM case directory using the *firefish.case* framework.

For flows with a Mach number above 0.3 compressible effects become non negligible. A
compressible solver must therefore be used. In this case we use *rhoCentralFoam*. The
control file must therefore be set accordingly:

.. literalinclude:: ../examples/openfoam_supersonic_wedge.py
   :pyobject: write_control_dict
   
The mesh needs to be set up using the *blockMeshDict*. The mesh consits of three blocks in order
to model the upstream and downstream portions as well as the wedge itself. The numbering order in which the 
vertices are set is very important! We declare a block via::

    hex', [0, 7, 2, 1, 8, 15, 10, 9], [40, 40, 1],
                'simpleGrading', [1, 1, 1]
 
The first line declares which vertices make up the corners of the block. This `explanation`_ best
describes the order in which the vertices should be listed. The second part of the statement
describes the cell density within the block in each of the three directions. The last part is used
when we want the mesh density to vary within the block.

.. _explanation: http://cfd.direct/openfoam/user-guide/blockmesh/

We must also set the thermodynamic properties of the gas. In this case the properties have been chosen
so that the gas has a ratio of specific heats of 1.4 and that, if the temperature is 1K, then the speed of sound
is 1m/s. As this is a commonly used fluid it can be done using the *write_standard_thermophysical_properties* function in
the *firefish.case* module. We do this via::

    write_standard_thermophysical_properties(case, StandardFluid.DIMENSIONLESS_AIR)

As this is a compressible flow we must also set the initial value of the temperatue field. Notice also that for the 
velocity we have set a slip boundary condition on the solid walls. This is because we are using an inviscid solver. When we
move to a viscous solver we must set a no slip boundary condition on the solid walls.

.. literalinclude:: ../examples/openfoam_supersonic_wedge.py
   :pyobject: write_initial_conditions

The example script includes a :py:func:`main` function which performs all of
these steps. A boolean value can be passed to :py:func:`main` in order to reduce the number of iterations
and so speed up automatic testing.

.. literalinclude:: ../examples/openfoam_supersonic_wedge.py
   :pyobject: main

After the example script is run, *paraFoam* may be run to inspect the solution.
