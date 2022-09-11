"""Intermediate Pythonic precursors to OpenSCAD.

These are intended for manipulation in scad_lissp applications.

"""
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Cube:
    size: tuple[float, float, float]
    center: bool
