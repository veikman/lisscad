"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from lisscad.data import inter


def cube(size: inter.Tuple3D, center: bool = True) -> inter.Cube:
    return inter.Cube(size, center)


def translate(coord: inter.Tuple3D, child: inter.LiteralShape3D):
    return inter.Translation3D(coord, child)
