# RUNS declarations

A machine's **declarations** are the half of its package that never runs. They record where that machine keeps each value and how it calls each routine: where each routine and field lies, how each routine is entered and left, which register or word holds each value, how each enum member is spelled in bits, how code is laid out, which device carries each value that comes in or goes out, and the words the machine needs that no rule reads. They record the original programmer's arbitrary choices, never game logic. They may name game Records, because they never run. A port leaves them behind with that machine's presentation.

_Avoid_: binding. The name is retired, because it read as a layer where hard RUNS text could be solved. RUNS-Spacewar's code keeps it. `tools/runsc.py` reads the declarations into its `Bindings` class and raises `BindError`, and `tools/pdp1.py` has a `Binding` class. Read each as the declarations.

Three texts build an image. The RUNS text is the game. The [machine description](./MACHINE_DESCRIPTION.md) states the original machine's types and operators, which the RUNS text computes with. The declarations state how one target carries that RUNS text. A **compiler** for the target reads all three and writes the image. With the original machine's declarations, the image is the original binary, byte for byte. With another machine's declarations, the image is the same game on that machine.

This document specifies the declarations in general terms, then shows each part on RUNS-Spacewar's PDP-1 declarations, `pdp1/` in [RUNS-Spacewar](https://github.com/wScottSh/RUNS-Spacewar). Its `pdp1/README.md` defines the full PDP-1 vocabulary. Each section also carries a sketch of declarations that a conversion would design for the byte-addressed machine of [A second machine](./MACHINE_DESCRIPTION.md#a-second-machine-an-8-bit-byte-with-carry), `micro8`, with registers `A`, `X` and `Y`, a status register `P`, and a vertical-blank interrupt. The sketches illustrate the form. They are not a vocabulary any compiler reads.

