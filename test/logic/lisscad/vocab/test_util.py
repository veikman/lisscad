"""Unit tests for the corresponding module."""

from lisscad.vocab.util import _generate_fillet_xy_coordinates
import pytest


@pytest.mark.parametrize(
    ('inputs', 'expected_return'),
    [
        pytest.param(
            (1, 1, 1, 1),
            [(0.0, 1), (1.0, 0)],
            id='unit-circle',
        ),
        pytest.param(
            (100, 100, 5, 20),
            [
                (0.0, 100),
                (2.0204102886728803, 80),
                (8.348486100883202, 60),
                (19.999999999999996, 40),
                (40.000000000000014, 20),
                (100.0, 0),
            ],
            id='100-circle',
        ),
        pytest.param(
            (300, 10, 4, 2.5),
            [
                (0.0, 10.0),
                (9.526249034443723, 7.5),
                (40.19237886466842, 5.0),
                (101.5686516701557, 2.5),
                (300.0, 0.0),
            ],
            id='ellipse',
        ),
    ],
)
def test_fillet(inputs, expected_return):
    """Exercise the _generate_fillet_xy_coordinates function.

    Deliberately contradictory inputs are not tested here.

    """
    ret = list(_generate_fillet_xy_coordinates(*inputs))
    assert ret == expected_return
