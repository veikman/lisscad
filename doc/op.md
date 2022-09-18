Single-character operators in `lisscad` are intended to provide a
CAD-friendly compromise between the library’s various ancestors and targets.

`lisscad` uses Lisp-style prefix notation for all operators and does not
privilege them syntactically. Some are used as condensed shorthand for
operations in OpenSCAD, to save space.

| Operator | OpenSCAD | Python | Lissp | Clojure | `lisscad` |
| -------- | -------- | ------ | ----- | ------- | --------- |
| `+` | Infix addition | Infix addition | N/A | Variary addition | Variary addition |
| `-` | Infix subtraction | Infix subtraction | N/A | Variary subtraction | Variary subtraction and OpenSCAD `difference` |
