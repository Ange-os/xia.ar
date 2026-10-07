"""
LEGADO — SimpleAgent (keywords).

Reemplazado en v2 por services.llm.LLMService + espejo Conversa.
Se mantiene solo por compatibilidad con imports antiguos; no usarlo.
"""


class SimpleAgent:
    def process_message(self, message: str) -> str:
        return (
            "Este agente fue reemplazado. Usá el backend v2 con LLM "
            f"(mensaje recibido: {message[:80]})."
        )
