"""Application model.

This module is intended to be imported from a Lissp script.

"""

import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import replace
from functools import partial
from itertools import chain, count
from multiprocessing import Manager, Pool, Process, Queue
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Callable, Generator, cast

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset, Gimbal, Image, Vector
from lisscad.py_to_scad import LineGen, transpile
from lisscad.shorthand import mirror, module, union

#############
# INTERFACE #
#############

Renamer = Callable[[str], str]

RenderJob = tuple[str, str, list[str]]

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
          argv: list[str] = None,
          rendering_program: Path = Path('openscad'),
          dir_scad: Path = DIR_SCAD,
          dir_render: Path = DIR_RENDER,
          **kwargs):
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts.

    """
    # CLI arguments control whether to render etc. These can be overridden from
    # the script itself, mainly for unit testing purposes.
    args = _define_cli().parse_args(sys.argv[1:] if argv is None else argv)

    scadjobs: dict[str, tuple[Asset, Path]] = {}
    renderjobs: list[RenderJob] = []

    dir_scad.mkdir(parents=True, exist_ok=True)
    if args.render:
        dir_render.mkdir(parents=True, exist_ok=True)

    assets_paths = map(
        partial(_prepare_assets, set(), dir_scad, next(_INVOCATION_ORDINAL)),
        zip(count(), protoasset))
    for asset, file_scad in chain(*assets_paths):
        scadjobs[asset.name] = (asset, file_scad)
        steps_cmds = _prepare_commands(
            partial(_compose_openscad_command, rendering_program, file_scad),
            asset, file_scad, dir_render, args.render)
        for step, cmd in steps_cmds:
            renderjobs.append((asset.name, step, cmd))

    _fork(scadjobs, renderjobs)


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()

_STEP_SCAD = 'scad'
_STEP_GEOMETRY = 'geo'
_STEP_IMAGES = 'img'


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
            else:
                assert isinstance(c, Vector)
                yield ','.join(map(str, list(c.eye) + list(c.center)))
        if image.size:
            yield '--imgsize'
            yield ','.join(map(str, image.size))
        if image.colorscheme:
            yield '--colorscheme'
            yield image.colorscheme
    yield str(input)


def _prepare_assets(paths: set[Path], dir_scad, n_invocation: int,
                    numbered: tuple[int, Asset],
                    **kwargs) -> Generator[tuple[Asset, Path], None, None]:
    n_protoasset, protoasset = numbered
    source_asset = _name_asset(protoasset, n_invocation, n_protoasset)
    for asset in _refine_nonmodule(source_asset, **kwargs):
        file_scad = _compose_scad_output_path(dir_scad, asset)

        if file_scad in paths:
            print(f'Duplicate output path: “{file_scad}”.', file=sys.stderr)
        paths.add(file_scad)

        yield (asset, file_scad)


def _prepare_commands(
        compose, asset: Asset, file_scad: Path, dir_render: Path,
        render: bool) -> Generator[tuple[str, list[str]], None, None]:
    if not render:
        return

    # Assume 3D geometry and OpenSCAD’s default flavour of STL.
    file_stl = (dir_render / file_scad.name).with_suffix('.stl')
    yield (_STEP_GEOMETRY, list(compose(output=file_stl)))

    for image in asset.images:
        file_img = dir_render / image.path
        yield (_STEP_IMAGES, list(compose(output=file_img, image=image)))


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


def _write_scad(asset: Asset, file: Path) -> None:
    scad = '\n'.join(_asset_to_scad(asset))
    file.write_text(scad)


def _render(q: Queue, asset: str, step: str, cmd: list[str]):
    """Write one file of rendered output based on one asset.

    This function has a serializable argument signature because it is designed
    to work with multiprocessing.

    """
    try:
        run(cmd, capture_output=True, check=True)
    except CalledProcessError:
        q.put([asset, step, False])
    else:
        q.put([asset, step, True])


def _render_all(q, renderjobs):
    if not renderjobs:
        return
    with Pool() as pool:
        pool.starmap(_render, ([q] + list(r) for r in renderjobs))


def _process_all(q, scadjobs, renderjobs: list[RenderJob]):
    """Write all output files.

    Transpilation to OpenSCAD happens first because it must be complete before
    each asset can be rendered. It is serial because it is assumed to be
    blocked mainly by file I/O, not CPU, and is relatively fast.

    The rest of the work is done in parallel where possible, using a maximum of
    one subprocess per processor on the user’s machine.

    """
    for name, job in scadjobs.items():
        try:
            _write_scad(*job)
        except Exception:
            raise
            q.put([name, _STEP_SCAD, False])
        else:
            q.put([name, _STEP_SCAD, True])

    _render_all(q, renderjobs)


def _fork(scadjobs, renderjobs: list[RenderJob]):
    manager = Manager()
    q = manager.Queue()
    process = Process(target=_process_all, args=(q, scadjobs, renderjobs))
    process.start()
    for n in range(len(scadjobs) + len(renderjobs)):
        print(q.get())
    process.join()


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
