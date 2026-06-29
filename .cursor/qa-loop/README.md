# QA Loop — Coordinator Tracking

## Student Roster

| ID | Name | Grade | Level | Goal | Key Trait |
|----|------|-------|-------|------|-----------|
| S01 | Itay | 11 | 4pt math | Bagrut in 4 months | Stressed, shaky fundamentals |
| S02 | Noa | 12 | 5pt math | Bagrut in 2 months | Strong, needs advanced depth |
| S03 | Yossi | 10 | 3pt math | Bagrut in 18 months | Very weak, first year HS |
| S04 | Amir | 11 | hs_physics | Physics Bagrut in 6 months | Physics student, math ok |
| S05 | Maya | 19 | university | Technion calc/LA prep | Post-Bagrut, university prep |
| S06 | Tamar | 12 | 4pt math | Bagrut in 2 months | Procrastinator, unmotivated |

## Specialist Agents

**Run mode (mandatory):** Every QA-loop subagent runs in **Cursor Auto** — not Sonnet, not Opus, not Composer 2.5 unless Auto routes there. When dispatching via Task, **do not pass a `model` override** (let Cursor Auto route). When opening manual chats, set the model picker to **Auto**.

| Role | Brief | Purpose |
|------|-------|---------|
| Student QA | `20-student-qa-simulator.md` | Simulate student experience |
| Researcher | `21-content-researcher.md` | Research curriculum gaps |
| Content Writer | `22-content-writer.md` | Write/fix lesson content |
| Evaluator | `23-evaluator.md` | Aggregate scores + tasks |
| Frontend | `01-frontend.md` | Fix UI/UX issues |
| Backend | `02-backend-api.md` | Fix API/DB issues |

## Round Log

### Round 0 (pre-fixes baseline)
- Itay simulation identified 19 issues (see chat transcript)

### Round 1 (after initial fixes)
- Fixed: lessons navigation, sidebar, quiz level filter, exam countdown, onboarding sliders
- Platform avg ~6.2/10

### Round 2–4
- Fixed: Study NOW card, track-filtered lessons, la_determinants rebuild, artifact removal (21 files), section labels, analytic_geometry 5pt scope + questions, arithmetic 3pt Hebrew
- R4 avg: 7.92/10

### Round 5 (final check — 633152a9)
- **Avg: 8.20/10** | **Satisfied (≥8.5): 2/6** — Noa 8.5, Amir 8.5
- Verified: arithmetic 3pt Hebrew, analytic_geometry Q7–Q10 schema
- **Continue loop** — top blockers: la_determinants Hebrew stubs (Maya), re-engagement nudge (Tamar), Bagrut exam mode (Itay/Yossi/Tamar)

### Round 6 (in progress — commit 11397c3)
- Pre-flight fixes committed: lesson mock, Learn nav, quiz i18n, recent lessons labels, progress bilingual, memory tab Neon-direct, goal completion banner
- 10 new diverse students launched (see round6-students.md)
- Evaluator + dispatch pending

## Satisfaction Targets
- **Stopping condition: platform score ≥ 8.5 AND no concrete improvements remain**
- Each student: ≥ 8.5/10 satisfaction at Month-4 checkpoint
- No P0 issues remaining
- No P1 issues older than 2 rounds
