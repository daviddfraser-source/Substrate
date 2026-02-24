import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.runtime_config import load_runtime_config  # noqa: E402


class RuntimeConfigTests(unittest.TestCase):
    def test_sqlite_fallback_selected_in_dev(self):
        cfg = load_runtime_config({"APP_ENV": "development"})
        self.assertTrue(cfg.database_url.startswith("sqlite:///"))

    def test_production_requires_database_url(self):
        with self.assertRaises(ValueError):
            load_runtime_config({"APP_ENV": "production"})

    def test_valid_postgres_url(self):
        cfg = load_runtime_config({"APP_ENV": "production", "DATABASE_URL": "postgresql://u:p@db:5432/substrate"})
        self.assertEqual(cfg.database_url, "postgresql://u:p@db:5432/substrate")


if __name__ == "__main__":
    unittest.main()
