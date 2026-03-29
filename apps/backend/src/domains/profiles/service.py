"""Profiles service – business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.profile import ProfileRead, ProfileUpdate
from .repository import ProfileRepository


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def get_profile(self, auth_uid: str) -> ProfileRead | None:
        profile = await self.repo.get_by_auth_uid(auth_uid)
        if not profile:
            return None
        return ProfileRead.model_validate(profile)

    async def get_or_create_profile(self, *, auth_uid: str, email: str, full_name: str = "") -> ProfileRead:
        profile = await self.repo.get_by_auth_uid(auth_uid)
        if not profile:
            profile = await self.repo.create(auth_uid=auth_uid, email=email, full_name=full_name)
        return ProfileRead.model_validate(profile)

    async def update_profile(self, auth_uid: str, data: ProfileUpdate) -> ProfileRead:
        profile = await self.repo.get_by_auth_uid(auth_uid)
        if not profile:
            raise ValueError("Profile not found")
        updated = await self.repo.update(profile, **data.model_dump(exclude_unset=True))
        return ProfileRead.model_validate(updated)
