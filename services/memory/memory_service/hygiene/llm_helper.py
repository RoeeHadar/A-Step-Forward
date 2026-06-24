"""Minimal Groq LLM helper for the dreaming pipeline."""

from __future__ import annotations

import logging

import httpx

from ..settings import MemorySettings

logger = logging.getLogger(__name__)

_GROQ_BASE = "https://api.groq.com/openai/v1"


async def dream_llm_complete(
    prompt: str,
    *,
    settings: MemorySettings | None = None,
) -> str:
    """Call Groq to generate a semantic memory. Returns empty string on any failure."""
    cfg = settings or MemorySettings()
    if not cfg.groq_api_key:
        return ""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{_GROQ_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": cfg.llm_default_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a Memory Steward. Synthesize episodic memories "
                                "into enduring semantic insights."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                return str(message.get("content") or "").strip()
            return ""
    except Exception:  # noqa: BLE001
        logger.exception("dream_llm_complete failed")
        return ""
