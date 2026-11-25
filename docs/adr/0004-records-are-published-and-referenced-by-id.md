---
status: accepted
date: 2026-06-05
---

# Records are published on their own and referenced by ID

A Record is a content-addressed event published on its own, the same as a Processor or a Network. A Network references the Records and Processors it wires by ID and never embeds them, so it stays wiring only. Three properties that "published" used to blur are separate:

- **Published or not**: is it an addressable event on the commons? A Record always is.
- **Reusable or game-specific**: a spectrum, from shared `runs:` Records to a schema no other game imports.
- **Baked or interpreted**: a Record is always baked into the build, never read at play time.

## Considered options

- **Not published.** Rejected. Source on the commons must be complete; a Network that references an unresolvable `spacewar:object` is a fragment. A Record is source code in the same sense a variable declaration is.
- **Embedded in the Network.** Rejected. The Network would reference Processors but contain Records, an asymmetry with no reason behind it.

## Consequences

- Nostr is a publication layer, not a real-time database, so the commons is touched only at lifecycle boundaries (discovery and build, AEMS load and save). Baking bridges the commons to the tick loop.
- A manifest pins the exact closure by content hash; the build tool resolves it, flattens the graph, and bakes one self-contained build.
- Untested: revisit when the first build tool exists.
