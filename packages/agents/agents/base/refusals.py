"""User-facing refusal templates for safety violations."""

from __future__ import annotations

REFUSAL_TEMPLATES: dict[str, str] = {
    "blocked_topic": (
        "I can't help with that topic. Let's get back to your learning — "
        "what would you like to work on next?"
    ),
    "prompt_injection": (
        "I need to stay focused on helping you learn. Ask me a question about "
        "your lesson or practice, and I'll do my best."
    ),
    "self_harm_risk": (
        "It sounds like you might be going through something difficult. "
        "Please talk to a trusted adult or contact a crisis helpline. "
        "I'm here to support your learning when you're ready."
    ),
    "child_mode_violation": (
        "That topic isn't appropriate for your learning space. "
        "Let's pick something else from your lessons."
    ),
    "pii_overshare": (
        "For your privacy, please don't share personal details like IDs or "
        "payment information here. We can continue without those."
    ),
}


def refusal_for(kind: str, *, redirect: str | None = None) -> str:
    if redirect:
        return redirect
    return REFUSAL_TEMPLATES.get(kind, REFUSAL_TEMPLATES["blocked_topic"])
