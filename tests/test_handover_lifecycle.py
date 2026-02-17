import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
import sys

sys.path.insert(0, str(SRC))

from governed_platform.governance.engine import GovernanceEngine  # noqa: E402
from governed_platform.governance.state_manager import StateManager  # noqa: E402


class HandoverLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.definition = {
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [{"id": "A", "wbs_ref": "1.1", "title": "A", "area_id": "1.0"}],
            "dependencies": {},
        }
        sm = StateManager(self.state_path)
        state = sm.load()
        state["packets"]["A"] = {
            "status": "pending",
            "assigned_to": None,
            "started_at": None,
            "completed_at": None,
            "notes": None,
        }
        sm.save(state)
        self.engine = GovernanceEngine(self.definition, sm)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_handover_and_resume_flow(self):
        ok, _ = self.engine.claim("A", "agent-1")
        self.assertTrue(ok)

        ok, _ = self.engine.handover(
            "A",
            "agent-1",
            "session timeout",
            progress_notes="implemented core logic",
            files_modified=["src/x.py", "tests/test_x.py"],
            remaining_work=["rerun tests", "update docs"],
            to_agent="agent-2",
        )
        self.assertTrue(ok)

        state = self.engine.status()
        pkt = state["packets"]["A"]
        self.assertEqual(pkt["status"], "in_progress")
        self.assertIsNone(pkt["assigned_to"])
        self.assertEqual(len(pkt.get("handovers", [])), 1)
        self.assertTrue(pkt["handovers"][0]["active"])

        ok, msg = self.engine.done("A", "agent-2", "done")
        self.assertFalse(ok)
        self.assertIn("active handover", msg)

        ok, _ = self.engine.resume("A", "agent-2")
        self.assertTrue(ok)
        state = self.engine.status()
        pkt = state["packets"]["A"]
        self.assertEqual(pkt["assigned_to"], "agent-2")
        self.assertFalse(pkt["handovers"][0]["active"])
        self.assertEqual(pkt["handovers"][0]["resumed_by"], "agent-2")

        ok, _ = self.engine.done("A", "agent-2", "done")
        self.assertTrue(ok)

    def test_handover_requires_current_owner(self):
        self.engine.claim("A", "agent-1")
        ok, msg = self.engine.handover("A", "agent-2", "handoff")
        self.assertFalse(ok)
        self.assertIn("owned by", msg)

    def test_resume_requires_active_handover(self):
        self.engine.claim("A", "agent-1")
        ok, msg = self.engine.resume("A", "agent-2")
        self.assertFalse(ok)
        self.assertIn("no active handover", msg)

    def test_resume_enforces_target_agent(self):
        self.engine.claim("A", "agent-1")
        self.engine.handover("A", "agent-1", "handoff", to_agent="agent-2")
        ok, msg = self.engine.resume("A", "agent-3")
        self.assertFalse(ok)
        self.assertIn("targeted to agent-2", msg)

    def test_single_active_handover_enforced(self):
        self.engine.claim("A", "agent-1")
        ok, _ = self.engine.handover("A", "agent-1", "handoff")
        self.assertTrue(ok)
        ok, msg = self.engine.handover("A", "agent-1", "second handoff")
        self.assertFalse(ok)
        self.assertIn("already has an active handover", msg)


if __name__ == "__main__":
    unittest.main()
