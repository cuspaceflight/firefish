"""This module provides tools for building and running SnappyHexMesh

"""
from firefish.case import FileName


class SnappyHexMesh(object):
	"""Encapsulates all the snappyHexMesh settings"""
	# pylint: disable=too-many-instance-attributes
	def __init__(self, geom, surfaceRefinement, case):
		"""Creates a Snappy Hex Mesh object with default settings and given
		refinement at surface

		Args:
			geom (firefish.geometry.Geometry): representation of geometry to mesh
			surfaceRefinement: level of refinement at the surface
			case (firefish.case.Case): the case to run SHM from
		"""

		self.geom = geom
		self.surfaceRefinement = surfaceRefinement
		self.case = case
		#we set up the default settings for snappy
		self.castellate = True
		self.snap = True
		self.addLayers = True
		self.maxLocalCells = 1000000
		self.maxGlobalCells = 200000
		self.minRefinementCells = 200
		self.maxLoadUnbalance = 0.1
		self.nCellsBetweenLevels = 3
		self.edgeRefinementLevel = 6
		self.refinementSurfaceMin = 5
		self.refinementSurfaceMax = 6
		self.resolveFeatureAngle = 30
		self.distanceRefinements = [0.1, 0.2]
		self.distanceLevels = [4, 3]
		self.locationToKeep = [0.001, 0.001, 0.0015]
		self.allowFreeStandingFaces = True
		self.nSmoothPatch = 3
		self.snapTolerance = 2
		self.nSolveIter = 30
		self.nRelaxIter = 5
		self.nFeatureSnapIter = 10
		self.implicitFeatureSnap = False
		self.explicitFeatureSnap = True
		self.multiRegionFeatureSnap = False
		self.relativeSizes = True
		self.nSurfaceLayers = 1
		self.expansionRatio = 1
		self.finalLayerThickness = 0.1
		self.minThickness = 0.1
		self.nGrow = 0
		self.featureAngle = 60
		self.slipFeatureAngle = 30
		self.nRelaxIter = 3
		self.nSmoothSurfaceNormals = 1
		self.nSmoothNormals = 1
		self.nSmoothThickness = 10
		self.maxFaceThicknessratio = 0.5
		self.maxThicknessToMedialRatio = 0.3
		self.minMedianAxisAngle = 90
		self.nBufferCellsNoExtrude = 0
		self.nLayerIter = 50
		self.mergeTolerance = 1e-6

	def write_snappy_dict(self):
		"""Writes the SHM dictionary

		.. note::
			This is called by SnappyHexMesh when it generates the mesh
		"""
		snappy_dict = {
			'castellatedMesh' : self.castellate,
			'snap' : self.snap,
			'addLayers' : self.addLayers,
			'geometry' : {
				self.geom.filename : {
					'type' : 'triSurfaceMesh'},
				},
			'castellatedMeshControls' : {
				'maxLocalCells' : self.maxLocalCells,
				'maxGlobalCells' : self.maxGlobalCells,
				'minRefinementCells' : self.minRefinementCells,
				'maxLoadUnbalance' : self.maxLoadUnbalance,
				'nCellsBetweenLevels' : self.nCellsBetweenLevels,
				'features' : [{'file' : '"{}.eMesh"'.format(self.geom.name),
							   'level' : self.surfaceRefinement}],
				'refinementSurfaces' : {self.geom.filename : {
					'level' : [self.refinementSurfaceMin, self.refinementSurfaceMax]}},
				'resolveFeatureAngle' : self.resolveFeatureAngle,
				'refinementRegions' : {self.geom.filename :
									   {'mode' : 'distance',
										'levels' :([[(self.distanceRefinements[x],\
													  self.distanceLevels[x])] for x in\
													range(len(self.distanceRefinements))])}},
				'locationInMesh' : self.locationToKeep,
				'allowFreeStandingZoneFaces' : self.allowFreeStandingFaces
				},
			'snapControls' :
			{
				'nSmoothPatch' : self.nSmoothPatch,
				'tolerance' : self.snapTolerance,
				'nRelaxIter' : self.nRelaxIter,
				'nSolveIter' : self.nSolveIter,
				'nFeatureSnapIter' : self.nFeatureSnapIter,
				'implicitFeatureSnap' : self.implicitFeatureSnap,
				'explicitFeatureSnap' : self.explicitFeatureSnap,
				'multiRegionFeatureSnap' : self.multiRegionFeatureSnap,
				},
			'addLayersControls' :
			{
				'relativeSizes' : self.relativeSizes,
				'layers' : {self.geom.filename : {'nSurfaceLayers' : self.nSurfaceLayers}},
				'expansionRatio' : self.expansionRatio,
				'finalLayerThickness' : self.finalLayerThickness,
				'minThickness' : self.minThickness,
				'nGrow' : self.nGrow,
				'featureAngle' : self.featureAngle,
				'slipFeatureAngle' : self.slipFeatureAngle,
				'nRelaxIter' : self.nRelaxIter,
				'nSmoothSurfaceNormals' : self.nSmoothSurfaceNormals,
				'nSmoothNormals' : self.nSmoothNormals,
				'nSmoothThickness' : self.nSmoothThickness,
				'maxFaceThicknessRatio' : self.maxFaceThicknessratio,
				'maxThicknessToMedialRatio' : self.maxThicknessToMedialRatio,
				'minMedianAxisAngle' : self.minMedianAxisAngle,
				'nBufferCellsNoExtrude' : self.nBufferCellsNoExtrude,
				'nLayerIter' : self.nLayerIter
				},
			'meshQualityControls' :
			{
				'#include' : '"meshQualityDict"'
				},
			'mergeTolerance' : self.mergeTolerance
			}
		with self.case.mutable_data_file(FileName.SNAPPY_HEX_MESH) as d:
			d.update(snappy_dict)

	def write_snappy_dict_multipart(self, part_list):
		"""Writes the SHM dictionary

		.. note::
			This is called by SnappyHexMesh when it generates the mesh
		"""
		feature_list = []
		refinement_surface_dict = {}
		layer_dict = {}
		geom_dict = {}

		for part in part_list:
			geom = {'"{}.stl"'.format(part) : {'type':'triSurfaceMesh', 'name':part}}
			geom_dict.update(geom)

			file_dict = {'file' : '"{}.eMesh"'.format(part),
						'level' : self.surfaceRefinement}
			feature_list.append(file_dict)

			refinement_surface = {part : {
								 'level' : [self.refinementSurfaceMin, self.refinementSurfaceMax]}}
			refinement_surface_dict.update(refinement_surface)

			layer = {part : {'nSurfaceLayers' : self.nSurfaceLayers}}
			layer_dict.update(layer)

		snappy_dict = {

			'castellatedMesh' : self.castellate,
			'snap' : self.snap,
			'addLayers' : self.addLayers,
			'geometry' :geom_dict,
			'castellatedMeshControls' : {
				'maxLocalCells' : self.maxLocalCells,
				'maxGlobalCells' : self.maxGlobalCells,
				'minRefinementCells' : self.minRefinementCells,
				'maxLoadUnbalance' : self.maxLoadUnbalance,
				'nCellsBetweenLevels' : self.nCellsBetweenLevels,
				'features' : feature_list,
				'refinementSurfaces': refinement_surface_dict,
				'resolveFeatureAngle' : self.resolveFeatureAngle,
				'refinementRegions' : {part_list[0] :
									   {'mode' : 'distance',
										'levels' :([[(self.distanceRefinements[x],\
													  self.distanceLevels[x])] for x in\
													range(len(self.distanceRefinements))])}},
				'locationInMesh' : self.locationToKeep,
				'allowFreeStandingZoneFaces' : self.allowFreeStandingFaces
				},
			'snapControls' :
			{
				'nSmoothPatch' : self.nSmoothPatch,
				'tolerance' : self.snapTolerance,
				'nRelaxIter' : self.nRelaxIter,
				'nSolveIter' : self.nSolveIter,
				'nFeatureSnapIter' : self.nFeatureSnapIter,
				'implicitFeatureSnap' : self.implicitFeatureSnap,
				'explicitFeatureSnap' : self.explicitFeatureSnap,
				'multiRegionFeatureSnap' : self.multiRegionFeatureSnap,
				},
			'addLayersControls' :
			{
				'relativeSizes' : self.relativeSizes,
				'expansionRatio' : self.expansionRatio,
				'finalLayerThickness' : self.finalLayerThickness,
				'minThickness' : self.minThickness,
				'nGrow' : self.nGrow,
				'layers': layer_dict,
				'featureAngle' : self.featureAngle,
				'slipFeatureAngle' : self.slipFeatureAngle,
				'nRelaxIter' : self.nRelaxIter,
				'nSmoothSurfaceNormals' : self.nSmoothSurfaceNormals,
				'nSmoothNormals' : self.nSmoothNormals,
				'nSmoothThickness' : self.nSmoothThickness,
				'maxFaceThicknessRatio' : self.maxFaceThicknessratio,
				'maxThicknessToMedialRatio' : self.maxThicknessToMedialRatio,
				'minMedianAxisAngle' : self.minMedianAxisAngle,
				'nBufferCellsNoExtrude' : self.nBufferCellsNoExtrude,
				'nLayerIter' : self.nLayerIter
				},
			'meshQualityControls' :
			{
				'#include' : '"meshQualityDict"'
				},
			'mergeTolerance' : self.mergeTolerance
			}
		with self.case.mutable_data_file(FileName.SNAPPY_HEX_MESH) as d:
			d.update(snappy_dict)


	def generate_mesh(self):
		"""Generates the mesh

		.. note::

			This extracts surface features, writes the main SHM dict, a mesh quality dict and then
			runs SHM.
			We assume that an underlying block mesh has already been produced
		"""
		self.geom.extract_features()
		self.geom.meshSettings.write_settings(self.case)
		self.write_snappy_dict()
		self.case.run_tool('snappyHexMesh')

	def generate_mesh_multipart(self, part_list):
		self.geom.add_features(part_list)
		self.geom.meshSettings.write_settings(self.case)
		self.write_snappy_dict_multipart(part_list)
		self.case.run_tool('snappyHexMesh')

	def add_mesh_features(self, file_list):
		"""test function which runs add_features in order to write the surfaceFeatureExtractDict"""
		self.geom.add_features(file_list)
