# Critical App Execution Checklist (IMP-001 to IMP-020)

## Completion Standard
Every packet requires:
- Output artifact in repo and linked in packet notes
- KPI impact measured or baselined
- Rollback path documented where applicable
- Owner sign-off captured in notes

## Required Lifecycle Commands
```bash
python3 .governance/wbs_cli.py claim ID agent
python3 .governance/wbs_cli.py done ID agent "summary + evidence"
python3 .governance/wbs_cli.py note ID agent "follow-up evidence"
```

## Packets

| ID | Packet | Output | Done When |
|----|--------|--------|-----------|
| 001 | Form vertical pods | `docs/pods.md` | Every workflow has one accountable pod |
| 002 | Mission-path scope | `docs/mission-path.md` | Non-critical items excluded |
| 003 | 72-hour build loop | `docs/72h-loop.md` | Median cycle follows day-1/2/3 pattern |
| 004 | Two-lane execution | Planning board | Both feature+reliability lanes active |
| 005 | Week-2 pilot policy | `docs/pilot-policy.md` | Every capability has pilot date |
| 006 | Scope cut | `docs/deferred-backlog.md` | 80% effort maps to mission path |
| 007 | Model routing | `docs/model-routing.md` | Expensive models policy-gated |
| 008 | Tool consolidation | `docs/tool-stack.md` | Duplicates removed or sunset-dated |
| 009 | Pod consolidation | Updated org map | Handoffs reduced by target % |
| 010 | Cost telemetry | `docs/cost-telemetry.md` | Cost per capability visible |
| 011 | Evidence-gated DoD | `docs/dod.md` | All transitions enforce evidence gate |
| 012 | AI role policy | `docs/ai-role-policy.md` | Human ownership explicit in workflow |
| 013 | Regression gates | `docs/release-gates.md` | Critical smoke tests mandatory |
| 014 | Accelerator templates | `templates/accelerators/` | Templates available |
| 015 | Template mandate | `docs/template-policy.md` | New work starts from template |
| 016 | Delivery KPIs | `docs/kpi-definitions.md` | Lead time, freq, MTTR tracked |
| 017 | Kill-review cadence | `docs/kill-review.md` | Low-impact work terminated |
| 018 | 90-day budget rule | `docs/budget-rule.md` | Variance triggers corrective action |
| 019 | Exec review | `docs/executive-review.md` | Blockers owner-assigned weekly |
| 020 | Target validation | `docs/target-validation.md` | 50% cost reduction demonstrated |
