# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · 🎶 **[MAPS Library](https://github.com/enduring-game-standard/maps-library)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Working draft, settled by one port. A verbatim port of Spacewar! 3.1 (the `spacewar-runs` repository, not yet published) has a reference evaluator, `tools/runs.py`, that parses RUNS, enforces its rules, and runs it. Checks compare the evaluator's Records with the original game running in the SIMH PDP-1 emulator, field by field. The syntax in these documents is the syntax that evaluator accepts. It is a draft and will change as more of Spacewar, and then other games, are ported. A compiler from RUNS to the exact original binary is in progress. So far it compiles one routine, the square root, and the result matches the original tape image by hash.

RUNS is a plain-text form for a game's rules. Its purpose is that a game's rules outlive the machine they were written for. Anyone can read, run, and change the text, and any future runtime can rebuild it into the same game.

## What RUNS requires

Five requirements follow from that purpose.

1. **The port is exact, glitches included.** Every sequence of inputs from power-on gives the same game as the original. A glitch that play can reach is part of the game. A re-release of Super Mario 64 without the backwards long jump would not be Super Mario 64. A port never changes the game to fit RUNS. Where RUNS cannot yet say what a game does, RUNS grows.
2. **The text is the game.** RUNS is deterministic and total, so every faithful runtime produces the same game. Nothing about the game lives only in a binary.
3. **Every rule can be swapped.** A rule is replaceable only if its whole contract is visible. A Processor's contract is the Records it reads and writes, and nothing else. A register left set, a shared scratch word, or a patched instruction would be a hidden channel. That is why all data flows through Records.
4. **The structure is visible.** The order in which rules fire, and the conditions under which they fire, are rules too. Networks state them in the text.
5. **Variation is native.** A house rule is an edit to one Processor or one Network line, not a fork of a program.

## Records, Processors, and Networks

RUNS has three parts.

- **A Record** is anything the game remembers: the object table, the random number, the frame's time budget, the tunables. Global data is a Record like any other. A Record holds one set of fields, or a fixed number of each field. A **stream** is a Record that collects ordered output, such as the points the display plots.
- **A Processor** is one rule. It declares the Records it reads and the Records it writes. Its body computes freely inside, and it may update its declared Records in place. Purity holds at the boundary. What a Processor does depends only on what it declares.
- **A Network** fires Processors and other Networks in order, chooses with guards, and repeats with bounded loops. A Network writes nothing. A guard is any expression that writes nothing, arithmetic included.

The topology is a Petri net. Records are the places and Processors are the transitions. No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record. RUNS has no functions. An earlier draft had them, and a call carried a value from one rule to another with no place in between, so functions were removed. The only calls left in RUNS are the word's own operators, such as `rcl`, `scr`, and `popcount`. If writers want call syntax, a tool that writes RUNS can offer it. RUNS itself has none.

The original program's subroutines, macros, and executed tunables all become Processors. A loop that runs a macro or a tunable becomes a Network loop. A subroutine's own loop stays inside its Processor. A value the original carried in a register from one routine to the next becomes a field of a Record.

Processor bodies are written in DIGS (Deterministic Inspectable Game Syntax). Firing is sequential. A Network runs its Processors in the order it states them, and each Processor sees everything earlier ones wrote. A compiler may find concurrency from the declared reads and writes, but concurrency is not part of the model. Assuming it would change Spacewar.

Here is a complete RUNS program. A `.runs` file declares Records and Networks:

```runs
record ball
  x: word = 0
  dx: word = 3

stream screen
  x: word

network tick
  writes: screen
  run move_ball
  if ball.x - 0100 >= 0:
    run bounce
  run draw_ball
```

A `.runs-prim` file declares Processors:

```runs-prim
processor move_ball
  writes: ball
  set ball.x = ball.x + ball.dx

processor bounce
  writes: ball
  set ball.dx = -ball.dx

processor draw_ball
  reads: ball
  writes: screen
  emit screen: ball.x
```

`tick` is a top Network, because nothing fires it, so it is a whole game. Its `writes: screen` is the game's boundary with presentation. To make a house rule where the ball stops instead of bouncing, replace `bounce` and change nothing else.

## Exact over every input, glitches included

A glitch is one of three kinds, by what it reads.

1. **A logic glitch** is the game's own logic, such as the backwards long jump. A verbatim port keeps it with no extra work. In Spacewar, the previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed.
2. **A layout glitch** reads past an array, through a stale pointer, or reads one kind of object as another, such as DOOM's `spechit` overflow. In those states the rule is whatever lies next in memory, so the layout is part of the game. Where play reads the layout, the RUNS text states it.
3. **A machine glitch** runs data as code or jumps into the middle of a routine. On that path the rule is that the machine runs those bytes. The original machine's instruction semantics are then part of the game, used only where play reaches them, and the original code bytes are part of the game's data.

