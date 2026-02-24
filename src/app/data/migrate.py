import sqlite3
from pathlib import Path
from typing import Iterable, List


MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def migration_files() -> List[Path]:
    return sorted(p for p in MIGRATIONS_DIR.glob("*.sql") if p.is_file())


def apply_sqlite_migrations(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        for path in migration_files():
            sql = path.read_text(encoding="utf-8")
            conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def migration_sql_has_postgres_compatible_types(sql_lines: Iterable[str]) -> bool:
    # This guards against SQLite-only affinity surprises in shared migration files.
    forbidden = {"AUTOINCREMENT"}
    for line in sql_lines:
        upper = line.upper()
        if any(token in upper for token in forbidden):
            return False
    return True
