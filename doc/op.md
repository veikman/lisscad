`lisscad` uses Lisp-style prefix notation for all operators and does not
privilege them syntactically. Some are single-character functions or macros,
the names of which would be illegal for functions in Python.

Single-character operators in `lisscad`’s standard prelude are intended to
provide a CAD-friendly compromise between the library’s various ancestors and
targets: Terse maths, collection literals, single-character modifiers as used
in OpenSCAD, and shorthand for OpenSCAD’s functions inspired by SolidPython.

| Operator | OpenSCAD | Python | Lissp | Clojure | `lisscad` |
| -------- | -------- | ------ | ----- | ------- | --------- |
| `+` | Infix addition | Infix addition | N/A | Variary addition | Variary addition |
| `-` | Infix subtraction | Infix subtraction | N/A | Variary subtraction | Variary subtraction; OpenSCAD `difference` |
| `*` | Infix multiplication; disabling modifier | Infix multiplication | N/A | Variary multiplication | Variary multiplication; OpenSCAD modifier |
| `/` | Infix true division | Infix true division | N/A | Variary true division | Variary true division |
| `%` | Infix modulo; backgrounding modifier | Infix modulo; string formatting | Hash-map literal | N/A | Hash-map literal; OpenSCAD modifier |
| `#` | Debug modifier | Comment | Strings that process Python escapes; set (collection) literal | Anonymous functions | Python string escapes; set literal; OpenSCAD modifier |
| `&` | N/A | AND | N/A | Argument to anonymous function | OpenSCAD `intersection` |
| `!` | Root modifier and negation | Negation as part of `!=` | Extra (reader macro) | N/A | OpenSCAD modifier, but it must be escaped (`\!`) |
| `@` | N/A | Matrix multiplication | List literal | Atom `deref` | List literal |
| `^` | Exponentiation | XOR | N/A | Metadata | N/A (undecided) |

Note: The pipe character, `|`, was used for `union` in `lisscad` until `hissp`
0.5.0 reserved that character for fragment tokens.
