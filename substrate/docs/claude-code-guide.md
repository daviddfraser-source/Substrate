# Using Substrate With Claude Code

Constitutional governance authority for this workflow is `constitution.md`.

## Initial Setup

1. Open project in Claude Code.
2. Claude reads `CLAUDE.md` at startup.
3. Ask for available work:
```bash
python3 .governance/wbs_cli.py ready
```

## Typical Workflow

### Start Work

1. identify packet:
```bash
scripts/cc-ready
```
2. claim packet:
```bash
scripts/cc-claim <PACKET_ID>
```
3. inspect scope:
```bash
python3 .governance/wbs_cli.py scope <PACKET_ID>
```

### Execute

- implement within packet scope
- run validation checks
- collect file-path evidence

### Complete

```bash
scripts/cc-done <PACKET_ID> "Evidence: files + validation results"
```

## Tips

- be explicit about scope boundaries
- request evidence summary before marking done
- use status/log frequently:
```bash
scripts/cc-status
python3 .governance/wbs_cli.py log 30
```

## Troubleshooting

- dependencies not met: run `ready` and complete upstream packets
- packet already claimed: check `status` and coordinate reassignment
- missing evidence quality: include exact paths and validation commands

## Multi-Claude Coordination

Use distinct agent names when needed (`claude-1`, `claude-2`) and coordinate assignment through a human lead.
