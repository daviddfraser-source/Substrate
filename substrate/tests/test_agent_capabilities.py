import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, str(ROOT / ".governance" / "wbs_cli.py")]
WBS = ROOT / ".governance" / "wbs.json"
STATE = ROOT / ".governance" / "wbs-state.json"
AGENTS = ROOT / ".governance" / "agents.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def write_agents_registry(mode: str, agent_caps: dict):
    registry = {
        "version": "1.0",
        "enforcement_mode": mode,
        "capability_taxonomy": ["code", "test", "docs", "review", "research", "deploy"],
        "agents": [],
    }
    for agent_id, caps in agent_caps.items():
        registry["agents"].append(
            {
                "id": agent_id,
                "type": "llm",
                "capabilities": caps,
                "constraints": {"max_concurrent_packets": 1},
                "metadata": {},
            }
        )
    AGENTS.write_text(json.dumps(registry, indent=2) + "\n")


class AgentCapabilitiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        cls._agents_backup = AGENTS.read_bytes() if AGENTS.exists() else None

    @classmethod
    def tearDownClass(cls):
        if cls._wbs_backup is None:
            WBS.unlink(missing_ok=True)
        else:
            WBS.write_bytes(cls._wbs_backup)

        if cls._state_backup is None:
            STATE.unlink(missing_ok=True)
        else:
            STATE.write_bytes(cls._state_backup)

        if cls._agents_backup is None:
            AGENTS.unlink(missing_ok=True)
        else:
            AGENTS.write_bytes(cls._agents_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        payload = {
            "metadata": {"project_name": "caps-test", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {
                    "id": "A",
                    "wbs_ref": "1.1",
                    "area_id": "1.0",
                    "title": "A",
                    "scope": "",
                    "required_capabilities": ["code", "test"],
                }
            ],
            "dependencies": {},
        }
        fd, path = tempfile.mkstemp(suffix="-wbs.json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)

    def test_advisory_mode_warns_but_allows_claim(self):
        write_agents_registry("advisory", {"docbot": ["docs"]})
        proc = run_cli(["claim", "A", "docbot"])
        self.assertIn("Capability warning", proc.stdout)

    def test_strict_mode_blocks_mismatched_claim(self):
        write_agents_registry("strict", {"docbot": ["docs"]})
        proc = run_cli(["claim", "A", "docbot"], expect=1)
        self.assertIn("missing required capabilities", proc.stdout)

    def test_disabled_mode_allows_mismatched_claim(self):
        write_agents_registry("disabled", {"docbot": ["docs"]})
        proc = run_cli(["claim", "A", "docbot"])
        self.assertIn("claimed by docbot", proc.stdout)

    def test_strict_mode_allows_matching_claim(self):
        write_agents_registry("strict", {"coder": ["code", "test", "docs"]})
        proc = run_cli(["claim", "A", "coder"])
        self.assertIn("claimed by coder", proc.stdout)


if __name__ == "__main__":
    unittest.main()
