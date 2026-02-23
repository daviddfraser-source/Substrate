# Timeline/Gantt View Backlog Spec

Status: backlog specification only (no implementation in this packet)

## Objective

Define a constrained timeline/Gantt feature that visualizes packet execution history and dependency sequencing without changing core lifecycle semantics.

## Data Model Inputs

- packet definitions: `.governance/wbs.json`
- runtime state: `.governance/wbs-state.json`
- log events: `started`, `completed`, `failed`, `noted`

## Proposed View

- one row per packet
- bars from `started_at` to `completed_at`
- unresolved packets shown as open bars
- dependency links optional overlay

## Required API Contract (Future)

- endpoint: `/api/timeline`
- payload:
  - packet id/title/wbs_ref/area
  - started/completed timestamps
  - status
  - dependency ids

## UX Scope (Phase-1)

- filter by area
- filter by status
- hover details for packet lifecycle timestamps

## Non-Goals

- critical path optimization engine
- auto-scheduling/resourcing
- calendar integrations

## Risks

- missing timestamps for legacy packets
- timezone rendering ambiguity
- visual clutter on large DAGs

## Acceptance Criteria (Future Implementation)

- timeline renders from current governance state without mutating it
- packet status in timeline matches status API
- view degrades safely when timestamps are absent
