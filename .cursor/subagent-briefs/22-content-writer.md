# Content Writer — Sub-agent Brief

## Run mode
- **Model: Composer 2.5 only.** Coordinator must pass `model: "composer-2.5-fast"` on every dispatch.
- Do NOT run as Sonnet or Opus. Those are reserved for the Coordinator.
- Coordinator dispatches with `subagent_type: generalPurpose`, `model: "composer-2.5-fast"`.

## Pedagogical goal
The platform must provide **full coverage of all topics** relevant to the Bagrut and Israeli university courses — in the same **nature** as Geva (יואל גבע) and Goren (בני גורן) textbooks. This does NOT mean matching their page count. It means:
- Every sub-topic is covered with the same pedagogical rigour: definition → theory → worked examples → checkpoints → exercises → method guide → exam prep
- Students who study only on this platform should be able to reach the required level for their exam
- No topic in the Bagrut/university syllabus should be missing or superficial
- The difficulty escalation (easy → medium → hard) must reach the actual exam question level — not a simplified version

## Primary mission — Goren/Geva pedagogical format

**Every lesson on this platform must look like an Israeli textbook chapter by Beni Goren or Yoel Geva.** These books are the gold standard for Bagrut math preparation. Their structure per sub-topic is the required output format for ALL lessons.

### The Goren/Geva section sequence (mandatory order):

