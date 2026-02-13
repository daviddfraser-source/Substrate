# Supervisor Enforcement in Lifecycle Transitions

The compatibility CLI now routes lifecycle mutations through `GovernanceEngine`, which enforces supervisor approval before state changes.

## Enforced Actions
- `claim`
- `done`
- `note`
- `fail`
- `closeout-l2`

## Current Deterministic Policy
- Mutating actions require `agent`.
- `done` requires non-empty completion notes.

## Operator Impact
- Empty-note completion attempts are rejected.
- Rejections return explicit supervisor denial reasons.
