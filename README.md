`lisscad` is a library for generating OpenSCAD code from Lissp scripts.

`lisscad` is in a pre-alpha state; it should not be used.

## History

`lisscad` is loosely patterned after `scad-clj`, ported from Clojure to another
dialect of Lisp. The new dialect, and `lisscad` itself, are implemented in
Python. This makes `lisscad` comparable to numerous Python-based OpenSCAD
generators/transpilers, including `SolidPython`, `SolidPy`, `openpyscad`,
`pycad`, `py2scad`, `py-scad` and `pyscad`.

`lisscad` was started to combine the best of its two ancestries: The simplicity
and elegance of a non-mutative Lisp like Clojure, and the JVM-free
accessibility and startup time of Python.

## Legal

Copyright (C) 2022 Viktor Eikman

`lisscad` is licensed as detailed in the accompanying file COPYING.md.
