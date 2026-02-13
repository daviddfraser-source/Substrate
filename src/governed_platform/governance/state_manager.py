import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


STATE_VERSION = "1.0"


class StateManager:
    """Version-aware state storage and migration entrypoint."""

    def __init__(self, state_path: Path):
        self.state_path = state_path

    def default_state(self) -> Dict[str, Any]:
        return {
            "version": STATE_VERSION,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "packets": {},
            "log": [],
            "area_closeouts": {},
        }

    def load(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return self.default_state()
        with open(self.state_path) as f:
            state = json.load(f)
        state = self._ensure_version(state)
        return state

    def save(self, state: Dict[str, Any]) -> None:
        state["version"] = state.get("version", STATE_VERSION)
        state["updated_at"] = datetime.now().isoformat()
        tmp = self.state_path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        tmp.replace(self.state_path)

    def _ensure_version(self, state: Dict[str, Any]) -> Dict[str, Any]:
        from governed_platform.governance.migrations.runner import migrate_state

        return migrate_state(state)
