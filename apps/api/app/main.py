from contextlib import asynccontextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import AsyncGenerator, List, Optional
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pptx import Presentation

from .bedrock import BedrockAgentError, analyze_slide_text
from .config import STORAGE_DIR, UPLOAD_DIR
from .db import get_db, init_db
from .schemas import (
    AnalysisDocument,
    DailyInspiration,
    DecisionsDocument,
    Sermon,
    SlideAnalysis,
    SlideContent,
    SlideDecision,
    SlideDecisionPayload,
    Suggestion,
    TranscriptDocument,
    TranscriptFetchPayload,
    TranscriptManualPayload,
    TranscriptSegment,
    VideoAttachPayload,
)
from .state import (
    init_sermon_state,
    load_analysis,
    load_decisions,
    load_transcript,
    save_analysis,
    save_decisions,
    save_transcript,
)
from .transcript_providers import fetch_transcript_with_fallback

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

INSPIRATION_FALLBACK = [
    {
        "kind": "verse",
        "text": "Trust in the Lord with all your heart and do not lean on your own understanding.",
        "citation": "Proverbs 3:5",
    },
    {
        "kind": "verse",
        "text": "Your word is a lamp to my feet and a light to my path.",
        "citation": "Psalm 119:105",
    },
    {
        "kind": "quote",
        "text": "He is no fool who gives what he cannot keep to gain what he cannot lose.",
        "citation": "Jim Elliot",
    },
    {
        "kind": "quote",
        "text": "I believe in Christianity as I believe that the sun has risen.",
        "citation": "C.S. Lewis",
    },
    {
        "kind": "quote",
        "text": "God cannot give us a happiness and peace apart from Himself.",
        "citation": "C.S. Lewis",
    },
    {
        "kind": "quote",
        "text": "The true test of faith is how we treat people in need.",
        "citation": "Tim Keller",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(title="Sermon-Wiki API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"ok": True}


@app.get("/inspiration/daily", response_model=DailyInspiration)
def get_daily_inspiration(db=Depends(get_db)) -> DailyInspiration:
    date_key = datetime.utcnow().date().isoformat()
    row = db.execute(
        """
        SELECT date_key, kind, text, citation
        FROM daily_inspiration
        WHERE date_key = ?
        """,
        (date_key,),
    ).fetchone()
    if row:
        return DailyInspiration(
            date=row["date_key"],
            kind=row["kind"],
            text=row["text"],
            citation=row["citation"],
        )

    generated = _generate_daily_inspiration(date_key)
    db.execute(
        """
        INSERT OR REPLACE INTO daily_inspiration (date_key, kind, text, citation, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            generated.date,
            generated.kind,
            generated.text,
            generated.citation,
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()
    return generated


def _ensure_pptx(file: UploadFile) -> None:
    filename = file.filename or ""
    if not filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pptx files are supported in MVP0.",
        )


def _validate_pptx_file(path: Path) -> None:
    try:
        Presentation(path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid PPTX file: {exc}",
        ) from exc


def _row_to_sermon(row) -> Sermon:
    created_at = datetime.fromisoformat(row["created_at"])
    relative_path = f"uploads/{row['id']}/{row['original_filename']}"
    sermon_date = row["week_or_date"]
    return Sermon(
        id=row["id"],
        sermonName=row["sermon_name"],
        seriesName=row["series_name"],
        sermonDate=sermon_date,
        weekOrDate=sermon_date,
        pastorName=row["pastor_name"],
        churchName=row["church_name"],
        youtubeUrl=row["youtube_url"],
        youtubeVideoId=row["youtube_video_id"],
        youtubeChannelId=row["youtube_channel_id"],
        videoStatus=row["video_status"] or "pending_match",
        transcriptStatus=row["transcript_status"] or "none",
        status=row["status"],
        filePath=relative_path,
        originalFilename=row["original_filename"],
        createdAt=created_at,
    )


def _extract_slide_text(slide) -> str:
    text_chunks = []
    for shape in slide.shapes:
        if not hasattr(shape, "text"):
            continue
        text = (shape.text or "").strip()
        if text:
            text_chunks.append(text)

    try:
        notes_text = slide.notes_slide.notes_text_frame.text
    except Exception:
        notes_text = ""

    notes_text = (notes_text or "").strip()
    if notes_text:
        text_chunks.append(f"Notes:\n{notes_text}")

    return "\n".join(text_chunks).strip()


def _build_sermon_summary(presentation: Presentation) -> str:
    highlights: List[str] = []
    for index, slide in enumerate(presentation.slides, start=1):
        text = _extract_slide_text(slide)
        if not text:
            continue
        first_line = text.splitlines()[0].strip()
        if not first_line:
            continue
        highlights.append(f"Slide {index}: {first_line[:220]}")
        if len(highlights) >= 8:
            break

    if not highlights:
        return "No readable text was found in this sermon presentation."

    return "Sermon summary:\n" + "\n".join(f"- {line}" for line in highlights)


def _build_transcript_summary(transcript_text: str) -> str:
    cleaned = " ".join((transcript_text or "").split())
    if not cleaned:
        return "Transcript is empty."

    chunks = re.split(r"(?<=[.!?])\s+", cleaned)
    lines: List[str] = []
    for chunk in chunks:
        snippet = chunk.strip()
        if not snippet:
            continue
        lines.append(snippet[:220])
        if len(lines) >= 8:
            break
    if not lines:
        lines.append(cleaned[:220])

    verse_refs = _extract_bible_references(transcript_text)
    summary = "Transcript summary:\n" + "\n".join(f"- {line}" for line in lines)
    if verse_refs:
        summary += "\n\nBible verses mentioned:\n" + "\n".join(
            f"- {ref}" for ref in verse_refs
        )
    else:
        summary += "\n\nBible verses mentioned:\n- None detected"
    return summary


def _extract_bible_references(text: str) -> List[str]:
    books = (
        "Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
        "Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|"
        "Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
        "Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|"
        "Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|"
        "Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|"
        "Hebrews|James|Peter|Jude|Revelation"
    )
    pattern = re.compile(
        rf"\b(?:[1-3]\s)?(?:{books})\s\d{{1,3}}:\d{{1,3}}(?:[-–]\d{{1,3}})?(?:,\d{{1,3}}(?:[-–]\d{{1,3}})?)*\b",
        flags=re.IGNORECASE,
    )

    matches = pattern.findall(text or "")
    refs: List[str] = []
    seen = set()
    for match in matches:
        normalized = re.sub(r"\s+", " ", match.strip())
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        refs.append(normalized)
    return refs


def _extract_json_object(raw: str) -> Optional[dict]:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _fallback_daily_inspiration(date_key: str) -> DailyInspiration:
    digest = hashlib.sha256(date_key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(INSPIRATION_FALLBACK)
    selected = INSPIRATION_FALLBACK[index]
    return DailyInspiration(
        date=date_key,
        kind=selected["kind"],
        text=selected["text"],
        citation=selected["citation"],
    )


def _generate_daily_inspiration(date_key: str) -> DailyInspiration:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return _fallback_daily_inspiration(date_key)

    api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
    model = os.getenv("GROK_MODEL", "grok-4-latest")
    payload = {
        "model": model,
        "stream": False,
        "temperature": 0.4,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return strictly JSON with keys: kind, text, citation. "
                    "kind must be verse or quote. "
                    "Use Christian scripture or a quote from a Christian preacher/apologist. "
                    "Keep text under 220 characters."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate one daily inspiration for date {date_key}. "
                    "Output JSON only."
                ),
            },
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        content = (body.get("choices") or [{}])[0].get("message", {}).get("content", "")
        parsed = _extract_json_object(content)
        if not parsed:
            return _fallback_daily_inspiration(date_key)
        kind = str(parsed.get("kind", "quote")).lower()
        if kind not in {"verse", "quote"}:
            kind = "quote"
        text = " ".join(str(parsed.get("text", "")).split())[:220].strip()
        citation = " ".join(str(parsed.get("citation", "")).split())[:120].strip()
        if not text or not citation:
            return _fallback_daily_inspiration(date_key)
        return DailyInspiration(
            date=date_key,
            kind=kind,
            text=text,
            citation=citation,
        )
    except Exception:
        return _fallback_daily_inspiration(date_key)


def _transcript_to_segments(transcript_text: str) -> List[TranscriptSegment]:
    lines = [line.strip() for line in (transcript_text or "").splitlines() if line.strip()]
    if not lines:
        return []
    per_segment = 20.0
    return [
        TranscriptSegment(
            startSeconds=index * per_segment,
            durationSeconds=per_segment,
            text=line,
        )
        for index, line in enumerate(lines)
    ]


def _resolve_upload_path(
    sermon_id: str, file_path: str, original_filename: str
) -> Path:
    stored_path = Path(file_path)
    if stored_path.is_absolute() and stored_path.exists():
        return stored_path

    candidate = UPLOAD_DIR / file_path
    if candidate.exists():
        return candidate

    return UPLOAD_DIR / sermon_id / original_filename


def _slugify(value: Optional[str]) -> str:
    source = (value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", source).strip("-")
    return slug or "series"


def _youtube_video_id(youtube_url: Optional[str]) -> Optional[str]:
    if not youtube_url:
        return None
    raw = youtube_url.strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        return candidate or None
    if "youtube.com" in host:
        query_video = parse_qs(parsed.query).get("v", [])
        if query_video and query_video[0]:
            return query_video[0]
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "live", "embed"}:
            return parts[1]
    return None


def _ensure_sermon_exists(db, sermon_id: str) -> None:
    row = db.execute(
        """
        SELECT id
        FROM sermons
        WHERE id = ?
        """,
        (sermon_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


def _get_sermon_file_row(db, sermon_id: str):
    row = db.execute(
        """
        SELECT id, sermon_name, series_name, week_or_date, file_path, original_filename
        FROM sermons
        WHERE id = ?
        """,
        (sermon_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return row


def _get_sermon_row(db, sermon_id: str):
    row = db.execute(
        """
        SELECT
            id, sermon_name, series_name, week_or_date, pastor_name, church_name,
            youtube_url, youtube_video_id, youtube_channel_id, video_status, transcript_status,
            status, file_path, original_filename, created_at
        FROM sermons
        WHERE id = ?
        """,
        (sermon_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return row


def _set_transcript_status(db, sermon_id: str, transcript_status: str) -> None:
    db.execute(
        "UPDATE sermons SET transcript_status = ? WHERE id = ?",
        (transcript_status, sermon_id),
    )
    db.commit()


def _get_presentation(db, sermon_id: str) -> Presentation:
    row = db.execute(
        """
        SELECT id, file_path, original_filename
        FROM sermons
        WHERE id = ?
        """,
        (sermon_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    file_path = _resolve_upload_path(
        row["id"], row["file_path"], row["original_filename"]
    )
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing")

    try:
        return Presentation(file_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sermon PPTX: {exc}",
        ) from exc


@app.post("/sermons", response_model=Sermon, status_code=status.HTTP_201_CREATED)
async def upload_sermon(
    file: UploadFile = File(...),
    sermonDate: Optional[str] = Form(None),
    weekOrDate: Optional[str] = Form(None),
    seriesName: Optional[str] = Form(None),
    sermonName: str = Form(...),
    pastorName: Optional[str] = Form(None),
    churchName: Optional[str] = Form(None),
    youtubeUrl: Optional[str] = Form(None),
    db=Depends(get_db),
) -> Sermon:
    """
    Store a sermon PPTX file with optional metadata.
    """
    _ensure_pptx(file)

    sermon_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()
    sermon_dir = UPLOAD_DIR / sermon_id
    sermon_dir.mkdir(parents=True, exist_ok=True)
    destination = sermon_dir / file.filename
    with destination.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)
    _validate_pptx_file(destination)
    resolved_date = sermonDate or weekOrDate
    video_id = _youtube_video_id(youtubeUrl)
    video_status = "attached" if video_id else "pending_match"

    db.execute(
        """
        INSERT INTO sermons (
            id, sermon_name, series_name, week_or_date, pastor_name, church_name,
            youtube_url, youtube_video_id, youtube_channel_id, video_status, transcript_status,
            status, file_path, original_filename, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sermon_id,
            sermonName,
            seriesName,
            resolved_date,
            pastorName,
            churchName,
            youtubeUrl,
            video_id,
            None,
            video_status,
            "none",
            "uploaded",
            f"{sermon_id}/{file.filename}",
            file.filename,
            created_at,
        ),
    )
    db.commit()
    init_sermon_state(sermon_id)

    return Sermon(
        id=sermon_id,
        sermonName=sermonName,
        seriesName=seriesName,
        sermonDate=resolved_date,
        weekOrDate=resolved_date,
        pastorName=pastorName,
        churchName=churchName,
        youtubeUrl=youtubeUrl,
        youtubeVideoId=video_id,
        youtubeChannelId=None,
        videoStatus=video_status,
        transcriptStatus="none",
        status="uploaded",
        filePath=f"uploads/{sermon_id}/{file.filename}",
        originalFilename=file.filename,
        createdAt=datetime.fromisoformat(created_at),
    )


@app.get("/sermons", response_model=List[Sermon])
def list_sermons(db=Depends(get_db)) -> List[Sermon]:
    rows = db.execute(
        """
        SELECT
            id, sermon_name, series_name, week_or_date, pastor_name, church_name,
            youtube_url, youtube_video_id, youtube_channel_id, video_status, transcript_status,
            status, file_path, original_filename, created_at
        FROM sermons
        ORDER BY created_at DESC
        """
    ).fetchall()
    return [_row_to_sermon(row) for row in rows]


@app.post("/sermons/{sermon_id}/video/attach", response_model=Sermon)
def attach_sermon_video(
    sermon_id: str,
    payload: VideoAttachPayload,
    db=Depends(get_db),
) -> Sermon:
    _ensure_sermon_exists(db, sermon_id)
    video_id = _youtube_video_id(payload.youtubeUrl)
    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL",
        )

    db.execute(
        """
        UPDATE sermons
        SET youtube_url = ?, youtube_video_id = ?, youtube_channel_id = ?, video_status = ?, transcript_status = ?
        WHERE id = ?
        """,
        (payload.youtubeUrl, video_id, payload.youtubeChannelId, "attached", "none", sermon_id),
    )
    db.commit()

    init_sermon_state(sermon_id)
    transcript_doc = load_transcript(sermon_id)
    transcript_doc.videoId = video_id
    transcript_doc.language = None
    transcript_doc.status = "none"
    transcript_doc.source = None
    transcript_doc.fetchedAt = None
    transcript_doc.transcriptText = ""
    transcript_doc.segments = []
    transcript_doc.note = "Video attached. Transcript not fetched yet."
    save_transcript(transcript_doc)

    return _row_to_sermon(_get_sermon_row(db, sermon_id))


@app.post("/sermons/{sermon_id}/transcript/fetch", response_model=TranscriptDocument)
def fetch_sermon_transcript(
    sermon_id: str,
    payload: Optional[TranscriptFetchPayload] = None,
    db=Depends(get_db),
) -> TranscriptDocument:
    row = _get_sermon_row(db, sermon_id)
    video_id = row["youtube_video_id"]
    youtube_url = row["youtube_url"]
    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No YouTube video attached",
        )

    init_sermon_state(sermon_id)
    preferred_language = (payload.language if payload else None) or None

    result = fetch_transcript_with_fallback(video_id, youtube_url, preferred_language)

    doc = load_transcript(sermon_id)
    doc.videoId = video_id
    doc.language = result.language
    doc.source = result.provider
    doc.fetchedAt = datetime.utcnow()
    doc.segments = result.segments
    doc.transcriptText = "\n".join(segment.text for segment in result.segments)
    doc.note = result.note
    doc.status = "ready" if result.segments else result.status
    save_transcript(doc)
    _set_transcript_status(db, sermon_id, doc.status)
    return doc


@app.get("/sermons/{sermon_id}/transcript", response_model=TranscriptDocument)
def get_sermon_transcript(sermon_id: str, db=Depends(get_db)) -> TranscriptDocument:
    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)
    return load_transcript(sermon_id)


