---
status: accepted
date: 2026-06-05
---

# The Game Logic is confluent: the wiring states the whole order

The colored Petri net pattern RUNS is built on is not deterministic by itself: when two consumers compete for one input, which one runs is a free choice. RUNS closes that with two structural rules on the Game Logic, and states no execution order at all:

1. **Every change goes through a Processor.** A shared resource, such as the random number, passes through one Record in wired order (`prng_v0` to `prng_vN`), so two Processors that touch one Record are always ordered by the wiring.
2. **The Guards on one Record partition**: exactly one is true, always.

Given both, one tick of the Game Logic is a DAG, and every topological order of it yields identical results. Two Processors the DAG leaves unordered touch no shared Record, so they may run in parallel. The loop across ticks is in the wiring; any other repetition is inside a Processor, where DIGS totality bounds it.

Confluence holds for the Game Logic only. The Presentation uses the same wiring but is exempt (ADR-0006).

## Consequences

- There is no execution-order primitive. `phases:` and `order:` are a crutch for resources that should pass through the wiring.
- A validator can check both rules statically. Game Logic that fails either is not deterministic.
- Revisit against the first second game in RUNS, where shared resources and parallel Dispatch are exercised.
