"""Sermons domain – SQLAlchemy models."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ...models_base import Base, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
    _embedding_type = Vector(1536)
except Exception:
    _embedding_type = Text()


class Sermon(TimestampMixin, Base):
    __tablename__ = "sermons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    preacher = Column(String(255), default="")
    date_preached = Column(String(20), default="")
    denomination = Column(String(100), default="")
    source_url = Column(Text, default="")
    audio_url = Column(Text, default="")
    transcript = Column(Text, default="")
    summary = Column(Text, default="")
    outline = Column(Text, default="")
    themes = Column(Text, default="")  # JSON array stored as text
    status = Column(String(50), default="draft")  # draft | processing | published
    sermonaudio_id = Column(String(100), default="", index=True)
    embedding = Column(_embedding_type, nullable=True)

    # -- Fields from Apologia --
    series_name = Column(String(255), default="")
    church_name = Column(String(255), default="")
    youtube_url = Column(Text, default="")
    youtube_video_id = Column(String(100), default="")
    youtube_channel_id = Column(String(100), default="")
    video_status = Column(String(50), default="pending_match")
    transcript_status = Column(String(50), default="none")
    file_path = Column(Text, default="")  # relative path to uploaded PPTX
    original_filename = Column(String(500), default="")

    author_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    author = relationship("Profile", back_populates="sermons", lazy="selectin")

    scriptures = relationship("SermonScripture", back_populates="sermon", cascade="all, delete-orphan", lazy="selectin")
    links_as_source = relationship("SermonLink", foreign_keys="SermonLink.source_sermon_id", back_populates="source_sermon", cascade="all, delete-orphan", lazy="selectin")


class UserSermon(TimestampMixin, Base):
    """User's personal sermon workspace entry."""
    __tablename__ = "user_sermons"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    notes = Column(Text, default="")
    status = Column(String(50), default="draft")

    profile = relationship("Profile", back_populates="user_sermons", lazy="selectin")
