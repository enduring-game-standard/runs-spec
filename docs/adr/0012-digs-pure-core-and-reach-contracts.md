---
status: accepted
date: 2026-06-06
---

# DIGS has a pure core and declared reach-contracts

Fixed arithmetic, a static step bound, and a static memory footprint are not part of being pure, total, and deterministic. Dhall is all three with unbounded naturals and lists, and Factorio is bit-deterministic across machines with an unbounded factory. DIGS has a core every Processor meets, and contracts declared in types that trade some games for some hardware reach.

**Core**, which validity checks:

- Outputs depend only on declared inputs; no observable state.
- Every Processor ends on every input: loop counts are fixed before the loop and unchanged during it, with no general recursion.
- Evaluation order is fixed by the grammar: no reassociation, no fused operations, fixed short-circuit order.

**Reach-contracts**, declared in types:

1. **Arithmetic**: the game logic declares every arithmetic it depends on (ADR-0002), so it gives identical bits on every machine. Floating point without it diverges across hardware; Quake demos desync, and fixed-point DOOM's do not.
2. **Static step bound**, optional: a ceiling on steps per tick for real-time targets. Totality does not imply it.
3. **Static memory footprint**, optional: bounded lists give a RAM ceiling at bake time for small targets.

## Considered options

- **Bounded lists required.** Rejected. Determinism does not need them, and they make games with unbounded deterministic state impossible to express.
- **Unbounded state moved to the Realization.** Rejected. It puts deterministic game logic on the side exempt from determinism.

## Consequences

- Lists may be unbounded. Spacewar's `object[24]` fits a PDP-1; Factorio's `entities[]` needs an allocator, and a PICO-8 Factorio is impossible, which is the true answer.
- "No dynamic allocation" becomes "no observable memory": no pointers, no addresses. Lockstep holds because DIGS exposes no addresses.
- Unbounded state lives in the game logic. Each Processor is a bounded loop; the only unbounded loop is the tick, in the wiring, visible in the topology. A leak in the game logic is deterministic and reproducible.
- Changing a reach-contract changes game logic, so it makes a Variant, not a Port. Chocolate DOOM on a TI-83 needs smaller limits, so it is a Variant.
- Validity checks the core only. "Too big" or "too slow" is advice or a target's decision.
