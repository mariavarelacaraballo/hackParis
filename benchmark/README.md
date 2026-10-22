# benchmark/ (María)

Tres variantes sobre todos los sujetos de WESAD, con las etiquetas reales:

| Variante | Regla |
| --- | --- |
| `naive_threshold` | FC > umbral fijo (p. ej. 100 lpm), igual para todos |
| `personal_baseline` | desviación respecto a la línea base de cada persona (FC + EDA) |
| `with_feedback` | igual que la anterior + umbrales ajustados con feedback simulado (las etiquetas reales hacen de cuidador) |

Métricas: detecciones (recall de episodios de estrés), falsas alarmas por hora, latencia (s).
Salida: `results.json` (lo sirve `GET /benchmark`) y `results.png` (para la entrega y la slide).
Validación: dejando un sujeto fuera (LOSO) para no hacer trampa.
