# Telemetry Model and Metrics Collection

Date: 2026-02-24
Packet: PRD-5-2

## Telemetry Schema

`TelemetryEvent` fields:

- `metric_name`
- `value`
- `tenant_id`
- `project_id`
- `tags`
- `recorded_at`

## Required Metrics Coverage

Implemented required metric set in `REQUIRED_METRICS`:

- packet_cycle_time_seconds
- claim_to_completion_seconds
- blocked_state_frequency
- reopened_packet_rate
- risk_density
- agent_execution_rate
- api_latency_ms
- db_query_time_ms
- grid_render_time_ms

## Instrumentation Hooks

Implemented hooks in `Instrumentation`:

- `on_packet_transition`
- `on_api_call`
- `on_db_query`

## Query Path

`TelemetryStore.query(metric_name, tenant_id, project_id)` supports filtered retrieval used by proposal generation and operational dashboards.
