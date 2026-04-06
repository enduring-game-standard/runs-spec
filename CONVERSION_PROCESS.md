# RUNS Conversion Process

*How to convert a game from original source to RUNS format.*

---

## Overview

Converting a game to RUNS is a seven-step process. Each step has defined inputs, outputs, acceptance criteria, and known failure modes derived from the Spacewar! 3.1 conversion — the first game converted to RUNS format.

The steps are strictly ordered. Each step's inputs are produced by prior steps. Work can pause at any step boundary and be resumed by a different person or agent without loss of context, because every step produces durable artifacts.

---

## Step 1: Source Acquisition and Deep Reading

### Definition

Obtain the canonical source code and read every line. Not skim — read. Produce a machine-parsed concordance that maps every line of original source to a functional description.

### Inputs

- A game whose source code exists in some form

### Outputs

1. **Canonical source archive** — the definitive version of the source, committed to the repository. If multiple versions exist, the choice of version is documented with reasoning.
2. **Source concordance** — a line-by-line (or routine-by-routine) mapping from original source to functional descriptions. Every line must be accounted for. Format: `line range → function name → what it does → which RUNS phase will consume it`.
3. **Edge case inventory** — a list of every non-obvious behavior discovered through source reading, gameplay observation, and external research (designer interviews, academic papers, community wikis). Each entry: `behavior → source evidence → why it matters`.

### How To Do It

- Write a parser for any structured data in the source (lookup tables, constant blocks, data arrays). Do not count by hand. Trust the parser.
- Play the game extensively on original hardware or accurate emulators. Observe behaviors the code doesn't explain.
- Read all available external documentation: designer notes, interviews, academic papers, community analyses.
- For each magic number, determine its derivation. Is `077777` a bitmask? A maximum value? A sentinel? Document it.

### Acceptance Criteria

- Every line of the original source appears in the concordance exactly once
- No magic number remains unexplained
- The edge case inventory contains at least one entry that was NOT obvious from reading the code alone (found through gameplay or external research)

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| Incomplete reading | Missing Processors in later steps | The concordance enforces completeness — every line must be assigned |
| Manual data counts | Wrong numbers propagate (Spacewar: bible said 478 stars, parser found 469) | Parse mechanically. Always. |
| Missing edge cases | Bugs discovered only at runtime | Play the game. Read external docs. Ask "what happens when X overflows?" |

### Evidence from Spacewar

The source concordance (`01_source_concordance.md`) mapped all 1,870 PDP-1 assembly lines. The edge case inventory discovered count-around prevention, collision diamond geometry, hyperspace risk escalation, negative-zero sentinel values, and fuel counting direction — none obvious from casual reading.

---

## Step 2: Entity Identification and Boundary Drawing

### Definition

Determine what the game's entities are using the AEMS four-test rubric. Draw the boundary between game logic (RUNS), entity identity (AEMS), and platform services (runtime). Write the runtime contract.

### Inputs

- Source concordance
- Edge case inventory

### Outputs

1. **AEMS layer document** — every candidate entity evaluated against the four-test rubric. Each candidate is either accepted (with Entity/Manifestation classification) or rejected (with reasoning). Exclusion decisions are as important as inclusion decisions.
2. **Runtime contract** — a formal statement of the boundary: what the game logic provides (state updates, render objects, audio triggers) and what the runtime provides (timing, input, display, sound). This is the API between the two sides.
3. **Inbound/outbound field inventory** — the exact Fields that cross the boundary in each direction.

### How To Do It

- For every noun in the game (ship, torpedo, star, explosion, score, timer), run the AEMS four-test rubric.
- For each candidate that passes: classify as Entity or Manifestation.
- For each candidate that fails: document WHY it was excluded.
- Write the runtime contract BEFORE defining Records. The contract determines the shape of everything downstream.

### Acceptance Criteria

- Every game noun has been evaluated against the four-test rubric
- At least one candidate has been excluded with documented reasoning
- The runtime contract specifies inbound and outbound Fields with types
- The AEMS/RUNS boundary rule ("changes gameplay = RUNS, changes appearance = AEMS") has been applied to every ambiguous case

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| Entity over-identification | Too many entities, tangled Records, bloated AEMS layer | The four-test rubric. If it fails any test, it's not an entity. |
| Missing the runtime boundary | Game logic contains rendering code, or runtime makes gameplay decisions | Write the contract first. If changing a value changes how the game plays, it's RUNS. |
| Runtime contract as afterthought | Discovered ad hoc during Processor writing | Write it before Records. The Spacewar postmortem explicitly recommends this. |

### Evidence from Spacewar

AEMS analysis produced 3 Entities and 4 Manifestations — far fewer than expected. Key exclusions: explosions (state transitions, not entities), the central star (environmental constant, not entity), the star catalog (cosmetic backdrop, not AEMS). The runtime contract defined 4 inbound and 3 outbound Record boundaries.

---

## Step 3: Type System and Record Definitions

### Definition

