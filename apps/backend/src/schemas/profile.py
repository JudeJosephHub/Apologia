"""Profile schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    denomination: Optional[str] = None
    bio: Optional[str] = None


class ProfileRead(ProfileBase):
    id: int
    auth_uid: str
    email: str
    avatar_url: Optional[str] = None
    role: str = "viewer"
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(ProfileBase):
    pass
