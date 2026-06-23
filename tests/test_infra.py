"""Infra smoke tests — keep CI green without external services."""

from __future__ import annotations

from pathlib import Path


def test_repo_layout() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "infra" / "docker-compose.yml").is_file()
    assert (root / "infra" / "alembic.ini").is_file()
    assert (root / "Makefile").is_file()


def test_alembic_model_metadata() -> None:
    from app.stores.models import Base as GatewayBase
    from memory_service.stores.models import Base as MemoryBase

    assert "episodic_memories" in MemoryBase.metadata.tables
    assert "gateway_users" in GatewayBase.metadata.tables
