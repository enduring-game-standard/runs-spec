# RUNS: Record Update Network System

🏠 **[DGS Overview](https://github.com/decentralized-game-standard)**
· 📦 **[AEMS](https://github.com/decentralized-game-standard/aems-standard)**
· ⚡ **[WOCS](https://github.com/decentralized-game-standard/wocs-standard)**
· 🎭 **[MAPS](https://github.com/decentralized-game-standard/ludic-notation-standard)**
· ❓ **[FAQ](https://github.com/decentralized-game-standard/.github/blob/main/profile/FAQ.md)**

> **Status**: Draft / RFC
> **Version**: 0.1.0

In 1956, a trucker named Malcom McLean loaded fifty-eight aluminum containers onto a converted oil tanker in Newark, New Jersey. Before that day, loading a ship took a week. Longshoremen carried each crate by hand. Every piece of cargo was a different shape, handled by different procedures, loaded by different equipment. After containers, loading took hours. Any crane could lift the box. Any ship could carry it. Any truck could haul it. The contents varied wildly — furniture, grain, electronics — but the interface was uniform. Containerization did not make shipping faster because the ships got bigger. It made shipping faster because the *shape became standard*, and everything built around that shape became interchangeable.

Game engines today are pre-container cargo ships. Physics, rendering, input, audio, networking, and AI are packed into a single monolithic hull by hand. Each engine loads its cargo differently. Swap the physics? Rewrite the coupling to rendering. Swap the renderer? Rewrite the coupling to input. When the engine company moves on, the entire ship sinks, cargo and all. Every mod is restricted to hooks the engine explicitly exposes. Every game is fused to the lifespan of its engine.

RUNS standardizes the container.

## The Model

RUNS has five concepts. Each one earns its existence by doing exactly one thing.

**Records** are the containers. Generic data holders with IDs and typed Fields. A Record might hold a character's position, a projectile's velocity, a door's lock state. The Record does not know what uses it. It holds data in a standard shape that any Processor can read.

**Fields** are the contents inside the container. Typed values: a float for position_x, an integer for health, a boolean for is_locked. Fields can be ultra-granular primitives or bundled composites. The level of granularity is a design choice, not a protocol constraint.

**Processors** are the cranes and trucks. Stateless transformations that read Fields, operate on them, and write results to Fields. A physics Processor reads position and velocity, applies forces, writes new position and velocity. A render Processor reads position and sprite data, draws pixels. The Processors share nothing with each other except the Records they read from and write to. Any Processor that reads the correct Field names and types can plug into any system that writes them.

**Networks** are the shipping routes. Explicit wiring that connects Processors into data-flow chains. Input Processor → Intent Fields → Movement Processor → Transform Fields → Render Processor → Screen. The wiring is declared, not implicit. You can read a Network and trace exactly where every piece of data flows.

**Runtimes** are the ports. They load Networks, schedule Processors, and handle the boundary between the data-flow graph and the outside world (screens, speakers, input devices, clocks). Different runtimes serve different purposes: a minimal web interpreter for prototyping, a high-performance native build for shipping, a headless server for multiplayer. All of them run the same Networks.

```
[Input Events] → (Input Processor) → [Intent Fields] → (Movement Processor) → [Transform Fields] → (Render Processor) → Screen
```

Swap the Movement Processor for a full physics bundle. The chain stays intact because the data shape between nodes hasn't changed. The container fits the crane.

## What This Makes Possible

A modder writes a weather Processor in 2026. It reads `runs:time` and `runs:transform`, writes `weather:precipitation` and `weather:wind_direction`. In 2036, someone wires that Processor into a game that does not yet exist, running on a runtime that has not yet been built, deployed to hardware that has not yet been manufactured. The Processor still works. It reads Fields. It writes Fields. The contract is the data shape, and data shapes have no expiration date.

Mods are Processors. Not sandboxed scripts operating through a restricted API. Full Processors with the same privileges as any factory-shipped component. A modder adds a gravity Processor. A different modder adds a grappling hook Processor. A third modder wires them together in a new Network. The result is a game mechanic that none of them individually authored, assembled from parts that compose because they share a standard data interface.

A designer prototypes a new game by composing high-level bundles: a combat system from one community, a map system from another, an inventory system from a third. Each bundle is a Network of Processors published as a plain-text Nostr event. The designer wires the bundles together, and the prototype is playable within hours. When the game matures, the same Networks flatten to optimized platform-specific binaries. The prototype and the production build share the same graph. No rewrite.

## Namespace Conventions

Field and Processor keys use namespaced strings (`prefix:name`) to prevent collisions in a fully decentralized ecosystem.

The `runs:` prefix is reserved exclusively for the RUNS Protocol and Standard Library. Runtimes claiming RUNS compliance must implement standard `runs:` schemas with exact keys, field names, types, and semantics. Core `runs:` schemas are pinned to this specification and the [Standard Library](https://github.com/decentralized-game-standard/runs-standard-library). Additions require RFC and overwhelming justification for universality.

Third-party bundles use their own short, human-readable prefixes as reusable brands (e.g., `pong:`, `hades:`, `zelda-oot:`). Bundles are published as plain-text Nostr events with a manifest:

```json
{
  "umbrella": "pong:",
  "version": "1.4.3",
  "note_id": "note1xyz...abc",
  "previous_note_id": "note1def...456",
  "author_npub": "npub1...",
  "components": ["health", "velocity"],
  "dependencies": {}
}
```

Data uses clean keys: `{ "pong:health": 100 }`. Tooling resolves prefixes via manifests, detects conflicts, and enables aliasing. Bundles chain provenance via dependencies and note IDs, producing self-describing artifacts from high-level systems down to granular primitives.

## Architecture

The protocol is the eternal kernel: unbreakable rules ensuring interoperability and decentralization. No default renderer, physics, or input model. No scripting language. No object hierarchy. No network transport. Networks are the composition mechanism.

The [Standard Library](https://github.com/decentralized-game-standard/runs-standard-library) is the shared palette: curated, optional schemas (e.g., `runs:transform`, `runs:time`, `runs:input`) for instant interoperability across the ecosystem.

The ecosystem is where flexibility flourishes: community bundles targeting protocol shapes, distributed as Nostr events, coordinated and funded through WOCS.

## Integration

| Standard | Role | Relationship |
|----------|------|-------------|
| AEMS | Persistent entities | Entities import as Records; Manifestations configure Processors |
| MAPS | Rule descriptions | Scores implemented as Processor Networks |
| WOCS | Coordination and funding | Funds Processor development, relay hosting, bundle curation |

## Status

RUNS is a draft specification. No production runtimes exist. The protocol defines the minimal kernel for composable game execution. Everything above the kernel — specific renderers, physics systems, input models, and game logic — lives in Processors and Networks built by whoever finds them useful.

**MIT License** — Open for implementation, extension, critique.