-- Aiven PostgreSQL: memoria del agente
CREATE TABLE IF NOT EXISTS residents (
  id            TEXT PRIMARY KEY,          -- = sujeto de WESAD (S2, S3…)
  name          TEXT NOT NULL,
  age           INT,
  room          TEXT,
  language      TEXT DEFAULT 'es',
  hr_baseline   REAL,
  eda_baseline  REAL,
  thresholds    JSONB DEFAULT '{}'::jsonb  -- lo que el agente ajusta con el feedback
);

CREATE TABLE IF NOT EXISTS schedule (        -- contexto: fisio, comidas, medicación
  id           SERIAL PRIMARY KEY,
  resident_id  TEXT REFERENCES residents(id),
  activity     TEXT NOT NULL,
  start_time   TIME NOT NULL,
  end_time     TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS medications (     -- el agente la cruza con Keenable
  id           SERIAL PRIMARY KEY,
  resident_id  TEXT REFERENCES residents(id),
  drug         TEXT NOT NULL,
  dose         TEXT,
  started_on   DATE
);

CREATE TABLE IF NOT EXISTS notes (
  id           SERIAL PRIMARY KEY,
  resident_id  TEXT REFERENCES residents(id),
  author       TEXT,
  text         TEXT NOT NULL,
  embedding    JSONB,                       -- vector de OpenAI (o pgvector si está disponible)
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
  id              SERIAL PRIMARY KEY,
  resident_id     TEXT REFERENCES residents(id),
  created_at      TIMESTAMPTZ DEFAULT now(),
  severity        TEXT,
  state_estimate  TEXT,
  confidence      REAL,
  message         TEXT,
  evidence        JSONB,
  reasoning       JSONB,
  audio_url       TEXT,
  status          TEXT DEFAULT 'open',
  true_label      TEXT                      -- etiqueta real de WESAD, para el benchmark
);

CREATE TABLE IF NOT EXISTS feedback (
  id          SERIAL PRIMARY KEY,
  alert_id    INT REFERENCES alerts(id),
  verdict     TEXT CHECK (verdict IN ('real', 'false_alarm')),
  note        TEXT,
  author      TEXT,
  learned     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_log (       -- de aquí sale el TXT "data layer in action"
  id          SERIAL PRIMARY KEY,
  alert_id    INT,
  step        INT,
  tool        TEXT,
  query       TEXT,
  result      TEXT,
  ms          INT,
  created_at  TIMESTAMPTZ DEFAULT now()
);
