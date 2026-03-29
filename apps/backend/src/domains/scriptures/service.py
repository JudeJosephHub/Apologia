"""Scriptures service – business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.scripture import ScriptureRead
from .repository import ScriptureRepository


class ScriptureService:
    def __init__(self, db: AsyncSession):
        self.repo = ScriptureRepository(db)

    async def get_scriptures_for_sermon(self, sermon_id: int) -> list[ScriptureRead]:
        mappings = await self.repo.get_by_sermon_id(sermon_id)
        return [ScriptureRead.model_validate(m.scripture) for m in mappings if m.scripture]

    async def link_scripture(self, *, sermon_id: int, book: str, chapter: int, verse_start: int, verse_end: int | None = None, text: str = "", context: str = ""):
        scripture = await self.repo.get_or_create(
            book=book, chapter=chapter, verse_start=verse_start, verse_end=verse_end, text=text
        )
        return await self.repo.link_scripture_to_sermon(sermon_id=sermon_id, scripture_id=scripture.id, context=context)

    async def search_by_book(self, book: str) -> list[ScriptureRead]:
        scriptures = await self.repo.search_by_book(book)
        return [ScriptureRead.model_validate(s) for s in scriptures]