All three kinds share one piece, a description of the original machine. It supplies RUNS's types. For Spacewar, that is the `word`, the PDP-1's 18-bit ones' complement word. Where play reads the layout, it supplies the layout. Where play reaches machine behavior, it supplies the instruction semantics. The rest of the game is RUNS.

A halt or a hang that the original reaches is a rule, not an error. Spacewar halts when a ship fires and the object table is full. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the port is wrong. These never mean the game may do anything.

Where play reaches layout or machine behavior is a fact to measure, not a guess. The Spacewar port measures it with `tools/reach_oracle.py`, which runs the original in SIMH through seventeen scripted matches. So far it has found no layout read that play observes. Spacewar's play reaches the machine outside the `word` type in one place. The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. Those words come in at the game's boundary.

## Gameplay and presentation split by consequence

Presentation is the screen, the sound, the controls, the pacing, and the machine underneath. It can be rebuilt for each platform. The game cannot. Games outlive their hardware only if the boundary between the two is thin.

What a piece of code's effects reach decides its side, not what the code was written for. Code is presentation only if nothing in the game can observe its effects. Spacewar's central star is presentation, but it draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the star's two draws are a game rule, and only the line it draws from them is presentation.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a Record the boundary declares.
2. A value goes out, such as a point to plot or a sound to play. It is a Record or stream the boundary declares.
3. The machine computes something the rules then read, such as a sum that wraps or a collision a video chip latches. That computation is a rule, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes a rule or a value that comes in.

Only the third could widen the boundary, and the port always resolves it by moving the computation into the game. So the boundary can grow in data, but it never gains a new kind of thing.

A Network can state a contract the way a Processor does, with `reads:` and `writes:`. A top Network is a whole game, and its contract is the game's boundary with presentation. The port stays verbatim. Presentation code stays where the original runs it, in the order it runs. The split says which of its effects the game must keep.

## The binding and the compiler

A **binding** maps RUNS onto one target machine. It holds only the choices play cannot observe: where each Record lives in memory, how an enum value is spelled as a word, how scratch space is laid out. Where the game states a layout, the binding follows it. The Spacewar port's PDP-1 binding, in its first form, is `tools/pdp1.py`.

A compiler takes RUNS plus a binding for a target. With the original machine's binding, the goal is the original binary, exactly. With other bindings, the goal is the same game on other machines. In the Spacewar port, work in progress compiles RUNS plus the PDP-1 binding to the C dialect of the `spacewar-c` project, which its `pdp1cc` compiler turns into PDP-1 code to be matched by hash against the original binary. The square root compiles this way and matches the original tape image. A planted change to the RUNS source breaks the match, so the RUNS text, not the existing C, drives the result. The rest of the game does not compile yet.

## Relationship to other EGS protocols

RUNS is a protocol on its own.

- **MAPS** is a separate protocol, a notation for studying and designing rules.
- **AEMS** is a separate protocol for assets and things. A game's assets belong there. RUNS defines no way to read AEMS data yet.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) is the reference for Processors in `.runs-prim` files: their declarations, statements, expressions, and the `word` type.
- [Network topology](./NETWORK_TOPOLOGY.md) is the reference for `.runs` files: types, enums, Records, streams, Networks, and the contract rules the loader enforces.
- [Conversion process](./CONVERSION_PROCESS.md) is how to port a game to RUNS, as the Spacewar port did it.

## Open questions

The Spacewar port has settled the model above. These parts are still open:

- **The syntax.** It is a working draft that covers what one slice of Spacewar needed.
- **The original-machine description.** RUNS has no settled text form for it yet. The loader skips `type` declarations, and the evaluator defines the PDP-1 `word` in code.
- **Stated layout.** RUNS has no syntax yet for stating a layout where play reads it, because Spacewar has not needed one.
- **Machine instruction semantics.** RUNS has no form yet for running the original machine's instructions where play reaches them.
- **Boundary inputs.** Values that come in belong in the top Network's contract. The control word, the sense switches, and the power-on words are not ported yet, so the form of that declaration is not decided. The loader does not yet require it.
- **Halts.** How a port writes a halt the original reaches is not decided. The Spacewar halt is not ported yet.
- **Other games.** Decisions about floating point, recursion, run-time allocation, versions, and code with no source come from a paper exercise against other games, recorded in the port's `INTENT.md`. No port has tested them.
- **Naming and distribution.** The draft grammar has no namespaces. How RUNS text is named, published, and shared, and what a shared library of Records and Processors would hold, is not settled. Earlier drafts proposed Nostr events and a `runs:` namespace. The port did not test either.

**MIT License.** Open for implementation, extension, and critique.
