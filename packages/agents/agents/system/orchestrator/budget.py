"""Orchestrator latency and cost budget."""

from __future__ import annotations

from schemas.agents import Budget

BUDGET = Budget(
    max_input_tokens=8_000,
    max_output_tokens=500,
    max_latency_ms=2_000,
    max_cost_usd=0.02,
)
