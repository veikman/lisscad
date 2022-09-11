"""Metadata model, for data that is not OpenSCAD."""

from lisscad.data.inter import Expression
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    model: Expression
    name: str = 'untitled'
