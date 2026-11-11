# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · 🎶 **[MAPS Library](https://github.com/enduring-game-standard/maps-library)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Draft, developed against one conversion: [RUNS-Spacewar](https://github.com/wScottSh/RUNS-Spacewar) converts Spacewar! 3.1 to RUNS. Its evaluator, `tools/runs.py`, loads and runs every `runs` and `runs-prim` example in these documents.

RUNS is a plain-text form for a game's rules, so that the rules outlive the machine they were written for. Anyone can read, run, and change the source, and a runtime on another machine rebuilds it into the same game where the source pins its arithmetic (CONTEXT.md 44-46).

RUNS applies the Linux model to game execution. There is no "RUNS engine," the way there is no single "Linux OS". Each game assembles its own engine from shared components into a standalone build, the way Android and the Steam Deck are different operating systems built around the same kernel and coreutils. An open-source engine removes the vendor but keeps the coupling, since the game is still written inside one engine's runtime. RUNS keeps the rules as source, apart from any engine.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) is the reference for Processors in `.runs-prim` files. It covers their declarations, statements, and expressions, why a Record holds no code, and the `word` type.
- [Network topology](./NETWORK_TOPOLOGY.md) is the reference for `.runs` files. It covers types, enums, Records, streams, Networks, top Networks, `wait`, and the contract rules the loader enforces.
- [Machine description](./MACHINE_DESCRIPTION.md) is the reference for `.runs-machine` files. It covers the original machine's types, literals, operators and their bodies in the core, address spaces, and stated layout. The PDP-1's description is its worked example.
- [Declarations](./DECLARATIONS.md) is the reference for a machine's declarations. It covers where a change goes, why the declarations only shrink, places, conventions, storage, encoding, code layout, events and devices, machine words, the host, and the mutation gate. The PDP-1 declarations are its worked example.
- [Conversion process](./CONVERSION_PROCESS.md) is how to convert a program on any machine to RUNS. It covers the toolkit a conversion builds, describing the machine, and the mapping of each routine, register, flag, interrupt, and device of the original to Records, Processors, and Networks. Spacewar is its worked example.

## A conversion is not a rewrite

A rewrite or a re-vibe re-creates a game for another machine, and a re-vibe that is only "good enough" yields a Variant ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md) 317-319). A conversion reorganizes an existing program into RUNS. It starts from the program's assembly, or from code lifted from it, and moves the program's rules into Records and Processors. At every step, the RUNS source plus the original machine's declarations rebuilds the original binary, so the binary checks the behavior while the conversion changes the structure.

## What RUNS requires

1. **The game is exact, glitches included.** Every sequence of inputs from power-on gives the same game as the original. A glitch that play can reach is part of the game. A re-release of Super Mario 64 without the backwards long jump would not be Super Mario 64. A conversion does not change the game to fit RUNS. Where RUNS cannot say what a game does, RUNS grows.
2. **The source is the game.** DIGS guarantees every Processor's body is pure, total, and deterministic (CONTEXT.md 40-43), so a faithful runtime gives the same results under any evaluation order. The same results on another machine also need the game's own numeric types, an opt-in contract (CONTEXT.md 44-46, 144-149). RUNS-Spacewar defines its `word` type, 18 bits in ones' complement. The Network can still hang, as a game can (CONTEXT.md 213-216). Nothing about the game lives only in a binary.
3. **Every rule can be swapped.** A rule is replaceable only if its whole contract is visible. A Processor's contract is its inputs and outputs, and nothing else. It names no Record, and the Network wires each input and output to one field: Records and Processors are mutually opaque, and only the Network knows both sides (CONTEXT.md 166-169). Two Processors with the same inputs and outputs can be swapped, down to the smallest one. A register left set, a scratch word the source never names, or a patched instruction would be a hidden channel. That is why all data flows through fields the Network names.
4. **The Network is the net.** A Network is the game's colored Petri net, with Records as places, field values as tokens, Processors as transitions, and guarded arcs as gates (CONTEXT.md 188-189). It is the explicit wiring of Record fields to Processors' inputs and outputs, and the order in which rules fire is derived from that wiring, never authored (CONTEXT.md 162-170, 197-199). The conditions under which rules fire are guards on arcs. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own. A tangle in the drawing is coupling in the code. The Network as written today falls short of the graph: it is structured code that states the original's order line by line, as [Where the order comes from](#where-the-order-comes-from) says.
5. **Variation is native.** A house rule is a Variant: an edit to one Processor or one wire of the Network, not a modified copy of a program (CONTEXT.md 388-394, 410-412).
6. **The source is pure.** Every interaction is a Record or a stateless Processor. Nothing else holds logic or values.
7. **The presentation is separable.** The presentation can be removed and replaced whole without touching a game Record. This is the enduring-games pattern of a Rules region and a Realization region joined by boundary Records. It is a convention, not a base primitive of RUNS (CONTEXT.md 131-135, 158-160), and RUNS-Spacewar holds itself to it.

