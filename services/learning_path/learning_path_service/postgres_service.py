"""Postgres-backed learning path service."""

from __future__ import annotations

from learner_model_service.api import get_learner_model_service
from schemas.learning_path import PlanConcept, QuizAnswerItem, QuizStartResponse, QuizSubmitResponse
from schemas.errors import ValidationFailed

from .engine import build_week_concept_groups, collect_weak_worklist, infer_subject
from .settings import LearningPathSettings
from .stores.database import session_scope
from .stores.repository import LearningPathRepository


class PostgresLearningPathService:
    def __init__(self, settings: LearningPathSettings | None = None) -> None:
        self.settings = settings or LearningPathSettings()
        self.repo = LearningPathRepository(self.settings)

    async def _prerequisite_map(self, concept_ids: set[str]) -> dict[str, list[str]]:
        learner_model = get_learner_model_service()
        prereq_map: dict[str, list[str]] = {}
        for concept_id in concept_ids:
            direct = await learner_model.get_prerequisites(concept_id)
            prereq_map[concept_id] = direct
        return prereq_map

    async def _enrich_week(self, concept_ids: list[str], student) -> list[PlanConcept]:
        subjects = student.profile.subjects if student.profile else []
        mastery = student.mastery
        enriched: list[PlanConcept] = []
        for concept_id in concept_ids:
            subject = infer_subject(concept_id, subjects)
            sections = await self.repo.find_sections(subject)
            bagrut = await self.repo.find_bagrut(subject)
            enriched.append(
                PlanConcept(
                    concept_id=concept_id,
                    name=concept_id.replace("_", " ").replace("-", " ").title(),
                    subject=subject,
                    mastery=mastery.get(concept_id),
                    suggested_sections=sections,
                    recommended_bagrut=bagrut,
                )
            )
        return enriched

    async def generate_plan(self, learner_id: str):
        from schemas.learning_path import LearningPlan

        learner_model = get_learner_model_service()
        student = await learner_model.get_student_model(learner_id)
        if student.profile is None:
            raise ValidationFailed("Complete onboarding before generating a learning plan")

        seed_worklist = collect_weak_worklist(student, {})
        prereq_map = await self._prerequisite_map(seed_worklist)
        # Expand map for any prerequisites discovered in the first pass.
        expanded = collect_weak_worklist(student, prereq_map)
        for concept_id in expanded:
            if concept_id not in prereq_map:
                prereq_map[concept_id] = await learner_model.get_prerequisites(concept_id)

        week_id_groups = build_week_concept_groups(student, prereq_map)
        week_groups = [await self._enrich_week(week, student) for week in week_id_groups]
        goal = student.profile.goal
        return await self.repo.replace_plan(learner_id, goal, week_groups)

    async def get_current_plan(self, learner_id: str):
        return await self.repo.get_current_plan(learner_id)

    async def get_week(self, learner_id: str, plan_id: str, week_number: int):
        return await self.repo.get_week(plan_id, week_number, learner_id)

    async def start_quiz(
        self, learner_id: str, plan_id: str, week_number: int
    ) -> QuizStartResponse:
        from .quiz_generator import build_quiz_items
        from .stores.quiz_repository import QuizRepository

        async with session_scope(self.settings) as session:
            week = await self.repo._get_week(session, plan_id, week_number, learner_id)
            concept_ids = [c.concept_id for c in week.concepts]
            subjects = list({c.subject for c in week.concepts})
            subject = subjects[0] if subjects else "math"
            items = await build_quiz_items(session, concept_ids, subject)
            quiz_repo = QuizRepository(session)
            result = await quiz_repo.start_quiz(
                learner_id=learner_id,
                plan_id=plan_id,
                week_num=week_number,
                items=items,
            )
            await session.commit()
            return result

    async def submit_quiz(
        self, learner_id: str, quiz_id: str, answers: list[QuizAnswerItem]
    ) -> QuizSubmitResponse:
        from .stores.quiz_repository import QuizRepository

        async with session_scope(self.settings) as session:
            quiz_repo = QuizRepository(session)
            result = await quiz_repo.submit_quiz(
                quiz_id=quiz_id,
                learner_id=learner_id,
                answers=answers,
                svc=self,
            )
            await session.commit()
            return result
