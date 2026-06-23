"""DeepEval suite for Tutor citation + output faithfulness (Phase-1, no live LLM).

Uses deterministic custom metrics so CI passes without API keys.
"""

from __future__ import annotations

import json
import re

from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class JsonShapeMetric(BaseMetric):
    """TutorOutput must parse as JSON with required fields."""

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""

    def measure(self, test_case: LLMTestCase) -> float:
        try:
            out = json.loads(test_case.actual_output)
        except json.JSONDecodeError as exc:
            self.reason = f"invalid JSON: {exc}"
            self.score = 0.0
            self.success = False
            return self.score
        required = ("reply", "next_step", "rationale", "pinned_memory_writes")
        missing = [k for k in required if k not in out]
        if missing:
            self.reason = f"missing keys: {missing}"
            self.score = 0.0
            self.success = False
            return self.score
        valid_steps = {"continue", "assess", "next_lesson", "rest"}
        if out["next_step"] not in valid_steps:
            self.reason = f"invalid next_step: {out['next_step']}"
            self.score = 0.0
            self.success = False
            return self.score
        self.reason = "valid TutorOutput shape"
        self.score = 1.0
        self.success = True
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success


class CitationPresenceMetric(BaseMetric):
    """When curriculum is referenced, reply should cite a lesson or chapter."""

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""

    def measure(self, test_case: LLMTestCase) -> float:
        out = json.loads(test_case.actual_output)
        reply = out.get("reply", "")
        if "Lesson" in reply or "Ch." in reply or "lesson" in reply.lower():
            self.score = 1.0
            self.success = True
            self.reason = "curriculum citation present"
        else:
            self.score = 0.0
            self.success = False
            self.reason = "expected curriculum citation marker"
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success


class FaithfulnessMetric(BaseMetric):
    """Reply should not contradict the input topic (keyword overlap heuristic)."""

    KEYWORD_RE = re.compile(r"[a-z]{4,}")

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""

    def measure(self, test_case: LLMTestCase) -> float:
        out = json.loads(test_case.actual_output)
        reply = out.get("reply", "").lower()
        input_text = (test_case.input or "").lower()
        keywords = set(self.KEYWORD_RE.findall(input_text)) - {"explain", "help", "what", "about"}
        if not keywords:
            self.score = 1.0
            self.success = True
            self.reason = "no topic keywords to check"
            return self.score
        hits = sum(1 for kw in keywords if kw in reply)
        self.score = hits / len(keywords)
        self.success = self.score >= self.threshold
        self.reason = f"topic overlap {hits}/{len(keywords)}"
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success


def _mock_tutor_output(message: str) -> str:
    """Mirror evals/providers/tutor_mock.js for deterministic DeepEval cases."""
    msg = message.lower()
    if "photosynthesis" in msg:
        return json.dumps(
            {
                "reply": "Let's connect your ideas to photosynthesis (see Lesson: Plant Biology Ch.2). What do plants need to grow?",
                "next_step": "continue",
                "rationale": "Socratic + curriculum citation",
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


def test_tutor_output_shape():
    message = "Help me with algebra."
    assert_test(
        LLMTestCase(input=message, actual_output=_mock_tutor_output(message)),
        [JsonShapeMetric()],
    )


def test_tutor_citation_accuracy():
    message = "I'm confused about photosynthesis."
    assert_test(
        LLMTestCase(input=message, actual_output=_mock_tutor_output(message)),
        [CitationPresenceMetric()],
    )


def test_tutor_faithfulness():
    message = "Explain photosynthesis simply."
    assert_test(
        LLMTestCase(input=message, actual_output=_mock_tutor_output(message)),
        [FaithfulnessMetric(threshold=0.5)],
    )
