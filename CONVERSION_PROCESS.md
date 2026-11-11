# How to convert a program to RUNS

This guide converts an existing program on any machine to RUNS. Its worked example is `RUNS-Spacewar`, which converts Spacewar! 3.1 on the PDP-1. Each rule is stated for any machine first, then shown on Spacewar.

A **conversion** is not a re-vibe or a rewrite. It reorganizes the **original** program, from its source, from code lifted from it, or from its machine code, into RUNS. Every sequence of inputs from power-on gives the same game, glitches included. The game does not change to fit RUNS. Where RUNS cannot say what the game does, RUNS grows, and that growth is a change to this spec. Every decision about the language that a conversion makes lands in this spec in the same step, with an example the conversion's tools run. A decision the spec does not state leaves the spec stale.

At every step, the RUNS text plus the original machine's declarations rebuilds the original binary. The binary checks the behavior. Purity is the structure, and the structure is what the conversion changes.

Two rules this guide holds a conversion to are conventions, not RUNS compliance. The split of a game into a Rules region and a Realization region is the enduring-games pattern, not a base-protocol primitive ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 131-135, 158-160). Decomposing a routine into Processors is convention too: a monolith that passes every test vector is the game ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 117-129). A conversion that follows this guide chooses both, and its tools enforce them as its own rules.

Three documents hold what this guide points to:

- [MACHINE_DESCRIPTION.md](./MACHINE_DESCRIPTION.md) defines the **machine description**, the `<machine>.runs-machine` file that states the original machine's types, literals, operators, and address spaces, and the `layout` declaration that states a layout play reads.
- [DECLARATIONS.md](./DECLARATIONS.md) defines a machine's **declarations**, the half of its package that never runs, which records where that machine keeps each value and how it calls each routine. It also states where a change goes, the host contract, and the mutation gate.
- [NETWORK_TOPOLOGY.md](./NETWORK_TOPOLOGY.md) and [DIGS_EXPRESSION_LANGUAGE.md](./DIGS_EXPRESSION_LANGUAGE.md) define the RUNS text itself.

## Before you start

You need:

