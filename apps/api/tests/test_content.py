"""Tests for public content browsing routes."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from app.main import create_app  # noqa: E402


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_subjects_public(client: AsyncClient) -> None:
    with patch(
        "app.stores.content_store.list_subjects",
        new=AsyncMock(return_value=[{"subject": "math", "section_count": 3, "sample_grade": "10"}]),
    ):
        resp = await client.get("/v1/content/subjects")
    assert resp.status_code == 200
    body = resp.json()
    assert body[0]["subject"] == "math"
    assert body[0]["section_count"] == 3


@pytest.mark.asyncio
async def test_list_sections_paginated(client: AsyncClient) -> None:
    with patch(
        "app.stores.content_store.list_sections",
        new=AsyncMock(
            return_value=(
                [
                    {
                        "subject": "math",
                        "grade": "10",
                        "title": "Algebra",
                        "body_md": "# Algebra",
                        "page_start": 1,
                        "page_end": 2,
                        "chunk_index": 0,
                    }
                ],
                1,
            )
        ),
    ):
        resp = await client.get("/v1/content/subjects/math/sections?page=1&page_size=20")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Algebra"
    assert body["items"][0]["body_md"] == "# Algebra"


@pytest.mark.asyncio
async def test_list_bagrut_public(client: AsyncClient) -> None:
    with patch(
        "app.stores.content_store.list_bagrut_exams",
        new=AsyncMock(
            return_value=[
                {
                    "display_name": "Math 2024",
                    "file_url": "/content/bagrut/math-2024.pdf",
                    "year": 2024,
                    "exam_type": "summer",
                }
            ]
        ),
    ):
        resp = await client.get("/v1/content/subjects/math/bagrut")
    assert resp.status_code == 200
    body = resp.json()
    assert body[0]["display_name"] == "Math 2024"
    assert body[0]["file_url"] == "/content/bagrut/math-2024.pdf"
