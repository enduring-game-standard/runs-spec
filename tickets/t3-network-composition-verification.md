# T3: Network Composition Verification

A tool that reads a `.runs` Network and statically checks for composition bugs: stale reads, write conflicts, guard cycles, missing state coverage, dead Processors.

**Needs**: Formal verification researcher who designs games.
**Estimated effort**: 6–12 months.
**Dependency**: ✅ Network formal grammar — resolved by [NETWORK_TOPOLOGY.md](../NETWORK_TOPOLOGY.md). The verification properties are now formalized in §Verification Properties of that specification.

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

The [Network Topology](../NETWORK_TOPOLOGY.md) §Verification Properties now formalizes these as mandatory compiler checks:

1. ✅ **Bipartite invariant** — every data dependency passes through a Record
2. ✅ **Dispatch boundedness** — maximum Processor firings computable from declarations
3. ✅ **Guard completeness** — every entity state has a matching guard
4. ✅ **Guard exclusivity** — at most one guard fires per entity per dispatch
5. ✅ **Write exclusivity** — no field written by multiple concurrent Processors per entity per tick
6. ✅ **Phase acyclicity** — data dependency graph between phases is a DAG
7. ✅ **Output completeness** — every declared output assigned by at least one phase

## What's Hard

Scaling to 200+ Processor Networks without combinatorial explosion. Making error messages actionable ("entity X oscillates between states A and B because Processors P and Q have contradictory guards"). Verification should be compositional: sub-Networks verified in isolation against their declared interfaces, then composed.
