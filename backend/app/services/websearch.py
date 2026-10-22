"""Keenable: búsqueda web del agente (opcional). [Pedro]

TODO(Pedro): mirar docs.keenable.ai (endpoint de búsqueda y cabecera de auth) y rellenar.
Devolver lista corta: [{"title", "url", "snippet"}]. Si no hay clave, devolver [] (el agente sigue sin web).
"""
from .. import config


def search(query: str) -> list[dict]:
    if not config.KEENABLE_API_KEY:
        return []
    # import httpx
    # r = httpx.post("<ENDPOINT DE KEENABLE>", headers={"Authorization": f"Bearer {config.KEENABLE_API_KEY}"},
    #                json={"query": query, "limit": 3}, timeout=10)
    # return [{"title": x["title"], "url": x["url"], "snippet": x.get("snippet", "")} for x in r.json()[...]]
    return []
