"""Write skill-adaptation memories when affect signals warrant it."""
from __future__ import annotations

from typing import Any

from schemas.common import Provenance
from schemas.memory import MemoryType, MemoryWriteInput

from .affect_detector import AffectResult, AffectSignal

# Maps each affect signal to an adaptation instruction stored in memory
ADAPTATIONS: dict[AffectSignal, str] = {
    AffectSignal.FRUSTRATED: (
        "Learner is showing frustration. Switch to shorter, simpler explanations. "
        "Add more encouragement. Ask one small, easy question before a harder one."
    ),
    AffectSignal.DESPAIR: (
        "Learner expressed despair or gave up. Immediately validate their effort, "
        "break the concept into the smallest possible step, offer a completely "
        "worked example before asking anything. Avoid challenges for this turn."
    ),
    AffectSignal.CONFUSED: (
        "Learner is confused. Rephrase using a concrete everyday analogy. "
        "Check understanding with a yes/no question first."
    ),
    AffectSignal.CELEBRATING: (
        "Learner is celebrating understanding. Good moment to introduce "
        "the next related concept or raise difficulty slightly."
    ),
    AffectSignal.BORED: (
        "Learner seems bored. Try a more challenging question or a surprising "
        "application of the concept."
    ),
}


async def maybe_write_skill(
    *,
    learner_id: str,
    agent_name: str,
    affect: AffectResult,
    memory_api: Any = None,
    child_mode: bool = False,
) -> str | None:
    """Write an adaptation note to memory. Returns the adaptation text, or None.

    Returns adaptation text for prompt injection even when memory write is skipped
    (offline mode, child mode, or write failure). Returns None for NEUTRAL/ENGAGED.
    """
    adaptation = ADAPTATIONS.get(affect.signal)
    if adaptation is None:
        return None

    if memory_api is not None and not child_mode:
        try:
            write_input = MemoryWriteInput(
                learner_id=learner_id,
                type=MemoryType.AFFECTIVE,
                content=f"[{agent_name}] Adaptation note: {adaptation}",
                summary=f"Affect={affect.signal.value} detected; adaptation written.",
                tags=["adaptation", affect.signal.value],
                provenance=Provenance(
                    kind="agent_reflection",
                    id=agent_name,
                    agent=agent_name,
                ),
            )
            await memory_api.write(write_input, agent_id=agent_name)
        except Exception:  # noqa: BLE001
            pass

    return adaptation
