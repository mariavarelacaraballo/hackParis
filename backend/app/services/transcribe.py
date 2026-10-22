"""OpenAI: transcribe lo que dice el interlocutor (botón Escuchar). Nunca se guarda el audio. [Pedro]"""
from openai import OpenAI

from .. import config


def transcribe(audio_bytes: bytes, filename="audio.webm") -> str:
    client = OpenAI()
    r = client.audio.transcriptions.create(model=config.TRANSCRIBE_MODEL, file=(filename, audio_bytes))
    return r.text
