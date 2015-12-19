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
    
    #write_mirror_mesh_dict(case)
    #case.run_tool('mirrorMesh')
    #modify_mirror_axes(case)
    #case.run_tool('mirrorMesh')
    #we prepare the thermophysical and turbulence properties
    #write_thermophysical_properties(case)
    #write_turbulence_properties(case)
    #we write fvScheme and fvSolution
    #write_fv_schemes(case)
    #write_fv_solution(case)
    #write_initial_conditions(case)
    #case.run_tool('rhoCentralFoam')

def create_new_case(case_dir):
    """Creates new case directory"""
    #Checks to make sure we don't overwrite and existing case
    if os.path.exists(case_dir):
        raise RuntimeError(
                'Refusing to write to existing path: {}'.format(case_dir)
            )
    #creates the case
    return Case(case_dir)

def write_control_dict(case, n_iter):
    """Sets up the control dictionary.
    In this example we use the rhoCentralFoam compressible solver"""

    # Control dict from tutorial
    control_dict = {
        'application': 'rhoCentralFoam',
        'startFrom': 'startTime',
        'startTime': 0,
        'stopAt': 'endTime',
        'endTime': n_iter,
        'deltaT': 0.00003,
        'writeControl': 'runTime',
        'writeInterval': 0.003,
        'purgeWrite': 0,
        'writeFormat': 'ascii',
        'writePrecision': 6,
        'writeCompression': 'off',
        'timeFormat': 'general',
        'timePrecision': 6,
        'runTimeModifiable': True,
        'adjustTimeStep' : 'no',
        'maxCo' : 1,
        'maxDeltaT' : 1e-6,
    }

    with case.mutable_data_file(FileName.CONTROL) as d:
        d.update(control_dict)

def write_block_mesh_dict(case):
    """Writes the block mesh"""
    block_mesh_dict = {
  
        'convertToMeters': 1,

        'vertices': [
            [0.5, 0, 0], [25, 0, 0], [0, 25, 0], [0, 0.5, 0],
            [0.5, 0, 0.05], [25, 0, 0.05], [0, 25, 0.05], [0, 0.5, 0.05],
        ],

        'blocks': [
            (
                'hex', [0, 1, 2, 3, 4, 5, 6, 7], [30, 30, 1],
                'simpleGrading', [8, 1, 1],
            )
        ],

        'edges': [

            'arc', (3, 0), [0.3536, 0.3536, 0],
            'arc', (4, 7), [0.3536, 0.3536, 0.05],
            'arc', (1, 2), [0.3536, 0.3536, 0],
            'arc', (5, 6), [0.3536, 0.3536, 0.05],
        ],

        # Note the odd way in which boundary is defined here as a
        # list of tuples.
        'boundary': [
            ('outerRim', {
                'type': 'patch',
                'faces': [[2, 6, 5, 1]],
            }),
        
            ('cylinder', {
                'type': 'wall',
                'faces': [[0, 4, 7, 3]],
            }),
        
            ('frontAndBack', {
                'type': 'empty',
                'faces': [
                    [0, 3, 2, 1],
                    [4, 5, 6, 7],
                ],
            }),
        ],

        'mergePatchPairs': [],
    }

    with case.mutable_data_file(FileName.BLOCK_MESH) as d:
        d.update(block_mesh_dict)


if __name__ == '__main__':
    main()
