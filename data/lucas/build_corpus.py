"""Genera el corpus sintético de Lucas (usuario ficticio con ELA).

- memory.jsonl: días 1-5, lo que el agente "recuerda" (frases con su contexto).
- test.jsonl:   días 6-8, una "época" por día para la curva de aprendizaje.
Las frases recurrentes reaparecen (la gente repite), y ~40 % de las de test son nuevas,
para que el benchmark no sea trivial. Corpus sintético: hay que decirlo en el pitch.
"""
import json
import random
from pathlib import Path

random.seed(7)
OUT = Path(__file__).parent

PROFILE = {
    "user_id": "lucas",
    "name": "Lucas",
    "age": 58,
    "condition": "ELA, escribe con la mirada",
    "language": "es",
    "contacts": {
        "Ana": "hija, viene por las tardes",
        "Javier": "hijo, llama los domingos",
        "Claire": "enfermera de noche, habla francés",
        "Marta": "logopeda, martes y jueves por la mañana",
        "Rosa": "mujer de Lucas",
    },
    "routines": [
        "08:00 desayuno y medicación",
        "11:00 fisioterapia",
        "14:00 comida",
        "18:00 visita de Ana",
        "21:00 cena",
        "23:00 Claire hace la ronda de noche",
    ],
    "interests": ["Real Betis", "flamenco", "nietos Pablo y Lola", "pesca"],
}

# (interlocutor, hora, frase anterior del interlocutor, estado, frase de Lucas)
RECURRENT = [
    ("Rosa", "08:00", "Buenos días, cariño. ¿Has dormido bien?", "calma", "He dormido regular, me desperté varias veces"),
    ("Rosa", "08:00", "¿Te traigo el desayuno?", "calma", "Sí, un café con leche, por favor"),
    ("Rosa", "08:10", "Aquí tienes las pastillas.", "calma", "Gracias, ¿me das un poco de agua?"),
    ("Marta", "11:00", "Hola Lucas, ¿empezamos con los ejercicios?", "calma", "Hoy estoy algo cansado, vamos despacio"),
    ("Marta", "11:30", "¿Cómo notas la garganta?", "calma", "Me cuesta más tragar que la semana pasada"),
    ("Rosa", "14:00", "¿Tienes hambre?", "calma", "Un poco, ¿qué hay de comer?"),
    ("Rosa", "14:30", "¿Estás cómodo así?", "activación", "Me duele la espalda, cámbiame de postura"),
    ("Ana", "18:00", "¡Hola papá! ¿Qué tal el día?", "calma", "Bien, algo cansado. ¿Y tú?"),
    ("Ana", "18:05", "Uf, mucho trabajo, como siempre.", "calma", "¿Qué tal el trabajo?"),
    ("Ana", "18:10", "Los niños te mandan besos.", "calma", "¿Cómo están Pablo y Lola?"),
    ("Ana", "18:20", "¿Quieres que pongamos algo en la tele?", "calma", "Pon el partido del Betis"),
    ("Ana", "18:50", "Me tengo que ir ya, papá.", "calma", "Gracias por venir, te quiero"),
    ("Rosa", "21:00", "¿Cenamos?", "calma", "Sí, pero algo ligero"),
    ("Claire", "23:00", "Bonsoir Lucas, ça va ?", "calma", "Estoy bien, gracias"),
    ("Claire", "23:05", "Vous avez besoin de quelque chose ?", "activación", "Tengo frío, ¿me traes otra manta?"),
    ("Claire", "02:00", "Je vous ai entendu, tout va bien ?", "activación", "Me duele la espalda, llama a la enfermera"),
    ("Javier", "12:00", "¡Hola papá! ¿Cómo estás?", "calma", "Bien, hijo. ¿Cuándo vienes a verme?"),
    ("Rosa", "16:00", "¿Quieres descansar un rato?", "calma", "Sí, baja la persiana, por favor"),
]

NOVEL = [
    ("Ana", "18:15", "El sábado es el cumple de Lola.", "calma", "Cómprale algo de mi parte"),
    ("Marta", "11:15", "Vamos a probar un ejercicio nuevo.", "calma", "Vale, explícamelo despacio"),
    ("Rosa", "14:40", "Ha llamado el médico.", "activación", "¿Qué ha dicho el doctor?"),
    ("Claire", "23:10", "Il fait chaud ici, non ?", "calma", "Abre un poco la ventana"),
    ("Ana", "18:30", "¿Te leo un rato?", "calma", "Sí, léeme el periódico"),
    ("Javier", "12:05", "He visto que ganó el Betis.", "calma", "Qué partidazo, por fin"),
    ("Rosa", "08:20", "Hoy viene tu hermano.", "calma", "Qué alegría, hace mucho que no lo veo"),
    ("Marta", "11:40", "Lo has hecho muy bien hoy.", "calma", "Gracias, me ayudas mucho"),
    ("Rosa", "15:00", "¿Te pongo música?", "calma", "Pon algo de flamenco"),
    ("Claire", "02:10", "Vous voulez boire ?", "activación", "Sí, agua, tengo la boca seca"),
    ("Ana", "18:40", "Mañana no puedo venir.", "calma", "No pasa nada, ven cuando puedas"),
    ("Rosa", "21:20", "¿Te ayudo a lavarte los dientes?", "calma", "Sí, y luego quiero acostarme"),
]


def day_rows(day, recurrent_share, n_novel):
    rows = [r for r in RECURRENT if random.random() < recurrent_share]
    rows += random.sample(NOVEL, n_novel)
    rows.sort(key=lambda r: r[1])
    return [
        {"user_id": "lucas", "date": f"2026-10-{day:02d}", "time": t, "interlocutor": who,
         "previous": prev, "state": state, "phrase": phrase}
        for who, t, prev, state, phrase in rows
    ]


def main():
    (OUT / "profile.json").write_text(json.dumps(PROFILE, ensure_ascii=False, indent=2))
    novel_pool = NOVEL[:]  # en memoria solo entran algunas frases nuevas; el resto aparece por primera vez en test
    memory = []
    for d in range(1, 6):
        memory += day_rows(d, recurrent_share=0.8, n_novel=1)
    test = []
    for d in range(6, 9):
        test += day_rows(d, recurrent_share=0.7, n_novel=5)
    with open(OUT / "memory.jsonl", "w") as f:
        for r in memory:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT / "test.jsonl", "w") as f:
        for r in test:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"memoria: {len(memory)} frases (días 1-5) · test: {len(test)} frases (días 6-8)")


if __name__ == "__main__":
    main()
