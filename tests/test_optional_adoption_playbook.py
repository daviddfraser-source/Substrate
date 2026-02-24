import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalAdoptionPlaybookTests(unittest.TestCase):
    def test_playbook_contains_required_sections(self):
        path = ROOT / "docs/codex-migration/optional-adoption-playbook.md"
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        for marker in ["Migration Paths", "Operational Tradeoffs", "Rollback", "Adoption Checklist"]:
            self.assertIn(marker, content)


if __name__ == "__main__":
    unittest.main()
