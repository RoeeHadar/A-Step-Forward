#!/usr/bin/env pwsh
# Build stacked GraphRAG PR branches from phase-0 skeleton -> full implementation.
$ErrorActionPreference = "Stop"
$Root = "c:\Users\roeeh\OneDrive\Desktop\Desktop\A Step Forward - AI Teaching Website"
$Backup = "$env:TEMP\asf-graphrag-backup"
Set-Location $Root

function Restore-GraphragFull {
  Copy-Item -Recurse -Force "$Backup\graphrag\*" "services/graphrag"
  Copy-Item -Recurse -Force "$Backup\retrieval\*" "evals/retrieval"
  Copy-Item -Force "$Backup\0002_kg_chunks.py" "infra/alembic/versions/0002_kg_chunks.py"
  Copy-Item -Force "$Backup\graph.py" "packages/schemas/schemas/graph.py"
  Copy-Item -Force "$Backup\env.example" ".env.example"
}

function Set-GraphragPhase0 {
  $paths = @(
    "services/graphrag/graphrag_service/stores",
    "services/graphrag/scripts",
    "services/graphrag/fixtures",
    "services/graphrag/graphrag_service/ingest/sources",
    "services/graphrag/graphrag_service/neo4j_service.py",
    "services/graphrag/graphrag_service/ingest/chunker.py",
    "services/graphrag/graphrag_service/ingest/embedder.py",
    "services/graphrag/graphrag_service/ingest/extractor.py",
    "services/graphrag/graphrag_service/ingest/resolver.py",
    "services/graphrag/graphrag_service/ingest/writer.py",
    "services/graphrag/graphrag_service/ingest/verifier.py",
    "services/graphrag/graphrag_service/ingest/snapshot.py",
    "services/graphrag/graphrag_service/ingest/types.py",
    "services/graphrag/graphrag_service/retrieval/queries.py",
    "services/graphrag/tests/test_ontology.py",
    "services/graphrag/tests/test_chunker.py",
    "services/graphrag/tests/test_pipeline.py",
    "services/graphrag/tests/conftest.py",
    "infra/alembic/versions/0002_kg_chunks.py",
    "evals/retrieval/kg/run_eval.py",
    "evals/retrieval/README.md"
  )
  foreach ($p in $paths) { if (Test-Path $p) { Remove-Item -Recurse -Force $p } }

  @'
"""Neo4j schema (constraints + indexes) for the KG ontology."""

from __future__ import annotations

CYPHER_CONSTRAINTS: list[str] = [
    "CREATE CONSTRAINT learner_id IF NOT EXISTS FOR (n:Learner) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT concept_canonical IF NOT EXISTS FOR (n:Concept) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT skill_canonical IF NOT EXISTS FOR (n:Skill) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT topic_canonical IF NOT EXISTS FOR (n:Topic) REQUIRE n.canonical_name IS UNIQUE",
    "CREATE CONSTRAINT course_id IF NOT EXISTS FOR (n:Course) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT lesson_id IF NOT EXISTS FOR (n:Lesson) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (n:Resource) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT assessment_id IF NOT EXISTS FOR (n:Assessment) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (n:Question) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT misconception_id IF NOT EXISTS FOR (n:Misconception) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT goal_id IF NOT EXISTS FOR (n:Goal) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT agent_name IF NOT EXISTS FOR (n:Agent) REQUIRE n.name IS UNIQUE",
]

CYPHER_INDEXES: list[str] = [
    "CREATE INDEX concept_aliases IF NOT EXISTS FOR (n:Concept) ON (n.aliases)",
    "CREATE INDEX lesson_title IF NOT EXISTS FOR (n:Lesson) ON (n.title)",
    "CREATE INDEX resource_title IF NOT EXISTS FOR (n:Resource) ON (n.title)",
    "CREATE INDEX masters_score IF NOT EXISTS FOR ()-[r:MASTERS]-() ON (r.score)",
    "CREATE INDEX prereq_weight IF NOT EXISTS FOR ()-[r:PREREQUISITE_OF]-() ON (r.weight)",
]
'@ | Set-Content -Encoding utf8 "services/graphrag/graphrag_service/ontology/schema.py"

  @'
from .schema import CYPHER_CONSTRAINTS, CYPHER_INDEXES

__all__ = ["CYPHER_CONSTRAINTS", "CYPHER_INDEXES"]
'@ | Set-Content -Encoding utf8 "services/graphrag/graphrag_service/ontology/__init__.py"

  @'
"""GraphRAG retrieval helpers (local, walk, hybrid, personalized).

The actual logic lives on `DefaultGraphRAGService` (Phase 0) and will move into
dedicated query builders in sub-agent 05's implementation.
"""
'@ | Set-Content -Encoding utf8 "services/graphrag/graphrag_service/retrieval/__init__.py"

  @'
from .pipeline import IngestionPipeline, IngestionResult, RawDocument

__all__ = ["IngestionPipeline", "IngestionResult", "RawDocument"]
'@ | Set-Content -Encoding utf8 "services/graphrag/graphrag_service/ingest/__init__.py"

  # pipeline stub already on disk from manual write - keep stub version
  git checkout -- services/graphrag/graphrag_service/ingest/pipeline.py 2>$null
  if (-not (Select-String -Path services/graphrag/graphrag_service/ingest/pipeline.py -Pattern "Ingestion pipeline skeleton" -Quiet)) {
    git show :services/graphrag/graphrag_service/ingest/pipeline.py | Set-Content services/graphrag/graphrag_service/ingest/pipeline.py
    # force stub
  }
  # Use explicit stub
  Copy-Item -Force "$Root\scripts\_graphrag_phase0_pipeline.py" "services/graphrag/graphrag_service/ingest/pipeline.py" -ErrorAction SilentlyContinue

  # settings phase 0
  (Get-Content services/graphrag/graphrag_service/settings.py) |
    Where-Object { $_ -notmatch 'use_neo4j|use_postgres_chunks|snapshot_|verification_sample' } |
    Set-Content services/graphrag/graphrag_service/settings.py

  # api phase 0
  @'
def get_graphrag_service() -> GraphRAGService:
    from .default_service import DefaultGraphRAGService

    return DefaultGraphRAGService()
'@ | Set-Content -Encoding utf8 "services/graphrag/graphrag_service/api_tail.py"
  $api = Get-Content services/graphrag/graphrag_service/api.py -Raw
  $api = $api -replace '(?s)def get_graphrag_service\(\).*', (Get-Content services/graphrag/graphrag_service/api_tail.py -Raw)
  $api | Set-Content -Encoding utf8 services/graphrag/graphrag_service/api.py
  Remove-Item services/graphrag/graphrag_service/api_tail.py

  # pyproject phase 0 deps
  @'
[project]
name = "graphrag-service"
version = "0.1.0"
description = "GraphRAG service over Neo4j + pgvector for A Step Forward."
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.7",
  "pydantic-settings>=2.4",
  "neo4j>=5.22",
  "httpx>=0.27",
  "structlog>=24.1",
  "schemas",
]

