"""A Lissp interface to the intermediate data model.

This interface is patterned after scad-clj.

"""

from lisscad.data import inter


def cube(size: tuple[float, float, float], center: bool = True):
    return inter.Cube(size, center)
