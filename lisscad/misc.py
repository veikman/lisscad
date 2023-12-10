"""Data and utilities shared between the package CLI and the script API."""

from os import getenv
from pathlib import Path

from lisscad.data.other import Gimbal, Image, Vector
from lisscad.py_to_scad import LineGen

DIR_RECENT = (
    Path(getenv('XDG_DATA_HOME', Path.home() / '.local/share'))
    / 'lisscad/recent'
)

EXECUTABLE_OPENSCAD = Path('openscad')


def compose_openscad_command(
    rendering_program: Path,
    input: Path,
    output: Path | None = None,
    image: Image | None = None,
) -> LineGen:
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
                position = [*c.translation, *c.rotation, c.distance]
                yield ','.join(map(str, position))
            else:
                assert isinstance(c, Vector)
                yield ','.join(map(str, [*c.eye, *c.center]))
        if image.size:
            yield '--imgsize'
            yield ','.join(map(str, image.size))
        if image.colorscheme:
            yield '--colorscheme'
            yield image.colorscheme
    yield str(input)
