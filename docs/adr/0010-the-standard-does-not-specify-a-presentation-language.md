---
status: accepted
date: 2026-06-06
---

# The standard does not specify a presentation language

Game logic bodies are DIGS. Presentation bodies are written in whatever the target needs, and the standard names no language for them. A presentation is thrown away and rewritten for each target: a Python script on a forgiving platform, a Vulkan pipeline in C++ on a demanding one. A portable presentation language would bring back the machine coupling the split exists to keep out, at the cost of maintaining a language for code meant to be rewritten. The Interface Records are the whole contract: a presentation's only duty to the game is the shape of the Interface Records it fills and reads.

## Considered options

- **A DIGS dialect exempt from determinism, with I/O.** Rejected. It puts I/O into the language whose identity is pure, total, and deterministic.

## Consequences

- A Port rewrites the presentation in the target's language. EGS claims only the game logic and the Interface Records will still be readable in a century.
- Network guards are DIGS expressions (ADR-0003). Whether guards inside a presentation are DIGS too is open until a real Port uses one; the lean is yes, because guards are wiring.
- **Open**: how much a target's platform provides (a fantasy console's `draw_sprite` or a raw framebuffer) depends on where the Runtime sits (ADR-0002).
