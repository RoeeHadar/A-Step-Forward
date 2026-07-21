# QA Round — 2026-07-21-adr0010-building

| Field | Value |
|-------|-------|
| Seed variant | `building` (locked — all crews) |
| Focus | Pilot + ADR-0010 |
| Runtime | Cursor Auto (CrewAI YAML = contract only) |
| Mode | Closed (ADR-0010 P0 journeys green on prod) |
| Iteration | **3 / 4** (closed; unanimous-clean false — F1/F2 + Playwright + Clerk HTTP deferred) |
| Ship | `0b61077b` mock-exam RSC + gate advance |

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
