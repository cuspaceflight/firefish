# STL example model files

## "Cartoon" rocket

This directory contains a ["cartoon" rocket model](cartoon-rocket.stl) which is
defined parametrically via an [OpenSCAD](http://www.openscad.org/) program.

The model is a "cartoon" in that it is made of simple shapes. Variables at the
top of the file may be altered to change the height, diameter, cone height or
fin shape.

It is intended as an example of a parametrised rocket CAD model. It is *not*
intended as an example of good aerodynamics!

To re-generate the STL file, run it through ``openscad``:
```console
$ openscad -o cartoon-rocket.stl cartoon-rocket.scad
```

The STL file is then surface-meshed via netgen which automatcally chooses a
resolution. (We may wish to investigate options such as ``-fine`` later on.)

The surface-meshed file is then volume-meshed via ``gmsh``. See the [.geo
file](cartoon-rocket.domain.geo) for a specification of the domain bounding box.

Alternatively the provided ``Makefile`` will run the commands for you.

The generated mesh can be viewed via ``paraview`` by converting it to a ``vtk``
file:

```console
$ gmsh -format vtk -o cartoon-rocket.domain.vtk cartoon-rocket.domain.msh -0
```

