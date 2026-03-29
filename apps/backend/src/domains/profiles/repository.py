"""Profiles repository – data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Profile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_auth_uid(self, auth_uid: str) -> Profile | None:
        result = await self.db.execute(select(Profile).where(Profile.auth_uid == auth_uid))
        return result.scalar_one_or_none()

    async def get_by_id(self, profile_id: int) -> Profile | None:
        result = await self.db.execute(select(Profile).where(Profile.id == profile_id))
        return result.scalar_one_or_none()

    async def create(self, *, auth_uid: str, email: str, full_name: str = "", role: str = "viewer") -> Profile:
        profile = Profile(auth_uid=auth_uid, email=email, full_name=full_name, role=role)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(self, profile: Profile, **kwargs) -> Profile:
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
