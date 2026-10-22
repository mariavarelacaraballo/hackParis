"""POST /context: actualiza la sesión y precalcula sugerencias sin escribir nada. [Pedro]"""
from fastapi import APIRouter

from .. import config
from ..models import ContextIn

router = APIRouter()


@router.post("/context")
def set_context(body: ContextIn):
    if config.MOCK:
        return {"ok": True, "suggestions": ["Bien, algo cansado. ¿Y tú?", "¿Qué tal el trabajo?", "¿Cómo están Pablo y Lola?"]}
    from ..db import valkey
    valkey.set_session(body.user_id, interlocutor=body.interlocutor, last_utterance=body.last_utterance)
    # TODO(Pedro): llamar al agente con input vacío ("sin iniciales: propón lo más probable") → 3 sugerencias.
    return {"ok": True, "suggestions": []}
