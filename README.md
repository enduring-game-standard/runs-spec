# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Draft, developed against one conversion: [RUNS-Spacewar](https://github.com/wScottSh/RUNS-Spacewar) converts Spacewar! 3.1 to RUNS. Its evaluator, `tools/runs.py`, loads and runs every `runs` and `runs-prim` example in these documents.

RUNS is a plain-text form for a game's logic, so that the Game Logic outlives the machine it was written for. Anyone can read, run, and change the source, and a runtime on another machine rebuilds it into the same game, because the source states the game's arithmetic, which is part of its Game Logic.

RUNS applies the Linux model to game execution. There is no "RUNS engine," the way there is no single "Linux OS". Each game assembles its own engine from shared components into a standalone build, the way Android and the Steam Deck are different operating systems built around the same kernel and coreutils. An open-source engine removes the vendor but keeps the coupling, since the game is still written inside one engine's runtime. RUNS keeps the Game Logic as source, apart from any engine.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md): read before you write a Processor body (`.runs-prim`). Statements, expressions, the `word`, and why a Record holds no code.
- [Network topology](./NETWORK_TOPOLOGY.md): read before you write Records, streams, or a Network (`.runs`, `.net`). Network files, Guards, order, loops, halts, contracts, and every loader error.
- [Machine description](./MACHINE_DESCRIPTION.md): read before you state a machine's arithmetic (`.runs-machine`) or a layout play reads. Types, literals, operators, the core, address spaces. Worked example: the PDP-1.
- [Declarations](./DECLARATIONS.md): read before you change a machine's Declarations or its compiler, or when a pure shape will not compile. Where a change goes, the seven sections, compiler checks, the mutation gate, the host. Worked example: the PDP-1.
- [Conversion Process](./CONVERSION_PROCESS.md): read before you convert an existing program. The route, the toolkit, the game-logic-or-machine test, the nine steps from describing the machine to the archive. Worked example: Spacewar.

## What the work is for

A Conversion makes the **reference** for a game: its original program rewritten into RUNS, with the game exactly the same ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Conversion). It is not a Game Port, which strips the Presentation and puts in new Presentation for another machine, and it is not a Variant, which changes the Game Logic. The Game Logic is pure and separate from the Presentation, and the whole original Presentation is still there. Compiled for the original machine, the reference is the original game. Run headless, its Game Logic runs alone on any machine. The reference is what goes into the archive untouched, and every later Game Port and Variant starts from it.

- **The Game Logic is everything that changes what happens in the game.** That includes the arithmetic: Spacewar's 18-bit ones' complement is as much part of the game as Yahtzee's six-sided die, and DOOM with floats would desync its demos and be a different game. It also includes the limits, and the order of steps wherever order changes a result. It includes how the program's own operations behave on the original machine, such as reading memory past the end of an array: the program did it, so it is part of the game. Intent is not the Game Logic. A choice of the original machine that changes nothing, such as which register or address holds a value, belongs to the machine's Declarations or its compiler, never to the RUNS. [Game Logic or machine: the one test](./CONVERSION_PROCESS.md#game-logic-or-machine-the-one-test) states the test and how to run it.
- **The oracle is the binary.** The RUNS source, compiled for the original machine, rebuilds the original binary exactly. Comparing play proves only the inputs tested. The identical binary proves every input, Presentation included.
- **The binary is the original** (GLOSSARY.md, Original). The archive identifies the Original by its hash and keeps the source and toolchain that rebuild it. The RUNS source carries everything the program does by default. Code the program never contained is the machine's. [The binary is the Original](#the-binary-is-the-original) states the three points.
- **The process is the product.** The aim is a documented process that repeats for every game that has existed or will, on any machine, as automatable as possible: run it on DOOM and it gives logical groupings of the Game Logic. A game born in RUNS follows the same specification from scratch. Spacewar is where the process is worked out, not its limit.
- **The groupings are what get shared.** Each grouping is a Sub-Network, named and described, made of smaller Sub-Networks down to single Processors, holding the Records it owns (GLOSSARY.md, Sub-Network). Published, it is a Bundle (GLOSSARY.md, Bundle). Anyone can find "Spacewar's gravity" on the commons and wire the Records at its edge to Records of their own game. Editing any part makes a new part with a new hash. What is unique to a game is its wiring.

