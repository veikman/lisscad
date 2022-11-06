"""Utilities for working directly with lisscad’s dataclasses."""

from typing import Type, cast

import lisscad.data.inter as d


def dimensionality(verb: str, *expressions) -> int:
    """Determine the common dimensionality of children."""
    assert expressions
    two: list[int] = []
    three: list[int] = []

    for i, e in enumerate(expressions):
        if isinstance(e, d.Base2D):
            two.append(i)
        elif isinstance(e, d.Base3D):
            three.append(i)
        elif isinstance(e, d.BaseND):
            pass
        else:
            raise TypeError(
                f'Cannot {verb} unknown OpenSCAD operation {type(e)!r}.')

    if two and three:
        # OpenSCAD’s behaviour is poorly defined. Best not to transpile.
        s = f'Cannot {verb} mixed 2D and 3D expressions.'
        if len(two) == 1 and len(three) != 1:
            s += f' One, in place {two[0] + 1} of {len(expressions)}, is 2D.'
        elif len(two) != 1 and len(three) == 1:
            s += f' One, in place {three[0] + 1} of {len(expressions)}, is 3D.'
        raise TypeError(s)

    if two:
        return 2

    # Assume object(s) of unknown dimensionality can be treated as 3D.
    return 3


def modify(type_2d: Type[d.BaseModifier2D], type_3d: Type[d.BaseModifier3D],
           child: d.LiteralExpression) -> d.BaseModifier2D | d.BaseModifier3D:
    """Wrap up a single expression of known dimensionality."""
    if dimensionality('modify', child) == 2:
        return type_2d(cast(d.LiteralExpression2D, child))
    return type_3d(cast(d.LiteralExpression3D, child))


def contain(
    type_2d: Type[d.BaseBoolean2D], type_3d: Type[d.BaseBoolean3D],
    children: tuple[d.LiteralExpression, ...]
) -> d.BaseBoolean2D | d.BaseBoolean3D:
    """Wrap up 1+ expressions of known dimensionality."""
    if dimensionality('contain', *children) == 2:
        return type_2d(cast(tuple[d.LiteralExpression2D, ...], children))
    return type_3d(cast(tuple[d.LiteralExpression3D, ...], children))
