from functools import partial, singledispatch
from typing import Generator

from lisscad.data import inter as dm

#############
# INTERFACE #
#############

LineGen = Generator[str, None, None]


@singledispatch
def transpile(intermediate) -> LineGen:
    raise TypeError(f'Cannot transpile {intermediate!r}.')


###########################
# DISPATCH IMPLEMENTATION #
###########################


@transpile.register
def _(intermediate: tuple) -> LineGen:
    yield from map(str, intermediate)


@transpile.register
def _(intermediate: dm.Union2D) -> LineGen:
    yield from _union(*intermediate.children)


@transpile.register
def _(intermediate: dm.Union3D) -> LineGen:
    yield from _union(*intermediate.children)


@transpile.register
def _(intermediate: dm.Difference2D) -> LineGen:
    yield from _difference(*intermediate.children)


@transpile.register
def _(intermediate: dm.Difference3D) -> LineGen:
    yield from _difference(*intermediate.children)


@transpile.register
def _(intermediate: dm.Intersection2D) -> LineGen:
    yield from _intersection(*intermediate.children)


@transpile.register
def _(intermediate: dm.Intersection3D) -> LineGen:
    yield from _intersection(*intermediate.children)


@transpile.register
def _(intermediate: dm.Circle) -> LineGen:
    yield f'circle(r={intermediate.radius});'


@transpile.register
def _(intermediate: dm.Square) -> LineGen:
    size = ', '.join(transpile(intermediate.size))
    yield f'square(size=[{size}], center={str(intermediate.center).lower()});'


@transpile.register
def _(intermediate: dm.Sphere) -> LineGen:
    yield f'circle(r={intermediate.radius});'


@transpile.register
def _(intermediate: dm.Cube) -> LineGen:
    size = ', '.join(transpile(intermediate.size))
    yield f'cube(size=[{size}], center={str(intermediate.center).lower()});'


@transpile.register
def _(intermediate: dm.Translation2D) -> LineGen:
    coord = ', '.join(transpile(intermediate.coord))
    yield from _translate(f'[{coord}]', intermediate.child)


@transpile.register
def _(intermediate: dm.Translation3D) -> LineGen:
    coord = ', '.join(transpile(intermediate.coord))
    yield from _translate(f'[{coord}]', intermediate.child)


@transpile.register
def _(intermediate: dm.Rotation2D) -> LineGen:
    yield from _rotate(f'a={intermediate.angle}', intermediate.child)


@transpile.register
def _(intermediate: dm.Rotation3D) -> LineGen:
    coord = ', '.join(transpile(intermediate.angle))
    yield from _translate(f'a=[{coord}]', intermediate.child)


############
# BACK END #
############


def _contain(keyword: str, head: str, *body: dm.LiteralExpression) -> LineGen:
    yield f'{keyword}({head}) {{'
    for child in body:
        for line in transpile(child):
            yield f'    {line}'
    yield '};'


_union = partial(_contain, 'union', '')
_difference = partial(_contain, 'difference', '')
_intersection = partial(_contain, 'intersection', '')
_translate = partial(_contain, 'translate')
_rotate = partial(_contain, 'rotate')
