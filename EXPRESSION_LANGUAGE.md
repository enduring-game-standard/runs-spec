# RUNS Expression Language
 
> **Status**: Open Design Question / Draft  
> **Version**: 0.0.1

## Purpose

RUNS Processor bodies are currently written in a `.runs-prim` notation — a draft sketch of a formal expression language. This document captures the requirements and design constraints for that language as currently understood.

The expression language is the enduring artifact in the RUNS compilation model. Runtimes compile it into platform-specific execution. The language must be readable, parseable, and compilable by any future runtime without dependence on any existing programming language.

## Design Constraints

The language must be:

1. **Pure** — No side effects beyond declared outputs. A Processor's outputs depend only on its declared inputs.
2. **Total** — All programs terminate. No unbounded loops. No general recursion. Programs that can run forever are excluded by construction.
3. **Deterministic** — Same inputs always produce the same outputs, on every platform, forever. No floating-point ambiguity where determinism is required (fixed-point types provide bit-exact results).
4. **Language-agnostic** — Not tied to any existing programming language's syntax or semantics. Readable by a human who has never programmed.
5. **Formally specified** — A grammar and evaluation semantics precise enough that two independent implementations produce identical results for all valid programs.

## Required Expressiveness

The language must express:

| Capability | Example | Why Needed |
|---|---|---|
| Integer arithmetic | `health - damage` | Combat, scoring, counters |
| Fixed-point arithmetic | `fixed16_mul(momx, friction)` | Deterministic physics (DOOM, Build engine, retro ports) |
| Floating-point arithmetic | `position + velocity * dt` | Modern physics where determinism is not required |
| Boolean logic and comparisons | `if health <= 0` | Conditionals in every game |
| Bitwise operations | `flags & MF_SHOOTABLE` | Flag fields (common in game state) |
| Conditionals | `if/else`, pattern matching | Branching logic |
| Record field access | `target.health`, `mobj.info.painchance` | Reading entity state |
| Record construction | `target with { health = new_health }` | Producing modified state without mutation |
| Bounded iteration | `for each mobj in world.mobjs` | Processing entity lists per tick |
| Processor composition | `result = doom:xy_movement(mobj, world)` | Calling sub-Processors |
| Typed inputs/outputs | `inputs: target: doom:mobj` | Interface declarations |
| Enumerated types | `state_action == "chase"` | State machines, dispatch |
| Nullable/optional types | `inflictor: doom:mobj?` | Entities that may or may not exist |
| Collection output | `spawn_requests: doom:spawn_request[]` | Processors that produce lists of side-effect descriptors |

## Deliberate Exclusions

The language must NOT express:

- **Unbounded loops or general recursion** — Programs always terminate.
- **I/O of any kind** — No rendering, sound, file access, networking. All I/O is the runtime's job.
- **Memory allocation or pointer arithmetic** — No manual memory management.
- **Global mutable state** — All state flows through declared inputs and outputs.
- **Platform-specific primitives** — No OS calls, no hardware intrinsics.
- **String manipulation beyond identifiers** — Not a general-purpose text processing language.

## Precedents

| System | What it is | What RUNS can learn |
|---|---|---|
| GLSL/HLSL | GPU shader languages | Pure, restricted, deterministic, compiled by platform-specific drivers |
| SQL | Database query language | Declarative, platform-independent, compiled by platform-specific engines |
| SPIR-V | Platform-independent shader IR | Formal spec enabling multiple backend compilers from one source |
| Dhall | Configuration language | Pure, total, deterministic, with imports and composition |
| MIDI | Musical event protocol | Specifies intent (notes), not realization (synthesis) |

## Relationship to Runtimes

```
  .runs-prim source          Runtime compiler           Platform execution
  (formal language)    →     (Tier 2)             →     (native code)
  
  The enduring artifact      Platform-specific          Replaceable,
  Human-readable             Optimization strategies    competitive
  Formally specified         SIMD, GPU offload          Performance varies
  Deterministic              Cache-friendly layouts     Behavior identical
```

The language specifies WHAT the computation does. The runtime decides HOW to execute it efficiently. Two runtimes compiling the same `.runs-prim` source must produce identical game behavior.

## Open Questions

1. **Syntax design** — What should the concrete syntax look like? The current `.runs-prim` examples use an imperative-looking style (`position.x = ...`). Should it stay imperative-looking for accessibility, or adopt a more explicitly functional style (`let new_position = ...`)? Accessibility to non-programmers is a design goal.

2. **Iteration semantics** — How does bounded iteration over Record collections interact with mid-iteration modification (e.g., DOOM's thinker list where entities can be marked for removal during iteration)? Current answer: explicit `pending_remove` flags with early-return checks, matching vanilla DOOM's lazy-deferred removal pattern.

3. **Error handling** — What happens when a Processor receives invalid input (division by zero, null dereference on a non-optional field)? Does the language enforce correctness at the type level, or provide explicit error paths?

4. **Versioning** — How does the language evolve without breaking existing source? Additive-only changes? Explicit version declarations in source files?

5. **Tooling bootstrap** — What is the minimal tooling needed for the first runtime to parse and execute `.runs-prim` source? A reference parser? A formal grammar?

---

*This document is a living draft. It captures the current understanding of what the expression language needs to be, not a finished specification.*

**MIT License** — Open for discussion, critique, and contribution.
