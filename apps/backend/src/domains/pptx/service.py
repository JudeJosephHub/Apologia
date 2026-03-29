"""PPTX processing service (ported from Apologia).

Handles PPTX upload, slide extraction, AI analysis via AWS Bedrock,
decision tracking, updated PPTX generation, transcript fetching, and
file-based state management.
"""

import json
import logging
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid4

import httpx
from pptx import Presentation

from ...core import get_settings
from .schemas import (
    AnalysisDocument,
    DecisionsDocument,
    SlideAnalysis,
    SlideContent,
    Suggestion,
    TranscriptDocument,
    TranscriptSegment,
)

logger = logging.getLogger(__name__)


# ── Bedrock Agent ─────────────────────────────────────────────────────────


class BedrockAgentError(RuntimeError):
    pass


def _read_completion(response) -> str:
    if "completion" in response:
        completion = response["completion"]
        if isinstance(completion, str):
            return completion
        if isinstance(completion, dict):
            data = completion.get("bytes")
            if data:
                return data.decode("utf-8")
        if hasattr(completion, "read"):
            return completion.read().decode("utf-8")
        chunks = []
        event_keys = []
        for event in completion:
            event_keys.append(",".join(event.keys()) if isinstance(event, dict) else type(event).__name__)
            chunk = event.get("chunk") if isinstance(event, dict) else None
            if not chunk:
                continue
            data = chunk.get("bytes")
            if not data:
                continue
            chunks.append(data.decode("utf-8"))
        if chunks:
            return "".join(chunks)
        raise BedrockAgentError(f"Empty Bedrock completion stream. Events: {event_keys}")
    output_text = response.get("outputText")
    if output_text:
        return output_text
    raise BedrockAgentError(f"Bedrock response missing completion: {list(response.keys())}")


