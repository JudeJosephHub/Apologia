"""Semantic sermon linking schemas."""

from pydantic import BaseModel


class LinkBase(BaseModel):
    source_sermon_id: int
    target_sermon_id: int
    link_type: str  # thematic | scriptural | topical | series
    score: float = 0.0
    reason: str | None = None


class LinkCreate(LinkBase):
    pass


class LinkRead(LinkBase):
    id: int

    model_config = {"from_attributes": True}


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10
    threshold: float = 0.5


class SemanticSearchResult(BaseModel):
    sermon_id: int
    title: str
    score: float
    snippet: str | None = None


class SemanticSearchResponse(BaseModel):
    results: list[SemanticSearchResult]
    total: int
