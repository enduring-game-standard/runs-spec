# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Draft, developed against one conversion: [RUNS-Spacewar](https://github.com/wScottSh/RUNS-Spacewar) converts Spacewar! 3.1 to RUNS. Its evaluator, `tools/runs.py`, loads and runs every `runs` and `runs-prim` example in these documents.

RUNS is a plain-text form for a game's rules, so that the rules outlive the machine they were written for. Anyone can read, run, and change the source, and a runtime on another machine rebuilds it into the same game, because the source states the game's arithmetic, which is one of its rules.

RUNS applies the Linux model to game execution. There is no "RUNS engine," the way there is no single "Linux OS". Each game assembles its own engine from shared components into a standalone build, the way Android and the Steam Deck are different operating systems built around the same kernel and coreutils. An open-source engine removes the vendor but keeps the coupling, since the game is still written inside one engine's runtime. RUNS keeps the rules as source, apart from any engine.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md): read before you write a Processor body (`.runs-prim`). Statements, expressions, the `word`, and why a Record holds no code.
- [Network topology](./NETWORK_TOPOLOGY.md): read before you write Records, streams, or a Network (`.runs`, `.net`). Network files, guards, order, loops, halts, contracts, and every loader error.
- [Machine description](./MACHINE_DESCRIPTION.md): read before you state a machine's arithmetic (`.runs-machine`) or a layout play reads. Types, literals, operators, the core, address spaces. Worked example: the PDP-1.
- [Declarations](./DECLARATIONS.md): read before you change a machine's declarations or its compiler, or when a pure shape will not compile. Where a change goes, the seven sections, compiler checks, the mutation gate, the host. Worked example: the PDP-1.
- [Conversion process](./CONVERSION_PROCESS.md): read before you convert an existing program. The route, the toolkit, the rule-or-machine test, the ten steps from describing the machine to the archive. Worked example: Spacewar.

## What the work is for

A conversion makes the **reference** for a game: its original program rewritten into RUNS, with the game exactly the same ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Conversion). It is not a Port, which strips the presentation and puts in new presentation for another machine, and it is not a Variant, which changes the rules. The rules are pure and separate from the presentation, and the whole original presentation is still there. Compiled for the original machine, the reference is the original game. Run headless, its rules run alone on any machine. The reference is what goes into the archive untouched, and every later Port and Variant starts from it.

