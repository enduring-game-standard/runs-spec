# RUNS Network topology

> Every accepted example on this page loads in RUNS-Spacewar's evaluator, `tools/runs.py`, passes `runs.check`, and runs. Every rejected example fails with the error its first line quotes. [Check the examples](./README.md#check-the-examples) says how. Blocks tagged `net` are network files, copied from RUNS-Spacewar's `runs/`. `tools/check_examples.py` does not run them. RUNS-Spacewar's own checks load and run them.

A `.runs` file declares the game's state and its structure. It holds types, enums, Records, streams, and Networks in the inline form. A `.net` file holds one Network as a graph, as [Network files](#network-files) describes. Processors live in `.runs-prim` files and are described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md). Records live in `.runs` files, each Processor in a `.runs-prim` file of its own, and each Network in a `.net` file, wired to the Records and Processors it names. RUNS-Spacewar's loader still accepts any declaration in either kind of file, a looser rule than the source follows.

## The net

A Network is the game's colored Petri net. Records are the places, field values are the tokens, Processors are the transitions, and guarded arcs are the gates ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Network). A Network is the explicit wiring of Record fields to Processors' inputs and outputs, and its wires and guards state the order of execution (GLOSSARY.md, Network). A network file writes that graph down. It lists places, transitions, and arcs, with no separate list of steps. A drawing of RUNS transcribes the files and adds no grouping or layout rule of its own. A tangle in the drawing is coupling in the code.

- No value goes from one Processor straight to another. Each value one rule hands to the next goes through a Record field that the Network names.
- A Processor names no Record. It declares inputs and outputs, and they are its whole contract. Records and Processors are mutually opaque, and only the Network knows both sides (GLOSSARY.md, Processor and Network). Two Processors with the same inputs and outputs can be swapped.
- A Network that another uses as a transition is a **bundle**. It declares inputs and outputs the same way, and wires them on to the routines it runs. Only a top Network names Records. A bundle names only its inputs and outputs and places of its own, so it can be wired into another game. RUNS-Spacewar's network files still let a bundle list Record fields among its places, and its bundles do, so none of them can be shared yet ([Open questions](./README.md#open-questions)). Seen from outside, a bundle is a Sub-Network, a Network used as a Processor (GLOSSARY.md, Sub-Network).
- Processors connect only through the Network, by way of Records, and composition is bundling (GLOSSARY.md, Network). An expression calls only the machine description's operators and the instruction constructors of `type insn`, never a routine.
- A Network writes nothing. It wires each input and output of each transition to a place, chooses with guards, and repeats in loop bundles.
- The original's order is part of the game, and the wires and guards carry it. [Order](#order) states the rule the loader enforces, and [Where the order comes from](./README.md#where-the-order-comes-from) says why it is the whole order.

## A running example

The examples on this page together form one program, a reduced version of Spacewar's object loop. Each object slot holds a calc routine. A torpedo counts down its life, drifting on each axis, and then explodes. An explosion plots a cloud of dots and then frees its slot. A switch on the console comes in from outside the game. While the operator holds it on, no new torpedo launches, and the busy light goes off.

## Declarations

### Types

A program's machine types come from its [machine description](./MACHINE_DESCRIPTION.md). A `.runs` file names the machine with a `machine` line, and every type that is not a count, a condition, or an enum is a type that description defines:

```text
machine pdp1
```

