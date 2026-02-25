# Phase 5 Agent Runtime and Prompt Governance

Implemented for packet `P5-02-AGENT-LLM-PROMPT-RUNTIME`.

## Delivered Components

- `src/substrate_core/model_adapter.py`
  - model adapter interface
  - deterministic echo adapter for governed baseline execution

- `src/substrate_core/prompt.py`
  - prompt version registration
  - prompt activation with approval requirements
  - active prompt resolution for runtime execution

- `src/substrate_core/runtime.py`
  - deterministic token/cost estimation
  - structured output validation
  - governed agent execution record generation

- `src/substrate_core/engine.py`
  - `register_prompt_version(...)`
  - `activate_prompt_version(...)`
  - `execute_agent_task(...)`

## Execution Flow

1. Register prompt version (`draft`).
2. Activate prompt version with approvals (`active`).
3. Execute agent task with active prompt and model adapter.
4. Validate structured output.
5. Persist execution record and lifecycle log event.

## Validation Coverage

- `tests/test_substrate_core_runtime.py`
  - prompt registry activation flow
  - successful governed execution path
  - structured output validation failure path
