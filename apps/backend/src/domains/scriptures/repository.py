"""Scriptures repository – data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Scripture, SermonScripture


class ScriptureRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_reference(self, *, book: str, chapter: int, verse_start: int, translation: str = "KJV") -> Scripture | None:
        result = await self.db.execute(
            select(Scripture).where(
                Scripture.book == book,
                Scripture.chapter == chapter,
                Scripture.verse_start == verse_start,
                Scripture.translation == translation,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, *, book: str, chapter: int, verse_start: int, verse_end: int | None = None, text: str = "", translation: str = "KJV") -> Scripture:
        existing = await self.get_by_reference(book=book, chapter=chapter, verse_start=verse_start, translation=translation)
        if existing:
            return existing
        scripture = Scripture(book=book, chapter=chapter, verse_start=verse_start, verse_end=verse_end, text=text, translation=translation)
        self.db.add(scripture)
        await self.db.commit()
        await self.db.refresh(scripture)
        return scripture

    async def get_by_sermon_id(self, sermon_id: int) -> list[SermonScripture]:
        result = await self.db.execute(
            select(SermonScripture).where(SermonScripture.sermon_id == sermon_id)
        )
        return list(result.scalars().all())

    async def link_scripture_to_sermon(self, *, sermon_id: int, scripture_id: int, context: str = "") -> SermonScripture:
        mapping = SermonScripture(sermon_id=sermon_id, scripture_id=scripture_id, context=context)
        self.db.add(mapping)
        await self.db.commit()
        await self.db.refresh(mapping)
        return mapping

    async def search_by_book(self, book: str) -> list[Scripture]:
        result = await self.db.execute(
            select(Scripture).where(Scripture.book.ilike(f"%{book}%")).order_by(Scripture.chapter, Scripture.verse_start)
        )
        return list(result.scalars().all())
