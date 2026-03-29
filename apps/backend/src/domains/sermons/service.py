"""Sermons service – business logic."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.sermon import SermonCreate, SermonList, SermonRead
from .repository import SermonRepository


class SermonService:
    def __init__(self, db: AsyncSession):
        self.repo = SermonRepository(db)

    async def list_sermons(self, *, offset: int = 0, limit: int = 20, search: str | None = None) -> SermonList:
        sermons, total = await self.repo.list_sermons(offset=offset, limit=limit, search=search)
        return SermonList(
            items=[SermonRead.model_validate(s) for s in sermons],
            total=total,
        )

    async def get_sermon(self, sermon_id: int) -> SermonRead:
        sermon = await self.repo.get_by_id(sermon_id)
        if not sermon:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
        return SermonRead.model_validate(sermon)

    async def create_sermon(self, data: SermonCreate) -> SermonRead:
        sermon = await self.repo.create(**data.model_dump())
        return SermonRead.model_validate(sermon)

    async def update_sermon(self, sermon_id: int, data: dict) -> SermonRead:
        sermon = await self.repo.get_by_id(sermon_id)
        if not sermon:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
        updated = await self.repo.update(sermon, **data)
        return SermonRead.model_validate(updated)

    async def delete_sermon(self, sermon_id: int) -> None:
        sermon = await self.repo.get_by_id(sermon_id)
        if not sermon:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
        await self.repo.delete(sermon)