@app.post("/sermons/{sermon_id}/transcript/manual", response_model=TranscriptDocument)
def save_manual_transcript(
    sermon_id: str,
    payload: TranscriptManualPayload,
    db=Depends(get_db),
) -> TranscriptDocument:
    _ensure_sermon_exists(db, sermon_id)
    cleaned = (payload.transcriptText or "").strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript text is required.",
        )

    init_sermon_state(sermon_id)
    existing = load_transcript(sermon_id)
    doc = TranscriptDocument(
        sermonId=sermon_id,
        videoId=existing.videoId,
        language=(payload.language or existing.language or "en"),
        status="ready",
        source="manual",
        fetchedAt=datetime.utcnow(),
        transcriptText=cleaned,
        segments=_transcript_to_segments(cleaned),
        note="Transcript provided manually.",
    )
    save_transcript(doc)
    _set_transcript_status(db, sermon_id, "ready")
    return doc


@app.get("/sermons/{sermon_id}/pptx")
def view_sermon_pptx(sermon_id: str, db=Depends(get_db)) -> FileResponse:
    row = _get_sermon_file_row(db, sermon_id)
    file_path = _resolve_upload_path(
        row["id"], row["file_path"], row["original_filename"]
    )
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing")
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@app.get("/sermons/{sermon_id}/download-original-pptx")
def download_original_pptx(sermon_id: str, db=Depends(get_db)) -> FileResponse:
    row = _get_sermon_file_row(db, sermon_id)
    file_path = _resolve_upload_path(
        row["id"], row["file_path"], row["original_filename"]
    )
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing")
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=row["original_filename"],
    )


