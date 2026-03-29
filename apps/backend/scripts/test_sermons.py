"""Quick test: does the sermon service work?"""
import asyncio
import os
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.database import get_engine, get_session_factory
from src.models_base import Base
from src.domains.sermons.models import Sermon, UserSermon
from src.domains.profiles.models import Profile
from src.domains.scriptures.models import Scripture, SermonScripture
from src.domains.links.models import SermonLink
from src.domains.courses.models import Course, CourseModule
from src.domains.sermons.service import SermonService


async def test():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = get_session_factory()
    async with factory() as session:
        svc = SermonService(session)
        try:
            result = await svc.list_sermons(offset=0, limit=3)
            print("SUCCESS!")
            print(f"Total: {result.total}")
            for item in result.items:
                print(f"  - {item.id}: {item.title} by {item.preacher}")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test())
