"""Coach agent budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=60_000,
    max_output_tokens=2_500,
    max_latency_ms=15_000,
    max_cost_usd=0.30,
)
