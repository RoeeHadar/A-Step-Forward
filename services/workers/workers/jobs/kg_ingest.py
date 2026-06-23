"""KG ingestion + verification jobs."""

from __future__ import annotations

from ..celery_app import app


@app.task(name="workers.jobs.kg_ingest.ingest_document")
def ingest_document(document_id: str) -> dict:
    # Sub-agent 05-graphrag implements this against the real pipeline.
    return {"document_id": document_id, "ingested": False, "reason": "phase-0 stub"}


@app.task(name="workers.jobs.kg_ingest.ingest_curriculum")
def ingest_curriculum(course_id: str) -> dict:
    """Project curriculum objectives/concepts into the KG."""
    return {
        "course_id": course_id,
        "ingested": False,
        "reason": "queued for graphrag pipeline",
        "nodes_projected": 0,
    }


@app.task(name="workers.jobs.kg_ingest.verify_recent")
def verify_recent() -> int:
    # Sub-agent 05: sample recent extractions and verify against KG; flag drift.
    return 0
