---
status: accepted
date: 2026-11-22
---

# Four layers: game logic, presentation, compiler, and the machine, which is outside RUNS

A game in RUNS has three layers, and it runs on a fourth that RUNS does not describe:

- **Game logic**: Processors in DIGS that work on any device. Every arithmetic they depend on is declared in their types, so they stay pure.
- **Presentation**: everything that is not game logic or an Interface Record. It is the machine-specific software that reads one machine's inputs and drives its outputs. It follows the machine's conventions; it does not encode the machine.
- **Compiler**: one per machine. It takes game logic and a presentation and makes a build for that machine.
- **Machine**: the hardware, or an emulator of it, that everything runs on. RUNS says nothing about it.

A Conversion's goal is the game, not the machine the game shipped on. So the line between game logic and machine follows the program. How the program's own operations behave on the hardware is game logic, declared in RUNS: arithmetic overflow, memory past an array, code the program writes for itself. Code the program never contained, such as bytes a player writes and the machine then runs, is the machine's behavior. A Conversion does not carry it, and a build that cannot run it changes no game logic, so it is not a Variant.

## Considered options

- **Everything the original machine does the same way every time is game logic.** Rejected. It makes the original machine part of the game, so a game's game logic would describe one machine's CPU and could not work on any device.

## Consequences

- `jump code at most N` stays in DIGS: it runs code the program wrote for itself, the way the original machine runs it.
- Super Mario World's source does not contain Flappy Bird, and its Conversion does not either.
- "Machine", "compiler", and "runtime" keep their ordinary computing meanings. A runtime environment (an OS, a browser, PICO-8) is part of the machine a binary targets.
