"""Links repository – data access layer for sermon links."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import SermonLink


class LinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_links_for_sermon(self, sermon_id: int) -> list[SermonLink]:
        result = await self.db.execute(
            select(SermonLink).where(
                or_(
                    SermonLink.source_sermon_id == sermon_id,
                    SermonLink.target_sermon_id == sermon_id,
                )
            ).order_by(SermonLink.score.desc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> SermonLink:
        link = SermonLink(**kwargs)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def delete(self, link: SermonLink) -> None:
        await self.db.delete(link)
        await self.db.commit()
