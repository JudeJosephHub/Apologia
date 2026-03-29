"""Apologia – unified FastAPI application.

AI-powered sermon encyclopedia combining PPTX processing, knowledge graph,
daily inspiration, auth, profiles, AI workbench, courses, and scripture linking.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import get_settings
from .core.middleware import RequestTimingMiddleware
from .domains.ai.routes import router as ai_router
from .domains.auth.routes import router as auth_router
from .domains.courses.routes import router as courses_router
from .domains.inspiration.routes import router as inspiration_router
from .domains.intelligence.routes import router as intelligence_router
from .domains.links.routes import router as links_router
from .domains.pptx.routes import router as pptx_router
from .domains.profiles.routes import router as profiles_router
from .domains.scriptures.routes import router as scriptures_router
from .domains.sermons.routes import router as sermons_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup – create tables if using SQLite fallback
    from .core.database import get_engine
    from .models_base import Base
    # Import all models so they're registered on Base.metadata
    from .domains.sermons.models import Sermon, UserSermon  # noqa: F401
    from .domains.profiles.models import Profile  # noqa: F401
    from .domains.scriptures.models import Scripture, SermonScripture  # noqa: F401
    from .domains.links.models import SermonLink  # noqa: F401
    from .domains.courses.models import Course, CourseModule  # noqa: F401
    from .domains.intelligence.models import SermonEntity, SermonEdge  # noqa: F401

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Shutdown
    try:
        await engine.dispose()
    except RuntimeError:
        pass


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Sermon Encyclopedia & Pastor Workbench",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestTimingMiddleware)

    # Routers – core
    prefix = "/api/v1"
    app.include_router(auth_router, prefix=prefix)
    app.include_router(profiles_router, prefix=prefix)
    app.include_router(sermons_router, prefix=prefix)
    app.include_router(scriptures_router, prefix=prefix)
    app.include_router(ai_router, prefix=prefix)
    app.include_router(links_router, prefix=prefix)
    app.include_router(courses_router, prefix=prefix)

    # Routers – Apologia features
    app.include_router(pptx_router, prefix=prefix)
    app.include_router(intelligence_router, prefix=prefix)
    app.include_router(inspiration_router, prefix=prefix)

    @app.get("/health")
    async def health():
        return {"ok": True, "service": settings.app_name}

    return app


app = create_app()
