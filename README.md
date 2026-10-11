# RUNS: Records Update on Neutral Substrate

🏠 **[EGS Overview](https://github.com/enduring-game-standard)** · 📦 **[AEMS](https://github.com/enduring-game-standard/aems-schema)** · 🎯 **[AEMS Conventions](https://github.com/enduring-game-standard/aems-conventions)** · 🔧 **[RUNS](https://github.com/enduring-game-standard/runs-spec)** · 📖 **[RUNS Library](https://github.com/enduring-game-standard/runs-library)** · ⚡ **[WOCS](https://github.com/enduring-game-standard/wocs-protocol)** · 🎼 **[MAPS](https://github.com/enduring-game-standard/maps-notation)** · 🎶 **[MAPS Library](https://github.com/enduring-game-standard/maps-library)** · ❓ **[FAQ](https://github.com/enduring-game-standard/.github/blob/main/profile/FAQ.md)** · 🔤 **[Glossary](https://github.com/enduring-game-standard/.github/blob/main/profile/README.md#glossary)**

> **Status.** Working draft, settled by one port. A verbatim port of Spacewar! 3.1 (the `spacewar-runs` repository, not yet published) writes the whole game in RUNS. Its reference evaluator, `tools/runs.py`, parses RUNS, checks it before anything runs, and runs it. Checks compare the evaluator's Records with the original game running in the SIMH PDP-1 emulator, or for the square root, with results recorded from it. Its compiler, `tools/runsc.py`, compiles the RUNS text with a PDP-1 binding to the original tape image, and the image's sha256 matches the original's. The syntax in these documents is the syntax that evaluator accepts. It is a draft and will change as other games are ported. [The compiler and what it proves](#the-compiler-and-what-it-proves) states what the port has and has not shown.

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

- **A Record** is anything the game remembers, such as the object table, the random number, the frame's time budget, or the tunables. Global data is a Record like any other. A Record holds one set of fields, or a fixed number of each field. A field with no initial value is unknown until the game sets it or the world gives it. A **stream** is a Record that collects ordered output, such as the points the display plots.
- **A Processor** is one rule. It declares the Records it reads and the Records it writes. Its body computes freely inside, and it may update its declared Records in place. Purity holds at the boundary. What a Processor does depends only on what it declares.
- **A Network** fires Processors and other Networks in order, chooses with guards, and repeats with bounded loops. A Network writes nothing. A guard is any expression that writes nothing, arithmetic included.

The topology is a Petri net. Records are the places and Processors are the transitions. No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record. RUNS has no functions. An earlier draft had them, and a call carried a value from one rule to another with no place in between, so functions were removed. The only calls left in RUNS are the word's own operators, such as `rcl`, `scr`, and `popcount`, and the constructors of the original machine's instructions. If writers want call syntax, a tool that writes RUNS can offer it. RUNS itself has none.

The original program's subroutines, macros, and executed tunables all become Processors. A subroutine that calls another becomes a Network. A loop that runs a macro or a tunable becomes a Network loop. A subroutine's own loop stays inside its Processor. A value the original carried in a register from one routine to the next becomes a field of a Record.

Processor bodies are written in DIGS (Deterministic Inspectable Game Syntax). Firing is sequential. A Network runs its Processors in the order it states them, and each Processor sees everything earlier ones wrote. A compiler may find concurrency from the declared reads and writes, but concurrency is not part of the model. Assuming it would change Spacewar.

Here is a complete RUNS program. A `.runs` file declares Records and Networks:

```runs
record ball
  x: word = 0
  dx: word = 3

record pad
  held: word                # no initial value: the player's button comes in

stream screen
  x: word

network tick
  reads: pad
  writes: screen
  run move_ball
  if ball.x - 0100 >= 0:
    run bounce
  run draw_ball
```

A `.runs-prim` file declares Processors:

```runs-prim
processor move_ball
  reads: pad
  writes: ball
  if pad.held == 0:
    set ball.x = ball.x + ball.dx

processor bounce
  writes: ball
  set ball.dx = -ball.dx

processor draw_ball
  reads: ball
  writes: screen
  emit screen: ball.x
```

`tick` is a top Network, because nothing fires it, so it is a whole game. Its contract is the game's boundary with presentation. The button comes in through `reads: pad`, and the points leave through `writes: screen`. To make a house rule where the ball stops instead of bouncing, replace `bounce` and change nothing else.

## Exact over every input, glitches included

A glitch is one of three kinds, by what it reads.

1. **A logic glitch** is the game's own logic, such as the backwards long jump. A verbatim port keeps it with no extra work. In Spacewar, the previous control word is never stored, so with sense switch 3 on, the fire button always counts as newly pressed. The port keeps it.
2. **A layout glitch** reads past an array, through a stale pointer, or reads one kind of object as another, such as DOOM's `spechit` overflow. In those states the rule is whatever lies next in memory, so the layout is part of the game. Where play reads the layout, the RUNS text states it.
3. **A machine glitch** runs data as code or jumps into the middle of a routine. On that path the rule is that the machine runs those bytes. The original machine's instruction semantics are then part of the game, used only where play reaches them, and the original code bytes are part of the game's data.

All three kinds share one piece, a description of the original machine. It supplies RUNS's types. For Spacewar, that is the `word`, the PDP-1's 18-bit ones' complement word, and the `insn`, a PDP-1 instruction. Where play reads the layout, it supplies the layout. Where play reaches machine behavior, it supplies the instruction semantics. The rest of the game is RUNS.

A halt or a hang that the original reaches is a rule, not an error. Spacewar halts when a ship fires and the object table is full, and the port writes `stop`. Spacewar also halts between games to show the scores, and the port writes an `emit` of the scores, then `wait`. In contrast, when a loop runs past its bound, a `requires:` fails, or the evaluator reaches `unreachable`, the port is wrong. These never mean the game may do anything.

Where play reaches layout or machine behavior is a fact to measure, not a guess. The Spacewar port measures it with `tools/reach_oracle.py`, which runs the original in SIMH through seventeen scripted matches, 59 million instructions. Its findings for Spacewar are these:

- Play observes no layout read. The main loop reads past the ships' two-word outline array for every torpedo slot, but only the ships' own slots use the word it loads. A check that poisons that word for every other slot still matches the original, so the binding carries the read and the RUNS text does not state it.
- The first match reads words of core that the tape never loads, such as the scores, so their power-on contents matter. Those words are fields with no initial value, and they come in at the game's boundary.
- The game writes code and runs it. At each new game, Spacewar's outline compiler writes each ship's outline as PDP-1 instructions, and each frame the spaceship jumps into them to draw the ship. The port states this with a Record of `insn` values that the compiler fills and a `jump` that runs them by the PDP-1's rules. The outlines are presentation, but the port keeps the code and runs it where the original does.
- Everywhere else, play reaches only the `word` type's own arithmetic, such as sums that wrap and shifts of negative numbers.

## Gameplay and presentation split by consequence

Presentation is the screen, the sound, the controls, the pacing, and the machine underneath. It can be rebuilt for each platform. The game cannot. Games outlive their hardware only if the boundary between the two is thin.

What a piece of code's effects reach decides its side, not what the code was written for. Code is presentation only if nothing in the game can observe its effects. Spacewar's central star is presentation, but it draws two random numbers each frame from the generator that also decides hyperspace jumps. Turning the star off with sense switch 6 changes hyperspace. So the star's two draws are a game rule, and only the line it draws from them is presentation.

The game touches the machine in four ways:

1. A value comes in, such as the controls, a clock, or the contents of core at power-on. It is a field with no initial value, in a Record the boundary declares under `reads:`.
2. A value goes out, such as a point to plot or a sound to play. It is a Record or stream the boundary declares under `writes:`.
3. The machine computes something the rules then read, such as a sum that wraps or a collision a video chip latches. That computation is a rule, and it moves inside the game.
4. Timing. Where the game's state depends on it, timing becomes a rule or a value that comes in.

Only the third could widen the boundary, and the port always resolves it by moving the computation into the game. So the boundary can grow in data, but it never gains a new kind of thing.

A top Network is a whole game, and its contract is the game's boundary with presentation. A game may have several top Networks, and together they are one game. Spacewar has three. The host fires one of two start Networks once, when the operator starts the machine at address 4 or 5, and then fires the frame once each frame. A Record they share does not cross the boundary.

Spacewar's boundary, as its top Networks declare it:

- **What comes in.** `console` holds the test word switches, the control boxes, and the six sense switches. `score` holds the two scores and the games left in the match, which start from what core held at power-on. `controls` holds which device the control word comes from, which the start address decides. `outline_code` holds the compiled outlines, which the start's new game writes before the first frame.
- **What goes out.** `display` holds the points the scope plots. `scoreboard` holds the scores that the halt between games shows on the console lights. `lights` holds the two program flags that light for the ship that survived a game.

`wait` is where the world takes a turn inside a firing. The host shows what has left the game and may change what comes in, and then the firing goes on.

Which device carries each field is not part of RUNS. A binding for each machine maps the boundary's fields to that machine's controls, lights, and start addresses. That mapping is the presentation side of the boundary. The Spacewar port keeps all of it for the PDP-1 in one file, `pdp1/devices.toml`, which the compiler and the checks both read.

The port stays verbatim. Presentation code stays where the original runs it, in the order it runs. The split says which of its effects the game must keep.

## The binding

A **binding** maps RUNS onto one target machine. It holds only the choices that play cannot observe:

- Where each routine and each Record field lies.
- How each routine is entered and left.
- Which register or word carries each value.
- How the code is laid out.
- Which device carries each boundary field.

A binding holds no game logic. It has no expressions, no statements, and no number that the game computes with. Where the game states a layout, the binding follows it. The Spacewar port's PDP-1 binding is `pdp1/` in `spacewar-runs`, and `pdp1/README.md` there defines its vocabulary and the rules its compiler enforces.

## The compiler and what it proves

A compiler takes RUNS plus a binding for a target. With the original machine's binding, the goal is the original binary, exactly. With other bindings, the goal is the same game on other machines.

In the Spacewar port, `tools/runsc.py` compiles the RUNS text and the PDP-1 binding to the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` compiles that C to a tape image. The whole game compiles this way. All 13 units are generated from RUNS, and the image's sha256 is the original's, `8744e9c9c8540cc5075c5cbb91c56745a4305fdf8e7afca43bea2e9e04ca4bdf`. No file of spacewar-c's lifted C takes part in the build. The port traced every file the build opens to show it.

The port has these checks:

- **The evaluator against SIMH.** Each routine and Network runs in the evaluator and in SIMH from the same state, and the checks compare Records and points. The square root is the exception. Its check compares all 65,536 inputs with results recorded earlier from SIMH. The samples are large but not exhaustive, except for the square root and for the sine and cosine, which matched on all 2^18 input words each in a run by hand. Whole frames, the game control from power-on through scoring and new games, and seventeen scripted matches all match. `tools/check_all.sh` runs these checks on each change. When each unit was ported, planted defects in its RUNS text, and five planted defects in the evaluator's machine rules, were caught by the checks. Those planted-defect runs and `reach_oracle.py` were run by hand then and have not run since.
- **The image against the original.** `runsc` compiles only RUNS that `runs.check` accepts. It refuses a binding key it does not know, a key it needs that no binding gives, a name the RUNS text lacks, a read of a shared word that holds another name, a skip return not set on every path, and a `carry` that the RUNS jump does not agree with.
- **The mutation gate.** `tools/check_compiled.py` mutates the RUNS of every routine and field that a binding compiles. In its last run, it made 9,346 mutants. 7,576 changed the image, 1,619 were refused by `runsc`, 113 were rejected by the evaluator, and 38 built the original image and were shown to be the same game. Each of those 38 fired the same as the original on 200 seeded Record states, or was the same text. None built the original image while firing differently. Deleting each of the bindings' 408 key lines and sections changed the image or was refused, so no key is dead.
- **Independent review.** Two rounds of adversarial review read the compiler and its checks. The first round, two reviewers on different models, found among other things that the binding chose a jump target without compiling the RUNS operand, that shared words were unchecked, that `runsc` compiled RUNS the evaluator rejects, and that a check masked unknown values. The second round, one reviewer, found that a register field turned into a local of the same name built the original image at 13 sites while the evaluator differed, and that random bindings could crash `runsc`. The port's decision log records a fix for every finding, and the gate now catches each class.

Together these show that the RUNS text drives every word of the image that the gate's mutations touch, and that the evaluator's game matches the original over the sampled play. They do not show these things:

- That the binding holds no game logic in every case. The gate does not mutate a `match`'s arms or insert statements. Swaps of fields of different types were swept once by hand, 939 mutants with none silent, and are not in the gate.
- That every equivalent mutant is the same game. Sameness is sampled on 200 states, not proved.
- That `runsc`'s layout rules are general. About a sixth of the mutants are refused rather than compiled, because many rules accept only the shape the original used. Several rules were shaped by one routine, and no independent reviewer has judged whether each is general.
- That the fixes from the second review are right. That reviewer's re-review of its own findings did not run. The port's author re-ran the reviewer's sweeps on the fixed code. No independent reviewer has re-read the shared-words check or the bit-level proof that lets a stale read stand.
- That the binding's vocabulary is the right size. It grew with each unit, with keys such as `walk`, `carry`, `stray`, `spill`, `exit`, and `pulse`. The decision log leaves those keys, and the sequence-break and start-vector words that `runsc` emits as PDP-1 runtime, open for a final independent review. It does not record whether the two review rounds closed them.
- That a binding for any other machine works. None exists.

The Expensive Planetarium's full window cycle, 2 times 16 times 020000 frames in a row, has not run. Frames from set counters and margins cover the margins instead.

## Relationship to other EGS protocols

RUNS is a protocol on its own.

- **MAPS** is a separate protocol, a notation for studying and designing rules.
- **AEMS** is a separate protocol for assets and things. A game's assets belong there. Spacewar's ship outlines and star catalog are data on the tape, so the port keeps them in the RUNS text as Records. RUNS defines no way to read AEMS data yet.
- **RUNS Library** is a separate repository that predates the Spacewar port. It is inconsistent with this spec. It proposes `runs:` namespaced fields, Nostr distribution, `state:` Records, bundles, and floating-point vector types, none of which the port tested. Read this spec where the two differ.

## What these documents cover

- [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) is the reference for Processors in `.runs-prim` files. It covers their declarations, statements, and expressions, code the game runs, and the `word` type.
- [Network topology](./NETWORK_TOPOLOGY.md) is the reference for `.runs` files. It covers types, enums, Records, streams, Networks, and the contract rules the loader enforces.
- [Conversion process](./CONVERSION_PROCESS.md) is how to port a game to RUNS, as the Spacewar port did it.

## Check the examples

Every RUNS example in these documents loads and runs in the Spacewar port's evaluator. `tools/check_examples.py` checks this. It loads each accepted example, then all of a document's accepted examples as one program, runs `runs.check`, and runs each top Network six passes. It confirms that each rejected example fails with the error its first line quotes. It also fails on an em dash or an en dash in the documents.

To run the check, put `spacewar-runs` beside this repository and run this command from this repository:

```sh
python3 tools/check_examples.py
```

To point it at other directories, pass them as arguments:

```sh
python3 tools/check_examples.py <runs-spec dir> <spacewar-runs dir>
```

The command exits with status 0 when every example passes.

## Open questions

The Spacewar port has settled the model above. These parts are still open:

- **The syntax.** It is a working draft that covers what Spacewar needed.
- **The original-machine description.** RUNS has no text form yet for the machine's rules. The loader skips `type word` and reads only the instruction list of `type insn`. The evaluator defines the word's arithmetic and each instruction's rule in code.
- **Stated layout.** RUNS has no syntax yet for stating a layout where play reads it, because Spacewar's play reads none.
- **Machine glitches.** `jump` runs code that the game writes. No port has yet run the original's own code bytes from data, so whether `jump` covers a machine glitch is untested.
- **Gameplay and presentation by field.** The port classifies by hand, from what each effect reaches. A tool that classifies each field by consequence is not built.
- **Other games.** Decisions about floating point, recursion, run-time allocation, versions, and code with no source come from a paper exercise against other games, recorded in the port's `INTENT.md`. No port has tested them.
- **Naming and distribution.** The draft grammar has no namespaces. How RUNS text is named, published, and shared, and what a shared library of Records and Processors would hold, is not settled. Earlier drafts and the RUNS Library proposed Nostr events and a `runs:` namespace. The port did not test either.

**MIT License.** Open for implementation, extension, and critique.
