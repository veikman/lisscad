"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj rather than OpenSCAD itself,
but has broader coverage than the other Lisscad vocab modules.

The module is intended to be star-imported from CAD scripts via a Lissp macro.

"""

from functools import partial
from pathlib import Path
from typing import cast

import lisscad.data.inter as d
from lisscad.data.util import contain, dimensionality, matched, modify

############
# INTERNAL #
############

__all__: list[str] = []


def _starred(member, name: str = ''):
    """Expose decorated member of module for star import."""
    __all__.append(name or member.__name__)
    return member


#############
# INTERFACE #
#############


@_starred
def comment(
    content: str | tuple[str, ...], subject: d.LiteralExpression | None = None
) -> d.Commented2D | d.Commented3D | d.Comment:
    """Export a comment in OpenSCAD code.

    This is intended for metadata like license statements, as well as for
    debugging outputs by making them more searchable.

    """
    if isinstance(content, str):
        content = (content,)
    c = d.Comment(content)
    if subject is None:
        return c
    if dimensionality('comment', subject) == 2:
        return d.Commented2D(c, cast(d.LiteralExpression2D, subject))
    return d.Commented3D(c, cast(d.LiteralExpression3D, subject))


@_starred
def background(child: d.LiteralExpression) -> d.Background2D | d.Background3D:
    """Implement OpenSCAD’s % modifier, known as transparent or background."""
    return cast(
        d.Background2D | d.Background3D,
        modify(d.Background2D, d.Background3D, child),
    )


@_starred
def debug(child: d.LiteralExpression) -> d.Debug2D | d.Debug3D:
    """Implement OpenSCAD’s # modifier, known as highlight or debug."""
    return cast(d.Debug2D | d.Debug3D, modify(d.Debug2D, d.Debug3D, child))


@_starred
def root(child: d.LiteralExpression) -> d.Root2D | d.Root3D:
    """Implement OpenSCAD’s ! modifier, known as show-only or root."""
    return cast(d.Root2D | d.Root3D, modify(d.Root2D, d.Root3D, child))


@_starred
def disable(child: d.LiteralExpression) -> d.Disable2D | d.Disable3D:
    """Implement OpenSCAD’s * modifier, known as disable."""
    return cast(
        d.Disable2D | d.Disable3D, modify(d.Disable2D, d.Disable3D, child)
    )


@_starred
def special(variable, *values: float | int) -> d.SpecialVariable:
    """Read or assign a value to one of OpenSCAD’s special variables.

    This is crude. Neither names nor data types are enforced, you can’t use
    this in place of a number in other expressions, and the only supported way
    to use a special variable on the value side of the expression is as a
    ternary on $preview, by passing two values.

    Passing a complete expression as if it were a variable name is cheating; it
    should not be considered a stable feature.

    """
    return d.SpecialVariable(variable, *values)


@_starred
def union(*children: d.LiteralExpression | tuple[()]) -> d.Union2D | d.Union3D:
    some = _some(children)
    return cast(d.Union2D | d.Union3D, contain(d.Union2D, d.Union3D, some))


@_starred
def difference(
    minuend: d.LiteralExpression, *children: d.LiteralExpression | tuple[()]
) -> d.Difference2D | d.Difference3D:
    subtrahend = _some(children)
    return cast(
        d.Difference2D | d.Difference3D,
        contain(
            d.Difference2D,
            d.Difference3D,
            (minuend, *subtrahend),
            verb_first='subtract from',
            verb_rest='subtract',
        ),
    )


@_starred
def intersection(
    *children: d.LiteralExpression | tuple[()],
) -> d.Intersection2D | d.Intersection3D:
    some = _some(children)
    return cast(
        d.Intersection2D | d.Intersection3D,
        contain(d.Intersection2D, d.Intersection3D, some),
    )


@_starred
def circle(radius: float) -> d.Circle:
    return d.Circle(radius)


@_starred
def square(
    size: float | d.Tuple2D, center: bool = True
) -> d.Square | d.Rectangle:
    if isinstance(size, (float, int)):
        return d.Square(size, center=center)
    return d.Rectangle(size, center=center)


@_starred
def polygon(points: tuple[d.Tuple2D, ...], **kwargs) -> d.Polygon:
    return d.Polygon(points, **kwargs)


@_starred
def text(text: str, **kwargs) -> d.Text:
    return d.Text(text, **kwargs)


