"""Application model.

This module is intended to be imported from a Lissp script.

"""

import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import replace
from functools import partial
from hashlib import sha1
from itertools import chain, count
from multiprocessing import Manager, Pool, Process, Queue
from pathlib import Path
from subprocess import PIPE, STDOUT, CalledProcessError, run
from traceback import format_exc
from typing import Callable, Generator, cast

from rich import print as pprint
from rich.panel import Panel
from rich.progress import Progress, TaskID

from lisscad.data.inter import BaseExpression, LiteralExpression
from lisscad.data.other import Asset
from lisscad.misc import (
    DIR_RECENT,
    EXECUTABLE_OPENSCAD,
    compose_openscad_command,
)
from lisscad.py_to_scad import LineGen, transpile
from lisscad.vocab.base import mirror, module, union

#############
# INTERFACE #
#############

REPORTKEY_INSTRUCTION = 'instruction'
REPORTKEY_PATH = 'output_path'
REPORTKEY_STDOUT_STDERR = 'output_term'
REPORTKEY_TRACEBACK = 'traceback'


class Failure(Exception):
    """A failure in transpilation or rendering."""

    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.description = kwargs


ScadJob = tuple[Asset, Path]
RenderJob = tuple[str, str, list[str], str]
Renamer = Callable[[str], str]
Report = tuple[str, str, bool, dict[str, str]]
Reporter = Callable[[Queue, list[ScadJob], list[RenderJob]], None]
Failer = Callable[[Failure], None]


def refine(asset: Asset, **kwargs) -> Asset:
    """Refine an asset with modules, flattening it."""
    content = tuple(
        e for a in _prepend_modules(asset, **kwargs) for e in a.content()
    )
    return replace(asset, content=lambda: content)


def write(
    *protoasset: Asset
    | dict
    | BaseExpression
    | Iterable[BaseExpression]
    | Callable[[], tuple[BaseExpression, ...]],
    argv: list[str] | None = None,
    rendering_program: Path = EXECUTABLE_OPENSCAD,
    report: Reporter | None = None,
    fail: Failer | None = None,
    dir_scad: Path = Path('.'),
    dir_render: Path = Path('.'),
    **kwargs,
) -> None:
    """Convert intermediate representations to OpenSCAD code.

    This function’s profile is relaxed to minimize boilerplate in CAD
    scripts. It’s got big side effects:
    * Read command-line arguments in addition to function arguments.
    * Increment a global-variable counter that’s used to name otherwise
      anonymous assets.
    * Create/update files of output. Rendering is parallelized.
    * Create/update references to files of output. These are used elsewhere in
      lisscad for recalling recent work.
    * Report progress. By default, this uses the calling terminal.

    """
    # CLI arguments control whether to render etc. These can be overridden from
    # the script itself, mainly for unit testing purposes.
    args = _define_cli().parse_args(sys.argv[1:] if argv is None else argv)

    scadjobs: list[ScadJob] = []
    renderjobs: list[RenderJob] = []

    _make_directories(dir_scad, dir_render if args.render else None)

    assets_paths = map(
        partial(_prepare_assets, set(), dir_scad, next(_INVOCATION_ORDINAL)),
        zip(count(), protoasset),
    )
    for asset, file_scad in chain(*assets_paths):
        scadjobs.append((asset, file_scad.resolve()))
        steps_cmds = _prepare_commands(
            partial(compose_openscad_command, rendering_program, file_scad),
            asset,
            file_scad,
            dir_render,
            args.render,
        )
        for step, cmd, file_render in steps_cmds:
            renderjobs.append(
                (asset.name, step, cmd, str(file_render.resolve()))
            )

    _fork(scadjobs, renderjobs, report or _report, fail or _fail)


############
# INTERNAL #
############

_INVOCATION_ORDINAL = count()

_STEP_SCAD = 'compose OpenSCAD code'
_STEP_GEOMETRY = 'render geometry'
_STEP_IMAGES = 'render image'


def _make_directories(*dirs: Path | None):
    """Make directories. This function exists to be patched out in testing."""
    for d in dirs:
        if d:
            d.mkdir(parents=True, exist_ok=True)


def _compose_scad_output_path(dirpath: Path, asset: Asset) -> Path:
    """Compose OpenSCAD output/input file path."""
    return dirpath / f'{asset.name}.scad'


