from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from substrate_core.model_adapter import ModelAdapter, ModelRequest


def estimate_token_cost(prompt_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    prompt_tokens = max(1, len((prompt_text or "").split()))
    context_tokens = max(0, len(str(context or {}).split()))
    estimated_tokens = prompt_tokens + context_tokens
    return {
        "estimated_tokens": estimated_tokens,
        "prompt_tokens": prompt_tokens,
        "context_tokens": context_tokens,
    }


def validate_structured_output(output: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
    if not isinstance(output, dict):
        return False, "Model output is not an object"
    missing = [field for field in (required_fields or []) if field not in output]
    if missing:
        return False, f"Missing output fields: {', '.join(missing)}"
    return True, "ok"


def execute_agent_run(
    state: Dict[str, Any],
    *,
    adapter: ModelAdapter,
    model_name: str,
    prompt_version: Dict[str, Any],
    agent_id: str,
    task_id: str,
    actor_id: str,
    context: Dict[str, Any],
    required_output_fields: List[str],
) -> Tuple[bool, str, Dict[str, Any]]:
    if not str(agent_id or "").strip():
        return False, "agent_id is required", {}
    if not str(task_id or "").strip():
        return False, "task_id is required", {}
    if not isinstance(prompt_version, dict):
        return False, "prompt_version is required", {}

    prompt_template = str(prompt_version.get("template_text") or "").strip()
    if not prompt_template:
        return False, "prompt template text missing", {}

    estimates = estimate_token_cost(prompt_template, context)
    request = ModelRequest(
        model_name=model_name,
        prompt=prompt_template,
        context={
            **(context if isinstance(context, dict) else {}),
            "task_id": task_id,
            "agent_id": agent_id,
            "prompt_version": prompt_version.get("version_id"),
        },
    )
    response = adapter.generate(request)
    ok, msg = validate_structured_output(response.output, required_output_fields)
    status = "success" if ok else "failed"
    execution_id = f"exec-{uuid4()}"
    record = {
        "execution_id": execution_id,
        "agent_id": agent_id,
        "task_id": task_id,
        "actor_id": actor_id,
        "model_name": response.model_name,
        "prompt_id": prompt_version.get("prompt_id"),
        "prompt_version_id": prompt_version.get("version_id"),
        "tokens_input_estimated": estimates["estimated_tokens"],
        "tokens_input": response.tokens_in,
        "tokens_output": response.tokens_out,
        "cost_estimate": response.cost_estimate,
        "status": status,
        "validation_message": msg,
        "output": response.output,
        "created_at": datetime.now().isoformat(),
    }
    state.setdefault("agent_executions", []).append(record)
    return ok, msg, record


__all__ = [
    "estimate_token_cost",
    "validate_structured_output",
    "execute_agent_run",
]
