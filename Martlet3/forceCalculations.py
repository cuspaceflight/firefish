"""
Script to calculate the forces on: dart, core, and one of the fins (symmetrical given neutral angle
	of attack)
"""
import os, math

from firefish.case import (
	Case, FileName, FileClass, Dimension)
from firefish.geometry import (
	Geometry,GeometryFormat, load_multiple_geometries)
from firefish.meshsnappy import SnappyHexMesh
from subprocess import call

###simulation parameters#####
part_list = ['dart', 'core', 'boatTail', 'fin1', 'fin2', 'fin3', 'fin4']
path_list = ['STLS/dart.stl', 'STLS/core.stl', 'STLS/boatTail.stl', 'STLS/fin1.stl', 'STLS/fin2.stl', 'STLS/fin3.stl', 'STLS/fin4.stl'] 

timeStep = 1e-7
endTime = 0.10
interval = 10000*timeStep
processors = 4
streamVelocity = 4
angle_of_attack = math.radians(0)
vy = streamVelocity * math.cos(angle_of_attack)
vx = streamVelocity * math.sin(angle_of_attack)
#####simulation parameters#######

def main(case_dir='turblenceTest', runRhoCentral = False, parallel = True):
	#Create a new case file, raise an error if the directory already exists
	case = create_new_case(case_dir)
	write_control_dict(case)
	#write the base block mesh
	make_block_mesh(case)
	parts = load_multiple_geometries(GeometryFormat.STL,path_list,part_list,case)
	snap = SnappyHexMesh(parts,4,case)
	###############un-comment out the code snippet below if you want to apply extra refinement#########
	snap.refinementSurfaceMin =7
	snap.maxGlobalCells=100000000
	snap.refinementSurfaceMax =8
	snap.distanceLevels = [7,6,4,2]
	snap.distanceRefinements = [0.010,0.020,0.06,0.2]
	snap.snap=True
	snap.snapTolerance = 8
	snap.edgeRefinementLevel = 8
	#############un-comment out the code snippet below if you want to apply extra refinement#########
	snap.locationToKeep = [0.0012,0.124,0.19] #odd numbers to ensure not on face
	snap.addLayers=False
	#we need to write fvSchemes and fvSolution to be able to use paraForm and run snappy?
	write_fv_schemes(case)
	write_fv_solution(case)
	write_thermophysical_properties(case)
	write_turbulence_properties(case)
	write_initial_conditions(case)
	write_decompose_settings(case, processors, "simple")
	snap.generate_mesh()
#	#getTrueMesh(case)
#	if runRhoCentral:
#		if parallel:
#  			case.run_tool('decomposePar')
#			case.run_tool('mpirun', '-np 4 rhoCentralFoam -parallel')
#  		else:
#  			case.run_tool('rhoCentralFoam')

def getTrueMesh(case):
	#the proper mesh is in the final time directory, delete the one in constant
	os.chdir(case.root_dir_path)
	call (["rm", "-r", "constant/polyMesh"])
	call (["mv", "{0}/polyMesh".format(2*timeStep), "constant/"])
	call (["rm", "-r", "{0}/".format(timeStep)])
	call (["rm", "-r", "{0}".format(2*timeStep)])
	os.chdir("../")

def create_new_case(case_dir):
	"""Creates new case directory"""
	# Check that the specified case directory does not already exist
	if os.path.exists(case_dir):
		raise RuntimeError(    
			'Refusing to write to existing path: {}'.format(case_dir)
		)

	# Create the case
	return Case(case_dir)

