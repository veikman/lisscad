"""For use in CAD-project Lissp source code."""


class _macro_:
    """Provide Hissp macros."""

    def standard():  # type: ignore[misc]
        """Provide the standard lisscad prelude."""
        return (
            (
                'lambda',
                (),
                # This works:
                (
                    'hissp.._macro_.prelude', ),
                ('print', ('quote', 'debug0')),
                ('exec', ('quote', 'print("debug1")')),
                # This imports the named module but not into the namespace of
                # the caller of the macro:
                ('exec', ('quote', 'from lisscad.shorthand import *')),
                # This is a syntax error:
                ('eval', ('quote', 'from lisscad.shorthand import *')),
            ), )
