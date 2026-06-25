"""Quiz persistence: weekly_quizzes CRUD + concept mastery updates."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.learning_path import (
    QuizAnswerItem,
    QuizQuestion,
    QuizStartResponse,
    QuizSubmitResponse,
    StoredQuizItem,
)
from schemas.errors import NotFoundError

from .models import PlanWeekRow, WeeklyQuizRow

ADAPT_WEAK_THRESHOLD = 0.4
ADAPT_TRIGGER_MIN = 2  # adapt next week if this many concepts score below threshold
DEFAULT_TIME_LIMIT_S = 30 * 60  # 30 minutes


def _score_answers(
    items: list[StoredQuizItem],
    answers: list[QuizAnswerItem],
) -> tuple[float, dict[str, float], list[str]]:
    """Return (overall_score, per_topic_score, weak_concepts)."""
    answer_map = {a.item_id: a.chosen.upper() for a in answers}
    topic_correct: dict[str, int] = {}
    topic_total: dict[str, int] = {}

    for item in items:
        topic_total[item.topic] = topic_total.get(item.topic, 0) + 1
        if answer_map.get(item.id, "").upper() == item.correct.upper():
            topic_correct[item.topic] = topic_correct.get(item.topic, 0) + 1

    per_topic: dict[str, float] = {}
    for topic, total in topic_total.items():
        correct = topic_correct.get(topic, 0)
        per_topic[topic] = round(correct / total, 4) if total > 0 else 0.0

    answered = sum(1 for a in answers if a.item_id in {i.id for i in items})
    correct_total = sum(topic_correct.values())
    overall = round(correct_total / len(items), 4) if items else 0.0

    weak = [topic for topic, score in per_topic.items() if score < ADAPT_WEAK_THRESHOLD]
    return overall, per_topic, weak


class QuizRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def start_quiz(
        self,
        *,
        learner_id: str,
        plan_id: str,
        week_num: int,
        items: list[StoredQuizItem],
    ) -> QuizStartResponse:
        """Create (or return existing) a WeeklyQuizRow for this week."""
        plan_uuid = UUID(plan_id)

        # Find the PlanWeekRow
        week_result = await self._session.execute(
            select(PlanWeekRow).where(
                PlanWeekRow.plan_id == plan_uuid,
                PlanWeekRow.week_number == week_num,
            )
        )
        week_row = week_result.scalar_one_or_none()
        if week_row is None:
            raise NotFoundError(f"Week {week_num} not found in plan {plan_id}")

        # Return existing quiz if pending/active
        quiz_result = await self._session.execute(
            select(WeeklyQuizRow).where(
                WeeklyQuizRow.week_id == week_row.id,
                WeeklyQuizRow.learner_id == learner_id,
                WeeklyQuizRow.status.in_(["pending", "started"]),
            )
        )
        existing = quiz_result.scalar_one_or_none()

        now = datetime.now(tz=timezone.utc)
        if existing is not None:
            stored_items = [StoredQuizItem.model_validate(i) for i in existing.items]
        else:
            existing = WeeklyQuizRow(
                week_id=week_row.id,
                learner_id=learner_id,
                items=[i.model_dump() for i in items],
                time_limit_s=DEFAULT_TIME_LIMIT_S,
                started_at=now,
                status="started",
            )
            self._session.add(existing)
            await self._session.flush()
            stored_items = items

        client_questions = [
            QuizQuestion(
                id=i.id,
                topic=i.topic,
                subject=i.subject,
                difficulty=i.difficulty,
                stem=i.stem,
                options=i.options,
            )
            for i in stored_items
        ]

        return QuizStartResponse(
            quiz_id=str(existing.id),
            week_id=str(week_row.id),
            plan_id=plan_id,
            week_number=week_num,
            time_limit_s=existing.time_limit_s,
            questions=client_questions,
            started_at=existing.started_at or now,
        )

    async def submit_quiz(
        self,
        *,
        quiz_id: str,
        learner_id: str,
        answers: list[QuizAnswerItem],
        svc,  # PostgresLearningPathService — to trigger plan adaptation
    ) -> QuizSubmitResponse:
        quiz_uuid = UUID(quiz_id)
        quiz_result = await self._session.execute(
            select(WeeklyQuizRow).where(
                WeeklyQuizRow.id == quiz_uuid,
                WeeklyQuizRow.learner_id == learner_id,
            )
        )
        quiz_row = quiz_result.scalar_one_or_none()
        if quiz_row is None:
            raise NotFoundError("Quiz not found")
        if quiz_row.status == "submitted":
            # Idempotent — return stored result
            return QuizSubmitResponse(
                quiz_id=quiz_id,
                score=float(quiz_row.score or 0),
                per_topic=quiz_row.per_topic or {},
                weak_concepts=list((quiz_row.per_topic or {}).keys()),
                plan_adapted=False,
            )

        stored_items = [StoredQuizItem.model_validate(i) for i in quiz_row.items]
        overall, per_topic, weak_concepts = _score_answers(stored_items, answers)

        quiz_row.submitted_at = datetime.now(tz=timezone.utc)
        quiz_row.score = overall  # type: ignore[assignment]
        quiz_row.per_topic = per_topic
        quiz_row.status = "submitted"
        await self._session.flush()

        # Update concept_mastery for each topic answered
        for topic, score in per_topic.items():
            await self._session.execute(
                text(
                    """
                    INSERT INTO concept_mastery (learner_id, concept_id, score, updated_at)
                    VALUES (:lid, :cid, :score, NOW())
                    ON CONFLICT (learner_id, concept_id)
                    DO UPDATE SET score = EXCLUDED.score, updated_at = NOW()
                    """
                ),
                {"lid": learner_id, "cid": topic, "score": score},
            )

        # Update learner_profiles weak/strong lists
        all_concepts = list(per_topic.keys())
        strong = [c for c in all_concepts if per_topic.get(c, 0) >= ADAPT_WEAK_THRESHOLD]
        await self._session.execute(
            text(
                """
                UPDATE learner_profiles
                SET weak_concepts = :weak, strong_concepts = :strong, updated_at = NOW()
                WHERE learner_id = :lid
                """
            ),
            {"weak": weak_concepts, "strong": strong, "lid": learner_id},
        )
        await self._session.flush()

        # Adapt plan if enough weak concepts remain
        plan_adapted = False
        next_week_concepts: list[str] | None = None
        if len(weak_concepts) > ADAPT_TRIGGER_MIN:
            try:
                new_plan = await svc.generate_plan(learner_id)
                plan_adapted = True
                # Surface concepts from the first week of the new plan
                if new_plan.weeks:
                    next_week_concepts = [c.concept_id for c in new_plan.weeks[0].concepts]
            except Exception:
                pass

        return QuizSubmitResponse(
            quiz_id=quiz_id,
            score=overall,
            per_topic=per_topic,
            weak_concepts=weak_concepts,
            plan_adapted=plan_adapted,
            next_week_concepts=next_week_concepts,
        )
