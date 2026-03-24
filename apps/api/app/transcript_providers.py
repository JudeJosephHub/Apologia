import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Callable, List, Optional

import httpx
from youtube_transcript_api import YouTubeTranscriptApi

from .schemas import TranscriptSegment


@dataclass
class TranscriptFetchResult:
    provider: str
    status: str
    language: Optional[str]
    segments: List[TranscriptSegment]
    note: str


def _segments_from_text_nodes(text_nodes) -> List[TranscriptSegment]:
    segments: List[TranscriptSegment] = []
    for node in text_nodes:
        content = " ".join(("".join(node.itertext()) or "").split())
        if not content:
            continue
        start = float(node.attrib.get("start", "0") or "0")
        duration = float(node.attrib.get("dur", "0") or "0")
        segments.append(
            TranscriptSegment(
                startSeconds=start,
                durationSeconds=duration,
                text=content,
            )
        )
    return segments


def fetch_youtube_timedtext(
    video_id: str,
    youtube_url: Optional[str],
    preferred_language: Optional[str],
) -> TranscriptFetchResult:
    del youtube_url
    with httpx.Client(timeout=15) as client:
        list_resp = client.get(
            "https://www.youtube.com/api/timedtext",
            params={"type": "list", "v": video_id},
        )
        list_resp.raise_for_status()

        root = ET.fromstring(list_resp.text or "<transcript_list />")
        tracks = root.findall(".//track")
        if not tracks:
            return TranscriptFetchResult(
                provider="youtube_timedtext",
                status="pending",
                language=None,
                segments=[],
                note="Transcript track list is empty.",
            )

        selected = None
        if preferred_language:
            for track in tracks:
                if track.attrib.get("lang_code") == preferred_language:
                    selected = track
                    break
        if selected is None:
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
        segments = _segments_from_text_nodes(text_root.findall(".//text"))

    return TranscriptFetchResult(
        provider="youtube_timedtext",
        status="ready" if segments else "pending",
        language=lang_code,
        segments=segments,
        note="ok" if segments else "No transcript segments returned by timedtext.",
    )


def fetch_youtube_transcript_api(
    video_id: str,
    youtube_url: Optional[str],
    preferred_language: Optional[str],
) -> TranscriptFetchResult:
    del youtube_url
    languages = []
    if preferred_language:
        languages.append(preferred_language)
    languages.extend(["en", "en-US", "en-GB"])
    try:
        fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except Exception:
        try:
            fetched = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as exc:
            return TranscriptFetchResult(
                provider="youtube_transcript_api",
                status="pending",
                language=None,
                segments=[],
                note=f"Provider failed: {exc}",
            )

    segments = [
        TranscriptSegment(
            startSeconds=float(item.get("start", 0.0)),
            durationSeconds=float(item.get("duration", 0.0)),
            text=" ".join((item.get("text", "") or "").split()),
        )
        for item in fetched
        if (item.get("text") or "").strip()
    ]
    return TranscriptFetchResult(
        provider="youtube_transcript_api",
        status="ready" if segments else "pending",
        language=preferred_language or "en",
        segments=segments,
        note="ok" if segments else "No transcript segments returned by youtube_transcript_api.",
    )


def _extract_json_block(raw: str) -> Optional[str]:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("{") and text.endswith("}"):
        return text
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return match.group(0) if match else None


