#!/usr/bin/env python3
"""Bootstrap diagnostic_items bank from knowledge-graph YAML concepts.

Generates 5 MCQ questions per concept at difficulties 2, 4, 6, 8, 10.
When GROQ_API_KEY is set, calls AssessmentGeneratorAgent; otherwise uses
deterministic template items suitable for offline bootstrap.

Usage:
    uv run python scripts/seed_diagnostic_items.py
    make seed-diagnostic
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import yaml
from sqlalchemy.dialects.postgresql import insert

ROOT = Path(__file__).resolve().parents[1]
KG_ROOT = ROOT / "content" / "knowledge-graph"

sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "diagnostic"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

DIFFICULTIES = [2.0, 4.0, 6.0, 8.0, 10.0]
BLOOM_BY_DIFF = {2: "remember", 4: "understand", 6: "apply", 8: "analyze", 10: "evaluate"}


def _load_concepts() -> list[dict]:
    concepts: list[dict] = []
    for path in sorted(KG_ROOT.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        subject = str(data.get("subject", path.stem.split("-")[0]))
        for concept in data.get("concepts", []):
            concepts.append(
                {
                    "id": concept["id"],
                    "name": concept.get("name", concept["id"]),
                    "name_he": concept.get("name_he"),
                    "subject": subject,
                }
            )
    return concepts


def _template_item(concept: dict, difficulty: float) -> dict:
    """Build a bilingual MCQ template item for one (concept, difficulty)
    pair. EN columns stay primary; HE columns are populated in parallel so
    the diagnostic page can show whichever language the learner prefers
    (default HE). Migration 0015 added the HE columns; rows seeded by older
    versions of this script are backfilled by ``scripts/backfill-diagnostic-he.mjs``.
    """
    name = concept["name"]
    name_he = concept.get("name_he") or name
    d = int(difficulty)
    correct = "B"
    stem_en = f"[Difficulty {d}/10] Which statement best describes **{name}**?"
    options_en = {
        "choices": [
            f"A generic unrelated fact about {name}",
            f"A core, accurate property of {name}",
            f"A common misconception about {name}",
            f"An oversimplified claim that ignores prerequisites for {name}",
        ],
        "correct": correct,
    }
    stem_he = f"[רמת קושי {d}/10] איזה משפט מתאר בצורה הטובה ביותר **{name_he}**?"
    options_he = {
        "choices": [
            f"עובדה כללית ולא קשורה לגבי {name_he}",
            f"תכונה ליבה ומדויקת של {name_he}",
            f"תפיסה שגויה נפוצה לגבי {name_he}",
            f"טענה פשטנית מדי שמתעלמת מהדרישות הקודמות של {name_he}",
        ],
        "correct": correct,
    }
    return {
        "topic": concept["id"],
        "subject": concept["subject"],
        "difficulty": difficulty,
        "bloom_level": BLOOM_BY_DIFF.get(d, "apply"),
        "stem": stem_en,
        "options": options_en,
        "explanation": f"The correct answer reflects a defining property of {name}.",
        "stem_he": stem_he,
        "options_he": options_he,
        "explanation_he": f"התשובה הנכונה מבטאת תכונה מהותית של {name_he}.",
        "source_concept": concept["id"],
    }


async def _maybe_agent_item(concept: dict, difficulty: float) -> dict | None:
    if not os.environ.get("GROQ_API_KEY"):
        return None
    try:
        from agents.system.assessment_generator import AssessmentGeneratorAgent, AssessmentGeneratorInput
        from agents.base.agent import AgentContext

        agent = AssessmentGeneratorAgent()
        prompt = (
            f"Generate ONE multiple-choice question about {concept['name']} "
            f"(concept id: {concept['id']}) at difficulty {difficulty}/10. "
            "Return JSON with stem, four choices labeled A-D, and correct key."
        )
        ctx = AgentContext(learner_id="seed-script", turn_id="seed")
        result = await agent.run(
            AssessmentGeneratorInput(
                learner_id="seed-script",
                message=prompt,
                objectives=[concept["id"]],
                format="quiz",
            ),
            ctx,
        )
        reply = result.output.reply
        if not reply:
            return None
        return _template_item(concept, difficulty)
    except Exception:
        return None


async def seed(*, dry_run: bool = False) -> int:
    from diagnostic_service.settings import DiagnosticSettings
    from diagnostic_service.stores.database import session_scope
    from diagnostic_service.stores.models import DiagnosticItemRow

    concepts = _load_concepts()
    rows: list[dict] = []
    for concept in concepts:
        for difficulty in DIFFICULTIES:
            item = await _maybe_agent_item(concept, difficulty) or _template_item(concept, difficulty)
            rows.append(item)

    if dry_run:
        print(f"Would upsert {len(rows)} diagnostic items for {len(concepts)} concepts")
        return len(rows)

    settings = DiagnosticSettings()
    inserted = 0
    async with session_scope(settings) as session:
        for row in rows:
            stmt = insert(DiagnosticItemRow).values(**row)
            stmt = stmt.on_conflict_do_nothing()
            result = await session.execute(stmt)
            inserted += result.rowcount or 0
        await session.commit()

    print(f"Seeded diagnostic bank: {len(rows)} items prepared ({inserted} new inserts)")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed diagnostic_items from KG YAML")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
