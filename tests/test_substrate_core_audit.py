import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.audit import (
    append_mutation_log,
    export_provenance_snapshot,
    provenance_chain,
    validate_append_only_log,
)
from substrate_core.storage import FileStorage


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "wbs-state.json"
        self.storage = FileStorage(self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_append_mutation_log_records_required_fields(self):
        entry = append_mutation_log(
            self.storage,
            packet_id="A",
            lifecycle_event="started",
            action="claim",
            actor={"user_id": "dfraser", "role": "developer", "source": "terminal"},
            result="success",
            notes="Claimed from terminal",
            exit_state="in_progress",
        )
        self.assertEqual(entry["packet_id"], "A")
        self.assertEqual(entry["event"], "started")
        self.assertEqual(entry["actor"], "dfraser")
        self.assertEqual(entry["role"], "developer")
        self.assertEqual(entry["source"], "terminal")
        self.assertEqual(entry["action"], "claim")
        self.assertEqual(entry["packet"], "A")
        self.assertEqual(entry["result"], "success")

    def test_append_mutation_log_persists_immutable_order(self):
        append_mutation_log(
            self.storage,
            packet_id="A",
            lifecycle_event="started",
            action="claim",
            actor={"user_id": "a", "role": "developer", "source": "cli"},
            result="success",
            exit_state="in_progress",
        )
        append_mutation_log(
            self.storage,
            packet_id="A",
            lifecycle_event="completed",
            action="done",
            actor={"user_id": "a", "role": "developer", "source": "cli"},
            result="success",
            exit_state="done",
        )
        state = json.loads(self.path.read_text())
        self.assertEqual([e["event"] for e in state["log"]], ["started", "completed"])

    def test_append_only_log_validator(self):
        old = [{"event": "started", "packet_id": "A"}]
        new_ok = [{"event": "started", "packet_id": "A"}, {"event": "completed", "packet_id": "A"}]
        ok, _ = validate_append_only_log(old, new_ok)
        self.assertTrue(ok)

        new_bad = [{"event": "mutated", "packet_id": "A"}]
        ok, msg = validate_append_only_log(old, new_bad)
        self.assertFalse(ok)
        self.assertIn("append-only invariant violated", msg)

    def test_provenance_snapshot_export(self):
        append_mutation_log(
            self.storage,
            packet_id="A",
            lifecycle_event="started",
            action="claim",
            actor={"user_id": "a", "role": "developer", "source": "cli"},
            result="success",
            exit_state="in_progress",
        )
        append_mutation_log(
            self.storage,
            packet_id="A",
            lifecycle_event="completed",
            action="done",
            actor={"user_id": "a", "role": "developer", "source": "cli"},
            result="success",
            exit_state="done",
        )
        state = json.loads(self.path.read_text())
        chain = provenance_chain(state, "A")
        self.assertEqual(len(chain), 2)
        snapshot = export_provenance_snapshot(state, "A")
        self.assertEqual(snapshot["packet_id"], "A")
        self.assertEqual(snapshot["event_count"], 2)


if __name__ == "__main__":
    unittest.main()