def fetch_grok_transcript(
    video_id: str,
    youtube_url: Optional[str],
    preferred_language: Optional[str],
) -> TranscriptFetchResult:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return TranscriptFetchResult(
            provider="grok",
            status="unavailable",
            language=None,
            segments=[],
            note="GROK_API_KEY is not configured.",
        )

    api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
    configured_model = os.getenv("GROK_MODEL", "grok-2-latest")
    timeout = float(os.getenv("GROK_TIMEOUT_SECONDS", "45"))

    input_url = youtube_url or f"https://www.youtube.com/watch?v={video_id}"
    preferred = preferred_language or "en"
    system_prompt = (
        "You are a transcript extraction assistant. "
        "Return strictly JSON and no markdown. "
        "JSON format: {\"language\": string|null, \"segments\": [{\"startSeconds\": number, "
        "\"durationSeconds\": number, \"text\": string}], \"note\": string}."
    )
    user_prompt = (
        f"Extract the transcript for this YouTube video: {input_url}\n"
        f"Preferred language: {preferred}\n"
        "If transcript is unavailable, return an empty segments array and explain in note."
    )

    model_candidates = []
    for name in [configured_model, "grok-3-latest", "grok-2-latest"]:
        if name and name not in model_candidates:
            model_candidates.append(name)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    body = None
    errors: List[str] = []
    with httpx.Client(timeout=timeout) as client:
        for model in model_candidates:
            payload = {
                "model": model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            try:
                resp = client.post(api_url, json=payload, headers=headers)
                resp.raise_for_status()
                body = resp.json()
                break
            except httpx.HTTPStatusError as exc:
                response_text = ""
                try:
                    response_text = exc.response.text[:260]
                except Exception:
                    response_text = str(exc)
                errors.append(f"{model}: {response_text or exc}")
            except Exception as exc:
                errors.append(f"{model}: {exc}")

    if body is None:
        reason = " | ".join(errors[:3]) if errors else "Grok call failed."
        return TranscriptFetchResult(
            provider="grok",
            status="pending",
            language=None,
            segments=[],
            note=f"Grok call failed: {reason}",
        )

    content = ""
    try:
        content = body["choices"][0]["message"]["content"]
    except Exception:
        pass
    if not content:
        return TranscriptFetchResult(
            provider="grok",
            status="pending",
            language=None,
            segments=[],
            note="Grok response did not contain message content.",
        )

    json_block = _extract_json_block(content)
    if not json_block:
        return TranscriptFetchResult(
            provider="grok",
            status="pending",
            language=None,
            segments=[],
            note="Grok returned non-JSON transcript payload.",
        )

    try:
        parsed = json.loads(json_block)
    except Exception as exc:
        return TranscriptFetchResult(
            provider="grok",
            status="pending",
            language=None,
            segments=[],
            note=f"Failed to parse Grok JSON: {exc}",
        )

    raw_segments = parsed.get("segments") or []
    segments: List[TranscriptSegment] = []
    for item in raw_segments:
        text = " ".join((str(item.get("text", "")) or "").split())
        if not text:
            continue
        segments.append(
            TranscriptSegment(
                startSeconds=float(item.get("startSeconds", 0.0)),
                durationSeconds=float(item.get("durationSeconds", 0.0)),
                text=text,
            )
        )

    return TranscriptFetchResult(
        provider="grok",
        status="ready" if segments else "pending",
        language=parsed.get("language") or preferred_language,
        segments=segments,
        note=str(parsed.get("note") or ("ok" if segments else "No segments from Grok.")),
    )


def fetch_transcript_with_fallback(
    video_id: str,
    youtube_url: Optional[str],
    preferred_language: Optional[str],
) -> TranscriptFetchResult:
    providers: dict[str, Callable[[str, Optional[str], Optional[str]], TranscriptFetchResult]] = {
        "youtube_timedtext": fetch_youtube_timedtext,
        "youtube_transcript_api": fetch_youtube_transcript_api,
        "grok": fetch_grok_transcript,
    }
    order = os.getenv(
        "TRANSCRIPT_PROVIDER_ORDER",
        "youtube_timedtext,youtube_transcript_api,grok",
    )
    names = [name.strip() for name in order.split(",") if name.strip()]
    if not names:
        names = ["youtube_timedtext", "youtube_transcript_api", "grok"]

    notes: List[str] = []
    best_pending: Optional[TranscriptFetchResult] = None
    for name in names:
        provider = providers.get(name)
        if provider is None:
            notes.append(f"{name}: unknown provider")
            continue
        try:
            result = provider(video_id, youtube_url, preferred_language)
        except Exception as exc:
            notes.append(f"{name}: exception {exc}")
            continue

        if result.status == "ready" and result.segments:
            return result

        notes.append(f"{name}: {result.note}")
        if best_pending is None and result.status in {"pending", "unavailable"}:
            best_pending = result

    if best_pending is not None:
        best_pending.note = " | ".join(notes[-5:])
        return best_pending

    return TranscriptFetchResult(
        provider="none",
        status="pending",
        language=None,
        segments=[],
        note="All transcript providers failed.",
    )
