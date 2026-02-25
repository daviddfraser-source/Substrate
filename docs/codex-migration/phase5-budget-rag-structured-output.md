# Phase 5 Budget, Scoped RAG, and Structured Output

Implemented for packet `P5-03-BUDGET-RAG-STRUCTURED-OUTPUT`.

## Delivered Components

- `src/substrate_core/budget.py`
  - agent budget configuration
  - pre-run budget checks
  - post-run token consumption ledger
  - remaining budget view

- `src/substrate_core/rag.py`
  - entity-scoped retrieval via relationship depth traversal
  - chunk/token caps
  - retrieval trace logging

- `src/substrate_core/engine.py`
  - `configure_agent_budget(...)`
  - budget-aware `execute_agent_task(...)`
  - optional scoped retrieval integration and retrieval traces in execution records

## Runtime Guard Sequence

1. Resolve active prompt version.
2. Run optional scoped retrieval with limits.
3. Estimate tokens for execution context.
4. Check budget caps before model call.
5. Execute model adapter and validate structured output.
6. Consume actual token budget and append ledger entry.
7. Persist execution record with budget and retrieval trace metadata.

## Validation Coverage

- `tests/test_substrate_core_runtime.py`
  - budget-deny path
  - successful budgeted execution
  - scoped retrieval trace path
  - structured output validation failure path
