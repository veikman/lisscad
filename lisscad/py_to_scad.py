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
def _(datum: int) -> LineGen:
    yield str(datum)


@transpile.register
def _(datum: float) -> LineGen:
    if datum.is_integer():
        # Cut off redundant decimals; likely added by Pydantic.
        yield from transpile(int(datum))
        return
    yield str(datum)


@transpile.register
def _(datum: tuple) -> LineGen:
    # Comma-separate values and wrap them in an OpenSCAD list.
    # Assume contents are nested tuples of numbers, or numbers.
    yield '[' + ', '.join(s for g in map(transpile, datum) for s in g) + ']'


@transpile.register
def _(datum: d.Comment) -> LineGen:
    for line in datum.content:
        yield f'// {line}'


@transpile.register
def _(datum: d.Commented2D) -> LineGen:
    yield from transpile(datum.comment)
    yield from transpile(datum.subject)


@transpile.register
def _(datum: d.Commented3D) -> LineGen:
    yield from transpile(datum.comment)
    yield from transpile(datum.subject)


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
    yield f'circle(r={_minimize(datum.radius)});'


@transpile.register
def _(datum: d.Square) -> LineGen:
    yield (f'square(size={_csv(datum.size)}, '
           f'center={str(datum.center).lower()});')


@transpile.register
def _(datum: d.Polygon) -> LineGen:
    points = _csv(datum.points)
    tail = ''
    if datum.paths:
        tail += f', paths={_csv(datum.paths)}'
    if datum.convexity > 1:
        tail += f', convexity={datum.convexity}'
    yield f'polygon(points={points}{tail});'


@transpile.register
def _(datum: d.Sphere) -> LineGen:
    yield f'sphere(r={_minimize(datum.radius)});'


@transpile.register
def _(datum: d.Cube) -> LineGen:
    yield (f'cube(size={_csv(datum.size)}, '
           f'center={str(datum.center).lower()});')


@transpile.register
def _(datum: d.Cylinder) -> LineGen:
    yield (f'cylinder(r={_minimize(datum.radius)}, '
           f'h={_minimize(datum.height)}, '
           f'center={str(datum.center).lower()});')


@transpile.register
def _(datum: d.Frustum) -> LineGen:
    yield (f'cylinder(r1={_minimize(datum.radii[0])}, '
           f'r2={_minimize(datum.radii[1])}, '
           f'h={_minimize(datum.height)}, '
           f'center={str(datum.center).lower()});')


@transpile.register
def _(datum: d.Translation2D) -> LineGen:
    yield from _translate(*datum.children, head=_csv(datum.coord))


@transpile.register
def _(datum: d.Translation3D) -> LineGen:
    yield from _translate(*datum.children, head=_csv(datum.coord))


@transpile.register
def _(datum: d.Rotation2D) -> LineGen:
    a = _rad_to_deg(datum.angle)
    yield from _rotate(*datum.children, head=f'a={a}')


@transpile.register
def _(datum: d.Rotation3D) -> LineGen:
    angles = _csv(tuple(map(_rad_to_deg, datum.angle)))
    yield from _rotate(*datum.children, head=f'a={angles}')


@transpile.register
def _(datum: d.Mirror2D) -> LineGen:
    yield from _mirror(datum)


@transpile.register
def _(datum: d.Mirror3D) -> LineGen:
    yield from _mirror(datum)


@transpile.register
def _(datum: d.ModuleDefinition2D) -> LineGen:
    yield from _module(datum.name, *datum.children)


@transpile.register
def _(datum: d.ModuleDefinition3D) -> LineGen:
    yield from _module(datum.name, *datum.children)


@transpile.register
def _(datum: d.ModuleCall2D) -> LineGen:
    yield from _contain(datum.name, *datum.children)


@transpile.register
def _(datum: d.ModuleCall3D) -> LineGen:
    yield from _contain(datum.name, *datum.children)


@transpile.register
def _(datum: d.ModuleCallND) -> LineGen:
    yield from _contain(datum.name)


@transpile.register
def _(datum: d.ModuleChildren) -> LineGen:
    yield 'children();'


############
# BACK END #
############


def _numeric(
    values: int | float | tuple[int | float | tuple[int | float, ...], ...]
) -> str:
    data = list(transpile(values))
    assert len(data) == 1
    return data[0]


def _minimize(value: int | float) -> str:
    return _numeric(value)


def _csv(values: tuple[int | float | tuple[int | float, ...], ...]) -> str:
    return _numeric(values)


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


def _contain(keyword: str,
             *body: d.LiteralExpression,
             prefix: str = '',
             head: str = '',
             postfix: str = ';') -> LineGen:
    lead = f'{prefix}{keyword}({head}) '
    if body:
        yield lead + '{'
        for child in body:
            for line in transpile(child):
                yield f'    {line}'
        yield '}' + postfix
    else:
        yield lead + '{}' + postfix


def _mirror(datum: d.Mirror2D | d.Mirror3D):
    axes = ', '.join(map(str, datum.axes))
    yield from _contain('mirror', *datum.children, head=f'v=[{axes}]')


_union = partial(_contain, 'union')
_difference = partial(_contain, 'difference')
_intersection = partial(_contain, 'intersection')
_translate = partial(_contain, 'translate')
_rotate = partial(_contain, 'rotate')
_module = partial(_contain, prefix='module ')
