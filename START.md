# Start Here (Bootstrap)

Use this file to start a new Codex chat quickly under this governance model.

## 1) Paste This Bootstrap Prompt

```text
You are operating in this repository.

Follow governance strictly:
1) Read constitution.md and AGENTS.md first.
2) Treat constitution.md as invariant authority; AGENTS.md as operational contract.
3) Use CLI-governed lifecycle only via python3 substrate/.governance/wbs_cli.py.
4) Run:
   - python3 substrate/.governance/wbs_cli.py briefing --format json
   - python3 substrate/.governance/wbs_cli.py ready
5) Claim only one packet unless I explicitly approve parallel work.
6) After claiming, load context:
   - python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
7) Before done/fail, report planned validation commands.
8) Completion must include: what changed, file paths, validation evidence, and risk ack.
9) Never edit runtime governance state directly; no direct edits to substrate/.governance/wbs-state.json.
```

## 2) Run This Command Sequence

```bash
./bootstrap.sh
python3 start.py --status
python3 substrate/.governance/wbs_cli.py briefing --format json
python3 substrate/.governance/wbs_cli.py ready
python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
```

Task shortcut alternative:

```bash
make bootstrap
```

## 3) Fresh Clone Initialization

```bash
substrate/scripts/init-scaffold.sh substrate/templates/wbs-codex-minimal.json
python3 substrate/.governance/wbs_cli.py ready
```

Optional post-clone cleanup profile:

```bash
substrate/scripts/post-clone-cleanup.sh --profile codex-only --yes
```

## Optional: Codex Convenience Wrappers

```bash
.codex/scripts/codex-ready
.codex/scripts/codex-status
.codex/scripts/codex-claim <PACKET_ID>
.codex/scripts/codex-done <PACKET_ID> "Evidence: ..."
```

## Optional: Break-Fix Quick Flow

```bash
python3 substrate/.governance/wbs_cli.py break-fix-open codex "Fix flaky suite" "Intermittent timeout" --severity high --packet <PACKET_ID>
python3 substrate/.governance/wbs_cli.py break-fix-start <BFIX_ID> codex
python3 substrate/.governance/wbs_cli.py break-fix-resolve <BFIX_ID> codex "Applied timeout + retry fix" --evidence substrate/tests/test_server_api.py
python3 substrate/.governance/wbs_cli.py break-fix-list --status open
```

Operator guide: `substrate/docs/break-fix-workflow.md`

## Optional: PRD Ideation Quick Flow

```bash
python3 substrate/.governance/wbs_cli.py prd --output substrate/docs/prd/my-feature-prd.md
python3 substrate/.governance/wbs_cli.py prd --from-json substrate/docs/prd/spec.json --output substrate/docs/prd/my-feature-prd.md --to-wbs substrate/.governance/wbs-prd-draft.json
```
