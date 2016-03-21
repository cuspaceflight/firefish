"""
Example which demonstrates the use of SnappyHexMesh
"""
import os

from firefish.case import (
	Case, FileName, FileClass, Dimension)
from firefish.geometry import (
	Geometry,GeometryFormat)
from firefish.meshsnappy import SnappyHexMesh
from subprocess import call

part_list = ['nosecone', 'tube']	
streamVelocity = 10

def main(case_dir='snappy'):
	#Create a new case file, raise an error if the directory already exists
	case = create_new_case(case_dir)
	write_control_dict(case)
	#write the base block mesh
	make_block_mesh(case)
	rocket = Geometry(GeometryFormat.STL,'empty.stl','empty',case)
	snap = SnappyHexMesh(rocket,4,case)
	snap.snap=True
	snap.snapTolerance = 8;
	snap.locationToKeep = [0.0012,0.124,0.19] #odd numbers to ensure not on face
	snap.addLayers=False
	#we need to write fvSchemes and fvSolution to be able to use paraForm and run snappy?
	write_transport_properties(case)
	write_fv_schemes(case)
	write_fv_solution(case)
	write_initial_conditions(case)
	snap.generate_mesh_multipart(part_list)
	#the proper mesh is in the final time directory, delete the one in constant
	#call (["cd", "snappy"], shell = True)
	#call (["rm", "-r", "constant/polyMesh"], shell = True)
	#call (["mv", "0.05/polyMesh", "constant/"], shell = True)
	#call (["rm -r 0.*"], shell = True)
	#case.run_tool('icoFoam')

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
	"""Sets up a token control dictionary"""
	#This is a token control dict needed in order to get everything to run
	control_dict = {
		'application': 'icoFoam',
		'startFrom': 'startTime',
		'startTime': 0,
		'stopAt': 'endTime',
		'endTime': 1.2,
		'deltaT': 0.02,
		'writeControl': 'timeStep',
		'writeInterval': 2,
		'purgeWrite': 0,
		'writeFormat': 'ascii',
		'writePrecision': 6,
		'writeCompression': 'off',
		'timeFormat': 'general',
		'timePrecision': 6,
		'runTimeModifiable': True
	}

	with case.mutable_data_file(FileName.CONTROL) as d:
		d.update(control_dict)

def make_block_mesh(case):
	"""Creates a block mesh to bound the geometry"""
	block_mesh_dict = {

		'vertices': [
			[-0.3, -1, -1], [3, -1, -1], [3, 1, -1], [-0.3, 1, -1],
			[-0.3, -1, 1], [3, -1, 1], [3, 1, 1], [-0.3, 1, 1],
		],

		'blocks': [
			(
				'hex', [0, 1, 2, 3, 4, 5, 6, 7], [30, 30, 30],
				'simpleGrading', [1, 1, 1],
			)
		],

		'edges': [],

		# Note the odd way in which boundary is defined here as a
		# list of tuples.
		'boundary': [
			('inlet', {
				'type': 'inlet',
				'faces': [ [0, 3, 4, 7] ],
			}),
			('outlet', {
				'type': 'outlet',
				'faces': [ [2, 6, 5, 1] ],
			}),
			('fixedWalls', {
				'type': 'wall',
				'faces': [
					[4, 7, 6, 5],
					[7, 6, 3, 2],
					[0, 3, 2, 1],
					[4, 5, 0, 1],
				],
			})
		],

		'mergePatchPairs': [],
	}

	with case.mutable_data_file(FileName.BLOCK_MESH) as d:
		d.update(block_mesh_dict)

	case.run_tool('blockMesh')

def write_transport_properties(case):
	with case.mutable_data_file(FileName.TRANSPORT_PROPERTIES) as tp:
		tp['nu'] = (Dimension(0, 2, -1, 0, 0, 0, 0), 0.01)

def write_fv_solution(case):
	"""Creates a default fvSolution dictionary so SHM can run"""
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
	"""Creates a default fvSchemes dictionary so SHM can run"""
	#needed so we can view it in paraFoam
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
		'inlet' : {'type' : 'zeroGradient'},
		'outlet': {'type': 'zeroGradient'},
		'fixedWalls': {'type': 'zeroGradient'}
	}
	boundaryDict.update(partBoundaries)

	with p_file as p:
		p.update({
			'dimensions': Dimension(0, 2, -2, 0, 0, 0, 0),
			'internalField': ('uniform', 0),
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
				   'value' : ('uniform', [streamVelocity, 0, 0])},
		'outlet': {
			'type' : 'fixedValue',
				   'value' : ('uniform', [streamVelocity, 0, 0])},
		'fixedWalls': {
			'type': 'zeroGradient'
		}
	}
	boundaryDict.update(partVelocities)
	with U_file as U:
		U.update({
			'dimensions': Dimension(0, 1, -1, 0, 0, 0, 0),
			'internalField': ('uniform', [streamVelocity, 0, 0]),
			'boundaryField': boundaryDict
		})

if __name__ == '__main__':
	main()