Define every piece of game state as typed Fields in named Records. Define game-specific types. Extract and document every constant.

### Inputs

- Source concordance
- AEMS layer document
- Runtime contract

### Outputs

1. **Type definitions** — any game-specific types (e.g., `spacewar:fixed18` with ones-complement rules, binary-point conventions, and negative-zero semantics).
2. **Record schemas** — every Record with every Field, typed and documented. Each Field traces back to the source concordance.
3. **Constants** — every magic number extracted, named, typed, and documented with its derivation from the source. Not just the value — the WHY.

### How To Do It

- Start with the entity table: what Fields does each entity carry? These become Record schemas.
- Identify shared Fields (position, velocity, state) vs. entity-specific Fields (fuel, reload timer).
- For every constant, trace its derivation: `tno = law i 16` → runtime value is `-16` (ones-complement) → 16 torpedoes per ship → used as countdown initial.
- If the original source uses a custom numeric representation, define it formally: bit width, signed/unsigned, complement system, binary-point conventions per context.

### Acceptance Criteria

- Every piece of mutable game state is captured in a Record Field
- Every constant has a documented derivation
- Game-specific types include all representation rules (overflow, rounding, complement)
- No Field is untyped

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| Wrong numeric type | Math bugs in Processors (the sqrt scaling disaster) | Document binary-point conventions per context, not just per type |
| Missing Fields | Processors need state that wasn't defined | Cross-reference against source concordance — every source variable must map to a Field |
| Under-specified types | Runtime implementations disagree on overflow behavior | Define every edge: what happens at max value? At zero? At negative zero? |

### Evidence from Spacewar

Defined 12 Records, the `spacewar:fixed18` custom type with 7 operation rules and 8 binary-point context conventions, and 17 named constants with full derivations.

---

## Step 4: Processor Extraction

### Definition

Identify every discrete operation in the original source. Define each as a Processor with typed inputs, outputs, and execution guards. Wire them into a Network with specified execution order.

### Inputs

- Record schemas
- Source concordance
- Edge case inventory

### Outputs

1. **Processor signatures** — for each Processor: name, inputs (which Fields it reads), outputs (which Fields it writes), guards (under what entity state it executes).
2. **Network topology** — the execution order of all Processors within a game tick, including guarded dispatch blocks and entity iteration order. The Network must follow the formal grammar defined in the [Network Topology](./NETWORK_TOPOLOGY.md) specification: phases, dispatch with guard arcs, sub-Network bundling, and the concurrency semantics derived from Record sharing.
3. **Data flow graph** — the graph of data dependencies between Processors, mediated by Records. Every edge in this graph must pass through a Record Field: Processor A writes Field X on Record R, Processor B reads Field X from Record R. Direct Processor-to-Processor data flow is a **Petri net violation** — Processors are transitions and Records are places; tokens never move transition-to-transition.

### How To Do It

- Walk the original source's main loop. Each distinct operation (update position, check collision, fire torpedo) becomes a Processor.
- For each Processor, examine which variables it reads → those are input Fields. Which it writes → output Fields.
- Determine the guard condition: does this Processor run for all entities, or only ships? Only torpedoes? Only entities in a specific state?
- Determine execution order: does Processor A's output feed Processor B's input within the same tick? Then A must run before B.
- Document entity iteration order if it matters (it usually does).

### Acceptance Criteria

- Every source routine maps to exactly one Processor (or is explicitly documented as excluded)
- Every Processor's inputs are Fields defined in Step 3
- Every Processor's outputs are Fields defined in Step 3
- The Network execution order is specified, not left to the runtime
- Entity iteration order is documented

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| Fused Processors | One Processor does too many things | If a Processor reads and writes unrelated Fields, split it |
| Missing guard conditions | Processor runs on wrong entity types | Trace the original source's conditional dispatch exactly |
| Wrong execution order | Stale reads (gravity reads position before movement updates it) | Build the data flow graph. Every read-before-write dependency must be respected. |
| Unspecified iteration order | Non-deterministic behavior across runtimes | The Spacewar postmortem: "slot-order determinism is more important than it looks" |
| Phantom fields | Processors appear to work but pass data through undeclared outputs that bypass Records | Build the data flow graph with Record edges. If a Processor output does not update a defined Record Field, it is phantom data — it cannot be serialized, inspected, or decoupled. The Spacewar postmortem: processor-to-processor pipelines were the #1 systemic failure. |

### Evidence from Spacewar

Extracted 24 Processors (6 math, 11 entity, 7 system). Network topology: 8 ordered phases with guarded dispatch. Entity iteration: slots 0–23, strictly ordered.

---

## Step 5: Processor Body Implementation

### Definition

Write the algorithm for each Processor in DIGS. Create test vectors alongside each body — not after.

### Inputs

- Processor signatures
- Source concordance
- Edge case inventory
- Record schemas with type definitions

### Outputs

