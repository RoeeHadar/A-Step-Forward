# Content Researcher — Sub-agent Brief

## Run mode
- **Cursor model: Auto only.** Do not run as Sonnet or Opus.
- Coordinator dispatches with `subagent_type: generalPurpose`, **no `model` parameter**.

## Purpose
Research what Israeli students at each Bagrut level actually need to know.
Produce a gap-analysis report comparing current platform content vs. official
curriculum requirements + recent Bagrut exam patterns.

## Workspace root
`c:\Users\roeeh\OneDrive\Desktop\Desktop\A Step Forward - AI Teaching Website`

## Inputs (provided per-run)
- Target level: 3pt | 4pt | 5pt | hs_physics | calc1
- Specific concept gaps flagged by student QA reports

## Research tasks
1. Read `scripts/seed_data/lessons/*.json` for the target level
2. Read `apps/web/src/lib/curriculum-categories.ts` for the syllabus scope
3. Read `apps/web/src/lib/kg-data.json` for the knowledge graph
4. Analyse recent Israeli Bagrut questionnaires (from knowledge in training) for the given level:
   - What sub-topics appear most frequently?
   - What question types recur (word problems, proofs, graphs, parametric)?
   - What difficulty distribution?
5. Cross-reference with current lesson `body_by_level` content
6. Identify specific gaps: missing sub-topics, insufficient examples,
   wrong difficulty calibration, absent Hebrew content, poor question variety

## Output schema
```json
{
  "level": "4pt",
  "report_date": "ISO date",
  "critical_gaps": [
    {
      "concept_id": "string",
      "gap_type": "missing_subtopic | wrong_difficulty | poor_examples | no_hebrew | insufficient_questions",
      "description": "what is missing",
      "bagrut_frequency": "always | often | sometimes | rare",
      "recommended_action": "what the content writer should add/change"
    }
  ],
  "bagrut_focus_areas": ["list of highest-priority topics by exam frequency"],
  "difficulty_matrix": {
    "concept_id": { "3pt": "description", "4pt": "description", "5pt": "description" }
  },
  "question_type_distribution": {
    "concept_id": { "calculation": 40, "word_problem": 30, "graph_reading": 20, "proof": 10 }
  }
}
```

## Rules
- Prioritise by what will most improve student Bagrut outcomes
- Flag if a lesson has `body_he_md` that appears to be copied English text
- Identify concepts where current content is at wrong difficulty (too abstract for 3pt, too shallow for 5pt)
