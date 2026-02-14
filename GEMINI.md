# Substrate - Gemini CLI Integration

This project uses packet-based governance for multi-agent coordination.
Constitutional baseline: `constitution.md`.

## Your Role as Gemini

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
python3 .governance/wbs_cli.py claim <PACKET_ID> gemini
```

3. Check current status:
```bash
python3 .governance/wbs_cli.py status
```

4. Mark complete with evidence:
```bash
python3 .governance/wbs_cli.py done <PACKET_ID> gemini "Created X, validated Y, evidence in Z"
```

## Packet Execution Rules

Read `AGENTS.md` for the full operating contract. Key rules:
- scope adherence: execute packet-defined required actions only
- evidence requirement: every `done` includes artifact paths + validation summary
- no silent scope expansion
- validation expected before completion
- if blocked or invalid, use `fail` with explicit reason

## Skills Available

Custom Gemini skills are in `scripts/`:
- `gc-ready`: Check for available packets
- `gc-claim`: Claim a packet
- `gc-done`: Mark a packet as done with evidence
- `gc-status`: Check project status

These are wrappers around the governance CLI.

### Advanced Skills (Agent-Only)
- `wbs-report`: Generate a comprehensive markdown status report.
- `deep-code-review`: Perform a deep, context-aware code review of recent changes.
- `architecture-check`: Verify code changes align with documented architecture and WBS.


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
3. `claim <id> gemini`
4. execute packet scope
5. run validation checks
6. `done <id> gemini "evidence"`
7. report result

## Error Handling

- if claim fails due dependencies: run `status` or `ready`
- if completion fails: fix validation gaps and retry
- if blocked: mark packet `failed` with reason

See `docs/PLAYBOOK.md` and `docs/governance-workflow-codex.md` for recovery patterns.