For Spacewar, that is `word`, the game's number. That a word is 18 bits in ones' complement is a rule of Spacewar, and the RUNS source states it exactly: [The PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) gives each operator a body, and the [DIGS reference](./DIGS_EXPRESSION_LANGUAGE.md#the-word) summarizes them.

`type insn` is a word of code, and a field of type `insn` is impure. The language parses it only for source that keeps code in a Record, as an earlier RUNS-Spacewar outline did. `instructions:` lists the original machine's instructions that the source builds. The evaluator knows the rules of `lac`, `lio`, `dac`, `dio`, `add`, `sub`, `jmp`, `stf`, `clf`, `szf`, `rcl`, `cma`, `ioh`, and `dpy`, and refuses any other. `display:` names the stream that `dpy` plots on. [A Record holds no code](./DIGS_EXPRESSION_LANGUAGE.md#a-record-holds-no-code) says why the loader counts each use as an impurity, and [Instructions are not part of the description](./MACHINE_DESCRIPTION.md#instructions-are-not-part-of-the-description) says where instruction encodings belong.

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

Members are written without the enum's name, as in `objects.routine[slot] == torpedo`. An enum value can only be compared with `==` and `!=`. It has no number visible to RUNS. The target's declarations decide how it is encoded.

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

game record warpage
  acceleration: word = 0    # what drift adds to a velocity

game record explosion_count
  particles: word = 0       # dots left to plot, counting up

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
- A slot is one entry of a collection, never an input or output. A field of a collection takes its index after the field name, as in `objects.x[slot]`, never `objects[slot].x`. A slot past the last is an error.
- A field's type is a type of the machine description, such as the PDP-1's `word`, or an enum. A field of type `insn` parses, and it is impure.
- The initial value is an expression that touches no Record. A field of a collection whose line ends in `=` takes one initial value a slot, one indented line each.
- A field with no initial value is unknown until the game sets it or the world gives it. Reading it while it is unknown is an error. That is how the source says what comes in from outside the game, such as the console's switches and the words core held at power-on.
- Global data is a Record like any other. RUNS has no separate kind for it.

Records are organized by meaning, not by where the original kept a value. A value the original carried in a register from one rule to the next is a field of the Record of the concern it belongs to, named for what it means, as `warpage.acceleration` below. Which register held it is the machine's, and the declarations say so. [Map each routine to Processors and Networks](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) states the rule.

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

The three kinds are the enduring-games pattern: `game` marks a Rules-region Record, `presentation` a Realization-region one, and `interface` a boundary Record (GLOSSARY.md, Processor). The pattern is a convention, not a base primitive of RUNS (GLOSSARY.md, Processor). RUNS-Spacewar's loader enforces it as this project's own rule.

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

The loader refuses a program that breaks these rules, and a Record with no kind breaks them. A conversion in progress reads its source with the purity report, which lists every impurity rather than stopping at the first. RUNS-Spacewar's report is `tools/check_purity.py`. [Give each Record a kind](./CONVERSION_PROCESS.md#5-give-each-record-a-kind-and-split-each-processor-by-it) says how a conversion splits its Processors and checks the split.

## Network files

A network file, `name.net`, states one Network as a graph. RUNS source writes Networks as network files. It lists the Network's places, its transitions, and the arcs between them, with no separate list of steps: the wires and guards state the order. RUNS-Spacewar writes every Network as a network file, every Processor in a `.runs-prim` file of its own, and its Records in `.runs` files. Its loader, `tools/graph.py`, reads each network file, checks it, and lowers it to the inline form that [Networks](#networks) describes. The evaluator runs the lowered Network.

### An example

Spacewar's cosine adds a quarter turn to the angle and takes the sine, as the original's `cos` does. This is `runs/arithmetic/cosine.net`, without its comment:

```net
network cosine
  in angle: word
  out result: word

places
  cosine_work.shifted

transitions
  shift: add_half_pi
  sine: sine

arcs
  angle -> shift.angle
  shift.shifted -> cosine_work.shifted
  cosine_work.shifted -> sine.angle
  sine.result -> result
```

`shift` is the Processor `add_half_pi`, and `sine` is a bundle with its own network file. `shift` gives `cosine_work.shifted` and `sine` takes it, so `shift` fires first. The file would mean the same with its transitions or its arcs in another order.

### Parts of a network file

A network file has a header and three sections. The header is the `network` line and the indented lines under it. Each section starts with its name on a line of its own, `places`, `transitions`, or `arcs`, and holds one entry an indented line. A comment runs from `#` to the end of the line.

| Header line | Meaning |
|-------------|---------|
| `network name` | The Network's name. Another network file uses it as a transition by this name. |
| `network name(slot)` | A Network that takes a slot from the transition that runs it. Its arcs use the slot to name one entry of a collection, as in `table[slot].routine`. |
| `in name: kind`, `out name: kind`, `inout name: kind` | An input or output, as on a Processor. Its kind is a type, an enum, `type[N]`, or the name of a Record or stream, which the input or output then holds whole. |
| `counter name: type` | The counter of a loop bundle. [Loop bundles](#loop-bundles) describes its forms. |
| `requires: a, b` and `produces: a, b` | On a top Network, the Records the host writes before it fires and reads after (GLOSSARY.md, Boundary Record). They lower to `reads:` and `writes:`. |
| `requires: condition` | A precondition, as in [Headers](#headers). |
| `assumes: place != member` | A precondition that a tested place never holds the member, so the test needs no side for it. |

| Section | Entry | Meaning |
|---------|-------|---------|
| `places` | `record.field`, `record.field[slot]` | A field of a Record, or one slot of it, that an arc names. |
| `places` | `name: kind` | A place of the Network's own that holds a whole Record, a whole field of a collection, or a stream. |
| `transitions` | `label: Processor` | A Processor that fires under this label. One Processor may fire under several labels. |
| `transitions` | `label: network` | Another network file, used as one transition. This is how bundles nest. |
| `transitions` | `label: name(slot)` | A Processor or network that takes a slot, with the slot or a number passed to it. |
| `arcs` | `place -> label.input` | The place's value goes to the input. |
| `arcs` | `label.output -> place` | The output's value goes to the place. |
| `arcs` | `place -> label` | The transition touches the place but has no input or output for it. The arc orders the transition as a wire would, and passes no value. A routine that touches the place by name, such as one that still declares its Records, needs it. |
| `arcs` | `place -> label when test` | A guard. The transition fires only on that side of the test. |

An input or output of the Network is a place too, named by itself (`angle`). An arc may name one entry of a place that holds a whole Record (`table[slot].dy`). A place that only arcs name needs no `places` line when it is an input or output of the Network, an entry of one, or an entry of one of the Network's own places.

### Each input and output wired once

Each input and output of each transition is wired exactly once, to a place of its kind. A `copy` may take and give a whole Record. An `inout` takes one place and gives one, the same place or another. An input of the Network is never written inside it. Each output of the Network is given by some arc. A place listed under `places` and wired to nothing is an error.

### Guards

The guards on one place form a partition. Exactly one side is true (GLOSSARY.md, Phase / Dispatch / Guard). The sides are one of these:

- A test and its else: `when < 0` and `when else`.
- An n-way dispatch: `when == m` for distinct members or numbers, then `when else`.
- On an enum, `when == m` for every member, with no else. A member that an `assumes:` line rules out needs no side.

A value of a type that is not an enum always needs its `when else`. A side `when != m` beside a side `when == m` is every side but `m`, not a second test. A test may compare its place with another place: `tally.first -> show when != tally.second`.

A guard only tests. A condition that needs arithmetic is a Processor that computes it into a place, and the guard tests that place. Only the first transition on a side needs a guard arc. A transition with no guard arc fires on the side whose transitions give its inputs.

### Order

Order comes only from the wires and the guards, never from names or the order of lines. One tick of the Rules region is a DAG of firings, and any topological order of it yields identical results (GLOSSARY.md, Network), so transitions that share no place may fire in parallel. RUNS-Spacewar's loader reads one order from the wires and guards, lowers the file to an inline Network in that order, and its evaluator fires one transition at a time. A transition fires after the transitions that give the places it reads, and after the transition that gives the place its guard tests. Several transitions may give one place. The wiring orders each two of them by a path from one to the other, or puts them on two sides of one test. The loader refuses two that it leaves unordered. A reader reads the value of the latest writer before it. A transition that takes a place and gives its result back to the same place fires after the place's earlier writers.

A transition may be `stop` in place of a Processor. It halts the machine, as Spacewar does when its object table has no free slot.

### Loop bundles

A loop bundle repeats its transitions. It declares one counter, `counter name: type`, an input set before the loop starts. A `count_down` transition takes the counter and gives it back one nearer its end, and no other transition writes it. Each pass fires every transition once and takes one token. The loop ends when the counter reaches 0, or after a pass in which a guard keeps the `count_down` from firing. Each `inout` of the bundle holds one value a pass, and the bundle's user sees the final values. The bundle's user sees one transition, never the cycle (GLOSSARY.md, Network). A place that a parent wires to a counter is the loop bundle's alone: no other transition of the parent reads it.

This is Spacewar's wait for a ship in the star, `runs/spaceship/wait_in_star.net`, without its comment. It takes one token a pass and does nothing else:

```net
network wait_in_star
  counter wait: word

transitions
  take: count_down                                          # count \ssn, .

arcs
  wait -> take.counter
  take.counter -> wait
```

Spacewar's counters hold minus the passes left, so its `count_down` adds 1. A counter has these forms:

| Form | Meaning |
|------|---------|
| `counter name: type` | The user sets the count. |
| `counter name: type = -count` | The bundle states the most passes it makes, and no user sets it. It needs a guard on its `count_down`, which stops the loop before the count runs out. |
| `counter name: type to end` | The counter counts up to an end, such as the slots of a collection. The passes may read it, and the user sees where it stopped. |
| `counter name: first .. last` | The counter walks the slots from `first` to `last`, a dispatch over a collection (GLOSSARY.md, Phase / Dispatch / Guard). Each pass's transitions take it as their slot, and no user sets it. |

### Grammar of a network file

```text
net_file    = "network" NAME [ "(" NAME { "," NAME } ")" ] { indented net_header }
              [ "places" { indented net_place } ]
              [ "transitions" { indented transition } ]
              [ "arcs" { indented arc } ]
net_header  = ( "in" | "out" | "inout" ) NAME ":" KIND
            | "counter" NAME ":" TYPE [ "=" NUMBER | "to" VALUE ]
            | "counter" NAME ":" expression ".." expression
            | ( "requires" | "produces" ) ":" NAME { "," NAME }
            | "requires" ":" expression
            | "assumes" ":" end "!=" NAME
net_place   = end | NAME ":" KIND
transition  = NAME ":" NAME [ "(" VALUE { "," VALUE } ")" ]
arc         = end "->" NAME [ "." NAME ]
            | NAME "." NAME "->" end
            | end "->" NAME "when" test
test        = "else" | OPERATOR ( VALUE | end )
end         = NAME [ "[" VALUE "]" ] [ "." NAME [ "[" VALUE "]" ] ]
```

`KIND` is a type, an enum, `type[N]`, or the name of a Record or stream. `OPERATOR` is a comparison of the [DIGS expressions](./DIGS_EXPRESSION_LANGUAGE.md#expressions). An arc's end is a transition when its first name is a label under `transitions`, so a label never has the name of a Record.

## Networks

This section describes the inline form of a Network, written in a `.runs` file. It states its order line by line. The inline form is what the loader lowers a network file to, and the evaluator runs it. RUNS source is written as network files, and RUNS-Spacewar has no inline Network left. The examples on this page use the inline form only because `tools/check_examples.py` runs only `runs` and `runs-prim` blocks, not `net` blocks.

A Network has a name, optional inputs and outputs, optional headers, and a body. The top Network, `frame`, walks the object slots and names the Records. Every Network below it is a bundle, which names only its inputs and outputs:

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
      run dim
        busy: lights.busy
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
        acceleration: warpage.acceleration
        particles: explosion_count.particles
        points: display

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
  inout acceleration: word
  inout particles: word
  inout points: display
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
  inout acceleration: word
  inout points: display
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
      x: shown

network drift
  inout velocity: word
  inout position: word
  inout acceleration: word                                  # AC into the inertia macro: cla
  run coast
    value: acceleration
  run inertia
```

### Inputs and outputs

An input or output is a header line, `direction name: kind`, the same on a Processor and on a Network. It replaces `reads:` and `writes:`. The loader's messages and code call each one a Port, as in `expand_ports`. In the EGS vocabulary a Port is the same game on other hardware, made by swapping its Realization Processors (GLOSSARY.md, Port).

| Direction | Meaning |
|-----------|---------|
| `in name: kind` | The routine reads the field wired here and never sets it. |
| `out name: kind` | The routine sets the field wired here. |
| `inout name: kind` | The routine reads the field wired here and sets it. |

An input or output carries one place. Its kind says how much: a type of the machine description or an enum, such as `word` or `calc_routine`, takes one word or one slot (`objects.x[slot]`); `type[N]`, such as `word[4]`, takes a whole field of a collection of N, and the routine indexes it itself, with the index as another input. The name of a Record or a stream, such as `display`, takes it whole: a Processor that emits takes its stream this way. A routine with inputs and outputs names no Record, takes no parameters, and has no `reads:` or `writes:`. Its body names only its inputs and outputs and its locals.

### Wires

A `run` wires each input and output of the routine it fires, one per indented line, `port: field`. The field is a field of a Record, a slot of one, a whole Record or stream, or an input or output of the Network that runs it. Each input and output is wired exactly once. A wire to a field of the same name may be left out: `run inertia` in `drift` wires `velocity` to `drift`'s input `velocity`, `position` to its `position`, and `acceleration` to its `acceleration`. `run torpedo` in `calc` leaves out every wire.

A bundle is a Sub-Network: a Network used as a Processor from outside, with typed inputs and outputs at its boundary, whose content references its parts by ID. There is no privileged sub-network entity, only regions of one graph at different zoom levels (GLOSSARY.md, Sub-Network and Network). In the inline form a bundle collapsed is `run name` and its wires. Expanded, it is its own lines. In a network file it is one transition, and expanded it is its own file. A bundle's input or output wired to an outer one resolves through to the field the top Network wires: the first `run drift` in `torpedo` moves `objects.dx[slot]` and `objects.x[slot]`, and the second moves `objects.dy[slot]` and `objects.y[slot]`. Any bundle, from one Processor up to the whole game, can be read and published alone, because its inputs and outputs are its whole contract.

Values between Processors stay Records that the Network names. A `let` stays local to one Processor, and no local outlives the firing.

Each distinct wiring of a routine is one copy of it: its source with each input and output replaced by the field wired to it, by reference, the way the original's macros were expanded at each use (Spacewar's `diff` once an axis). The evaluator runs the copies, and a compiler emits one copy a wiring, or one shared subroutine where the target's declarations call it, as [Declarations](./DECLARATIONS.md#conventions) states. The loader names each copy after its routine and a number, as in `inertia_1`.

### A Network's own field

The loader still reads `owns name: kind`, a field that only one Network touches, from an earlier form of the source. A conversion does not write it. A value one Processor hands to another is a field of a Record: the Processor takes it out, computes, and puts it back, and the next Processor takes it from there.

### Headers

| Header | Meaning |
|--------|---------|
| `reads: a, b` | Records the top Network's contract says come in from outside it. |
| `writes: a, b` | Records and streams the top Network's contract says leave it. |
| `requires: condition` | A precondition. If it is false when the Network fires, the RUNS source is wrong. |

A network file names a top Network's boundary Records with `requires:`, the inbound Records the host writes before the tick, and `produces:`, the outbound ones it reads after (GLOSSARY.md, Boundary Record). The loader lowers them to the inline form's `reads:` and `writes:`. A precondition is a DIGS boolean a routine declares (GLOSSARY.md, Precondition). The header line shows which `requires:` is meant: a list of Records, or a condition.

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
| `loop at most N:` | Fire the body again and again until a guard breaks out. Running more than N passes means the RUNS source is wrong. |
| `break` | Leave the innermost `loop`. Valid only inside a `loop`. |
| `stop` | The machine halts, and halts again each time the operator continues it. Nothing after it fires. |
| `wait` | Hand the firing to the world in the middle of a firing. The loader still reads it, from an earlier form. RUNS source does not use it: nothing computes between ticks, and a halt the operator continues past ends the tick. |
| `unreachable` | Mark a path the game never takes. Reaching it means the RUNS source is wrong. |

A Dispatch is a bounded fold whose count is fixed before it starts, with no `break`, `continue`, or early return (GLOSSARY.md, Phase / Dispatch / Guard). `for` has that shape. `loop at most N:` with `break` does not, and network files write a loop as a loop bundle instead. The inline form's `if` fires its first true arm and may omit `else`, while `match` must cover every member of its enum; a network file's guards partition, as [Guards](#guards) states.

An inline guard compares values that Records hold, with each other or with constants, and joins comparisons with `and`, `or` and `not`. A bundle's guard tests its inputs and outputs, which are fields. It uses the expression syntax of [DIGS](./DIGS_EXPRESSION_LANGUAGE.md#expressions), so word comparisons follow the word's rules. Arithmetic inside a slot's index chooses a slot and is allowed. Arithmetic on a value belongs in a Processor, as [Guards](#guards) states.

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

An input or output that no wire reaches is refused, when the Network that runs it has no input or output of its name:

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

One Network fires the game's Processors and the presentation's in one order. `plot` above is the presentation's, and `torpedo` runs it between the game's steps. With the presentation removed, `torpedo` is `count_down`, `explode`, `drift` twice and `show` in the same order.

### Halts, hangs, and exit points

A halt or a hang that the original reaches is part of the game's rules. A halt that halts again when continued is `stop`. A halt that the operator continues past emits what it shows and ends the tick, and a Record the tick produces makes the next tick the operator's answer. [Spacewar's rules and the machine](./README.md#spacewars-rules-and-the-machine) gives Spacewar's two halts.

An exit point is not a halt. It is where play leaves an edition: the state and the step past which the edition states nothing and the original binary alone governs ([GLOSSARY.md](https://github.com/enduring-game-standard/.github/blob/main/GLOSSARY.md), Exclusion). The original keeps running past it, so it is not `stop`, and the RUNS source is not wrong there, so it is not `unreachable`. RUNS has no form for an exit point yet. Which form a network file uses to state one is a work item. Spacewar's edition has no exclusions, so its source has no exit point.

### The Network loop

This is the one statement of the loop rule; other pages point here. Every loop is bounded, and the only unbounded loop is the tick feedback through `state:` Records (GLOSSARY.md, Network). Every loop within a tick runs through a counter Record set before the loop starts: each pass consumes one token, and the loop ends when the counter reaches zero or a guard stops it. This is a rule for the whole graph, and a loop need not sit in a bundle of its own (owner, 2026-11-14). RUNS-Spacewar's loader reads a loop only as a [loop bundle](#loop-bundles) (a network file with a `counter` line), so every loop in its source is one; reading a counter loop anywhere in a graph is tool work still to do.

The inline form, which network files lower to, has its own Network loop, described below.

A loop in a Network must hold, among its own statements, an `if` with an arm that ends in `break`. That `if` is the loop's exit. The arm may fire things before it breaks. By convention, the exit's guard reads fields that the Processors in the body write. The loader does not check this. A Processor that the original ran inside a loop, such as a macro, becomes a Network loop that fires it. The explosion's dot loop is the model. The dots left to plot are `particles`, which the frame wires to `explosion_count.particles`:

```runs
network explosion
  inout routine: calc_routine
  inout counter: word
  in x: word
  in shift: word
  inout number: word
  out dot: word
  inout particles: word                                     # dots left to plot, counting up
  inout points: display
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

Here totality comes from the bound on the loop. A bounded fold has no `break` (GLOSSARY.md, Phase / Dispatch / Guard), so a network file writes this loop as a loop bundle.

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
  in x: word
  inout points: display
  emit points: x, 1

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
  in dot: word
  inout points: display
  emit points: dot, 3

processor free_slot
  out routine: calc_routine
  set routine = none

processor dim
  out busy: light
  set busy = off
```

`plot` and `plot_particle` take the stream `display` as an `inout` and emit to it by that name. Each bundle on the way passes the stream on, from the frame, which wires it to `display`. `show` copies the torpedo's x into `sight`, and `plot` reads it there. `scatter` leaves the dot in `particle`, an interface Record, and `plot_particle` reads it there.

## Network contracts

A bundle's contract is its inputs and outputs. A top Network names Records, so its contract is the Records it declares under `reads:` and `writes:`: they cross its boundary, and every other Record the routines inside it touch belongs to it.

The loader checks the contract of every Network that has a `reads:` or `writes:` header, and of every top Network. A Network in the form a conversion starts from, with no inputs or outputs, may declare one too. A **top Network** is one that nothing fires. A game may have several. Spacewar has three. The host fires one of its two start Networks once, when the operator starts the machine, and then fires `tick` once each tick. Together the top Networks are one game, so a Record they share does not cross the boundary. Their contracts are what crosses between the program and the world: what comes in, and what the presentation sends out.

For a checked Network, "inside" means the Network and every routine it fires, directly or through sub-Networks, each copy with its inputs and outputs replaced by the fields wired to them. A Processor that nothing fires does not count as outside. The loader enforces six rules:

1. A Record that a Processor inside writes must be in `writes:` if a Processor outside also touches it, or if it is a stream.
2. A Record that is read inside, but not written inside, must be in `reads:` or `writes:` if a Processor outside touches it. Reads by guards count.
3. Each Record in `writes:` must be written by a Processor inside.
4. Each Record in `reads:` must be read inside, by a guard or by a Processor that declares it under `reads:` or `writes:`.
5. A top Network must declare under `reads:` each Record with a field that has no initial value, if a routine inside reads that Record.
6. A top Network must declare under `writes:` each Record that a Processor inside writes and nothing in the game reads. Such a Record only leaves the game, as Spacewar's console lights do.

In the example, `frame` is the top Network. Every Processor is inside it, so only the stream leaves it, and `lights`, which nothing reads. `console` has a field with no initial value, and the frame's guard reads it, so `console` comes in. `explosion` and `drift` are bundles: their inputs and outputs are their contracts.

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

As it loads the source, the loader checks each routine's inputs and outputs and each `run`'s wires, and makes one copy of a routine for each distinct wiring. Before anything runs, `runs.check` checks the shape of each kind, the names each copy and each other routine uses, and the contracts. While a routine runs, the evaluator checks each Processor's Record accesses, every read of an unknown field, and every bound.

| Error | When |
|-------|------|
| `a network only fires and chooses (set)` | A Network uses `let`, `set`, `emit`, `return`, `continue`, or `jump`. |
| `a network loop needs an exit: an if with an arm that ends in break` | A Network `loop` has no `if` with an arm that ends in `break`. |
| `break outside a loop` | A Network uses `break` outside a `loop`. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network`, `wait belongs to a network` | A Processor uses `run`, `match`, `stop`, or `wait`. |
| `... defined twice` | Two routines share a name. |
| ``a Port is `direction name: kind`, the kind a type or type[N]`` | An input's or output's header line is not `direction name: kind`. |
| `... names ... twice` | A routine declares two inputs or outputs, or one and its own field (`owns`), of one name. |
| `...: no kind ...` | An input's or output's kind is not a type or an enum. |
| `its ... has a Record's name` | An input, an output, or a Network's own field has the name of a Record. |
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
| `its Port ... is not wired, and ... has no Port or scratch ...` | An input or output has no wire, and the Network that runs it has no input, output or own field of its name. |
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

The loop bound, `requires:`, and `unreachable` errors never describe the game. If one of them fires, the RUNS source is wrong.

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

`machine_line` and `layout` are in the [machine description's grammar](./MACHINE_DESCRIPTION.md#grammar). A field whose line ends in `=` takes one indented expression a slot. A routine has inputs and outputs or a parameter list, not both. A `wire`'s `place` is a field, a slot of one, a whole Record or stream, or an input or output of the Network the `run` stands in. Names have no namespace prefix. `processor` is described in [DIGS expression language](./DIGS_EXPRESSION_LANGUAGE.md#grammar).

*MIT License. Open for implementation, extension, and critique.*
