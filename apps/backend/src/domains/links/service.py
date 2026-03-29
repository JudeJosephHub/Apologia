"""Links service – semantic sermon linking business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.link import LinkCreate, LinkRead, SemanticSearchRequest, SemanticSearchResponse, SemanticSearchResult
from ..ai.service import AIService
from .repository import LinkRepository


class LinkService:
    def __init__(self, db: AsyncSession):
        self.repo = LinkRepository(db)
        self.db = db
        self.ai = AIService()

    async def get_links(self, sermon_id: int) -> list[LinkRead]:
        links = await self.repo.get_links_for_sermon(sermon_id)
        return [LinkRead.model_validate(link) for link in links]

    async def create_link(self, data: LinkCreate) -> LinkRead:
        link = await self.repo.create(**data.model_dump())
        return LinkRead.model_validate(link)

    async def semantic_search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """Search sermons by semantic similarity using pgvector."""
        try:
            query_embedding = await self.ai.generate_embedding(request.query)
        except Exception:
            return SemanticSearchResponse(results=[], total=0)

        from sqlalchemy import text

        sql = text("""
            SELECT id, title, 1 - (embedding <=> :embedding::vector) AS score
            FROM sermons
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        result = await self.db.execute(sql, {"embedding": str(query_embedding), "limit": request.limit})
        rows = result.fetchall()

        results = [
            SemanticSearchResult(sermon_id=row.id, title=row.title, score=row.score)
            for row in rows
            if row.score >= request.threshold
        ]
        return SemanticSearchResponse(results=results, total=len(results))
