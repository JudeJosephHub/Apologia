"""Courses domain – SQLAlchemy models."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ...models_base import Base, TimestampMixin


class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    author_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    status = Column(String(50), default="draft")  # draft | published | archived

    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan", lazy="selectin", order_by="CourseModule.order")


class CourseModule(TimestampMixin, Base):
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    sermon_id = Column(Integer, ForeignKey("sermons.id"), nullable=True)
    order = Column(Integer, default=0)

    course = relationship("Course", back_populates="modules", lazy="selectin")
