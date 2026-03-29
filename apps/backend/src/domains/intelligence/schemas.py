"""Intelligence schemas for encyclopedia endpoints."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class SermonIntelligence(BaseModel):
    sermon_id: int
    sermon_name: str
    pastor_name: Optional[str] = None
    themes: List[str] = []
    scripture_refs: List[str] = []
    theological_concepts: List[str] = []
    traditions: List[str] = []
    chunk_count: int = 0
    indexed_at: Optional[str] = None


class GraphEdgeSchema(BaseModel):
    type: str
    weight: float
    shared: List[str] = []


class RelatedSermonSchema(BaseModel):
    sermon_id: int
    sermon_name: str
    pastor_name: Optional[str] = None
    total_weight: float = 0.0
    similarity: Optional[float] = None
    edges: List[GraphEdgeSchema] = []


class SermonGraphSchema(BaseModel):
    sermon_id: int
    entities: dict = {}
    related_sermons: List[RelatedSermonSchema] = []
    edge_count: int = 0


class GraphNodeSchema(BaseModel):
    id: int
    sermon_name: str
    pastor_name: Optional[str] = None
    denomination: Optional[str] = None
    entities: dict = {}


class FullGraphSchema(BaseModel):
    nodes: List[GraphNodeSchema] = []
    edges: List[dict] = []


class EntityExplorationSchema(BaseModel):
    entity_type: str
    entity_value: str
    sermon_count: int
    sermons: List[dict] = []


class CourseSuggestionSchema(BaseModel):
    topic: str
    sermon_count: int
    sermons: List[dict] = []
    themes_covered: List[str] = []
    concepts_covered: List[str] = []
    scripture_refs: List[str] = []


class IndexResultSchema(BaseModel):
    indexed: int
    total_chunks: int
    sermons: List[dict] = []
