import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.template_engine import TemplateCatalog, TemplateInstaller, TemplateManifest  # noqa: E402


class TemplateEnginePhase5Tests(unittest.TestCase):
    def test_install_rollback_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            install_root = Path(tmp) / "installs"
            audit_log = Path(tmp) / "audit" / "template-audit.jsonl"

            catalog = TemplateCatalog()
            catalog.register(TemplateManifest("starter", "1.0.0", "Starter", ["README.md", "seed/config.json"], {"packet_seed": 3}))
            catalog.register(TemplateManifest("starter", "1.1.0", "Starter", ["README.md", "seed/config.json"], {"packet_seed": 4}))

            installer = TemplateInstaller(catalog, install_root=install_root, audit_log=audit_log)
            v1 = installer.install("starter", "1.0.0")
            v2 = installer.install("starter", "1.1.0")
            self.assertTrue((v1 / "README.md").exists())
            self.assertTrue((v2 / "seed-data.json").exists())

            installer.rollback("starter", "1.1.0", "1.0.0")
            installer.uninstall("starter", "1.1.0")
            self.assertFalse(v2.exists())

            lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
            self.assertGreaterEqual(len(lines), 4)
            first = json.loads(lines[0])
            self.assertEqual(first["action"], "install")


if __name__ == "__main__":
    unittest.main()
