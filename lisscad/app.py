"""Application model.

This module is intended to be imported from a Lissp script.

"""

from lisscad.data.other import Asset
from lisscad.py_to_scad import transpile


def write(assets: list[dict | Asset]):
    """Convert intermediate representations to OpenSCAD code."""
    for a in assets:
        if not isinstance(a, Asset):
            a = Asset(**a)
        with open(f'{a.name}.scad', mode='w') as f:
            f.writelines('\n'.join(transpile(a.model)) + '\n')
