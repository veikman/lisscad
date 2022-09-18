"""Application model.

This module is intended to be imported from a Lissp script.

"""

from itertools import count
from pathlib import Path
from typing import cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset
from lisscad.py_to_scad import transpile

#############
# INTERFACE #
#############

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'


def write(*assets: Asset | dict | BaseExpression, dir_scad: Path = DIR_SCAD):
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts.

    """
    invocation_ordinal = next(_INVOCATION_ORDINAL)
    _asset_ordinal = count()

    for a in assets:
        asset_ordinal = next(_asset_ordinal)

        if isinstance(a, Asset):
            pass
        elif isinstance(a, dict):
            a = Asset(**a)
        elif isinstance(a, BaseExpression):
            a = Asset(model=cast(LiteralExpression, a),
                      name=f'untitled_{invocation_ordinal}_{asset_ordinal}')
        else:
            raise TypeError(f'Unable to process {a!r} as a lisscad asset.')

        file_out = _compose_scad_output_path(dir_scad, a)
        file_out.parent.mkdir(parents=True, exist_ok=True)
        file_out.write_text('\n'.join(transpile(a.model)) + '\n')


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    return dirpath / f'{asset.name}.scad'
