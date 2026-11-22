---
status: accepted
date: 2026-06-06
---

# The two laws of a guarded branch: totality and thinness

A guarded branch is the Network choosing exactly one outgoing path. It obeys two laws:

1. **Totality**: the guards partition the value they test, exactly one true, always. A closed enum lets a tool check every case; an open type (an integer, a string) needs an explicit `else` arc.
2. **Thinness**: a guard reads a fact and never computes one. It tests a Field a Processor already wrote (`can_see_player`, a state tag).

Decision structure lives in the arcs; computation and actions live in Processors. A Processor that decides and then acts splits into perceive, route, act: one Processor writes the tag, the arcs route on it, downstream Processors act. No Processor contains an `if` that steers the Network, so every branch target is composable.

## Consequences

- A validator checks the partition over the tested value's type, and that each guard only reads existing Fields.
- The law depends on decomposition (ADR-0011): it binds once the branch targets are separate Processors.
- The conventions recommend closed-enum tags over strings as the tested value.
