"""POST /wearable/samples: muestras de la pulsera → ClickHouse + estado en Valkey. [María + Pedro]

Mismo formato que tendría un agregador (Terra) o una app con HealthKit / Health Connect.
"""
from fastapi import APIRouter

from .. import config
from ..models import SamplesIn

router = APIRouter()


@router.post("/wearable/samples")
def samples(body: SamplesIn):
    from ..services.state import estimate
    rows = [s.model_dump() for s in body.samples]
    st = estimate(rows)
    if not config.MOCK:
        from ..db import clickhouse, valkey
        valkey.set_state(body.user_id, st)
        try:
            from datetime import datetime
            clickhouse.insert_samples([(body.user_id, datetime.fromisoformat(r["ts"].replace("Z", "+00:00")), r["hr"], r["eda"],
                                        r["acc"], st["activation"], float(st["confidence"])) for r in rows])
        except Exception as e:  # ClickHouse opcional: la demo sigue funcionando sin él
            print("ClickHouse no disponible:", e)
    return {"ok": True, "state": st}
