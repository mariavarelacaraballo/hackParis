# NeuroVoice: idea, encaje con el hackathon y futuro

> **One-liner:** NeuroVoice da a quien no puede hablar una voz que suena como se siente: mide su estado con sensores, recuerda cómo se comunica y aprende de cada conversación.

Hackathon Accel AI Innovate (París) · Entrega: 22 oct 2026, 15:00 · Equipo: María, Pedro, Marc

---

# PARTE 1. La idea de partida (NeuroVoice Express)

## 1. El concepto

### El problema
Las prótesis de habla para pacientes con ELA, afasia motora o ictus son **robóticas, monótonas y lentas**. Convierten texto plano en voz sin prosodia, así que el paciente pierde su identidad afectiva: no puede sonar urgente, aliviado o cansado.

### La innovación: dos canales separados
El contenido (qué se dice) y la emoción (cómo se dice) se tratan por separado:

1. **Canal semántico (qué):** el mensaje del paciente.
2. **Canal afectivo (cómo):** su estado fisiológico (activación y valencia) se mide con sensores y se convierte en **audio tags de ElevenLabs v3** (`[calm]`, `[urgently]`, `[sighs]`, `[relieved]`, `[whispers]`).
3. **Proyección translingüe:** la misma frase con la misma emoción y la voz del paciente, en inglés y en francés.

### Ajustes de honestidad sobre el plan original
- **El EEG no invasivo no decodifica frases.** Los modelos EEG-to-text sobre ZuCo rinden prácticamente igual con ruido como entrada, y Brain2Qwerty usa MEG. En la demo, **el canal semántico es el comunicador del paciente** (texto elegido con eye-tracking o pictogramas, como ya hacen hoy). Si se muestra un decodificador, se presenta como simulado.
- **La asimetría frontal alfa es un marcador débil.** El canal afectivo usa sobre todo **ECG y EDA** (FC, variabilidad, conductancia de la piel), que son más robustos. El EEG queda como opcional.
- **La voz clonada ya existe** (ElevenLabs con Smartbox, Predictable, Cboard). La novedad es que **la emoción medida module la voz automáticamente**.
- **La cifra de 8.000 M$ de mercado no tiene fuente.** No usarla en el pitch sin citar.

## 2. Modelos y datos

| Componente | Herramienta | Función |
| --- | --- | --- |
| Señal fisiológica real | **WESAD** (ECG, EDA y movimiento; 15 sujetos; baseline, estrés y diversión) | Canal afectivo con etiquetas reales |
| Features | **NeuroKit2** + SciPy | FC, RMSSD, EDA tónica, picos SCR |
| Estado afectivo | **scikit-learn** (random forest / regresión logística) | Activación y valencia con probabilidad |
| EEG (opcional) | **MNE-Python** | Bandas de potencia (asimetría frontal) como señal secundaria |
| Agente | **Claude** (tool use) | Ver la Parte 2 |
| Voz | **ElevenLabs `eleven_v3`** + clonación | Voz del paciente con emoción, en varios idiomas |
| Frontend | **Lovable** | Comunicador + panel |
| Backend y datos | **Aiven Runtime** + ClickHouse + PostgreSQL + Valkey | Obligatorio en el reto (sustituye a Modal) |

## 3. Pitch base (3 minutos)

- **Problema (0:00–0:30):** "Cuando un paciente con ELA pierde el habla, la tecnología le devuelve una voz monótona. Puede decir *me duele*, pero no puede sonar a que le duele."
- **Tesis (0:30–1:15):** "Separamos lo que dice de cómo lo dice. El qué lo elige el paciente; el cómo lo miden sus sensores."
- **Demo (1:15–2:15):** el paciente elige una frase → los sensores marcan activación alta → la voz suena urgente → la misma frase en francés con la misma emoción.
- **Cierre (2:15–3:00):** evidencia medida, primeros usuarios y visión.

---

# PARTE 2. Cómo la integramos con los criterios del hackathon

El plan original es un pipeline fijo: señal → tags → voz. Para puntuar hace falta **un agente que dependa de datos**, que **recuerde y aprenda**, y **resultados medibles**. La idea se mantiene; lo que cambia es que NeuroVoice pasa a ser un **agente de comunicación con memoria**.

## 4. El producto que construimos hoy

**NeuroVoice Agent:** un copiloto de comunicación para personas que usan un comunicador (ELA, afasia, parálisis cerebral, ictus).

