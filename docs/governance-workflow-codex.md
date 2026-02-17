# Codex Governance Workflow

Constitutional constraints are defined in `constitution.md`. This workflow document is operational guidance that must remain consistent with that constitution.

## Session Start

0. Use the versioned briefing/context contract as the session read-model baseline:
   - `docs/codex-migration/briefing-context-schema.md`
1. Check ready scope:
   - `python3 .governance/wbs_cli.py ready`
2. Inspect current state:
   - `python3 .governance/wbs_cli.py status`
3. Claim one packet:
   - `python3 .governance/wbs_cli.py claim <packet_id> <agent>`
4. Inspect packet context bundle before execution:
   - `python3 .governance/wbs_cli.py context <packet_id> --format json --max-events 40 --max-notes-bytes 4000`

## Execution

1. Implement only packet-scoped work.
2. Record evidence paths in notes:
   - `python3 .governance/wbs_cli.py note <packet_id> <agent> "Evidence: ..."`
3. Validate changes (tests/lint/contracts) before completion.

## Session Continuity

If a session must hand off mid-packet:

1. Create handover record:
   - `python3 .governance/wbs_cli.py handover <packet_id> <agent> "<reason>" --to <next_agent> --remaining "item1|item2"`
2. Resume from the next session:
   - `python3 .governance/wbs_cli.py resume <packet_id> <next_agent>`

Invariant expectations:
- packet remains `in_progress` during handover
- only one active handover per packet is allowed
- `resume` atomically assigns packet ownership to the resuming agent

## Completion

1. Mark done with evidence summary:
   - `python3 .governance/wbs_cli.py done <packet_id> <agent> "Evidence: ..."`
2. Reconcile status/log:
   - `python3 .governance/wbs_cli.py status`
   - `python3 .governance/wbs_cli.py log 40`

## Runtime State Guard

Repository automation blocks direct commits to `.governance/wbs-state.json` by default.

Preferred path:
- use CLI lifecycle transitions so state changes are generated through governance commands.

Emergency/manual correction override:
- include commit message token: `[allow-wbs-state-edit]`
- or set local env var for one-off bypass: `ALLOW_WBS_STATE_EDIT=1`

## Agent Capability Profiles

Claim-time capability checks are configured in `.governance/agents.json`.

Useful commands:
- `python3 .governance/wbs_cli.py agent-list`
- `python3 .governance/wbs_cli.py agent-mode <disabled|advisory|strict>`
- `python3 .governance/wbs_cli.py agent-register <id> <type> <cap1,cap2,...>`

Modes:
- `disabled`: no capability checks
- `advisory`: warn on mismatch but allow claim
- `strict`: reject mismatched claims

## Guided Planning

Generate WBS definitions through planner flow instead of hand-editing:
- `python3 .governance/wbs_cli.py plan --from-json planner-spec.json --output .governance/wbs-draft.json`
- `python3 .governance/wbs_cli.py plan --apply` (interactive)

Experimental markdown import:
- `python3 .governance/wbs_cli.py plan --import-markdown docs/project-proposal.md --output .governance/wbs-imported.json`
- ambiguous imports are blocked from `--apply` unless `--allow-ambiguous` is set.

## Rollout Operations

Reference: `docs/codex-migration/enhancement-rollout.md`

Minimum weekly operations:
1. Run KPI evidence commands from rollout doc.
2. Review `capability_warning` events in `.governance/wbs-state.json`.
3. Confirm planner-generated WBS files still pass:
   - `python3 .governance/wbs_cli.py validate`
4. Record residual risk and next action in weekly operator notes.

## Git-Native Governance

Contract authority:
- `docs/codex-migration/git-native-governance.md`
- rollout playbook: `docs/codex-migration/git-native-rollout.md`

Mode semantics:
- `disabled`: current baseline behavior
- `advisory`: transition proceeds with warning when commit linkage fails
- `strict`: transition fails when commit linkage cannot be established

Primary operator commands:
- `python3 .governance/wbs_cli.py git-governance`
- `python3 .governance/wbs_cli.py git-governance-mode <disabled|advisory|strict>`
- `python3 .governance/wbs_cli.py git-governance-autocommit <on|off>`
- `python3 .governance/wbs_cli.py --json git-verify-ledger --strict`
- `python3 .governance/wbs_cli.py git-reconstruct --limit 500 --output reports/git-reconstruct.json`

Rollout sequence:
1. Start with `disabled`.
2. Enable `advisory` + `auto-commit on`, monitor warning rate.
3. Promote to `strict` only after strict ledger verification passes.
4. Use rollback commands from `git-native-rollout.md` if strict/advisory behavior degrades operations.

Opt-in branch-per-packet helper workflow (when git worktree is available):
- `python3 .governance/wbs_cli.py git-branch-open <packet_id> <agent> [--from ref]`
- `python3 .governance/wbs_cli.py git-branch-close <packet_id> <agent> [--base main] [--keep-branch]`

Guardrails:
- branch-open requires packet to be `in_progress` and assigned to the requesting agent.
- branch-close requires ownership consistency with packet assignment.
- workflow is optional and does not replace lifecycle transitions.

## Level-2 Closeout (Required)

When all packets in `<N.0>` are done:

```bash
python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> docs/codex-migration/drift-wbs<N>.md "notes"
```

Drift doc must include all required sections listed in `docs/drift-assessment-template.md`.

## Delivery Reporting

When asked for a delivery report, include:
- scope covered
- completion summary by status
- per-packet lines (id/title/owner/start/completion/notes)
- evidence sources (`.governance/wbs-state.json` + log entries)
- risks/gaps + immediate next actions
