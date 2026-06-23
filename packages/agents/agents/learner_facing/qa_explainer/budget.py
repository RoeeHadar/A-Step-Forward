"""Q&A Explainer budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=80_000,
    max_output_tokens=3_000,
    max_latency_ms=20_000,
    max_cost_usd=0.35,
)
