# Product Owner Mode

This guide is for operators who want to run delivery without diving into governance internals.

## Core Loop

1. Check project status:
```bash
python3 start.py --status
```

2. View available work:
```bash
python3 substrate/.governance/wbs_cli.py ready
```

3. Claim one packet:
```bash
python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
```

4. Ask agent to execute packet scope and validations.

5. Complete packet with evidence:
```bash
python3 substrate/.governance/wbs_cli.py done <PACKET_ID> codex "Evidence: changed files and validations" --risk none
python3 substrate/.governance/wbs_cli.py note <PACKET_ID> codex "Evidence paths: ..."
```

## Daily Commands

```bash
python3 substrate/.governance/wbs_cli.py status
python3 substrate/.governance/wbs_cli.py log 40
python3 substrate/.governance/wbs_cli.py progress
```

## If Blocked

```bash
python3 substrate/.governance/wbs_cli.py fail <PACKET_ID> codex "Blocked: <reason>; Impact: <downstream impact>"
```

## Delivery Reports

When requesting a report, ask for:
- scope covered
- completion summary by status
- per-packet details
- evidence sources
- risks/gaps and immediate next actions

## Optional PRD Ideation Mode

Use this only when you want to define requirements before creating packets.

Generate a PRD draft:
```bash
python3 substrate/.governance/wbs_cli.py prd --output substrate/docs/prd/my-feature-prd.md
```

Generate PRD + WBS draft from a JSON ideation spec:
```bash
python3 substrate/.governance/wbs_cli.py prd \
  --from-json substrate/docs/prd/spec.json \
  --output substrate/docs/prd/my-feature-prd.md \
  --to-wbs substrate/.governance/wbs-prd-draft.json
```

Then review and apply WBS when ready:
```bash
python3 substrate/.governance/wbs_cli.py plan --from-json substrate/.governance/wbs-prd-draft.json --apply
```

## Quick Bootstrap

Use `START.md` for new chat bootstrap prompt + command sequence.
