"""estimate_state() que usa el backend (services/state.py). [estado]

Recibe muestras de /wearable/samples (hr, eda, acc) y las normaliza con la línea base del usuario.
Para la demo, "lucas" usa la línea base del sujeto de WESAD que se reproduce (equivale a una calibración en reposo).
"""
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

MODEL = Path(__file__).parent / "model.joblib"


@lru_cache(maxsize=1)
def _model():
    return joblib.load(MODEL)


def estimate_state(samples: list[dict], subject: str | None = None) -> dict:
    m = _model()
    stats = m["baselines"].get(subject or m["demo_subject"])
    feats = m["features"]
    X = np.array([[(float(s.get(f, stats[f][0])) - stats[f][0]) / stats[f][1] for f in feats] for s in samples])
    p = m["clf"].predict_proba(X.mean(axis=0, keepdims=True))[0]
    classes = list(m["clf"].classes_)
    p_stress = float(p[classes.index("estres")])
    return {"activation": "alta" if p_stress >= 0.5 else "baja",
            "confidence": round(max(p_stress, 1 - p_stress), 2),
            "p_stress": round(p_stress, 2)}
