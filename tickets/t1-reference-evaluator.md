# T1: Reference Evaluator

Tree-walking interpreter that evaluates a Processor's AST against input values and produces output values. This is the **oracle** — any optimizing compiler's output must match it.

**Estimated size**: 800–1200 lines.
**Depends on**: Reference parser (t1-reference-parser).
**Produces**: The ground truth for all future compilers to test against.

## Acceptance Criteria

- Evaluates all Spacewar math Processor bodies against PDP-1 test vectors
- Handles all `runs-prim` 1.0 constructs: `let`, `if`/`elif`/`else`, `for`/`range`, `output`, `with`, sub-Processor calls
- Implements `int`, `int32`, `fixed16`, `bool`, and game-defined types (`spacewar:fixed18` with ones-complement)
- Reports precondition violations with the failing expression
