# The data layer in action (borrador para la entrega)

## Qué datos usa el agente
- Señales fisiológicas en streaming (WESAD: ECG → FC y RMSSD, EDA, acelerómetro).
- Línea base personal de cada residente.
- Agenda (fisioterapia, comidas) y medicación.
- Fuentes externas vía Keenable (efectos de la medicación, causas probables), siempre citadas.
- Notas de los cuidadores (con embeddings para buscar casos parecidos).
- Feedback de cada alerta (real / falsa alarma) y lo aprendido.

## Dónde vive
| Dato | Servicio |
| --- | --- |
| Señales y features | Aiven ClickHouse |
| Residentes, agenda, notas, alertas, feedback, log del agente | Aiven PostgreSQL |
| Eventos en directo | Aiven Valkey (pub/sub) |
| Búsqueda web con fuentes | Keenable |
| Audios de alertas, login | Supabase |

## Cómo fluye
1. El simulador publica ventanas de señal → ClickHouse + evento en Valkey.
2. El agente (Claude) se activa con el evento y llama a sus herramientas:
   tendencia (ClickHouse) → agenda y feedback previo (PostgreSQL) → notas similares (embeddings OpenAI) → si hay medicación reciente, Keenable busca efectos conocidos y cita la fuente.
3. Decide si avisar; si avisa, ElevenLabs genera la voz y el panel la recibe por Valkey/SSE.
4. El cuidador responde; el feedback se guarda y ajusta los umbrales de esa persona.

## Consultas reales (pegar del agent_log al final)
