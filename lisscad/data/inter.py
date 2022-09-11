"""Intermediate Pythonic precursors to OpenSCAD.

These are intended for manipulation in scad_lissp applications.

"""

from pydantic.dataclasses import dataclass

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]


class Transformation2D:
    pass


class Transformation3D:
    pass


class Shape2D:
    pass


class Shape3D:
    pass


@dataclass(frozen=True)
class Cube(Shape3D):
    size: Tuple3D
    center: bool


LiteralShape3D = Cube


@dataclass(frozen=True)
class Translation3D(Transformation3D):
    coord: Tuple3D
    child: LiteralShape3D


LiteralTransformation3D = Translation3D

LiteralShape = LiteralShape3D | LiteralTransformation3D
