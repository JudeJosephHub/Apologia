from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class Sermon(BaseModel):
    id: str
    sermonName: str
    seriesName: Optional[str] = None
    sermonDate: Optional[str] = None
    weekOrDate: Optional[str] = None
    pastorName: Optional[str] = None
    churchName: Optional[str] = None
    youtubeUrl: Optional[str] = None
    youtubeVideoId: Optional[str] = None
    youtubeChannelId: Optional[str] = None
    videoStatus: str = "pending_match"
    transcriptStatus: str = "none"
    status: str
    filePath: str
    originalFilename: str
    createdAt: datetime

    class Config:
        from_attributes = True


class SlideContent(BaseModel):
    slideId: str
    slideNumber: int
    originalText: str


class Suggestion(BaseModel):
    id: str
    category: str
    original: str
    proposed: str
    explanation: Optional[str] = None
    confidence: Optional[float] = None


class SlideAnalysis(BaseModel):
    slideId: str
    slideNumber: int
    originalText: str
    suggestions: List[Suggestion] = []


class AnalysisDocument(BaseModel):
    sermonId: str
    createdAt: datetime
    slides: List[SlideAnalysis] = []


class SuggestionDecision(BaseModel):
    suggestionId: str
    decision: Literal["accepted", "rejected", "edited"]
    finalText: Optional[str] = None


class SlideDecision(BaseModel):
    slideId: str
    slideNumber: int
    decisions: List[SuggestionDecision] = []


class DecisionsDocument(BaseModel):
    sermonId: str
    updatedAt: datetime
    slides: List[SlideDecision] = []


class SlideDecisionPayload(BaseModel):
    decisions: List[SuggestionDecision] = []


class VideoAttachPayload(BaseModel):
    youtubeUrl: str
    youtubeChannelId: Optional[str] = None


class TranscriptFetchPayload(BaseModel):
    language: Optional[str] = None


class TranscriptManualPayload(BaseModel):
    transcriptText: str
    language: Optional[str] = None


class TranscriptSegment(BaseModel):
    startSeconds: float
    durationSeconds: float
    text: str


class TranscriptDocument(BaseModel):
    sermonId: str
    videoId: Optional[str] = None
    language: Optional[str] = None
    status: Literal["none", "pending", "ready", "unavailable"] = "none"
    source: Optional[str] = None
    fetchedAt: Optional[datetime] = None
    transcriptText: str = ""
    segments: List[TranscriptSegment] = []
    note: Optional[str] = None


class DailyInspiration(BaseModel):
    date: str
    kind: Literal["verse", "quote"]
    text: str
    citation: str
