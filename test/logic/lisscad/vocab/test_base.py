"""Unit tests for the corresponding module."""

from contextlib import nullcontext as does_not_raise

from lisscad.vocab.base import circle, sphere, union
from pytest import mark, raises


@mark.parametrize('_, vocab, args, verdict', [
    ('one_unknown', union, (1, ),
     raises(TypeError,
            match="Cannot contain unknown OpenSCAD operation <class 'int'>.")),
    ('two_unknown', union, ('1', 2),
     raises(TypeError,
            match="Cannot contain unknown OpenSCAD operation <class 'str'>.")),
    ('trailing_unknown', union, (circle(1), 2),
     raises(TypeError,
            match="Cannot contain unknown OpenSCAD operation <class 'int'>.")),
    ('all_2d', union, (circle(1), circle(2)), does_not_raise()),
    ('all_3d', union, (sphere(1), sphere(2)), does_not_raise()),
    ('one_of_each', union, (circle(1), sphere(2)),
     raises(TypeError, match='Cannot contain mixed 2D and 3D expressions.$')),
    ('two_of_each', union, (circle(1), sphere(1), circle(2), sphere(2)),
     raises(TypeError, match='Cannot contain mixed 2D and 3D expressions.$')),
    ('one_2d', union, (circle(1), sphere(2), sphere(3)),
     raises(TypeError,
            match='Cannot contain mixed 2D and 3D expressions. '
            'One, in place 1 of 3, is 2D.')),
    ('one_3d', union, (circle(1), circle(2), sphere(3)),
     raises(TypeError,
            match='Cannot contain mixed 2D and 3D expressions. '
            'One, in place 3 of 3, is 3D.')),
])
def test_basic_safeguards(_, vocab, args, verdict):
    with verdict:
        vocab(*args)
