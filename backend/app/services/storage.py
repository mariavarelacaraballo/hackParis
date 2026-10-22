"""Supabase Storage para los MP3 (opcional). Sin Supabase → base64 en la respuesta. [Pedro]"""
import base64

from .. import config


def upload_audio(name: str, audio: bytes) -> dict:
    if not config.SUPABASE_URL:
        return {"audio_b64": base64.b64encode(audio).decode()}
    # TODO(Pedro): from supabase import create_client; client.storage.from_(bucket).upload(f"{name}.mp3", audio,
    #              {"content-type": "audio/mpeg", "upsert": "true"}); devolver {"audio_url": public_url}
    return {"audio_b64": base64.b64encode(audio).decode()}
