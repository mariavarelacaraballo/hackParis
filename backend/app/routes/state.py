from fastapi import APIRouter

from .. import config

router = APIRouter()


@router.get("/state/{user_id}")
def get_state(user_id: str):
    if config.MOCK:
        return {"activation": "alta", "confidence": 0.81, "suggested_tone": "molesto"}
    from ..db import valkey
    return valkey.get_state(user_id)
