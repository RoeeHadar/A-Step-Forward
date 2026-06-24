"""Shared helpers for learner-facing agent implementations."""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel

from .llm import LLM, STUB_PREFIX, LLMRequest, LLMResponse

O = TypeVar("O", bound=BaseModel)


def is_stub_llm_response(response: LLMResponse) -> bool:
    return response.text.startswith(STUB_PREFIX)


def extract_json_object(text: str) -> dict | None:
    """Best-effort JSON extraction from model text."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


async def complete_turn(
    llm: LLM,
    *,
    system: str,
    user_message: str,
    trace_name: str,
    max_output_tokens: int = 4_000,
) -> LLMResponse:
    return await llm.complete(
        LLMRequest(
            system=system,
            messages=[{"role": "user", "content": user_message}],
            metadata={"trace_name": trace_name},
            cache_system=True,
            max_output_tokens=max_output_tokens,
        )
    )


def parse_output(response: LLMResponse, model: type[O], fallback: O) -> O:
    if is_stub_llm_response(response):
        return fallback
    payload = extract_json_object(response.text)
    if payload is None:
        return fallback
    return model.model_validate(payload)
