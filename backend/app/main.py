"""API de Vigil. Con MOCK=1 (por defecto si no hay PG_URI) devuelve datos de ejemplo
para que el frontend pueda avanzar sin backend real."""
import asyncio
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv()
MOCK = os.getenv("MOCK", "1" if not os.getenv("PG_URI") else "0") == "1"

app = FastAPI(title="Vigil API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "*")],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESIDENTS = [
    {"id": "S2", "name": "Lucía", "age": 81, "room": "104", "status": "attention", "hr": 92,
     "hr_baseline": 71, "eda_level": 1.8, "last_update": "2026-10-22T11:42:05Z",
     "hr_sparkline": [70, 72, 71, 75, 80, 86, 92]},
    {"id": "S3", "name": "Manuel", "age": 77, "room": "106", "status": "calm", "hr": 66,
     "hr_baseline": 68, "eda_level": 0.6, "last_update": "2026-10-22T11:42:05Z",
     "hr_sparkline": [67, 66, 68, 67, 66, 65, 66]},
    {"id": "S4", "name": "Carmen", "age": 88, "room": "110", "status": "calm", "hr": 74,
     "hr_baseline": 73, "eda_level": 0.9, "last_update": "2026-10-22T11:42:05Z",
     "hr_sparkline": [72, 73, 75, 74, 73, 74, 74]},
]
ALERTS = [{
    "id": 57, "resident_id": "S2", "resident_name": "Lucía", "created_at": "2026-10-22T11:42:10Z",
    "severity": "high", "state_estimate": "estres", "confidence": 0.83,
    "message": "Lucía lleva 12 minutos con la frecuencia cardíaca un 28 % por encima de su línea base "
               "y la actividad electrodérmica alta. No coincide con su fisioterapia. Conviene ir a verla.",
    "evidence": [{"label": "FC vs línea base", "value": "+28 %"},
                 {"label": "Duración", "value": "12 min"},
                 {"label": "Notas similares", "value": "2 episodios de dolor abdominal"}],
    "reasoning": ["Consulté la tendencia de 15 min en ClickHouse: FC media 92 vs base 71.",
                  "Revisé su agenda: no hay fisioterapia ahora.",
                  "Busqué notas parecidas: 2 episodios previos por dolor abdominal.",
                  "Feedback previo: 0 falsas alarmas en este patrón. Decido avisar."],
    "audio_url": None, "status": "open",
}]


class Feedback(BaseModel):
    verdict: str  # "real" | "false_alarm"
    note: str = ""
    author: str = ""


@app.get("/health")
def health():
    return {"ok": True, "mock": MOCK}


@app.get("/residents")
def residents():
    return RESIDENTS


@app.get("/residents/{rid}")
def resident(rid: str):
    r = next(x for x in RESIDENTS if x["id"] == rid)
    return {**r, "notes": [{"id": 12, "author": "Ana", "text": "Se agita antes de la fisioterapia de las 11.",
                            "created_at": "2026-10-20T10:55:00Z"}],
            "recent_alerts": [a for a in ALERTS if a["resident_id"] == rid]}


@app.get("/residents/{rid}/signals")
def signals(rid: str, minutes: int = 30):
    r = next(x for x in RESIDENTS if x["id"] == rid)
    return {"resident_id": rid, "points": [{"ts": f"2026-10-22T11:{35 + i}:00Z", "hr": h, "eda": r["eda_level"]}
                                           for i, h in enumerate(r["hr_sparkline"])]}


@app.get("/alerts")
def alerts(status: str | None = None):
    return [a for a in ALERTS if status is None or a["status"] == status]


@app.post("/alerts/{aid}/feedback")
def feedback(aid: int, fb: Feedback):
    a = next(x for x in ALERTS if x["id"] == aid)
    a["status"] = "confirmed" if fb.verdict == "real" else "dismissed"
    learned = ("Mantengo el umbral: patrón confirmado como real." if fb.verdict == "real"
               else "Subo el umbral de Lucía durante la fisioterapia (10:30–11:30).")
    return {"alert": a, "learned": learned}


@app.get("/shift-summary")
def shift_summary():
    return {"period": "22:00–06:00", "alerts": 4, "false_alarms": 1,
            "summary": "Noche tranquila salvo Lucía: 3 episodios de activación entre 2:00 y 4:00."}


@app.get("/benchmark")
def benchmark():
    return [
        {"variant": "naive_threshold", "detections": 0.71, "false_alarms_per_hour": 3.4, "latency_s": 2.1},
        {"variant": "personal_baseline", "detections": 0.80, "false_alarms_per_hour": 1.6, "latency_s": 2.3},
        {"variant": "with_feedback", "detections": 0.82, "false_alarms_per_hour": 0.7, "latency_s": 2.3},
    ]


@app.get("/events")
async def events():
    async def gen():
        i = 0
        while True:
            r = RESIDENTS[0]
            yield {"event": "resident_update",
                   "data": json.dumps({"id": r["id"], "status": r["status"], "hr": r["hr_sparkline"][i % 7]})}
            i += 1
            await asyncio.sleep(2)
    return EventSourceResponse(gen())
