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
COPY apps/api apps/api

# Re-sync to ensure editable installs are wired
RUN uv sync --frozen --no-dev --package asf-api

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/api"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
