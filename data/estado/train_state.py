"""Entrena el modelo de estado con WESAD (pulsera) y lo valida dejando un sujeto fuera (LOSO). [estado]

Uso:  python data/estado/train_state.py --wesad ~/Downloads/WESAD
Salidas (en data/estado/): model.joblib, loso.json, features.csv
Modelo: regresión logística (una "neurona"), interpretable y con probabilidad calibrada.
También se calcula la validación cruzada MEZCLADA para mostrar la fuga temporal (TFG): no usarla como resultado.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import KFold

sys.path.insert(0, str(Path(__file__).parent))
from features import FULL, RUNTIME, baseline_stats, load_subject, windows, zvec  # noqa: E402

OUT = Path(__file__).parent


def loso(per_subject, feats, classes):
    """Acierto balanceado por sujeto entrenando con todos los demás."""
    res = {}
    subjects = sorted(per_subject)
    for test in subjects:
        Xtr, ytr = [], []
        for s in subjects:
            if s == test:
                continue
            rows, st = per_subject[s]
            for r in rows:
                if r["label"] in classes:
                    Xtr.append(zvec(r, st, feats)); ytr.append(r["label"])
        rows, st = per_subject[test]
        Xte = [zvec(r, st, feats) for r in rows if r["label"] in classes]
        yte = [r["label"] for r in rows if r["label"] in classes]
        if len(set(yte)) < 2:
            continue
        clf = LogisticRegression(class_weight="balanced", max_iter=1000).fit(Xtr, ytr)
        res[test] = round(balanced_accuracy_score(yte, clf.predict(Xte)), 3)
    return res


def shuffled_cv(per_subject, feats, classes):
    """Validación mezclada (INCORRECTA en series temporales): solo para enseñar la fuga."""
    X, y = [], []
    for rows, st in per_subject.values():
        for r in rows:
            if r["label"] in classes:
                X.append(zvec(r, st, feats)); y.append(r["label"])
    X, y = np.array(X), np.array(y)
    accs = []
    for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
        clf = LogisticRegression(class_weight="balanced", max_iter=1000).fit(X[tr], y[tr])
        accs.append(balanced_accuracy_score(y[te], clf.predict(X[te])))
    return round(float(np.mean(accs)), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wesad", default=os.path.expanduser("~/Downloads/WESAD"))
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.wesad, "S*", "S*.pkl")))
    if not files:
        sys.exit(f"No encuentro WESAD en {args.wesad} (esperaba S2/S2.pkl, S3/S3.pkl…)")

    per_subject, all_rows = {}, []
    for f in files:
        s = load_subject(f)
        rows = windows(s)
        per_subject[s["subject"]] = (rows, baseline_stats(rows, FULL))
        all_rows += rows
        print(f"{s['subject']}: {len(rows)} ventanas")

    import csv
    with open(OUT / "features.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
        w.writeheader(); w.writerows(all_rows)

    report = {}
    for name, feats, classes in [("binario_completo", FULL, {"reposo", "estres"}),
                                 ("binario_runtime", RUNTIME, {"reposo", "estres"}),
                                 ("tres_clases_completo", FULL, {"reposo", "estres", "diversion"})]:
        per = loso(per_subject, feats, classes)
        vals = list(per.values())
        report[name] = {"features": feats, "classes": sorted(classes),
                        "loso_mean": round(float(np.mean(vals)), 3), "loso_std": round(float(np.std(vals)), 3),
                        "per_subject": per, "shuffled_cv_NO_USAR": shuffled_cv(per_subject, feats, classes)}
        print(f"{name:22s} LOSO {report[name]['loso_mean']:.2f} ± {report[name]['loso_std']:.2f}   "
              f"(mezclada, inflada: {report[name]['shuffled_cv_NO_USAR']:.2f})")

    # Modelo desplegado: features que llegan por /wearable/samples (FC, EDA, movimiento), binario.
    X, y = [], []
    for rows, st in per_subject.values():
        for r in rows:
            if r["label"] in {"reposo", "estres"}:
                X.append(zvec(r, st, RUNTIME)); y.append(r["label"])
    clf = LogisticRegression(class_weight="balanced", max_iter=1000).fit(X, y)
    per_rt = report["binario_runtime"]["per_subject"]
    demo = max(per_rt, key=per_rt.get)  # sujeto con el cambio más claro → para la demo
    joblib.dump({"clf": clf, "features": RUNTIME,
                 "baselines": {s: baseline_stats(r, RUNTIME) for s, (r, _) in per_subject.items()},
                 "demo_subject": demo,
                 "weights": dict(zip(RUNTIME, clf.coef_[0].round(3).tolist()))}, OUT / "model.joblib")
    report["deployed"] = {"model": "binario_runtime", "demo_subject": demo,
                          "weights": dict(zip(RUNTIME, clf.coef_[0].round(3).tolist())),
                          "positive_class": str(clf.classes_[1])}
    (OUT / "loso.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nModelo guardado. Sujeto para la demo: {demo} (LOSO {per_rt[demo]}). Pesos: {report['deployed']['weights']}")
    print("Cifra para la evidencia: binario_completo LOSO (media ± desviación). NO usar la validación mezclada.")


if __name__ == "__main__":
    main()
