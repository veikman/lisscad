"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj rather than OpenSCAD itself.

"""

# Imports are styled so as to limit pollution when this module is star-imported
# via lisscad.prelude. TODO: Transition to __all__.

from functools import partial as _partial
from pathlib import Path as _Path
from typing import Type as _Type
from typing import cast as _cast

import lisscad.data.inter as d

#############
# INTERFACE #
#############


def comment(
    content: str | tuple[str, ...],
    subject: d.LiteralExpression | None = None
) -> d.Commented2D | d.Commented3D | d.Comment:
    """Export a comment in OpenSCAD code.

    This is intended for metadata like license statements, as well as for
    debugging outputs by making them more searchable.

    """
    if isinstance(content, str):
        content = (content, )
    c = d.Comment(content)
    if subject is None:
        return c
    if _dimensionality('comment', subject) == 2:
        return d.Commented2D(c, _cast(d.LiteralExpression2D, subject))
    return d.Commented3D(c, _cast(d.LiteralExpression3D, subject))


def background(child: d.LiteralExpression) -> d.Background2D | d.Background3D:
    """Implement OpenSCAD’s % modifier, known as transparent or background."""
    return _cast(d.Background2D | d.Background3D,
                 _modify(d.Background2D, d.Background3D, child))


def debug(child: d.LiteralExpression) -> d.Debug2D | d.Debug3D:
    """Implement OpenSCAD’s # modifier, known as highlight or debug."""
    return _cast(d.Debug2D | d.Debug3D, _modify(d.Debug2D, d.Debug3D, child))


def root(child: d.LiteralExpression) -> d.Root2D | d.Root3D:
    """Implement OpenSCAD’s ! modifier, known as show-only or root."""
    return _cast(d.Root2D | d.Root3D, _modify(d.Root2D, d.Root3D, child))


def disable(child: d.LiteralExpression) -> d.Disable2D | d.Disable3D:
    """Implement OpenSCAD’s * modifier, known as disable."""
    return _cast(d.Disable2D | d.Disable3D,
                 _modify(d.Disable2D, d.Disable3D, child))


def union(*children: d.LiteralExpression) -> d.Union2D | d.Union3D:
    return _cast(d.Union2D | d.Union3D, _contain(d.Union2D, d.Union3D,
                                                 children))


def difference(
        *children: d.LiteralExpression) -> d.Difference2D | d.Difference3D:
    return _cast(d.Difference2D | d.Difference3D,
                 _contain(d.Difference2D, d.Difference3D, children))


def intersection(
        *children: d.LiteralExpression) -> d.Intersection2D | d.Intersection3D:
    return _cast(d.Intersection2D | d.Intersection3D,
                 _contain(d.Intersection2D, d.Intersection3D, children))


def circle(radius: float) -> d.Circle:
    return d.Circle(radius)


def square(size: float | d.Tuple2D,
           center: bool = True) -> d.Square | d.Rectangle:
    if isinstance(size, (float, int)):
        return d.Square(size, center=center)
    return d.Rectangle(size, center=center)


def polygon(points: tuple[d.Tuple2D, ...], **kwargs) -> d.Polygon:
    return d.Polygon(points, **kwargs)


def text(text: str, **kwargs) -> d.Text:
    return d.Text(text, **kwargs)


def import_(file: _Path, **kwargs) -> d.Import2D | d.Import3D:
    # The word “import” is reserved in Python, unusable in Lissp.
    # The alias “import_” is also used in SolidPython.
    match _Path(file).suffix.lower():
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


def projection(child: d.LiteralExpressionNon2D,
               cut: bool = False) -> d.Projection:
    """Implement an OpenSCAD projection.

    For ease of use in threading macros, cutting is also available as a
    separate operation (“cut”), as in scad-clj.

    """
    return d.Projection(child, cut=cut)


cut = _partial(projection, cut=True)


def sphere(radius: float) -> d.Sphere:
    return d.Sphere(radius)


def cube(size: d.Tuple3D, center: bool = True) -> d.Cube:
    return d.Cube(size, center)


