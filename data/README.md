# data/ (María)

1. Descargar WESAD (fuera del repo, carpeta `WESAD/` está en .gitignore).
2. `load_wesad.py`: ventanas de 10 s por sujeto → HR, RMSSD, EDA tónica, SCR/min, ACC, label → tabla `signals` de ClickHouse.
3. Calcular línea base por sujeto (tramo `baseline`) → `residents.hr_baseline`, `eda_baseline` en PostgreSQL.
4. Asignar a cada sujeto un nombre y una agenda ficticios (`schedule`) para la demo.
