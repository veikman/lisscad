"""Intermediate Pythonic precursors to OpenSCAD.

These are object-oriented, intended to provide type safety with some automatic
parsing by Pydantic, an abstraction layer for multiple front-end shorthands,
and strong introspection in applications.

In this data model, angles are uniformly described in radians, as in scad-clj.

"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import tau
from pathlib import Path
from typing import ClassVar, Literal, Union

from pydantic import PositiveFloat, PositiveInt
from pydantic.dataclasses import dataclass as dantaclass

############
# METADATA #
############


@dataclass(frozen=True)
class SCADAdapter:
    """Metadata specific to OpenSCAD, built into a precursor class."""

    keyword: str
    container: str = ''  # Name of field for contents.
    field_names: dict[str, str] = field(default_factory=dict)


#########
# BASES #
#########

Tuple2D = tuple[float, float]
Tuple3D = tuple[float, float, float]
Tuple4D = tuple[float, float, float, float]


@dantaclass(frozen=True)
class SCADTerm:
    """A mix-in for classes that match OpenSCAD’s wording."""

    scad: ClassVar[SCADAdapter]


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


@dantaclass(frozen=True)
class BaseModifier2D(Base2D, BaseModifier):
    child: LiteralExpressionNon3D


@dantaclass(frozen=True)
class BaseModifier3D(Base3D, BaseModifier):
    child: LiteralExpressionNon2D


@dantaclass(frozen=True)
class BaseBoolean2D(Base2D, SCADTerm):
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class BaseBoolean3D(Base3D, SCADTerm):
    children: tuple[LiteralExpressionNon2D, ...]


class BaseTransformation2D(Base2D):
    pass


class BaseTransformation3D(Base3D):
    pass


@dantaclass(frozen=True)
class BaseMirror(BaseExpression, SCADTerm):
    scad = SCADAdapter('mirror', 'children', {'vector': 'v'})
    vector: tuple[int, int, int]  # Coefficients by axis.


class BaseShape2D(Base2D):
    pass


class BaseShape3D(Base3D):
    pass


@dantaclass(frozen=True)
class BaseExtrusion(Base3D):
    children: tuple[LiteralExpressionNon3D, ...]
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class BaseModuleDefinition(BaseExpression):
    name: str


@dantaclass(frozen=True)
class BaseModuleCall(BaseExpression):
    name: str


################################
# COMMENTS, ECHOES AND SIMILAR #
################################


@dantaclass(frozen=True)
class Comment(BaseND):
    content: tuple[str, ...]


@dantaclass(frozen=True)
class Commented2D(Base2D):
    comment: Comment
    subject: LiteralExpressionNon3D


@dantaclass(frozen=True)
class Commented3D(Base3D):
    comment: Comment
    subject: LiteralExpressionNon2D


@dantaclass(frozen=True)
class SpecialVariable(BaseND):
    variable: str
    assignment_preview: float | None = None
    assignment_render: float | None = None


@dantaclass(frozen=True)
class Echo(BaseND):
    content: tuple[str, ...]


################
# 2D MODIFIERS #
################


@dantaclass(frozen=True)
class Background2D(BaseModifier2D):
    pass


@dantaclass(frozen=True)
class Debug2D(BaseModifier2D):
    pass


@dantaclass(frozen=True)
class Root2D(BaseModifier2D):
    pass


@dantaclass(frozen=True)
class Disable2D(BaseModifier2D):
    pass


LiteralModifier2D = Background2D | Debug2D | Root2D | Disable2D

################
# 3D MODIFIERS #
################


@dantaclass(frozen=True)
class Background3D(BaseModifier3D):
    pass


@dantaclass(frozen=True)
class Debug3D(BaseModifier3D):
    pass


@dantaclass(frozen=True)
class Root3D(BaseModifier3D):
    pass


@dantaclass(frozen=True)
class Disable3D(BaseModifier3D):
    pass


LiteralModifier3D = Background3D | Debug3D | Root3D | Disable3D

###############
# 2D BOOLEANS #
###############


@dantaclass(frozen=True)
class Union2D(BaseBoolean2D):
    # An OpenSCAD union, not a typing.Union.
    scad = SCADAdapter('union', 'children')


@dantaclass(frozen=True)
class Difference2D(BaseBoolean2D):
    scad = SCADAdapter('difference', 'children')


@dantaclass(frozen=True)
class Intersection2D(BaseBoolean2D):
    scad = SCADAdapter('intersection', 'children')


LiteralBoolean2D = Union2D | Difference2D | Intersection2D

###############
# 3D BOOLEANS #
###############


@dantaclass(frozen=True)
class Union3D(BaseBoolean3D):
    scad = SCADAdapter('union', 'children')


@dantaclass(frozen=True)
class Difference3D(BaseBoolean3D):
    scad = SCADAdapter('difference', 'children')


@dantaclass(frozen=True)
class Intersection3D(BaseBoolean3D):
    scad = SCADAdapter('intersection', 'children')


LiteralBoolean3D = Union3D | Difference3D | Intersection3D

#############
# 2D SHAPES #
#############


@dantaclass(frozen=True)
class Circle(BaseShape2D, SCADTerm):
    scad = SCADAdapter('circle', field_names={'radius': 'r'})
    radius: float


@dantaclass(frozen=True)
class Square(BaseShape2D, SCADTerm):
    scad = SCADAdapter('square')
    size: float
    center: bool = False


@dantaclass(frozen=True)
class Rectangle(BaseShape2D, SCADTerm):
    scad = SCADAdapter('square')  # Sic.
    size: Tuple2D
    center: bool = False


@dantaclass(frozen=True)
class Polygon(BaseShape2D, SCADTerm):
    scad = SCADAdapter('polygon')
    points: tuple[Tuple2D, ...]
    paths: tuple[tuple[int, ...], ...] = ()
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class Text(BaseShape2D, SCADTerm):
    scad = SCADAdapter('text')
    text: str
    size: PositiveFloat = 10
    font: str = ''
    halign: Literal['left', 'center', 'right'] = 'left'
    valign: Literal['top', 'center', 'baseline', 'bottom'] = 'baseline'
    spacing: PositiveFloat = 1
    direction: Literal['ltr', 'rtl', 'ttb', 'btt'] = 'ltr'
    language: str = 'en'
    script: str = 'latin'


@dantaclass(frozen=True)
class Import2D(BaseShape2D, SCADTerm):
    scad = SCADAdapter('import')
    file: Path
    layer: str = ''
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class Projection(BaseShape2D, SCADTerm):
    scad = SCADAdapter('projection', 'child')
    child: LiteralExpressionNon2D
    cut: bool = False


LiteralShape2D = (
    Circle | Square | Rectangle | Polygon | Text | Import2D | Projection
)

#############
# 3D SHAPES #
#############


@dantaclass(frozen=True)
class Sphere(BaseShape3D, SCADTerm):
    scad = SCADAdapter('sphere', field_names={'radius': 'r'})
    radius: float


@dantaclass(frozen=True)
class Cube(BaseShape3D, SCADTerm):
    scad = SCADAdapter('cube')
    size: Tuple3D
    center: bool = False


@dantaclass(frozen=True)
class Cylinder(BaseShape3D, SCADTerm):
    scad = SCADAdapter('cylinder', field_names={'radius': 'r', 'height': 'h'})
    radius: float
    height: float
    center: bool = False


@dantaclass(frozen=True)
class Frustum(BaseShape3D, SCADTerm):
    scad = SCADAdapter(
        'cylinder',
        field_names={'radius_bottom': 'r1', 'radius_top': 'r2', 'height': 'h'},
    )
    radius_bottom: float
    radius_top: float
    height: float
    center: bool = False


@dantaclass(frozen=True)
class Polyhedron(BaseShape3D, SCADTerm):
    scad = SCADAdapter('polyhedron')
    points: tuple[Tuple3D, ...]
    faces: tuple[tuple[int, ...], ...] = ()
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class Import3D(BaseShape3D, SCADTerm):
    scad = SCADAdapter('import')
    file: Path
    layer: str = ''
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class LinearExtrusion(BaseExtrusion, SCADTerm):
    scad = SCADAdapter('linear_extrude', 'children')
    height: PositiveFloat = 100  # Default not documented in OpenSCAD manual.
    center: bool = False
    twist: float = 0
    slices: PositiveInt | None = None  # Variable default in OpenSCAD.
    scale: PositiveFloat = 1


@dantaclass(frozen=True)
class RotationalExtrusion(BaseExtrusion, SCADTerm):
    scad = SCADAdapter('rotate_extrude', 'children')
    angle: float = tau  # Not called “a” in OpenSCAD.


@dantaclass(frozen=True)
class Surface(BaseShape3D, SCADTerm):
    scad = SCADAdapter('surface')
    file: Path
    center: bool = False
    invert: bool = False
    convexity: PositiveInt = 1


LiteralShape3D = (
    Sphere
    | Cube
    | Cylinder
    | Frustum
    | Polyhedron
    | Import3D
    | LinearExtrusion
    | RotationalExtrusion
    | Surface
)

######################
# 2D TRANSFORMATIONS #
######################


@dantaclass(frozen=True)
class Translation2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('translate', 'children', {'vector': 'v'})
    vector: Tuple2D
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class Rotation2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('rotate', 'children', {'angle': 'a'})
    angle: float  # Called “a” in OpenSCAD; cf. RotationalExtrusion.
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class Scaling2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('scale', 'children', {'vector': 'v'})
    vector: Tuple2D
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class Size2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('resize', 'children', {'vector': 'newsize'})
    vector: Tuple2D
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class Mirror2D(BaseTransformation2D, BaseMirror):
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class AffineTransformation2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('multmatrix', 'children', {'matrix': 'm'})
    matrix: tuple[Tuple4D, ...]
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class Color2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('color', 'children', {'color': 'c'})
    color: Tuple4D | str
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class RoundedOffset(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('offset', 'children', {'distance': 'r'})
    distance: float
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class AngledOffset(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('offset', 'children', {'distance': 'delta'})
    distance: float
    children: tuple[LiteralExpressionNon3D, ...]
    chamfer: bool = False


@dantaclass(frozen=True)
class Hull2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('hull', 'children')
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class MinkowskiSum2D(BaseTransformation2D, SCADTerm):
    scad = SCADAdapter('minkowski', 'children')
    children: tuple[LiteralExpressionNon3D, ...]
    convexity: PositiveInt = 1


LiteralTransformation2D = (
    Translation2D
    | Rotation2D
    | Scaling2D
    | Size2D
    | Mirror2D
    | AffineTransformation2D
    | Color2D
    | RoundedOffset
    | AngledOffset
    | Hull2D
    | MinkowskiSum2D
)

######################
# 3D TRANSFORMATIONS #
######################


@dantaclass(frozen=True)
class Translation3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('translate', 'children', {'vector': 'v'})
    vector: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Rotation3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('rotate', 'children', {'angle': 'a'})
    angle: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Scaling3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('scale', 'children', {'vector': 'v'})
    vector: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Size3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('resize', 'children', {'vector': 'newsize'})
    vector: Tuple3D
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Mirror3D(BaseTransformation3D, BaseMirror):
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class AffineTransformation3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('multmatrix', 'children', {'matrix': 'm'})
    matrix: tuple[Tuple4D, ...]
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Color3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('color', 'children', {'color': 'c'})
    color: Tuple4D | str
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class Hull3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('hull', 'children')
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class MinkowskiSum3D(BaseTransformation3D, SCADTerm):
    scad = SCADAdapter('minkowski', 'children')
    children: tuple[LiteralExpressionNon2D, ...]
    convexity: PositiveInt = 1


@dantaclass(frozen=True)
class Rendering3D(BaseTransformation3D, SCADTerm):
    # A “render” operation does not change geometry and is not listed as a
    # transformation in the OpenSCAD cheat sheet, but is applied like one.
    scad = SCADAdapter('render', 'children')
    children: tuple[LiteralExpressionNon2D, ...]
    convexity: PositiveInt = 1


LiteralTransformation3D = (
    Translation3D
    | Rotation3D
    | Scaling3D
    | Size3D
    | Mirror3D
    | AffineTransformation3D
    | Color3D
    | Hull3D
    | MinkowskiSum3D
    | Rendering3D
)

##############
# 2D MODULES #
##############


@dantaclass(frozen=True)
class ModuleDefinition2D(Base2D, BaseModuleDefinition):
    children: tuple[LiteralExpressionNon3D, ...]


@dantaclass(frozen=True)
class ModuleCall2D(Base2D, BaseModuleCall):
    children: tuple[LiteralExpressionNon3D, ...]


LiteralModule2D = ModuleDefinition2D | ModuleCall2D

##############
# 3D MODULES #
##############


@dantaclass(frozen=True)
class ModuleDefinition3D(Base3D, BaseModuleDefinition):
    children: tuple[LiteralExpressionNon2D, ...]


@dantaclass(frozen=True)
class ModuleCall3D(Base3D, BaseModuleCall):
    children: tuple[LiteralExpressionNon2D, ...]


LiteralModule3D = ModuleDefinition3D | ModuleCall3D

###########################
# ANY-DIMENSIONAL MODULES #
###########################


@dantaclass(frozen=True)
class ModuleCallND(BaseND, BaseModuleCall):
    pass


@dantaclass(frozen=True)
class ModuleChildren(BaseND):
    pass


##########
# ROSTER #
##########

LiteralExpression2D = Union[
    Commented2D,
    LiteralModifier2D,
    LiteralBoolean2D,
    LiteralShape2D,
    LiteralTransformation2D,
    LiteralModule2D,
]
LiteralExpression3D = Union[
    Commented3D,
    LiteralModifier3D,
    LiteralBoolean3D,
    LiteralShape3D,
    LiteralTransformation3D,
    LiteralModule3D,
]
LiteralExpressionND = Union[
    Comment, SpecialVariable, Echo, ModuleCallND, ModuleChildren
]

LiteralExpressionNon2D = Union[LiteralExpression3D, LiteralExpressionND]
LiteralExpressionNon3D = Union[LiteralExpression2D, LiteralExpressionND]
LiteralExpression = Union[
    LiteralExpression2D, LiteralExpression3D, LiteralExpressionND
]
