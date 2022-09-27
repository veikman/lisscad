"""Application model.

This module is intended to be imported from a Lissp script.

"""

import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import replace
from functools import partial
from itertools import count
from multiprocessing import Pool
from pathlib import Path
from subprocess import run
from typing import Callable, Generator, cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset, Gimbal, Image, Vector
from lisscad.py_to_scad import LineGen, transpile
from lisscad.shorthand import mirror, module, union

#############
# INTERFACE #
#############

Renamer = Callable[[str], str]

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'
DIR_RENDER = DIR_OUTPUT / 'render'


def refine(asset: Asset, **kwargs) -> Asset:
    content = tuple(e for a in _prepend_modules(asset, **kwargs)
                    for e in a.content())
    return replace(asset, content=lambda: content)


def write(*protoasset: Asset | dict | BaseExpression
          | Iterable[BaseExpression]
          | Callable[[], tuple[BaseExpression, ...]],
          argv: str = None,
          rendering_program: Path = Path('openscad'),
          dir_scad: Path = DIR_SCAD,
          dir_render: Path = DIR_RENDER,
          **kwargs):
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts.

    """
    n_invocation = next(_INVOCATION_ORDINAL)
    _asset_ordinal = count()
    paths: set[Path] = set()

    args = _define_cli().parse_args(sys.argv[1:] if argv is None else argv)
    jobs: list[tuple[str, Path, list[list[str]]]] = []

    dir_scad.mkdir(parents=True, exist_ok=True)
    if args.render:
        dir_render.mkdir(parents=True, exist_ok=True)

    for p in protoasset:
        source_asset = _name_asset(p, n_invocation, next(_asset_ordinal))
        for asset in _refine_nonmodule(source_asset, **kwargs):
            file_scad = _compose_scad_output_path(dir_scad, asset)

            if file_scad in paths:
                print(f'Duplicate output path: “{file_scad}”.',
                      file=sys.stderr)
            paths.add(file_scad)

            # Transpilation is serial because multiprocessing can’t deal with
            # the arbitrary types used in the intermediate data model.
            scad = '\n'.join(_asset_to_scad(asset))

            cmds = list(
                _prepare_commands(
                    partial(_compose_openscad_command, rendering_program,
                            file_scad), asset, file_scad, dir_render,
                    args.render))
            jobs.append((scad, file_scad, cmds))

    # Do the remainder of the work in parallel. Maximum of one subprocess per
    # processor on the user’s machine.
    with Pool() as pool:
        pool.starmap(_process, jobs)


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    """Compose OpenSCAD output/input file path."""
    return dirpath / f'{asset.name}.scad'


def _compose_openscad_command(rendering_program: Path,
                              input: Path,
                              output: Path = None,
                              image: Image = None) -> LineGen:
    """Compose a complete, shell-ready command for running OpenSCAD."""
    yield str(rendering_program)
    if output:
        yield '-o'
        yield str(output)
    if image:
        if image.camera:
            c = image.camera
            yield '--camera'
            if isinstance(c, Gimbal):
                yield ','.join(
                    map(str,
                        list(c.translation) + list(c.rotation) + [c.distance]))
            assert isinstance(c, Vector)
            yield ','.join(map(str, list(c.eye) + list(c.center)))
        if image.size:
            yield '--imgsize'
            yield ','.join(map(str, image.size))
        if image.colorscheme:
            yield '--colorscheme'
            yield image.colorscheme
    yield str(input)


def _prepare_commands(compose, asset: Asset, file_scad: Path, dir_render: Path,
                      render: bool) -> Generator[list[str], None, None]:
    if not render:
        return

    # Assume 3D geometry and OpenSCAD’s default flavour of STL.
    file_stl = (dir_render / file_scad.name).with_suffix('.stl')
    yield list(compose(output=file_stl))

    for image in asset.images:
        file_img = dir_render / image.path
        yield list(compose(output=file_img, image=image))


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


def _asset_to_scad(asset: Asset) -> LineGen:
    """Put a blank line between assets."""
    for expression in asset.content():
        yield from transpile(expression)
        yield ''


def _process(scad: str, file_scad: Path, render_cmds: list[list[str]]):
    """Write output file(s) corresponding to one asset.

    This function has a serializable argument signature because it is designed
    to work with multiprocessing.

    """
    with file_scad.open('w') as f:
        f.write(scad)

    for cmd in render_cmds:
        run(cmd, capture_output=True, check=True)


def _define_cli():
    """Define a command-line interface for controlling CAD output.

    This is designed to let the CAD engineer do temporary behavioural tweaks
    without having to set environment variables or modify input files. It’s not
    related to lisscad.__main__, and unlike lisscad.__main__, it doesn’t use
    Typer because it isn’t modal and can’t act immediately on its arguments.

    """
    parser = ArgumentParser()
    parser.add_argument('-r',
                        '--render',
                        default=False,
                        action='store_true',
                        help='Call OpenSCAD to render to e.g. STL.')
    return parser
