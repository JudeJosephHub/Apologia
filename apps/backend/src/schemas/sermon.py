"""Sermon schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SermonBase(BaseModel):
    title: str
    preacher: Optional[str] = None
    date_preached: Optional[str] = None
    audio_url: Optional[str] = None
    source_url: Optional[str] = None
    denomination: Optional[str] = None


class SermonCreate(SermonBase):
    sermonaudio_id: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    outline: Optional[str] = None
    themes: Optional[str] = None
    status: Optional[str] = "published"
    # Apologia fields
    series_name: Optional[str] = None
    church_name: Optional[str] = None
    youtube_url: Optional[str] = None


class SermonRead(SermonBase):
    id: int
    sermonaudio_id: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    outline: Optional[str] = None
    themes: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    # Apologia fields
    series_name: Optional[str] = None
    church_name: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_video_id: Optional[str] = None
    video_status: Optional[str] = None
    transcript_status: Optional[str] = None
    file_path: Optional[str] = None
    original_filename: Optional[str] = None

    class Config:
        from_attributes = True


class SermonList(BaseModel):
    items: list[SermonRead]
    total: int


class UserSermonBase(BaseModel):
    title: str
    content: Optional[str] = None
    notes: Optional[str] = None


class UserSermonCreate(UserSermonBase):
    pass


class UserSermonRead(UserSermonBase):
    id: int
    profile_id: int
    status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserSermonList(BaseModel):
    items: list[UserSermonRead]
    total: int
