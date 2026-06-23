"""Semantic chunking for GraphRAG ingestion."""

from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

from ..settings import GraphRAGSettings


@dataclass(frozen=True)
class TextChunk:
    ordinal: int
    text: str
    heading: str | None
    token_count: int


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class SemanticChunker:
    def __init__(self, settings: GraphRAGSettings) -> None:
        self.settings = settings
        try:
            self._enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._enc = None

    def _count_tokens(self, text: str) -> int:
        if self._enc is None:
            return max(1, len(text) // 4)
        return len(self._enc.encode(text))

    def split(self, text: str) -> list[TextChunk]:
        target = self.settings.chunk_tokens
        overlap = self.settings.chunk_overlap
        sections: list[tuple[str | None, str]] = []
        last = 0
        current_heading: str | None = None
        for match in _HEADING_RE.finditer(text):
            start = match.start()
            if start > last:
                sections.append((current_heading, text[last:start].strip()))
            current_heading = match.group(2).strip()
            last = match.end()
        if last < len(text):
            sections.append((current_heading, text[last:].strip()))

        if not sections:
            sections = [(None, text.strip())]

        chunks: list[TextChunk] = []
        ordinal = 0
        for heading, body in sections:
            if not body:
                continue
            words = body.split()
            window: list[str] = []
            window_tokens = 0
            for word in words:
                token_guess = self._count_tokens(word + " ")
                if window_tokens + token_guess > target and window:
                    chunk_text = " ".join(window)
                    chunks.append(
                        TextChunk(
                            ordinal=ordinal,
                            text=chunk_text,
                            heading=heading,
                            token_count=self._count_tokens(chunk_text),
                        )
                    )
                    ordinal += 1
                    if overlap > 0:
                        overlap_words = window[-max(1, overlap // 4) :]
                        window = overlap_words
                        window_tokens = self._count_tokens(" ".join(window))
                    else:
                        window = []
                        window_tokens = 0
                window.append(word)
                window_tokens += token_guess
            if window:
                chunk_text = " ".join(window)
                chunks.append(
                    TextChunk(
                        ordinal=ordinal,
                        text=chunk_text,
                        heading=heading,
                        token_count=self._count_tokens(chunk_text),
                    )
                )
                ordinal += 1
        return chunks
