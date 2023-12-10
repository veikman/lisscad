"""Utilities built on top of OpenSCAD."""

from builtins import round as round_number
from typing import Any, Callable, Iterable, cast

import more_itertools as mi
from lisscad.data.inter import (
    AngledOffset,
    LinearExtrusion,
    LiteralExpression,
    LiteralExpressionNon3D,
    RoundedOffset,
    Union2D,
    Union3D,
)
from lisscad.vocab.base import hull, mirror, offset, union

μm = 0.001


def wafer(*shape: LiteralExpressionNon3D, height=μm, **kwargs):
    """Extrude passed 2D shape by a small amount, to a wafer.

    This is like base.extrude, but with a height much smaller than the default
    value built into OpenSCAD. This is intended for use with sliding_hull,
    particularly in Lissp threading macros, where passing in a height parameter
    can be awkward.

    """
    return LinearExtrusion(shape, height=height, **kwargs)


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


def round(
    radius: float | int,
    *shapes: LiteralExpressionNon3D,
    ndigits: int | None = None,
    **kwargs,
) -> RoundedOffset | AngledOffset | float:
    """Apply a pair of offsets to round off the corners of a 2D shape.

    The passed shapes must be large enough that the initial negative offset
    does not eliminate them.

    Given a number, apply builtins.round instead. The optional ndigits
    parameter to builtins.round must be passed via keyword.

    """
    if not shapes or ndigits is not None:
        assert not shapes
        return round_number(radius, ndigits=ndigits)
    inner = offset(
        -radius, *cast(tuple[LiteralExpressionNon3D, ...], shapes), **kwargs
    )
    return offset(radius, inner, **kwargs)


def union_map(
    function: Callable[[Any], LiteralExpression],
    iterable: Iterable[LiteralExpression],
):
    """The union of the outputs of a mapping.

    Similar to an OpenSCAD for statement.

    """
    return union(*map(function, iterable))


def bilateral_symmetry_x(shape: LiteralExpression) -> Union2D | Union3D:
    """Keep shape alongside a mirror image of it in the x axis."""
    # This is simple enough that it can be implemented in
    # lisscad/prelude.lissp, for instance like this:
    #
    # (define bilateral-symmetry-x
    #   (lambda ($#shape)
    #     (lisscad.vocab.base..union
    #       $#shape
    #       (lisscad.vocab.base..mirror '(1 0 0) $#shape))))
    #
    # Because of the `(progn ...) template in the metamacro there, as of hissp
    # v0.4.0 the symbols are too long, and later definitions within the
    # template can’t call the function.
    return union(shape, mirror((1, 0, 0), shape))


def bilateral_symmetry_y(shape: LiteralExpression) -> Union2D | Union3D:
    """Keep shape alongside a mirror image of it in the y axis."""
    return union(shape, mirror((0, 1, 0), shape))


def bilateral_symmetry_xy(shape: LiteralExpression) -> Union2D | Union3D:
    """Keep shape adding quadrilateral symmetry. Four copies in total."""
    return bilateral_symmetry_y(bilateral_symmetry_x(shape))
