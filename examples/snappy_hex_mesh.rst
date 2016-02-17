.. This file is read by doc/examples.rst and inserted into the documentation. It
   lives here so that it is more clearly associated with
   snappy_hex_example.py. Note that file paths are, however, relative to
   the doc/ directory.
   
Snappy Hex Mesh Example
---------------------

The :download:`snappy_hex_example.py < ../examples/snappy_hex_mesh.py>`
script provides an example of running snappyHexMesh.

In order to be able to run snappyHexMesh we need to set up a control dictionary even though
it plays no part in the actual mesh generation process. Likewise, in order to use paraFoam, we need
to set up fvSchemes and fvSolution.

For snappyHexMesh to work we must have an underlying block mesh. This is generated in *make_block_mesh* and follows
the same procedure as in previous examples.

For the actual mesh generation we first of all load a geometry using the new Geometry class::

    rocket = Geometry(GeometryFormat.STL,'example.stl','example',case)

The idea behind this class is that, when we support more geometry file types in the future, it will abstract away
the need to worry about wether something is an STL or OBJ etc.

We next scale and translate the rocket::

    rocket.scale(0.5);
    rocket.translate([0.5,2,2])

The Geometry class also contains mesh quality settings for this particular geometry.

Now that the geometry has been loaded we use it to initialise the *SnappyHexMesh* class::

    snap = SnappyHexMesh(rocket,4,case)

This creates a new SnappyHexMesh class based on the example geometry and with a surface refinement level of 4.
The SnappyHexMesh class automatically sets the mesh generation settings to a set of default values. These can be altered::

    snap.snap=True
    snap.snapTolerance = 8;
    snap.locationToKeep = [0.0012,0.124,0.19]
    snap.addLayers=False
    
Once the mesh generator is set up we can make the mesh via the call::

    snap.generate_mesh()
    
Several things happen all at once here:
* Surface features are extracted from the geometry (saving the STL in the trisurfaces directory if it has not already done so)
* The mesh quality settings are written to a dictionary
* The snappyHexMesh dictionary is written using the attributes of the SnappyHexMesh class
* snappyHexMesh is run as a tool within the case directory

Once this has run the mesh can be viewed via *paraFoam*