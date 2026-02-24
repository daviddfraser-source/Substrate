#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd):
    start = datetime.now(timezone.utc).isoformat()
    try:
        subprocess.run(command, check=True, cwd=cwd)
        result = "success"
    except subprocess.CalledProcessError:
        result = "failure"
    end = datetime.now(timezone.utc).isoformat()
    return {"command": " ".join(command), "cwd": str(cwd), "result": result, "start": start, "end": end}


def main():
    scenarios = [
        (["npm", "run", "test"], ROOT / "templates" / "ai-substrate"),
        (["node", "scripts/eval-policy.js"], ROOT),
    ]
    report = {"scenarios": [], "generated_at": datetime.now(timezone.utc).isoformat()}
    for cmd, cwd in scenarios:
        report["scenarios"].append(run(cmd, cwd))
        if report["scenarios"][-1]["result"] == "failure":
            break

    with open("reports/ai-substrate-eval.json", "w") as handle:
        json.dump(report, handle, indent=2)

    if any(s["result"] == "failure" for s in report["scenarios"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
