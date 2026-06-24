"""LangGraph orchestration graph.

Nodes: route → hydrate (stub) → invoke agent → finalize.
Checkpointing and parallel multi-agent composition are Phase 2 extensions.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict
from uuid import uuid4

from agents import AGENT_FACTORIES
from agents.base.agent import AgentContext
from agents.base.child_mode import resolve_child_mode
from agents.system.orchestrator import OrchestratorAgent, OrchestratorInput, build_agent_summaries
from langgraph.graph import END, START, StateGraph
from schemas.agents import AgentName, ChatChunk, ChatRequest, RouteDecision

from .invoke import AGENT_DISPATCH, invoke_registered_agent


class GraphState(TypedDict):
    request: ChatRequest
    ctx: AgentContext
    decision: RouteDecision | None
    chunks: Annotated[list[ChatChunk], operator.add]


async def route_node(state: GraphState) -> dict[str, object]:
    request = state["request"]
    orchestrator = OrchestratorAgent()
    result = await orchestrator(
        OrchestratorInput(
            learner_id=request.learner_id,
            message=request.message,
            requested_agent=request.requested_agent,
            session_id=request.session_id,
            locale=request.locale,
            available_agents=build_agent_summaries(),
        ),
        state["ctx"],
    )
    return {"decision": result.output.decision}


async def invoke_node(state: GraphState) -> dict[str, object]:
    decision = state["decision"]
    if decision is None:
        return {
            "chunks": [
                ChatChunk(kind="error", agent=AgentName.ORCHESTRATOR, text="Routing failed."),
                ChatChunk(kind="done", agent=AgentName.ORCHESTRATOR),
            ]
        }

    selected = decision.selected_agents[0]
    request = state["request"]
    ctx = state["ctx"]

    factory = AGENT_FACTORIES.get(selected)
    if factory is None:
        return {
            "chunks": [
                ChatChunk(
                    kind="token",
                    agent=selected,
                    text=(
                        f"The {selected.value.replace('_', ' ')} agent is registered but not "
                        "implemented yet. Sub-agent 03 will add it in a follow-up PR."
                    ),
                ),
                ChatChunk(kind="done", agent=selected),
            ]
        }

    if selected not in AGENT_DISPATCH:
        return {
            "chunks": [
                ChatChunk(
                    kind="token",
                    agent=selected,
                    text=f"[stub] Agent '{selected}' invoked successfully.",
                ),
                ChatChunk(kind="done", agent=selected),
            ]
        }

    agent = factory()
    chunks = await invoke_registered_agent(selected, agent, request, ctx)
    return {"chunks": chunks}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("route", route_node)
    graph.add_node("invoke", invoke_node)
    graph.add_edge(START, "route")
    graph.add_edge("route", "invoke")
    graph.add_edge("invoke", END)
    return graph.compile()


def new_context(
    request: ChatRequest,
    *,
    child_mode: bool = False,
    age: int | None = None,
    memory_api: Any = None,
) -> AgentContext:
    return AgentContext(
        learner_id=request.learner_id,
        session_id=request.session_id or str(uuid4()),
        turn_id=str(uuid4()),
        locale=request.locale,
        child_mode=resolve_child_mode(age=age, child_mode_flag=child_mode),
        memory_api=memory_api,
    )
