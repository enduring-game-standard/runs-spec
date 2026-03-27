# T1: Runtime Interface Specification

Formal spec for the four-service boundary between RUNS game logic and platform runtimes: timing, input, rendering, audio.

**Depends on**: At least two runtimes to validate the abstraction.
**Produces**: The contract that all RUNS runtimes implement.

## The Four Services

1. **Timing** — Runtime provides `delta_time` and `tick_count` as inbound Fields. Fixed-timestep semantics.
2. **Input** — Runtime provides player input state as inbound Fields. Abstracted over physical devices.
3. **Rendering** — Game logic produces render objects as outbound Fields. Runtime realizes them visually.
4. **Audio** — Game logic produces audio triggers as outbound Fields. Runtime realizes them sonically.

## Precedent

libretro's four-abstraction API (video, audio, input, state) is the closest existing model. RUNS adds typed Fields and capability negotiation.

## Open Questions

- Should the spec define a minimal set of render object types (sprite, mesh, text)?
- Should audio triggers reference AEMS sound assets or describe waveforms?
- How does state serialization (save/load) interact with the runtime interface?
