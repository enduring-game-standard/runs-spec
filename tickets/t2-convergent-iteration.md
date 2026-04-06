# T2: Convergent Iteration Construct

A `runs-prim` language construct for "iterate until convergence, with a provable upper bound."

**Needs**: Programming language theorist who understands game algorithms.
**Estimated effort**: 1–3 months of language design.

## The Problem

Many game algorithms (A* pathfinding, physics constraint solvers, raycasting, Newton-Raphson, continuous collision detection) iterate until a condition is met. The iteration count is data-dependent, not compile-time-known. `runs-prim` 1.0 has only `for i in range(n)` where `n` must be compile-time-known.

The fuel pattern (pass an explicit max-iteration budget) works but is unsatisfying — it pollutes the Processor interface with an implementation detail and wastes cycles on trivial cases.

## Candidate Design

```runs-prim
for step in converge(max: graph.node_count):
  # ... A* logic ...
  if goal_reached:
    break
```

`converge(max: expr)` iterates at most `expr` times (totality preserved). `break` exits early (avoids waste). The `max` expression must derive from inputs (compiler verifies finiteness).

## Open Questions

- Does `break` compromise purity? (Probably not — it's control flow, not mutation.)
- Should `converge` be a statement or an expression (producing the final loop state)?
- Can the compiler infer the bound from usage patterns, eliminating the explicit `max`?
- Precedent: Idris/Agda fuel pattern, GLSL bounded loops.

## Cross-Reference: Network-Level Bounded Iteration

The [Network Topology](../NETWORK_TOPOLOGY.md) specification introduces an `iterate:` phase primitive for bounded repetition at the Network level (e.g., physics constraint solver iterations). This addresses the multi-pass-over-collections use case (Gauss-Seidel relaxation, iterative rendering) but does NOT address the within-Processor convergence case (A* early termination, Newton-Raphson). Both levels of bounded iteration are needed — `iterate:` for Network-level repetition, `converge` for DIGS-level early exit.
