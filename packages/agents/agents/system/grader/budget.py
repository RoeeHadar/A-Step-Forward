"""Grader budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=100_000,
    max_output_tokens=4_000,
    max_latency_ms=35_000,
    max_cost_usd=0.75,
)