1. **Processor bodies** — the complete algorithm for each Processor, expressed in DIGS (`.runs-prim` files). Every source line consumed by this Processor (per the concordance) must be represented.
2. **Test vectors** — for every Processor that performs computation: a set of `{inputs → expected_outputs}` pairs derived from the original source's known behavior.

### How To Do It

- Translate each algorithm **literally**. Do not improve. Do not optimize. Do not reinterpret. If the source says `if angle > pi: angle -= pi`, write exactly that. Do not "improve" it to `while angle > pi: angle -= 2*pi`. Fidelity is correctness.
- For each Processor body, simultaneously create test vectors from: (a) hand-traced examples from the original source, (b) known behaviors from gameplay observation, (c) boundary values for the type system.
- Cross-reference each body against the source concordance. Every line assigned to this Processor must be accounted for in the body.

### Acceptance Criteria

- Every Processor has a complete body in DIGS
- Every math Processor has test vectors with at least: zero input, maximum input, minimum input, one "normal" input, and one boundary case
- Every source line in the concordance is consumed by exactly one Processor body
- No Processor body contains logic that was "improved" relative to the original — deviations are documented as intentional with reasoning

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| "Improving" the original algorithm | Runtime behavior diverges from the original game | Translate literally. The runtime postmortem: "the temptation to improve things introduced every bug." |
| Missing test vectors | Bugs discovered only at runtime, not during implementation | Create vectors alongside bodies. If you can't write a test vector, you don't understand the algorithm. |
| Wrong binary-point convention | Math produces plausible but incorrect results (the sqrt scaling bug) | Test vectors catch this — `sqrt(2048)` must produce `23168`, not `45` |

### Evidence from Spacewar

24 Processor bodies written. The PICO-8 runtime revealed 4 bugs — all translation errors where the implementer deviated from the source rather than translating literally.

---

## Step 6: Source Verification

### Definition

Verify the complete RUNS source against the original game's behavior. Check structural completeness, logical consistency, and behavioral correctness.

### Inputs

- Complete RUNS source (Records, Processors, Networks)
- Test vectors
- Source concordance

### Outputs

1. **Verification report** — results of all checks: concordance completeness, Network coverage, test vector results, known deviations.
2. **Confidence assessment** — honest statement of what has been verified and what hasn't.

### How To Do It

- Check concordance completeness mechanically: every source line assigned to exactly one Processor body or explicitly excluded.
- Check Network coverage: for every entity state declared in the Record schemas, verify at least one Processor's guard matches.
- Run test vectors through the reference evaluator if one exists. If not, hand-trace critical math Processors.
- Compare against original hardware emulation if available.
- Check Record-mediation completeness: for every Processor I/O declaration, verify the Field exists on a defined Record. For every Processor output, verify it writes through a Record (e.g., `output object = object with { field = value }`), not as a phantom output (`output phantom_name = value` where `phantom_name` is not a Record Field).
- Document what CANNOT be verified without a runtime.

### Acceptance Criteria

- 100% concordance coverage (every source line accounted for)
- Network guard coverage ≥ 100% (every entity state handled)
- All test vectors pass
- Known deviations list is complete

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| False confidence from static checks | Source looks complete but has execution bugs | Be honest about what static checks can and cannot prove. |
| Missing Network paths | Entity gets stuck in a state with no handler | Enumerate all states × all guard conditions. |

### Evidence from Spacewar

Verification confirmed 100% concordance coverage and 6 intentional deviations. Static verification was necessary but not sufficient — the runtime revealed 4 additional bugs.

---

## Step 7: Runtime Implementation and Validation

### Definition

Build a runtime that compiles or interprets the RUNS source for a specific platform. Play the game. Compare against original behavior. Write the postmortem.

### Inputs

- Verified RUNS source
- Test vectors
- A target platform

### Outputs

1. **Playable game** on at least one platform
2. **Deviation manifest** — every departure from strict DIGS evaluation, documented with reasoning
3. **Runtime postmortem** — what the runtime revealed about the source, the spec, and the conversion process

### How To Do It

- Choose the simplest viable target platform. Simpler is better.
- Compile RUNS source to platform code. Document every substitution or adaptation.
- Run test vectors on the compiled code first. Fix math before playing.
- Play the game. Compare against original behavior.
- Write the postmortem.

### Acceptance Criteria

- The game runs and is playable
- All test vectors pass on the compiled code
- Every deviation from strict evaluation is documented
- The postmortem is written (not deferred)

### Known Failure Modes

| Failure | How it manifests | Prevention |
|---------|-----------------|------------|
| Translation errors | Gameplay defects (wrong gravity, garbled outlines) | Run test vectors FIRST |
| "Improving" during translation | Bugs from reinterpretation | Translate literally |
| Platform numeric limitations | Data values exceed target integer range | Check type ranges; pre-compute data tables if needed |
| Skipping the postmortem | Lessons lost | The postmortem is a deliverable, not optional |

### Evidence from Spacewar

PICO-8 runtime: 820 lines of Lua. 4 bugs found and fixed — all translation errors. The game played correctly after fixes. The runtime forced the DIGS specification into existence.
