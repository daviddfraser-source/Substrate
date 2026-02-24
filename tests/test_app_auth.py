import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.auth.config import AuthSettings  # noqa: E402
from app.auth.jwt_validation import JwtValidationError, create_test_hs256_jwt  # noqa: E402
from app.auth.service import AuthError, AuthService  # noqa: E402


class AuthServiceTests(unittest.TestCase):
    def _env(self, **overrides):
        base = {
            "AUTH_PROVIDER": "keycloak",
            "AUTH_ISSUER": "https://issuer.example",
            "AUTH_AUDIENCE": "substrate-api",
            "AUTH_JWT_SIGNING_SECRET": "top-secret",
            "APP_ENV": "development",
            "AUTH_ALLOW_DEV_LOGIN": "true",
            "AUTH_DEV_SUBJECT": "dev-tester",
            "AUTH_SESSION_TTL_SECONDS": "600",
        }
        base.update(overrides)
        return base

    def test_local_dev_login_allowed_only_in_dev(self):
        settings = AuthSettings.from_env(self._env())
        service = AuthService(settings)
        session = service.local_dev_login()
        self.assertEqual(session["mode"], "local-dev")

        with self.assertRaises(ValueError):
            AuthSettings.from_env(self._env(APP_ENV="production"))

    def test_bearer_jwt_validation(self):
        settings = AuthSettings.from_env(self._env(AUTH_ALLOW_DEV_LOGIN="false"))
        service = AuthService(settings)

        payload = {
            "sub": "user-123",
            "iss": settings.issuer,
            "aud": settings.audience,
            "exp": int(time.time()) + 600,
        }
        token = create_test_hs256_jwt(payload, settings.jwt_signing_secret)
        session = service.authenticate_bearer(token)
        self.assertEqual(session["subject"], "user-123")
        self.assertEqual(service.session_status(session)["authenticated"], True)

    def test_bearer_rejects_bad_signature(self):
        settings = AuthSettings.from_env(self._env(AUTH_ALLOW_DEV_LOGIN="false"))
        service = AuthService(settings)
        payload = {
            "sub": "user-123",
            "iss": settings.issuer,
            "aud": settings.audience,
            "exp": int(time.time()) + 600,
        }
        bad_token = create_test_hs256_jwt(payload, "wrong-secret")
        with self.assertRaises(AuthError):
            service.authenticate_bearer(bad_token)

    def test_expired_token_rejected(self):
        settings = AuthSettings.from_env(self._env(AUTH_ALLOW_DEV_LOGIN="false"))
        payload = {
            "sub": "user-123",
            "iss": settings.issuer,
            "aud": settings.audience,
            "exp": int(time.time()) - 1,
        }
        token = create_test_hs256_jwt(payload, settings.jwt_signing_secret)
        with self.assertRaises(JwtValidationError):
            from app.auth.jwt_validation import validate_hs256_jwt

            validate_hs256_jwt(token, settings.jwt_signing_secret, settings.issuer, settings.audience)


if __name__ == "__main__":
    unittest.main()
