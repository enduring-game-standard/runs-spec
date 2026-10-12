# How to port a game to RUNS

This guide ports a game to RUNS the way the Spacewar! 3.1 port (`RUNS-Spacewar`) did. The port is verbatim. Every sequence of inputs from power-on gives the same game, glitches included. You never change the game to fit RUNS. Where RUNS cannot say what the game does, RUNS has to grow, and that is a change to this spec.

The Spacewar port is complete. Every routine of the game is written in RUNS, and the RUNS text with its PDP-1 binding compiles to the original tape image, byte for byte. Each step below names what Spacewar needed. A second game may need more.

## Before you start

You need:

- The original program, as source or as machine code. Code with no source is ported from its machine code.
- The original running in an emulator you can script and whose state you can read. Spacewar uses SIMH running an image of the original program. The running original is the authority. Reading the source is not.
- The reference evaluator, `tools/runs.py` in the Spacewar port. It parses RUNS, runs `runs.check` before anything runs, and runs a Network over Records.

## 1. Find every Record

A Record field is any word of the original that carries meaning from one routine to another or from one frame to the next.

1. Name each field for what it means, not for its symbol. Put the original symbol in a comment, as in `particles: word = 0  # mxc`.
2. Make a value that a routine sets before it reads it, and never hands on, a local of the Processor instead.
3. Keep a word that the game counts and never reads, such as Spacewar's `objects_seen`. It becomes a field that no Processor reads, and the graph shows it is dead.
4. Drop words that only the machine uses and play never observes, such as a cursor kept in an instruction's address field. They belong to the binding.
5. Keep global data in Records like any other state. Data on the tape, such as Spacewar's star catalog and ship outlines, is a Record whose field takes one initial value a slot.
6. Give a field no initial value if its value comes from outside the game. Spacewar's scores start from whatever core held at power-on, so `score` has no initial value.
7. Keep one field for one word, even when the original reads it under two meanings. Spacewar's divide keeps the dividend's high half and then the remainder in one word, and the port keeps one field.

A routine word that names which code runs an object is a state. Make it an enum. In Spacewar, the calc routine word becomes `enum calc_routine`, and the sign bit that marks whether an object collides is a function of that enum. A program flag that a routine sets and tests is an enum too, as a field when it carries from one firing to the next and as a local when the routine clears it before it reads it.

## 2. Map each routine to Processors and Networks

The original passes values between routines in registers. RUNS passes every value through a Record. Map each way the original shares a rule:

| In the original | In RUNS |
|-----------------|---------|
| A subroutine (`jda sqt`) | A Processor over the routine's own words, which form one Record. |
| A subroutine that calls another (`imp` calls `mpy`) | A Network. A Processor sets the callee's Record, the callee runs, and a Processor reads the callee's results. |
| The word after a call, which the callee executes each time it reads it (`jda mpy / lac b`) | A field the caller sets before the run, if no caller names a word the callee writes. That held for every call in Spacewar. |
| Two entries into one body (`idv` shifts its dividend, then jumps into `dvd`) | A Network that runs the first Processor, then the shared routine. The jump past the entry word is the binding's. |
| A macro with arguments (`dislis J, Q, B`) | A Processor or a Network with parameters, run with constants. |
| A jump into a run of copies, past as many as a number says | A counted `for` from a local. The binding lays it out as the jump. |
| A store of an address part (`dap`) | A `set` that keeps the rest of the word, as in `set f = f & 0770000 \| 020`. |
| A skip return (`dvd` returns one word further when the quotient fits) | An enum field whose members are the outcomes. The binding says which member skips. |
| A tunable executed with `xct` | A Processor of its own. What it takes from and leaves in the registers are fields of a `handoff` Record. |
| A macro (`random`, `diff`) | A Processor. A macro that works on one axis at a time becomes one Processor per axis. |
| A loop that runs a macro or a tunable | A Network `loop at most N:` that fires the Processor and exits on a guard. |
| A routine that runs a macro or a tunable | A Network that fires Processors in the original's order. |
| A skip instruction | A Network guard that tests what the skip tests. |
| A label that several places jump to | A Network of its own. Each jump is a `run` of it as the last thing a branch does. |
| The main loop | A top Network, in the original's order. The host fires it once each frame. |
| A start address | A top Network that the host fires once, when the operator starts the machine there. |
| A jump through a routine word | A `match` on the enum. |
| A jump through a table on a number | An `if` chain over the values. |
| A halt that the operator continues past | An `emit` of what the halt shows, then `wait`. |
| A halt that halts again when continued | `stop`. |
| Code the program writes, then runs | A Record field of type `insn` that the writer fills, and a Processor that runs it with `jump`. A place in the code is a slot index, and the binding holds the address. |
| A word the routine rewrites, then copies into the code | A field of type `insn` whose initial value is the word the tape holds. |
| An instruction built at run time and executed | The rule it computes. Spacewar's explosion builds a shift from a random number, and the port writes a shift by `popcount` places. |
| A value carried in a register between two rules | A field of `handoff`, with a comment naming the register and the instruction. |

