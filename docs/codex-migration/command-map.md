# Command Mapping Matrix (Claude -> Codex)

| Intent | Claude Style | Codex / CLI Style |
|---|---|---|
| Status | `/wbs-status` | `python3 .governance/wbs_cli.py status` |
| Ready work | `/wbs-status` (ready view) | `python3 .governance/wbs_cli.py ready` |
| Claim packet | `/claim-packet <id> <agent>` | `python3 .governance/wbs_cli.py claim <id> <agent>` |
| Complete packet | `/complete-packet <id> <agent> done "notes"` | `python3 .governance/wbs_cli.py done <id> <agent> "notes"` |
| Fail packet | `/complete-packet <id> <agent> failed "reason"` | `python3 .governance/wbs_cli.py fail <id> <agent> "reason"` |
| Add notes | n/a | `python3 .governance/wbs_cli.py note <id> <agent> "notes"` |
| Reset in-progress | `/reset-packet <id>` | `python3 .governance/wbs_cli.py reset <id>` |
| Level-2 closeout | n/a | `python3 .governance/wbs_cli.py closeout-l2 <area_id|n> <agent> <drift_assessment.md> [notes]` |
| Recent log | `/wbs-log` | `python3 .governance/wbs_cli.py log 20` |
| Progress summary | `/wbs-report` | `python3 .governance/wbs_cli.py progress` |

## Guidance
- Use CLI commands as the source of truth.
- Use `--json` for automation output.
