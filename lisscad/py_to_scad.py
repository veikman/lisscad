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
    OpenSCAD or are translated using field_names.

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
        yield f'{name}={_scalar(value)}'


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


def _from_scadterm(datum: d.SCADTerm, **kwargs) -> LineGen:
    container = False
    children: tuple[d.LiteralExpression, ...] = ()
    if container_attr := datum.scad.container:
        container = True
        children = getattr(datum, container_attr)
        if not isinstance(children, tuple):
            children = (children, )

    yield from _format(datum.scad.keyword,
                       *children,
                       container=container,
                       head=', '.join(_fields_from_dataclass(datum)))


_module = partial(_contain, prefix='module ')
