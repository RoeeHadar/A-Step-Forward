"""Dispatch registered runtime agents from a routed turn."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from schemas.agents import AgentName, ChatChunk, ChatRequest

from agents.base.agent import AgentContext
from agents.learner_facing.coach import CoachInput
from agents.learner_facing.qa_explainer import QAExplainerInput
from agents.learner_facing.tutor import TutorInput
from agents.system.assessment_generator import AssessmentGeneratorInput
from agents.system.content_curator import ContentCuratorInput
from agents.system.curriculum_designer import CurriculumDesignerInput
from agents.system.grader import GraderInput
from agents.system.kg_builder import KGBuilderInput
from agents.system.progress_analyzer import ProgressAnalyzerInput
from agents.system.research import ResearchInput


@dataclass(frozen=True)
class AgentDispatch:
    build_input: Callable[[ChatRequest], Any]
    format_chunks: Callable[[Any], list[ChatChunk]]


def _token(agent: AgentName, text: str) -> list[ChatChunk]:
    return [ChatChunk(kind="token", agent=agent, text=text)]


def _qa_chunks(result: Any) -> list[ChatChunk]:
    chunks: list[ChatChunk] = []
    for citation in result.output.citations:
        chunks.append(ChatChunk(kind="citation", agent=AgentName.QA_EXPLAINER, citation=citation))
    chunks.append(ChatChunk(kind="token", agent=AgentName.QA_EXPLAINER, text=result.output.answer))
    return chunks


def _research_chunks(result: Any) -> list[ChatChunk]:
    chunks: list[ChatChunk] = []
    for citation in result.output.citations:
        chunks.append(ChatChunk(kind="citation", agent=AgentName.RESEARCH, citation=citation))
    chunks.append(ChatChunk(kind="token", agent=AgentName.RESEARCH, text=result.output.report))
    return chunks


AGENT_DISPATCH: dict[AgentName, AgentDispatch] = {
    AgentName.TUTOR: AgentDispatch(
        build_input=lambda r: TutorInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.TUTOR, result.output.reply),
    ),
    AgentName.QA_EXPLAINER: AgentDispatch(
        build_input=lambda r: QAExplainerInput(learner_id=r.learner_id, message=r.message),
        format_chunks=_qa_chunks,
    ),
    AgentName.COACH: AgentDispatch(
        build_input=lambda r: CoachInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.COACH, result.output.reply),
    ),
    AgentName.CURRICULUM_DESIGNER: AgentDispatch(
        build_input=lambda r: CurriculumDesignerInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.CURRICULUM_DESIGNER, result.output.reply),
    ),
    AgentName.ASSESSMENT_GENERATOR: AgentDispatch(
        build_input=lambda r: AssessmentGeneratorInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.ASSESSMENT_GENERATOR, result.output.reply),
    ),
    AgentName.GRADER: AgentDispatch(
        build_input=lambda r: GraderInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.GRADER, result.output.reply),
    ),
    AgentName.PROGRESS_ANALYZER: AgentDispatch(
        build_input=lambda r: ProgressAnalyzerInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.PROGRESS_ANALYZER, result.output.reply),
    ),
    AgentName.RESEARCH: AgentDispatch(
        build_input=lambda r: ResearchInput(learner_id=r.learner_id, message=r.message),
        format_chunks=_research_chunks,
    ),
    AgentName.CONTENT_CURATOR: AgentDispatch(
        build_input=lambda r: ContentCuratorInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.CONTENT_CURATOR, result.output.reply),
    ),
    AgentName.KG_BUILDER: AgentDispatch(
        build_input=lambda r: KGBuilderInput(learner_id=r.learner_id, message=r.message),
        format_chunks=lambda result: _token(AgentName.KG_BUILDER, result.output.reply),
    ),
}


async def invoke_registered_agent(
    agent_name: AgentName,
    agent: Any,
    request: ChatRequest,
    ctx: AgentContext,
) -> list[ChatChunk]:
    dispatch = AGENT_DISPATCH[agent_name]
    result = await agent(dispatch.build_input(request), ctx)
    chunks = dispatch.format_chunks(result)
    chunks.append(ChatChunk(kind="done", agent=agent_name))
    return chunks
