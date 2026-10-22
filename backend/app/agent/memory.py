"""Memoria: embeddings (OpenAI) y aprendizaje. [Pedro]"""
from functools import lru_cache

from openai import OpenAI

from .. import config

_oa = None


def oa():
    global _oa
    if _oa is None:
        _oa = OpenAI()
    return _oa


@lru_cache(maxsize=2048)
def _embed_cached(text: str):
    return tuple(oa().embeddings.create(model=config.EMBED_MODEL, input=text).data[0].embedding)


def embed(text: str):
    import numpy as np
    return np.array(_embed_cached(text))


def memory_text(phrase, interlocutor=None, previous=None):
    """Texto que se embebe por recuerdo: incluye contexto para que la búsqueda semántica lo use."""
    return f"{interlocutor or ''}: {previous or ''} → {phrase}"


def initials_of(text: str) -> str:
    import re
    return " ".join(w[0] for w in re.findall(r"[\wáéíóúñü]+", text.lower()))


def learn_from_choice(user_id, chosen, interlocutor, state, previous, edited=False):
    """Aprendizaje: la frase elegida (o corregida) entra en memoria o refuerza la existente.
    TODO(Pedro): llamar desde routes/choice.py.
    """
    from ..db import postgres
    emb = embed(memory_text(chosen, interlocutor, previous))
    return postgres.upsert_memory(user_id, chosen, initials_of(chosen), interlocutor, state, previous, emb,
                                  source="correction" if edited else "choice")
