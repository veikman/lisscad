"""Narrowed, English-friendly alternatives to OpenSCAD vocabulary."""

from typing import cast

import lisscad.data.inter as d
from lisscad.data.util import dimensionality
from lisscad.vocab import base

##########
# SHAPES #
##########


def ellipse(size: d.Tuple2D, **kwargs):
    """Define an ellipse aligned with the coordinate axes."""
    return cast(d.Size2D, base.resize(size, base.circle(max(size), **kwargs)))


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


def cylinder(radius: float, *args, **kwargs):
    """Define a literal cylinder."""
    assert isinstance(radius, (float, int))
    return base.cylinder(radius, *args, **kwargs)


def cylindroid(radius0: float, radius1: float, height: float, **kwargs):
    """Define an elliptic cylinder aligned with the coordinate axes.

    radius0 here is the radius of the elliptic profile on the x axis, not at
    the base. For a shape that gets wider or narrow, see frustum.

    """
    # This may change to a centred extrusion.
    profile = (radius0, radius1)
    return cast(
        d.Size3D,
        base.resize(
            (*profile, height), base.cylinder(max(profile), height, **kwargs)
        ),
    )


def frustum(radius0: float, radius1: float, *args, **kwargs):
    """Define a frustum."""
    assert isinstance(radius0, (float, int))
    assert isinstance(radius1, (float, int))
    return base.cylinder((radius0, radius1), *args, **kwargs)


################
# TRANSLATIONS #
################

# Inspired by Evan Jones’s directional helpers in SolidPython.


def left(
    distance: float, *children: d.LiteralExpression
) -> d.Translation2D | d.Translation3D:
    """Translate along negative x."""
    n = dimensionality('translate', *children)
    if n == 2:
        return d.Translation2D(
            (-distance, 0), cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.Translation3D(
        (-distance, 0, 0), cast(tuple[d.LiteralExpression3D, ...], children)
    )


def right(
    distance: float, *children: d.LiteralExpression
) -> d.Translation2D | d.Translation3D:
    """Translate along positive x."""
    return left(-distance, *children)


def back(
    distance: float, *children: d.LiteralExpression
) -> d.Translation2D | d.Translation3D:
    """Translate along negative y."""
    n = dimensionality('translate', *children)
    if n == 2:
        return d.Translation2D(
            (0, -distance), cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.Translation3D(
        (0, -distance, 0), cast(tuple[d.LiteralExpression3D, ...], children)
    )


def forward(
    distance: float, *children: d.LiteralExpression
) -> d.Translation2D | d.Translation3D:
    """Translate along positive y."""
    return back(-distance, *children)


def down(distance: float, *children: d.LiteralExpression3D) -> d.Translation3D:
    """Translate along negative z."""
    return d.Translation3D((0, 0, -distance), children)


def up(distance: float, *children: d.LiteralExpression3D) -> d.Translation3D:
    """Translate along positive z."""
    return down(-distance, *children)
