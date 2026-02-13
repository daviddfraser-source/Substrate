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

## Concurrency and Atomicity

State and definition writes use temporary files plus atomic replace semantics.

Key guarantees:
- write operations are all-or-nothing at file replacement boundary
- readers never observe partial JSON writes
- lock-aware flows are used where available to reduce concurrent mutation races

## State Machine Formalism

Packet lifecycle states:
- `pending`
- `in_progress`
- `done`
- `failed`
- `blocked`

Dependency enforcement:
- packet claim allowed only when all declared upstream dependencies are `done`
- failure can block downstream packets according to dependency graph
- completion unblocks downstream candidates

## Governance/Evolution Layers

The hardened platform layers separate policy/governance from execution mechanics:
- governance engine interfaces and state manager
- schema registry and versioning contracts
- supervisor hooks for transition authority
- deterministic execution/fingerprinting modules
- skill sandbox and permissions policy model

## API Surface

Dashboard API (`.governance/wbs_server.py`) exposes:
- read: `/api/status`, `/api/ready`, `/api/progress`, `/api/log`, `/api/packet`, `/api/file`
- lifecycle: `/api/claim`, `/api/done`, `/api/note`, `/api/fail`, `/api/reset`, `/api/closeout-l2`
- editing: `/api/add-area`, `/api/add-packet`, `/api/add-dep`, `/api/remove-dep`, `/api/edit-area`, `/api/edit-packet`, `/api/remove-packet`, `/api/save-wbs`

The CLI remains authoritative for transition semantics; API writes are adapters to CLI/engine logic.

## Rationale Summary

Design priorities are deterministic governance behavior, low operational friction, and auditable state transitions over platform complexity.
