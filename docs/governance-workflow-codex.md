# Codex Governance Workflow

Constitutional constraints are defined in `constitution.md`. This workflow document is operational guidance that must remain consistent with that constitution.

## Session Start

1. Check ready scope:
   - `python3 .governance/wbs_cli.py ready`
2. Inspect current state:
   - `python3 .governance/wbs_cli.py status`
3. Claim one packet:
   - `python3 .governance/wbs_cli.py claim <packet_id> <agent>`

## Execution

1. Implement only packet-scoped work.
2. Record evidence paths in notes:
   - `python3 .governance/wbs_cli.py note <packet_id> <agent> "Evidence: ..."`
3. Validate changes (tests/lint/contracts) before completion.

## Completion

1. Mark done with evidence summary:
   - `python3 .governance/wbs_cli.py done <packet_id> <agent> "Evidence: ..."`
2. Reconcile status/log:
   - `python3 .governance/wbs_cli.py status`
   - `python3 .governance/wbs_cli.py log 40`

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
