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
- Running: All 6 students simultaneously

## Satisfaction Targets
- Each student: ≥ 7/10 satisfaction at Month-4 checkpoint
- Platform score: ≥ 7.5/10
- No P0 issues remaining
- No P1 issues older than 2 rounds
