# observability-baseline Skill Operation

## Run
```bash
./skills/observability-baseline/scripts/smoke.sh
./skills/observability-baseline/scripts/run.sh
```

## Outputs
- `docs/codex-migration/skills/observability-report.md`
- `docs/codex-migration/skills/observability-events.json`

## Validation
- Confirm sample includes lifecycle event fields:
  - `packet_id`
  - `event`
  - `timestamp`
