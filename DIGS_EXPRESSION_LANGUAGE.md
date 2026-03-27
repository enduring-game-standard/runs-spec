# DIGS — Deterministic Inspectable Game Syntax

> **Status**: Draft Specification  
> **Version**: 1.0.0-draft.1  
> **File extension**: `.runs-prim`

## Purpose

DIGS is the expression language for RUNS Processor bodies. It is the formal syntax in which game logic is written, parsed, and compiled. Source files use the `.runs-prim` extension.

DIGS is part of the EGS protocol family:

| Protocol | Phonetic | Purpose |
|----------|----------|---------|
| **AEMS** | "he aims" | Asset-Entity-Manifestation-State — what things ARE |
| **RUNS** | "he runs" | Records Update on Neutral Substrate — how things CHANGE |
| **DIGS** | "he digs" | Deterministic Inspectable Game Syntax — how Processors COMPUTE |
| **MAPS** | "he maps" | — how rules are DESIGNED |
| **WOCS** | "he wocs" | Work Offered, Claimed, Settled — how things COORDINATE |

DIGS is the enduring artifact in the RUNS compilation model. Runtimes compile it into platform-specific execution. The language must be readable, parseable, and compilable by any future runtime without dependence on any existing programming language, toolchain, or platform.

Every decision in this specification is driven by one question: *can a solo developer in a century implement this from scratch, with nothing but this document?*

---

## Design Constraints

The language is:

1. **Pure** — No side effects beyond declared outputs. A Processor's outputs depend only on its declared inputs. No I/O, no global mutable state, no external calls.
2. **Total** — All programs terminate. No unbounded loops. No general recursion. Termination is provable by structural inspection of the source, not by runtime analysis.
3. **Deterministic** — Same inputs always produce the same outputs, on every platform, forever. Fixed-point and integer types guarantee bit-exact cross-platform results. Floating-point types explicitly opt in to platform-dependent rounding.
4. **Language-agnostic** — The syntax is not borrowed from any existing programming language. It is designed to be readable by a human who has never programmed.
5. **Formally specified** — The grammar and evaluation rules in this document are precise enough that two independent implementations, written by people who never communicate, will produce identical results for all valid programs.

---

## Lexical Structure

### Character Set

Source files are UTF-8 encoded. The language uses only ASCII for keywords, operators, and identifiers. UTF-8 characters outside the ASCII range may appear only in comments and string literals.

### Line Structure

Logical lines are terminated by a newline character (U+000A). Carriage return (U+000D) preceding a newline is ignored. A source file must end with a newline.

### Indentation

Block structure is expressed through indentation. Each level of nesting increases indentation by exactly **two spaces**. Tab characters (U+0009) are illegal in indentation. A block begins after a colon (`:`) at the end of a line and consists of all subsequent lines indented deeper than the introducing line.

```
if x > 0:
  let y = x + 1      # indented two spaces: inside the if-block
  output result = y
```

### Comments

A comment begins with `#` and extends to the end of the line. There are no multi-line comment delimiters. Comments carry no semantic meaning.

```
# This is a comment
let x = 5  # This is also a comment
```

### Keywords

The following identifiers are reserved and may not be used as variable names:

```
let  output  if  elif  else  for  in  with  not  and  or
true  false  none  range
```

### Identifiers

An identifier begins with a letter (a–z, A–Z) or underscore, followed by zero or more letters, digits (0–9), or underscores. Identifiers are case-sensitive.

```
position_x
velocityY
_scratch
ship1
```

### Qualified Names

A qualified name is an optional namespace prefix followed by a colon and an identifier. Namespaces follow the same rules as identifiers.

```
spacewar:fixed18      # namespace "spacewar", name "fixed18"
doom:mobj             # namespace "doom", name "mobj"
runs:transform        # namespace "runs", name "transform"
ship                  # no namespace (local scope)
```

---

## Literals

### Integer Literals

Integer literals may be written in decimal, hexadecimal, octal, or binary. Underscores may appear between digits for readability and carry no semantic meaning.

