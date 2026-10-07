#!/usr/bin/env python3
"""
xIA Backend API v2
Auth Google · LLM · cuotas · espejo Conversa (canal web)
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.config import get_settings, load_environment_config
from services.auth import (
    AuthError,
    issue_session_token,
    require_auth,
    verify_google_id_token,
)
from services.conversa import ConversaClient
from services.llm import LLMService
from services.recaptcha import RecaptchaError, verify_recaptcha_token
from services.safety import SAFE_REJECTION_REPLY, detect_prompt_injection
from services.store import Store

load_environment_config()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("xia")

try:
    from flask_cors import CORS

    cors_available = True
except ImportError:
    cors_available = False
    logger.warning("Flask-CORS no instalado")

try:
    from agents.notification_service import NotificationService

    notification_service = NotificationService()
except ImportError:
    notification_service = None

settings = get_settings()
store = Store(settings.database_path)
llm = LLMService(settings)
conversa = ConversaClient(settings)

app = Flask(__name__)
if cors_available:
    CORS(app)

app.config["SECRET_KEY"] = settings.secret_key
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

PUBLIC_DIR = os.path.abspath(os.path.join(backend_dir, "..", "public"))
auth = require_auth(settings, store)


@app.route("/")
def serve_frontend():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(PUBLIC_DIR, "assets"), filename)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "auth_required": settings.auth_required,
                "google_configured": bool(settings.google_client_id),
                "llm_configured": llm.is_configured,
                "conversa_configured": conversa.is_configured,
                "recaptcha_configured": bool(settings.recaptcha_site_key and settings.recaptcha_secret_key),
                "daily_message_limit": settings.daily_message_limit,
            },
        }
    )


@app.route("/api/auth/config", methods=["GET"])
def auth_config():
    return jsonify(
        {
            "google_client_id": settings.google_client_id or None,
            "auth_required": settings.auth_required,
            "daily_message_limit": settings.daily_message_limit,
            "recaptcha_site_key": settings.recaptcha_site_key or None,
            "recaptcha_required": bool(settings.recaptcha_secret_key),
        }
    )


@app.route("/api/auth/google", methods=["POST"])
def auth_google():
    data = request.get_json(silent=True) or {}
    id_token = (data.get("id_token") or data.get("credential") or "").strip()
    captcha_token = (data.get("captcha_token") or data.get("g-recaptcha-response") or "").strip()
    if not id_token:
        return jsonify({"error": "id_token requerido"}), 400

    try:
        verify_recaptcha_token(captcha_token, settings, remote_ip=request.remote_addr)
    except RecaptchaError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    try:
        profile = verify_google_id_token(id_token, settings.google_client_id)
    except AuthError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    user = store.upsert_google_user(
        google_sub=profile["google_sub"],
        email=profile["email"],
        name=profile.get("name"),
        picture=profile.get("picture"),
    )
    token = issue_session_token(user, settings)
    used = store.get_daily_usage(user["id"])

    return jsonify(
        {
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name"),
                "picture": user.get("picture"),
            },
            "quota": {
                "used": used,
                "limit": settings.daily_message_limit,
                "remaining": max(0, settings.daily_message_limit - used),
            },
        }
    )


@app.route("/api/me", methods=["GET"])
@auth
def me():
    user = request.xia_user  # type: ignore[attr-defined]
    used = store.get_daily_usage(user["id"])
    return jsonify(
        {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name"),
                "picture": user.get("picture"),
            },
            "quota": {
                "used": used,
                "limit": settings.daily_message_limit,
                "remaining": max(0, settings.daily_message_limit - used),
            },
        }
    )


@app.route("/api/chat", methods=["POST"])
@auth
def chat():
    user = request.xia_user  # type: ignore[attr-defined]
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Mensaje no puede estar vacío"}), 400
    if len(message) > settings.max_message_length:
        return jsonify(
            {"error": f"Mensaje demasiado largo (máx. {settings.max_message_length})"}
        ), 400

    injection = detect_prompt_injection(message)
    if injection:
        logger.warning(
            "Posible prompt injection user=%s reason=%s",
            user.get("email"),
            injection,
        )
        used = store.get_daily_usage(user["id"])
        # No gasta cuota ni llama al LLM; responde con rechazo seguro
        return jsonify(
            {
                "response": SAFE_REJECTION_REPLY,
                "mode": "blocked",
                "timestamp": datetime.now().isoformat(),
                "quota": {
                    "used": used,
                    "limit": settings.daily_message_limit,
                    "remaining": max(0, settings.daily_message_limit - used),
                },
            }
        )

    used = store.get_daily_usage(user["id"])
    if used >= settings.daily_message_limit:
        return (
            jsonify(
                {
                    "error": "quota_exceeded",
                    "message": "Alcanzaste el límite diario de consultas.",
                    "quota": {
                        "used": used,
                        "limit": settings.daily_message_limit,
                        "remaining": 0,
                    },
                }
            ),
            429,
        )

    conversation = store.get_or_create_conversation(user["id"])
    bot_on = conversa.bot_enabled(conversation.get("conversa_conversation_id"))

    user_msg = store.add_message(conversation["id"], "user", message)
    mirror_user = conversa.mirror_message(
        sender_id=user["google_sub"],
        email=user["email"],
        name=user.get("name"),
        picture=user.get("picture"),
        text=message,
        role="contact",
        external_conversation_id=conversation["id"],
        external_message_id=user_msg["id"],
    )
    if mirror_user and mirror_user.get("conversation_id"):
        store.set_conversa_conversation_id(
            conversation["id"], str(mirror_user["conversation_id"])
        )
        conversation = store.get_or_create_conversation(user["id"])
        bot_on = conversa.bot_enabled(conversation.get("conversa_conversation_id"))

    if not bot_on:
        used = store.increment_daily_usage(user["id"])
        return jsonify(
            {
                "response": (
                    "Un especialista del equipo está atendiendo esta conversación. "
                    "Te responderán por este mismo chat."
                ),
                "mode": "human",
                "timestamp": datetime.now().isoformat(),
                "quota": {
                    "used": used,
                    "limit": settings.daily_message_limit,
                    "remaining": max(0, settings.daily_message_limit - used),
                },
            }
        )

    history = store.recent_messages(conversation["id"], limit=20)
    llm_messages = [
        {"role": "assistant" if m["role"] == "assistant" else "user", "content": m["content"]}
        for m in history
        if m["role"] in ("user", "assistant")
    ]

    try:
        if llm.is_configured:
            reply = llm.chat(llm_messages)
        else:
            reply = (
                "El asistente LLM aún no está configurado. "
                "Definí LLM_API_KEY en el entorno. Mientras tanto, "
                "un especialista puede ver tu consulta en el inbox."
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error LLM")
        if notification_service:
            try:
                notification_service.send_error_notification(
                    error_type="LLM Error",
                    error_message=str(exc),
                    error_details="",
                    user_message=message,
                )
            except Exception:  # noqa: BLE001
                pass
        return jsonify({"error": "Error al generar respuesta"}), 500

    assistant_msg = store.add_message(conversation["id"], "assistant", reply)
    mirror_bot = conversa.mirror_message(
        sender_id=user["google_sub"],
        email=user["email"],
        name=user.get("name"),
        picture=user.get("picture"),
        text=reply,
        role="bot",
        external_conversation_id=conversation["id"],
        external_message_id=assistant_msg["id"],
    )
    if mirror_bot and mirror_bot.get("conversation_id"):
        store.set_conversa_conversation_id(
            conversation["id"], str(mirror_bot["conversation_id"])
        )

    used = store.increment_daily_usage(user["id"])
    return jsonify(
        {
            "response": reply,
            "mode": "bot",
            "timestamp": datetime.now().isoformat(),
            "quota": {
                "used": used,
                "limit": settings.daily_message_limit,
                "remaining": max(0, settings.daily_message_limit - used),
            },
        }
    )


@app.route("/api/chat/clear", methods=["POST"])
@auth
def clear_chat():
    user = request.xia_user  # type: ignore[attr-defined]
    conversation = store.get_or_create_conversation(user["id"])
    store.clear_conversation_messages(conversation["id"])
    return jsonify({"ok": True})


@app.route("/api/inbox/poll", methods=["GET"])
@auth
def poll_inbox():
    """Mensajes de operadores (Conversa → xIA) pendientes de mostrar en el chat."""
    user = request.xia_user  # type: ignore[attr-defined]
    messages = store.pull_pending_agent_messages(user["id"])
    return jsonify(
        {
            "messages": [
                {
                    "id": m["id"],
                    "content": m["content"],
                    "created_at": m["created_at"],
                    "role": "agent",
                }
                for m in messages
            ]
        }
    )


@app.route("/api/webhooks/conversa/outbound", methods=["POST"])
def conversa_outbound():
    """
    Recibe respuestas humanas desde Conversa cuando un operador escribe
    en una conversación channel=web.
    """
    api_key = request.headers.get("X-XIA-API-Key") or request.headers.get("X-API-Key")
    if settings.conversa_api_key and api_key != settings.conversa_api_key:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    sender_id = (data.get("senderId") or data.get("sender_id") or "").strip()
    text = (data.get("text") or data.get("content") or "").strip()
    if not sender_id or not text:
        return jsonify({"error": "senderId y text requeridos"}), 400

    user = store.get_user_by_google_sub(sender_id)
    if not user:
        return jsonify({"error": "Usuario xIA no encontrado", "ok": False}), 404

    conversation = store.get_or_create_conversation(user["id"])
    store.add_message(conversation["id"], "agent", text)
    pending = store.enqueue_agent_message(user["id"], text)

    return jsonify({"ok": True, "pending_id": pending["id"]})


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint no encontrado"}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    port = int(os.environ.get("PORT", 5000))

    print(f"🚀 xIA Backend v2 en puerto {port}")
    print(f"🔐 Auth required: {settings.auth_required}")
    print(f"🤖 LLM: {'OK' if llm.is_configured else 'NO CONFIGURADO'}")
    print(f"🪞 Conversa: {'OK' if conversa.is_configured else 'NO CONFIGURADO'}")
    print(f"📊 Límite diario: {settings.daily_message_limit}")

    app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
