# DIGS: Deterministic Inspectable Game Syntax

> **Status.** Working draft. This reference describes the Processor syntax that the Spacewar port's reference evaluator, `tools/runs.py`, accepts and enforces. Every accepted example on this page loads in that evaluator, passes its contract check, and runs. Every rejected example fails with the error quoted in its first line.

DIGS is the language of Processor bodies. Processors live in `.runs-prim` files. Records, streams, enums, and Networks live in `.runs` files and are described in [Network topology](./NETWORK_TOPOLOGY.md). Network guards use the expressions on this page.

A Processor is one rule of the game. It declares the Records it reads and the Records it writes. Inside its body it computes freely. It binds locals, loops, and updates its declared Records in place. Purity holds at the boundary. What a Processor does depends only on the Records and parameters it declares, and its only effects are on the Records it declares as written.

## A running example

The examples on this page together form one program. Its Processors are taken from the Spacewar port: the integer square root, the random number generator, and the explosion's dot. The square root matches the original on all 65,536 inputs the port checked against SIMH. The plot is simplified to read one position instead of the object table.

```runs
record square_root_call
  entry: word = 0           # sqt: jda leaves the argument here; it doubles as the remainder
  passes_left: word = 0     # sq1
  root: word = 0            # sq2: the result

record random
  number: word = 0          # ran

record cloud
  spread: word = 1          # which shift spreads the dots, scr 1s or scr 3s
  scatter: word = 0         # places this dot's scl shifts

record position
  x: word = 0
  y: word = 0

stream display
  x: word
  y: word
  intensity: int

network demo
  writes: display
  run next_random
  run take_entry
  run square_root
  run scatter_particle
  run plot_particle
```

## Processor declarations

A Processor has a name, optional parameters, headers, and a body:

```runs-prim
# The `random` macro: the generator's next value.
processor next_random
  writes: random
  set random.number = (rar(random.number, 1) ^ 0355670) + 0355670

processor take_entry
  reads: random
  writes: square_root_call
  set square_root_call.entry = random.number & 0377777
```

| Header | Meaning |
|--------|---------|
| `reads: a, b` | Records the body may read. |
| `writes: a, b` | Records and streams the body may write. A Processor may also read what it writes. |
| `requires: expression` | A precondition. If it is false when the Processor fires, the port is wrong. |

Parameters are the values a Network passes with `run`, such as the slot index in `run count_down(slot)`. They have no declared type. A Network usually passes a count.

The evaluator checks each Record access when it happens. A read of a Record in neither `reads:` nor `writes:` is an error, and so is a write to a Record not in `writes:`:

```runs-prim-rejected
# rejected: peek does not declare reads: random
record random
  number: word = 0

record seen
  value: word = 0

network top
  run peek

processor peek
  writes: seen
  set seen.value = random.number
```

A Processor fires no routine. It has no `run`, `match`, or `stop`, and an expression cannot call a Processor or a Network:

```runs-prim-rejected
# rejected: square_root is not an operator of the word; a routine is run, not called
processor half_root
  writes: square_root_call
  set square_root_call.root = square_root(square_root_call.entry) >> 1
```

A routine the original called, such as the square root subroutine, becomes a Processor over the Records it hands values through. The caller becomes a Network that sets the input, fires the Processor, and then fires a Processor that uses the output.

## Statements

| Statement | Meaning |
|-----------|---------|
| `let name = e` | Bind a new local. |
| `let (a, b) = e` | Bind two locals from a pair, such as the result of `scr`. |
| `set target = e` | Update a local bound by `let`, or a field of a declared Record. The target may be a pair, as in `set (high, low) = rcl(high, low, 18)`. |
| `if e:` ... `elif e:` ... `else:` | Run the first arm whose condition is true. |
| `loop at most N:` | Run the body again and again until `break` or `return`. Running more than N passes means the port is wrong. |
| `for i in a .. b:` | Run the body once for each count from `a` to `b`, both included, in ascending order. |
| `break` | Leave the innermost `loop`. |
| `continue` | Start the next pass of the innermost `loop`. |
| `return` | End the Processor. |
| `emit stream: a, b, c` | Append one entry to a declared stream, one value per field in order. |
| `unreachable` | Mark a path the game never takes. Reaching it means the port is wrong. |

Here is the Spacewar square root, a loop with `continue` and `return`:

