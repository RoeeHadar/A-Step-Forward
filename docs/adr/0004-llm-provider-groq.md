# ADR-0004 — Groq Cloud as the primary LLM provider

- **Status**: Accepted
- **Date**: 2026-06-24
- **Deciders**: Opus + Agents sub-agent (Composer 2.5)

> Note: the original brief referenced "ADR-0002" but slots 0001–0003 are already
> taken; this ADR uses the next available number (0004).

## Context

The Tutor (and the rest of the learner-facing roster) needs a real LLM to
produce answers. Until now `packages/agents/agents/base/llm.py` returned a
hard-coded `[stub LLM response — provider not configured]` placeholder, and the
deployed frontend papered over it with the `getMockResponse` fallback in
`apps/web/src/app/api/chat/route.ts`. That made the demo look broken.

Hard constraints set by the project owner:

1. **No paid providers.** No Anthropic, OpenAI, Voyage, or Cohere keys.
2. **No credit card required.** That rules out Cloudflare Workers AI, AWS
   Bedrock, and most Together AI tiers.
3. **Must work today on the free public site
   (https://a-step-forward-waij.vercel.app).**

We still want the standard agent contract: async, streaming, retry on
transient errors, OpenAI-shaped messages, and an offline stub for CI.

## Decision

Adopt **Groq Cloud** (https://console.groq.com) as the primary LLM provider for
all runtime agents.

- Default model: `llama-3.3-70b-versatile` (general-purpose tutoring quality).
- Cheap / bulk model: `llama-3.1-8b-instant` (Note-Taker, Engagement, KG batch).
- Transport: OpenAI-compatible REST API at `https://api.groq.com/openai/v1`,
  consumed through the official `groq` Python SDK (`AsyncGroq`).
- Config: `GROQ_API_KEY`, `LLM_DEFAULT_MODEL`, `LLM_CHEAP_MODEL` loaded via
  `pydantic-settings` (`LLMSettings`). No `os.getenv` inline (rule
  `20-python-style.mdc`).
- Retries: 3 attempts with exponential backoff + jitter on 429 / 5xx /
  network-level errors. 30 s timeout per call.
- Streaming: `LLM.astream()` yields token-text chunks; the Tutor's new
  `astream_reply` forwards them as `ChatChunk(kind="token", ...)` over the
  existing SSE endpoint.
- Offline behavior: when `groq_api_key` is unset, `LLM.complete()` and
  `LLM.astream()` return a deterministic stub prefixed with `STUB_PREFIX`
  that includes the user's question and a one-line setup hint. The Tutor
  detects that and substitutes its existing Socratic stub so the demo still
  reads naturally.

## Consequences

- The deployed site can return real LLM responses with a one-time, free
  signup (no credit card). Setup is documented in `BLOCKED.md` §5c.
- Smoke tests, `pytest packages/agents/tests/`, and CI still run offline —
  the stub fallback keeps every test that asserted on the Socratic opener
  ("Let's explore…", "worked example") green.
- The `groq` SDK is added to `packages/agents/pyproject.toml`. The OpenAI
  and Anthropic SDKs remain in deps for future routing experiments but are
  not called from runtime code today.
- Real per-token streaming now ships end-to-end for the Tutor; other agents
  remain on the non-streaming dispatch path until they implement
  `astream_reply`.
- Vendor lock-in risk is low: the OpenAI-compatible surface means swapping
  to another provider (Together, Cerebras, an internal vLLM, OpenRouter)
  is a base-URL + model-name change.
- Free-tier limits (≈30 RPM / 14 400 RPD as of 2026-06) are sufficient for
  the launch / demo phase. If we exceed them in production we re-evaluate.

## Alternatives considered

- **Together AI** — $5 starter credit but credit cards required after that,
  and the credit expires. Rejected for launch.
- **Cloudflare Workers AI** — requires a Cloudflare account with payment
  details on file even for the free tier. Rejected by hard constraint #2.
- **Anthropic Claude / OpenAI GPT** — best models but the owner explicitly
  refuses to pay. Rejected by hard constraint #1.
- **Self-hosted (vLLM on Fly/Render free tier)** — too heavy for the
  resource ceilings on those free tiers; cold-start latency would ruin the
  Tutor UX.
- **No provider at all (keep the stub)** — the public site already exists,
  and a hard-coded placeholder undermines every other claim in the README.
  Rejected.

## Follow-ups

- Add a second provider behind the same `LLM` surface (e.g. OpenRouter free
  models) and use `fallback_model` for cross-provider failover.
- Wire per-agent budget enforcement (`Budget.max_cost_usd`) once we have a
  pricing table for Groq.
- Promote streaming to additional agents (`Coach`, `QAExplainer`) by
  giving each its own `astream_reply`.
