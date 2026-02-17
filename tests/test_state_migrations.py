import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from governed_platform.governance.state_manager import StateManager  # noqa: E402
from governed_platform.governance.migrations.runner import migrate_state  # noqa: E402


class StateMigrationTests(unittest.TestCase):
    def test_backward_compat_legacy_unversioned(self):
        legacy = {"packets": {"A": {"status": "pending"}}, "log": []}
        migrated = migrate_state(legacy)
        self.assertEqual(migrated["version"], "1.0")
        self.assertIn("area_closeouts", migrated)
        self.assertIn("packets", migrated)

    def test_forward_incompatible_version_rejected(self):
        state = {"version": "99.0", "packets": {}, "log": []}
        with self.assertRaises(ValueError):
            migrate_state(state)

    def test_state_manager_loads_and_saves_versioned_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            path.write_text(json.dumps({"packets": {}, "log": []}))
            sm = StateManager(path)
            state = sm.load()
            self.assertEqual(state["version"], "1.0")
            sm.save(state)
            saved = json.loads(path.read_text())
            self.assertEqual(saved["version"], "1.0")
            self.assertIn("updated_at", saved)


if __name__ == "__main__":
    unittest.main()
