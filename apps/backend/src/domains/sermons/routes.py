"""Sermons routes."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...schemas.sermon import SermonCreate, SermonList, SermonRead
from .service import SermonService

router = APIRouter(prefix="/sermons", tags=["sermons"])


@router.get("", response_model=SermonList)
async def list_sermons(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    svc = SermonService(db)
    return await svc.list_sermons(offset=offset, limit=limit, search=search)


@router.get("/{sermon_id}", response_model=SermonRead)
async def get_sermon(sermon_id: int, db: AsyncSession = Depends(get_db)):
    svc = SermonService(db)
    return await svc.get_sermon(sermon_id)


@router.post("", response_model=SermonRead, status_code=201)
async def create_sermon(
    data: SermonCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = SermonService(db)
    return await svc.create_sermon(data)


class SermonUpdate(BaseModel):
    title: str | None = None
    preacher: str | None = None
    transcript: str | None = None
    summary: str | None = None
    outline: str | None = None
    themes: str | None = None
    status: str | None = None


@router.patch("/{sermon_id}", response_model=SermonRead)
async def update_sermon(
    sermon_id: int,
    data: SermonUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = SermonService(db)
    return await svc.update_sermon(sermon_id, data.model_dump(exclude_unset=True))


@router.delete("/{sermon_id}", status_code=204)
async def delete_sermon(
    sermon_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = SermonService(db)
    await svc.delete_sermon(sermon_id)
