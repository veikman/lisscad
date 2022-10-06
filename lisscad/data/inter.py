"""Intermediate Pythonic precursors to OpenSCAD.

These are object-orieneted, intended to provide type safety with some automatic
parsing by Pydantic, an abstraction layer for multiple front-end shorthands,
and strong introspection in applications.

In this data model, angles are uniformly described in radians, as in scad-clj.

"""
from __future__ import annotations

from math import tau
from pathlib import Path
from typing import ClassVar, Literal, Union

from pydantic import PositiveFloat, PositiveInt
from pydantic.dataclasses import dataclass

#########
# BASES #
#########

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]


class SCADTerm:
    """A mix-in for classes that match OpenSCAD’s wording."""

    keyword: ClassVar[str] = ''


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
class BaseBoolean2D(Base2D, SCADTerm):
    children: tuple[LiteralExpressionNon3D, ...]


@dataclass(frozen=True)
class BaseBoolean3D(Base3D, SCADTerm):
    children: tuple[LiteralExpressionNon2D, ...]


class BaseTransformation2D(Base2D):
    pass


class BaseTransformation3D(Base3D):
    pass


@dataclass(frozen=True)
class BaseMirror(BaseExpression, SCADTerm):
    keyword: ClassVar[str] = 'mirror'
    v: tuple[int, int, int]  # Coefficients by axis. Named as in OpenSCAD.


class BaseShape2D(Base2D):
    pass


class BaseShape3D(Base3D):
    pass


@dataclass(frozen=True)
class BaseExtrusion(Base3D):
    children: tuple[LiteralExpressionNon3D, ...]
    convexity: PositiveInt = 1


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


############
# COMMENTS #
############


@dataclass(frozen=True)
class Comment(BaseND):
    content: tuple[str, ...]


@dataclass(frozen=True)
class Commented2D(Base2D):
    comment: Comment
    subject: LiteralExpressionNon3D


@dataclass(frozen=True)
class Commented3D(Base3D):
    comment: Comment
    subject: LiteralExpressionNon2D


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
    # An OpenSCAD union, not a typing.Union.
    keyword: ClassVar[str] = 'union'


@dataclass(frozen=True)
class Difference2D(BaseBoolean2D):
    keyword: ClassVar[str] = 'difference'


@dataclass(frozen=True)
class Intersection2D(BaseBoolean2D):
    keyword: ClassVar[str] = 'intersection'


LiteralBoolean2D = Union2D | Difference2D | Intersection2D

###############
# 3D BOOLEANS #
###############


@dataclass(frozen=True)
class Union3D(BaseBoolean3D):
    keyword: ClassVar[str] = 'union'


@dataclass(frozen=True)
class Difference3D(BaseBoolean3D):
    keyword: ClassVar[str] = 'difference'


@dataclass(frozen=True)
class Intersection3D(BaseBoolean3D):
    keyword: ClassVar[str] = 'intersection'


LiteralBoolean3D = Union3D | Difference3D | Intersection3D

#############
# 2D SHAPES #
#############


@dataclass(frozen=True)
class Circle(BaseShape2D):
    radius: float


@dataclass(frozen=True)
class Square(BaseShape2D, SCADTerm):
    keyword: ClassVar[str] = 'square'
    size: float
    center: bool = False


@dataclass(frozen=True)
class Rectangle(BaseShape2D, SCADTerm):
    keyword: ClassVar[str] = 'square'  # Sic.
    size: Tuple2D
    center: bool = False


@dataclass(frozen=True)
class Polygon(BaseShape2D):
    points: tuple[Tuple2D, ...]
    paths: tuple[tuple[int, ...], ...] = ()
    convexity: PositiveInt = 1


