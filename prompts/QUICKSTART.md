# 2-Minute Quickstart (CLI-First)

```bash
# 1) Start from a template
python3 .governance/wbs_cli.py init templates/wbs-feature.json

# 2) Find ready packets
python3 .governance/wbs_cli.py ready

# 3) Claim one packet
python3 .governance/wbs_cli.py claim PACKET-ID your-agent

# 4) Complete with evidence
python3 .governance/wbs_cli.py done PACKET-ID your-agent "Implemented X; evidence: docs/file.md"

# 5) Update note later (optional)
python3 .governance/wbs_cli.py note PACKET-ID your-agent "Added validation evidence: logs/output.txt"
```

## Quick Reference

| Command | Purpose |
|---|---|
| `ready` | Show claimable packets |
| `claim ID AGENT` | Reserve packet |
| `done ID AGENT "notes"` | Mark complete |
| `note ID AGENT "notes"` | Update notes/evidence |
| `fail ID AGENT "reason"` | Mark failed |
| `status` | Full project state |
| `log 20` | Recent lifecycle events |
