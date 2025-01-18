"""Utilities built on top of OpenSCAD."""

from builtins import round as round_number
from math import pi, tau
from typing import Any, Callable, Iterable, cast

import more_itertools as mi
from lisscad.data.inter import (
    AngledOffset,
    LinearExtrusion,
    LiteralExpression,
    LiteralExpressionNon3D,
    RoundedOffset,
    Tuple3D,
    Union2D,
    Union3D,
)
from lisscad.exc import LisscadError
from lisscad.vocab.base import hull, mirror, offset, rotate, union

μm = 0.001


def wafer(*shape: LiteralExpressionNon3D, height=μm, **kwargs):
    """Extrude passed 2D shape by a small amount, to a wafer.

    This is like base.extrude, but with a height much smaller than the default
    value built into OpenSCAD. This is intended for use with sliding_hull,
    particularly in Lissp threading macros, where passing in a height parameter
    could be awkward until the thread-through macro was introduced.

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
    iterable: Iterable[float | int | LiteralExpression],
):
    """Unite the outputs of a mapping.

    Similar to an OpenSCAD for statement.

    """
    if not callable(function):
        raise LisscadError('Invalid union map: First argument not callable.')
    try:
        return union(*map(function, iterable))
    except LisscadError as exc:
        raise LisscadError(f'Invalid union map: {exc}') from exc


def rotational_symmetry(
    angles: float | int | Tuple3D, *children: LiteralExpression
) -> Union2D | Union3D:
    """Rotate copies."""
    turn_angle, number_of_turns = _prepare_rotational_symmetry(angles)

    def turn_copy(index: int) -> LiteralExpression:
        if index:
            return rotate(turn_angle(index), *children)
        if len(children) > 1:
            return union(*children)
        return children[0]

    return union_map(turn_copy, range(number_of_turns))


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


def bilateral_symmetry_z(shape: LiteralExpression) -> Union2D | Union3D:
    """Keep shape alongside a mirror image of it in the z axis."""
    return union(shape, mirror((0, 0, 1), shape))


def bilateral_symmetry_xy(shape: LiteralExpression) -> Union2D | Union3D:
    """Keep shape adding quadrilateral symmetry. Four copies in total."""
    return bilateral_symmetry_y(bilateral_symmetry_x(shape))


############
# INTERNAL #
############


def _check_rotation_symmetry(angle: float | int) -> None:
    """Smoke-check passed angle."""
    if not angle:
        raise ValueError('Rotational symmetry requires a non-zero angle.')
    if angle < 0:
        raise ValueError('Rotational symmetry requires a positive angle.')
    if angle > pi:
        raise ValueError(
            'Rotational symmetry requires an angle of at most π radians.'
        )


def _prepare_rotational_symmetry(
    angles: float | int | Tuple3D,
) -> tuple[Callable[[int], float | int | Tuple3D], int]:
    """Check and tune parameters for rotational symmetry.

    Return a function for calculating the angle of rotation at each step, and
    the total number of steps.

    """
    if isinstance(angles, (float, int)):
        _check_rotation_symmetry(angles)
        return lambda i: i * angles, int(tau / angles)

    candidates = [a for a in angles if a]
    if not candidates:
        raise ValueError('3D rotational symmetry requires an angle.')

    if len(candidates) > 1:
        raise ValueError('Multi-planar rotational symmetry is not supported.')

    if len(angles) != 3:
        raise ValueError(
            '3D rotational symmetry requires a 3-tuple of angles. '
            'Exactly one of them must be non-zero.'
        )

    angle = candidates[0]
    _check_rotation_symmetry(angle)
    return lambda i: cast(Tuple3D, tuple(i * a for a in angles)), int(
        tau / angle
    )
