# concept-resolver — Baseline Numbers

Captured: 2026-07-24  
Resolver mode: **baseline** (substring matching — `findRelevantConcepts()` in `apps/web/src/app/api/chat/route.ts`)  
Total cases: **80**

## Per-kind recall

| kind        | total | hits | recall |
|-------------|------:|-----:|-------:|
| exact       |    24 |   24 | 100 %  |
| morphology  |    24 |    0 |   0 %  |
| paraphrase  |    11 |    0 |   0 %  |
| phenomenon  |     9 |    0 |   0 %  |

## Negative false-positive rate

| metric              | value |
|---------------------|------:|
| total negatives     |    12 |
| false positives     |     0 |
| FP rate             |   0 % |

## Floor assertions (CI gates)

| assertion                         | threshold | actual | status |
|-----------------------------------|:---------:|-------:|:------:|
| exact recall ≥ 0.90               |    0.90   |  1.00  |  ✅    |
| negative FP rate ≤ 0.20           |    0.20   |  0.00  |  ✅    |

## Gap analysis

The baseline (pure substring match) achieves **perfect recall on exact
matches** — when the learner types a concept's exact English name, Hebrew
name, or ID (with spaces), it is found today.

However, all morphology, paraphrase, and phenomenon cases score **0%**.
This measures the gap that `resolveConceptsTiered()` (tier: `alias`) must
close:

| kind       | failing messages                                                      |
|------------|-----------------------------------------------------------------------|
| morphology | Hebrew inflected forms: "הנגזרת", "בפונקציות הריבועיות", "בעיית קיצון", "כלל שרשרת", ... (24 cases) |
| paraphrase | Natural rephrasing: "how to find the vertex of a parabola", "איך מוצאים שיפוע הגרף" ... (11 cases) |
| phenomenon | Phenomenon descriptions: "why does the ball slow down going up", "הכדור מאט" ... (9 cases) |

## Test runner

```bash
pnpm --filter @asf/web test -- concept-resolver
```

Runner: `apps/web/src/lib/__tests__/concept-resolver.eval.test.ts`  
Cases: `evals/retrieval/concept-resolver/cases.json`

When `apps/web/src/lib/concept-resolver.ts` is present, the test
automatically switches from `baseline` → `tiered` mode and re-reports
numbers. Promote a new baseline here once tiered mode beats the thresholds.