| Format | Prefix | Example | Value |
|--------|--------|---------|-------|
| Decimal | (none) | `65536` | 65536 |
| Hexadecimal | `0x` | `0x1_0000` | 65536 |
| Octal | `0o` | `0o200000` | 65536 |
| Binary | `0b` | `0b1_0000_0000_0000_0000` | 65536 |

Negative integer literals are written with the unary minus operator: `-65536`.

### Fixed-Point Literals

Fixed-point literals are decimal numbers with a fractional part, suffixed with `fx`:

```
3.5fx            # 3.5 in 16.16 fixed-point
-0.25fx          # -0.25 in 16.16 fixed-point
```

The exact binary representation depends on the target fixed-point type. The compiler rounds to the nearest representable value.

### Float Literals

Float literals are decimal numbers with a fractional part or an exponent, with no suffix:

```
3.14159
1.0e-6
-0.5
```

### Boolean Literals

```
true
false
```

### String Literals

String literals are enclosed in double quotes. They may contain any UTF-8 character except unescaped newlines. String literals are used only for enum comparisons and diagnostic annotations — the language has no string manipulation.

```
"hello"
```

### List Literals

List literals are enclosed in square brackets, with elements separated by commas:

```
[1, 2, 3]
[]                # empty list
```

All elements must have the same type. The list's type is inferred from its elements.

---

## Type System

### Primitive Types

| Type | Width | Semantics | Cross-Platform Determinism |
|------|-------|-----------|---------------------------|
| `int` | Unbounded | Arbitrary-precision signed integer | ✅ Exact |
| `int8` | 8 bits | Signed two's-complement, wrapping | ✅ Exact |
| `int16` | 16 bits | Signed two's-complement, wrapping | ✅ Exact |
| `int32` | 32 bits | Signed two's-complement, wrapping | ✅ Exact |
| `uint8` | 8 bits | Unsigned, wrapping | ✅ Exact |
| `uint16` | 16 bits | Unsigned, wrapping | ✅ Exact |
| `uint32` | 32 bits | Unsigned, wrapping | ✅ Exact |
| `bool` | 1 bit | `true` or `false` | ✅ Exact |
| `float` | 64 bits | IEEE 754 binary64 | ⚠️ See §Determinism |
| `fixed16` | 32 bits | 16.16 signed fixed-point, two's-complement | ✅ Exact |

**Wrapping** means arithmetic overflow wraps modularly. `int32` max is `2147483647`; adding 1 yields `-2147483648`.

**Arbitrary-precision** means `int` never overflows. It is the default integer type when bit-width constraints are not required.

### Fixed-Point Arithmetic (`fixed16`)

`fixed16` stores a 32-bit signed two's-complement value where the lower 16 bits represent the fractional part. The value represented is `raw_bits / 65536`.

| Operation | Semantics |
|-----------|-----------|
| `a + b` | Add raw bits. Wraps on overflow. |
| `a - b` | Subtract raw bits. Wraps on overflow. |
| `a * b` | Multiply to 64-bit intermediate, arithmetic right shift by 16, truncate to 32 bits. |
| `a / b` | Extend `a` to 64 bits by left-shifting 16, signed divide by `b`'s raw bits, truncate to 32 bits. |
| `a >> n` | Arithmetic right shift of raw bits by `n`. |
| `a << n` | Left shift of raw bits by `n`. |

### Game-Defined Types

Games may define custom numeric types. A type definition specifies the representation, binary point, arithmetic rules, and value range:

```runs-prim
type spacewar:fixed18
  storage: int32
  width: 18
  binary_point: 17
  complement: ones
  range: -131071 to 131071
```

Fields of the type definition:
- **storage** — The primitive type used to hold the value in memory.
- **width** — The number of significant bits.
- **binary_point** — The bit position of the binary (radix) point, counted from the right. A `binary_point` of 17 means the value is an integer (point to the right of all 18 bits). A `binary_point` of 9 means 9 bits of integer and 9 bits of fraction.
- **complement** — Either `ones` or `twos`. Specifies the signed number representation. Ones-complement has two representations of zero (+0 and −0); two's-complement does not.
- **range** — The inclusive range of representable values.

