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

Plan 27.12.15
Integrate drag coefficient calculation
Look into how to reduce computation time without compromising Courant number
Add U as a parameter into the initial conditions function, so that a suites of
tests can be run
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
    
    write_mirror_mesh_dict(case, [1, 0, 0])
    #mirror the quarter cylinder, need to run with -noFunctionObjects
    case.run_tool('mirrorMesh', '-noFunctionObjects')
    write_mirror_mesh_dict(case, [0, 1, 0])
    case.run_tool('mirrorMesh', '-noFunctionObjects')
    
    #we prepare the thermophysical and turbulence properties
    write_thermophysical_properties(case)
    write_turbulence_properties(case)
    #we write fvScheme and fvSolution
    write_fv_schemes(case)
    write_fv_solution(case)
    
    write_initial_conditions(case)
    case.run_tool('rhoCentralFoam')

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
        'endTime': 0.1,
        'deltaT': 0.00005,
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

        'functions': {
        	'forceCoefficients': {
        		'type' : 'forceCoeffs',
        		'functionObjectLibs' : ['"libforces.so"'],
        		'log' : 'yes',
        		'patches' : ['cylinder'],
        		'dragDir':  [1, 0, 0],
        		'liftDir': [0, 1, 0],
        		'pitchAxis': [0, 0, 1],
        		'magUInf': 300,
        		'lRef': 1,
        		'Aref': 1,

        		'rhoName': 'rhoInf',
        		'rhoInf': 1,
        		'origin': [0, 0, 0],
        		'coordinateRotation': {
        			'type':'EulerRotation',
        			'degrees': 'true',
        			'rotation': [0,0,0],
        		}

        	}
        }
    }

    with case.mutable_data_file(FileName.CONTROL) as d:
        d.update(control_dict)

