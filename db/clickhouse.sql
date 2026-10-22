-- Aiven ClickHouse: señales (escala y frescura)
CREATE TABLE IF NOT EXISTS signals (
  resident_id  LowCardinality(String),
  ts           DateTime64(3),
  hr           Float32,      -- latidos/min (ventana de 10 s)
  rmssd        Float32,      -- ms
  eda          Float32,      -- µS, nivel tónico
  scr_rate     Float32,      -- picos SCR por minuto
  acc          Float32,      -- magnitud del acelerómetro
  label        LowCardinality(String)  -- baseline / stress / amusement (solo benchmark)
) ENGINE = MergeTree
ORDER BY (resident_id, ts);

-- Consulta tipo que usa el agente: tendencia de 15 min frente a la línea base
-- SELECT avg(hr), avg(eda), max(scr_rate)
-- FROM signals
-- WHERE resident_id = {rid:String} AND ts > now64() - INTERVAL 15 MINUTE;
