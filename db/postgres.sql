-- Aiven PostgreSQL: memoria del usuario. Ejecutar con backend/scripts/init_db.py
-- Requiere la extensión pgvector (en Aiven: disponible; si falla CREATE EXTENSION, avisar a mentores de Aiven).
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
  id          TEXT PRIMARY KEY,           -- 'lucas'
  name        TEXT NOT NULL,
  language    TEXT DEFAULT 'es',
  voice_id    TEXT,                       -- ElevenLabs
  profile     JSONB DEFAULT '{}'::jsonb   -- condición, intereses...
);

CREATE TABLE IF NOT EXISTS contacts (
  user_id     TEXT REFERENCES users(id),
  name        TEXT,
  relation    TEXT,                       -- 'hija', 'enfermera de noche'...
  language    TEXT DEFAULT 'es',
  PRIMARY KEY (user_id, name)
);

CREATE TABLE IF NOT EXISTS routines (
  id          SERIAL PRIMARY KEY,
  user_id     TEXT REFERENCES users(id),
  at_time     TIME,
  description TEXT                        -- '18:00 visita de Ana'
);

-- Cada frase dicha o elegida, con su contexto. Es lo que busca search_memory.
CREATE TABLE IF NOT EXISTS memories (
  id            SERIAL PRIMARY KEY,
  user_id       TEXT REFERENCES users(id),
  phrase        TEXT NOT NULL,
  initials      TEXT NOT NULL,            -- 'm d l e' (índice para búsqueda exacta por iniciales)
  interlocutor  TEXT,
  said_at       TIMESTAMPTZ,              -- fecha simulada en el corpus; now() en la app
  state         TEXT,                     -- 'calma' | 'activación'
  previous      TEXT,                     -- lo que le acababan de decir
  times_used    INT DEFAULT 1,            -- sube con cada elección (aprendizaje)
  source        TEXT DEFAULT 'corpus',    -- 'corpus' | 'choice' | 'correction'
  embedding     vector(1536)              -- OpenAI text-embedding-3-small de "interlocutor: previous → phrase"
);
CREATE INDEX IF NOT EXISTS memories_user_initials ON memories (user_id, initials);
-- Índice vectorial (opcional con <10k filas): CREATE INDEX ON memories USING hnsw (embedding vector_cosine_ops);

-- Cada elección/corrección en la app: fuente del aprendizaje y de la métrica real de uso.
CREATE TABLE IF NOT EXISTS choices (
  id                SERIAL PRIMARY KEY,
  user_id           TEXT,
  input             TEXT,
  candidates        JSONB,
  chosen            TEXT,
  edited_text       TEXT,
  rank              INT,                  -- posición de la elegida (1-5) o NULL si la editó/escribió
  tone              TEXT,
  tone_was_changed  BOOLEAN,
  created_at        TIMESTAMPTZ DEFAULT now()
);

-- Traza del agente: panel lateral de la demo + entrega "data layer in action".
CREATE TABLE IF NOT EXISTS agent_log (
  id              SERIAL PRIMARY KEY,
  user_id         TEXT,
  request_id      TEXT,
  step            INT,
  tool            TEXT,
  args            JSONB,
  result_summary  TEXT,
  ms              INT,
  created_at      TIMESTAMPTZ DEFAULT now()
);
