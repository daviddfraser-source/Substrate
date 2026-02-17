# Error Recovery Playbook (JSON State)

This playbook implements recovery procedures under `constitution.md`.

## Agent Stuck (in progress too long)
```bash
python3 .governance/wbs_cli.py stale 30
python3 .governance/wbs_cli.py reset ID
```

## Wrong Work Done
- Revert code changes using normal git workflow.
- Update packet evidence or corrective notes:
```bash
python3 .governance/wbs_cli.py note ID agent "Correction details + evidence"
```
- If rework is required, open a follow-up packet.

## Dependency Failed
```bash
python3 .governance/wbs_cli.py fail ID agent "Failure reason"
python3 .governance/wbs_cli.py status
```
Lead decides retry strategy and when to clear/rework.

## Re-initialize from Definition
```bash
scripts/reset-scaffold.sh templates/wbs-codex-minimal.json
# or direct CLI path:
python3 .governance/wbs_cli.py init .governance/wbs.json
```

## State File Integrity
```bash
python3 -m json.tool .governance/wbs-state.json >/dev/null
python3 -m json.tool .governance/wbs.json >/dev/null
```

## Session Crash Recovery
```bash
python3 .governance/wbs_cli.py status
python3 .governance/wbs_cli.py log 30
```
Reconcile packet notes with actual file changes before continuing.
