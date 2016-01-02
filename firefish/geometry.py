"""
This module deals with the loading, saving and manipulation of geometry.

Most manipulation functions deal with instances of :py:class:`stl.mesh.Mesh`. See
the `numpy-stl documentation`_ for more information.

.. _numpy-stl documentation: http://numpy-stl.readthedocs.org/en/latest/stl.html#module-stl.mesh

"""
import numpy as np
import stl.mesh as mesh

def _erase_attr(o, attr):
    """Delete the attribute *attr* from *o* but only if present."""
    if hasattr(o, attr):
        delattr(o, attr)

def load(path):
    """Convenience function to load a :py:class:`stl.mesh.Mesh` from disk.

    .. note::

        The :py:meth:`save` method on :py:class:`stl.mesh.Mesh` may be used to
        write geometry to disk.

    Args:
        path (str): pathname to STL file

    Returns:
        an new instance of :py:class:`stl.mesh.Mesh`
    """
    return mesh.Mesh.from_file(path)

def bounds(geom):
    """Compute the bounding box of the geometry.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        A pair giving the minimum and maximum X, Y and Z co-ordinates as
        three-dimensional array-likes.

    """
    return geom.min_, geom.max_

def geometric_centre(geom):
    """Compute the centre of the bounding box.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        An array like giving the X, Y and Z co-ordinates of the centre.

    """
    return 0.5 * (geom.max_ + geom.min_)

def copy(geom):
    """Copy a geometry.

    Use this function sparingly. Geometry can be quite heavyweight as data
    structures go.

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        A deep copy of the geometry.

    """
    return mesh.Mesh(geom.data, calculate_normals=False, name=geom.name)

def translate(geom, delta):
    """Translate a geometry along some vector.

    This function modifies the passed geometry.

    Args:
        geom (stl.mesh.Mesh): STL geometry
        delta (array like): 3-vector giving translation in X, Y and Z

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    cx, cy, cz = np.atleast_1d(delta)
    geom.x += cx
    geom.y += cy
    geom.z += cz

    # Delete cached minimum and maximum values. Other cached values are
    # unaffected. (This sort of magic is why we write wrappers!)
    _erase_attr(geom, '_min')
    _erase_attr(geom, '_max')

    return geom

def recentre(geom):
    """Centre a geometry such that its bounding box is centred on the origin.

    This function modifies the passed geometry.

    Equivalent to::

        translate(geom, -geometric_centre(geom))

    Args:
        geom (stl.mesh.Mesh): STL geometry

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    return translate(geom, -geometric_centre(geom))

def scale(geom, factor):
    """Scale geometry by a fixed factor.

    This function modifies the passed geometry. If the scale factor is a single
    scalar it is applied to each axis. If it is a 3-vector then the elements
    specify the scaling along the X, Y and Z axes.

    Args:
        geom (stl.mesh.Mesh): STL geometry
        factor (scalar or array like): scale factor to apply

    Returns:
        The passed geometry to allow for easy chaining of calls.

    """
    factor = np.atleast_1d(factor)
    if factor.shape == (1,):
        factor = np.ones(3) * factor[0]
    sx, sy, sz = factor

    geom.x *= sx
    geom.y *= sy
    geom.z *= sz

    # Delete cached minimum, maximum and area values. Other cached values are
    # unaffected. (This sort of magic is why we write wrappers!)
    _erase_attr(geom, '_min')
    _erase_attr(geom, '_max')
    _erase_attr(geom, '_areas')

    return geom