def write_block_mesh_dict(case):
    """Writes the block mesh"""
    block_mesh_dict = {
  
        'convertToMeters': 10,

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
            'arc', (1, 2), [17.68, 17.68, 0],
            'arc', (5, 6), [17.68, 17.68, 0.05],
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

def write_mirror_mesh_dict(case, normalLine):
    """defines the axes for mirroring the quarter cylinder"""
    mirror_mesh_dict = {
        'planeType' : 'pointAndNormal',
        'pointAndNormalDict' : {'basePoint':[0,0,0], 'normalVector':normalLine},
        'planeTolerance' : 1e-06
        }

    with case.mutable_data_file(FileName.MIRROR_MESH) as d:
        d.update(mirror_mesh_dict)

def write_thermophysical_properties(case):
    """Sets the thermdynamic properties of the gas to match that of (dry) air"""
    thermo_dict = {
        'thermoType' : {'type' : 'hePsiThermo', 'mixture' : 'pureMixture',
                        'transport' : 'const', 'thermo'  : 'hConst',
                        'equationOfState' : 'perfectGas', 'specie' : 'specie',
                        'energy' : 'sensibleEnthalpy'},
        'mixture' : {'specie' : {'nMoles' : 1, 'molWeight' : 28.96},
                      'thermodynamics' : {'Cp' : 1004.5, 'Hf' : 2.544e+06},
                      'transport' : {'mu' : 1.8e-05, 'Pr' : 0.7}}}
    with case.mutable_data_file(FileName.THERMOPHYSICAL_PROPERTIES) as d:
        d.update(thermo_dict)

def write_turbulence_properties(case):
    """Use the Sparlart Allmaras turbulence model"""
    turbulence_dict = {
        'simulationType' : 'RAS',
        'RAS' : {'RASModel' : 'SpalartAllmaras', 'turbulence': 'on',
                 'printCoeffs' : 'on'}
        }
    with case.mutable_data_file(FileName.TURBULENCE_PROPERTIES) as d:
        d.update(turbulence_dict)

def write_fv_schemes(case):
    """Sets fv_schemes"""
    fv_schemes = {
        'fluxScheme' : 'Kurganov',
        'ddtSchemes'  : {'default' : 'Euler'},
        'gradSchemes' : {'default' : 'Gauss'},
        'divSchemes'  : {'default' : 'none', 'div(tauMC)' : 'Gauss linear',
                        'div(phi,U)': 'bounded Gauss linearUpwind grad(U)',
                        'div(phi,nuTilda)':'bounded Gauss linearUpwind gradu(nuTilda)',
                        'div((nuEff*dev2(T(grad(U)))))':'Gauss linear'},
        'laplacianSchemes' : {'default' : 'Gauss linear corrected'},
        'interpolationSchemes' : {'default' : 'linear',
                                  'reconstruct(rho)' : 'vanLeer',
                                  'reconstruct(U)' : 'vanLeerV',
                                  'reconstruct(T)': 'vanLeer'},
        'snGradSchemes' : {'default': 'corrected'},
        'wallDist' : {'method':'meshWave'}
    }
    with case.mutable_data_file(FileName.FV_SCHEMES) as d:
        d.update(fv_schemes)

def write_fv_solution(case):
    """Sets fv_solution"""
    fv_solution = {
        'solvers' : {'"(rho|rhoU|rhoE)"': {'solver' : 'diagonal'},
                     '"(U|e)"' : {'solver'  : 'smoothSolver',
                            'smoother' : 'GaussSeidel',
                            'nSweeps' : 2,
                            'tolerance' : 1e-09,
                            'relTol' : 0.01},
                     'h' : {'$U' : ' ',
                            'tolerance' : 1e-10,
                            'relTol' : 0},
                    'nuTilda': {'solver' : 'smoothSolver',
                                'smoother': 'GaussSeidel',
                                'nSweeps':2,
                                'tolerance':1e-08,
                                'relTol':0.1}
                    }
    }
    with case.mutable_data_file(FileName.FV_SOLUTION) as d:
        d.update(fv_solution)

def write_initial_conditions(case):
    """Sets the intial conditions"""
    #creates the p initial conditions
    p_file = case.mutable_data_file(
        '0/p', create_class = FileClass.SCALAR_FIELD_3D
    )
    with p_file as p:
        p.update({
            'dimensions': Dimension(1, -1, -2, 0, 0, 0, 0),
            'internalField': ('uniform', 100000),
            'boundaryField': {
                'cylinder' : {
                    'type' : 'zeroGradient'
                },
                'outerRim' : {
                    'type' : 'outletInlet',
                    'outletValue' : ('uniform', 100000)
                },
                'frontAndBack' : {
                    'type' : 'empty'
                },
            },
        })

    #create U initial conditions
    U_file = case.mutable_data_file(
        '0/U', create_class = FileClass.VECTOR_FIELD_3D
    )

    with U_file as U:
        U.update({
            'dimensions': Dimension(0, 1, -1, 0, 0, 0, 0),
            'internalField': ('uniform', [300, 0, 0]),
            'boundaryField': {
                'cylinder' : {
                    'type' : 'fixedValue',
                    'value' : ('uniform', [0, 0, 0] )
                },
                'outerRim' : {
                    'type' : 'inletOutlet',
                    'inletValue' : ('uniform', [300, 0, 0]),
                },
                'frontAndBack' : {
                    'type' : 'empty'
                },
            },
        })

    #create T initial conditions
    T_file = case.mutable_data_file(
        '0/T', create_class = FileClass.SCALAR_FIELD_3D        
    )

    with T_file as T:
        T.update({
            'dimensions': Dimension(0, 0, 0, 1, 0, 0, 0),
            'internalField' : ('uniform', 273),
            'boundaryField' : {
                'cylinder':{
                    'type' : 'zeroGradient'
                },
                'outerRim':{
                    'type' : 'zeroGradient'
                },
                'frontAndBack':{
                    'type' : 'empty'
                },
            },
        })

    nut_file = case.mutable_data_file(
        '0/nut', create_class = FileClass.SCALAR_FIELD_3D
    )

    with nut_file as nut:
        nut.update({
            'dimensions': Dimension(0, 2, -1, 0, 0, 0, 0),
            'internalField' : ('uniform', 0.14),
            'boundaryField' : {
                'cylinder':{
                    'type' : 'zeroGradient',
                    'value': ('uniform', 0.14)
                },
                'outerRim':{
                    'type' : 'freestream',
                    'freestreamValue' : ('uniform', 0.14)
                },
                'frontAndBack':{
                    'type' : 'empty'
                },
            },
        })

    nuTilda_file = case.mutable_data_file(
        '0/nuTilda', create_class = FileClass.SCALAR_FIELD_3D
    )
    
    with nuTilda_file as nuTilda:
        nuTilda.update({
            'dimensions': Dimension(0, 2, -1, 0, 0, 0, 0),
            'internalField' : ('uniform', 0.14),
            'boundaryField' : {
                'cylinder':{
                    'type' : 'zeroGradient',
                    'value': ('uniform', 0)
                },
                'outerRim':{
                    'type' : 'freestream',
                    'freestreamValue' : ('uniform', 0.14)
                },
                'frontAndBack':{
                    'type' : 'empty'
                },
            },
        })

    alphat_file = case.mutable_data_file(
        '0/alphat', create_class = FileClass.SCALAR_FIELD_3D
    )

    with alphat_file as alphat:
        alphat.update({
            'dimensions': Dimension(1, -1, -1, 0, 0, 0, 0),
            'internalField' : ('uniform', 0),
            'boundaryField' : {
                'cylinder':{
                    'type' : 'calculated',
                    'value': ('uniform', 0)
                },
                'outerRim':{
                    'type' : 'calculated',
                    'freestreamValue' : ('uniform', 0)
                },
                'frontAndBack':{
                    'type' : 'empty'
                },
            },
        })

if __name__ == '__main__':
    main()
