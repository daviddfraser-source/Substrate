# Operational Endpoints and Logging Contract

Date: 2026-02-24
Packet: PRD-3-3

## Implemented Endpoints

- Health endpoint contract: `health_endpoint()`
- Metrics endpoint contract: `metrics_endpoint(store)`
- Webhook event dispatcher: `WebhookDispatcher.publish()`

## Structured Logging Contract

`log_json(event_type, correlation_id, actor, details)` emits compact JSON with:

- `event_type`
- `correlation_id`
- `actor`
- `details`
- `timestamp`

This contract is suitable for downstream ingestion in log pipelines.

## Metrics Event Shape

Each metric event captures:

- `metric_name`
- `metric_value`
- `tenant_id`
- `recorded_at`

## Validation

Run:

- `python3 -m unittest tests/test_operations_endpoints.py`
