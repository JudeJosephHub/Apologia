"""Profile domain – SQLAlchemy models."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from ...models_base import Base, TimestampMixin


class Profile(TimestampMixin, Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    auth_uid = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(320), nullable=False)
    full_name = Column(String(255), default="")
    avatar_url = Column(Text, default="")
    role = Column(String(50), default="viewer")  # viewer | contributor | admin
    denomination = Column(String(100), default="")
    bio = Column(Text, default="")

    sermons = relationship("Sermon", back_populates="author", lazy="selectin")
    user_sermons = relationship("UserSermon", back_populates="profile", lazy="selectin")
