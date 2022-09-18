"""Usability features. Not all related to CAD."""

from functools import reduce
from numbers import Number
from operator import mul as _mul
from operator import sub as _sub

from lisscad.shorthand import difference, disable

#############
# AGNOSTICS #
#############

# Functions to act upon numbers and OpenSCAD expressions.
# By design, for the sake of functional-programming simplicity, these do not
# use Python’s object-oriented magic methods.


def sub(*args):
    """Negate, subtract, or apply OpenSCAD’s difference operation."""
    if not args:
        raise Exception('“-” requires at least one operand.')
    assert len(args) != 0
    if _numeric(args):
        if len(args) == 1:
            return -args[0]
        return reduce(_sub, args)
    # Arguments are not all numeric. Fall back to OpenSCAD model.
    return difference(*args)


def mul(*args):
    """Multiply or apply OpenSCAD’s disabling modifier."""
    if not args:
        raise Exception('“*” requires at least one operand.')
    assert len(args) != 0
    if _numeric(args):
        if len(args) < 2:
            raise Exception('Numeric “*” requires at least two operands.')
        return reduce(_mul, args)
    if len(args) != 1:
        raise Exception('Non-numeric “*” requires exactly one operand.')
    return disable(*args)


############
# INTERNAL #
############


def _numeric(args) -> bool:
    return all(isinstance(a, Number) for a in args)
