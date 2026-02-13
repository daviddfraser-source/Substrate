import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
import sys
sys.path.insert(0, str(SRC))

from governed_platform.governance.engine import GovernanceEngine  # noqa: E402
from governed_platform.governance.state_manager import StateManager  # noqa: E402


class GovernanceEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.definition = {
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [
                {"id": "A", "wbs_ref": "1.1", "title": "A", "area_id": "1.0"},
                {"id": "B", "wbs_ref": "1.2", "title": "B", "area_id": "1.0"},
            ],
            "dependencies": {"B": ["A"]},
        }
        sm = StateManager(self.state_path)
        state = sm.load()
        state["packets"]["A"] = {"status": "pending", "assigned_to": None, "started_at": None, "completed_at": None, "notes": None}
        state["packets"]["B"] = {"status": "pending", "assigned_to": None, "started_at": None, "completed_at": None, "notes": None}
        sm.save(state)
        self.engine = GovernanceEngine(self.definition, sm)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_claim_and_done(self):
        ok, _ = self.engine.claim("A", "agent")
        self.assertTrue(ok)
        ok, _ = self.engine.done("A", "agent", "done")
        self.assertTrue(ok)
        ready = self.engine.ready()["ready"]
        self.assertEqual([x["id"] for x in ready], ["B"])

    def test_fail_blocks_dependents(self):
        self.engine.claim("A", "agent")
        ok, msg = self.engine.fail("A", "agent", "bad")
        self.assertTrue(ok)
        self.assertIn("failed", msg)
        state = self.engine.status()
        self.assertEqual(state["packets"]["B"]["status"], "blocked")

    def test_closeout_l2(self):
        self.engine.claim("A", "agent")
        self.engine.done("A", "agent", "done")
        self.engine.claim("B", "agent")
        self.engine.done("B", "agent", "done")

        drift = Path(self.tmpdir.name) / "drift.md"
        drift.write_text(
            "\n".join(
                [
                    "## Scope Reviewed",
                    "## Expected vs Delivered",
                    "## Drift Assessment",
                    "## Evidence Reviewed",
                    "## Residual Risks",
                    "## Immediate Next Actions",
                ]
            )
        )
        ok, _ = self.engine.closeout_l2("1", "agent", str(drift), "ok")
        self.assertTrue(ok)
        state = self.engine.status()
        self.assertIn("1.0", state.get("area_closeouts", {}))

    def test_legacy_state_migrated(self):
        legacy = {"packets": {}, "log": []}
        self.state_path.write_text(json.dumps(legacy))
        sm = StateManager(self.state_path)
        state = sm.load()
        self.assertEqual(state["version"], "1.0")
        self.assertIn("area_closeouts", state)


if __name__ == "__main__":
    unittest.main()
