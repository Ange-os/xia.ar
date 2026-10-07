"""Cliente espejo hacia Conversa Platform (canal web)."""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

from services.config import Settings

logger = logging.getLogger(__name__)


class ConversaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.conversa_api_url and self.settings.conversa_api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-XIA-API-Key": self.settings.conversa_api_key,
        }

    def mirror_message(
        self,
        *,
        sender_id: str,
        email: str,
        name: Optional[str],
        text: str,
        role: str,
        external_conversation_id: str,
        external_message_id: str,
        picture: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Espeja un mensaje a Conversa.
        role: contact | bot | agent
        """
        if not self.is_configured:
            logger.warning("Conversa no configurado; se omite espejo")
            return None

        payload = {
            "senderId": sender_id,
            "email": email,
            "name": name,
            "picture": picture,
            "text": text,
            "role": role,
            "externalConversationId": external_conversation_id,
            "externalMessageId": external_message_id,
            "source": "xia.ar",
        }
        url = f"{self.settings.conversa_api_url}/webhooks/xia/inbound"

        try:
            response = requests.post(
                url, json=payload, headers=self._headers(), timeout=20
            )
            if response.status_code >= 400:
                logger.error(
                    "Conversa mirror error %s: %s",
                    response.status_code,
                    response.text[:500],
                )
                return None
            data = response.json()
            logger.info(
                "Conversa mirror ok conversation_id=%s role=%s",
                data.get("conversation_id"),
                role,
            )
            return data
        except requests.RequestException as exc:
            logger.error("Conversa mirror request failed: %s", exc)
            return None

    def get_conversation(self, conversation_id: str) -> Optional[dict[str, Any]]:
        if not self.is_configured or not conversation_id:
            return None
        url = f"{self.settings.conversa_api_url}/conversations/{conversation_id}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code >= 400:
                return None
            return response.json()
        except requests.RequestException as exc:
            logger.error("Conversa get conversation failed: %s", exc)
            return None

    def bot_enabled(self, conversation_id: Optional[str]) -> bool:
        """True si el bot puede responder (tag bot-activo o sin bot-apagado)."""
        if not conversation_id:
            return True
        data = self.get_conversation(conversation_id)
        if not data:
            return True
        tags = {t.get("name") for t in data.get("tags") or []}
        if "bot-apagado" in tags:
            return False
        status = data.get("status")
        if status == "pending_human":
            return False
        return True
