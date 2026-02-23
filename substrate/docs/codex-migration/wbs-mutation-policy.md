# WBS Mutation Control Policy

## Purpose
Prevent unauthorized replacement of active WBS definitions and enforce auditable approval for governance-structure changes.

## Protected Artifacts
- Active WBS definition for the selected project (`wbs.json`)
- Project runtime state (`wbs-state.json`) when changed by structural migration/apply operations
- Governance mutation controls (`.governance/current-project.json`, mutation policy config)

## Mutation Classes
- Low-risk lifecycle mutations:
  - `claim`, `done`, `note`, `fail`, `resume`, `handover`, log/risk/break-fix operations
  - These do not require WBS structural approval.
- High-risk structural mutations:
  - `init` when source differs from active WBS
  - `add-area`, `add-packet`, `add-dep`, `remove`
  - draft apply operations and project switch operations
  - These require explicit approval token.

## Approval Requirements
- Mode: `strict` by default.
- Required token format: `WBS-APPROVED:<ticket-or-change-id>`.
- Token can be provided via:
  - CLI flag: `--wbs-approval <token>`
  - Environment variable: `WBS_CHANGE_APPROVAL=<token>`
- In `strict` mode, missing/invalid approval blocks mutation.
- In `advisory` mode, mutation proceeds with warning.
- In `disabled` mode, mutation proceeds without approval checks.

## Commit Governance
- Commits touching protected WBS/governance files must include trailer:
  - `WBS-Change-Approved: <ticket-or-change-id>`
- Recommended companion trailer:
  - `WBS-Project: <project-id>`

## Draft Apply Workflow
- Agents create/update draft WBS (`wbs.draft.json`).
- Active WBS changes only via explicit `draft-apply` command with approval token.
- `draft-apply` logs actor, project, source draft path, and approval reference.

## Project Isolation
- A selected active project sits above WBS.
- Each project has isolated artifacts:
  - `wbs.json`, `wbs-state.json`, break-fix/e2e/risk stores
- Structural operations apply only to active project context.

## Rejection Conditions
- Invalid approval token format.
- Missing approval in strict mode for structural mutation.
- Attempt to mutate unknown/non-active project without explicit selection.
- Draft apply from missing/invalid JSON source.

## Audit Expectations
- Every approved structural mutation should leave:
  - lifecycle log evidence (`note` with changed files + validation)
  - commit metadata trailer (`WBS-Change-Approved`)
  - project context (`WBS-Project`)