[tool.uv.sources]
schemas = { path = "../../packages/schemas", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["graphrag_service"]
'@ | Set-Content -Encoding utf8 services/graphrag/pyproject.toml

  # graph.py remove KGChunk block
  $graph = Get-Content packages/schemas/schemas/graph.py -Raw
  $graph = $graph -replace '(?s)\r?\n\r?\nclass KGChunk\(BaseModel\):.*', ''
  $graph | Set-Content -Encoding utf8 packages/schemas/schemas/graph.py

  # default_service phase 0 - restore from git index first chunk then simplify
  git show :services/graphrag/graphrag_service/default_service.py | Set-Content services/graphrag/graphrag_service/default_service.py
}

# Ensure pipeline stub exists
@'
"""Ingestion pipeline skeleton."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from schemas.common import Provenance
from schemas.graph import KGEdge, KGNode, NodeKind
from ..api import GraphRAGService

@dataclass
class RawDocument:
    id: str
    title: str
    text: str
    source: Provenance
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class IngestionResult:
    document_id: str
    chunks: int
    nodes_written: int
    edges_written: int
    pending_review: int

class IngestionPipeline:
    def __init__(self, service: GraphRAGService) -> None:
        self.service = service

    async def chunk(self, doc: RawDocument) -> list[str]:
        size, overlap = 1200, 100
        text = doc.text
        chunks: list[str] = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + size])
            if i + size >= len(text):
                break
            i += size - overlap
        return chunks

    async def embed(self, chunks: list[str]) -> list[list[float]]:
        return [[0.0] * 1024 for _ in chunks]

    async def extract(self, chunks: list[str], doc: RawDocument):
        from schemas.graph import Extraction
        return Extraction(entities=[], relations=[], claims=[], confidence=0.0, notes="low_confidence")

    async def resolve_and_write(self, extraction, doc: RawDocument) -> IngestionResult:
        node = KGNode(
            id=f"resource:{doc.id}",
            kind=NodeKind.RESOURCE,
            canonical_name=doc.title,
            summary=doc.text[:200],
            provenance=doc.source,
            pending_review=False,
        )
        await self.service.upsert_node(node)
        return IngestionResult(document_id=doc.id, chunks=0, nodes_written=1, edges_written=0, pending_review=0)

    async def run(self, doc: RawDocument) -> IngestionResult:
        chunks = await self.chunk(doc)
        _embs = await self.embed(chunks)
        extraction = await self.extract(chunks, doc)
        result = await self.resolve_and_write(extraction, doc)
        result.chunks = len(chunks)
        return result
'@ | Set-Content -Encoding utf8 "$Root\scripts\_graphrag_phase0_pipeline.py"

Set-GraphragPhase0

# Stage all non-graphrag unstaged + graphrag phase0
git add -A

if (-not (git rev-parse HEAD 2>$null)) {
  git commit -m "$(cat <<'EOF'
chore: initial monorepo scaffold

Phase-0 foundation for A Step Forward including GraphRAG skeleton service.
EOF
)"
} else {
  Write-Host "HEAD exists, skipping initial commit"
}

git checkout -B feat/graphrag/01-ontology-migration
# Phase 1 restore
Copy-Item -Recurse -Force "$Backup\graphrag\graphrag_service\stores" "services/graphrag/graphrag_service/stores"
Copy-Item -Recurse -Force "$Backup\graphrag\scripts" "services/graphrag/scripts"
Copy-Item -Force "$Backup\0002_kg_chunks.py" "infra/alembic/versions/0002_kg_chunks.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\ontology\schema.py" "services/graphrag/graphrag_service/ontology/schema.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\ontology\__init__.py" "services/graphrag/graphrag_service/ontology/__init__.py"
Copy-Item -Force "$Backup\graphrag\tests\test_ontology.py" "services/graphrag/tests/test_ontology.py"
Copy-Item -Force "$Backup\graphrag\tests\conftest.py" "services/graphrag/tests/conftest.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\settings.py" "services/graphrag/graphrag_service/settings.py"
Copy-Item -Force "$Backup\graphrag\pyproject.toml" "services/graphrag/pyproject.toml"
# graph.py with KGChunk
$g = Get-Content "$Backup\graph.py" -Raw
if ($g -match 'class KGChunk') { Copy-Item -Force "$Backup\graph.py" "packages/schemas/schemas/graph.py" }
git add services/graphrag infra/alembic/versions/0002_kg_chunks.py packages/schemas/schemas/graph.py
git commit -m "$(cat <<'EOF'
feat(graphrag): ontology migration and kg_chunks table

Add Neo4j schema apply script, store layer scaffolding, pgvector kg_chunks
Alembic migration, and KGChunk schema.
EOF
)"

git checkout -B feat/graphrag/02-ingestion-pipeline
Copy-Item -Recurse -Force "$Backup\graphrag\graphrag_service\ingest" "services/graphrag/graphrag_service/ingest"
Copy-Item -Recurse -Force "$Backup\graphrag\fixtures" "services/graphrag/fixtures"
Copy-Item -Force "$Backup\graphrag\scripts\ingest_seed.py" "services/graphrag/scripts/ingest_seed.py"
Copy-Item -Force "$Backup\graphrag\tests\test_chunker.py" "services/graphrag/tests/test_chunker.py"
Copy-Item -Force "$Backup\graphrag\tests\test_pipeline.py" "services/graphrag/tests/test_pipeline.py"
git add services/graphrag
git commit -m "$(cat <<'EOF'
feat(graphrag): ingestion pipeline and seed corpus

Wire chunk, embed, extract, resolve, write, and verify stages with source
connectors and offline fallbacks for local dev.
EOF
)"

git checkout -B feat/graphrag/03-retrieval-modes
Copy-Item -Force "$Backup\graphrag\graphrag_service\neo4j_service.py" "services/graphrag/graphrag_service/neo4j_service.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\retrieval\queries.py" "services/graphrag/graphrag_service/retrieval/queries.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\retrieval\__init__.py" "services/graphrag/graphrag_service/retrieval/__init__.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\default_service.py" "services/graphrag/graphrag_service/default_service.py"
Copy-Item -Force "$Backup\graphrag\graphrag_service\api.py" "services/graphrag/graphrag_service/api.py"
git add services/graphrag
git commit -m "$(cat <<'EOF'
feat(graphrag): retrieval modes and Neo4j service

Add local, walk, hybrid, and personalized retrieval plus Neo4jGraphRAGService.
EOF
)"

git checkout -B feat/graphrag/04-mcp-evals
Restore-GraphragFull
git add services/graphrag evals/retrieval packages/schemas/schemas/graph.py .env.example
git commit -m "$(cat <<'EOF'
feat(graphrag): MCP wiring and retrieval evals

Add KG retrieval eval suite, seed ingest CLI, and service factory toggles.
EOF
)"

Write-Host "Branches ready:" 
git log --oneline --decorate --graph --all -n 10
