"""Memory service — single front door for all learner memory.

The service is intentionally the only writer/reader of memory tables. Routes,
agents, and MCP servers all go through `MemoryService` (or its MCP facade).
"""

from .settings import MemorySettings
from .api import MemoryService, get_memory_service

__all__ = ["MemorySettings", "MemoryService", "get_memory_service"]
