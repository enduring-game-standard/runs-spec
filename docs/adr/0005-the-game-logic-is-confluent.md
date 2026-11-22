---
status: accepted
date: 2026-06-05
---

# The game logic is confluent: the wiring states the whole order

The colored Petri net pattern RUNS is built on is not deterministic by itself: when two consumers compete for one input, which one runs is a free choice. RUNS closes that with two structural rules on the game logic, and states no execution order at all:

1. **Every change goes through a Processor.** A shared resource, such as the random number, passes through one Record in wired order (`prng_v0` to `prng_vN`), so two Processors that touch one Record are always ordered by the wiring.
2. **The guards on one Record partition**: exactly one is true, always.

Given both, one tick of the game logic is a DAG, and every topological order of it yields identical results. Two Processors the DAG leaves unordered touch no shared Record, so they may run in parallel. The loop across ticks is in the wiring; any other repetition is inside a Processor, where DIGS totality bounds it.

Confluence holds for the game logic only. The Realization uses the same wiring but is exempt (ADR-0006).

## Consequences

- There is no execution-order primitive. `phases:` and `order:` are a crutch for resources that should pass through the wiring.
- A validator can check both rules statically. Game logic that fails either is not deterministic.
- Revisit against the first second game in RUNS, where shared resources and parallel dispatch are exercised.
