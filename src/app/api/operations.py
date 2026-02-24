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


def health_endpoint() -> Dict[str, Any]:
    return {
        "status": "ok",
        "timestamp": time.time(),
    }


def metrics_endpoint(store: MetricsStore) -> Dict[str, Any]:
    return {
        "count": len(store.list_events()),
        "events": [
            {
                "metric_name": event.metric_name,
                "metric_value": event.metric_value,
                "tenant_id": event.tenant_id,
                "recorded_at": event.recorded_at,
            }
            for event in store.list_events()
        ],
    }


def log_json(event_type: str, correlation_id: str, actor: str, details: Dict[str, Any]) -> str:
    payload = {
        "event_type": event_type,
        "correlation_id": correlation_id,
        "actor": actor,
        "details": details,
        "timestamp": time.time(),
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)
