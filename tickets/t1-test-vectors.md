# T1: Spacewar Test Vectors

Input/output pairs for each Spacewar math Processor, verified against PDP-1 emulator behavior.

**Depends on**: Existing Spacewar `.runs` source files.
**Produces**: The "first silicon" verification suite — proves the reference evaluator is correct.

## Required Vectors

| Processor | Example cases |
|-----------|--------------|
| `spacewar:sqrt` | `sqrt(0)`, `sqrt(1)`, `sqrt(2048)→23168`, `sqrt(131071)` |
| `spacewar:sin` | `sin(0)→0`, quadrant boundaries, near-overflow |
| `spacewar:cos` | Same coverage as sin, phase-shifted |
| `spacewar:random` | Known seed → known sequence (first 10 outputs) |
| `spacewar:multiply` | Small, large, negative, overflow-boundary values |
| `spacewar:divide` | Normal, near-zero divisor, maximum dividend |

## Format

JSON. One file per Processor. Each test case: `{ inputs: {...}, expected_outputs: {...} }`.
