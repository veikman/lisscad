"""Metadata model, for data that is not OpenSCAD."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, cast

from lisscad.data.inter import BaseExpression, LiteralExpression, Tuple3D
from pydantic import PositiveFloat, validator
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Gimbal:
    """A gimbal camera setup."""

    translation: Tuple3D
    rotation: Tuple3D
    distance: PositiveFloat


@dataclass(frozen=True)
class Vector:
    """A vector camera setup."""

    eye: Tuple3D
    center: Tuple3D = (0, 0, 0)


@dataclass(frozen=True)
class Image:
    """A two-dimensional picture of an asset."""

    path: Path  # Relative to render directory.
    camera: Gimbal | Vector | None = None
    size: tuple[int, int] | None = None
    colorscheme: str = ''


@dataclass(frozen=True)
class Asset:
    """A CAD asset composed of zero or more OpenSCAD models."""

    content: Callable[[], tuple[LiteralExpression, ...]]

    name: str = 'untitled'
    modules: tuple[Asset, ...] = ()
    suffixes: tuple[str, ...] = ('.stl',)
    images: tuple[Image, ...] = ()
    chiral: bool = False
    mirrored: bool = False

    @validator('content', pre=True)
    def _content_to_thunk(cls, value):
        """Convert content to a maker of a tuple.

        This flexibility is a convenience for use in CAD scripts.

        """
        if callable(value):
            # Assume nullary. Assume valid output.
            return value

        if isinstance(value, BaseExpression):
            value = (value,)
        elif isinstance(value, list):
            value = tuple(value)

        if isinstance(value, tuple):
            return lambda: cast(tuple[LiteralExpression, ...], value)

        raise TypeError(
            f'{type(value)} cannot form the content of a lisscad asset.'
        )

    @validator('modules', pre=True)
    def _modules_to_assets(cls, value):
        """Accept and package a single dict or instance.

        This flexibility is a convenience for use in CAD scripts.

        """
        if not isinstance(value, (tuple, list)):
            value = (value,)
        return value
