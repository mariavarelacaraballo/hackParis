-- Aiven ClickHouse: series temporales y métricas. Ejecutar con backend/scripts/init_db.py

CREATE TABLE IF NOT EXISTS wearable_samples (
  user_id     LowCardinality(String),
  ts          DateTime64(3),
  hr          Float32,          -- lpm
  eda         Float32,          -- µS
  acc         Float32,          -- magnitud del acelerómetro
  activation  LowCardinality(String),  -- estimado: 'baja' | 'alta'
  confidence  Float32
) ENGINE = MergeTree ORDER BY (user_id, ts);

-- Una fila por petición de la app (para latencia/coste reales de la demo)
CREATE TABLE IF NOT EXISTS metrics (
  ts          DateTime64(3) DEFAULT now64(),
  user_id     LowCardinality(String),
  endpoint    LowCardinality(String),  -- 'expand' | 'speak' | 'context'
  latency_ms  UInt32,
  cost_eur    Float64,
  cached      UInt8
) ENGINE = MergeTree ORDER BY (endpoint, ts);

-- Resultados del benchmark (María)
CREATE TABLE IF NOT EXISTS benchmark_results (
  run_id      String,
  ts          DateTime DEFAULT now(),
  variant     UInt8,
  name        String,
  ksr         Float32,
  top1        Float32,
  top5        Float32,
  p50_ms      UInt32,
  p95_ms      UInt32,
  cost_usd    Float64
) ENGINE = MergeTree ORDER BY (run_id, variant);
