"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from typing import cast

from lisscad.data import inter


def union(*children: inter.LiteralExpression) -> inter.Union2D | inter.Union3D:
    if all(isinstance(c, inter.Base2D) for c in children):
        return inter.Union2D(cast(tuple[inter.LiteralExpression2D], children))
    if all(isinstance(c, inter.Base3D) for c in children):
        return inter.Union3D(cast(tuple[inter.LiteralExpression3D], children))
    # TODO: Probably move validation into Pydantic model.
    raise TypeError('Mixed dimensionalities in union.')


def square(size: inter.Tuple2D, center: bool = True) -> inter.Square:
    return inter.Square(size, center)


def cube(size: inter.Tuple3D, center: bool = True) -> inter.Cube:
    return inter.Cube(size, center)


def translate(coord: inter.Tuple2D | inter.Tuple3D,
              child: inter.LiteralExpression):
    if len(coord) == 2:
        return inter.Translation2D(cast(inter.Tuple2D, coord),
                                   cast(inter.LiteralExpression2D, child))
    return inter.Translation3D(cast(inter.Tuple3D, coord),
                               cast(inter.LiteralExpression3D, child))
