# 2-Minute Quickstart (Clone -> First Claim)

Run from repo root:

```bash
# 1) Initialize state from a template
python3 .governance/wbs_cli.py init templates/wbs-feature.json

# 2) See claimable work
python3 .governance/wbs_cli.py ready

# 3) Claim your first packet
python3 .governance/wbs_cli.py claim PACKET-ID your-agent
```

Optional next step after you finish work:

```bash
python3 .governance/wbs_cli.py done PACKET-ID your-agent "Changed <files>; evidence: <paths>"
```
