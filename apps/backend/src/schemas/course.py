"""Course schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int
    author_id: Optional[int] = None
    status: str = "draft"
    created_at: datetime

    class Config:
        from_attributes = True


class CourseModuleBase(BaseModel):
    title: str
    content: Optional[str] = None
    order: int = 0
    sermon_id: Optional[int] = None


class CourseModuleCreate(CourseModuleBase):
    course_id: int


class CourseModuleRead(CourseModuleBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True


class CourseDetail(CourseRead):
    modules: list[CourseModuleRead] = []