Put only register hand-offs in `handoff`. A word the original keeps in core between two rules is a Record field named for what it means.

Here is a torpedo's flight from the Spacewar port, reduced to the x axis. The original executes the tunable `the` with `xct` and passes values through AC:

```runs
record objects[2]
  x: word = 0               # nx1: position
  dx: word = 0              # ndx: velocity

record handoff
  coordinate: word = 0      # AC into `the`: a torpedo's coordinate, sar 9s
  acceleration: word = 0    # AC into diff: from `the`, or 0 (cla)

network torpedo_flight
  for slot in 0 .. 1:
    run warp_from_x(slot)                                   # tc1
    run torpedo_space_warpage
    run inertia_x(slot)
```

```runs-prim
processor warp_from_x(slot)                                 # lac i mx1; sar 9s
  reads: objects
  writes: handoff
  set handoff.coordinate = objects.x[slot] >> 9

processor torpedo_space_warpage                             # the
  writes: handoff
  set handoff.acceleration = handoff.coordinate >> 9

processor inertia_x(slot)                                   # diff \mdx, mx1, (sar 3s
  reads: handoff
  writes: objects
  set objects.dx[slot] = handoff.acceleration + objects.dx[slot]
  set objects.x[slot] = (objects.dx[slot] >> 3) + objects.x[slot]
```

An operator can still patch `torpedo_space_warpage`, the rule and not only the number, as the original's authors could patch `the`.

Structured text cannot enter a loop in two places. If the original does, state the loop once and repeat the statement that the second entry skips. Spacewar's sine enters its reduction loop in two places, so the RUNS states the reduction step before the loop and again at the end of its body. The binding lays the two out as one.

## 3. Keep the order

The order in which the original runs its rules is part of the game. Firing in RUNS is sequential, and each Processor sees every write before it.

- Fire Processors in the order the original runs them, even when the order looks like an accident.
- Do not split a loop into phases. In Spacewar, object *i* is tested against every later colliding object and then moves, before object *i+1* is touched. A conversion that collided all objects after moving them changed 294 of 300 test frames.
- Keep dead tests and odd ranges. Spacewar's explosion tests a size that can never pass, and its last object slot is never tested for collisions. Both stay.

## 4. Split gameplay from presentation by consequence

Code is presentation only if nothing in the game can observe its effects.

1. For each piece of display, sound, or pacing code, list every Record it changes.
2. If the game reads any of those Records later, that effect is a rule. Spacewar's central star draws two random numbers each frame from the generator that hyperspace also uses, so the draws are rules. The line the star draws from them is presentation.
3. Leave presentation code where the original runs it, in the order it runs. The split decides which effects the game must keep. It does not move code. Spacewar's ship outlines are presentation, and the port still runs them as the original does, as compiled code.
4. Declare what crosses the boundary in the top Networks' contracts.
   - Every stream the game writes, and every Record that leaves, goes in `writes:`. Spacewar's frame declares `writes: display, scoreboard, lights`.
   - Every Record with a field that has no initial value, and that a routine inside reads, goes in `reads:`. Spacewar's frame declares `reads: console, score, controls, outline_code`. The loader refuses a top Network that misses one.
5. Leave the devices out of RUNS. Which switch, light, or start address carries each field is the presentation side of the boundary, and the binding for each machine states it. The Spacewar port states all of them in `pdp1/devices.toml`.

## 5. Measure where play reaches the machine

Do not guess where the game depends on the machine. Measure it by running the original through real play. The Spacewar port's `tools/reach_oracle.py` runs seventeen scripted matches in SIMH, 59 million instructions, and names every data access by the Record field or source label it lands in. It reports these kinds of site:

- One instruction that reads several places, such as a read past the end of an array.
- Reads of core the program never loaded. In Spacewar, the scores and the game count start from whatever core held at power-on, and the first match reads them.
- Code the program writes and then runs.
- Jumps to unnamed places.
- Halts.
- Every place the word's own machine behavior shows, such as a sum that wraps.

Then decide each site:

