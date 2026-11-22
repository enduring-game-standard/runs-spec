---
status: accepted
date: 2026-06-06
---

# Processor granularity is a spectrum; decomposition is a convention

A Processor can be as large as a whole original function rewritten in DIGS, or as small as one atomic operation (`vec_x`), and both are valid RUNS. Full decomposition, a game built from shared atomic Processors bundled into Sub-Networks, is a convention. DOOM puts several Processors' worth of logic in one C function; a rewrite of each function into one Processor is still DOOM exactly, and forbidding it would make every Conversion decompose before it can run. The commons also has no body to enforce decomposition.

## Consequences

- Convert first, decompose later: a function-for-function rewrite is valid RUNS from the start.
- The guard laws (ADR-0008) bind only once branch targets are separate Processors. A monolith may hold an internal `if state == torpedo:`, because the Network sees one Processor. Once the targets are separate Processors, a dispatcher Processor that calls them is forbidden steering, and arc guards must route instead. A body `if` that writes a tag (`state = exploding`) is action, not steering.
- Decomposition follows behavior, not original intent: `vec_3` composes `vec_x`, `vec_y`, `vec_z` by what they compute.
- No validator reports a Processor as too coarse.
- **Open**: the Standard stage of the conversion process requires complying with the conventions, and decomposition is one. Whether a Conversion must be fully decomposed to reach Standard is not decided.
