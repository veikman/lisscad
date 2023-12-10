"""Usability features. Not all related to CAD."""

from functools import reduce
from itertools import starmap
from numbers import Number
from operator import add as _add
from operator import mul as _mul
from operator import sub as _sub
from operator import truediv as _div

from lisscad.data.inter import BaseExpression
from lisscad.vocab.base import background, debug, difference, disable

#############
# AGNOSTICS #
#############

# Functions to act upon numbers and OpenSCAD expressions:
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
    if _1dmatrices(args):
        if len(args) == 1:
            return tuple(-n for n in args[0])
        return tuple(starmap(sub, zip(*args)))
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


# Similarly, functions to make collections or act upon OpenSCAD expressions:


def background_dict(*args):
    """Make a dict or apply OpenSCAD’s background modifier."""
    if len(args) == 1 and isinstance(args[0], BaseExpression):
        return background(args[0])

    # Emulate hissp.macros.._macro_.% by imperative means.
    # Overwrite any repeated keys.
    if len(args) % 2 != 0:
        raise Exception(
            '“%” takes one OpenSCAD expression or an even number of arguments.'
        )
    coll = {}
    for i in map(lambda n: 2 * n, range(len(args) // 2)):
        coll[args[i]] = args[i + 1]
    return coll


def debug_set(arg, *args):
    """Make a set or apply OpenSCAD’s debug modifier."""
    if not args and isinstance(arg, BaseExpression):
        return debug(arg)

    # Emulate hissp.macros.._macro_.#.
    return {arg, *args}


##############
# MATHS ONLY #
##############

# Where there is little risk of confusion, these functions are overloadable by
# Python’s object-oriented magic methods.


def add(*args):
    """Add. Numbers and one-dimensional matrices only."""
    if not args:
        return 0  # As in Clojure.
    if _1dmatrices(args):
        if len(args) == 1:
            return args[0]
        return tuple(starmap(add, zip(*args)))
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


def _1dmatrices(args) -> bool:
    """Return True if arguments are same-length one-dimensional matrices."""
    return (
        all(isinstance(a, (tuple, list)) for a in args)
        and all(map(_numeric, args))
        and len(set(map(len, args))) == 1
    )
