# A Step Forward — top-level Makefile (Phase 0).
# Sub-agent 09-infra extends this with deploy targets, eval gates, and
# per-service helpers. Keep targets cross-platform-friendly where possible.

PYTHON ?= python

.PHONY: help up down dev migrate migrate-revision seed evals evals-ci lint fmt test smoke

help:
	@echo "Targets:"
	@echo "  up               Start Docker Compose (Postgres, Redis, Neo4j, Langfuse, MinIO, Mailhog, OTel, Prometheus, Grafana)"
	@echo "  down             Stop the stack"
	@echo "  dev              Start API + web in dev mode (requires up)"
	@echo "  migrate          Run Alembic upgrade head against compose Postgres"
	@echo "  migrate-revision Autogenerate Alembic revision (msg=...)"
	@echo "  seed             Seed curriculum + sample learner"
	@echo "  evals            Run full eval suite (promptfoo + DeepEval + memory)"
	@echo "  evals-ci         Run touched-only evals (CI default)"
	@echo "  lint fmt         ruff/eslint/prettier"
	@echo "  test             pytest + vitest"
	@echo "  smoke            Run Phase-0 smoke tests (memory, graphrag, orchestrator)"

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

dev:
	@echo "Run 'cd apps/api && uv run uvicorn app.main:app --reload' in one terminal,"
	@echo "and 'cd apps/web && pnpm dev' in another."

migrate:
	uv run alembic -c infra/alembic.ini upgrade head

migrate-revision:
	uv run alembic -c infra/alembic.ini revision --autogenerate -m "$(msg)"

seed:
	uv run python scripts/seed_curriculum.py

evals:
	uv sync
	cd evals && pnpm install
	uv run python evals/runner.py

evals-ci:
	uv run python evals/runner.py --touched

lint:
	uv run ruff check .
	cd apps/web && pnpm lint

fmt:
	uv run ruff format .
	cd apps/web && pnpm exec prettier --write .

test:
	uv run pytest
	cd apps/web && pnpm test

smoke:
	$(PYTHON) services/memory/tests/test_smoke.py
	$(PYTHON) services/graphrag/tests/test_smoke.py
	$(PYTHON) services/orchestrator/tests/test_smoke.py