@app.get("/series/{series_name}/download")
def download_series_pptx(series_name: str, db=Depends(get_db)) -> FileResponse:
    rows = db.execute(
        """
        SELECT id, sermon_name, week_or_date, file_path, original_filename
        FROM sermons
        WHERE lower(coalesce(series_name, '')) = lower(?)
        ORDER BY created_at DESC
        """,
        (series_name,),
    ).fetchall()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    exports_dir = STORAGE_DIR / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    series_slug = _slugify(series_name)
    archive_path = exports_dir / f"{series_slug}.zip"

    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for index, row in enumerate(rows, start=1):
            source_path = _resolve_upload_path(
                row["id"], row["file_path"], row["original_filename"]
            )
            if not source_path.exists():
                continue
            sermon_slug = _slugify(row["sermon_name"]) or f"sermon-{index}"
            suffix = _slugify(row["week_or_date"]) if row["week_or_date"] else str(index)
            arcname = f"{series_slug}/{suffix}-{sermon_slug}.pptx"
            archive.write(source_path, arcname=arcname)

    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"{series_slug}.zip",
    )


@app.get("/sermons/{sermon_id}/slides", response_model=List[SlideContent])
def list_sermon_slides(sermon_id: str, db=Depends(get_db)) -> List[SlideContent]:
    presentation = _get_presentation(db, sermon_id)
    slides = []
    for index, slide in enumerate(presentation.slides, start=1):
        slide_id = f"{sermon_id}:{index}"
        slides.append(
            SlideContent(
                slideId=slide_id,
                slideNumber=index,
                originalText=_extract_slide_text(slide),
            )
        )
    return slides


