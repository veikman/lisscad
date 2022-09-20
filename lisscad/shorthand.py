"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj rather than OpenSCAD itself.

"""

# Imports are styled so as to limit pollution when this module is star-imported
# via lisscad.prelude. TODO: Transition to __all__.
from typing import Type as _Type
from typing import cast as _cast

import lisscad.data.inter as d

#############
# INTERFACE #
#############


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


def square(size: d.Tuple2D, center: bool = True) -> d.Square:
    return d.Square(size, center)


def sphere(radius: float) -> d.Sphere:
    return d.Sphere(radius)


def cube(size: d.Tuple3D, center: bool = True) -> d.Cube:
    return d.Cube(size, center)


def translate(coord: d.Tuple2D | d.Tuple3D, *children: d.LiteralExpression):
    if len(coord) == 2:
        return d.Translation2D(
            _cast(d.Tuple2D, coord),
            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Translation3D(_cast(d.Tuple3D, coord),
                           _cast(tuple[d.LiteralExpression3D, ...], children))


def rotate(coord: float | int | d.Tuple3D, *children: d.LiteralExpression):
    if isinstance(coord, (float, int)):
        return d.Rotation2D(coord,
                            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Rotation3D(coord,
                        _cast(tuple[d.LiteralExpression3D, ...], children))


def mirror(axes: tuple[int, int, int], *children: d.LiteralExpression):
    if _is_2d(*children):
        return d.Mirror2D(axes,
                          _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Mirror3D(axes, _cast(tuple[d.LiteralExpression3D, ...], children))


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


def children():
    """Place the children of a call to a module inside that module.

    Neither indexing nor counting of children are currently supported.

    """
    return d.ModuleChildren()


############
# INTERNAL #
############


def _is_2d(*expressions):
    assert expressions
    return all(isinstance(e, d.Base2D) for e in expressions)


def _modify(type_2d: _Type[d.BaseModifier2D], type_3d: _Type[d.BaseModifier3D],
            child: d.LiteralExpression) -> d.BaseModifier2D | d.BaseModifier3D:
    """Wrap up a single expression of known dimensionality."""
    if _is_2d(child):
        return type_2d(_cast(d.LiteralExpression2D, child))
    return type_3d(_cast(d.LiteralExpression3D, child))


def _contain(
    type_2d: _Type[d.BaseBoolean2D], type_3d: _Type[d.BaseBoolean3D],
    children: tuple[d.LiteralExpression, ...]
) -> d.BaseBoolean2D | d.BaseBoolean3D:
    """Wrap up 1+ expressions of known dimensionality."""
    if _is_2d(*children):
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
    if _is_2d(*children):
        return d.ModuleDefinition2D(
            name, _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.ModuleDefinition3D(
        name, _cast(tuple[d.LiteralExpression3D, ...], children))


def _call_module(
    name: str, *children: d.LiteralExpression
) -> d.ModuleCall2D | d.ModuleCall3D | d.ModuleCallND:
    if children:
        if _is_2d(*children):
            return d.ModuleCall2D(
                name, _cast(tuple[d.LiteralExpression2D, ...], children))
        return d.ModuleCall3D(
            name, _cast(tuple[d.LiteralExpression3D, ...], children))
    return d.ModuleCallND(name)
