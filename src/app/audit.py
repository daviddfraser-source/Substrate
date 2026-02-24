import csv
import io
import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class AuditEntry:
    entry_id: str
    tenant_id: str
    actor: str
    packet_id: str
    event_type: str
    created_at: str


class AuditViewer:
    def __init__(self, entries: Optional[List[AuditEntry]] = None):
        self._entries = list(entries or [])

    def query(self, tenant_id: str = "", actor: str = "", packet_id: str = "", start_date: str = "", end_date: str = "") -> List[AuditEntry]:
        out = []
        for entry in self._entries:
            if tenant_id and entry.tenant_id != tenant_id:
                continue
            if actor and entry.actor != actor:
                continue
            if packet_id and entry.packet_id != packet_id:
                continue
            if start_date and entry.created_at < start_date:
                continue
            if end_date and entry.created_at > end_date:
                continue
            out.append(entry)
        return out

    def paginate(self, entries: List[AuditEntry], page: int, page_size: int) -> List[AuditEntry]:
        start = max(page, 0) * page_size
        end = start + page_size
        return entries[start:end]

    def export_json(self, entries: List[AuditEntry]) -> str:
        return json.dumps([entry.__dict__ for entry in entries], indent=2)

    def export_csv(self, entries: List[AuditEntry]) -> str:
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=["entry_id", "tenant_id", "actor", "packet_id", "event_type", "created_at"])
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.__dict__)
        return out.getvalue()
