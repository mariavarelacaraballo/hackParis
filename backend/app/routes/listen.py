"""POST /listen: audio del navegador → texto (se guarda solo el texto). [Pedro]"""
from fastapi import APIRouter, File, Form, UploadFile

from .. import config

router = APIRouter()


@router.post("/listen")
async def listen(audio: UploadFile = File(...), user_id: str = Form("lucas")):
    if config.MOCK:
        return {"text": "¡Hola papá! ¿Qué tal el día?"}
    from ..db import valkey
    from ..services.transcribe import transcribe
    text = transcribe(await audio.read(), audio.filename or "audio.webm")
    valkey.set_session(user_id, last_utterance=text)
    return {"text": text}
