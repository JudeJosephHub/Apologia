"""AI-related request/response schemas."""

from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 500


class SummarizeResponse(BaseModel):
    summary: str


class BrainstormRequest(BaseModel):
    topic: str
    scripture_refs: list[str] = []
    style: str = "expository"


class BrainstormResponse(BaseModel):
    outline: str
    key_points: list[str]
    suggested_scriptures: list[str]


class SermonDraftRequest(BaseModel):
    topic: str
    outline: str | None = None
    scripture_refs: list[str] = []
    style: str = "expository"
    length: str = "medium"  # short | medium | long


class SermonDraftResponse(BaseModel):
    draft: str
    title_suggestion: str


class TranscriptionStatus(BaseModel):
    sermon_id: int
    status: str  # queued | processing | completed | failed
    transcript: str | None = None


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    embedding: list[float]
