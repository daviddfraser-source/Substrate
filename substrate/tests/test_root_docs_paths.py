import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


class RootDocPathConsistencyTests(unittest.TestCase):
    def test_root_docs_use_substrate_governance_paths(self):
        docs = [
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "codex.md",
            "START.md",
        ]
        forbidden_patterns = [
            r"python3\s+\.governance/wbs_cli\.py",
            r"(?<!substrate/)\.governance/wbs-state\.json",
            r"(?<!substrate/)scripts/init-scaffold\.sh\s+templates/",
            r"(?<!substrate/)scripts/reset-scaffold\.sh\s+templates/",
        ]

        for doc in docs:
            text = read(doc)
            for pattern in forbidden_patterns:
                self.assertIsNone(
                    re.search(pattern, text),
                    f"{doc} contains legacy path matching: {pattern}",
                )

    def test_start_has_bootstrap_sequence(self):
        text = read("START.md")
        required = [
            "python3 substrate/.governance/wbs_cli.py briefing --format json",
            "python3 substrate/.governance/wbs_cli.py ready",
            "python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex",
            "python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000",
        ]
        for line in required:
            self.assertIn(line, text)


if __name__ == "__main__":
    unittest.main()
