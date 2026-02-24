import secrets
import time
from typing import Any, Dict, Optional, Tuple

from .config import AuthSettings
from .jwt_validation import JwtValidationError, validate_hs256_jwt


class AuthError(RuntimeError):
    pass


class AuthService:
    def __init__(self, settings: AuthSettings):
        self.settings = settings

    def authenticate_bearer(self, token: str) -> Dict[str, Any]:
        try:
            claims = validate_hs256_jwt(
                token,
                secret=self.settings.jwt_signing_secret,
                expected_issuer=self.settings.issuer,
                expected_audience=self.settings.audience,
            )
        except JwtValidationError as exc:
            raise AuthError(str(exc)) from exc
        return self._new_session(subject=str(claims.get("sub") or "unknown"), claims=claims, mode="oidc")

    def local_dev_login(self) -> Dict[str, Any]:
        if not self.settings.allow_dev_login:
            raise AuthError("Local development login is disabled")
        if self.settings.environment not in {"local", "development"}:
            raise AuthError("Local development login is only allowed in local/development environments")

        claims = {
            "sub": self.settings.dev_subject,
            "iss": self.settings.issuer,
            "aud": self.settings.audience,
            "mode": "local-dev",
        }
        return self._new_session(subject=self.settings.dev_subject, claims=claims, mode="local-dev")

    def logout(self, session: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {"ok": True, "revoked_session_id": (session or {}).get("session_id")}

    def session_status(self, session: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not session:
            return {"authenticated": False}
        expires_at = int(session.get("expires_at") or 0)
        return {
            "authenticated": expires_at > int(time.time()),
            "session_id": session.get("session_id"),
            "subject": session.get("subject"),
            "expires_at": expires_at,
            "mode": session.get("mode"),
        }

    def login_endpoint(self, authorization_header: str = "", use_dev_login: bool = False) -> Tuple[int, Dict[str, Any]]:
        if use_dev_login:
            return 200, self.local_dev_login()

        if not authorization_header.startswith("Bearer "):
            return 401, {"error": "missing bearer token"}

        token = authorization_header.split(" ", 1)[1].strip()
        return 200, self.authenticate_bearer(token)

    def logout_endpoint(self, session: Optional[Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        return 200, self.logout(session)

    def session_endpoint(self, session: Optional[Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        return 200, self.session_status(session)

    def _new_session(self, subject: str, claims: Dict[str, Any], mode: str) -> Dict[str, Any]:
        now = int(time.time())
        return {
            "session_id": secrets.token_urlsafe(16),
            "subject": subject,
            "claims": claims,
            "issued_at": now,
            "expires_at": now + self.settings.session_ttl_seconds,
            "mode": mode,
        }
