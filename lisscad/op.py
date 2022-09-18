"""Usability features. Not all related to CAD."""

from functools import reduce
from numbers import Number
from operator import add as _add
from operator import mul as _mul
from operator import sub as _sub
from operator import truediv as _div

from lisscad.shorthand import difference, disable

#############
# AGNOSTICS #
#############

# Functions to act upon numbers and OpenSCAD expressions.
# By design, for the sake of functional-programming simplicity, these are
# variary and do not use Python’s object-oriented magic methods.


def sub(*args):
    """Negate, subtract, or apply OpenSCAD’s difference operation."""
    if not args:
        # In Clojure, this is an ArityException.
        raise Exception('“-” requires at least one operand.')
    if _numeric(args):
        if len(args) == 1:
            return -args[0]
        return reduce(_sub, args)
    # Arguments are not all numeric. Fall back to OpenSCAD model.
    return difference(*args)


def mul(*args):
    """Multiply or apply OpenSCAD’s disabling modifier."""
    if not args:
        return 1  # As in Clojure.
    if _numeric(args):
        if len(args) == 1:
            return args[0]  # As in Clojure.
        return reduce(_mul, args)
    if len(args) != 1:
        raise Exception('Non-numeric “*” requires exactly one operand.')
    return disable(*args)


##############
# MATHS ONLY #
##############

# Where there is little risk of confusion, these functions are overloadable by
# Python’s object-oriented magic methods.


def add(*args):
    """Add. Numbers only."""
    if not args:
        return 0  # As in Clojure.
    if not _numeric(args):
        raise Exception('“+” is mathematical. Use “|” for unions.')
    if len(args) == 1:
        return args[0]  # As in Clojure.
    return reduce(_add, args)


def div(*args):
    """Divide. Numbers only."""
    if not args:
        # In Clojure, this is an ArityException.
        raise Exception('“/” requires at least one operand.')
    if len(args) == 1:
        return 1 / args[0]  # As in Clojure.
    return reduce(_div, args)


############
# INTERNAL #
############


def _numeric(args) -> bool:
    return all(isinstance(a, Number) for a in args)
