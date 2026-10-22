"""Reproduce el sujeto de la demo de WESAD (pulsera) como si fuera en directo → POST /wearable/samples.

Uso:
  python backend/scripts/replay_wesad.py --wesad ~/Downloads/WESAD --url http://localhost:8000
  python backend/scripts/replay_wesad.py --wesad ~/Downloads/WESAD --url https://<aiven> --from estres --speed 5
Datos GRABADOS (WESAD), reproducidos en tiempo real: decirlo así en la demo.
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data" / "estado"))
from features import load_subject, windows  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wesad", default=os.path.expanduser("~/Downloads/WESAD"))
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--subject", default=None, help="por defecto, el demo_subject de model.joblib")
    ap.add_argument("--from", dest="start", default="reposo", choices=["reposo", "estres", "diversion"])
    ap.add_argument("--speed", type=float, default=5.0, help="ventanas de 10 s reproducidas cada 10/speed s")
    args = ap.parse_args()

    subject = args.subject
    if not subject:
        import joblib
        subject = joblib.load(Path(__file__).resolve().parents[2] / "data/estado/model.joblib")["demo_subject"]
    rows = windows(load_subject(os.path.join(args.wesad, subject, f"{subject}.pkl")))
    first = next(i for i, r in enumerate(rows) if r["label"] == args.start)
    print(f"Reproduciendo {subject} desde '{args.start}' ({len(rows) - first} ventanas) → {args.url}")
    for r in rows[first:]:
        sample = {"ts": datetime.now(timezone.utc).isoformat(), "hr": r["hr"] if r["hr"] == r["hr"] else 75.0,
                  "eda": r["eda"], "acc": r["acc"]}
        out = requests.post(f"{args.url}/wearable/samples", json={"user_id": "lucas", "samples": [sample]}, timeout=10).json()
        st = out.get("state", {})
        print(f"t={r['t']:6.0f}s  real={r['label']:9s}  FC={sample['hr']:5.1f}  EDA={r['eda']:.2f}  →  "
              f"{st.get('activation')} ({st.get('confidence')}) tono={st.get('suggested_tone')}")
        time.sleep(10 / args.speed)


if __name__ == "__main__":
    main()
