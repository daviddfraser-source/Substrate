import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "codex-migration" / "briefing-context-schema.md"


class BriefingContextContractTests(unittest.TestCase):
    def test_contract_doc_exists(self):
        self.assertTrue(DOC.exists())

    def test_json_examples_are_parseable_and_have_required_keys(self):
        text = DOC.read_text()
        blocks = re.findall(r"```json\r?\n(.*?)\r?\n```", text, flags=re.DOTALL)
        self.assertGreaterEqual(len(blocks), 2)

        briefing = json.loads(blocks[0])
        context = json.loads(blocks[1])

        briefing_required = {
            "schema_id",
            "schema_version",
            "generated_at",
            "mode",
            "truncated",
            "limits",
            "project",
            "counts",
            "ready_packets",
            "blocked_packets",
            "active_assignments",
            "recent_events",
        }
        context_required = {
            "schema_id",
            "schema_version",
            "generated_at",
            "mode",
            "truncated",
            "limits",
            "packet_id",
            "packet_definition",
            "runtime_state",
            "dependencies",
            "history",
            "handovers",
            "file_manifest",
            "truncation",
        }

        self.assertTrue(briefing_required.issubset(set(briefing.keys())))
        self.assertTrue(context_required.issubset(set(context.keys())))
        self.assertEqual(briefing["schema_id"], "wbs.briefing")
        self.assertEqual(context["schema_id"], "wbs.context_bundle")


if __name__ == "__main__":
    unittest.main()
