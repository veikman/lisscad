from functools import singledispatch
from typing import Generator

from scadl.data import inter as dm

LineGen = Generator[str, None, None]


@singledispatch
def transpile(intermediate) -> LineGen:
    raise TypeError(f'Cannot transpile {intermediate!r}.')


@transpile.register
def _(intermediate: dm.Tuple3D) -> LineGen:
    yield str(intermediate.x)
    yield str(intermediate.y)
    yield str(intermediate.z)


@transpile.register
def _(intermediate: dm.Cube) -> LineGen:
    size = ', '.join(transpile(intermediate.size))
    yield f'cube(size=[{size}], center={intermediate.center});'
