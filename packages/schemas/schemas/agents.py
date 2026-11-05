from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ._dynamic import FlexibleModel, flexible_model


class AgentName(StrEnum):
    TUTOR = "tutor"
    MENTOR = "mentor"
    COACH = "coach"
    QA_EXPLAINER = "qa_explainer"
    REVIEWER = "reviewer"
    NOTE_TAKER = "note_taker"
    ENGAGEMENT = "engagement"
    ACCESSIBILITY = "accessibility"
    ORCHESTRATOR = "orchestrator"
    CURRICULUM_DESIGNER = "curriculum_designer"
    ASSESSMENT_GENERATOR = "assessment_generator"
    GRADER = "grader"
    PROGRESS_ANALYZER = "progress_analyzer"
    CONTENT_CURATOR = "content_curator"
    RESEARCH = "research"
    KG_BUILDER = "kg_builder"
    MEMORY_STEWARD = "memory_steward"
    SAFETY_MODERATION = "safety_moderation"
    ANALYTICS_INSIGHTS = "analytics_insights"
    EVAL_AGENT = "eval_agent"


class ToolRef(FlexibleModel):
    name: str = ""
    description: str = ""
    # AS-90: fields read in production (was model_extra fallback).
    server: Any = None
    transport: str | None = None


class Budget(FlexibleModel):
    max_tokens: int | None = None
    timeout_s: float | None = None
    # Declared (AS-88): FlexibleModel.__getattr__ returns None for undeclared
    # extras, so these must be real fields for attribute reads to work.
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_latency_ms: int | None = None
    max_cost_usd: float | None = None


class AgentManifest(FlexibleModel):
    name: AgentName | str
    description: str = ""
    role: str = ""
    goal: str = ""
    tools: list[ToolRef] = Field(default_factory=list)
    budget: Budget | None = None
    # AS-90: fields read in production (was model_extra fallback).
    fallback_model: Any = None
    memory_policy: Any = None
    primary_model: Any = None
    prompt_version: str | None = None


class ChatRequest(FlexibleModel):
    learner_id: str | None = None
    session_id: str | None = None
    locale: str = "en"
    message: str | None = None
    requested_agent: AgentName | None = None


class ChatChunk(FlexibleModel):
    kind: str = "token"
    agent: AgentName | str | None = None
    text: str | None = None
    # AS-90: fields read in production (was model_extra fallback).
    citation: Any = None


class RouteDecision(FlexibleModel):
    selected_agents: list[AgentName] = Field(default_factory=lambda: [AgentName.TUTOR])
    rationale: str | None = None


def __getattr__(name: str) -> Any:
    model = flexible_model(name)
    globals()[name] = model
    return model
