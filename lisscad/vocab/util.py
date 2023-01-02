"""Utilities built on top of OpenSCAD."""

from builtins import round as round_number
from numbers import Number
from typing import Any, Callable, Iterable, cast

import more_itertools as mi
from lisscad.data.inter import (AngledOffset, LiteralExpression,
                                LiteralExpressionNon3D, RoundedOffset)
from lisscad.vocab.base import extrude, hull, offset, union

μm = 0.001


def wafer(*shape: LiteralExpressionNon3D, height=μm, **kwargs):
    """Extrude passed 2D shape by a small amount, to a wafer.

    This is indeed just a call to extrude(), but with a height much smaller
    than the default value built into OpenSCAD. This is intended for use with
    sliding_hull, particularly in Lissp threading macros, where passing in a
    height parameter can be awkward.

    """
    return extrude(shape, height=height, **kwargs)


def sliding_hull(*shapes: LiteralExpression, n: int = 2):
    """Unite the hulls of each n-tuple of shapes in a sliding window.

    The tuples viewed in the sliding window will have an overlap of n - 1
    shapes. For example, at n = 3, the sliding hull of the shapes
    [A, B, C, D, E] is the hull of [A, B, C] in a union with the hull of
    [B, C, D] and the hull of [C, D, E].

    """
    return union(*(hull(*w) for w in mi.sliding_window(shapes, n)))


def radiate(hub: LiteralExpression, *spokes: LiteralExpression):
    return sliding_hull(*mi.intersperse(hub, spokes))


def round(radius: float | int, *shapes: LiteralExpressionNon3D | Number,
          **kwargs) -> RoundedOffset | AngledOffset | float:
    """Apply a pair of offsets to round off the corners of a 2D shape.

    Given one or two numbers, apply builtins.round instead.

    The passed shapes must be large enough that the initial negative offset
    does not eliminate them.

    """
    if not shapes or isinstance(shapes[0], Number):
        return round_number(radius, *shapes)
    inner = offset(-radius, *cast(tuple[LiteralExpressionNon3D, ...], shapes),
                   **kwargs)
    return offset(radius, inner, **kwargs)


def union_map(function: Callable[[Any], LiteralExpression],
              iterable: Iterable[LiteralExpression]):
    """The union of the outputs of a mapping.

    Similar to an OpenSCAD for statement.

    """
    return union(*map(function, iterable))
