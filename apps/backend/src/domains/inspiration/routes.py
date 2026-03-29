"""Daily inspiration route (ported from Apologia)."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from .service import generate_daily_inspiration

router = APIRouter(tags=["inspiration"])


class DailyInspiration(BaseModel):
    date: str
    kind: str
    text: str
    citation: str


# Simple in-memory cache (one day at a time)
_cache: dict = {}


@router.get("/inspiration/daily", response_model=DailyInspiration)
async def get_daily_inspiration():
    date_key = datetime.now(timezone.utc).date().isoformat()
    if date_key in _cache:
        return DailyInspiration(**_cache[date_key])
    data = generate_daily_inspiration(date_key)
    _cache[date_key] = data
    return DailyInspiration(**data)
