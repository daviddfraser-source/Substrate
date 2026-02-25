import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from substrate_core.storage import FileStorage


class FileStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "wbs-state.json"
        self.storage = FileStorage(self.state_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_read_state_returns_compatible_default_shape(self):
        state = self.storage.read_state()
        self.assertEqual(state["version"], "1.0")
        self.assertEqual(state["packets"], {})
        self.assertEqual(state["log"], [])
        self.assertEqual(state["area_closeouts"], {})
        self.assertEqual(state["log_integrity_mode"], "plain")

    def test_write_state_persists_payload(self):
        state = self.storage.read_state()
        state["packets"]["A"] = {"status": "pending"}
        self.storage.write_state(state)

        persisted = json.loads(self.state_path.read_text())
        self.assertEqual(persisted["packets"]["A"]["status"], "pending")
        self.assertIn("updated_at", persisted)

    def test_append_audit_adds_entry_and_persists(self):
        entry = {"packet_id": "A", "event": "started", "agent": "codex"}
        self.storage.append_audit(entry)

        persisted = json.loads(self.state_path.read_text())
        self.assertEqual(len(persisted["log"]), 1)
        self.assertEqual(persisted["log"][0]["event"], "started")


if __name__ == "__main__":
    unittest.main()
