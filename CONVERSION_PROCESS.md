# How to port a game to RUNS

This guide ports a game to RUNS the way the Spacewar! 3.1 port (`spacewar-runs`) did. The port is verbatim. Every sequence of inputs from power-on gives the same game, glitches included. You never change the game to fit RUNS. Where RUNS cannot say what the game does, RUNS has to grow, and that is a change to this spec.

The Spacewar port has finished a slice so far: the square root, four calc routines, and the frame Network. The spaceship, the game control, and the boundary's inputs are not ported yet. Steps that depend on them are marked as open.

## Before you start

You need:

- The original program, as source or as machine code. Code with no source is ported from its machine code.
- The original running in an emulator you can script and whose state you can read. Spacewar uses SIMH running an image of the original program. The running original is the authority. Reading the source is not.
- The reference evaluator, `tools/runs.py` in the Spacewar port. It parses RUNS, enforces its rules, and runs a Network over Records.

## 1. Find every Record

A Record field is any word of the original that carries meaning from one routine to another or from one frame to the next.

1. Name each field for what it means, not for its symbol. Put the original symbol in a comment: `particles: word = 0  # mxc`.
2. Make a value that a routine sets before it reads it, and never hands on, a local of the Processor instead.
3. Keep a word that the game counts and never reads, such as Spacewar's `objects_seen`. It becomes a field that no Processor reads, and the graph shows it is dead.
4. Drop words that only the machine uses and play never observes, such as a cursor kept in an instruction's address field. They belong to the binding.
5. Keep global data in Records like any other state.

A routine word that names which code runs an object is a state. Make it an enum. In Spacewar, the calc routine word becomes `enum calc_routine`, and the sign bit that marks whether an object collides is a function of that enum.

## 2. Map each routine to Processors and Networks

The original passes values between routines in registers. RUNS passes every value through a Record. Map each way the original shares a rule:

| In the original | In RUNS |
|-----------------|---------|
| A subroutine (`jda sqt`) | A Processor over the routine's own words, which form one Record. |
| A tunable executed with `xct` | A Processor of its own. What it takes from and leaves in the registers are fields of a `handoff` Record. |
| A macro (`random`, `diff`) | A Processor. A macro that works on one axis at a time becomes one Processor per axis. |
| A loop that runs a macro or a tunable | A Network `loop at most N:` that fires the Processor and exits on a guard. |
| A routine that runs a macro or a tunable | A Network that fires Processors in the original's order. |
| A skip instruction | A Network guard that tests what the skip tests. |
| The main loop | The top Network, in the original's order. |
| A jump through a routine word | A `match` on the enum. |
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

## 3. Keep the order

The order in which the original runs its rules is part of the game. Firing in RUNS is sequential, and each Processor sees every write before it.

- Fire Processors in the order the original runs them, even when the order looks like an accident.
- Do not split a loop into phases. In Spacewar, object *i* is tested against every later colliding object and then moves, before object *i+1* is touched. A conversion that collided all objects after moving them changed 294 of 300 test frames.
- Keep dead tests and odd ranges. Spacewar's explosion tests a size that can never pass, and its last object slot is never tested for collisions. Both stay.

## 4. Split gameplay from presentation by consequence

Code is presentation only if nothing in the game can observe its effects.

1. For each piece of display, sound, or pacing code, list every Record it changes.
2. If the game reads any of those Records later, that effect is a rule. Spacewar's central star draws two random numbers each frame from the generator that hyperspace also uses, so the draws are rules. The line the star draws from them is presentation.
3. Leave presentation code where the original runs it, in the order it runs. The split decides which effects the game must keep. It does not move code.
4. Declare what crosses the boundary in the top Network's contract. Every stream the game writes must be in its `writes:`. The Spacewar frame declares `writes: display`.

Values that come in, such as the controls and the words of core the game reads at power-on, also belong in the top Network's contract. Spacewar's inputs are not ported yet, so the form of that declaration is open.

## 5. Measure where play reaches the machine

Do not guess where the game depends on the machine. Measure it by running the original through real play. The Spacewar port's `tools/reach_oracle.py` runs seventeen scripted matches in SIMH and names every data access by the Record field or source label it lands in. It reports these kinds of site:

- One instruction that reads several places, such as a read past the end of an array.
- Reads of core the program never loaded. In Spacewar, the scores and the game count start from whatever core held at power-on, and the first match reads them. Those words come in at the boundary.
- Code the program writes and then runs.
- Jumps to unnamed places.
- Halts.
- Every place the word's own machine behavior shows, such as a sum that wraps.

Then decide each site:

| What play reaches | What the port does |
|-------------------|--------------------|
| The word's arithmetic | Nothing more. The `word` type already states it. |
| A layout that play observes | State the layout in the RUNS text. RUNS has no syntax for this yet, because Spacewar has not needed one. |
| Machine instructions running from data | Use the original machine's instruction semantics on that path. RUNS has no form for this yet. |
| A halt or a hang | Port it as a rule. How to write it is open. |
| A layout that play does not observe | Leave it to the binding. |

Make the tool check itself against the emulator. The Spacewar tool compares its copy of core with SIMH's at the end of each match, and its model of the word's arithmetic with SIMH's results.

## 6. Grade the port against the original

Run the RUNS source in the evaluator and the original in the emulator from the same Records, then compare every field and every output point.

1. Write a binding that maps each Record field to the original's memory. The Spacewar port's `tools/pdp1.py` takes the addresses from the original's symbol table.
2. For a small routine, check every input. The square root matched on all 65,536 inputs.
3. For calc routines and Networks, check many states. The Spacewar frame Network matched on 1,500 frames that held 4,343 collisions.
4. Make sure each check can fail. Plant defects in the RUNS source, such as an off-by-one or a dropped random draw, and confirm the check catches each one. The Spacewar port does this with `tools/mutate.sh`.

If a loop runs past its bound, a `requires:` fails, or `unreachable` fires, the port is wrong. Fix the port. Never treat those errors as the game's behavior.

## 7. Compile with a binding

A compiler takes RUNS plus a binding for a target. The binding holds only what play cannot observe: where Records live, how enums are spelled, how scratch space is laid out. With the original machine's binding, the result should be the original binary, exactly.

In the Spacewar port, this step is in progress. The work compiles RUNS plus the PDP-1 binding to the C dialect of `spacewar-c`, which `pdp1cc` compiles to PDP-1 code to be matched by hash against the original binary. The square root compiles this way and matches the original tape image. The rest of the game does not compile yet.

## Assets

Assets, such as art and sound, are the concern of AEMS, a separate protocol.

*MIT License. Open for implementation, extension, and critique.*
