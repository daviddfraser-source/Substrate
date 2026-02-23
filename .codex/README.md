# Codex Workspace

This folder is a Codex-first operator toolkit for this repository.

## Fast Start

```bash
python3 start.py --status
python3 substrate/.governance/wbs_cli.py briefing --format json
python3 substrate/.governance/wbs_cli.py ready
```

## Packet Lifecycle (One Packet At A Time)

```bash
python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
# implement + validate
python3 substrate/.governance/wbs_cli.py done <PACKET_ID> codex "Evidence: changed files + validations" --risk none
python3 substrate/.governance/wbs_cli.py note <PACKET_ID> codex "Evidence paths: ..."
python3 substrate/.governance/wbs_cli.py status
python3 substrate/.governance/wbs_cli.py log 40
```

## Codex Wrappers

- `.codex/scripts/codex-ready`
- `.codex/scripts/codex-claim <packet_id> [agent]`
- `.codex/scripts/codex-done <packet_id> <evidence> [none|declared] [risk-file] [agent]`
- `.codex/scripts/codex-note <packet_id> <note> [agent]`
- `.codex/scripts/codex-status`

Use `codex` as default agent, or pass an explicit agent id.

## Optional Shell Shortcuts

Bash/Zsh (session-only):

```bash
alias codex-ready='.codex/scripts/codex-ready'
alias codex-status='.codex/scripts/codex-status'
alias codex-claim='.codex/scripts/codex-claim'
alias codex-note='.codex/scripts/codex-note'
alias codex-done='.codex/scripts/codex-done'
```

PowerShell (session-only):

```powershell
function codex-ready { .\.codex\scripts\codex-ready @args }
function codex-status { .\.codex\scripts\codex-status @args }
function codex-claim { .\.codex\scripts\codex-claim @args }
function codex-note { .\.codex\scripts\codex-note @args }
function codex-done { .\.codex\scripts\codex-done @args }
```
