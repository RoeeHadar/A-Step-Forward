# Infrastructure

Local development, migrations, CI/CD, secrets, and observability for **A Step Forward**.

| Doc | Contents |
| --- | --- |
| [local-dev.md](./local-dev.md) | Docker Compose stack, ports, first-run |
| [migrations.md](./migrations.md) | Alembic async setup, autogenerate workflow |
| [ci-cd.md](./ci-cd.md) | GitHub Actions workflows, staging vs production |
| [secrets.md](./secrets.md) | Doppler, Vercel envs, local `.env.local` |
| [observability.md](./observability.md) | Langfuse, OTel, Prometheus, Grafana, Sentry |

## Quick start

```bash
cp .env.example .env.local   # edit secrets as needed
make up
make migrate
```

## Layout

```
infra/
  docker-compose.yml    # local stack
  alembic.ini           # Alembic config (async Postgres)
  alembic/              # env.py + versions/
  otel-collector.yaml
  prometheus.yml
  grafana/provisioning/
  fly/                  # Fly.io app configs (staging/prod)
.github/workflows/      # lint-test, evals, deploy-*
```

See also: `skills/deploy/SKILL.md`, `skills/db-migrations/SKILL.md`, `.cursor/subagent-briefs/09-infra.md`.
