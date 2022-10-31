"""Narrowed, English-friendly alternatives to OpenSCAD vocabulary."""

from lisscad.vocab import base


def square(side: float, **kwargs):
    """Define a literal square."""
    return base.square((side, side), **kwargs)


# OpenSCAD’s square function, as modelled in base, draws rectangles.
rectangle = base.square


def cube(side: float, **kwargs):
    """Define a literal cube."""
    return base.cube((side, side, side), **kwargs)


# OpenSCAD’s cube function, as modelled in base, draws rectangular cuboids.
cuboid = base.cube
