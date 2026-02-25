from __future__ import annotations

import json
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from governed_platform.governance.file_lock import atomic_write_json
from governed_platform.governance.log_integrity import normalize_log_mode
from governed_platform.governance.status import normalize_packet_status_map

STATE_VERSION = "1.0"


class StorageInterface(ABC):
    """Storage boundary for packet runtime state and mutation log persistence."""

    @abstractmethod
    def read_state(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_state(self, state: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def append_audit(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class FileStorage(StorageInterface):
    """State/audit adapter backed by `.governance/wbs-state.json`."""

    def __init__(self, state_path: Path):
        self.state_path = Path(state_path)

    def default_state(self) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "version": STATE_VERSION,
            "created_at": now,
            "updated_at": now,
            "packets": {},
            "log": [],
            "area_closeouts": {},
            "log_integrity_mode": "plain",
        }

    def read_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return self.default_state()
        with open(self.state_path, encoding="utf-8") as f:
            state = json.load(f)
        state.setdefault("packets", {})
        state.setdefault("log", [])
        state.setdefault("area_closeouts", {})
        state.setdefault("log_integrity_mode", "plain")
        state["log_integrity_mode"] = normalize_log_mode(state.get("log_integrity_mode"))
        return normalize_packet_status_map(state)

    def write_state(self, state: Dict[str, Any]) -> None:
        payload = deepcopy(state)
        payload["version"] = payload.get("version", STATE_VERSION)
        payload["updated_at"] = datetime.now().isoformat()
        atomic_write_json(self.state_path, payload)

    def append_audit(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        state = self.read_state()
        audit = state.setdefault("log", [])
        audit.append(deepcopy(entry))
        self.write_state(state)
        return entry


__all__ = ["StorageInterface", "FileStorage", "STATE_VERSION"]
