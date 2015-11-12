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

Alternatively the provided ``Makefile`` will run the command for you.

