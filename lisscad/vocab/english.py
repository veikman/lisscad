"""Narrowed, English-friendly alternatives to OpenSCAD vocabulary."""

from lisscad.vocab import base


def cube(side: float, **kwargs):
    """Define a literal cube."""
    return base.cube((side, side, side), **kwargs)
