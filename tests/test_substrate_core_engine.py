import copy
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.engine import PacketEngine
from substrate_core.state import ActorContext
from substrate_core.storage import StorageInterface


class InMemoryStorage(StorageInterface):
    def __init__(self, state):
        self.state = copy.deepcopy(state)
        self.writes = 0

    def read_state(self):
        return copy.deepcopy(self.state)

    def write_state(self, state):
        self.state = copy.deepcopy(state)
        self.writes += 1

    def append_audit(self, entry):
        self.state.setdefault("log", []).append(copy.deepcopy(entry))
        self.writes += 1
        return entry


class PacketEngineTests(unittest.TestCase):
    def _definition(self):
        return {
            "packets": [
                {"id": "A", "title": "A"},
                {"id": "B", "title": "B"},
            ],
            "dependencies": {"B": ["A"]},
        }

    def _state(self):
        return {
            "packets": {
                "A": {"status": "pending", "assigned_to": None, "started_at": None, "completed_at": None, "notes": None},
                "B": {"status": "pending", "assigned_to": None, "started_at": None, "completed_at": None, "notes": None},
            },
            "log": [],
            "area_closeouts": {},
            "log_integrity_mode": "plain",
        }

    def _engine(self):
        storage = InMemoryStorage(self._state())
        engine = PacketEngine(storage=storage, definition=self._definition())
        actor = ActorContext(user_id="dev", role="developer", source="api")
        return engine, storage, actor

    def test_valid_claim_transition(self):
        engine, storage, actor = self._engine()
        result = engine.claim("A", actor)
        self.assertTrue(result.ok)
        self.assertEqual(storage.state["packets"]["A"]["status"], "in_progress")
        self.assertGreaterEqual(storage.writes, 1)

    def test_invalid_claim_transition(self):
        engine, storage, actor = self._engine()
        engine.claim("A", actor)
        again = engine.claim("A", actor)
        self.assertFalse(again.ok)
        self.assertIn("not pending", again.message)

    def test_dependency_violation(self):
        engine, _storage, actor = self._engine()
        result = engine.claim("B", actor)
        self.assertFalse(result.ok)
        self.assertIn("Blocked by A", result.message)

    def test_invalid_state_move_done_requires_in_progress(self):
        engine, _storage, actor = self._engine()
        result = engine.done("A", actor, "done")
        self.assertFalse(result.ok)
        self.assertIn("not in_progress", result.message)

    def test_audit_entry_creation(self):
        engine, storage, actor = self._engine()
        engine.claim("A", actor)
        log = storage.state.get("log", [])
        self.assertEqual(len(log), 1)
        entry = log[0]
        self.assertEqual(entry["event"], "started")
        self.assertEqual(entry["action"], "claim")
        self.assertEqual(entry["actor"], "dev")
        self.assertEqual(entry["source"], "api")

    def test_storage_write_on_note(self):
        engine, storage, actor = self._engine()
        before = storage.writes
        result = engine.note("A", "evidence", actor)
        self.assertTrue(result.ok)
        self.assertGreater(storage.writes, before)

    def test_validate_state(self):
        engine, _storage, _actor = self._engine()
        result = engine.validate()
        self.assertTrue(result.ok)

    def test_claim_rejects_invalid_ontology_dependency(self):
        definition = {
            "packets": [
                {"id": "A", "title": "A", "entity_type": "Risk"},
                {"id": "B", "title": "B", "entity_type": "Packet"},
            ],
            "dependencies": {"B": ["A"]},
        }
        storage = InMemoryStorage(self._state())
        engine = PacketEngine(storage=storage, definition=definition)
        actor = ActorContext(user_id="dev", role="developer", source="api")

        result = engine.claim("B", actor)
        self.assertFalse(result.ok)
        self.assertIn("Invalid relationship", result.message)

    def test_claim_rejects_by_policy_rule(self):
        definition = {
            "packets": [
                {"id": "A", "title": "A"},
                {"id": "B", "title": "B"},
            ],
            "dependencies": {"B": ["A"]},
            "policy": {
                "version": "1.0",
                "rules": [
                    {
                        "id": "deny-dev-claim",
                        "domain": "constitutional",
                        "type": "role",
                        "effect": "deny",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    }
                ],
            },
        }
        state = self._state()
        state["packets"]["A"]["status"] = "done"
        storage = InMemoryStorage(state)
        engine = PacketEngine(storage=storage, definition=definition)
        actor = ActorContext(user_id="dev", role="developer", source="api")

        result = engine.claim("B", actor)
        self.assertFalse(result.ok)
        self.assertIn("Denied by policy rule", result.message)

    def test_graph_queries(self):
        engine, _storage, _actor = self._engine()
        up = engine.upstream("B")
        self.assertTrue(up.ok)
        self.assertEqual(up.payload["upstream"], ["A"])

        down = engine.downstream("A")
        self.assertTrue(down.ok)
        self.assertEqual(down.payload["downstream"], ["B"])

        cp = engine.critical_path()
        self.assertTrue(cp.ok)
        self.assertEqual(cp.payload["critical_path"], ["A", "B"])

        q = engine.postgres_query_templates()
        self.assertTrue(q.ok)
        self.assertIn("upstream", q.payload["queries"])

    def test_snapshot_and_diff(self):
        engine, _storage, actor = self._engine()
        snap1 = engine.snapshot("s1", actor)
        self.assertTrue(snap1.ok)
        engine.claim("A", actor)
        engine.done("A", actor, "done")
        snap2 = engine.snapshot("s2", actor)
        self.assertTrue(snap2.ok)

        diff = engine.diff("s1", "s2")
        self.assertTrue(diff.ok)
        self.assertEqual(diff.payload["change_count"], 1)
        self.assertEqual(diff.payload["changes"][0]["packet_id"], "A")

    def test_register_and_activate_policy_version(self):
        engine, storage, actor = self._engine()
        reg = engine.register_policy_version(
            version_id="2.0",
            policy={
                "version": "2.0",
                "rules": [
                    {
                        "id": "allow-developer-claim",
                        "domain": "governance",
                        "type": "role",
                        "effect": "allow",
                        "match": {"roles": ["developer"], "transition": "claim"},
                    }
                ],
            },
            actor=actor,
            rationale="New policy package",
        )
        self.assertTrue(reg.ok)

        act = engine.activate_policy_version(
            version_id="2.0",
            actor=actor,
            approvals=["security-lead"],
            rationale="Approval complete",
        )
        self.assertTrue(act.ok)
        self.assertEqual(storage.state["policy_registry"]["active_version"], "2.0")

    def test_claim_fails_when_opa_required_without_decision(self):
        definition = {
            "packets": [
                {"id": "A", "title": "A"},
            ],
            "dependencies": {},
            "policy": {
                "version": "3.0",
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
            },
        }
        storage = InMemoryStorage(self._state())
        engine = PacketEngine(storage=storage, definition=definition)
        actor = ActorContext(user_id="dev", role="developer", source="api")
        result = engine.claim("A", actor)
        self.assertFalse(result.ok)
        self.assertIn("OPA decision unavailable", result.message)

    def test_register_and_score_trust_model(self):
        engine, _storage, actor = self._engine()
        reg = engine.register_trust_model(
            version_id="1.0",
            weights={"quality": 0.5, "policy": 0.5},
            actor=actor,
            rationale="Initial trust baseline",
            approvals=["security-lead"],
        )
        self.assertTrue(reg.ok)
        score = engine.score_trust({"quality": 0.8, "policy": 0.7})
        self.assertTrue(score.ok)
        self.assertEqual(score.payload["model_version"], "1.0")


if __name__ == "__main__":
    unittest.main()
