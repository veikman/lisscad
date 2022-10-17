"""Utilities built on top of OpenSCAD."""

from itertools import pairwise

from lisscad.data.inter import LiteralExpression
from lisscad.vocab.base import hull, union


def pairwise_hull(*shapes: LiteralExpression):
    """The combined hulls of each overlapping pair of shapes."""
    return union(*(hull(*pair) for pair in pairwise(shapes)))
