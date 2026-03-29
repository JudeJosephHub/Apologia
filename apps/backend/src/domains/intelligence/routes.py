"""Intelligence / Encyclopedia routes (ported from Apologia)."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ..sermons.models import Sermon
from .schemas import (
    CourseSuggestionSchema,
    EntityExplorationSchema,
    FullGraphSchema,
    IndexResultSchema,
    SermonGraphSchema,
    SermonIntelligence,
)
from .service import (
    analyze_sermon_intelligence,
    explore_entity,
    find_related_sermons,
    get_all_entities,
    get_full_graph,
    get_sermon_graph,
    index_all_sermons,
    search_sermons,
    suggest_course,
)

router = APIRouter(prefix="/encyclopedia", tags=["encyclopedia"])


@router.post("/index", response_model=IndexResultSchema)
async def index_sermons(db: AsyncSession = Depends(get_db)):
    """Index all sermons with content into vector store and build knowledge graph."""
    result = await index_all_sermons(db)
    return IndexResultSchema(**result)


@router.get("/graph", response_model=FullGraphSchema)
async def full_graph(db: AsyncSession = Depends(get_db)):
    """Return the complete knowledge graph for visualization."""
    data = await get_full_graph(db)
    return FullGraphSchema(**data)


@router.get("/entities")
async def all_entities(db: AsyncSession = Depends(get_db)):
    """Return all entities grouped by type."""
    return await get_all_entities(db)


@router.get("/explore/{entity_type}/{entity_value}", response_model=EntityExplorationSchema)
async def explore(entity_type: str, entity_value: str, db: AsyncSession = Depends(get_db)):
    """Find all sermons related to a specific entity."""
    data = await explore_entity(db, entity_type, entity_value)
    return EntityExplorationSchema(**data)


@router.get("/search")
async def semantic_search(q: str = Query(...), n: int = Query(10)):
    """Semantic search across all sermon content."""
    return search_sermons(q, n_results=n)


@router.get("/courses/suggest", response_model=CourseSuggestionSchema)
async def suggest_course_endpoint(
    topic: str = Query(...),
    max_sermons: int = Query(10),
    db: AsyncSession = Depends(get_db),
):
    """Suggest a course / learning path for a theological topic."""
    data = await suggest_course(db, topic, max_sermons=max_sermons)
    return CourseSuggestionSchema(**data)


# ── Per-sermon intelligence endpoints ────────────────────────────────────


@router.get("/sermons/{sermon_id}/intelligence", response_model=SermonIntelligence)
async def sermon_intelligence(sermon_id: int, db: AsyncSession = Depends(get_db)):
    """Run intelligence extraction on a single sermon."""
    result = await db.execute(select(Sermon).where(Sermon.id == sermon_id))
    sermon = result.scalar_one_or_none()
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    content = sermon.transcript
    if not content:
        raise HTTPException(status_code=404, detail="No content available for this sermon")
    intel = analyze_sermon_intelligence(
        sermon_id=sermon.id,
        sermon_name=sermon.title,
        content=content,
        preacher=sermon.preacher,
        themes_json=sermon.themes,
        denomination=sermon.denomination,
    )
    return SermonIntelligence(**intel)


@router.get("/sermons/{sermon_id}/related")
async def related_sermons(sermon_id: int, n: int = Query(5), db: AsyncSession = Depends(get_db)):
    """Find semantically related sermons via vector similarity."""
    result = await db.execute(select(Sermon).where(Sermon.id == sermon_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sermon not found")
    return find_related_sermons(sermon_id, n_results=n)


@router.get("/sermons/{sermon_id}/graph", response_model=SermonGraphSchema)
async def sermon_graph(sermon_id: int, db: AsyncSession = Depends(get_db)):
    """Get the knowledge graph centered on this sermon."""
    result = await db.execute(select(Sermon).where(Sermon.id == sermon_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sermon not found")
    data = await get_sermon_graph(db, sermon_id)
    return SermonGraphSchema(**data)
