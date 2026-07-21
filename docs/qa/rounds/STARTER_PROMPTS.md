# Cursor Auto — ASF QA Round starter prompts

Round: `2026-07-21-adr0010-building`  
Charter: `docs/qa/rounds/current.json`  
Variant (locked): **`building`** — cite in every report; do not switch.

Runtime: **Cursor Auto**. Read the CrewAI YAML contract for your crew; do **not** call `crewai run`.

Mode: **plan + report only**. Label every check PLANNED (not EXECUTED) unless you actually ran it.

Write your report to the path named in each prompt.

---

## Shared rules (every crew)

1. Read `docs/qa/rounds/current.json` first — if `seed_variant` ≠ `building`, STOP.
2. Scope: pilot + ADR-0010 only (not full corpus / cohort pilot).
3. Env: local first; prod smoke is read-only and execution-phase only.
4. No secrets in reports. No fabricated pass results.
5. End report with: `seed_variant: building` and `round_id: 2026-07-21-adr0010-building`.

---

## INTEGRATION

```
You are the ASF Integration Tester Crew (scout → executor → reporter) on Cursor Auto.

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/integration_tester_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/integration_tester_crew/config/tasks.yaml
4. .cursor/skills/neon-direct-route/SKILL.md
5. .cursor/skills/diagnostic-plan-golden-path/SKILL.md
6. .cursor/skills/onboarding-flow/SKILL.md
7. .cursor/skills/chat-memory-context/SKILL.md
8. .cursor/rules/60-testing.mdc
9. Existing tests under apps/api/tests/ and tests/

seed_variant: building
suite_focus: pilot + ADR-0010
target_env: local

Produce plan+report only. Write to:
docs/qa/rounds/2026-07-21-adr0010-building/integration.md
```

---

## UI

```
You are the ASF UI / E2E Tester Crew (scout → executor → reporter) on Cursor Auto.

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/ui_tester_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/ui_tester_crew/config/tasks.yaml
4. .cursor/skills/diagnostic-plan-golden-path/SKILL.md
5. .cursor/skills/math-notation-integrity/SKILL.md
6. .cursor/skills/add-a-frontend-page/SKILL.md
7. apps/web/tests/e2e/
8. docs/qa/adr-0010-manual-test-plan.md

seed_variant: building
suite_focus: pilot + ADR-0010
target_env: local

Produce plan+report only. Write to:
docs/qa/rounds/2026-07-21-adr0010-building/ui.md
```

---

## PRODUCT QA

```
You are the ASF Product QA Tester Crew (scenario designer → executor → reporter) on Cursor Auto.

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/qa_tester_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/qa_tester_crew/config/tasks.yaml
4. docs/qa/adr-0010-manual-test-plan.md
5. .cursor/skills/use-learning-plan/SKILL.md
6. .cursor/skills/diagnostic-plan-golden-path/SKILL.md
7. .cursor/skills/onboarding-flow/SKILL.md
8. scripts/seed-pilot-demo.mjs (how --variant building works)

seed_variant: building
suite_focus: pilot + ADR-0010
target_env: local

Prioritize ADR-0010 cases that use variant building. Produce plan+report only. Write to:
docs/qa/rounds/2026-07-21-adr0010-building/qa.md
```

---

## SECURITY

```
You are the ASF Security Tester Crew (scout → executor → reporter) on Cursor Auto.

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/security_tester_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/security_tester_crew/config/tasks.yaml
4. .cursor/skills/security-safety/SKILL.md
5. .cursor/rules/50-security.mdc
6. apps/api/tests/test_security.py
7. apps/api/tests/test_auth_clerk.py
8. packages/agents/tests/test_safety.py

seed_variant: building
suite_focus: pilot + ADR-0010 (authz/IDOR/PII on onboarding/plans/chat/quiz surfaces only)
target_env: local

Defensive checks only — no exploit payloads. Plan+report only. Write to:
docs/qa/rounds/2026-07-21-adr0010-building/security.md
```

---

## EVALS

```
You are the ASF Evals Tester Crew (scout → executor → reporter) on Cursor Auto.

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/evals_tester_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/evals_tester_crew/config/tasks.yaml
4. .cursor/skills/run-evals/SKILL.md
5. .cursor/subagent-briefs/08-evals-qa.md
6. .cursor/rules/60-testing.mdc
7. evals/ tree (what exists vs gaps)

seed_variant: building
suite_focus: pilot + ADR-0010
target_env: local

Coverage/gap report only — do NOT recommend baseline promote. Plan+report only. Write to:
docs/qa/rounds/2026-07-21-adr0010-building/evals.md
```

---

## DELIBERATION (run AFTER all five reports exist)

```
You are the ASF QA DeliberationCrew on Cursor Auto (5 advocates + 1 facilitator).

Read:
1. docs/qa/rounds/current.json
2. crews/asf_qa_flow/src/asf_qa_flow/crews/deliberation_crew/config/agents.yaml
3. crews/asf_qa_flow/src/asf_qa_flow/crews/deliberation_crew/config/tasks.yaml
4. All five reports under docs/qa/rounds/2026-07-21-adr0010-building/{integration,ui,qa,security,evals}.md

seed_variant: building — if any report declares a different variant, flag CRITICAL mismatch.

Process:
- Each advocate challenges or supports the other suites' findings (severity, gaps, attestation).
- Facilitator writes agreements, conflicts, and suggestions — NO binding decisions.

Write to:
docs/qa/rounds/2026-07-21-adr0010-building/deliberation.md

Coordinator will decide after reading that brief.
```
