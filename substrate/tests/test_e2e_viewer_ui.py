import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / '.governance' / 'static' / 'index.html'


class E2EViewerUiTests(unittest.TestCase):
    def test_static_index_contains_e2e_viewer_controls(self):
        text = INDEX.read_text(encoding='utf-8')
        self.assertIn("showE2ERuns()", text)
        self.assertIn("modal-e2e-runs", text)
        self.assertIn("/api/e2e/runs", text)
        self.assertIn("/api/e2e/run", text)
        self.assertIn("e2e-findings", text)


if __name__ == '__main__':
    unittest.main()
