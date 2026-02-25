import copy
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.engine import PacketEngine
from substrate_core.model_adapter import ModelAdapter, ModelRequest, ModelResponse
from substrate_core.state import ActorContext
from substrate_core.storage import StorageInterface


class InMemoryStorage(StorageInterface):
    def __init__(self, state):
        self.state = copy.deepcopy(state)

    def read_state(self):
        return copy.deepcopy(self.state)

    def write_state(self, state):
        self.state = copy.deepcopy(state)

    def append_audit(self, entry):
        self.state.setdefault("log", []).append(copy.deepcopy(entry))
        return entry


class BrokenAdapter(ModelAdapter):
    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            model_name=request.model_name,
            output={"task_id": "missing-required-fields"},
            tokens_in=1,
            tokens_out=1,
            cost_estimate=0.0,
            raw_text="{}",
        )


class RuntimeTests(unittest.TestCase):
    def _definition(self):
        return {"packets": [{"id": "A", "title": "A"}], "dependencies": {}}

    def _state(self):
        return {
            "packets": {
                "A": {
                    "status": "pending",
                    "assigned_to": None,
                    "started_at": None,
                    "completed_at": None,
                    "notes": None,
                }
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

    def test_prompt_registry_activation_flow(self):
        engine, storage, actor = self._engine()
        reg = engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        self.assertTrue(reg.ok)

        act = engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        self.assertTrue(act.ok)
        self.assertEqual(
            storage.state["prompt_registry"]["prompts"]["chat.summary"]["active_version"],
            "1.0",
        )

    def test_execute_agent_task_with_active_prompt(self):
        engine, storage, actor = self._engine()
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1000, run_cap=500, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        result = engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-1",
            prompt_id="chat.summary",
            actor=actor,
            requested_tools=["filesystem.read"],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["execution"]["status"], "success")
        self.assertEqual(result.payload["execution"]["prompt_version_id"], "1.0")
        self.assertTrue(storage.state.get("agent_executions"))
        self.assertTrue(storage.state.get("ai_events"))
        event = storage.state["ai_events"][-1]
        for key in (
            "actor_id",
            "agent_id",
            "prompt_version",
            "model_version",
            "tokens_in",
            "tokens_out",
            "policy_result",
            "constraint_result",
            "cost_estimate",
            "timestamp",
        ):
            self.assertIn(key, event)

    def test_execute_agent_task_rejects_invalid_output(self):
        engine, _storage, actor = self._engine()
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1000, run_cap=500, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        result = engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-2",
            prompt_id="chat.summary",
            actor=actor,
            adapter=BrokenAdapter(),
            requested_tools=["filesystem.read"],
        )
        self.assertFalse(result.ok)
        self.assertIn("Missing output fields", result.message)

    def test_execute_agent_task_denied_by_budget(self):
        engine, _storage, actor = self._engine()
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1, run_cap=1, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="This prompt intentionally exceeds tiny budget caps.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Budget test prompt",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        result = engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-3",
            prompt_id="chat.summary",
            actor=actor,
            requested_tools=["filesystem.read"],
        )
        self.assertFalse(result.ok)
        self.assertIn("exceed", result.message.lower())

    def test_execute_agent_task_records_scoped_retrieval_trace(self):
        engine, storage, actor = self._engine()
        state = storage.read_state()
        state["relationships"] = [{"source_entity_id": "E-1", "target_entity_id": "E-2"}]
        state["documents"] = [
            {"id": "D-1", "entity_id": "E-1", "content": "alpha bravo charlie"},
            {"id": "D-2", "entity_id": "E-2", "content": "delta echo foxtrot"},
            {"id": "D-3", "entity_id": "E-9", "content": "outside scope"},
        ]
        storage.write_state(state)
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1000, run_cap=500, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        result = engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-4",
            prompt_id="chat.summary",
            actor=actor,
            scope_entity_id="E-1",
            retrieval_depth=1,
            retrieval_max_chunks=5,
            retrieval_max_tokens=200,
            requested_tools=["filesystem.read"],
        )
        self.assertTrue(result.ok)
        trace = result.payload["execution"].get("retrieval_trace", {})
        self.assertEqual(trace.get("scope_entity_id"), "E-1")
        self.assertGreaterEqual(trace.get("retrieved_count", 0), 1)

    def test_observability_metrics_snapshot(self):
        engine, _storage, actor = self._engine()
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1000, run_cap=500, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-5",
            prompt_id="chat.summary",
            actor=actor,
            requested_tools=["filesystem.read"],
        )
        metrics = engine.observability_metrics()
        self.assertTrue(metrics.ok)
        self.assertGreaterEqual(metrics.payload.get("event_count", 0), 1)
        burns = metrics.payload.get("token_burn_per_agent", {})
        self.assertIn("agent-1", burns)

    def test_execute_agent_task_denied_when_tool_not_allowed(self):
        engine, _storage, actor = self._engine()
        engine.register_agent_profile(
            agent_id="agent-1",
            owner="platform",
            capabilities=["execute"],
            allowed_tools=["filesystem.read"],
            allowed_models=["deterministic-echo-v1"],
            actor=actor,
        )
        engine.configure_agent_budget(agent_id="agent-1", daily_cap=1000, run_cap=500, actor=actor)
        engine.register_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            template_text="Summarize packet state.",
            owner="platform",
            model_compatibility=["deterministic-echo-v1"],
            actor=actor,
            rationale="Initial prompt baseline",
        )
        engine.activate_prompt_version(
            prompt_id="chat.summary",
            version_id="1.0",
            actor=actor,
            approvals=["gov-lead"],
            rationale="Approved for runtime use",
        )
        result = engine.execute_agent_task(
            agent_id="agent-1",
            task_id="task-6",
            prompt_id="chat.summary",
            actor=actor,
            requested_tools=["filesystem.write"],
        )
        self.assertFalse(result.ok)
        self.assertIn("Tool access denied", result.message)


if __name__ == "__main__":
    unittest.main()