Arithmetic operations on game-defined types follow the declared complement and width rules. A compiler targeting a two's-complement machine must emulate ones-complement behavior for types that declare `complement: ones`. This emulation is a compile-time concern — the expression language semantics are defined in terms of the declared arithmetic, not the host machine's arithmetic.

### Enum Types

Enum types are declared in Record definition files (`.runs`), not in Processor bodies:

```
enum spacewar:object_state
  empty
  ship
  torpedo
  exploding
  hyperspace_in
  hyperspace_out
```

In expressions, enum values are referenced by their qualified name:

```runs-prim
if object.state == spacewar:exploding:
  # ...
```

Enum values have no numeric encoding visible to the expression language. Comparison is by identity (`==`, `!=`), not by ordinal.

### Optional Types

A field declared with a trailing `?` may hold the value `none` (absence):

```
inputs:
  inflictor: doom:mobj?     # may be absent
```

An optional value must be tested before its fields are accessed:

```runs-prim
let damage = if inflictor != none then inflictor.damage else 0
```

Accessing a field on an optional value without testing for `none` is a compile-time error. The compiler rejects the program.

### List Types

A field declared with trailing `[]` is a bounded, homogeneous list:

```
inputs:
  entities: spacewar:object[24]    # list of exactly 24 objects
```

The bound is part of the type. A list's length is fixed at the value declared in its schema. There is no dynamic allocation.

### Record Types

Record types are declared in `.runs` files (Record definitions), not in the expression language. In expressions, Records are accessed via field paths and constructed via the `with` expression.

---

## Expressions

### Arithmetic Operators

| Operator | Meaning | Types |
|----------|---------|-------|
| `+` | Addition | All numeric types |
| `-` | Subtraction | All numeric types |
| `*` | Multiplication | All numeric types |
| `/` | Division | All numeric types (see §Preconditions for zero) |
| `%` | Modulo (remainder) | Integer types only |
| `-` (unary) | Negation | All numeric types |

Division of integers truncates toward zero: `7 / 2 = 3`, `-7 / 2 = -3`.

### Comparison Operators

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

All comparison operators produce `bool`. Comparisons are valid between values of the same type. Comparing values of different types is a compile-time error.

### Logical Operators

| Operator | Meaning |
|----------|---------|
| `and` | Logical conjunction (short-circuiting) |
| `or` | Logical disjunction (short-circuiting) |
| `not` | Logical negation |

Operands must be `bool`. `and` evaluates the right operand only if the left is `true`. `or` evaluates the right operand only if the left is `false`.

### Bitwise Operators

| Operator | Meaning | Types |
|----------|---------|-------|
| `&` | Bitwise AND | Integer and fixed-point types |
| `\|` | Bitwise OR | Integer and fixed-point types |
| `^` | Bitwise XOR | Integer and fixed-point types |
| `~` (unary) | Bitwise NOT (complement) | Integer and fixed-point types |
| `>>` | Arithmetic right shift (sign-extending) | Integer and fixed-point types |
| `<<` | Left shift (zero-filling) | Integer and fixed-point types |
| `>>>` | Rotate right | Fixed-width integer types only |

**Arithmetic right shift** (`>>`) fills vacated high bits with the sign bit. This matches the behavior of the PDP-1's `sar` instruction, C's signed right shift on two's-complement machines, and the dominant convention across all hardware since 1970.

**Rotate right** (`>>>`) treats the value as a circular bit register — the lowest bit wraps to the highest position. This is required for specific algorithms (e.g., the PDP-1 PRNG in Spacewar uses `rar 1s`). Rotate operates on the declared width of the type: a `uint16` rotates within 16 bits; an `int32` rotates within 32 bits.

### Operator Precedence

From highest to lowest binding:

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `not`, `-` (unary), `~` | Right |
| 2 | `*`, `/`, `%` | Left |
| 3 | `+`, `-` | Left |
| 4 | `<<`, `>>`, `>>>` | Left |
| 5 | `&` | Left |
| 6 | `^` | Left |
| 7 | `\|` | Left |
| 8 | `==`, `!=`, `<`, `>`, `<=`, `>=` | None (no chaining) |
| 9 | `and` | Left |
| 10 | `or` | Left |

