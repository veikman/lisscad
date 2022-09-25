"""Unit tests for the corresponding module."""

from lisscad.data.inter import Circle
from lisscad.data.other import Asset
from pytest import mark


@mark.parametrize('_, input, oracle',
                  [('empty_tuple', (), ()), ('empty_list', [], ()),
                   ('expression', Circle(1), (Circle(1), )),
                   ('tuple', (Circle(1), Circle(2)), (Circle(1), Circle(2))),
                   ('list', [Circle(1), Circle(2)], (Circle(1), Circle(2))),
                   ('callable', lambda:
                    (Circle(1), Circle(2)), (Circle(1), Circle(2)))])
def test_asset_convenience(_, input, oracle):
    asset = Asset(content=input)
    ret = asset.content()
    assert ret == oracle
    assert type(ret) is type(oracle)
