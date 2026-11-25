---
status: accepted
date: 2026-06-06
---

# The standard does not specify a Presentation language

Game Logic bodies are DIGS. Presentation bodies are written in whatever the target needs, and the standard names no language for them. A Presentation is thrown away and rewritten for each target: a Python script on a forgiving platform, a Vulkan pipeline in C++ on a demanding one. A portable Presentation language would bring back the machine coupling the split exists to keep out, at the cost of maintaining a language for code meant to be rewritten. The Interface Records are the whole contract: a Presentation's only duty to the game is the shape of the Interface Records it fills and reads.

## Considered options

- **A DIGS dialect exempt from determinism, with I/O.** Rejected. It puts I/O into the language whose identity is pure, total, and deterministic.

## Consequences

- A Game Port rewrites the Presentation in the target's language. EGS claims only the Game Logic and the Interface Records will still be readable in a century.
- Network Guards are DIGS expressions (ADR-0003). Whether Guards inside a Presentation are DIGS too is open until a real Game Port uses one; the lean is yes, because Guards are wiring.
- How much Presentation a game needs depends on how much its machine provides: a fantasy console's `draw_sprite` leaves little, a raw framebuffer leaves a lot.
