# Local development stack

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- [uv](https://docs.astral.sh/uv/) (Python 3.11+)
- [pnpm](https://pnpm.io/) 9.x (for `apps/web`)

## Start services

```bash
make up
# or
docker compose -f infra/docker-compose.yml up -d
```

## Service map

| Service | URL / port | Purpose |
| --- | --- | --- |
| Postgres + pgvector | `localhost:5432` | App DB (`astepforward`) |
| Redis | `localhost:6379` | Cache, Celery broker |
| Neo4j | `http://localhost:7474`, bolt `7687` | Knowledge graph |
| MinIO (S3) | API `9000`, console `9001` | Local object storage |
| Mailhog | SMTP `1025`, UI `8025` | Dev email capture |
| Langfuse | `http://localhost:3001` | LLM tracing UI |
| OTel collector | gRPC `4317`, HTTP `4318` | Trace/metric ingestion |
| Prometheus | `http://localhost:9090` | Metrics |
| Grafana | `http://localhost:3002` | Dashboards (`admin` / `admin`) |

Default credentials match `.env.example`. **Never use these in staging or production.**

## App processes

After `make up`:

```bash
make migrate
cd apps/api && uv sync && uv run uvicorn app.main:app --reload
cd apps/web && pnpm install && pnpm dev
```

## MinIO bucket

`minio-init` creates the `astepforward-media` bucket on first boot. Set in `.env.local`:

```
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=miniominio
S3_BUCKET=astepforward-media
```

## Tear down

```bash
make down
# Remove volumes (destructive):
docker compose -f infra/docker-compose.yml down -v
```
