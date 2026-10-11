# RUNS Network topology

> **Status.** Working draft. This reference describes the `.runs` syntax that the Spacewar port's reference evaluator, `tools/runs.py`, accepts and enforces. Every accepted example on this page loads in that evaluator, passes its contract check, and runs. Every rejected example fails with the error quoted in its first line.

A `.runs` file declares the game's state and its structure: types, enums, Records, streams, and Networks. Processors live in `.runs-prim` files and are described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md). The loader reads every declaration kind from either kind of file, so the split between the two is a convention.

## The topology is a Petri net

Records are the places. Processors are the transitions. A Network says which transitions fire, in what order, and under what conditions.

- No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record.
- RUNS has no functions. A Processor cannot call a Processor, and an expression cannot call a routine. The only calls are the word's own operators.
- A Network writes nothing. It fires Processors and other Networks, chooses with guards, and repeats with bounded loops.
- Firing is sequential. A Network fires its statements in the order written, and each Processor sees every write made before it. A compiler may derive concurrency from the declared reads and writes. Concurrency is not part of the model.

The order is part of the game. In Spacewar's main loop, object *i* is tested against every later colliding object, and then *i*'s calc routine runs in the same frame on the changed state, before object *i+1* is touched. Moving the collision test into its own phase after all objects move changes 294 of 300 test frames.

## A running example

The examples on this page together form one program, a reduced version of the Spacewar port's object loop. Each object slot holds a calc routine. A torpedo counts down its life and then explodes. An explosion plots a cloud of dots and then frees its slot.

## Declarations

### Types

A `type` declaration describes a type of the original machine:

```runs
type word
  bits: 18
  complement: ones          # -0 exists; add and subtract are the PDP-1's
  compare: sign             # word < 0 tests the sign bit; == compares all 18 bits
```

The loader skips `type` declarations and their indented lines. The evaluator defines `word`, the PDP-1's 18-bit ones' complement word, in code. How a game states the original machine's types as text is an open question. The [DIGS reference](./DIGS_EXPRESSION_LANGUAGE.md#the-word) describes what `word` does.

### Enums

An `enum` lists its members, one per indented line:

```runs
enum calc_routine
  none                      # a free slot
  torpedo
  explosion
```

Members are written without the enum's name, as in `objects.routine[slot] == torpedo`. An enum value can only be compared with `==` and `!=`. It has no number visible to RUNS. The binding decides how the target spells it.

### Records

A `record` declares something the game remembers. Each indented line is a field: its name, its type, and an optional initial value.

```runs
record objects[4]
  routine: calc_routine = none
  x: word = 0
  counter: word = 0         # frames left, counting up toward 0
  dx: word = 0

record random
  number: word = 0

record handoff
  acceleration: word = 0    # what the original carries in AC into its inertia macro

record cloud
  particles: word = 0       # dots left to plot, counting up
```

- `record name` holds one value of each field.
- `record name[N]` holds N values of each field. The count is a number literal. A number with a leading `0` is octal, so `[030]` is 24.
- A field of a collection takes its index after the field name, as in `objects.x[slot]`, never `objects[slot].x`.
- A field's type is `word` or an enum. The loader does not check the type name.
- The initial value is an expression that touches no Record. A field with no initial value starts as the word 0.
- Global data is a Record like any other. RUNS has no separate kind for it.

A field that exists only because the original passed a value in a register, such as `handoff.acceleration`, says so in a comment that names the register and the instruction.

### Streams

A `stream` is ordered output. Each `emit` in a Processor appends one entry. A stream field's type is `word` or `int`, where `int` is a count.

```runs
stream display
  x: word
  intensity: int
```

## Networks

A Network has a name, optional parameters, optional headers, and a body.

