.. This file is read by doc/examples.rst and inserted into the documentation. It
   lives here so that it is more clearly associated with
   snappy_hex_example.py. Note that file paths are, however, relative to
   the doc/ directory.

Join STL Example
--------------------------

The :download:`join_stl_example.py <../examples/join_stl_example.py>` script
provides an example of combining multiple STL files into a single geometry and then
generating a mesh through snappyHexMesh. It is worth having a look at 
:download:`snappy_hex_example.py <../examples/snappy_hex_example.py>` first in order to 
get a more detailed overview on how SnappyHexMesh works.

It is now very straightforwards to generate a mesh made up from multiple *.STL* files.

Firstly one needs to make a list containing the paths of each STL file::

    path_list = ['STLS/nosecone.stl', 'STLS/upperTube.stl', 'STLS/lowerTube.stl', 'STLS/finCan.stl', 'STLS/tail.stl']

One then needs to make a list of the human-readable names that correspond to each file::

    part_list = ['nosecone', 'upperTube', 'lowerTube', 'finCan', 'tail']
    
When examining the mesh in paraFoam or when getting force outputs it will be these names that appear.

Once this has been done the Geometry classes can be loaded by a single call of::

    parts = load_multiple_geometries(GeometryFormat.STL,path_list,part_list,case)
    
This produces a list of *firefish.geometry.Geometry* objects which can scaled, translated
and rotated independently as required using the normal geometry functions.

We now use this list of Geometry objects to initialise SnappyHexMesh::

    snap = SnappyHexMesh(parts,4,case)
    
As in :download:`snappy_hex_example.py <../examples/snappy_hex_example.py>`, we can now
alter the settings of Snappy Hex Mesh by altering the attributes of the SnappyHexMesh class. Once
we've updated these we generate the mesh via::

    snap.generate_mesh()
    
This generates four different meshes: the blank block mesh, the castellated mesh, the snapped mesh
and a mesh with layer addition. In order to use the final mesh as the starting point of our simulation
we perform some trickery to delete the meshes we don't want and move the mesh we do want into the constant folder

.. literalinclude:: ../examples/join_stl_example.py
    :pyobject: getTrueMesh


