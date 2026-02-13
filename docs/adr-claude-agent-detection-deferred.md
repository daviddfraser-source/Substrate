# ADR: Defer Caller Auto-Detection in CLI

## Status
Accepted

## Context

A proposal suggested adding automatic caller detection (Claude/Codex/human) in `.governance/wbs_cli.py` and changing output format based on detected caller.

## Decision

Do not implement caller auto-detection or implicit output-mode switching at this stage.

## Rationale

- preserves agent-agnostic deterministic CLI behavior
- avoids hidden behavior changes based on environment variables
- keeps integrations explicit through existing `--json` contract
- simplifies testability and operator predictability

## Consequences

- integrations must pass explicit agent names and output flags
- no special-case logic for Claude Code in lifecycle engine
- future reconsideration requires explicit contract + tests
