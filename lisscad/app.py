"""Application model.

This module is intended to be imported from a Lissp script.

"""

import sys
from collections.abc import Iterable
from dataclasses import replace
from itertools import count
from pathlib import Path
from typing import Callable, Generator, cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset
from lisscad.py_to_scad import transpile
from lisscad.shorthand import mirror, module, union

#############
# INTERFACE #
#############

Renamer = Callable[[str], str]

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'


def refine(asset: Asset, **kwargs) -> Asset:
    content = tuple(e for a in _prepend_modules(asset, **kwargs)
                    for e in a.content())
    return replace(asset, content=lambda: content)


def write(*protoasset: Asset | dict | BaseExpression
          | Iterable[BaseExpression]
          | Callable[[], tuple[BaseExpression, ...]],
          dir_scad: Path = DIR_SCAD,
          **kwargs):
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts.

    """
    n_invocation = next(_INVOCATION_ORDINAL)
    _asset_ordinal = count()
    paths: set[Path] = set()

    for p in protoasset:
        source_asset = _name_asset(p, n_invocation, next(_asset_ordinal))
        for asset in _refine_nonmodule(source_asset, **kwargs):
            file_out = _compose_scad_output_path(dir_scad, asset)

            if file_out in paths:
                print(f'Duplicate output path: “{file_out}”.', file=sys.stderr)

            file_out.parent.mkdir(parents=True, exist_ok=True)

            with file_out.open('w') as f:
                for expression in asset.content():
                    for line in transpile(expression):
                        f.write(line + '\n')
                    f.write('\n')

            paths.add(file_out)


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    return dirpath / f'{asset.name}.scad'


def _name_asset(raw: Asset | dict | BaseExpression
                | Iterable[BaseExpression]
                | Callable[[], tuple[BaseExpression, ...]], n_invocation: int,
                n_asset: int) -> Asset:
    """Find a likely-distinct name for a content-only asset."""
    if isinstance(raw, Asset):
        # Assume caller is satisfied with current name.
        return raw
    if isinstance(raw, dict):
        # Assume caller has specified a name or wants the default.
        return Asset(**raw)

    # Make up a non-default name.
    name = f'untitled_{n_invocation}_{n_asset}'
    return Asset(content=cast(Callable[[], tuple[LiteralExpression, ...]],
                              raw),
                 name=name)


def _rename_asset(asset: Asset,
                  if_mirrored: Renamer = lambda s: f'{s}_mirrored',
                  if_chiral: Renamer = lambda s: s,
                  if_achiral: Renamer = lambda s: s,
                  **_) -> Asset:
    """Rename asset based on chirality and mirroring."""
    function = if_achiral
    if asset.mirrored:
        function = if_mirrored
    elif asset.chiral:
        function = if_chiral
    return replace(asset, name=function(asset.name))


def _finalize_asset(modularize: bool,
                    asset: Asset,
                    flip_chiral: bool = True,
                    **kwargs) -> Asset:
    """Flip an asset if it’s chiral and package it for transpilation.

    Flipping is intended to support CAD assets that need to come in two forms
    with different handedness.

    """
    content = asset.content()
    if modularize and len(content) > 1:
        content = (union(*content), )
    mirrored = asset.mirrored
    if asset.chiral and not mirrored and flip_chiral:
        mirrored = True
        content = (mirror((1, 0, 0), content[0]), )
    if modularize:
        content = (module(asset.name, *content), )
    return _rename_asset(
        replace(asset, content=lambda: content, modules=(), mirrored=mirrored),
        **kwargs)


def _prepend_modules(parent: Asset, **kwargs) -> Generator[Asset, None, None]:
    """Flatten an asset with modules into a range of assets without them."""
    for child in parent.modules:
        yield _finalize_asset(True, child, **kwargs)
    yield replace(_finalize_asset(False, parent, **kwargs), modules=())


def _flatten(asset: Asset, flip_chiral: bool = True, **kwargs):
    """Ensure that an asset has its modules as part of its content."""
    content = tuple(
        e for a in _prepend_modules(asset, flip_chiral=flip_chiral, **kwargs)
        for e in a.content())
    return _rename_asset(
        replace(asset,
                content=lambda: content,
                mirrored=asset.chiral and flip_chiral), **kwargs)


def _refine_nonmodule(asset: Asset,
                      flip_chiral: bool = True,
                      **kwargs) -> Generator[Asset, None, None]:
    """Generate one or two top-level assets.

    These may have modules as part of their content, but may not be modules.

    A second asset can be generated only for chiral assets, in which case it is
    mirrored relative to the original.

    """
    yield _flatten(asset, flip_chiral=False, **kwargs)
    if asset.chiral and not asset.mirrored and flip_chiral:
        yield _flatten(asset, flip_chiral=True, **kwargs)
