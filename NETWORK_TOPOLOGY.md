# RUNS Network topology

> **Status.** Working draft. This reference describes the `.runs` syntax that RUNS-Spacewar's reference evaluator, `tools/runs.py`, accepts and enforces. The whole of Spacewar! 3.1 is written in this syntax. Every accepted example on this page loads in that evaluator, passes `runs.check`, and runs. Every rejected example fails with the error quoted in its first line. `tools/check_examples.py` checks both.

A `.runs` file declares the game's state and its structure. It holds types, enums, Records, streams, and Networks. Processors live in `.runs-prim` files and are described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md). The loader reads every declaration kind from either kind of file, so the split between the two is a convention.

## The text is the net

The RUNS text is the game's Petri net. Records are the places. Processors are the transitions. A Network says which transitions fire, in what order, and under what conditions. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own. A tangle in the drawing is coupling in the code.

- No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record.
- RUNS has no functions. A Processor cannot call a Processor, and an expression cannot call a routine. The only calls are the word's own operators and the instruction constructors of `type insn`.
- A Network writes nothing. It fires Processors and other Networks, chooses with guards, and repeats with bounded loops.
- Firing is sequential. A Network fires its statements in the order written, and each Processor sees every write made before it. A compiler may derive concurrency from the declared reads and writes. Concurrency is not part of the model.

The order is part of the game. In Spacewar's main loop, object *i* is tested against every later colliding object, and then *i*'s calc routine runs in the same frame on the changed state, before object *i+1* is touched. Moving the collision test into its own phase after all objects move changes 294 of 300 test frames.

## A running example

The examples on this page together form one program, a reduced version of Spacewar's object loop. Each object slot holds a calc routine. A torpedo counts down its life and then explodes. An explosion plots a cloud of dots and then frees its slot. A switch on the console comes in from outside the game. While the operator holds it on, no new torpedo launches, and the frame waits.

## Declarations

### Types

A `type` declaration describes a type of the original machine. The loader reads `type insn` and skips every other `type` declaration:

```runs
type word
  bits: 18
  complement: ones          # -0 exists; add and subtract are the PDP-1's
  compare: sign             # word < 0 tests the sign bit; == compares all 18 bits
```

