"""Check every RUNS example in the runs-spec docs against RUNS-Spacewar's tools/runs.py.

Fenced blocks tagged `runs` or `runs-prim` are accepted examples. Each must load
alone. All accepted blocks of one document then load together as one program,
pass runs.check, and every top Network in it runs six passes. Before each top
Network runs, the world gives every field of its `reads:` Records that has no
initial value: the word 0, or the enum's first member.
Blocks tagged `runs-rejected` or `runs-prim-rejected` must start with
`# rejected: <text>`; loading and running them must raise a RunsError whose
message contains <text>.

The docs' prose must have no em dash or en dash.

usage: python3 tools/check_examples.py [<runs-spec dir> [<RUNS-Spacewar dir>]]
The defaults are this repository and ../RUNS-Spacewar beside it."""
import re
import sys
import tempfile
from pathlib import Path

spec = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
port = Path(sys.argv[2]) if len(sys.argv) > 2 else spec.parent / "RUNS-Spacewar"
sys.path.insert(0, str(port / "tools"))
import runs  # noqa: E402

FENCE = re.compile(r"^```(runs|runs-prim|runs-rejected|runs-prim-rejected)\n(.*?)^```", re.M | re.S)


def tops(prog):
    fired = set().union(*(runs.runs_of(r.body) - {r.name} for r in prog.routines.values()))
    return [r.name for r in prog.routines.values() if r.kind == "network" and r.name not in fired]


def give_inputs(m, prog, network):
    for name in prog.routines[network].reads:
        rec = prog.records[name]
        for fld, (typ, _) in rec.fields.items():
            if typ == "insn":
                continue
            value = runs.Member(typ, prog.enums[typ][0]) if typ in prog.enums else runs.W(0)
            slots = m.state[name][fld] if rec.count is not None else None
            if slots is None and m.state[name][fld] is runs.UNKNOWN:
                m.state[name][fld] = value
            for k in range(len(slots or [])):
                if slots[k] is runs.UNKNOWN:
                    slots[k] = value


def exercise(root: Path):
    prog = runs.program(root)
    for name in tops(prog):
        m = runs.Machine(prog)
        give_inputs(m, prog, name)
        for _ in range(6):
            try:
                m.run(name)
            except runs.Stop:
                pass
    return prog


failures = 0
for doc in sorted(spec.glob("*.md")):
    text = doc.read_text()
    for n, line in enumerate(text.splitlines(), 1):
        if "—" in line or "–" in line:
            print(f"FAIL {doc.name}:{n} has a dash: {line.strip()[:60]}")
            failures += 1
    blocks = FENCE.findall(text)
    if not blocks:
        continue
    with tempfile.TemporaryDirectory() as whole:
        accepted = 0
        for n, (tag, body) in enumerate(blocks):
            ext = "runs-prim" if tag.startswith("runs-prim") else "runs"
            with tempfile.TemporaryDirectory() as alone:
                f = Path(alone) / f"example.{ext}"
                f.write_text(body)
                if tag.endswith("rejected"):
                    want = re.match(r"# rejected: (.*)", body).group(1).strip()
                    try:
                        exercise(Path(alone))
                    except runs.RunsError as e:
                        if want in str(e):
                            print(f"ok   {doc.name} #{n} rejected: {e}")
                            continue
                        print(f"FAIL {doc.name} #{n} rejected for another reason: {e}")
                    else:
                        print(f"FAIL {doc.name} #{n} was accepted")
                    failures += 1
                    continue
                try:
                    runs.load([f])
                except runs.RunsError as e:
                    print(f"FAIL {doc.name} #{n} does not load: {e}")
                    failures += 1
                    continue
            (Path(whole) / f"{n:02}.{ext}").write_text(body)
            accepted += 1
        try:
            prog = exercise(Path(whole))
            print(f"ok   {doc.name}: {accepted} blocks load as one program; ran {tops(prog)}")
        except Exception as e:
            print(f"FAIL {doc.name}: program: {type(e).__name__}: {e}")
            failures += 1
sys.exit(1 if failures else 0)