@app.post("/sermons/{sermon_id}/summary")
def summarize_sermon(sermon_id: str, db=Depends(get_db)) -> dict:
    presentation = _get_presentation(db, sermon_id)
    return {"sermonId": sermon_id, "summary": _build_sermon_summary(presentation)}


@app.post("/sermons/{sermon_id}/summary/from-transcript")
def summarize_from_transcript(sermon_id: str, db=Depends(get_db)) -> dict:
    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)
    transcript = load_transcript(sermon_id)
    if not (transcript.transcriptText or "").strip():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transcript not ready (status={transcript.status}).",
        )
    return {
        "sermonId": sermon_id,
        "source": "transcript",
        "summary": _build_transcript_summary(transcript.transcriptText),
    }


@app.post(
    "/sermons/{sermon_id}/slides/{slide_number}/analyze",
    response_model=SlideAnalysis,
)
def analyze_slide(
    sermon_id: str, slide_number: int, db=Depends(get_db)
) -> SlideAnalysis:
    if slide_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slide number"
        )

    presentation = _get_presentation(db, sermon_id)
    try:
        slide = presentation.slides[slide_number - 1]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    slide_id = f"{sermon_id}:{slide_number}"
    original_text = _extract_slide_text(slide)
    try:
        suggestions = analyze_slide_text(slide_id, original_text)
    except (BedrockAgentError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Bedrock analysis failed: {exc}",
        ) from exc
    analysis = SlideAnalysis(
        slideId=slide_id,
        slideNumber=slide_number,
        originalText=original_text,
        suggestions=suggestions,
    )

    init_sermon_state(sermon_id)
    doc = load_analysis(sermon_id)
    for idx, existing in enumerate(doc.slides):
        if existing.slideId == slide_id:
            doc.slides[idx] = analysis
            break
    else:
        doc.slides.append(analysis)
    save_analysis(doc)

    return analysis


