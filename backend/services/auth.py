"""Autenticación Google (id_token) + JWT de sesión xIA."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Optional

import jwt
from flask import jsonify, request

from services.config import Settings
from services.store import Store


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def verify_google_id_token(id_token: str, client_id: str) -> dict[str, Any]:
    if not client_id:
        raise AuthError("GOOGLE_CLIENT_ID no configurado", 503)
    if not id_token:
        raise AuthError("id_token requerido")

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests

        info = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            client_id,
        )
    except Exception as exc:  # noqa: BLE001
        raise AuthError(f"Token de Google inválido: {exc}") from exc

    if info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise AuthError("Issuer de Google inválido")

    sub = info.get("sub")
    email = info.get("email")
    if not sub or not email:
        raise AuthError("Token de Google incompleto")

    return {
        "google_sub": sub,
        "email": email,
        "name": info.get("name"),
        "picture": info.get("picture"),
        "email_verified": bool(info.get("email_verified")),
    }


def issue_session_token(user: dict[str, Any], settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["id"],
        "google_sub": user["google_sub"],
        "email": user["email"],
        "name": user.get("name"),
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_session_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Sesión expirada") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Sesión inválida") from exc


def get_bearer_token() -> Optional[str]:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return None


def require_auth(settings: Settings, store: Store) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not settings.auth_required:
                # Modo desarrollo sin Google: usuario local fijo
                user = store.upsert_google_user(
                    google_sub="dev-local",
                    email="dev@xia.local",
                    name="Dev Local",
                )
                request.xia_user = user  # type: ignore[attr-defined]
                return fn(*args, **kwargs)

            token = get_bearer_token()
            if not token:
                return jsonify({"error": "auth_required", "message": "Iniciá sesión con Google"}), 401
            try:
                payload = decode_session_token(token, settings)
            except AuthError as exc:
                return jsonify({"error": "auth_invalid", "message": exc.message}), exc.status_code

            user = store.get_user(payload["sub"])
            if not user:
                return jsonify({"error": "auth_invalid", "message": "Usuario no encontrado"}), 401

            request.xia_user = user  # type: ignore[attr-defined]
            return fn(*args, **kwargs)

        return wrapper

    return decorator
