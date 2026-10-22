"""Crea las tablas en Aiven PostgreSQL y ClickHouse. Ejecutar una vez. [Pedro]
python backend/scripts/init_db.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.db import clickhouse, postgres  # noqa: E402

with postgres.conn().cursor() as cur:
    cur.execute((ROOT / "db/postgres.sql").read_text())
print("PostgreSQL OK")

for stmt in (ROOT / "db/clickhouse.sql").read_text().split(";"):
    body = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
    if body:
        clickhouse.client().command(body)
print("ClickHouse OK")
