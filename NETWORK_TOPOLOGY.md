# RUNS Network Topology

> **Status**: Draft Specification
> **Version**: 1.0.0-draft.1
> **File extension**: `.runs`

## Purpose

This specification defines the Network topology: the wiring syntax that connects Records to Processors and governs the execution order of a game tick. It is the composition layer of the RUNS protocol — the mechanism by which pure, stateless Processors are organized into deterministic, bounded, inspectable game logic.

A Network is a bipartite directed graph where Records and Processors are two disjoint node types. Every arc connects a Record to a Processor or a Processor to a Record. An arc never connects two Records or two Processors directly. This bipartite structure is not a convention — it is a mandatory invariant. Violation makes a Network non-compliant.

Processors define computation (specified in [DIGS](./DIGS_EXPRESSION_LANGUAGE.md)). Records define state. Networks define the wiring between them — what fires when, in what order, over which entities, under what conditions. The Network is the composition layer where game architecture becomes explicit, inspectable, and composable.

Networks are declared in `.runs` files alongside Record schemas and enum definitions. The `network` keyword introduces a Network declaration; the `record` keyword introduces a Record schema. Both share the `.runs` extension because both describe structure, not computation. Processor bodies (computation) use the `.runs-prim` extension and the DIGS syntax.

Every decision in this specification is driven by one question: *can a solo developer in a century implement this from scratch, with nothing but this document?*

---

## Design Constraints

The Network topology is:

1. **Bipartite** — Every arc connects a Record to a Processor or a Processor to a Record. No Processor reads directly from another Processor's output without an intermediate Record. No Record writes directly to another Record. All data flow is mediated by the bipartite structure.
2. **Deterministic** — The same Network with the same input Records produces the same output Records, in the same execution order, on every platform, forever. There is no nondeterminism in firing order, entity iteration, or guard evaluation.
3. **Bounded** — All iteration is over finite, declared collections. Every tick terminates in finite time and bounded memory. The compiler can prove this statically from the Network source alone, without executing the program.
4. **Static** — The Network topology is fixed at compile time. No Processors are added or removed at runtime. No arcs are rewired during execution. Variation at runtime is expressed through guard conditions on static arcs, not through topology modification.
5. **Concurrent** — Processors that share no Records are independent. The Network topology defines the causal dependencies between Processors through their shared Record access. A compliant runtime must produce results equivalent to any valid execution order of independent Processors — which includes simultaneous execution.

---

## Network Declaration

### Top-Level Network

A top-level Network declares the complete game tick. It is the entry point called by the runtime each frame.

```
network spacewar:game_tick

  requires:
    tick:         spacewar:tick_input
    controls_1:   spacewar:player_controls

  produces:
    render_list:  spacewar:render_object[]
    match:        spacewar:match_result

  state:
    objects:      spacewar:object[24]
    prng:         spacewar:prng_state
    star_catalog: spacewar:star_catalog

  phases:
    # ... (phase declarations)
```

A top-level Network has four blocks:

| Block | Required | Contents | Persists Between Ticks |
|-------|----------|----------|----------------------|
| `requires:` | Yes | Inbound boundary Records — provided by the runtime each tick | No (fresh each tick) |
| `produces:` | Yes | Outbound boundary Records — read by the runtime after each tick | No (snapshot) |
| `state:` | No | Internal persistent Records — carried between ticks | Yes |
| `phases:` | Yes | Ordered execution stages | N/A |

A Record appearing in `state:` may also appear in `produces:` — the runtime reads it after each tick, but the game logic owns and persists it.

### Sub-Network

A sub-Network is a reusable composition unit invoked from within a dispatch phase or another phase. It declares explicit inputs and outputs rather than boundary blocks:

```
network spacewar:ship_update
  inputs:
    object:     spacewar:object
    controls:   spacewar:player_controls
    config:     spacewar:game_config
    consts:     spacewar:game_constants
    prng:       spacewar:prng_state
  outputs:
    object:       spacewar:object
    prng:         spacewar:prng_state
    spawn_request: spacewar:spawn_request

  phases:
    - processor: spacewar:rotation_update(object, controls, config, consts)
    - processor: spacewar:gravity(object, config, consts)
    - processor: spacewar:thrust(object, consts)
    - processor: spacewar:wrap_position(object.position_x, object.position_y)
    - processor: spacewar:torpedo_launch(object, controls, config, consts)
    - processor: spacewar:hyperspace_check(object, controls, consts)
```

