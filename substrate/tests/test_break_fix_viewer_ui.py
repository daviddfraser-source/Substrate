import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / '.governance' / 'static' / 'index.html'


class BreakFixViewerUiTests(unittest.TestCase):
    def test_static_index_contains_break_fix_controls(self):
        text = INDEX.read_text(encoding='utf-8')
        self.assertIn("showBreakFixPanel()", text)
        self.assertIn("modal-break-fix", text)
        self.assertIn("/api/break-fix/open", text)
        self.assertIn("/api/break-fix/resolve", text)
        self.assertIn("bf-findings", text)


if __name__ == '__main__':
    unittest.main()