| What play reaches | What the port does |
|-------------------|--------------------|
| The word's arithmetic | Nothing more. The `word` type already states it. |
| Core the program never loaded | Fields with no initial value, which the top Networks declare under `reads:`. |
| Code the program writes, then runs | A Record of `insn` values and `jump`. |
| A halt or a hang | `stop`, or `emit` then `wait`. |
| A layout that play observes | State the layout in the RUNS text. RUNS has no syntax for this yet, because Spacewar has not needed one. |
| A layout that play does not observe | Leave it to the binding. |

A read past an array is not a layout glitch until play observes it. Prove that it does not before you leave it to the binding. Spacewar's main loop reads past the ships' two-word outline array for every torpedo slot. The port's `tools/check_frame.py poison` patches SIMH so that every such read loads a jump to address 0, and 1,500 frames with collisions still match the evaluator. With the ships' own slots poisoned too, SIMH stops at once, so the check can fail. Play never observes the read, and the binding carries it.

Make the tool check itself against the emulator. The Spacewar tool compares its copy of core with SIMH's at the end of each match, and its model of the word's arithmetic with SIMH's results.

## 6. Grade the port against the original

Run the RUNS source in the evaluator and the original in the emulator from the same Records, then compare every field and every output point.

1. Write a check that maps each Record field to the original's memory. The Spacewar port's `tools/pdp1.py` takes the addresses from the original's symbol table.
2. For a small routine, check every input. Spacewar's sine and cosine matched SIMH on all 2^18 input words each, in a run by hand.
3. For calc routines and Networks, check many seeded states with the edge cases. The Spacewar frame Network matched SIMH on 1,500 frames that held 4,747 collisions and 2,009,045 points.
4. Check the inputs. The Spacewar game control matched SIMH on 3,000 seeded cases, 1,226 of them starting from random power-on scores, and an evaluator field that is unknown where SIMH holds a value counts as a difference. The one exception is the `lights` Record, program flags 1 and 2, which keep what the machine held at power-on and which nothing reads.
5. Make sure each check can fail. Plant defects in the RUNS source, such as an off-by-one or a dropped random draw, and confirm the check catches each one. The Spacewar port does this with `tools/mutate.sh`.

If a loop runs past its bound, a `requires:` fails, or `unreachable` fires, the port is wrong. Fix the port. Never treat those errors as the game's behavior.

## 7. Compile with a binding

A compiler takes RUNS plus a binding for a target. With the original machine's binding, the result is the original binary, exactly.

The binding holds only choices that play cannot observe:

- Tape order. Where each routine and each Record field lies.
- Calling conventions. How each routine is entered and left, such as `jda`, `jsp`, `xct`, or a skip return.
- Storage. Which register or word carries each value.
- Code layout. Where a block of code lies when the original lays it out of order.
- Devices. Which switch, light, or start address carries each boundary field.

A binding holds no game logic. It has no expressions, no statements, and no number that the game computes with. The Spacewar port's binding is `pdp1/`, a TOML file for each unit plus `devices.toml`, and `pdp1/README.md` defines its vocabulary.

The Spacewar compiler, `tools/runsc.py`, writes the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` compiles that C to a tape image. `runsc` refuses RUNS that `runs.check` rejects, a binding key it does not know, a key it needs that no binding gives, a name the RUNS text does not have, and a read of a shared word that holds another name. It lays code out by rules of its own, keyed on the shape of the RUNS text.

Prove that the RUNS text, not the binding, decides the image. The Spacewar port's `tools/check_compiled.py` mutates the RUNS of every routine and field that a binding compiles. Among other mutations, it changes each number, each field reference, each operator, and each enum member, deletes each statement, and swaps each pair of adjacent statements. Each mutant must change the image, be refused by `runsc` or the evaluator, or be shown the same game. A mutant is the same game when it is the same text, or when it fires the same as the original on 200 seeded Record states and at least 50 of those firings run clean through the mutated routine. It also deletes each binding key, which must change the image or be refused, so no key is dead.

A unit counts as ported when all of these pass:

1. `runsc` prints `MATCH`.
2. `check_compiled` passes.
3. Each RUNS routine of the unit matches the original in the emulator, over every input or over a seeded sample with the edge cases.
4. The checks of earlier units still pass. In the Spacewar port, `tools/check_all.sh` runs them all.

## Assets

Assets, such as art and sound, are the concern of AEMS, a separate protocol. Spacewar's ship outlines and star catalog are data on the tape, so the port keeps them in the RUNS text as Records. Conceptually they are assets.

*MIT License. Open for implementation, extension, and critique.*
