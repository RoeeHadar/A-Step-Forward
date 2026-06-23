"""Curriculum Designer budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=120_000,
    max_output_tokens=6_000,
    max_latency_ms=45_000,
    max_cost_usd=1.00,
)
