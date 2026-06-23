"""Agent orchestrator — routes user intent to the right agent(s) and composes
multi-agent flows on top of LangGraph.

Phase 0 ships a deterministic declarative router so the rest of the system has
a working orchestrator from day one. Sub-agent 03-agents promotes it to an
LLM-routed graph with checkpointing + parallel composition.
"""

from .graph import build_graph, new_context
from .router import Router, RoutedTurn
from .runner import OrchestratorRunner

__all__ = ["Router", "RoutedTurn", "OrchestratorRunner", "build_graph", "new_context"]
