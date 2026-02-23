# State Machine Specification

## States

- `pending`
- `in_progress`
- `done`
- `failed`
- `blocked`

## Valid Transitions

| From | Action | To | Constraint |
|---|---|---|---|
| `pending` | `claim` | `in_progress` | all dependencies must be `done` |
| `in_progress` | `done` | `done` | actor must match assignment |
| `in_progress` | `fail` | `failed` | failure reason should be recorded |
| `in_progress` | `reset` | `pending` | explicit operator action |

## Derived/Propagation Behavior

- downstream packets may remain `pending` until dependency conditions are met
- on failure, downstream can be set to `blocked` depending on dependency chain
- completion of upstream packet can make downstream packet claimable

## Invalid Transitions (examples)

- `pending` -> `done` without claim
- `done` -> `in_progress`
- `failed` -> `done` without reset/rework flow
- claim when dependencies are unresolved

## Atomicity and Safety

- state mutations use temp-file write plus atomic replace
- lock-aware mutation paths are used where available
- transition checks and write operations are coupled in the governing command path

## Operator Checks

- `python3 .governance/wbs_cli.py ready`
- `python3 .governance/wbs_cli.py status`
- `python3 .governance/wbs_cli.py log 40`
