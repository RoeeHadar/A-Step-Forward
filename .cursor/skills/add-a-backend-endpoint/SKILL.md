---
name: add-a-backend-endpoint
description: How to add a FastAPI endpoint in apps/api with Pydantic schemas, auth/RBAC, rate limit, repository access, and OpenAPI docs. Read BEFORE adding or modifying any route under apps/api/.
---

# Add a Backend Endpoint

## When to use
Adding a route under `apps/api/app/routers/...`.

## Steps

1. **Define schemas** in `packages/schemas/<area>.py` (Pydantic v2). Inputs end with `Input`, outputs with `Output` (or a domain noun).
2. **Add the router** in `apps/api/app/routers/<area>.py`:
   ```python
   from fastapi import APIRouter, Depends
   from app.core.auth import require_learner, AuthCtx
   from app.core.rate_limit import per_user
   from schemas.memory import MemorySearchInput, MemoryRecord
   from services.memory.memory_service.api import MemoryService, get_memory_service

   router = APIRouter(prefix="/v1/memory", tags=["memory"])

   @router.post("/search", response_model=list[MemoryRecord])
   async def search(
       body: MemorySearchInput,
       ctx: AuthCtx = Depends(require_learner),
       mem: MemoryService = Depends(get_memory_service),
       _ = Depends(per_user("memory.search", per_min=120)),
   ) -> list[MemoryRecord]:
       return await mem.search(body, ctx)
   ```
3. **Errors**: raise from `packages/schemas/errors.py`; handlers in `app/core/exception_handlers.py` map to HTTP.
4. **Telemetry**: spans are auto-created via OpenTelemetry middleware; add custom attributes for `learner_id`, `route`.
5. **Tests**:
   - Unit test the router with a fake service via dependency override.
   - Integration test against Docker Compose Postgres/Redis.
6. **OpenAPI**: title + description per route; example bodies via `model_config`.

## Pitfalls
- Never accept `learner_id` from request body for reads — always from `AuthCtx`.
- Never bypass the service layer to talk to Postgres/Redis/Neo4j.
- Never return Pydantic models from internal services without re-validating at the API boundary.
- Don't add a new HTTP verb for what should be a query parameter (e.g., no `POST /search-and-count`).
- **`EmailStr` requires `email-validator`** — add it to `apps/api/pyproject.toml` and run `uv lock`, or use `str` + `Field(pattern=...)` instead. FastAPI builds OpenAPI schemas at startup; missing `email-validator` crashes Render/Docker with `ImportError` even though root `pytest` never imported the app.
- After adding a router, run **`uv run --package asf-api python -c "from app.main import app"`** locally (mirrors Render). CI runs this as **API import smoke** — root `pytest tests/` alone does not load `apps/api`.
