# Evidence it works (ENTREGA · rellenar con benchmark/results/)

Todo en simulación, con corpus sintético de un usuario ficticio (Lucas). Memoria y test separados por fecha (sin fuga temporal).

## Ablación
| # | Variante | KSR | Top-1 | Top-5 | p95 (ms) | €/frase |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Escribir entero | 0 | — | — | — | 0 |
| 2 | Predicción por frecuencia | | | | | |
| 3 | LLM sin memoria ni contexto | | | | | |
| 4 | LLM + contexto | | | | | |
| 5 | LLM + memoria (NeuroVoice) | | | | | |
| 6 | NeuroVoice + hora y estado | | | | | |
Referencia: SpeakFaster, KSR 0,657 vs 0,482 (Gboard), en simulación (Nature Communications, 2024).

## Curva de aprendizaje
Mismo día de test con 0, 1 y 2 días más de uso en memoria → benchmark/results/learning_curve.png

## Tono preseleccionado
Pulsaciones extra por frase = (1 − acierto LOSO del modelo de estado) × 1, frente a 1 con selección manual.
TODO(María): acierto LOSO de data/estado → benchmark/tone_metric.py

## Latencia de punta a punta
p50/p95 de /expand y /speak (ClickHouse, tabla metrics).
