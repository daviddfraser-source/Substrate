import hashlib
import secrets
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class OAuthSettings:
    authorize_url: str
    token_url: str
    client_id: str
    client_secret: str


class OAuthError(RuntimeError):
    pass


class OAuthClient:
    def __init__(self, settings: OAuthSettings):
        self.settings = settings

    def build_authorize_url(self, state: str, redirect_uri: str, scope: str = "openid profile email") -> str:
        if not state.strip():
            raise OAuthError("state is required")
        if not redirect_uri.strip():
            raise OAuthError("redirect_uri is required")
        return (
            f"{self.settings.authorize_url}?response_type=code"
            f"&client_id={self.settings.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&state={state}"
        )

    def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, str]:
        if not code.strip():
            raise OAuthError("authorization code is required")
        if not redirect_uri.strip():
            raise OAuthError("redirect_uri is required")

        digest = hashlib.sha256(f"{code}:{redirect_uri}:{self.settings.client_id}".encode("utf-8")).hexdigest()
        return {
            "access_token": secrets.token_urlsafe(24),
            "id_token": secrets.token_urlsafe(24),
            "token_type": "Bearer",
            "subject": f"oauth-{digest[:12]}",
            "expires_in": "3600",
        }
