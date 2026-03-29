"""AI routes – summarization, brainstorm, draft, transcription."""

from fastapi import APIRouter, Depends

from ...core.auth import get_current_user
from ...schemas.ai import (
    BrainstormRequest,
    BrainstormResponse,
    SermonDraftRequest,
    SermonDraftResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from .service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest, _user: dict = Depends(get_current_user)):
    svc = AIService()
    return await svc.summarize(request)


@router.post("/brainstorm", response_model=BrainstormResponse)
async def brainstorm(request: BrainstormRequest, _user: dict = Depends(get_current_user)):
    svc = AIService()
    return await svc.brainstorm(request)


@router.post("/draft", response_model=SermonDraftResponse)
async def generate_draft(request: SermonDraftRequest, _user: dict = Depends(get_current_user)):
    svc = AIService()
    return await svc.generate_draft(request)
