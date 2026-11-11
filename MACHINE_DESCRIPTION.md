# RUNS machine description

> Blocks tagged `runs-machine` on this page are machine-description text. `tools/check_examples.py` does not run them. RUNS-Spacewar's evaluator, `tools/runs.py`, holds [The PDP-1 description](#the-pdp-1-description) in code.

A **machine description** is a text file, `<machine>.runs-machine`, that states everything RUNS takes from the original machine. Every type a RUNS text uses that is not a count, a condition, or an enum comes from it. The evaluator reads it. Nothing about the machine lives in evaluator code.

A machine description is game-neutral. Every game on that machine shares it. A conversion of a second PDP-1 game uses the same `pdp1.runs-machine`, and extends it only with an operator that game's play reaches.

A machine description is how a RUNS text takes up the arithmetic reach-contract ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md) 40-49, 321-326). Its types and operators pin the original's arithmetic bit for bit, so a Port can keep the Rules region bit-exact. CONTEXT.md calls these game-defined numeric types; here a game takes them from its machine's description, which every game on that machine shares. CONTEXT.md makes the contract opt-in, not required for compliance. This page's rule that every program names one machine is the rule of this format. Whether a RUNS text that takes up no arithmetic contract names a machine is open.

A machine description holds four things:

- **Types.** Each type is a fixed-width bit vector, such as the PDP-1's 18-bit `word`.
- **Literals.** How a number in RUNS text is written for this machine.
- **Operators.** Every operation RUNS text performs on a value of a machine type, each with a body.
- **Address spaces.** The memories whose layout play reads, with their unit, address width, and byte order.