1. **`intro`** — Why this topic exists, where it appears in Bagrut/university exams, what the student will be able to do after mastering it.
2. **`definition`** — Formal mathematical definition, clean and precise. For physics: the governing law/formula.
3. **`theory`** — Explanation, intuition, key observations, decision strategy overview. Max 2 paragraphs before the first example.
4. **`worked_example` (easy, #1)** — Mechanical application, 4-5 explicit steps, full LaTeX, bilingual. Students see exactly what to write.
5. **`checkpoint`** (after easy example) — 1 question the student must solve before continuing. Solution in `checkpoint_solution_en/he`.
6. **`worked_example` (medium, #2)** — Multi-step, includes a common twist. Full solution.
7. **`checkpoint`** (after medium example) — Medium difficulty question. Solution provided.
8. **`worked_example` (hard, #3)** — Exam-level. May require multiple techniques. Full solution with two methods where relevant.
9. **`method_guide`** — Decision flowchart or table: "How to identify which technique to use". This is the most valued section — students return to it before every exam.
10. **`exercise_set`** — 8–15 graduated exercises stored in the `exercises[]` array: 4 easy, 5 medium, 4 hard. Each has `solution_en/he`.
11. **`pitfall`** — Top 3–5 mistakes students make. Call them out explicitly.
12. **`before_exam`** — Formula table, common exam question patterns, what examiners look for. Looks like a study card.
13. **`summary`** — 3–5 bullet takeaways.

**Not all lessons need all sections.** Short focused topics can omit `definition` if redundant, or collapse medium/hard examples. But `worked_example` (with difficulty) + `checkpoint` + `exercise_set` + `before_exam` are **always required**.

---

## Section JSON schema

```json
{
  "kind": "worked_example",
  "difficulty": "easy",
  "example_number": 1,
  "title_en": "Worked Example 1 — Direct Substitution",
  "title_he": "דוגמה פתורה 1 — הצבה ישירה",
  "body_en_md": "**Given:** ...\n\n**Step 1:** ...\n\n**Step 2:** ...\n\n**Answer:** $x = 5$ ✓",
  "body_he_md": "**נתון:** ...\n\n**שלב 1:** ...\n\n**שלב 2:** ...\n\n**תשובה:** $x = 5$ ✓"
}
```

```json
{
  "kind": "checkpoint",
  "title_en": "Stop & Practice",
  "title_he": "עצור ותרגל",
  "body_en_md": "Compute $\\lim_{x\\to 3}\\frac{x^2-9}{x-3}$ before continuing.",
  "body_he_md": "חשבו $\\lim_{x\\to 3}\\frac{x^2-9}{x-3}$ לפני המשך.",
  "checkpoint_solution_en": "Factor: $(x-3)(x+3)/(x-3) = x+3 \\to 6$. ∎",
  "checkpoint_solution_he": "פירוק: $x+3 \\to 6$. ∎"
}
```

```json
{
  "kind": "method_guide",
  "title_en": "Choosing the Right Technique",
  "title_he": "איך לבחור את הטכניקה הנכונה",
  "body_en_md": "| Situation | Technique |\n|-----------|----------|\n| ...",
  "body_he_md": "| מצב | טכניקה |\n|-----|--------|\n| ..."
}
```

```json
{
  "kind": "exercise_set",
  "title_en": "Practice Exercises",
  "title_he": "תרגילים",
  "body_en_md": "",
  "body_he_md": "",
  "exercises": [
    {
      "id": "e1",
      "difficulty": "easy",
      "body_en": "...",
      "body_he": "...",
      "solution_en": "...",
      "solution_he": "...",
      "points": 5
    }
  ]
}
```

```json
{
  "kind": "before_exam",
  "title_en": "Before the Exam — Summary",
  "title_he": "לפני הבחינה — סיכום",
  "body_en_md": "### Key Formulas\n...\n\n### Common Exam Patterns\n...\n\n### What Examiners Check\n...",
  "body_he_md": "### נוסחאות מפתח\n...\n\n### תבניות שאלות נפוצות\n...\n\n### מה הבוחנים בודקים\n..."
}
```

---

## Lesson-level schema (unchanged fields)

```json
{
  "id": "concept_id",
  "title_en": "...",
  "title_he": "...",
  "summary_en": "One sentence: what this lesson covers.",
  "summary_he": "משפט אחד: מה השיעור מכסה.",
  "math_track": ["3pt", "4pt", "5pt"],
  "est_minutes": 45,
  "version": 2,
  "sections": [ ... ],
  "questions": [ ... ]
}
```

`est_minutes` should now reflect the **real** study time in Goren/Geva format: 
- Short focused lesson: 30–40 min
- Full topic with exercises: 50–70 min  
- Combined exam-prep lesson: 80–90 min

---

## Questions array (end-of-lesson quiz)

Keep the `questions[]` array for the lesson quiz panel, but the **main learning** happens through the section exercises. Questions should be `type: "open"` primarily, calibrated to Bagrut/university level:

```json
{
  "id": "q1",
  "type": "open",
  "difficulty": "medium",
  "points": 12,
  "body_en": "...",
  "body_he": "...",
  "expected_steps_en": "Step-by-step solution outline...",
  "expected_steps_he": "...",
  "sample_solution_en": "Full worked solution...",
  "sample_solution_he": "...",
  "rubric_en": "Marking scheme...",
  "rubric_he": "...",
  "skill_atoms": ["skill_atom_id"]
}
```

---

## Difficulty calibration

| Level | Worked Examples | Exercise Difficulty | Theory Depth |
|-------|----------------|-------------------|--------------|
| 3pt | Concrete, numeric, no letters | Easy–medium | Minimal, example-first |
| 4pt | Parametric, some proofs | Medium–hard | 1 theory paragraph before example |
| 5pt | Full analytic, formal notation | Hard + proof | Full treatment including edge cases |
| hs_physics | Formula derivation, Bagrut patterns | Real Bagrut Q types | Law → formula → example |
| calc1/la | Proof-level, $\varepsilon$-$\delta$ | Hard + proof exam level | Full rigorous treatment |

---

## LaTeX rules

- All LaTeX in JSON strings must use **escaped backslashes**: `\\frac`, `\\lim`, `\\sin`, `\\sqrt`, `\\infty`, `\\to`, `\\cdot`, `\\leq`, `\\geq`, `\\in`, `\\forall`, `\\exists`, `\\Rightarrow`.
- Inline: `$...$`, display: `$$...$$`.
- Hebrew direction is RTL — keep LaTeX left-to-right inside `$...$`.

---

## Hebrew quality rule

`body_he_md` must be real, natural Hebrew — not a translation of English structure. Math terminology in Hebrew:
- limit → גבול, derivative → נגזרת, integral → אינטגרל, continuous → רציפה, series → טור, sequence → סדרה, vector → וקטור, matrix → מטריצה, eigenvalue → ערך עצמי, determinant → דטרמיננטה, probability → הסתברות, function → פונקציה, equation → משוואה.

---

## Output verification checklist

Before finishing any lesson file, confirm:
- [ ] All new section kinds present: `worked_example` x3 (easy/medium/hard), `checkpoint` x2, `method_guide`, `exercise_set` (≥8 exercises), `before_exam`
- [ ] All sections have both `body_en_md` and `body_he_md` with real content
- [ ] All `difficulty` and `example_number` fields set on `worked_example` sections
- [ ] All `checkpoint_solution_en/he` fields populated
- [ ] `exercises[]` array has ≥8 items with `solution_en/he`
- [ ] `est_minutes` updated to realistic value
- [ ] Valid JSON (no trailing commas, properly escaped LaTeX)
