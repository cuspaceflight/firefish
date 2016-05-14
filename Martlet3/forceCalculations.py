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

part_list = ['dart', 'core', 'fin1', 'fin2', 'fin3', 'fin4']
path_list = ['STLS/dart.stl', 'STLS/core.stl', 'STLS/fin1.stl', 'STLS/fin2.stl', 'STLS/fin3.stl', 'STLS/fin4.stl',] 
streamVelocity = 1
angle_of_attack = math.radians(10)
vy = streamVelocity * math.cos(angle_of_attack)
vx = streamVelocity * math.sin(angle_of_attack)

def main(case_dir='joinSTL', runRhoCentral = False):
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
	snap.distanceLevels = [6,5,4,2]
	snap.distanceRefinements = [0.005,0.01,0.03,0.1]
	snap.snap=True
	snap.snapTolerance = 8
	snap.edgeRefinementLevel = 7
	#############un-comment out the code snippet below if you want to apply extra refinement#########
	snap.locationToKeep = [0.0012,0.124,0.19] #odd numbers to ensure not on face
	snap.addLayers=True
	#we need to write fvSchemes and fvSolution to be able to use paraForm and run snappy?
	write_fv_schemes(case)
	write_fv_solution(case)
	write_thermophysical_properties(case)
	write_turbulence_properties(case)
	write_initial_conditions(case)
	snap.generate_mesh()
	getTrueMesh(case)
	if runRhoCentral:
		case.run_tool('rhoCentralFoam')
  
def getTrueMesh(case):
	#the proper mesh is in the final time directory, delete the one in constant
	os.chdir(case.root_dir_path)
	call (["rm", "-r", "constant/polyMesh"])
	call (["mv", "0.002/polyMesh", "constant/"])
	call (["rm", "-r", "0.001/"])
	call (["rm", "-r", "0.002/"])
	os.chdir("../")

def create_new_case(case_dir):
	"""Creates new case directory"""
	# Check that the specified case directory does not already exist
	if os.path.exists(case_dir):
		call(["rm", "-r", "snappy"])
		#raise RuntimeError(    
		#    'Refusing to write to existing path: {}'.format(case_dir)
		#)

	# Create the case
	return Case(case_dir)

def write_control_dict(case):
	"""Sets up the control dictionary.
	In this example we use the rhoCentralFoam compressible solver"""

	# Control dict from tutorial
	control_dict = {
		'application': 'rhoCentralFoam',
		'startFrom': 'startTime',
		'startTime': 0,
		'stopAt': 'endTime',
		'endTime': 5,
		'deltaT': 0.000015,
		'writeControl': 'runTime',
		'writeInterval': 1,
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
			#whole
			'forces1':{
				'type': 'forces',
				'functionObjectLibs' : ['"libforces.so"'],
				'patches':part_list[0:1],
				'rhoName': 'rhoInf',
				'rhoInf':4.7,
				'CofR':[0, 0, 0],
			},
			##core
			#'forces2':{
			#	'type': 'forces',
			#	'functionObjectLibs' : ['"libforces.so"'],
			#	'patches':part_list[1:2],
			#	'rhoName': 'rhoInf',
			#	'rhoInf':4.7,
			#	'CofR':[0, 0, 0],
			#},
			##fin
			#'forces3':{
			#	'type': 'forces',
			#	'functionObjectLibs' : ['"libforces.so"'],
			#	'patches':part_list[2:3],
			#	'rhoName': 'rhoInf',
			#	'rhoInf':4.7,
			#	'CofR':[0, 0, 0],
			#},
		}
	}

	with case.mutable_data_file(FileName.CONTROL) as d:
		d.update(control_dict)
		
def make_block_mesh(case):
	"""Creates a block mesh to bound the geometry"""
	block_mesh_dict = {

		'vertices': [
			[-3, -1.5, -3], [3.25, -1.5, -3], [3.25, 3.5, -3], [-3, 3.5, -3],
			[-3, -1.5, 3.25], [3.25, -1.5, 3.25], [3.25, 3.5, 3.25], [-3, 3.5, 3.25],

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
		'solvers' : {'"(rho|rhoU|rhoE)"': {'solver' : 'diagonal'},
					 'U' : {'solver'  : 'smoothSolver',
							'smoother' : 'GaussSeidel',
							'nSweeps' : 2,
							'tolerance' : 1e-09,
							'relTol' : 0.01},
					 'h' : {'$U' : ' ',
							'tolerance' : 1e-10,
							'relTol' : 0}}}
	with case.mutable_data_file(FileName.FV_SOLUTION) as d:
		d.update(fv_solution)

def write_fv_schemes(case):
	"""Sets fv_schemes"""
	fv_schemes = {
		'ddtSchemes'  : {'default' : 'Euler'},
		'gradSchemes' : {'default' : 'Gauss linear'},
		'divSchemes'  : {'default' : 'none', 'div(tauMC)' : 'Gauss linear'},
		'laplacianSchemes' : {'default' : 'Gauss linear corrected'},
		'interpolationSchemes' : {'default' : 'linear',
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
					  'transport' : {'mu' : 0, 'Pr' : 1}}}
	with case.mutable_data_file(FileName.THERMOPHYSICAL_PROPERTIES) as d:
		d.update(thermo_dict)

def write_turbulence_properties(case):
	"""Disables the turbulent solver"""
	turbulence_dict = {
		'simulationType' : 'laminar'}
	with case.mutable_data_file(FileName.TURBULENCE_PROPERTIES) as d:
		d.update(turbulence_dict)

def write_decompose_settings(case):
	"""writes settings for splitting the task into different processors"""
	#number of domains should equal number of computers
	 decomposepar_dict = {
	 	'startTime': 0,
	 	'method': 'scotch',
	 	'distributed' : 'no',
	 	'roots' : [],
	 }

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

if __name__ == '__main__':
	main()