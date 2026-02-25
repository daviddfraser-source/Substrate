import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class AnalyticsEvent:
    tenant_id: str
    project_id: str
    metric_name: str
    metric_value: float
    timestamp: str
    tags: Dict[str, str]


class AnalyticsService:
    def __init__(self):
        self._events: List[AnalyticsEvent] = []
        self._cache: Dict[str, Dict[str, object]] = {}

    def record(self, tenant_id: str, project_id: str, metric_name: str, metric_value: float, tags: Optional[Dict[str, str]] = None) -> None:
        event = AnalyticsEvent(
            tenant_id=tenant_id,
            project_id=project_id,
            metric_name=metric_name,
            metric_value=float(metric_value),
            timestamp=datetime.now(timezone.utc).isoformat(),
            tags=tags or {},
        )
        self._events.append(event)
        self._cache.clear()

    def aggregate(self, tenant_id: str, project_id: str, metric_name: str = "") -> Dict[str, object]:
        key = f"{tenant_id}:{project_id}:{metric_name}"
        if key in self._cache:
            return dict(self._cache[key])

        rows = [e for e in self._events if e.tenant_id == tenant_id and e.project_id == project_id]
        if metric_name:
            rows = [e for e in rows if e.metric_name == metric_name]

        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for row in rows:
            totals[row.metric_name] = totals.get(row.metric_name, 0.0) + row.metric_value
            counts[row.metric_name] = counts.get(row.metric_name, 0) + 1

        summary = {
            "tenant_id": tenant_id,
            "project_id": project_id,
            "metrics": [
                {
                    "metric_name": name,
                    "count": counts[name],
                    "total": round(totals[name], 6),
                    "average": round(totals[name] / counts[name], 6),
                }
                for name in sorted(totals.keys())
            ],
            "event_count": len(rows),
        }
        self._cache[key] = dict(summary)
        return summary

    def export_json(self, tenant_id: str, project_id: str) -> str:
        return json.dumps(self.aggregate(tenant_id, project_id), indent=2) + "\n"

    def export_csv(self, tenant_id: str, project_id: str) -> str:
        summary = self.aggregate(tenant_id, project_id)
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=["metric_name", "count", "total", "average"])
        writer.writeheader()
        for row in summary["metrics"]:
            writer.writerow(row)
        return out.getvalue()

    def endpoint_summary(self, tenant_id: str, project_id: str, metric_name: str = "") -> Dict[str, object]:
        payload = self.aggregate(tenant_id, project_id, metric_name)
        return {"ok": True, "summary": payload}

    def endpoint_export(self, tenant_id: str, project_id: str, fmt: str = "json") -> Dict[str, object]:
        token = fmt.strip().lower()
        if token == "json":
            return {"ok": True, "format": "json", "payload": self.export_json(tenant_id, project_id)}
        if token == "csv":
            return {"ok": True, "format": "csv", "payload": self.export_csv(tenant_id, project_id)}
        return {"ok": False, "error": "unsupported format"}