## A Conversion is not a re-vibe

A re-vibe re-creates a game from an impression of it, and a re-vibe that is only "good enough" yields a Variant ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Game Port and Variant). A Conversion completely rewrites an existing program into RUNS and keeps the game exactly the same. It reorganizes the program, not the game. It starts from the program's assembly, or from code lifted from it, and moves the program's Game Logic into Records and Processors. At every step, the RUNS source plus the original machine's Declarations rebuilds the original binary, so the binary checks the behavior while the conversion changes the structure.

## What RUNS requires

1. **The Game Logic is complete, so the game is exact.** Every sequence of inputs from power-on gives the same game as the Original. The RUNS source states the Game Logic completely, including how the program's own operations behave on the original machine, and the original's Glitches emerge from it. The RUNS source carries everything the program does by default. [The Game Logic is complete, and Glitches emerge from it](#the-game-logic-is-complete-and-glitches-emerge-from-it) says why. RUNS fits the game, never the reverse: where RUNS cannot say what a game does, RUNS grows.
2. **The source is the game.** DIGS guarantees every Processor's body is pure, total, and deterministic, so a faithful runtime gives the same results under any evaluation order (GLOSSARY.md, DIGS). Every RUNS game, converted or born in RUNS, states its arithmetic: its number types and their operations. The arithmetic is Game Logic, and another arithmetic is another game. RUNS-Spacewar's `word` is 18 bits in ones' complement. The Network can still hang, as a game can (GLOSSARY.md, Network). Nothing about the game lives only in a binary.
3. **Every Processor can be swapped.** A Processor's contract is its inputs and outputs, and nothing else. It names no Record, and the Network wires each input and output to one place, a Field or a whole Record. Records and Processors are mutually opaque, and only the Network knows both sides (GLOSSARY.md, Processor and Network). Two Processors with the same inputs and outputs can be swapped, down to the smallest one. All data flows through Fields the Network names, so a register left set, an unnamed scratch word, or a patched instruction has no channel to hide in.
4. **The Network is the net.** A Network is the game's colored Petri net, with Records as places, Field values as tokens, Processors as transitions, and guarded arcs as gates (GLOSSARY.md, Network). Its wires and Guards state when and in what order Processors fire. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own, so a tangle in the drawing is coupling in the code. [Where the order comes from](#where-the-order-comes-from) says how.
5. **Variation is native.** A change to the Game Logic is a Variant: an edit to one Processor or one wire of the Network, not a modified copy of a program (GLOSSARY.md, Variant).
6. **The source is pure.** Every interaction is a Record or a stateless Processor. Nothing else holds logic or values.
7. **The Presentation is separable.** The Presentation can be removed and replaced whole without touching a game Record. This is the enduring-games pattern of Game Logic and Presentation joined by Interface Records. It is a convention, not a base primitive of RUNS (GLOSSARY.md, Processor), and RUNS-Spacewar holds itself to it.

## Records, Processors, and Networks

RUNS has three parts.

- **A Record** is anything the game remembers, such as the object table, the random number, the frame's time budget, or the tunables. It is data and nothing else, a set of named Fields with values. Global data is a Record like any other. A Record holds one set of Fields, or a fixed number of each Field. A Field with no initial value is unknown until the game sets it or the world gives it. A **stream** is a Record that collects ordered output for a device, such as the points the display plots. A Record keeps its value until a Processor gives it a new one. Only a Processor changes a Record. It takes the value out, computes, and may put the result back in the same place or in another (GLOSSARY.md, Record). A value that changes needs no new Record.
- **A Processor** computes its outputs from its inputs, and it is stateless. It names no Record. It declares inputs and outputs, each `in`, `out` or `inout`, with the kind of value it carries, and takes and gives values only through them. A Game Logic Processor's body, written in DIGS (Deterministic Inspectable Game Syntax), computes with locals, and no local outlives the firing. What a Processor does depends only on its inputs. A Presentation Processor's body is not DIGS, and the standard names no language for it (GLOSSARY.md, Processor). RUNS-Spacewar writes its Presentation Processors in DIGS too, so its evaluator can run them.
- **A Network** is the explicit bipartite wiring of Records to Processors. Each wire is one line from a Record Field to a Processor's input or output, and the wires and Guards state the order of execution (GLOSSARY.md, Network). A Network writes nothing and computes nothing. A Network inside another is a Sub-Network: it holds its own Records and Processors, and shares a Record with the Network around it only where Processors on both sides touch it (GLOSSARY.md, Sub-Network). RUNS source writes each Network as a Network file, a `.net` file that lists its places, its transitions, and its arcs, with no separate list of steps. In a Network file a Sub-Network declares the Records it shares as inputs and outputs, as a Processor does, so it is collapsed as one transition and expanded as its own file. [Network files](./NETWORK_TOPOLOGY.md#network-files) defines the format. The loader lowers each Network file to a Network in the inline form, which states its order line by line, and the evaluator runs that.

The game runs as a sequence of ticks. A top Network fires once a tick and runs to its end. Nothing computes between ticks. Whatever the original computed between two steps is a transition in the Network, wired so that it fires in its turn.

In RUNS-Spacewar every Record is one of three kinds: a **game** Record, an **interface** Record, or a **Presentation** Record. `game` marks a Game Logic Record, `presentation` a Presentation one, and `interface` an Interface Record. [Three kinds of Record](#three-kinds-of-record) states the rules.

Each value one Processor hands to the next goes through a Record Field that the Network names. Processors connect only through the Network, by way of Records, and Networks compose by nesting Sub-Networks (GLOSSARY.md, Sub-Network). A Processor never calls another. A body computes with locals, which never leave it, and its only calls are the operators of the [machine description](./MACHINE_DESCRIPTION.md), such as the PDP-1's `rcl`, `scr`, and `popcount`.

Records are organized by meaning, not by where the original kept a value. [Conversion Process](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) maps each routine, macro, and register of an original program to Records, Processors, and Networks.

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

The example uses the inline form, so `tick` states its order line by line. As a Network file, `tick` would list its places, transitions, and arcs instead. `tick` is a top Network, because nothing fires it, so it is a whole game, and it is the one routine that names Records. Each Processor names only its inputs and outputs, and `tick` wires each one to one place, one wire a line. The button comes in through `reads: pad`, and the points leave through `writes: screen`. `draw_ball` takes the stream as an `inout` of the stream's kind and emits to it by that name. The ball's speed, and how far past the wall it is, are the game's own. `reach_wall` computes the distance into a Record, and the Guard only tests it. Its position is in the interface, because the game moves it and the Presentation shows it. `draw_ball` is the Presentation. To make a Variant where the ball stops instead of bouncing, replace `bounce` and change nothing else. To show the ball on another screen, replace `draw_ball` and `screen` and change nothing in the game.

## Where the order comes from

The source has no separate list of steps: the wires and Guards state the order. Two rules make the wiring state the whole order within the Game Logic: every change goes through a Processor, and the Guards on one place partition. Under the first, the wires and Guards order any two Processors that touch one place, so the random number's values, `prng_v0` to `prng_vN`, pass through one place in wired order. Given both, one tick of the Game Logic is a DAG of firings, and any topological order of it yields identical results (GLOSSARY.md, Network). Transitions that share no place may fire in parallel. Where two touch one place, the wires and Guards make one wait for the other. `phases:` and `order:` are a crutch for resources that should be threaded (GLOSSARY.md, Network).

The loader reads the order from the wires and Guards alone, so shuffling the lines of a Network file leaves the lowered program the same. RUNS-Spacewar's evaluator then fires one transition at a time in that order, and each Processor sees everything earlier ones wrote.

Two Processors may write the same Record. `collision` and each object's calc routine both write Spacewar's object table, and changing their order changes 294 of 300 test frames. In `runs/frame/active_object.net`, the collisions give the table to the place `collided`, and `calc` takes it from there, so the collisions come first. The loader refuses two writers of one place that the wiring leaves unordered.

A Guard only tests, and values pass only through wires. A condition that needs arithmetic is a Processor that computes it into a Record, and the Guard tests that Record. Spacewar's breakout test, `(random.number | 0400000) + ships.uncertainty[slot] >= 0`, is the Processor `weigh_breakout`, which writes `breakout_check.margin`, and the Guard `breakout_check.margin >= 0`. The image is unchanged: the compiler keeps the margin in AC, where the original kept it, because no declaration gives `breakout_check` a word. [Guards](./NETWORK_TOPOLOGY.md#guards) and [Order](./NETWORK_TOPOLOGY.md#order) state the rules the loader enforces, and [The Network loop](./NETWORK_TOPOLOGY.md#the-network-loop) states the rule for loops.

## The Game Logic is complete, and Glitches emerge from it

In a digital game the machine fills every gap in the Game Logic. A board game leaves its gaps to the players. A digital game's gaps get the machine's answer, the same every time, in every state, for every input. So a digital game's logic is complete whether anyone meant it or not: it is the original program running on its original machine. The designer's intent is never complete. **Intent is not the Game Logic**, and intent is not what the reference archives. The source code is not the Game Logic either. C leaves an out-of-bounds read, a use after free, and an uninitialized read undefined. The compiler and the CPU decide them, and the binary records what they decided. That is one reason the oracle is the binary.

The Game Logic is the boundary of the game's possibility space: every state reachable from power-on by any sequence of inputs, and how each state moves to the next. Gameplay is the paths players take inside that space, Glitches included. Gameplay emerges from the Game Logic. The Game Logic is not gameplay. "Intended" and "unintended" describe the designer's map of the space, not the space. Super Mario 64's backwards long jump is gameplay that emerges from its Game Logic: Mario's backward speed has no cap. A glitchless speedrun category is a constraint the players add on top, and the game is unchanged. Removing a Glitch from the game itself means writing different Game Logic into the gap, and that makes a different game, a Variant ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Variant).

The boundary is not always clear, for three reasons:

- The reachable space cannot be listed in general, so Glitches are found after the fact. Ocarina of Time's stale reference manipulation was found in late 2019, 21 years after release. Super Mario 64's Tick Tock Clock upwarp is still unexplained.
- Anything a player can observe, someone will depend on (Hyrum's law). Speedrunners and demo authors do.
- The program and the machine were one system. The line between "game" and "machine" is drawn afterward.

So a Conversion neither recreates Glitches nor removes them. It states the Game Logic completely, including how the program's own operations behave on the original machine. The Glitches then emerge by themselves on any machine that runs that Game Logic, including Glitches nobody has found yet. Glitches cannot be listed, so a Conversion's completeness is judged on its Game Logic, never against a list of Glitches.

### Sort a behavior at the machine's edge

When the machine changes, sort each behavior by following its data across the edge of the original machine, never by whether it was intended. The edge is the one physical boundary the game has.

- **In** is whatever the program reads from a device, such as the controller, the switches, a clock, or a count of video frames, and memory the program never set, such as the contents of memory at power-on.
- **Out** is the screen and the speaker.
- **Inside the edge**, a value that only ever flows out is Presentation. Everything else is Game Logic, including how the program's own operations behave on the hardware: the arithmetic, memory past the end of an array, and code the program writes for itself. Code the program never contained, such as bytes the player writes and the machine then runs, is the machine's behavior, not Game Logic.

Spacewar's 18-bit ones' complement is Game Logic. Its toroidal wrap is defined nowhere: it falls out of the coordinate arithmetic, and the game is not Spacewar without it. The RUNS source states this Game Logic. A machine that drops it is not running the same game. DOOM shows what that costs: Boom fixed vanilla DOOM's overflows and broke vanilla demos, PrBoom added compatibility levels, and Chocolate Doom emulates the `spechit`, reject, and intercepts overflows to keep vanilla demos in sync.

Lag reaches the Game Logic, if it reaches it at all, as a clock reading, which is an input. On the original machine that input carries the lag. A Game Port feeds it different values, so the Game Logic is the same and the gameplay differs. "Better" and "worse" describe the gameplay, not the game: GoldenEye's lookdown, and Ocarina of Time on the N64 and on the Wii Virtual Console, which are one game with separate leaderboards. Space Invaders moves one invader per video interrupt, an input, by its Game Logic. No line of the program says "speed up": the fewer invaders are left, the more often each one moves. The curve was found by accident and kept because it made a better game. It is not lag. It emerges from the input and the Game Logic on any machine that feeds the same interrupts.

An effect that only flows out belongs to the Presentation, such as DOOM's visplane-overflow crash. The reference keeps it, with the whole original Presentation. A Game Port changes it by definition ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Game Port). That crash also ends the program, and so stops the Game Logic; how RUNS states a Presentation effect that ends the program is open, as [Open questions](#open-questions) states.

A Game Port keeps all the Game Logic, changes what only flows out, and feeds the Game Logic its own inputs. For a game born in RUNS, the RUNS semantics are the machine: whatever RUNS defines in its own gaps is that game's hardware behavior.

Time is why the RUNS source has to state the hardware's behavior. The original binary carries every Glitch only while a faithful machine exists to run it. Hardware dies, and emulators differ: some Ocarina of Time tricks work on the Wii Virtual Console and crash a real N64, and TASVideos rejects them for N64 runs. Speedrunners and demo authors already treat the machine as part of the game, and leaderboards split by version and platform. Over a thousand years, the RUNS source is the only lasting statement of the Game Logic.

What counts as the machine is still a judgment: which revision, and where specified behavior ends and physical fault begins. A flipped bit is a fault. A documented CPU quirk is behavior. It is made once per machine, in that machine's description ([Machine description](./MACHINE_DESCRIPTION.md#what-counts-as-the-machine)).

### The binary is the original

1. **The binary is the Original.** The reference archive identifies it by its hash and keeps the source and the toolchain that rebuild it; the rebuilt binary is verified against the hash. On the original machine it has everything, uninterpreted. A game's GitHub repo keeps the hash in place of the binary. Each shipped version is its own original: Ocarina of Time 1.0 keeps Glitches that later versions fixed. A game born in RUNS has no binary, and its RUNS source is the Original.
2. **The RUNS source carries everything the program does, by default.** Every behavior of the program is in the Game Logic. Glitches are never purged: removing one changes the Game Logic, and the result is a Variant.
3. **The check.** The Game Logic, run alone, matches the Original. Compiled for the original machine, the RUNS source still rebuilds the original binary, the oracle.

Code that runs splits in two ([ADR-0002](./docs/adr/0002-four-layers-and-the-machine-is-outside-runs.md)). Code the program writes for itself is Game Logic, and the RUNS source carries it like any other: Spacewar's outline code, which the program writes from its own tables, and a jump at the wrong entry into the program's own bytes. Code the program never contained, such as bytes the player writes and the machine then runs, is the machine's behavior. A Conversion does not carry it, and a build that cannot run it changes no Game Logic, so it is not a Variant. Super Mario World's source does not contain Flappy Bird, and its conversion does not either.

How the three worked games sort:

- **Spacewar.** Carried: the ones' complement arithmetic and so the wrap, the fire Glitch with sense switch 3 on, the halt when the object table is full, the central star's random draws, and the outline code the program writes for itself. The contents of core at power-on are an input. A player can give the program only switches and controls, never code. The reach oracle shows that play reaches only the word's own arithmetic, and the poison check shows the one read past an array unobserved.
- **DOOM.** Carried: 16.16 fixed point, the random table and its draw order, the limits, the order of thinkers, and the `spechit`, reject, and intercepts overflows, as stated layout where play reaches them, because vanilla demos depend on them. Wallrunning and strafe-running emerge. The visplane crash is Presentation, and the reference keeps it. Code the player gets the program to run is the machine's.
- **Ocarina of Time.** Carried: single-precision float modes, the random number generator, the update rate, the culling flag set while drawing, Z-targeting's screen test, and what stale reference manipulation writes into freed actor memory, so the RUNS source states the memory reuse. Lag is a clock input. The machine's: arbitrary code execution. From the step where control jumps into bytes the player chose, the machine runs code the program never contained.

### Spacewar's Game Logic and the machine

Spacewar's own logic has a Glitch that emerges from its Game Logic. The previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed. The conversion states the logic as the program has it, and the Glitch emerges.

The [machine description](./MACHINE_DESCRIPTION.md) holds the hardware behavior that every game on a machine shares. It supplies RUNS's types and every operator on them. For Spacewar, that is the `word`, the game's number. That a word is 18 bits in ones' complement is part of Spacewar's Game Logic, and the source states it exactly, in the description's operator bodies that [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes. Where the program reads memory past an array, the layout is part of the complete Game Logic: the RUNS source states it, and the description's address spaces carry it. Where the program runs code it fixed for itself or jumps into the middle of a routine, the Game Logic is what the machine does with those bytes on that path. The RUNS source states it in a Processor, as it states any other, and a general compiler for the machine reproduces the bytes in the binary. RUNS itself never keeps instructions in a Record to run them. The rest of the game is RUNS.

A halt or a hang that the original reaches is part of the Game Logic, not an error. Spacewar halts when a ship fires and the object table is full, and the conversion writes `stop`. Spacewar also halts between games to show the scores. The conversion emits the scores and ends the tick there, and the `pause` Record makes the next tick the operator's answer. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the RUNS source is wrong.

A conversion measures which machine behavior the program reaches, so that the RUNS source states every behavior the hardware supplies and nothing the program never reaches, as [Conversion Process](./CONVERSION_PROCESS.md#6-measure-where-play-reaches-the-machine) states. RUNS-Spacewar measures it with `tools/reach_oracle.py`, which runs scripted matches of the Original in SIMH. Its findings for Spacewar are these:

- The Game Logic reaches no layout past an array. The main loop reads past the ships' two-word outline array for every torpedo slot, but only the ships' own slots use the word it loads. A check that poisons that word for every other slot still matches the Original, so that layout is not part of the Game Logic, and the image's layout carries the read.
- The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. They are inputs: memory the program never set. Those words are Fields with no initial value, and they come in at the game's boundary.
- The game writes code and runs it. At each new game, Spacewar's outline compiler writes each ship's outline as PDP-1 instructions, and each frame the spaceship jumps into them to draw the ship. The outlines are Presentation. The program fixes this code for itself from its own tables, so it is Game Logic, and the RUNS source carries it. RUNS-Spacewar states what the outline code draws: the outline compiler decodes each outline into strokes (`outline_code`), and `draw_outline` walks them. The compiler reproduces the instructions.
- Everywhere else, the program reaches only the `word` type's own arithmetic, such as sums that wrap and shifts of negative numbers.

## Three kinds of Record

Presentation is the screen, the sound, the controls and the pacing; the machine under them is outside RUNS. A Game Port rebuilds the Presentation for each machine and leaves the Game Logic alone, so the Presentation has to come out whole with no change to the Game Logic. The Conversion keeps the Original's Presentation whole: it is the record of how the Original looked, sounded and played, and each Game Port reads it to decide what to keep. Every Record has one of three Kinds, and each Kind says which Processors may touch it: Game Logic and Presentation meet only at Interface Records. Kinds are a convention, not a primitive of RUNS (GLOSSARY.md, Kind).

- **A game Record** holds what only the Game Logic uses, such as Spacewar's fuel, the random number, or a ship's angular momentum.
- **An Interface Record** holds what the game and its Presentation share. The game writes what there is to show, such as each object's position and heading. The world writes what comes in, such as the controls and the switches.
- **A Presentation Record** belongs to one platform, such as the pen that traces a ship's outline, the scope's points, or the frame's time budget.

One Network wires the game's Processors and the Presentation's. Remove every Presentation Processor and every run of one, and the game's Records are the same at every step. A new platform supplies its own Presentation Processors and Records, reads the same interface, and changes nothing in the game. The Interface Records are the whole contract between the two. [Three kinds of Record](./NETWORK_TOPOLOGY.md#three-kinds-of-record) states the rules the loader enforces.

A Record's Kind follows from what its values reach, not from what the code was written for. A value is the game's if any Game Logic can observe it. Spacewar's central star draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the two draws are the game's, and only the line the star draws from them is Presentation. A Processor that does both, as the original's code often does, splits in two. The game's half writes the value to an Interface Record, and the Presentation's half reads it.

A conversion checks its split by running the game with every Presentation Processor removed against the Original, as [Conversion Process](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) states.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a Field with no initial value, in a Record the host writes before a tick, which the top Network declares under `requires:`. An outbound Interface Record is read after the tick and declared under `produces:` (GLOSSARY.md, Interface Record). Spacewar's `tick` requires `console, score, controls, outline_code, pause` and produces `display, scoreboard, lights, pause`. The loader lowers them to `reads:` and `writes:`, the inline form's keywords. On a routine, `requires:` is a Precondition instead.
2. A value goes out to the Presentation. It is an Interface Record the game writes.
3. The machine computes something the Game Logic then reads, such as a sum that wraps or a collision a video chip latches. That computation is Game Logic, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes Game Logic or a value that comes in.

Only the third could widen the boundary, and a conversion always resolves it by moving the computation into the game. So the interface can grow in data, but it does not gain a new kind of thing.

## The Declarations

A machine's **Declarations** are the half of its package that never runs. They hold only choices that play cannot observe, such as where each routine and Field lies, which register carries a value, how an enum is encoded in bits, and which device carries each value that comes in or goes out. They record the original programmer's arbitrary choices, never Game Logic, and a Game Port leaves them behind with that machine's Presentation. Their count of entries only shrinks. [Declarations](./DECLARATIONS.md) is the reference. RUNS-Spacewar's PDP-1 Declarations are `pdp1/`.

## The compiler

A compiler takes RUNS plus a target's Declarations. Each target machine has its own compiler, and every game for that machine shares it. With the original machine's Declarations, the original machine's compiler builds the original binary exactly. Running the game on another machine is a Game Port: new Presentation Processors and Records, that machine's Declarations, and that machine's compiler.

The compiler for a machine is general. It holds that machine's details, such as registers, addresses, scratch words, and the instructions that move a word, and no game's logic or timing, which live in the Network (GLOSSARY.md, Compiler). A change to it is a general rule for the machine that a second program on that machine uses, never a fix to make one game's shape compile. The owner said on 2026-11-11 that "there should be no changes at all to the compiler... Everything should be in how the network is structured", meaning no bending it for one game, and called it "a general pdp1 compiler"; on 2026-11-14, "that's the job for the compiler to make sure that it runs on the PDP-1". When a pure shape does not compile to the original binary, the RUNS source changes first, then the compiler gains a general rule, as [Where a change goes](./DECLARATIONS.md#where-a-change-goes) states.

In RUNS-Spacewar, `tools/runsc.py` compiles the RUNS source and the PDP-1 Declarations to the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` compiles that C to a tape image. The image's sha256 is the Original's, `8744e9c9c8540cc5075c5cbb91c56745a4305fdf8e7afca43bea2e9e04ca4bdf`.

RUNS-Spacewar checks the conversion these ways:

- **The evaluator against SIMH.** Each routine and Network runs in the evaluator and in SIMH from the same state, and the checks compare Records and points.
- **The image against the Original.** `runsc` builds the image from RUNS and prints `identical to the original` when its hash is the Original's.
- **The mutation gate.** `tools/check_compiled.py` mutates the RUNS source and the Declarations, as [The mutation gate](./DECLARATIONS.md#the-mutation-gate) states.
- **The order is in the wires.** `tools/check_names.py` renames every transition of the Network files and checks that the image stays the same.
- **The Fields hold what the arcs write.** `tools/check_fields.py` checks the compiled RUNS against what each arc writes, after each firing.
- **A second program.** The same compiler builds Minskytron's image from its RUNS source, and `tools/check_minskytron.py` checks its points.

`tools/check_all.sh` runs them all.

## Relationship to other EGS protocols

RUNS is a protocol on its own.

- **MAPS** is a separate protocol. How it relates to RUNS is open.
- **AEMS** is a separate protocol for assets and things. A game's assets belong there. Spacewar's ship outlines and star catalog are data on the tape, so the conversion keeps them in the RUNS source as Records. RUNS defines no way to read AEMS data.
- **RUNS Library** is a separate repository that predates this spec and differs from it. Where they differ, this spec governs.

## Check the examples

Every `runs` and `runs-prim` example in these documents loads and runs in RUNS-Spacewar's evaluator, and every `-rejected` block fails with the error its first line quotes. The examples' machine is the PDP-1, and they omit the `machine pdp1` line, because that evaluator holds the [PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) in code. Blocks tagged `runs-machine`, `net`, and `text` are not run. Every accepted example gives each Record and stream a Kind, so the loader checks it for purity. `tools/check_examples.py` states what it checks in its docstring.

Run it from this repository, with the RUNS-Spacewar checkout beside it. It passes when it prints only `ok` lines and exits 0:

```sh
python3 tools/check_examples.py . ../runs-spacewar
```

## Open questions

- **The kind of each Record.** A conversion decides each kind by hand, from what the Record's values reach. A tool could trace each value through the Original in SIMH instead.
- **What a halt means for unordered transitions.** What `stop` means for transitions the wiring leaves unordered is not settled. (The loop rule itself is settled, [The Network loop](./NETWORK_TOPOLOGY.md#the-network-loop); reading a counter loop outside a loop Sub-Network is tool work still to do.)
- **How fine to cut Processors, and the shape of Sub-Networks.** How small a Processor should be, and how Sub-Networks of Sub-Networks are cut and named, is not settled. Decomposition is convention, not compliance (GLOSSARY.md, Processor).
- **The order of the Conversion Process.** Which order turns an original program into coherent groupings of Game Logic best, and how to automate it, is not settled. [Conversion Process](./CONVERSION_PROCESS.md#the-route) states the route and the owner's stated wish.
- **What done means.** A purity count of 0 is necessary. What else a finished Conversion requires is not settled.
- **Recursion.** A routine that keeps values across a call to itself needs a copy of them per depth. One Field cannot hold them. Spacewar does not recurse.
- **What counts as the machine.** Which revision of a machine, and where its specified behavior ends and physical fault begins, is a judgment made once per machine in its description ([Machine description](./MACHINE_DESCRIPTION.md#what-counts-as-the-machine)). The form a description states it in is not settled, and the PDP-1 description does not state it yet.
- **A Presentation effect that ends the program.** DOOM's visplane-overflow crash only flows out, so it is Presentation, and the reference keeps it. It also ends the program, which stops the Game Logic. How RUNS states that is not settled.
- **The jump into code the program never contained.** That code is the machine's ([ADR-0002](./docs/adr/0002-four-layers-and-the-machine-is-outside-runs.md)). How the RUNS source marks the step where the program jumps into it is not settled.
- **Naming and distribution.** How RUNS source is named, published, and shared, and what a shared library of Records and Processors holds.

**MIT License.** Open for implementation, extension, and critique.
