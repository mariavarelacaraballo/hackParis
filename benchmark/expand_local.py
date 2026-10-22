"""Versión local de expand() para que el benchmark funcione antes de que la API de Pedro esté lista.

Cuando el backend esté desplegado, define EXPAND_URL en .env y el benchmark llamará a la API real,
para que lo medido sea exactamente lo que se enseña en la demo.
"""
import json
import os
import re
import time

import anthropic

MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-4-5")
PRICE_IN = float(os.getenv("PRICE_IN_PER_MTOK", "3.0"))    # USD por millón de tokens de entrada
PRICE_OUT = float(os.getenv("PRICE_OUT_PER_MTOK", "15.0"))  # USD por millón de tokens de salida
_client = None

SYSTEM = (
    "Eres el motor de predicción de un comunicador para una persona con ELA que escribe con la mirada. "
    "Recibes las iniciales de cada palabra de la frase que quiere decir (y a veces alguna palabra completa). "
    "Devuelve las 5 frases completas más probables, en español, cuyas palabras empiecen por esas iniciales y en ese orden. "
    "Usa el contexto y los recuerdos si se dan. Responde SOLO con un array JSON de 5 strings."
)


def client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def build_prompt(initials, context=None, memories=None):
    parts = [f"Iniciales: {initials}"]
    if context:
        parts.append("Contexto:\n" + "\n".join(f"- {k}: {v}" for k, v in context.items() if v))
    if memories:
        parts.append("Frases que esta persona ha dicho antes en situaciones parecidas:\n" +
                     "\n".join(f"- {m}" for m in memories))
    return "\n\n".join(parts)


def expand(initials, context=None, memories=None):
    """Devuelve (candidatas, latencia_ms, coste_usd)."""
    t0 = time.perf_counter()
    msg = client().messages.create(
        model=MODEL, max_tokens=400, system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(initials, context, memories)}],
    )
    ms = (time.perf_counter() - t0) * 1000
    text = msg.content[0].text
    match = re.search(r"\[.*\]", text, re.S)
    try:
        cands = json.loads(match.group(0)) if match else []
    except json.JSONDecodeError:
        cands = []
    cost = msg.usage.input_tokens / 1e6 * PRICE_IN + msg.usage.output_tokens / 1e6 * PRICE_OUT
    return [str(c) for c in cands][:5], ms, cost
