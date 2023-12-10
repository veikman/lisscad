"""Transpilation from intermediate data structures to OpenSCAD code."""

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
    if isinstance(datum, d.SCADTerm):
        yield from _from_scadterm(datum)
        return
    raise TypeError(f'Cannot transpile {datum!r}.')


###########################
# DISPATCH IMPLEMENTATION #
###########################


@transpile.register
def _(datum: bool) -> LineGen:
    yield str(datum).lower()


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
def _(datum: str) -> LineGen:
    """Format a string for use in OpenSCAD, with double quotes.

    Check for badly nested quotation marks assuming shell-like syntax. Raise
    ValueError if there’s a problem.

    """
    candidate = f'"{datum}"'
    n = len(
        split(candidate)
    )  # May raise e.g. “ValueError: No closing quotation”.
    if n != 1:
        # Escape codes needed.
        raise ValueError(
            f'Python string {datum!r} would form multiple OpenSCAD strings.'
        )
    yield candidate


@transpile.register
def _(datum: Path) -> LineGen:
    yield from transpile(str(datum))


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
def _(datum: d.SpecialVariable) -> LineGen:
    if datum.assignment_preview is None:
        yield f'{datum.variable};'
    elif datum.assignment_render is None:
        v = next(transpile(datum.assignment_preview))
        yield f'{datum.variable} = {v};'
    else:
        v1 = next(transpile(datum.assignment_preview))
        v2 = next(transpile(datum.assignment_render))
        yield f'{datum.variable} = $preview ? {v1} : {v2};'


@transpile.register
def _(datum: d.Echo) -> LineGen:
    args = ', '.join(list(transpile(arg))[0] for arg in datum.content)
    yield f'echo({args});'


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


def _rad_to_deg(radians: float) -> float:
    return (radians * 180) / pi


def _modifier(symbol: str, target: d.LiteralExpression) -> LineGen:
    """Prepend a modifier to OpenSCAD code."""
    head, *tail = transpile(target)
    yield symbol + head
    yield from tail


_background = partial(_modifier, '%')
_debug = partial(_modifier, '#')
_root = partial(_modifier, '!')
_disable = partial(_modifier, '*')


def _contain(
    keyword: str,
    *body: d.LiteralExpression,
    prefix: str = '',
    head: str = '',
    postfix: str = ';',
) -> LineGen:
    """Compose OpenSCAD code for a branch expression."""
    lead = f'{prefix}{keyword}({head}) '
    if body:
        yield lead + '{'
        for child in body:
            for line in transpile(child):
                yield f'    {line}'
        yield '}' + postfix
    else:
        yield lead + '{}' + postfix


def _terminate(
    keyword: str, prefix: str = '', head: str = '', postfix: str = ';'
) -> str:
    """Compose OpenSCAD code for a leaf expression."""
    return f'{prefix}{keyword}({head}){postfix}'


def _format(
    keyword: str, *body: d.LiteralExpression, container: bool = True, **kwargs
) -> LineGen:
    """Compose typical OpenSCAD code."""
    if container or body:
        yield from _contain(keyword, *body, **kwargs)
    else:
        yield _terminate(keyword, **kwargs)


def _fields_from_dataclass(
    datum: d.SCADTerm,
    denylist: frozenset[str] = frozenset(['child', 'children']),
    rad: frozenset[str] = frozenset(['angle', 'twist']),
) -> LineGen:
    """Generate minimal OpenSCAD from dataclass fields.

    This will only work where field names on the dataclass already match
    OpenSCAD or are translated using field_names in metadata.

    """
    field_names = datum.scad.field_names
    for f in fields(datum):
        if f.name in denylist:
            continue
        value = getattr(datum, f.name)
        if value == f.default:
            continue
        if f.name in rad:
            if isinstance(value, float):
                value = _rad_to_deg(value)
            else:
                value = tuple(map(_rad_to_deg, value))
        name = field_names.get(f.name, f.name)
        csv = list(transpile(value))
        assert len(csv) == 1
        yield f'{name}={csv[0]}'


def _from_scadterm(datum: d.SCADTerm, **kwargs) -> LineGen:
    """Grab metadata about a typical OpenSCAD term from its precursor."""
    container = False
    children: tuple[d.LiteralExpression, ...] = ()
    if container_attr := datum.scad.container:
        container = True
        children = getattr(datum, container_attr)
        if not isinstance(children, tuple):
            children = (children,)

    yield from _format(
        datum.scad.keyword,
        *children,
        container=container,
        head=', '.join(_fields_from_dataclass(datum)),
    )


_module = partial(_contain, prefix='module ')
