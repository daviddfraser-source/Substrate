from dataclasses import dataclass
from typing import Mapping


SUPPORTED_PROVIDERS = {"azure_ad", "auth0", "keycloak", "okta"}


@dataclass(frozen=True)
class AuthSettings:
    provider: str
    issuer: str
    audience: str
    jwt_signing_secret: str
    environment: str
    allow_dev_login: bool
    dev_subject: str
    session_ttl_seconds: int

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "AuthSettings":
        provider = (env.get("AUTH_PROVIDER") or "keycloak").strip().lower()
        issuer = (env.get("AUTH_ISSUER") or "").strip()
        audience = (env.get("AUTH_AUDIENCE") or "").strip()
        jwt_signing_secret = (env.get("AUTH_JWT_SIGNING_SECRET") or "").strip()
        environment = (env.get("APP_ENV") or "development").strip().lower()
        allow_dev_login = (env.get("AUTH_ALLOW_DEV_LOGIN") or "false").strip().lower() == "true"
        dev_subject = (env.get("AUTH_DEV_SUBJECT") or "dev-user").strip()
        session_ttl_seconds = int((env.get("AUTH_SESSION_TTL_SECONDS") or "3600").strip())

        settings = cls(
            provider=provider,
            issuer=issuer,
            audience=audience,
            jwt_signing_secret=jwt_signing_secret,
            environment=environment,
            allow_dev_login=allow_dev_login,
            dev_subject=dev_subject,
            session_ttl_seconds=session_ttl_seconds,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError("Unsupported AUTH_PROVIDER")
        if not self.issuer:
            raise ValueError("AUTH_ISSUER is required")
        if not self.audience:
            raise ValueError("AUTH_AUDIENCE is required")
        if not self.jwt_signing_secret:
            raise ValueError("AUTH_JWT_SIGNING_SECRET is required")
        if self.session_ttl_seconds <= 0:
            raise ValueError("AUTH_SESSION_TTL_SECONDS must be greater than zero")
        if self.allow_dev_login and self.environment not in {"local", "development"}:
            raise ValueError("AUTH_ALLOW_DEV_LOGIN is only permitted in local or development environments")
