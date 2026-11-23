---
status: accepted
date: 2026-06-06
---

# Protocol, conventions, and ecosystem; `runs:` is reserved and fixed but optional

RUNS has three tiers:

- **Protocol**: Records, Fields, Processors, Networks, DIGS, and the reservation of `runs:`. Valid RUNS. It changes rarely. It lives in this repo.
- **Conventions**: recommended Record shapes and Processor signatures, naming, the manifest format, and namespace governance. Standard RUNS. It lives in runs-library.
- **Ecosystem**: bundles on the commons, published as Nostr events.

Only the standard defines `runs:` keys. A program that uses one uses the standard's exact keys, types, and meaning. Using `runs:` is optional: a game built on its own prefix, such as `spacewar:`, is valid RUNS.

## Consequences

- A runtime does not "implement a schema"; it runs baked Processors. Games target data shapes.
- runs-library is an index, never a vault: it holds the contracts and governance, and points by content ID at reference bodies on the commons. One artifact has one home (ADR-0004), and a rival body needs no one's permission. Until reference bodies exist, it holds conceptual examples, which are not reference implementations and do not graduate into them.
- Only `runs:` is governed. Identity is cryptographic: the author's npub roots the namespace and the content hash roots the artifact. Two authors' `pong:object` never collide, so other prefixes are for reading, not identity.
- **Open**: this decision once renamed this repo to `runs` and runs-library to `runs-conventions`. Neither rename has happened.
