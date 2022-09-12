"""Intermediate Pythonic precursors to OpenSCAD.

These are intended for manipulation in scad_lissp applications.

"""

from __future__ import annotations

from typing import Union

from pydantic.dataclasses import dataclass

#########
# BASES #
#########

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]


class Base2D:
    pass


class Base3D:
    pass


@dataclass(frozen=True)
class BaseBoolean2D(Base2D):
    children: tuple[LiteralExpression2D, ...]


@dataclass(frozen=True)
class BaseBoolean3D(Base3D):
    children: tuple[LiteralExpression3D, ...]


class BaseTransformation2D(Base2D):
    pass


class BaseTransformation3D(Base3D):
    pass


class BaseShape2D(Base2D):
    pass


class BaseShape3D(Base3D):
    pass


def update_forward_refs(*model):
    """Update forward references on a Pydantic class."""
    for m in model:
        m.__pydantic_model__.update_forward_refs()


###############
# 2D BOOLEANS #
###############


@dataclass(frozen=True)
class Union2D(BaseBoolean2D):
    # An OpenSCAD union. No relation to typing.Union.
    pass


@dataclass(frozen=True)
class Difference2D(BaseBoolean2D):
    pass


@dataclass(frozen=True)
class Intersection2D(BaseBoolean2D):
    pass


LiteralBoolean2D = Union2D | Difference2D | Intersection2D

###############
# 3D BOOLEANS #
###############


@dataclass(frozen=True)
class Union3D(BaseBoolean3D):
    pass


@dataclass(frozen=True)
class Difference3D(BaseBoolean3D):
    pass


@dataclass(frozen=True)
class Intersection3D(BaseBoolean3D):
    pass


LiteralBoolean3D = Union3D | Difference3D | Intersection3D

#############
# 2D SHAPES #
#############


@dataclass(frozen=True)
class Circle(BaseShape2D):
    radius: float


@dataclass(frozen=True)
class Square(BaseShape2D):
    size: Tuple2D
    center: bool


LiteralShape2D = Circle | Square

#############
# 3D SHAPES #
#############


@dataclass(frozen=True)
class Sphere(BaseShape3D):
    radius: float


@dataclass(frozen=True)
class Cube(BaseShape3D):
    size: Tuple3D
    center: bool


LiteralShape3D = Sphere | Cube

######################
# 2D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation2D(BaseTransformation2D):
    coord: Tuple2D
    child: LiteralExpression2D


@dataclass(frozen=True)
class Rotation2D(BaseTransformation2D):
    angle: float
    child: LiteralExpression2D


LiteralTransformation2D = Translation2D | Rotation2D

######################
# 3D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation3D(BaseTransformation3D):
    coord: Tuple3D
    child: LiteralExpression3D


@dataclass(frozen=True)
class Rotation3D(BaseTransformation3D):
    angle: Tuple3D
    child: LiteralExpression3D


LiteralTransformation3D = Translation3D | Rotation3D

##########
# ROSTER #
##########

LiteralExpression2D = Union[LiteralBoolean2D, LiteralShape2D,
                            LiteralTransformation2D]
LiteralExpression3D = Union[LiteralBoolean3D, LiteralShape3D,
                            LiteralTransformation3D]
LiteralExpression = Union[LiteralExpression2D, LiteralExpression3D]

update_forward_refs(Union2D, Union3D, Translation2D, Translation3D)
