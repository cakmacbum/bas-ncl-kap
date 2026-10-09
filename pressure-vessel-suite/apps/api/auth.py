"""Supabase JWT doğrulaması (FastAPI bağımlılığı `require_user`).

- Asimetrik anahtarlar: ${SUPABASE_URL}/auth/v1/.well-known/jwks.json (önbellekli).
- Yedek: SUPABASE_JWT_SECRET ile HS256.
- AUTH_MODE=anonymous (varsayılan) | supabase. AUTH_DISABLED=true => anonymous (geriye uyum).
- `require_owner`: proje sahibi kimliği (`user:<sub>` veya `anon:<uuid>`).
Ortam değişkenleri istek anında okunur (testlerde monkeypatch edilebilsin diye).
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

logger = logging.getLogger("basincli-kap.auth")

AUDIENCE = "authenticated"
_ASYMMETRIC_ALGS = ["RS256", "ES256", "EdDSA"]

_jwks_clients: dict[str, PyJWKClient] = {}


def auth_disabled() -> bool:
    return os.environ.get("AUTH_DISABLED", "").strip().lower() in {"1", "true", "yes"}


def auth_mode() -> str:
    """'supabase' yalnızca AUTH_MODE=supabase ve AUTH_DISABLED kapalıyken; aksi halde 'anonymous'."""
    if auth_disabled():
        return "anonymous"
    mode = os.environ.get("AUTH_MODE", "anonymous").strip().lower()
    return "supabase" if mode == "supabase" else "anonymous"


def _supabase_url() -> str:
    return os.environ.get("SUPABASE_URL", "").strip().rstrip("/")


def _jwks_client(base: str) -> PyJWKClient:
    client = _jwks_clients.get(base)
    if client is None:
        client = PyJWKClient(
            f"{base}/auth/v1/.well-known/jwks.json",
            cache_keys=True,
            cache_jwk_set=True,
            lifespan=3600,
            timeout=5,
        )
        _jwks_clients[base] = client
    return client


def _unauthorized(message: str = "Invalid or missing authentication token") -> HTTPException:
    return HTTPException(
        status_code=401, detail=message, headers={"WWW-Authenticate": "Bearer"}
    )


def verify_token(token: str) -> dict[str, Any]:
    base = _supabase_url()
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    issuer = f"{base}/auth/v1" if base else None
    options = {"require": ["exp", "sub"]}
    try:
        alg = jwt.get_unverified_header(token).get("alg")
        if alg == "HS256" and secret:
            return jwt.decode(
                token, secret, algorithms=["HS256"], audience=AUDIENCE,
                issuer=issuer, options=options,
            )
        if alg in _ASYMMETRIC_ALGS and base:
            key = _jwks_client(base).get_signing_key_from_jwt(token).key
            return jwt.decode(
                token, key, algorithms=_ASYMMETRIC_ALGS, audience=AUDIENCE,
                issuer=issuer, options=options,
            )
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token expired") from None
    except jwt.PyJWKClientError:
        logger.warning("JWKS anahtarı alınamadı/bulunamadı")
        raise _unauthorized() from None
    except jwt.PyJWTError:
        raise _unauthorized() from None
    except Exception:  # noqa: BLE001 - ağ vb. iç hata istemciye sızmasın
        logger.exception("Token doğrulama beklenmeyen hata")
        raise _unauthorized() from None
    raise _unauthorized()


def require_user(request: Request) -> dict[str, Any]:
    """Authorization: Bearer <jwt> doğrular; claim sözlüğünü döndürür."""
    if auth_disabled():
        return {"sub": "dev-user", "auth_disabled": True}
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise _unauthorized()
    return verify_token(token.strip())


def require_owner(request: Request) -> str:
    """Proje sahibi dizgesi döndürür: supabase => `user:<sub>`, anonymous => `anon:<uuid>`."""
    if auth_mode() == "supabase":
        claims = require_user(request)
        return f"user:{claims['sub']}"
    raw = request.headers.get("x-client-id", "")
    try:
        client_id = str(uuid.UUID(raw))
    except ValueError:
        client_id = ""
    if not client_id or client_id != raw.lower():  # yalnızca kanonik tireli biçim
        raise HTTPException(status_code=400, detail="Missing or invalid X-Client-Id")
    return f"anon:{client_id}"
