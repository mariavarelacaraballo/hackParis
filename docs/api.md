# Contrato de API (v2, NeuroVoice)

Base URL: Aiven Runtime (local: http://localhost:8000). JSON. Si cambias algo, avisa ANTES de hacer push.
Implementación: `backend/app/routes/`. Esquemas: `backend/app/models.py`.

## POST /context        (lo llama el frontend al cambiar quién está o al escuchar algo)
Prepara el contexto y precalienta sugerencias (para que /expand sea rápido).
```json
{"user_id": "lucas", "interlocutor": "Ana", "last_utterance": "¡Hola papá! ¿Qué tal el día?"}
→ {"ok": true, "suggestions": ["Bien, algo cansado. ¿Y tú?", "¿Qué tal el trabajo?", "¿Cómo están Pablo y Lola?"]}
```

## POST /expand         (cada vez que el usuario deja de escribir ~400 ms)
```json
{"user_id": "lucas", "mode": "initials", "input": "m d l e",
 "context": {"interlocutor": "Ana", "last_utterance": "...", "time": "18:05", "state": "activación"},
 "memories": null}
→ {"candidates": ["Me duele la espalda", "Me duele la espalda, llama a la enfermera", "...", "...", "..."],
   "suggested_tone": "molesto",
   "trace": [{"tool": "search_memory", "args": {...}, "result_summary": "4 recuerdos", "ms": 85}, ...],
   "latency_ms": 1840, "cost_eur": 0.0021}
```
- `mode`: "initials" | "pictos" (en pictos, `input` es una lista: ["yo", "dolor", "espalda"]).
- `context` es opcional: si falta, el backend lo toma de la sesión (Valkey).
- `memories`: solo lo usa el benchmark para fijar la memoria (ablación). La app lo deja en null.

## POST /choice         (cuando el usuario elige o edita una frase) → el agente aprende
```json
{"user_id": "lucas", "input": "m d l e", "candidates": [...], "chosen": "Me duele la espalda",
 "edited_text": null, "tone": "molesto", "tone_was_changed": false}
→ {"ok": true, "learned": "Guardada en memoria con contexto Ana · 18:05 · activación"}
```

## POST /speak
```json
{"user_id": "lucas", "text": "Me duele la espalda", "tone": "molesto", "language": "es"}
→ {"audio_url": "https://...mp3", "cached": false, "latency_ms": 930}
```
`tone`: neutro | tranquilo | contento | cansado | molesto | urgente · `language`: es | fr | en

## POST /listen         (botón "Escuchar": audio de ~10 s del navegador)
multipart `audio` + `user_id` → `{"text": "¡Hola papá! ¿Qué tal el día?"}` (se guarda solo el texto, nunca el audio)

## POST /wearable/samples   (pulsera; en la demo lo alimenta replay_wesad.py)
```json
{"user_id": "lucas", "samples": [{"ts": "2026-10-22T18:05:00Z", "hr": 92, "eda": 1.8, "acc": 0.1}]}
→ {"ok": true, "state": {"activation": "alta", "confidence": 0.81, "suggested_tone": "molesto"}}
```

## GET /state/{user_id}     → {"activation": "alta", "confidence": 0.81, "suggested_tone": "molesto"}
## GET /trace/{user_id}?limit=20   → últimas entradas de agent_log (panel lateral de la demo)
## GET /health               → {"ok": true}
