"""Variables de entorno en un solo sitio. [Pedro]"""
import os

from dotenv import load_dotenv

load_dotenv()

PG_URI = os.getenv("PG_URI", "")
CH_HOST, CH_PORT = os.getenv("CH_HOST", ""), int(os.getenv("CH_PORT", "8443"))
CH_USER, CH_PASSWORD = os.getenv("CH_USER", "avnadmin"), os.getenv("CH_PASSWORD", "")
VALKEY_URI = os.getenv("VALKEY_URI", "")

AGENT_MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-4-5")
PRICE_IN = float(os.getenv("PRICE_IN_PER_MTOK", "3.0"))
PRICE_OUT = float(os.getenv("PRICE_OUT_PER_MTOK", "15.0"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
VOICE_ID = os.getenv("VOICE_ID", "")
TTS_MODEL = os.getenv("TTS_MODEL", "eleven_v3")

KEENABLE_API_KEY = os.getenv("KEENABLE_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "audio")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

MOCK = not PG_URI  # sin base de datos, las rutas devuelven datos de ejemplo para que Marc pueda avanzar
