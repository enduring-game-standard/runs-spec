---
status: accepted
date: 2026-11-22
---

# The split between game logic and presentation is a convention, not protocol

The protocol is valid RUNS: Records, Processors, the Network, and DIGS. It hardens now and stays still. The conventions are standard RUNS: how compliant a program is, and what that unlocks (shared Records and Processors, side-by-side comparison, Ports, the check that the game logic run alone matches the original). The split between game logic and presentation belongs to the conventions, because where the line falls is a judgment a later editor may revise. A protocol holds rules that stay still, and a judgment open to revision cannot be one. Bitcoin draws the same line between consensus rules (what is valid) and standardness policy (what nodes relay).

## Considered options

- **Split in the protocol**: every valid program declares its game logic and its presentation. Rejected. Every step of a conversion before full separation would be invalid RUNS, so the protocol would forbid the route to its own goal. It also hardens today's two-region model against games that need another shape.

## Consequences

- A program that rewrites an original line for line into Records, Processors, and Networks, with no split, is valid RUNS and not yet standard.
- Port and Variant are defined against the conventions, not the protocol.
- Kinds are a typesafe convention. From the Separated stage on, every Record and Processor declares Game Logic, Interface, or Presentation, and a check confirms they agree. The protocol ignores Kinds, so a program before the split declares none.
