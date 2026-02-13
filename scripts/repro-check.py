#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from governed_platform.determinism.validator import build_reproducibility_record


def main():
    state_path = ROOT / ".governance" / "wbs-state.json"
    state = json.loads(state_path.read_text())
    execution = {
        "command": ["python3", ".governance/wbs_cli.py", "status"],
        "returncode": 0,
        "stdout": "",
        "stderr": "",
    }
    artifacts = [
        ROOT / "AGENTS.md",
        ROOT / ".governance" / "wbs.json",
    ]
    record = build_reproducibility_record(execution, state, artifacts)
    out = ROOT / "docs" / "codex-migration" / "reproducibility-record.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