```runs
network frame
  writes: display
  if objects.routine[0] == none:
    run launch
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
| `requires: expression` | A precondition. If it is false when the Network fires, the port is wrong. |

[Network contracts](#network-contracts) describes what the loader checks about `reads:` and `writes:`.

### Statements

A Network body may hold only these statements.

| Statement | Meaning |
|-----------|---------|
| `run name` or `run name(a, b)` | Fire a Processor or a Network. Each argument is an expression, evaluated before the routine fires. |
| `if g:` ... `elif g:` ... `else:` | Fire the first arm whose guard is true. |
| `for i in a .. b:` | Fire the body once for each count from `a` to `b`, both included, in ascending order. If `b` is less than `a`, the body does not fire. The bounds may use an outer index. |
| `match e:` | Fire the arm named by the enum value `e`. Each arm is `member: statement` on one line, or `member:` followed by an indented block. |
| `loop at most N:` | Fire the body again and again until a guard breaks out. Running more than N passes means the port is wrong. |
| `break` | Leave the innermost `loop`. Valid only inside a `loop`. |
| `stop` | End this pass of the top Network. Nothing after it fires. |
| `unreachable` | Mark a path the game never takes. Reaching it means the port is wrong. |

A guard is any expression that writes nothing. It can read any Record and use any operator, arithmetic included. It uses the expression syntax of [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#expressions), so word comparisons follow the word's rules. One guard from the Spacewar port is `if (random.number | 0400000) + ships.uncertainty[slot] >= 0:`.

A Network has no `let`, `set`, `emit`, `return`, or `continue`.

### The Network loop

A loop in a Network must hold, among its own statements, an `if` whose only statement is `break`. That `if` is the loop's exit. By convention, its guard reads Records that the Processors in the body write. The loader does not check this. A Processor that the original ran inside a loop, such as a macro, becomes a Network loop that fires it. The explosion's dot loop is the model:

```runs
network explosion(slot)
  writes: objects, display
  run size_cloud(slot)
  loop at most 0400001:
    run next_random
    run plot_particle(slot)
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
  writes: objects
  set objects.routine[0] = torpedo
  set objects.counter[0] = -2
  set objects.dx[0] = 5

processor count_down(slot)
  writes: objects
  set objects.counter[slot] = objects.counter[slot] + 1

processor explode(slot)
  writes: objects
  set objects.routine[slot] = explosion
  set objects.counter[slot] = -2

processor coast
  writes: handoff
  set handoff.acceleration = 0

processor inertia(slot)
  reads: handoff
  writes: objects
  set objects.dx[slot] = handoff.acceleration + objects.dx[slot]
  set objects.x[slot] = (objects.dx[slot] >> 3) + objects.x[slot]

processor plot(slot)
  reads: objects
  writes: display
  emit display: objects.x[slot], 1

processor size_cloud(slot)
  writes: cloud
  set cloud.particles = -3

processor next_random
  writes: random
  set random.number = (rar(random.number, 1) ^ 0355670) + 0355670

processor plot_particle(slot)
  reads: random, objects
  writes: cloud, display
  emit display: (random.number >> 9) + objects.x[slot], 3
  set cloud.particles = cloud.particles + 1

processor free_slot(slot)
  writes: objects
  set objects.routine[slot] = none
```

## Network contracts

A Network can state a contract the way a Processor does. The Records it declares cross its boundary. Every other Record its Processors touch belongs to it.

The loader checks the contract of every Network that has a `reads:` or `writes:` header, and of every top Network. A **top Network** is one that nothing fires. It is a whole game, and its contract is the game's boundary with presentation.

For a checked Network, "inside" means the Network and every routine it fires, directly or through sub-Networks. The loader enforces four rules:

1. A Record that a Processor inside writes must be in `writes:` if a Processor outside also touches it, or if it is a stream.
2. A Record that is read inside, but not written inside, must be in `reads:` or `writes:` if a Processor outside touches it. Reads by guards count.
3. Each Record in `writes:` must be written by a Processor inside.
4. Each Record in `reads:` must be read inside, by a Processor or a guard.

In the example, `explosion` declares `writes: objects, display`. Processors outside it, such as `launch`, also touch `objects`, and `display` is a stream. `random` and `cloud` are touched only inside `explosion`, so they belong to it and stay out of its contract. `frame` is the top Network. Every Processor is inside it, so only the stream crosses its boundary.

A top Network that writes a stream must declare it. Without `writes: display`, the Spacewar frame does not load:

```runs-rejected
# rejected: display leaves it; declare writes: display
stream display
  x: word

