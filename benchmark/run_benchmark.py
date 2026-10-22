"""Benchmark de NeuroVoice: ablación de 6 variantes + curva de aprendizaje.

Uso:
    python data/lucas/build_corpus.py
    python benchmark/run_benchmark.py            # todas las variantes
    python benchmark/run_benchmark.py --quick    # solo el primer día de test (para probar)

Métrica principal: KSR = 1 - acciones / caracteres de la frase objetivo.
Acciones contadas como en SpeakFaster: cada letra escrita, cada clic de selección y cada reintento.
Protocolo (por frase):
  1) escribe las iniciales; si la frase está en las 5 candidatas -> 1 clic de selección;
  2) si no, escribe además la primera palabra completa y reintenta; si aparece -> 1 clic;
  3) si tampoco, escribe la frase entera (sin ahorro).
Sin fuga temporal: la memoria solo contiene días anteriores al día que se evalúa.
"""
import argparse
import json
import os
import re
import statistics
import sys
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from expand_local import expand as expand_local  # noqa: E402

OUT = Path(__file__).parent / "results"
EXPAND_URL = os.getenv("EXPAND_URL")  # si existe, se usa la API real de Pedro


def load(name):
    return [json.loads(l) for l in open(ROOT / "data/lucas" / name, encoding="utf-8")]


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]", "", s).strip()


def words(s):
    return norm(s).split()


def initials(s):
    return " ".join(w[0] for w in words(s))


def hour(t):
    return int(t.split(":")[0])


# ---------- recuperación de memoria (variante 5 y 6) ----------
def retrieve(memory, row, use_time_state, k=8):
    """Recuerdos relevantes: mismas iniciales, mismo interlocutor y, si procede, hora y estado parecidos."""
    target_init = initials(row["phrase"]).split()
    scored = []
    for m in memory:
        mi = initials(m["phrase"]).split()
        s = 0.0
        if mi == target_init:
            s += 3
        elif mi[:2] == target_init[:2]:
            s += 1
        if m["interlocutor"] == row["interlocutor"]:
            s += 1
        if use_time_state:
            if abs(hour(m["time"]) - hour(row["time"])) <= 1:
                s += 1
            if m["state"] == row["state"]:
                s += 0.5
        scored.append((s, m["phrase"]))
    scored.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for s, p in scored:
        if s > 0 and p not in seen:
            seen.add(p)
            out.append(p)
        if len(out) == k:
            break
    return out


def context_for(row, variant):
    if variant < 4:
        return None
    ctx = {"interlocutor": row["interlocutor"], "last_utterance": row["previous"]}
    if variant == 6:
        ctx["time"] = row["time"]
        ctx["state"] = row["state"]  # estado medido por la pulsera
    return ctx


def call_expand(inp, ctx, mem):
    if EXPAND_URL:
        import requests
        r = requests.post(EXPAND_URL, json={"user_id": "lucas", "mode": "initials", "input": inp,
                                            "context": ctx or {}, "memories": mem if mem is not None else []}, timeout=60)
        j = r.json()
        return j["candidates"], j.get("latency_ms", 0), j.get("cost_eur", 0)
    return expand_local(inp, ctx, mem)


# ---------- variantes ----------
def eval_full_typing(row):
    n = len(row["phrase"])
    return {"actions": n, "chars": n, "top1": 0, "top5": 0, "ms": 0, "cost": 0}


def eval_frequency(row, unigram):
    """Predicción de palabras por frecuencia: escribe letras hasta que la palabra aparece entre las 3 primeras."""
    actions = 0
    for w in words(row["phrase"]):
        typed = ""
        for ch in w:
            cands = [x for x, _ in unigram.most_common() if x.startswith(typed)][:3] if typed else []
            if w in cands:
                break
            typed += ch
            actions += 1
        cands = [x for x, _ in unigram.most_common() if x.startswith(typed)][:3]
        actions += 1 if w in cands else 0  # clic de selección o espacio
    n = len(row["phrase"])
    return {"actions": min(actions, n), "chars": n, "top1": 0, "top5": 0, "ms": 0, "cost": 0}


def eval_llm(row, variant, memory):
    target = norm(row["phrase"])
    ini = initials(row["phrase"])
    ctx = context_for(row, variant)
    mem = retrieve(memory, row, use_time_state=(variant == 6)) if variant >= 5 else None
    n = len(row["phrase"])
    cands, ms, cost = call_expand(ini, ctx, mem)
    normed = [norm(c) for c in cands]
    top1 = int(bool(normed) and normed[0] == target)
    top5 = int(target in normed)
    actions = len(ini.replace(" ", "")) + 1
    if not top5:
        first = words(row["phrase"])[0]
        retry = f"{first} " + " ".join(ini.split()[1:])
        cands2, ms2, cost2 = call_expand(retry, ctx, mem)
        ms += ms2
        cost += cost2
        if target in [norm(c) for c in cands2]:
            actions = len(ini.replace(" ", "")) + len(first) + 1
        else:
            actions = n
    return {"actions": min(actions, n), "chars": n, "top1": top1, "top5": top5, "ms": ms, "cost": cost}


