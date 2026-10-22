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

@app.exception_handler(Exception)
async def show_error(request, exc):
    """Durante el hackathon: devolver el error completo para depurar rápido."""
    import traceback
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"error": repr(exc), "status": getattr(exc, "status_code", None), "body": str(getattr(exc, "body", ""))[:500], "trace": traceback.format_exc().splitlines()[-12:]})


for r in (health, context, expand, choice, speak, listen, wearable, state, trace):
    app.include_router(r.router)
