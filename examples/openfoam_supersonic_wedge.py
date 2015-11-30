""" 
Example which produces flow over a supersonic wedge
"""

import os
from cusfsim.case import Case,FileName, FileClass

def main(case_dir='wedge'):
    #Try to create new case directory
    case = create_new_case(case_dir)
    # Add the information needed by blockMesh.
    write_initial_control_dict(case)
    write_block_mesh_dict(case)
    #we prepare the thermophysical and turbulence properties
    write_thermophysical_properties(case)
    write_turbulence_properties(case)
    #we write fvScheme and fvSolution
    write_fv_schemes(case)
    write_fv_solution(case)


def create_new_case(case_dir):
    #Checks to make sure we don't overwite an existing case
    if os.path.exists(case_dir):
        raise RuntimeError(
                'Refusing to write to existing path: {}'.format(case_dir)
            )
    #Creates the case
    return Case(case_dir)

def write_initial_control_dict(case):
    # Control dict from tutorial
    control_dict = {
        'application': 'rhoCentralFoam',
        'startFrom': 'startTime',
        'startTime': 0,
        'stopAt': 'endTime',
        'endTime': 10,
        'deltaT': 0.005,
        'writeControl': 'runTime',
        'writeInterval': 0.5,
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
    block_mesh_dict = {
        'convertToMeters': 1,

        'vertices': [
            [0, 0, 0], [0, 1, 0], [0.5, 1, 0], [1.5, 1, 0],
            [3, 1, 0], [3, 0.1763, 0], [1.5, 0.1763, 0], [0.5, 0, 0],
            [0, 0, 1], [0, 1, 1], [0.5, 1, 1], [1.5, 1, 1],
            [3, 1, 1], [3, 0.1763, 1], [1.5, 0.1763, 1], [0.5, 0, 1],
        ],

        'blocks': [
            (
                'hex', [0, 7, 2, 1, 8, 15, 10, 9], [40, 20, 1], 'simpleGrading', [1, 1, 1],
                'hex', [7, 6, 3, 2, 15, 14, 11, 10], [40, 20, 1], 'simpleGrinading', [1, 1, 1],
                'hex', [6, 5, 4, 3, 14, 13, 12, 11], [40, 20, 1], 'simpleGrading', [1, 1, 1],
            )
        ],

        'edges': [],

        # Note the odd way in which boundary is defined here as a
        # list of tuples.
        'boundary': [
            ('inlet', {
                'type': 'patch',
                'faces': [ [0, 1, 9, 8] ],
            }),
            ('outlet', {
                'type': 'patch',
                'faces': [ [12, 4, 5, 13] ],
            }),
            ('fixedWalls', {
                'type': 'wall',
                'faces': [
                    [0, 8, 15, 7],
                    [7, 15, 14, 6],
                    [6, 14, 13, 5],
                    [9, 1, 2, 10],
                    [10, 2, 3, 11],
                    [11, 3, 4, 12],
                ],
            }),
            ('frontAndBack', {
                'type': 'empty',
                'faces': [
                    [1,0,7,2],
                    [2,7,6,3],
                    [3,6,5,4],
                    [8,9,10,15],
                    [15,10,11,14],
                    [14,11,12,13],
                ],
            }),
        ],

        'mergePatchPairs': [],
    }

    with case.mutable_data_file(FileName.BLOCK_MESH) as d:
        d.update(block_mesh_dict)
        
def write_thermophysical_properties(case):
    thermo_dict = {
        'thermoType' : { 'type' : 'hePsiThermo', 'mixture' : 'pureMixture',
                         'transport' : 'const' , 'thermo'  : 'hConst',
                         'equationOfState' : 'perfectGas', 'specie' : 'specie',
                         'energy' : 'sensibleInternalEnergy' },
        'mixture' : { 'specie' : { 'nMoles' : 1 , 'molWeight' : 11640.3 },
                      'thermodynamics' : { 'Cp' : 2.5, 'Hf' : 0 },
                      'transport' : { 'mu' : 0, 'Pr' : 1 } } }
    with case.mutable_data_file(FileName.THERMOPHYSICAL_PROPERTIES) as d:
        d.update(thermo_dict)
        
def write_turbulence_properties(case):
    turbulence_dict = {
        'simulationType' : 'laminar' }
    with case.mutable_data_file(FileName.TURBULENCE_PROPERTIES) as d:
        d.update(turbulence_dict)
        

        

def write_fv_schemes(case):
    fv_schemes={
        'ddtSchemes'  : { 'default' : 'Euler' },
        'gradSchemes' : { 'default' : 'Gauss linear' },
        'divSchemes'  : { 'default' : 'none', 'div(tauMC)' : 'Gauss linear' },
        'laplacianSchemes' : { 'default' : 'Gauss linear corrected' },
        'interpolationSchemes' : { 'default' : 'linear', 'reconstruct(rho)' : 'vanLeer',
                                   'reconstruct(U)' : 'vanLeerV', 'reconstruct(T)': 'vanLeer' },
        'snGradSchemes' : { 'default': 'corrected' } }
    with case.mutable_data_file(FileName.FV_SCHEMES) as d:
        d.update(fv_schemes)
        
def write_fv_solution(case):
    fv_solution = { 
        'solvers' : { '"(rho|rhoU|rhoE)"': { 'solver' : 'diagonal' },
                      'U' : { 'solver'  : 'smoothSolver', 'smoother' : 'GaussSeidel', 
                              'nSweeps' : 2, 'tolerance' : 1e-09, 'relTol' : 0.01 },
                      'h' : { '$U' : ' ', 'tolerance' : 1e-10, 'relTol' : 0 } } }
    with case.mutable_data_file(FileName.FV_SOLUTION) as d:
        d.update(fv_solution)
        
        
if __name__ == '__main__':
    main()
