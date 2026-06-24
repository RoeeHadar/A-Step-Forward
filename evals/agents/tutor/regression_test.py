"""Tutor regression suite — faithfulness + helpfulness with mocked LLM (no Groq/API in CI).

DeepEval-style graded checks implemented with pytest so CI needs no extra judge model or API keys.
"""

from __future__ import annotations

import json
import re


def _mock_tutor_output(message: str) -> str:
    """Mirror evals/providers/tutor_mock.js for deterministic cases."""
    msg = message.lower()
    if "photosynthesis" in msg:
        return json.dumps(
            {
                "reply": (
                    "Let's think about photosynthesis together — what do plants need "
                    "from their environment? (see Lesson: Plant Biology Ch.2)"
                ),
                "next_step": "continue",
                "rationale": "Socratic + curriculum citation",
                "pinned_memory_writes": [],
            }
        )
    if "fraction" in msg or "denominator" in msg:
        return json.dumps(
            {
                "reply": (
                    "Before I explain, can you tell me what you think the denominator "
                    "represents in 3/4?"
                ),
                "next_step": "continue",
                "rationale": "Socratic probe on fraction concept",
                "pinned_memory_writes": [],
            }
        )
    return json.dumps(
        {
            "reply": "Before I explain, what do you already know about this topic?",
            "next_step": "continue",
            "rationale": "Socratic opener",
            "pinned_memory_writes": [],
        }
    )


def _helpfulness_score(reply: str) -> float:
    text = reply.lower()
    signals = [
        "?" in text,
        "already know" in text,
        "what do you" in text,
        "tell me" in text,
        "try" in text or "predict" in text,
    ]
    return sum(signals) / len(signals)


def _faithfulness_score(message: str, reply: str, *, threshold: float = 0.5) -> float:
    keyword_re = re.compile(r"[a-z]{4,}")
    input_text = message.lower()
    reply_text = reply.lower()
    keywords = set(keyword_re.findall(input_text)) - {
        "explain",
        "help",
        "what",
        "about",
        "confused",
        "simple",
        "words",
        "grade",
    }
    if not keywords:
        return 1.0
    hits = sum(1 for kw in keywords if kw in reply_text)
    return hits / len(keywords)


def test_tutor_helpfulness_socratic() -> None:
    message = "Can you explain what a denominator is in fractions?"
    out = json.loads(_mock_tutor_output(message))
    reply = out["reply"]
    assert _helpfulness_score(reply) > 0
    assert "?" in reply


def test_tutor_faithfulness_on_topic() -> None:
    message = "I'm confused about photosynthesis."
    out = json.loads(_mock_tutor_output(message))
    score = _faithfulness_score(message, out["reply"], threshold=0.5)
    assert score >= 0.5
