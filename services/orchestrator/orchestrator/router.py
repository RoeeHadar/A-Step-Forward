"""Declarative router — re-exported from the agents package.

The routing policy lives in `packages/agents/agents/system/orchestrator/router.py`
so it can be unit-tested and eval'd without pulling in the LangGraph runner.
"""

from __future__ import annotations

from dataclasses import dataclass

from schemas.agents import ChatRequest, RouteDecision

from agents.system.orchestrator import DeclarativeRouter, OrchestratorInput


@dataclass
class RoutedTurn:
    request: ChatRequest
    decision: RouteDecision


class Router:
    def __init__(self) -> None:
        self._inner = DeclarativeRouter()

    def route(self, request: ChatRequest) -> RoutedTurn:
        decision = self._inner.route(
            OrchestratorInput(
                learner_id=request.learner_id,
                message=request.message,
                requested_agent=request.requested_agent,
                session_id=request.session_id,
                locale=request.locale,
            )
        )
        return RoutedTurn(request=request, decision=decision)
