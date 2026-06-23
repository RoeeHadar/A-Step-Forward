"""Assessment Generator budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=80_000,
    max_output_tokens=5_000,
    max_latency_ms=30_000,
    max_cost_usd=0.60,
)