Sub-Networks are Processors from the outside — they have typed inputs and outputs at their interface boundary. Inside, they contain phases that wire Records to Processors. This is the bundling mechanism for hierarchical composition: a sub-Network used in a dispatch arc is indistinguishable from a Processor at the call site.

### Record Declarations

Record references in `requires:`, `produces:`, `state:`, `inputs:`, and `outputs:` blocks follow the same format:

```
name: qualified_type
name: qualified_type[count]
name: qualified_type[max: count]
name: qualified_type[]
```

| Notation | Meaning |
|----------|---------|
| `type` | Single instance |
| `type[N]` | Fixed collection of exactly N instances |
| `type[max: N]` | Bounded collection of at most N instances |
| `type[]` | Variable-length list (bounded by the Record schema's declaration) |

The count in `[N]` or `[max: N]` must be a positive integer literal. This count is known at compile time and is the mechanism by which the compiler proves dispatch termination.

### Data Source Declaration

A Record in the `state:` block may declare a build-time data source:

```
state:
  star_catalog:  spacewar:star_catalog
    source: aems:manifestation/expensive_planetarium

  sectors:       doom:sector[max: 512]
    source: doom:wad/SECTORS
```

The `source:` annotation tells the build tool where to find the data that populates this Record's initial state. The source identifier is a qualified reference to a data artifact — an AEMS Manifestation event, a game-specific data file (WAD lump, ROM segment), or an embedded literal.

The `source:` annotation is declarative metadata. It does not affect the Network's runtime semantics. The build tool resolves sources and populates Records before the first tick. At runtime, the Record is already populated.

The format of the source data — how binary bytes map to Record fields — is defined by a companion format specification artifact, not by this document. See §Relationship to Other EGS Components.

---

## Phases

A tick is an ordered sequence of phases. Phases execute in declaration order. Each phase is one of five types:

| Phase Type | Keyword | Purpose |
|-----------|---------|---------|
| Processor | `processor:` | Unconditional invocation of a single Processor |
| Network | `network:` | Unconditional invocation of a sub-Network |
| Dispatch | `dispatch:` | Bounded iteration over an entity collection with guarded routing |
| Iterate | `iterate:` | Bounded repetition of a phase body |

### Processor Phase

Invokes a single Processor unconditionally:

```
- processor: spacewar:collision_detect(objects, consts)
```

The Processor receives the named Records as arguments. Argument order matches the Processor's declared `inputs:` order. The Processor's outputs overwrite the corresponding Record fields in the enclosing scope.

### Network Phase

Invokes a sub-Network unconditionally:

```
- network: spacewar:ship_update(object, controls, config, consts, prng)
```

Semantically identical to a Processor phase — the sub-Network's `inputs:` receive the named Records, and its `outputs:` overwrite the corresponding Records in the enclosing scope.

### Dispatch Phase

Iterates over a bounded Record collection, firing guarded arcs for each entity:

```
- dispatch: objects
    order: slot
    arcs:
      - guard: .state == ship and slot == 0
        network: spacewar:ship_update(., controls_1, config, consts, prng)

      - guard: .state == torpedo
        processor: spacewar:torpedo_update(., consts)

      - guard: .state == empty
        skip: true
```

Components of a dispatch phase:

#### Collection Reference

`dispatch: objects` names a Record collection from the enclosing scope (`state:`, `requires:`, or sub-Network `inputs:`). The collection must have a declared count (`[N]` or `[max: N]`).

#### Ordering

`order: slot` specifies the deterministic iteration order:

| Ordering | Meaning |
|----------|---------|
| `slot` | Iterate by index: 0, 1, 2, ..., N−1 |
| `insertion` | Iterate in the order entities were added to the collection |

Custom orderings may be defined by referencing a sort key field:

```
order: .priority descending
```

The ordering must be total and deterministic — every entity has a unique position in the iteration sequence. The compiler verifies this.

#### Current Entity

Within a dispatch phase, `.` (dot) refers to the current entity being dispatched. `.state`, `.position_x`, etc. access fields on the current entity. This notation is valid only inside dispatch arcs.

The `slot` variable is implicitly available and holds the current entity's index in the collection (0-indexed).

#### Guard Arcs

Each arc in the `arcs:` block is a conditional route:

```
- guard: .state == torpedo
  processor: spacewar:torpedo_update(., consts)
```

The `guard:` expression is a DIGS boolean expression evaluated against the current entity's fields. If the guard evaluates to `true`, the arc fires — invoking the named Processor or sub-Network. If `false`, the arc is skipped and the next arc is evaluated.

**Mutual exclusivity:** For a given entity, at most one arc fires per dispatch. The compiler should warn (and may error) if guards are not mutually exclusive for all possible entity states. Overlapping guards produce undefined execution — different runtimes could fire different arcs.

**Completeness:** Every possible entity state must be handled by at least one arc. The compiler must verify that no entity state falls through all guards unhandled. The `skip: true` directive is the explicit "do nothing" handler for states that require no processing:

```
- guard: .state == empty
  skip: true
```

**Argument passing:** Arc targets receive arguments in parentheses. The `.` argument passes the current entity. Other arguments are Records from the enclosing scope. The compiler verifies that argument types match the target's declared inputs.

**Secondary collection access:** An arc target may receive the full dispatch collection as a read-only secondary input, in addition to the current entity:

```
- guard: .needs_perception
  processor: tlou:perception_scan(., all_agents, cover_graph)
```

This enables cross-entity queries (collision detection, perception, spatial lookups) where a Processor operating on one entity needs to read from other entities in the same or different collections.

### Iterate Phase

Bounded repetition of a phase body:

```
- iterate: 8
  phases:
    - dispatch: constraints[max: 512]
        order: slot
        arcs:
          - guard: .active == true
            processor: physics:resolve_constraint(., bodies)
```

The `iterate:` value specifies how many times the enclosed phases execute. The value must be:
- A positive integer literal, or
- A reference to a declared constant field with a known upper bound

The compiler verifies the bound is finite and computes the maximum total Processor firings:

```
total_firings ≤ iterate_count × dispatch_count × arcs_per_entity
```

For the example above: `8 × 512 × 1 = 4,096` maximum firings. Finite, bounded, provable.

Iterate phases exist for algorithms that require multiple passes over the same data per tick — physics constraint solvers, iterative relaxation, multi-pass rendering. The iteration count is a game design fact: more iterations produce more accurate results at higher computational cost. On constrained hardware, a lower count produces less accurate but still functional results.

**What iterate does NOT permit:**

- `iterate: until_converged` — the iteration count must be finite and known at compile time. Convergence-based termination is not expressible. See §Deliberate Exclusions.
- Nesting limit: iterate phases may contain dispatch phases, processor phases, and network phases. An iterate phase may NOT contain another iterate phase. This prevents unbounded nesting and maintains the compiler's ability to compute a static upper bound on total firings.

---

## Concurrency Semantics

The Network topology is a bipartite graph. The graph structure determines which Processors can execute independently.

**Definition:** Two Processors are **independent** if and only if they share no Records — neither reads a Record that the other writes, and neither writes a Record that the other writes.

**Rule:** Independent Processors are concurrent. A compliant runtime must produce results equivalent to any valid execution order of independent Processors, which includes simultaneous execution.

**Consequence:** Phase ordering in the `phases:` block establishes sequencing only where data dependencies exist. Phases that access disjoint Record sets are concurrent by the topology, regardless of their declaration order. The declaration order serves as the canonical sequential interpretation that all valid execution orders must be equivalent to.

**Example from Spacewar:**

```
# These phases access disjoint Record sets:
- processor: spacewar:advance_starfield_scroll(starfield, config)
- processor: spacewar:check_restart(objects, result, consts)
```

`advance_starfield_scroll` reads/writes `starfield` and reads `config`. `check_restart` reads/writes `objects` and `result`, reads `consts`. They share `consts` as a read-only input but neither writes to it. They are independent and may execute concurrently.

```
# These phases share a Record — they must be sequential:
- processor: spacewar:check_restart(objects, result, consts)
- processor: spacewar:update_scores(objects, result)
```

Both read and write `result`. `check_restart` must complete before `update_scores` begins. The declaration order determines which comes first.

**Read-only sharing does not create a dependency.** Two Processors that both read the same Record (without writing it) are independent. Dependencies arise only from write-write or read-write conflicts on the same Record.

**Within a dispatch phase:** Entities dispatched in the same phase are independent if and only if their Processors write only to the current entity's fields (`.`) and to no shared state. If a dispatched Processor writes to a shared Record (e.g., a score counter), entities within that dispatch are NOT independent and must execute in the declared order.

---

## Hierarchical Composition

### Bundling

A sub-Network bundles a sequence of Processors into a reusable unit. From the outside, it behaves exactly like a Processor — typed inputs, typed outputs, invoked from an arc or phase.

From the inside, it contains its own phases. This is the mechanism for hierarchical decomposition:

```
Top-Level Network
  └─ Phase 1: Dispatch entities
       ├─ Arc: ship → Sub-Network: ship_update
       │                └─ Phase: rotation
       │                └─ Phase: gravity
       │                └─ Phase: thrust
       │                └─ Phase: wrap
       │                └─ Phase: torpedo
       │                └─ Phase: hyperspace
       ├─ Arc: torpedo → Processor: torpedo_update
       └─ Arc: explosion → Processor: explosion_tick
  └─ Phase 2: Processor: process_spawns
  └─ Phase 3: Processor: collision_detect
```

There is no limit on nesting depth. A sub-Network may invoke other sub-Networks. The compiler flattens the entire hierarchy into a single execution schedule.

### Hierarchical Data (Depth-Level Dispatch)

Systems with parent-child relationships (skeletal animation, UI trees, scene graphs) use sequential dispatch phases ordered by hierarchy depth:

```
# Propagate transforms top-down through a bone hierarchy
- dispatch: bones[max: 256]
    order: .depth == 0
    arcs:
      - guard: .depth == 0
        processor: animation:root_transform(.)

- dispatch: bones[max: 256]
    order: .depth == 1
    arcs:
      - guard: .depth == 1
        processor: animation:child_transform(., bones[.parent_index])

- dispatch: bones[max: 256]
    order: .depth == 2
    arcs:
      - guard: .depth == 2
        processor: animation:child_transform(., bones[.parent_index])
```

The maximum hierarchy depth must be known at compile time. Each depth level is a separate dispatch phase, ensuring parent transforms are computed before children. This pattern requires no new primitive — it is a composition of dispatch phases with depth-based guards.

For game-specific hierarchies with fixed depth (skeletal rigs: typically ≤30 levels), this scales cleanly. For dynamic hierarchies with unknown depth, the formalism does not apply — see §Deliberate Exclusions.

---

## Variable-Rate Execution

The runtime drives the tick loop. The Network has no concept of "time" — it transforms inputs to outputs. Timing is a runtime concern.

### Sub-Ticking

Some systems require multiple passes at a higher frequency (e.g., physics at 240 Hz while rendering at 60 Hz). This is expressed through inbound boundary Records:

```
requires:
  tick: runs:tick_input
    # Includes:
    #   frame_number: int
    #   delta_time: fixed16
    #   substep_index: int        # 0..substep_count-1
    #   substep_count: int        # e.g. 4
    #   is_substep: bool          # true during physics substeps
```

The runtime calls the Network multiple times per visual frame with different `substep_index` values. Guards in the Network select which phases run during substeps vs. main ticks:

```
phases:
  # Physics runs every substep
  - guard: tick.is_substep == true or tick.substep_index == 0
    processor: physics:integrate(objects, tick)

  # Scoring runs only on the main tick
  - guard: tick.is_substep == false
    processor: gameplay:update_scores(objects, result)
```

This is a library convention using the existing `requires:` mechanism. The spec provides the guarding mechanism; the library standardizes the field names. No additional primitive is required.

### Variable-Rate Entity Dispatch

Entities that update at different rates (e.g., DOOM's state machine where different states have different `tics` durations) are handled through guards:

```
- dispatch: mobjs
    order: slot
    arcs:
      - guard: .tics_remaining == 0
        processor: doom:state_transition(., state_table)
      - guard: .tics_remaining > 0
        processor: doom:decrement_tics(.)
```

The "cooperative multitasking" pattern — where only a fraction of entities perform AI logic each tick — emerges naturally from guard-based dispatch. No special scheduling primitive is needed.

---

## Formal Grammar

The following grammar is in extended Backus-Naur form (EBNF). Terminals are in double quotes. Nonterminals are in lowercase. `{ ... }` means zero or more repetitions. `[ ... ]` means optional.

```ebnf
network_file      = { comment NEWLINE }
                    network_decl ;

network_decl      = "network" qualified_name NEWLINE
                    ( top_level_blocks | sub_network_blocks )
                    phases_block ;

(* Top-level Network: boundary declarations *)
top_level_blocks  = requires_block
                    produces_block
                    [ state_block ] ;

(* Sub-Network: explicit inputs/outputs *)
sub_network_blocks = inputs_block
                     outputs_block ;

requires_block    = INDENT "requires:" NEWLINE
                    { INDENT INDENT record_ref NEWLINE } ;

produces_block    = INDENT "produces:" NEWLINE
                    { INDENT INDENT record_ref NEWLINE } ;

state_block       = INDENT "state:" NEWLINE
                    { INDENT INDENT record_ref [ source_annotation ] NEWLINE } ;

inputs_block      = INDENT "inputs:" NEWLINE
                    { INDENT INDENT record_ref NEWLINE } ;

outputs_block     = INDENT "outputs:" NEWLINE
                    { INDENT INDENT record_ref NEWLINE } ;

record_ref        = identifier ":" qualified_name [ collection_spec ] ;

collection_spec   = "[" integer_literal "]"
                  | "[" "max:" integer_literal "]"
                  | "[" "]" ;

source_annotation = NEWLINE INDENT INDENT INDENT "source:" qualified_ref ;
qualified_ref     = qualified_name { "/" identifier } ;

(* Phase declarations *)
phases_block      = INDENT "phases:" NEWLINE
                    { INDENT INDENT phase } ;

phase             = processor_phase
                  | network_phase
                  | dispatch_phase
                  | iterate_phase
                  | guarded_phase ;

processor_phase   = "-" "processor:" invocation NEWLINE ;

network_phase     = "-" "network:" invocation NEWLINE ;

guarded_phase     = "-" "guard:" expression NEWLINE
                    INDENT phase ;

dispatch_phase    = "-" "dispatch:" identifier NEWLINE
                    INDENT "order:" ordering NEWLINE
                    INDENT "arcs:" NEWLINE
                    { INDENT arc } ;

ordering          = "slot"
                  | "insertion"
                  | "." identifier [ "ascending" | "descending" ] ;

arc               = "-" "guard:" expression NEWLINE
                    ( INDENT "processor:" invocation NEWLINE
                    | INDENT "network:" invocation NEWLINE
                    | INDENT "skip:" "true" NEWLINE ) ;

iterate_phase     = "-" "iterate:" bound NEWLINE
                    INDENT phases_block ;

bound             = integer_literal
                  | field_path ;

invocation        = qualified_name "(" [ arg_list ] ")" ;
arg_list          = argument { "," argument } ;
argument          = "."
                  | identifier
                  | field_path ;

(* Shared with DIGS — guard expressions use DIGS expression syntax *)
expression        = (* see DIGS_EXPRESSION_LANGUAGE.md §Formal Grammar *) ;

field_path        = identifier { "." identifier } ;
qualified_name    = [ identifier ":" ] identifier ;

integer_literal   = DIGIT+ ;

comment           = "#" { any_character } ;
```

### Grammar Notes

1. **Indentation** follows the same rules as DIGS: two spaces per nesting level, no tabs.
2. **Guard expressions** use the DIGS expression grammar. Any boolean DIGS expression is valid as a guard. Within a dispatch phase, `.` and `slot` are available as implicit variables.
3. **Invocations** pass Records by name. The `.` argument in dispatch arcs passes the current entity. Arguments may use field paths (`object.position_x`) for partial Record access.
4. **Comments** begin with `#` and extend to end of line, identical to DIGS.

---

## Deliberate Exclusions

The Network topology does not and will never express:

| Excluded Feature | Rationale |
|------------------|-----------|
| Convergence loops (`iterate: until_stable`) | Violates boundedness. All iteration counts must be finite and compile-time-known. Physics accuracy is traded against iteration count — the game author picks N. |
| Intra-tick feedback (cyclic data dependencies) | Violates the bipartite DAG within a tick. Feedback is achieved through state Records that persist between ticks. A Processor's output in tick N becomes its input in tick N+1 via `state:` Records. |
| Dynamic topology | Violates static composition. Processors and arcs cannot be added, removed, or rewired at runtime. Variation is expressed through guard conditions on static arcs. |
| Unbounded collections | Violates bounded memory. All collections in `dispatch:` must have a declared maximum size. The compile-time bound is what makes termination provable. |
| Event-driven execution | The Network is a synchronous computation that fires once per tick. Event collection, buffering, and delivery to the Network are runtime concerns. The `requires:` boundary Records are the only mechanism by which external events enter the Network. |
| Side effects | No I/O, no rendering, no sound. The Network produces outbound boundary Records. The runtime interprets them. What happens after the tick — pixels, waveforms, network packets — is entirely the runtime's business. |
| Nested iterate phases | An `iterate:` phase may not contain another `iterate:` phase. This prevents unbounded nesting of repetition and maintains the compiler's ability to compute a static upper bound on total Processor firings per tick. |

---

## Verification Properties

A compliant compiler must verify the following properties statically. Violations are compile-time errors.

### Bipartite Invariant

Every data dependency passes through a Record. If Processor A produces a value that Processor B reads, that value must be written to a Record field by A and read from the same Record field by B. Direct Processor-to-Processor data flow is illegal.

### Dispatch Boundedness

For every `dispatch:` phase, the collection has a declared size (`[N]` or `[max: N]`). The compiler computes the maximum number of Processor firings per tick as:

```
total ≤ Σ (iterate_count × dispatch_size × max_arcs_per_entity) for all phases
```

This sum is finite and computed from declarations alone.

### Guard Completeness

For every `dispatch:` phase, the set of guard conditions must cover all possible entity states. No entity may fall through all guards unhandled. The `skip: true` directive satisfies this requirement for states that need no processing.

The compiler may compute completeness by enumerating the cross-product of guard-relevant fields (typically enum states) and verifying coverage.

### Guard Exclusivity

For every `dispatch:` phase and every possible entity state, at most one guard evaluates to `true`. Overlapping guards — where two arcs could both fire for the same entity — are a compile-time warning at minimum and may be an error at the compiler's discretion.

### Write Exclusivity

No Record field is written by two different Processors in the same tick for the same entity. If Processor A writes `object.velocity_x` and Processor B also writes `object.velocity_x`, and both execute for the same entity in the same tick, the Network is invalid.

Sequential phases writing the same field on the same entity are permitted — the later phase's write takes precedence. Write exclusivity applies only to Processors that could execute concurrently (same dispatch phase, or concurrent independent phases).

### Phase Acyclicity

The data dependency graph between phases must be acyclic. Phase A depends on Phase B if A reads a Record that B writes. The dependency graph must be a DAG. This is guaranteed by declaration order for sequential phases and by the concurrency rule for independent phases.

### Output Completeness

Every Record declared in `produces:` must be populated by at least one phase. Every Record declared in a sub-Network's `outputs:` must be populated by the sub-Network's phases.

---

## Versioning

### Parallel to DIGS

Network files do not carry an explicit version declaration in v1.0. The `network` keyword at the top of the file identifies it as a Network declaration, distinct from `record` (Record schema) and `processor` (DIGS body).

Future versions of this specification may introduce a version declaration (e.g., `#! runs-net 2.0`) if breaking changes become necessary.

### Evolution Rules

1. **Additive only** — Future versions may add new phase types, new collection modifiers, or new annotation keywords. They may never remove or change the semantics of existing constructs.
2. **Version 1.0 is forever** — A Network valid under version 1.0 will be valid under every future version. Its meaning will never change.
3. **No feature flags** — The specification version is the only mechanism for feature gating. There are no compiler flags, pragmas, or conditional compilation directives.

---

## Reference Implementation Bootstrap

The minimum viable tooling for the first Network compiler consists of:

### 1. Reference Grammar File

The EBNF grammar in this document, published as a machine-readable PEG file. This file is the canonical syntax definition.

### 2. Reference Parser

A single-file parser that reads `.runs` Network files and emits the Network structure as JSON. The JSON representation must capture:
- Record declarations (names, types, collection bounds, source annotations)
- Phase sequence (type, target, arguments)
- Dispatch phases (collection, ordering, arc guards, arc targets)
- Iterate phases (bound, nested phases)

Estimated size: 400–600 lines.

### 3. Reference Scheduler

A tool that reads a parsed Network and produces the execution schedule: the flat sequence of Processor invocations for one tick, with concrete iteration bounds.

Input: Network JSON + initial Record states.
Output: Ordered list of `(processor, entity_index, arguments)` tuples.

The scheduler is the **oracle**: any optimizing compiler's execution must produce the same output Records as executing these tuples in order.

Estimated size: 300–500 lines.

### 4. Test Vectors

For the first RUNS game (Spacewar! 3.1), the execution schedule for one tick with known initial state:

| Input State | Expected Schedule |
|-------------|-------------------|
| Two ships, no torpedoes | 2 ship_update calls, 22 skips, process_spawns, collision_detect, check_restart, update_scores, advance_starfield, build_render_list, display_starfield |
| Ship fires torpedo | ship_update (slot 0) produces spawn_request; process_spawns allocates slot 2; collision_detect includes 3 active entities |
| Ship explodes | explosion_tick (slot 0), ship_update (slot 1), 22 skips, ... |

These test vectors verify that a compiler's scheduling matches the reference scheduler's output.

---

## Relationship to Other EGS Components

```
  MAPS Notation          RUNS Source Files           Compiled Game
  (design blueprint)     (enduring artifact)         (platform binary)

  States  ─────────────→ Records (.runs)
  Verbs   ─────────────→ Processors (.runs-prim)  ──→ native functions   ← DIGS governs
  Arcs    ─────────────→ Networks (.runs)          ──→ compiled schedule  ← This spec governs
  Marks   ─────────────→ Annotations               ──→ metadata tables
```

### DIGS (Deterministic Inspectable Game Syntax)

DIGS defines what Processors compute. This specification defines when they fire, in what order, and over which entities. Guard expressions in Network arcs use the DIGS expression grammar. The DIGS recursion prohibition (DAG call graph) applies to sub-Processor calls within a body — it does NOT constrain the Network topology, which may invoke the same Processor at multiple points per tick.

### AEMS (Asset-Entity-Manifestation-State)

AEMS defines what things ARE — Entity identity, Manifestation variants, and presentation data. Data from AEMS artifacts may be consumed by RUNS Records through the `source:` annotation on state Records. The build tool reads the AEMS data, parses it according to a format specification, and populates the Record's initial state.

The format specification — how binary bytes from an AEMS Manifestation, a WAD lump, or a ROM segment map to Record fields — is a separate artifact type. Format specs declare byte offsets, endianness, field widths, and data encoding. They are plain-text, inspectable, and enduring, like everything else in the ecosystem.

### MAPS (Notation)

MAPS describes rules as studyable notation. Network arcs with guard conditions implement MAPS arc guards. The relationship is design-to-implementation: a MAPS Score is the blueprint, a RUNS Network is the wiring that implements it.

### Runtime

The runtime is everything outside the Network: event collection, tick timing, rendering, audio, input polling, and platform lifecycle. The boundary between the Network and the runtime is defined by Records:

- **Inbound** (`requires:`): The runtime populates these Records before each tick.
- **Outbound** (`produces:`): The runtime reads these Records after each tick.

What happens outside this boundary is the runtime's concern. The Network is a pure, synchronous, deterministic computation that transforms `requires:` Records into `produces:` Records.

---

*MIT License — Open for implementation, extension, critique.*
