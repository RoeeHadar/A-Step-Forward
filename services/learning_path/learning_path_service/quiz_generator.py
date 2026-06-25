"""Weekly quiz question generator.

Priority: pull from diagnostic_items bank (matching week concepts).
Fallback: generate new questions via Groq LLM when bank is sparse.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.learning_path import QuizOption, StoredQuizItem

MIN_BANK_QUESTIONS = 5
TARGET_QUIZ_SIZE = 8
GROQ_MODEL = "llama-3.3-70b-versatile"


def _bank_row_to_stored_item(row: Any) -> StoredQuizItem | None:
    """Convert a diagnostic_items DB row to a StoredQuizItem."""
    try:
        opts: dict = row["options"] if isinstance(row["options"], dict) else json.loads(row["options"])
        choices: list[str] = opts.get("choices", [])
        correct: str = str(opts.get("correct", "A"))
        keys = ["A", "B", "C", "D"]
        quiz_options = [
            QuizOption(key=keys[i], text=text_val)
            for i, text_val in enumerate(choices[:4])
        ]
        if len(quiz_options) < 2:
            return None
        return StoredQuizItem(
            id=str(row["id"]),
            topic=row["topic"],
            subject=row["subject"],
            difficulty=float(row["difficulty"]),
            stem=row["stem"],
            options=quiz_options,
            correct=correct,
            source="bank",
        )
    except Exception:
        return None


async def fetch_bank_items(
    session: AsyncSession,
    concept_ids: list[str],
    *,
    limit: int = TARGET_QUIZ_SIZE * 2,
) -> list[StoredQuizItem]:
    """Pull questions from diagnostic_items matching the given concept IDs."""
    if not concept_ids:
        return []
    result = await session.execute(
        text(
            """
            SELECT id::text, topic, subject, difficulty, stem, options
            FROM diagnostic_items
            WHERE source_concept = ANY(:concepts)
               OR topic = ANY(:concepts)
            ORDER BY random()
            LIMIT :lim
            """
        ),
        {"concepts": concept_ids, "lim": limit},
    )
    items: list[StoredQuizItem] = []
    for row in result.mappings().all():
        item = _bank_row_to_stored_item(row)
        if item is not None:
            items.append(item)
    return items


def _parse_llm_questions(raw: str, concept_ids: list[str], subject: str) -> list[StoredQuizItem]:
    """Parse LLM JSON output into StoredQuizItem list."""
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        data: list[dict] = json.loads(raw[start:end])
        items: list[StoredQuizItem] = []
        for q in data:
            choices: list[str] = q.get("choices", [])
            correct: str = str(q.get("correct", "A")).upper()
            if not correct or correct not in "ABCD":
                correct = "A"
            keys = ["A", "B", "C", "D"]
            quiz_options = [QuizOption(key=keys[i], text=c) for i, c in enumerate(choices[:4])]
            if len(quiz_options) < 2:
                continue
            stem = q.get("stem") or q.get("question", "")
            topic = q.get("topic") or (concept_ids[0] if concept_ids else "general")
            items.append(
                StoredQuizItem(
                    id=str(uuid.uuid4()),
                    topic=topic,
                    subject=subject,
                    difficulty=float(q.get("difficulty", 5.0)),
                    stem=stem,
                    options=quiz_options,
                    correct=correct,
                    source="llm",
                )
            )
        return items
    except Exception:
        return []


async def generate_via_llm(
    concept_ids: list[str],
    subject: str,
    count: int = 5,
) -> list[StoredQuizItem]:
    """Call Groq to generate quiz questions when the bank is sparse."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _stub_questions(concept_ids, subject, count)

    try:
        import httpx

        prompt = (
            f"Generate exactly {count} multiple-choice quiz questions for these concepts: "
            f"{', '.join(concept_ids[:5])}. Subject: {subject}.\n\n"
            "Return a JSON array only (no prose). Each object must have:\n"
            '  "topic": concept id string,\n'
            '  "stem": question text,\n'
            '  "choices": [A text, B text, C text, D text],\n'
            '  "correct": "A"|"B"|"C"|"D",\n'
            '  "difficulty": number 1-10\n'
            "Make questions academically rigorous and Bloom-level appropriate."
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an expert quiz generator. Reply with JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
            )
            if resp.status_code != 200:
                return _stub_questions(concept_ids, subject, count)
            raw = resp.json()["choices"][0]["message"]["content"]
            parsed = _parse_llm_questions(raw, concept_ids, subject)
            if parsed:
                return parsed[:count]
    except Exception:
        pass

    return _stub_questions(concept_ids, subject, count)


def _stub_questions(concept_ids: list[str], subject: str, count: int) -> list[StoredQuizItem]:
    """Deterministic fallback when LLM is unavailable."""
    items: list[StoredQuizItem] = []
    for i, concept_id in enumerate(concept_ids[:count]):
        name = concept_id.replace("_", " ").replace("-", " ").title()
        items.append(
            StoredQuizItem(
                id=str(uuid.uuid4()),
                topic=concept_id,
                subject=subject,
                difficulty=5.0,
                stem=f"Which of the following best describes **{name}**?",
                options=[
                    QuizOption(key="A", text=f"An unrelated fact about {name}"),
                    QuizOption(key="B", text=f"A defining property of {name}"),
                    QuizOption(key="C", text=f"A common misconception about {name}"),
                    QuizOption(key="D", text=f"An oversimplified claim about {name}"),
                ],
                correct="B",
                source="stub",
            )
        )
    return items


async def build_quiz_items(
    session: AsyncSession,
    concept_ids: list[str],
    subject: str,
    *,
    target: int = TARGET_QUIZ_SIZE,
) -> list[StoredQuizItem]:
    """Main entry: fetch from bank, top up with LLM if needed."""
    bank = await fetch_bank_items(session, concept_ids, limit=target * 3)
    if len(bank) >= MIN_BANK_QUESTIONS:
        # Deduplicate by stem prefix, cap at target
        seen: set[str] = set()
        deduped: list[StoredQuizItem] = []
        for item in bank:
            key = item.stem[:40]
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped[:target]

    # Supplement from LLM
    needed = max(0, target - len(bank))
    llm_items = await generate_via_llm(concept_ids, subject, needed)
    combined = bank + llm_items
    return combined[:target]
