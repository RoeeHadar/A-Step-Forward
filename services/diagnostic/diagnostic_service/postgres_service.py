"""Postgres-backed diagnostic service."""

from __future__ import annotations

from datetime import datetime, timezone

from learner_model_service.api import get_learner_model_service
from schemas.diagnostic import (
    DiagnosticAnswerRequest,
    DiagnosticAnswerResponse,
    DiagnosticSessionState,
    DiagnosticStartRequest,
    DiagnosticStartResponse,
)
from schemas.errors import ValidationFailed

from .engine import (
    QUESTIONS_TARGET,
    START_DIFFICULTY,
    Response,
    estimate_mastery_by_topic,
    next_difficulty,
    should_stop,
)
from .settings import DiagnosticSettings
from .stores.repository import DiagnosticRepository


class PostgresDiagnosticService:
    def __init__(self, settings: DiagnosticSettings | None = None) -> None:
        self.settings = settings or DiagnosticSettings()
        self.repo = DiagnosticRepository(self.settings)

    async def _resolve_topics(self, learner_id: str, requested: list[str]) -> list[str]:
        if requested:
            return requested
        profile = await get_learner_model_service().get_profile(learner_id)
        if profile and profile.self_scores:
            return list(profile.self_scores.keys())
        if profile and profile.subjects:
            return profile.subjects
        raise ValidationFailed("Provide topics or complete onboarding first")

    async def start(self, learner_id: str, body: DiagnosticStartRequest) -> DiagnosticStartResponse:
        topics = await self._resolve_topics(learner_id, body.topics)
        session = await self.repo.create_session(learner_id, topics)
        difficulty = START_DIFFICULTY
        item = await self.repo.pick_question(topics=topics, difficulty=difficulty, exclude_ids=set())
        question = self.repo.item_to_question(item)
        session.question_idx = 1
        session.results = {
            "responses": [],
            "current_difficulty": difficulty,
            "current_item_id": question.id,
        }
        await self.repo.save_session(session)
        return DiagnosticStartResponse(
            session_id=str(session.id),
            question=question,
            question_number=1,
            total_estimate=QUESTIONS_TARGET,
        )

    async def answer(
        self, learner_id: str, session_id: str, body: DiagnosticAnswerRequest
    ) -> DiagnosticAnswerResponse:
        session = await self.repo.get_session(session_id, learner_id=learner_id)
        if session.status != "active":
            raise ValidationFailed("Diagnostic session is already complete")

        item = await self.repo.get_item(body.item_id)
        options = self.repo.item_to_question(item).options
        correct_key = self._correct_key(item.options, options)
        was_correct = body.chosen.strip().upper() == correct_key

        results = dict(session.results or {})
        responses = self.repo.responses_from_row(session)
        current_difficulty = float(results.get("current_difficulty", START_DIFFICULTY))
        responses.append(
            Response(
                item_id=body.item_id,
                topic=item.topic,
                difficulty=float(item.difficulty),
                correct=was_correct,
                chosen=body.chosen,
            )
        )
        new_difficulty = next_difficulty(current_difficulty, was_correct)
        results["responses"] = [
            {
                "item_id": r.item_id,
                "topic": r.topic,
                "difficulty": r.difficulty,
                "correct": r.correct,
                "chosen": r.chosen,
            }
            for r in responses
        ]
        results["current_difficulty"] = new_difficulty

        if should_stop(responses):
            mastery_by_topic = estimate_mastery_by_topic(responses)
            results["mastery_by_topic"] = mastery_by_topic
            session.status = "complete"
            session.completed_at = datetime.now(timezone.utc)
            session.results = results
            session.question_idx = len(responses)
            await self.repo.save_session(session)

            learner_svc = get_learner_model_service()
            for topic, score in mastery_by_topic.items():
                await learner_svc.upsert_mastery(learner_id, topic, score, data_points=len(responses))

            return DiagnosticAnswerResponse(
                complete=True,
                question_number=len(responses),
                total_estimate=QUESTIONS_TARGET,
                results={"mastery_by_topic": mastery_by_topic, "responses": results["responses"]},
            )

        exclude = {r.item_id for r in responses}
        next_item = await self.repo.pick_question(
            topics=list(session.topics),
            difficulty=new_difficulty,
            exclude_ids=exclude,
        )
        question = self.repo.item_to_question(next_item)
        results["current_item_id"] = question.id
        session.question_idx = len(responses) + 1
        session.results = results
        await self.repo.save_session(session)

        return DiagnosticAnswerResponse(
            complete=False,
            question=question,
            question_number=len(responses) + 1,
            total_estimate=QUESTIONS_TARGET,
        )

    async def get_session(self, learner_id: str, session_id: str) -> DiagnosticSessionState:
        session = await self.repo.get_session(session_id, learner_id=learner_id)
        results = session.results or {}
        current_question = None
        item_id = results.get("current_item_id")
        if session.status == "active" and item_id:
            item = await self.repo.get_item(str(item_id))
            current_question = self.repo.item_to_question(item)
        return DiagnosticSessionState(
            session_id=str(session.id),
            learner_id=session.learner_id,
            status=session.status,
            topics=list(session.topics),
            question_idx=session.question_idx,
            total_estimate=QUESTIONS_TARGET,
            current_question=current_question,
            results=results if session.status == "complete" else None,
            completed_at=session.completed_at,
        )

    def _correct_key(self, raw_options: dict, parsed_options: list) -> str:
        if isinstance(raw_options, dict):
            if "correct" in raw_options:
                return str(raw_options["correct"]).strip().upper()
            if "answer" in raw_options:
                return str(raw_options["answer"]).strip().upper()
        return parsed_options[0].key if parsed_options else "A"
