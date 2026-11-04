"""Minimal LLM helper for the dreaming pipeline.

AS-93: goes through the guarded ``agents.base.llm.LLM`` client (resolve_model,
retries, offline stub) instead of a direct Groq HTTP call.
"""

from __future__ import annotations

import logging
from typing import Any

from ..settings import MemorySettings

logger = logging.getLogger(__name__)


async def dream_llm_complete(
    prompt: str,
    *,
    settings: MemorySettings | None = None,
    llm: Any | None = None,
) -> str:
    """Generate a semantic memory. Returns empty string on any failure or offline stub."""
    cfg = settings or MemorySettings()
    if llm is None and not cfg.groq_api_key:
        return ""
    try:
        from agents.base.llm import LLM, STUB_PREFIX, LLMRequest

        client = llm or LLM(model=cfg.llm_default_model)
        resp = await client.complete(
            LLMRequest(
                system=(
                    "You are a Memory Steward. Synthesize episodic memories "
                    "into enduring semantic insights."
                ),
                messages=[{"role": "user", "content": prompt}],
                max_output_tokens=200,
                temperature=0.3,
                metadata={"trace_name": "memory_dream"},
            )
        )
        if resp.text.startswith(STUB_PREFIX):
            return ""
        return resp.text.strip()
    except Exception:
        logger.exception("dream_llm_complete failed")
        return ""
