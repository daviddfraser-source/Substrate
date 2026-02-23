import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from governed_platform.governance.engine import GovernanceEngine  # noqa: E402
from governed_platform.governance.state_manager import StateManager  # noqa: E402


class SupervisorEnforcementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmp.name) / "state.json"
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
        self.tmp.cleanup()

    def test_done_requires_notes(self):
        ok, _ = self.engine.claim("A", "agent")
        self.assertTrue(ok)
        ok, msg = self.engine.done("A", "agent", "")
        self.assertFalse(ok)
        self.assertIn("Supervisor denied", msg)

    def test_claim_requires_agent(self):
        ok, msg = self.engine.claim("A", "")
        self.assertFalse(ok)
        self.assertIn("Supervisor denied", msg)


if __name__ == "__main__":
    unittest.main()
