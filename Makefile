# A Step Forward — top-level Makefile (Phase 0).
# Sub-agent 09-infra extends this with deploy targets, eval gates, and
# per-service helpers. Keep targets cross-platform-friendly where possible.

PYTHON ?= python
UV ?= uv
UV_FLAGS ?= --system-certs

.PHONY: help up down dev migrate migrate-revision seed seed-kg seed-diagnostic ingest evals evals-ci lint fmt test smoke sync

help:
	@echo "Targets:"
	@echo "  sync             uv sync (Python 3.11 workspace)"
	@echo "  up               Start Docker Compose stack"
	@echo "  down             Stop the stack"
	@echo "  dev              Start API + web in dev mode (requires up)"
	@echo "  migrate          Run Alembic upgrade head against compose Postgres"
	@echo "  migrate-revision Autogenerate Alembic revision (msg=...)"
	@echo "  seed             Seed curriculum + sample learner"
	@echo "  seed-kg          Seed Neo4j prerequisite graph from content/knowledge-graph/"
	@echo "  seed-diagnostic  Bootstrap diagnostic_items MCQ bank from KG YAML"
	@echo "  ingest           Ingest Learning Database PDFs into Postgres"
	@echo "  evals            Run full eval suite (promptfoo + DeepEval + memory)"
	@echo "  evals-ci         Run touched-only evals (CI default)"
	@echo "  lint fmt         ruff/eslint/prettier"
	@echo "  test             pytest + vitest"
	@echo "  smoke            Run Phase-0 smoke tests (memory, graphrag, orchestrator)"

sync:
	$(UV) sync --all-groups --python 3.11 $(UV_FLAGS)

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

dev:
	@echo "Run 'cd apps/api && uv run uvicorn app.main:app --reload' in one terminal,"
	@echo "and 'cd apps/web && pnpm dev' in another."

migrate:
	$(UV) run $(UV_FLAGS) alembic -c infra/alembic.ini upgrade head

migrate-revision:
	$(UV) run $(UV_FLAGS) alembic -c infra/alembic.ini revision --autogenerate -m "$(msg)"

seed:
	$(UV) run $(UV_FLAGS) python scripts/seed_curriculum.py

seed-kg:
	$(UV) run $(UV_FLAGS) python scripts/seed_knowledge_graph.py

seed-diagnostic:
	$(UV) run $(UV_FLAGS) python scripts/seed_diagnostic_items.py

ingest:
	$(UV) run $(UV_FLAGS) python scripts/ingest_learning_db.py --db-url $(DATABASE_URL) \
	  --source "Learning Database/" --storage-bucket $(R2_BUCKET)

evals:
	$(UV) sync --all-groups --python 3.11 $(UV_FLAGS)
	cd evals && pnpm install
	$(UV) run $(UV_FLAGS) python evals/runner.py

evals-ci:
	$(UV) run $(UV_FLAGS) python evals/runner.py --touched

lint:
	$(UV) run $(UV_FLAGS) ruff check infra tests scripts
	cd apps/web && pnpm lint

fmt:
	$(UV) run $(UV_FLAGS) ruff format infra tests scripts
	cd apps/web && pnpm exec prettier --write .

test:
	$(UV) run $(UV_FLAGS) pytest
	cd apps/web && pnpm test

smoke:
	$(PYTHON) services/memory/tests/test_smoke.py
	$(PYTHON) services/graphrag/tests/test_smoke.py
	$(PYTHON) services/orchestrator/tests/test_smoke.py
