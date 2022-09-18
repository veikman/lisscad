"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from typing import Type as _Type
from typing import cast as _cast

import lisscad.data.inter as d


def _is_2d(*expressions):
    return all(isinstance(e, d.Base2D) for e in expressions)


def _contain(
    type_2d: _Type[d.BaseBoolean2D], type_3d: _Type[d.BaseBoolean3D],
    children: tuple[d.LiteralExpression, ...]
) -> d.BaseBoolean2D | d.BaseBoolean3D:
    if _is_2d(*children):
        return type_2d(_cast(tuple[d.LiteralExpression2D, ...], children))
    return type_3d(_cast(tuple[d.LiteralExpression3D, ...], children))


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


def rotate(coord: float | d.Tuple3D, *children: d.LiteralExpression):
    if isinstance(coord, float):
        return d.Rotation2D(coord,
                            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Rotation3D(coord,
                        _cast(tuple[d.LiteralExpression3D, ...], children))


def background(child: d.LiteralExpression) -> d.Background2D | d.Background3D:
    if _is_2d(child):
        return d.Background2D(_cast(d.LiteralShape2D, child))
    return d.Background3D(_cast(d.LiteralShape3D, child))
