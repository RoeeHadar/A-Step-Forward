"""Diagnostic service protocol."""

from __future__ import annotations

from typing import Protocol

from schemas.diagnostic import (
    DiagnosticAnswerRequest,
    DiagnosticAnswerResponse,
    DiagnosticSessionState,
    DiagnosticStartRequest,
    DiagnosticStartResponse,
)

from .settings import DiagnosticSettings


class DiagnosticService(Protocol):
    settings: DiagnosticSettings

    async def start(self, learner_id: str, body: DiagnosticStartRequest) -> DiagnosticStartResponse: ...
    async def answer(
        self, learner_id: str, session_id: str, body: DiagnosticAnswerRequest
    ) -> DiagnosticAnswerResponse: ...
    async def get_session(self, learner_id: str, session_id: str) -> DiagnosticSessionState: ...


_service: DiagnosticService | None = None


def get_diagnostic_service() -> DiagnosticService:
    global _service
    if _service is None:
        from .postgres_service import PostgresDiagnosticService

        _service = PostgresDiagnosticService()
    return _service
