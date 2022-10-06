from dataclasses import fields
from functools import partial, singledispatch
from math import pi
from pathlib import Path
from shlex import split
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
    # Assume contents are numbers or (nested) tuples of numbers.
    # Comma-separate values and wrap them in an OpenSCAD list.
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
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.Rectangle) -> LineGen:
    yield from _from_scadterm(datum)


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
def _(datum: d.Text) -> LineGen:
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.Import2D) -> LineGen:
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.Import3D) -> LineGen:
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.Projection) -> LineGen:
    yield from _from_scadterm(datum)


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
def _(datum: d.Polyhedron) -> LineGen:
    points = _csv(datum.points)
    faces = _csv(datum.faces)
    tail = ''
    if datum.convexity > 1:
        tail += f', convexity={datum.convexity}'
    yield f'polyhedron(points={points}, faces={faces}{tail});'


@transpile.register
def _(datum: d.LinearExtrusion) -> LineGen:
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.RotationalExtrusion) -> LineGen:
    yield from _from_scadterm(datum)


@transpile.register
def _(datum: d.Surface) -> LineGen:
    yield from _from_scadterm(datum)


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


def _bool(value: bool) -> str:
    return str(value).lower()


def _string(value: str) -> str:
    """Format a string for use in OpenSCAD

    OpenSCAD needs double quotes.

    Check for badly nested quotation marks assuming shell-like syntax. Raise
    ValueError if there’s a problem.

    """
    candidate = f'"{value}"'
    n = len(
        split(candidate))  # May raise e.g. “ValueError: No closing quotation”.
    if n != 1:
        # Escape codes needed.
        raise ValueError(
            'Python string {value!r} would form multiple OpenSCAD strings.')
    return candidate


def _scalar(value: int | float | str) -> str:
    if isinstance(value, bool):
        return _bool(value)
    if isinstance(value, (str, Path)):
        return _string(value)
    return _minimize(value)


def _fields_from_dataclass(
        datum: d.SCADTerm,
        denylist: frozenset[str] = frozenset(['child', 'children']),
        rad: frozenset[str] = frozenset(['angle', 'twist']),
) -> LineGen:
    """Generate minimal OpenSCAD from dataclass fields.

    This will only work where field names on the dataclass already match
    OpenSCAD.

    """
    for f in fields(datum):
        if f.name in denylist:
            continue
        value = getattr(datum, f.name)
        if value == f.default:
            continue
        if f.name in rad:
            value = _rad_to_deg(value)
        yield f'{f.name}={_scalar(value)}'


def _rad_to_deg(radians: float) -> float:
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


def _terminate(keyword: str,
               prefix: str = '',
               head: str = '',
               postfix: str = ';') -> str:
    return f'{prefix}{keyword}({head}){postfix}'


def _format(keyword: str,
            *body: d.LiteralExpression,
            container: bool = True,
            **kwargs) -> LineGen:
    if container or body:
        yield from _contain(keyword, *body, **kwargs)
    else:
        yield _terminate(keyword, **kwargs)


def _from_scadterm(datum: d.SCADTerm, ) -> LineGen:
    container = False
    children: tuple[d.LiteralExpression, ...] = ()
    try:
        children = (datum.child, )  # type: ignore[attr-defined]
        container = True
    except AttributeError:
        try:
            children = datum.children  # type: ignore[attr-defined]
            container = True
        except AttributeError:
            pass

    yield from _format(datum.keyword,
                       *children,
                       container=container,
                       head=', '.join(_fields_from_dataclass(datum)))


def _mirror(datum: d.Mirror2D | d.Mirror3D):
    axes = _csv(datum.axes)
    yield from _contain('mirror', *datum.children, head=f'v={axes}')


_union = partial(_contain, 'union')
_difference = partial(_contain, 'difference')
_intersection = partial(_contain, 'intersection')
_translate = partial(_contain, 'translate')
_rotate = partial(_contain, 'rotate')
_module = partial(_contain, prefix='module ')