## Records, Processors, and Networks

RUNS has three parts.

- **A Record** is anything the game remembers, such as the object table, the random number, the frame's time budget, or the tunables. It is data and nothing else, a set of named fields with values. Global data is a Record like any other. A Record holds one set of fields, or a fixed number of each field. A field with no initial value is unknown until the game sets it or the world gives it. A **stream** is a Record that collects ordered output for a device, such as the points the display plots. In the vision a Record is written once and never overwritten: a change is a fresh value in a fresh place (CONTEXT.md 90-92). Today's source and evaluator update fields in place, so they fall short of it.
- **A Processor** is one rule, and it is stateless. It names no Record. It declares inputs and outputs, each `in`, `out` or `inout`, with the kind of value it carries, and takes and gives values only through them. A Rules Processor's body, written in DIGS (Deterministic Inspectable Game Syntax), computes with locals, and no local outlives the firing. What a Processor does depends only on its inputs. A Realization Processor's body is not DIGS, and the standard names no language for it (CONTEXT.md 150-155). RUNS-Spacewar writes its presentation Processors in DIGS too, so its evaluator can run them.
- **A Network** is the explicit bipartite wiring of Records to Processors. Each wire is one line from a Record field to a Processor's input or output, and the order of execution is derived from the wiring (CONTEXT.md 162-170, 197-199). A Network writes nothing and computes nothing. A Network used as a Processor from outside is a Sub-Network, with typed inputs and outputs at its boundary. There is no privileged sub-network entity, only regions of one graph at different zoom levels (CONTEXT.md 218-236). The Network as written today falls short of the graph. It fires Processors and other Networks in the order it states, chooses with guards, and repeats with bounded loops. Only a top Network, one that nothing fires, names Records. Every other Network is a **bundle**: it declares inputs and outputs the same way and wires them on, so it is collapsed as `run name` and expanded as its own lines. A Network may own scratch, a field only it touches, written before it is read in every firing. A guard only tests values that fields hold, and a `run` passes only wires. [Where the order comes from](#where-the-order-comes-from) says how the vision differs.

