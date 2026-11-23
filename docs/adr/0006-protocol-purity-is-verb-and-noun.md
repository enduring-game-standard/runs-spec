---
status: accepted
date: 2026-06-06
---

# Protocol purity is verb and noun; determinism is a game-logic convention

"Pure" did two jobs: a Processor transforms and a Record stores (verb and noun), and a Processor's outputs depend only on its declared inputs (determinism). A renderer is a verb, so it is a Processor, but it is not deterministic. The protocol keeps only the verb and noun split, with one kind of Processor. Determinism is a convention that holds for the game logic (ADR-0001), which makes the game logic confluent (ADR-0005).

## Consequences

- A game's Processors split into game logic (DIGS, deterministic, works on any device) and presentation (machine-specific I/O: timing and input in, rendering and audio out, exempt from determinism).
- The two sides meet only at Interface Records. A Record is inert data and belongs to neither side; a Processor at the seam would have to pick a side, and would then be the first Processor of that side. Any translation is a Processor on one side, up to the seam.
- Two independent swaps follow: replace game logic Processors and you have a **Variant**; replace the presentation and you have a **Port**.
- A Port keeps the game logic bit for bit, so its reach-contracts too (ADR-0012). A target that cannot hold them needs changed game logic, which makes the result a Variant.
- The names are functional, not implementation names: "game logic" and "presentation", not "DIGS" and "machine".
- Revisit against the first game with two presentations of one game logic.
