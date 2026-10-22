# benchmark/ (María)

```bash
python data/lucas/build_corpus.py
python benchmark/run_benchmark.py --quick --variants 1,2,3,5   # prueba rápida
python benchmark/run_benchmark.py                               # completo → results/
```
- run_benchmark.py: 6 variantes de ablación + curva de aprendizaje. KSR, top-1/top-5, latencia, coste.
- expand_local.py: expand() local con Claude, para medir antes de que la API esté lista.
- Con EXPAND_URL en .env se mide la API real de Pedro (lo correcto para la entrega).
- tone_metric.py: pulsaciones extra por el tono (usa data/estado/loso.json).
- TODO(María): subir results a ClickHouse (tabla benchmark_results) para la entrega de data layer.
Sin fuga temporal: cada día de test se evalúa solo con la memoria de los días anteriores.
