FROM python:3.11-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.10 /uv /uvx /usr/local/bin/

# Copy workspace definition files first for layer caching
COPY pyproject.toml uv.lock ./
COPY apps/api/pyproject.toml apps/api/
COPY packages/schemas/pyproject.toml packages/schemas/
COPY packages/agents/pyproject.toml packages/agents/
COPY services/memory/pyproject.toml services/memory/
COPY services/graphrag/pyproject.toml services/graphrag/
COPY services/orchestrator/pyproject.toml services/orchestrator/
COPY services/workers/pyproject.toml services/workers/
COPY services/curriculum/pyproject.toml services/curriculum/
COPY services/learner_model/pyproject.toml services/learner_model/
COPY services/diagnostic/pyproject.toml services/diagnostic/
COPY services/learning_path/pyproject.toml services/learning_path/

# Install all workspace dependencies
RUN uv sync --frozen --no-dev --package asf-api

# Copy source code
COPY packages/schemas packages/schemas
COPY packages/agents packages/agents
COPY services/__init__.py services/__init__.py
COPY services/memory services/memory
COPY services/graphrag services/graphrag
COPY services/orchestrator services/orchestrator
COPY services/workers services/workers
COPY services/curriculum services/curriculum
COPY services/learner_model services/learner_model
COPY services/diagnostic services/diagnostic
COPY services/learning_path services/learning_path
COPY apps/api apps/api

# Re-sync to ensure editable installs are wired
RUN uv sync --frozen --no-dev --package asf-api

# Belt-and-suspenders for Render's aggressive layer caching: explicitly
# ensure `email-validator` is installed even if an earlier `uv sync` layer
# was cached from before this dep was added. Without this, pydantic's
# `EmailStr` (used in routers/bookings.py) raises at module import time.
RUN /app/.venv/bin/pip install --no-cache-dir 'email-validator>=2.2' \
    && /app/.venv/bin/python -c "import email_validator; print('email_validator OK', email_validator.__version__)"

# Verify learner-model + diagnostic packages import (matches CI import smoke)
RUN uv run --package asf-api python -c "\
from app.main import app; \
from learner_model_service.api import get_learner_model_service; \
from diagnostic_service.api import get_diagnostic_service; \
from learning_path_service.api import get_learning_path_service; \
assert app.title; get_learner_model_service; get_diagnostic_service; get_learning_path_service"

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/api"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
