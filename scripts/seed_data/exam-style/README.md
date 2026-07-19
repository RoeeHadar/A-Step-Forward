# Exam-style corpus (ASF original)

Original multi-part Bagrut / university-finals practice items used as the
**primary reference** for weekly gates, `/app/quiz`, and LLM mock exams.

## Rules

- `source` must be `asf_original` — never MoE transcripts.
- Official PDFs under `apps/web/public/content/bagrut/` are **style reference only**.
- Every part must be uniquely solvable; include worked solutions + rubrics.
- Prefer hard / very_hard multi-part (א–ג) items (~20–25 pts).

## Build

```bash
node scripts/build-exam-style-corpus.mjs
```

Writes `apps/web/src/lib/exam-style-corpus.generated.json` (authored JSON +
extracted open items from `scripts/seed_data/mock_exams/`).
