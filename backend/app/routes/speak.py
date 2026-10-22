"""POST /speak: frase elegida + tono → voz clonada. [Pedro + Marc]"""
from fastapi import APIRouter

from .. import config
from ..models import SpeakIn

router = APIRouter()


@router.post("/speak")
def speak(body: SpeakIn):
    if config.MOCK and not config.ELEVENLABS_API_KEY:
        return {"audio_url": None, "cached": False, "latency_ms": 0}
    from ..services.voice import speak as tts
    out = tts(body.user_id, body.text, body.tone, body.language)
    try:
        from ..db import clickhouse
        clickhouse.log_metric(body.user_id, "speak", out["latency_ms"], 0.0, int(out["cached"]))
    except Exception:
        pass
    return out
