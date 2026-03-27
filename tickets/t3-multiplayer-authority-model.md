# T3: Multiplayer Authority Model

A distribution annotation layer for RUNS Networks — metadata specifying which Processors run where and how state is synchronized across machines.

**Needs**: Someone who has shipped multiplayer games AND designed protocol specifications.
**Estimated effort**: 12+ months. Vast design space.

## The Problem

RUNS game logic is pure (`inputs → state → outputs`) but has no concept of:
- Which machine is authoritative for which state
- Client-side prediction and rollback reconciliation
- Conflict resolution (two players grab the same item simultaneously)
- Consistency requirements (strict for gameplay state, eventual for particles)

## Candidate Primitives

```yaml
network fps:game_tick
  authority: server
  client_predicted: [fps:movement, fps:weapon_fire]
  server_only: [fps:damage, fps:item_pickup]
  reconciliation: rollback
```

The game logic (Processors) stays unchanged. Distribution is a runtime concern layered on top.

## Open Questions

- What are the correct authority models? (`lockstep`, `server`, `peer-to-peer`, `hybrid`?)
- How does rollback interact with RUNS state serialization?
- How does this interact with WOCS (the coordination protocol)?
- Can the same game Network run in lockstep mode for local multiplayer and server-authoritative mode for online?

## Precedent

GGPO (rollback for fighting games), Valve Source Engine (client prediction + server reconciliation), Age of Empires (lockstep deterministic simulation).