def _note_recent(path: Path) -> None:
    """Update cache of recently created files, for one file.

    Take an absolute path. Hash it to avoid collisions between projects.

    """
    h = sha1()  # Security is not important for this use case.
    h.update(str(path).encode('utf-'))
    file = DIR_RECENT / h.hexdigest()
    file.write_text(str(path))


def _prepare_assets(
    paths: set[Path],
    dir_scad,
    n_invocation: int,
    numbered: tuple[int, Asset],
    **kwargs,
) -> Generator[tuple[Asset, Path], None, None]:
    n_protoasset, protoasset = numbered
    source_asset = _name_asset(protoasset, n_invocation, n_protoasset)
    for asset in _refine_nonmodule(source_asset, **kwargs):
        file_scad = _compose_scad_output_path(dir_scad, asset)

        if file_scad in paths:
            print(f'Duplicate output path: “{file_scad}”.', file=sys.stderr)
        paths.add(file_scad)

        yield (asset, file_scad)


def _prepare_commands(
    compose, asset: Asset, file_scad: Path, dir_render: Path, render: bool
) -> Generator[tuple[str, list[str], Path], None, None]:
    if not render:
        return

    # Apply each suffix for rendering the asset, not images of it.
    for suffix in asset.suffixes:
        suffixed = (dir_render / file_scad.name).with_suffix(suffix)
        yield (_STEP_GEOMETRY, list(compose(output=suffixed)), suffixed)

    for image in asset.images:
        file_img = dir_render / image.path
        yield (
            _STEP_IMAGES,
            list(compose(output=file_img, image=image)),
            file_img,
        )


def _name_asset(
    raw: Asset
    | dict
    | BaseExpression
    | Iterable[BaseExpression]
    | Callable[[], tuple[BaseExpression, ...]],
    n_invocation: int,
    n_asset: int,
) -> Asset:
    """Find a likely-distinct name for a content-only asset."""
    if isinstance(raw, Asset):
        # Assume caller is satisfied with current name.
        return raw
    if isinstance(raw, dict):
        # Assume caller has specified a name or wants the default.
        return Asset(**raw)

    # Make up a non-default name.
    name = f'untitled_{n_invocation}_{n_asset}'
    return Asset(
        content=cast(Callable[[], tuple[LiteralExpression, ...]], raw),
        name=name,
    )


def _rename_asset(
    asset: Asset,
    if_mirrored: Renamer = lambda s: f'{s}_mirrored',
    if_chiral: Renamer = lambda s: s,
    if_achiral: Renamer = lambda s: s,
    **_,
) -> Asset:
    """Rename asset based on chirality and mirroring."""
    function = if_achiral
    if asset.mirrored:
        function = if_mirrored
    elif asset.chiral:
        function = if_chiral
    return replace(asset, name=function(asset.name))


def _finalize_asset(
    modularize: bool, asset: Asset, flip_chiral: bool = True, **kwargs
) -> Asset:
    """Flip an asset if it’s chiral and package it for transpilation.

    Flipping is intended to support CAD assets that need to come in two forms
    with different handedness.

    """
    content = asset.content()
    if modularize and len(content) > 1:
        content = (union(*content),)
    mirrored = asset.mirrored
    if asset.chiral and not mirrored and flip_chiral:
        mirrored = True
        content = (mirror((1, 0, 0), content[0]),)
    if modularize:
        content = (module(asset.name, *content),)
    return _rename_asset(
        replace(asset, content=lambda: content, modules=(), mirrored=mirrored),
        **kwargs,
    )


def _prepend_modules(parent: Asset, **kwargs) -> Generator[Asset, None, None]:
    """Flatten an asset with modules into a range of assets without them."""
    for child in parent.modules:
        yield _finalize_asset(True, child, **kwargs)
    yield replace(_finalize_asset(False, parent, **kwargs), modules=())


def _flatten(asset: Asset, flip_chiral: bool = True, **kwargs):
    """Ensure that an asset has its modules as part of its content."""
    content = tuple(
        e
        for a in _prepend_modules(asset, flip_chiral=flip_chiral, **kwargs)
        for e in a.content()
    )
    return _rename_asset(
        replace(
            asset,
            content=lambda: content,
            mirrored=asset.chiral and flip_chiral,
        ),
        **kwargs,
    )


def _refine_nonmodule(
    asset: Asset, flip_chiral: bool = True, **kwargs
) -> Generator[Asset, None, None]:
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


