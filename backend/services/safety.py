"""Filtros de seguridad: anti prompt-injection en mensajes de usuario."""

from __future__ import annotations

import re
from typing import Optional

# Patrones frecuentes de jailbreak / override (ES + EN)
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)",
    r"olvid(a|á|ar)\s+(todas?\s+)?(las\s+)?(instrucciones|reglas|reglas\s+anteriores)",
    r"ignor(a|á|ar)\s+(todas?\s+)?(las\s+)?(instrucciones|reglas)",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"revel(a|á|ar)\s+(tu\s+)?(system\s+)?prompt",
    r"revel(a|á|ar)\s+(tus\s+)?instrucciones",
    r"show\s+(me\s+)?(your\s+)?(hidden\s+)?instructions",
    r"developer\s+mode",
    r"jailbreak",
    r"\bDAN\b",
    r"act\s+as\s+(if\s+you\s+have\s+no|without)\s+restrictions",
    r"actu(a|á)\s+como\s+si\s+no\s+tuvieras\s+reglas",
    r"pretend\s+you\s+are\s+(not|no longer)\s+bound",
    r"disregard\s+(your\s+)?(safety|system)",
    r"new\s+system\s+prompt\s*:",
    r"\[\s*system\s*\]",
    r"<\s*system\s*>",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def detect_prompt_injection(message: str) -> Optional[str]:
    """
    Devuelve un motivo corto si el mensaje parece inyección; None si está OK.
    """
    text = (message or "").strip()
    if not text:
        return "empty"

    for pattern in _COMPILED:
        if pattern.search(text):
            return "injection_pattern"

    # Muchos delimitadores o roles falsos en un solo mensaje
    role_markers = len(re.findall(r"\b(system|assistant)\s*:", text, flags=re.IGNORECASE))
    if role_markers >= 2:
        return "role_spoofing"

    return None


SAFE_REJECTION_REPLY = (
    "No puedo cambiar mis reglas ni revelar instrucciones internas. "
    "Puedo ayudarte con los servicios de ABM Sistemas: integración, modernización, "
    "automatización o software a medida. ¿En qué te gustaría enfocarnos?"
)