1. **Predice lo que quiere decir** a partir de su memoria (frases habituales, personas, rutinas, la hora, con quién está) para que escriba **mucho menos**. Hoy un usuario de eye-tracking escribe a unas pocas palabras por minuto.
2. **Mide cómo se siente** (ECG/EDA) y pone esa emoción en la voz.
3. **Habla con su voz**, en el idioma de quien le escucha.
4. **Aprende de cada corrección:** si elige otra frase, o dice "no me sentía así", el agente ajusta sus predicciones y su mapeo de emoción para esa persona.
5. **Avisa al cuidador** si detecta malestar sostenido sin que el paciente haya escrito nada.

## 5. Encaje criterio por criterio (20 % cada uno)

| Criterio | Cómo lo cumple NeuroVoice |
| --- | --- |
| **01 Problema y valor** | Usuario claro: personas con ELA, afasia o ictus que usan comunicador, y su logopeda o cuidador. Dolor real: comunicación lenta y sin emoción. Lo adoptarían porque se integra con el comunicador que ya usan. |
| **02 Agente** | Multi-paso y autónomo: lee el contexto → consulta la memoria → predice frases → mide el estado → elige la emoción → genera la voz → aprende de la corrección. También avisa por iniciativa propia. No es una sola llamada al LLM. |
| **03 Datos en el núcleo** | **Frescura:** señales en streaming (ClickHouse, Valkey). **Memoria:** historial de frases, personas, rutinas y correcciones (PostgreSQL). **Grounding:** cada predicción cita de qué recuerdo sale. **Escala:** todo WESAD más el historial de conversaciones. Sin datos, el agente no sirve: es la tesis del producto. |
| **04 Evidencia** | Benchmark frente a líneas base ingenuas (sección 7). |
| **05 Ejecución y pitch** | La demo es muy visual y emotiva (la misma frase dicha plana y con emoción), con una diferencia clara frente a los comunicadores actuales y un camino creíble a los primeros usuarios (sección 10). |

## 6. Datos y dónde viven (Aiven)

| Dato | Servicio | Uso del agente |
| --- | --- | --- |
| Señales y features (ECG, EDA, ACC) | **Aiven ClickHouse** | Tendencia del estado afectivo en los últimos minutos |
| Perfil, frases, personas, rutinas, correcciones, log del agente | **Aiven PostgreSQL** | Memoria a largo plazo; predicción personalizada |
| Eventos en directo | **Aiven Valkey** | Estado y frases sugeridas en tiempo real en el comunicador |
| Búsqueda semántica en el historial | PostgreSQL + embeddings **OpenAI** (o **OpenSearch**) | "¿Qué suele decir en una situación parecida?" |
| Contexto externo | **Keenable** | Respuestas con información actual cuando el paciente pregunta algo del mundo, con fuente |
| Audios generados y login | **Supabase** | Storage de MP3 y auth |

**Herramientas del agente:**

| Herramienta | Fuente |
| --- | --- |
| `get_affect(user, minutes)` | ClickHouse + modelo de scikit-learn |
| `recall(user, context)` | PostgreSQL + embeddings: frases y situaciones parecidas |
| `get_profile(user)` | PostgreSQL: personas, rutinas, idioma, voz |
| `suggest_phrases(context)` | LLM (Claude) a partir de los recuerdos recuperados |
| `speak(text, affect, language)` | ElevenLabs `eleven_v3` con tags de emoción |
| `web_search(query)` | Keenable |
| `learn(correction)` | PostgreSQL: actualiza frecuencias, preferencias y el mapeo de emoción |
| `notify_caregiver(...)` | Valkey + panel |

Toda consulta se registra en `agent_log`, que sirve para la traza visible en la demo y para la entrega "data layer in action".

## 7. Evidencia: tres benchmarks medibles

| Benchmark | Línea base ingenua | NeuroVoice | Métrica |
| --- | --- | --- | --- |
| **A. Predicción de frases** | Sin memoria: autocompletado genérico (o LLM sin contexto) | LLM con la memoria del usuario | **Pulsaciones ahorradas (%)**, acierto en el top 3, palabras por minuto estimadas |
| **B. Estado afectivo** | Modelo genérico igual para todos | Normalizado a la línea base de cada persona + ajuste con correcciones | Accuracy balanceada con validación dejando un sujeto fuera (WESAD) |
| **C. Latencia** | — | Del evento a la voz | Segundos de punta a punta (objetivo: menos de 2–3 s) |

