"""Application model.

This module is intended to be imported from a Lissp script.

"""

from pathlib import Path

from lisscad.data.other import Asset
from lisscad.py_to_scad import transpile

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    return dirpath / f'{asset.name}.scad'


def write(*assets: dict | Asset, dir_scad: Path = DIR_SCAD):
    """Convert intermediate representations to OpenSCAD code."""
    for a in assets:
        if not isinstance(a, Asset):
            a = Asset(**a)
        file_out = _compose_scad_output_path(dir_scad, a)
        file_out.parent.mkdir(parents=True, exist_ok=True)
        file_out.write_text('\n'.join(transpile(a.model)) + '\n')