def write_control_dict(case):
	"""Sets up the control dictionary.
	In this example we use the rhoCentralFoam compressible solver"""

	# Control dict from tutorial
	control_dict = {
		'application': 'rhoCentralFoam',
		'startFrom': 'latestTime',
		'startTime': 0,
		'stopAt': 'endTime',
		'endTime': endTime,
		'deltaT': timeStep,
		'writeControl': 'runTime',
		'writeInterval': interval,
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
		#function objects for calculating drag coefficients with the simulation
		#forces given in body co-ordinates
		'functions': {
			#dart
			'forcesDart':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[0:1],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			##core
			'forcesCore':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[1:2],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			#fin
			'forcesboatTail':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[2:3],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			#fin
			'forcesFin1':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[3:4],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			#fin
			'forcesFin2':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[4:5],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			#fin
			'forcesFin3':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[5:6],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			#fin
			'forcesFin4':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[6:7],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
		}
	}

	with case.mutable_data_file(FileName.CONTROL) as d:
		d.update(control_dict)
		
def make_block_mesh(case):
	"""Creates a block mesh to bound the geometry"""
	block_mesh_dict = {

		'vertices': [
			[-4.858, -3.5, -4.859], [5.142, -3.5, -4.859], [5.142, 6.5, -4.859], [-4.858, 6.5, -4.859],
			[-4.858, -3.5, 5.141], [5.142, -3.5, 5.141], [5.142, 6.5, 5.141], [-4.858, 6.5, 5.141],

		],

		'blocks': [
			(
				'hex', [0, 1, 2, 3, 4, 5, 6, 7], [20, 20, 20],
				'simpleGrading', [1, 1, 1],
			)
		],

		'edges': [],

		# Note the odd way in which boundary is defined here as a
		# list of tuples.
		'boundary': [
			('inlet', {
				'type': 'inlet',
				'faces': [ [7, 6, 3, 2] ],
			}),
			('outlet', {
				'type': 'outlet',
				'faces': [ [4, 5, 0, 1] ],
			}),
			('fixedWalls', {
				'type': 'wall',
				'faces': [
					[0, 3, 2, 1],
					[4, 7, 5, 6],
					[0, 3, 4, 7],
					[2, 6, 5, 1],
				],
			})
		],

		'mergePatchPairs': [],
	}

	with case.mutable_data_file(FileName.BLOCK_MESH) as d:
		d.update(block_mesh_dict)

	case.run_tool('blockMesh')
	
def write_fv_solution(case):
	"""Sets fv_solution"""
	fv_solution = {
		'solvers' : {
			'"(rho|rhoU|rhoE)"': {'solver' : 'diagonal'},
			'U' : {
				'solver'  : 'smoothSolver',
				'smoother' : 'GaussSeidel',
				'nSweeps' : 2,
				'tolerance' : 1e-09,
				'relTol' : 0.01
			},
			'"(h|e)"' : {
				'$U' : ' ',
				'tolerance' : 1e-10,
				'relTol' : 0
			},
			'k' : {
				'solver' : 'PBiCG',
				'preconditioner': 'DILU',
				'tolerance': 1e-05,
				'relTol' : 0.1				
			},
			'epsilon' : {
				'solver' : 'PBiCG',
				'preconditioner': 'DILU',
				'tolerance': 1e-05,
				'relTol' : 0.1				
			}			
		}
	}
	with case.mutable_data_file(FileName.FV_SOLUTION) as d:
		d.update(fv_solution)

def write_fv_schemes(case):
	"""Sets fv_schemes"""
	fv_schemes = {
		'ddtSchemes'  : {'default' : 'Euler'},
		'gradSchemes' : {'default' : 'leastSquares'},
		'divSchemes'  : {
			'default' : 'Gauss skewCorrected', 
			'div(tauMC)' : 'Gauss linear',
			'div(phi,U)'   :   'bounded Gauss upwind',
			'div(phi,k)'   :   'bounded Gauss upwind',
			'div(phi,epsilon)' : 'bounded Gauss upwind',
			'div(phi,R)'   :   'bounded Gauss upwind',
			'div(R)'       :   'Gauss linear',
			'div(phi,nuTilda)' : 'bounded Gauss upwind',
			'div((nuEff*dev(T(grad(U)))))' : 'Gauss linear'
		},
		'laplacianSchemes' : {'default' : 'Gauss linear corrected'},
		'interpolationSchemes' : {'default' : 'linear skewCorrected',
								  'reconstruct(rho)' : 'vanLeer',
								  'reconstruct(U)' : 'vanLeerV',
								  'reconstruct(T)': 'vanLeer'},
		'snGradSchemes' : {'default': 'corrected'}}
	
	with case.mutable_data_file(FileName.FV_SCHEMES) as d:
		d.update(fv_schemes)

