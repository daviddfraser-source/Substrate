# Substrate - Codex Integration

This project uses packet-based governance for multi-agent coordination.
Constitutional baseline: `constitution.md`.

This guide is for **all Codex model variants** (for example: Codex 5.x line, including Codex 5.3).
Model-specific tuning should be treated as additive guidance, not a replacement for governance rules.

Related agent-specific guides:
- `CLAUDE.md`
- `GEMINI.md`

## Your Role as Codex

You are an execution agent operating inside governed lifecycle controls. You:
- claim packets via CLI before execution
- execute only packet-scoped `required_actions`
- complete with concrete evidence and validation
- fail explicitly when blocked

## Quick Start

0. If this is a fresh clone, initialize scaffold:
```bash
substrate/scripts/init-scaffold.sh substrate/templates/wbs-codex-minimal.json
```

1. Bootstrap session context:
```bash
python3 substrate/.governance/wbs_cli.py briefing --format json
```

2. Check ready work:
```bash
python3 substrate/.governance/wbs_cli.py ready
```

3. Claim one packet:
```bash
python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
```

4. Load packet context:
```bash
python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
```

5. Check runtime state:
```bash
python3 substrate/.governance/wbs_cli.py status
```

6. Complete with evidence:
```bash
python3 substrate/.governance/wbs_cli.py done <PACKET_ID> codex "Changed X in Y, validated with Z" --risk none
```

## Packet Execution Rules

Read `AGENTS.md` for the full contract. Core invariants:
- execute packet scope only
- do not silently expand scope
- include artifact paths and validation evidence in completion
- run relevant checks before `done`
- use `fail` when blocked; do not fabricate completion

## Codex-Native Working Pattern

Prefer deterministic, tool-driven execution:
- use terminal commands for discovery, edits, and validation
- use fast search (`rg`) for file/content lookup
- parallelize independent reads/status checks when safe
- apply minimal diffs and keep unrelated files untouched

Recommended execution sequence:
1. `briefing` -> `ready` -> `claim`
2. inspect scope (`context`, relevant files)
3. implement scoped changes
4. validate locally
5. `done` with explicit evidence
6. `note` for supplementary evidence if needed

## Codex Tools and Practices

When running in Codex-style agent environments:
- shell execution: use non-interactive, copy-pasteable commands
- patching: prefer focused patch edits over broad rewrites
- verification: run targeted tests first, then broader checks only if required
- reporting: summarize exact file changes, validation commands, and residual risk

If tool wrappers are available (for example terminal exec, patch application, parallel reads), use them to improve determinism and traceability.

## Multi-Model Codex Guidance

Default behavior for all Codex models:
- keep prompts and notes explicit, short, and evidence-linked
- avoid hidden assumptions about scope or dependencies
- treat `wbs_cli.py` as the source of truth for packet state

Variant handling:
- higher-capacity models may produce larger plans; keep execution atomic and packet-bound
- faster/smaller variants should prefer tighter loops (small change -> validate -> record evidence)

## Codex 5.3-Specific Guidance

Use this section only when the active model is Codex 5.3.

- Prefer concise progress updates during long edits or validations.
- Favor parallel read operations for independent context gathering.
- Keep implementation diffs surgical; avoid style-only churn unless requested.
- For substantial packets, provide a short explicit plan before major edits.
- Before completion, reconcile `status` and recent `log` entries to ensure lifecycle accuracy.

These are optimization patterns, not governance overrides.

## File Locations

- governance CLI: `.governance/wbs_cli.py`
- packet definitions: `substrate/.governance/wbs.json`
- runtime state: `substrate/.governance/wbs-state.json` (do not edit directly)
- packet schema: `.governance/packet-schema.json`
- agent profiles: `.governance/agents.json`
- Codex workflow reference: `substrate/docs/governance-workflow-codex.md`

## What Not To Do

- do not modify `substrate/.governance/wbs-state.json` directly
- do not edit packet lifecycle state outside CLI commands
- do not claim multiple packets without user approval
- do not mark `done` without concrete evidence and validation context

## Error Handling

- claim blocked by dependencies: run `ready` and `status`
- completion rejected: resolve validation/evidence gaps and retry
- execution blocked: use `fail` with clear reason and dependency impact
- mid-packet transfer: use `handover`; next session uses `resume`

See `substrate/docs/PLAYBOOK.md` and `substrate/docs/governance-workflow-codex.md` for recovery workflows.

## Completion and Closeout

Per packet:
```bash
python3 substrate/.governance/wbs_cli.py done <PACKET_ID> codex "Evidence: ..." --risk none
python3 substrate/.governance/wbs_cli.py note <PACKET_ID> codex "Evidence paths: ..."
python3 substrate/.governance/wbs_cli.py status
python3 substrate/.governance/wbs_cli.py log 40
```

Level-2 closeout (when all packets in `<N.0>` are `done`):
```bash
python3 substrate/.governance/wbs_cli.py closeout-l2 <area_id|n> codex substrate/docs/codex-migration/drift-wbs<N>.md "notes"
```

Drift docs must follow `substrate/docs/drift-assessment-template.md` required sections.
