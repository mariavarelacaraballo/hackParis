# data/estado — modelo de estado (María)

Viene del pipeline del TFG (DACIU), solo la parte de WESAD (sin datos de pacientes).
Objetivo: estimate_state(window) → {"activation": "baja"|"alta", "confidence": 0-1}

Pasos:
1. features.py: ventana de muñeca (BVP, EDA, ACC) → FC, RMSSD, EDA tónica, picos SCR, |ACC|.
   Hallazgos del TFG: la activación se calcula con la FC; los picos SCR como eventos puntuales (habituación).
2. train_state.py: entrenar con WESAD (baseline vs estrés), validación LOSO (dejando un sujeto fuera) → acierto real.
   Normalizar por la línea base de cada sujeto. Guardar model.joblib y loso.json (acierto por sujeto).
3. estimate.py: cargar model.joblib; recibir las muestras de /wearable/samples y devolver el estado.
4. benchmark/tone_metric.py usa loso.json para la métrica "pulsaciones extra por el tono".