def write_thermophysical_properties(case):
	"""Sets the thermdynamic properties of the gas.
	These are chosen such that at a temperature of 1K the speed of sound is
	1m/s"""
	thermo_dict = {
		'thermoType' : {'type' : 'hePsiThermo', 'mixture' : 'pureMixture',
						'transport' : 'const', 'thermo'  : 'hConst',
						'equationOfState' : 'perfectGas', 'specie' : 'specie',
						'energy' : 'sensibleInternalEnergy'},
		'mixture' : {'specie' : {'nMoles' : 1, 'molWeight' : 11640.3},
					  'thermodynamics' : {'Cp' : 2.5, 'Hf' : 0},
					  'transport' : {'mu' : 5.45e-08, 'Pr' : 1}}}
	
	with case.mutable_data_file(FileName.THERMOPHYSICAL_PROPERTIES) as d:
		d.update(thermo_dict)

def write_turbulence_properties(case):
	"""Disables the turbulent solver"""
	turbulence_dict = {
		'simulationType' : 'RAS',
		'RAS' : {
			'RASModel' : 'kEpsilon',
			'turbulence' : 'on',
			'printCoeffs' : 'on'
		}
	}
	
	with case.mutable_data_file(FileName.TURBULENCE_PROPERTIES) as d:
		d.update(turbulence_dict)

def write_decompose_settings(case, processors, scheme):
	"""writes settings for splitting the task into different processors"""
	#number of domains should equal number of computers
	decomposepar_dict = {
		'numberOfSubdomains': processors,
		'distributed' : 'no',
		'roots' : [],
	}
	if scheme == "scotch":	
		decomposepar_dict.update({'method': 'scotch'})
	if scheme == "simple":
		decomposepar_dict.update({'method' : 'simple'})
		simpleCoeffs = {
			'simpleCoeffs' : {'n' : "(2 1 2)", 'delta' : 0.001}
		}
		decomposepar_dict.update(simpleCoeffs)
	with case.mutable_data_file(FileName.DECOMPOSE) as d:
		d.update(decomposepar_dict)

