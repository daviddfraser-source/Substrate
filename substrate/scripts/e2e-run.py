#!/usr/bin/env python3
"""Run an E2E command and persist normalized run output for dashboard consumption."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_store(path: Path) -> Dict:
    if not path.exists():
        return {"schema_version": "1.0", "updated_at": now_iso(), "runs": []}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("schema_version", "1.0")
    data.setdefault("updated_at", now_iso())
    data.setdefault("runs", [])
    return data


def parse_unittest_summary(output: str) -> Dict[str, int] | None:
    ran = re.search(r"Ran\s+(\d+)\s+tests?", output)
    if not ran:
        return None
    total = int(ran.group(1))
    if "\nOK" in output or output.rstrip().endswith("OK"):
        return {"passed": total, "failed": 0, "skipped": 0, "total": total}
    failed = 0
    skipped = 0
    m = re.search(r"FAILED\s*\((.*?)\)", output)
    if m:
        parts = m.group(1)
        mf = re.search(r"failures=(\d+)", parts)
        me = re.search(r"errors=(\d+)", parts)
        ms = re.search(r"skipped=(\d+)", parts)
        failed = int(mf.group(1)) if mf else 0
        failed += int(me.group(1)) if me else 0
        skipped = int(ms.group(1)) if ms else 0
    passed = max(total - failed - skipped, 0)
    return {"passed": passed, "failed": failed, "skipped": skipped, "total": total}


def parse_pytest_summary(output: str) -> Dict[str, int] | None:
    line = None
    for candidate in output.splitlines()[::-1]:
        if " passed" in candidate or " failed" in candidate:
            line = candidate
            break
    if not line:
        return None

    def grab(key: str) -> int:
        m = re.search(rf"(\d+)\s+{key}", line)
        return int(m.group(1)) if m else 0

    passed = grab("passed")
    failed = grab("failed") + grab("error") + grab("errors")
    skipped = grab("skipped") + grab("xfailed") + grab("xpassed")
    total = passed + failed + skipped
    if total == 0:
        return None
    return {"passed": passed, "failed": failed, "skipped": skipped, "total": total}


def parse_summary(output: str, exit_code: int) -> Dict[str, int]:
    for parser in (parse_unittest_summary, parse_pytest_summary):
        summary = parser(output)
        if summary:
            return summary
    return {"passed": 0 if exit_code else 1, "failed": 1 if exit_code else 0, "skipped": 0, "total": 1}


def extract_failures(output: str, limit: int = 20) -> List[Dict[str, str | None]]:
    patterns = [
        re.compile(r"^FAIL:\s+(?P<test>.+)$"),
        re.compile(r"^FAILED\s+(?P<test>.+?)\s+-\s+(?P<msg>.+)$"),
        re.compile(r"^(?P<file>[^:\s]+\.py):\d+:\s+AssertionError: (?P<msg>.+)$"),
        re.compile(r"^E\s+AssertionError:\s+(?P<msg>.+)$"),
        re.compile(r"^ERROR:\s+(?P<test>.+)$"),
    ]

    findings: List[Dict[str, str | None]] = []
    seen = set()
    lines = output.splitlines()

    for idx, line in enumerate(lines):
        stripped = line.strip()
        for pat in patterns:
            match = pat.match(stripped)
            if not match:
                continue
            test_id = match.groupdict().get("test")
            file_path = match.groupdict().get("file")
            msg = match.groupdict().get("msg") or stripped
            snippet = None
            if idx + 1 < len(lines):
                nxt = lines[idx + 1].strip()
                snippet = nxt[:240] if nxt else None
            key = (test_id or "", file_path or "", msg)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                {
                    "test_id": test_id,
                    "message": msg,
                    "file": file_path,
                    "snippet": snippet,
                }
            )
            if len(findings) >= limit:
                return findings
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run e2e suite and persist normalized run output")
    parser.add_argument("--suite", required=True, help="Suite name (e.g. ui-regression, api-e2e)")
    parser.add_argument("--cmd", required=True, help="Shell command for the e2e run")
    parser.add_argument("--agent", default=os.environ.get("E2E_AGENT", "codex"))
    parser.add_argument("--packet-id", default=os.environ.get("E2E_PACKET_ID"))
    parser.add_argument("--trigger", choices=["local", "ci", "manual"], default=os.environ.get("E2E_TRIGGER", "local"))
    parser.add_argument("--artifact", action="append", default=[], help="Additional artifact path(s)")
    parser.add_argument("--max-runs", type=int, default=200, help="Retention limit for stored runs")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    substrate_root = repo_root / "substrate"
    gov_dir = substrate_root / ".governance"
    store_path = gov_dir / "e2e-runs.json"
    log_dir = substrate_root / "reports" / "e2e"
    log_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"e2e-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    started = datetime.now(timezone.utc)

    cmd_argv = shlex.split(args.cmd)
    proc = subprocess.run(
        cmd_argv,
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    ended = datetime.now(timezone.utc)
    duration = (ended - started).total_seconds()

    output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    log_path = log_dir / f"{run_id}.log"
    log_path.write_text(output, encoding="utf-8")

    summary = parse_summary(output, proc.returncode)
    failures = extract_failures(output)
    status = "pass" if proc.returncode == 0 else "fail"

    artifacts = [str(log_path.relative_to(repo_root))]
    artifacts.extend(args.artifact)

    entry = {
        "run_id": run_id,
        "timestamp": started.isoformat(),
        "agent": args.agent,
        "packet_id": args.packet_id,
        "trigger": args.trigger,
        "suite": args.suite,
        "status": status,
        "duration_sec": round(duration, 3),
        "command": args.cmd,
        "exit_code": proc.returncode,
        "summary": summary,
        "failures": failures,
        "artifacts": artifacts,
    }

    store = load_store(store_path)
    runs = store.get("runs", [])
    runs.insert(0, entry)
    store["runs"] = runs[: max(1, args.max_runs)]
    store["updated_at"] = now_iso()
    store["schema_version"] = "1.0"
    store_path.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": proc.returncode == 0, "run_id": run_id, "store": str(store_path), "log": str(log_path)}, indent=2))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
