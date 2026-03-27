# T1: Reference Parser

Single-file parser that reads `.runs-prim` source and emits an AST as JSON.

**Estimated size**: 500–800 lines in Python, JavaScript, or Lua.
**Depends on**: [EXPRESSION_LANGUAGE.md](../DIGS_EXPRESSION_LANGUAGE.md) EBNF grammar.
**Produces**: The canonical tool for validating that the grammar is implementable and unambiguous.

## Acceptance Criteria

- Parses all Spacewar Processor bodies without error
- Rejects syntactically invalid input with line/column error messages
- Emits a JSON AST that roundtrips (AST → pretty-print → re-parse → identical AST)
- No dependencies beyond the implementation language's standard library
