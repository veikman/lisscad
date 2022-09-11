"""Metadata model, for data that is not OpenSCAD."""

from lisscad.data.inter import LiteralShape
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    model: LiteralShape
    name: str = 'untitled'
