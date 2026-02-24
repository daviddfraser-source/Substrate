import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


REQUIRED_METRICS = {
    "packet_cycle_time_seconds",
    "claim_to_completion_seconds",
    "blocked_state_frequency",
    "reopened_packet_rate",
    "risk_density",
    "agent_execution_rate",
    "api_latency_ms",
    "db_query_time_ms",
    "grid_render_time_ms",
}


@dataclass
class TelemetryEvent:
    metric_name: str
    value: float
    tenant_id: Optional[str]
    project_id: Optional[str]
    tags: Dict[str, str]
    recorded_at: float


class TelemetryStore:
    def __init__(self):
        self._events: List[TelemetryEvent] = []

    def record(self, metric_name: str, value: float, tenant_id: Optional[str] = None, project_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> TelemetryEvent:
        event = TelemetryEvent(
            metric_name=metric_name,
            value=float(value),
            tenant_id=tenant_id,
            project_id=project_id,
            tags=dict(tags or {}),
            recorded_at=time.time(),
        )
        self._events.append(event)
        return event

    def query(self, metric_name: str = "", tenant_id: str = "", project_id: str = "") -> List[TelemetryEvent]:
        out = []
        for event in self._events:
            if metric_name and event.metric_name != metric_name:
                continue
            if tenant_id and event.tenant_id != tenant_id:
                continue
            if project_id and event.project_id != project_id:
                continue
            out.append(event)
        return out

    def coverage(self) -> Dict[str, bool]:
        found = {event.metric_name for event in self._events}
        return {metric: metric in found for metric in sorted(REQUIRED_METRICS)}


class Instrumentation:
    def __init__(self, store: TelemetryStore):
        self.store = store

    def on_packet_transition(self, packet_id: str, from_state: str, to_state: str, elapsed_seconds: float) -> None:
        self.store.record(
            "packet_cycle_time_seconds",
            elapsed_seconds,
            tags={"packet_id": packet_id, "from": from_state, "to": to_state},
        )

    def on_api_call(self, route: str, latency_ms: float, status_code: int) -> None:
        self.store.record(
            "api_latency_ms",
            latency_ms,
            tags={"route": route, "status_code": str(status_code)},
        )

    def on_db_query(self, query_name: str, elapsed_ms: float) -> None:
        self.store.record("db_query_time_ms", elapsed_ms, tags={"query_name": query_name})
