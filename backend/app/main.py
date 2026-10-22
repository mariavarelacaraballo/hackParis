"""API de NeuroVoice (FastAPI). Se despliega en Aiven Runtime. [Pedro]

Arranque local:  uvicorn backend.app.main:app --reload
Despliegue: TODO(Pedro) seguir la guía de Aiven Runtime (comando de arranque = el de arriba con --host 0.0.0.0 --port $PORT).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .routes import choice, context, expand, health, listen, speak, state, trace, wearable

app = FastAPI(title="NeuroVoice API")
app.add_middleware(CORSMiddleware, allow_origins=[config.FRONTEND_ORIGIN], allow_methods=["*"], allow_headers=["*"])

for r in (health, context, expand, choice, speak, listen, wearable, state, trace):
    app.include_router(r.router)
