"""Usability features. Not all related to CAD."""

from functools import reduce
from numbers import Number
from operator import sub as _sub

from lisscad.shorthand import difference

#############
# AGNOSTICS #
#############

# Functions to act upon numbers and OpenSCAD expressions.
# By design, for the sake of functional-programming simplicity, these do not
# use Python’s object-oriented magic methods.


def sub(*args):
    """Subtraction."""
    assert len(args) != 0
    if _numeric(args):
        if len(args) == 1:
            return -args[0]
        return reduce(_sub, args)
    # Arguments are not all numeric. Fall back to OpenSCAD model.
    return difference(*args)


############
# INTERNAL #
############


def _numeric(args) -> bool:
    return all(isinstance(a, Number) for a in args)
