"""Links routes – semantic sermon linking and search."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...schemas.link import LinkCreate, LinkRead, SemanticSearchRequest, SemanticSearchResponse
from .service import LinkService

router = APIRouter(prefix="/links", tags=["links"])


@router.get("/sermon/{sermon_id}", response_model=list[LinkRead])
async def get_links(sermon_id: int, db: AsyncSession = Depends(get_db)):
    svc = LinkService(db)
    return await svc.get_links(sermon_id)


@router.post("", response_model=LinkRead, status_code=201)
async def create_link(
    data: LinkCreate,
    _user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = LinkService(db)
    return await svc.create_link(data)


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = LinkService(db)
    return await svc.semantic_search(request)
