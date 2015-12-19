"""
Example which produces flow over a cylinder and uses function objects in order 
to calculate the drag coefficient over it.

The case will test the use of function objects, use of mirrorMesh to generate 
symmetrical geometries, and application of the Spalart-Allmaras turbulent model.

>>> import os
>>> case_dir = os.path.join(getfixture('tmpdir').strpath, 'cylinder')
>>> main(case_dir,1)
>>> os.path.isdir(os.path.join(case_dir, '1'))
True

"""

import os
from firefish.case import (
    Case, Dimension, FileName, FileClass
)

def main(case_dir='cylinder', n_iter=10):
    #Try to create new case directory
    case = create_new_case(case_dir)
    # Add the information needed by blockMesh.
    write_control_dict(case, n_iter)
    write_block_mesh_dict(case)
    #we generate the mesh
    case.run_tool('blockMesh')
    case.run_tool('mirrorMesh')
    modify_mirror_axes(case)
    case.run_tool('mirrorMesh')
    #we prepare the thermophysical and turbulence properties
    write_thermophysical_properties(case)
    write_turbulence_properties(case)
    #we write fvScheme and fvSolution
    write_fv_schemes(case)
    write_fv_solution(case)
    write_initial_conditions(case)
    case.run_tool('rhoCentralFoam')

if __name__ == '__main__':
    main()
