import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.audit import AuditEntry, AuditViewer  # noqa: E402


class AuditViewerTests(unittest.TestCase):
    def _sample(self):
        return [
            AuditEntry("1", "t1", "alice", "P1", "claim", "2026-02-24T10:00:00"),
            AuditEntry("2", "t1", "bob", "P2", "done", "2026-02-24T10:05:00"),
            AuditEntry("3", "t2", "alice", "P3", "note", "2026-02-24T11:00:00"),
        ]

    def test_filters_and_pagination(self):
        viewer = AuditViewer(self._sample())
        filtered = viewer.query(tenant_id="t1")
        self.assertEqual(len(filtered), 2)
        page = viewer.paginate(filtered, page=0, page_size=1)
        self.assertEqual(len(page), 1)

    def test_export_json_and_csv(self):
        viewer = AuditViewer(self._sample())
        filtered = viewer.query(actor="alice")
        payload = viewer.export_json(filtered)
        parsed = json.loads(payload)
        self.assertEqual(len(parsed), 2)

        csv_payload = viewer.export_csv(filtered)
        self.assertIn("entry_id,tenant_id,actor,packet_id,event_type,created_at", csv_payload)
        self.assertIn("alice", csv_payload)


if __name__ == "__main__":
    unittest.main()
