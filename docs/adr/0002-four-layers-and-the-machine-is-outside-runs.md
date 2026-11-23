---
status: accepted
date: 2026-11-22
---

# Four layers: Game Logic, Presentation, compiler, and the machine, which is outside RUNS

A game in RUNS has three layers, and it runs on a fourth that RUNS does not describe:

- **Game Logic**: Processors in DIGS that work on any device. Every arithmetic they depend on is declared in their types, so they stay pure.
- **Presentation**: everything that is not Game Logic or an Interface Record. It is the machine-specific software that reads one machine's inputs and drives its outputs. It follows the machine's conventions; it does not encode the machine.
- **Compiler**: one per machine. It takes Game Logic and a Presentation and makes a build for that machine.
- **Machine**: the hardware, or an emulator of it, that everything runs on. RUNS says nothing about it.

A Conversion's goal is the game, not the machine the game shipped on. So the line between Game Logic and machine follows the program. How the program's own operations behave on the hardware is Game Logic, declared in RUNS: arithmetic overflow, memory past an array, code the program writes for itself. Code the program never contained, such as bytes a player writes and the machine then runs, is the machine's behavior. A Conversion does not carry it, and a build that cannot run it changes no Game Logic, so it is not a Variant.

## Considered options

- **Everything the original machine does the same way every time is Game Logic.** Rejected. It makes the original machine part of the game, so a game's Game Logic would describe one machine's CPU and could not work on any device.

## Consequences

- Game Logic and Presentation meet only at Interface Records, never at a Processor. A Record is data, so it belongs to neither side; a Processor's code is written for one side, so a Processor on the line would already be on one side of it. Any translation is a Processor on one side.
- `jump code at most N` stays in DIGS: it runs code the program wrote for itself, the way the original machine runs it.
- Super Mario World's source does not contain Flappy Bird, and its Conversion does not either.
- "Machine", "compiler", and "runtime" keep their ordinary computing meanings. A runtime environment (an OS, a browser, PICO-8) is part of the machine a binary targets.
