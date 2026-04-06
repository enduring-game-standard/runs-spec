# T1: Network Formal Grammar

> **Status**: ✅ Resolved — see [NETWORK_TOPOLOGY.md](../NETWORK_TOPOLOGY.md)

The RUNS spec describes Networks at arm's length. The Spacewar conversion invented a Network syntax. That syntax needs to become a formal grammar in the spec, like the expression language EBNF.

**Depends on**: A second game's Network to validate the grammar isn't over-fitted to Spacewar.

## Resolution

The [Network Topology](../NETWORK_TOPOLOGY.md) specification formalizes the grammar with five phase types (Processor, Network, Dispatch, Iterate, Guarded), a complete EBNF grammar, concurrency semantics, verification properties, and deliberate exclusions.

The grammar was stress-tested against three tiers of complexity (Spacewar, DOOM, TLOU) during design. The second-game validation dependency remains — the grammar should be verified against actual DOOM conversion.

## Must Express

- ✅ Ordered execution phases
- ✅ Guarded dispatch (state-based routing to Processors)
- ✅ Slot-order iteration over entity collections
- ✅ Sub-Network bundling (hierarchical composition)
- ✅ Inbound/outbound boundary Field declarations
- ✅ Bounded iteration for physics constraint solvers (added during design)

## From the Postmortem

> "The spec needs a formal Network grammar. This should be written before the second RUNS game, not after."
