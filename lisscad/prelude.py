"""For use in CAD-project Lissp source code."""


class _macro_:
    """Provide Hissp macros."""

    def standard():  # type: ignore[misc]
        """Provide the standard lisscad prelude."""
        return (
            (
                'lambda',
                (),
                ('hissp.._macro_.prelude', ),  # The standard Hissp prelude.
                # OpenSCAD-like CSG CAD functions:
                ('exec', ('quote', 'from lisscad.shorthand import *'),
                 ('globals', )),
            ), )
