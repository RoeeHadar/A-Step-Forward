"""Dispatch Phase-1 learner-facing agents from a routed turn."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from schemas.agents import AgentName, ChatChunk, ChatRequest

from agents.base.agent import AgentContext
from agents.learner_facing.coach import CoachInput
from agents.learner_facing.qa_explainer import QAExplainerInput
from agents.learner_facing.tutor import TutorInput


def _tutor_input(request: ChatRequest) -> TutorInput:
    return TutorInput(learner_id=request.learner_id, message=request.message)


def _qa_input(request: ChatRequest) -> QAExplainerInput:
    return QAExplainerInput(learner_id=request.learner_id, message=request.message)


def _coach_input(request: ChatRequest) -> CoachInput:
    return CoachInput(learner_id=request.learner_id, message=request.message)


PHASE1_INPUT_BUILDERS: dict[AgentName, Callable[[ChatRequest], Any]] = {
    AgentName.TUTOR: _tutor_input,
    AgentName.QA_EXPLAINER: _qa_input,
    AgentName.COACH: _coach_input,
}


def _tutor_reply(result: Any) -> str:
    return result.output.reply


def _qa_reply(result: Any) -> tuple[str, list[ChatChunk]]:
    chunks: list[ChatChunk] = []
    for citation in result.output.citations:
        chunks.append(
            ChatChunk(kind="citation", agent=AgentName.QA_EXPLAINER, citation=citation)
        )
    return result.output.answer, chunks


def _coach_reply(result: Any) -> str:
    return result.output.reply


async def invoke_phase1_agent(
    agent_name: AgentName,
    agent: Any,
    request: ChatRequest,
    ctx: AgentContext,
) -> list[ChatChunk]:
    builder = PHASE1_INPUT_BUILDERS[agent_name]
    result = await agent(builder(request), ctx)
    chunks: list[ChatChunk] = []

    if agent_name == AgentName.QA_EXPLAINER:
        text, citation_chunks = _qa_reply(result)
        chunks.extend(citation_chunks)
        chunks.append(ChatChunk(kind="token", agent=agent_name, text=text))
    else:
        text = _tutor_reply(result) if agent_name == AgentName.TUTOR else _coach_reply(result)
        chunks.append(ChatChunk(kind="token", agent=agent_name, text=text))

    chunks.append(ChatChunk(kind="done", agent=agent_name))
    return chunks
