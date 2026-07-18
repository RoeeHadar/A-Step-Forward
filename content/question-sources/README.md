# Question sources — staging area

Drop transcribed source material here, one subfolder per tier. Ingestion
(`scripts/ingest-question-sources.mjs`) reads these and enforces the source-tier
policy. This folder is an authoring-time input; nothing here ships to learners
directly.

## Tiers

| Tier | Folder | License | Handling |
|------|--------|---------|----------|
| MoE Meyda (official Bagrut exams) | `moe_meyda/` | `public-official` | Stored **verbatim**; official answer keys become verifier ground truth; `display_publicly` allowed. |
| Hebrew Wikibooks | `wikibooks/` | CC BY-SA 4.0 (copyleft) | **Style-only.** Emits metadata-only seeds; no source text is stored. |
| motib/bagrut, the-openclass.org | `motib/`, `openclass/` | none / all-rights-reserved | **Style-only.** Same as above. |

## Raw item shape (JSON array per file)

```jsonc
{
  "concept_id": "derivatives_rules",
  "subject": "math",
  "level": "high_school",
  "math_track": ["5pt"],
  "points_level": "5pt",
  "kind": "short_answer",              // or a multi-part item via "parts": [...]
  "difficulty": "medium",
  "stem_en": "...", "stem_he": "...",
  "answer_payload": { "acceptable_answers": ["..."] },
  "explanation_en": "", "explanation_he": "",
  "skill_atoms": ["chain_rule"],
  "verify": { "check": "derivative", "of": "sin(x**2)", "var": "x", "claimed": "2*x*cos(x**2)" },
  "source_ref": "MoE Meyda 2023 Summer 35582 Q3",
  "official_answer": "2*x*cos(x**2)",   // ground truth for the verifier (moe_meyda)
  "display_publicly": true               // moe_meyda only
}
```

Multi-part (composite) items: set top-level `stem_en`/`stem_he` to the shared
stem and provide `parts: [{ ord, kind, stem_en, stem_he, answer_payload, ... }]`.

## Assisted transcription (MoE Meyda)

`scripts/gen/transcribe_moe.py` removes the mechanical work (PDF extraction,
question segmentation, schema scaffolding). It uses `pymupdf`/`pdfplumber`/
`pypdf` if installed, otherwise accepts a `.txt` you extracted yourself.

```powershell
# 1. drop exams:            content/question-sources/moe_meyda/_pdf/*.pdf   (or _txt/*.txt)
# 2. scaffold drafts:
python scripts/gen/transcribe_moe.py draft --input content/question-sources/moe_meyda/_pdf --exam-id 35582 --year 2023 --season summer
#    -> content/question-sources/moe_meyda/_drafts/35582.draft.json  (reviewed=false, TODO placeholders)
# 3. HUMAN: fix LaTeX math, set concept_id + skill_atoms + kind + answer_payload +
#    official_answer (+ optional CAS verify), set "reviewed": true, and SAVE to
#    content/question-sources/moe_meyda/35582.json
# 4. gate the approved files:
python scripts/gen/transcribe_moe.py check --strict
```

A **fully reviewed / approved** item looks like this (this is the sign-off bar):

```jsonc
{
  "reviewed": true,
  "concept_id": "derivatives_rules",
  "subject": "math", "level": "high_school", "math_track": ["5pt"], "points_level": "5pt",
  "kind": "short_answer", "difficulty": "medium",
  "stem_en": "Differentiate $f(x) = \\sin(x^2)$.",
  "stem_he": "גזרו את $f(x) = \\sin(x^2)$.",
  "answer_payload": { "acceptable_answers": ["2*x*cos(x**2)", "2x\\cos(x^2)"] },
  "explanation_en": "Chain rule: outer sin, inner x^2.",
  "explanation_he": "כלל שרשרת: חיצוני sin, פנימי x^2.",
  "skill_atoms": ["chain_rule"],
  "verify": { "check": "derivative", "of": "sin(x**2)", "var": "x", "claimed": "2*x*cos(x**2)" },
  "official_answer": "2*x*cos(x**2)",
  "display_publicly": true,
  "source_ref": "MoE Meyda 2023 summer 35582 Q3"
}
```

## Pipeline

```powershell
# 1. transcribe (above) -> approved content/question-sources/moe_meyda/*.json
# 2. ingest (applies license policy, writes to content/question-store/ingested|seeds)
node scripts/ingest-question-sources.mjs

# 3. verify + store + (optionally) bake into a lesson
node scripts/pipeline-run.mjs --concept=<id> --generated=content/question-store/ingested/moe_meyda.json --bake --write
```

Style-only tiers never produce store items; they produce seeds under
`content/question-store/seeds/` for the clean-room generator
(`scripts/gen/generate_math_items.py`).
