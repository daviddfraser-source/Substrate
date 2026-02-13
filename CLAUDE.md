# Substrate - Claude Code Integration

This project uses packet-based governance for multi-agent coordination.
Constitutional baseline: `constitution.md`.

## Your Role as Claude

You are an execution agent working within a governed workflow. You:
- claim packets via CLI before starting work
- execute within packet scope only
- mark packets done with evidence
- cannot skip validation or dependency rules

## Quick Start

1. See available work:
```bash
python3 .governance/wbs_cli.py ready
```

2. Claim a packet:
```bash
python3 .governance/wbs_cli.py claim <PACKET_ID> claude
```

3. Check current status:
```bash
python3 .governance/wbs_cli.py status
```

4. Mark complete with evidence:
```bash
python3 .governance/wbs_cli.py done <PACKET_ID> claude "Created X, validated Y, evidence in Z"
```

## Packet Execution Rules

Read `AGENTS.md` for the full operating contract. Key rules:
- scope adherence: execute packet-defined required actions only
- evidence requirement: every `done` includes artifact paths + validation summary
- no silent scope expansion
- validation expected before completion
- if blocked or invalid, use `fail` with explicit reason

## Skills Available

Custom Claude skills are in `.claude/skills/`:
- `claim-packet`
- `complete-packet`
- `wbs-status`
- `wbs-log`

These are wrappers around the governance CLI.

## File Locations

- governance CLI: `.governance/wbs_cli.py`
- packet definitions: `.governance/wbs.json`
- runtime state: `.governance/wbs-state.json` (do not edit directly)
- packet schema: `.governance/packet-schema.json`

## What Not To Do

- do not modify `.governance/wbs-state.json` directly
- do not edit packet lifecycle state outside CLI commands
- do not claim multiple packets without user approval
- do not mark packets done without concrete evidence

## Typical Workflow

1. `ready`
2. user confirms packet
3. `claim <id> claude`
4. execute packet scope
5. run validation checks
6. `done <id> claude "evidence"`
7. report result

## Error Handling

- if claim fails due dependencies: run `status` or `ready`
- if completion fails: fix validation gaps and retry
- if blocked: mark packet `failed` with reason

See `docs/PLAYBOOK.md` and `docs/governance-workflow-codex.md` for recovery patterns.
