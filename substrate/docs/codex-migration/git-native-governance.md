# Git-Native Governance Contract

Status: active contract baseline for WBS `11.0` (`UPG-052` and follow-on packets).  
Implementation status: partial (protocol, auto-commit modes, linkage verification/export, and branch helpers available; rollout hardening still in progress).

## Purpose

Define deterministic semantics for treating Git as an active governance ledger while preserving compatibility with current file-based Substrate workflows.

This contract covers:
- governance object model for Git linkage
- commit protocol shape
- operating modes and fallback behavior
- failure semantics and rollback expectations

## Scope and Non-Goals

In scope:
- lifecycle transition to commit linkage for mutating operations
- machine-readable commit metadata for reconstruction
- compatibility for non-git or restricted environments

Out of scope:
- replacing WBS packet/state schemas
- replacing existing tamper-evident hash-chain logging
- introducing centralized locking infrastructure

## Git-Native Object Model

### `GitGovernanceConfig`

Location: `.governance/git-governance.json`

Required fields:
- `version`: config contract version
- `mode`: `disabled|advisory|strict`
- `auto_commit`: boolean
- `branch_per_packet`: boolean (opt-in helper workflow)
- `commit_protocol_version`: protocol version for metadata parsing

### `GovernanceCommitRecord`

Represents normalized metadata parsed from a governance commit.

Required fields:
- `protocol_version`
- `packet_id`
- `action`
- `actor`
- `event_id`
- `timestamp`
- `commit`

Optional fields:
- `branch`
- `closeout_area`
- `notes_digest`

### `LogEvent` Git Link Fields

Substrate runtime `LogEvent` remains authoritative for transition order.  
Git-native mode adds optional linkage fields:
- `git_commit`
- `git_event_id`
- `git_action`
- `git_actor`
- `git_closeout_tag`
- `git_mode`
- `git_link_status` (`linked|warning`)
- `git_link_error` (only when linkage is degraded)

## Commit Protocol Contract

Subject format:

```text
substrate(packet=<PACKET_ID>,action=<ACTION>,actor=<ACTOR>)
```

Required trailers:
- `Substrate-Protocol: 1`
- `Substrate-Event-ID: <EVENT_ID>`
- `Substrate-Packet: <PACKET_ID>`
- `Substrate-Action: <ACTION>`
- `Substrate-Actor: <ACTOR>`
- `Substrate-Timestamp: <ISO8601>`

Optional trailers:
- `Substrate-Area: <AREA_ID>`
- `Substrate-Closeout: <AREA_ID>`

CLI reference (current tooling):
- `python3 .governance/wbs_cli.py git-protocol`
- `python3 .governance/wbs_cli.py git-protocol --parse <commit-message-file>`

Parser requirements:
- strict key matching for required trailers
- deterministic normalization for casing/whitespace
- reject partial/ambiguous metadata

## Transition Semantics by Mode

Mutating operations covered:
- `claim`, `done`, `note`, `fail`, `reset`, `handover`, `resume`, `closeout-l2`

### `disabled` (default)

- No git requirement.
- Lifecycle behavior remains current baseline.
- No failure caused by missing git worktree.

### `advisory`

- Attempt git linkage when possible.
- Transition succeeds even if commit linkage fails.
- Must emit explicit warning signal (`git_link_status=warning` + actionable message).

### `strict`

- Git linkage is required for mutating transitions.
- If git preconditions fail, transition must fail with non-zero exit.
- No silent state/commit divergence is allowed.

## Non-Git Fallback Contract

If no git worktree is detected:
- `disabled`: continue silently
- `advisory`: continue with explicit warning
- `strict`: fail with actionable error:
  - "Git-native strict mode requires an active git worktree."

If repository exists but commit cannot be created (permissions, identity, conflicts):
- `disabled`: continue (no linkage attempt required)
- `advisory`: continue with warning
- `strict`: fail transition and preserve deterministic state integrity guarantees

## Failure and Recovery Semantics

Strict mode must provide transactional guarantees:
- either transition and linked commit are both recorded
- or transition is rejected with no durable state mutation

Advisory mode may proceed without commit linkage, but must:
- record linkage degradation in runtime log
- include remediation guidance in command output

## Integrity and Concurrency Position

Git-native linkage complements, not replaces:
- hash-chain lifecycle integrity (`log-mode hash-chain`, `verify-log`)
- state boundary enforcement (`governance-state-guard`)

Concurrency model:
- optimistic pull/retry on push conflicts
- explicit operator-visible failure on unresolved non-fast-forward
- no hidden auto-merge of governance state

## Closeout and Snapshot Contract

Level-2 closeout may emit deterministic tags:
- `substrate-closeout-<AREA_ID>-<YYYYMMDDHHMMSS>`

Tag semantics:
- must reference commit containing closeout transition
- must be reproducible from closeout log linkage

Reconstruction tooling:
- `python3 .governance/wbs_cli.py git-reconstruct --limit 500`
- `python3 .governance/wbs_cli.py git-reconstruct --limit 500 --output reports/git-reconstruct.json`

## Compatibility Rules

- Existing repositories must remain functional with Git-native mode disabled.
- New linkage fields are additive and optional at read boundaries.
- Consumers must ignore unknown fields.
- Breaking protocol changes require contract major version increment.
