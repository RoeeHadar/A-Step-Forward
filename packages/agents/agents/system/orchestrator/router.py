"""Declarative intent router for the orchestrator.

Phase 1 uses pattern matching against the user message (and optional explicit
`requested_agent`). An LLM-backed router can be layered on later using
`prompts/orchestrator/v1.md` without changing the public contract.
"""

from __future__ import annotations

import re

from schemas.agents import AgentName, RouteDecision

from .input import OrchestratorInput

# Order matters: first match wins.
_INTENT_PATTERNS: list[tuple[re.Pattern[str], AgentName, str]] = [
    (
        re.compile(r"\b(quiz|test me|assessment|exercise|worksheet)\b", re.IGNORECASE),
        AgentName.ASSESSMENT_GENERATOR,
        "assessment intent",
    ),
    (
        re.compile(r"\b(review my|feedback on my|check my (?:code|essay|solution|work))\b", re.IGNORECASE),
        AgentName.REVIEWER,
        "submission review intent",
    ),
    (
        re.compile(r"\b(grade|score|rubric)\b", re.IGNORECASE),
        AgentName.GRADER,
        "grading intent",
    ),
    (
        re.compile(r"\b(motivat|goal|study habit|burn(?:ed|t) out|accountability)\b", re.IGNORECASE),
        AgentName.MENTOR,
        "mentoring intent",
    ),
    (
        re.compile(r"\b(practice|drill|flashcard|spaced repetition|fsrs)\b", re.IGNORECASE),
        AgentName.COACH,
        "practice intent",
    ),
    (
        re.compile(r"\b(notes?|recap|summary|study guide)\b", re.IGNORECASE),
        AgentName.NOTE_TAKER,
        "note-taking intent",
    ),
    (
        re.compile(r"\b(translate|plain language|dyslexia|read aloud|accessibility)\b", re.IGNORECASE),
        AgentName.ACCESSIBILITY,
        "accessibility intent",
    ),
    (
        re.compile(r"\b(progress|where am i|knowledge gap|at.?risk|mastery)\b", re.IGNORECASE),
        AgentName.PROGRESS_ANALYZER,
        "progress analysis intent",
    ),
    (
        re.compile(r"\b(curriculum|lesson plan|what should i learn next)\b", re.IGNORECASE),
        AgentName.CURRICULUM_DESIGNER,
        "curriculum intent",
    ),
    (
        re.compile(r"\b(research|find me sources|cite|references|literature review)\b", re.IGNORECASE),
        AgentName.RESEARCH,
        "research intent",
    ),
    (
        re.compile(r"\b(content|resource|reading list|materials for)\b", re.IGNORECASE),
        AgentName.CONTENT_CURATOR,
        "content curation intent",
    ),
    (
        re.compile(r"\b(why|how does|explain|what is|what are|define)\b", re.IGNORECASE),
        AgentName.QA_EXPLAINER,
        "explanation intent",
    ),
    (
        re.compile(r"\b(lesson|teach me|walk me through|tutor)\b", re.IGNORECASE),
        AgentName.TUTOR,
        "lesson intent",
    ),
]


class DeclarativeRouter:
    """Maps user intent to one agent using ordered regex patterns."""

    def route(self, inp: OrchestratorInput) -> RouteDecision:
        if inp.requested_agent is not None:
            return RouteDecision(
                selected_agents=[inp.requested_agent],
                rationale="explicit user request",
            )

        message = inp.message.strip()
        for pattern, agent, label in _INTENT_PATTERNS:
            if pattern.search(message):
                return RouteDecision(
                    selected_agents=[agent],
                    rationale=f"declarative router: matched {label}",
                )

        return RouteDecision(
            selected_agents=[AgentName.TUTOR],
            rationale="declarative router: default to Tutor for adaptive lesson handling",
        )
