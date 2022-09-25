"""Metadata model, for data that is not OpenSCAD."""

from __future__ import annotations

from typing import Callable, cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from pydantic import validator
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """A CAD asset composed of zero or more OpenSCAD models."""
    content: Callable[[], tuple[LiteralExpression, ...]]

    name: str = 'untitled'
    modules: tuple[Asset, ...] = ()
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
            value = (value, )
        elif isinstance(value, list):
            value = tuple(value)

        if isinstance(value, tuple):
            return lambda: cast(tuple[LiteralExpression, ...], value)

        raise TypeError(
            f'{type(value)} cannot form the content of a lisscad asset.')

    @validator('modules', pre=True)
    def _modules_to_assets(cls, value):
        """Accept and package a single dict or instance.

        This flexibility is a convenience for use in CAD scripts.

        """
        if not isinstance(value, (tuple, list)):
            value = (value, )
        return value
