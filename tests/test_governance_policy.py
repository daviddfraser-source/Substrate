import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text()


class GovernancePolicyTests(unittest.TestCase):
    def test_agents_has_required_contract_sections(self):
        text = read("AGENTS.md")
        required_sections = [
            "## WBS Execution Rules",
            "## Required Delivery Reporting",
            "## Closeout Expectations",
            "## Execution Discipline (Latest Practice)",
            "## Anti-Drift Controls",
            "## Validation and Evals",
            "## Decision and Escalation Rules",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_agents_has_required_commands(self):
        text = read("AGENTS.md")
        self.assertIn("python3 .governance/wbs_cli.py closeout-l2", text)
        self.assertIn(".governance/packet-schema.json", text)




if __name__ == "__main__":
    unittest.main()
