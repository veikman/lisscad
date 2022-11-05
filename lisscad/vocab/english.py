"""Narrowed, English-friendly alternatives to OpenSCAD vocabulary."""

from typing import cast

import lisscad.data.inter as d
from lisscad.vocab import base


def square(side: float, **kwargs):
    """Define a literal square."""
    return base.square((side, side), **kwargs)


# OpenSCAD’s square function, as modelled in base, draws rectangles.
rectangle = base.square


def spheroid(size: d.Tuple3D, **kwargs) -> d.Size3D:
    """Define a tri-axial ellipsoid aligned with the coordinate axes."""
    return cast(d.Size3D, base.resize(size, base.sphere(max(size), **kwargs)))


def cube(side: float, **kwargs):
    """Define a literal cube."""
    return base.cube((side, side, side), **kwargs)


# OpenSCAD’s cube function, as modelled in base, draws rectangular cuboids.
cuboid = base.cube
