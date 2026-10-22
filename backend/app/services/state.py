"""Estado del usuario a partir del wearable → tono sugerido. [María]

Usa data/estado/estimate.py (pipeline del TFG sobre WESAD de muñeca).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

ACTIVATION_TO_TONE = {"baja": "tranquilo", "alta": "molesto"}  # TODO(María): afinar (p. ej. 'urgente' si confianza > 0.9)


def estimate(samples: list[dict]) -> dict:
    """samples: [{ts, hr, eda, acc}] → {activation, confidence, suggested_tone}"""
    try:
        from data.estado.estimate import estimate_state
        s = estimate_state(samples)
    except Exception:
        # Respaldo mientras María termina el modelo: umbral simple sobre la FC
        hr = sum(x["hr"] for x in samples) / max(len(samples), 1)
        s = {"activation": "alta" if hr > 90 else "baja", "confidence": 0.5}
    s["suggested_tone"] = ACTIVATION_TO_TONE.get(s["activation"], "neutro") if s["confidence"] >= 0.6 else "neutro"
    return s
