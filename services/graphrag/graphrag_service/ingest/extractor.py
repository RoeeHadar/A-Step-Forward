"""LLM entity/relation extraction for GraphRAG."""

from __future__ import annotations

import json
import os
import re

import httpx
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
    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        self._api_key = os.getenv("ANTHROPIC_API_KEY", "")

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
        if not self._api_key:
            log.warning("extractor.offline_mode", reason="ANTHROPIC_API_KEY not set")
            return self._heuristic_extract(chunks)

        payload = {
            "model": self.settings.extraction_model,
            "max_tokens": 4096,
            "temperature": 0.0,
            "system": _EXTRACTION_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": "\n\n---\n\n".join(f"Chunk {i}:\n{c}" for i, c in enumerate(chunks)),
                }
            ],
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
            text_blocks = [b["text"] for b in body.get("content", []) if b.get("type") == "text"]
            raw = "\n".join(text_blocks).strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            data = json.loads(raw)
            return Extraction.model_validate(data)
