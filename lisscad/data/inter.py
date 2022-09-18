"""Intermediate Pythonic precursors to OpenSCAD.

These are object-orieneted, intended to provide type safety with some automatic
parsing by Pydantic, an abstraction layer for multiple front-end shorthands,
and strong introspection in applications.

"""

from __future__ import annotations

from typing import Union

from pydantic.dataclasses import dataclass

#########
# BASES #
#########

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]


class BaseExpression:
    """A base class for all of lisscad’s precursors."""


class Base2D(BaseExpression):
    pass


class Base3D(BaseExpression):
    pass


class BaseModifier(BaseExpression):
    """A modifier such as “%”, “#” or “!”. Scoped for just one expression."""


@dataclass(frozen=True)
class BaseModifier2D(Base2D, BaseModifier):
    child: LiteralExpression2D


@dataclass(frozen=True)
class BaseModifier3D(Base3D, BaseModifier):
    child: LiteralExpression3D


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
    """Update forward references on Pydantic classes."""
    for m in model:
        m.__pydantic_model__.update_forward_refs()


################
# 2D MODIFIERS #
################


@dataclass(frozen=True)
class Background2D(BaseModifier2D):
    pass


@dataclass(frozen=True)
class Debug2D(BaseModifier2D):
    pass


@dataclass(frozen=True)
class Root2D(BaseModifier2D):
    pass


LiteralModifier2D = Background2D | Debug2D | Root2D

################
# 3D MODIFIERS #
################


@dataclass(frozen=True)
class Background3D(BaseModifier3D):
    pass


@dataclass(frozen=True)
class Debug3D(BaseModifier3D):
    pass


@dataclass(frozen=True)
class Root3D(BaseModifier3D):
    pass


LiteralModifier3D = Background3D | Debug3D | Root3D

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
    children: tuple[LiteralExpression2D, ...]


@dataclass(frozen=True)
class Rotation2D(BaseTransformation2D):
    angle: float
    children: tuple[LiteralExpression2D, ...]


LiteralTransformation2D = Translation2D | Rotation2D

######################
# 3D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation3D(BaseTransformation3D):
    coord: Tuple3D
    children: tuple[LiteralExpression3D, ...]


@dataclass(frozen=True)
class Rotation3D(BaseTransformation3D):
    angle: Tuple3D
    children: tuple[LiteralExpression3D, ...]


LiteralTransformation3D = Translation3D | Rotation3D

##########
# ROSTER #
##########

LiteralExpression2D = Union[LiteralModifier2D, LiteralBoolean2D,
                            LiteralShape2D, LiteralTransformation2D]
LiteralExpression3D = Union[LiteralModifier3D, LiteralBoolean3D,
                            LiteralShape3D, LiteralTransformation3D]
LiteralExpression = Union[LiteralExpression2D, LiteralExpression3D]

update_forward_refs(Background2D, Debug2D, Root2D, Background3D, Debug3D,
                    Root3D, Union2D, Union3D, Difference2D, Difference3D,
                    Intersection2D, Intersection3D, Translation2D,
                    Translation3D)
