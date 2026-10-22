"""Carga el perfil y la memoria de Lucas (data/lucas/) en PostgreSQL con embeddings. [Pedro]
python data/lucas/build_corpus.py && python backend/scripts/seed_memory.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.agent.memory import embed, initials_of, memory_text  # noqa: E402
from backend.app.db import postgres  # noqa: E402

profile = json.loads((ROOT / "data/lucas/profile.json").read_text())
with postgres.conn().cursor() as cur:
    cur.execute("INSERT INTO users (id, name, language, profile) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                (profile["user_id"], profile["name"], profile["language"], json.dumps(profile, ensure_ascii=False)))
    for name, rel in profile["contacts"].items():
        cur.execute("INSERT INTO contacts (user_id, name, relation) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                    (profile["user_id"], name, rel))
    cur.execute("DELETE FROM routines WHERE user_id = %s", (profile["user_id"],))  # idempotente
    for r in profile["routines"]:
        t, desc = r.split(" ", 1)
        cur.execute("INSERT INTO routines (user_id, at_time, description) VALUES (%s,%s,%s)", (profile["user_id"], t, desc))

rows = [json.loads(l) for l in open(ROOT / "data/lucas/memory.jsonl", encoding="utf-8")]
with postgres.conn().cursor() as cur:
    cur.execute("DELETE FROM memories WHERE user_id = %s AND source = 'corpus'", (profile["user_id"],))  # idempotente
    for r in rows:
        cur.execute(
            "INSERT INTO memories (user_id, phrase, initials, interlocutor, said_at, state, previous, source, embedding) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,'corpus',%s)",
            (r["user_id"], r["phrase"], initials_of(r["phrase"]), r["interlocutor"], f"{r['date']} {r['time']}",
             r["state"], r["previous"], embed(memory_text(r["phrase"], r["interlocutor"], r["previous"]))))
print(f"{len(rows)} recuerdos cargados")
# Nota: solo memory.jsonl (días 1-5). test.jsonl NO se carga: es el examen del benchmark.
