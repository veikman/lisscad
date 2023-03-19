"""Unit tests for the corresponding module."""

import re
from contextlib import nullcontext as does_not_raise

from lisscad.vocab.base import circle, sphere, translate, union
from pytest import mark, raises


@mark.parametrize('_, vocab, args, verdict', [
    ('one_unknown', union, (1, ),
     raises(
         TypeError,
         match=
         "Cannot contain non-OpenSCAD expression “1” of type <class 'int'>.")),
    ('two_unknown', union, ('1', 2),
     raises(
         TypeError,
         match=
         "Cannot contain non-OpenSCAD expression “1” of type <class 'str'>.")),
    ('trailing_unknown', union, (circle(1), 2),
     raises(
         TypeError,
         match=
         "Cannot contain non-OpenSCAD expression “2” of type <class 'int'>.")),
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
    ('mismatch_0d', translate, ((), circle(1)),
     raises(
         ValueError,
         match='Cannot translate OpenSCAD expression with 0D argument ().')),
    ('mismatch_1d', translate, ((1, ), circle(1)),
     raises(
         ValueError,
         match=re.escape(
             'Cannot translate OpenSCAD expression with 1D argument (1,).'))),
    ('mismatch_2d', translate, ((1, 2), sphere(1)),
     raises(ValueError,
            match=re.escape('Cannot translate 3D OpenSCAD expression '
                            'with 2D argument (1, 2).'))),
    ('mismatch_3d', translate, ((1, 2, 3), circle(1)),
     raises(ValueError,
            match=re.escape('Cannot translate 2D OpenSCAD expression '
                            'with 3D argument (1, 2, 3).'))),
    ('mismatch_4d', translate, ((1, 2, 3, 4), circle(1)),
     raises(ValueError,
            match=re.escape('Cannot translate OpenSCAD expression '
                            'with 4D argument (1, 2, 3, 4).'))),
    ('mismatch_multiexpression', translate, ((1, 2, 3), circle(1), circle(2)),
     raises(ValueError,
            match=re.escape('Cannot translate 2D OpenSCAD expressions '
                            'with 3D argument (1, 2, 3).')))
])
def test_basic_safeguards(_, vocab, args, verdict):
    with verdict:
        vocab(*args)
