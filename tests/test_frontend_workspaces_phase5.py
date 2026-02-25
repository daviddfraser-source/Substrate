import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrontendWorkspacesPhase5Tests(unittest.TestCase):
    def test_core_ai_workspaces_exist(self):
        expected = {
            "templates/ai-substrate/app/chat/page.tsx": "Governed Chat",
            "templates/ai-substrate/app/assistant/page.tsx": "RAG Assistant",
            "templates/ai-substrate/app/prompt-lab/page.tsx": "Prompt Lab",
            "templates/ai-substrate/app/agent-console/page.tsx": "Agent Console",
        }
        for rel, marker in expected.items():
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            self.assertIn(marker, path.read_text(encoding="utf-8"))

    def test_ops_workspaces_exist(self):
        expected = {
            "templates/ai-substrate/app/documents/page.tsx": "Document Management",
            "templates/ai-substrate/app/kanban/page.tsx": "Kanban and Gantt",
            "templates/ai-substrate/app/timeline/page.tsx": "Timeline Viewer",
            "templates/ai-substrate/app/approvals/page.tsx": "Approvals",
            "templates/ai-substrate/app/knowledge/page.tsx": "Knowledge Base",
            "templates/ai-substrate/app/risks/page.tsx": "Risk Register",
        }
        for rel, marker in expected.items():
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            self.assertIn(marker, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