Parentheses override precedence: `(a + b) * c`.

### Field Access

Fields of a Record are accessed with the dot operator:

```runs-prim
object.position_x
config.heavy_star
ship_config.outline_data
```

Field access on a value that is not a Record, or access of a field name that does not exist in the Record's schema, is a compile-time error.

### Indexed Access

Elements of a list are accessed with bracket notation:

```runs-prim
entities[0]
objects[i]
```

The index must be a non-negative integer less than the list's declared bound. Out-of-bounds access is a compile-time error when detectable, or a precondition violation at runtime.

### Sub-Processor Calls

A Processor may invoke another Processor as a pure function call:

```runs-prim
let sin_result = spacewar:sin(angle)
let product = spacewar:multiply(a, b)
```

The called Processor's declared inputs become the call arguments (positional, matching declaration order). The call returns the Processor's declared outputs as a Record — individual output fields are accessed with the dot operator:

```runs-prim
let sqrt_out = spacewar:sqrt(value)
let root = sqrt_out.root
```

**Recursion prohibition**: The call graph of all Processors must form a directed acyclic graph (DAG). A Processor may not call itself, directly or through any chain of intermediate calls. The compiler verifies this statically by topologically sorting the call graph. A cycle is a compile-time error.

This prohibition, combined with bounded iteration (below), guarantees totality: every Processor terminates.

### Record Update (`with`)

The `with` expression creates a new Record with specified fields changed:

```runs-prim
let updated = object with { velocity_x = 0, velocity_y = 0, state = spacewar:exploding }
```

The original Record is not modified — `with` produces a new value. Fields not mentioned retain their values from the original.

A compiler is permitted to optimize `with` into in-place mutation if it can prove the original value is not referenced after the update. This is an implementation detail invisible to the expression language semantics.

### Conditional Expression (Inline)

```runs-prim
let max_val = if a > b then a else b
```

Both branches must produce values of the same type. The `else` branch is required — a conditional expression always produces a value.

### List Concatenation

```runs-prim
let extended = existing_list ++ [new_element]
```

The `++` operator concatenates two lists of the same element type. The result's length is the sum of the operands' lengths. If the result exceeds the declared bound of the target output field, it is a precondition violation.

---

## Statements

### `let` Binding

Introduces an immutable name bound to a value:

```runs-prim
let velocity = old_velocity + acceleration
```

A name bound by `let` may not be reassigned. A subsequent `let` in the same scope with the same name **shadows** the previous binding — it introduces a new, independent binding. The previous value is not mutated.

```runs-prim
let x = 5
let x = x + 1    # shadows: new 'x' is 6. Old 'x' (value 5) is gone.
```

Shadowing exists to enable sequential refinement of a value through a pipeline of operations, without requiring unique names for every intermediate step. It is semantically equivalent to introducing fresh temporaries — the compiler may implement it either way.

### `output` Statement

Assigns a value to a declared output field:

```runs-prim
output position_x = new_x
output object = object with { state = spacewar:ship }
```

Every declared output field must be assigned exactly once along every execution path. The compiler verifies this statically. An output field that is not assigned on some path is a compile-time error — the Processor would produce undefined output for those inputs, violating purity.

Indexed output assignment is permitted for list outputs:

```runs-prim
output entities[i] = updated_entity
```

### `if` / `elif` / `else` Statement

Conditional execution:

```runs-prim
if health <= 0:
  output state = dead
elif health < 20:
  output state = critical
else:
  output state = alive
```

The condition must be `bool`. `elif` and `else` are optional. When output assignments appear inside conditional blocks, the compiler verifies that every output is assigned on all reachable paths (see `output` requirements above).

### `for` Statement

Bounded iteration over a finite collection:

```runs-prim
for entity in entities:
  if entity.state == spacewar:torpedo:
    let updated = spacewar:torpedo_update(entity)
    output entities[entity.index] = updated
```

