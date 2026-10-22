# Arquitectura y flujo (quién llama a quién)

## Flujo de la demo
1. Lovable → POST /context (entra Ana / botón Escuchar → POST /listen → texto)
   - backend guarda la sesión en Valkey y precalcula sugerencias (agente) → 3 frases sin escribir nada.
2. Usuario escribe "m d l e" → (debounce 400 ms) → POST /expand
   - agente (Claude con tools) → 5 candidatas + tono sugerido + traza.
3. Usuario elige (selección por permanencia) → POST /choice  → memoria actualizada (aprende).
4. Lovable → POST /speak con el tono (preseleccionado, editable) → ElevenLabs → audio (caché en Valkey).
5. En paralelo: replay_wesad.py → POST /wearable/samples → ClickHouse + estado en Valkey.

## El agente (backend/app/agent/agent.py)
Bucle de tool use de Claude con un máximo de 4 rondas:
```
user: iniciales + contexto de sesión
 → Claude decide: search_memory(...)        [PostgreSQL + pgvector]
 → Claude decide: get_context(...)          [Valkey: hora, interlocutor, última frase, rutinas de ahora]
 → Claude decide: get_state(...)            [Valkey/ClickHouse: activación y tono sugerido]
 → (opcional) web_search(...)               [Keenable, si la frase habla de algo actual]
 → Claude termina con propose_phrases(...)  [herramienta "final": 5 candidatas estructuradas]
```
Cada llamada a herramienta se registra en agent_log (tool, args, resumen del resultado, ms).

### Por qué un agente y no una sola llamada
- Decide qué recuerdos buscar (por iniciales, por interlocutor, por tema) y puede buscar dos veces.
- Combina fuentes (memoria, sesión, estado, web).
- Aprende: /choice escribe en memoria y la siguiente búsqueda ya lo encuentra (curva de aprendizaje del benchmark).

### Latencia
- /context precalienta: sesión + recuerdos del interlocutor en Valkey → /expand no repite trabajo.
- Caché en Valkey de expansiones (clave = user + input + interlocutor) y de audios (user + texto + tono + idioma).
- Medimos p50/p95 en ClickHouse (tabla metrics).

## Tablas
- PostgreSQL (db/postgres.sql): users, contacts, routines, memories (con embedding vector), choices, agent_log.
- ClickHouse (db/clickhouse.sql): wearable_samples, metrics (cada /expand y /speak), benchmark_results.
- Valkey: session:{user}, state:{user}, cache:expand:{hash}, cache:audio:{hash}.
