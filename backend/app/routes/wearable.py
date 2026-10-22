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
        clickhouse.insert_samples([(body.user_id, r["ts"], r["hr"], r["eda"], r["acc"], st["activation"], st["confidence"])
                                   for r in rows])
    return {"ok": True, "state": st}
