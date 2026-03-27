# T1: Capability Manifest Format

Machine-readable declaration of what a game requires and what a platform provides.

**Depends on**: At least two games and two runtimes to validate the vocabulary.

## Required Dimensions

- `display`: resolution, color depth
- `input`: player count, buttons/axes per player
- `audio`: channel count (or `none`)
- `spatial_logic`: `0d`, `1d`, `2d`, `3d` — the mechanical dimensionality of the game logic
- `compute`: max entity count, Processors per tick

## Design Principle

The manifest answers "can this platform run this game?" — not "what kind of platform is this?" Capability-based, not identity-based. Follows the WASI model.
