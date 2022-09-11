"""Metadata model, for data that is not OpenSCAD."""

from lisscad.data.inter import LiteralExpression
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    model: LiteralExpression
    name: str = 'untitled'
