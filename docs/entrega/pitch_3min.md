# Guion del vídeo (3 min)
0:00 Problema — "Lucas tiene ELA y habla con la mirada: menos de 10 palabras por minuto. Decir 'me duele la espalda' son 40 miradas. Y su voz suena plana."
0:25 Idea — "NeuroVoice es un agente con memoria. Lucas escribe las iniciales y el agente completa la frase con lo que sabe de él: quién está, qué suele decir, cómo está. Él elige siempre."
0:45 Demo — Rosa pregunta "¿Estás cómodo?" → "m d l e" → 5 frases → elige con la mirada → suena con su voz.
       Abrir el panel de razonamiento: memoria (Postgres) → contexto (Valkey) → estado de la pulsera.
       Claire (FR) → la misma frase en francés. Pulsera en estrés → tono sugerido 'molesto', Lucas lo confirma.
1:50 Datos — "Todo vive en Aiven: memoria con pgvector, sesión en Valkey, señales y métricas en ClickHouse, y la API en Runtime."
2:15 Evidencia — "Con el mismo modelo, su memoria triplica las frases acertadas a la primera: del 12 al 36 %. La pulsera distingue reposo de estrés con un 95 % en personas que el modelo no ha visto. Todo en simulación."
2:40 Primeros usuarios — "Piloto con usuarios de ELA vía adELA, Fundación Luzón y ARSLA; después, complemento de Grid 3 y TD Snap. 97 millones de personas podrían beneficiarse de la comunicación aumentativa. Empezamos por la ELA."
