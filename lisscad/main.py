"""Logic for the use of lisscad itself as a CLI application."""

from os import chdir
from pathlib import Path
from subprocess import run
from sys import stderr
from typing import Generator

from hissp.reader import transpile_file
from inotify_simple import INotify, flags
from typer import Argument, Exit, Typer

from lisscad import __version__ as version

app = Typer()


@app.command()
def to_python(source: Path = Argument(...,
                                      exists=True,
                                      readable=True,
                                      help='Directory or file to read')):
    """Transpile Lissp code to Python code once, for debugging.

    This will clobber Python artifacts even if they are newer than their
    Lissp sources. If you don’t want the intermediate Python code, run the
    lissp interpreter on the file(s) instead.

    """
    list(_files_to_python(source))


@app.command()
def watch(source: Path = Argument(...,
                                  exists=True,
                                  readable=True,
                                  file_okay=False,
                                  help='Directory to watch')):
    """Reactively transpile Lissp code to Python code, indefinitely.

    The watcher is recreated in each pass, because neither its default
    behaviour nor flags.ONESHOT produce one new event per file write.

    """
    while True:
        inotify = INotify()
        inotify.add_watch(source, flags.MODIFY | flags.ONESHOT)
        for event in inotify.read():
            if Path(event.name).suffix == '.lissp':
                to_python(source)
                break


@app.command()
def new(dir_new: Path = Argument(..., help='Directory to create')):
    """Dump boilerplate into a new lisscad project."""
    name = dir_new.name

    if dir_new.exists():
        print(f'Cannot create {dir_new}: Already exists.', file=stderr)
        raise Exit(1)

    dir_new.mkdir(parents=True)

    file_script = dir_new / 'main.lissp'
    file_script.write_text(_TEMPLATE_SCRIPT.format(name=name))

    file_gitignore = dir_new / '.gitignore'
    file_gitignore.write_text(_TEMPLATE_GITIGNORE)

    chdir(dir_new)
    run(['git', 'init'], check=True)
    run(['git', 'commit', '--allow-empty', '-m', 'Start project'], check=True)
    run(['git', 'add', '.'], check=True)
    run(['git', 'add', '--force', '.gitignore'], check=True)
    run([
        'git', 'commit', '-m',
        _TEMPLATE_COMMIT.format(version=version, name=name)
    ],
        check=True)


############
# INTERNAL #
############

_TEMPLATE_SCRIPT = """(lisscad.prelude.._macro_.lisp)

(define main
  (circle 10))

(write (% "name" "{name}"  "content" main))
"""

_TEMPLATE_GITIGNORE = """.*
output/
"""

_TEMPLATE_COMMIT = """Apply template

This commit instantiates a template built into lisscad {version},
using the project name {name}."""


def _file_to_python(*source: Path) -> Generator[Path, None, None]:
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
