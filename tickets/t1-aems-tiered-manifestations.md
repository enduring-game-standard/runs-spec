# T1: AEMS Tiered Manifestation System

Guidance and schema for multi-fidelity visual representations of entities, authored bottom-up (tier 1 first).

**Depends on**: AEMS spec, at least one game with visual assets.

## The Principle

Every Manifestation MUST include a tier 1 representation: a visual form simple enough for a 128×128, 16-color display. This is the canonical visual identity, not a fallback. Higher tiers are enhancements layered on top.

```
Tier 1: foundation (pixel art, wireframe, colored rectangle)
Tier 2: enhancement (sprites with animation, low-poly)
Tier 3: enhancement (full 3D, PBR materials)
```

## Why Bottom-Up

The "de-make problem" (how to turn 3D models into pixel art) dissolves when authoring starts at the bottom. Tier 1 is authored first. Higher tiers are additive, like flying buttresses on a chapel. Inspired by the progressive enhancement revolution in web design (mobile-first CSS).

## Precedent

Spacewar already works this way: the ship's visual identity is 7 direction codes tracing a wireframe. That IS the ship. Any runtime can interpret those codes at its native fidelity.