It holds nothing else. Status flags, instructions, and the host are not part of it. [Status flags and registers](#status-flags-and-registers), [Instructions are not part of the description](#instructions-are-not-part-of-the-description), and [The host is not part of the description](#the-host-is-not-part-of-the-description) say where each belongs.

Operator bodies are written in the **core**, a small machine-neutral language that every evaluator implements. An evaluator that implements the core runs any machine description.

## A RUNS text names its machine

A `.runs` file names the program's machine with a `machine` line at the top level:

```text
machine pdp1
```

The rules:

- Every program names exactly one machine. One `.runs` file of the program holds the `machine` line. Other files may repeat it. Every `machine` line in the program names the same machine.
- The loader finds `<name>.runs-machine` in the program's directory first, then in each machine directory the runtime is given, in order. The first file found is the description.
- The description's first line is `machine <name>`, and the name is the file's name.
- A `.runs` file declares no machine type. The `type word` block that RUNS-Spacewar's `spacewar.runs` holds belongs in `pdp1.runs-machine`. `type insn` is the one `type` declaration a `.runs` file may hold, and it is impure. [Instructions are not part of the description](#instructions-are-not-part-of-the-description) says why.

### What the loader does with it

The loader reads a program in this order:

1. It reads every `.runs` and `.runs-prim` file of the program and finds the `machine` line.
2. It finds the description and reads it. It checks the description's grammar, each type's width, the literal forms, each address space, and each operator's signature and body. It computes the type of every expression in every body and refuses a mismatch. [What the loader rejects](#what-the-loader-rejects) lists each error.
3. It reads every number in the RUNS text by the description's literal forms. Collection sizes, loop bounds, and layout addresses are numbers too.
4. It takes the description's type names as the names a Record field or a stream field may have, besides the enums the text declares and `int`, the count.
5. `runs.check` resolves each operator symbol and each operator call in the RUNS text to one operator of the description, by the operands' types. It checks each operand where the signature has a literal, and each `requires:` whose operands are all constants.
6. It checks each `layout` declaration against the description's address spaces.
7. While a routine runs, the evaluator runs each operator's body in the core. A value of a machine type is a bit vector of the type's width.

### How RUNS uses the description's types

- A field's type is an enum, `int` in a stream, or a type of the description.
- An operator symbol in RUNS text, such as `a + b`, runs the operator the description gives that symbol for the operands' types. A call by name, such as `rcl(h, l, 2)`, runs the operator of that name.
- A name that is not an operator of the description, a declared instruction, or a RUNS form is refused. A routine is run, not called.
- An operator's result may be a tuple. RUNS takes it apart with `let (a, b) = ...` or `set (a, b) = ...`, one place per element. `_` takes an element that nothing reads.
- **Counts meet machine types.** A count is RUNS's own integer, and RUNS computes on counts itself. If either operand of `+`, `-`, `==`, `!=`, `<`, `<=`, `>`, or `>=` is a count, the other converts to a count by its type's `as count` operator, and RUNS computes on the two integers. In every other place, a count where an operator's parameter is a machine type converts to that type by the type's `as literal` operator. A value of a machine type where RUNS needs a count, such as an index or a loop bound, converts by its type's `as count` operator.
- **A literal's type.** A literal takes the machine type its context gives: the type of the field it is stored in, of the parameter it fills, or of the other operand. Where its context gives no machine type, a literal is a value of the description's literal type, and a count context converts it by `as count`. On the PDP-1 every literal is a `word`.
- Enums, conditions, and counts are RUNS's own. Their comparisons and the count arithmetic are not in the description.

## Types

A **type** is a fixed-width bit vector. Its declaration states its width and how its bits read as a number:

```runs-machine
type word
  bits: 18
  reads_as: ones_complement
```

| Key | Meaning |
|-----|---------|
| `bits: N` | The width in bits. N is a whole number, 1 or more. |
| `reads_as: R` | How the bits read as a number, for tools that show a value. |

`reads_as` is a convenience. Tools that show values, such as a trace or a debugger view, read a value by it. The operators define every behavior. Nothing in the evaluator branches on `reads_as`.

| `reads_as` | The bits read as |
|------------|------------------|
| `unsigned` | A binary number from 0 to 2^N - 1. |
| `twos_complement` | A binary number from -2^(N-1) to 2^(N-1) - 1. |
| `ones_complement` | Sign and complement: a set top bit means the negation of the complement. All ones is minus zero. |
| `sign_magnitude` | The top bit is the sign, the rest is the magnitude. |
| `bcd` | Decimal digits, four bits each, the lowest digit in the lowest bits. |
| `ieee754_binary16`, `ieee754_binary32`, `ieee754_binary64` | The IEEE 754 binary interchange format of that width. |
| `fields` | Named bit ranges, one indented line each. |

A `fields` type names its ranges, from the most significant bit to the least. Bit 0 is the least significant:

```runs-machine
type extended
  bits: 80
  reads_as: fields
    sign: [79:79]
    exponent: [78:64]
    significand: [63:0]
```

A machine may have several types. An 8-bit micro with a 16-bit address bus has `byte` with 8 bits and `addr` with 16. An x87 FPU has `extended` with 80. A machine with a carry flag that play stores has `bit` with 1.

### Edge words

The **edge words** of an integer type are the values where its operators change behavior: 0, 1, -1, the most positive and the most negative value, every value with a second encoding (such as the ones' complement -0), and the low half of the bits set, with and without the sign bit. The checks of a conversion and the mutation gate draw a share of their values from them. [The PDP-1 description](#the-pdp-1-description) and [A second machine](#a-second-machine-an-8-bit-byte-with-carry) list theirs.

## Literals

The `literals` block says how numbers are written in RUNS text for this machine, and which type a literal takes when its context gives none:

```runs-machine
literals
  type: word
  prefix 0 base 8
  default base 10
```

| Line | Meaning |
|------|---------|
| `type: T` | The type of a literal whose context gives no machine type. |
| `prefix P base B` | A literal of two or more characters that starts with `P` is read in base B, from the digits after `P`. B is 2, 8, 10, or 16. |
| `default base B` | A literal that matches no prefix is read in base B. A lone `0` matches no prefix. |

A prefix is `0`, or `0` and one letter, such as `0x`. A literal starts with a digit, so RUNS text has one token form for every machine. Where two prefixes match, the longer wins. A literal holds only digits of its base. On the PDP-1 `0355670` is octal and `9` is decimal, and `09` is refused with `09 is not an octal number`.

A literal is a whole number with no sign. `-04000` is the operator `unary -` applied to the literal `04000`. The type's `as literal` operator turns the number into a value of the type and refuses a number that does not fit.

## Operators

An **operator** is a total, deterministic function from values to values that the description defines. Every operation RUNS text performs on a value of a machine type is an operator. An operator has a signature, an optional symbol, optional `requires:` lines, and a body:

```runs-machine
operator add(a: word, b: word) -> word as +
  let s = bits(a) + bits(b)
  let e = (s + s div 0o1000000) mod 0o1000000
  if e == 0o777777:
    vec(0, 18)
  else:
    vec(e, 18)
```

### Signatures

- Each parameter is `name: T`, where T is a type of the description, `count`, or `cond`.
- A parameter may be a literal in place of a name, such as `0` in `operator negative(a: word, 0) -> cond as <`. The operand in RUNS text must then be that literal. `runs.check` refuses any other operand before anything runs. This is how a description says which comparisons a type allows.
- The result is one type, or a tuple of two or more in parentheses, such as `(word, word)` or `(byte, bit, bit)`.
- `count` is a RUNS count, an integer with no bound. `cond` is a RUNS condition. In the core a `cond` is a 1-bit vector, where 1 is true.

### Symbols

`as` gives an operator a symbol of RUNS text, or names it as one of a type's two conversions. An operator with no `as` is called by its name, as `rcl(h, l, 2)` is.

| Symbol | RUNS text | Signature |
|---------|-----------|-----------|
| `as +`, `as -`, `as &`, `as \|`, `as ^` | `a + b` and the others | Two operands, one result. |
| `as <<`, `as >>` | `a << n`, `a >> n` | Two operands, one result. |
| `as ==`, `as !=`, `as <`, `as <=`, `as >`, `as >=` | `a == b` and the others | Two operands, result `cond`. |
| `as unary -`, `as ~` | `-a`, `~a` | One operand, one result. |
| `as literal` | A literal, or a count where the type is wanted | One `count`, result the type. |
| `as count` | A value of the type where a count is wanted | One operand of the type, result `count`. |

Several operators may take one symbol if their operand types differ. RUNS text picks the one whose parameter types match the operands. Two operators that take one symbol on the same operand types are refused. An operator's name is unique in the description.

A type allows exactly the operations the description defines for it. An 8-bit micro's description may give `byte` no `+` at all, because the machine adds only with carry. RUNS text then writes `adc`.

### Requires

A `requires:` line is a condition the operands must meet, with the message the error carries:

```runs-machine
operator word_of(n: count) -> word as literal
  requires: and(n >= -0o777777, n <= 0o777777) else "{n} does not fit a word"
  if n >= 0:
    vec(n, 18)
  else:
    not(vec(-n, 18))
```

If the condition is false, the RUNS text is wrong, and the evaluator stops with the message. A parameter's name in braces stands for its value. `runs.check` evaluates a `requires:` before anything runs when every operand is a constant in the RUNS text.

CONTEXT.md calls a condition of this kind a precondition (372-384) and uses `requires:` for a top Network's inbound boundary Records (272-274). The two senses of the keyword are a gap.

### Bodies

A body is written in [the core](#the-core). It computes the result from the parameters and nothing else. It reads no Record, writes nothing, and keeps nothing between calls. A body may call an operator that the description defines above it, so the operators form no cycle.

A body is **total** and **deterministic**. It gives a result for every operand its signature and its `requires:` lines admit, and the same operands always give the same result. Nothing else about the run, the evaluator, or the host machine reaches a body.

## The core

The **core** is the language of operator bodies. It has two kinds of value:

- An **integer**, with no bound.
- A **bit vector** of a stated width, `w` bits from bit 0, the least significant, to bit `w - 1`.

A tuple of values is the result of a body, or a value `let` takes apart.

The width of every vector is known when the description loads. The loader computes it for every expression.

### Primitives

These are the core's only operations. Nothing else exists.

| Primitive | Takes | Gives |
|-----------|-------|-------|
| `a + b`, `a - b`, `a * b` | Integers | Integer. |
| `a div b`, `a mod b` | Integers, b not 0 | Floor division, and the remainder with the sign of b. `-7 div 2` is -4, `-7 mod 2` is 1. |
| `-a` | Integer | Integer. |
| `a == b`, `a != b`, `a < b`, `a <= b`, `a > b`, `a >= b` | Integers | 1-bit vector, 1 if true. |
| `bits(x)` | Vector | The integer x reads as unsigned, 0 to 2^w - 1. |
| `vec(n, w)` | Integer n, constant w of 1 or more | The w-bit vector of n mod 2^w. A negative n wraps as two's complement. |
| `x[hi:lo]` | Vector, constants hi >= lo, both below its width | Bits hi to lo, a vector of hi - lo + 1 bits. |
| `x[i]` | Vector, integer i from 0 to its width - 1 | Bit i, a 1-bit vector. i need not be constant. |
| `cat(a, b)` | Vectors | a's bits above b's bits, a vector of their two widths. |
| `and(a, b)`, `or(a, b)`, `xor(a, b)` | Vectors of one width | Bitwise, the same width. |
| `not(a)` | Vector | Every bit flipped, the same width. |
| `(a, b, ...)` | Values | A tuple. |

A constant is an integer literal, or `+`, `-`, `*`, `div`, or `mod` of constants. Integer literals in the core are written as decimal digits, or with `0o`, `0x`, or `0b` for octal, hexadecimal, or binary. A core literal has no leading `0` of its own, so it reads the same on every machine.

A condition is a 1-bit vector. `and`, `or`, and `not` join conditions as they join any vectors. Both sides of `and` and `or` are evaluated.

### Statements

| Statement | Meaning |
|-----------|---------|
| `let name = e` | Give a name a value. If an enclosing block of the body already names it, the `let` sets it there: the name holds the new value through the rest of that block. The new value has the old one's type and width. |
| `let (a, b) = e` | Take a tuple apart, one name per element. `_` takes an element and names nothing. |
| `if c:` ... `elif c:` ... `else:` | Run the first arm whose 1-bit condition is 1. |
| `for i in a .. b:` | Run the block once for each integer from a to b, both included, ascending. a and b are evaluated once, before the first pass. If a > b, the block does not run. `_` in place of `i` names nothing. |

A block is a run of statements, each on its own line, indented two spaces from the line that opens it. A body is a block whose last line is its **value**: an expression, or an `if` with an `else` whose every arm is a block that ends in a value. A name a block gives is gone when the block ends, unless it is a name of an enclosing block.

Every `for` runs a finite number of passes, so every body ends. A body that reaches `div` or `mod` by 0, or `x[i]` with i outside the vector, has no result for that operand, and the description is wrong. The evaluator stops with the error.

### What the core leaves out

The core has no recursion, no unbounded loop, no floating point, no memory, no Records, and no input or output. Each of these is something the description builds from the primitives, or something RUNS states elsewhere. A machine's floating point is a type with operators. A machine's memory is an address space and a `layout`.

## Status flags and registers

A carry, an overflow, or a condition bit is not part of a type. A type is a bit vector, and an operator is a function of its operands. An operator that the machine runs with a flag takes the flag as an operand and returns the new flag in its result.

A flag that one routine leaves and another reads is a value the original carried between rules. It is a field of the Record of the concern it belongs to, exactly as a value the original carried in AC or IO is. The operator returns it, and the RUNS text stores it. A flag that a routine sets and reads before it hands it on is a local.

A machine's add with carry shows the form. It returns the byte, the carry out, and the signed overflow:

```runs-machine
operator adc(a: byte, m: byte, c: bit) -> (byte, bit, bit)
  let s = bits(a) + bits(m) + bits(c)
  let r = vec(s, 8)
  (r, vec(s div 256, 1), and(not(xor(a[7], m[7])), xor(a[7], r[7])))
```

A 16-bit score kept in two bytes adds its low bytes in one routine and its high bytes in the next. The carry between them is a field:

```text
game record score
  low: byte = 0
  high: byte = 0
  carry: bit = 0            # C: add_low leaves it, add_high reads it

processor add_low
  reads: points
  writes: score
  let (low, carry, _) = adc(score.low, points.value, 0)
  set score.low = low
  set score.carry = carry

processor add_high
  writes: score
  let (high, _, _) = adc(score.high, 0, score.carry)
  set score.high = high
```

This example is in today's text form. Each Processor declares the Records it reads and writes, and both set fields of `score` in place. In the vision a Processor knows no Record, and the Network wires each Field to its inputs and outputs (CONTEXT.md 166-169). Each new value lands in a fresh place and never overwrites the old (90-92, 194-196). How the carry's chain of values is written in the vision's graph is open.

A register is the same. A value the original carries in a register from one routine to the next is a field. A comment may name the register. The declarations say which register holds the field.

## Floating point

A machine's floating point is a type with operators. Each operator states the machine's exact result: its rounding, its NaN bits, its subnormals, its signed zeros.

An operator states that result one of two ways:

- **A body in the core.** The core holds integers and bit vectors, so a body states any rounding a machine does, bit for bit.
- **A citation.** In place of a body, `cites:` names an operation of IEEE 754-2019. A description cites only where the machine follows the standard bit for bit on every operand. The evaluator implements a cited operation itself, to the standard.

```runs-machine
type single
  bits: 32
  reads_as: ieee754_binary32

operator fadd_standard(a: single, b: single) -> single
  cites: ieee754 binary32 addition, round ties_to_even, nan 0x7fc00000
```

A citation names the format, the operation, the rounding direction, and the NaN result. The standard leaves which NaN a result carries to the machine, so a citation states it:

- `nan N`: every NaN result is the bit pattern N.
- `nan first N`: a NaN operand gives its own bits with the quiet bit set, the first such operand where two are NaN. An invalid operation with no NaN operand gives N.

| Part | Choices |
|------|---------|
| Format | `binary16`, `binary32`, `binary64`, `binary128` |
| Operation | `addition`, `subtraction`, `multiplication`, `division`, `squareRoot`, `fusedMultiplyAdd` |
| Rounding | `ties_to_even`, `ties_to_away`, `toward_zero`, `toward_positive`, `toward_negative` |

Where the machine deviates from the standard, the body states the deviation. A machine that flushes subnormal operands and results to zero, keeping the sign, wraps the cited operation:

```runs-machine
operator flush(x: single) -> single
  if bits(x[30:23]) == 0:
    cat(x[31], vec(0, 31))
  else:
    x

operator fadd(a: single, b: single) -> single as +
  flush(fadd_standard(flush(a), flush(b)))
```

A machine with no hardware floating point has no floating type. Its game's floating-point library is code, and the conversion writes it as Processors over the machine's integer types, as Spacewar's multiply and divide are written over `mus` and `dis`.

## Address spaces

An **address space** is a memory whose layout play reads. It states its unit, its address width, and its byte order:

```runs-machine
space ram
  unit: 8
  address: 16
  order: little_endian
```

| Key | Meaning |
|-----|---------|
| `unit: N` | Bits in one unit, the value one address holds. |
| `address: N` | Bits in an address. The space holds 2^N units. Address arithmetic wraps at 2^N. |
| `order: little_endian` or `order: big_endian` | Which unit of a value wider than one unit lies at the lowest address. `little_endian` puts the least significant unit there. A space with no `order` holds only types one unit wide. |

The PDP-1 has one space, core, of 4096 18-bit words:

```runs-machine
space core
  unit: 18
  address: 12
```

A machine with several memories that play reads, such as a console's video memory or a cartridge's banks, has one space for each. A description needs a space only where some game's play reads layout. A space states no contents. Which Records lie where is the RUNS text's `layout`.

## Stated layout

In a layout glitch, play reads past the last slot of a collection, or reads one kind of object as another. In that state the rule is whatever lies there in memory, so the layout is part of the game. The RUNS text states it with a **layout** declaration in a `.runs` file. The declarations place everything the layout does not, and follow the layout where it states it.

```text
layout ram
  record hits at 0x0300
  record lines after hits
  fixed at 0x0313: 0xa9, 0x00
```

| Line | Meaning |
|------|---------|
| `record R at A` | R's first unit lies at address A. |
| `record R after Q` | R's first unit lies right after the last unit of Q. |
| `record R over Q` | R's first unit lies at Q's first unit. R and Q share units. |
| `... by slot` | A collection's fields lie slot by slot: slot 0's fields in declared order, then slot 1's. This is the default. |
| `... by field` | A collection's fields lie field by field: every slot of the first field, then every slot of the next. |
| `field R.f at A`, `field R.f after Q` | One field's slots lie together, for a Record whose fields do not. |
| `fixed at A: v, ...` | Units whose contents play reads and the game never writes, such as the bytes of code a stray read reaches. One value per unit. |

Only Records that play reads through layout are placed. A placed Record has no enum field: where play reads a value's bits through layout, the bits are the game's, so the field has a machine type and the RUNS text gives its values. Each field's type is a whole number of the space's units wide. Two placements that share a unit are refused, unless one is `over` the other.

### The read rule

A placed Record's fields live in the space's units. A field of type T is `k` units wide, its type's bits over the space's unit. Slot i of field f lies at:

- `by slot`: R's address, plus i times the units of one slot, plus the units of the fields declared before f.
- `by field`: R's address, plus R's count times the units of the fields declared before f, plus i times k.
- `field R.f`: f's address, plus i times k.

The address wraps at the space's address width. i is any integer. A slot from 0 to the last reads and writes as it always does. An index past the last slot, or below 0, reads what the layout puts at that address:

1. Take the k units from the address up.
2. Take each unit's bits from the field slot or the `fixed` value that holds that unit.
3. Join the units in the space's order into one vector of k units. That vector is the value, of f's type.

A write past the last slot splits the value into k units in the space's order and writes each unit into the field slot that holds it. It replaces that slice of the slot's value and leaves its other bits.

Every unit a read or write reaches is placed. A read or write that reaches a unit no layout places, or a write that reaches a `fixed` unit, means the RUNS text is wrong. A unit the game writes is part of a Record, and the conversion places that Record.

The contract still holds. A Processor that reads through layout declares every Record whose units it reads, under `reads:` or `writes:`. A Processor that writes through layout declares every Record whose units it writes, under `writes:`. A field slot with no initial value is unknown until the game sets it or the world gives it, through layout as elsewhere. A read through layout that reaches it is the same error as any read of an unknown field. A write through layout that covers only part of an unknown slot is an error too.

Records placed `over` each other are one memory read two ways. Every read or write of one is a read or write of the units they share, so a Processor that touches one declares both.

This contract is today's text form, and it falls short of the vision in two ways. In the vision a Processor declares no Records, and only the Network knows which Fields reach its inputs and outputs (CONTEXT.md 166-169). A write here replaces part of a slot in place, where the vision writes each value once into a fresh place (90-92). How a read or write through layout is wired in the vision is open.

### An example

A machine with the `ram` space above, and two Records:

```text
game record hits[8]
  line: addr = 0            # 2 units a slot

game record lines
  count: byte = 0           # 1 unit
  first: addr = 0           # 2 units
```

`hits` takes units 0x0300 to 0x030f. `lines.count` lies at 0x0310, and `lines.first` at 0x0311 and 0x0312. A read of `hits.line[8]` reaches 0x0310 and 0x0311. Little-endian, the unit at 0x0310 is the low byte. So the read gives `cat(low byte of lines.first, lines.count)`, and the Processor declares `reads: lines`. A write of `hits.line[8]` sets `lines.count` to the value's low byte and the low byte of `lines.first` to its high byte.

A reference the original kept as an address becomes an index into the collection it points into. The declarations spell the index as the machine's address. A stale reference is an index the game kept after its slot changed meaning. In range, it reads that slot as it is now. Past the end, it reads what the layout puts there.

## Instructions are not part of the description

`type insn` is not part of a machine description. A Record that holds code is impure, because instructions a Processor runs are logic, and logic lives in a Processor's own text. [A Record holds no code](./DIGS_EXPRESSION_LANGUAGE.md#a-record-holds-no-code) states the rule.

A machine glitch runs data as code or jumps into the middle of a routine. Its rule is what the machine does with those bytes on that path, and the RUNS text states that rule in a Processor. The instruction encodings that rebuild the bytes belong to the target's compiler.

## The host is not part of the description

A machine description says nothing about how the world drives the game. The events that fire a top Network (power-on, reset, a start address, a frame, an interrupt) and the devices that carry what comes in and what leaves belong to the machine's declarations. [Declarations](./DECLARATIONS.md) states them. The description holds types, literals, operators, and address spaces.

## The PDP-1 description

This is `pdp1.runs-machine`. It holds every operator Spacewar's play reaches.

The PDP-1 manual numbers a word's bits from 0 at the sign to 17 at the least significant. The core numbers from 0 at the least significant. So the manual's bit 17 is `a[0]`, and the sign, the manual's bit 0, is `a[17]`.

```runs-machine
machine pdp1

type word
  bits: 18
  reads_as: ones_complement

literals
  type: word
  prefix 0 base 8
  default base 10

space core
  unit: 18
  address: 12

# A number fits a word if its magnitude fits 18 bits. A negative number is
# the complement of its magnitude, so -0 is 0o777777.
operator word_of(n: count) -> word as literal
  requires: and(n >= -0o777777, n <= 0o777777) else "{n} does not fit a word"
  if n >= 0:
    vec(n, 18)
  else:
    not(vec(-n, 18))

operator count_of(a: word) -> count as count
  requires: not(a[17]) else "not a count"
  bits(a)

# add: end-around carry. A sum of all ones is +0, so add never gives -0.
operator add(a: word, b: word) -> word as +
  let s = bits(a) + bits(b)
  let e = (s + s div 0o1000000) mod 0o1000000
  if e == 0o777777:
    vec(0, 18)
  else:
    vec(e, 18)

# sub: complement a, add b with end-around carry, complement the sum. It gives
# -0 where the hardware does, as in 0 - 0.
operator sub(a: word, b: word) -> word as -
  let s = bits(not(a)) + bits(b)
  let e = (s + s div 0o1000000) mod 0o1000000
  not(vec(e, 18))

operator neg(a: word) -> word as unary -
  not(a)

operator com(a: word) -> word as ~
  not(a)

operator bit_and(a: word, b: word) -> word as &
  and(a, b)

operator bit_or(a: word, b: word) -> word as |
  or(a, b)

operator bit_xor(a: word, b: word) -> word as ^
  xor(a, b)

# sal: the sign stays, bits 16 to 1 take bits 15 to 0, bit 0 takes the sign.
operator sal(a: word, n: count) -> word as <<
  let v = a
  for _ in 1 .. n:
    let v = cat(cat(v[17], v[15:0]), v[17])
  v

# sar: the sign stays and fills from the top.
operator sar(a: word, n: count) -> word as >>
  let v = a
  for _ in 1 .. n:
    let v = cat(v[17], v[17:1])
  v

operator ral(a: word, n: count) -> word
  let v = a
  for _ in 1 .. n:
    let v = cat(v[16:0], v[17])
  v

operator rar(a: word, n: count) -> word
  let v = a
  for _ in 1 .. n:
    let v = cat(v[0], v[17:1])
  v

# The pair operators work on the 36 bits h:l, h above l.
operator rcl(h: word, l: word, n: count) -> (word, word)
  let p = cat(h, l)
  for _ in 1 .. n:
    let p = cat(p[34:0], p[35])
  (p[35:18], p[17:0])

operator rcr(h: word, l: word, n: count) -> (word, word)
  let p = cat(h, l)
  for _ in 1 .. n:
    let p = cat(p[0], p[35:1])
  (p[35:18], p[17:0])

# scl: h's sign stays, and is shifted in at the bottom of l.
operator scl(h: word, l: word, n: count) -> (word, word)
  let p = cat(h, l)
  for _ in 1 .. n:
    let p = cat(cat(p[35], p[33:0]), p[35])
  (p[35:18], p[17:0])

# scr: h's sign stays and fills from the top; l takes h's low bit.
operator scr(h: word, l: word, n: count) -> (word, word)
  let p = cat(h, l)
  for _ in 1 .. n:
    let p = cat(p[35], p[35:1])
  (p[35:18], p[17:0])

# mus, one multiply step: if l's low bit is set, add m to h with end-around
# carry. Then shift h:l right one place, a 0 in at the top.
operator mus(h: word, l: word, m: word) -> (word, word)
  let ac = h
  if l[0]:
    let s = bits(h) + bits(m)
    let ac = vec((s + s div 0o1000000) mod 0o1000000, 18)
  (cat(vec(0, 1), ac[17:1]), cat(ac[0], l[17:1]))

# dis, one divide step: rotate h:l left one place with h's sign complemented
# into l's low bit. If that bit is 1, add the complement of m, else add m + 1,
# with end-around carry. A sum of all ones is +0.
operator dis(h: word, l: word, m: word) -> (word, word)
  let ac = cat(h[16:0], l[17])
  let io = cat(l[16:0], not(h[17]))
  let s = bits(ac) + bits(m) + 1
  if io[0]:
    let s = bits(ac) + bits(not(m))
  let e = (s + s div 0o1000000) mod 0o1000000
  if e == 0o777777:
    (vec(0, 18), io)
  else:
    (vec(e, 18), io)

operator popcount(a: word) -> count
  let c = 0
  for i in 0 .. 17:
    let c = c + bits(a[i])
  c

# == and != compare all 18 bits, so -0 != 0.
operator same(a: word, b: word) -> cond as ==
  bits(a) == bits(b)

operator differs(a: word, b: word) -> cond as !=
  bits(a) != bits(b)

# A word orders against 0 only, by its sign. -0 < 0 is true.
operator negative(a: word, 0) -> cond as <
  a[17]

operator not_positive(a: word, 0) -> cond as <=
  or(a[17], bits(a) == 0)

operator positive(a: word, 0) -> cond as >
  not(or(a[17], bits(a) == 0))

operator not_negative(a: word, 0) -> cond as >=
  not(a[17])
```

| RUNS text | Operator | The PDP-1's |
|-----------|----------|-------------|
| a literal | `word_of` | A word as the assembler writes it. |
| `a + b` | `add` | `add` |
| `a - b` | `sub` | `sub` |
| `-a`, `~a` | `neg`, `com` | `cma` |
| `a & b`, `a \| b`, `a ^ b` | `bit_and`, `bit_or`, `bit_xor` | `and`, `ior`, `xor` |
| `a << n`, `a >> n` | `sal`, `sar` | `sal`, `sar` |
| `ral(a, n)`, `rar(a, n)` | `ral`, `rar` | `ral`, `rar` |
| `rcl(h, l, n)`, `rcr(h, l, n)` | `rcl`, `rcr` | `rcl`, `rcr` on AC:IO |
| `scl(h, l, n)`, `scr(h, l, n)` | `scl`, `scr` | `scl`, `scr` on AC:IO |
| `mus(h, l, m)` | `mus` | `mus`, AC:IO and the word it adds |
| `dis(h, l, m)` | `dis` | `dis`, AC:IO and the divisor |
| `popcount(a)` | `popcount` | No instruction. Spacewar builds an `scl` from a random number, and `popcount` gives the places it shifts. |
| `a == b`, `a != b` | `same`, `differs` | `sad`, `sas` |
| `a < 0`, `a <= 0`, `a > 0`, `a >= 0` | `negative`, `not_positive`, `positive`, `not_negative` | `spa`, `sma`, `sza` and their combinations |

The PDP-1 word has no `*` or `/`. Spacewar multiplies and divides with subroutines over `mus` and `dis`, and RUNS-Spacewar writes them as Processors.

The word's edge words are 0, -0 (`0777777`), 1, -1 (`0777776`), the extremes `0377777` and `0400000`, and `0777` and `0400777`.

The PDP-1 description states `core` for a PDP-1 game whose play reads layout. Spacewar's play reads none, so its text has no `layout`.

## A second machine: an 8-bit byte with carry

A generic 8-bit micro has two's complement bytes, a carry flag, a 16-bit address bus, and little-endian memory, as a 6502 does. Its description has the same form with other parameters. The sketches in [Declarations](./DECLARATIONS.md) declare a game on this machine:

```runs-machine
machine micro8

type byte
  bits: 8
  reads_as: twos_complement

type bit
  bits: 1
  reads_as: unsigned

type addr
  bits: 16
  reads_as: unsigned

literals
  type: byte
  prefix 0x base 16
  prefix 0b base 2
  default base 10

space ram
  unit: 8
  address: 16
  order: little_endian

operator byte_of(n: count) -> byte as literal
  requires: and(n >= -128, n <= 255) else "{n} does not fit a byte"
  vec(n, 8)

operator bit_of(n: count) -> bit as literal
  requires: and(n >= 0, n <= 1) else "{n} does not fit a bit"
  vec(n, 1)

operator addr_of(n: count) -> addr as literal
  requires: and(n >= 0, n <= 0xffff) else "{n} does not fit an addr"
  vec(n, 16)

# An index register counts 0 to 255.
operator byte_count(a: byte) -> count as count
  bits(a)

operator addr_count(a: addr) -> count as count
  bits(a)

operator adc(a: byte, m: byte, c: bit) -> (byte, bit, bit)
  let s = bits(a) + bits(m) + bits(c)
  let r = vec(s, 8)
  (r, vec(s div 256, 1), and(not(xor(a[7], m[7])), xor(a[7], r[7])))

# Shift left: the byte and the carry out.
operator asl(a: byte) -> (byte, bit)
  (cat(a[6:0], vec(0, 1)), a[7])

operator byte_and(a: byte, b: byte) -> byte as &
  and(a, b)

operator byte_same(a: byte, b: byte) -> cond as ==
  bits(a) == bits(b)

operator byte_differs(a: byte, b: byte) -> cond as !=
  bits(a) != bits(b)
```

What changed from the PDP-1 is only parameters and bodies. There are three types, not one. The default literal base is decimal, with `0x` and `0b` prefixes. The space has 8-bit units and an order. `byte` has no `+`, because the machine adds only with carry, so the RUNS text writes `adc` and stores the carry where a later routine reads it. `byte` has no ordering comparison. A game that branches on the carry or the sign stores that bit and compares it with `==`.

The byte's edge words are `0x00`, `0x01`, `0xFF`, `0x7F`, `0x80`, `0x0F`, and `0x8F`. It has no -0.

## What the loader rejects

Each error comes from one of four stages. The description stage finds an error as the loader reads the machine description. `runs.check` finds an error in the RUNS text against the description before anything runs. The layout stage finds an error in a `layout` declaration. Run time finds an error while a routine runs. An error at the description stage means the description is wrong. A failed `requires:` and a layout error at run time mean the RUNS text is wrong.

| Error | Stage | When |
|-------|-------|------|
| `the program names no machine; declare machine <name> in a .runs file` | Description | No `.runs` file of the program has a `machine` line. |
| `the program names two machines, <a> and <b>` | Description | Two `machine` lines name different machines. |
| `no <name>.runs-machine in the program's directory or a machine directory` | Description | The loader finds no description file. |
| `<file> describes machine <a>, not <b>` | Description | The description's `machine` line does not match its file name. |
| `<name> belongs to the machine description` | Description | A `.runs` file declares a `type` other than `insn`. |
| `... defined twice` | Description | Two types, two spaces, or two operators share a name, or the description has two `literals` blocks. |
| `type <T>: bits is a whole number, 1 or more` | Description | A type has no `bits`, or its `bits` is not a whole number of 1 or more. |
| `type <T>: no reading <R>` | Description | `reads_as` names a reading the table above does not list. |
| `type <T>: field <f> is outside its <N> bits`, `type <T>: fields <f> and <g> overlap` | Description | A `fields` range reaches past the type's width, or two ranges share a bit. |
| `literals: no type` | Description | The `literals` block names no type, or a type the description does not declare. |
| `literals: <P> is not a prefix` | Description | A prefix is not `0` or `0` and one letter. |
| `literals: base <B>` | Description | A base is not 2, 8, 10, or 16. |
| `space <S>: unit and address are whole numbers, 1 or more` | Description | A space lacks `unit` or `address`, or either is not a whole number of 1 or more. |
| `space <S>: order is little_endian or big_endian` | Description | `order` has another value. |
| `operator <X>: no type <T>` | Description | A signature names a type the description does not declare. |
| `operator <X>: <name> is a primitive of the core` | Description | An operator takes the name of a core primitive. |
| `operator <X>: <name> is not a primitive of the core or an operator above it` | Description | A body calls anything but a core primitive or an operator defined above it. |
| `operator <X>: <op> takes vectors of one width, not <a> and <b>` | Description | `and`, `or`, or `xor` gets vectors of two widths. |
| `operator <X>: <op> takes an integer, not a vector`, `... takes a vector, not an integer` | Description | A primitive gets the wrong kind of value. |
| `operator <X>: [<hi>:<lo>] of a <w>-bit vector` | Description | A slice's bounds are not constants, hi is below lo, or hi is not below the width. |
| `operator <X>: vec takes a constant width` | Description | `vec`'s width is not a constant of 1 or more. |
| `operator <X>: returns <a>, not <b>` | Description | The body's value has another type, width, or tuple size than the signature's result. |
| `operator <X>: a body ends in its value` | Description | A block that must give a value does not end in an expression or an `if` with `else` whose every arm gives one. |
| `operator <X>: let changes <name> from <a> to <b>` | Description | A `let` gives a name a value of another type or width. |
| `operator <X>: unknown name <name>` | Description | A body uses a name that is not a parameter or a name bound on every path. |
| `operator <X> as <b>: takes <n> operands` | Description | An operator has the wrong number of parameters for its symbol. |
| `operator <X> as <b>: a comparison gives cond` | Description | A comparison operator's result is not `cond`. |
| `operator <X> as literal takes one count and gives a type`, `operator <X> as count takes one type and gives a count` | Description | A conversion's signature is wrong. |
| `operators <X> and <Y> both take <b> on (<types>)` | Description | Two operators take one symbol on the same operand types. |
| `operator <X>: cites no operation <text>` | Description | A citation names a format, operation, rounding, or NaN rule the tables above do not list. |
| `<t> is not an octal number` (or `binary`, `decimal`, `hexadecimal`) | Parser | A literal holds a digit outside its base. |
| `<X> is not an operator of the machine; a routine is run, not called` | Parser | RUNS text calls a name that is not an operator of the description or a declared instruction. |
| `no type <T>` | `runs.check` | A field's type is not an enum, `int` in a stream, or a type of the description. |
| `no operator <b> on (<types>)` | `runs.check` | RUNS text uses a symbol on operand types no operator takes. |
| `<X> takes <n> values, not <m>` | `runs.check` | A call passes the wrong number of operands. |
| `<X> takes a <T>, not a <U>` | `runs.check` | An operand has another type than its parameter, and no conversion makes it one. |
| `<T> has no literals` | `runs.check` | A literal stands where a type with no `as literal` operator is wanted. |
| `<T> is not a count` | `runs.check` | A value stands where a count is wanted, and its type has no `as count` operator. |
| `<b> compares a <T> with <literal> only` | `runs.check` | An operand where the signature has a literal is anything else. |
| the operator's `requires:` message | `runs.check`, run time | A `requires:` is false. `runs.check` finds it when its operands are constants. On the PDP-1 these are `<n> does not fit a word` and `not a count`. |
| `operator <X> divides by zero`, `operator <X>: bit <i> of a <w>-bit vector` | Run time | A body reaches `div` or `mod` by 0, or a bit outside a vector. |
| `layout <S>: no space <S> on machine <M>` | Layout | A `layout` names a space the description does not declare. |
| `layout <S>: <R> is placed twice` | Layout | Two lines place one Record or one field. |
| `layout <S>: <R> and <Q> share address <A>` | Layout | Two placements share a unit, and neither is `over` the other. |
| `layout <S>: <R> is not placed` | Layout | `after` or `over` names a Record that no line before it places. |
| `layout <S>: <R>.<f> is an enum; its bits are the game's, so give it a machine type` | Layout | A placed Record has an enum field. |
| `layout <S>: <R>.<f> is a <T> of <n> bits, not whole <u>-bit units` | Layout | A placed field's type is not a whole number of units wide. |
| `layout <S>: <R>.<f> spans units in a space with no order` | Layout | A field wider than one unit lies in a space that states no `order`. |
| `layout <S>: <A> is past the space's <N> units` | Layout | A placement or a `fixed` value reaches past the space. |
| `layout <S>: <v> does not fit a <u>-bit unit` | Layout | A `fixed` value is wider than a unit. |
| `address <A> of <S> holds nothing the layout places` | Run time | A read or write through layout reaches an unplaced unit. |
| `address <A> of <S> is fixed; a unit the game writes is a Record's` | Run time | A write through layout reaches a `fixed` unit. |
| `<P> does not declare reads: <Q>`, `... writes: <Q>` | Run time | A read or write through layout reaches units of a Record the Processor does not declare. |
| `<R>.<f>[<i>] is unknown: the game has not set it, so the world gives it` | Run time | A read through layout, or a write that covers part of a slot, reaches a field slot with no value. |

## Grammar

This grammar describes a `.runs-machine` file, the core, and the two declarations a `.runs` file gains. Indentation is two spaces a level. A comment runs from `#` to the end of the line.

```text
description = "machine" NAME { declaration }
declaration = type | literals | space | operator

type        = "type" NAME { indented type_line }
type_line   = "bits" ":" NUMBER
            | "reads_as" ":" READING
            | "reads_as" ":" "fields" { indented NAME ":" "[" NUMBER ":" NUMBER "]" }
READING     = "unsigned" | "twos_complement" | "ones_complement" | "sign_magnitude" | "bcd"
            | "ieee754_binary16" | "ieee754_binary32" | "ieee754_binary64"

literals    = "literals" { indented literal_line }
literal_line= "type" ":" NAME
            | "prefix" PREFIX "base" BASE
            | "default" "base" BASE
PREFIX      = "0" [ LETTER ]
BASE        = "2" | "8" | "10" | "16"

space       = "space" NAME { indented space_line }
space_line  = "unit" ":" NUMBER
            | "address" ":" NUMBER
            | "order" ":" ( "little_endian" | "big_endian" )

operator    = "operator" NAME "(" [ param { "," param } ] ")" "->" result [ "as" symbol ]
              { indented requires } ( indented cites | body )
param       = NAME ":" tname | NUMBER
result      = tname | "(" tname "," tname { "," tname } ")"
tname       = NAME | "count" | "cond"
symbol      = "+" | "-" | "&" | "|" | "^" | "<<" | ">>"
            | "==" | "!=" | "<" | "<=" | ">" | ">="
            | "unary" "-" | "~" | "literal" | "count"
requires    = "requires" ":" cexpr "else" STRING
cites       = "cites" ":" "ieee754" FORMAT OPERATION "," "round" ROUNDING "," "nan" [ "first" ] NUMBER
FORMAT      = "binary16" | "binary32" | "binary64" | "binary128"
OPERATION   = "addition" | "subtraction" | "multiplication" | "division"
            | "squareRoot" | "fusedMultiplyAdd"
ROUNDING    = "ties_to_even" | "ties_to_away" | "toward_zero" | "toward_positive" | "toward_negative"

body        = { indented step } indented value
step        = "let" names "=" cexpr
            | "if" cexpr ":" steps { "elif" cexpr ":" steps } [ "else" ":" steps ]
            | "for" ( NAME | "_" ) "in" cexpr ".." cexpr ":" steps
steps       = { indented step }
value       = cexpr
            | "if" cexpr ":" body { "elif" cexpr ":" body } "else" ":" body
names       = NAME | "(" ( NAME | "_" ) { "," ( NAME | "_" ) } ")"
cexpr       = sum [ ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) sum ]
sum         = product { ( "+" | "-" ) product }
product     = negation { ( "*" | "div" | "mod" ) negation }
negation    = "-" negation | postfix
postfix     = primary { "[" cexpr [ ":" cexpr ] "]" }
primary     = NUMBER
            | NAME [ "(" [ cexpr { "," cexpr } ] ")" ]
            | "(" cexpr { "," cexpr } ")"
NUMBER      = DIGIT { DIGIT } | "0o" OCTAL { OCTAL } | "0x" HEX { HEX } | "0b" BIT { BIT }

machine_line= "machine" NAME                                        (in a .runs file)
layout      = "layout" NAME { indented placement }                  (in a .runs file)
placement   = "record" NAME ( "at" NUMBER | "after" NAME | "over" NAME ) [ "by" ( "slot" | "field" ) ]
            | "field" NAME "." NAME ( "at" NUMBER | "after" NAME )
            | "fixed" "at" NUMBER ":" NUMBER { "," NUMBER }
```

In `body`, `steps`, and `value`, each line is indented one level from the line that opens it. A body's last line is its value, so an `if` on the last line of a body is a `value`, and an `if` on any other line is a `step`. A call in `primary` names a core primitive (`bits`, `vec`, `cat`, `and`, `or`, `xor`, `not`) or an operator defined above. In the `.runs` declarations, NUMBER is read by the description's literal forms, and in a body by the core's.

*MIT License. Open for implementation, extension, and critique.*
