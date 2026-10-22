# Vigil — contexto para Claude Code

Hackathon (Accel AI Innovate, París). Entrega: 22 oct 2026, 15:00. Equipo: María, Pedro, Marc.

## Producto
Vigil: un agente que aprende cómo es cada residente de una residencia y avisa al cuidador cuando algo va mal,
aunque la persona no pueda decirlo (demencia, discapacidad, no verbal).

## Reto y criterios (20 % cada uno)
1. Problema real para un usuario claro. 2. Agente avanzado (multi-paso, autonomía, aprendizaje), no una sola llamada al LLM.
3. Datos en el núcleo (frescura, escala, grounding, memoria). 4. Evidencia medible frente a una línea base ingenua o sin datos.
5. Demo pulida y camino creíble a primeros usuarios.
Obligatorio: desplegar en Aiven Runtime y usar sus datos gestionados.

## Stack
- Backend: Python + FastAPI (`backend/`), desplegado en Aiven Runtime.
- Aiven ClickHouse: señales (`db/clickhouse.sql`). Aiven PostgreSQL: memoria (`db/postgres.sql`). Aiven Valkey: pub/sub en directo.
- Agente: Claude (API de Claude Platform, modelo en `AGENT_MODEL`) con tool use.
- Herramientas del agente: tendencia en ClickHouse, agenda/medicación/feedback en Postgres, notas similares (embeddings OpenAI),
  Keenable (búsqueda web con fuentes sobre medicación y causas probables), crear alerta.
- Voz: ElevenLabs `eleven_v3` con audio tags; cachear audios.
- Frontend: repo aparte `vigil-frontend` hecho en Lovable; consume esta API (contrato en `docs/api.md`). NO usa Supabase para datos.
- Supabase: solo login de cuidadores y Storage de MP3.
- Dataset: WESAD (ECG, EDA, ACC del pecho a 700 Hz; etiquetas baseline/stress/amusement; 15 sujetos). Cada sujeto = un residente ficticio.

## Reglas
- `docs/api.md` es el contrato. Si cambias la API, cámbialo primero.
- Cada persona en su carpeta y su rama: María `data/` + `benchmark/`, Pedro `backend/`, Marc frontend + pitch.
- Claves solo en `.env` (ver `.env.example`). Nunca subir `.env` ni datos de WESAD.
- Todas las consultas del agente se registran en `agent_log` (de ahí sale la entrega "data layer in action").
- El agente nunca diagnostica: da contexto con datos y fuentes citadas, y el cuidador decide.
- Prioridad: que funcione de punta a punta antes que añadir funciones. 13:30 congelamos código.
