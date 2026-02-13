# Shared Skill Contract

## Required Repository Layout
- `skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/README.md`
- `skills/<skill-name>/scripts/run.sh`
- `skills/<skill-name>/scripts/smoke.sh`
- Optional: `skills/<skill-name>/assets/`

## Required `SKILL.md` Sections
- `Purpose`
- `Inputs`
- `Outputs`
- `Preconditions`
- `Workflow`
- `Commands`
- `Failure Modes and Fallbacks`
- `Validation`
- `Evidence Notes Template`
- `References`

## Command Contract
- `run.sh`: executes the skill’s primary workflow.
- `smoke.sh`: fast verification (non-destructive) for tool wiring.
- Both scripts must exit non-zero on failure.

## Evidence Contract
- Each skill must emit at least one artifact path for packet evidence.
- Artifact path(s) must be included in packet completion notes.

## Governance Contract
- Use explicit commands; avoid assistant-specific slash aliases.
- Keep skill output deterministic where possible.
- Prefer machine-readable outputs (`json`, `sarif`, `junit`, or plain markdown tables).
