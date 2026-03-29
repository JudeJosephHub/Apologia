"""Links domain – SQLAlchemy models for semantic sermon linking."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ...models_base import Base, TimestampMixin


class SermonLink(TimestampMixin, Base):
    __tablename__ = "sermon_links"

    id = Column(Integer, primary_key=True, index=True)
    source_sermon_id = Column(Integer, ForeignKey("sermons.id", ondelete="CASCADE"), nullable=False)
    target_sermon_id = Column(Integer, ForeignKey("sermons.id", ondelete="CASCADE"), nullable=False)
    link_type = Column(String(50), nullable=False)  # thematic | scriptural | topical | series
    score = Column(Float, default=0.0)
    reason = Column(Text, default="")

    source_sermon = relationship("Sermon", foreign_keys=[source_sermon_id], back_populates="links_as_source", lazy="selectin")
    target_sermon = relationship("Sermon", foreign_keys=[target_sermon_id], lazy="selectin")
