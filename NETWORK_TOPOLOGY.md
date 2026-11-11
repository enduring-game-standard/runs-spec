# RUNS Network topology

> Every accepted example on this page loads in RUNS-Spacewar's evaluator, `tools/runs.py`, passes `runs.check`, and runs. Every rejected example fails with the error its first line quotes. [Check the examples](./README.md#check-the-examples) says how.

A `.runs` file declares the game's state and its structure. It holds types, enums, Records, streams, and Networks. Processors live in `.runs-prim` files and are described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md). The loader reads every declaration kind from either kind of file, so the split between the two is a convention.

## The net

A Network is the game's colored Petri net. Records are the places, field values are the tokens, Processors are the transitions, and guarded arcs are the gates ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md) 188-189). A Network is the explicit wiring of Record fields to Processors' inputs and outputs, and execution order is derived from that wiring, never authored (CONTEXT.md 162-170, 197-199). Today's Network text falls short of the graph: it says which transitions fire, in what order, and under what conditions, as structured code. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own. A tangle in the drawing is coupling in the code.

- No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record field that the Network names.
- A Processor names no Record. It declares inputs and outputs, and they are its whole contract. Records and Processors are mutually opaque, and only the Network knows both sides (CONTEXT.md 166-169). Two Processors with the same inputs and outputs can be swapped.
- Only a top Network names Records. Every other Network is a **bundle**: it declares inputs and outputs the same way, and wires them on to the routines it runs. Seen from outside, a bundle is a Sub-Network, a Network used as a Processor (CONTEXT.md 229-231).
- Today's RUNS has no functions. A Processor cannot call a Processor, and an expression cannot call a routine. The only calls are the machine description's operators and the instruction constructors of `type insn`. The vision allows a DIGS sub-Processor call inside a body, which is not a Network edge: its result is a body-local, never a Record (CONTEXT.md 172-186).
- A Network writes nothing. Today it fires Processors and other Networks, wires each input and output of each one to a field, chooses with guards, and repeats with bounded loops.
- In the vision, one tick of the Rules region is a DAG, and any topological order of it yields identical results, so a runtime may run it in parallel (CONTEXT.md 193-199). Today firing is sequential: a Network fires its statements in the order written, and each Processor sees every write made before it.

The original's order is part of the game. [Where the order comes from](./README.md#where-the-order-comes-from) says how today's text states it and how the vision derives it.

## A running example

The examples on this page together form one program, a reduced version of Spacewar's object loop. Each object slot holds a calc routine. A torpedo counts down its life, drifting on each axis, and then explodes. An explosion plots a cloud of dots and then frees its slot. A switch on the console comes in from outside the game. While the operator holds it on, no new torpedo launches, and the frame waits.

## Declarations

### Types

A program's machine types come from its [machine description](./MACHINE_DESCRIPTION.md). A `.runs` file names the machine with a `machine` line, and every type that is not a count, a condition, or an enum is a type that description defines:

```text
machine pdp1
```

