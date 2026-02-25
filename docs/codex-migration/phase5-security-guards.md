# Phase 5 Runtime Security Guards

Implemented for packet `P5-05-AI-SECURITY-GUARDS`.

## Delivered Components

- `src/substrate_core/security.py`
  - agent profile registry (capabilities, allowed tools, allowed models, owner, trust baseline)
  - execution guard validation for actor identity, model allow-list, and tool allow-list

- `src/substrate_core/engine.py`
  - `register_agent_profile(...)`
  - `execute_agent_task(...)` now enforces guard validation before prompt/budget/runtime processing

## Guard Rules

1. Actor identity must be present.
2. Agent profile must exist.
3. Requested model must be allowed for the agent profile.
4. Requested tools must be a subset of allowed tools.

## Validation Coverage

- `tests/test_substrate_core_runtime.py`
  - normal guarded execution with explicit profile
  - denial when unauthorized tool is requested