@_starred
def import_(file: Path, **kwargs) -> d.Import2D | d.Import3D:
    # The word “import” is reserved in Python, unusable in Lissp.
    # The alias “import_” is also used in SolidPython.
    match Path(file).suffix.lower():
        case '.3mf':
            return d.Import3D(file, **kwargs)
        case '.amf':
            return d.Import3D(file, **kwargs)
        case '.dxf':
            return d.Import2D(file, **kwargs)
        case '.off':
            return d.Import3D(file, **kwargs)
        case '.stl':
            return d.Import3D(file, **kwargs)
        case '.svg':
            return d.Import2D(file, **kwargs)
    raise ValueError(f'Unknown file suffix for {file}.')


@_starred
def projection(
    child: d.LiteralExpressionNon2D, cut: bool = False
) -> d.Projection:
    """Implement an OpenSCAD projection.

    For ease of use in threading macros, cutting is also available as a
    separate operation (“cut”), as in scad-clj.

    """
    return d.Projection(child, cut=cut)


cut = _starred(partial(projection, cut=True), name='cut')


@_starred
def sphere(radius: float) -> d.Sphere:
    return d.Sphere(radius)


@_starred
def cube(size: d.Tuple3D, center: bool = True) -> d.Cube:
    return d.Cube(size, center)


@_starred
def cylinder(
    radius: float | tuple[float, float], height: float, center: bool = True
) -> d.Cylinder | d.Frustum:
    # Take the radius argument first, like scad-clj.
    if isinstance(radius, (int, float)):
        return d.Cylinder(radius, height, center=center)
    return d.Frustum(radius[0], radius[1], height, center=center)


@_starred
def polyhedron(
    points: tuple[d.Tuple3D, ...], faces=tuple[tuple[int, ...], ...], **kwargs
):
    return d.Polyhedron(points, faces, **kwargs)


@_starred
def extrude(
    *children: d.LiteralExpressionNon3D, rotate: bool | None = None, **kwargs
) -> d.LinearExtrusion | d.RotationalExtrusion:
    """Extrude translationally by default."""
    if rotate is True or (rotate is None and 'angle' in kwargs):
        return d.RotationalExtrusion(children=children, **kwargs)
    return d.LinearExtrusion(children=children, **kwargs)


@_starred
def surface(file: Path, center: bool = True, **kwargs) -> d.Surface:
    return d.Surface(file, center=center, **kwargs)


@_starred
def translate(
    coord: d.Tuple2D | d.Tuple3D, *children: d.LiteralExpression
) -> d.Translation2D | d.Translation3D:
    if matched('translate', coord, children) == 2:
        return d.Translation2D(
            cast(d.Tuple2D, coord),
            cast(tuple[d.LiteralExpression2D, ...], children),
        )
    return d.Translation3D(
        cast(d.Tuple3D, coord),
        cast(tuple[d.LiteralExpression3D, ...], children),
    )