For Spacewar, that is `word`, the game's number. That a word is 18 bits in ones' complement is a rule of Spacewar, and the RUNS text states it exactly: [The PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) gives each operator a body, and the [DIGS reference](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes them.

`type insn` is a word of code, and a field of type `insn` is impure. The language parses it only for a text that keeps code in a Record, as Spacewar's outline does. `instructions:` lists the original machine's instructions that the text builds. The evaluator knows the rules of `lac`, `lio`, `dac`, `dio`, `add`, `sub`, `jmp`, `stf`, `clf`, `szf`, `rcl`, `cma`, `ioh`, and `dpy`, and refuses any other. `display:` names the stream that `dpy` plots on. [A Record holds no code](./DIGS_EXPRESSION_LANGUAGE.md#a-record-holds-no-code) says why the loader counts each use as an impurity, and [Instructions are not part of the description](./MACHINE_DESCRIPTION.md#instructions-are-not-part-of-the-description) says where instruction encodings belong.

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

Members are written without the enum's name, as in `objects.routine[slot] == torpedo`. An enum value can only be compared with `==` and `!=`. It has no number visible to RUNS. The target's declarations decide how it is spelled.

Two enums may share a member's name, as `switch` and `light` share `off` and `on`. The name means the member of the enum that the value is compared with or stored as.

### Records

A `record` declares something the game remembers. Each indented line is a field with a name, a type, and an optional initial value.

```runs
interface record objects[4]
  routine: calc_routine = none
  x: word = 0
  counter: word = 0         # frames left, counting up toward 0
  dx: word = 0
  y: word = 0
  dy: word = 1

game record random
  number: word = 0

interface record particle
  x: word = 0               # where the explosion puts its next dot

interface record sight
  x: word = 0               # where the torpedo is drawn

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
- `record name[N]` holds N values of each field. The count is a number literal, read by the machine description's [literal forms](./MACHINE_DESCRIPTION.md#literals). On the PDP-1 a leading `0` is octal, so `[030]` is 24.
- A field of a collection takes its index after the field name, as in `objects.x[slot]`, never `objects[slot].x`. A slot past the last is an error.
- A field's type is a type of the machine description, such as the PDP-1's `word`, or an enum. A field of type `insn` parses, and it is impure.
- The initial value is an expression that touches no Record. A field of a collection whose line ends in `=` takes one initial value a slot, one indented line each.
- A field with no initial value is unknown until the game sets it or the world gives it. Reading it while it is unknown is an error. That is how the text says what comes in from outside the game, such as the console's switches and the words core held at power-on.
- Global data is a Record like any other. RUNS has no separate kind for it.

Records are organized by meaning, not by where the original kept a value. A value the original carried in a register from one rule to the next is a field the Network names: a field of the Record of the concern it belongs to when it is read outside the Network, or the Network's own scratch when only that Network touches it, as the acceleration of `drift` below. [Map each routine to Processors and Networks](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) states the rule.

### Streams

A `stream` is ordered output. Each `emit` in a Processor appends one entry. A stream field's type is a type of the machine description or `int`, where `int` is a count.

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

The three kinds are the enduring-games pattern: `game` marks a Rules-region Record, `presentation` a Realization-region one, and `interface` a boundary Record (CONTEXT.md 131-160). The pattern is a convention, not a base primitive of RUNS (CONTEXT.md 133-134, 159-160). RUNS-Spacewar's loader enforces it as this project's own rule.

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
# rejected: network frame: a guard reads the presentation's budget, and the game's advance
presentation record budget
  left: word = 0

game record clock
  ticks: word = 0

network frame
  run spend
    left: budget.left
  if budget.left >= 0:
    run advance
      ticks: clock.ticks

processor spend
  inout left: word
  set left = left + 1

processor advance
  inout ticks: word
  set ticks = ticks + 1
```

The loader refuses a program that breaks these rules, and a Record with no kind breaks them. A conversion in progress reads its text with the purity report, which lists every impurity rather than stopping at the first. RUNS-Spacewar's report is `tools/check_purity.py`. [Give each Record a kind](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) says how a conversion splits its Processors and checks the split.

## Networks

A Network has a name, optional inputs and outputs, optional headers, and a body. This is today's text form, which states the order line by line and falls short of the vision's graph, as [The net](#the-net) says. The top Network, `frame`, walks the object slots and names the Records. Every Network below it is a bundle, which names only its inputs and outputs:

```runs
network frame
  reads: console
  writes: display, lights
  if objects.routine[0] == none:
    if console.hold == off:
      run launch
        routine: objects.routine[0]
        counter: objects.counter[0]
        dx: objects.dx[0]
        busy: lights.busy
    else:
      wait
  for slot in 0 .. 3:
    if objects.routine[slot] != none:
      run calc
        routine: objects.routine[slot]
        counter: objects.counter[slot]
        x: objects.x[slot]
        dx: objects.dx[slot]
        y: objects.y[slot]
        dy: objects.dy[slot]
        shift: spreads.shift[slot]
        number: random.number
        dot: particle.x
        shown: sight.x

network calc
  inout routine: calc_routine
  inout counter: word
  inout x: word
  inout dx: word
  inout y: word
  inout dy: word
  in shift: word
  inout number: word
  out dot: word
  out shown: word
  match routine:
    none: unreachable
    torpedo: run torpedo
    explosion: run explosion

network torpedo
  inout routine: calc_routine
  inout counter: word
  inout x: word
  inout dx: word
  inout y: word
  inout dy: word
  out shown: word
  run count_down
  if counter >= 0:
    run explode
  else:
    run drift
      velocity: dx
      position: x
    run drift
      velocity: dy
      position: y
    run show
      value: x
    run plot

network drift
  inout velocity: word
  inout position: word
  owns acceleration: word                                   # AC into the inertia macro: cla
  run coast
    value: acceleration
  run inertia
```

### Inputs and outputs

An input or output is a header line, `direction name: kind`, the same on a Processor and on a Network. It replaces `reads:` and `writes:`. The loader's messages and code call each one a Port, as in `expand_ports`. In the EGS vocabulary a Port is the same game on other hardware, made by swapping its Realization Processors (CONTEXT.md 313-320).

| Direction | Meaning |
|-----------|---------|
| `in name: kind` | The routine reads the field wired here and never sets it. |
| `out name: kind` | The routine sets the field wired here. |
| `inout name: kind` | The routine reads the field wired here and sets it. |

An input or output is one field, never a whole Record. Its kind says how much of the field: a type of the machine description or an enum, such as `word` or `calc_routine`, takes one word or one slot (`objects.x[slot]`); `type[N]`, such as `word[4]`, takes a whole field of a collection of N, and the routine indexes it itself, with the index as another input. A routine with inputs and outputs names no Record, takes no parameters, and has no `reads:` or `writes:`. Its body names only its inputs and outputs, its locals, and, on a Network, its scratch.

### Wires

A `run` wires each input and output of the routine it fires, one per indented line, `port: field`. The field is a field of a Record, a slot of one, an input or output of the Network that runs it, or that Network's scratch. Each input and output is wired exactly once. A wire to a field of the same name may be left out: `run inertia` in `drift` wires `velocity` to `drift`'s input `velocity`, `position` to its `position`, and `acceleration` to its scratch `acceleration`. `run torpedo` in `calc` leaves out every wire.

In the vision a bundle is a Sub-Network: a Network used as a Processor from outside, with typed inputs and outputs at its boundary, whose content references its parts by ID. There is no privileged sub-network entity, only regions of one graph at different zoom levels (CONTEXT.md 218-236). In today's text a bundle collapsed is `run name` and its wires. Expanded, it is its own lines. A bundle's input or output wired to an outer one resolves through to the field the top Network wires: the first `run drift` in `torpedo` moves `objects.dx[slot]` and `objects.x[slot]`, and the second moves `objects.dy[slot]` and `objects.y[slot]`. Any bundle, from one Processor up to the whole game, can be read and published alone, because its inputs and outputs are its whole contract.

Values between Processors stay Records that the Network names. A `let` stays local to one Processor, and no local outlives the firing.

Each distinct wiring of a routine is one copy of it: its text with each input and output replaced by the field wired to it, by reference, the way the original's macros were expanded at each use (Spacewar's `diff` once an axis). The evaluator runs the copies, and a compiler emits one copy a wiring, or one shared subroutine where the target's declarations call it, as [Declarations](./DECLARATIONS.md#conventions) states. The loader names each copy after its routine and a number, as in `inertia_1`.

### Scratch

`owns name: kind` declares a value only that Network touches. It is one field of a type or an enum, never a collection. Each firing writes it before it reads it, so it is scratch, never memory. The Network has one shared copy, as the original kept such a value in one register: every copy of the Network uses the same field. Anything read outside the Network is an input or output, not scratch. `drift`'s acceleration is scratch: `coast` writes it, `inertia` reads it, and nothing outside `drift` sees it. Nothing outside the Network can name its scratch. Scratch is written anew in every firing, so it falls short of the vision's Records, which are written once and never overwritten (CONTEXT.md 90-92). How scratch fits the vision is open.

The evaluator holds scratch in a field of its own. A compiler keeps it where the target keeps a value between two steps. RUNS-Spacewar's PDP-1 compiler makes it a local of the routine it compiles the Network into, declared once, so it lands in AC or IO where the original kept it. A declaration names it as it names a `let` (`io = ["input_bits"]`).

### Headers

| Header | Meaning |
|--------|---------|
| `reads: a, b` | Records the top Network's contract says come in from outside it. |
| `writes: a, b` | Records and streams the top Network's contract says leave it. |
| `requires: condition` | A precondition. If it is false when the Network fires, the RUNS text is wrong. |

The vision's keywords differ. An inbound boundary Record, written by the runtime before a tick, is declared under `requires:`, and an outbound one, read after the tick, under `produces:` (CONTEXT.md 272-275). A precondition is a DIGS boolean a Processor declares (CONTEXT.md 372-384). Today's `reads:`, `writes:` and `requires:` disagree with them.

A bundle's contract is its inputs and outputs. [Network contracts](#network-contracts) describes what the loader checks about `reads:` and `writes:`.

### Statements

A Network body may hold only these statements.

| Statement | Meaning |
|-----------|---------|
| `run name`, then one `port: field` a line | Fire a Processor or a Network, with each of its inputs and outputs wired to a field. |
| `run name` or `run name(slot)` | Fire a routine with no inputs or outputs. The form with a slot is the form a conversion starts from, and the loader still reads it. |
| `if g:` ... `elif g:` ... `else:` | Fire the first arm whose guard is true. |
| `for i in a .. b:` | Fire the body once for each count from `a` to `b`, both included, in ascending order. If `b` is less than `a`, the body does not fire. The bounds may use an outer index. |
| `match e:` | Fire the arm named by the enum value `e`. Each arm is `member: statement` on one line, or `member:` followed by an indented block. |
| `loop at most N:` | Fire the body again and again until a guard breaks out. Running more than N passes means the RUNS text is wrong. |
| `break` | Leave the innermost `loop`. Valid only inside a `loop`. |
| `stop` | The machine halts, and halts again each time the operator continues it. Nothing after it fires. |
| `wait` | Hand the firing to the world. The host shows what has left the game, may change what comes in, and then the firing goes on. |
| `unreachable` | Mark a path the game never takes. Reaching it means the RUNS text is wrong. |

This is today's statement set, and parts of it fall short of the vision. `for` has the shape of the vision's Dispatch, a bounded fold whose count is fixed before it starts (CONTEXT.md 343-350). `loop at most N:` with `break` does not: a Dispatch has no `break`, `continue`, or early return, and one tick of the Rules region is a DAG (CONTEXT.md 197-199, 345-346). The vision's guards on a branch partition, exactly one true, and an open-typed discriminant needs an explicit `else` arc (CONTEXT.md 351-356). Today's `if` fires its first true arm and may omit `else`, while `match` must cover every member of its enum.

A guard only tests. It compares values that Records hold, with each other or with constants, and joins comparisons with `and`, `or` and `not`. A bundle's guard tests its inputs, its outputs and its scratch, which are fields. It uses the expression syntax of [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#expressions), so word comparisons follow the word's rules. Arithmetic inside a slot's index chooses a slot and is allowed. A condition that needs arithmetic on a value is a Processor that computes it into a Record, and the guard tests that Record. The README's [Where the order comes from](./README.md#where-the-order-comes-from) says how today's text writes the order, how each line is a place, and how the vision derives the order instead.

A `run` passes only wires. `slot` stays in the one Network that walks the slots, `frame` above, and a bundle gets `objects.x[slot]` already chosen. A slot that the game computes, such as the free slot a new torpedo takes, lives in a Record, and the walking Network wires the whole field beside it. A `run` that passes a value instead of a wire, in the form a conversion starts from, is an impurity. The loader reports a guard that computes and a `run` that passes a value, and refuses them.

A guard that computes is refused:

```runs-rejected
# rejected: a guard computes
game record clock
  ticks: word = 0

network frame
  run advance
    ticks: clock.ticks
  if clock.ticks - 010 >= 0:
    stop

processor advance
  inout ticks: word
  set ticks = ticks + 1
```

So is a `run` that hands a value to the routine it fires:

```runs-rejected
# rejected: run grow passes step as a value
game record clock
  ticks: word = 0

network frame
  run grow(3)

processor grow(step)
  writes: clock
  set clock.ticks = clock.ticks + step
```

An input or output that no wire reaches is refused, when the Network that runs it has no input, output or scratch of its name:

```runs-rejected
# rejected: its Port velocity is not wired
game record body
  x: word = 0
  dx: word = 1

network frame
  run inertia
    position: body.x

processor inertia
  inout velocity: word
  inout position: word
  set position = (velocity >> 3) + position
```

A wire's field must be of the kind of the input or output it reaches. A whole field of a collection is not one word:

```runs-rejected
# rejected: position is word, wired to body.x, word[2]
game record body[2]
  x: word = 0
  dx: word = 1

network frame
  for slot in 0 .. 1:
    run inertia
      velocity: body.dx[slot]
      position: body.x

processor inertia
  in velocity: word
  inout position: word
  set position = (velocity >> 3) + position
```

A routine never sets an `in` input:

```runs-rejected
# rejected: inertia sets velocity, an in Port
game record body
  x: word = 0
  dx: word = 1

network frame
  run inertia
    velocity: body.dx
    position: body.x

processor inertia
  in velocity: word
  inout position: word
  set velocity = velocity + 1
  set position = (velocity >> 3) + position
```

A routine with inputs and outputs names no Record:

```runs-rejected
# rejected: a routine with Ports touches only its Ports
game record body
  x: word = 0
  dx: word = 1

network frame
  run inertia
    position: body.x

processor inertia
  inout position: word
  set position = (body.dx >> 3) + position
```

A Network has no `let`, `set`, `emit`, `return`, `continue`, or `jump`.

Today a Network fires the game's Processors and the presentation's in one order. `plot` above is the presentation's, and `torpedo` runs it between the game's steps. With the presentation removed, `torpedo` is `count_down`, `explode`, `drift` twice and `show` in the same order.

A halt or a hang that the original reaches is a rule of the game, written as `stop`, or as an `emit` of what the halt shows and then `wait`. [Exact over every input](./README.md#exact-over-every-input-glitches-included) gives Spacewar's two halts.

### The Network loop

The vision has no loop inside a tick. One tick of the Rules region is a DAG, the only unbounded loop is the tick feedback through `state:` Records, and a Dispatch is a bounded fold with no `break` (CONTEXT.md 197-199, 204-206, 343-347). Today's text has a Network loop, and this section describes it. How a loop whose exit depends on data is expressed in the vision is open.

A loop in a Network must hold, among its own statements, an `if` with an arm that ends in `break`. That `if` is the loop's exit. The arm may fire things before it breaks. By convention, the exit's guard reads fields that the Processors in the body write. The loader does not check this. A Processor that the original ran inside a loop, such as a macro, becomes a Network loop that fires it. The explosion's dot loop is the model. The dots left to plot are its scratch:

```runs
network explosion
  inout routine: calc_routine
  inout counter: word
  in x: word
  in shift: word
  inout number: word
  out dot: word
  owns particles: word                                      # dots left to plot, counting up
  run size_cloud
  loop at most 0400001:
    run next_random
    run scatter
    run plot_particle
    if particles >= 0:
      break
  run count_down
  if counter >= 0:
    run free_slot
```

Today totality comes from the bound on each loop. The vision's bounded fold also has no `break` (CONTEXT.md 345-346), so this loop falls short of it.

### The Processors of the example

These Processors complete the running example. [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md) describes their syntax.

```runs-prim
processor launch
  out routine: calc_routine
  out counter: word
  out dx: word
  out busy: light
  set routine = torpedo
  set counter = -2
  set dx = 040
  set busy = on

processor count_down
  inout counter: word
  set counter = counter + 1

processor explode
  out routine: calc_routine
  out counter: word
  set routine = explosion
  set counter = -2

processor coast
  out value: word
  set value = 0

processor inertia
  in acceleration: word
  inout velocity: word
  inout position: word
  set velocity = acceleration + velocity
  set position = (velocity >> 3) + position

processor show
  in value: word
  out shown: word
  set shown = value

processor plot
  reads: sight
  writes: display
  emit display: sight.x, 1

processor size_cloud
  out particles: word
  set particles = -3

processor next_random
  inout number: word
  set number = (rar(number, 1) ^ 0355670) + 0355670

processor scatter
  in number: word
  in shift: word
  in x: word
  inout particles: word
  out dot: word
  set dot = (number >> shift) + x
  set particles = particles + 1

processor plot_particle
  reads: particle
  writes: display
  emit display: particle.x, 3

processor free_slot
  out routine: calc_routine
  set routine = none
```

`plot` and `plot_particle` keep `reads:` and `writes:`, because they emit to a stream, and a stream is not a field an output can carry. `show` copies the torpedo's x into `sight` for `plot`, as `scatter` leaves the dot in `particle`. How a stream passes through an output is an [open question](./README.md#open-questions).

## Network contracts

A bundle's contract is its inputs and outputs. A top Network names Records, so its contract is the Records it declares under `reads:` and `writes:`: they cross its boundary, and every other Record the routines inside it touch belongs to it.

The loader checks the contract of every Network that has a `reads:` or `writes:` header, and of every top Network. A Network in the form a conversion starts from, with no inputs or outputs, may declare one too. A **top Network** is one that nothing fires. A game may have several. Spacewar has three. The host fires one of its two start Networks once, when the operator starts the machine, and then fires the frame once each frame. Together the top Networks are one game, so a Record they share does not cross the boundary. Their contracts are what crosses between the program and the world: what comes in, and what the presentation sends out.

For a checked Network, "inside" means the Network and every routine it fires, directly or through sub-Networks, each copy with its inputs and outputs replaced by the fields wired to them. A Processor that nothing fires does not count as outside. The loader enforces six rules:

1. A Record that a Processor inside writes must be in `writes:` if a Processor outside also touches it, or if it is a stream.
2. A Record that is read inside, but not written inside, must be in `reads:` or `writes:` if a Processor outside touches it. Reads by guards count.
3. Each Record in `writes:` must be written by a Processor inside.
4. Each Record in `reads:` must be read inside, by a guard or by a Processor that declares it under `reads:` or `writes:`.
5. A top Network must declare under `reads:` each Record with a field that has no initial value, if a routine inside reads that Record.
6. A top Network must declare under `writes:` each Record that a Processor inside writes and nothing in the game reads. Such a Record only leaves the game, as Spacewar's console lights do.

In the example, `frame` is the top Network. Every Processor is inside it, so only the stream leaves it, and `lights`, which nothing reads. `console` has a field with no initial value, and the frame's guard reads it, so `console` comes in. `explosion` and `drift` are bundles: their inputs and outputs are their contracts, and their scratch is touched by nothing outside them.

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

Which device holds each field that comes in or goes out is not part of RUNS. Each machine's declarations state it, under [Events and devices](./DECLARATIONS.md#events-and-devices).

## What the loader and the evaluator reject

As it loads the text, the loader checks each routine's inputs and outputs and each `run`'s wires, and makes one copy of a routine for each distinct wiring. Before anything runs, `runs.check` checks the shape of each kind, the names each copy and each other routine uses, and the contracts. While a routine runs, the evaluator checks each Processor's Record accesses, every read of an unknown field, and every bound.

| Error | When |
|-------|------|
| `a network only fires and chooses (set)` | A Network uses `let`, `set`, `emit`, `return`, `continue`, or `jump`. |
| `a network loop needs an exit: an if with an arm that ends in break` | A Network `loop` has no `if` with an arm that ends in `break`. |
| `break outside a loop` | A Network uses `break` outside a `loop`. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network`, `wait belongs to a network` | A Processor uses `run`, `match`, `stop`, or `wait`. |
| `... defined twice` | Two routines share a name. |
| ``a Port is `direction name: kind`, the kind a type or type[N]`` | An input's or output's header line is not `direction name: kind`. |
| `... names ... twice` | A routine declares two inputs or outputs, or one and its scratch, of one name. |
| `...: no kind ...` | An input's or output's kind is not a type or an enum. |
| `its ... has a Record's name` | An input, an output, or scratch has the name of a Record. |
| `only a Network owns scratch` | A Processor declares `owns`. |
| `scratch is one field, not ...` | An `owns` line names a collection's kind, `type[N]`. |
| `its Ports are its contract; it declares no reads: or writes:` | A routine with inputs and outputs declares `reads:` or `writes:`. |
| `a routine with Ports takes no slot; its wires choose the field` | A routine with inputs and outputs takes parameters. |
| `names the Record ...; a routine with Ports touches only its Ports` | A routine with inputs and outputs names a Record or a stream. |
| `... is a Port of ..., not a local` | A `let` or a `for` binds the name of an input or output. |
| `... sets ..., an in Port` | A routine sets its own `in` input. |
| `a run passes wires, one a line, and nothing after its routine's name`, `a wire is port: field` | A `run` with wires also passes a slot, or a wire line is not `port: field`. |
| `...'s ... is wired twice` | A `run` wires one input or output twice. |
| `... has no Ports to wire` | A `run` wires a routine with no inputs or outputs. |
| `... has Ports: a run wires them and passes no slot` | A `run` passes a slot to a routine with inputs and outputs. |
| `... has no Port ...` | A wire names an input or output the routine lacks. |
| `its Port ... is not wired, and ... has no Port or scratch ...` | An input or output has no wire, and the Network that runs it has no input, output or scratch of its name. |
| `... is out, wired to ...'s in Port ...`, the same for `inout` | A Network wires its own `in` input to an input or output the routine it runs may set. |
| `... is wired to ..., which is no field` | A wire names something that is not a field, or a slot of one. |
| `... is word, wired to ..., word[N]` and the other kinds | A wire's field is not of the kind of the input or output it reaches. |
| `its wires name ..., which ... names itself` | A wire's slot uses a name that the routine it wires uses for a local of its own. |
| `... fires itself` | A routine fires itself, through its copies too. A recursion is written as a stack Record and a bounded Network loop. |
| `... is no routine`, `... takes N arguments` | A `run` names a routine that does not exist, or passes the wrong number of slots to a routine with no inputs or outputs. |
| `a match's arms are members of one enum` | A `match` has arms from no enum or from several. |
| `nothing in the game reads ..., so it leaves the game; declare writes: ...` | A top Network does not declare a Record that only leaves the game (rule 6). |
| `... leaves it; declare writes: ...` and the other contract errors | A contract breaks one of the rules in [Network contracts](#network-contracts). |
| `... comes in from outside the game` | A top Network does not declare a Record with a field that has no initial value, and a routine inside reads it. |
| `... initial values for N slots` | A field with one initial value a slot has the wrong number of lines. |
| `the machine has no rules for [...]` | `type insn` lists an instruction the evaluator does not know. |
| `stream ...: a stream leaves to a device, so it is a presentation stream` | A stream has a kind other than presentation. |
| `...: say whether it is a game, interface or presentation record` | A Record has no kind. |
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

This grammar describes a `.runs` file. Indentation is two spaces a level. A comment runs from `#` to the end of the line. `expression` is the [DIGS expression](./DIGS_EXPRESSION_LANGUAGE.md#expressions).

```text
file        = { declaration }
declaration = machine_line | layout | type | enum | record | stream | network | processor
type        = "type" "insn" { indented ( "instructions" ":" NAME { NAME } | "display" ":" NAME ) }
enum        = "enum" NAME { indented NAME }
record      = kind "record" NAME [ "[" NUMBER "]" ] { indented field }
stream      = kind "stream" NAME { indented field }
kind        = "game" | "interface" | "presentation"
field       = NAME ":" TYPE [ "=" ( expression | { indented expression } ) ]
network     = "network" NAME [ "(" NAME { "," NAME } ")" ] { indented ( header | port | owns | net_stmt ) }
header      = "reads" ":" NAME { "," NAME }
            | "writes" ":" NAME { "," NAME }
            | "requires" ":" expression
port        = ( "in" | "out" | "inout" ) NAME ":" TYPE [ "[" NUMBER "]" ]
owns        = "owns" NAME ":" TYPE
net_stmt    = "run" NAME [ "(" [ expression { "," expression } ] ")" ]
            | "run" NAME wire { wire }
            | "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ]
            | "for" NAME "in" expression ".." expression ":" block
            | "match" expression ":" { indented NAME ":" ( net_stmt | block ) }
            | "loop" "at" "most" expression ":" block
            | "break" | "stop" | "wait" | "unreachable"
block       = { indented net_stmt }
wire        = indented NAME ":" place
place       = NAME [ "." NAME [ "[" expression "]" ] ]
```

`machine_line` and `layout` are in the [machine description's grammar](./MACHINE_DESCRIPTION.md#grammar). A field whose line ends in `=` takes one indented expression a slot. A routine has inputs and outputs or a parameter list, not both. A `wire`'s `place` is a field, a slot of one, or an input, output or scratch of the Network the `run` stands in. Names have no namespace prefix. `processor` is described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md#grammar).

*MIT License. Open for implementation, extension, and critique.*
