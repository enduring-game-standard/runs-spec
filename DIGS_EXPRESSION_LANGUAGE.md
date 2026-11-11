# DIGS: Deterministic Inspectable Game Syntax

> Every accepted example on this page loads in RUNS-Spacewar's evaluator, `tools/runs.py`, passes `runs.check`, and runs. Every rejected example fails with the error its first line quotes. [Check the examples](./README.md#check-the-examples) says how.

DIGS is the language of Processor bodies. Processors live in `.runs-prim` files. Records, streams, enums, and Networks live in `.runs` files and are described in [Network topology](./NETWORK_TOPOLOGY.md). Network guards use the expressions on this page.

A Processor is one rule of the game, and it is stateless. It names no Record. It declares its inputs and outputs, and the Network that runs it wires each one to one field. It takes values from its `in` and `inout` lines and gives values to its `out` and `inout` lines. Inside its body it declares locals and runs loops, and no local outlives the firing. What a Processor does depends only on its inputs, and its only effects are on the fields wired to the outputs it sets. A Record is data and nothing else, so a Processor's logic lives in its own text and never in a Record.

In the vision, a body's semantics are single-assignment dataflow: a `set` that looks like reassignment is a new version of the value, and a loop is a bounded fold ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 112-115). Today's evaluator runs a body as statements in order, and its loops can exit early (see [Statements](#statements)).

DIGS is the language of Rules Processor bodies. A Realization Processor's body is not DIGS, and the standard specifies no language for it ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 150-157). RUNS-Spacewar writes its presentation Processors in DIGS too, as `plot_particle` below shows.

## A running example

The examples on this page together form one program with one top Network, `demo`. The integer square root, the random number generator, and the explosion's dot are taken from RUNS-Spacewar. The plot is simplified to read one position instead of the object table.

```runs
game record square_root_call
  entry: word = 0           # sqt: jda leaves the argument here; it doubles as the remainder
  passes_left: word = 0     # sq1
  root: word = 0            # sq2: the result

interface record random
  number: word = 0          # ran

presentation record cloud
  spread: word = 1          # which shift spreads the dots, scr 1s or scr 3s
  scatter: word = 0         # places this dot's scl shifts

interface record position
  x: word = 0
  y: word = 0

presentation stream display
  x: word
  y: word
  intensity: int

network demo
  writes: display
  run next_random
    number: random.number
  run take_entry
    number: random.number
    entry: square_root_call.entry
  run square_root
    entry: square_root_call.entry
    passes_left: square_root_call.passes_left
    root: square_root_call.root
  run scatter_particle
    number: random.number
    scatter: cloud.scatter
  run plot_particle
```

## Processor declarations

A Processor has a name, inputs and outputs, optional headers, and a body:

```runs-prim
# The `random` macro: the generator's next value.
processor next_random
  inout number: word
  set number = (rar(number, 1) ^ 0355670) + 0355670

processor take_entry
  in number: word
  out entry: word
  set entry = number & 0377777
```

| Header | Meaning |
|--------|---------|
| `in name: kind` | An input the body reads and never sets. |
| `out name: kind` | An output the body sets. |
| `inout name: kind` | An input and output the body reads and sets. |
| `requires: condition` | A precondition. If it is false when the Processor fires, the RUNS text is wrong. If it is not a condition, such as a word, the evaluator rejects it. |

An input's or output's kind is a type of the machine description or an enum, for one word or one slot, or `type[N]` for a whole field of a collection of N, which the body indexes itself. The body uses its name as it would use the field: it reads it, sets it, and indexes it. [Network topology](./NETWORK_TOPOLOGY.md#inputs-and-outputs) states how a Network wires them, and the checks on each wire.

In the vision, a precondition is a DIGS boolean a Processor declares, and the guards that route to the Processor discharge it ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 372-384). The vision also names a top Network's inbound boundary Records `requires:` ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 272-275). Today's text uses `requires:` for the precondition, so the keyword disagrees with the vision's.

A conversion starts from an older form, which the loader still reads. That Processor names Records under `reads:` (Records the body may read) and `writes:` (Records and streams the body may write, and read), and takes parameters, the slot a Network passes with `run`, as in `run count_down(slot)`. A parameter only chooses a slot of a collection, so a Network passes a count. A Processor that emits to a stream keeps this form, because an output does not carry a stream yet. The older form falls short of the vision, where a Processor knows nothing of a Record and only the Network knows both sides ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 166-169).

`runs.check` checks each Processor's text before anything runs, and the evaluator checks each Record access again when it happens. A Processor in the older form that reads a Record in neither `reads:` nor `writes:` is an error, and so is one that writes a Record not in `writes:`:

```runs-prim-rejected
# rejected: peek does not declare reads: random
interface record random
  number: word = 0

game record seen
  value: word = 0

network top
  run peek

processor peek
  writes: seen
  set seen.value = random.number
```

A Processor fires no routine. It has no `run`, `match`, `stop`, or `wait`, and an expression cannot call a Processor or a Network. The vision allows a body to call a sub-Processor: a pure call whose intermediates are locals of the body, which the Network sees as one transition ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 172-186). Today's DIGS has no such call:

```runs-prim-rejected
# rejected: square_root is not an operator of the word; a routine is run, not called
processor half_root
  writes: square_root_call
  set square_root_call.root = square_root(square_root_call.entry) >> 1
```

A routine the original called, such as the square root subroutine, becomes a Processor whose inputs and outputs are the values it hands through. The caller becomes a Network that wires them: it fires a Processor that sets the input field, fires the routine with its inputs and outputs wired to that field and to the result fields, and then fires a Processor that uses the output.

## Statements

| Statement | Meaning |
|-----------|---------|
| `let name = e` | Declare a new local. |
| `let (a, b) = e` | Declare one local for each element of a tuple, such as the pair `scr` gives. `_` takes an element that nothing reads. |
| `set target = e` | Update a local bound by `let`, an output (`out` or `inout`), or, in the older form, a field of a declared Record. The target may be a pair, as in `set (high, low) = rcl(high, low, 18)`. |
| `if e:` ... `elif e:` ... `else:` | Run the first arm whose condition is true. |
| `loop at most N:` | Run the body again and again until `break` or `return`. Running more than N passes means the RUNS text is wrong. |
| `jump code at most N` | Run the words of code from `code`, a slot of a Record field of type `insn`, by the original machine's rules. It is impure. [A Record holds no code](#a-record-holds-no-code) says why. |
| `for i in a .. b:` | Run the body once for each count from `a` to `b`, both included, in ascending order. |
| `break` | Leave the innermost `loop`. |
| `continue` | Start the next pass of the innermost `loop`. |
| `return` | End the Processor. It takes no value. |
| `emit stream: a, b, c` | Append one entry to a declared stream, one value per field in order. A Processor that emits keeps the older form, with the stream under `writes:`. |
| `unreachable` | Mark a path the game never takes. Reaching it means the RUNS text is wrong. |

In the vision, a loop in a body is a bounded fold whose count is fixed before it starts, with no `break`, `continue`, or early `return` ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 112-115, 344-347). Today's `loop`, `break`, `continue`, and `return` fall short of that. How a body states a loop whose exit depends on data, such as the square root below, is open.

`runs.check` follows each local through every path. A local that some path reaches unbound is an error before anything runs.

Here is the Spacewar square root, a loop with `continue` and `return`:

```runs-prim
# BBN integer square root (sqt), over its own words. Binary point right of
# bit 17 in square_root_call.entry, between bits 8 and 9 in .root. Two bits
# of input per pass, 18 passes.
processor square_root                                       # sqt
  inout entry: word
  out passes_left: word
  out root: word
  set passes_left = -023
  set root = 0
  let input_bits = entry
  set entry = 0
  loop at most 023:
    set passes_left = passes_left + 1
    if passes_left >= 0:
      return
    set root = root << 1
    let next = entry
    set (next, input_bits) = rcl(next, input_bits, 2)
    if next == 0:
      continue
    set entry = next
    set next = (root << 1) + 1 - entry
    if next > 0:
      continue
    if next < 0:
      set next = -next
    set entry = next
    set root = root + 1
```

`passes_left` and `root` are outputs, not locals, because they are the routine's own words in the original, `sq1` and `sq2`. The Network wires them to fields of `square_root_call`. A value that a Processor sets before it reads it, and never hands on, is a local.

## Expressions

An expression produces one of six kinds of value:

