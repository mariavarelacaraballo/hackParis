# Contrato de API (v1)

Base URL: la de Aiven Runtime (en local `http://localhost:8000`). Todo en JSON.
Si cambias algo aquí, avisa al equipo antes de hacer push.

## GET /residents
Lista de residentes con su estado actual.
```json
[
  {
    "id": "S2",
    "name": "Lucía",
    "age": 81,
    "room": "104",
    "status": "attention",
    "hr": 92,
    "hr_baseline": 71,
    "eda_level": 1.8,
    "last_update": "2026-10-22T11:42:05Z",
    "hr_sparkline": [70, 72, 71, 75, 80, 86, 92]
  }
]
```
`status`: `calm` | `attention` | `alert`

## GET /residents/{id}
Igual que arriba más notas y alertas recientes.
```json
{
  "id": "S2",
  "name": "Lucía",
  "notes": [
    {"id": 12, "author": "Ana", "text": "Se agita antes de la fisioterapia de las 11.", "created_at": "2026-10-20T10:55:00Z"}
  ],
  "recent_alerts": [ "…objetos Alert…" ]
}
```

## GET /residents/{id}/signals?minutes=30
Serie para la gráfica.
```json
{"resident_id": "S2", "points": [{"ts": "2026-10-22T11:40:00Z", "hr": 88, "eda": 1.6}]}
```

## GET /alerts?status=open
```json
[
  {
    "id": 57,
    "resident_id": "S2",
    "resident_name": "Lucía",
    "created_at": "2026-10-22T11:42:10Z",
    "severity": "high",
    "state_estimate": "estres",
    "confidence": 0.83,
    "message": "Lucía lleva 12 minutos con la frecuencia cardíaca un 28 % por encima de su línea base y la actividad electrodérmica alta. No coincide con su fisioterapia. Conviene ir a verla.",
    "evidence": [
      {"label": "FC vs línea base", "value": "+28 %"},
      {"label": "Duración", "value": "12 min"},
      {"label": "Notas similares", "value": "2 episodios de dolor abdominal"}
    ],
    "reasoning": [
      "Consulté la tendencia de 15 min en ClickHouse: FC media 92 vs base 71.",
      "Revisé su agenda: no hay fisioterapia ahora.",
      "Busqué notas parecidas: 2 episodios previos por dolor abdominal.",
      "Feedback previo: 0 falsas alarmas en este patrón. Decido avisar."
    ],
    "audio_url": "https://…/alert_57.mp3",
    "status": "open"
  }
]
```
`severity`: `low` | `medium` | `high` · `status`: `open` | `confirmed` | `dismissed`

## POST /alerts/{id}/feedback
```json
{"verdict": "real", "note": "Tenía dolor de tripa", "author": "Ana"}
```
`verdict`: `real` | `false_alarm`
Respuesta: la alerta actualizada + qué ha aprendido el agente:
```json
{"alert": {"…": "…"}, "learned": "Subo el umbral de Lucía durante la fisioterapia (10:30–11:30)."}
```

## GET /events  (Server-Sent Events)
Stream en directo para que el panel se actualice solo.
```
event: resident_update
data: {"id": "S2", "status": "attention", "hr": 92}

event: new_alert
data: {"…objeto Alert…"}
```

## GET /shift-summary
```json
{"period": "22:00–06:00", "summary": "Noche tranquila salvo Lucía: 3 episodios de activación entre 2:00 y 4:00…", "alerts": 4, "false_alarms": 1}
```

## POST /demo/replay  (solo para la demo)
Reproduce un tramo de WESAD como si fuera en directo.
```json
{"resident_id": "S2", "scenario": "stress", "speed": 10}
```

## GET /benchmark
Resultados para la entrega de evidencia.
```json
[
  {"variant": "naive_threshold", "detections": 0.71, "false_alarms_per_hour": 3.4, "latency_s": 2.1},
  {"variant": "personal_baseline", "detections": 0.80, "false_alarms_per_hour": 1.6, "latency_s": 2.3},
  {"variant": "with_feedback", "detections": 0.82, "false_alarms_per_hour": 0.7, "latency_s": 2.3}
]
```
(Los números son de ejemplo; los reales salen de `benchmark/`.)
