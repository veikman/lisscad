"""Unit tests for the corresponding module."""

from pytest import mark

from lisscad.data.inter import Circle, Difference2D, Disable2D
from lisscad.op import add, mul, sub


@mark.parametrize('args, oracle', [
    ((), 0),
    ((0, ), 0),
    ((1, ), 1),
    ((-1, ), -1),
    ((-1, -1), -2),
    ((0, -1), -1),
    ((1, -1), 0),
    ((0, 0), 0),
    ((1, 1), 2),
    ((1, 1, 1), 3),
    ((1, 1, 1, -1), 2),
    ((10, 3.3, 3.3, -0.3), 16.3),
])
def test_add(args, oracle):
    """Check that add works as in Clojure."""
    assert add(*args) == oracle


@mark.parametrize('args, oracle', [
    ((0, ), 0),
    ((1, ), -1),
    ((-1, ), 1),
    ((-1, -1), 0),
    ((0, -1), 1),
    ((1, -1), 2),
    ((0, 0), 0),
    ((1, 1), 0),
    ((1, 1, 1), -1),
    ((1, 1, 1, -1), 0),
    ((10, 3.3, 3.3, -0.3), 3.7),
    ((Circle(3), Circle(2)), Difference2D((Circle(3), Circle(2)))),
])
def test_sub(args, oracle):
    """Check that subtraction is agnostic."""
    assert sub(*args) == oracle


@mark.parametrize('args, oracle', [
    ((), 1),
    ((0, ), 0),
    ((1, ), 1),
    ((-1, ), -1),
    ((-1, -1), 1),
    ((0, -1), 0),
    ((1, -1), -1),
    ((0, 0), 0),
    ((1, 1), 1),
    ((1, 1, 1), 1),
    ((1, 1, 1, -1), -1),
    ((2, 2), 4),
    ((Circle(1), ), Disable2D(Circle(1))),
])
def test_mul(args, oracle):
    """Check that subtraction is agnostic."""
    assert mul(*args) == oracle