- **The original image.** The exact binary the original machine loads (a tape, a ROM, a disk image, an executable), with its hash. Each version of a game is its own game. A conversion picks one image and reproduces that image. Spacewar's image is `build/oracle.rim`, assembled from `source/spacewar3.1_complete.txt`.
- **The original program, as source or as machine code.** Code with no source is converted from its machine code, through a disassembly. Spacewar has its source, and RUNS-Spacewar also lifted it to C, in `lift/`.
- **A symbol table or a disassembly with names.** It names every address the conversion maps. Spacewar's is the assembler listing, `build/oracle.lst`.
- **The original running in an emulator you can script and whose state you can read and write.** The running original is the authority. Reading the source is not. Spacewar uses SIMH's PDP-1 simulator, built into `build/pdp1` by `tools/build-simh.sh`.
- **An evaluator.** It reads the machine description and the RUNS text, runs `runs.check` before anything runs, and runs a Network over Records. RUNS-Spacewar's is `tools/runs.py`.
- **The machine description**, if the machine already has one. A machine description is game-neutral, so every game on that machine shares it. [1. Describe the machine](#1-describe-the-machine) writes one when none exists.

## The toolkit

A conversion builds or reuses the tools below. Each has a contract: what it takes, what it gives, and what it checks about itself. A tool that does not check itself is not evidence. Each entry names RUNS-Spacewar's file for it.

### The emulator harness

The **emulator harness** runs the original under script control.

- **Takes.** The original image. A starting state, as words to deposit in memory and values for registers. One or more stop addresses. Scripted input, as values for each device at each stop.
- **Gives.** Every word of memory and every register, status flags included, at each stop, and why the run stopped (a stop address, an interrupt taken, a halt, an instruction limit). On request, a trace of every instruction run, with its effective address, for the reach oracle.
- **Checks about itself.** A deposit followed by a read gives back the word deposited, at every address the conversion uses. Two runs from the same state with the same input stop at the same places with the same state, so the emulator is deterministic under the harness. It runs the unmodified image from its start address to a known stop.
- **Spacewar.** SIMH, in `build/pdp1`, running `build/oracle.rim`. The checks drive it through `tools/pdp1cc/gate/simh.py`. The scripted matches, each with a start address, sense switch settings, a seed, and a control policy, are in `tools/check-main-loop-frames.py`.

### The state map

The **state map** maps each Record field to the place in the original that holds it.

- **Takes.** The RUNS Records, the places in the declarations, and the symbol table or the disassembly.
- **Gives.** For each field and each slot of a collection, its address or register in the original. For each value, how it is spelled as the machine's bits (an enum member, an address). A function from a set of Records to the deposits that put them in the emulator, and a function from the emulator's memory back to Records.
- **Checks about itself.** Every address comes from the symbol table or the disassembly, never from a hard-coded number. Every field the RUNS text declares is mapped. Two fields share one place only where the declarations say they share it. Depositing a set of Records and reading them back gives the same Records.
- **Spacewar.** `tools/pdp1.py`. Its `FIELDS` table names each field by its source symbol, and its `Binding` class reads the declarations and gives addresses, spellings, deposits, and reads. The addresses come from the listing through `oracle_symbols` in `tools/oracle_check.py`.

### The evaluator

The **evaluator** runs the RUNS text.

- **Takes.** The machine description, the RUNS text, a set of Records, and the name of a top Network to fire.
- **Gives.** The Records after the firing, the contents of each stream, and how the firing ended: it returned, it reached `wait`, it reached `stop`, or the RUNS text is wrong (a loop past its bound, a failed `requires:`, `unreachable`, a read of an unknown value). It is one host, as [The host](./DECLARATIONS.md#the-host) defines.
- **Checks about itself.** It runs `runs.check` before anything runs, and refuses every text that check refuses. Its operators are the machine description's operator bodies, and [1. Describe the machine](#1-describe-the-machine) checks each body against the emulator.
- **Spacewar.** `tools/runs.py`. It holds the PDP-1 description's operators in code. `tools/check_examples.py` in this repository runs every `runs` example of these documents through it.

### The reach oracle

The **reach oracle** finds where play depends on the machine instead of on the rules.

- **Takes.** The emulator harness with its instruction trace, the state map, the symbol table, and scripted play: real matches from power-on, with every start address, every switch setting, and input that drives the game into its edge states.
- **Gives.** A report of every site where play reaches the machine, by kind (see [6. Measure where play reaches the machine](#6-measure-where-play-reaches-the-machine)). Each data access is named by the Record field or the source label it lands in. Each site gives its address, its source line, and the places it touched with their counts.
- **Checks about itself.** It keeps its own copy of memory as the program writes it, and compares that copy with the emulator's at the end of every scenario. It models the result of each arithmetic, logic, shift, and rotate instruction from the machine description, and compares the result with the register the emulator shows after the instruction. A difference in either check fails the run.
- **Spacewar.** `tools/reach_oracle.py`. It runs the scripted matches of `tools/check-main-loop-frames.py` in SIMH with CPU history on. Its report is `docs/reach-oracle.txt`. The report's first line states the scenarios, the instructions run, and the words where its copy of core differs from SIMH's.

### The comparison checks

The **comparison checks** compare the evaluator with the emulator.

- **Takes.** A routine or a Network of the RUNS text, the matching entry and exit addresses in the original, a generator of Record states, the state map, the emulator harness, and the evaluator.
- **Gives.** For each state, whether every field of every Record the routine touches, every output point, every stream entry in order, and the way the run ended are the same on both sides. A count of matches and differences, and the first difference in full.
- **Checks about itself.** It can fail. A defect planted in the RUNS text (an off-by-one, a dropped random draw, a swapped operator) makes it report a difference. A field the evaluator holds as unknown, where the emulator holds a value, counts as a difference. A run that ends early on one side counts as a difference.
- **Spacewar.** One check per routine, such as `tools/check_square_root.py`, `tools/check_multiply.py`, `tools/check_divide.py`, and `tools/check_sincos.py`. `tools/check_calc_routines.py` checks the calc routines. `tools/check_frame.py` checks a whole frame, and its `alone` mode checks the game with the presentation removed. `tools/check_game.py` checks the start Networks, scoring, and the halt between games. `tools/mutate.sh` runs a check on a copy of `runs/` with one edit, to show that the check sees it.

### The purity report

The **purity report** lists every place the RUNS text is not pure.

- **Takes.** The RUNS text, and optionally an earlier revision to compare with.
- **Gives.** One line per impurity, then the count. Against an earlier revision, a failure for every line the earlier revision did not have, except a line that a Record newly given a kind reveals.
- **Checks about itself.** It applies the loader's own kind and purity rules, so it cannot disagree with the loader. When the count is 0, the loader refuses every impurity on its own.
- **Spacewar.** `tools/check_purity.py`, with `--against REF`.

### The compiler and the declarations for the original machine

The **compiler** turns the RUNS text plus a machine's declarations into an image for one target machine. With the original machine's declarations, it gives the original image.

- **Takes.** The RUNS text, the machine description, the declarations, and the machine's own toolchain, if the route uses one.
- **Gives.** An image, and whether its hash is the original's.
- **Checks about itself.** It compiles only RUNS that `runs.check` accepts. It refuses what [DECLARATIONS.md](./DECLARATIONS.md) lists under its compiler checks.
- **Spacewar.** `tools/runsc.py`, with the declarations in `pdp1/`. It prints `MATCH` when the image's hash is the original's.

### The mutation gate

The **mutation gate** checks that the RUNS text, not the declarations, decides the image. [The mutation gate](./DECLARATIONS.md#the-mutation-gate) specifies it.

- **Takes.** The RUNS text, the declarations, the compiler, and the evaluator.
- **Gives.** For each mutant, its class: it changes the image, it is refused, or it is shown to be the same game. A failure for every mutant that is none of these, and for every declaration whose deletion changes nothing.
- **Checks about itself.** It builds the unmutated image first, and that image must match the original. A silent mutant passes only when enough of its firings run clean through the mutated routine.
- **Spacewar.** `tools/check_compiled.py`.

### One script that runs every check

The conversion has one script that runs every check above in order and fails on the first failure.

- **Takes.** Nothing but the repository.
- **Gives.** One line per check, and a nonzero exit on the first failure.
- **Spacewar.** `tools/check_all.sh` runs the compile, the mutation gate on a sample of 8000 mutants, the comparison checks, and this spec's examples against the conversion's evaluator (`tools/check_examples.py`). The full gate, the reach oracle, the purity report, and `tools/mutate.sh` run by hand.

## Move in small steps that each compile

A conversion moves in small steps. Each step rebuilds the original binary from the RUNS text and the declarations, and passes the checks in [8. Compile with the declarations](#8-compile-with-the-declarations), before the next step begins.

The conversion's progress is the purity report. Nothing is exempt. A flag, a marker, or an exception that hides an impurity from the report is not allowed. The loader refuses every impurity, a Record with no kind included. Only the purity report reads a text that is not yet pure, so a finished conversion is checked with no switch to remove.

When a pure shape does not compile to the original binary, the RUNS text changes first. Purity stays as it is. Look for the change in this order, as [Where a change goes](./DECLARATIONS.md#where-a-change-goes) states:

1. The RUNS text. Hard text means its shape is wrong. Sketch at least two pure shapes for the rule and compile each.
2. The compiler. It belongs to the target machine, and every game for that machine shares it. Change it only by a general rule, for an idiom that a second program for that machine uses.
3. Neither works. Stop, and report the shapes tried and the evidence.

The declarations are never the place to make hard text compile. Their count of entries only shrinks, as [The declarations only shrink](./DECLARATIONS.md#the-declarations-only-shrink) states.

A step is one routine, one Record, or one change of shape. A step that moves several routines at once hides which change broke a check.

When one change of shape sweeps every unit of the text, such as splitting each Processor as far as it goes, take the riskiest unit first and finish it end to end before the rest. The risk is the compiler's: count the values each split hands from one piece to the next through a field where the original kept them in a register, the control flow inside the routines, and the routines the declarations name. The unit with the most of these, and a comparison check strong enough to catch a wrong binary, goes first. Pieces it shares with other units get one file in that unit, and the other units' routines point to that file during the sweep.

**Done when** the five conditions of [8. Compile with the declarations](#8-compile-with-the-declarations) pass after every step.

## 1. Describe the machine

The machine description states everything RUNS takes from the original machine. Every type a RUNS text uses that is not a count, a condition, or an enum comes from it. [MACHINE_DESCRIPTION.md](./MACHINE_DESCRIPTION.md) defines its form. This step writes it and checks it.

1. **Find the types play computes with.** List every width of value the original's arithmetic and logic run on. An 18-bit word machine has one type. An 8-bit microprocessor has a byte and a 16-bit address. A machine with a floating point unit has a type for each format it computes in. Spacewar computes with one type, the PDP-1's 18-bit ones' complement `word`.
2. **List the operators play uses.** Read each routine of the original, and write down each operation it performs on a value of a machine type: each add, subtract, compare, shift, rotate, multiply step, and logic operation, and each operation that leaves a status bit a later instruction reads. Spacewar uses add and subtract with end-around carry, the shifts `sal` and `sar`, the rotates `ral` and `rar`, the pair rotates and shifts `rcl`, `rcr`, `scl`, and `scr`, the multiply and divide steps `mus` and `dis`, a count of set bits, and the comparisons.
3. **Write each operator's body** in the description's core, as [MACHINE_DESCRIPTION.md](./MACHINE_DESCRIPTION.md) defines it. A status bit that an instruction leaves (a carry, an overflow, a zero flag) is a result of the operator, returned with the value. It is not part of the type. The RUNS text stores it in a field of the Record of the concern it belongs to.
4. **State the literals.** Write down the bases the original's numbers are written in. Spacewar's source writes octal with a leading 0, and decimal otherwise.
5. **State an address space** for each memory whose layout some game's play on the machine reads. [6. Measure where play reaches the machine](#6-measure-where-play-reaches-the-machine) finds whether this game's does. Spacewar's play reads no layout, so its text has no `layout`. The PDP-1 description states `core` for other PDP-1 games.
6. **Leave out what is not the machine's arithmetic.** Instruction encodings belong to the target's compiler, not to the description (see [A Record holds no code](./DIGS_EXPRESSION_LANGUAGE.md#a-record-holds-no-code)). Events and devices belong to the declarations.
7. **Check each operator against the emulator.** For each operator, deposit its inputs in the emulator, run the one instruction (or the short sequence) that performs it, and read the registers and flags it leaves. Compare them with the operator's body in the evaluator. Check every input when the inputs fit in an exhaustive run. An 8-bit add with carry has 2^17 inputs, so check them all. Otherwise check the type's [edge words](./MACHINE_DESCRIPTION.md#edge-words), each power of two and its negation, and a seeded random sample. Spacewar's reach oracle models every add, subtract, shift, and rotate it runs and compares each with the AC SIMH shows after the instruction.

A conversion on a machine that already has a description uses it. It adds an operator only when play reaches an operation the description lacks, and it checks that operator the same way. Every game on the machine shares the description, so a change to an existing operator's body is a change for every game, and every game's checks run again.

**Done when** every operator the RUNS text uses has a body in the description, every body matches the emulator on every input or on the edge words and a seeded sample, and the evaluator loads the description with no error.

## 2. Find every Record

A Record field is any value of the original that carries meaning from one routine to another or from one frame to the next. On most machines such a value lives in a memory word. It can also live in a register, a status flag, a device register the program reads back, an instruction's operand, or a stack slot.

1. Name each field for what it means, not for its symbol. Put the original symbol in a comment, as in `particles: word = 0  # mxc`.
2. Make a value that a routine sets before it reads it, and never hands on, a local of the Processor instead. Make a value that the routines of one Network hand between them, set before it is read in every firing and touched by nothing outside that Network, the Network's scratch (`owns`), as the original kept such a value in one register. Anything read outside the Network is a field.
3. Keep a value that the game counts and never reads, such as Spacewar's `objects_seen`. It becomes a field that no Processor reads, and the graph shows it is dead.
4. Drop values that only the machine uses and play never observes, such as a cursor kept in an instruction's address field, a return address on a call stack, or a saved register an interrupt handler restores. They belong to the declarations.
5. Keep global data in Records like any other state. Data in the image, such as Spacewar's star catalog and ship outlines, is a Record whose field takes one initial value a slot.
6. Give a field no initial value if its value comes from outside the game: memory the image does not load and the game reads before it writes, a device register, a clock. Spacewar's scores start from whatever core held at power-on, so `score` has no initial value.
7. Keep one field for one value, even when the original reads it under two meanings. Spacewar's divide keeps the dividend's high half and then the remainder in one word, and the conversion keeps one field.
8. Make a status flag that one routine leaves and another reads a field, of the Record of the concern it belongs to. A 6502 routine that returns with the carry set to say "not found" leaves a value the caller reads. The carry becomes a field of the search's Record, and the operator that sets it returns it (see [Status flags and registers](./MACHINE_DESCRIPTION.md#status-flags-and-registers)).
9. Make a value held in a field of several words, or packed several to a word, one field per value. Where play reads the packing (a bit field that overflows into its neighbor), the type or the stated layout states the packing.

A routine word that names which code runs an object is a state. Make it an enum. In Spacewar, the calc routine word becomes `enum calc_routine`, and the sign bit that marks whether an object collides is a function of that enum. A program flag that a routine sets and tests is an enum too, as a field when it carries from one firing to the next and as a local when the routine clears it before it reads it. A pointer that the game only compares and follows to one of a few known places is an enum too. The declarations spell each member as the address.

**Done when** every place the reach oracle names as a data access lands in a field, a local, or a choice the declarations hold, and the state map maps every field, and a deposit and read of every Record through the state map gives the same Records.

## 3. Map each routine to Processors and Networks

The original passes values between routines in registers, in flags, on a stack, and in shared memory. RUNS passes every value through a Record field that a Network names. A Processor names no Record: it declares its inputs and outputs, its whole contract, and the Network that runs it wires each one to one field. Records and Processors know nothing of each other, and the Network is the only thing that knows both sides ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 166-169). Only a top Network names Records. Every other Network is a bundle with inputs and outputs of its own, which it wires on to the routines it runs. [Network topology](./NETWORK_TOPOLOGY.md#inputs-and-outputs) states the syntax.

A conversion may start from an older form, which the loader still reads: Processors that name the Records they touch under `reads:` and `writes:`, and Networks that pass a slot with `run name(slot)`. Convert each to inputs, outputs, and wires, one interaction at a time. `slot` stays only in the Network that walks the slots. A bundle gets `objects.x[slot]` already chosen, as the original's pointers gave each routine "this object's x". A slot the game computes, such as the free slot a new torpedo takes, lives in a Record, and the walking Network wires the whole field beside it, to an input or output of kind `word[N]`.

Organize Records by meaning, not by where the original kept a value. A value the original carried in a register from one routine to the next becomes a field of the Record of the concern it belongs to, named for what it means. A comment names the register and the instruction. Do not collect register carries into one Record named for the register. Spacewar's `handoff` Record does, so it is impure by this rule, and its conversion splits it.

Map each way the original shares a rule. The first column is the idiom on any machine. The third column is the Spacewar (PDP-1) instance. An empty third column names no Spacewar instance.

| In the original | In RUNS | In Spacewar |
|-----------------|---------|-------------|
| A subroutine that takes and returns values in registers | A Processor whose inputs and outputs are the routine's own values. The Network wires them to the fields of one Record, sets the parameter fields before the run, and reads the result fields after it. | `jda sqt`, which takes AC into `square_root_call.entry`. |
| A subroutine that calls another | A Network. A Processor sets the callee's parameter fields, the callee runs with its inputs and outputs wired to its fields, and a Processor reads the callee's results. | `imp` calls `mpy`. |
| A parameter placed after the call, which the callee reads through its return address | A field the caller sets before the run, if no caller names a value the callee writes. | `jda mpy / lac b`, where the callee executes the word after the call each time it reads it. That held for every call in Spacewar. |
| Two entries into one body | A Network that runs the first Processor, then the shared routine. The declarations lay out the jump past the entry. | `idv` shifts its dividend, then jumps into `dvd`. |
| A macro with arguments | A Processor or a Network with inputs and outputs, wired at each use to the fields its arguments name. Each distinct wiring is one copy, as each expansion was one. A constant argument is a slot of a Record of constants. | `dislis J, Q, B`. `diff \mdx, mx1, (sar 3s`. |
| A macro with no arguments | A Processor. A macro that works on one axis at a time is one Processor with inputs and outputs, wired once an axis. | `random`. `diff`, as `inertia` wired to each axis's velocity and position. |
| A computed jump into unrolled code, past as many copies as a number says | A counted `for` from a local. The compiler lays it out as the jump. | |
| A store into part of a word, such as an instruction's address field | A `set` that keeps the rest of the word. | `dap`, as in `set f = f & 0770000 \| 020`. |
| A return that reports its outcome by where it returns, or by a status flag | An enum field whose members are the outcomes. The declarations say which member skips, branches, or sets which flag. | `dvd` returns one word further when the quotient fits. |
| Status flags that a later routine branches on | The operator that sets them returns them. The RUNS text stores each in a field of the Record of the concern it belongs to, and a guard tests the field. | |
| A conditional skip or branch | A Network guard that tests what the skip or branch tests. | `sma`, `sza`, `spa`. |
| A tunable executed in place | A Processor of its own. What it takes from and leaves in the registers are its inputs and outputs, wired to fields of the Records of the concerns they belong to. | `xct the`, the space warpage. |
| A loop that runs a macro or a tunable | Today, a Network `loop at most N:` that fires the Processor and exits on a guard. See **Loops** below. | |
| A routine that runs macros or tunables | A Network of the Processors. Today's text fires them in the original's order (see [4. Keep the order](#4-keep-the-order)). | |
| A label that several places jump to | A Network of its own. Each jump is a `run` of it as the last thing a branch does. | |
| The main loop | A top Network. Today's text states it in the original's order (see [4. Keep the order](#4-keep-the-order)). The host fires it on the frame event the declarations name. | `network frame`, from `ml0`. |
| A vertical-blank wait, or a busy-wait on a hardware register that paces the frame | Nothing in the game. The frame event the declarations name fires the top Network. Where the wait's count reaches game state, the count is a value that comes in. | The spare-time loop burns the rest of the frame's instruction budget. Nothing in the game reads the budget after, so `spare_time` is presentation. |
| A start address, a reset vector, or a power-on entry | A top Network that the host fires once, on the event the declarations name for that entry. | `start_with_test_word` at 5 and `start_with_control_boxes` at 4. |
| An interrupt handler | A top Network that the host fires on that event. Where the handler lands mid-routine and play observes it, that is timing (see below). | The PDP-1 sequence break words at 0 to 3 are machine words in the declarations. Play raises no sequence break, so no top Network handles one. |
| A main loop that waits for a flag the interrupt handler sets, then runs the frame | A top Network of its own, from the instruction after the wait to the wait. The event the declarations name fires the handler's Network, then this one. The flag belongs to the declarations when no rule reads it. | |
| An idle loop that only waits for interrupts | The end of the start Network. The host fires the handler's Network on each event. | |
| Registers an interrupt handler saves and restores | Nothing in the RUNS text. The interrupt convention in the declarations saves and restores them. | |
| A jump through a word that names a routine | A `match` on the enum. | `match objects.routine[slot]`, the calc routine. |
| A jump table indexed by a number | An `if` chain over the values that ends in `else`, or a `match` when the number is an enum. See **Guards** below. | |
| A halt that the operator continues past, or a wait for a key | An `emit` of what the halt shows, then `wait`. | The halt between games shows the scores. |
| A halt that halts again when continued, or a hang | `stop`. | A ship fires when the object table is full. |
| Code the program writes, then runs (self-modifying code) | Processors that state what the code computes. The compiler reproduces the code's words. A Record of `insn` values run with `jump` is impure. | The outline compiler writes each ship's outline as instructions. |
| A word the routine rewrites, then copies into the code | A field that holds what the word means. The compiler reproduces the instruction around it. | |
| An instruction built at run time and executed | The rule it computes. | The explosion builds a shift from a random number, and the conversion writes a shift by `popcount` places. |
| A value carried in a register between two rules | A field the Network names, of the Record of the concern it belongs to, named for what it means. When only one Network touches it, and every firing sets it before reading it, it is that Network's scratch. | The space warpage's AC, as in the example below. |
| A bank switch | Layout. The declarations place each routine and Record in its bank, and the compiler emits the switch. Where play reads through a bank the game did not mean to map, the stated layout places those Records. | |
| A DMA transfer to a device | Presentation. The Records it copies are interface Records or a stream, and the device the declarations name carries them out. Where play observes the transfer's timing, that is timing. | |
| A DMA transfer from memory to memory | A Processor that states the copy. | |
| A stack used for calls | The return addresses belong to the conventions in the declarations. A value pushed to pass to a callee is a field of the callee's Record. | |
| Recursion | Today, a stack Record (a collection with a depth field) and a bounded Network loop that pushes and pops it. See **Loops** below. A stack that overflows into other data is layout. | |
| A heap allocator | The game's own allocator, converted like any routine, over a Record that holds the pool. A stale reference does what the stated layout says. | |
| A memory-mapped device read | A field with no initial value in an interface Record that comes in. The devices in the declarations say which register carries it. | `console.test_word`, read by `lat`. |
| A memory-mapped device write | An interface Record or a stream that the presentation writes. The devices in the declarations say which register carries it. | `lights`, program flags 1 and 2. The `display` stream. |
| A fixed-point multiply or divide routine | The routine, converted step by step with the machine description's operators. | `mpy` and `dvd`, from `mus` and `dis` steps. |
| A floating-point library call | The library is code of the program, so it is converted like any routine. A hardware floating-point instruction is an operator of the machine description. | |

Rules that cover more than one row:

- **Interrupts.** An interrupt handler is a top Network that the host fires on that event. [The host](./DECLARATIONS.md#the-host) fires it between two firings of other top Networks. Where the interrupt lands inside a routine and play observes where it landed, the landing point is timing, the fourth way the game touches the machine (see [Three kinds of Record](./README.md#three-kinds-of-record)). It becomes a rule the RUNS text states, or a value that comes in.
- **Guards.** In the vision, the guards of one branch form a complete partition: exactly one is true. A discriminant that is not an enum needs an explicit `else` arc. A guard reads a fact a Processor computed into a Record, and never computes one ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 351-358). Today's Network grammar makes `else` optional ([Grammar](./NETWORK_TOPOLOGY.md#grammar)), and `tools/runs.py` does not check that guards partition.
- **Loops.** In the vision, one tick of the Rules region is a DAG. The only unbounded loop is the tick feedback through `state:` Records, in the wiring. A Dispatch is a bounded fold whose count is fixed before the loop, with no `break`, `continue`, or early return ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 204-206, 344-347). Today's Network loops exit early on a guard. How a conversion expresses a loop whose exit depends on data is open.
- **Recursion.** Today, a recursive routine becomes a stack Record and a bounded Network loop. The bound is the deepest the original's stack can go before it overflows. A stack that overflows is layout, and the stated layout says what the overflow reads and writes.
- **Allocation.** The game's own allocator is converted. RUNS has no allocator of its own. A stale reference does what the stated layout says.
- **Versions.** Each version of a game is its own game, with its own RUNS text. Two versions share Processors only by copying them.
- **Code with no source.** It is converted from its machine code, through a disassembly. Each routine's symbol names come from the disassembly.

Here is a torpedo's flight from Spacewar, reduced to the x axis. The original executes the tunable `the` with `xct` and passes values through AC. The values belong to the space warpage, so they are fields of `warpage`. RUNS-Spacewar's text keeps them in `handoff`.

```runs
interface record objects[2]
  x: word = 0               # nx1: position
  dx: word = 0              # ndx: velocity

game record warpage
  coordinate: word = 0      # AC into `the`: a torpedo's coordinate, sar 9s
  acceleration: word = 0    # AC into diff: from `the`, or 0 (cla)

network torpedo_flight
  for slot in 0 .. 1:
    run warp_from                                           # tc1
      position: objects.x[slot]
      coordinate: warpage.coordinate
    run torpedo_space_warpage
      coordinate: warpage.coordinate
      acceleration: warpage.acceleration
    run inertia                                             # diff \mdx, mx1, (sar 3s
      acceleration: warpage.acceleration
      velocity: objects.dx[slot]
      position: objects.x[slot]
```

```runs-prim
processor warp_from                                         # lac i mx1; sar 9s
  in position: word
  out coordinate: word
  set coordinate = position >> 9

processor torpedo_space_warpage                             # the
  in coordinate: word
  out acceleration: word
  set acceleration = coordinate >> 9

processor inertia                                           # diff
  in acceleration: word
  inout velocity: word
  inout position: word
  set velocity = acceleration + velocity
  set position = (velocity >> 3) + position
```

The example shows today's text form. `inout` updates a field in place, where the vision writes each value once and a change is a fresh value in a fresh place ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 90-92).

`inertia` names no axis. The y axis is the same Processor, wired to `objects.dy[slot]` and `objects.y[slot]`, as the original expanded `diff` once an axis.

An operator can still patch `torpedo_space_warpage`, the rule and not only the number, as the original's authors could patch `the`.

On a machine with status flags, the same rule moves each flag into a Record. [Status flags and registers](./MACHINE_DESCRIPTION.md#status-flags-and-registers) shows the shape, a carry that one routine leaves and the next reads.

Today's text is structured code, and it cannot enter a loop in two places. If the original does, state the loop once and repeat the statement that the second entry skips. Spacewar's sine enters its reduction loop in two places, so the RUNS states the reduction step before the loop and again at the end of its body. The declarations lay the two out as one.

**Done when** every routine of the original is a Processor or a Network of the RUNS text, every value it passes goes through a field a Network names, `runs.check` accepts the text, and the step's compile passes.

## 4. Keep the order

The order in which the original runs its rules is part of the game. In the vision, a Network is a colored Petri net, and execution order is derived from its wiring, never authored. Each Record is written once, a shared resource is a threaded chain of distinct values, and any topological order of one tick gives the same results ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 90-92, 188-199).

Today's RUNS text falls short of that. Its Records are updated in place, and two Processors can write the same Record. In Spacewar, `collision` and each object's calc routine both write the object table, so their reads and writes give no order between them. The text states the order instead: firing is sequential, in the order of the Network's lines, and each Processor sees every write before it. How a conversion turns such a shared Record into a threaded chain is open. Until then:

- Fire Processors in the order the original runs them, even when the order looks like an accident.
- Do not split a loop into phases. In Spacewar, object *i* is tested against every later colliding object and then moves, before object *i+1* is touched. [Where the order comes from](./README.md#where-the-order-comes-from) says what a split changes.
- Keep dead tests and odd ranges. Spacewar's explosion tests a size that can never pass, and its last object slot is never tested for collisions. Both stay.
- Keep the order of events. Where the original handles two events in a fixed order (a reset before a frame, an interrupt before the main loop resumes), the host fires their top Networks in that order, as [The host](./DECLARATIONS.md#the-host) states.

**Done when** the comparison checks of each routine and Network the step touched match the emulator, including the per-frame check.

## 5. Give each Record a kind, and split each Processor by it

Each Record is the game's, the interface's, or the presentation's. `game` marks a Record of the Rules region, `presentation` one of the Realization region, and `interface` a boundary Record between them. The split is the enduring-games convention ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 131-135, 158-160), and RUNS-Spacewar's loader enforces it as that project's own rule. [Three kinds of Record](./NETWORK_TOPOLOGY.md#three-kinds-of-record) states the rules the loader enforces. The presentation then comes out and is replaced whole, with no change to a rule.

1. Decide each Record's kind by what its values reach, not by what the code was written for. A value is the game's if any rule can observe it. Spacewar's central star draws two random numbers each frame from the generator that hyperspace also uses, so the draws are the game's. The line the star draws from them is presentation.
2. Put in the interface each Record that both sides need: what the game writes for the presentation to show, such as each object's position, and what comes in from the world, such as the controls.
3. Split each Processor that touches both a game Record and a presentation Record. The original often does both in one routine. Spacewar's exhaust burns a unit of fuel and plots a dot in each pass of one loop. The game's half becomes one Processor and the presentation's half another, and today's Network fires them in the original's order (see [4. Keep the order](#4-keep-the-order)). In today's text a loop that holds both moves up into the Network, as a loop that runs a macro does. The vision has no loop inside a tick but a bounded fold whose count is fixed before it starts (CONTEXT.md 204-206, 344-347); how such a loop is written is open.
4. Where a game value reaches the presentation through a shared word, give the value its own interface field. Spacewar computed a torpedo's start from the pen that draws the ship. The game now computes the ship's nose and the torpedo from it, and the outline starts its pen at the nose. The declarations keep both names in the original's words, so the image does not change.
5. Make every stream presentation. Every stream leaves to a device, so a stream of another kind does not load. A Processor that emits to a stream is presentation, so split from it any work that touches a game Record.
6. Check the split by observation. Run the game with every presentation Processor removed against the original. Every game Record must match. RUNS-Spacewar does this with `tools/check_frame.py` in its `alone` mode.
7. Declare in the top Networks' contracts what crosses between the program and the world.
   - Every stream the presentation writes, and every Record that leaves, goes in `writes:`. Spacewar's frame declares `writes: display, scoreboard, lights`.
   - Every Record with a field that has no initial value, and that a routine inside reads, goes in `reads:`. Spacewar's frame declares `reads: console, score, controls, outline_code`. The loader refuses a top Network that misses one.

   These Records are the boundary Records. The vision names inbound ones `requires:`, written by the runtime before a tick, and outbound ones `produces:`, read after it ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 272-275). It makes a precondition a DIGS boolean a Processor declares ([CONTEXT.md](https://github.com/enduring-game-standard/.github/blob/main/CONTEXT.md), lines 372-384). Today's text uses `reads:` and `writes:` for the boundary and `requires:` for the precondition, so its keywords disagree with the vision's.
8. Leave the devices out of RUNS. Which switch, joypad port, device register, light, or start address carries each field belongs to the declarations, and each machine's declarations state it in their events and devices (see [DECLARATIONS.md](./DECLARATIONS.md)). RUNS-Spacewar states all of them in `pdp1/devices.toml`.

Timing, pacing, and the machine underneath are presentation unless a game value depends on them. A frame budget, a wait for vertical blank, and a delay loop are presentation. A rule that reads how many instructions ran, or which line the beam was on, reads timing, and timing becomes a rule or a value that comes in.

**Done when** every Record has a kind, the purity report does not grow (Spacewar runs `tools/check_purity.py --against` the previous revision), the game with the presentation removed matches the original on every game Record, and the top Networks' contracts load. The conversion is done when the purity report's count is 0.

## 6. Measure where play reaches the machine

Do not guess where the game depends on the machine. Measure it by running the original through real play with the reach oracle. The scripted play covers every start address, every switch setting, and inputs that drive the game into its edge states: full tables, empty tables, the end of a match, every way an object dies. RUNS-Spacewar's `tools/reach_oracle.py` runs seventeen scripted matches in SIMH and names every data access by the Record field or source label it lands in.

The reach oracle reports these kinds of site. Spacewar's oracle reports the first seven.

- One instruction that reads or writes several places, such as a read past the end of an array, or a pointer into the wrong table.
- Reads of memory the image never loaded, before the program wrote it. In Spacewar, the scores and the game count start from whatever core held at power-on, and the first match reads them.
- Code the program writes and then runs.
- Code read as data, an instruction word read whole as a value.
- Jumps to unnamed places, including a jump into the middle of a routine or an instruction.
- Halts and hangs.
- Every place the machine's own arithmetic shows, such as a sum that wraps, a shift of a negative number, or a status flag that a later instruction reads.
- Reads of device registers, and the value each read returned.
- Interrupts taken, and the instruction each one interrupted.
- Reads through a bank mapping, a stack slot outside the current frame, or memory a DMA transfer writes.

Then decide each site:

| What play reaches | What the conversion does |
|-------------------|--------------------|
| The machine's arithmetic | Nothing more. The machine description's operators state it. |
| A status flag a later instruction reads | A field that the operator returns and the RUNS text stores. |
| Memory the image never loaded | Fields with no initial value, which the top Networks declare under `reads:`. |
| A device register | A field with no initial value in an interface Record, which the top Networks declare under `reads:`. The devices in the declarations name the register. |
| Code the program writes, then runs | Processors that state what the code computes. The compiler reproduces the code. |
| A jump into the middle of code | A machine glitch. A Processor states the rule the machine runs on that path. The compiler reproduces the bytes. |
| A halt or a hang | `stop`, or `emit` then `wait`. |
| An interrupt whose landing point play observes | Timing. A rule the RUNS text states, or a value that comes in. |
| A layout that play observes | A `layout` declaration in the RUNS text, as [MACHINE_DESCRIPTION.md](./MACHINE_DESCRIPTION.md) defines it under stated layout. It places only the Records play reads through layout. |
| A layout that play does not observe | Leave it out of the RUNS text. |

A read past an array is not a layout glitch until play observes it. Show that it does not before you leave it out of the RUNS text. Patch the emulator so that every such read loads a value no rule could use (a jump to address 0, an illegal opcode, a value that crashes the next instruction), and run the per-frame comparison. If every frame still matches the evaluator, play does not observe the read. Run the same check with the legitimate slots poisoned too, and confirm the emulator then fails, so the check can fail. Spacewar's main loop reads past the ships' two-word outline array for every torpedo slot. RUNS-Spacewar's `tools/check_frame.py` in its `poison` mode loads a jump to address 0 on every such read, and every frame with collisions still matches the evaluator. In its `poison-all` mode, the ships' own slots are poisoned too, and SIMH stops at once. Play never observes the read, and the image's layout carries it.

A read past an array that play does observe is a layout glitch. State the layout with a `layout` declaration that places the array and what follows it, in the machine description's address space, by its unit and byte order. Then the evaluator reads past the array what the layout puts there, and the comparison checks test it.

Make the tool check itself against the emulator. The reach oracle compares its copy of memory with the emulator's at the end of each scenario, and its model of the machine's arithmetic with the emulator's results. The Spacewar oracle compares its copy of core with SIMH's at the end of each match, and its model of each add, subtract, shift, and rotate with the AC that SIMH shows.

**Done when** the reach oracle's self-checks show no difference, every site in its report has a decision from the table above, and each layout read left out of the RUNS text has a poison check that passes and a control that fails.

## 7. Grade the conversion against the original

Run the RUNS source in the evaluator and the original in the emulator from the same Records, then compare every field and every output point.

1. Write a state map from each Record field to the original's memory and registers, from the symbol table or the disassembly. RUNS-Spacewar's `tools/pdp1.py` takes the addresses from the original's listing.
2. For a small routine, check every input when the inputs fit in an exhaustive run. Spacewar's sine and cosine each take one word, so their 2^18 inputs fit. `tools/check_sincos.py` checks a seeded sample with the edges on each change.
3. For larger routines and for Networks, check many seeded states that include the edge words, and states as play leaves them. A **seeded state** is a set of Records drawn by a seeded random generator from values the game itself can hold. The Spacewar frame Network matches SIMH on frames bunched so that collisions happen.
4. Check the inputs. Start from random power-on contents where the original reads them, and from every switch setting. An evaluator field that is unknown where the emulator holds a value counts as a difference. A field that keeps what the machine held at power-on and that nothing reads is left out of the comparison only by name, with that reason. In Spacewar, that is the `lights` Record, program flags 1 and 2.
5. Make sure each check can fail. Plant defects in the RUNS source, such as an off-by-one or a dropped random draw, and confirm the check catches each one. RUNS-Spacewar does this with `tools/mutate.sh`.

If a loop runs past its bound, a `requires:` fails, or `unreachable` fires, the RUNS text is wrong. Fix the text. Those errors are never the game's behavior.

**Done when** every comparison check matches the emulator on its states, and each check reports a difference for each defect planted in it.

## 8. Compile with the declarations

A compiler takes RUNS plus a target's declarations. With the original machine's declarations, the result is the original binary, exactly. Every step of a conversion runs this compile. [DECLARATIONS.md](./DECLARATIONS.md) defines the sections of the declarations, what every compiler refuses, and the layout rules that belong to the compiler, not the declarations. RUNS-Spacewar's PDP-1 declarations are `pdp1/`, a TOML file for each unit plus `devices.toml`, and `pdp1/README.md` defines their vocabulary.

The route from RUNS to the image is the compiler's. It can emit a high-level language that an existing toolchain compiles, assembly, or machine code directly, whichever reproduces the original binary. The Spacewar compiler, `tools/runsc.py`, writes the C dialect of the `spacewar-c` project, and spacewar-c's `pdp1cc` (in RUNS-Spacewar's `tools/pdp1cc`) compiles that C to a tape image.

Check that the RUNS text, not the declarations, decides the image, with [the mutation gate](./DECLARATIONS.md#the-mutation-gate). RUNS-Spacewar's is `tools/check_compiled.py`.

A new machine needs a declarations vocabulary of its own. [Designing a vocabulary for a new machine](./DECLARATIONS.md#designing-a-vocabulary-for-a-new-machine) says how a conversion designs one.

A step is done when all of these pass:

1. The compiler reports that the image matches the original. Spacewar's `runsc` prints `MATCH`.
2. The mutation gate passes. Spacewar's is `check_compiled`.
3. Each RUNS routine the step changed matches the original in the emulator, over every input or over a seeded sample with the edge words.
4. The checks of earlier steps still pass. In RUNS-Spacewar, `tools/check_all.sh` runs them.
5. The count of entries in the declarations did not rise. Spacewar's check is `tools/check_declarations.py`.

## Assets

Assets, such as art and sound, are the concern of AEMS, a separate protocol. Spacewar's ship outlines and star catalog are data on the tape, so the conversion keeps them in the RUNS text as Records.

*MIT License. Open for implementation, extension, and critique.*
