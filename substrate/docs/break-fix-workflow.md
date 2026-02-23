# Break-Fix Workflow

This guide describes the minor-issue break-fix mode and how to keep a complete, auditable history.

## Data Contract

Break-fix records are persisted in:
- `substrate/.governance/break-fix-log.json`
- schema: `substrate/.governance/break-fix-log.schema.json`

Core fields:
- lifecycle: `open -> in_progress -> resolved|rejected`
- severity: `low|medium|high|critical`
- ownership/timestamps: `created_by`, `owner`, `created_at`, `started_at`, `resolved_at`, `rejected_at`, `updated_at`
- packet linkage: `packet_id`, `linked_packets`
- evidence chain: `findings[]`, `evidence[]`, `notes[]`, `history[]`

Resolve guard:
- `resolve` requires at least one evidence path.

## CLI Lifecycle

Open:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-open codex "Fix flaky test" "Timeout in API smoke" --severity high --packet E2E-6-4
```

Start:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-start BFIX-0001 codex --owner codex
```

Add note/findings/evidence:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-note BFIX-0001 codex "Reproduced in CI" --evidence substrate/reports/e2e/e2e-123.log --findings "Timeout after 5s|Only on cold start"
```

Resolve (evidence required):
```bash
python3 substrate/.governance/wbs_cli.py break-fix-resolve BFIX-0001 codex "Increased timeout and retry window" --evidence substrate/.governance/wbs_server.py,substrate/tests/test_server_api.py
```

Reject:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-reject BFIX-0001 codex "Duplicate of BFIX-0002"
```

Inspect:
```bash
python3 substrate/.governance/wbs_cli.py break-fix-list --status open --limit 50
python3 substrate/.governance/wbs_cli.py break-fix-show BFIX-0001
```

## API Endpoints

Read:
- `GET /api/break-fix/items`
- `GET /api/break-fix/item?id=<BFIX-ID>`
- `GET /api/break-fix/summary`

Write:
- `POST /api/break-fix/open`
- `POST /api/break-fix/start`
- `POST /api/break-fix/resolve`
- `POST /api/break-fix/reject`
- `POST /api/break-fix/note`

## Viewer Workflow

Use the **Break-Fix** button in the WBS dashboard:
- filter queue by status/severity/packet
- create a break-fix item
- execute lifecycle transitions
- inspect linked packets, findings, and evidence

Packet and status views surface unresolved break-fix counts (`open` + `in_progress`).

## Reporting and Exports

`status` and `briefing` include break-fix summaries:
```bash
python3 substrate/.governance/wbs_cli.py --json status
python3 substrate/.governance/wbs_cli.py --json briefing
```

Export records for delivery reports:
```bash
python3 substrate/.governance/wbs_cli.py export break-fix-json substrate/reports/break-fix/latest.json
```

## Evidence Chain Expectations

For every resolved item:
- include reproducer context in `notes`
- include concrete verification artifacts in `evidence`
- include user-visible impact in `resolution_summary`

This ensures closeout and delivery reporting can trace:
- what changed
- why it changed
- where validation evidence lives
