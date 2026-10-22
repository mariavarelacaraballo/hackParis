"""Reproduce un sujeto de WESAD (pulsera) como si fuera en directo → POST /wearable/samples. [María]

Uso: python backend/scripts/replay_wesad.py --subject S2 --speed 20 --url http://localhost:8000
TODO(María):
  1. Cargar WESAD/S{n}/S{n}.pkl → signal['wrist']: BVP (64 Hz), EDA (4 Hz), ACC (32 Hz).
  2. Ventanas de 10 s: FC desde BVP (neurokit2.ppg_process), EDA media, |ACC| media.
  3. Enviar cada ventana con un ts "ahora", durmiendo 10/speed segundos.
  4. Para la demo: saltar directamente al tramo de estrés (label 2) cuando Lucas va a decir "me duele la espalda".
"""
