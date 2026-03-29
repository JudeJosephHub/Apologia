"""Scriptures domain – SQLAlchemy models."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ...models_base import Base, TimestampMixin


class Scripture(TimestampMixin, Base):
    __tablename__ = "scriptures"

    id = Column(Integer, primary_key=True, index=True)
    book = Column(String(50), nullable=False, index=True)
    chapter = Column(Integer, nullable=False)
    verse_start = Column(Integer, nullable=False)
    verse_end = Column(Integer, nullable=True)
    text = Column(Text, default="")
    translation = Column(String(20), default="KJV")

    sermon_mappings = relationship("SermonScripture", back_populates="scripture", lazy="selectin")


class SermonScripture(Base):
    """Many-to-many relationship between sermons and scriptures."""
    __tablename__ = "sermon_scriptures"

    id = Column(Integer, primary_key=True, index=True)
    sermon_id = Column(Integer, ForeignKey("sermons.id", ondelete="CASCADE"), nullable=False)
    scripture_id = Column(Integer, ForeignKey("scriptures.id", ondelete="CASCADE"), nullable=False)
    context = Column(Text, default="")  # How this scripture is used

    sermon = relationship("Sermon", back_populates="scriptures", lazy="selectin")
    scripture = relationship("Scripture", back_populates="sermon_mappings", lazy="selectin")
