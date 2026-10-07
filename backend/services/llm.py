"""Cliente LLM (compatible OpenAI / DeepSeek)."""

from __future__ import annotations

import logging
from typing import Any

import requests

from services.config import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sos el asistente de xIA, consultoría especializada en sistemas de programación.
Respondé en español, de forma clara y práctica.
Ayudás con arquitectura, stack, APIs, bases de datos, deploy, seguridad y producto.
Si falta contexto, pedí detalles concretos.
No inventes hechos sobre el negocio del usuario.
Si la consulta requiere intervención humana, sugerí que un especialista del equipo la revise."""


class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.llm_api_key)

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not self.is_configured:
            raise RuntimeError(
                "LLM no configurado. Definí LLM_API_KEY (o DEEPSEEK_API_KEY) en el .env"
            )

        payload = {
            "model": self.settings.llm_model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            "temperature": 0.4,
        }
        url = f"{self.settings.llm_base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        logger.info("LLM request model=%s messages=%s", self.settings.llm_model, len(messages))
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code >= 400:
            logger.error("LLM error %s: %s", response.status_code, response.text[:500])
            raise RuntimeError(f"Error del LLM ({response.status_code})")

        data: dict[str, Any] = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Respuesta LLM inválida") from exc

        return (content or "").strip() or "No pude generar una respuesta. Probá reformular la consulta."
