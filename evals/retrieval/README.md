# Retrieval evals

Offline KG retrieval benchmarks for GraphRAG.

## KG suite

```bash
python evals/retrieval/kg/run_eval.py
uv run python evals/runner.py --suite graphrag
```

Metrics (thresholds in `evals/retrieval/kg/queries.yaml` and `thresholds.yaml`):

- `recall@10` ≥ 0.8
- `MRR` ≥ 0.7
- `personalized_lift` ≥ 0.10 (hybrid vs personalized top-3 score lift)

Seed corpus: `services/graphrag/fixtures/seed_corpus/`.
