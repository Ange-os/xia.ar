"""Carga de configuración (.env) para desarrollo y producción."""

from __future__ import annotations

import os
from dataclasses import dataclass


def load_environment_config() -> bool:
    """Detecta entorno y carga variables desde .env."""
    is_production = os.path.exists("/home/xia")

    if is_production:
        env_path = os.path.expanduser("~/.config/xia/.env")
        print("🏭 Modo PRODUCCIÓN detectado")
    else:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        print("💻 Modo DESARROLLO detectado")

    print(f"📁 Buscando archivo .env en: {env_path}")

    if not os.path.exists(env_path):
        print(f"⚠️ Archivo .env no encontrado en: {env_path}")
        return False

    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
        print(f"✅ Variables de entorno cargadas desde: {env_path}")
        return True
    except ImportError:
        print("⚠️ python-dotenv no instalado. Usando variables del sistema.")
        return False


@dataclass(frozen=True)
class Settings:
    secret_key: str
    google_client_id: str
    jwt_expire_hours: int
    daily_message_limit: int
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    conversa_api_url: str
    conversa_api_key: str
    database_path: str
    auth_required: bool
    recaptcha_site_key: str
    recaptcha_secret_key: str
    recaptcha_min_score: float
    max_message_length: int


def get_settings() -> Settings:
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    default_db = os.path.join(backend_dir, "data", "xia.db")

    return Settings(
        secret_key=os.environ.get("SECRET_KEY", "dev-key-change-in-production"),
        google_client_id=os.environ.get("GOOGLE_CLIENT_ID", "").strip(),
        jwt_expire_hours=int(os.environ.get("JWT_EXPIRE_HOURS", "168")),
        daily_message_limit=int(os.environ.get("DAILY_MESSAGE_LIMIT", "20")),
        llm_api_key=os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", ""),
        llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com"),
        llm_model=os.environ.get("LLM_MODEL", "deepseek-chat"),
        conversa_api_url=os.environ.get("CONVERSA_API_URL", "").rstrip("/"),
        conversa_api_key=os.environ.get("CONVERSA_API_KEY", "").strip(),
        database_path=os.environ.get("DATABASE_PATH", default_db),
        auth_required=os.environ.get("AUTH_REQUIRED", "true").lower() in ("1", "true", "yes"),
        recaptcha_site_key=os.environ.get("RECAPTCHA_SITE_KEY", "").strip(),
        recaptcha_secret_key=os.environ.get("RECAPTCHA_SECRET_KEY", "").strip(),
        recaptcha_min_score=float(os.environ.get("RECAPTCHA_MIN_SCORE", "0.5")),
        max_message_length=int(os.environ.get("MAX_MESSAGE_LENGTH", "1000")),
    )
