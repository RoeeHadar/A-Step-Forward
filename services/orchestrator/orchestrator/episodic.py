"""Episodic memory persistence for completed orchestrator chat turns."""

from __future__ import annotations

import logging

from memory_service.api import MemoryService
from schemas.agents import AgentName, ChatChunk, ChatRequest
from schemas.common import Provenance
from schemas.memory import MemoryType, MemoryWriteInput

from agents.base.agent import AgentContext

logger = logging.getLogger(__name__)

_MAX_CONTENT_LEN = 20_000


def build_episodic_content(*, user_message: str, agent: AgentName, response: str) -> str:
    content = f"User: {user_message}\n\nAgent ({agent.value}): {response}"
    if len(content) <= _MAX_CONTENT_LEN:
        return content
    return content[: _MAX_CONTENT_LEN - 3] + "..."


def extract_response_text(chunks: list[ChatChunk]) -> str:
    parts = [chunk.text for chunk in chunks if chunk.kind == "token" and chunk.text]
    return " ".join(parts).strip()


async def persist_episodic_turn(
    memory: MemoryService,
    *,
    request: ChatRequest,
    ctx: AgentContext,
    agent: AgentName,
    chunks: list[ChatChunk],
    child_mode: bool,
) -> None:
    """Persist one episodic row summarizing a completed chat turn."""
    response = extract_response_text(chunks)
    if not response:
        return

    content = build_episodic_content(
        user_message=request.message,
        agent=agent,
        response=response,
    )
    summary = f"Chat with {agent.value}: {request.message[:120]}"

    try:
        await memory.write(
            MemoryWriteInput(
                learner_id=request.learner_id,
                type=MemoryType.EPISODIC,
                content=content,
                summary=summary,
                tags=["chat", agent.value],
                provenance=Provenance(
                    kind="chat",
                    id=ctx.turn_id,
                    agent=agent.value,
                ),
            ),
            agent_id=agent.value,
            child_mode=child_mode,
        )
    except Exception:
        logger.exception(
            "orchestrator.episodic_write_failed",
            extra={"learner_id": request.learner_id, "agent": agent.value},
        )
