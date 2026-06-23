# Observability

Stack per `PLAN.md` §11 and `skills/deploy/SKILL.md`.

## Local (Docker Compose)

| Tool | Access | Role |
| --- | --- | --- |
| **Langfuse** | http://localhost:3001 | LLM traces, prompt versioning |
| **OTel collector** | OTLP gRPC `4317`, HTTP `4318` | Ingest traces/metrics/logs from apps |
| **Prometheus** | http://localhost:9090 | Scrape OTel exporter metrics |
| **Grafana** | http://localhost:3002 | Dashboards (default `admin` / `admin`) |

Apps should export OTLP to `http://localhost:4318` (or gRPC `4317`) when `APP_ENV=local`.

Langfuse keys: set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` in `.env.local` after creating a project in the local Langfuse UI.

## Production

| Tool | Deployment | Notes |
| --- | --- | --- |
| **Langfuse** | Self-hosted on Fly | Primary LLM trace store |
| **Sentry** | SaaS | Error tracking; `SENTRY_DSN` per app |
| **Prometheus + Grafana** | Fly or managed | Latency, cost, tokens, eval scores |
| **Structured logs** | JSON + correlation IDs | `structlog` in Python services |

## Metrics to watch

- Request latency p50/p95 per route and agent
- LLM token usage and cost per learner/session
- Retrieval recall@k (GraphRAG / memory)
- Eval regression flags from `evals.yml`
- Error rate and RBAC denial rate

## Alerts (Phase 4+)

- Cost spikes
- Eval score regressions vs baseline
- Elevated 5xx / health-check failures on Fly
