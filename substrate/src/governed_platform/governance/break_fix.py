from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from governed_platform.governance.file_lock import atomic_write_json


BREAK_FIX_SCHEMA_VERSION = "1.0"
BREAK_FIX_SEVERITIES = {"low", "medium", "high", "critical"}
BREAK_FIX_STATUSES = {"open", "in_progress", "resolved", "rejected"}
BREAK_FIX_ACTIONS = {"open", "start", "resolve", "reject", "note"}
ACTIVE_BREAK_FIX_STATUSES = {"open", "in_progress"}


def _now() -> str:
    return datetime.now().isoformat()


def _norm_token(value: Any) -> str:
    return str(value or "").strip().lower()


def _norm_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Missing required field: {field}")
    return text


def _norm_optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _norm_list(values: Any, *, dedupe: bool = True) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        source = [values]
    elif isinstance(values, list):
        source = values
    else:
        raise ValueError("Expected list or string value")
    out: List[str] = []
    seen = set()
    for item in source:
        token = str(item or "").strip()
        if not token:
            continue
        if dedupe:
            if token in seen:
                continue
            seen.add(token)
        out.append(token)
    return out


def normalize_break_fix_severity(value: Any) -> str:
    severity = _norm_token(value)
    if severity not in BREAK_FIX_SEVERITIES:
        raise ValueError(f"Invalid severity: {value!r} (use low|medium|high|critical)")
    return severity


def normalize_break_fix_status(value: Any) -> str:
    status = _norm_token(value)
    if status not in BREAK_FIX_STATUSES:
        raise ValueError(f"Invalid break-fix status: {value!r} (use open|in_progress|resolved|rejected)")
    return status


def default_break_fix_store() -> Dict[str, Any]:
    now = _now()
    return {
        "schema_version": BREAK_FIX_SCHEMA_VERSION,
        "created_at": now,
        "updated_at": now,
        "items": [],
    }


def _next_break_fix_id(payload: Dict[str, Any]) -> str:
    max_num = 0
    for item in payload.get("items", []):
        rid = str(item.get("fix_id") or "")
        if rid.startswith("BFIX-"):
            tail = rid[5:]
            if tail.isdigit():
                max_num = max(max_num, int(tail))
    return f"BFIX-{max_num + 1:04d}"


