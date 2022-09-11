"""Intermediate Pythonic precursors to OpenSCAD.

These are intended for manipulation in scad_lissp applications.

"""

from __future__ import annotations

from pydantic.dataclasses import dataclass

#########
# BASES #
#########

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]


class Boolean:
    pass


class Transformation2D:
    pass


class Transformation3D:
    pass


class Shape2D:
    pass


class Shape3D:
    pass


def update_forward_refs(*model):
    """Update forward references on a Pydantic class."""
    for m in model:
        m.__pydantic_model__.update_forward_refs()


#############
# 2D SHAPES #
#############


@dataclass(frozen=True)
class Square(Shape2D):
    size: Tuple2D
    center: bool


LiteralShape2D = Square

#############
# 3D SHAPES #
#############


@dataclass(frozen=True)
class Cube(Shape3D):
    size: Tuple3D
    center: bool


LiteralShape3D = Cube

######################
# 2D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation2D(Transformation2D):
    coord: Tuple2D
    child: Expression


LiteralTransformation2D = Translation2D

######################
# 3D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation3D(Transformation3D):
    coord: Tuple3D
    child: Expression


LiteralTransformation3D = Translation3D

##########
# ROSTER #
##########

Expression = (LiteralShape2D | LiteralShape3D | LiteralTransformation2D
              | LiteralTransformation3D)

update_forward_refs(Translation2D, Translation3D)
