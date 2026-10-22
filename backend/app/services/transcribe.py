"""OpenAI: transcribe lo que dice el interlocutor (botón Escuchar). Nunca se guarda el audio. [Pedro]"""
from openai import OpenAI

from .. import config


def _ext(b: bytes) -> str:
    """El navegador (Safari graba mp4, Chrome webm) no siempre pone bien el nombre: miramos los bytes."""
    if b[:4] == b"\x1aE\xdf\xa3":
        return "webm"
    if b[4:8] == b"ftyp":
        return "mp4"
    if b[:4] == b"OggS":
        return "ogg"
    if b[:4] == b"RIFF":
        return "wav"
    if b[:3] == b"ID3" or b[:2] in (b"\xff\xfb", b"\xff\xf3"):
        return "mp3"
    return "webm"


def transcribe(audio_bytes: bytes, filename="audio.webm") -> str:
    if len(audio_bytes) < 1500:  # grabación vacía o demasiado corta
        return ""
    client = OpenAI()
    r = client.audio.transcriptions.create(model=config.TRANSCRIBE_MODEL, language="en",
                                           file=(f"audio.{_ext(audio_bytes)}", audio_bytes))
    return r.text
