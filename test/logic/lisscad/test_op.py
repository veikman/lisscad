"""Unit tests for the corresponding module."""

from lisscad.data.inter import Circle, Difference2D
from lisscad.op import sub
from pytest import mark


@mark.parametrize('args, oracle',
                  [((0, ), 0), ((1, ), -1), ((-1, ), 1), ((-1, -1), 0),
                   ((0, -1), 1), ((1, -1), 2), ((0, 0), 0), ((1, 1), 0),
                   ((1, 1, 1), -1), ((1, 1, 1, -1), 0),
                   ((10, 3.3, 3.3, -0.3), 3.7), ((10, 3.3, 3.3, -0.3), 3.7),
                   ((Circle(3), Circle(2)), Difference2D(
                       (Circle(3), Circle(2))))])
def test_sub(args, oracle):
    """Check that subtraction is agnostic."""
    assert sub(*args) == oracle
