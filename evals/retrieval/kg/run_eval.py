"""KG retrieval eval runner (recall@k, MRR, personalized lift)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

from schemas.common import Provenance  # noqa: E402
from schemas.graph import EdgeKind, KGEdge, KGNode, KGHybridInput, KGSearchInput, NodeKind  # noqa: E402

from graphrag_service.default_service import DefaultGraphRAGService  # noqa: E402
from graphrag_service.ingest.pipeline import IngestionPipeline, RawDocument  # noqa: E402


def _recall_at_k(expected: list[str], retrieved: list[str], k: int) -> float:
    if not expected:
        return 1.0
    top = set(retrieved[:k])
    hits = sum(1 for name in expected if name in top)
    return hits / len(expected)


def _mrr(expected: list[str], retrieved: list[str]) -> float:
    for idx, name in enumerate(retrieved, start=1):
        if name in expected:
            return 1.0 / idx
    return 0.0



async def _seed_service() -> DefaultGraphRAGService:
    svc = DefaultGraphRAGService()
    corpus = ROOT / "services" / "graphrag" / "fixtures" / "seed_corpus" / "fractions.md"
    text = corpus.read_text(encoding="utf-8")
    pipeline = IngestionPipeline(svc)
    await pipeline.run(
        RawDocument(
            id="fractions-seed",
            title="Fractions Seed",
            text=text,
            source=Provenance(kind="import", id="fractions-seed"),
        )
    )

    learner_id = "learner-eval-1"
    await svc.upsert_node(
        KGNode(id=f"learner:{learner_id}", kind=NodeKind.LEARNER, canonical_name=learner_id)
    )
    mastered = {
        "Fractions",
        "Division",
        "Equivalent Fractions",
        "Common Misconception",
        "Adding Fractions",
    }
    for node in list(svc._nodes.values()):
        if node.kind == NodeKind.CONCEPT and node.canonical_name in mastered:
            await svc.upsert_edge(
                KGEdge(
                    id=f"m:{node.id}",
                    kind=EdgeKind.MASTERS,
                    src=f"learner:{learner_id}",
                    dst=node.id,
                    properties={"score": 0.9},
                )
            )
    return svc


async def run_eval(config_path: Path) -> dict[str, float]:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    svc = await _seed_service()
    recalls: list[float] = []
    mrrs: list[float] = []
    hybrid_scores: list[float] = []
    personalized_scores: list[float] = []

    for item in cfg["queries"]:
        expected = item["expected_node_names"]
        query = item["query"]
        rows = await svc.search(KGSearchInput(query=query, k=10))
        names = [r.node.canonical_name for r in rows]
        recalls.append(_recall_at_k(expected, names, 10))
        mrrs.append(_mrr(expected, names))

        hybrid_rows = await svc.hybrid(KGHybridInput(query=query, k=10, depth=2))
        pers_rows = await svc.personalized(learner_id="learner-eval-1", query=query, k=10)
        hybrid_scores.append(sum(r.score for r in hybrid_rows[:3]) / min(3, len(hybrid_rows) or 1))
        personalized_scores.append(sum(r.score for r in pers_rows[:3]) / min(3, len(pers_rows) or 1))

    recall_at_10 = sum(recalls) / len(recalls)
    mrr = sum(mrrs) / len(mrrs)
    hybrid_avg = sum(hybrid_scores) / len(hybrid_scores)
    personalized_avg = sum(personalized_scores) / len(personalized_scores)
    lift = (personalized_avg - hybrid_avg) / hybrid_avg if hybrid_avg > 0 else 0.0
    return {
        "recall_at_10": recall_at_10,
        "mrr": mrr,
        "personalized_lift": lift,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run KG retrieval evals.")
    parser.add_argument(
        "--config",
        default=str(ROOT / "evals" / "retrieval" / "kg" / "queries.yaml"),
    )
    args = parser.parse_args()
    metrics = asyncio.run(run_eval(Path(args.config)))
    thresholds = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))["thresholds"]
    ok = (
        metrics["recall_at_10"] >= thresholds["recall_at_10"]
        and metrics["mrr"] >= thresholds["mrr"]
        and metrics["personalized_lift"] >= thresholds["personalized_lift"]
    )
    print({"ok": ok, "metrics": metrics, "thresholds": thresholds})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
