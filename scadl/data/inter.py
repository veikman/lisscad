"""Intermediate Pythonic precursors to OpenSCAD.

These are intended for manipulation in scad_lissp applications.

"""

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Tuple2D:
    x: float
    y: float


@dataclass(frozen=True)
class Tuple3D:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Cube:
    size: Tuple3D
    center: bool = True
