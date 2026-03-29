"""Scripture schemas."""

from pydantic import BaseModel


class ScriptureBase(BaseModel):
    book: str
    chapter: int
    verse_start: int
    verse_end: int | None = None
    text: str | None = None
    translation: str = "KJV"


class ScriptureRead(ScriptureBase):
    id: int

    class Config:
        from_attributes = True


class SermonScriptureMapping(BaseModel):
    sermon_id: int
    scripture_id: int
    context: str | None = None
