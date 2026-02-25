import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.policy import (  # noqa: E402
    activate_policy_version,
    evaluate_policy,
    evaluate_policy_with_opa,
    register_policy_version,
)
from substrate_core.state import ActorContext  # noqa: E402


class PolicyTests(unittest.TestCase):
    def _state(self):
        return {
            "packets": {
                "A": {"status": "pending"},
            }
        }

    def test_no_policy_config_allows(self):
        decision = evaluate_policy({}, packet_id="A", actor=ActorContext("u", "developer", "api"), transition="claim", state=self._state())
        self.assertTrue(decision.allow)

    def test_missing_policy_version_fails_closed(self):
        definition = {"policy": {"rules": []}}
        decision = evaluate_policy(definition, packet_id="A", actor=ActorContext("u", "developer", "api"), transition="claim", state=self._state())
        self.assertFalse(decision.allow)
        self.assertIn("Missing policy version", decision.message)

    def test_higher_precedence_deny_wins(self):
        definition = {
            "policy": {
                "version": "1.0",
                "rules": [
                    {
                        "id": "gov-allow-dev-claim",
                        "domain": "governance",
                        "type": "role",
                        "effect": "allow",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    },
                    {
                        "id": "const-deny-dev-claim",
                        "domain": "constitutional",
                        "type": "role",
                        "effect": "deny",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    },
                ],
            }
        }
        decision = evaluate_policy(
            definition,
            packet_id="A",
            actor=ActorContext("u", "developer", "api"),
            transition="claim",
            state=self._state(),
        )
        self.assertFalse(decision.allow)
        self.assertIn("Denied by policy rule", decision.message)

    def test_policy_registry_activation_flow(self):
        state = self._state()
        actor = ActorContext("u", "governance-admin", "api")
        ok, msg = register_policy_version(
            state,
            version_id="2.0",
            policy={"rules": []},
            actor=actor,
            rationale="Initial governance package",
        )
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

        ok, msg = activate_policy_version(
            state,
            version_id="2.0",
            actor=actor,
            approvals=["security-lead"],
            rationale="Approved for activation",
        )
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")
        self.assertEqual(state["policy_registry"]["active_version"], "2.0")

    def test_policy_version_requires_rationale_and_approval(self):
        state = self._state()
        actor = ActorContext("u", "governance-admin", "api")
        ok, _ = register_policy_version(
            state,
            version_id="2.1",
            policy={"rules": []},
            actor=actor,
            rationale="draft",
        )
        self.assertTrue(ok)
        ok, msg = activate_policy_version(
            state,
            version_id="2.1",
            actor=actor,
            approvals=[],
            rationale="",
        )
        self.assertFalse(ok)
        self.assertIn("rationale", msg)

    def test_opa_optional_fallback_to_native(self):
        definition = {
            "policy": {
                "version": "3.0",
                "opa": {"enabled": True, "mode": "optional"},
                "rules": [
                    {
                        "id": "allow-dev-claim",
                        "domain": "governance",
                        "type": "role",
                        "effect": "allow",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    }
                ],
            }
        }
        decision = evaluate_policy_with_opa(
            definition,
            packet_id="A",
            actor=ActorContext("u", "developer", "api"),
            transition="claim",
            state=self._state(),
        )
        self.assertTrue(decision.allow)

    def test_opa_required_denies_when_unavailable(self):
        definition = {
            "policy": {
                "version": "3.1",
                "opa": {"enabled": True, "mode": "required"},
                "rules": [
                    {
                        "id": "allow-dev-claim",
                        "domain": "governance",
                        "type": "role",
                        "effect": "allow",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    }
                ],
            }
        }
        decision = evaluate_policy_with_opa(
            definition,
            packet_id="A",
            actor=ActorContext("u", "developer", "api"),
            transition="claim",
            state=self._state(),
        )
        self.assertFalse(decision.allow)
        self.assertIn("OPA decision unavailable", decision.message)


if __name__ == "__main__":
    unittest.main()
