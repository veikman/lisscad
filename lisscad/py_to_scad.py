from functools import singledispatch
from typing import Generator

from lisscad.data import inter as dm

LineGen = Generator[str, None, None]


@singledispatch
def transpile(intermediate) -> LineGen:
    raise TypeError(f'Cannot transpile {intermediate!r}.')


@transpile.register
def _(intermediate: tuple) -> LineGen:
    yield from map(str, intermediate)


@transpile.register
def _(intermediate: dm.Cube) -> LineGen:
    size = ', '.join(transpile(intermediate.size))
    yield f'cube(size=[{size}], center={intermediate.center});'


@transpile.register
def _(intermediate: dm.Translation3D) -> LineGen:
    coord = ', '.join(transpile(intermediate.coord))
    yield f'translate([{coord}]) {{'
    for line in transpile(intermediate.child):
        yield f'    {line}'
    yield '};'
