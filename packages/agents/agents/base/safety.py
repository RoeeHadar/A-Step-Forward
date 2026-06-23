"""Safety / moderation pre & post hooks.

Fast regex rules run first; ambiguous cases delegate to SafetyModerationAgent
(Haiku-class model). Child mode applies stricter thresholds.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from schemas.agents import AgentName

from .child_mode import child_mode_violation
from .refusals import refusal_for

if TYPE_CHECKING:
    from ..system.safety_moderation.agent import SafetyModerationAgent

_BLOCKED_PATTERNS = [
    re.compile(r"\bhow do i (?:make|build) (?:a bomb|explosives?)\b", re.IGNORECASE),
    re.compile(r"\bself[- ]?harm\b", re.IGNORECASE),
]

_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore (?:all|previous) instructions", re.IGNORECASE),
    re.compile(r"reveal (?:your |the )?system prompt", re.IGNORECASE),
    re.compile(r"you are now [a-z ]{3,30}", re.IGNORECASE),
    re.compile(r"disregard (?:your |the )?(?:rules|guidelines)", re.IGNORECASE),
    re.compile(r"developer mode", re.IGNORECASE),
]

_PII_OVERSHARE_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
]


class SafetyViolation(Exception):
    def __init__(self, kind: str, detail: str, *, redirect: str | None = None) -> None:
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail
        self.redirect = redirect or refusal_for(kind)

    def user_message(self) -> str:
        return self.redirect or refusal_for(self.kind)


def _rule_classify(text: str, *, child_mode: bool) -> str | None:
    for pat in _BLOCKED_PATTERNS:
        if pat.search(text):
            return "blocked_topic"
    for pat in _PROMPT_INJECTION_PATTERNS:
        if pat.search(text):
            return "prompt_injection"
    if re.search(r"\b(kill myself|end my life|want to die)\b", text, re.IGNORECASE):
        return "self_harm_risk"
    if child_mode and child_mode_violation(text):
        return "child_mode_violation"
    if not child_mode:
        for pat in _PII_OVERSHARE_PATTERNS:
            if pat.search(text):
                return "pii_overshare"
    return None


class SafetyModeration:
    def __init__(self, *, agent: SafetyModerationAgent | None = None, use_llm: bool = True) -> None:
        self._agent = agent
        self._use_llm = use_llm

    async def _get_agent(self) -> SafetyModerationAgent:
        if self._agent is None:
            from ..system.safety_moderation.agent import SafetyModerationAgent

            self._agent = SafetyModerationAgent()
        return self._agent

    async def classify(
        self,
        *,
        text: str,
        agent: AgentName,
        child_mode: bool,
        phase: str,
    ) -> None:
        kind = _rule_classify(text, child_mode=child_mode)
        if kind:
            raise SafetyViolation(kind, f"{phase} input matches {kind}")

        if not self._use_llm:
            return

        from ..base.agent import AgentContext
        from ..system.safety_moderation.agent import SafetyModerationInput

        mod_agent = await self._get_agent()
        ctx = AgentContext(learner_id="system", session_id="safety", turn_id="safety", child_mode=child_mode)
        result = await mod_agent.run(
            SafetyModerationInput(
                text=text,
                phase="pre" if phase == "pre" else "post",
                target_agent=agent,
                child_mode=child_mode,
            ),
            ctx,
        )
        categories = [c for c in result.output.categories if c != "safe"]
        if not categories:
            return
        primary = categories[0]
        raise SafetyViolation(
            primary,
            result.output.rationale or f"{phase} flagged by classifier",
            redirect=result.output.redirect,
        )

    async def pre(self, *, text: str, agent: AgentName, child_mode: bool) -> None:
        await self.classify(text=text, agent=agent, child_mode=child_mode, phase="pre")

    async def post(self, *, text: str, agent: AgentName, child_mode: bool) -> None:
        await self.classify(text=text, agent=agent, child_mode=child_mode, phase="post")
