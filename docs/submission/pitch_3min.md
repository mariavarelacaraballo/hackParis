# Video script (3 min)
0:00 Problem: "Lucas has ALS and speaks with his eyes: under 10 words per minute. Saying 'my back hurts' takes 40 glances. And his synthetic voice sounds flat."
0:25 Idea: "NeuroVoice is an agent with memory. Lucas types the initials and the agent completes the sentence with what it knows about him: who is with him, what he usually says, how he feels. He always chooses."
0:45 Demo: Rosa asks "Are you comfortable?" → "m d l e" → 5 sentences → he selects with his gaze → it plays in his voice.
     Open the agent reasoning panel: memory (Postgres) → context (Valkey) → wristband state.
     Claire (French nurse) → the same sentence in French. Wristband shows stress → suggested tone 'annoyed', Lucas confirms it.
1:50 Data: "Everything lives on Aiven: memory with pgvector, session in Valkey, signals and metrics in ClickHouse, and the API on Runtime."
2:15 Evidence: "Same model, but his memory triples the sentences guessed right on the first try: from 12% to 36%. The wristband tells rest from stress with 95% accuracy on people the model has never seen. All in simulation."
2:40 First users: "Pilot with ALS users through patient associations (adELA, Fundación Luzón, ARSLA), then a plug-in for Grid 3 and TD Snap. 97 million people could benefit from AAC. We start with ALS."
