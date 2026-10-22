"""Conexión a Aiven PostgreSQL + pgvector y consultas de memoria. [Pedro]"""
import psycopg
from pgvector.psycopg import register_vector

from .. import config

_conn = None


def conn():
    """Conexión única reutilizada (suficiente para el hackathon)."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(config.PG_URI, autocommit=True)
        register_vector(_conn)
    return _conn


def search_memories(user_id: str, query_embedding, initials: str | None = None,
                    interlocutor: str | None = None, k: int = 8):
    """Recuerdos más parecidos. Estrategia híbrida:
    1) coincidencia exacta de iniciales (lo más fiable),
    2) similitud de embedding (pgvector, distancia coseno <=>),
    3) bonus si coincide el interlocutor y por times_used (lo que más dice).
    TODO(Pedro): ajustar pesos si el benchmark lo pide.
    """
    sql = """
        SELECT id, phrase, interlocutor, state, times_used,
               (embedding <=> %(emb)s) AS dist
        FROM memories
        WHERE user_id = %(u)s
        ORDER BY
          (CASE WHEN initials = %(ini)s THEN 0 ELSE 1 END),
          (CASE WHEN interlocutor = %(who)s THEN 0 ELSE 1 END),
          (embedding <=> %(emb)s) - 0.01 * LEAST(times_used, 10)
        LIMIT %(k)s
    """
    with conn().cursor() as cur:
        cur.execute(sql, {"u": user_id, "emb": query_embedding, "ini": initials or "", "who": interlocutor or "", "k": k})
        return [dict(zip(["id", "phrase", "interlocutor", "state", "times_used", "dist"], r)) for r in cur.fetchall()]


def upsert_memory(user_id, phrase, initials, interlocutor, state, previous, embedding, source="choice"):
    """Aprendizaje: si la frase ya existe, sube times_used; si no, la inserta."""
    with conn().cursor() as cur:
        cur.execute("UPDATE memories SET times_used = times_used + 1, said_at = now() "
                    "WHERE user_id = %s AND phrase = %s RETURNING id", (user_id, phrase))
        if cur.fetchone():
            return "reforzada"
        cur.execute("INSERT INTO memories (user_id, phrase, initials, interlocutor, said_at, state, previous, source, embedding) "
                    "VALUES (%s,%s,%s,%s,now(),%s,%s,%s,%s)",
                    (user_id, phrase, initials, interlocutor, state, previous, source, embedding))
        return "nueva"


def log_step(user_id, request_id, step, tool, args, result_summary, ms):
    """Cada herramienta del agente → agent_log (traza de la demo + entrega)."""
    import json
    with conn().cursor() as cur:
        cur.execute("INSERT INTO agent_log (user_id, request_id, step, tool, args, result_summary, ms) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (user_id, request_id, step, tool, json.dumps(args, ensure_ascii=False), result_summary, ms))


def save_choice(c: dict):
    """TODO(Pedro): INSERT en choices (rank = posición de chosen en candidates, o NULL si editó)."""
    raise NotImplementedError


def get_profile(user_id):
    """TODO(Pedro): users + contacts + routines → dict para el prompt del agente."""
    raise NotImplementedError


def recent_trace(user_id, limit=20):
    """TODO(Pedro): SELECT de agent_log para GET /trace."""
    raise NotImplementedError
