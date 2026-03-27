# T3: Network Composition Verification

A tool that reads a `.runs` Network and statically checks for composition bugs: stale reads, write conflicts, guard cycles, missing state coverage, dead Processors.

**Needs**: Formal verification researcher who designs games.
**Estimated effort**: 6–12 months. Requires the Network formal grammar first.

## The Problem

Individual Processors are pure and type-checked. But 200+ Processors wired into a Network can have emergent bugs that no individual Processor check catches:

| Bug class | Example |
|-----------|---------|
| Stale read | Processor A reads position BEFORE Processor B updates it |
| Write conflict | Two Processors write the same output field on the same entity |
| Guard cycle | State A → State B → State A every tick |
| Missing path | No Processor handles entity in state X with condition Y |
| Dead Processor | A Processor's guard conditions are never satisfiable |

## Individual Checks (each well-understood)

1. Data dependency ordering (topological sort of field read/write graph)
2. Output coverage (every declared output assigned on every path)
3. Guard completeness (every entity state has a matching guard)
4. Guard acyclicity (guard dispatch graph is DAG within a tick)
5. Write exclusivity (no field written by multiple Processors per entity per tick)

## What's Hard

Scaling to 200+ Processor Networks without combinatorial explosion. Making error messages actionable ("entity X oscillates between states A and B because Processors P and Q have contradictory guards").
