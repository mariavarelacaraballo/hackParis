from fastapi import APIRouter

from .. import config

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True, "mock": config.MOCK}
