# ASF QA Flow — CrewAI Tester Teams (contract)

**Active runtime: Cursor Auto** — see `docs/qa/rounds/STARTER_PROMPTS.md` and
`docs/qa/rounds/current.json`. Do **not** `crewai run` with external LLMs for
the current round.

| Crew | Role |
|------|------|
| `integration_tester_crew` | API / Neon integration plan+report |
| `ui_tester_crew` | UI / E2E plan+report |
| `qa_tester_crew` | ADR-0010 product QA plan+report |
| `security_tester_crew` | Security plan+report |
| `evals_tester_crew` | Evals gap plan+report |
| `deliberation_crew` | 5 advocates + facilitator (non-binding) |

Shared lock: `seed_variant` from charter (`building` this round) injected into
every task. Coordinator decides after Deliberation.

## Round artifacts

`docs/qa/rounds/<round_id>/` — reports, deliberation, `iterations/N.md`
