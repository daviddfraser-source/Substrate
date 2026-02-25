import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TemplateManifest:
    template_id: str
    version: str
    name: str
    files: List[str]
    seed_data: Dict[str, object]


class TemplateError(ValueError):
    pass


class TemplateCatalog:
    def __init__(self):
        self._templates: Dict[Tuple[str, str], TemplateManifest] = {}
        self._active_versions: Dict[str, str] = {}

    def register(self, manifest: TemplateManifest) -> None:
        if not manifest.template_id.strip() or not manifest.version.strip():
            raise TemplateError("template_id and version are required")
        key = (manifest.template_id, manifest.version)
        self._templates[key] = manifest
        self._active_versions.setdefault(manifest.template_id, manifest.version)

    def resolve(self, template_id: str, version: Optional[str] = None) -> TemplateManifest:
        token = (template_id or "").strip()
        if not token:
            raise TemplateError("template_id is required")
        resolved_version = (version or self._active_versions.get(token) or "").strip()
        key = (token, resolved_version)
        item = self._templates.get(key)
        if item is None:
            raise TemplateError(f"Template not found: {token}@{resolved_version}")
        return item

    def set_active_version(self, template_id: str, version: str) -> None:
        self.resolve(template_id, version)
        self._active_versions[template_id] = version


class TemplateInstaller:
    def __init__(self, catalog: TemplateCatalog, install_root: Path, audit_log: Path):
        self.catalog = catalog
        self.install_root = Path(install_root)
        self.audit_log = Path(audit_log)
        self.install_root.mkdir(parents=True, exist_ok=True)
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

    def validate_manifest(self, manifest: TemplateManifest) -> Tuple[bool, str]:
        if not manifest.files:
            return False, "manifest.files cannot be empty"
        if any(".." in f or f.startswith("/") for f in manifest.files):
            return False, "manifest.files must be relative paths"
        return True, "ok"

    def install(self, template_id: str, version: Optional[str] = None) -> Path:
        manifest = self.catalog.resolve(template_id, version)
        ok, msg = self.validate_manifest(manifest)
        if not ok:
            raise TemplateError(msg)

        target = self.install_root / manifest.template_id / manifest.version
        if target.exists():
            raise TemplateError(f"Template already installed: {manifest.template_id}@{manifest.version}")

        target.mkdir(parents=True, exist_ok=False)
        for rel in manifest.files:
            path = target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# seeded by {manifest.template_id}@{manifest.version}\n", encoding="utf-8")

        (target / "seed-data.json").write_text(json.dumps(manifest.seed_data, indent=2) + "\n", encoding="utf-8")
        self._append_audit("install", manifest.template_id, manifest.version, str(target))
        return target

    def rollback(self, template_id: str, from_version: str, to_version: str) -> None:
        from_dir = self.install_root / template_id / from_version
        to_dir = self.install_root / template_id / to_version
        if not from_dir.exists() or not to_dir.exists():
            raise TemplateError("Both from_version and to_version must be installed")
        self.catalog.set_active_version(template_id, to_version)
        self._append_audit("rollback", template_id, f"{from_version}->{to_version}", str(to_dir))

    def uninstall(self, template_id: str, version: str) -> None:
        target = self.install_root / template_id / version
        if not target.exists():
            raise TemplateError("Template install not found")
        shutil.rmtree(target)
        self._append_audit("uninstall", template_id, version, str(target))

    def _append_audit(self, action: str, template_id: str, version: str, target: str) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "template_id": template_id,
            "version": version,
            "target": target,
        }
        with self.audit_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
