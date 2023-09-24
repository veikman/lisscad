The main goal of the `lisscad` project is to provide a simple programmatic CAD
tool.

By way of explanation, the main goal of `lisscad` is based on the understanding
that OpenSCAD itself is not and will not be simple. Its built-in text editor is
not as good as general text editors. More importantly, OpenSCAD has some
deficiencies even as a domain-specific programming language, including its
awkward syntax.

`lisscad` tries to deliver simplicity mainly through consistency and minimalism
at the scripting stage. Specifically:

* The scripting language is Lissp, a minimalistic dialect of Lisp, similar to
  Clojure.
* Operations are well defined. There is less room for error than in OpenSCAD.

`lisscad` has the following secondary goals:

* The power of a high-order general programming language instead of a DSL.
* Interoperability with Python, another general programming language.
* Ease of use. Outside of the minimalistic scripting environment, `lisscad` has
  bells and whistles.
    * Good CLI utilities for project management.
    * Built-in safety checks with error messages for common mistakes, such as a
      mismatch between the number of dimensions in an operation’s argument and
      its operand.
    * Thanks to Lissp’s ability to handle special characters in [operator
      names](op.md), special OpenSCAD operations like `%` are accessible by
      their original names, not mangled as they would have to be for Python.
    * Optionally saving 2D images of 3D renders etc.
* Built-in higher-level CAD operations.

The following are not goals of `lisscad`:

* Absolute fidelity to OpenSCAD’s vocabulary. A more faithful interface could
  be added as an alternative prelude, but this is not planned.
* Laxity for the sake of working flexibly with 2 or 3 dimensions. OpenSCAD will
  not complain if, for example, you `translate` a 3D shape with coordinates for
  only 2 dimensions, or vice versa. `lisscad` will complain if you do that, so
  as not to hide error.
* Mutability. Some Python–OpenSCAD transpilers are marketed with the argument
  that values are more mutable in Python than they are in OpenSCAD. `lisscad`
  does not do this, because of the primary goal of simplicity.
* Object orientation.
