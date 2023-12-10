"""Utilities for working directly with lisscad’s dataclasses."""

from typing import Any, Type, cast

import lisscad.data.inter as d


def dimensionality(
    verb_base: str, *expressions, verb_first='', verb_rest=''
) -> int:
    """Determine the common dimensionality of children."""
    assert expressions
    two: list[int] = []
    three: list[int] = []

    for i, e in enumerate(expressions):
        verb = verb_first or verb_base
        if i:
            verb = verb_rest or verb_base

        if isinstance(e, d.Base2D):
            two.append(i)
        elif isinstance(e, d.Base3D):
            three.append(i)
        elif isinstance(e, d.BaseND):
            pass
        else:
            s = _quote_value(e)
            raise TypeError(f'Cannot {verb} non-OpenSCAD expression {s}.')

    if two and three:
        # OpenSCAD’s behaviour is poorly defined. Best not to transpile.
        s = f'Cannot {verb_base} mixed 2D and 3D expressions.'
        if len(two) == 1 and len(three) != 1:
            s += f' One, in place {two[0] + 1} of {len(expressions)}, is 2D.'
        elif len(two) != 1 and len(three) == 1:
            s += f' One, in place {three[0] + 1} of {len(expressions)}, is 3D.'
        raise TypeError(s)

    if two:
        return 2

    # Assume object(s) of unknown dimensionality can be treated as 3D.
    return 3


def matched(
    verb: str,
    argument: tuple[float, ...],
    expressions: tuple[d.LiteralExpression, ...],
):
    """Check that expressions match dimensionality of argument.

    Assume that the argument describes the dimensionality of an operation upon
    the expressions.

    If they match, return their common dimensionality.

    """
    n0 = len(argument)
    nx = len(expressions)
    suffix = '' if nx == 1 else 's'

    if n0 == 2:
        n1 = 3
    elif n0 == 3:
        n1 = 2
    else:
        raise ValueError(
            f'Cannot {verb} OpenSCAD expression{suffix} '
            f'with {n0}D argument {argument}.'
        )

    if n0 == dimensionality(verb, *expressions):
        return n0

    raise ValueError(
        f'Cannot {verb} {n1}D OpenSCAD expression{suffix} '
        f'with {n0}D argument {argument}.'
    )


def modify(
    type_2d: Type[d.BaseModifier2D],
    type_3d: Type[d.BaseModifier3D],
    child: d.LiteralExpression,
) -> d.BaseModifier2D | d.BaseModifier3D:
    """Wrap up a single expression of known dimensionality."""
    if dimensionality('modify', child) == 2:
        return type_2d(cast(d.LiteralExpression2D, child))
    return type_3d(cast(d.LiteralExpression3D, child))


def contain(
    type_2d: Type[d.BaseBoolean2D],
    type_3d: Type[d.BaseBoolean3D],
    children: tuple[d.LiteralExpression, ...],
    **kwargs,
) -> d.BaseBoolean2D | d.BaseBoolean3D:
    """Wrap up 1+ expressions of known dimensionality."""
    if dimensionality('contain', *children, **kwargs) == 2:
        return type_2d(cast(tuple[d.LiteralExpression2D, ...], children))
    return type_3d(cast(tuple[d.LiteralExpression3D, ...], children))


def _quote_value(value: Any) -> str:
    """Describe a bad value for the benefit of the user."""
    t = f'of type {type(value)!r}'
    try:
        value = str(value)
    except Exception:
        return t

    if len(value) > 30:
        return f'“{value[:20]}...” (truncated) {t}'

    return f'“{value}” {t}'
