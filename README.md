# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Draft, developed against one conversion: [RUNS-Spacewar](https://github.com/wScottSh/RUNS-Spacewar) converts Spacewar! 3.1 to RUNS. Its evaluator, `tools/runs.py`, loads and runs every `runs` and `runs-prim` example in these documents.

RUNS is a plain-text form for a game's rules, so that the rules outlive the machine they were written for. Anyone can read, run, and change the source, and a runtime on another machine rebuilds it into the same game, because the source states the game's arithmetic, which is one of its rules.

RUNS applies the Linux model to game execution. There is no "RUNS engine," the way there is no single "Linux OS". Each game assembles its own engine from shared components into a standalone build, the way Android and the Steam Deck are different operating systems built around the same kernel and coreutils. An open-source engine removes the vendor but keeps the coupling, since the game is still written inside one engine's runtime. RUNS keeps the rules as source, apart from any engine.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) is the reference for Processors in `.runs-prim` files. It covers their declarations, statements, and expressions, why a Record holds no code, and the `word` type.
- [Network topology](./NETWORK_TOPOLOGY.md) is the reference for `.runs` and `.net` files. It covers types, enums, Records, streams, network files, Networks, top Networks, `wait`, and the contract rules the loader enforces.
- [Machine description](./MACHINE_DESCRIPTION.md) is the reference for `.runs-machine` files. It covers the original machine's types, literals, operators and their bodies in the core, address spaces, and stated layout. The PDP-1's description is its worked example.
- [Declarations](./DECLARATIONS.md) is the reference for a machine's declarations. It covers where a change goes, why the declarations only shrink, places, conventions, storage, encoding, code layout, events and devices, machine words, the host, and the mutation gate. The PDP-1 declarations are its worked example.
- [Conversion process](./CONVERSION_PROCESS.md) is how to convert a program on any machine to RUNS. It covers the toolkit a conversion builds, describing the machine, and the mapping of each routine, register, flag, interrupt, and device of the original to Records, Processors, and Networks. Spacewar is its worked example.

## What the work is for

A conversion makes the **reference** for a game: its original program rewritten into RUNS, with the game exactly the same ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Conversion). It is not a Port, which strips the presentation and puts in new presentation for another machine, and it is not a Variant, which changes the rules. The rules are pure and separate from the presentation, and the whole original presentation is still there. Compiled for the original machine, the reference is the original game. Run headless, its rules run alone on any machine. The reference is what goes into the archive untouched, and every later Port and Variant starts from it.

- **The rules are everything that changes what happens in the game.** That includes the arithmetic: Spacewar's 18-bit ones' complement is as much a rule as Yahtzee's six-sided die, and DOOM with floats would desync its demos and be a different game. It also includes the limits, and the order of steps wherever order changes a result. It includes what the original machine supplied deterministically, such as memory past the end of an array, because in a digital game the machine fills every gap in the rules. Intent is not the rules. A choice of the original machine that changes nothing, such as which register or address holds a value, belongs to the machine's declarations or its compiler, never to the RUNS. [Rule or machine: the one test](./CONVERSION_PROCESS.md#rule-or-machine-the-one-test) states the test and how to run it.
- **The oracle is the binary.** The RUNS source, compiled for the original machine, rebuilds the original binary exactly. Comparing play proves only the inputs tested. The identical binary proves every input, presentation included.
- **The process is the product.** The aim is a documented process that repeats for every game that has existed or will, on any machine, as automatable as possible: run it on DOOM and it gives logical groupings of the game's rules. A game born in RUNS follows the same specification from scratch. Spacewar is where the process is worked out, not its limit.
- **The groupings are what get shared.** Each grouping is a stateless bundle, named and described, made of smaller bundles down to atomic Processors (CONTEXT.md, Sub-Network). It takes values in and gives values out and names no Record. Anyone can find "Spacewar's gravity" on the commons, wire it into another game, and edit it in place. The edit makes it theirs, and a different game. What is unique to a game is its wiring. A Processor that reads one game's Records can be used by no other game.

## A conversion is not a re-vibe

A re-vibe re-creates a game from an impression of it, and a re-vibe that is only "good enough" yields a Variant ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Port and Variant). A conversion completely rewrites an existing program into RUNS and keeps the game exactly the same. It reorganizes the program, not the game. It starts from the program's assembly, or from code lifted from it, and moves the program's rules into Records and Processors. At every step, the RUNS source plus the original machine's declarations rebuilds the original binary, so the binary checks the behavior while the conversion changes the structure.