**Cómo se hace el A sin usuarios reales:** se crea el historial de conversaciones de un usuario ficticio (unos días de frases, personas y rutinas). Se reserva el último día como test y se compara cuántas letras tendría que escribir sin sugerencias, con sugerencias genéricas y con NeuroVoice.

**Mensaje objetivo:** *"Con memoria, NeuroVoice ahorra un X % de las pulsaciones frente a un comunicador sin contexto, y detecta su estado con un Y % de acierto frente al Z % de un modelo genérico."*

## 8. Recorrido de la demo (3 minutos)

1. Pantalla del comunicador de "Lucas" (usuario ficticio con ELA). Llega su hija por la tarde.
2. El agente consulta la memoria y sugiere: "Hola cariño, ¿qué tal el trabajo?". Lucas lo elige con un clic: 1 selección en vez de 35 letras.
3. Entra la señal de WESAD en situación de estrés y la FC y la EDA suben. Lucas elige "Me duele la espalda".
4. **La voz suena con urgencia.** Se reproduce la misma frase plana para comparar.
5. La enfermera francesa entra: la misma frase en francés, con la misma emoción.
6. Lucas corrige ("no era urgente, solo molesto"). El agente lo guarda y la siguiente vez ajusta el tono.
7. Sin que Lucas escriba nada, el estrés sostenido dispara un aviso al cuidador.
8. Para cerrar, la tabla del benchmark en pantalla.

## 9. Repo y reparto

```
hackParis/
├── backend/     FastAPI + agente (Claude) + Postgres/Valkey     → Pedro
├── data/        WESAD → ClickHouse; historial ficticio de frases → María
├── benchmark/   A (pulsaciones), B (afecto), C (latencia)      → María
├── db/          esquemas SQL
├── docs/        api.md, data-layer.md, IDEA.md
└── CLAUDE.md    contexto para Claude Code
vigil-frontend/  (Lovable) comunicador + panel del cuidador       → Marc (+ pitch y vídeo)
```

**Uso de los partners:**

| Partner | Papel |
| --- | --- |
| **Aiven** | Runtime + ClickHouse + PostgreSQL + Valkey (+ OpenSearch) |
| **Claude Platform** | Agente: predicción, decisión y aprendizaje |
| **OpenAI** | Embeddings de la memoria; transcripción de lo que dice el interlocutor (contexto para predecir) |
| **ElevenLabs** | Voz clonada con emoción, en varios idiomas |
| **Keenable** | Contexto externo con fuentes |
| **Lovable** | Comunicador y panel |
| **Supabase** | Auth y audios |

## 10. Camino a los primeros usuarios (para la slide)

1. **Asociaciones de pacientes de ELA:** ADELA, Fundación Luzón (España) y ARSLA (Francia). Acceso directo a usuarios y logopedas para pilotar.
2. **Unidades de ELA y de daño cerebral** de hospitales, con logopedas como prescriptores.
3. **Integración con fabricantes de comunicadores:** Irisbond (España), Tobii Dynavox, Smartbox. NeuroVoice como capa de software sobre sus dispositivos.
4. **Programa de impacto de ElevenLabs**, que ya da voces gratis a pacientes de ELA: un socio natural.

---

# PARTE 3. Futuro: NeuroVoice + DACIU

## 11. La extensión natural

DACIU (Universidad de Sevilla, con Ciudad San Juan de Dios) trabaja con ECG/EDA en personas no verbales. Encaja de dos formas:

**A. Personas sin canal semántico (PIMD, demencia avanzada)**
- No hay frase que elegir, así que la voz habla **en tercera persona** sobre el estado medido: "Lucía muestra activación alta desde hace 10 minutos, compatible con malestar".
- Aquí el producto es la **monitorización del estado para cuidadores** (la idea "Vigil"): el mismo agente, la misma memoria y el mismo aprendizaje con el feedback del personal.
- Regla ética: **nunca poner en boca de la persona algo que no ha elegido.**

**B. Detectar comprensión oculta y dar un canal sí/no (I+D)**
- Potenciales evocados (**N400, P300**) para detectar si una persona comprende el lenguaje sin que tenga que responder.
- Si comprende: **BCI reactivo** (P300 o SSVEP) con pictogramas para responder sí/no y elegir, y NeuroVoice lo dice con su voz.
- **Validación obligatoria con tests ciegos** (preguntas cuya respuesta el cuidador no conoce), por el precedente de la comunicación facilitada.
- Es una línea de doctorado de alto impacto y poco explorada en PIMD.