In RUNS-Spacewar every Record is one of three kinds: a **game** Record, an **interface** Record, or a **presentation** Record. `game` marks a Rules-region Record, `presentation` a Realization-region one, and `interface` a boundary Record. [Three kinds of Record](#three-kinds-of-record) states the rules.

The topology is a Petri net. Records are the places and Processors are the transitions. No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record field that the Network names. The vision allows a DIGS sub-Processor call inside a body, `let r = ns:proc(x)`. It is not a Network edge: its result is a body-local, never a Record, and the calls collapse into one transition seen from outside (CONTEXT.md 172-186). Today's DIGS has no such call. Its only calls are the operators of the [machine description](./MACHINE_DESCRIPTION.md), such as the PDP-1's `rcl`, `scr`, and `popcount`, and the constructors of the original machine's instructions.

Records are organized by meaning, not by where the original kept a value. [Conversion process](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) maps each routine, macro, and register of an original program to Records, Processors, and Networks.

In the vision, one tick of the Rules region is a DAG, and any topological order of it yields identical results, so a runtime may run it in parallel (CONTEXT.md 193-199). Today's evaluator fires sequentially: a Network runs its Processors in the order it states them, and each Processor sees everything earlier ones wrote. Spacewar's Records are updated in place, so firing its rules in another order would change it, as [Where the order comes from](#where-the-order-comes-from) says.

Here is a complete RUNS program. A `.runs` file declares Records and Networks:

```runs
game record speed
  dx: word = 3

game record wall
  past: word = 0            # how far past the wall the ball is

interface record ball
  x: word = 0

interface record pad
  held: word                # no initial value: the player's button comes in

presentation stream screen
  x: word

network tick
  reads: pad
  writes: screen
  run move_ball
    held: pad.held
    x: ball.x
    dx: speed.dx
  run reach_wall
    x: ball.x
    past: wall.past
  if wall.past >= 0:
    run bounce
      dx: speed.dx
  run draw_ball
```

A `.runs-prim` file declares Processors:

```runs-prim
processor move_ball
  in held: word
  inout x: word
  in dx: word
  if held == 0:
    set x = x + dx

processor reach_wall
  in x: word
  out past: word
  set past = x - 0100

processor bounce
  inout dx: word
  set dx = -dx

processor draw_ball
  reads: ball
  writes: screen
  emit screen: ball.x
```

The example follows today's source, so `tick` states its order line by line. `tick` is a top Network, because nothing fires it, so it is a whole game, and it is the one routine that names Records. Each Processor names only its inputs and outputs, and `tick` wires each one to one field, one wire a line. The button comes in through `reads: pad`, and the points leave through `writes: screen`. `draw_ball` emits to a stream, which an output does not carry yet, so it keeps `reads:` and `writes:`, the form a conversion starts from. The ball's speed, and how far past the wall it is, are the game's own. `reach_wall` computes the distance into a Record, and the guard only tests it. Its position is in the interface, because the game moves it and the presentation shows it. `draw_ball` is the presentation. To make a house rule where the ball stops instead of bouncing, replace `bounce` and change nothing else. To show the ball on another screen, replace `draw_ball` and `screen` and change nothing in the game.

## Where the order comes from

In the vision, the source states no order. A Network is the explicit wiring of Records to Processors (CONTEXT.md 162-170). Two rules make the order a fact derived from that wiring within the Rules region: single-assignment purity, where a shared resource such as the random number is a threaded chain of distinct values, `prng_v0` to `prng_vN`, and guards that partition. Given both, one tick is a DAG, and any topological order yields identical results (CONTEXT.md 193-199). `phases:` and `order:` are a crutch for resources that should be threaded (CONTEXT.md 226-227, 342-343). The only unbounded loop is the tick feedback through `state:` Records, in the wiring (CONTEXT.md 204-206).

Today's source falls short of that. A Network is structured code that states the original's order, one line after another, because Spacewar's Records do not carry it. They are updated in place, and two Processors may write the same Record. `collision` and each object's calc routine both write the object table, so their reads and writes give no order between them, yet changing that order changes 294 of 300 test frames. How Spacewar's object table becomes a threaded chain, so that the wiring carries this order, is open. Today the source reads order this way:

- **A line after a line is a place.** `run a` followed by `run b` means `a` puts a turn marker in a place, and `b` fires only when the marker is there. The place holds no data, only the turn. The source writes it as one line under another.
- **A loop is a marker that goes around**, back to the loop's first line until the exit's guard sends it on. The vision has no such loop inside a tick: a Dispatch is a bounded fold whose count is fixed before it starts, with no `break` (CONTEXT.md 343-347).

Two rules of today's source already follow the vision:

- **A guard only tests.** It compares values that Records hold, with each other or with constants, and joins comparisons with `and`, `or` and `not`. It computes nothing on a value. A condition that needs arithmetic is a Processor that computes it into a Record, and the guard tests that Record. Spacewar's breakout test, `(random.number | 0400000) + ships.uncertainty[slot] >= 0`, is the Processor `weigh_breakout`, which writes `breakout_check.margin`, and the guard `breakout_check.margin >= 0`. The image is unchanged. The compiler keeps the margin in AC, where the original kept it, because no declaration gives `breakout_check` a word.
- **A `run` passes only wires.** Each wire names the one field an input or output of the routine takes. `slot` stays in the one Network that walks the slots: a bundle gets `objects.x[slot]` already chosen, as the original's pointers gave each routine "this object's x". A slot the game computes, such as the free slot a new torpedo takes, lives in a Record, and the walking Network wires the whole field beside it. The form a conversion starts from, `run explosion(slot)`, still loads, with the slot used only to choose a slot of a collection.

The vision also has the guards of each branch partition, exactly one true, with an explicit `else` arc for an open-typed discriminant (CONTEXT.md 351-358). Today's `if` fires its first true arm and may omit `else`, so it falls short.

The loader reports a guard that computes and a `run` that passes a value as impurities and refuses them.

## Exact over every input, glitches included

A glitch is one of three kinds, by what it reads.

1. **A logic glitch** is the game's own logic, such as the backwards long jump. A conversion keeps it with no extra work. In Spacewar, the previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed. The conversion keeps it.
2. **A layout glitch** reads past an array, through a stale pointer, or reads one kind of object as another, such as DOOM's `spechit` overflow. In those states the rule is whatever lies next in memory, so the layout is part of the game. Where play reads the layout, the RUNS source states it.
3. **A machine glitch** runs data as code or jumps into the middle of a routine. On that path the rule is what the machine does with those bytes. The RUNS source states that rule in a Processor, as it states any other. A general compiler for the machine reproduces the bytes in the binary. RUNS itself never keeps instructions in a Record to run them.

All three kinds share one piece, the [machine description](./MACHINE_DESCRIPTION.md). It supplies RUNS's types and every operator on them. For Spacewar, that is the `word`, the game's number. That a word is 18 bits in ones' complement is a rule of Spacewar, and the source states it exactly, in the description's operator bodies that [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes. Where play reads the layout, its address spaces carry the layout the RUNS source states. The rest of the game is RUNS.

A halt or a hang that the original reaches is a rule, not an error. Spacewar halts when a ship fires and the object table is full, and the conversion writes `stop`. Spacewar also halts between games to show the scores, and the conversion writes an `emit` of the scores, then `wait`. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the RUNS source is wrong.

A conversion measures where play reaches layout or machine behavior, as [Conversion process](./CONVERSION_PROCESS.md#6-measure-where-play-reaches-the-machine) states. RUNS-Spacewar measures it with `tools/reach_oracle.py`, which runs scripted matches of the original in SIMH. Its findings for Spacewar are these:

- Play observes no layout read. The main loop reads past the ships' two-word outline array for every torpedo slot, but only the ships' own slots use the word it loads. A check that poisons that word for every other slot still matches the original, so the image's layout carries the read and the RUNS source does not state it.
- The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. Those words are fields with no initial value, and they come in at the game's boundary.
- The game writes code and runs it. At each new game, Spacewar's outline compiler writes each ship's outline as PDP-1 instructions, and each frame the spaceship jumps into them to draw the ship. The outlines are presentation. RUNS-Spacewar's source states them with a Record of `insn` values and a Processor that runs them with `jump`. Both are impure, and the purity report counts each one. The pure form states what the outline code draws in Processors of its own, and the compiler reproduces the instructions.
- Everywhere else, play reaches only the `word` type's own arithmetic, such as sums that wrap and shifts of negative numbers.

## Three kinds of Record

Presentation is the screen, the sound, the controls, the pacing, and the machine underneath. It is rebuilt for each platform, and the game is not, so the presentation has to come out whole with no change to a rule. In RUNS-Spacewar every Record is one of three kinds, and each kind says which Processors may touch it. The kinds are the enduring-games pattern: a Rules region and a Realization region joined only by boundary Records (CONTEXT.md 131-160). That pattern is a convention, not a base primitive of RUNS (CONTEXT.md 133-134, 159-160). RUNS-Spacewar's loader enforces it as this project's own rule.

- **A game Record** holds what only the rules use, such as Spacewar's fuel, the random number, or a ship's angular momentum.
- **An interface Record** holds what the game and its presentation share. The game writes what there is to show, such as each object's position and heading. The world writes what comes in, such as the controls and the switches.
- **A presentation Record** belongs to one platform, such as the pen that traces a ship's outline, the scope's points, or the frame's time budget.

A Processor that touches a presentation Record is part of the presentation. Every other Processor is part of the game. Every stream leaves to a device, so every stream is presentation, and a Processor that emits to one is presentation too. A presentation Processor touches no game Record and writes no interface Record, and a guard that reads a presentation Record guards only the presentation. [Three kinds of Record](./NETWORK_TOPOLOGY.md#three-kinds-of-record) states the rules as the loader enforces them.

One Network wires both kinds of Processor. Remove every presentation Processor and every run of one, and what is left is the game. The rules make its Records the same with the presentation or without it. A new platform supplies its own presentation Processors and Records, reads the same interface, and changes nothing in the game. The interface Records are the whole contract between the two.

A Record's kind follows from what its values reach, not from what the code was written for. A value is the game's if any rule can observe it. Spacewar's central star draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the two draws are the game's, and only the line the star draws from them is presentation. A Processor that does both, as the original's code often does, splits in two. The game's half writes the value to an interface Record, and the presentation's half reads it.

A conversion checks its split by running the game with every presentation Processor removed against the original, as [Conversion process](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) states.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a field with no initial value, in an interface Record that the top Network declares under `reads:`. The vision calls it an inbound boundary Record, written by the runtime before a tick and declared under `requires:`, and an outbound one is read after the tick and declared under `produces:` (CONTEXT.md 272-275). Today's keywords disagree: `reads:` and `writes:` declare boundary Records, and `requires:` is a precondition.
2. A value goes out to the presentation. It is an interface Record the game writes.
3. The machine computes something the rules then read, such as a sum that wraps or a collision a video chip latches. That computation is a rule, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes a rule or a value that comes in.

Only the third could widen the boundary, and a conversion always resolves it by moving the computation into the game. So the interface can grow in data, but it does not gain a new kind of thing.

## The declarations

A machine's **declarations** are the half of its package that never runs. They hold only choices that play cannot observe, such as where each routine and field lies, which register carries a value, how an enum is encoded in bits, and which device carries each value that comes in or goes out. They record the original programmer's arbitrary choices, never game logic, and a port leaves them behind with that machine's presentation. They are not a place to make hard RUNS source compile, and their count of entries only shrinks. [Declarations](./DECLARATIONS.md) states every section they have, where a change goes, what the compiler refuses, how the host fires a game, and the mutation gate. RUNS-Spacewar's PDP-1 declarations are `pdp1/`, and `pdp1/README.md` there defines their full vocabulary.

## The compiler

A compiler takes RUNS plus a target's declarations. With the original machine's declarations, it builds the original binary exactly. With another machine's declarations, it builds the same game on that machine. The compiler belongs to the target machine, and every game for that machine shares it. When a pure shape does not compile to the original binary, the RUNS source changes first, then the compiler gains a general rule, as [Where a change goes](./DECLARATIONS.md#where-a-change-goes) states.

In RUNS-Spacewar, `tools/runsc.py` compiles the RUNS source and the PDP-1 declarations to the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` compiles that C to a tape image. The image's sha256 is the original's, `8744e9c9c8540cc5075c5cbb91c56745a4305fdf8e7afca43bea2e9e04ca4bdf`.

RUNS-Spacewar checks the conversion three ways:

- **The evaluator against SIMH.** Each routine and Network runs in the evaluator and in SIMH from the same state, and the checks compare Records and points.
- **The image against the original.** `runsc` builds the image from RUNS and prints `MATCH` when its hash is the original's.
- **The mutation gate.** `tools/check_compiled.py` mutates the RUNS source and the declarations, as [The mutation gate](./DECLARATIONS.md#the-mutation-gate) states.

`tools/check_all.sh` runs all three.

## Relationship to other EGS protocols

RUNS is a protocol on its own.

- **MAPS** is a separate protocol, a notation for studying and designing rules.
- **AEMS** is a separate protocol for assets and things. A game's assets belong there. Spacewar's ship outlines and star catalog are data on the tape, so the conversion keeps them in the RUNS source as Records. RUNS defines no way to read AEMS data.
- **RUNS Library** is a separate repository that predates this spec and differs from it. Where they differ, this spec governs.

## Check the examples

Every `runs` and `runs-prim` example in these documents loads and runs in RUNS-Spacewar's evaluator. The examples' machine is the PDP-1, and they omit the `machine pdp1` line, because that evaluator holds the [PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) in code and reads no `machine` line. Blocks tagged `runs-machine` and `text` are not run. Every accepted example gives each Record and stream a kind, so the loader checks it for purity. `tools/check_examples.py` checks this. It parses each accepted example alone, then loads all of a document's accepted examples as one program, wires each `run`, runs `runs.check`, and runs each top Network six passes. A block alone is not wired, because its runs may wire routines that another block declares. It confirms that each rejected example fails with the error its first line quotes. It also fails on an em dash or an en dash in the documents.

To run the check, put `RUNS-Spacewar` beside this repository and run this command from this repository:

```sh
python3 tools/check_examples.py
```

To point it at other directories, pass them as arguments:

```sh
python3 tools/check_examples.py <runs-spec dir> <RUNS-Spacewar dir>
```

The command exits with status 0 when every example passes.

## Open questions

- **The kind of each Record.** A conversion decides each kind by hand, from what the Record's values reach. A tool could trace each value through the original in SIMH instead.
- **A stream through an output.** A Processor that emits names its stream, so it keeps `reads:` and `writes:`. How a stream passes through a Processor's output, so that an emitting Processor names no Record either, is not settled.
- **The Network as a graph.** The vision's Network is a wiring graph whose order is derived (CONTEXT.md 162-170, 197-199). How that graph is written down, how a Network loop whose exit depends on data is expressed in it, and how a Record that two Processors write becomes a threaded chain, are not settled.
- **Recursion.** A routine that keeps values across a call to itself needs a copy of them per depth. One field, an input's or scratch, cannot hold them. Spacewar does not recurse.
- **Naming and distribution.** How RUNS source is named, published, and shared, and what a shared library of Records and Processors holds.

**MIT License.** Open for implementation, extension, and critique.