- A value of a **machine type**, such as Spacewar's `word`. The [machine description](./MACHINE_DESCRIPTION.md#how-runs-uses-the-descriptions-types) gives each literal its type. On the PDP-1 every number literal is a word.
- A **count** is an integer used as an index or a bound. A `for` index, a parameter that a Network passed as a count, and the result of `popcount` are counts.
- A **condition** is `true` or `false`, the result of a comparison, `and`, `or`, or `not`.
- An **enum member**, written by its name.
- A **tuple**, the result of an operator that gives several values, such as the PDP-1's `rcl`, `rcr`, `scl`, `scr`, `mus`, and `dis`, or written as `(a, b)`.
- An **instruction**, a word of code built by an instruction's name. It is impure. [A Record holds no code](#a-record-holds-no-code) describes it.

### Names and places

- `record.field` reads a field of a single Record.
- `record.field[i]` reads element `i` of a field of a collection. `i` is a count. A slot past the last is an error.
- A bare name is a parameter, a local, an enum member, or an instruction that takes no operand.
- A Record's name alone is not a value. A Record is read by its fields.

Reading a field that has no initial value, before the game sets it or the world gives it, is an error.

A number literal starts with a digit. The machine description's [literal forms](./MACHINE_DESCRIPTION.md#literals) say how it is read. On the PDP-1 a literal with a leading `0` is octal, as in `0355670` and `-04000`, and holds only the digits 0 to 7, other literals are decimal, and a literal fits in 18 bits. RUNS has no fractional or string literals.

### Operators

From the tightest to the loosest:

| Level | Operators |
|-------|-----------|
| 1 | `.field`, `[index]`, operator calls such as `rcl(a, b, 2)`, instructions such as `lac(pen.x)` |
| 2 | unary `-`, unary `~` |
| 3 | `+`, `-` |
| 4 | `<<`, `>>` |
| 5 | `&` |
| 6 | `^` |
| 7 | `\|` |
| 8 | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| 9 | `not` |
| 10 | `and` |
| 11 | `or` |

Binary operators group from the left. The bitwise operators group tighter than the comparisons, so `a | b == c` means `(a | b) == c`. Arithmetic groups tighter than `|`, so `(random.number | 0400000) + x` needs its parentheses. `and` and `or` take conditions and evaluate their right side only when they need it.

RUNS has no `*` or `/`. A machine's multiply or divide instruction is a named operator of its description. The PDP-1 has only a multiply step and a divide step, so Spacewar's multiply and divide are Processors over `mus` and `dis`, as the original writes them.

```runs-prim-rejected
# rejected: cannot read
game record area
  width: word = 3
  size: word = 0

network top
  run measure

processor measure
  writes: area
  set area.size = area.width * area.width
```

If either operand of `+`, `-`, or a comparison is a count, the operation is on counts, so `slot + 1` is a count. A word that is not negative can stand where a count is needed, such as a shift amount.

## The word