## 12. Frameworks y librerías para la versión de investigación

| Área | Librerías y herramientas |
| --- | --- |
| Señal fisiológica (ECG, EDA, PPG) | NeuroKit2, BioSPPy, HeartPy, SciPy |
| EEG | MNE-Python, pyRiemann (geometría riemanniana), MOABB (benchmarks de BCI), Braindecode (EEGNet y redes profundas), PyTorch |
| BCI en tiempo real | Lab Streaming Layer (LSL), BrainFlow, OpenViBE, PsychoPy (estímulos N400/P300) |
| ML y personalización | scikit-learn, PyTorch, aprendizaje self-supervised sobre señales de wearables, transfer learning entre sujetos |
| Agente y LLM | Claude (tool use), LangGraph o el Agent SDK de Claude, embeddings (OpenAI) |
| Datos | Aiven ClickHouse (series), PostgreSQL (+ pgvector), Valkey, OpenSearch |
| Voz | ElevenLabs (Voice Design para quien nunca ha hablado; clonación para quien conserva grabaciones) |
| Comunicador | Grid 3, Proloquo2Go, Cboard (open source); estándares de pictogramas como ARASAAC (Aragón, gratuito) |

**Hardware**
- **Fisiológico:** Empatica EmbracePlus, Shimmer3, Bitalino (barato y de investigación), parches de ECG.
- **EEG:** OpenBCI (investigación de bajo coste), g.tec Unicorn (BCI P300), Emotiv, y diademas secas para mejor tolerancia.
- **Eye-tracking:** Irisbond, Tobii.

**Datasets para investigar**
- **Afecto:** WESAD, DEAP (EEG + periféricos con valencia y activación), DREAMER, AMIGOS, CASE.
- **Wearables en la vida real:** PPG-DaLiA.
- **BCI P300:** conjuntos de MOABB (BNCI, EPFL P300).
- **Clínico:** MIMIC-IV (PhysioNet).

## 13. Clientes y socios a futuro

| Segmento | Quién | Qué compra |
| --- | --- | --- |
| Personas con ELA, afasia o ictus (B2C/B2B2C) | Usuarios y familias, vía asociaciones (ADELA, Fundación Luzón, ARSLA) | Voz con emoción y comunicación más rápida |
| Fabricantes de comunicadores (B2B) | Irisbond, Tobii Dynavox, Smartbox | Licencia del motor afectivo y de predicción |
| Centros de discapacidad (B2B) | Ciudad San Juan de Dios y otros centros de PIMD | Monitorización del estado y apoyo al cuidador |
| Residencias de mayores (B2B) | Cadenas de residencias | Detección de malestar en demencia, por cama y mes |
| Hospitales | Unidades de ELA, neurología, UCI | Comunicación y monitorización |
| Financiación | CaixaImpulse, EIT Health, 21st by CentraleSupélec, Andalucía Open Future, proyectos europeos (Horizon) | Transferencia de investigación a producto |

## 14. Próximos pasos tras el hackathon

1. **Hablar con el Dr. Calvillo:** propiedad intelectual de DACIU, vía de spin-off con la OTRI y piloto con San Juan de Dios.
2. **Comité de ética** para el piloto: consentimiento de tutores y RGPD para datos de salud.
3. **Contactar con una asociación de ELA** para validar la versión de comunicación con usuarios reales.
4. **Revisar antecedentes:** el proyecto europeo INSENSION (PIMD) y la investigación holandesa sobre indicadores fisiológicos de emoción en PIMD.
5. **Aplicar a 21st** (lunes) con esta hipótesis: *comunicación y monitorización afectiva para personas que no pueden hablar; entrada por ELA y PIMD, y escala a demencia.*

---

## Entregas del hackathon (antes de las 14:45)

- [ ] Nombre: **NeuroVoice**
- [ ] One-liner: *Una voz que suena como se siente quien no puede hablar: mide su estado, recuerda cómo se comunica y aprende de cada conversación.*
- [ ] Demo de 3 min en MP4 (sección 8)
- [ ] Data layer in action: sección 6 + consultas reales de `agent_log`
- [ ] Evidencia: los benchmarks A, B y C (sección 7)
- [ ] Slide pública: para quién, problema, por qué ahora, arquitectura con Aiven, resultados y primeros usuarios
