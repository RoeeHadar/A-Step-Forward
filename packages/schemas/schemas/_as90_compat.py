"""AS-90 r1: base-output parity for fields AS-90 declared.

AS-90 declared fields that used to live in ``model_extra``. On the base tree an
unset one was simply absent from JSON output; a declared field with a ``None``
default would now be emitted as ``null``. Production writers and routes listed
in items/AS-90/asf-coder.md call :func:`as90_unset_exclude` /
:func:`dump_base_compat` so that a field is omitted exactly when AS-90 declared
it and it was never set. Fields set explicitly (including to ``None``) and all
pre-AS-90 fields serialize exactly as before.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

# Generated: model_fields on AS-90 r0 minus model_fields on base tree 5d1d9b63.
AS90_DECLARED: dict[str, frozenset[str]] = {
    "schemas.agents.AgentManifest": frozenset(
        {"fallback_model", "memory_policy", "primary_model", "prompt_version"}
    ),
    "schemas.agents.ChatChunk": frozenset({"citation"}),
    "schemas.agents.ToolRef": frozenset({"server", "transport"}),
    "schemas.common.Citation": frozenset({"quote", "score", "source_id", "source_kind"}),
    "schemas.common.Provenance": frozenset({"id", "model"}),
    "schemas.curriculum.CourseSummary": frozenset(
        {"id", "lesson_count", "level", "summary", "title", "unit_count"}
    ),
    "schemas.curriculum.LearningPathSuggestion": frozenset({"goal_id", "learner_id", "steps"}),
    "schemas.curriculum.LessonMatch": frozenset(
        {"course_id", "lesson", "matched_concepts", "unit_id"}
    ),
    "schemas.curriculum.PathStep": frozenset({"est_minutes", "lesson_id", "reason", "title"}),
    "schemas.curriculum_seed.SeedBundle": frozenset({"source"}),
    "schemas.diagnostic.DiagnosticAnswerRequest": frozenset({"chosen", "item_id"}),
    "schemas.diagnostic.DiagnosticAnswerResponse": frozenset(
        {"complete", "question", "question_number", "results", "total_estimate"}
    ),
    "schemas.diagnostic.DiagnosticOption": frozenset({"key"}),
    "schemas.diagnostic.DiagnosticQuestion": frozenset(
        {"difficulty", "options", "stem", "subject", "topic"}
    ),
    "schemas.diagnostic.DiagnosticSessionState": frozenset(
        {
            "completed_at",
            "current_question",
            "learner_id",
            "question_idx",
            "results",
            "session_id",
            "status",
            "topics",
            "total_estimate",
        }
    ),
    "schemas.diagnostic.DiagnosticStartRequest": frozenset({"topics"}),
    "schemas.diagnostic.DiagnosticStartResponse": frozenset(
        {"question", "question_number", "session_id", "total_estimate"}
    ),
    "schemas.graph.Entity": frozenset({"confidence", "kind", "name"}),
    "schemas.graph.Extraction": frozenset(
        {"claims", "confidence", "entities", "notes", "relations"}
    ),
    "schemas.graph.KGChunk": frozenset(
        {
            "created_at",
            "document_id",
            "embedding",
            "heading",
            "ordinal",
            "provenance",
            "token_count",
        }
    ),
    "schemas.graph.KGEdge": frozenset({"dst", "id", "properties", "provenance", "src", "weight"}),
    "schemas.graph.KGHybridInput": frozenset({"depth", "k", "learner_id", "query"}),
    "schemas.graph.KGNode": frozenset(
        {
            "aliases",
            "canonical_name",
            "created_at",
            "pending_review",
            "properties",
            "provenance",
            "summary",
        }
    ),
    "schemas.graph.KGPath": frozenset({"score"}),
    "schemas.graph.KGSearchInput": frozenset({"k", "query"}),
    "schemas.graph.KGSearchResult": frozenset({"node", "score", "snippet"}),
    "schemas.graph.KGWalkInput": frozenset({"depth", "limit", "seed_node_ids"}),
    "schemas.graph.Relation": frozenset({"confidence", "dst_name", "kind", "src_name"}),
    "schemas.learner_model.AdaptiveLearnerProfile": frozenset(
        {
            "attention_span",
            "background_notes",
            "created_at",
            "goal",
            "grade_level",
            "hours_per_week",
            "points_group",
            "preferred_style",
            "self_scores",
            "subjects",
            "updated_at",
        }
    ),
    "schemas.learner_model.LearnerProfileInput": frozenset(
        {
            "attention_span",
            "background_notes",
            "goal",
            "grade_level",
            "hours_per_week",
            "points_group",
            "preferred_style",
            "self_scores",
            "subjects",
        }
    ),
    "schemas.learner_model.StudentModel": frozenset(
        {"developing", "last_active", "mastery", "profile", "strong", "weak"}
    ),
    "schemas.learners.LearnerProfile": frozenset(
        {"age", "child_mode", "clerk_user_id", "display_name", "id"}
    ),
    "schemas.learning_path.BagrutRef": frozenset({"display_name", "exam_type", "file_url", "year"}),
    "schemas.learning_path.ContentSectionRef": frozenset({"chunk_index", "page_start", "title"}),
    "schemas.learning_path.LearningPlan": frozenset(
        {"end_date", "goal", "id", "start_date", "status"}
    ),
    "schemas.learning_path.PlanConcept": frozenset(
        {"mastery", "name", "recommended_bagrut", "subject", "suggested_sections"}
    ),
    "schemas.learning_path.PlanWeek": frozenset(
        {"content_ids", "id", "plan_id", "quiz_due_at", "status"}
    ),
    "schemas.learning_path.QuizAnswerItem": frozenset({"chosen", "item_id"}),
    "schemas.learning_path.QuizOption": frozenset({"key"}),
    "schemas.learning_path.QuizQuestion": frozenset(
        {"difficulty", "id", "options", "stem", "subject", "topic"}
    ),
    "schemas.learning_path.QuizStartResponse": frozenset(
        {"plan_id", "questions", "started_at", "time_limit_s", "week_id", "week_number"}
    ),
    "schemas.learning_path.QuizSubmitRequest": frozenset({"answers"}),
    "schemas.learning_path.QuizSubmitResponse": frozenset(
        {"next_week_concepts", "per_topic", "plan_adapted", "quiz_id", "weak_concepts"}
    ),
    "schemas.learning_path.StoredQuizItem": frozenset(
        {"correct", "difficulty", "options", "source", "stem", "subject", "topic"}
    ),
    "schemas.memory.CompactionInput": frozenset({"messages", "pinned_memory_ids", "target_tokens"}),
    "schemas.memory.CompactionOutput": frozenset(
        {"compacted_summary", "estimated_tokens", "kept_verbatim_count", "messages"}
    ),
    "schemas.memory.MemoryConflict": frozenset({"existing", "incoming", "rationale", "resolution"}),
    "schemas.memory.MemoryConsolidateResult": frozenset({"merged_or_candidates"}),
    "schemas.memory.MemoryDeleteResult": frozenset({"deleted"}),
    "schemas.memory.MemoryHealthReport": frozenset(
        {
            "conflicts_pending",
            "conflicts_resolved",
            "coverage_gaps",
            "drift_notes",
            "items_archived",
            "items_merged",
            "items_promoted",
            "items_reviewed",
            "learner_id",
            "window_end",
            "window_start",
        }
    ),
    "schemas.memory.MemoryRecord": frozenset(
        {"access_count", "kg_node_ids", "superseded_at", "superseded_by"}
    ),
    "schemas.memory.MemorySearchInput": frozenset({"agent_id", "k", "min_strength"}),
    "schemas.memory.MemorySearchResult": frozenset({"components", "record", "score"}),
    "schemas.progress.KnowledgeGaps": frozenset({"gaps", "learner_id"}),
    "schemas.progress.MasteryEntry": frozenset({"concept_id", "concept_title", "score"}),
    "schemas.progress.ProgressSummary": frozenset(
        {"learner_id", "mastery", "next_review_at", "streak_days"}
    ),
    "schemas.progress.StreakInfo": frozenset({"learner_id", "next_review_at", "streak_days"}),
    "schemas.progress.UpdateMasteryResult": frozenset({"entry", "updated"}),
}


def _key(cls: type) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def as90_unset_exclude(value: Any) -> Any:
    """Nested pydantic ``exclude`` spec dropping unset AS-90-declared fields."""
    if isinstance(value, BaseModel):
        spec: dict[Any, Any] = {}
        declared = AS90_DECLARED.get(_key(type(value)), frozenset())
        for name in declared - value.model_fields_set:
            spec[name] = True
        items = dict(value.__dict__)
        items.update(value.__pydantic_extra__ or {})
        for name, child in items.items():
            if name in spec:
                continue
            sub = as90_unset_exclude(child)
            if sub:
                spec[name] = sub
        return spec or None
    if isinstance(value, (list, tuple)):
        seq = {i: s for i, item in enumerate(value) if (s := as90_unset_exclude(item))}
        return seq or None
    if isinstance(value, dict):
        mapping = {k: s for k, item in value.items() if (s := as90_unset_exclude(item))}
        return mapping or None
    return None


def dump_base_compat(value: Any, **kwargs: Any) -> Any:
    """``model_dump(mode="json")`` with unset AS-90 fields omitted (lists too)."""
    kwargs.setdefault("mode", "json")
    if isinstance(value, (list, tuple)):
        return [dump_base_compat(v, **kwargs) for v in value]
    return value.model_dump(exclude=as90_unset_exclude(value), **kwargs)
