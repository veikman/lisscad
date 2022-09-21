"""Metadata model, for data that is not OpenSCAD."""

from typing import Callable

from lisscad.data.inter import BaseExpression, LiteralExpression
from pydantic import validator
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    content: Callable[[], tuple[LiteralExpression, ...]]
    name: str = 'untitled'

    chiral: bool = False
    mirrored: bool = False

    @validator('content', pre=True)
    def _to_list(cls, value):
        """Convert content to a maker of a tuple.

        This flexibility is a convenience for use in CAD scripts.

        """
        if isinstance(value, BaseExpression):
            value = (value, )
        if isinstance(value, tuple):
            return lambda: value

        return value
