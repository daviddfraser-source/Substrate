#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime

def run(command):
    start = datetime.utcnow().isoformat() + "Z"
    try:
        subprocess.run(command, shell=True, check=True)
        result = "success"
    except subprocess.CalledProcessError:
        result = "failure"
    end = datetime.utcnow().isoformat() + "Z"
    return {"command": command, "result": result, "start": start, "end": end}


def main():
    scenarios = [
        "npm run lint",
        "npm run typecheck",
        "npm run test",
        "node scripts/eval-policy.js"
    ]
    report = {"scenarios": [], "generated_at": datetime.utcnow().isoformat() + "Z"}
    for cmd in scenarios:
        report["scenarios"].append(run(cmd))
        if report["scenarios"][-1]["result"] == "failure":
            break

    with open("reports/ai-substrate-eval.json", "w") as handle:
        json.dump(report, handle, indent=2)

    if any(s["result"] == "failure" for s in report["scenarios"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
