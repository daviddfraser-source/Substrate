import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
CHECKLIST = ROOT / "docs" / "release-checklist-codex.md"


class GitCiGovernanceTests(unittest.TestCase):
    def test_workflow_includes_git_native_governance_checks(self):
        text = WORKFLOW.read_text()
        self.assertIn("Git-native governance protocol checks", text)
        self.assertIn("python3 .governance/wbs_cli.py git-protocol --json", text)
        self.assertIn("python3 .governance/wbs_cli.py --json git-verify-ledger --strict", text)

    def test_release_checklist_includes_git_native_evidence_commands(self):
        text = CHECKLIST.read_text()
        self.assertIn("Git-native governance checks captured", text)
        self.assertIn("python3 .governance/wbs_cli.py git-protocol --json", text)
        self.assertIn("python3 .governance/wbs_cli.py --json git-verify-ledger --strict", text)


if __name__ == "__main__":
    unittest.main()
