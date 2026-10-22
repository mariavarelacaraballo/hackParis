"""Bucle del agente (Claude con tool use). [Pedro]

expand() es LA función que usan la app (/expand) y el benchmark (vía EXPAND_URL).
"""
import json
import time
import uuid

import anthropic

from .. import config
from .prompts import SYSTEM
from .tools import TOOLS, run_tool

MAX_ROUNDS = 4
_client = None


def client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def expand(user_id: str, mode: str, user_input, context: dict, state: dict, profile: str = "",
           fixed_memories: list[str] | None = None, log=None) -> dict:
    """Devuelve {candidates, suggested_tone, trace, latency_ms, cost_eur}.

    log: función (step, tool, args, summary, ms) para escribir en agent_log (None en benchmark).
    """
    t0 = time.perf_counter()
    request_id = uuid.uuid4().hex[:8]
    ctx = {"user_id": user_id, "context": context, "state": state, "fixed_memories": fixed_memories}
    shown = user_input if isinstance(user_input, str) else " + ".join(user_input)
    messages = [{"role": "user", "content": f"Modo: {mode}. Entrada del usuario: {shown}"}]
    system = SYSTEM.format(name=profile.split()[0] if profile else "el usuario", profile=profile)
    trace, cost = [], 0.0

    for step in range(MAX_ROUNDS):
        # En la última ronda forzamos la herramienta final para no pasarnos de latencia.
        tool_choice = {"type": "tool", "name": "propose_phrases"} if step == MAX_ROUNDS - 1 else {"type": "any"}
        msg = client().messages.create(model=config.AGENT_MODEL, max_tokens=600, system=system,
                                       tools=TOOLS, tool_choice=tool_choice, messages=messages)
        cost += msg.usage.input_tokens / 1e6 * config.PRICE_IN + msg.usage.output_tokens / 1e6 * config.PRICE_OUT
        messages.append({"role": "assistant", "content": msg.content})
        results = []
        for block in msg.content:
            if block.type != "tool_use":
                continue
            if block.name == "propose_phrases":
                out = block.input
                return {
                    "candidates": out["candidates"][:5],
                    "suggested_tone": out.get("suggested_tone", "neutro"),
                    "trace": trace + [{"tool": "propose_phrases", "args": {}, "result_summary": out.get("why", ""), "ms": 0}],
                    "latency_ms": int((time.perf_counter() - t0) * 1000),
                    "cost_eur": round(cost * 0.92, 5),  # USD→EUR aproximado; TODO ajustar
                    "request_id": request_id,
                }
            t1 = time.perf_counter()
            result = run_tool(block.name, block.input, ctx)
            ms = int((time.perf_counter() - t1) * 1000)
            summary = result[:120]
            trace.append({"tool": block.name, "args": block.input, "result_summary": summary, "ms": ms})
            if log:
                log(step, block.name, block.input, summary, ms)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": results})

    return {"candidates": [], "suggested_tone": "neutro", "trace": trace,
            "latency_ms": int((time.perf_counter() - t0) * 1000), "cost_eur": round(cost * 0.92, 5)}


# TODO(Pedro), optimización si la latencia pasa de ~3 s:
#  - Prefetch en /context: search_memory del interlocutor y guardarlo en ctx para ahorrar una ronda.
#  - Caché en Valkey por (user, input, interlocutor).
#  - Probar un modelo más rápido para /expand y dejar el grande para /context.
