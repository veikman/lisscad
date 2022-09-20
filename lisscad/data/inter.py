"""Intermediate Pythonic precursors to OpenSCAD.

These are object-orieneted, intended to provide type safety with some automatic
parsing by Pydantic, an abstraction layer for multiple front-end shorthands,
and strong introspection in applications.

In this data model, angles are uniformly described in radians, as in scad-clj.

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


class BaseND(BaseExpression):
    pass


class BaseModifier(BaseExpression):
    """A modifier such as “%”, “#” or “!”. Scoped for just one expression."""


@dataclass(frozen=True)
class BaseModifier2D(Base2D, BaseModifier):
    child: LiteralExpressionNon3D


@dataclass(frozen=True)
class BaseModifier3D(Base3D, BaseModifier):
    child: LiteralExpressionNon2D


@dataclass(frozen=True)
class BaseBoolean2D(Base2D):
    children: tuple[LiteralExpressionNon3D, ...]


@dataclass(frozen=True)
class BaseBoolean3D(Base3D):
    children: tuple[LiteralExpressionNon2D, ...]


class BaseTransformation2D(Base2D):
    pass


class BaseTransformation3D(Base3D):
    pass


@dataclass(frozen=True)
class BaseMirror(BaseExpression):
    axes: tuple[int, int, int]


class BaseShape2D(Base2D):
    pass


class BaseShape3D(Base3D):
    pass


@dataclass(frozen=True)
class BaseModuleDefinition(BaseExpression):
    name: str


@dataclass(frozen=True)
class BaseModuleCall(BaseExpression):
    name: str


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


@dataclass(frozen=True)
class Disable2D(BaseModifier2D):
    pass


LiteralModifier2D = Background2D | Debug2D | Root2D | Disable2D

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


@dataclass(frozen=True)
class Disable3D(BaseModifier3D):
    pass


LiteralModifier3D = Background3D | Debug3D | Root3D | Disable3D

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
    children: tuple[LiteralExpressionNon3D, ...]


@dataclass(frozen=True)
class Rotation2D(BaseTransformation2D):
    angle: float
    children: tuple[LiteralExpressionNon3D, ...]


@dataclass(frozen=True)
class Mirror2D(BaseTransformation2D, BaseMirror):
    children: tuple[LiteralExpressionNon3D, ...]


LiteralTransformation2D = Translation2D | Rotation2D | Mirror2D

######################
# 3D TRANSFORMATIONS #
######################


@dataclass(frozen=True)
class Translation3D(BaseTransformation3D):
    coord: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dataclass(frozen=True)
class Rotation3D(BaseTransformation3D):
    angle: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dataclass(frozen=True)
class Mirror3D(BaseTransformation3D, BaseMirror):
    children: tuple[LiteralExpressionNon2D, ...]


LiteralTransformation3D = Translation3D | Rotation3D | Mirror3D

##############
# 2D MODULES #
##############


@dataclass(frozen=True)
class ModuleDefinition2D(Base2D, BaseModuleDefinition):
    children: tuple[LiteralExpressionNon3D, ...]


@dataclass(frozen=True)
class ModuleCall2D(Base2D, BaseModuleCall):
    children: tuple[LiteralExpressionNon3D, ...]


LiteralModule2D = ModuleDefinition2D | ModuleCall2D

##############
# 3D MODULES #
##############


@dataclass(frozen=True)
class ModuleDefinition3D(Base3D, BaseModuleDefinition):
    children: tuple[LiteralExpressionNon2D, ...]


@dataclass(frozen=True)
class ModuleCall3D(Base3D, BaseModuleCall):
    children: tuple[LiteralExpressionNon2D, ...]


LiteralModule3D = ModuleDefinition3D | ModuleCall3D

###########################
# ANY-DIMENSIONAL MODULES #
###########################


@dataclass(frozen=True)
class ModuleCallND(BaseND, BaseModuleCall):
    pass


@dataclass(frozen=True)
class ModuleChildren(BaseND):
    pass


##########
# ROSTER #
##########

LiteralExpression2D = Union[LiteralModifier2D, LiteralBoolean2D,
                            LiteralShape2D, LiteralTransformation2D,
                            LiteralModule2D]
LiteralExpression3D = Union[LiteralModifier3D, LiteralBoolean3D,
                            LiteralShape3D, LiteralTransformation3D,
                            LiteralModule3D]
LiteralExpressionND = Union[ModuleCallND, ModuleChildren]

LiteralExpressionNon2D = Union[LiteralExpression3D, LiteralExpressionND]
LiteralExpressionNon3D = Union[LiteralExpression2D, LiteralExpressionND]
LiteralExpression = Union[LiteralExpression2D, LiteralExpression3D,
                          LiteralExpressionND]

###############
# FINALIZATON #
###############

update_forward_refs(Background2D, Debug2D, Root2D, Disable2D, Union2D,
                    Difference2D, Intersection2D, Translation2D, Rotation2D,
                    Mirror2D,
                    ModuleDefinition2D, ModuleCall2D)
update_forward_refs(Background3D, Debug3D, Root3D, Disable3D, Union3D,
                    Difference3D, Intersection3D, Translation3D, Rotation3D,
                    Mirror3D,
                    ModuleDefinition3D, ModuleCall3D)