VARIANTS = {
    1: "Escribir entero",
    2: "Predicción por frecuencia",
    3: "LLM sin memoria ni contexto",
    4: "LLM + contexto conversacional",
    5: "LLM + memoria (NeuroVoice)",
    6: "NeuroVoice + hora y estado",
}


def summarize(res):
    acts = sum(r["actions"] for r in res)
    chars = sum(r["chars"] for r in res)
    lat = [r["ms"] for r in res if r["ms"]]
    return {
        "n": len(res),
        "ksr": round(1 - acts / chars, 3),
        "top1": round(statistics.mean(r["top1"] for r in res), 3),
        "top5": round(statistics.mean(r["top5"] for r in res), 3),
        "latency_p50_ms": round(statistics.median(lat)) if lat else 0,
        "latency_p95_ms": round(sorted(lat)[int(0.95 * (len(lat) - 1))]) if lat else 0,
        "cost_usd_per_phrase": round(sum(r["cost"] for r in res) / len(res), 5),
    }


def run_day(test_rows, memory, variant):
    if variant == 1:
        return [eval_full_typing(r) for r in test_rows]
    if variant == 2:
        unigram = Counter(w for m in memory for w in words(m["phrase"]))
        return [eval_frequency(r, unigram) for r in test_rows]
    with ThreadPoolExecutor(max_workers=8) as ex:
        return list(ex.map(lambda r: eval_llm(r, variant, memory), test_rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="solo el primer día de test")
    ap.add_argument("--variants", default="1,2,3,4,5,6")
    args = ap.parse_args()
    variants = [int(v) for v in args.variants.split(",")]

    memory0 = load("memory.jsonl")
    test = load("test.jsonl")
    days = sorted({r["date"] for r in test})[: 1 if args.quick else None]
    OUT.mkdir(exist_ok=True)

    # Ablación: cada día se evalúa con la memoria de los días anteriores (sin fuga temporal);
    # tras evaluar un día, sus frases (lo que Lucas eligió o corrigió) entran en memoria.
    results = {}
    for v in variants:
        memory, per_v = list(memory0), []
        for d in days:
            rows = [r for r in test if r["date"] == d]
            per_v += run_day(rows, memory, v)
            memory += rows
        results[v] = {"variant": v, "name": VARIANTS[v], **summarize(per_v)}
        print(f"{v}. {VARIANTS[v]:32s} {results[v]}")

    # Curva de aprendizaje: el MISMO día final evaluado con cada vez más días de uso en memoria.
    curve = []
    if 5 in variants and len(days) > 1:
        final = [r for r in test if r["date"] == days[-1]]
        for k in range(len(days)):
            learned = [r for r in test if r["date"] in days[:k]]
            s_ = summarize(run_day(final, memory0 + learned, 5))
            curve.append({"extra_days_of_use": k, "memory_size": len(memory0) + len(learned), **s_})
            print(f"  curva: +{k} días de uso, memoria={len(memory0) + len(learned)} top1={s_['top1']} ksr={s_['ksr']}")

    (OUT / "ablation.json").write_text(json.dumps(list(results.values()), ensure_ascii=False, indent=2))
    (OUT / "learning_curve.json").write_text(json.dumps(curve, ensure_ascii=False, indent=2))
    plot(results, curve)


def plot(results, curve):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = list(results.values())
    fig, ax = plt.subplots(figsize=(8, 4.2))
    names = [f"{r['variant']}. {r['name']}" for r in rows]
    vals = [r["ksr"] for r in rows]
    colors = ["#2a6fdb" if r["variant"] == 5 else "#b9c3d1" for r in rows]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 0.01, i, f"{v:.0%}", va="center", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Ahorro de pulsaciones (KSR), en simulación")
    ax.set_title("Con memoria personal, NeuroVoice ahorra más pulsaciones")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "ablation.png", dpi=200)

    if curve:
        fig, ax = plt.subplots(figsize=(6, 3.6))
        xs = [c["extra_days_of_use"] for c in curve]
        ax.plot(xs, [c["top1"] for c in curve], marker="o", color="#2a6fdb")
        for c in curve:
            ax.annotate(f"{c['top1']:.0%}", (c["extra_days_of_use"], c["top1"]), textcoords="offset points", xytext=(0, 8), ha="center")
        ax.set_xticks(xs)
        ax.set_xlabel("Días de uso aprendidos antes del día evaluado")
        ax.set_ylabel("Acierto a la primera (top-1)")
        ax.set_ylim(0, 1)
        ax.set_title("NeuroVoice aprende con cada día de uso")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(OUT / "learning_curve.png", dpi=200)


if __name__ == "__main__":
    main()
