"""Research agent budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=200_000,
    max_output_tokens=8_000,
    max_latency_ms=90_000,
    max_cost_usd=2.0,
)