- `type word` is a comment to the reader. The evaluator defines `word`, the PDP-1's 18-bit ones' complement word, in code. The [DIGS reference](./DIGS_EXPRESSION_LANGUAGE.md#the-word) describes what `word` does.
- `type insn` is a word of code, and a field of type `insn` is impure. The language still parses it only because an unfinished conversion, Spacewar's outline, still uses it. `instructions:` lists the original machine's instructions that the text builds. The evaluator knows the rules of `lac`, `lio`, `dac`, `dio`, `add`, `sub`, `jmp`, `stf`, `clf`, `szf`, `rcl`, `cma`, `ioh`, and `dpy`, and refuses any other. `display:` names the stream that `dpy` plots on. [A Record holds no code](./DIGS_EXPRESSION_LANGUAGE.md#a-record-holds-no-code) says why the loader counts each use as an impurity.

How a game states the original machine's types as text, rules included, is an open question.

### Enums

An `enum` lists its members, one per indented line:

```runs
enum calc_routine
  none                      # a free slot
  torpedo
  explosion

enum switch
  off
  on

enum light
  off
  on
```

Members are written without the enum's name, as in `objects.routine[slot] == torpedo`. An enum value can only be compared with `==` and `!=`. It has no number visible to RUNS. The binding decides how the target spells it.

Two enums may share a member's name, as `switch` and `light` share `off` and `on`. The name means the member of the enum that the value is compared with or stored as.

### Records

A `record` declares something the game remembers. Each indented line is a field with a name, a type, and an optional initial value.

```runs
interface record objects[4]
  routine: calc_routine = none
  x: word = 0
  counter: word = 0         # frames left, counting up toward 0
  dx: word = 0

game record random
  number: word = 0

game record motion
  acceleration: word = 0    # added to an object's velocity; AC into the inertia macro

game record cloud
  particles: word = 0       # dots left to plot, counting up

interface record particle
  x: word = 0               # where the explosion puts its next dot

interface record console
  hold: switch              # no initial value: the operator sets it

interface record lights
  busy: light = off

game record spreads[4]
  shift: word =             # one initial value a slot
    1
    3
    1
    3
```

- Each Record starts with its kind: `game`, `interface`, or `presentation`. [Three kinds of Record](#three-kinds-of-record) states what each kind allows.
- `record name` holds one value of each field.
- `record name[N]` holds N values of each field. The count is a number literal. A number with a leading `0` is octal, so `[030]` is 24.
- A field of a collection takes its index after the field name, as in `objects.x[slot]`, never `objects[slot].x`. A slot past the last is an error.
- A field's type is `word` or an enum. A field of type `insn` parses, and it is impure.
- The initial value is an expression that touches no Record. A field of a collection whose line ends in `=` takes one initial value a slot, one indented line each.
- A field with no initial value is unknown until the game sets it or the world gives it. Reading it while it is unknown is an error. That is how the text says what comes in from outside the game, such as the console's switches and the words core held at power-on.
- Global data is a Record like any other. RUNS has no separate kind for it.

Records are organized by meaning, not by where the original kept a value. A value the original carried in a register from one routine to the next, such as the acceleration above, is a field of the Record of the concern it belongs to, named for what it means. A comment may name the register and the instruction. No Record collects the values that pass through one register. Spacewar's `handoff` Record does, so it is impure by this rule, and its conversion splits it.

### Streams

A `stream` is ordered output. Each `emit` in a Processor appends one entry. A stream field's type is `word` or `int`, where `int` is a count.

```runs
presentation stream display
  x: word
  intensity: int
```

A stream has a kind, as a Record does. Every stream leaves to a device, so every stream is presentation, and a Processor that emits to a stream is presentation too. A stream of another kind does not load:

```runs-prim-rejected
# rejected: stream score: a stream leaves to a device, so it is a presentation stream
game record points
  value: word = 0

game stream score
  value: word

network frame
  writes: score
  run show

processor show
  reads: points
  writes: score
  emit score: points.value
```

### Three kinds of Record

A game Record holds what only the rules use. An interface Record holds what the game and its presentation share: what the game writes for the presentation to show, and what the world writes for the game to read. A presentation Record belongs to one platform.

A Processor that touches a presentation Record is part of the presentation. Every other Processor is part of the game. The loader enforces three rules:

1. A presentation Processor touches no game Record.
2. A presentation Processor writes no interface Record. Only the game and the world write the interface.
3. A guard that reads a presentation Record guards only the presentation's routines. A Network that fires only presentation routines is part of the presentation too.

Together these make the presentation removable. Delete every presentation Processor and every run of one, and the game's Records are the same at every step. A new platform replaces the presentation whole and changes nothing in the game.

In the example, the explosion's next dot is the game's, because it draws from the random number that the rest of the game also draws from. The game writes the dot to `particle`, and the presentation plots it:

```runs-prim-rejected
# rejected: processor plot_particle: touches the presentation's display and the game's random; split it, or give the game's value to an interface record
game record random
  number: word = 0

presentation stream display
  x: word

processor plot_particle
  reads: random
  writes: display
  emit display: random.number >> 3
```

The presentation may not hand anything back to the game through the interface:

```runs-prim-rejected
# rejected: processor plot_particle: the presentation writes the interface record particle; only the game and the world write it
interface record particle
  x: word = 0

presentation stream display
  x: word

processor plot_particle
  writes: particle, display
  emit display: particle.x
  set particle.x = 0
```

A game rule may not depend on the presentation's state through a guard either:

```runs-rejected
# rejected: network frame: a guard reads the presentation's budget, and the game's advance runs under it
presentation record budget
  left: word = 0

game record clock
  ticks: word = 0

network frame
  run spend
  if budget.left >= 0:
    run advance

processor spend
  writes: budget
  set budget.left = budget.left + 1

processor advance
  writes: clock
  set clock.ticks = clock.ticks + 1
```

A conversion proves its split by observation. It runs the game with every presentation Processor removed against the original, and every game Record must match.

The loader enforces these rules on a program whose Records all have kinds, so a finished conversion is checked with no switch to remove. A conversion gives its Records kinds as it converts them. Until the last one has a kind, the conversion's purity report lists every remaining impurity, and nothing is exempt from it. RUNS-Spacewar's report is `tools/check_purity.py`.

## Networks

A Network has a name, optional parameters, optional headers, and a body.

```runs
network frame
  reads: console
  writes: display, lights
  if objects.routine[0] == none:
    if console.hold == off:
      run launch
    else:
      wait
  for slot in 0 .. 3:
    if objects.routine[slot] != none:
      run calc(slot)

network calc(slot)
  match objects.routine[slot]:
    none: unreachable
    torpedo: run torpedo(slot)
    explosion: run explosion(slot)

network torpedo(slot)
  run count_down(slot)
  if objects.counter[slot] >= 0:
    run explode(slot)
  else:
    run coast
    run inertia(slot)
    run plot(slot)
```

### Headers

| Header | Meaning |
|--------|---------|
| `reads: a, b` | Records the Network's contract says come in from outside it. |
| `writes: a, b` | Records and streams the Network's contract says leave it. |
| `requires: condition` | A precondition. If it is false when the Network fires, the RUNS text is wrong. |

[Network contracts](#network-contracts) describes what the loader checks about `reads:` and `writes:`.

### Statements

A Network body may hold only these statements.

| Statement | Meaning |
|-----------|---------|
| `run name` or `run name(a, b)` | Fire a Processor or a Network. Each argument is an expression, evaluated before the routine fires. |
| `if g:` ... `elif g:` ... `else:` | Fire the first arm whose guard is true. |
| `for i in a .. b:` | Fire the body once for each count from `a` to `b`, both included, in ascending order. If `b` is less than `a`, the body does not fire. The bounds may use an outer index. |
| `match e:` | Fire the arm named by the enum value `e`. Each arm is `member: statement` on one line, or `member:` followed by an indented block. |
| `loop at most N:` | Fire the body again and again until a guard breaks out. Running more than N passes means the RUNS text is wrong. |
| `break` | Leave the innermost `loop`. Valid only inside a `loop`. |
| `stop` | The machine halts, and halts again each time the operator continues it. Nothing after it fires. |
| `wait` | Hand the firing to the world. The host shows what has left the game, may change what comes in, and then the firing goes on. |
| `unreachable` | Mark a path the game never takes. Reaching it means the RUNS text is wrong. |

A guard is any expression that writes nothing. It can read any Record and use any operator, arithmetic included. It uses the expression syntax of [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#expressions), so word comparisons follow the word's rules. One guard from RUNS-Spacewar is `if (random.number | 0400000) + ships.uncertainty[slot] >= 0:`.

A Network has no `let`, `set`, `emit`, `return`, `continue`, or `jump`.

A Network fires the game's Processors and the presentation's in one order. `plot` above is the presentation's, and `torpedo` runs it between the game's steps. With the presentation removed, `torpedo` is `count_down`, `explode`, `coast` and `inertia` in the same order.

A halt or a hang that the original reaches is a rule of the game. Spacewar halts when a ship fires and the object table is full, and the conversion writes that halt as `stop`. Spacewar also halts between games to show the scores on the console lights, and the operator may flip switches before continuing. The conversion writes that halt as an `emit` of the scores to a stream, then `wait`.

### The Network loop

A loop in a Network must hold, among its own statements, an `if` with an arm that ends in `break`. That `if` is the loop's exit. The arm may fire things before it breaks. By convention, the exit's guard reads Records that the Processors in the body write. The loader does not check this. A Processor that the original ran inside a loop, such as a macro, becomes a Network loop that fires it. The explosion's dot loop is the model:

```runs
network explosion(slot)
  writes: objects, display
  run size_cloud
  loop at most 0400001:
    run next_random
    run scatter(slot)
    run plot_particle
    if cloud.particles >= 0:
      break
  run count_down(slot)
  if objects.counter[slot] >= 0:
    run free_slot(slot)
```

Totality comes from the bound on each loop, not from forbidding `break`.

### The Processors of the example

These Processors complete the running example. [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) describes their syntax.

```runs-prim
processor launch
  writes: objects, lights
  set objects.routine[0] = torpedo
  set objects.counter[0] = -2
  set objects.dx[0] = 5
  set lights.busy = on

processor count_down(slot)
  writes: objects
  set objects.counter[slot] = objects.counter[slot] + 1

processor explode(slot)
  writes: objects
  set objects.routine[slot] = explosion
  set objects.counter[slot] = -2

processor coast
  writes: motion
  set motion.acceleration = 0

processor inertia(slot)
  reads: motion
  writes: objects
  set objects.dx[slot] = motion.acceleration + objects.dx[slot]
  set objects.x[slot] = (objects.dx[slot] >> 3) + objects.x[slot]

processor plot(slot)
  reads: objects
  writes: display
  emit display: objects.x[slot], 1

processor size_cloud
  writes: cloud
  set cloud.particles = -3

processor next_random
  writes: random
  set random.number = (rar(random.number, 1) ^ 0355670) + 0355670

processor scatter(slot)
  reads: random, objects, spreads
  writes: cloud, particle
  set particle.x = (random.number >> spreads.shift[slot]) + objects.x[slot]
  set cloud.particles = cloud.particles + 1

processor plot_particle
  reads: particle
  writes: display
  emit display: particle.x, 3

processor free_slot(slot)
  writes: objects
  set objects.routine[slot] = none
```

## Network contracts

A Network can state a contract the way a Processor does. The Records it declares cross its boundary. Every other Record its Processors touch belongs to it.

The loader checks the contract of every Network that has a `reads:` or `writes:` header, and of every top Network. A **top Network** is one that nothing fires. A game may have several. Spacewar has three. The host fires one of its two start Networks once, when the operator starts the machine, and then fires the frame once each frame. Together the top Networks are one game, so a Record they share does not cross the boundary. Their contracts are what crosses between the program and the world: what comes in, and what the presentation sends out.

For a checked Network, "inside" means the Network and every routine it fires, directly or through sub-Networks. A Processor that nothing fires does not count as outside. The loader enforces five rules:

1. A Record that a Processor inside writes must be in `writes:` if a Processor outside also touches it, or if it is a stream.
2. A Record that is read inside, but not written inside, must be in `reads:` or `writes:` if a Processor outside touches it. Reads by guards count.
3. Each Record in `writes:` must be written by a Processor inside.
4. Each Record in `reads:` must be read inside, by a guard or by a Processor that declares it under `reads:` or `writes:`.
5. A top Network must declare under `reads:` each Record with a field that has no initial value, if a routine inside reads that Record.
6. A top Network must declare under `writes:` each Record that a Processor inside writes and nothing in the game reads. Such a Record only leaves the game, as Spacewar's console lights do.

In the example, `explosion` declares `writes: objects, display`. Processors outside it, such as `launch`, also touch `objects`, and `display` is a stream. `random` and `cloud` are touched only inside `explosion`, so they belong to it and stay out of its contract. `frame` is the top Network. Every Processor is inside it, so only the stream leaves it, and `lights`, which nothing reads. `console` has a field with no initial value, and the frame's guard reads it, so `console` comes in.

A top Network that writes a stream must declare it. Without `writes: display`, the Spacewar frame does not load:

```runs-rejected
# rejected: display leaves it; declare writes: display
presentation stream display
  x: word

network frame
  run plot_point

processor plot_point
  writes: display
  emit display: 0
```

A top Network that reads a field with no initial value must declare its Record. Spacewar's `start_with_test_word` does not load without `reads: score`, and this frame does not load without `reads: console`:

```runs-rejected
# rejected: console comes in from outside the game
interface record console
  launch: word

network frame
  if console.launch == 0:
    stop
```

A declared Record that nothing inside uses is also an error:

```runs-rejected
# rejected: declares reads: ['random'], but nothing inside reads them
game record random
  number: word = 0

network idle
  reads: random
  stop
```

Which device holds each field that comes in or goes out is not part of RUNS. The binding for each machine states it. RUNS-Spacewar's PDP-1 binding states every console switch, light, and start address in one file, `pdp1/devices.toml`.

## What the loader and the evaluator reject

Before anything runs, `runs.check` checks the shape of each kind, the names each routine uses, and the contracts. While a routine runs, the evaluator checks each Processor's Record accesses, every read of an unknown field, and every bound.

| Error | When |
|-------|------|
| `a network only fires and chooses (set)` | A Network uses `let`, `set`, `emit`, `return`, `continue`, or `jump`. |
| `a network loop needs an exit: an if with an arm that ends in break` | A Network `loop` has no `if` with an arm that ends in `break`. |
| `break outside a loop` | A Network uses `break` outside a `loop`. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network`, `wait belongs to a network` | A Processor uses `run`, `match`, `stop`, or `wait`. |
| `... defined twice` | Two routines share a name. |
| `... is no routine`, `... takes N arguments` | A `run` names a routine that does not exist, or passes the wrong number of arguments. |
| `a match's arms are members of one enum` | A `match` has arms from no enum or from several. |
| `nothing in the game reads ..., so it leaves the game; declare writes: ...` | A top Network does not declare a Record that only leaves the game (rule 6). |
| `... leaves it; declare writes: ...` and the other contract errors | A contract breaks one of the rules in [Network contracts](#network-contracts). |
| `... comes in from outside the game` | A top Network does not declare a Record with a field that has no initial value, and a routine inside reads it. |
| `... initial values for N slots` | A field with one initial value a slot has the wrong number of lines. |
| `the machine has no rules for [...]` | `type insn` lists an instruction the evaluator does not know. |
| `stream ...: a stream leaves to a device, so it is a presentation stream` | A program whose Records all have kinds declares a stream that is not presentation. |
| `match misses [...]` (also in `runs.check`) | A `match` that fires has no arm for some member of the enum. |
| `... is unknown: the game has not set it, so the world gives it` | A routine reads a field with no initial value before the game sets it or the world gives it. |
| `loop ran past its bound` | A `loop` runs more passes than its bound. |
| `precondition fails` | A `requires:` is false when its routine fires. |
| `reached unreachable` | An `unreachable` fires. |

A Network that writes a Record is rejected before it runs:

```runs-rejected
# rejected: a network only fires and chooses
record frame
  spare_time: word = 0

network begin
  set frame.spare_time = -04000
```

So is a Network loop without an exit:

```runs-rejected
# rejected: a network loop needs an exit
network forever
  loop at most 10:
    stop
```

The loop bound, `requires:`, and `unreachable` errors never describe the game. If one of them fires, the RUNS text is wrong.

## Grammar

This summary describes what `tools/runs.py` accepts. Indentation is two spaces a level. A comment runs from `#` to the end of the line. `expression` is the [DIGS expression](./DIGS_EXPRESSION_LANGUAGE.md#expressions).

```text
file        = { declaration }
declaration = type | enum | record | stream | network | processor
type        = "type" "insn" { indented ( "instructions" ":" NAME { NAME } | "display" ":" NAME ) }
            | "type" NAME { indented line }                  (skipped by the loader)
enum        = "enum" NAME { indented NAME }
record      = kind "record" NAME [ "[" NUMBER "]" ] { indented field }
stream      = kind "stream" NAME { indented field }
kind        = "game" | "interface" | "presentation"
field       = NAME ":" TYPE [ "=" ( expression | { indented expression } ) ]
network     = "network" NAME [ "(" NAME { "," NAME } ")" ] { indented ( header | net_stmt ) }
header      = "reads" ":" NAME { "," NAME }
            | "writes" ":" NAME { "," NAME }
            | "requires" ":" expression
net_stmt    = "run" NAME [ "(" [ expression { "," expression } ] ")" ]
            | "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ]
            | "for" NAME "in" expression ".." expression ":" block
            | "match" expression ":" { indented NAME ":" ( net_stmt | block ) }
            | "loop" "at" "most" expression ":" block
            | "break" | "stop" | "wait" | "unreachable"
block       = { indented net_stmt }
```

A field whose line ends in `=` takes one indented expression a slot. Names have no namespace prefix. `processor` is described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md#grammar).

## Open questions

- The syntax is a working draft. It holds what Spacewar needed and will change as other games are converted.
- The Network side of purity depends on the Network's form, which is not decided. Three questions are open. May a guard compute, as the RUNS-Spacewar guard above does, or only test values that Records hold? May a `run` pass values as arguments, as `run calc(slot)` does, or must every value go through a Record? Is the firing order authored in the text, as on this page, or derived from the wiring of reads and writes?
- RUNS has no text form yet for the original-machine description. The loader skips `type word`, and the evaluator holds the word's rules and the instructions' rules in code.
- RUNS has no syntax yet for stating a Record's layout where play reads it. Spacewar's play reads no layout, so its conversion did not need one.
- Names have no namespaces, and how RUNS text is named and shared is not decided.

*MIT License. Open for implementation, extension, and critique.*
