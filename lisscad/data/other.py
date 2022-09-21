"""Metadata model, for data that is not OpenSCAD."""

from lisscad.data.inter import BaseExpression, LiteralExpression
from pydantic import validator
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    content: tuple[LiteralExpression, ...]
    name: str = 'untitled'

    chiral: bool = False
    mirrored: bool = False

    @validator('content', pre=True)
    def _to_list(cls, value):
        """Convert content to a tuple if it’s just one expression.

        This is a convenience for use in CAD scripts.

        """
        if isinstance(value, BaseExpression):
            return (value, )
        return value