- **The rules are everything that changes what happens in the game.** That includes the arithmetic: Spacewar's 18-bit ones' complement is as much a rule as Yahtzee's six-sided die, and DOOM with floats would desync its demos and be a different game. It also includes the limits, and the order of steps wherever order changes a result. It includes what the original machine does the same way every time, such as memory past the end of an array, because in a digital game the machine fills every gap in the rules. Intent is not the rules. A choice of the original machine that changes nothing, such as which register or address holds a value, belongs to the machine's declarations or its compiler, never to the RUNS. [Rule or machine: the one test](./CONVERSION_PROCESS.md#rule-or-machine-the-one-test) states the test and how to run it.
- **The oracle is the binary.** The RUNS source, compiled for the original machine, rebuilds the original binary exactly. Comparing play proves only the inputs tested. The identical binary proves every input, presentation included.
- **The binary is the original, and the RUNS source is an edition of it** (CONTEXT.md, Original, Edition, Exclusion). The archive identifies the original by its hash and keeps the source and toolchain that rebuild it. The edition carries everything the binary does by default. Where it departs, it says so in its exclusion list, at an exit point, with evidence and who decided it. [The binary is the original; the RUNS source is its edition](#the-binary-is-the-original-the-runs-source-is-its-edition) states the six rules.
- **The process is the product.** The aim is a documented process that repeats for every game that has existed or will, on any machine, as automatable as possible: run it on DOOM and it gives logical groupings of the game's rules. A game born in RUNS follows the same specification from scratch. Spacewar is where the process is worked out, not its limit.
- **The groupings are what get shared.** Each grouping is a stateless bundle, named and described, made of smaller bundles down to atomic Processors (CONTEXT.md, Sub-Network). It takes values in and gives values out and names no Record. Anyone can find "Spacewar's gravity" on the commons, wire it into another game, and edit it in place. The edit makes it theirs, and a different game. What is unique to a game is its wiring. A Processor that reads one game's Records can be used by no other game.

## A conversion is not a re-vibe

A re-vibe re-creates a game from an impression of it, and a re-vibe that is only "good enough" yields a Variant ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Port and Variant). A conversion completely rewrites an existing program into RUNS and keeps the game exactly the same. It reorganizes the program, not the game. It starts from the program's assembly, or from code lifted from it, and moves the program's rules into Records and Processors. At every step, the RUNS source plus the original machine's declarations rebuilds the original binary, so the binary checks the behavior while the conversion changes the structure.

## What RUNS requires

1. **The rules are complete, so the game is exact.** Every sequence of inputs from power-on gives the same game as the original. The RUNS source states the rules completely, including what the original machine does the same way every time, and the original's glitches emerge from it. The RUNS source carries everything by default, and a departure is a stated exclusion. [The rules are complete, and glitches emerge from them](#the-rules-are-complete-and-glitches-emerge-from-them) says why. RUNS fits the game, never the reverse: where RUNS cannot say what a game does, RUNS grows.
2. **The source is the game.** DIGS guarantees every Processor's body is pure, total, and deterministic, so a faithful runtime gives the same results under any evaluation order (CONTEXT.md, DIGS). Every RUNS game, converted or born in RUNS, states its arithmetic: its number types and their operations. The arithmetic is a rule, and another arithmetic is another game. RUNS-Spacewar's `word` is 18 bits in ones' complement. The Network can still hang, as a game can (CONTEXT.md, Network). Nothing about the game lives only in a binary.
3. **Every rule can be swapped.** A Processor's contract is its inputs and outputs, and nothing else. It names no Record, and the Network wires each input and output to one place, a field or a whole Record. Records and Processors are mutually opaque, and only the Network knows both sides (CONTEXT.md, Processor and Network). Two Processors with the same inputs and outputs can be swapped, down to the smallest one. All data flows through fields the Network names, so a register left set, an unnamed scratch word, or a patched instruction has no channel to hide in.
4. **The Network is the net.** A Network is the game's colored Petri net, with Records as places, field values as tokens, Processors as transitions, and guarded arcs as gates (CONTEXT.md, Network). Its wires and guards state when and in what order rules fire. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own, so a tangle in the drawing is coupling in the code. [Where the order comes from](#where-the-order-comes-from) says how.
5. **Variation is native.** A house rule is a Variant: an edit to one Processor or one wire of the Network, not a modified copy of a program (CONTEXT.md, Variant).
6. **The source is pure.** Every interaction is a Record or a stateless Processor. Nothing else holds logic or values.
7. **The presentation is separable.** The presentation can be removed and replaced whole without touching a game Record. This is the enduring-games pattern of a Rules region and a Realization region joined by boundary Records. It is a convention, not a base primitive of RUNS (CONTEXT.md, Processor), and RUNS-Spacewar holds itself to it.

## Records, Processors, and Networks

RUNS has three parts.

- **A Record** is anything the game remembers, such as the object table, the random number, the frame's time budget, or the tunables. It is data and nothing else, a set of named fields with values. Global data is a Record like any other. A Record holds one set of fields, or a fixed number of each field. A field with no initial value is unknown until the game sets it or the world gives it. A **stream** is a Record that collects ordered output for a device, such as the points the display plots. A Record keeps its value until a Processor gives it a new one. Only a Processor changes a Record. It takes the value out, computes, and may put the result back in the same place or in another (CONTEXT.md, Record). A value that changes needs no new Record.
- **A Processor** is one rule, and it is stateless. It names no Record. It declares inputs and outputs, each `in`, `out` or `inout`, with the kind of value it carries, and takes and gives values only through them. A Rules Processor's body, written in DIGS (Deterministic Inspectable Game Syntax), computes with locals, and no local outlives the firing. What a Processor does depends only on its inputs. A Realization Processor's body is not DIGS, and the standard names no language for it (CONTEXT.md, Processor). RUNS-Spacewar writes its presentation Processors in DIGS too, so its evaluator can run them.
- **A Network** is the explicit bipartite wiring of Records to Processors. Each wire is one line from a Record field to a Processor's input or output, and the wires and guards state the order of execution (CONTEXT.md, Network). A Network writes nothing and computes nothing. A Network used as a Processor from outside is a Sub-Network, with typed inputs and outputs at its boundary. There is no privileged sub-network entity, only regions of one graph at different zoom levels (CONTEXT.md, Network and Sub-Network). RUNS source writes each Network as a network file, a `.net` file that lists its places, its transitions, and its arcs, with no separate list of steps. A Network that another uses as a transition is a **bundle**. It declares inputs and outputs as a Processor does, so it is collapsed as one transition and expanded as its own file. [Network files](./NETWORK_TOPOLOGY.md#network-files) defines the format. The loader lowers each network file to a Network in the inline form, which states its order line by line, and the evaluator runs that.

The game runs as a sequence of ticks. A top Network fires once a tick and runs to its end. Nothing computes between ticks. Whatever the original computed between two steps is a transition in the Network, wired so that it fires in its turn.

In RUNS-Spacewar every Record is one of three kinds: a **game** Record, an **interface** Record, or a **presentation** Record. `game` marks a Rules-region Record, `presentation` a Realization-region one, and `interface` a boundary Record. [Three kinds of Record](#three-kinds-of-record) states the rules.

Each value one rule hands to the next goes through a Record field that the Network names. Processors connect only through the Network, by way of Records, and composition is bundling (CONTEXT.md, Network). A Processor never calls another. A body computes with locals, which never leave it, and its only calls are the operators of the [machine description](./MACHINE_DESCRIPTION.md), such as the PDP-1's `rcl`, `scr`, and `popcount`.

Records are organized by meaning, not by where the original kept a value. [Conversion process](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) maps each routine, macro, and register of an original program to Records, Processors, and Networks.

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
    x: ball.x
    points: screen
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
  in x: word
  inout points: screen
  emit points: x
```

The example uses the inline form, so `tick` states its order line by line. As a network file, `tick` would list its places, transitions, and arcs instead. `tick` is a top Network, because nothing fires it, so it is a whole game, and it is the one routine that names Records. Each Processor names only its inputs and outputs, and `tick` wires each one to one place, one wire a line. The button comes in through `reads: pad`, and the points leave through `writes: screen`. `draw_ball` takes the stream as an `inout` of the stream's kind and emits to it by that name. The ball's speed, and how far past the wall it is, are the game's own. `reach_wall` computes the distance into a Record, and the guard only tests it. Its position is in the interface, because the game moves it and the presentation shows it. `draw_ball` is the presentation. To make a house rule where the ball stops instead of bouncing, replace `bounce` and change nothing else. To show the ball on another screen, replace `draw_ball` and `screen` and change nothing in the game.

## Where the order comes from

The source has no separate list of steps: the wires and guards state the order. Two rules make the wiring state the whole order within the Rules region: every change goes through a Processor, and the guards on one place partition. Under the first, the wires and guards order any two Processors that touch one place, so the random number's values, `prng_v0` to `prng_vN`, pass through one place in wired order. Given both, one tick of the Rules region is a DAG of firings, and any topological order of it yields identical results (CONTEXT.md, Network). Transitions that share no place may fire in parallel. Where two touch one place, the wires and guards make one wait for the other. `phases:` and `order:` are a crutch for resources that should be threaded (CONTEXT.md, Network and Phase / Dispatch / Guard).

The loader reads the order from the wires and guards alone, so shuffling the lines of a network file leaves the lowered program the same. RUNS-Spacewar's evaluator then fires one transition at a time in that order, and each Processor sees everything earlier ones wrote.

Two Processors may write the same Record. `collision` and each object's calc routine both write Spacewar's object table, and changing their order changes 294 of 300 test frames. In `runs/frame/active_object.net`, the collisions give the table to the place `collided`, and `calc` takes it from there, so the collisions come first. The loader refuses two writers of one place that the wiring leaves unordered.

A guard only tests, and values pass only through wires. A condition that needs arithmetic is a Processor that computes it into a Record, and the guard tests that Record. Spacewar's breakout test, `(random.number | 0400000) + ships.uncertainty[slot] >= 0`, is the Processor `weigh_breakout`, which writes `breakout_check.margin`, and the guard `breakout_check.margin >= 0`. The image is unchanged: the compiler keeps the margin in AC, where the original kept it, because no declaration gives `breakout_check` a word. [Guards](./NETWORK_TOPOLOGY.md#guards) and [Order](./NETWORK_TOPOLOGY.md#order) state the rules the loader enforces, and [The Network loop](./NETWORK_TOPOLOGY.md#the-network-loop) states the rule for loops.

## The rules are complete, and glitches emerge from them

In a digital game the machine fills every gap in the rules. A board game leaves its gaps to the players. A digital game's gaps get the machine's answer, the same every time, in every state, for every input. So a digital game's rules are complete whether anyone meant them or not: they are the original program running on its original machine. The designer's intent is never complete. **Intent is not the rules**, and intent is not what the reference archives. The source code is not the rules either. C leaves an out-of-bounds read, a use after free, and an uninitialized read undefined. The compiler and the CPU decide them, and the binary records what they decided. That is one reason the oracle is the binary.

The rules are the boundary of the game's possibility space: every state reachable from power-on by any sequence of inputs, and how each state moves to the next. Gameplay is the paths players take inside that space, glitches included. Gameplay emerges from the rules. The rules are not gameplay. "Intended" and "unintended" describe the designer's map of the space, not the space. Super Mario 64's backwards long jump is gameplay that emerges from its rules: Mario's backward speed has no cap. A glitchless speedrun category is a rule the players add on top, and the game is unchanged. Removing a glitch from the game itself means writing a different rule into the gap, and that makes a different game, a Variant ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Variant).

The boundary is not always clear, for three reasons:

- The reachable space cannot be listed in general, so glitches are found after the fact. Ocarina of Time's stale reference manipulation was found in late 2019, 21 years after release. Super Mario 64's Tick Tock Clock upwarp is still unexplained.
- Anything a player can observe, someone will depend on (Hyrum's law). Speedrunners and demo authors do.
- The program and the machine were one system. The line between "game" and "machine" is drawn afterward.

So a conversion neither recreates glitches nor removes them. It states the rules completely, including what the original machine does the same way every time. The glitches then emerge by themselves on any machine that runs those rules, including glitches nobody has found yet. Glitches cannot be listed, so a conversion's completeness is judged on its rules, never against a list of glitches.

### Sort a behavior at the machine's edge

When the machine changes, sort each behavior by following its data across the edge of the original machine, never by whether it was intended. The edge is the one physical boundary the game has.

- **In** is whatever the program reads from a device, such as the controller, the switches, a clock, or a count of video frames, and memory the program never set, such as the contents of memory at power-on.
- **Out** is the screen and the speaker.
- **Inside the edge**, a value that only ever flows out is presentation. Everything else is the rules, including what the hardware does the same way every time: the arithmetic, memory past the end of an array, and code the program runs.

Spacewar's 18-bit ones' complement is a rule. Its toroidal wrap is defined nowhere: it falls out of the coordinate arithmetic, and the game is not Spacewar without it. The RUNS source states these rules. A machine that drops them is not running the same rules. DOOM shows what that costs: Boom fixed vanilla DOOM's overflows and broke vanilla demos, PrBoom added compatibility levels, and Chocolate Doom emulates the `spechit`, reject, and intercepts overflows to keep vanilla demos in sync.

Lag reaches the rules, if it reaches them at all, as a clock reading, which is an input. On the original machine that input carries the lag. A Port feeds it different values, so the rules are the same and the gameplay differs. "Better" and "worse" describe the gameplay, not the game: GoldenEye's lookdown, and Ocarina of Time on the N64 and on the Wii Virtual Console, which are one game with separate leaderboards. Space Invaders moves one invader per video interrupt, an input, by a rule. No line of the program says "speed up": the fewer invaders are left, the more often each one moves. The curve was found by accident and kept because it made a better game. It is not lag. It emerges from the input and the rule on any machine that feeds the same interrupts.

An effect that only flows out belongs to the presentation, such as DOOM's visplane-overflow crash. The reference keeps it, with the whole original presentation. A Port changes it by definition ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Port). That crash also ends the program, and so stops the rules; how RUNS states a presentation effect that ends the program is open, as [Open questions](#open-questions) states.

A Port keeps every rule, changes what only flows out, and feeds the rules its own inputs. For a game born in RUNS, the RUNS semantics are the machine: whatever RUNS defines in its own gaps is that game's hardware behavior.

Time is why the RUNS source has to state the hardware's behavior. The original binary carries every glitch only while a faithful machine exists to run it. Hardware dies, and emulators differ: some Ocarina of Time tricks work on the Wii Virtual Console and crash a real N64, and TASVideos rejects them for N64 runs. Speedrunners and demo authors already treat the machine as part of the game, and leaderboards split by version and platform. Over a thousand years, the RUNS source is the only lasting statement of the rules.

What counts as the machine is still a judgment: which revision, and where specified behavior ends and physical fault begins. A flipped bit is a fault. A documented CPU quirk is behavior. It is made once per machine, in that machine's description ([Machine description](./MACHINE_DESCRIPTION.md#what-counts-as-the-machine)).

### The binary is the original; the RUNS source is its edition

Inside one deterministic system, every line between "game" and "machine" is drawn by whoever looks, and intent cannot be read from the binary. A line by "who writes the program" fails: Screeps and Baba Is You make writing code and rewriting the rules the game itself. Textual scholarship met the same problem, an author's intent against errors in transmission, and settled not the intent question but how to handle the judgment: keep the original witness untouched, and make each editorial judgment explicit, with its evidence, attributed, and open to revision. RUNS takes the same stance (owner, 2026-11-15; CONTEXT.md, Original, Edition, Exclusion, Exclusion list):

1. **The binary is the original.** The reference archive identifies it by its hash and keeps the source and the toolchain that rebuild it; the rebuilt binary is verified against the hash. On the original machine it has everything, uninterpreted. A game's GitHub repo keeps the hash in place of the binary (owner, 2026-11-15: "it doesn't make sense to keep the binary in a GitHub repo for so many reasons. but a hash of the binary is a fine shortcut").
2. **The RUNS source is an edition of it, and carries everything by default.** Every behavior of the binary is in the rules. Glitches are never purged.
3. **An exclusion is a stated decision, never a silence.** The RUNS source states the exit point, the state and the step where play leaves the edition. The behavior past it is the binary's alone.
4. **Every exclusion carries its evidence and who decided it.** Evidence is developer statements, the manual, speedrun categories, sequels, and the choices of port communities. Intent never decides silently. A later editor may disagree and make another edition. The binary does not change.
5. **The check.** The rules, run alone against the binary, match everywhere except the listed exclusions, the only places they may differ. Compiled for the original machine, the edition still rebuilds the original binary, the oracle.
6. **A game born in RUNS has no exclusions.** It has no binary, and its RUNS source is the original.

Code the program runs splits in two. Code the program fixes for itself is the original's behavior, and the edition carries it like any other: Spacewar's outline code, which the program writes from its own tables, and a jump at the wrong entry into the program's own bytes. Code the player writes and the program then runs is the standard example of an exclusion.

How the three worked games sort:

- **Spacewar.** Carried: the ones' complement arithmetic and so the wrap, the fire glitch with sense switch 3 on, the halt when the object table is full, the central star's random draws, and the outline code the program writes for itself. The contents of core at power-on are an input. Exclusions: none. That is an inference from the reach oracle: play reaches only the word's own arithmetic, and the one read past an array is shown unobserved by the poison check (RUNS-Spacewar's `docs/exclusions.md`).
- **DOOM.** Carried: 16.16 fixed point, the random table and its draw order, the limits, the order of thinkers, and the `spechit` and reject overflows, as stated layout, because vanilla demos depend on them. Wallrunning and strafe-running emerge. The visplane crash is presentation, and the reference keeps it. Exclusion candidates: the intercepts overflow, whose emulation Chocolate Doom's users advise leaving off unless a demo needs it, and any code execution. Chocolate Doom's choices of what to emulate are ready-made evidence.
- **Ocarina of Time.** Carried: single-precision float modes, the random number generator, the update rate, the culling flag set while drawing, Z-targeting's screen test, and what stale reference manipulation writes into freed actor memory, so the RUNS source states the memory reuse. Lag is a clock input. Exclusion: code the player writes. Its exit point is the step where control jumps into bytes the player chose. Evidence: the community places it apart (Zelda Wiki: "commonly restricted or placed in its own category"), and TASBot's talk is listed as "How to hack an N64 through the controller ports". Each shipped version is its own original with its own edition, and 1.0 keeps glitches later versions fixed.

### Spacewar's rules and the machine

Spacewar's own logic has a glitch that emerges from its rules. The previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed. The conversion states the rule as the program has it, and the glitch emerges.

The [machine description](./MACHINE_DESCRIPTION.md) holds the hardware's rules that every game on a machine shares. It supplies RUNS's types and every operator on them. For Spacewar, that is the `word`, the game's number. That a word is 18 bits in ones' complement is a rule of Spacewar, and the source states it exactly, in the description's operator bodies that [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes. Where the program reads memory past an array, the layout is part of the complete rules: the RUNS source states it, and the description's address spaces carry it. Where the program runs code it fixed for itself or jumps into the middle of a routine, the rule is what the machine does with those bytes on that path. The RUNS source states that rule in a Processor, as it states any other, and a general compiler for the machine reproduces the bytes in the binary. RUNS itself never keeps instructions in a Record to run them. The rest of the game is RUNS.

A halt or a hang that the original reaches is part of the rules, not an error. Spacewar halts when a ship fires and the object table is full, and the conversion writes `stop`. Spacewar also halts between games to show the scores. The conversion emits the scores and ends the tick there, and the `pause` Record makes the next tick the operator's answer. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the RUNS source is wrong.

A conversion measures which machine behavior the program reaches, so that the RUNS source states every rule the hardware supplies and nothing the program never reaches, as [Conversion process](./CONVERSION_PROCESS.md#6-measure-where-play-reaches-the-machine) states. RUNS-Spacewar measures it with `tools/reach_oracle.py`, which runs scripted matches of the original in SIMH. Its findings for Spacewar are these:

- The rules reach no layout past an array. The main loop reads past the ships' two-word outline array for every torpedo slot, but only the ships' own slots use the word it loads. A check that poisons that word for every other slot still matches the original, so that layout is not part of the rules, and the image's layout carries the read.
- The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. They are inputs: memory the program never set. Those words are fields with no initial value, and they come in at the game's boundary.
- The game writes code and runs it. At each new game, Spacewar's outline compiler writes each ship's outline as PDP-1 instructions, and each frame the spaceship jumps into them to draw the ship. The outlines are presentation. The program fixes this code for itself from its own tables, so the edition carries it, and no exclusion touches it. RUNS-Spacewar states what the outline code draws: the outline compiler decodes each outline into strokes (`outline_code`), and `draw_outline` walks them. The compiler reproduces the instructions.
- Everywhere else, the program reaches only the `word` type's own arithmetic, such as sums that wrap and shifts of negative numbers.

## Three kinds of Record

Presentation is the screen, the sound, the controls, the pacing, and the machine underneath. It is rebuilt for each platform, and the game is not, so the presentation has to come out whole with no change to a rule. In RUNS-Spacewar every Record is one of three kinds, and each kind says which Processors may touch it. The kinds are the enduring-games pattern, a Rules region and a Realization region joined only by boundary Records. The pattern is a convention, not a base primitive of RUNS (CONTEXT.md, Processor), and RUNS-Spacewar's loader enforces it as this project's own rule.

- **A game Record** holds what only the rules use, such as Spacewar's fuel, the random number, or a ship's angular momentum.
- **An interface Record** holds what the game and its presentation share. The game writes what there is to show, such as each object's position and heading. The world writes what comes in, such as the controls and the switches.
- **A presentation Record** belongs to one platform, such as the pen that traces a ship's outline, the scope's points, or the frame's time budget.

One Network wires the game's Processors and the presentation's. Remove every presentation Processor and every run of one, and the game's Records are the same at every step. A new platform supplies its own presentation Processors and Records, reads the same interface, and changes nothing in the game. The interface Records are the whole contract between the two. [Three kinds of Record](./NETWORK_TOPOLOGY.md#three-kinds-of-record) states the rules the loader enforces.

A Record's kind follows from what its values reach, not from what the code was written for. A value is the game's if any rule can observe it. Spacewar's central star draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the two draws are the game's, and only the line the star draws from them is presentation. A Processor that does both, as the original's code often does, splits in two. The game's half writes the value to an interface Record, and the presentation's half reads it.

A conversion checks its split by running the game with every presentation Processor removed against the original, as [Conversion process](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) states.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a field with no initial value, in an inbound boundary Record: the host writes it before a tick, and the top Network declares it under `requires:`. An outbound boundary Record is read after the tick and declared under `produces:` (CONTEXT.md, Boundary Record). Spacewar's `tick` requires `console, score, controls, outline_code, pause` and produces `display, scoreboard, lights, pause`. The loader lowers them to `reads:` and `writes:`, the inline form's keywords. On a routine, `requires:` is a precondition instead.
2. A value goes out to the presentation. It is an interface Record the game writes.
3. The machine computes something the rules then read, such as a sum that wraps or a collision a video chip latches. That computation is a rule, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes a rule or a value that comes in.

Only the third could widen the boundary, and a conversion always resolves it by moving the computation into the game. So the interface can grow in data, but it does not gain a new kind of thing.

## The declarations

A machine's **declarations** are the half of its package that never runs. They hold only choices that play cannot observe, such as where each routine and field lies, which register carries a value, how an enum is encoded in bits, and which device carries each value that comes in or goes out. They record the original programmer's arbitrary choices, never game logic, and a Port leaves them behind with that machine's presentation. Their count of entries only shrinks. [Declarations](./DECLARATIONS.md) is the reference. RUNS-Spacewar's PDP-1 declarations are `pdp1/`.

## The compiler

A compiler takes RUNS plus a target's declarations. Each target machine has its own compiler, and every game for that machine shares it. With the original machine's declarations, the original machine's compiler builds the original binary exactly. Running the game on another machine is a Port: new presentation Processors and Records, that machine's declarations, and that machine's compiler.

The compiler for a machine is general. It holds that machine's details, such as registers, addresses, scratch words, and the instructions that move a word, and no game's logic or timing, which live in the Network (CONTEXT.md, Compiler). A change to it is a general rule for the machine that a second program on that machine uses, never a fix to make one game's shape compile. The owner said on 2026-11-11 that "there should be no changes at all to the compiler... Everything should be in how the network is structured", meaning no bending it for one game, and called it "a general pdp1 compiler"; on 2026-11-14, "that's the job for the compiler to make sure that it runs on the PDP-1". When a pure shape does not compile to the original binary, the RUNS source changes first, then the compiler gains a general rule, as [Where a change goes](./DECLARATIONS.md#where-a-change-goes) states.

In RUNS-Spacewar, `tools/runsc.py` compiles the RUNS source and the PDP-1 declarations to the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` compiles that C to a tape image. The image's sha256 is the original's, `8744e9c9c8540cc5075c5cbb91c56745a4305fdf8e7afca43bea2e9e04ca4bdf`.

RUNS-Spacewar checks the conversion these ways:

- **The evaluator against SIMH.** Each routine and Network runs in the evaluator and in SIMH from the same state, and the checks compare Records and points.
- **The image against the original.** `runsc` builds the image from RUNS and prints `identical to the original` when its hash is the original's.
- **The mutation gate.** `tools/check_compiled.py` mutates the RUNS source and the declarations, as [The mutation gate](./DECLARATIONS.md#the-mutation-gate) states.
- **The order is in the wires.** `tools/check_names.py` renames every transition of the network files and checks that the image stays the same.
- **The fields hold what the arcs write.** `tools/check_fields.py` checks the compiled RUNS against what each arc writes, after each firing.
- **A second program.** The same compiler builds Minskytron's image from its RUNS source, and `tools/check_minskytron.py` checks its points.

`tools/check_all.sh` runs them all.

## Relationship to other EGS protocols

RUNS is a protocol on its own.

- **MAPS** is a separate protocol. How it relates to RUNS is open.
- **AEMS** is a separate protocol for assets and things. A game's assets belong there. Spacewar's ship outlines and star catalog are data on the tape, so the conversion keeps them in the RUNS source as Records. RUNS defines no way to read AEMS data.
- **RUNS Library** is a separate repository that predates this spec and differs from it. Where they differ, this spec governs.

## Check the examples

Every `runs` and `runs-prim` example in these documents loads and runs in RUNS-Spacewar's evaluator, and every `-rejected` block fails with the error its first line quotes. The examples' machine is the PDP-1, and they omit the `machine pdp1` line, because that evaluator holds the [PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) in code. Blocks tagged `runs-machine`, `net`, and `text` are not run. Every accepted example gives each Record and stream a kind, so the loader checks it for purity. `tools/check_examples.py` states what it checks in its docstring.

Run it from this repository, with the RUNS-Spacewar checkout beside it. It passes when it prints only `ok` lines and exits 0:

```sh
python3 tools/check_examples.py . ../runs-spacewar
```

## Open questions

- **The kind of each Record.** A conversion decides each kind by hand, from what the Record's values reach. A tool could trace each value through the original in SIMH instead.
- **What a halt means for unordered transitions.** What `stop` means for transitions the wiring leaves unordered is not settled. (The loop rule itself is settled, [The Network loop](./NETWORK_TOPOLOGY.md#the-network-loop); reading a counter loop outside a loop bundle is tool work still to do.)
- **How fine to cut Processors, and the shape of bundles.** How small a Processor should be, and how bundles of bundles are cut and named, is not settled. Decomposition is convention, not compliance (CONTEXT.md, Processor).
- **A bundle that names no game's Record.** RUNS-Spacewar's bundles still list Record fields as places, such as `cosine_work.shifted` and `pause.phase`, so none can be shared with another game yet. How a bundle holds a value between two of its transitions without naming a game's Record is not settled.
- **The order of the conversion process.** Which order turns an original program into coherent groupings of rules best, and how to automate it, is not settled. [Conversion process](./CONVERSION_PROCESS.md#the-route) states the route and the owner's stated wish.
- **What done means.** A purity count of 0 is necessary. What else a finished conversion requires is not settled.
- **Recursion.** A routine that keeps values across a call to itself needs a copy of them per depth. One field cannot hold them. Spacewar does not recurse.
- **What counts as the machine.** Which revision of a machine, and where its specified behavior ends and physical fault begins, is a judgment made once per machine in its description ([Machine description](./MACHINE_DESCRIPTION.md#what-counts-as-the-machine)). The form a description states it in is not settled, and the PDP-1 description does not state it yet.
- **A presentation effect that ends the program.** DOOM's visplane-overflow crash only flows out, so it is presentation, and the reference keeps it. It also ends the program, which stops the rules. How RUNS states that is not settled.
- **The form of an exit point, and the check that honors it.** An exclusion states the state and the step where play leaves the edition. RUNS has no form for it yet ([Network topology](./NETWORK_TOPOLOGY.md#halts-hangs-and-exit-points)). No tool yet runs the rules alone against the binary and allows differences only at the listed exclusions.
- **Naming and distribution.** How RUNS source is named, published, and shared, and what a shared library of Records and Processors holds.

**MIT License.** Open for implementation, extension, and critique.
