"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from typing import cast as _cast

import lisscad.data.inter as d


def union(*children: d.LiteralExpression) -> d.Union2D | d.Union3D:
    if all(isinstance(c, d.Base2D) for c in children):
        return d.Union2D(_cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Union3D(_cast(tuple[d.LiteralExpression3D, ...], children))


def difference(
        *children: d.LiteralExpression) -> d.Difference2D | d.Difference3D:
    if all(isinstance(c, d.Base2D) for c in children):
        return d.Difference2D(
            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Difference3D(_cast(tuple[d.LiteralExpression3D, ...], children))


def intersection(
        *children: d.LiteralExpression) -> d.Intersection2D | d.Intersection3D:
    if all(isinstance(c, d.Base2D) for c in children):
        return d.Intersection2D(
            _cast(tuple[d.LiteralExpression2D, ...], children))
    return d.Intersection3D(_cast(tuple[d.LiteralExpression3D, ...], children))


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
