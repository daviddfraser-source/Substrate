# Optional App Scaffold Profile Specification

Date: 2026-02-24
Packet: PRD-7-1

## Objective

Allow adopters to use Substrate core governance services without requiring the full app scaffold UI package.

## Profile Model

Two deployment profiles are defined:

- `core-governance`
- `full-scaffold`

`core-governance` is the safe baseline profile for teams that only need governance APIs and lifecycle tooling.

## Feature Toggles

Required toggles for deterministic behavior:

- `SUBSTRATE_PROFILE=core-governance|full-scaffold`
- `ENABLE_APP_SCAFFOLD_UI=true|false`
- `ENABLE_DEP_GRAPH_UI=true|false`
- `ENABLE_RISK_HEATMAP_UI=true|false`
- `ENABLE_EXTENSION_PANELS=true|false`

### Toggle Rules

- If `SUBSTRATE_PROFILE=core-governance`, UI toggles default to `false`.
- If `SUBSTRATE_PROFILE=full-scaffold`, UI toggles default to `true`.
- Explicit toggle values always override profile defaults.
- Invalid values fail startup validation (no silent fallback).

## Mandatory vs Optional Boundary

Mandatory in all profiles:

- Governance lifecycle CLI/API
- Authentication and RBAC enforcement
- Audit/event logging
- Packet/dependency/risk data models and APIs
- Health and metrics endpoints

Optional in `core-governance`:

- Full app-shell UI packaging
- Optional dashboard extension panels
- High-interaction scaffold modules

## Non-Blocking Constraint

Optional modules must not be hard dependencies for:

- packet lifecycle transitions (`claim`, `done`, `note`, `fail`, `reset`)
- API governance endpoints
- release closeout workflows

## Validation Scenarios

Minimum checks to prove determinism:

1. Start with `SUBSTRATE_PROFILE=core-governance` and confirm governance CLI/API functions with UI toggles disabled.
2. Start with `SUBSTRATE_PROFILE=full-scaffold` and confirm optional UI modules initialize.
3. Start with explicit overrides and confirm override precedence.
4. Start with invalid profile/toggle values and confirm startup fails with explicit errors.

## Adoption Guidance

Recommended rollout path:

1. Begin with `core-governance` in regulated or API-first environments.
2. Enable optional modules incrementally by explicit toggles.
3. Move to `full-scaffold` only when UI modules are needed and validated.

