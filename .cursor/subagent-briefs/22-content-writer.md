# Content Writer — Sub-agent Brief

## Purpose
Write and improve lesson content in `scripts/seed_data/lessons/*.json` based on:
1. Researcher gap reports
2. Student QA feedback
3. Israeli Bagrut curriculum requirements

## Workspace root
`c:\Users\roeeh\OneDrive\Desktop\Desktop\A Step Forward - AI Teaching Website`

## Lesson JSON schema
```json
{
  "id": "concept_id",
  "title_en": "...", "title_he": "...",
  "math_track": ["3pt","4pt","5pt"],
  "est_minutes": 25,
  "sections": [
    {
      "id": "section_slug",
      "title_en": "...", "title_he": "...",
      "body_en_md": "...", "body_he_md": "...",
      "body_by_level": {
        "3pt": { "body_en_md": "...", "body_he_md": "..." },
        "4pt": { "body_en_md": "...", "body_he_md": "..." },
        "5pt": { "body_en_md": "...", "body_he_md": "..." }
      }
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq | open",
      "difficulty": "easy | medium | hard",
      "level_focus": "3pt | 4pt | 5pt",
      "body_en": "...", "body_he": "...",
      "options_en": ["A", "B", "C", "D"],
      "options_he": ["א", "ב", "ג", "ד"],
      "answer_en": "...", "answer_he": "...",
      "explanation_en": "...", "explanation_he": "...",
      "skill_atoms": ["skill description"]
    }
  ]
}
```

## Difficulty calibration rules
- **3pt**: Concrete, numeric examples. Avoid letters where possible. 
  Step-by-step with explanations at every step. Minimal theory.
  No calculus, no open/closed interval notation, no P(x)/Q(x) notation.
- **4pt**: Adds parametric problems, some proofs, wider trig.
  Still example-driven. 1 theory paragraph max before an example.
- **5pt**: Full analytic treatment. Can use formal notation.
  Expects 4pt mastery. Includes harder edge cases.
- **hs_physics**: Practical, formula-based. Tie to real Bagrut questionnaire Q numbers.

## Question writing rules  
- Hard for 3pt ≠ Hard for 5pt — calibrate to the level
- At least 3 question types per concept (MCQ + open + word problem)
- Include at least 1 question that mirrors a past Bagrut question type
- Hebrew must be real Hebrew, not copied English with Hebrew formatting

## Output
Edit the JSON file directly. After editing, verify:
- All sections have `body_he_md` that is real Hebrew (not English)
- Question count ≥ 6 per lesson, ≥ 2 per level
- All `body_by_level` keys populated for the lesson's `math_track`
