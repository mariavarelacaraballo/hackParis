# NeuroVoice

> NeuroVoice convierte cuatro letras en la frase que una persona con ELA quiere decir, con su memoria y su voz.

Hackathon Accel AI Innovate (París) · entrega 22 oct 2026, 15:30 (objetivo 15:15) · María, Pedro, Marc.
Plan completo: ver el "Plan maestro" (doc compartido) y `docs/`.

## Mapa del repo (dueño entre corchetes)

```
docs/                 contrato, arquitectura, entregas y checklist        [todos]
db/                   esquemas SQL de Aiven PostgreSQL y ClickHouse       [Pedro]
backend/app/          API FastAPI desplegada en Aiven Runtime             [Pedro]
  config.py           variables de entorno
  models.py           esquemas de entrada/salida (= docs/api.md)
  db/                 conexiones: postgres.py, clickhouse.py, valkey.py
  agent/              el agente: prompts, tools, bucle de tool use, memoria
  services/           voz (ElevenLabs), transcripción (OpenAI), estado, web (Keenable), storage (Supabase)
  routes/             un archivo por endpoint
backend/scripts/      init_db, seed_memory, replay_wesad                  [Pedro / María]
data/lucas/           usuario ficticio: perfil, memoria y test            [María]
data/estado/          modelo de estado (pipeline del TFG sobre WESAD)     [María]
benchmark/            ablación, curva de aprendizaje y métrica de tono    [María]
```
El frontend vive en el repo de Lovable (Marc). Sus prompts: `docs/lovable_prompts.md`.

## Arrancar en local
```bash
cp .env.example .env                  # rellenar claves (nunca subir .env)
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/scripts/init_db.py     # crea tablas en Aiven
python data/lucas/build_corpus.py     # genera el corpus de Lucas
python backend/scripts/seed_memory.py # carga la memoria con embeddings
uvicorn backend.app.main:app --reload # http://localhost:8000/docs
```

## Reglas
1. Cada uno en su carpeta y su rama (`maria`, `pedro`, `marc`); merge a `main` cada hora; `main` se despliega.
2. Claves solo en `.env`. Nada de datos de pacientes (solo WESAD y el corpus sintético).
3. Si cambias la API, cambia antes `docs/api.md` y avisa.
4. 14:30 congelamos código. Checklist en `docs/checklist.md`.
