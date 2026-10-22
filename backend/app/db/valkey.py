"""Aiven Valkey (compatible con Redis): sesión, estado y cachés. [Pedro]

Claves:
  session:{user}        hash  interlocutor, last_utterance, updated_at
  state:{user}          hash  activation, confidence, suggested_tone
  cache:expand:{hash}   json  respuesta de /expand (TTL 1 h)
  cache:audio:{hash}    str   audio_url de /speak (TTL 24 h)
"""
import hashlib
import json

import redis

from .. import config

_r = None


class _MemoryStore:
    """Respaldo en memoria mientras Valkey no está configurado (misma interfaz mínima)."""
    def __init__(self):
        self.d = {}

    def hset(self, k, mapping):
        self.d.setdefault(k, {}).update({a: str(b) for a, b in mapping.items()})

    def hgetall(self, k):
        return dict(self.d.get(k, {}))

    def get(self, k):
        return self.d.get(k)

    def set(self, k, v, ex=None):
        self.d[k] = v


def r():
    global _r
    if _r is None:
        _r = redis.from_url(config.VALKEY_URI, decode_responses=True) if config.VALKEY_URI else _MemoryStore()
    return _r


def key_hash(*parts) -> str:
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]


def set_session(user_id, **fields):
    r().hset(f"session:{user_id}", mapping={k: v for k, v in fields.items() if v is not None})


def get_session(user_id) -> dict:
    return r().hgetall(f"session:{user_id}")


def set_state(user_id, state: dict):
    r().hset(f"state:{user_id}", mapping={k: str(v) for k, v in state.items()})


def get_state(user_id) -> dict:
    return r().hgetall(f"state:{user_id}") or {"activation": "baja", "confidence": "0", "suggested_tone": "neutro"}


def cache_get(kind, h):
    v = r().get(f"cache:{kind}:{h}")
    return json.loads(v) if v else None


def cache_set(kind, h, value, ttl):
    r().set(f"cache:{kind}:{h}", json.dumps(value, ensure_ascii=False), ex=ttl)
