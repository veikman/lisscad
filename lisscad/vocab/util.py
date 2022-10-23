"""Utilities built on top of OpenSCAD."""

from builtins import round as round_number
from itertools import pairwise
from numbers import Number
from typing import Any, Callable, Iterable, cast

from lisscad.data.inter import (AngledOffset, LiteralExpression,
                                LiteralExpressionNon3D, RoundedOffset)
from lisscad.vocab.base import hull, offset, union


def pairwise_hull(*shapes: LiteralExpression):
    """The combined hulls of each overlapping pair of shapes."""
    return union(*(hull(*pair) for pair in pairwise(shapes)))


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
