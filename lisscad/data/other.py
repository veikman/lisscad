"""Metadata model, for data that is not OpenSCAD."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, cast

from lisscad.data.inter import BaseExpression, LiteralExpression, Tuple3D
from pydantic import PositiveFloat
from pydantic.dataclasses import dataclass
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


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

    content: Annotated[
        Callable[[], tuple[LiteralExpression, ...]],
        BeforeValidator(_content_thunk),
    ]

    name: str = 'untitled'
    modules: Annotated[
        tuple[Asset, ...], BeforeValidator(_modules_to_assets)
    ] = ()
    suffixes: tuple[str, ...] = ('.stl',)
    images: tuple[Image, ...] = ()
    chiral: bool = False
    mirrored: bool = False


def _content_thunk(v: Any) -> Callable[[], tuple[LiteralExpression, ...]]:
    """Convert content to a thunk that makes a tuple.

    This flexibility is a convenience for use in CAD scripts.

    """
    if callable(v):
        # Assume nullary. Assume valid output.
        return v

    if isinstance(v, BaseExpression):
        v = (v,)
    elif isinstance(v, list):
        v = tuple(v)

    if isinstance(v, tuple):
        return lambda: cast(tuple[LiteralExpression, ...], v)

    raise TypeError(f'{type(v)} cannot form the content of a lisscad asset.')


def _modules_to_assets(
    v: Asset | tuple[Asset, ...] | list[Asset]
) -> tuple[Asset, ...] | list[Asset]:
    """Accept and package a single dict or instance.

    This flexibility is a convenience for use in CAD scripts.

    """
    if not isinstance(v, (tuple, list)):
        v = (v,)
    return v