def cylinder(radius: float | tuple[float, float],
             height: float,
             center: bool = True) -> d.Cylinder | d.Frustum:
    # Take the radius argument first, like scad-clj.
    if isinstance(radius, (int, float)):
        return d.Cylinder(radius, height, center=center)
    return d.Frustum(radius[0], radius[1], height, center=center)


def polyhedron(points: tuple[d.Tuple3D, ...],
               faces=tuple[tuple[int, ...], ...],
               **kwargs):
    return d.Polyhedron(points, faces, **kwargs)


def extrude(*children: d.LiteralExpressionNon3D,
            rotate: bool | None = None,
            **kwargs) -> d.LinearExtrusion | d.RotationalExtrusion:
    """Extrude translationally by default."""
    if rotate is True or (rotate is None and 'angle' in kwargs):
        return d.RotationalExtrusion(children=children, **kwargs)
    return d.LinearExtrusion(children=children, **kwargs)


def surface(file: _Path, center: bool = True, **kwargs) -> d.Surface:
    return d.Surface(file, center=center, **kwargs)


def translate(
        coord: d.Tuple2D | d.Tuple3D,
        *children: d.LiteralExpression) -> d.Translation2D | d.Translation3D:
    if len(coord) == 2:
        return d.Translation2D(
            _cast(d.Tuple2D, coord),
            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Translation3D(_cast(d.Tuple3D, coord),
                           _cast(tuple[d.LiteralExpression3D, ...], children))


def rotate(angles: float | int | d.Tuple3D,
           *children: d.LiteralExpression) -> d.Rotation2D | d.Rotation3D:
    if isinstance(angles, (float, int)):
        return d.Rotation2D(angles,
                            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Rotation3D(angles,
                        _cast(tuple[d.LiteralExpression3D, ...], children))


def scale(factors: d.Tuple2D | d.Tuple3D,
          *children: d.LiteralExpression) -> d.Scaling2D | d.Scaling3D:
    if len(factors) == 2:
        return d.Scaling2D(_cast(d.Tuple2D, factors),
                           _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Scaling3D(_cast(d.Tuple3D, factors),
                       _cast(tuple[d.LiteralExpression3D, ...], children))


def resize(size: d.Tuple2D | d.Tuple3D,
           *children: d.LiteralExpression) -> d.Size2D | d.Size3D:
    if len(size) == 2:
        return d.Size2D(_cast(d.Tuple2D, size),
                        _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Size3D(_cast(d.Tuple3D, size),
                    _cast(tuple[d.LiteralExpression3D, ...], children))


def mirror(axes: tuple[int, int, int],
           *children: d.LiteralExpression) -> d.Mirror2D | d.Mirror3D:
    if _dimensionality('mirror', *children) == 2:
        return d.Mirror2D(axes,
                          _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Mirror3D(axes, _cast(tuple[d.LiteralExpression3D, ...], children))


def multmatrix(
    matrix: tuple[d.Tuple4D, ...], *children: d.LiteralExpression
) -> d.AffineTransformation2D | d.AffineTransformation3D:
    # OpenSCAD can apply a multmatrix to a two-dimensional object, but as of
    # 2022 there are no examples or specifications in the manual.
    if _dimensionality('transform', *children) == 2:
        return d.AffineTransformation2D(
            matrix, _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.AffineTransformation3D(
        matrix, _cast(tuple[d.LiteralExpression3D, ...], children))


def color(value: d.Tuple4D | str,
          *children: d.LiteralExpression) -> d.Color2D | d.Color3D:
    if _dimensionality('color', *children) == 2:
        return d.Color2D(value,
                         _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Color3D(value, _cast(tuple[d.LiteralExpression3D, ...], children))


def offset(distance: float,
           *children: d.LiteralExpressionNon3D,
           round: bool = True,
           chamfer: bool = False) -> d.RoundedOffset | d.AngledOffset:
    if round:
        assert not chamfer  # Chamfering is meaningless in this context.
        return d.RoundedOffset(distance, children)
    return d.AngledOffset(distance, children, chamfer=chamfer)


def hull(*children: d.LiteralExpression) -> d.Hull2D | d.Hull3D:
    if _dimensionality('form a hull around', *children) == 2:
        return d.Hull2D(_cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Hull3D(_cast(tuple[d.LiteralExpression3D, ...], children))


def minkowski(*children: d.LiteralExpression,
              **kwargs) -> (d.MinkowskiSum2D | d.MinkowskiSum3D):
    if _dimensionality('minkowski-add', *children) == 2:
        return d.MinkowskiSum2D(
            _cast(tuple[d.LiteralExpression2D, ...], children), **kwargs)
    return d.MinkowskiSum3D(_cast(tuple[d.LiteralExpression3D, ...], children),
                            **kwargs)


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


def echo(*content: str) -> d.Echo:
    """Order text to be printed to the OpenSCAD console.

    This implementation does not support arbitrary keyword arguments.

    """
    return d.Echo(content)


def children() -> d.ModuleChildren:
    """Place the children of a call to a module inside that module.

    Neither indexing nor counting of children are currently supported.

    """
    return d.ModuleChildren()


############
# INTERNAL #
############


def _dimensionality(verb: str, *expressions) -> int:
    """Determine the common dimensionality of children."""
    assert expressions
    two: list[int] = []
    three: list[int] = []

    for i, e in enumerate(expressions):
        if isinstance(e, d.Base2D):
            two.append(i)
        elif isinstance(e, d.Base3D):
            three.append(i)
        elif isinstance(e, d.BaseND):
            pass
        else:
            raise TypeError(
                f'Cannot {verb} unknown OpenSCAD operation {type(e)!r}.')

    if two and three:
        # OpenSCAD’s behaviour is poorely defined. Best not to transpile.
        s = f'Cannot {verb} mixed 2D and 3D expressions.'
        if len(two) == 1 and len(three) != 1:
            s += f' One, in place {two[0] + 1} of {len(expressions)}, is 2D.'
        elif len(two) != 1 and len(three) == 1:
            s += f' One, in place {three[0] + 1} of {len(expressions)}, is 3D.'
        raise TypeError(s)

    if two:
        return 2
    # Assume object(s) of unknown dimensionality can be treated as 3D.
    return 3


def _modify(type_2d: _Type[d.BaseModifier2D], type_3d: _Type[d.BaseModifier3D],
            child: d.LiteralExpression) -> d.BaseModifier2D | d.BaseModifier3D:
    """Wrap up a single expression of known dimensionality."""
    if _dimensionality('modify', child) == 2:
        return type_2d(_cast(d.LiteralExpression2D, child))
    return type_3d(_cast(d.LiteralExpression3D, child))


def _contain(
    type_2d: _Type[d.BaseBoolean2D], type_3d: _Type[d.BaseBoolean3D],
    children: tuple[d.LiteralExpression, ...]
) -> d.BaseBoolean2D | d.BaseBoolean3D:
    """Wrap up 1+ expressions of known dimensionality."""
    if _dimensionality('contain', *children) == 2:
        return type_2d(_cast(tuple[d.LiteralExpression2D, ...], children))
    return type_3d(_cast(tuple[d.LiteralExpression3D, ...], children))


def _define_module(
    name: str, *children: d.LiteralExpression
) -> d.ModuleDefinition2D | d.ModuleDefinition3D:
    """Define an OpenSCAD module.

    This is intended for use in limiting the sheer amount of OpenSCAD code
    generated for a repetitive design. Depending on the development of
    OpenSCAD, there may be caching benefits as well.

    Like scad-clj, lisscad does not support arguments to modules.

    """
    if _dimensionality('define module of', *children) == 2:
        return d.ModuleDefinition2D(
            name, _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.ModuleDefinition3D(
        name, _cast(tuple[d.LiteralExpression3D, ...], children))


def _call_module(
    name: str, *children: d.LiteralExpression
) -> d.ModuleCall2D | d.ModuleCall3D | d.ModuleCallND:
    if children:
        if _dimensionality('call module using', *children) == 2:
            return d.ModuleCall2D(
                name, _cast(tuple[d.LiteralExpression2D, ...], children))
        return d.ModuleCall3D(
            name, _cast(tuple[d.LiteralExpression3D, ...], children))
    return d.ModuleCallND(name)
