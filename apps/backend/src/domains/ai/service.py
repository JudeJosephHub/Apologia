"""AI service – integrations with OpenAI, Groq, AssemblyAI."""

import logging

from fastapi import HTTPException, status

from ...core import get_settings
from ...schemas.ai import (
    BrainstormRequest,
    BrainstormResponse,
    SermonDraftRequest,
    SermonDraftResponse,
    SummarizeRequest,
    SummarizeResponse,
)

logger = logging.getLogger(__name__)

_AI_UNAVAILABLE = "AI features require API keys. Configure OPENAI_API_KEY in your .env file."


class AIService:
    def __init__(self):
        settings = get_settings()
        self._openai = None
        self._groq = None
        if settings.openai_api_key:
            import openai
            self._openai = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        if settings.groq_api_key:
            from groq import Groq
            self._groq = Groq(api_key=settings.groq_api_key)
        if settings.assemblyai_api_key:
            import assemblyai
            assemblyai.settings.api_key = settings.assemblyai_api_key

    def _require_openai(self):
        if not self._openai:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=_AI_UNAVAILABLE)

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        self._require_openai()
        response = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a theology expert. Provide a concise sermon summary."},
                {"role": "user", "content": f"Summarize the following sermon text in {request.max_length} words or fewer:\n\n{request.text}"},
            ],
            max_tokens=request.max_length * 2,
        )
        return SummarizeResponse(summary=response.choices[0].message.content or "")

    async def brainstorm(self, request: BrainstormRequest) -> BrainstormResponse:
        self._require_openai()
        prompt = f"Help brainstorm a {request.style} sermon on '{request.topic}'."
        if request.scripture_refs:
            prompt += f"\nKey scriptures: {', '.join(request.scripture_refs)}"
        prompt += "\nProvide: 1) A sermon outline 2) Key points 3) Suggested additional scriptures."

        response = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a pastor's assistant specializing in sermon preparation."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return BrainstormResponse(outline=content, key_points=[], suggested_scriptures=[])

    async def generate_draft(self, request: SermonDraftRequest) -> SermonDraftResponse:
        self._require_openai()
        prompt = f"Write a {request.length} {request.style} sermon on '{request.topic}'."
        if request.outline:
            prompt += f"\nFollow this outline:\n{request.outline}"
        if request.scripture_refs:
            prompt += f"\nIncorporate these scriptures: {', '.join(request.scripture_refs)}"

        response = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert sermon writer."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return SermonDraftResponse(draft=content, title_suggestion=request.topic)

    async def generate_embedding(self, text: str) -> list[float]:
        self._require_openai()
        response = await self._openai.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding

    def transcribe_audio(self, audio_url: str) -> str:
        """Synchronous transcription via AssemblyAI – call from Celery worker."""
        import assemblyai
        transcriber = assemblyai.Transcriber()
        transcript = transcriber.transcribe(audio_url)
        if transcript.status == assemblyai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription failed: {transcript.error}")
        return transcript.text or ""