def _extract_json(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(payload[start : end + 1])


def analyze_slide_text(slide_id: str, text: str) -> List[Suggestion]:
    """Invoke AWS Bedrock Agent to get improvement suggestions for slide text."""
    import boto3

    settings = get_settings()
    if not settings.bedrock_agent_id or not settings.bedrock_agent_alias_id:
        raise BedrockAgentError("Bedrock agent not configured")

    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    input_payload = json.dumps({"slide_id": slide_id, "slide_text": text})
    response = client.invoke_agent(
        agentId=settings.bedrock_agent_id,
        agentAliasId=settings.bedrock_agent_alias_id,
        sessionId=str(uuid4()),
        inputText=input_payload,
    )
    completion = _read_completion(response)
    data = _extract_json(completion)
    return [Suggestion(**item) for item in data.get("suggestions", [])]


# ── PPTX Helpers ──────────────────────────────────────────────────────────


def extract_slide_text(slide) -> str:
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


def get_presentation(file_path: Path) -> Presentation:
    return Presentation(file_path)


def list_slides(prs: Presentation, sermon_id: str) -> List[SlideContent]:
    slides = []
    for index, slide in enumerate(prs.slides, start=1):
        slide_id = f"{sermon_id}:{index}"
        slides.append(
            SlideContent(slideId=slide_id, slideNumber=index, originalText=extract_slide_text(slide))
        )
    return slides


def build_sermon_summary(prs: Presentation) -> str:
    highlights: List[str] = []
    for index, slide in enumerate(prs.slides, start=1):
        text = extract_slide_text(slide)
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


# ── Transcript helpers ────────────────────────────────────────────────────

_BIBLE_BOOKS = (
    "Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    "Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|"
    "Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
    "Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|"
    "Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|"
    "Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|"
    "Hebrews|James|Peter|Jude|Revelation"
)
_BIBLE_REF_PATTERN = re.compile(
    rf"\b(?:[1-3]\s)?(?:{_BIBLE_BOOKS})\s\d{{1,3}}:\d{{1,3}}(?:[-–]\d{{1,3}})?(?:,\d{{1,3}}(?:[-–]\d{{1,3}})?)*\b",
    flags=re.IGNORECASE,
)


def extract_bible_references(text: str) -> List[str]:
    matches = _BIBLE_REF_PATTERN.findall(text or "")
    refs, seen = [], set()
    for match in matches:
        normalized = re.sub(r"\s+", " ", match.strip())
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            refs.append(normalized)
    return refs


def build_transcript_summary(transcript_text: str) -> str:
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
    verse_refs = extract_bible_references(transcript_text)
    summary = "Transcript summary:\n" + "\n".join(f"- {line}" for line in lines)
    if verse_refs:
        summary += "\n\nBible verses mentioned:\n" + "\n".join(f"- {ref}" for ref in verse_refs)
    else:
        summary += "\n\nBible verses mentioned:\n- None detected"
    return summary


def transcript_to_segments(text: str) -> List[TranscriptSegment]:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return []
    per_segment = 20.0
    return [
        TranscriptSegment(startSeconds=i * per_segment, durationSeconds=per_segment, text=line)
        for i, line in enumerate(lines)
    ]


# ── YouTube transcript providers ──────────────────────────────────────────

def _segments_from_xml(text_nodes) -> List[TranscriptSegment]:
    segments = []
    for node in text_nodes:
        content = " ".join(("".join(node.itertext()) or "").split())
        if not content:
            continue
        start = float(node.attrib.get("start", "0") or "0")
        duration = float(node.attrib.get("dur", "0") or "0")
        segments.append(TranscriptSegment(startSeconds=start, durationSeconds=duration, text=content))
    return segments


def fetch_youtube_timedtext(video_id: str) -> Tuple[str, List[TranscriptSegment], str]:
    """Returns (status, segments, note)."""
    with httpx.Client(timeout=15) as client:
        list_resp = client.get("https://www.youtube.com/api/timedtext", params={"type": "list", "v": video_id})
        list_resp.raise_for_status()
        root = ET.fromstring(list_resp.text or "<transcript_list />")
        tracks = root.findall(".//track")
        if not tracks:
            return "pending", [], "Transcript track list is empty."
        selected = None
        for track in tracks:
            if (track.attrib.get("lang_code") or "").startswith("en"):
                selected = track
                break
        if selected is None:
            selected = tracks[0]
        lang_code = selected.attrib.get("lang_code")
        params = {"v": video_id, "lang": lang_code}
        if selected.attrib.get("name"):
            params["name"] = selected.attrib["name"]
        if selected.attrib.get("kind"):
            params["kind"] = selected.attrib["kind"]
        text_resp = client.get("https://www.youtube.com/api/timedtext", params=params)
        text_resp.raise_for_status()
        text_root = ET.fromstring(text_resp.text or "<transcript />")
        segments = _segments_from_xml(text_root.findall(".//text"))
    status = "ready" if segments else "pending"
    return status, segments, "ok" if segments else "No segments returned."


def fetch_youtube_transcript_api(video_id: str) -> Tuple[str, List[TranscriptSegment], str]:
    """Returns (status, segments, note) using youtube_transcript_api library."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return "unavailable", [], "youtube_transcript_api not installed."
    try:
        fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
    except Exception:
        try:
            fetched = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as exc:
            return "pending", [], f"Provider failed: {exc}"
    segments = [
        TranscriptSegment(
            startSeconds=float(item.get("start", 0.0)),
            durationSeconds=float(item.get("duration", 0.0)),
            text=" ".join((item.get("text", "") or "").split()),
        )
        for item in fetched
        if (item.get("text") or "").strip()
    ]
    return ("ready" if segments else "pending"), segments, ("ok" if segments else "Empty.")


def fetch_transcript_with_fallback(video_id: str) -> Tuple[str, str, List[TranscriptSegment], str]:
    """Try multiple providers. Returns (source, status, segments, note)."""
    for name, fn in [("youtube_timedtext", fetch_youtube_timedtext), ("youtube_transcript_api", fetch_youtube_transcript_api)]:
        try:
            status, segments, note = fn(video_id)
            if segments:
                return name, status, segments, note
        except Exception:
            continue
    return "none", "pending", [], "All providers failed."


# ── File-based state management ───────────────────────────────────────────


def _state_dir(sermon_id: str) -> Path:
    settings = get_settings()
    d = settings.storage_path / "sermons" / sermon_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def init_sermon_state(sermon_id: str) -> None:
    d = _state_dir(sermon_id)
    analysis_file = d / "analysis.json"
    if not analysis_file.exists():
        doc = AnalysisDocument(sermonId=sermon_id, createdAt=datetime.now(timezone.utc), slides=[])
        analysis_file.write_text(doc.model_dump_json(indent=2))
    decisions_file = d / "decisions.json"
    if not decisions_file.exists():
        doc = DecisionsDocument(sermonId=sermon_id, updatedAt=datetime.now(timezone.utc), slides=[])
        decisions_file.write_text(doc.model_dump_json(indent=2))
    transcript_file = d / "transcript.json"
    if not transcript_file.exists():
        doc = TranscriptDocument(sermonId=sermon_id, status="none", segments=[])
        transcript_file.write_text(doc.model_dump_json(indent=2))


def load_analysis(sermon_id: str) -> AnalysisDocument:
    return AnalysisDocument.model_validate_json((_state_dir(sermon_id) / "analysis.json").read_text())


def save_analysis(analysis: AnalysisDocument) -> None:
    (_state_dir(analysis.sermonId) / "analysis.json").write_text(analysis.model_dump_json(indent=2))


def load_decisions(sermon_id: str) -> DecisionsDocument:
    return DecisionsDocument.model_validate_json((_state_dir(sermon_id) / "decisions.json").read_text())


def save_decisions(decisions: DecisionsDocument) -> None:
    (_state_dir(decisions.sermonId) / "decisions.json").write_text(decisions.model_dump_json(indent=2))


def load_transcript(sermon_id: str) -> TranscriptDocument:
    path = _state_dir(sermon_id) / "transcript.json"
    if not path.exists():
        init_sermon_state(sermon_id)
    raw = path.read_text()
    if not raw.strip():
        return TranscriptDocument(sermonId=sermon_id, status="none", segments=[])
    return TranscriptDocument.model_validate_json(raw)


def save_transcript(transcript: TranscriptDocument) -> None:
    (_state_dir(transcript.sermonId) / "transcript.json").write_text(transcript.model_dump_json(indent=2))


# ── PPTX generation with decisions ───────────────────────────────────────


def _replace_in_text_frame(text_frame, replacements: List[Tuple[str, str]]) -> None:
    for paragraph in text_frame.paragraphs:
        for original, replacement in replacements:
            if not original or original not in paragraph.text:
                continue
            for run in paragraph.runs:
                if original in run.text:
                    run.text = run.text.replace(original, replacement)


def apply_decisions_to_pptx(
    prs: Presentation,
    analysis: AnalysisDocument,
    decisions: DecisionsDocument,
) -> None:
    suggestion_map = {}
    for slide in analysis.slides:
        for suggestion in slide.suggestions:
            suggestion_map[suggestion.id] = suggestion

    for index, slide in enumerate(prs.slides, start=1):
        slide_id = f"{analysis.sermonId}:{index}"
        decision_block = next((e for e in decisions.slides if e.slideId == slide_id), None)
        if not decision_block:
            continue
        replacements = []
        for decision in decision_block.decisions:
            suggestion = suggestion_map.get(decision.suggestionId)
            if not suggestion or decision.decision == "rejected":
                continue
            replacement = decision.finalText or suggestion.proposed if decision.decision == "edited" else suggestion.proposed
            replacements.append((suggestion.original, replacement))
        if replacements:
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False):
                    _replace_in_text_frame(shape.text_frame, replacements)
            try:
                notes_frame = slide.notes_slide.notes_text_frame
                _replace_in_text_frame(notes_frame, replacements)
            except Exception:
                pass