```runs-prim
# BBN integer square root (sqt), over its own words. Binary point right of
# bit 17 in square_root_call.entry, between bits 8 and 9 in .root. Two bits
# of input per pass, 18 passes.
processor square_root                                       # sqt
  writes: square_root_call
  set square_root_call.passes_left = -023
  set square_root_call.root = 0
  let input_bits = square_root_call.entry
  set square_root_call.entry = 0
  loop at most 023:
    set square_root_call.passes_left = square_root_call.passes_left + 1
    if square_root_call.passes_left >= 0:
      return
    set square_root_call.root = square_root_call.root << 1
    let next = square_root_call.entry
    set (next, input_bits) = rcl(next, input_bits, 2)
    if next == 0:
      continue
    set square_root_call.entry = next
    set next = (square_root_call.root << 1) + 1 - square_root_call.entry
    if next > 0:
      continue
    if next < 0:
      set next = -next
    set square_root_call.entry = next
    set square_root_call.root = square_root_call.root + 1
```

`sq1` and `sq2` are fields of `square_root_call`, not locals, because they are the routine's own words in the original. A value that a Processor sets before it reads it, and never hands on, is a local.

## Expressions

An expression produces one of five kinds of value:

- A **word**: the 18-bit word of the original machine. Every number literal and every Record field of type `word` is a word.
- A **count**: an integer used as an index or a bound. A `for` index, a parameter that a Network passed as a count, and the result of `popcount` are counts.
- A **condition**: `true` or `false`, the result of a comparison, `and`, `or`, or `not`.
- An **enum member**, written by its name.
- A **pair** of words, the result of `rcl`, `rcr`, `scl`, `scr`, and `mus`, or written as `(a, b)`.

### Names and places

- `record.field` reads a field of a single Record.
- `record.field[i]` reads element `i` of a field of a collection. `i` is a count.
- A bare name is a parameter, a local, or an enum member.

A number literal is a run of digits. A literal with a leading `0` is octal, as in `0355670` and `-04000`. Other literals are decimal. A literal must fit in 18 bits. RUNS has no hexadecimal, fractional, or string literals.

### Operators

From the tightest binding to the loosest:

| Level | Operators |
|-------|-----------|
| 1 | `.field`, `[index]`, operator calls such as `rcl(a, b, 2)` |
| 2 | unary `-`, unary `~` |
| 3 | `*`, `/` |
| 4 | `+`, `-` |
| 5 | `<<`, `>>` |
| 6 | `&` |
| 7 | `^` |
| 8 | `\|` |
| 9 | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| 10 | `not` |
| 11 | `and` |
| 12 | `or` |

Binary operators group from the left. The bitwise operators bind tighter than the comparisons, so `a | b == c` means `(a | b) == c`. Arithmetic binds tighter than `|`, so `(random.number | 0400000) + x` needs its parentheses. `and` and `or` take conditions and evaluate their right side only when they need it.

`*` and `/` parse, but the word defines no multiply or divide, so evaluating either is an error. Spacewar's multiply and divide are not ported yet.

If either operand of `+`, `-`, or a comparison is a count, the operation is on counts, so `slot + 1` is a count. A word that is not negative can stand where a count is needed, such as a shift amount.

## The word

`word` is the PDP-1's 18-bit ones' complement word. The evaluator defines it in code. RUNS has no text form yet for the original-machine description that should supply it. The Spacewar port's `tools/reach_oracle.py` checked the evaluator's `+`, `-`, `<<`, `>>`, `ral`, and `rar` against SIMH on 5,967,629 results from real play, and all of them matched. The pair operators and `mus` have no such check yet.

| Operation | What it does |
|-----------|--------------|
| `-a`, `~a` | Flip all 18 bits. Both are the ones' complement negation. `-0` is minus zero, `0777777`. |
| `a + b`, `a - b` | The PDP-1's add and subtract, with end-around carry. Positions wrap around, so Spacewar's screen is a torus. |
| `a & b`, `a \| b`, `a ^ b` | Bitwise on all 18 bits. |
| `a << n` | The PDP-1's `sal`. Shift left `n` places, keep the sign bit, and shift the sign bit in at the bottom. `-1 << 1` is `-2`. |
| `a >> n` | The PDP-1's `sar`. Shift right `n` places and copy the sign bit. A negative word rounds toward zero, so `-1 >> 1` is `-0`. |
| `a == b`, `a != b` | Compare all 18 bits. `-0 == 0` is false. |
| `a < 0`, `a <= 0`, `a > 0`, `a >= 0` | Test the sign. A word compares with 0 only. The evaluator checks this when the comparison runs, and the right side must then be the word 0. `-0 < 0` is true. `-0 <= 0` is true. `0 <= 0` is true. |

