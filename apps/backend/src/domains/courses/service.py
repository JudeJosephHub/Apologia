"""Courses service – business logic."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.course import CourseCreate, CourseDetail, CourseModuleCreate, CourseRead
from .repository import CourseRepository


class CourseService:
    def __init__(self, db: AsyncSession):
        self.repo = CourseRepository(db)

    async def list_courses(self, *, offset: int = 0, limit: int = 20) -> dict:
        courses, total = await self.repo.list_courses(offset=offset, limit=limit)
        return {"items": [CourseRead.model_validate(c) for c in courses], "total": total}

    async def get_course(self, course_id: int) -> CourseDetail:
        course = await self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return CourseDetail.model_validate(course)

    async def create_course(self, data: CourseCreate) -> CourseRead:
        course = await self.repo.create(**data.model_dump())
        return CourseRead.model_validate(course)

    async def add_module(self, course_id: int, data: CourseModuleCreate) -> dict:
        course = await self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        module = await self.repo.add_module(course_id=course_id, **data.model_dump())
        return {"id": module.id, "title": module.title}

    async def delete_course(self, course_id: int) -> None:
        course = await self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        await self.repo.delete(course)
