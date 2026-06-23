"""PII redaction before any memory write.

Uses Presidio when installed and enabled; always applies custom regex rules.
Never bypass — `MemoryService.write` calls this first.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..settings import MemorySettings

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PASSPORT_RE = re.compile(r"\b[A-Z]{1,2}\d{6,9}\b")
DRIVERS_LICENSE_RE = re.compile(r"\b[A-Z0-9]{5,15}\b")

_CUSTOM_RULES: list[tuple[re.Pattern[str], str]] = [
    (EMAIL_RE, "[EMAIL]"),
    (SSN_RE, "[SSN]"),
    (CC_RE, "[CC]"),
    (IP_RE, "[IP]"),
    (PHONE_RE, "[PHONE]"),
    (PASSPORT_RE, "[PASSPORT]"),
]


@lru_cache(maxsize=1)
def _presidio_engine():
    try:
        from presidio_analyzer import AnalyzerEngine  # type: ignore[import-untyped]
        from presidio_anonymizer import AnonymizerEngine  # type: ignore[import-untyped]

        return AnalyzerEngine(), AnonymizerEngine()
    except ImportError:
        return None, None


def _apply_regex_rules(text: str) -> str:
    for pattern, placeholder in _CUSTOM_RULES:
        text = pattern.sub(placeholder, text)
    return text


def _apply_presidio(text: str) -> str:
    analyzer, anonymizer = _presidio_engine()
    if analyzer is None or anonymizer is None:
        return text
    results = analyzer.analyze(text=text, language="en")
    if not results:
        return text
    return anonymizer.anonymize(text=text, analyzer_results=results).text


async def redact(text: str, *, settings: MemorySettings | None = None) -> str:
    """Return `text` with PII replaced by placeholders."""
    from ..settings import MemorySettings

    cfg = settings or MemorySettings()
    if cfg.presidio_enabled:
        text = _apply_presidio(text)
    return _apply_regex_rules(text)
