"""Diagnostic persistence and item selection."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from schemas.diagnostic import DiagnosticOption, DiagnosticQuestion
from schemas.errors import NotFoundError, ValidationFailed

from ..engine import QUESTIONS_TARGET, START_DIFFICULTY, Response
from ..settings import DiagnosticSettings
from .database import session_scope
from .models import DiagnosticItemRow, DiagnosticSessionRow


def _parse_options(raw: dict[str, Any] | list[Any]) -> list[DiagnosticOption]:
    if isinstance(raw, list):
        return [
            DiagnosticOption(key=str(item.get("key", chr(65 + i))), text=str(item.get("text", item)))
            if isinstance(item, dict)
            else DiagnosticOption(key=chr(65 + i), text=str(item))
            for i, item in enumerate(raw)
        ]
    if isinstance(raw, dict):
        if "choices" in raw and isinstance(raw["choices"], list):
            correct = raw.get("correct")
            return [
                DiagnosticOption(key=chr(65 + i), text=str(choice))
                for i, choice in enumerate(raw["choices"])
            ]
        return [DiagnosticOption(key=str(k), text=str(v)) for k, v in raw.items()]
    return []


def _item_to_question(row: DiagnosticItemRow) -> DiagnosticQuestion:
    return DiagnosticQuestion(
        id=str(row.id),
        topic=row.topic,
        subject=row.subject,
        difficulty=float(row.difficulty),
        stem=row.stem,
        options=_parse_options(row.options),
    )


def _responses_from_results(results: dict[str, Any] | None) -> list[Response]:
    if not results:
        return []
    raw = results.get("responses", [])
    return [
        Response(
            item_id=str(item["item_id"]),
            topic=str(item["topic"]),
            difficulty=float(item["difficulty"]),
            correct=bool(item["correct"]),
            chosen=str(item.get("chosen", "")),
        )
        for item in raw
    ]


class DiagnosticRepository:
    def __init__(
        self,
        settings: DiagnosticSettings,
        *,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.settings = settings
        self._external_session = session
        from .database import get_session_factory

        self._session_factory = session_factory or get_session_factory(settings)

    async def create_session(self, learner_id: str, topics: list[str]) -> DiagnosticSessionRow:
        if self._external_session is not None:
            return await self._create_session(self._external_session, learner_id, topics)
        async with session_scope(self.settings) as session:
            row = await self._create_session(session, learner_id, topics)
            await session.commit()
            return row

    async def _create_session(
        self, session: AsyncSession, learner_id: str, topics: list[str]
    ) -> DiagnosticSessionRow:
        row = DiagnosticSessionRow(
            learner_id=learner_id,
            status="active",
            topics=topics,
            question_idx=0,
            results={"responses": [], "current_difficulty": START_DIFFICULTY},
        )
        session.add(row)
        await session.flush()
        return row

    async def get_session(self, session_id: str, *, learner_id: str | None = None) -> DiagnosticSessionRow:
        if self._external_session is not None:
            return await self._get_session(self._external_session, session_id, learner_id=learner_id)
        async with session_scope(self.settings) as session:
            return await self._get_session(session, session_id, learner_id=learner_id)

    async def _get_session(
        self, session: AsyncSession, session_id: str, *, learner_id: str | None = None
    ) -> DiagnosticSessionRow:
        try:
            sid = UUID(session_id)
        except ValueError as exc:
            raise NotFoundError(f"invalid session id: {session_id}") from exc
        result = await session.execute(select(DiagnosticSessionRow).where(DiagnosticSessionRow.id == sid))
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(f"diagnostic session not found: {session_id}")
        if learner_id is not None and row.learner_id != learner_id:
            raise NotFoundError(f"diagnostic session not found: {session_id}")
        return row

    async def pick_question(
        self,
        *,
        topics: list[str],
        difficulty: float,
        exclude_ids: set[str],
    ) -> DiagnosticItemRow:
        if self._external_session is not None:
            return await self._pick_question(
                self._external_session, topics=topics, difficulty=difficulty, exclude_ids=exclude_ids
            )
        async with session_scope(self.settings) as session:
            return await self._pick_question(
                session, topics=topics, difficulty=difficulty, exclude_ids=exclude_ids
            )

    async def _pick_question(
        self,
        session: AsyncSession,
        *,
        topics: list[str],
        difficulty: float,
        exclude_ids: set[str],
    ) -> DiagnosticItemRow:
        lo = max(1.0, difficulty - 1.5)
        hi = min(10.0, difficulty + 1.5)
        stmt = (
            select(DiagnosticItemRow)
            .where(
                and_(
                    DiagnosticItemRow.topic.in_(topics),
                    DiagnosticItemRow.difficulty >= lo,
                    DiagnosticItemRow.difficulty <= hi,
                )
            )
            .order_by(func.abs(DiagnosticItemRow.difficulty - difficulty))
            .limit(20)
        )
        result = await session.execute(stmt)
        candidates = [row for row in result.scalars().all() if str(row.id) not in exclude_ids]
        if not candidates:
            fallback = await session.execute(
                select(DiagnosticItemRow)
                .where(DiagnosticItemRow.topic.in_(topics))
                .order_by(func.random())
                .limit(20)
            )
            candidates = [row for row in fallback.scalars().all() if str(row.id) not in exclude_ids]
        if not candidates:
            raise ValidationFailed("No diagnostic items available for the selected topics")
        return candidates[0]

    async def get_item(self, item_id: str) -> DiagnosticItemRow:
        if self._external_session is not None:
            return await self._get_item(self._external_session, item_id)
        async with session_scope(self.settings) as session:
            return await self._get_item(session, item_id)

    async def _get_item(self, session: AsyncSession, item_id: str) -> DiagnosticItemRow:
        try:
            iid = UUID(item_id)
        except ValueError as exc:
            raise NotFoundError(f"invalid item id: {item_id}") from exc
        result = await session.execute(select(DiagnosticItemRow).where(DiagnosticItemRow.id == iid))
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(f"diagnostic item not found: {item_id}")
        return row

    async def save_session(self, row: DiagnosticSessionRow) -> None:
        if self._external_session is not None:
            await self._external_session.merge(row)
            await self._external_session.commit()
            return
        async with session_scope(self.settings) as session:
            await session.merge(row)
            await session.commit()

    def item_to_question(self, row: DiagnosticItemRow) -> DiagnosticQuestion:
        return _item_to_question(row)

    def responses_from_row(self, row: DiagnosticSessionRow) -> list[Response]:
        return _responses_from_results(row.results)
