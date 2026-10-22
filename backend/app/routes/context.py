"""POST /context: actualiza la sesión, sugiere interlocutor y precalcula frases sin escribir nada. [Pedro]"""
import time

from fastapi import APIRouter

from .. import config
from ..models import ContextIn

router = APIRouter()


def suggest_interlocutor(profile: dict) -> str | None:
    """Por la rutina: el contacto mencionado en la rutina más cercana a la hora actual (±60 min)."""
    now = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))
    best, best_d = None, 61
    for r in profile.get("routines", []):
        hh, mm = map(int, r.split(" ", 1)[0].split(":"))
        d = abs(hh * 60 + mm - now)
        for name in profile.get("contacts", {}):
            if name in r and d < best_d:
                best, best_d = name, d
    return best


@router.post("/context")
def set_context(body: ContextIn):
    if config.MOCK:
        return {"ok": True, "suggested_interlocutor": "Ana",
                "suggestions": ["Bien, algo cansado. ¿Y tú?", "¿Qué tal el trabajo?", "¿Cómo están Pablo y Lola?"]}
    from ..agent.agent import expand as agent_expand
    from ..db import postgres, valkey

    profile = postgres.get_profile(body.user_id)
    who = body.interlocutor or suggest_interlocutor(profile)
    valkey.set_session(body.user_id, interlocutor=who, last_utterance=body.last_utterance)
    valkey.add_turn(body.user_id, who or "otra persona", body.last_utterance)
    context = {**valkey.get_session(body.user_id), "time": time.strftime("%H:%M"),
               "conversation": valkey.get_history(body.user_id)}
    out = agent_expand(body.user_id, "context", "(no initials: propose the most likely sentences right now, in English)", context,
                       valkey.get_state(body.user_id), profile=postgres.profile_text(profile),
                       log=lambda step, tool, args, summary, ms: postgres.log_step(body.user_id, "", step, tool, args, summary, ms))
    return {"ok": True, "suggested_interlocutor": who, "suggestions": out["candidates"][:3],
            "suggested_tone": out.get("suggested_tone", "neutro"), "trace": out.get("trace", [])}