def _render(q: Queue, asset: str, step: str, cmd: list[str], path: str):
    """Write one file of rendered output based on one asset.

    This function has a serializable argument signature because it is designed
    to work with multiprocessing.

    """
    try:
        run(cmd, check=True, text=True, stdout=PIPE, stderr=STDOUT)
    except CalledProcessError as e:
        q.put(
            (
                asset,
                step,
                False,
                {
                    REPORTKEY_INSTRUCTION: ' '.join(cmd),
                    REPORTKEY_STDOUT_STDERR: e.stdout,
                },
            )
        )
    else:
        q.put((asset, step, True, {REPORTKEY_PATH: path}))


def _render_all(q, renderjobs):
    if not renderjobs:
        return
    with Pool() as pool:
        pool.starmap(_render, ([q] + list(r) for r in renderjobs))


def _process_all(q, scadjobs: list[ScadJob], renderjobs: list[RenderJob]):
    """Write all output files.

    Transpilation to OpenSCAD happens first because it must be complete before
    each asset can be rendered. It is serial because it is assumed to be
    blocked mainly by file I/O, not CPU, and is relatively fast.

    The rest of the work is done in parallel where possible, using a maximum of
    one subprocess per processor on the user’s machine.

    """
    for job in scadjobs:
        asset, path = job
        try:
            _write_scad(*job)
        except Exception:
            q.put(
                (
                    asset.name,
                    _STEP_SCAD,
                    False,
                    {REPORTKEY_TRACEBACK: format_exc()},
                )
            )
        else:
            q.put((asset.name, _STEP_SCAD, True, {REPORTKEY_PATH: path}))

    _render_all(q, renderjobs)


def _report(
    q: Queue, scadjobs: list[ScadJob], renderjobs: list[RenderJob]
) -> None:
    """Display progress bars, one per asset, in terminal."""
    total_steps = len(scadjobs) + len(renderjobs)
    step_counts_by_name: dict[str, int] = {a.name: 1 for a, _ in scadjobs}
    for name, _, _, _ in renderjobs:
        step_counts_by_name[name] += 1
    tasks: dict[str, TaskID] = {}

    cache = True
    try:
        DIR_RECENT.mkdir(parents=True, exist_ok=True)
    except Exception:
        print(f'Failed to create cache at “{DIR_RECENT}”.', file=sys.stderr)
        cache = False

    with Progress() as progress:
        for name, n in step_counts_by_name.items():
            tasks[name] = progress.add_task(name, total=n)

        for i in range(total_steps):
            name, step, result, other = q.get()

            if not result:
                raise Failure(f'Failed to {step} for asset “{name}”.', **other)

            if cache and (path := other.get(REPORTKEY_PATH)):
                _note_recent(path)

            progress.update(tasks[name], advance=1)


def _fail(e: Failure):
    """Display information about a failure to transpile or render."""
    pprint(f'[bold red]Error:[/bold red] {e}')
    if REPORTKEY_INSTRUCTION in e.description:
        print('External command used:')
        print('    ' + e.description[REPORTKEY_INSTRUCTION])
        if REPORTKEY_STDOUT_STDERR in e.description:
            print('Output from external command:')
            pprint(Panel.fit(e.description[REPORTKEY_STDOUT_STDERR].rstrip()))
    if REPORTKEY_TRACEBACK in e.description:
        # This will start with a line like “Traceback (most recent call last):”
        print(e.description[REPORTKEY_TRACEBACK])


def _fork(
    scadjobs: list[ScadJob],
    renderjobs: list[RenderJob],
    report: Reporter,
    fail: Failer,
):
    manager = Manager()
    q = manager.Queue()

    process = Process(target=_process_all, args=(q, scadjobs, renderjobs))
    process.start()

    try:
        report(cast(Queue, q), scadjobs, renderjobs)
    except Failure as e:
        fail(e)

    process.join()


def _define_cli():
    """Define a command-line interface for controlling CAD output.

    This is designed to let the CAD engineer do temporary behavioural tweaks
    without having to set environment variables or modify input files. It’s not
    related to lisscad.__main__, and unlike lisscad.__main__, it doesn’t use
    Typer because it isn’t modal and can’t act immediately on its arguments.

    """
    parser = ArgumentParser()
    parser.add_argument(
        '-r',
        '--render',
        default=False,
        action='store_true',
        help='Call OpenSCAD to render to e.g. STL.',
    )
    return parser