network frame
  run plot_point

processor plot_point
  writes: display
  emit display: 0
```

A declared Record that nothing inside uses is also an error:

```runs-rejected
# rejected: declares reads: ['random'], but nothing inside reads them
record random
  number: word = 0

network idle
  reads: random
  stop
```

Values that come in, such as the controls and the words of core the game reads at power-on, also belong in the top Network's contract. The loader does not require that declaration yet, and its form is open, because the Spacewar port has not ported those inputs.

## What the loader and the evaluator reject

The loader checks the shape of every routine before anything runs. While a routine runs, the evaluator checks every Record access.

| Error | When |
|-------|------|
| `a network only fires and chooses (set)` | A Network uses `let`, `set`, `emit`, `return`, or `continue`. |
| `a network loop needs an exit: if <guard>: break` | A Network `loop` has no `if` whose only statement is `break`. |
| `break outside a loop` | A Network uses `break` outside a `loop`. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network` | A Processor uses `run`, `match`, or `stop`. |
| `... defined twice` | Two routines share a name. |
| `... leaves it; declare writes: ...` and the other contract errors | A contract breaks one of the rules in [Network contracts](#network-contracts). |
| `match misses [...]` | A `match` that fires has no arm for some member of the enum. |
| `loop ran past its bound` | A `loop` runs more passes than its bound. |
| `precondition fails` | A `requires:` is false when its routine fires. |
| `reached unreachable` | An `unreachable` fires. |
| `... is not ported` | A `run` names a routine that does not exist. |

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

The loop bound, `requires:`, and `unreachable` errors never describe the game. If one of them fires, the port is wrong. A halt or a hang that the original reaches is a rule of the game and must be ported as one. How a port writes a halt is open.

## Grammar

This summary describes what `tools/runs.py` accepts. Indentation is two spaces a level. A comment runs from `#` to the end of the line. `expression` is the [DIGS expression](./DIGS_EXPRESSION_LANGUAGE.md#expressions).

```text
file        = { declaration }
declaration = type | enum | record | stream | network | processor
type        = "type" NAME { indented line }                  (skipped by the loader)
enum        = "enum" NAME { indented NAME }
record      = "record" NAME [ "[" NUMBER "]" ] { indented field }
stream      = "stream" NAME { indented field }
field       = NAME ":" TYPE [ "=" expression ]
network     = "network" NAME [ "(" NAME { "," NAME } ")" ] { indented ( header | net_stmt ) }
header      = "reads" ":" NAME { "," NAME }
            | "writes" ":" NAME { "," NAME }
            | "requires" ":" expression
net_stmt    = "run" NAME [ "(" [ expression { "," expression } ] ")" ]
            | "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ]
            | "for" NAME "in" expression ".." expression ":" block
            | "match" expression ":" { indented NAME ":" ( net_stmt | block ) }
            | "loop" "at" "most" expression ":" block
            | "break" | "stop" | "unreachable"
block       = { indented net_stmt }
```

Names have no namespace prefix. `processor` is described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md#grammar).

## Open questions

- The syntax is a working draft. It holds what one slice of Spacewar needed and will change as more is ported.
- RUNS has no text form yet for the original-machine description, so the loader skips `type` declarations.
- RUNS has no syntax yet for stating a Record's layout where play reads it.
- Inputs belong in the top Network's contract. The form of that declaration, and what the loader checks about it, is not decided.
- How a port writes a halt or a hang the original reaches is not decided.

*MIT License. Open for implementation, extension, and critique.*
