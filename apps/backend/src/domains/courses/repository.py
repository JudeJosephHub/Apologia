"""Courses repository – data access layer."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Course, CourseModule


class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_courses(self, *, offset: int = 0, limit: int = 20) -> tuple[list[Course], int]:
        count_result = await self.db.execute(select(func.count(Course.id)))
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(Course).order_by(Course.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, course_id: int) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Course:
        course = Course(**kwargs)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def update(self, course: Course, **kwargs) -> Course:
        for key, value in kwargs.items():
            if hasattr(course, key):
                setattr(course, key, value)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def delete(self, course: Course) -> None:
        await self.db.delete(course)
        await self.db.commit()

    async def add_module(self, *, course_id: int, **kwargs) -> CourseModule:
        module = CourseModule(course_id=course_id, **kwargs)
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module
