"""Celery worker configuration and tasks."""

import logging

from celery import Celery

from .core import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "sermonopedia",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def transcribe_sermon_task(self, sermon_id: int, audio_url: str):
    """Background task: transcribe audio via AssemblyAI then generate embeddings."""
    from .domains.ai.service import AIService

    try:
        ai = AIService()
        transcript = ai.transcribe_audio(audio_url)
        logger.info("Transcription complete for sermon %s (%d chars)", sermon_id, len(transcript))
        # In production, update the sermon record in DB with transcript + embedding
        # This would use a sync DB session since Celery tasks are synchronous
        return {"sermon_id": sermon_id, "transcript_length": len(transcript)}
    except Exception as exc:
        logger.error("Transcription failed for sermon %s: %s", sermon_id, exc)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(bind=True, max_retries=3)
def generate_embedding_task(self, sermon_id: int, text: str):
    """Background task: generate sermon embedding."""
    import asyncio

    from .domains.ai.service import AIService

    try:
        ai = AIService()
        embedding = asyncio.run(ai.generate_embedding(text))
        logger.info("Embedding generated for sermon %s (%d dims)", sermon_id, len(embedding))
        return {"sermon_id": sermon_id, "embedding_dims": len(embedding)}
    except Exception as exc:
        logger.error("Embedding generation failed for sermon %s: %s", sermon_id, exc)
        raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
