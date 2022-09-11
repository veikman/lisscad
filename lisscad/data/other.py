"""Metadata model, for data that is not OpenSCAD."""

from pydantic.dataclasses import dataclass
from lisscad.data.inter import Cube


@dataclass(frozen=True)
class Asset:
    model: Cube  # Placeholder.
    name: str = 'untitled'
