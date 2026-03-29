"""Daily inspiration service (ported from Apologia)."""

import hashlib
import json
import re
from typing import Optional

import httpx

from ...core import get_settings

FALLBACK_INSPIRATIONS = [
    {"kind": "verse", "text": "Trust in the Lord with all your heart and do not lean on your own understanding.", "citation": "Proverbs 3:5"},
    {"kind": "verse", "text": "Your word is a lamp to my feet and a light to my path.", "citation": "Psalm 119:105"},
    {"kind": "quote", "text": "He is no fool who gives what he cannot keep to gain what he cannot lose.", "citation": "Jim Elliot"},
    {"kind": "quote", "text": "I believe in Christianity as I believe that the sun has risen.", "citation": "C.S. Lewis"},
    {"kind": "quote", "text": "God cannot give us a happiness and peace apart from Himself.", "citation": "C.S. Lewis"},
    {"kind": "quote", "text": "The true test of faith is how we treat people in need.", "citation": "Tim Keller"},
]


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


def get_fallback(date_key: str) -> dict:
    digest = hashlib.sha256(date_key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(FALLBACK_INSPIRATIONS)
    selected = FALLBACK_INSPIRATIONS[index]
    return {"date": date_key, "kind": selected["kind"], "text": selected["text"], "citation": selected["citation"]}


def generate_daily_inspiration(date_key: str) -> dict:
    settings = get_settings()
    if not settings.grok_api_key:
        return get_fallback(date_key)

    payload = {
        "model": settings.grok_model,
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
                "content": f"Generate one daily inspiration for date {date_key}. Output JSON only.",
            },
        ],
    }
    headers = {"Authorization": f"Bearer {settings.grok_api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(settings.grok_api_url, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        content = (body.get("choices") or [{}])[0].get("message", {}).get("content", "")
        parsed = _extract_json_object(content)
        if not parsed:
            return get_fallback(date_key)
        kind = str(parsed.get("kind", "quote")).lower()
        if kind not in {"verse", "quote"}:
            kind = "quote"
        text = " ".join(str(parsed.get("text", "")).split())[:220].strip()
        citation = " ".join(str(parsed.get("citation", "")).split())[:120].strip()
        if not text or not citation:
            return get_fallback(date_key)
        return {"date": date_key, "kind": kind, "text": text, "citation": citation}
    except Exception:
        return get_fallback(date_key)
