# QA Round — 2026-07-21-adr0010-building

| Field | Value |
|-------|-------|
| Seed variant | `building` (locked — all crews) |
| Focus | Pilot + ADR-0010 |
| Runtime | Cursor Auto (CrewAI YAML = contract only) |
| Mode | Plan + report → Cursor streams execute |
| Iteration | 1 / 4 max |

## Layout

```
docs/qa/rounds/2026-07-21-adr0010-building/
  README.md
  integration.md
  ui.md
  qa.md
  security.md
  evals.md
  deliberation.md
  iterations/
    1.md
```

## Variant fingerprint (`building`)

Expect roughly: readiness mock-capped ~70%, multi-week plan, rich interactive start.
Re-seed: `node scripts/seed-pilot-demo.mjs --variant building`
