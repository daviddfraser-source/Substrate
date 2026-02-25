import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class AuditRecord:
    event_id: str
    actor: str
    action: str
    timestamp: str
    details: Dict[str, object]


class ImmutableAuditLog:
    def __init__(self):
        self._records: List[AuditRecord] = []

    def append(self, actor: str, action: str, details: Dict[str, object]) -> AuditRecord:
        record = AuditRecord(
            event_id=f"evt-{len(self._records)+1:06d}",
            actor=actor,
            action=action,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=dict(details),
        )
        self._records.append(record)
        return record

    def export(self) -> str:
        return json.dumps([r.__dict__ for r in self._records], indent=2) + "\n"

    def records(self) -> List[AuditRecord]:
        return list(self._records)


class BackupRecoveryManager:
    def backup(self, paths: Iterable[Path], backup_root: Path) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = backup_root / f"backup-{timestamp}"
        target.mkdir(parents=True, exist_ok=False)

        manifest: List[Dict[str, str]] = []
        for path in paths:
            src = Path(path)
            if not src.exists():
                continue
            rel = src.name
            dst = target / rel
            if src.is_dir():
                shutil.copytree(src, dst)
                manifest.append({"source": str(src), "target": str(dst), "type": "dir"})
            else:
                shutil.copy2(src, dst)
                manifest.append({"source": str(src), "target": str(dst), "type": "file"})

        (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return target

    def restore(self, backup_path: Path, restore_root: Path) -> None:
        backup = Path(backup_path)
        manifest_path = backup / "manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in payload:
            src = Path(item["target"])
            dst = Path(restore_root) / Path(item["source"]).name
            if item["type"] == "dir":
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
