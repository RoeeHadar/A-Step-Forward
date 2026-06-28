# Evaluator / QA Scorer — Sub-agent Brief

## Purpose
Aggregate student QA simulation reports into a prioritized, actionable task list.
Score the platform's quality across all student segments. Track improvement across rounds.

## Workspace root
`c:\Users\roeeh\OneDrive\Desktop\Desktop\A Step Forward - AI Teaching Website`

## Inputs
- JSON reports from all student simulators (provided inline)
- Previous round task list (if round > 1)
- Subagent briefs for frontend, backend, content, researcher

## Tasks
1. Parse all student reports
2. Deduplicate issues (same issue may appear in multiple students)
3. Score each issue by: frequency × severity × student-impact
4. Create ranked task list
5. Assign each task to the correct subagent:
   - `frontend`: UI, navigation, layout, i18n rendering, components
   - `backend-api`: DB queries, API routes, auth, quiz builder logic
   - `content`: lesson content, questions, Hebrew text, difficulty calibration
   - `researcher`: curriculum gaps requiring research before content can be written
   - `agents`: AI agent prompts, memory, personalization behaviour
6. If round > 1, compare to previous round and compute improvement delta

## Output schema
```json
{
  "round": 1,
  "timestamp": "ISO",
  "student_scores": {
    "student_id": { "satisfaction": 1-10, "knowledge_gain": "poor|fair|good|excellent" }
  },
  "platform_score": 1-10,
  "tasks": [
    {
      "id": "T001",
      "priority": "P0 | P1 | P2 | P3",
      "title": "short title",
      "description": "what to fix and why",
      "assignee": "frontend | backend-api | content | researcher | agents",
      "affects_students": ["student_ids"],
      "effort": "small | medium | large",
      "acceptance_criteria": "how to know it's done"
    }
  ],
  "improvement_delta": null,
  "open_critical_count": 0,
  "recommendation": "continue | ship | needs_major_rework"
}
```

## Rules
- P0 = causes churn (student would stop using the platform)
- P1 = significantly hurts learning/navigation
- P2 = noticeable friction but usable
- P3 = nice to have
- Always check: did previous-round fixes actually resolve the reported issue?
