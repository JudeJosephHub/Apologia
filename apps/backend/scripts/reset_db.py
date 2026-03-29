"""Drop all tables and recreate with current schema."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import text
from src.core.database import get_engine, get_session_factory
from src.models_base import Base
from src.domains.sermons.models import Sermon, UserSermon  # noqa: F401
from src.domains.profiles.models import Profile  # noqa: F401
from src.domains.scriptures.models import Scripture, SermonScripture  # noqa: F401
from src.domains.links.models import SermonLink  # noqa: F401
from src.domains.courses.models import Course, CourseModule  # noqa: F401


async def reset():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped")
        await conn.run_sync(Base.metadata.create_all)
        print("All tables recreated")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset())
