# NeuroVoice — contexto para Claude Code

Hackathon Accel AI Innovate (París). Entrega: 22 oct 2026, 15:30. Equipo: María (benchmark, estado), Pedro (backend, agente), Marc (Lovable, voz, pitch).

## Producto
Copiloto de comunicación para personas con ELA que escriben con la mirada. Escriben iniciales ("m d l e"); un agente con
memoria personal (quién está, qué suele decir, hora, estado) propone 5 frases; el usuario elige SIEMPRE; suena con su voz
clonada (ElevenLabs eleven_v3) y con un tono preseleccionado por un wearable (WESAD, pulsera) que el usuario puede cambiar.
Aprende de cada elección y corrección.

## Criterios del jurado (20 % cada uno)
Problema real · agente avanzado (multi-paso, aprendizaje) · datos en el núcleo · evidencia medida frente a líneas base · pitch.
Obligatorio: desplegar en Aiven Runtime y usar sus datos gestionados.

## Stack
FastAPI (backend/), Aiven PostgreSQL + pgvector (memoria), Aiven ClickHouse (señal y métricas), Aiven Valkey (caché, sesión, eventos),
Claude con tool use (agente), OpenAI (embeddings, transcripción), ElevenLabs (voz), Keenable (web, opcional), Supabase (login y audios, opcional),
Lovable (frontend, repo aparte).

## Reglas de diseño (no negociables)
- Nada se pronuncia sin selección explícita del usuario. El agente propone, nunca habla por él.
- El tono es una sugerencia visible y anulable. No decir "leemos emociones".
- Todo lo que hace el agente se registra en agent_log (traza de la demo y entrega "data layer").
- El benchmark llama a la MISMA lógica que la app (/expand). Sin fuga temporal: memoria de días anteriores al evaluado.
- No hay alertas clínicas (evita clasificar como producto sanitario).
- Prioridad: flujo de punta a punta antes que extras. Ver docs/checklist.md.