The sketches declare the ball game of the [README](./README.md#records-processors-and-networks): the Records `speed`, `wall`, `ball` and `pad`, the stream `screen`, the Processors `move_ball`, `reach_wall`, `bounce` and `draw_ball`, and the top Network `tick`. A sketch names a Processor as the text writes it, and a field the `tick` wires to one of its Ports, such as `ball.x`. Where a sketch needs an enum or a status flag the README's game lacks, it names one and says so.

## Where a change goes

The declarations are not a place to make hard RUNS text compile. When a pure shape does not compile to the original image, look for the change in this order:

1. **The RUNS text.** Hard text means its shape is wrong. Sketch at least two pure shapes and compile each.
2. **The compiler.** A general rule keyed on RUNS shape (see [Layout rules keyed on RUNS shape](#layout-rules-keyed-on-runs-shape)), backed by a second program on the same machine that uses the same idiom. The conversion's record of the change names the idiom and that program.
3. **Neither works.** Stop, and report the shapes tried and the evidence.

Purity stays as it is. A new declaration is not a step of this order.

## The declarations only shrink

A conversion counts the entries of its declarations: every scalar value and every list element of the TOML, with an empty table or list counted as one. A name added to an existing list counts the same as a new line. The count is recorded beside the declarations, and a check in every commit fails when the count rises. A commit that removes entries lowers the record. Only the user who owns the conversion raises it, and the record of that commit quotes the user.

Each cut derives entries the compiler no longer needs: by a general rule backed by a second program, or by a default. RUNS-Spacewar's compiler takes the object table's Records from the fields its walks index, where a `[table]` list once named them, and a routine that names no convention is a block when every run of it is the last thing its caller does.

In RUNS-Spacewar the check is `tools/check_declarations.py`, and the record is `pdp1/DECLARATIONS`. The user raised the count once, for one PDP-1 spelling entry, `[inverse_skip]`.

## Files and units

A machine's declarations are a set of TOML files in one directory.

- **A unit file** declares one **unit**, a span of the image that the target's toolchain lays out as one piece. The original's source files, or its assembler's sections, usually decide the units. A unit file declares every routine and field that lies in its span.
- **`devices.toml`** declares the events and the devices. It is the only file that names a control, a light, a port, a start address, or an interrupt. Two kinds of declaration may instead lie in a unit file, because they are instructions of that unit's code: the device of a stream, in the unit that emits to it, and an event that is a jump of that unit, such as a main loop that starts again when it ends.

Every routine and every field that the image holds is declared in at most one unit file. A field that lives only in a register, or only in another field's word, is declared where that register or word is declared. The compiler derives the rest from the RUNS text. A Record that no declaration gives a word lives in registers.

In RUNS-Spacewar each unit file is named for the unit of the original's lift that it replaces (`pdp1/divide.toml` for `lift/divide.c`), and the compiler refuses a unit of the lift that no unit file replaces.

## What the declarations may say

The declarations have seven sections. Each section below states what it may say, what the compiler refuses, the PDP-1 instance, and a sketch on the byte-addressed machine.

### Places

**Places** state the order and the addresses of routines and Record fields in the target's memory.

A place is one of these:

- A routine: a Processor or a Network compiled to one piece of code.
- A list of Record fields laid out as data words, each holding its RUNS initial value in the target's encoding.
- A range of slots of a collection's field, laid out the same way.
- Reserved room: a count of words or bytes that no rule reads, such as room left for an operator's patches.

A unit's places lie in the order the unit file lists them. A place may state its address where the original fixes it. Every other address follows from the order and the sizes.

The compiler refuses:

- A place that names no routine, field, or collection of the RUNS text.
- A routine or field placed twice, or not placed at all when the image holds it.
- Two places that overlap, or a place outside the target's address space.
- A data word whose RUNS initial value the target's type cannot hold.
- A field with no data word of its own (a register, an entry word), or one whose word the image does not load, whose RUNS initial value is other than the value the image gives that storage at load. The PDP-1's object table is not on the tape, and the game writes each of its words before it reads it, so the compiler requires each table field's initial value to be its zero word.
- A collection laid out with a slot count other than its RUNS count. The count is the game's, so a different count builds a different image.

**PDP-1.** `pdp1/multiply.toml` lays out `integer_multiply`, then the word `multiply_call.partial`, then `multiply`, in tape order:

```toml
[[place]]
routine = "integer_multiply"
convention = "JDA"
entry = "integer_multiply_call.entry"
byname = "integer_multiply_call.factor"
result = ["integer_multiply_call.product"]

[[place]]
fields = ["multiply_call.partial"]
```

`pdp1/outlines.toml` lays out each ship's outline as a range of slots, then five words of room no rule reads:

```toml
[[place]]
slots = "outlines.codes"
range = [0, 0o7]
reserve = 5
```

The PDP-1 compiler refuses any RUNS initial value but 0 on a field with no data word of its own, because an entry word or a register has no value on the tape.

**Sketch.** Declarations for the byte-addressed machine place the game's words in page zero, the code at the cartridge's start, and room after it:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
[[place]]
fields = ["speed.dx", "wall.past", "ball.x"]
at = 0x0010

[[place]]
routine = "tick"
at = 0x8000

[[place]]
routine = "move_ball"

[[place]]
reserve = 32
```

### Conventions

**Conventions** state how each routine is entered and left, and where its parameters and results travel.

A convention may say:

- How the routine is entered: a call instruction, a jump, laid out in place at each run (inline), a block that other routines jump into, an instruction executed in place, or an interrupt handler's entry and return.
- Where each parameter field arrives: a register, a word the call writes, a word after the call instruction, a stack slot.
- Where each result field leaves: a register, a pair of registers, a word.
- A skip or branch return: the routine returns to another place in its caller when a field holds a given enum member. The member is the RUNS text's; the convention says only which return place it selects.

A `run` in the RUNS text compiles to the routine's convention. The sets of the routine's parameter fields just before the run are its arguments. The result fields read just after the run come from where the convention leaves them.

A routine with Ports is one copy a distinct wiring: its text with each Port replaced by the field the `run` wires to it, as the original's macros were expanded at each use. A declaration names the routine as the RUNS text writes it, and applies to every copy. A routine laid out at each run (inline) lays out each copy where it runs. A called subroutine is one piece of code, so every `run` of it must wire it the same way.

The compiler refuses:

- A convention it does not know.
- A called subroutine with Ports whose runs wire it more than one way. The error names each wiring.
- A parameter or result that names a field the routine does not read or write.
- A block convention on a routine whose `run` is not the last thing its branch does, since a jump does not come back.
- A skip return whose field is not set on every path, or is not set last to the skip member.
- An interrupt convention on a routine that no event in `devices.toml` fires.

**PDP-1.** `pdp1/divide.toml` declares `divide` as a `jda` subroutine: the dividend's high half is the entry word, the low half arrives in IO, the divisor is the word after the call, executed by name. Its steps are a block that `integer_divide` jumps into. It returns one word further when the quotient fits:

```toml
[[place]]
routine = "divide"
convention = "JDA"
entry = "divide_call.high"
io_param = "divide_call.low"
byname = "divide_call.divisor"
block = "divide_steps"
result = ["divide_call.result", "divide_call.high"]
skips = ["divide_call.outcome", "fits"]
```

`pdp1/tunables.toml` declares a tunable that the original executes with `xct` as an `XCT` routine. The compiler derives its parameter and result registers from the RUNS text: the register fields it reads before writing them, and the ones it writes.

```toml
[[place]]
routine = "torpedo_velocity"
convention = "XCT"
```

The `diff` macro is one routine with Ports in RUNS, `inertia`, wired once an axis (`velocity: objects.dx[slot]`, `position: objects.x[slot]`, and the y axis's). One `[[inline]]` entry names it and lays out both copies, where two entries named one routine an axis. RUNS-Spacewar's `tools/check_ports_scratch.py` builds the original image from that text. Declared as a `JSP` subroutine instead, it is refused, because its runs wire it two ways. Minskytron, the second PDP-1 program, keeps each count its pick chooses with one Processor, `keep` (`in value: word`, `out kept: word`), wired six ways (`kept: shifts.ya` to `kept: shifts.xc`). No declaration names it, and its image matches.

```toml
[[inline]]
routine = "inertia"
shifts = "xct"
```

**Sketch.** `move_ball` is a subroutine entered by a call instruction and left by a return, with `ball.x` arriving and leaving in `A`. `tick` is the handler of the vertical-blank interrupt:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
[[place]]
routine = "move_ball"
convention = "subroutine"
param = { "ball.x" = "A" }
result = { "ball.x" = "A" }

[[place]]
routine = "tick"
convention = "interrupt"
```

### Storage

**Storage** states which register, memory word, status flag, or instruction operand holds each field and each local.

Storage may say:

- A local or field lives in a register, not in a word of its own.
- A Record's fields live in registers between routines. The Record is then a handoff: the original carried those values in registers from one routine to the next.
- A field lives in a status flag. A carry or overflow bit that one routine leaves and another reads is a field of a Record, as the machine description requires. Storage says it lives in the flag.
- A field lives in the operand of an instruction: the address field of the instruction that reads through it.
- A field lives in another field's word (a **shared word**), where the original reused one word for two values.
- A local or field lives in a stack slot, such as a value the original pushes to keep it across a call and pulls after.
- A field holds an address: a place in a collection, held as its address in the target's encoding.

The compiler refuses:

- Storage that names no field or local of the routine.
- Two fields in one register or word that the RUNS text needs at once. This is the shared-words check, under [Compiler checks on the declarations](#compiler-checks-on-the-declarations).
- A status-flag field that a later instruction of the compiled code would change before the field is read.
- A field held in an instruction operand when the instruction is not the one that reads it.

**PDP-1.** `pdp1/spaceship.toml` keeps the ship's nose in the pen's words, because the pen starts at the nose, and keeps the rocket bit in program flag 6 and the pen's side in flag 5:

```toml
[share]
"pen.x" = "ship_nose.x"
"pen.y" = "ship_nose.y"
"pen.down_x" = "spaceship.nose_step_x"
"pen.down_y" = "spaceship.nose_step_y"
"spaceship.star_wait" = "spaceship.nose_step_x"

[flags]
"spaceship.rocket" = 6
"pen.side" = 5
```

`pdp1/main_loop.toml` names a Record that lives in AC or IO between routines though one of its fields has a place, and the fields that live in the assembler's pool words. A Record none of whose fields has a place lives in registers with no declaration:

```toml
registers = ["outline_call"]
pool = ["pacing.spare_time", "frame.restart_delay", "frame.objects_seen",
        "score.first", "score.second", "score.games_left", "controls.source"]
```

`pdp1/outline_compiler.toml` keeps the outline word the compiler reads in the address field of the instruction that reads it (`ocg, lio .`):

```toml
[homes]
"outline_compiler.table" = "pointer"
```

**Sketch.** Suppose `reach_wall` computes `wall.past` with the machine description's `adc`, which returns the byte and the carry, and the RUNS text stores the carry in a field `wall.carry` that `bounce` reads. The original left that carry in the status register:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
# wall.carry is a field this sketch adds to the README's game.
[storage]
"wall.past" = "A"
"wall.carry" = "P.C"
"speed.dx" = "zero_page"
```

### Spelling

**Spelling** states the bit pattern of each enum member, and of each value whose encoding is the machine's own, such as an address or a pointer.

An enum member in RUNS is abstract. It compares only with `==` and `!=`. Its bits are a choice of the image, so the declarations spell them. A member may be spelled as a number, as a routine's address, or as an address with some bits added. An address is spelled by the machine description's address space: its unit and its byte order.

The compiler refuses:

- An enum that an image word holds with no spelling, or a member with no spelling.
- Two members of one enum spelled the same.
- A spelling as a routine's address when the routine is not placed.
- A spelling wider than the storage that holds it, such as a member other than 0 and 1 in a one-bit flag.

**PDP-1.** `pdp1/objects.toml` spells each calc routine member as the routine's address, with the sign bit for an object that does not collide. The torpedo's word is taken from a constant where the others are built by `law`. The two are the same word; which one the original wrote is an encoding:

```toml
[spell.calc_routine]
none = 0
explosion = { routine = "explosion", sign = true }
in_hyperspace = { routine = "in_hyperspace", sign = true }
breakout = { routine = "breakout" }
torpedo = { routine = "torpedo", literal = true }
first_spaceship = { routine = "first_spaceship" }
second_spaceship = { routine = "second_spaceship" }
```

**Sketch.** A ball whose state is an enum `ball_state` (this sketch adds it), spelled as the bytes the original wrote, and a member spelled as a routine's 16-bit address, little-endian by the description's address space:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
[spell.ball_state]
rolling = 0x00
stopped = 0x80

[spell.handler]
bounce = { routine = "bounce" }
```

### Code layout

**Code layout** states where a routine's blocks lie when the original lays them out of order.

Code layout may say:

- A loop's first exit falls through into the code after the loop, and the rest of its body lies after the routine's last return.
- The first arm of an if lies apart, after a loop or after the routine, and jumps back.
- The routine's exit lies at a named point.
- Data words lie inside the routine's code, at a point control cannot reach.
- A routine's body is a block other routines jump into.

A code layout key names a routine, a Processor, a field, or a local. It never names an expression or a statement by its text. It changes the order of the code, not what runs.

The compiler refuses:

- A layout the routine's shape does not allow, such as a loop layout on a routine with no loop, or an exit after a Processor the routine does not run.
- A layout that would change what runs on any path.

**PDP-1.** `pdp1/sincos.toml` lays out sine's reduction loop with its first exit falling into the series and the rest after the last return, and makes its series a block that cosine jumps into:

```toml
[[place]]
routine = "sine"
convention = "JDA"
entry = "sine_call.angle"
cells = ["sine_call.x"]
block = "sine_series"
block_takes_entry = true
io = ["sign"]
loops = "exit first"
result = ["sine_call.result"]
```

`pdp1/heavens.toml` lays out the first arm of each if with an else apart, after the scan's loop, and puts the exit in the skip of the frame count:

```toml
arms = "apart"
exit_after = "count_frames"
```

**Sketch.** The original lays the bounce after `tick`'s return and jumps back to the code after the guard:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
[[place]]
routine = "tick"
convention = "interrupt"
apart = ["bounce"]
```

### Events and devices

**Events and devices** live in `devices.toml`. They are the presentation side of the boundary. Play sees the value of each field that comes in and goes out, never the device.

`devices.toml` may say:

- **Events.** Each event of the host that fires a top Network: power-on, reset, each start address, each frame or vertical blank, each interrupt or timer the original handles, and the main loop starting again when a firing ends. An event names one top Network, or several that the host fires in the stated order. A machine whose vertical-blank interrupt runs a handler and then lets a waiting main loop go on names the handler's Network, then the main loop's.
- **Inputs.** For each field that comes in, the device that carries it: a switch, a joypad port, a memory-mapped register, a bit of a register, a sense line. It says how the device's bits become the field's value, such as which bit of a port is the field. A device that gives its bits over several reads, such as a joypad shift register that gives the next button on each read after a strobe, assigns each button's field to its read. The compiler emits the strobe and the reads.
- **Outputs.** For each field that goes out, the device it drives: a light, a memory-mapped register, a sound chip register.
- **Streams.** For each stream, the device that takes its tuples: a display that plots a point, the lights that show two words, a sprite table that a DMA transfer copies out.

The compiler refuses:

- Declarations with no `devices.toml`.
- A top Network that no event fires, or an event that names a routine that is not a top Network.
- A field that comes in from a device (a field of a top Network's `reads:` with no initial value, whose word the image does not hold) with no input device. A field whose value is the machine's power-on contents of a word the image leaves unloaded, such as Spacewar's scores, needs no device.
- A device declared for a field of a game Record. Devices carry interface and presentation Records only.
- A device the compiler does not know for this machine, or a device used two ways at once.

**PDP-1.** `pdp1/devices.toml` declares the console's test word and control boxes, six sense switches, the two survival lights, and the two start addresses:

```toml
[console]
"console.test_word" = "lat"
"console.control_boxes" = { read = "control_boxes", or_into_io = true }
"console.angular_momentum" = { sense = 1 }
"console.light_star" = { sense = 2 }
"console.single_shot" = { sense = 3 }
"console.no_planetarium" = { sense = 4 }
"console.star_kills" = { sense = 5 }
"console.no_star" = { sense = 6 }

[lights]
"lights.first_survived" = 1
"lights.second_survived" = 2

[[start]]
at = 0o4
network = "start_with_control_boxes"
tape = true

[[start]]
at = 0o5
network = "start_with_test_word"
```

The PDP-1 declarations name each stream's instruction in the unit that emits to it. `pdp1/objects.toml` plots the display stream with `dpy`, and `pdp1/main_loop.toml` shows the scoreboard on the console lights with `hlt`:

```toml
[streams]
display = "dpy"
```

```toml
[streams]
scoreboard = "hlt"
```

The frame is not an interrupt on the PDP-1. Spacewar's main loop starts again whenever a firing ends, and `pdp1/main_loop.toml`, whose code holds that jump, names the Network the machine runs again:

```toml
repeat = "frame"
```

**Sketch.** Reset fires a start Network once, the vertical-blank interrupt fires `tick`, the joypad's first read after its strobe is `pad.held`, and the screen stream writes the ball's x to a video register:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
# power_on is a start Network this sketch adds to the README's game.
[[event]]
on = "reset"
network = "power_on"

[[event]]
on = "vertical blank"
network = "tick"

[inputs]
"pad.held" = { port = 0xD010, strobe = true, read = 0, bit = 0 }

[streams]
screen = { write = 0xD400 }
```

### Machine words

**Machine words** are words the target machine or its operator needs that no rule reads: interrupt vectors, sequence-break words, the assembler's constants pool and variables pool, patch space, and the header bytes a cartridge needs.

A machine word is a kind of place the compiler knows for its target, the way it knows the call instruction. A machine word may hold an address or a jump that the events determine, such as a start vector. It never holds a number the game computes with. A constant of the image is a number of the RUNS text, and a pool word is a field.

The compiler refuses:

- A machine word kind it does not know.
- A machine word that a rule reads as a place.
- A machine word that a field's RUNS initial value would have to fill.

**PDP-1.** `pdp1/tunables.toml` begins the tape with the sequence break words and the start vectors, which come from `devices.toml`. `pdp1/core_layout.toml` lays out the constants, the pool words, and the patch space, then places the object table (`table = true`), which is a place of Records, not a machine word:

```toml
[[place]]
machine = "sequence break"

[[place]]
machine = "start vectors"
```

```toml
[[place]]
machine = "constants"

[[place]]
machine = "variables"

[[place]]
machine = "patch space"
reserve = 0o200

[[place]]
table = true
```

Play never raises a sequence break, so no event fires a Network on it. The words are there because the machine and the original's operator need them.

**Sketch.** The interrupt and reset vectors at the top of memory, filled from the events, and a cartridge header:

```toml
# Sketch: declarations a conversion would design for the byte-addressed machine.
[[place]]
machine = "header"
at = 0x7FF0

[[place]]
machine = "vectors"
at = 0xFFFA
```

## What the declarations may not say

The declarations hold no game logic. It has no expressions, no statements, and no number the game computes with. Every word of the image that the rules decide comes from the RUNS text. Every RUNS reference compiles as the field it names.

A declaration's value is one of these:

- A name of the RUNS text: a field, a local, a routine, a Record, an enum member.
- A name the declarations give a word of the target's code that the RUNS text does not name, such as a cursor, a block, or an exit. Such a name never reaches the image.
- A kind the compiler knows: a convention, a register, a device, a machine word kind, a layout.
- A number that is an address, a count of reserved words, a register or flag number, a bit position, or an enum member's bits.

A number the game computes with is not on that list. A tunable's value, a bound, a constant in an expression, and a field's initial value are all RUNS text. Where play reads the layout, the RUNS text states the layout (see the machine description's stated layout), and the declarations follow it.

## Compiler checks on the declarations

Every compiler checks these before it writes an image:

1. **Only accepted RUNS.** It compiles only RUNS text that `runs.check` accepts: what each kind may say, the contracts, a static scope check of names, fields and runs, each routine's Ports and each wire to them (or, in the older form, each Processor's `reads:` and `writes:` against its text in both directions), the type of each expression, and no routine that fires itself.
2. **Unknown keys refused.** Every key of every declarations file is one the compiler knows, with a value of its kind. An unknown key is an error that names the file and the key.
3. **Needed keys missing refused.** A choice the RUNS text needs and no declaration gives is an error that names what is missing, such as a routine with no convention or an enum with no spelling.
4. **Names checked.** Every name the declarations give is a name of the RUNS text of the right kind. A member's name means the member of the enum of the field it is stored in or compared with, as in the evaluator. A name the declarations give a word of their own names nothing else: no other such word, no routine, Record or field, and no word of the target toolchain.
5. **The shared-words check.** Several RUNS names can live in one word or register: a shared word, a register that holds a field and a local, the halves of a pair, a call's result. The compiler follows, through every routine and across the runs between them, which name each such word holds: the last one written and those copied from it since. A top Network starts with none. A read of a name the word does not hold is refused. So is a routine that returns a result field whose word holds another name.

Each refusal is an error that names the RUNS construct and the declaration's key. Refused declarations build no image.

In RUNS-Spacewar, `tools/runsc.py` is the compiler and raises `BindError`. Its shared-words check lets one case through: a bit-level pass that proves the Processor's effects use no bit of the value read (`draw_jump` and `plot_particle` shift IO's old value out).

## Layout rules keyed on RUNS shape

Some choices of layout follow from the shape of the RUNS text alone, the same for every game on the target. They belong to the compiler for that target, not to any machine's declarations. A declaration decides a choice that differs between routines. A compiler rule decides a choice that one shape of RUNS always makes the same way on that machine, and each rule that replaces declarations lets the count fall.

The PDP-1 compiler's rules are this kind. Among them:

- A loop whose one exit is its last statement, `if c: break`, tests at the bottom and jumps back to the top while `c` fails.
- `set x = x + 1` followed by a test of `x` against 0 is one index-and-skip (`isp`).
- A counted loop from a local up to n that does not read its index is a jump into a run of n + 1 copies of its body (Duff's device).
- An if-chain with no else whose guards test one value for `== n` over 0 to some n is a jump table.
- A `match` whose arms each run the routine their member is spelled as is a jump through the field's word.
- `stop` is a halt that halts again when continued (`hlt / jmp .-1`).

RUNS-Spacewar's `pdp1/README.md` lists every rule. A compiler for another machine gains a rule only for an idiom a second program on that machine would use.

## The mutation gate

The **mutation gate** checks that the declarations hold no logic and that the image comes from the RUNS text. It mutates the RUNS text and the declarations one change at a time, rebuilds, and classifies each mutant. A conversion runs it over every routine and field the declarations compile.

### Mutants of the RUNS text

The gate makes each of these, one at a time:

- **Numbers.** Each number one up.
- **Initial values.** Each field's initial value: a number one up, a member to each other member of its enum.
- **Field references.** Each field reference to each other field of its Record, of its type and of another type, and to the field of the same name in another Record.
- **Operators.** Each operator to its counterpart: `+` and `-`, `&` and `|`, `^` to `|`, `<<` and `>>`, `<` and `>=`, `>` and `<=`, `==` and `!=`, `and` and `or`.
- **Enum members.** Each member to each other member of its enum.
- **Run targets and arguments.** Each `run` to each other routine of its kind and arity. Each argument to 0, to 1, to itself plus 1, to its negation, and to each other name in scope.
- **Guards.** Each guard negated.
- **Arms.** An if's arm swapped with its else, and its first two arms with each other. Each two arms of a match swapped.
- **Statements.** Each statement deleted, duplicated, swapped with the next, and moved to every other place in its block.
- **Inserted sets.** After each `let` and `set`, a set of each other place the routine sets, to the same value. A step of its own place (`set p = p + 1`) inserted before it and after it.
- **Sets made locals.** Each set of a field at a Processor's top level made a local of the field's name, which the Processor's later statements read instead.
- **Contract entries.** Each Record a Processor declares under `reads:` or `writes:` deleted.
- **Preconditions.** Each `requires:` deleted.
- **Loop bounds.** Each loop's bound mutated as a number, a field, an operator, or a member.

### Mutants of the declarations

In each declarations file, `devices.toml` included, the gate makes each of these:

- Each key line deleted.
- Each section deleted.
- Each element of a list or an inline table deleted.
- Each value replaced: a quoted name by each other name of its shape in the file, a number one up and one down, a flag flipped.

### The outcome each mutant must have

A **RUNS mutant** must have one of these outcomes:

1. It builds a different image.
2. The evaluator rejects it before anything runs (`runs.check`).
3. The compiler refuses it with an error that names the RUNS construct.
4. It builds the original image and is shown to be the same game, by the rule for its kind below.

A **declarations mutant** must build a different image or be refused. A declarations mutant that builds the original image means the key, element or value is dead, and the gate fails. A dead entry is deleted, and the count falls. The one exception is a value that is a name the declarations give a word of their own, which never reaches the image. Replacing it renames the word.

A crash of the compiler fails the gate. So does any mutant without one of these outcomes.

### Same game

A mutant that builds the original image is **silent**. A silent mutant passes only when the evaluator shows it is the same game. **Same game** means: fired before and after the mutation, on the same states with the same arguments, every firing leaves the same Records (every field of every Record, every slot), the same stream contents, and the same error, or no error in both.

The states are these:

- **Seeded states.** At least 200 Record states, from a seed fixed per mutant. Each word field takes a value drawn over its type's full width. A quarter of the draws are the type's [edge words](./MACHINE_DESCRIPTION.md#edge-words). Each enum field takes a member drawn at random. Each argument is drawn from the arguments the RUNS text passes.
- **Played states.** Up to 60 Record states per routine as play leaves them just before its firings, kept from games the evaluator plays from power-on with random power-on words, random console or controller settings, and inputs drawn anew each frame. Random states seldom take a long routine clean to its end; played states do.

At least a quarter of the seeded count must run clean, with no error, through the mutated routine. A mutant that only errors, or never reaches the mutated routine, is not shown the same.

The routine fired is the mutated routine. When it alone differs, the gate fires each declared routine that compiles it, because what the image holds is that routine, and the mutant passes when one of them is the same game. A swap of two identical statements is the same text and passes.

Three kinds have their own rule:

- **An initial value.** The gate plays games from power-on before and after, on the same inputs (RUNS-Spacewar plays 60 games of 30 frames). The mutant passes when every firing puts out the same and every game ends with the same Records, the changed field aside.
- **A deleted `requires:`.** A precondition is the conversion's check that a firing is one the game makes, not code. The mutant passes when every firing the precondition lets run is the same and the precondition stops some firing. A precondition that stops no firing says nothing, and the gate fails.
- **A loop bound.** A bound is RUNS's check that the loop ends, and it compiles to nothing. The gate does not build the mutant. It passes when every firing is the same or stops at the bound it states.

The PDP-1 instance is `tools/check_compiled.py`.

## The host

A **host** is any runtime that runs a RUNS game. The evaluator is one host. The compiled image on the original machine is another: there the machine itself is the host, and the declarations' events and devices are how it plays that part.

Every host does these, and nothing else:

1. **It fires top Networks on events.** Each event the declarations name fires its top Networks, in order: power-on, reset, a start address, each frame or vertical blank, each interrupt or timer, the main loop starting again. A firing runs to its end before the next begins.
2. **Before a firing, it gives the world's values.** Each field that comes in takes the value its device holds now. At power-on, each field with no initial value takes the machine's power-on contents. Each stream is emptied.
3. **During a firing, `wait` hands it the turn.** The host takes each stream's contents so far to its device, may change what comes in, then the firing goes on from the `wait`.
4. **`stop` ends the game** as the original halts. No event fires after it.
5. **After a firing, it takes each stream's contents** to the device the declarations name, in the order emitted.

An error is not an event of the game. A loop past its bound, a failed `requires:`, a read of an unknown field, or a reached `unreachable` means the RUNS text is wrong. The host reports it and the game does not go on.

The host's choices are presentation. Two hosts that fire the same top Networks on the same events, with the same values coming in, give the same Records and the same streams.

**PDP-1.** The operator starts the machine at 4 or at 5. Each start fires its start Network once, `start_with_control_boxes` or `start_with_test_word`. When a firing ends, the machine runs `frame` again (`repeat`), and so does the evaluator's host, firing `frame` once a frame. Between games, `show_scores` emits the scores to the `scoreboard` stream and then waits. On the PDP-1 that pair is `hlt`, which shows the two words on the console lights. The operator sets the test word and continues, and the firing goes on. RUNS-Spacewar's frame Network is declared this way:

```text
network frame                                               # ml0
  reads: console, score, controls, outline_code
  writes: display, scoreboard, lights
```

**Sketch.** On the byte-addressed machine, reset fires `power_on` once, vertical blank fires `tick` each frame, the host reads the joypad port into `pad.held` before each firing, and after it writes each tuple of `screen` to the video register. Where the original's main loop runs past the start of the next vertical blank and the interrupt lands inside it, the landing point is timing, as [Interrupts](./CONVERSION_PROCESS.md#3-map-each-routine-to-processors-and-networks) states.

## The PDP-1 vocabulary

Each general section maps to keys of RUNS-Spacewar's PDP-1 declarations. Its `pdp1/README.md` defines every key.

| Section | PDP-1 keys | Example file |
| --- | --- | --- |
| Places | `[[place]]` with `routine`, `fields`, `slots` and `range`, `reserve`, `table = true`; `[[inline]]`; `[addresses]` | `pdp1/outlines.toml` |
| Conventions | `convention` (`JDA`, `JSP`, `XCT`, `BLOCK`), `entry`, `io_param`, `byname`, `inline`, `result`, `skips`, `block`, `block_takes_entry`, `[[code]]`, `pulse`, `exit`, `jsp_slot` | `pdp1/divide.toml` |
| Storage | `io`, `cells`, `pool`, `spill`, `io_reads`, `registers`, `[share]`, `[flags]`, `flags`, `[homes]`, `homes`, `[into]`, `into`, `[walk]`, `held_as_code`, `shifts` | `pdp1/spaceship.toml` |
| Spelling | `[spell.<enum>]` with numbers, `routine`, `sign`, `literal`; `[inverse_skip]` | `pdp1/objects.toml` |
| Code layout | `loops = "exit first"`, `arms = "apart"`, `exit_after`, `data`, `args_done`, `block` | `pdp1/sincos.toml` |
| Events and devices | `[console]`, `[lights]`, `[[start]]`, `[streams]`, `repeat` | `pdp1/devices.toml` |
| Machine words | `machine = "sequence break"`, `"sequence break flush"`, `"start vectors"`, `"constants"`, `"variables"`, `"patch space"` | `pdp1/tunables.toml` |

Some PDP-1 keys serve two sections. `block` is a convention and a layout of code. `[walk]` steps the cursors that hold Record fields, which is storage, and its `carry` loads a jump's word, which is a convention.

## Designing a vocabulary for a new machine

A conversion on a machine with no declarations vocabulary designs its own. It starts from the seven sections and grows the vocabulary one key at a time.

1. **Start from the sections.** Each key belongs to one of them. A choice that fits none of them is either logic, which goes in the RUNS text, or a compiler rule keyed on RUNS shape.
2. **Add a key only when the original's image needs it.** A key earns its place when the original's image makes a choice play cannot observe, and the compiler cannot derive that choice from the RUNS text's shape. If every routine of that shape makes the choice the same way, it is a compiler rule, not a key.
3. **Give each key a refusal rule.** For each key the compiler states what it refuses: a name of the wrong kind, a value out of range, a choice the routine's shape does not allow, a storage the shared-words check rejects.
4. **Cover each key with the mutation gate.** Delete it, delete each element, replace each value. Each mutant must change the image or be refused. A key whose mutants build the same image holds nothing, and the conversion removes it.
5. **Keep devices in one file.** Every event and every device the original uses goes in `devices.toml`, but for the two kinds [Files and units](#files-and-units) lets a unit file hold. The presentation side of the declarations is then in one place.
6. **Record the count.** Once the image matches, the count of entries only shrinks, as [The declarations only shrink](#the-declarations-only-shrink) states.

When a pure RUNS shape will not compile to the original binary, change the RUNS text first, then add a general compiler rule, then stop and report, as [Where a change goes](#where-a-change-goes) states.
