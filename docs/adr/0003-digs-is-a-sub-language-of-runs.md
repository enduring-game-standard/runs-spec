---
status: accepted
date: 2026-06-04
---

# DIGS is a sub-language of RUNS, not a fifth protocol

RUNS has three layers: data (Records and Fields), wiring (Networks), and computation (Processor bodies). DIGS is the language of the third, and Network Guards reuse its expressions. It has its own name, spec page, and file extension (`.runs-prim`), which invites promoting it to a peer protocol or its own repo. It stays in this spec and versions with RUNS, because it means nothing outside RUNS. It does not write MAPS, which has its own notation. The wiring layer stays unnamed ("RUNS Networks"): one named sub-language is enough.
