"""Logic for the use of lisscad itself as a CLI application."""

import re
import sys
from itertools import islice
from os import chdir
from pathlib import Path
from shutil import which
from subprocess import DEVNULL, Popen, run
from sys import stderr
from typing import Generator

from hissp.reader import transpile_file
from inotify_simple import INotify, flags
from typer import Argument, Exit, Option, Typer

from lisscad import __version__ as _version
from lisscad.app import DIR_RECENT
from lisscad.misc import EXECUTABLE_OPENSCAD, compose_openscad_command

app = Typer(context_settings={'help_option_names': ['-h', '--help']})


@app.command()
def version():
    """Print the version ID of lisscad."""
    print(f'lisscad {_version}')


@app.command(context_settings={'allow_extra_args': True})
def to_python(
    source: Path = Argument(
        ..., exists=True, readable=True, help='Directory or file to read.'
    ),
    cut_argv: bool = Option(True, help='Remove CLI arguments up to “--”.'),
):
    """Transpile Lissp code to Python code once, for debugging.

    This will clobber Python artifacts even if they are newer than their
    Lissp sources. If you don’t want the intermediate Python code, run the
    lissp interpreter on the file(s) instead.

    """
    if cut_argv:
        sys.argv = _recompose_argv(source, sys.argv)
    list(_files_to_python(source))


@app.command(context_settings={'allow_extra_args': True})
def track(
    source: Path = Argument(
        Path('.'),
        exists=True,
        readable=True,
        file_okay=False,
        help='Directory to watch.',
    ),
    regex: str = Option(
        r'\.lissp$',
        help=(
            'Regular expression identifying files which, when changed, '
            'trigger transpilation of Lissp code.'
        ),
    ),
):
    """Reactively transpile Lissp code to Python code, indefinitely."""
    # The watcher is recreated in each pass, because neither its default
    # behaviour nor flags.ONESHOT produce one new event per file write.
    #
    # Note that, even when configured to allow_extra_args, a Typer CLI will
    # still attempt to parse CLI options intended for a CAD script as arguments
    # to this function. To watch the current working directory and re-render
    # the result on each change, you would need to call something like this:
    #
    #     lisscad track . -- --render
    #
    # ... because Typer will otherwise read “--render” as the name of the
    # directory to watch.
    sys.argv = _recompose_argv(source, sys.argv)
    while True:
        inotify = INotify()
        inotify.add_watch(source, flags.MODIFY | flags.ONESHOT)
        for event in inotify.read():
            if re.search(regex, event.name):
                to_python(source, cut_argv=False)
                break


@app.command()
def new(dir_new: Path = Argument(..., help='Directory to create.')):
    """Dump boilerplate into a new lisscad project."""
    name = dir_new.name

    if dir_new.exists():
        print(f'Cannot create {dir_new}: Already exists.', file=stderr)
        raise Exit(1)

    dir_new.mkdir(parents=True)

    file_script = dir_new / 'main.lissp'
    file_script.write_text(_TEMPLATE_SCRIPT.format(name=name))

    file_gitignore = dir_new / '.gitignore'
    file_gitignore.write_text(_TEMPLATE_GITIGNORE.lstrip())

    chdir(dir_new)
    run(['git', 'init'], check=True)
    run(['git', 'commit', '--allow-empty', '-m', 'Start project'], check=True)
    run(['git', 'add', '.'], check=True)
    run(['git', 'add', '--force', '.gitignore'], check=True)
    run(
        [
            'git',
            'commit',
            '-m',
            _TEMPLATE_COMMIT.format(version=_version, name=name),
        ],
        check=True,
    )


@app.command(name='list')
def list_(
    n: int = Option(10, '--number', '-n', help='Number of files.'),
    pattern: str = Option('', help='Regular expression filter.'),
):
    """Print names of recently created files to terminal."""
    for path in islice(_read_cache(pattern), n):
        print(path)


@app.command()
def view(
    pattern: str = Option('.scad$', help='Regular expression filter.'),
    prefix: str = Option('nohup', help='Prefix to OpenSCAD command.'),
    program: Path = Option(EXECUTABLE_OPENSCAD, help='Path to OpenSCAD.'),
    dry_run: bool = Option(False, help='Do not start subprocess.'),
    verbose: bool = Option(False, help='Show command.'),
):
    """Open the most recently created file in OpenSCAD."""

    def error(msg):
        print(f'Cannot view most recent file: {msg}', file=stderr)
        raise Exit(1)

    try:
        file = next(_read_cache(pattern))
    except StopIteration:
        error('No match for pattern.')

    if prefix and which(prefix) is None:
        # Calling Popen would raise FileNotFoundError.
        error(f'Prefix command “{prefix}” not available.')
    if which(program.name) is None:
        # If prefix is non-empty, calling Popen in this case would raise no
        # error. The command would silently fail.
        error(f'OpenSCAD not available (as “{program.name}”).')

    cmd = [prefix] if prefix else []
    cmd.extend(compose_openscad_command(program, file))

    if verbose:
        print(*cmd)
    if not dry_run:
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)


############
# INTERNAL #
############

_TEMPLATE_SCRIPT = """(lisscad.prelude.._macro_.english-util)

(define main
  (circle 10))

(write (% "name" "{name}"  "content" main))
"""

_TEMPLATE_GITIGNORE = """
*.out
*.png
*.py
*.scad
*.stl
.*
"""

_TEMPLATE_COMMIT = """Apply template

This commit instantiates a template built into lisscad {version},
using the project name {name}."""


def _recompose_argv(source: Path, vector: list[str]) -> list[str]:
    """Compose a new vector of CLI arguments.

    This function is designed to blank out sys.argv up to the first double dash
    (if any). This is a precaution, so that CLI options passed to lisscad.main
    are not also passed to any CLI parser inside a target script.

    """
    try:
        return [source.name, *vector[vector.index('--') + 1 :]]
    except ValueError:
        # No “--” in argv.
        return [source.name]


def _file_to_python(*source: Path) -> Generator[Path, None, None]:
    """Transpile Lissp file contents, thereby executing a CAD script."""
    transpile_file(*source)
    for s in source:
        yield Path(s.stem + '.py')


def _files_to_python(source: Path) -> Generator[Path, None, None]:
    if source.is_dir():
        files = list(source.glob('*.lissp'))
        if not files:
            print(f'Empty directory: {source}', file=stderr)
            raise Exit(1)
        yield from _file_to_python(*files)
    elif source.is_file():
        yield from _file_to_python(source)
    else:
        print(f'Not a file or directory: {source}', file=stderr)
        raise Exit(1)


def _read_cache(pattern: str, n_discard: int = 100):
    """Generate files matching pattern, in order from most to least recent.

    Also clean the cache by deleting files older than the most recent
    n_discard.

    Use the mtime of user-created files in preference to the mtime of cached
    references to them.

    """
    staging: list[Path] = []
    for f in DIR_RECENT.glob('*'):
        raw = f.read_text()
        path = Path(raw)
        if not path.is_file():
            f.unlink()
            continue
        staging.append(path)
    staging.sort(key=lambda p: p.stat().st_mtime)
    while len(staging) > n_discard:
        del staging[0]
    for path in reversed(staging):
        if re.search(pattern, str(path)):
            yield path