## What RUNS requires

1. **The rules are complete, so the game is exact.** Every sequence of inputs from power-on gives the same game as the original. The RUNS source states the rules completely, including what the original machine supplied deterministically, such as its arithmetic. Glitches are not rules. They are gameplay that emerges from the rules, so a conversion neither recreates nor removes them, and they emerge from the RUNS source as they did from the original. A re-release of Super Mario 64 whose rules capped Mario's backward speed would lose the backwards long jump and would not be Super Mario 64. [The rules are complete, and glitches emerge from them](#the-rules-are-complete-and-glitches-emerge-from-them) says why. A conversion does not change the game to fit RUNS. Where RUNS cannot say what a game does, RUNS grows.
2. **The source is the game.** DIGS guarantees every Processor's body is pure, total, and deterministic (CONTEXT.md, DIGS), so a faithful runtime gives the same results under any evaluation order. The same results on another machine come from the game's own numeric types, which the source states as rules (CONTEXT.md, DIGS). Every RUNS game states its arithmetic, its number types and their operations, whether it is a conversion or born in RUNS, because the arithmetic is a rule of the game; another arithmetic is another game (CONTEXT.md, DIGS). RUNS-Spacewar defines its `word` type, 18 bits in ones' complement. The Network can still hang, as a game can (CONTEXT.md, Network). Nothing about the game lives only in a binary.
3. **Every rule can be swapped.** A rule is replaceable only if its whole contract is visible. A Processor's contract is its inputs and outputs, and nothing else. It names no Record, and the Network wires each input and output to one place, a field or a whole Record: Records and Processors are mutually opaque, and only the Network knows both sides (CONTEXT.md, Processor and Network). Two Processors with the same inputs and outputs can be swapped, down to the smallest one. A register left set, a scratch word the source never names, or a patched instruction would be a hidden channel. That is why all data flows through fields the Network names.
4. **The Network is the net.** A Network is the game's colored Petri net, with Records as places, field values as tokens, Processors as transitions, and guarded arcs as gates (CONTEXT.md, Network). It is the explicit wiring of Record fields to Processors' inputs and outputs, and its wires and guards state the order in which rules fire (CONTEXT.md, Network). The conditions under which rules fire are guards on arcs. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own. A tangle in the drawing is coupling in the code. Spacewar's source writes each Network as a network file, a list of places, transitions, and arcs, with no separate list of steps, as [Where the order comes from](#where-the-order-comes-from) says.
5. **Variation is native.** A house rule is a Variant: an edit to one Processor or one wire of the Network, not a modified copy of a program (CONTEXT.md, Variant).
6. **The source is pure.** Every interaction is a Record or a stateless Processor. Nothing else holds logic or values.
7. **The presentation is separable.** The presentation can be removed and replaced whole without touching a game Record. This is the enduring-games pattern of a Rules region and a Realization region joined by boundary Records. It is a convention, not a base primitive of RUNS (CONTEXT.md, Processor), and RUNS-Spacewar holds itself to it.

## Records, Processors, and Networks

RUNS has three parts.

