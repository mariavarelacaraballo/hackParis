# The data layer in action (ENTREGA · rellenar a las 14:30 con datos reales)

## Qué datos usa el agente
- Memoria personal de Lucas: frases dichas antes con su contexto (quién, cuándo, estado) → PostgreSQL + pgvector.
- Contactos y rutinas → PostgreSQL.
- Sesión en vivo: interlocutor, última frase escuchada, hora → Valkey.
- Señal del wearable (FC, EDA, movimiento; WESAD pulsera) y estado estimado → ClickHouse + Valkey.
- Elecciones y correcciones del usuario → PostgreSQL (así aprende).
- Métricas de cada petición (latencia, coste) y resultados del benchmark → ClickHouse.

## Dónde vive y cómo fluye
(pegar el diagrama del Plan maestro o docs/architecture.md)

## Consultas reales del agente (pegar de agent_log)
TODO(Pedro, 14:30): SELECT tool, args, result_summary, ms FROM agent_log ORDER BY id DESC LIMIT 15;

## Prueba de que los datos importan
TODO(María): misma petición con y sin memoria → resultado distinto (de benchmark/results/ablation.json).
