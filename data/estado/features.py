"""Features de ventana de la pulsera de WESAD (Empatica E4). [estado]

Señales de muñeca: BVP 64 Hz, EDA 4 Hz, ACC 32 Hz. Etiquetas a 700 Hz: 1 reposo, 2 estrés, 3 diversión.
Ventanas de 60 s cada 10 s. Solo numpy/scipy (rápido y sin sorpresas).
Hallazgos del TFG aplicados: la activación se apoya en la FC; los picos de SCR como eventos (conteo), no como nivel.
"""
import pickle

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

FS_BVP, FS_EDA, FS_ACC, FS_LABEL = 64, 4, 32, 700
WIN, STEP = 60, 10
LABELS = {1: "reposo", 2: "estres", 3: "diversion"}
FULL = ["hr", "rmssd", "eda", "scr_min", "acc"]   # modelo completo (evidencia)
RUNTIME = ["hr", "eda", "acc"]                     # lo que manda /wearable/samples (demo)


def load_subject(path):
    with open(path, "rb") as f:
        d = pickle.load(f, encoding="latin1")
    w = d["signal"]["wrist"]
    return {"subject": d["subject"], "bvp": w["BVP"].ravel(), "eda": w["EDA"].ravel(),
            "acc": w["ACC"].astype(float), "label": d["label"].ravel()}


def _bandpass(x, lo, hi, fs, order=3):
    b, a = butter(order, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x)


def hr_rmssd(bvp):
    """FC (lpm) y RMSSD (ms) desde BVP: filtro 0,7-3,5 Hz + detección de picos."""
    if len(bvp) < FS_BVP * 10:
        return np.nan, np.nan
    x = _bandpass(bvp, 0.7, 3.5, FS_BVP)
    peaks, _ = find_peaks(x, distance=int(0.33 * FS_BVP), prominence=np.std(x) * 0.3)
    ibi = np.diff(peaks) / FS_BVP
    ibi = ibi[(ibi > 0.33) & (ibi < 1.5)]
    if len(ibi) < 5:
        return np.nan, np.nan
    d = np.diff(ibi)
    d = d[np.abs(d) < 0.25]  # quitar saltos de artefacto
    return 60.0 / np.median(ibi), (np.sqrt(np.mean(d ** 2)) * 1000 if len(d) else np.nan)


def eda_feats(eda):
    """Nivel medio (µS) y picos de SCR por minuto."""
    if len(eda) < FS_EDA * 10:
        return np.nan, np.nan
    peaks, _ = find_peaks(eda, prominence=0.01, distance=FS_EDA)
    return float(np.mean(eda)), len(peaks) / (len(eda) / FS_EDA / 60)


def acc_feat(acc):
    """Movimiento: desviación típica de la magnitud del acelerómetro."""
    mag = np.linalg.norm(acc, axis=1) / 64.0  # E4: 1/64 g por unidad
    return float(np.std(mag))


def windows(s, keep=(1, 2, 3)):
    """Lista de ventanas con features y etiqueta (moda del tramo, ≥80 % puro)."""
    dur = len(s["eda"]) / FS_EDA
    out = []
    for t in np.arange(0, dur - WIN, STEP):
        lab = s["label"][int(t * FS_LABEL): int((t + WIN) * FS_LABEL)]
        if not len(lab):
            continue
        vals, cnt = np.unique(lab, return_counts=True)
        m = vals[cnt.argmax()]
        if m not in keep or cnt.max() / len(lab) < 0.8:
            continue
        hr, rm = hr_rmssd(s["bvp"][int(t * FS_BVP): int((t + WIN) * FS_BVP)])
        e, scr = eda_feats(s["eda"][int(t * FS_EDA): int((t + WIN) * FS_EDA)])
        a = acc_feat(s["acc"][int(t * FS_ACC): int((t + WIN) * FS_ACC)])
        out.append({"subject": s["subject"], "t": float(t), "label": LABELS[int(m)],
                    "hr": hr, "rmssd": rm, "eda": e, "scr_min": scr, "acc": a})
    return out


def baseline_stats(rows, feats):
    """Media y desviación de cada feature en el tramo de reposo del sujeto (normalización del TFG)."""
    base = [r for r in rows if r["label"] == "reposo"]
    stats = {}
    for f in feats:
        v = np.array([r[f] for r in base], dtype=float)
        v = v[~np.isnan(v)]
        stats[f] = (float(v.mean()) if len(v) else 0.0, float(v.std()) + 1e-6 if len(v) > 1 else 1.0)
    return stats


def zvec(r, stats, feats):
    return [((r[f] if r[f] == r[f] else stats[f][0]) - stats[f][0]) / stats[f][1] for f in feats]
