"""Agent-related shared schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ._compat import StrEnum
from .common import Citation, IDStr
from .memory import MemoryAccessPolicy


class AgentName(StrEnum):
    # Learner-facing
    TUTOR = "tutor"
    MENTOR = "mentor"
    COACH = "coach"
    QA_EXPLAINER = "qa_explainer"
    REVIEWER = "reviewer"
    NOTE_TAKER = "note_taker"
    ENGAGEMENT = "engagement"
    ACCESSIBILITY = "accessibility"
    # System
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
    EVAL_AGENT = "eval_agent"
    ANALYTICS_INSIGHTS = "analytics_insights"


class Budget(BaseModel):
    """Per-agent budget."""

    max_input_tokens: int = 100_000
    max_output_tokens: int = 4_000
    max_latency_ms: int = 30_000
    max_cost_usd: float = 0.50


class ToolRef(BaseModel):
    """Reference to an MCP tool (or local function tool)."""

    transport: Literal["mcp", "local"] = "mcp"
    server: str | None = None  # for mcp
    name: str


class AgentManifest(BaseModel):
    """Static description of an agent — used for routing and docs."""

    name: AgentName
    description: str
    prompt_version: str
    primary_model: str
    fallback_model: str | None = None
    tools: list[ToolRef] = Field(default_factory=list)
    memory_policy: MemoryAccessPolicy
    budget: Budget = Field(default_factory=Budget)


class ChatRequest(BaseModel):
    learner_id: IDStr
    message: str
    requested_agent: AgentName | None = None
    session_id: IDStr | None = None
    locale: str = "en"


class ChatChunk(BaseModel):
    """A single SSE chunk going back to the client."""

    kind: Literal["token", "tool_call", "tool_result", "citation", "done", "error"]
    agent: AgentName | None = None
    text: str | None = None
    citation: Citation | None = None
    tool: str | None = None
    payload: dict | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RouteDecision(BaseModel):
    """Output of the Orchestrator's Router."""

    selected_agents: list[AgentName]
    rationale: str
    parallel: bool = False
