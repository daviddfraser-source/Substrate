# observability-baseline

## Purpose
Establish packet lifecycle telemetry conventions and baseline artifacts using OpenTelemetry-compatible event structures.

## Inputs
- Packet lifecycle events from `.governance/wbs-state.json` log.

## Outputs
- Event schema: `skills/observability-baseline/assets/event-schema.json`
- Collector config: `skills/observability-baseline/assets/otel-collector.yaml`
- Baseline report: `docs/codex-migration/skills/observability-report.md`
- Sample events: `docs/codex-migration/skills/observability-events.json`

## Preconditions
- Python 3 available.

## Workflow
1. Validate event schema and source log availability.
2. Extract sample lifecycle events.
3. Write baseline telemetry report.

## Commands
```bash
./skills/observability-baseline/scripts/smoke.sh
./skills/observability-baseline/scripts/run.sh
```

## Failure Modes and Fallbacks
- Missing state log: fail and require WBS initialization.
- Missing events: produce empty sample with warning in report.

## Validation
- Report and events artifacts exist.
- Events include core fields (`packet_id`, `event`, `timestamp`).

## Evidence Notes Template
`Evidence: docs/codex-migration/skills/observability-report.md, docs/codex-migration/skills/observability-events.json`

## References
- https://opentelemetry.io/docs/collector/