The `for` statement iterates over a list value. The loop variable is bound to each element in order, from index 0 to length−1. The loop body executes exactly once per element. There is no `break`, `continue`, or early return.

**`range(n)` built-in**: For counted iteration, `range(n)` produces a list of integers from `0` to `n-1`:

```runs-prim
for step in range(18):
  # step takes values 0, 1, 2, ..., 17
```

The argument to `range` must be a non-negative integer known at compile time (a literal or a constant derived from the Processor's declared inputs). This is the mechanism by which the compiler proves termination: `range` always produces a finite list.

**No mutation during iteration**: The `for` body may read the collection being iterated but may not structurally modify it (add or remove elements). Modifications are expressed by producing an output collection:

```runs-prim
# Pattern: iterate input, produce modified output
for mobj in input_entities:
  if mobj.health <= 0:
    output remove_list = remove_list ++ [mobj.index]
  else:
    output output_entities[mobj.index] = doom:move_mobj(mobj)
```

The runtime applies structural changes (removals, insertions) after the Processor completes. This pattern matches the deferred-removal convention used by DOOM's thinker list, DOOM II's linedef crossing, and most real-time game engines.

**Accumulated state (`from` clause)**: When the loop body needs to carry state between iterations, a `from` clause declares accumulated variables with initial values:

```runs-prim
# Binary digit-by-digit square root: 18 iterations
for step in range(18) from result = 0, remainder = 0, num = value:
  let result = result << 1
  let t = (remainder << 2) | ((num >> 16) & 3)
  let num = (num << 2) & 262143
  let d = (result << 1) + 1
  let result = if t != 0 and d <= t then result + 1 else result
  let remainder = if t == 0 then remainder elif d <= t then t - d else t

output root = result
```

Semantics:

1. Before iteration 0, each accumulated name is bound to its initial value.
2. During each iteration, the accumulated names hold their values from the end of the previous iteration (or the initial values for the first iteration).
3. `let` bindings in the body may shadow the accumulated names. The final binding of each name at the end of the body becomes that name's value for the next iteration.
4. If a name is not shadowed in the body, it retains its start-of-iteration value.
5. After the loop completes, the final values of all accumulated names are available in the enclosing scope.

The `from` clause works with both `range(n)` and collection iteration:

```runs-prim
# Advance PRNG by 2×pcount steps
for step in range(pcount) from rng = prng:
  let rng = spacewar:random(rng)
  let rng = spacewar:random(rng)

output prng = rng
```

Totality is preserved: a `from` clause does not change the iteration bound. A `for ... from` over `range(n)` executes exactly `n` iterations, identical to writing `n` sequential `let` shadows manually. The `from` clause is syntactic sugar for the unrolled form — it adds no new expressive power.

A `for` body may use both `from` accumulators and `output` statements. They serve different purposes: `from` threads local computation state across iterations, while `output` writes to the Processor's declared outputs.

---

## Processor Structure

A complete Processor definition in the expression language:

```runs-prim
#! runs-prim 1.0

processor spacewar:gravity
  inputs:
    object:   spacewar:object
    config:   spacewar:game_config
    consts:   spacewar:game_constants
  outputs:
    gravity_x: spacewar:fixed18
    gravity_y: spacewar:fixed18
    object:    spacewar:object
  preconditions:
    object.state == spacewar:ship

  # Body: sequence of let-bindings, conditionals, and output statements
  if config.disable_gravity:
    output gravity_x = 0
    output gravity_y = 0
    output object = object
  else:
    let xn = object.position_x >> 11
    let yn = object.position_y >> 11
    let x_sq = xn * xn
    let y_sq = yn * yn
    let r_sq = x_sq + y_sq - consts.star_capture_radius

    if r_sq <= 0:
      let zeroed = object with { velocity_x = 0, velocity_y = 0 }
      if config.star_teleport:
        output gravity_x = 0
        output gravity_y = 0
        output object = zeroed with { position_x = 131071, position_y = 131071 }
      else:
        output gravity_x = 0
        output gravity_y = 0
        output object = zeroed with { state = spacewar:exploding, lifetime = -8 }
    else:
      let r_sq_full = r_sq + consts.star_capture_radius
      let sqrt_result = spacewar:sqrt(r_sq_full)
      let r_scaled = sqrt_result.root >> 9
      let product = spacewar:multiply(r_scaled, r_sq_full)
      let divisor = product.low >> 2
      let div = if config.heavy_star then divisor else divisor >> 2

      if div == 0:
        output gravity_x = 0
        output gravity_y = 0
        output object = object
      else:
        output gravity_x = (0 - object.position_x) / div
        output gravity_y = (0 - object.position_y) / div
        output object = object
```

### Version Declaration

The first line of every Processor body is a version declaration:

```
#! runs-prim 1.0
```

This declares which version of the expression language the body is written in. A runtime must support every version it claims compliance with. Version 1.0 is the "forever" version — it will never be removed from the specification.

### Inputs and Outputs

The `inputs` block declares the Processor's read-only parameters. The `outputs` block declares the values the Processor must produce. Both are typed, named fields.

An input may share a name with an output. This means the Processor receives a value and produces a (potentially modified) version of it. The input is never mutated — the output is a new value.

### Preconditions

The `preconditions` block declares conditions that must be true when the Processor is invoked. If a precondition is violated, the behavior is undefined by the expression language — the runtime may halt, log, or substitute a default value. The game logic's Network wiring is responsible for ensuring preconditions hold.

Common preconditions:
- `divisor != 0` — prevents division by zero
- `object.state == spacewar:ship` — ensures the Processor is only called for ships
- `value >= 0` — restricts input range (e.g., square root of negative numbers)

The compiler may insert precondition checks at call sites. It may also use preconditions for optimization — if `divisor != 0` is guaranteed, the compiled code can skip a zero check.

---

## Determinism

This section is normative. It defines the contract between the expression language and its compilers.

### The Strict Evaluation Rule

When a Processor body is present in the `.runs` source, the compiler MUST produce code that computes the **exact same output** as the reference evaluation of the body, given the same inputs. There is no latitude for approximation or substitution.

Formally: let `E(body, inputs)` be the result of evaluating the Processor body according to the rules in this specification. For any compiler `C` and any valid inputs `I`, the compiled code must satisfy:

```
C(body)(I) == E(body, I)
```

This is not approximate. It is bit-exact for all types except `float`.

### Permitted Optimizations

A compiler MAY:
- Inline sub-Processor calls
- Unroll `for` loops
- Reorder independent `let` bindings
- Eliminate dead code (unreachable branches, unused bindings)
- Replace an algorithm with a different algorithm **if and only if** the replacement produces identical output for every possible input within the declared type's range

A compiler MAY NOT:
- Substitute a platform-native function for a Processor body unless it can prove bit-exact equivalence for all valid inputs
- Reorder operations that have data dependencies
- Change the evaluation order of short-circuiting operators (`and`, `or`)

### Float Determinism

Operations on `float` values are computed using IEEE 754 binary64 arithmetic. The specification does not guarantee cross-platform bit-identical results for:
- Transcendental functions (`sin`, `cos`, `exp`, `log`, `sqrt` on float operands)
- Fused multiply-add optimizations
- Expression evaluation order where intermediate rounding differs

Games that require cross-platform determinism (demo playback, lockstep netcode, tournament verification) MUST use integer or fixed-point types. The choice of type IS the determinism contract.

### Adapted Compilation

A runtime MAY declare documented deviations from strict evaluation for specific Processors. Each deviation must be published in a machine-readable deviation manifest:

```yaml
deviations:
  - processor: spacewar:sqrt
    substitution: platform.native_sqrt
    justification: "Native sqrt is equivalent for non-negative inputs in the target range"
    impact: "Results may differ by ±1 LSB from strict evaluation"
```

A game compiled in adapted mode may produce different output from strict mode. The deviation manifest is the record of exactly where and why.

Adapted mode exists to serve constrained platforms (PICO-8, Game Boy, embedded systems) where strict evaluation of every Processor body would exceed hardware limits. It is never the default.

---

## Formal Grammar

The following grammar is in extended Backus-Naur form (EBNF). Terminals are in double quotes. Nonterminals are in lowercase. `{ ... }` means zero or more repetitions. `[ ... ]` means optional.

```ebnf
processor_file    = version_decl processor_decl ;

version_decl      = "#!" "runs-prim" version_number NEWLINE ;
version_number    = DIGIT+ "." DIGIT+ ;

processor_decl    = "processor" qualified_name NEWLINE
                    inputs_block
                    outputs_block
                    [ preconditions_block ]
                    body ;

inputs_block      = INDENT "inputs:" NEWLINE
                    { INDENT INDENT field_decl NEWLINE } ;

outputs_block     = INDENT "outputs:" NEWLINE
                    { INDENT INDENT field_decl NEWLINE } ;

preconditions_block = INDENT "preconditions:" NEWLINE
                      { INDENT INDENT expression NEWLINE } ;

field_decl        = identifier ":" type_expr ;

type_expr         = qualified_name [ "?" ] [ "[" [ integer_literal ] "]" ] ;

body              = { statement NEWLINE } ;

statement         = let_stmt | output_stmt | if_stmt | for_stmt ;

let_stmt          = "let" identifier "=" expression ;

output_stmt       = "output" output_target "=" expression ;
output_target     = field_path [ "[" expression "]" ] ;

if_stmt           = "if" expression ":" NEWLINE
                    INDENT body
                    { "elif" expression ":" NEWLINE INDENT body }
                    [ "else:" NEWLINE INDENT body ] ;

for_stmt          = "for" identifier "in" expression ":" NEWLINE
                    INDENT body ;

expression        = or_expr ;

or_expr           = and_expr { "or" and_expr } ;
and_expr          = bitor_expr { "and" bitor_expr } ;
bitor_expr        = bitxor_expr { "|" bitxor_expr } ;
bitxor_expr       = bitand_expr { "^" bitand_expr } ;
bitand_expr       = equality_expr { "&" equality_expr } ;
equality_expr     = relational_expr [ ( "==" | "!=" ) relational_expr ] ;
relational_expr   = shift_expr [ ( "<" | ">" | "<=" | ">=" ) shift_expr ] ;
shift_expr        = additive_expr { ( "<<" | ">>" | ">>>" ) additive_expr } ;
additive_expr     = multiplicative_expr { ( "+" | "-" ) multiplicative_expr } ;
multiplicative_expr = unary_expr { ( "*" | "/" | "%" ) unary_expr } ;

unary_expr        = [ "-" | "not" | "~" ] postfix_expr ;

postfix_expr      = primary_expr { "." identifier | "[" expression "]" | "(" [ arg_list ] ")" } ;

arg_list          = expression { "," expression } ;

primary_expr      = identifier
                  | qualified_name
                  | integer_literal
                  | float_literal
                  | fixed_literal
                  | bool_literal
                  | "none"
                  | list_literal
                  | "(" expression ")"
                  | "if" expression "then" expression "else" expression
                  | record_update
                  | range_expr ;

list_literal      = "[" [ expression { "," expression } ] "]" ;

record_update     = expression "with" "{" field_assign { "," field_assign } "}" ;
field_assign      = identifier "=" expression ;

range_expr        = "range" "(" expression ")" ;

field_path        = identifier { "." identifier } ;
qualified_name    = [ identifier ":" ] identifier ;

integer_literal   = DECIMAL_DIGITS
                  | "0x" HEX_DIGITS
                  | "0o" OCTAL_DIGITS
                  | "0b" BINARY_DIGITS ;

float_literal     = DECIMAL_DIGITS "." DECIMAL_DIGITS [ ( "e" | "E" ) [ "+" | "-" ] DECIMAL_DIGITS ] ;

fixed_literal     = DECIMAL_DIGITS "." DECIMAL_DIGITS "fx" ;

bool_literal      = "true" | "false" ;
```

---

## Deliberate Exclusions

The language does not and will never express:

| Excluded Feature | Rationale |
|------------------|-----------|
| Unbounded loops (`while`, `loop`) | Violates totality. All iteration must be over finite collections. |
| General recursion | Violates totality. The call graph must be a DAG. |
| I/O of any kind | Rendering, sound, file access, and networking are the runtime's job. |
| Memory allocation | No `new`, no pointers, no manual memory management. |
| Global mutable state | All state flows through declared inputs and outputs. |
| Platform-specific intrinsics | No OS calls, no hardware-specific operations. |
| String manipulation | The language is not a text processing tool. |
| Dynamic dispatch | All calls are statically resolved. Networks handle dispatch. |
| Exceptions or panics | No `throw`, no `catch`. Error handling is via preconditions and total functions. |

---

## Versioning

### The `#!` Declaration

Every Processor body begins with a version declaration:

```
#! runs-prim 1.0
```

The version number is `major.minor`. A runtime claiming support for version `X.Y` must also support all versions `X.Z` where `Z < Y`, and all versions `W.0` where `W < X`.

### Evolution Rules

1. **Additive only** — Future versions may add new constructs (operators, statement types, type features). They may never remove or change the semantics of existing constructs.
2. **Version 1.0 is forever** — A program valid under version 1.0 will be valid under every future version. Its meaning will never change.
3. **Major version for breaking changes** — If a breaking change is ever unavoidable (the specification makes no promise this will happen), it requires a major version increment. A runtime supporting version 2.0 need not support version 1.0 — but version 1.0 source files remain readable and archivable as historical artifacts.
4. **No feature flags** — The version number is the only mechanism for feature gating. There are no compiler flags, pragmas, or conditional compilation directives.

---

## Reference Implementation Bootstrap

The minimum viable tooling for the first runtime consists of:

### 1. Reference Grammar File

The EBNF grammar in this document, published as a machine-readable PEG (Parsing Expression Grammar) file. This file is the canonical definition of the syntax — if the EBNF and the PEG disagree, the PEG governs.

### 2. Reference Parser

A single-file parser that reads `.runs-prim` source text and emits an abstract syntax tree (AST) as JSON. No dependencies beyond the standard library of the implementation language.

Estimated size: 500–800 lines.

The AST format is not specified here — it is an implementation detail of the reference tooling. Any format that faithfully represents the parse tree is acceptable.

### 3. Reference Evaluator

A tree-walking interpreter that evaluates a Processor's AST against a given set of input values and produces the output values. This evaluator is the **oracle**: any optimizing compiler's output must match the evaluator's output for all valid inputs.

Estimated size: 800–1200 lines.

### 4. Test Vectors

For each Processor in the first RUNS game (Spacewar! 3.1), a set of input/output pairs verified against PDP-1 emulator behavior:

| Processor | Example Vector |
|-----------|---------------|
| `spacewar:sqrt` | `sqrt(2048) → root = 23168` (binary point at bit 9) |
| `spacewar:sin` | `sin(0) → 0`, `sin(0o62210) → 0o377777` |
| `spacewar:random` | `random(0) → (known value from rotate-XOR-add sequence)` |
| `spacewar:multiply` | `multiply(32, 32) → high = 0, low = 1024` |

These test vectors are the "first chip" — the hardware verification vectors defined before the first silicon.

---

## Relationship to Other EGS Components

```
  MAPS Notation          RUNS Source Files           Compiled Game
  (design blueprint)     (enduring artifact)         (platform binary)

  States  ─────────────→ Records (.runs)
  Verbs   ─────────────→ Processors (.runs-prim)  ──→ native functions   ← DIGS governs this
  Arcs    ─────────────→ Networks (.runs)          ──→ compiled call graph
  Marks   ─────────────→ Annotations               ──→ metadata tables
```

Records are declared in `.runs` files using a separate schema syntax (not defined in this specification). Networks are declared in `.runs` files using a separate wiring syntax. DIGS defines ONLY the body of a Processor — the computation that transforms inputs into outputs.

---

*MIT License — Open for implementation, extension, critique.*
