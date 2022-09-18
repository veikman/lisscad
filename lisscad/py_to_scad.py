from functools import partial, singledispatch
from math import pi
from typing import Generator

from lisscad.data import inter as d

#############
# INTERFACE #
#############

LineGen = Generator[str, None, None]


@singledispatch
def transpile(datum) -> LineGen:
    raise TypeError(f'Cannot transpile {datum!r}.')


###########################
# DISPATCH IMPLEMENTATION #
###########################


@transpile.register
def _(datum: tuple) -> LineGen:
    yield from map(str, datum)


@transpile.register
def _(datum: d.Background2D) -> LineGen:
    yield from _background(datum.child)


@transpile.register
def _(datum: d.Background3D) -> LineGen:
    yield from _background(datum.child)


@transpile.register
def _(datum: d.Debug2D) -> LineGen:
    yield from _debug(datum.child)


@transpile.register
def _(datum: d.Debug3D) -> LineGen:
    yield from _debug(datum.child)


@transpile.register
def _(datum: d.Root2D) -> LineGen:
    yield from _root(datum.child)


@transpile.register
def _(datum: d.Root3D) -> LineGen:
    yield from _root(datum.child)


@transpile.register
def _(datum: d.Disable2D) -> LineGen:
    yield from _disable(datum.child)


@transpile.register
def _(datum: d.Disable3D) -> LineGen:
    yield from _disable(datum.child)


@transpile.register
def _(datum: d.Union2D) -> LineGen:
    yield from _union(*datum.children)


@transpile.register
def _(datum: d.Union3D) -> LineGen:
    yield from _union(*datum.children)


@transpile.register
def _(datum: d.Difference2D) -> LineGen:
    yield from _difference(*datum.children)


@transpile.register
def _(datum: d.Difference3D) -> LineGen:
    yield from _difference(*datum.children)


@transpile.register
def _(datum: d.Intersection2D) -> LineGen:
    yield from _intersection(*datum.children)


@transpile.register
def _(datum: d.Intersection3D) -> LineGen:
    yield from _intersection(*datum.children)


@transpile.register
def _(datum: d.Circle) -> LineGen:
    yield f'circle(r={datum.radius});'


@transpile.register
def _(datum: d.Square) -> LineGen:
    size = ', '.join(transpile(datum.size))
    yield f'square(size=[{size}], center={str(datum.center).lower()});'


@transpile.register
def _(datum: d.Sphere) -> LineGen:
    yield f'sphere(r={datum.radius});'


@transpile.register
def _(datum: d.Cube) -> LineGen:
    size = ', '.join(transpile(datum.size))
    yield f'cube(size=[{size}], center={str(datum.center).lower()});'


@transpile.register
def _(datum: d.Translation2D) -> LineGen:
    coord = ', '.join(transpile(datum.coord))
    yield from _translate(f'[{coord}]', *datum.children)


@transpile.register
def _(datum: d.Translation3D) -> LineGen:
    coord = ', '.join(transpile(datum.coord))
    yield from _translate(f'[{coord}]', *datum.children)


@transpile.register
def _(datum: d.Rotation2D) -> LineGen:
    a = _rad_to_deg(datum.angle)
    yield from _rotate(f'a={a}', *datum.children)


@transpile.register
def _(datum: d.Rotation3D) -> LineGen:
    angles = ', '.join(transpile(tuple(map(_rad_to_deg, datum.angle))))
    yield from _rotate(f'a=[{angles}]', *datum.children)


############
# BACK END #
############


def _rad_to_deg(radians: float):
    return (radians * 180) / pi


def _modifier(symbol: str, target: d.LiteralExpression) -> LineGen:
    head, *tail = transpile(target)
    yield symbol + head
    yield from tail


_background = partial(_modifier, '%')
_debug = partial(_modifier, '#')
_root = partial(_modifier, '!')
_disable = partial(_modifier, '*')


def _contain(keyword: str, head: str, *body: d.LiteralExpression) -> LineGen:
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
