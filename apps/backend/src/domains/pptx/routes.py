"""PPTX routes (ported from Apologia).

Handles PPTX upload, slide viewing, AI slide analysis, decision tracking,
updated PPTX generation, transcript management, and summaries.
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pptx import Presentation
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import get_settings
from ...core.database import get_db
from ..sermons.models import Sermon
from .schemas import (
    AnalysisDocument,
    DecisionsDocument,
    SlideAnalysis,
    SlideContent,
    SlideDecision,
    SlideDecisionPayload,
    TranscriptDocument,
    TranscriptFetchPayload,
    TranscriptManualPayload,
    VideoAttachPayload,
)
from .service import (
    BedrockAgentError,
    analyze_slide_text,
    apply_decisions_to_pptx,
    build_sermon_summary,
    build_transcript_summary,
    extract_slide_text,
    fetch_transcript_with_fallback,
    init_sermon_state,
    list_slides,
    load_analysis,
    load_decisions,
    load_transcript,
    save_analysis,
    save_decisions,
    save_transcript,
    transcript_to_segments,
)

router = APIRouter(prefix="/pptx", tags=["pptx"])


def _youtube_video_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    raw = url.strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be"):
        return parsed.path.strip("/").split("/")[0] or None
    if "youtube.com" in host:
        qv = parse_qs(parsed.query).get("v", [])
        if qv and qv[0]:
            return qv[0]
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "live", "embed"}:
            return parts[1]
    return None


def _slugify(value: Optional[str]) -> str:
    source = (value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", source).strip("-")
    return slug or "series"


async def _get_sermon(db: AsyncSession, sermon_id: int) -> Sermon:
    result = await db.execute(select(Sermon).where(Sermon.id == sermon_id))
    sermon = result.scalar_one_or_none()
    if not sermon:
        raise HTTPException(status_code=404, detail="Sermon not found")
    return sermon


def _resolve_upload_path(sermon: Sermon) -> Path:
    settings = get_settings()
    if sermon.file_path:
        candidate = settings.upload_path / sermon.file_path
        if candidate.exists():
            return candidate
    if sermon.original_filename:
        return settings.upload_path / str(sermon.id) / sermon.original_filename
    raise HTTPException(status_code=404, detail="No PPTX file associated with this sermon")


def _get_presentation(sermon: Sermon) -> Presentation:
    path = _resolve_upload_path(sermon)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PPTX file missing from disk")
    try:
        return Presentation(path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid PPTX: {exc}") from exc


# ── Upload ────────────────────────────────────────────────────────────────


@router.post("/upload", status_code=201)
async def upload_pptx(
    file: UploadFile = File(...),
    sermonName: str = Form(...),
    seriesName: Optional[str] = Form(None),
    sermonDate: Optional[str] = Form(None),
    pastorName: Optional[str] = Form(None),
    churchName: Optional[str] = Form(None),
    youtubeUrl: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    filename = file.filename or ""
    if not filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are supported.")

    safe_filename = Path(filename).name
    video_id = _youtube_video_id(youtubeUrl)
    video_status = "attached" if video_id else "pending_match"

    sermon = Sermon(
        title=sermonName,
        preacher=pastorName or "",
        date_preached=sermonDate or "",
        series_name=seriesName or "",
        church_name=churchName or "",
        youtube_url=youtubeUrl or "",
        youtube_video_id=video_id or "",
        video_status=video_status,
        transcript_status="none",
        status="uploaded",
        original_filename=safe_filename,
    )
    db.add(sermon)
    await db.flush()  # get the ID

    settings = get_settings()
    sermon_dir = settings.upload_path / str(sermon.id)
    sermon_dir.mkdir(parents=True, exist_ok=True)
    destination = sermon_dir / safe_filename
    with destination.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    try:
        Presentation(destination)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        await db.rollback()
        raise HTTPException(status_code=422, detail=f"Invalid PPTX file: {exc}") from exc

    sermon.file_path = f"{sermon.id}/{safe_filename}"
    await db.commit()
    await db.refresh(sermon)

    init_sermon_state(str(sermon.id))

    return {
        "id": sermon.id,
        "title": sermon.title,
        "status": sermon.status,
        "file_path": sermon.file_path,
    }


# ── Slides ────────────────────────────────────────────────────────────────


@router.get("/{sermon_id}/slides", response_model=List[SlideContent])
async def get_slides(sermon_id: int, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    prs = _get_presentation(sermon)
    return list_slides(prs, str(sermon_id))


@router.post("/{sermon_id}/summary")
async def summarize_sermon(sermon_id: int, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    prs = _get_presentation(sermon)
    return {"sermonId": sermon_id, "summary": build_sermon_summary(prs)}


@router.post("/{sermon_id}/summary/from-transcript")
async def summarize_from_transcript(sermon_id: int, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    transcript = load_transcript(str(sermon_id))
    if not (transcript.transcriptText or "").strip():
        raise HTTPException(status_code=409, detail=f"Transcript not ready (status={transcript.status}).")
    return {"sermonId": sermon_id, "source": "transcript", "summary": build_transcript_summary(transcript.transcriptText)}


# ── Slide Analysis ────────────────────────────────────────────────────────


@router.post("/{sermon_id}/slides/{slide_number}/analyze", response_model=SlideAnalysis)
async def analyze_slide(sermon_id: int, slide_number: int, db: AsyncSession = Depends(get_db)):
    if slide_number < 1:
        raise HTTPException(status_code=400, detail="Invalid slide number")
    sermon = await _get_sermon(db, sermon_id)
    prs = _get_presentation(sermon)
    try:
        slide = prs.slides[slide_number - 1]
    except IndexError:
        raise HTTPException(status_code=404, detail="Slide not found")

    slide_id = f"{sermon_id}:{slide_number}"
    original_text = extract_slide_text(slide)
    try:
        suggestions = analyze_slide_text(slide_id, original_text)
    except (BedrockAgentError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=f"Bedrock analysis failed: {exc}") from exc

    analysis = SlideAnalysis(slideId=slide_id, slideNumber=slide_number, originalText=original_text, suggestions=suggestions)

    init_sermon_state(str(sermon_id))
    doc = load_analysis(str(sermon_id))
    for idx, existing in enumerate(doc.slides):
        if existing.slideId == slide_id:
            doc.slides[idx] = analysis
            break
    else:
        doc.slides.append(analysis)
    save_analysis(doc)
    return analysis


@router.get("/{sermon_id}/analysis", response_model=AnalysisDocument)
async def get_analysis(sermon_id: int, db: AsyncSession = Depends(get_db)):
    await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    return load_analysis(str(sermon_id))


# ── Decisions ─────────────────────────────────────────────────────────────


@router.post("/{sermon_id}/slides/{slide_number}/decisions", response_model=SlideDecision)
async def save_slide_decisions(
    sermon_id: int, slide_number: int, payload: SlideDecisionPayload, db: AsyncSession = Depends(get_db)
):
    if slide_number < 1:
        raise HTTPException(status_code=400, detail="Invalid slide number")
    await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    slide_id = f"{sermon_id}:{slide_number}"
    decision = SlideDecision(slideId=slide_id, slideNumber=slide_number, decisions=payload.decisions)
    doc = load_decisions(str(sermon_id))
    doc.updatedAt = datetime.now(timezone.utc)
    for idx, existing in enumerate(doc.slides):
        if existing.slideId == slide_id:
            doc.slides[idx] = decision
            break
    else:
        doc.slides.append(decision)
    save_decisions(doc)
    return decision


@router.get("/{sermon_id}/decisions", response_model=DecisionsDocument)
async def get_decisions(sermon_id: int, db: AsyncSession = Depends(get_db)):
    await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    return load_decisions(str(sermon_id))


# ── Generate updated PPTX ────────────────────────────────────────────────


@router.post("/{sermon_id}/generate-updated-pptx")
async def generate_updated_pptx(sermon_id: int, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    analysis = load_analysis(str(sermon_id))
    decisions = load_decisions(str(sermon_id))
    prs = _get_presentation(sermon)
    apply_decisions_to_pptx(prs, analysis, decisions)
    settings = get_settings()
    output_path = settings.storage_path / "sermons" / str(sermon_id) / "output.pptx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_path)
    return {"status": "ready"}


@router.get("/{sermon_id}/download-updated-pptx")
async def download_updated_pptx(sermon_id: int, db: AsyncSession = Depends(get_db)):
    await _get_sermon(db, sermon_id)
    settings = get_settings()
    output_path = settings.storage_path / "sermons" / str(sermon_id) / "output.pptx"
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Updated PPTX not generated yet")
    return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=f"sermon-{sermon_id}-updated.pptx")


@router.get("/{sermon_id}/download-original-pptx")
async def download_original_pptx(sermon_id: int, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    path = _resolve_upload_path(sermon)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Original file missing")
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=sermon.original_filename or f"sermon-{sermon_id}.pptx")


# ── Video / Transcript ────────────────────────────────────────────────────


@router.post("/{sermon_id}/video/attach")
async def attach_video(sermon_id: int, payload: VideoAttachPayload, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    video_id = _youtube_video_id(payload.youtubeUrl)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    sermon.youtube_url = payload.youtubeUrl
    sermon.youtube_video_id = video_id
    sermon.youtube_channel_id = payload.youtubeChannelId or ""
    sermon.video_status = "attached"
    sermon.transcript_status = "none"
    await db.commit()

    init_sermon_state(str(sermon_id))
    transcript_doc = load_transcript(str(sermon_id))
    transcript_doc.videoId = video_id
    transcript_doc.status = "none"
    transcript_doc.source = None
    transcript_doc.transcriptText = ""
    transcript_doc.segments = []
    transcript_doc.note = "Video attached. Transcript not fetched yet."
    save_transcript(transcript_doc)

    return {"ok": True, "video_id": video_id}


@router.post("/{sermon_id}/transcript/fetch", response_model=TranscriptDocument)
async def fetch_sermon_transcript(sermon_id: int, payload: Optional[TranscriptFetchPayload] = None, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    video_id = sermon.youtube_video_id
    if not video_id:
        raise HTTPException(status_code=400, detail="No YouTube video attached")

    init_sermon_state(str(sermon_id))
    source, t_status, segments, note = fetch_transcript_with_fallback(video_id)

    doc = load_transcript(str(sermon_id))
    doc.videoId = video_id
    doc.source = source
    doc.fetchedAt = datetime.now(timezone.utc)
    doc.segments = segments
    doc.transcriptText = "\n".join(s.text for s in segments)
    doc.note = note
    doc.status = "ready" if segments else t_status
    save_transcript(doc)

    sermon.transcript_status = doc.status
    await db.commit()
    return doc


@router.get("/{sermon_id}/transcript", response_model=TranscriptDocument)
async def get_transcript(sermon_id: int, db: AsyncSession = Depends(get_db)):
    await _get_sermon(db, sermon_id)
    init_sermon_state(str(sermon_id))
    return load_transcript(str(sermon_id))


@router.post("/{sermon_id}/transcript/manual", response_model=TranscriptDocument)
async def save_manual_transcript(sermon_id: int, payload: TranscriptManualPayload, db: AsyncSession = Depends(get_db)):
    sermon = await _get_sermon(db, sermon_id)
    cleaned = (payload.transcriptText or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Transcript text is required.")
    init_sermon_state(str(sermon_id))
    existing = load_transcript(str(sermon_id))
    doc = TranscriptDocument(
        sermonId=str(sermon_id),
        videoId=existing.videoId,
        language=payload.language or existing.language or "en",
        status="ready",
        source="manual",
        fetchedAt=datetime.now(timezone.utc),
        transcriptText=cleaned,
        segments=transcript_to_segments(cleaned),
        note="Transcript provided manually.",
    )
    save_transcript(doc)
    sermon.transcript_status = "ready"
    await db.commit()
    return doc


# ── Series download ──────────────────────────────────────────────────────


@router.get("/series/{series_name}/download")
async def download_series_pptx(series_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Sermon)
        .where(Sermon.series_name.ilike(series_name))
        .order_by(Sermon.created_at.desc())
    )
    sermons = result.scalars().all()
    if not sermons:
        raise HTTPException(status_code=404, detail="No sermons found in this series")

    settings = get_settings()
    exports_dir = settings.storage_path / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    series_slug = _slugify(series_name)
    archive_path = exports_dir / f"{series_slug}.zip"

    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for index, sermon in enumerate(sermons, start=1):
            try:
                source_path = _resolve_upload_path(sermon)
            except HTTPException:
                continue
            if not source_path.exists():
                continue
            slug = _slugify(sermon.title) or f"sermon-{index}"
            suffix = _slugify(sermon.date_preached) if sermon.date_preached else str(index)
            arcname = f"{series_slug}/{suffix}-{slug}.pptx"
            archive.write(source_path, arcname=arcname)

    return FileResponse(archive_path, media_type="application/zip", filename=f"{series_slug}.zip")
