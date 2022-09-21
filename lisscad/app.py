"""Application model.

This module is intended to be imported from a Lissp script.

"""

from itertools import count
from pathlib import Path
from typing import Callable, cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset
from lisscad.py_to_scad import transpile

#############
# INTERFACE #
#############

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'


def write(*assets: Asset | dict | BaseExpression | list[BaseExpression],
          dir_scad: Path = DIR_SCAD):
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts.

    """
    n_invocation = next(_INVOCATION_ORDINAL)
    _asset_ordinal = count()

    for raw in assets:
        asset = _package_asset(raw, n_invocation, next(_asset_ordinal))

        file_out = _compose_scad_output_path(dir_scad, asset)
        file_out.parent.mkdir(parents=True, exist_ok=True)

        with file_out.open('w') as f:
            for expression in asset.content():
                for line in transpile(expression):
                    f.write(line + '\n')
                f.write('\n')


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    return dirpath / f'{asset.name}.scad'


def _package_asset(raw: Asset | dict | BaseExpression | list[BaseExpression]
                   | Callable[[], list[BaseExpression]], n_invocation: int,
                   n_asset: int) -> Asset:
    if isinstance(raw, Asset):
        return raw
    if isinstance(raw, dict):
        return Asset(**raw)

    name = f'untitled_{n_invocation}_{n_asset}'
    if isinstance(raw, BaseExpression):
        return Asset(content=lambda: (cast(LiteralExpression, raw), ),
                     name=name)
    if isinstance(raw, (list, tuple)):
        return Asset(content=lambda: cast(tuple[LiteralExpression, ...], raw),
                     name=name)
    if callable(raw):
        return Asset(content=cast(Callable[[], tuple[LiteralExpression, ...]],
                                  raw),
                     name=name)

    raise TypeError(f'Unable to process {raw!r} as a lisscad asset.')
