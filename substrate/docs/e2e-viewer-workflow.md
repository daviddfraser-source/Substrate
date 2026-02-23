# E2E Viewer Workflow

This document describes how E2E test runs are captured and surfaced in the WBS dashboard.

## Data Contract

Runtime store:
- `substrate/.governance/e2e-runs.json`

Schema:
- `substrate/.governance/e2e-runs.schema.json`

Each run records:
- run identity (`run_id`, `timestamp`, `agent`, `packet_id`, `trigger`, `suite`)
- execution result (`status`, `duration_sec`, `command`, `exit_code`)
- summary counts (`passed`, `failed`, `skipped`, `total`)
- findings list (`test_id`, `message`, `file`, `snippet`)
- artifact references (for example run logs)

## Capture Runs

Use the writer script:

```bash
python3 substrate/scripts/e2e-run.py \
  --suite governance-viewer-smoke \
  --trigger local \
  --agent codex \
  --packet-id E2E-6-5 \
  --cmd "python3 -m unittest substrate/tests/test_root_docs_paths.py -v"
```

## API Endpoints

- `GET /api/e2e/runs?limit=200&status=pass&suite=...&packet_id=...`
- `GET /api/e2e/run?id=<run_id>`

Server implementation:
- `substrate/.governance/wbs_server.py`

## Viewer UX

Open dashboard and click `E2E Runs`.

UI file:
- `substrate/.governance/static/index.html`

The modal displays:
- run history list
- status/suite filters
- selected run JSON
- findings panel
- artifact links with preview support

## CI/Local Integration

Local quality gates call `substrate/scripts/e2e-run.py`.

CI (`.github/workflows/test.yml`):
- runs quality gates
- uploads `substrate/.governance/e2e-runs.json` and `substrate/reports/e2e/*.log` as artifacts

## Governance Evidence Flow

Recommended packet completion evidence:
1. E2E run command used
2. `run_id`
3. `e2e-runs.json` path
4. log artifact path under `substrate/reports/e2e/`
