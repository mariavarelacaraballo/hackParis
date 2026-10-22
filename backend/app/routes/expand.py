"""POST /expand: iniciales/pictos → 5 frases. Es la ruta que mide el benchmark. [Pedro]"""
import time

from fastapi import APIRouter

from .. import config
from ..models import ExpandIn

router = APIRouter()


@router.post("/expand")
def expand(body: ExpandIn):
    if config.MOCK:
        return {"candidates": ["Me duele la espalda", "Me duele la espalda, llama a la enfermera",
                               "Me duele la espalda otra vez", "Me duele la espalda desde ayer", "Me duele la espalda mucho"],
                "suggested_tone": "molesto", "trace": [], "latency_ms": 0, "cost_eur": 0.0}
    from ..agent.agent import expand as agent_expand
    from ..db import clickhouse, postgres, valkey

    t0 = time.perf_counter()
    given = body.context.model_dump(exclude_none=True) if body.context else {}
    if body.memories is not None:
        # Modo benchmark: aislado. Solo el contexto y la memoria que manda el benchmark (ablación limpia).
        context, state = {k: v for k, v in given.items() if k != "state"}, ({"activation": given["state"]} if "state" in given else {})
    else:
        context = {**valkey.get_session(body.user_id), **given}
        context.setdefault("time", time.strftime("%H:%M"))
        state = valkey.get_state(body.user_id)

    # TODO(Pedro): caché en Valkey por (user, input, interlocutor) — salvo si viene 'memories' (benchmark).
    out = agent_expand(body.user_id, body.mode, body.input, context, state,
                       profile="Lucas, 58 años, ELA",  # TODO: postgres.get_profile(body.user_id)
                       fixed_memories=body.memories,
                       log=None if body.memories is not None else
                       (lambda step, tool, args, summary, ms: postgres.log_step(body.user_id, "", step, tool, args, summary, ms)))
    try:
        clickhouse.log_metric(body.user_id, "expand", out["latency_ms"], out["cost_eur"], 0)
    except Exception:
        pass
    return out
