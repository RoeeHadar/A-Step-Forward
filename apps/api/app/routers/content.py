"""Public content browsing routes (free tier — no auth)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..core.db import get_db
from ..stores import content_store

router = APIRouter(prefix="/v1", tags=["content"])


@router.get("/subjects")
async def list_subjects(session=Depends(get_db)) -> list[dict]:
    return await content_store.list_subjects(session)


@router.get("/subjects/{subject}/sections")
async def list_sections(subject: str, session=Depends(get_db)) -> list[dict]:
    return await content_store.list_sections(session, subject=subject)


@router.get("/subjects/{subject}/sections/{chunk_index}")
async def get_section(subject: str, chunk_index: int, session=Depends(get_db)) -> dict:
    row = await content_store.get_section(session, subject=subject, chunk_index=chunk_index)
    if row is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return row


@router.get("/subjects/{subject}/bagrut")
async def list_bagrut(subject: str, session=Depends(get_db)) -> list[dict]:
    return await content_store.list_bagrut_exams(session, subject=subject)
