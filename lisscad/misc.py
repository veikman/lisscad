"""Data and utilities shared between the package CLI and the script API."""

from os import getenv
from pathlib import Path

from lisscad.data.other import Gimbal, Image, Vector
from lisscad.py_to_scad import LineGen

DIR_OUTPUT = Path('output')
DIR_SCAD = DIR_OUTPUT / 'scad'
DIR_RENDER = DIR_OUTPUT / 'render'
DIR_RECENT = Path(getenv('XDG_DATA_HOME',
                         Path.home() / '.local/share')) / 'lisscad/recent'

EXECUTABLE_OPENSCAD = Path('openscad')


def compose_openscad_command(rendering_program: Path,
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
