# NeuroVoice — submission texts (copy & paste)

## Project name
NeuroVoice

## One-line pitch
NeuroVoice turns four letters into the full sentence a person with ALS wants to say — using their personal memory, and speaking it in their own voice.

## Hosted URL
- App (communicator): <Lovable or Aiven Runtime URL>
- API (agent + data) on Aiven Runtime: https://01a1639e-6ccd-7279-8971-f24b4fece063-8080.eur-1.aiven.app  (/docs, /health)

## Evidence it works
All results come from SIMULATED runs on a fictional user (Lucas, ALS) with a synthetic corpus: memory = days 1–5, test = days 6–8 (56 sentences), no temporal leakage. Same LLM in every variant; only the data changes.

| Variant | Exact sentence, 1st try (top-1) | In top-5 | Keystroke savings (KSR) | p50 latency | Cost/sentence |
|---|---|---|---|---|---|
| LLM, no memory | 12.5% | 14.3% | 11.6% | 3.8 s | $0.0034 |
| LLM + conversation context | 12.5% | 17.9% | 25.5% | 3.6 s | $0.0036 |
| **NeuroVoice (LLM + personal memory in Aiven PostgreSQL/pgvector)** | **35.7%** | **42.9%** | **44.8%** | **3.0 s** | **$0.0038** |
| NeuroVoice + time & wearable state | 21.4% | 32.1% | 42.3% | 3.5 s | $0.0043 |
| Classic predictive keyboard (word frequency) | — | — | 53.0% | — | — |

Takeaways:
- Personal memory is what makes the agent useful: same model, ~3× more sentences guessed right on the first try (12.5% → 35.7%).
- A word-frequency keyboard still saves slightly more keystrokes (53%) in this simulation; NeuroVoice's gain is predicting the WHOLE sentence in one selection, which matters most for eye-gaze users (each selection costs 1–2 s). Next step: hybrid fallback (sentence first, word prediction when it misses).
- Adding time + wearable state to sentence prediction did not help (35.7% → 21.4%), so we use the wearable for the voice tone, not for choosing words.
- Reference: Google's SpeakFaster (Nature Communications, 2024) reported KSR 0.657 vs 0.482 for Gboard with fine-tuned LLMs.

Wearable state model (tone suggestion):
- WESAD wrist sensor (Empatica E4), 15 subjects, rest vs. stress: **95 ± 6% balanced accuracy, leave-one-subject-out** (logistic regression on heart rate, EDA and movement, normalised per person with a short resting calibration).
- 3 classes (rest/stress/amusement): 70 ± 16%, so the agent combines arousal with the meaning of the sentence to suggest the tone, and the user confirms it.
- Shuffled cross-validation would report 97% (inflated by temporal leakage); we report LOSO only.
- Lab data, recorded and replayed in real time, not live sensor data.

## The data layer in action
See data-layer.txt
