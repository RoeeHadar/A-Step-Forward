"""Assessment generation and grading routes."""

from __future__ import annotations

import json
import re
from typing import Literal

from agents.base.agent_helpers import is_stub_llm_response
from agents.base.llm import LLM, LLMRequest
from agents.base.llm_settings import get_llm_settings
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from ..core.auth import AuthCtx, require_learner
from ..core.rate_limit import per_user

router = APIRouter(prefix="/v1", tags=["assessment"])


class QuestionModel(BaseModel):
    id: str
    question: str
    type: Literal["multiple_choice", "open"]
    options: list[str] | None = None
    answer_key: str | None = None


class GradeRequest(BaseModel):
    question: str
    answer: str


class GradeResponse(BaseModel):
    correct: bool
    score: float = Field(ge=0.0, le=1.0)
    feedback: str


def _get_llm() -> LLM:
    settings = get_llm_settings()
    return LLM(model=settings.llm_default_model or "llama-3.3-70b-versatile")


def _extract_json_array(text: str) -> list | None:
    """Best-effort JSON array extraction from model text."""
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


def _fallback_questions(topic: str, level: str) -> list[QuestionModel]:
    """Hardcoded fallback when LLM output cannot be parsed."""
    return [
        QuestionModel(
            id="q1",
            question=f"What is a core concept in {topic} at the {level} level?",
            type="multiple_choice",
            options=[
                f"A fundamental principle of {topic}",
                "An unrelated historical event",
                "A random vocabulary word",
                "None of the above",
            ],
            answer_key=f"A fundamental principle of {topic}",
        ),
        QuestionModel(
            id="q2",
            question=f"Explain one key idea about {topic} in your own words.",
            type="open",
            answer_key=f"A clear explanation of a {level}-level concept in {topic}.",
        ),
        QuestionModel(
            id="q3",
            question=f"Which statement best describes {topic}?",
            type="multiple_choice",
            options=[
                f"It relates to understanding {topic} systematically",
                "It has no practical applications",
                "It is only memorization with no reasoning",
                "It cannot be learned at any level",
            ],
            answer_key=f"It relates to understanding {topic} systematically",
        ),
    ]


def _parse_questions(raw: list, topic: str, level: str) -> list[QuestionModel]:
    questions: list[QuestionModel] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        q_id = str(item.get("id") or f"q{idx + 1}")
        question_text = str(item.get("question") or "").strip()
        if not question_text:
            continue
        q_type = item.get("type", "open")
        if q_type not in ("multiple_choice", "open"):
            q_type = "open"
        options = item.get("options")
        if q_type == "multiple_choice" and not isinstance(options, list):
            options = None
        answer_key = item.get("answer_key")
        if answer_key is not None:
            answer_key = str(answer_key)
        questions.append(
            QuestionModel(
                id=q_id,
                question=question_text,
                type=q_type,  # type: ignore[arg-type]
                options=options,
                answer_key=answer_key,
            )
        )
    if not questions:
        return _fallback_questions(topic, level)
    return questions


@router.get("/assessment", response_model=list[QuestionModel])
async def get_assessment(
    topic: str = Query(..., min_length=1),
    level: Literal["beginner", "intermediate", "advanced"] = Query(...),
    ctx: AuthCtx = Depends(require_learner),
    llm: LLM = Depends(_get_llm),
    _=Depends(per_user("assessment.get", per_min=20)),
) -> list[QuestionModel]:
    _ = ctx
    system = (
        "You are an educational assessment generator. "
        f"Create {level} level questions about {topic}. "
        "Return ONLY a valid JSON array of 3-5 question objects. "
        "Each object must have: id (string), question (string), "
        'type ("multiple_choice" or "open"). '
        "For multiple_choice, include options (array of 4 strings) and answer_key (string). "
        "For open questions, include answer_key (string) as a model answer. "
        "Do not wrap the JSON in markdown code fences."
    )
    response = await llm.complete(
        LLMRequest(
            system=system,
            messages=[{"role": "user", "content": f"Generate assessment questions about {topic}."}],
            temperature=0.3,
            metadata={"trace_name": "assessment:generate"},
        )
    )

    if is_stub_llm_response(response):
        return _fallback_questions(topic, level)

    raw = _extract_json_array(response.text)
    if raw is None:
        return _fallback_questions(topic, level)

    return _parse_questions(raw, topic, level)


@router.post("/grade", response_model=GradeResponse)
async def grade_answer(
    body: GradeRequest,
    ctx: AuthCtx = Depends(require_learner),
    llm: LLM = Depends(_get_llm),
    _=Depends(per_user("assessment.grade", per_min=30)),
) -> GradeResponse:
    _ = ctx
    system = (
        "You are an educational grader. Evaluate the learner's answer against the question. "
        "Return ONLY a valid JSON object with: "
        'correct (boolean), score (number 0.0-1.0), feedback (string with brief explanation). '
        "Do not wrap the JSON in markdown code fences."
    )
    user_content = (
        f"Question: {body.question}\n"
        f"Learner answer: {body.answer}\n"
        "Grade this answer."
    )
    response = await llm.complete(
        LLMRequest(
            system=system,
            messages=[{"role": "user", "content": user_content}],
            temperature=0.2,
            metadata={"trace_name": "assessment:grade"},
        )
    )

    fallback = GradeResponse(
        correct=False,
        score=0.0,
        feedback="Unable to evaluate. Please try again.",
    )

    if is_stub_llm_response(response):
        return fallback

    text = response.text.strip()
    payload: dict | None = None
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            pass
    if payload is None:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    payload = parsed
            except json.JSONDecodeError:
                return fallback

    if payload is None:
        return fallback

    try:
        score = float(payload.get("score", 0.0))
        score = max(0.0, min(1.0, score))
        return GradeResponse(
            correct=bool(payload.get("correct", False)),
            score=score,
            feedback=str(payload.get("feedback") or fallback.feedback),
        )
    except (TypeError, ValueError):
        return fallback
