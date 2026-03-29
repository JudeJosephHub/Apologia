"""Scriptures routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...schemas.scripture import ScriptureRead
from .service import ScriptureService

router = APIRouter(prefix="/scriptures", tags=["scriptures"])


@router.get("/sermon/{sermon_id}", response_model=list[ScriptureRead])
async def get_scriptures_for_sermon(sermon_id: int, db: AsyncSession = Depends(get_db)):
    svc = ScriptureService(db)
    return await svc.get_scriptures_for_sermon(sermon_id)


@router.get("/search", response_model=list[ScriptureRead])
async def search_scriptures(book: str, db: AsyncSession = Depends(get_db)):
    svc = ScriptureService(db)
    return await svc.search_by_book(book)
