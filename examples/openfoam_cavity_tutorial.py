"""
Example which re-creates the OpenFOAM cavity tutorial case.

>>> import os
>>> case_dir = os.path.join(getfixture('tmpdir').strpath, 'cavity')
>>> main(case_dir)
>>> os.path.isdir(os.path.join(case_dir, '0.5'))
True

"""
import os

from firefish.case import (
    Case, Dimension, FileName, FileClass
)

def main(case_dir='cavity'):
    # Create a new case file, raising RuntimeError if the directory already
    # exists.
    case = create_new_case(case_dir)

    # Add the information needed by blockMesh.
    write_initial_control_dict(case)
    write_block_mesh_dict(case)

    # At this point there is enough to run blockMesh.
    case.run_tool('blockMesh')

    # Update the physical properties.
    with case.mutable_data_file(FileName.TRANSPORT_PROPERTIES) as tp:
        tp['nu'] = (Dimension(0, 2, -1, 0, 0, 0, 0), 0.01)

    # Write the fvSolution and fvSchemes files.
    write_fv_solution(case)
    write_fv_schemes(case)

    # Write the initial conditions for the p and U fields.
    write_initial_conditions(case)

    # Run the icoFoam application.
    case.run_tool('icoFoam')

def create_new_case(case_dir):
    # Check that the specified case directory does not already exist
    if os.path.exists(case_dir):
        raise RuntimeError(
            'Refusing to write to existing path: {}'.format(case_dir)
        )

    # Create the case
    return Case(case_dir)

def write_initial_control_dict(case):
    # Control dict from tutorial
    control_dict = {
        'application': 'icoFoam',
        'startFrom': 'startTime',
        'startTime': 0,
        'stopAt': 'endTime',
        'endTime': 0.5,
        'deltaT': 0.005,
        'writeControl': 'timeStep',
        'writeInterval': 20,
        'purgeWrite': 0,
        'writeFormat': 'ascii',
        'writePrecision': 6,
        'writeCompression': 'off',
        'timeFormat': 'general',
        'timePrecision': 6,
        'runTimeModifiable': True,
    }

    with case.mutable_data_file(FileName.CONTROL) as d:
        d.update(control_dict)

def write_block_mesh_dict(case):
    block_mesh_dict = {
        'convertToMeters': 0.1,

        'vertices': [
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 0.1], [1, 0, 0.1], [1, 1, 0.1], [0, 1, 0.1],
        ],

        'blocks': [
            (
                'hex', [0, 1, 2, 3, 4, 5, 6, 7], [20, 20, 1],
                'simpleGrading', [1, 1, 1],
            )
        ],

        'edges': [],

        # Note the odd way in which boundary is defined here as a
        # list of tuples.
        'boundary': [
            ('movingWall', {
                'type': 'wall',
                'faces': [ [3, 7, 6, 2] ],
            }),
            ('fixedWalls', {
                'type': 'wall',
                'faces': [
                    [0, 4, 7, 3],
                    [2, 6, 5, 1],
                    [1, 5, 4, 0],
                ],
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

def write_fv_solution(case):
    fv_solution = {
        'solvers': {
            'p': {
                'solver': 'PCG',
                'preconditioner': 'DIC',
                'tolerance': 1e-6,
                'relTol': 0,
            },
            'U': {
                'solver': 'smoothSolver',
                'smoother': 'symGaussSeidel',
                'tolerance': 1e-5,
                'relTol': 0,
            },
        },
        'PISO': {
            'nCorrectors': 2,
            'nNonOrthogonalCorrectors': 0,
            'pRefCell': 0,
            'pRefValue': 0,
        }
    }

    with case.mutable_data_file(FileName.FV_SOLUTION) as d:
        d.update(fv_solution)

def write_fv_schemes(case):
    fv_schemes = {
        'ddtSchemes': { 'default': 'Euler' },
        'gradSchemes': { 'default': 'Gauss linear', 'grad(p)': 'Gauss linear' },
        'divSchemes': { 'div(phi,U)': 'Gauss linear', 'default': 'none' },
        'laplacianSchemes': { 'default': 'Gauss linear orthogonal' },
        'interpolationSchemes': { 'default': 'linear' },
        'snGradSchemes': { 'default': 'orthogonal' },
    }

    with case.mutable_data_file(FileName.FV_SCHEMES) as d:
        d.update(fv_schemes)

def write_initial_conditions(case):
    # Create the p initial conditions
    p_file = case.mutable_data_file(
        '0/p', create_class=FileClass.SCALAR_FIELD_3D
    )
    with p_file as p:
        p.update({
            'dimensions': Dimension(0, 2, -2, 0, 0, 0, 0),
            'internalField': ('uniform', 0),
            'boundaryField': {
                'movingWall': { 'type': 'zeroGradient' },
                'fixedWalls': { 'type': 'zeroGradient' },
                'frontAndBack': { 'type': 'empty' },
            },
        })

    # Create the U initial conditions
    U_file = case.mutable_data_file(
        '0/U', create_class=FileClass.VECTOR_FIELD_3D
    )
    with U_file as U:
        U.update({
            'dimensions': Dimension(0, 1, -1, 0, 0, 0, 0),
            'internalField': ('uniform', [0, 0, 0]),
            'boundaryField': {
                'movingWall': {
                    'type': 'fixedValue', 'value': ('uniform', [1, 0, 0])
                },
                'fixedWalls': {
                    'type': 'fixedValue', 'value': ('uniform', [0, 0, 0])
                },
                'frontAndBack': { 'type': 'empty' },
            },
        })

if __name__ == '__main__':
    main()
