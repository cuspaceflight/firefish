"""
Example which demonstrates the use of SnappyHexMesh
"""
import os

from firefish.case import (
	Case, FileName)
from firefish.geometry import (
	Geometry,GeometryFormat)
from firefish.meshsnappy import SnappyHexMesh

def main(case_dir='snappy'):
	#Create a new case file, raise an error if the directory already exists
	case = create_new_case(case_dir)
	write_control_dict(case)
	#write the base block mesh
	make_block_mesh(case)

	rocket = Geometry(GeometryFormat.STL,'whole.stl','whole',case)
	snap = SnappyHexMesh(rocket,4,case)
	snap.snap=True
	snap.snapTolerance = 8;
	snap.locationToKeep = [0.0012,0.124,0.19] #odd numbers to ensure not on face
	snap.addLayers=False
	#we need to write fvSchemes and fvSolution to be able to use paraForm and run snappy?
	write_fv_schemes(case)
	write_fv_solution(case)
	part_list = ['nosecone', 'tube']
	snap.generate_mesh_multipart(part_list)

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

def make_block_mesh(case):
	"""Creates a block mesh to bound the geometry"""
	block_mesh_dict = {

		'vertices': [
			[-3, -1, -1], [3, -1, -1], [3, 1, -1], [-3, 1, -1],
			[-3, -1, 1], [3, -1, 1], [3, 1, 1], [-3, 1, 1],
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

	case.run_tool('blockMesh')

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

if __name__ == '__main__':
	main()