@dataclass(frozen=True)
class Text(BaseShape2D, SCADTerm):
    keyword: ClassVar[str] = 'text'
    text: str
    size: PositiveFloat = 10
    font: str = ''
    halign: Literal['left', 'center', 'right'] = 'left'
    valign: Literal['top', 'center', 'baseline', 'bottom'] = 'baseline'
    spacing: PositiveFloat = 1
    direction: Literal['ltr', 'rtl', 'ttb', 'btt'] = 'ltr'
    language: str = 'en'
    script: str = 'latin'


@dataclass(frozen=True)
class Import2D(BaseShape2D, SCADTerm):
    keyword: ClassVar[str] = 'import'
    file: Path
    layer: str = ''
    convexity: PositiveInt = 1


@dataclass(frozen=True)
class Projection(BaseShape2D, SCADTerm):
    keyword: ClassVar[str] = 'projection'
    child: LiteralExpressionNon2D
    cut: bool = False


LiteralShape2D = (Circle | Square | Rectangle | Polygon | Text | Import2D
                  | Projection)

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


@dataclass(frozen=True)
class Cylinder(BaseShape3D):
    radius: float
    height: float
    center: bool


@dataclass(frozen=True)
class Frustum(BaseShape3D):
    radii: tuple[float, float]
    height: float
    center: bool


@dataclass(frozen=True)
class Polyhedron(BaseShape3D):
    points: tuple[Tuple3D, ...]
    faces: tuple[tuple[int, ...], ...] = ()
    convexity: PositiveInt = 1


@dataclass(frozen=True)
class Import3D(BaseShape3D, SCADTerm):
    keyword: ClassVar[str] = 'import'
    file: Path
    layer: str = ''
    convexity: PositiveInt = 1


@dataclass(frozen=True)
class LinearExtrusion(BaseExtrusion, SCADTerm):
    keyword: ClassVar[str] = 'linear_extrude'
    height: PositiveFloat = 100  # Default not documented in OpenSCAD manual.
    center: bool = False
    twist: float = 0
    slices: PositiveInt | None = None  # Variable default in OpenSCAD.
    scale: PositiveFloat = 1


@dataclass(frozen=True)
class RotationalExtrusion(BaseExtrusion, SCADTerm):
    keyword: ClassVar[str] = 'rotate_extrude'
    angle: float = tau


@dataclass(frozen=True)
class Surface(BaseShape3D, SCADTerm):
    keyword: ClassVar[str] = 'surface'
    file: Path
    center: bool = False
    invert: bool = False
    convexity: PositiveInt = 1


LiteralShape3D = (Sphere | Cube | Cylinder | Frustum | Polyhedron | Import3D
                  | LinearExtrusion | RotationalExtrusion | Surface)

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

LiteralExpression2D = Union[Commented2D, LiteralModifier2D, LiteralBoolean2D,
                            LiteralShape2D, LiteralTransformation2D,
                            LiteralModule2D]
LiteralExpression3D = Union[Commented3D, LiteralModifier3D, LiteralBoolean3D,
                            LiteralShape3D, LiteralTransformation3D,
                            LiteralModule3D]
LiteralExpressionND = Union[Comment, ModuleCallND, ModuleChildren]

LiteralExpressionNon2D = Union[LiteralExpression3D, LiteralExpressionND]
LiteralExpressionNon3D = Union[LiteralExpression2D, LiteralExpressionND]
LiteralExpression = Union[LiteralExpression2D, LiteralExpression3D,
                          LiteralExpressionND]

###############
# FINALIZATON #
###############

update_forward_refs(Commented2D, Background2D, Debug2D, Root2D, Disable2D,
                    Union2D, Difference2D, Intersection2D, Translation2D,
                    Rotation2D, Mirror2D, ModuleDefinition2D, ModuleCall2D,
                    Projection)
update_forward_refs(Commented3D, Background3D, Debug3D, Root3D, Disable3D,
                    Union3D, Difference3D, Intersection3D, Translation3D,
                    Rotation3D, Mirror3D, ModuleDefinition3D, ModuleCall3D,
                    LinearExtrusion, RotationalExtrusion)
