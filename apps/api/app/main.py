"""FastAPI gateway entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    lessons,
    memory,
    memory_admin,
    onboarding,
    progress,
    search,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    validate_auth_config()
    await warmup_clerk_jwks()
    configure_logging(settings)
    configure_sentry(settings)
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
