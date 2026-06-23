"""Context-window compaction for the orchestrator."""

from __future__ import annotations

from schemas.memory import CompactionInput, CompactionOutput

from ..settings import MemorySettings

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None  # type: ignore[assignment]


def _approx_tokens(text: str, *, encoding_name: str = "cl100k_base") -> int:
    if tiktoken is not None:
        try:
            enc = tiktoken.get_encoding(encoding_name)
            return len(enc.encode(text))
        except Exception:
            pass
    return max(1, len(text) // 4)


def _message_tokens(message: dict) -> int:
    role = str(message.get("role", ""))
    content = str(message.get("content", ""))
    return _approx_tokens(f"{role}: {content}")


def _total_tokens(messages: list[dict]) -> int:
    return sum(_message_tokens(m) for m in messages)


def _structured_summary(older: list[dict]) -> str:
    facts: list[str] = []
    decisions: list[str] = []
    open_questions: list[str] = []

    for message in older:
        role = message.get("role", "msg")
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        line = f"[{role}] {content[:300]}"
        if "?" in content:
            open_questions.append(line)
        elif any(kw in content.lower() for kw in ("decided", "will", "plan")):
            decisions.append(line)
        else:
            facts.append(line)

    parts = ["Prior conversation summary (compacted):"]
    if facts:
        parts.append("Facts:")
        parts.extend(f"- {f}" for f in facts[:12])
    if decisions:
        parts.append("Decisions:")
        parts.extend(f"- {d}" for d in decisions[:8])
    if open_questions:
        parts.append("Open questions:")
        parts.extend(f"- {q}" for q in open_questions[:8])
    return "\n".join(parts)


async def compact_context(
    input: CompactionInput,
    *,
    settings: MemorySettings | None = None,
) -> CompactionOutput:
    cfg = settings or MemorySettings()
    target = input.target_tokens
    msgs = list(input.messages)
    current = _total_tokens(msgs)

    if current <= target:
        return CompactionOutput(
            messages=msgs,
            compacted_summary="",
            kept_verbatim_count=len(msgs),
            estimated_tokens=current,
        )

    kept_count = max(2, cfg.compaction_verbatim_turns)
    kept_verbatim = msgs[-kept_count:] if len(msgs) > kept_count else msgs
    older = msgs[:-kept_count] if len(msgs) > kept_count else []

    summary = _structured_summary(older)
    if input.pinned_memory_ids:
        summary += "\n\nPinned memories: " + ", ".join(input.pinned_memory_ids)

    summary_msg = {"role": "system", "content": summary}
    new_msgs = [summary_msg, *kept_verbatim]

    while _total_tokens(new_msgs) > target and len(kept_verbatim) > 2:
        kept_verbatim = kept_verbatim[1:]
        new_msgs = [summary_msg, *kept_verbatim]

    return CompactionOutput(
        messages=new_msgs,
        compacted_summary=summary,
        kept_verbatim_count=len(kept_verbatim),
        estimated_tokens=_total_tokens(new_msgs),
    )
