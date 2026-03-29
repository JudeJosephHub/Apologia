"""Profiles routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...schemas.profile import ProfileRead, ProfileUpdate
from .service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileRead)
async def get_my_profile(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = ProfileService(db)
    profile = await svc.get_or_create_profile(auth_uid=user["id"], email=user.get("email", ""))
    return profile


@router.patch("/me", response_model=ProfileRead)
async def update_my_profile(
    data: ProfileUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    return await svc.update_profile(user["id"], data)
