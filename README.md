`lisscad` is a library for generating OpenSCAD code from Lissp scripts.

Don’t worry! You’re not supposed to track all the parentheses yourself. With an
automatic formatter like `parinfer`, Lissp is easier than Python.

## Features

* The terseness of Lisp.
* The usability of Lisp. For example, with the `->>` threading macro, you can
  code for OpenSCAD operations in the order that they will be executed, instead
  of the order they have in OpenSCAD scripts.
* The `lisscad` package is executable on the command line to manage CAD
  projects, including watching a project with `inotify` to re-render work in
  progress.
* It takes one line in CAD scripts to import `lisscad`, and one line to
  transpile to OpenSCAD. Both of these and a Git repo are included in a
  template for new projects.
* Most of `lisscad` is pure, type-annotated Python 3.10+. It can be used
  without the Lissp layer. Conversely, you can use any Python code from Lissp.

The data model is based on dataclasses, not object-oriented Python. Pydantic
handles type conversions for you in the back end.

See also the [goals](doc/goal.md) of the project.

## Usage

`lisscad` is in a pre-alpha state; it should not be used. The following is a
draft.

### Command-line interface

To start a new project:

```shell
lisscad new myproject
cd myproject
```

The shape of your model(s) is defined by `main.lissp`. Edit it. To render your
project to OpenSCAD once, run the normal Lissp compiler:

```shell
lissp main.lissp
```

To render a 3D model all the way to STL, pass a CLI argument via the Lissp
compiler with `--`:

```shell
lissp main.lissp -- -r
lissp main.lissp -- --render  # Equivalent long option.
```

To view the most recently transpiled model in the OpenSCAD GUI:

```shell
lisscad view
```

To automatically transpile to OpenSCAD each time you edit `main.lissp`, so that
the GUI always shows the current version:

```shell
lisscad watch
```

### Scripting interface

The vocabulary of `lisscad` is very similar to that of OpenSCAD.
However, some function signatures have been adjusted to reduce the overall
complexity of the interface.

* Example: `lisscad`’s `cube` is centred by default, because `sphere` is
  centred in both OpenSCAD and `lisscad`.
* Example: If you want to use a keyword argument to define an angle, it’s named
  `angle`; it doesn’t vary.

For maximum fidelity to OpenSCAD, use the `lisp` prelude:

```lisp
(lisscad.prelude.._macro_.lisp)

(translate '(1 0) (square '(2 3)))
```

`lisscad` gives you the choice of consistency with standard geometric and
English terms instead. For example, in its `english` prelude, `lisscad` has a
`square` function that draws squares, and a `rectangle` function that draws
rectangles.

```lisp
(lisscad.prelude.._macro_.english)

(right 1 (rectangle '(2 3)))
```

For the use of operators like `+`, see [here](doc/op.md).

### Editor integration

Lissp is not a common dialect, so you may need to inform your text editor that
it is Lisp. Here is an example of how to do that in Vim (`~/.vimrc`) or Neovim
(`init.vim`):

    au BufRead,BufNewFile *.lissp             setfiletype lisp

## History

`lisscad` is loosely patterned after `scad-clj`, ported from Clojure to another
dialect of Lisp. The new dialect, and `lisscad` itself, are implemented in
Python. This makes `lisscad` comparable to numerous Python-based OpenSCAD
generators/transpilers, including SolidPython, SolidPy, `openpyscad`,
`pycad`, `py2scad`, `py-scad` and `pyscad`.

`lisscad` was started to combine the best of its two ancestries: The simplicity
and elegance of a Lisp similar to Clojure, and the JVM-free accessibility and
startup time of Python. One notable difference is that whereas `scad-clj` uses
hash tables as an implementation detail in its intermediate data model, and
SolidPython has its own object-oriented data model, `lisscad` uses Pydantic
dataclasses.

## Legal

Copyright (C) 2022 Viktor Eikman

`lisscad` is licensed as detailed in the accompanying file COPYING.md.
