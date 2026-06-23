"""Post-ingestion verification pass."""

from __future__ import annotations

import random

import structlog
from schemas.graph import Claim, Extraction

log = structlog.get_logger(__name__)


class VerificationResult:
    def __init__(self) -> None:
        self.checked = 0
        self.flagged = 0


class Verifier:
    def __init__(self, sample_rate: float = 0.1) -> None:
        self.sample_rate = sample_rate

    def sample_claims(self, extraction: Extraction) -> list[Claim]:
        if not extraction.claims:
            return []
        if self.sample_rate >= 1.0:
            return extraction.claims
        k = max(1, int(len(extraction.claims) * self.sample_rate))
        return random.sample(extraction.claims, k=min(k, len(extraction.claims)))

    async def verify(self, extraction: Extraction) -> VerificationResult:
        result = VerificationResult()
        claims = self.sample_claims(extraction)
        for claim in claims:
            result.checked += 1
            if claim.confidence < 0.5:
                result.flagged += 1
                log.info(
                    "verification.flagged",
                    statement=claim.statement[:120],
                    confidence=claim.confidence,
                )
        if extraction.confidence < 0.5 or extraction.notes == "low_confidence":
            result.flagged += 1
        return result
