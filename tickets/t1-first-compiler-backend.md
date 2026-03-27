# T1: First Compiler Backend

A `runs-prim` → target language compiler that reads Processor ASTs and emits executable code for one platform.

**Estimated size**: 500–1000 lines per backend.
**Depends on**: Reference parser, test vectors.
**Produces**: The first machine-compiled RUNS game.

## Candidate Targets

| Target | Pros | Cons |
|--------|------|------|
| JavaScript | Runs in any browser, instant demo | Float semantics need care |
| Lua (PICO-8) | Already hand-compiled, can validate against existing cartridge | Token limits constrain output |
| C | Performance, N64/embedded path | More boilerplate |
| WASM | Portable binary, near-native speed | Needs runtime host |

## Acceptance Criteria

- Compiles all Spacewar Processors to target language
- Compiled output produces identical results to reference evaluator for all test vectors
- Automated: `runs compile spacewar --target js` produces a playable artifact
