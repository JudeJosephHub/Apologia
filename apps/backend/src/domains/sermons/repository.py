"""Sermons repository – data access layer."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Sermon, UserSermon


class SermonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_sermons(self, *, offset: int = 0, limit: int = 20, search: str | None = None) -> tuple[list[Sermon], int]:
        query = select(Sermon).where(Sermon.status == "published")
        count_query = select(func.count(Sermon.id)).where(Sermon.status == "published")

        if search:
            pattern = f"%{search}%"
            query = query.where(Sermon.title.ilike(pattern) | Sermon.preacher.ilike(pattern))
            count_query = count_query.where(Sermon.title.ilike(pattern) | Sermon.preacher.ilike(pattern))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Sermon.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, sermon_id: int) -> Sermon | None:
        result = await self.db.execute(select(Sermon).where(Sermon.id == sermon_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Sermon:
        sermon = Sermon(**kwargs)
        self.db.add(sermon)
        await self.db.commit()
        await self.db.refresh(sermon)
        return sermon

    async def update(self, sermon: Sermon, **kwargs) -> Sermon:
        for key, value in kwargs.items():
            if hasattr(sermon, key):
                setattr(sermon, key, value)
        await self.db.commit()
        await self.db.refresh(sermon)
        return sermon

    async def delete(self, sermon: Sermon) -> None:
        await self.db.delete(sermon)
        await self.db.commit()


class UserSermonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_profile(self, profile_id: int, *, offset: int = 0, limit: int = 20) -> tuple[list[UserSermon], int]:
        count_result = await self.db.execute(
            select(func.count(UserSermon.id)).where(UserSermon.profile_id == profile_id)
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(UserSermon)
            .where(UserSermon.profile_id == profile_id)
            .order_by(UserSermon.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, sermon_id: int, profile_id: int) -> UserSermon | None:
        result = await self.db.execute(
            select(UserSermon).where(UserSermon.id == sermon_id, UserSermon.profile_id == profile_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, profile_id: int, **kwargs) -> UserSermon:
        sermon = UserSermon(profile_id=profile_id, **kwargs)
        self.db.add(sermon)
        await self.db.commit()
        await self.db.refresh(sermon)
        return sermon

    async def update(self, sermon: UserSermon, **kwargs) -> UserSermon:
        for key, value in kwargs.items():
            if hasattr(sermon, key):
                setattr(sermon, key, value)
        await self.db.commit()
        await self.db.refresh(sermon)
        return sermon

    async def delete(self, sermon: UserSermon) -> None:
        await self.db.delete(sermon)
        await self.db.commit()
