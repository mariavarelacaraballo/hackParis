# Prompts para Lovable (Marc) — pegarlos en orden

## 1. Base
Build "NeuroVoice", an AAC communicator for people with ALS who type with eye gaze. Big, high-contrast, calm design.
Layout: top bar with the person present (chips: Ana, Rosa, Claire, Marta, Javier, editable), language switch (ES/FR/EN),
and a "Listen" button. Center: 5 large phrase buttons (suggestions). Below: an "initials" input with a large on-screen
keyboard. Right side: tone selector (neutro, tranquilo, contento, cansado, molesto, urgente) with the suggested tone
pre-selected and highlighted, plus a collapsible "Agent trace" panel. Do NOT use Supabase for data: call an external REST
API at a configurable BASE_URL. Use mock data until BASE_URL is set.

## 2. API
- On person change or after Listen: POST {BASE_URL}/context {user_id:"lucas", interlocutor, last_utterance} → show `suggestions`.
- On typing in the initials box, debounce 400 ms then POST {BASE_URL}/expand {user_id:"lucas", mode:"initials", input}
  → show `candidates` as the 5 buttons, pre-select `suggested_tone`, render `trace` in the side panel.
- On selecting a phrase: POST {BASE_URL}/choice {...} then POST {BASE_URL}/speak {user_id, text, tone, language}
  → play `audio_url`. Allow editing the phrase before speaking (pencil icon).
- Listen button: record ~8 s with MediaRecorder, POST multipart to {BASE_URL}/listen → put `text` as last_utterance.
- Poll GET {BASE_URL}/state/lucas every 3 s to update the suggested tone.

## 3. Eye-gaze mode
Add an "Eye-gaze mode" toggle (on by default). Every button and key activates by dwelling: if the pointer stays over it
for 1.2 s it activates, with a circular progress ring. Buttons at least 120 px tall, generous spacing. Setting for dwell time 0.8–2.0 s.

## 4. (Extra) Pictograms
Mode switch "Initials | Pictograms". In Pictograms mode, show a grid of 16 ARASAAC pictograms (I, want, pain, back, water,
food, toilet, tired, cold, hot, family, doctor, yes, no, thank you, help) from https://api.arasaac.org, footer
"Pictogramas: ARASAAC (CC BY-NC-SA)". Send {mode:"pictos", input:[...]} to /expand.

## 5. (Extra) Login y audios con Supabase
Supabase SOLO para login (email) y, si se quiere, guardar los MP3. Nada de memoria ni datos del usuario en Supabase.

## Despliegue
Conectar Lovable a GitHub; exportar el build y servirlo desde Aiven Runtime (o enlazar la URL de Lovable en la entrega
si Runtime solo aloja el backend: preguntar a los mentores de Aiven).