@app.get("/sermons/{sermon_id}/analysis", response_model=AnalysisDocument)
def get_sermon_analysis(sermon_id: str, db=Depends(get_db)) -> AnalysisDocument:
    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)
    return load_analysis(sermon_id)


@app.get(
    "/sermons/{sermon_id}/slides/{slide_number}/analysis",
    response_model=SlideAnalysis,
)
def get_slide_analysis(
    sermon_id: str, slide_number: int, db=Depends(get_db)
) -> SlideAnalysis:
    if slide_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slide number"
        )

    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)

    slide_id = f"{sermon_id}:{slide_number}"
    doc = load_analysis(sermon_id)
    for slide in doc.slides:
        if slide.slideId == slide_id:
            return slide

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@app.post(
    "/sermons/{sermon_id}/slides/{slide_number}/decisions",
    response_model=SlideDecision,
)
def save_slide_decisions(
    sermon_id: str,
    slide_number: int,
    payload: SlideDecisionPayload,
    db=Depends(get_db),
) -> SlideDecision:
    if slide_number < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slide number"
        )

    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)

    slide_id = f"{sermon_id}:{slide_number}"
    decision = SlideDecision(
        slideId=slide_id,
        slideNumber=slide_number,
        decisions=payload.decisions,
    )

    doc = load_decisions(sermon_id)
    doc.updatedAt = datetime.utcnow()
    for idx, existing in enumerate(doc.slides):
        if existing.slideId == slide_id:
            doc.slides[idx] = decision
            break
    else:
        doc.slides.append(decision)
    save_decisions(doc)

    return decision


