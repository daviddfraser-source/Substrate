import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrontendFoundationPhase5Tests(unittest.TestCase):
    def test_layout_navigation_and_shell(self):
        content = (ROOT / "templates/ai-substrate/app/layout.tsx").read_text(encoding="utf-8")
        self.assertIn("sidebarCollapsed", content)
        self.assertIn("Main navigation", content)
        self.assertIn("CommandPalette", content)

    def test_workspace_view_supports_all_modes(self):
        content = (ROOT / "templates/ai-substrate/components/governance/WorkspaceView.tsx").read_text(encoding="utf-8")
        for mode in ["table", "kanban", "tree", "graph"]:
            self.assertIn(mode, content)

    def test_api_client_uses_post_for_mutations(self):
        content = (ROOT / "templates/ai-substrate/lib/governance/api-client.ts").read_text(encoding="utf-8")
        self.assertIn("async function post", content)
        self.assertIn("claimPacket", content)
        self.assertIn("completePacket", content)
        self.assertIn("addNote", content)


if __name__ == "__main__":
    unittest.main()
