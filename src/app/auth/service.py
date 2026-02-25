import secrets
import time
from typing import Any, Dict, Optional, Tuple

from .config import AuthSettings
from .jwt_validation import JwtValidationError, validate_hs256_jwt
from .oauth import OAuthClient, OAuthSettings


class AuthError(RuntimeError):
    pass


class AuthService:
    def __init__(self, settings: AuthSettings):
        self.settings = settings
        self._revoked_sessions = set()
        self._revoked_jti = set()
        self._oauth_client = OAuthClient(
            OAuthSettings(
                authorize_url=settings.oauth_authorize_url,
                token_url=settings.oauth_token_url,
                client_id=settings.oauth_client_id,
                client_secret=settings.oauth_client_secret,
            )
        )

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
        jti = str(claims.get("jti") or "").strip()
        if jti and jti in self._revoked_jti:
            raise AuthError("JWT was revoked")
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
        token = session or {}
        session_id = str(token.get("session_id") or "").strip()
        if session_id:
            self._revoked_sessions.add(session_id)
        jti = str((token.get("claims") or {}).get("jti") or "").strip()
        if jti:
            self._revoked_jti.add(jti)
        return {"ok": True, "revoked_session_id": session_id or None, "revoked_jti": jti or None}

    def session_status(self, session: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not session:
            return {"authenticated": False}
        session_id = str(session.get("session_id") or "")
        if session_id in self._revoked_sessions:
            return {"authenticated": False, "session_id": session_id, "revoked": True}
        expires_at = int(session.get("expires_at") or 0)
        return {
            "authenticated": expires_at > int(time.time()),
            "session_id": session_id,
            "subject": session.get("subject"),
            "expires_at": expires_at,
            "mode": session.get("mode"),
        }

    def refresh_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        status = self.session_status(session)
        if not status.get("authenticated"):
            raise AuthError("Cannot refresh expired or revoked session")
        refreshed = self._new_session(
            subject=str(session.get("subject") or "unknown"),
            claims=dict(session.get("claims") or {}),
            mode=str(session.get("mode") or "oidc"),
        )
        refreshed["rotated_from"] = session.get("session_id")
        self._revoked_sessions.add(str(session.get("session_id") or ""))
        return refreshed

    def oauth_authorize(self, state: str, redirect_uri: str) -> Dict[str, Any]:
        return {"authorize_url": self._oauth_client.build_authorize_url(state=state, redirect_uri=redirect_uri)}

    def oauth_exchange(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        token_payload = self._oauth_client.exchange_code(code=code, redirect_uri=redirect_uri)
        claims = {
            "sub": token_payload["subject"],
            "iss": self.settings.issuer,
            "aud": self.settings.audience,
            "mode": "oauth-code",
        }
        session = self._new_session(subject=token_payload["subject"], claims=claims, mode="oauth")
        return {"session": session, "token_type": token_payload["token_type"]}

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