The word's own operators are the only calls in RUNS:

| Operator | What it does |
|----------|--------------|
| `ral(a, n)`, `rar(a, n)` | Rotate the word left or right `n` places. |
| `rcl(h, l, n)`, `rcr(h, l, n)` | Rotate the 36-bit pair `h`, `l` left or right `n` places. The result is a pair. |
| `scl(h, l, n)`, `scr(h, l, n)` | Shift the 36-bit pair left or right `n` places and keep the sign of `h`. `scl` shifts the sign of `h` in at the bottom of `l`. The result is a pair. |
| `mus(h, l, m)` | One step of the PDP-1's multiply. The result is a pair. |
| `popcount(a)` | The number of bits set in `a`, as a count. |

The explosion's dot shows the pair operators. The original builds an `scl` instruction from a random number and then executes it. RUNS states that rule as a shift by `popcount` places.

```runs-prim
# The original builds an scl from the random number's low 9 bits; it
# shifts one place per bit set.
processor scatter_particle
  reads: random
  writes: cloud
  set cloud.scatter = popcount(random.number & 0777)

# The dot is presentation. The random number drawn for it is the game:
# hyperspace draws from the same generator.
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

## What the evaluator rejects

| Error | When |
|-------|------|
| `... does not declare reads: ...` or `... writes: ...` | A Processor touches a Record it did not declare. |
| `... is not an operator of the word; a routine is run, not called` | An expression calls anything but a word operator. |
| `run belongs to a network`, `match belongs to a network`, `stop belongs to a network` | A Processor uses `run`, `match`, or `stop`. |
| `set ... before let` | `set` names a local that `let` has not bound. |
| `let binds a local name` | `let` names a Record field. |
| `an initial value touches no Record` | A Record field's initial value reads a Record. |
| `no word operator *` | An expression evaluates `*` or `/`. |
| `a word compares with 0 only` | `<`, `<=`, `>`, or `>=` runs with a word on the left and anything but the word 0 on the right. |
| `... does not fit a word` | A literal is wider than 18 bits. |
| `loop ran past its bound` | A `loop` runs more passes than its bound. |
| `precondition fails` | A `requires:` is false when the Processor fires. |
| `reached unreachable` | An `unreachable` runs. |

A word compared with anything but 0 is rejected when it runs:

```runs-prim-rejected
# rejected: a word compares with 0 only
record score
  first: word = 0
  second: word = 5

network top
  run tie_test

processor tie_test
  writes: score
  if score.first < score.second:
    set score.first = 0
```

The loop bound, `requires:`, and `unreachable` errors never describe the game. If one of them fires, the port is wrong.

## Grammar

This summary describes what `tools/runs.py` accepts. Indentation is two spaces a level. A comment runs from `#` to the end of the line.

```text
processor   = "processor" NAME [ "(" NAME { "," NAME } ")" ] { indented ( header | statement ) }
header      = "reads" ":" NAME { "," NAME }
            | "writes" ":" NAME { "," NAME }
            | "requires" ":" expression
statement   = ( "let" | "set" ) target "=" expression
            | "if" expression ":" block { "elif" expression ":" block } [ "else" ":" block ]
            | "loop" "at" "most" expression ":" block
            | "for" NAME "in" expression ".." expression ":" block
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
sum         = product { ( "+" | "-" ) product }
product     = unary { ( "*" | "/" ) unary }
unary       = ( "-" | "~" ) unary | postfix
postfix     = primary { "." NAME | "[" expression "]" | "(" [ expression { "," expression } ] ")" }
primary     = NUMBER | "true" | "false" | NAME | "(" expression { "," expression } ")"
```

A call in `postfix` is valid only on the name of a word operator.

## Open questions

- The syntax is a working draft. It holds what one slice of Spacewar needed and will change as more is ported.
- RUNS has no text form yet for the original-machine description. It should supply `word` and any other type of the original machine, such as floating point.
- The word has no multiply or divide. Spacewar's multiply and divide are not ported yet, so how they appear in RUNS is not decided.
- Running the original machine's instructions where play reaches them, for a machine glitch, has no form yet.

*MIT License. Open for implementation, extension, and critique.*
