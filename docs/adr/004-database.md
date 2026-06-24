# ADR-004: Neon (Postgres) + Upstash (Redis) + Neo4j AuraDB Free (Graph)
Status: Accepted
Date: 2026-06-24

## Context
- The system needs three data stores: relational + vector (Postgres/pgvector), cache/queue (Redis), and knowledge graph (Neo4j).
- All three must be available on free tiers with no credit card required.
- Neon offers a serverless Postgres free tier (no credit card, 0.5 GB storage, auto-pause).
- Upstash offers a serverless Redis free tier (no credit card, 10,000 commands/day).
- Neo4j AuraDB Free offers a managed Neo4j instance (no credit card, 200K nodes limit).
- Self-hosted alternatives (via Docker) work locally but not on free cloud tiers.

## Decision
- Postgres: Neon (serverless, pgvector enabled for embeddings)
- Redis: Upstash (serverless Redis, used for caching and rate limiting)
- Graph DB: Neo4j AuraDB Free (knowledge graph for GraphRAG)
- Connection strings are stored in Render env vars and Vercel env vars (not in repo)

## Consequences
- Positive: No credit card required across all three stores; zero operating cost at launch.
- Trade-off: Neon auto-pauses after 5 minutes of inactivity on the free tier, causing ~1-2s connection latency on the first query after idle.
- Trade-off: Upstash free tier limits of 10,000 commands/day may be hit under sustained load.
- Trade-off: Neo4j AuraDB Free has a 200,000 node / 400,000 relationship limit.
- Future: Migrate to paid tiers when user growth warrants. The abstraction layers (SQLAlchemy, redis-py, neo4j driver) make migration straightforward.
