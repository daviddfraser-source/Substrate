from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ModelRequest:
    model_name: str
    prompt: str
    context: Dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    model_name: str
    output: Dict[str, Any]
    tokens_in: int
    tokens_out: int
    cost_estimate: float
    raw_text: str


class ModelAdapter:
    """Abstract model adapter interface for governed runtime execution."""

    def generate(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError


class DeterministicEchoAdapter(ModelAdapter):
    """
    Deterministic adapter used for governed execution tests.
    It echoes a structured payload and computes deterministic token/cost estimates.
    """

    def __init__(self, model_name: str = "deterministic-echo-v1"):
        self.model_name = model_name

    def generate(self, request: ModelRequest) -> ModelResponse:
        prompt = request.prompt or ""
        context = request.context if isinstance(request.context, dict) else {}
        input_tokens = max(1, len(prompt.split()))
        output = {
            "summary": f"Executed {context.get('task_id', 'task')}",
            "task_id": context.get("task_id"),
            "agent_id": context.get("agent_id"),
            "prompt_version": context.get("prompt_version"),
            "model_name": request.model_name or self.model_name,
        }
        raw_text = str(output)
        output_tokens = max(1, len(raw_text.split()))
        cost_estimate = round((input_tokens + output_tokens) * 0.000001, 8)
        return ModelResponse(
            model_name=request.model_name or self.model_name,
            output=output,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            cost_estimate=cost_estimate,
            raw_text=raw_text,
        )


__all__ = [
    "ModelAdapter",
    "ModelRequest",
    "ModelResponse",
    "DeterministicEchoAdapter",
]
