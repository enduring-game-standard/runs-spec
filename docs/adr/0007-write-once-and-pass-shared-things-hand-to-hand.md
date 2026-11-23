---
status: accepted
date: 2026-06-06
---

# Write once, never overwrite; pass shared things hand to hand

The law holds at every scale: across the Network, where a fan-in is a fold that passes its accumulator from one Processor to the next; and inside a Processor body, as static single assignment. A Record keeps its value until a Processor gives it a new one. A shared resource (the random number, an accumulator, an object pool) passes hand to hand as a chain of values, `v0` to `vN`. Source that looks imperative is shorthand for the law: `x = x + 1` is `x_v1 = x_v0 + 1`, and a loop is a bounded fold. The compiled form may still use real registers.

## Consequences

- `position = position + velocity` is pure as written: one link of a chain, `position_v0` to `position_v1`.
- Game logic that overwrites a Record outside the wiring, or needs authored execution order, likely carries an original machine's workaround. Pass it hand to hand instead, and the order follows (ADR-0005).
- The game logic steps by a fixed quantum, delivered on an Interface Record (a tick count or a constant step). Variable time, such as render interpolation, is presentation.
- A validator lowers bodies to static single assignment, then checks the two rules of ADR-0005 in one pass.
