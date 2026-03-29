"""Courses routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...schemas.course import CourseCreate, CourseDetail, CourseModuleCreate, CourseRead
from .service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
async def list_courses(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    svc = CourseService(db)
    return await svc.list_courses(offset=offset, limit=limit)


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    svc = CourseService(db)
    return await svc.get_course(course_id)


@router.post("", response_model=CourseRead, status_code=201)
async def create_course(
    data: CourseCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CourseService(db)
    return await svc.create_course(data)


@router.post("/{course_id}/modules")
async def add_module(
    course_id: int,
    data: CourseModuleCreate,
    _user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CourseService(db)
    return await svc.add_module(course_id, data)


@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: int,
    _user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CourseService(db)
    await svc.delete_course(course_id)
