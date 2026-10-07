"""Verificación de Google reCAPTCHA v2/v3."""

from __future__ import annotations

import logging
from typing import Any

import requests

from services.config import Settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class RecaptchaError(Exception):
    def __init__(self, message: str, status_code: int = 403):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def verify_recaptcha_token(token: str, settings: Settings, remote_ip: str | None = None) -> dict[str, Any]:
    """
    Valida el token con Google.
    Si RECAPTCHA_SECRET_KEY no está configurada, omite la verificación (dev).
    """
    secret = (settings.recaptcha_secret_key or "").strip()
    if not secret:
        logger.warning("reCAPTCHA no configurado; se omite verificación")
        return {"success": True, "skipped": True}

    if not (token or "").strip():
        raise RecaptchaError("Completá el captcha antes de continuar")

    payload: dict[str, str] = {
        "secret": secret,
        "response": token.strip(),
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        response = requests.post(VERIFY_URL, data=payload, timeout=10)
        data = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("reCAPTCHA verify request failed: %s", exc)
        raise RecaptchaError("No se pudo verificar el captcha", 503) from exc

    if not data.get("success"):
        codes = data.get("error-codes") or []
        logger.warning("reCAPTCHA rejected: %s", codes)
        raise RecaptchaError("Captcha inválido o expirado. Probá de nuevo.")

    # reCAPTCHA v3 incluye score
    score = data.get("score")
    if score is not None:
        min_score = settings.recaptcha_min_score
        if float(score) < min_score:
            logger.warning("reCAPTCHA score bajo: %s < %s", score, min_score)
            raise RecaptchaError("No pasamos la verificación anti-bot. Probá de nuevo.")

    return data
