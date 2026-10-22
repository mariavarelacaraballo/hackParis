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
        try:
            register_vector(_conn)  # falla si la extensión aún no existe (antes de init_db)
        except Exception:
            pass
    return _conn


def reset():
    """Cierra la conexión (init_db la usa tras crear la extensión vector)."""
    global _conn
    if _conn is not None:
        _conn.close()
    _conn = None


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
               (CASE WHEN %(emb)s::vector IS NULL THEN NULL ELSE (embedding <=> %(emb)s::vector) END) AS dist
        FROM memories
        WHERE user_id = %(u)s
        ORDER BY
          (CASE WHEN initials = %(ini)s THEN 0 WHEN %(ini)s <> '' AND initials LIKE %(ini)s || '%%' THEN 1 ELSE 2 END),
          (CASE WHEN interlocutor = %(who)s THEN 0 ELSE 1 END),
          (CASE WHEN %(emb)s::vector IS NULL THEN 0 ELSE (embedding <=> %(emb)s::vector) END) - 0.01 * LEAST(times_used, 10)
        LIMIT %(k)s
    """
    with conn().cursor() as cur:
        cur.execute(sql, {"u": user_id, "emb": query_embedding, "ini": initials or "", "who": interlocutor or "", "k": k * 3})
        rows = [dict(zip(["id", "phrase", "interlocutor", "state", "times_used", "dist"], r)) for r in cur.fetchall()]
    # Quitar duplicados (la misma frase dicha varios días) sumando cuántas veces se usó
    seen = {}
    for r in rows:
        if r["phrase"] in seen:
            seen[r["phrase"]]["times_used"] += r["times_used"]
        else:
            seen[r["phrase"]] = r
    out = list(seen.values())
    if initials:  # con iniciales, solo recuerdos que encajan (evita que lo más usado, p. ej. 'me duele', lo tape todo)
        out = [r for r in out if (r.get("phrase") and _ini(r["phrase"]).startswith(initials))]
    return out[:k]


def _ini(phrase):
    import re
    return " ".join(w[0] for w in re.findall(r"[\wáéíóúñü]+", phrase.lower()))


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
    """Guarda cada elección: rank = posición de la elegida (1-5) o NULL si la editó."""
    import json
    rank = None if c.get("edited_text") else (c["candidates"].index(c["chosen"]) + 1 if c["chosen"] in c["candidates"] else None)
    with conn().cursor() as cur:
        cur.execute("INSERT INTO choices (user_id, input, candidates, chosen, edited_text, rank, tone, tone_was_changed) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (c["user_id"], json.dumps(c["input"], ensure_ascii=False), json.dumps(c["candidates"], ensure_ascii=False),
                     c["chosen"], c.get("edited_text"), rank, c.get("tone"), c.get("tone_was_changed", False)))


def get_profile(user_id) -> dict:
    """users + contacts + routines → dict para el prompt del agente y para sugerir interlocutor."""
    with conn().cursor() as cur:
        cur.execute("SELECT name, profile FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.execute("SELECT name, relation FROM contacts WHERE user_id = %s", (user_id,))
        contacts = dict(cur.fetchall())
        cur.execute("SELECT to_char(at_time, 'HH24:MI'), description FROM routines WHERE user_id = %s ORDER BY at_time", (user_id,))
        routines = [f"{t} {d}" for t, d in cur.fetchall()]
    name, profile = (row or ("el usuario", {}))
    return {"name": name, "profile": profile or {}, "contacts": contacts, "routines": routines}


def profile_text(p: dict) -> str:
    pr = p.get("profile", {})
    return (f"{p['name']}, {pr.get('age', '')} años, {pr.get('condition', '')}. "
            f"Contactos: {'; '.join(f'{k} ({v})' for k, v in p['contacts'].items())}. "
            f"Rutinas: {'; '.join(p['routines'])}. Intereses: {', '.join(pr.get('interests', []))}.")


def recent_trace(user_id, limit=20):
    with conn().cursor() as cur:
        cur.execute("SELECT tool, args, result_summary, ms, created_at FROM agent_log WHERE user_id = %s "
                    "ORDER BY id DESC LIMIT %s", (user_id, limit))
        return [{"tool": t, "args": a, "result_summary": r, "ms": m, "at": str(c)} for t, a, r, m, c in cur.fetchall()]