- **A Record** is anything the game remembers, such as the object table, the random number, the frame's time budget, or the tunables. It is data and nothing else, a set of named fields with values. Global data is a Record like any other. A Record holds one set of fields, or a fixed number of each field. A field with no initial value is unknown until the game sets it or the world gives it. A **stream** is a Record that collects ordered output for a device, such as the points the display plots. A Record keeps its value until a Processor gives it a new one. Only a Processor changes a Record. It takes the value out, computes, and may put the result back in the same place or in another (CONTEXT.md, Record). A value that changes needs no new Record.
- **A Processor** is one rule, and it is stateless. It names no Record. It declares inputs and outputs, each `in`, `out` or `inout`, with the kind of value it carries, and takes and gives values only through them. A Rules Processor's body, written in DIGS (Deterministic Inspectable Game Syntax), computes with locals, and no local outlives the firing. What a Processor does depends only on its inputs. A Realization Processor's body is not DIGS, and the standard names no language for it (CONTEXT.md, Processor). RUNS-Spacewar writes its presentation Processors in DIGS too, so its evaluator can run them.
- **A Network** is the explicit bipartite wiring of Records to Processors. Each wire is one line from a Record field to a Processor's input or output, and the wires and guards state the order of execution (CONTEXT.md, Network). A Network writes nothing and computes nothing. A Network used as a Processor from outside is a Sub-Network, with typed inputs and outputs at its boundary. There is no privileged sub-network entity, only regions of one graph at different zoom levels (CONTEXT.md, Network and Sub-Network). Spacewar's source writes each Network as a network file, a `.net` file that lists its places, its transitions, and its arcs, with no separate list of steps. A Network that another uses as a transition is a **bundle**. It declares inputs and outputs as a Processor does, so it is collapsed as one transition and expanded as its own file. A **loop bundle** fires its transitions once a pass, through a counter set before the loop starts. A guard only tests values that places hold, and values pass only through wires. [Network files](./NETWORK_TOPOLOGY.md#network-files) defines the format. The loader lowers each network file to a Network in the inline form, which states its order line by line, and the evaluator runs that.

The game runs as a sequence of ticks. A top Network fires once a tick and runs to its end. Nothing computes between ticks. Whatever the original computed between two steps is a transition in the Network, wired so that it fires in its turn.

In RUNS-Spacewar every Record is one of three kinds: a **game** Record, an **interface** Record, or a **presentation** Record. `game` marks a Rules-region Record, `presentation` a Realization-region one, and `interface` a boundary Record. [Three kinds of Record](#three-kinds-of-record) states the rules.

The topology is a Petri net. Records are the places and Processors are the transitions. No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record field that the Network names. A Processor never calls another Processor. Processors connect only through the Network, by way of Records, and composition is bundling: a bundle is its own network file (CONTEXT.md, Network). A body may compute with locals, which never leave it. RUNS-Spacewar's DIGS has no Processor call. Its only calls are the operators of the [machine description](./MACHINE_DESCRIPTION.md), such as the PDP-1's `rcl`, `scr`, and `popcount`, and the constructors of the original machine's instructions.

Records are organized by meaning, not by where the original kept a value. [Conversion process](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) maps each routine, macro, and register of an original program to Records, Processors, and Networks.

One tick of the Rules region is a DAG of firings, and any topological order of it yields identical results (CONTEXT.md, Network). Transitions that share no place may fire in parallel. Where two touch one place, the wires and guards make one wait for the other, and the loader refuses two writers that the wiring leaves unordered. RUNS-Spacewar's evaluator fires one transition at a time, in an order it reads from the wires and guards, and each Processor sees everything earlier ones wrote. Several of Spacewar's Processors write one Record, so the order between them is part of the game, and the wiring states it, as [Where the order comes from](#where-the-order-comes-from) says.

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

The source has no separate list of steps: the wires and guards state the order. A Network is the explicit wiring of Records to Processors (CONTEXT.md, Network). Two rules make the wiring state the whole order within the Rules region: every change goes through a Processor, and guards partition. Under the first rule, the wires and guards order any two Processors that touch one place, so the random number's values, `prng_v0` to `prng_vN`, pass through one place in wired order (CONTEXT.md, Network). Given both, one tick is a DAG, and any topological order yields identical results (CONTEXT.md, Network). `phases:` and `order:` are a crutch for resources that should be threaded (CONTEXT.md, Network and Phase / Dispatch / Guard). The only unbounded loop is the tick feedback through `state:` Records, in the wiring (CONTEXT.md, Network).

Spacewar's source has no separate list of steps either. Each Network is a network file of places, transitions, and arcs ([Network files](./NETWORK_TOPOLOGY.md#network-files)). The loader reads the order from the wires and guards alone. Shuffling the lines of a network file leaves the lowered program the same.

Two Processors may write the same Record. `collision` and each object's calc routine both write the object table, and changing their order changes 294 of 300 test frames. In `runs/frame/active_object.net`, the collisions give the table to the place `collided`, and `calc` takes it from there, so the collisions come first. The loader refuses two writers of one place that the wiring leaves unordered.

Spacewar writes each loop of a Network as a loop bundle. Its cycle runs through a counter set before the loop starts. Each pass takes one token, and the loop ends when the counter reaches 0 or a guard stops it (CONTEXT.md, Network). Its user sees one transition.

Two more rules of the source:

- **A guard only tests.** It compares values that Records hold, with each other or with constants, and joins comparisons with `and`, `or` and `not`. It computes nothing on a value. A condition that needs arithmetic is a Processor that computes it into a Record, and the guard tests that Record. Spacewar's breakout test, `(random.number | 0400000) + ships.uncertainty[slot] >= 0`, is the Processor `weigh_breakout`, which writes `breakout_check.margin`, and the guard `breakout_check.margin >= 0`. The image is unchanged. The compiler keeps the margin in AC, where the original kept it, because no declaration gives `breakout_check` a word.
- **Values pass only through wires.** Each arc names the one place an input or output takes. A Network may take a slot, `network calc(slot)`, and pass it on, `first: first_spaceship(slot)`. The slot chooses which entry of a collection an arc names, as the original's pointers gave each routine "this object".

The guards on one place partition: exactly one is true, and an open-typed value has an explicit `when else` (CONTEXT.md, Phase / Dispatch / Guard). The inline form, which the loader lowers network files to, lets `if` fire its first true arm and omit `else`. RUNS source does not use it.

The loader reports a guard that computes and a `run` that passes a value as impurities and refuses them.

## The rules are complete, and glitches emerge from them

In a digital game the machine fills every gap in the rules. A board game leaves its gaps to the players. A digital game's gaps get the machine's answer, the same every time, in every state, for every input. So a digital game's rules are complete whether anyone meant them or not: they are the original program running on its original machine. The designer's intent is never complete. **Intent is not the rules**, and intent is not what the reference archives. The source code is not the rules either. C leaves an out-of-bounds read, a use after free, and an uninitialized read undefined. The compiler and the CPU decide them, and the binary records what they decided. That is one reason the oracle is the binary.

The rules are the boundary of the game's possibility space: every state reachable from power-on by any sequence of inputs, and how each state moves to the next. Gameplay is the paths players take inside that space, glitches included. Gameplay emerges from the rules. The rules are not gameplay. "Intended" and "unintended" describe the designer's map of the space, not the space. Super Mario 64's backwards long jump is gameplay that emerges from its rules: Mario's backward speed has no cap. A glitchless speedrun category is a rule the players add on top, and the game is unchanged. Removing a glitch from the game itself means writing a different rule into the gap, and that makes a different game, a Variant ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Variant).

The boundary is not always clear, for three reasons:

- The reachable space cannot be listed in general, so glitches are found after the fact. Ocarina of Time's stale reference manipulation was found in late 2019, 21 years after release. Super Mario 64's Tick Tock Clock upwarp is still unexplained.
- Anything a player can observe, someone will depend on (Hyrum's law). Speedrunners and demo authors do.
- The program and the machine were one system. The line between "game" and "machine" is drawn afterward.

So a conversion neither recreates glitches nor removes them. It states the rules completely, including what the original machine supplied deterministically. The glitches then emerge by themselves on any machine that runs those rules, including glitches nobody has found yet. Glitches cannot be listed, so a conversion's completeness is judged on its rules, never against a list of glitches.

### Sort a behavior by its cause

When the machine changes, sort each behavior by where its cause sits, never by whether it was intended.

1. **Machine behavior the program reaches deterministically is a rule.** This covers the arithmetic, memory past the end of an array, data run as code, and timing the program itself produces. Spacewar's 18-bit ones' complement is one. Its toroidal wrap is defined nowhere: it falls out of the coordinate arithmetic, and the game is not Spacewar without it. Space Invaders moves one invader per video interrupt, because the machine could not move them all in one frame, so the fewer are left, the more often each one moves. No line of the program says "speed up". The difficulty curve was found by accident and kept because it made a better game. It is not lag: every tick does the same work, so the curve emerges from the rule on any machine. The RUNS source states these rules. A machine that drops them is not running the same rules. DOOM shows what that costs: Boom fixed vanilla DOOM's overflows and broke vanilla demos, PrBoom added compatibility levels, and Chocolate Doom emulates the `spechit`, reject, and intercepts overflows to keep vanilla demos in sync.
2. **What comes in from outside the game is an input, not a rule.** This covers player input, outside clocks, physical faults such as a flipped bit, the contents of memory at power-on, and differences between console revisions. The same rules with different inputs take different paths. A glitch that only such an input opens can be absent while the rules stay the same and the conversion stays exact.
3. **An effect that lands only in the presentation** belongs to the presentation, such as DOOM's visplane-overflow crash. The reference keeps it, with the whole original presentation. A Port changes it by definition ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), Port).

A Port keeps every case 1 rule, changes case 3, and keeps case 2 as far as its inputs are the same. For a game born in RUNS, the RUNS semantics are the machine: whatever RUNS defines in its own gaps is that game's case 1.

Time is why the RUNS source has to state case 1. The original binary carries every glitch only while a faithful machine exists to run it. Hardware dies, and emulators differ: some Ocarina of Time tricks work on the Wii Virtual Console and crash a real N64, and TASVideos rejects them for N64 runs. Speedrunners and demo authors already treat the machine as part of the game, and leaderboards split by version and platform. Over a thousand years, the RUNS source is the only lasting statement of the rules.

How RUNS draws the lines inside these cases is open, as [Open questions](#open-questions) states.

### Spacewar's rules and the machine

Spacewar's own logic has a glitch that emerges from its rules. The previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed. The conversion states the rule as the program has it, and the glitch emerges.

The [machine description](./MACHINE_DESCRIPTION.md) holds the case 1 rules every game on a machine shares. It supplies RUNS's types and every operator on them. For Spacewar, that is the `word`, the game's number. That a word is 18 bits in ones' complement is a rule of Spacewar, and the source states it exactly, in the description's operator bodies that [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes. Where the program reads memory past an array, the layout is part of the complete rules: the RUNS source states it, and the description's address spaces carry it. Where the program runs data as code or jumps into the middle of a routine, the rule is what the machine does with those bytes on that path. The RUNS source states that rule in a Processor, as it states any other, and a general compiler for the machine reproduces the bytes in the binary. RUNS itself never keeps instructions in a Record to run them. The rest of the game is RUNS.

A halt or a hang that the original reaches is part of the rules, not an error. Spacewar halts when a ship fires and the object table is full, and the conversion writes `stop`. Spacewar also halts between games to show the scores. The conversion emits the scores and ends the tick there, and the `pause` Record makes the next tick the operator's answer. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the RUNS source is wrong.

A conversion measures which machine behavior the program reaches, so that the RUNS source states every case 1 rule and nothing the program never reaches, as [Conversion process](./CONVERSION_PROCESS.md#6-measure-where-play-reaches-the-machine) states. RUNS-Spacewar measures it with `tools/reach_oracle.py`, which runs scripted matches of the original in SIMH. Its findings for Spacewar are these:

- The rules reach no layout past an array. The main loop reads past the ships' two-word outline array for every torpedo slot, but only the ships' own slots use the word it loads. A check that poisons that word for every other slot still matches the original, so that layout is not part of the rules, and the image's layout carries the read.
- The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. They are inputs (case 2). Those words are fields with no initial value, and they come in at the game's boundary.
- The game writes code and runs it. At each new game, Spacewar's outline compiler writes each ship's outline as PDP-1 instructions, and each frame the spaceship jumps into them to draw the ship. The outlines are presentation. RUNS-Spacewar states what the outline code draws: the outline compiler decodes each outline into strokes (`outline_code`), and `draw_outline` walks them. The compiler reproduces the instructions.
- Everywhere else, the program reaches only the `word` type's own arithmetic, such as sums that wrap and shifts of negative numbers.

## Three kinds of Record

Presentation is the screen, the sound, the controls, the pacing, and the machine underneath. It is rebuilt for each platform, and the game is not, so the presentation has to come out whole with no change to a rule. In RUNS-Spacewar every Record is one of three kinds, and each kind says which Processors may touch it. The kinds are the enduring-games pattern: a Rules region and a Realization region joined only by boundary Records (CONTEXT.md, Processor). That pattern is a convention, not a base primitive of RUNS (CONTEXT.md, Processor). RUNS-Spacewar's loader enforces it as this project's own rule.

- **A game Record** holds what only the rules use, such as Spacewar's fuel, the random number, or a ship's angular momentum.
- **An interface Record** holds what the game and its presentation share. The game writes what there is to show, such as each object's position and heading. The world writes what comes in, such as the controls and the switches.
- **A presentation Record** belongs to one platform, such as the pen that traces a ship's outline, the scope's points, or the frame's time budget.

A Processor that touches a presentation Record is part of the presentation. Every other Processor is part of the game. Every stream leaves to a device, so every stream is presentation, and a Processor that emits to one is presentation too. A presentation Processor touches no game Record and writes no interface Record, and a guard that reads a presentation Record guards only the presentation. [Three kinds of Record](./NETWORK_TOPOLOGY.md#three-kinds-of-record) states the rules as the loader enforces them.

One Network wires both kinds of Processor. Remove every presentation Processor and every run of one, and what is left is the game. The rules make its Records the same with the presentation or without it. A new platform supplies its own presentation Processors and Records, reads the same interface, and changes nothing in the game. The interface Records are the whole contract between the two.

A Record's kind follows from what its values reach, not from what the code was written for. A value is the game's if any rule can observe it. Spacewar's central star draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the two draws are the game's, and only the line the star draws from them is presentation. A Processor that does both, as the original's code often does, splits in two. The game's half writes the value to an interface Record, and the presentation's half reads it.

A conversion checks its split by running the game with every presentation Processor removed against the original, as [Conversion process](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) states.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a field with no initial value, in an inbound boundary Record: the host writes it before a tick, and the top Network declares it under `requires:`. An outbound boundary Record is read after the tick and declared under `produces:` (CONTEXT.md, Boundary Record). Spacewar's `tick` requires `console, score, controls, outline_code, pause` and produces `display, scoreboard, lights, pause`. The loader lowers them to `reads:` and `writes:`, the inline form's keywords. On a routine, `requires:` is a precondition instead.
2. A value goes out to the presentation. It is an interface Record the game writes.
3. The machine computes something the rules then read, such as a sum that wraps or a collision a video chip latches. That computation is a rule, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes a rule or a value that comes in.

Only the third could widen the boundary, and a conversion always resolves it by moving the computation into the game. So the interface can grow in data, but it does not gain a new kind of thing.

## The declarations

A machine's **declarations** are the half of its package that never runs. They hold only choices that play cannot observe, such as where each routine and field lies, which register carries a value, how an enum is encoded in bits, and which device carries each value that comes in or goes out. They record the original programmer's arbitrary choices, never game logic, and a port leaves them behind with that machine's presentation. They are not a place to make hard RUNS source compile, and their count of entries only shrinks. [Declarations](./DECLARATIONS.md) states every section they have, where a change goes, what the compiler refuses, how the host fires a game, and the mutation gate. RUNS-Spacewar's PDP-1 declarations are `pdp1/`, and `pdp1/README.md` there defines their full vocabulary.

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

Every `runs` and `runs-prim` example in these documents loads and runs in RUNS-Spacewar's evaluator. The examples' machine is the PDP-1, and they omit the `machine pdp1` line, because that evaluator holds the [PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) in code and reads no `machine` line. Blocks tagged `runs-machine`, `net`, and `text` are not run. Every accepted example gives each Record and stream a kind, so the loader checks it for purity. `tools/check_examples.py` checks this. It parses each accepted example alone, then loads all of a document's accepted examples as one program, wires each `run`, runs `runs.check`, and runs each top Network six passes. A block alone is not wired, because its runs may wire routines that another block declares. It confirms that each rejected example fails with the error its first line quotes. It also fails on an em dash or an en dash in the documents.

To run the check, put the RUNS-Spacewar checkout beside this repository and pass both directories, from this repository:

```sh
python3 tools/check_examples.py . ../runs-spacewar
```

The general form is:

```sh
python3 tools/check_examples.py <runs-spec dir> <RUNS-Spacewar dir>
```

The command exits with status 0 when every example passes.

## Open questions

- **The kind of each Record.** A conversion decides each kind by hand, from what the Record's values reach. A tool could trace each value through the original in SIMH instead.
- **Loops and halts in the graph.** Every loop within a tick runs through a counter and need not sit in a bundle (owner, 2026-11-14); RUNS-Spacewar's loader reads a loop only as a loop bundle (a network file with a `counter` line), so every loop in its source is one; reading a counter loop anywhere in a graph is tool work still to do. Neither is what a halt (`stop`) means for transitions the wiring leaves unordered.
- **How fine to cut Processors, and the shape of bundles.** How small a Processor should be, and how bundles of bundles are cut and named, is not settled. Decomposition is convention, not compliance (CONTEXT.md, Processor).
- **A bundle that names no game's Record.** RUNS-Spacewar's bundles still list Record fields as places, such as `cosine_work.shifted` and `pause.phase`, so none can be shared with another game yet. How a bundle holds a value between two of its transitions without naming a game's Record is not settled.
- **The order of the conversion process.** Which order turns an original program into coherent groupings of rules best, and how to automate it, is not settled. [Conversion process](./CONVERSION_PROCESS.md#the-route) states the route and the owner's stated wish.
- **What done means.** A purity count of 0 is necessary. What else a finished conversion requires is not settled.
- **Recursion.** A routine that keeps values across a call to itself needs a copy of them per depth. One field cannot hold them. Spacewar does not recurse.
- **How RUNS operationalizes the cause-based sort.** The owner holds that RUNS must distinguish machine behavior that is part of the design (Space Invaders' kept speed-up, Spacewar's wrap) from emergent design gaps on complex hardware (such as arbitrary code execution), and does not yet know how RUNS should make that distinction (2026-11-15). Also open: lag from drawing load that feeds the rules; hardware faults against consistent hardware behavior; which machine revision counts; and a read past an array whose reach cannot be decided. [The rules are complete, and glitches emerge from them](#the-rules-are-complete-and-glitches-emerge-from-them) states the principle these questions apply.
- **Naming and distribution.** How RUNS source is named, published, and shared, and what a shared library of Records and Processors holds.

**MIT License.** Open for implementation, extension, and critique.
