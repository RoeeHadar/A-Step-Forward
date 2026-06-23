"""PII redaction tests."""

from __future__ import annotations

import pytest

from memory_service.hygiene.pii import redact
from memory_service.settings import MemorySettings


@pytest.mark.asyncio
async def test_email_redacted() -> None:
    out = await redact("Email bob@test.org now", settings=MemorySettings(presidio_enabled=False))
    assert "[EMAIL]" in out
    assert "bob@test.org" not in out


@pytest.mark.asyncio
async def test_ssn_redacted() -> None:
    out = await redact("SSN 123-45-6789", settings=MemorySettings(presidio_enabled=False))
    assert "[SSN]" in out
