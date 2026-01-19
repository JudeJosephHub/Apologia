from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class Sermon(BaseModel):
    id: str
    sermonName: str
    seriesName: Optional[str] = None
    weekOrDate: Optional[str] = None
    pastorName: Optional[str] = None
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