def load_break_fix_store(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return default_break_fix_store()
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.setdefault("schema_version", BREAK_FIX_SCHEMA_VERSION)
    payload.setdefault("created_at", _now())
    payload.setdefault("updated_at", _now())
    payload.setdefault("items", [])
    if not isinstance(payload.get("items"), list):
        payload["items"] = []
    for item in payload["items"]:
        _normalize_loaded_item(item)
    return payload


def save_break_fix_store(path: Path, payload: Dict[str, Any]) -> None:
    payload["schema_version"] = payload.get("schema_version", BREAK_FIX_SCHEMA_VERSION)
    payload.setdefault("created_at", _now())
    payload["updated_at"] = _now()
    payload.setdefault("items", [])
    atomic_write_json(path, payload)


def _normalize_loaded_item(item: Dict[str, Any]) -> None:
    item.setdefault("fix_id", "")
    item.setdefault("title", "")
    item.setdefault("description", "")
    item["severity"] = normalize_break_fix_severity(item.get("severity", "medium"))
    item["status"] = normalize_break_fix_status(item.get("status", "open"))
    item.setdefault("created_at", _now())
    item.setdefault("created_by", "")
    item["owner"] = _norm_optional_text(item.get("owner"))
    item["packet_id"] = _norm_optional_text(item.get("packet_id"))
    item["linked_packets"] = _norm_list(item.get("linked_packets"))
    item["findings"] = _norm_list(item.get("findings"), dedupe=False)
    item["evidence"] = _norm_list(item.get("evidence"))
    item.setdefault("notes", [])
    item.setdefault("history", [])
    item.setdefault("started_at", None)
    item.setdefault("resolved_at", None)
    item.setdefault("resolved_by", None)
    item.setdefault("resolution_summary", None)
    item.setdefault("rejected_at", None)
    item.setdefault("rejected_by", None)
    item.setdefault("rejection_reason", None)
    item.setdefault("updated_at", item.get("created_at", _now()))


def _find_item(payload: Dict[str, Any], fix_id: str) -> Dict[str, Any]:
    token = str(fix_id or "").strip()
    for item in payload.get("items", []):
        if str(item.get("fix_id") or "").strip() == token:
            return item
    raise ValueError(f"Break-fix item not found: {token}")


def _append_history(
    item: Dict[str, Any],
    *,
    action: str,
    actor: str,
    from_status: str | None,
    to_status: str | None,
    note: str | None = None,
    evidence: List[str] | None = None,
    findings: List[str] | None = None,
) -> None:
    if action not in BREAK_FIX_ACTIONS:
        raise ValueError(f"Invalid break-fix history action: {action}")
    item.setdefault("history", []).append(
        {
            "timestamp": _now(),
            "actor": _norm_text(actor, "actor"),
            "action": action,
            "from_status": from_status,
            "to_status": to_status,
            "note": _norm_optional_text(note),
            "evidence": _norm_list(evidence or []),
            "findings": _norm_list(findings or [], dedupe=False),
        }
    )


def _append_note(item: Dict[str, Any], actor: str, note: str) -> None:
    item.setdefault("notes", []).append(
        {"timestamp": _now(), "actor": _norm_text(actor, "actor"), "note": _norm_text(note, "note")}
    )


def _merge_evidence_and_findings(item: Dict[str, Any], evidence: Any, findings: Any) -> Tuple[List[str], List[str]]:
    evidence_list = _norm_list(evidence)
    findings_list = _norm_list(findings, dedupe=False)
    if evidence_list:
        merged = _norm_list(list(item.get("evidence", [])) + evidence_list)
        item["evidence"] = merged
    else:
        evidence_list = []
    if findings_list:
        merged_findings = list(item.get("findings", []))
        merged_findings.extend(findings_list)
        item["findings"] = _norm_list(merged_findings, dedupe=False)
    else:
        findings_list = []
    return evidence_list, findings_list


def open_break_fix(
    path: Path,
    *,
    actor: str,
    title: str,
    description: str,
    severity: str = "medium",
    packet_id: str = "",
    linked_packets: Any = None,
    findings: Any = None,
    evidence: Any = None,
) -> str:
    payload = load_break_fix_store(path)
    item = {
        "fix_id": _next_break_fix_id(payload),
        "title": _norm_text(title, "title"),
        "description": _norm_text(description, "description"),
        "severity": normalize_break_fix_severity(severity),
        "status": "open",
        "created_at": _now(),
        "created_by": _norm_text(actor, "actor"),
        "owner": None,
        "packet_id": _norm_optional_text(packet_id),
        "linked_packets": _norm_list(linked_packets),
        "findings": _norm_list(findings, dedupe=False),
        "evidence": _norm_list(evidence),
        "notes": [],
        "history": [],
        "started_at": None,
        "resolved_at": None,
        "resolved_by": None,
        "resolution_summary": None,
        "rejected_at": None,
        "rejected_by": None,
        "rejection_reason": None,
        "updated_at": _now(),
    }
    _append_history(item, action="open", actor=actor, from_status=None, to_status="open")
    payload.setdefault("items", []).append(item)
    save_break_fix_store(path, payload)
    return item["fix_id"]


def start_break_fix(path: Path, *, fix_id: str, actor: str, owner: str = "", note: str = "") -> Tuple[bool, str]:
    payload = load_break_fix_store(path)
    item = _find_item(payload, fix_id)
    status = normalize_break_fix_status(item.get("status"))
    if status != "open":
        return False, f"Cannot start {fix_id}: status is {status} (expected open)"

    item["status"] = "in_progress"
    item["owner"] = _norm_optional_text(owner) or _norm_text(actor, "actor")
    item["started_at"] = _now()
    item["updated_at"] = _now()
    if note:
        _append_note(item, actor, note)
    _append_history(item, action="start", actor=actor, from_status="open", to_status="in_progress", note=note or None)
    save_break_fix_store(path, payload)
    return True, f"{fix_id} started"


def resolve_break_fix(
    path: Path,
    *,
    fix_id: str,
    actor: str,
    resolution_summary: str,
    evidence: Any,
    findings: Any = None,
    note: str = "",
) -> Tuple[bool, str]:
    payload = load_break_fix_store(path)
    item = _find_item(payload, fix_id)
    status = normalize_break_fix_status(item.get("status"))
    if status != "in_progress":
        return False, f"Cannot resolve {fix_id}: status is {status} (expected in_progress)"

    summary = _norm_text(resolution_summary, "resolution_summary")
    evidence_list = _norm_list(evidence)
    if not evidence_list:
        return False, "Resolve requires at least one evidence path"

    merged_evidence, merged_findings = _merge_evidence_and_findings(item, evidence_list, findings)
    item["status"] = "resolved"
    item["resolved_at"] = _now()
    item["resolved_by"] = _norm_text(actor, "actor")
    item["resolution_summary"] = summary
    item["updated_at"] = _now()
    if note:
        _append_note(item, actor, note)
    _append_history(
        item,
        action="resolve",
        actor=actor,
        from_status="in_progress",
        to_status="resolved",
        note=summary if not note else f"{summary} | {note}",
        evidence=merged_evidence,
        findings=merged_findings,
    )
    save_break_fix_store(path, payload)
    return True, f"{fix_id} resolved"


def reject_break_fix(path: Path, *, fix_id: str, actor: str, reason: str, note: str = "") -> Tuple[bool, str]:
    payload = load_break_fix_store(path)
    item = _find_item(payload, fix_id)
    status = normalize_break_fix_status(item.get("status"))
    if status in {"resolved", "rejected"}:
        return False, f"Cannot reject {fix_id}: status is {status}"

    rejection_reason = _norm_text(reason, "reason")
    item["status"] = "rejected"
    item["rejected_at"] = _now()
    item["rejected_by"] = _norm_text(actor, "actor")
    item["rejection_reason"] = rejection_reason
    item["updated_at"] = _now()
    if note:
        _append_note(item, actor, note)
    _append_history(
        item,
        action="reject",
        actor=actor,
        from_status=status,
        to_status="rejected",
        note=rejection_reason if not note else f"{rejection_reason} | {note}",
    )
    save_break_fix_store(path, payload)
    return True, f"{fix_id} rejected"


def note_break_fix(
    path: Path,
    *,
    fix_id: str,
    actor: str,
    note: str,
    evidence: Any = None,
    findings: Any = None,
) -> Tuple[bool, str]:
    payload = load_break_fix_store(path)
    item = _find_item(payload, fix_id)
    note_text = _norm_text(note, "note")
    evidence_list, findings_list = _merge_evidence_and_findings(item, evidence, findings)
    _append_note(item, actor, note_text)
    _append_history(
        item,
        action="note",
        actor=actor,
        from_status=normalize_break_fix_status(item.get("status")),
        to_status=normalize_break_fix_status(item.get("status")),
        note=note_text,
        evidence=evidence_list,
        findings=findings_list,
    )
    item["updated_at"] = _now()
    save_break_fix_store(path, payload)
    return True, f"{fix_id} noted"


def list_break_fixes(
    path: Path,
    *,
    status: str = "",
    severity: str = "",
    packet_id: str = "",
    owner: str = "",
    limit: int = 0,
) -> List[Dict[str, Any]]:
    payload = load_break_fix_store(path)
    status_filter = _norm_token(status)
    severity_filter = _norm_token(severity)
    packet_filter = str(packet_id or "").strip()
    owner_filter = str(owner or "").strip().lower()

    if status_filter:
        normalize_break_fix_status(status_filter)
    if severity_filter:
        normalize_break_fix_severity(severity_filter)

    rows: List[Dict[str, Any]] = []
    for item in payload.get("items", []):
        if status_filter and _norm_token(item.get("status")) != status_filter:
            continue
        if severity_filter and _norm_token(item.get("severity")) != severity_filter:
            continue
        if packet_filter:
            linked = [str(v).strip() for v in item.get("linked_packets", [])]
            if str(item.get("packet_id") or "").strip() != packet_filter and packet_filter not in linked:
                continue
        if owner_filter and _norm_token(item.get("owner")) != owner_filter:
            continue
        rows.append(item)
    rows.sort(key=lambda it: str(it.get("updated_at") or ""), reverse=True)
    if limit and limit > 0:
        return rows[:limit]
    return rows


def get_break_fix(path: Path, fix_id: str) -> Dict[str, Any]:
    payload = load_break_fix_store(path)
    token = str(fix_id or "").strip()
    for item in payload.get("items", []):
        if str(item.get("fix_id") or "").strip() == token:
            return item
    return {}


def break_fix_summary(path: Path) -> Dict[str, Any]:
    payload = load_break_fix_store(path)
    counts = {status: 0 for status in sorted(BREAK_FIX_STATUSES)}
    by_severity = {sev: 0 for sev in sorted(BREAK_FIX_SEVERITIES)}
    by_packet: Dict[str, int] = {}
    by_packet_active: Dict[str, int] = {}
    for item in payload.get("items", []):
        status = normalize_break_fix_status(item.get("status", "open"))
        severity = normalize_break_fix_severity(item.get("severity", "medium"))
        counts[status] = counts.get(status, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        packet = str(item.get("packet_id") or "").strip()
        if packet:
            by_packet[packet] = by_packet.get(packet, 0) + 1
        for linked in item.get("linked_packets", []):
            token = str(linked or "").strip()
            if token:
                by_packet[token] = by_packet.get(token, 0) + 1
        if status in ACTIVE_BREAK_FIX_STATUSES:
            keys = []
            if packet:
                keys.append(packet)
            keys.extend([str(v).strip() for v in item.get("linked_packets", []) if str(v).strip()])
            for token in set(keys):
                by_packet_active[token] = by_packet_active.get(token, 0) + 1

    active = sum(counts.get(status, 0) for status in ACTIVE_BREAK_FIX_STATUSES)
    return {
        "schema_version": payload.get("schema_version", BREAK_FIX_SCHEMA_VERSION),
        "updated_at": payload.get("updated_at"),
        "total": len(payload.get("items", [])),
        "active": active,
        "counts": counts,
        "by_severity": by_severity,
        "by_packet": by_packet,
        "by_packet_active": by_packet_active,
    }
