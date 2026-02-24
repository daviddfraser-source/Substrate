import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.agents import AgentRegistry  # noqa: E402


class AgentRegistryTests(unittest.TestCase):
    def test_register_issue_key_and_claim(self):
        registry = AgentRegistry(rate_limit_per_minute=5)
        agent = registry.register_agent("tenant-a", "codex-agent", "packet-executor")
        key = registry.issue_api_key("tenant-a", agent.agent_id)

        payload = registry.claim_packet_endpoint("tenant-a", key, "PRD-5-1")
        self.assertEqual(payload["action"], "claim")
        self.assertEqual(payload["agent_id"], agent.agent_id)

    def test_tenant_isolation_enforced(self):
        registry = AgentRegistry(rate_limit_per_minute=5)
        agent = registry.register_agent("tenant-a", "codex-agent", "packet-executor")
        key = registry.issue_api_key("tenant-a", agent.agent_id)
        with self.assertRaises(PermissionError):
            registry.claim_packet_endpoint("tenant-b", key, "PRD-5-1")

    def test_rate_limit_enforced(self):
        registry = AgentRegistry(rate_limit_per_minute=1)
        agent = registry.register_agent("tenant-a", "codex-agent", "packet-executor")
        key = registry.issue_api_key("tenant-a", agent.agent_id)
        registry.claim_packet_endpoint("tenant-a", key, "P1")
        with self.assertRaises(PermissionError):
            registry.claim_packet_endpoint("tenant-a", key, "P2")


if __name__ == "__main__":
    unittest.main()