def write_initial_conditions(case):
	"""Sets the initial conditions"""
	# Create the p initial conditions
	p_file = case.mutable_data_file(
		'0/p', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {part:{'type':'zeroGradient'}}
		partBoundaries.update(partDict)
	boundaryDict = {
		'inlet' : {'type' : 'fixedValue', 'value' : 'uniform 1'},
		'outlet': {'type': 'zeroGradient'},
		'fixedWalls': {'type': 'zeroGradient'}
	}
	boundaryDict.update(partBoundaries)
	with p_file as p:
		p.update({
			'dimensions': Dimension(1, -1, -2, 0, 0, 0, 0),
			'internalField': ('uniform', 1),
			'boundaryField':boundaryDict
		})
	# Create the U initial conditions
	U_file = case.mutable_data_file(
		'0/U', create_class=FileClass.VECTOR_FIELD_3D
	)
	partVelocities = {}
	for part in part_list:
		partDict = {part:{'type':'slip'}}
		partVelocities.update(partDict)
	boundaryDict = {
		'inlet' : {'type' : 'fixedValue',
				   'value' : ('uniform', [-vx, -vy, 0])},
		'outlet': {
			'type' : 'zeroGradient'
		},
		'fixedWalls': {
			'type': 'zeroGradient'
		}
	}
	boundaryDict.update(partVelocities)
	with U_file as U:
		U.update({
			'dimensions': Dimension(0, 1, -1, 0, 0, 0, 0),
			'internalField': ('uniform', [-vx, -vy, 0]),
			'boundaryField': boundaryDict
		})
	#write T boundary conditions
	T_file = case.mutable_data_file(
		'0/T', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {part:{'type':'zeroGradient'}}
		partBoundaries.update(partDict)

	boundaryDict = {
		'inlet' : {'type' : 'fixedValue', 'value' : ('uniform 1')},
		'outlet': {'type': 'zeroGradient'},
		'fixedWalls': {'type': 'zeroGradient'}
	}
	boundaryDict.update(partBoundaries)
	with T_file as T:
		T.update({
			'dimensions': Dimension(0, 0, 0, 1, 0, 0, 0),
			'internalField': ('uniform', 1),
			'boundaryField': boundaryDict
		})
	#write k boundary conditions
	K_file = case.mutable_data_file(
		'0/k', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {part:{'type':'kqRWallFunction', 'value':('uniform 0.0503')}}
		partBoundaries.update(partDict)

	boundaryDict = {
		'inlet' : {'type' : 'fixedValue', 'value' : ('uniform 0.0503')},
		'outlet': {'type': 'zeroGradient'},
		'fixedWalls': {'type': 'zeroGradient'}
	}
	boundaryDict.update(partBoundaries)
	with K_file as K:
		K.update({
			'dimensions': Dimension(0, 2, -2, 0, 0, 0, 0),
			'internalField': ('uniform', 0.0503),
			'boundaryField': boundaryDict
		})
	#write epsilon boundary conditions
	EPSILON_file = case.mutable_data_file(
		'0/epsilon', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {part:{'type':'epsilonWallFunctions', 'value':('uniform 2.67')}}
		partBoundaries.update(partDict)

	boundaryDict = {
		'inlet' : {'type' : 'fixedValue', 'value' : ('uniform 2.67')},
		'outlet': {'type': 'zeroGradient'},
		'fixedWalls': {'type': 'zeroGradient'}
	}
	boundaryDict.update(partBoundaries)
	with EPSILON_file as EPSILON:
		EPSILON.update({
			'dimensions': Dimension(0, 2, -3, 0, 0, 0, 0),
			'internalField': ('uniform', 2.67),
			'boundaryField': boundaryDict
		})
	#write turbulent viscosity (nut) boundary conditions
	NUT_file = case.mutable_data_file(
		'0/nut', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {part:{'type':'nutkWallFunction', 'value':('uniform 0')}}
		partBoundaries.update(partDict)
	boundaryDict = {
		'inlet' : {'type' : 'calculated', 'value' : ('uniform 0')},
		'outlet' : {'type' : 'calculated', 'value' : ('uniform 0')},
		'fixedWalls' : {'type' : 'calculated', 'value' : ('uniform 0')},
	}
	boundaryDict.update(partBoundaries)
	with NUT_file as NUT:
		NUT.update({
			'dimensions': Dimension(0, 2, -1, 0, 0, 0, 0),
			'internalField': ('uniform', 0),
			'boundaryField': boundaryDict
		})
	
	#write alphat boundary conditions
	ALPHAT_file = case.mutable_data_file(
		'0/alphat', create_class=FileClass.SCALAR_FIELD_3D
	)
	partBoundaries = {}
	for part in part_list:
		partDict = {
					part:{
						'type':'compressible::alphatWallFunction', 
						'value':('uniform 0'), 
						'Prt' : 0.85}
					}
		partBoundaries.update(partDict)
	boundaryDict = {
		'inlet' : {'type' : 'calculated', 'value' : ('uniform 0')},
		'outlet' : {'type' : 'calculated', 'value' : ('uniform 0')},
		'fixedWalls' : {'type' : 'calculated', 'value' : ('uniform 0')},
	}
	boundaryDict.update(partBoundaries)
	with ALPHAT_file as ALPHAT:
		ALPHAT.update({
			'dimensions': Dimension(0, 1, -1, 0, 0, 0, 0),
			'internalField': ('uniform', 0),
			'boundaryField': boundaryDict
		})

if __name__ == '__main__':
	main()