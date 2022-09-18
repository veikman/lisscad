Single-character operators in `lisscad` are intended to provide a
CAD-friendly compromise between the library’s various ancestors and targets.

`lisscad` uses Lisp-style prefix notation for all operators and does not
privilege them syntactically. Some are used as condensed shorthand for
operations in OpenSCAD, to save space.

| Operator | OpenSCAD | Python | Lissp | Clojure | `lisscad` |
| -------- | -------- | ------ | ----- | ------- | --------- |
| `+` | Infix addition | Infix addition | N/A | Variary addition | Variary addition |
| `-` | Infix subtraction | Infix subtraction | N/A | Variary subtraction | Variary subtraction and OpenSCAD `difference` |
| `*` | Infix multiplication and disabling modifier | Infix multiplication | N/A | Variary multiplication | Variary multiplication and OpenSCAD modifier |
| `/` | Infix true division | Infix true division | N/A | Variary true division | Variary true division |
| `%` | Infix modulo and backgrounding modifier | Infix modulo | Hash-map literal | N/A | OpenSCAD modifier |
| `#` | Debug modifier | Comment | Strings that process Python escapes | Anonymous functions | OpenSCAD modifier |
| `\|` | N/A | OR, including union | N/A | N/A | OpenSCAD `union` |
| `&` | N/A | AND | N/A | Argument to anonymous function | OpenSCAD `intersection` |
| `!` | Root modifier | Part of `!=` | Extra (reader macro) | N/A | OpenSCAD modifier, but it must be escaped (`\!`) |
