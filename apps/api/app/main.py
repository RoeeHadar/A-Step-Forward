"""FastAPI gateway entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio

from .core.auth import validate_auth_config, warmup_clerk_jwks
from .core.exception_handlers import register_exception_handlers
from .core.settings import get_settings
from .core.telemetry import configure_logging, configure_sentry, instrument_app
from .routers import (
    admin,
    agents,
    assessment,
    bookings,
    chat,
    content,
    diagnostic,
    graphrag,
    health,
    learners,
    learning_path,
    lessons,
    memory,
    memory_admin,
    onboarding,
    progress,
    search,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Keep startup ultra-fast so cold-start health checks always pass.

    Render's free tier sometimes shows a "deploy failed (health check
    timed out)" email when the cold-start exceeds its internal window,
    even though the new image is healthy. We:
      - run only quick synchronous config here, and
      - fire the JWKS warmup as a background task so an unreachable
        Clerk doesn't delay the first ``/healthz`` response.
    """
    settings = get_settings()
    validate_auth_config()
    configure_logging(settings)
    configure_sentry(settings)
    asyncio.create_task(warmup_clerk_jwks())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="A Step Forward API",
        version="0.1.0",
        description="Gateway for the A Step Forward learning center.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    instrument_app(app, settings)

    app.include_router(health.router)
    app.include_router(assessment.router)
    app.include_router(chat.router)
    app.include_router(agents.router)
    app.include_router(learners.router)
    app.include_router(learning_path.router)
    app.include_router(onboarding.router)
    app.include_router(diagnostic.router)
    app.include_router(lessons.router)
    app.include_router(content.router)
    app.include_router(bookings.router)
    app.include_router(progress.router)
    app.include_router(memory.router)
    app.include_router(graphrag.router)
    app.include_router(search.router)
    app.include_router(admin.router)
    app.include_router(memory_admin.router)
    return app


app = create_app()
