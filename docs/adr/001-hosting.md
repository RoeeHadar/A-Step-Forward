# ADR-001: Vercel (Web) + Render (API) over Fly.io
Status: Accepted
Date: 2026-06-24

## Context
- Frontend (Next.js) benefits from Vercel's native integration: zero-config deployment, edge CDN, and native GitHub App support.
- Backend (FastAPI) needed a free-tier PaaS that does not require a credit card to deploy.
- Fly.io was the original plan but requires a credit card even for the free tier, which is a blocker for this open-source, no-budget-at-launch project.
- Render offers a free web service tier with no credit card requirement.
- Railway was considered but also requires payment information.

## Decision
- Web app → Vercel (using native GitHub App integration, not Vercel CLI)
- API gateway → Render free tier (service: asf-api-q566.onrender.com)
- Background workers → Render Cron Jobs (when implemented)
- Langfuse observability → self-host on Render free tier if needed

## Consequences
- Positive: No credit card required; both Vercel and Render have generous free tiers for solo projects.
- Trade-off: Render free web services spin down after 15 minutes of inactivity, causing ~15s cold-start latency on first request. The frontend has a "Connecting to your AI tutor, please wait…" message to handle this gracefully.
- Trade-off: Render free tier has 750 instance-hours/month limit. Sufficient for early-stage use.
- Future: When the project scales, migrate API to Render paid tier or Fly.io (once a card is available).
