"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from typing import cast

from lisscad.data import inter


def square(size: inter.Tuple2D, center: bool = True) -> inter.Square:
    return inter.Square(size, center)


def cube(size: inter.Tuple3D, center: bool = True) -> inter.Cube:
    return inter.Cube(size, center)


def translate(coord: inter.Tuple2D | inter.Tuple3D, child: inter.Expression):
    if len(coord) == 2:
        return inter.Translation2D(cast(inter.Tuple2D, coord), child)
    return inter.Translation3D(cast(inter.Tuple3D, coord), child)