Every operator on a machine type comes from the program's [machine description](./MACHINE_DESCRIPTION.md). The `word` is the game's number. That it is 18 bits in ones' complement is a rule of Spacewar, which the RUNS text states exactly: the examples on this page use the PDP-1 description, where Spacewar's word is defined. [The PDP-1 description](./MACHINE_DESCRIPTION.md#the-pdp-1-description) defines each operator below with a body. These tables summarize them.

| Operation | What it does |
|-----------|--------------|
| `-a`, `~a` | Flip all 18 bits. Both are the ones' complement negation. `-0` is minus zero, `0777777`. |
| `a + b`, `a - b` | The PDP-1's add and subtract, with end-around carry. Positions wrap around, so Spacewar's screen is a torus. |
| `a & b`, `a \| b`, `a ^ b` | Bitwise on all 18 bits. |
| `a << n` | The PDP-1's `sal`. Shift left `n` places, keep the sign bit, and shift the sign bit in at the bottom. `-1 << 1` is `-2`. |
| `a >> n` | The PDP-1's `sar`. Shift right `n` places and copy the sign bit. A negative word rounds toward zero, so `-1 >> 1` is `-0`. |
| `a == b`, `a != b` | Compare all 18 bits. `-0 == 0` is false. |
| `a < 0`, `a <= 0`, `a > 0`, `a >= 0` | Test the sign. A word compares with 0 only. `runs.check` rejects any other right side, unless the left side is a slot or a count (a parameter or a `for` variable, as in `slot < 2`). `-0 < 0` is true. `-0 <= 0` is true. `0 <= 0` is true. |

The machine description's named operators are the only calls in RUNS. The PDP-1's are these:

| Operator | What it does |
|----------|--------------|
| `ral(a, n)`, `rar(a, n)` | Rotate the word left or right `n` places. |
| `rcl(h, l, n)`, `rcr(h, l, n)` | Rotate the 36-bit pair `h`, `l` left or right `n` places. The result is a pair. |
| `scl(h, l, n)`, `scr(h, l, n)` | Shift the 36-bit pair left or right `n` places and keep the sign of `h`. `scl` shifts the sign of `h` in at the bottom of `l`. The result is a pair. |
| `mus(h, l, m)` | One step of the PDP-1's multiply (`mus`). The result is a pair. |
| `dis(h, l, m)` | One step of the PDP-1's divide (`dis`). The result is a pair. |
| `popcount(a)` | The number of bits set in `a`, as a count. |

The explosion's dot shows the pair operators. The original builds an `scl` instruction from a random number and then executes it. RUNS states that rule as a shift by `popcount` places.

```runs-prim
# The original builds an scl from the random number's low 9 bits; it
# shifts one place per bit set.
processor scatter_particle
  in number: word
  out scatter: word
  set scatter = popcount(number & 0777)

# The dot is presentation. The random number it reads is in the interface:
# the draw is the game's, because hyperspace draws from the same generator.
processor plot_particle
  reads: random, position, cloud
  writes: display
  let (high, low) = scr(random.number, 0, 9)
  set low = low >> 9
  set (high, low) = scr(high, low, cloud.spread)
  set (high, low) = scl(high, low, cloud.scatter)
  set high = high + position.y
  set (high, low) = rcl(high, low, 18)
  set high = high + position.x
  emit display: high, low, 3
```

## A Record holds no code

A Record holds data and nothing else. Instructions that a Processor runs are logic. So instructions kept in a Record and run with `jump` are logic in a Record, and that is impure.

Some original programs run data as code. Spacewar's outline compiler writes each ship's outline as PDP-1 instructions at the start of each game, and each frame the spaceship jumps into that code to draw the ship. A pure RUNS text states what that code computes, in Processors of its own. The binary holds the instructions. A general compiler for the machine reproduces those bytes, and RUNS itself does not hold them. The explosion's dot above shows the pattern on a smaller scale. The original builds an `scl` and executes it, and RUNS states the shift it computes.

The language parses `type insn`, the instruction constructors, and `jump` for a text that keeps code in a Record, as RUNS-Spacewar's outline does. The loader counts each use as an impurity, with one of two messages:

- `<record>.<field>: a Record holds data; instructions a Processor runs are logic`, for each field of type `insn`.
- `processor <name>: runs instructions from a Record (jump); its logic belongs in its own text`, for each Processor that runs `jump`.

A program does not load while it keeps instructions in a Record:

```runs-prim-rejected
# rejected: patch.insn: a Record holds data; instructions a Processor runs are logic
type insn
  instructions: lac add dac jmp

game record counter
  value: word = 0
  step: word = 3

game record patch[4]
  insn: insn                # no initial value

network patched
  reads: patch
  run write_patch
  run run_patch
  run after_patch

processor write_patch
  writes: patch
  set patch.insn[0] = lac(counter.value)
  set patch.insn[1] = add(counter.step)
  set patch.insn[2] = dac(counter.value)
  set patch.insn[3] = jmp(after_patch)

processor run_patch
  reads: patch
  writes: counter
  jump patch.insn[0] at most 4

processor after_patch
  writes: counter
  set counter.step = -counter.step
```

The pure form of `patched` is one Processor that adds the step to the value, then `after_patch`.

To read a text that uses these forms:

- A field of type `insn` holds one word of code. An expression builds an instruction by its name and operand, as in `lac(counter.value)` or `jmp(after_patch)`. An instruction with no operand, such as `cma`, is a bare name. Naming a word does not read it, so building `lac(counter.value)` is not a read of `counter`. `rcl` with one operand is the instruction. With three, it is the pair operator.
- `jump code at most N` runs the words from `code` by the original machine's rules, at most N instructions. Each word it fetches, reads, or writes goes through the running Processor's contract. AC, IO, and the program flags belong to the code, and are unknown until it sets them. The code ends at a jump to a routine, and the Network must run that routine next.
- The parser needs `type insn` to read an instruction, so a file that builds instructions loads only together with the file that declares it. [Network topology](./NETWORK_TOPOLOGY.md#types) describes `type insn`.

## What the evaluator rejects

Each error comes from one of three stages. The parser finds an error as it reads the text. `runs.check` finds an error before anything runs. The evaluator finds an error while a routine runs, or as it gives each Record its initial values. A message that names the word is the PDP-1's form of an error on a machine type. [What the loader rejects](./MACHINE_DESCRIPTION.md#what-the-loader-rejects) gives the general form.

| Error | Stage | When |
|-------|-------|------|
| `indentation is two spaces a level` | Parser | A line is indented by an odd number of spaces. |
| `cannot read ...` | Parser | The text holds a character RUNS does not use, such as `*` or `/`. |
| `... is not an octal number` | Parser | A literal with a leading `0` holds an 8 or a 9. |
| `... is not an operator of the word; a routine is run, not called` | Parser | An expression calls anything but a word operator or a declared instruction. |
| `jump <word of code> at most N` | Parser | A `jump` bound is more than one number or name. |
| `... sets ..., an in Port`, `... names the Record ...; a routine with Ports touches only its Ports`, and the other input, output, and wire errors | Parser | A Processor's inputs and outputs, or a Network's wires to them, break a rule. [What the loader and the evaluator reject](./NETWORK_TOPOLOGY.md#what-the-loader-and-the-evaluator-reject) lists each. The loader checks them as it reads the text and makes each copy. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network`, `wait belongs to a network` | `runs.check` | A Processor uses `run`, `match`, `stop`, or `wait`. |
| `... does not declare reads: ...` or `... writes: ...` | `runs.check`, run time | A Processor touches a Record it did not declare. The evaluator checks this again at run time, for every word that `jump` touches too. |
| `... declares ... under reads: and writes:` | `runs.check` | A Processor lists a Record under both. `writes:` lets it read the Record too. |
| `... writes ...; declare writes: ...`, `... reads ...; declare reads: ...` | `runs.check` | The text touches a Record its headers do not declare. |
| `... declares reads: ..., but nothing in it reads ...`, the same for `writes:` | `runs.check` | A header declares a Record the text never touches. |
| `... holds ..., not ...`, `... is passed ...` | `runs.check` | A value of one type goes where another is wanted: a member into a word field, an instruction where a word goes, or a parameter passed different types by different runs. |
| `... fires itself` | `runs.check` | A routine fires itself. Today a recursion is written as a stack Record and a bounded Network loop. |
| `... compares a word with 0 only, or a slot or count with a number` | `runs.check` | An ordering compare has a word on the left and anything but 0 on the right. |
| `... of two constants is constant` | `runs.check` | A comparison or operator has a constant on both sides. |
| `... does not fit a word` (in `runs.check`) | `runs.check` | A literal is wider than 18 bits. |
| `... has N slots, not slot ...` | `runs.check` | A constant index is past a collection's last slot. |
| `... takes N values, not ...` | `runs.check` | A word operator gets the wrong number of operands. |
| `its parameter ... is never read`, `the local ... is never read` | `runs.check` | A routine's parameter, or a local, is never read. A value a pair spreads into and nothing reads is named `_`. |
| `nothing after ... runs`, `... takes nothing after it` | `runs.check` | A statement follows `break`, `continue`, `return`, `stop`, or `unreachable` in the same block, or `return` has a value. |
| `... outside a loop` | `runs.check` | `break` or `continue` stands outside a `loop`. |
| `unknown name ...` | `runs.check` | A name is not a parameter, a local bound on every path, an enum member, or an instruction. |
| `set ... before let` | `runs.check` | `set` names a local that `let` has not bound on every path. |
| `let binds a local name` | `runs.check` | `let` names a Record field. |
| `... has no field ...`, `... is a collection`, `... is one word` | `runs.check` | A place names a field its Record lacks, or indexes it wrongly. |
| `... is no stream`, `... takes N values` | `runs.check` | An `emit` names something that is not a stream, or passes the wrong number of values. |
| `... takes a number`, `... names a word of a Record` | `runs.check` | An instruction's operand is not the kind of operand the instruction takes. |
| `code is a slot of a collection` | `runs.check` | A `jump` names a word that is not a slot of a collection. |
| `an initial value touches no Record` | Initial values | A Record field's initial value reads a Record. |
| `... does not fit a word` | Run time | A literal is wider than 18 bits. |
| `a word compares with 0 only` | Run time | `<`, `<=`, `>`, or `>=` runs with a word on the left and anything but the word 0 on the right. |
| `not a condition` | Run time | A `requires:`, a guard, `and`, `or`, or `not` gets a value that is not `true` or `false`. |
| `not a count` | Run time | A negative word stands where a count is needed, such as an index, a bound, or a shift amount. |
| `... holds ..., not ...`, `... holds an instruction, not ...` | Run time | A `set` stores a value of the wrong type in a field of an enum or of `insn`. |
| `... is unknown: the game has not set it, so the world gives it` | Run time | A routine reads a field with no initial value before the game sets it or the world gives it. |
| `slot ... is past the collection's ... slots` | Run time | An index reaches past a collection's last slot. |
| `break or continue outside a loop` | Run time | A Processor runs `break` or `continue` outside a `loop`. |
| `the code ran past N instructions` | Run time | A `jump` runs more instructions than its bound. |
| `a jump from ... to ...` | Run time | Code that `jump` runs jumps into another Record field. |
| `the code jumped to ..., so the Network runs it next` | Run time | The Network does not run the routine that the code jumped to right after the Processor. |
| `loop ran past its bound` | Run time | A `loop` runs more passes than its bound. |
| `precondition fails` | Run time | A `requires:` is false when the Processor fires. |
| `reached unreachable` | Run time | An `unreachable` runs. |

A word compared with anything but 0 is rejected when it runs:

```runs-prim-rejected
# rejected: < compares a word with 0 only, or a slot or count with a number
game record score
  first: word = 0
  second: word = 5

network top
  run tie_test

processor tie_test
  writes: score
  if score.first < score.second:
    set score.first = 0
```

An octal literal holds only octal digits:

```runs-prim-rejected
# rejected: 09 is not an octal number
game record score
  first: word = 0

network top
  run reset

processor reset
  writes: score
  set score.first = 09
```

The loop bound, `jump` bound, `requires:`, and `unreachable` errors never describe the game. If one of them fires, the RUNS text is wrong.

## Grammar

This grammar describes a Processor. Indentation is two spaces a level. A comment runs from `#` to the end of the line.

```text
processor   = "processor" NAME [ "(" NAME { "," NAME } ")" ] { indented ( port | header | statement ) }
port        = ( "in" | "out" | "inout" ) NAME ":" TYPE [ "[" NUMBER "]" ]
header      = "reads" ":" NAME { "," NAME }
            | "writes" ":" NAME { "," NAME }
            | "requires" ":" expression
statement   = ( "let" | "set" ) target "=" expression
            | "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ]
            | "loop" "at" "most" expression ":" block
            | "for" NAME "in" expression ".." expression ":" block
            | "jump" place "at" "most" ( NUMBER | NAME )
            | "break" | "continue" | "return" | "unreachable"
            | "emit" NAME ":" expression { "," expression }
block       = { indented statement }
target      = place | "(" place { "," place } ")"
place       = NAME | NAME "." NAME [ "[" expression "]" ]
expression  = or
or          = and { "or" and }
and         = not { "and" not }
not         = "not" not | compare
compare     = bitor { ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) bitor }
bitor       = bitxor { "|" bitxor }
bitxor      = bitand { "^" bitand }
bitand      = shift { "&" shift }
shift       = sum { ( "<<" | ">>" ) sum }
sum         = unary { ( "+" | "-" ) unary }
unary       = ( "-" | "~" ) unary | postfix
postfix     = primary { "." NAME | "[" expression "]" | "(" [ expression { "," expression } ] ")" }
primary     = NUMBER | "true" | "false" | NAME | "(" expression { "," expression } ")"
```

A call in `postfix` is valid only on the name of an operator of the machine description or of an instruction that `type insn` declares. A Processor has inputs and outputs, or the older form's parameters and `reads:` and `writes:`, not both.

*MIT License. Open for implementation, extension, and critique.*
