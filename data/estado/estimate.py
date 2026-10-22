"""estimate_state() para el backend (services/state.py). [María]"""


def estimate_state(samples: list[dict]) -> dict:
    """samples: [{ts, hr, eda, acc}] (ya agregadas por ventana) → {"activation", "confidence"}.
    TODO(María): cargar model.joblib una vez, construir el vector de features con la línea base del usuario
    y devolver la predicción con su probabilidad.
    """
    raise NotImplementedError