@app.get("/sermons/{sermon_id}/decisions", response_model=DecisionsDocument)
def get_sermon_decisions(sermon_id: str, db=Depends(get_db)) -> DecisionsDocument:
    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)
    return load_decisions(sermon_id)


def _output_pptx_path(sermon_id: str) -> Path:
    return STORAGE_DIR / "sermons" / sermon_id / "output.pptx"


def _replace_in_text_frame(text_frame, replacements: List[tuple[str, str]]) -> None:
    for paragraph in text_frame.paragraphs:
        for original, replacement in replacements:
            if not original or original not in paragraph.text:
                continue
            replaced_in_runs = False
            for run in paragraph.runs:
                if original in run.text:
                    run.text = run.text.replace(original, replacement)
                    replaced_in_runs = True
            if not replaced_in_runs:
                updated = paragraph.text.replace(original, replacement)
                if updated != paragraph.text:
                    paragraph.text = updated


def _apply_text_replacements(slide, replacements: List[tuple[str, str]]) -> None:
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue
        _replace_in_text_frame(shape.text_frame, replacements)

    try:
        notes_frame = slide.notes_slide.notes_text_frame
    except Exception:
        notes_frame = None

    if notes_frame is not None:
        _replace_in_text_frame(notes_frame, replacements)


@app.post("/sermons/{sermon_id}/generate-updated-pptx")
def generate_updated_pptx(sermon_id: str, db=Depends(get_db)) -> dict:
    _ensure_sermon_exists(db, sermon_id)
    init_sermon_state(sermon_id)

    analysis = load_analysis(sermon_id)
    decisions = load_decisions(sermon_id)
    suggestion_map = {}
    for slide in analysis.slides:
        for suggestion in slide.suggestions:
            suggestion_map[suggestion.id] = suggestion

    presentation = _get_presentation(db, sermon_id)
    for index, slide in enumerate(presentation.slides, start=1):
        slide_id = f"{sermon_id}:{index}"
        decision_block = next(
            (entry for entry in decisions.slides if entry.slideId == slide_id), None
        )
        if not decision_block:
            continue

        replacements = []
        for decision in decision_block.decisions:
            suggestion = suggestion_map.get(decision.suggestionId)
            if not suggestion:
                continue
            if decision.decision == "rejected":
                continue
            if decision.decision == "accepted":
                replacement = suggestion.proposed
            else:
                replacement = decision.finalText or suggestion.proposed
            replacements.append((suggestion.original, replacement))

        if replacements:
            _apply_text_replacements(slide, replacements)

    output_path = _output_pptx_path(sermon_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(output_path)
    return {"status": "ready"}


@app.get("/sermons/{sermon_id}/download-updated-pptx")
def download_updated_pptx(sermon_id: str, db=Depends(get_db)) -> FileResponse:
    _ensure_sermon_exists(db, sermon_id)
    output_path = _output_pptx_path(sermon_id)
    if not output_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{sermon_id}-updated.pptx",
    )
