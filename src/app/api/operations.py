import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MetricEvent:
    metric_name: str
    metric_value: float
    tenant_id: Optional[str]
    recorded_at: float


@dataclass
class TraceEvent:
    trace_id: str
    span_id: str
    name: str
    status: str
    started_at: float
    ended_at: Optional[float]
    attributes: Dict[str, Any]


class MetricsStore:
    def __init__(self):
        self._events: List[MetricEvent] = []

    def record(self, metric_name: str, metric_value: float, tenant_id: Optional[str] = None) -> MetricEvent:
        event = MetricEvent(metric_name=metric_name, metric_value=float(metric_value), tenant_id=tenant_id, recorded_at=time.time())
        self._events.append(event)
        return event

    def list_events(self, metric_name: str = "") -> List[MetricEvent]:
        if metric_name:
            return [event for event in self._events if event.metric_name == metric_name]
        return list(self._events)


class WebhookDispatcher:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def publish(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_type": event_type,
            "payload": payload,
            "delivered_at": time.time(),
        }
        self._events.append(event)
        return event

    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)


class TraceStore:
    def __init__(self):
        self._events: Dict[str, TraceEvent] = {}

    def start_span(self, trace_id: str, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> TraceEvent:
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            name=name,
            status="running",
            started_at=time.time(),
            ended_at=None,
            attributes=attributes or {},
        )
        self._events[span_id] = event
        return event

    def finish_span(self, span_id: str, status: str = "ok", attributes: Optional[Dict[str, Any]] = None) -> Optional[TraceEvent]:
        event = self._events.get(span_id)
        if event is None:
            return None
        event.status = status
        event.ended_at = time.time()
        if attributes:
            event.attributes.update(attributes)
        return event

    def events(self, trace_id: str = "") -> List[TraceEvent]:
        rows = list(self._events.values())
        if trace_id:
            rows = [event for event in rows if event.trace_id == trace_id]
        return sorted(rows, key=lambda e: (e.started_at, e.span_id))


def health_endpoint(checks: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    checks = checks or {"runtime": True}
    status = "ok" if all(checks.values()) else "degraded"
    return {
        "status": status,
        "timestamp": time.time(),
        "checks": checks,
    }


def liveness_endpoint() -> Dict[str, Any]:
    return {"status": "alive", "timestamp": time.time()}


def readiness_endpoint(checks: Dict[str, bool]) -> Dict[str, Any]:
    return health_endpoint(checks)


def metrics_endpoint(store: MetricsStore) -> Dict[str, Any]:
    events = store.list_events()
    grouped: Dict[str, int] = {}
    for event in events:
        grouped[event.metric_name] = grouped.get(event.metric_name, 0) + 1
    return {
        "count": len(events),
        "series": grouped,
        "events": [
            {
                "metric_name": event.metric_name,
                "metric_value": event.metric_value,
                "tenant_id": event.tenant_id,
                "recorded_at": event.recorded_at,
            }
            for event in events
        ],
    }


def traces_endpoint(store: TraceStore, trace_id: str = "") -> Dict[str, Any]:
    events = store.events(trace_id=trace_id)
    return {
        "count": len(events),
        "events": [
            {
                "trace_id": event.trace_id,
                "span_id": event.span_id,
                "name": event.name,
                "status": event.status,
                "started_at": event.started_at,
                "ended_at": event.ended_at,
                "attributes": event.attributes,
            }
            for event in events
        ],
    }


def log_json(
    event_type: str,
    correlation_id: str,
    actor: str,
    details: Dict[str, Any],
    severity: str = "INFO",
    trace_id: str = "",
) -> str:
    payload = {
        "event_type": event_type,
        "correlation_id": correlation_id,
        "actor": actor,
        "severity": severity.upper(),
        "trace_id": trace_id or None,
        "details": details,
        "timestamp": time.time(),
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
