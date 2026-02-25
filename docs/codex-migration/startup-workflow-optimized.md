# Optimized Session Startup Workflow

## Goal
Reduce context reconstruction by making packet-first startup mandatory.

## Standard Flow
1. Generate session brief.
2. Inspect ready packets.
3. Claim one packet.
4. Generate packet-scoped context bundle.
5. Execute packet and record evidence.

## Commands
```bash
scripts/session-start.sh codex
scripts/session-start.sh codex <packet_id>
```

Equivalent manual path:
```bash
python3 scripts/generate-session-brief.py
python3 .governance/wbs_cli.py ready --json
python3 .governance/wbs_cli.py claim <packet_id> <agent>
python3 scripts/generate-packet-bundle.py <packet_id>
python3 .governance/wbs_cli.py context <packet_id> --format json
```

## Handoff Consistency
Use same packet-first pattern during transfer:
- `handover` from current session
- `resume` in next session
- regenerate `docs/session-brief.md` and packet bundle before execution resumes
