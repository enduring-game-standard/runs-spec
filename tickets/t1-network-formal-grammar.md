# T1: Network Formal Grammar

The RUNS spec describes Networks at arm's length. The Spacewar conversion invented a Network syntax. That syntax needs to become a formal grammar in the spec, like the expression language EBNF.

**Depends on**: A second game's Network to validate the grammar isn't over-fitted to Spacewar.

## Must Express

- Ordered execution phases
- Guarded dispatch (state-based routing to Processors)
- Slot-order iteration over entity collections
- Sub-Network bundling (hierarchical composition)
- Inbound/outbound boundary Field declarations

## From the Postmortem

> "The spec needs a formal Network grammar. This should be written before the second RUNS game, not after."
