---
status: accepted
date: 2026-11-22
---

# The split between game logic and Realization is a convention, not protocol

The protocol is valid RUNS: Records, Processors, the Network, and DIGS. It hardens now and stays still. The conventions are standard RUNS: how compliant a program is, and what that unlocks (shared Records and Processors, side-by-side comparison, Ports, the check that the game logic run alone matches the original). The split between game logic and Realization belongs to the conventions, because where the line falls is a judgment a later editor may revise. A protocol holds rules that stay still, and a judgment open to revision cannot be one. Bitcoin draws the same line between consensus rules (what is valid) and standardness policy (what nodes relay).

## Considered options

- **Split in the protocol**: every valid program declares its game logic and its Realization. Rejected. Every step of a conversion before full separation would be invalid RUNS, so the protocol would forbid the route to its own goal. It also hardens today's two-region model against games that need another shape.

## Consequences

- A program that rewrites an original line for line into Records, Processors, and Networks, with no split, is valid RUNS and not yet standard.
- Port and Variant are defined against the conventions, not the protocol.
- This spec declares Record kinds today (`game`, `interface`, `presentation`; DIGS_EXPRESSION_LANGUAGE.md, the running example). They move to the conventions, or the spec marks them as convention.
