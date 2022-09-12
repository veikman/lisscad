"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from typing import cast

from lisscad.data.inter import (Base2D, Circle, Cube, Difference2D,
                                Difference3D, Intersection2D, Intersection3D,
                                LiteralExpression, LiteralExpression2D,
                                LiteralExpression3D, Rotation2D, Rotation3D,
                                Sphere, Square, Translation2D, Translation3D,
                                Tuple2D, Tuple3D, Union2D, Union3D)


def union(*children: LiteralExpression) -> Union2D | Union3D:
    if all(isinstance(c, Base2D) for c in children):
        return Union2D(cast(tuple[LiteralExpression2D, ...], children))
    return Union3D(cast(tuple[LiteralExpression3D, ...], children))


def difference(*children: LiteralExpression) -> Difference2D | Difference3D:
    if all(isinstance(c, Base2D) for c in children):
        return Difference2D(cast(tuple[LiteralExpression2D, ...], children))
    return Difference3D(cast(tuple[LiteralExpression3D, ...], children))


def intersection(
        *children: LiteralExpression) -> Intersection2D | Intersection3D:
    if all(isinstance(c, Base2D) for c in children):
        return Intersection2D(cast(tuple[LiteralExpression2D, ...], children))
    return Intersection3D(cast(tuple[LiteralExpression3D, ...], children))


def circle(radius: float) -> Circle:
    return Circle(radius)


def square(size: Tuple2D, center: bool = True) -> Square:
    return Square(size, center)


def sphere(radius: float) -> Sphere:
    return Sphere(radius)


def cube(size: Tuple3D, center: bool = True) -> Cube:
    return Cube(size, center)


def translate(coord: Tuple2D | Tuple3D, *children: LiteralExpression):
    if len(coord) == 2:
        return Translation2D(cast(Tuple2D, coord),
                             cast(tuple[LiteralExpression2D, ...], children))
    return Translation3D(cast(Tuple3D, coord),
                         cast(tuple[LiteralExpression3D, ...], children))


def rotate(coord: float | Tuple3D, *children: LiteralExpression):
    if isinstance(coord, float):
        return Rotation2D(coord, cast(tuple[LiteralExpression2D, ...],
                                      children))
    return Rotation3D(coord, cast(tuple[LiteralExpression3D, ...], children))
