import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WbsGridContractTests(unittest.TestCase):
    def test_required_ui_module_files_exist(self):
        required = [
            ROOT / "app/src/ui/wbsGridTypes.ts",
            ROOT / "app/src/ui/wbsGridConfig.ts",
            ROOT / "app/src/ui/wbsGridActions.ts",
            ROOT / "app/src/ui/wbsTreeGrid.ts",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")

    def test_edit_controls_and_bulk_actions_declared(self):
        content = (ROOT / "app/src/ui/wbsGridActions.ts").read_text(encoding="utf-8")
        self.assertIn("unauthorized_edit", content)
        self.assertIn("applyBulkAction", content)

    def test_status_heatmap_declared(self):
        content = (ROOT / "app/src/ui/wbsGridConfig.ts").read_text(encoding="utf-8")
        for status in ["pending", "in_progress", "done", "failed", "blocked"]:
            self.assertIn(status, content)


if __name__ == "__main__":
    unittest.main()
