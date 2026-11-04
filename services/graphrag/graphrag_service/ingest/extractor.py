"""LLM entity/relation extraction for GraphRAG."""

from __future__ import annotations

import json
import re
from typing import Any

import structlog
from schemas.graph import EdgeKind, Entity, Extraction, NodeKind, Relation

from ..settings import GraphRAGSettings

log = structlog.get_logger(__name__)

_EXTRACTION_PROMPT = """Extract educational knowledge-graph entities and relations from the text chunks.
Return JSON with keys: entities, relations, claims, confidence, notes.
Only use these node kinds: Concept, Skill, Topic, Lesson, Resource, Assessment, Question, Misconception.
Only use these edge kinds: PREREQUISITE_OF, TEACHES, COVERS, TESTS, OPPOSES, REQUIRES.
Keep entities concise and canonical."""


class Extractor:
    def __init__(self, settings: GraphRAGSettings, llm: Any | None = None) -> None:
        # AS-93: extraction goes through the guarded agents LLM client (resolve_model
        # maps extraction_model, e.g. claude-sonnet-4-5, to a Groq id per ADR-0004)
        # instead of a direct Anthropic HTTP call. No key -> offline stub -> heuristic.
        self.settings = settings
        self._llm = llm

    def _heuristic_extract(self, chunks: list[str]) -> Extraction:
        """Offline fallback using markdown headings and keyword patterns."""
        entities: list[Entity] = []
        relations: list[Relation] = []
        seen: set[str] = set()
        heading_re = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
        bold_re = re.compile(r"\*\*(.+?)\*\*")

        for chunk in chunks:
            for match in heading_re.findall(chunk):
                name = match.strip()
                key = name.lower()
                if key and key not in seen:
                    seen.add(key)
                    entities.append(Entity(name=name, kind=NodeKind.CONCEPT, confidence=0.65))
            for match in bold_re.findall(chunk):
                name = match.strip()
                key = name.lower()
                if len(name) >= 3 and key not in seen:
                    seen.add(key)
                    kind = NodeKind.MISCONCEPTION if "misconception" in key else NodeKind.CONCEPT
                    entities.append(Entity(name=name, kind=kind, confidence=0.55))

            lower = chunk.lower()
            if "division" in lower and "fraction" in lower and "prerequisite" in lower:
                relations.append(
                    Relation(
                        src_name="Division",
                        dst_name="Fractions",
                        kind=EdgeKind.PREREQUISITE_OF,
                        confidence=0.6,
                    )
                )
            if "misconception" in lower and "equivalent fractions" in lower:
                relations.append(
                    Relation(
                        src_name="Common Misconception",
                        dst_name="Equivalent Fractions",
                        kind=EdgeKind.OPPOSES,
                        confidence=0.55,
                    )
                )

        notes: str = "" if entities else "low_confidence"
        return Extraction(
            entities=entities,
            relations=relations,
            claims=[],
            confidence=0.6 if entities else 0.0,
            notes=notes,  # type: ignore[arg-type]
        )

    async def extract(self, chunks: list[str]) -> Extraction:
        if not chunks:
            return Extraction(entities=[], relations=[], claims=[], confidence=0.0, notes="low_confidence")
        from agents.base.llm import LLM, STUB_PREFIX, LLMRequest

        llm = self._llm or LLM(model=self.settings.extraction_model)
        resp = await llm.complete(
            LLMRequest(
                system=_EXTRACTION_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": "\n\n---\n\n".join(f"Chunk {i}:\n{c}" for i, c in enumerate(chunks)),
                    }
                ],
                max_output_tokens=4096,
                temperature=0.0,
                metadata={"trace_name": "graphrag_extractor"},
            )
        )
        if resp.text.startswith(STUB_PREFIX):
            log.warning("extractor.offline_mode", reason="LLM not configured")
            return self._heuristic_extract(chunks)
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        data = json.loads(raw)
        return Extraction.model_validate(data)
