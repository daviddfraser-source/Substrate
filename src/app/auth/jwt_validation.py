import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict


class JwtValidationError(ValueError):
    pass


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def parse_jwt(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise JwtValidationError("Malformed JWT")
    header_raw, payload_raw, _ = parts
    try:
        header = json.loads(_b64url_decode(header_raw).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_raw).decode("utf-8"))
    except Exception as exc:
        raise JwtValidationError("JWT decode failed") from exc
    return {"header": header, "payload": payload}


def validate_hs256_jwt(token: str, secret: str, expected_issuer: str, expected_audience: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise JwtValidationError("Malformed JWT")

    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    signature = _b64url_decode(parts[2])
    decoded = parse_jwt(token)
    header = decoded["header"]
    payload = decoded["payload"]

    if header.get("alg") != "HS256":
        raise JwtValidationError("Unsupported JWT algorithm")

    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise JwtValidationError("JWT signature verification failed")

    if payload.get("iss") != expected_issuer:
        raise JwtValidationError("JWT issuer mismatch")

    audience = payload.get("aud")
    if isinstance(audience, list):
        if expected_audience not in audience:
            raise JwtValidationError("JWT audience mismatch")
    elif audience != expected_audience:
        raise JwtValidationError("JWT audience mismatch")

    now = int(time.time())
    exp = int(payload.get("exp") or 0)
    if exp <= now:
        raise JwtValidationError("JWT is expired")

    nbf = int(payload.get("nbf") or 0)
    if nbf and nbf > now:
        raise JwtValidationError("JWT not active yet")

    return payload


def create_test_hs256_jwt(payload: Dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h_part}.{p_part}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    s_part = _b64url_encode(signature)
    return f"{h_part}.{p_part}.{s_part}"
