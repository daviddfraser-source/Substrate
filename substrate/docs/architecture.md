# Architecture

## Overview

This repository implements a file-backed governance layer for packetized work execution. The architecture is intentionally simple so state is inspectable, mergeable, and easy to audit in normal repository workflows.

Constitutional governance rules for this architecture are defined in `constitution.md`.

## Core Components

- `.governance/wbs.json`
  - Work areas, packets, and dependency graph definition.
- `.governance/wbs-state.json`
  - Runtime packet lifecycle state and activity log.
- `.governance/wbs_cli.py`
  - Source-of-truth lifecycle operations (`claim`, `done`, `fail`, `reset`, `closeout-l2`, etc.).
- `.governance/wbs_server.py`
  - Dashboard/API adapter over the same state and definition.
- `src/governed_platform/`
  - Governance/execution hardening modules (engine, supervisor, schema registry, determinism, skills sandbox).

## Data Model Strategy

File-based JSON state was chosen for:
- Git-friendly diffs and history
- Low operational overhead
- Explicit, inspectable governance records
- No external database dependency for baseline usage

Tradeoff:
- Less suited for high-write distributed workloads than a dedicated transactional store.

## Object Model

Governance behavior is implemented across four distinct objects:

- `PacketDefinition`
  - Source: `.governance/wbs.json` packet entries.
  - Purpose: planned work contract (scope, ownership intent, dependencies, validation intent).
  - Lifecycle field semantics: packet-definition `status` values follow schema enum semantics (`DRAFT|PENDING|IN_PROGRESS|BLOCKED|DONE|FAILED`).
- `RuntimeState`
  - Source: `.governance/wbs-state.json` packet state map.
  - Purpose: execution truth used by claim/done/fail/reset transitions.
  - Lifecycle field semantics: canonical runtime values are lowercase (`pending|in_progress|done|failed|blocked`).
- `LogEvent`
  - Source: append records under `.governance/wbs-state.json` `log`.
  - Purpose: immutable-by-behavior lifecycle history (event, agent, timestamp, notes).
  - Optional integrity fields when hash-chain mode is enabled: `event_id`, `prev_hash`, `hash`.
- `AreaCloseout`
  - Source: `.governance/wbs-state.json` `area_closeouts`.
  - Purpose: Level-2 closeout record with drift assessment path and closure metadata.

## Concurrency and Atomicity

State and definition writes use cross-platform lock files plus temporary-file atomic replace semantics.

Key guarantees:
- write operations are all-or-nothing at file replacement boundary
- readers never observe partial JSON writes
- lock acquisition is explicit and deterministic on Linux/Windows (`<target>.lock`)
- stale lock recovery is best-effort via lock age checks

## State Machine Formalism

Packet lifecycle states:
- `pending`
- `in_progress`
- `done`
- `failed`
- `blocked`

## Status Contract and Boundary Normalization

Canonical contract:
- Runtime state is lowercase (`pending|in_progress|done|failed|blocked`).
- Packet-definition schema may use uppercase enum values for definition-time validation.

Boundary rule:
- Any input crossing schema/API/CLI boundaries must be normalized to canonical runtime form before transition checks.
- Normalization must be deterministic and case-insensitive (`DONE`, `done`, `Done` -> `done`).
- Invalid status values must fail fast in strict validation flows instead of silently drifting.

Dependency enforcement:
- packet claim allowed only when all declared upstream dependencies are `done`
- failure can block downstream packets according to dependency graph
- completion unblocks downstream candidates

## Briefing and Context Output Contracts

Session bootstrap and handover-oriented read models are governed by versioned output contracts:

- `wbs.briefing` (`schema_version` `1.0`)
- `wbs.context_bundle` (`schema_version` `1.0`)

Contract authority:
- `docs/codex-migration/briefing-context-schema.md`

Rules:
- every payload includes a common envelope (`schema_id`, `schema_version`, `generated_at`, `mode`, `limits`, `truncated`)
- JSON key semantics are contract-stable across minor versions
- size controls and truncation metadata are explicit so context-window behavior remains deterministic

## Git-Native Governance Contract (Planned)

Git-native governance is defined as a versioned contract in:
- `docs/codex-migration/git-native-governance.md`

Contract position:
- Git linkage is additive to existing state/log model.
- Runtime state (`.governance/wbs-state.json`) remains transition authority.
- Git commit metadata and event linkage provide traceability and reconstruction capability.

Planned operating modes:
- `disabled`: legacy behavior, no git requirement
- `advisory`: best-effort git linkage with explicit warnings on failure
- `strict`: transition requires valid git linkage and fails on unmet preconditions

Compatibility requirement:
- repositories without an active git worktree must continue functioning in `disabled` mode.

## Governance/Evolution Layers

The hardened platform layers separate policy/governance from execution mechanics:
- governance engine interfaces and state manager
- schema registry and versioning contracts
- supervisor hooks for transition authority
- deterministic execution/fingerprinting modules
- skill sandbox and permissions policy model

## API Surface

Dashboard API (`.governance/wbs_server.py`) exposes:
- read: `/api/status`, `/api/ready`, `/api/progress`, `/api/log`, `/api/packet`, `/api/file`, `/api/docs-index`
- lifecycle: `/api/claim`, `/api/done`, `/api/note`, `/api/fail`, `/api/reset`, `/api/closeout-l2`
- editing: `/api/add-area`, `/api/add-packet`, `/api/add-dep`, `/api/remove-dep`, `/api/edit-area`, `/api/edit-packet`, `/api/remove-packet`, `/api/save-wbs`

The CLI remains authoritative for transition semantics; API writes are adapters to CLI/engine logic.

## Rationale Summary

Design priorities are deterministic governance behavior, low operational friction, and auditable state transitions over platform complexity.
