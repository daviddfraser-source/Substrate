# Trust Scoring v1 Contract

## Model

Trust score is a deterministic weighted aggregation over bounded `[0, 1]` signals.

`score = sum(weight_i * signal_i) / sum(weight_i)`

Signals are clamped to `[0, 1]`. Weights are non-negative.

## Governance Controls

- Every trust model is versioned (`version_id`).
- Registration requires:
  - rationale text
  - approval identities
- Active model is tracked in `state["trust_registry"]["active_model"]`.
- Scoring output includes:
  - `model_version`
  - `score`
  - per-signal contribution breakdown
  - rationale

## Core APIs

- `PacketEngine.register_trust_model(...)`
- `PacketEngine.score_trust(signals)`
- `substrate_core.trust.compute_trust_score(...)`

## Determinism

For identical model weights and signals, score and contribution outputs are byte-stable.
