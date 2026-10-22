"""Estado del usuario a partir del wearable → tono sugerido. [María]

El modelo mide ACTIVACIÓN (WESAD: reposo / estrés / diversión), no emociones. El tono final lo decide el agente
combinando esta activación con el significado de la frase (ver agent/prompts.py), y el usuario lo confirma.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

CLASS_TO_TONE = {"reposo": "tranquilo", "estres": "molesto", "diversion": "contento",
                 "baja": "tranquilo", "alta": "molesto"}


def estimate(samples: list[dict]) -> dict:
    """samples: [{ts, hr, eda, acc}] → {activation, confidence, suggested_tone}"""
    try:
        from data.estado.estimate import estimate_state
        s = estimate_state(samples)
    except Exception:
        # Respaldo mientras María termina el modelo: umbral simple sobre la FC
        hr = sum(x["hr"] for x in samples) / max(len(samples), 1)
        s = {"activation": "alta" if hr > 90 else "baja", "confidence": 0.5}
    s["suggested_tone"] = CLASS_TO_TONE.get(s["activation"], "neutro") if float(s["confidence"]) >= 0.6 else "neutro"
    return s