@_starred
def rotate(
    angles: float | int | d.Tuple3D, *children: d.LiteralExpression
) -> d.Rotation2D | d.Rotation3D:
    if isinstance(angles, (float, int)):
        return d.Rotation2D(
            angles, cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.Rotation3D(
        angles, cast(tuple[d.LiteralExpression3D, ...], children)
    )


@_starred
def scale(
    factors: d.Tuple2D | d.Tuple3D, *children: d.LiteralExpression
) -> d.Scaling2D | d.Scaling3D:
    if matched('scale', factors, children) == 2:
        return d.Scaling2D(
            cast(d.Tuple2D, factors),
            cast(tuple[d.LiteralExpression2D, ...], children),
        )
    return d.Scaling3D(
        cast(d.Tuple3D, factors),
        cast(tuple[d.LiteralExpression3D, ...], children),
    )


@_starred
def resize(
    size: d.Tuple2D | d.Tuple3D, *children: d.LiteralExpression
) -> d.Size2D | d.Size3D:
    if matched('resize', size, children) == 2:
        return d.Size2D(
            cast(d.Tuple2D, size),
            cast(tuple[d.LiteralExpression2D, ...], children),
        )
    return d.Size3D(
        cast(d.Tuple3D, size),
        cast(tuple[d.LiteralExpression3D, ...], children),
    )


@_starred
def mirror(
    axes: tuple[int, int, int], *children: d.LiteralExpression
) -> d.Mirror2D | d.Mirror3D:
    # Do not require dimensionality of axes to match that of children.
    if dimensionality('mirror', *children) == 2:
        return d.Mirror2D(
            axes, cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.Mirror3D(axes, cast(tuple[d.LiteralExpression3D, ...], children))


@_starred
def multmatrix(
    matrix: tuple[d.Tuple4D, ...], *children: d.LiteralExpression
) -> d.AffineTransformation2D | d.AffineTransformation3D:
    # OpenSCAD can apply a multmatrix to a two-dimensional object, but as of
    # 2022 there are no examples or specifications in the manual.
    if dimensionality('transform', *children) == 2:
        return d.AffineTransformation2D(
            matrix, cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.AffineTransformation3D(
        matrix, cast(tuple[d.LiteralExpression3D, ...], children)
    )


@_starred
def color(
    value: d.Tuple4D | str, *children: d.LiteralExpression
) -> d.Color2D | d.Color3D:
    if dimensionality('color', *children) == 2:
        return d.Color2D(
            value, cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.Color3D(value, cast(tuple[d.LiteralExpression3D, ...], children))


@_starred
def offset(
    distance: float,
    *children: d.LiteralExpressionNon3D,
    round: bool = True,
    chamfer: bool = False,
) -> d.RoundedOffset | d.AngledOffset:
    if round:
        assert not chamfer  # Chamfering is meaningless in this context.
        return d.RoundedOffset(distance, children)
    return d.AngledOffset(distance, children, chamfer=chamfer)


@_starred
def hull(*children: d.LiteralExpression) -> d.Hull2D | d.Hull3D:
    if dimensionality('form a hull around', *children) == 2:
        return d.Hull2D(cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Hull3D(cast(tuple[d.LiteralExpression3D, ...], children))


@_starred
def minkowski(
    *children: d.LiteralExpression, **kwargs
) -> d.MinkowskiSum2D | d.MinkowskiSum3D:
    if dimensionality('minkowski-add', *children) == 2:
        return d.MinkowskiSum2D(
            cast(tuple[d.LiteralExpression2D, ...], children), **kwargs
        )
    return d.MinkowskiSum3D(
        cast(tuple[d.LiteralExpression3D, ...], children), **kwargs
    )


@_starred
def render(*children: d.LiteralExpressionNon2D, **kwargs) -> d.Rendering3D:
    # OpenSCAD supports rendering 2D shapes, probably for agnosticism, but
    # there is no practical need to do it.
    return d.Rendering3D(children, **kwargs)


@_starred
def module(name: str, *children: d.LiteralExpression, call=False):
    """Define an OpenSCAD module, or call one.

    This function does both partly because a name like “define_module” would be
    non-idiomatic in Lissp, partly because the OpenSCAD syntax to call a module
    is just the name of it with postfix parentheses.

    """
    if call:
        return _call_module(name, *children)
    assert children
    return _define_module(name, *children)


@_starred
def echo(*content: str) -> d.Echo:
    """Order text to be printed to the OpenSCAD console.

    This implementation does not support arbitrary keyword arguments.

    """
    return d.Echo(content)


@_starred
def children() -> d.ModuleChildren:
    """Place the children of a call to a module inside that module.

    Neither indexing nor counting of children are currently supported.

    """
    return d.ModuleChildren()


############
# INTERNAL #
############


def _some(
    items: tuple[d.LiteralExpression | tuple[()], ...]
) -> tuple[d.LiteralExpression, ...]:
    return tuple(filter(lambda x: x != (), items))  # type: ignore[arg-type]


def _define_module(
    name: str, *children: d.LiteralExpression
) -> d.ModuleDefinition2D | d.ModuleDefinition3D:
    """Define an OpenSCAD module.

    This is intended for use in limiting the sheer amount of OpenSCAD code
    generated for a repetitive design. Depending on the development of
    OpenSCAD, there may be caching benefits as well.

    Like scad-clj, lisscad does not support arguments to modules.

    """
    if dimensionality('define module of', *children) == 2:
        return d.ModuleDefinition2D(
            name, cast(tuple[d.LiteralExpression2D, ...], children)
        )
    return d.ModuleDefinition3D(
        name, cast(tuple[d.LiteralExpression3D, ...], children)
    )


def _call_module(
    name: str, *children: d.LiteralExpression
) -> d.ModuleCall2D | d.ModuleCall3D | d.ModuleCallND:
    if children:
        if dimensionality('call module using', *children) == 2:
            return d.ModuleCall2D(
                name, cast(tuple[d.LiteralExpression2D, ...], children)
            )
        return d.ModuleCall3D(
            name, cast(tuple[d.LiteralExpression3D, ...], children)
        )
    return d.ModuleCallND(name)
