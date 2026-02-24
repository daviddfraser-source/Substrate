from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class RuntimeConfig:
    app_env: str
    database_url: str
    sqlite_fallback_path: str
    profile: str


def load_runtime_config(env: Mapping[str, str]) -> RuntimeConfig:
    app_env = (env.get("APP_ENV") or "development").strip().lower()
    database_url = (env.get("DATABASE_URL") or "").strip()
    sqlite_fallback_path = (env.get("SQLITE_FALLBACK_PATH") or "./data/substrate-dev.db").strip()
    profile = (env.get("SUBSTRATE_PROFILE") or "core-governance").strip()

    if app_env == "production" and not database_url:
        raise ValueError("DATABASE_URL is required in production")

    if database_url:
        if not (database_url.startswith("postgresql://") or database_url.startswith("sqlite:///")):
            raise ValueError("DATABASE_URL must use postgresql:// or sqlite:///")
    else:
        database_url = f"sqlite:///{sqlite_fallback_path}"

    return RuntimeConfig(
        app_env=app_env,
        database_url=database_url,
        sqlite_fallback_path=sqlite_fallback_path,
        profile=profile,
    )
