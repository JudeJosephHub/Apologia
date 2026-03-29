"""SQLAlchemy async engine and session factory."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from . import get_settings

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None

_SQLITE_URL = "sqlite+aiosqlite:///./sermonopedia.db"


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        db_url = settings.database_url
        if not db_url or "[YOUR-PASSWORD]" in db_url:
            logger.warning("DATABASE_URL not configured – falling back to local SQLite")
            db_url = _SQLITE_URL
        kwargs = {"echo": settings.debug}
        if db_url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            kwargs["pool_pre_ping"] = True
            kwargs["pool_size"] = 5
            kwargs["max_overflow"] = 10
        _engine = create_async_engine(db_url, **kwargs)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _session_factory


async def get_db() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        yield session
