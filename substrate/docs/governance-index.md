# Governance Index

Canonical governance and operational references for this repository.

## Constitutional Layer

- `constitution.md`
  - Invariant governance rules and conformance matrix.

## Operating Contracts

- `AGENTS.md`
  - Primary operator contract for Codex and agent-neutral execution.
- `CLAUDE.md`
  - Claude Code integration workflow under constitutional constraints.

## Governance Engine

- `.governance/wbs_cli.py`
  - Source-of-truth packet lifecycle transitions and governance commands.
- `.governance/wbs.json`
  - Packet definitions and dependency graph.
- `.governance/wbs-state.json`
  - Runtime state and immutable event log.

## Standards and Schemas

- `.governance/packet-schema.json`
  - Canonical packet schema.
- `docs/packet-schema-guide.md`
  - Field-level packet schema guidance.
- `docs/state-machine.md`
  - Formal state transition model.

## Recovery and Closeout

- `docs/PLAYBOOK.md`
  - Error recovery procedures.
- `docs/drift-assessment-template.md`
  - Required template for level-2 closeout drift assessments.
- `docs/governance-workflow-codex.md`
  - Operational lifecycle workflow for governed execution.

## Architecture and Hardening

- `docs/architecture.md`
  - Architecture decisions and runtime model.
- `docs/error-codes.md`
  - Error code taxonomy.
- `docs/logging.md`
  - Logging controls and formats.

## Agent Integration Guides

- `docs/claude-code-guide.md`
  - Claude Code usage guide.
