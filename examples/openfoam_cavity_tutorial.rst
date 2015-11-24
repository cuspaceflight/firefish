.. This file is read by doc/examples.rst and inserted into the documentation. It
   lives here so that it is more clearly associated with
   openfoam_cavity_tutorial.py. Note that file paths are, however, relative to
   the doc/ directory.

Lid-driven cavity flow
----------------------

The :download:`openfoam_cavity_tutorial.py <../examples/openfoam_cavity_tutorial.py>`
script provides an example of low-level manipulation of OpenFOAM cases. In this
example we shall re-create the `initial example`_ from the OpenFOAM users'
guide. It's worth reading over that section first before trying to follow the
transliteration below.

.. _initial example: http://cfd.direct/openfoam/user-guide/cavity/#x5-40002.1

Firstly, we need to import some things from the :py:mod:`cusfsim.case` module::

   from cusfsim.case import Case, FileName, FileClass

The :py:class:`~.case.Case` class encapsulates an OpenFOAM case
directory. We don't want to overwrite an existing case and so we write a little
convenience wrapper function:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: create_new_case

The :py:meth:`~.case.Case.mutable_data_file` method will return a *context
manager* which can be used to manipulate an OpenFOAM data file. The data file is
created if it does not yet exist, its contents are parsed into a dictionary and
the dictionary is returned from the context manager. One the context is left the
dictionary is re-written to disk.

The upshot of this is that the programmer is insulated from manipulating
OpenFOAM data files directly. Let's write the *controlDict* file from the
tutorial:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: write_initial_control_dict

Well-known file names are available through the :py:class:`~.case.FileName`
class.

The *blockMeshDict* file is the next one to be created. This is an example of a
relatively complex file. The complexity is somewhat hidden by the mapping to and
from the Python domain but there is still some subtlety. Notice particularly the
rather odd way in which the *boundary* dictionary is specified:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: write_block_mesh_dict


At this point in the tutorial we're ready to run the *blockMesh* command which
is one function call away::

   case.run_tool('blockMesh')

We're close to being able to run the *icoFoam* utility. The transport properties
need to be defined::

   from cusfsim.case import Dimension

   with case.mutable_data_file(FileName.TRANSPORT_PROPERTIES) as tp:
      tp['nu'] = (Dimension(0, 2, -1, 0, 0, 0, 0), 0.01)

We also need to create the initial conditions. Notice that we have to specify a
different class when creating them:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: write_initial_conditions

Before we can run *icoFoam*, we must create the mysterious *fvSolution* file:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: write_fv_solution

And also the equally mysterious *fvSchemes* file:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: write_fv_schemes

The example script includes a :py:func:`main` function which performs all of
these steps:

.. literalinclude:: ../examples/openfoam_cavity_tutorial.py
   :pyobject: main

After the example script is run, *paraFoam* may be run to inspect the solution.

