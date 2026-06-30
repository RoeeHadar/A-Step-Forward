#!/usr/bin/env python3
"""Author 3 university stats/probability lessons + 2 makhina physics lessons."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"


def _section(sid, title_en, title_he, body_en_md, body_he_md, level_min):
    return {
        "id": sid,
        "title_en": title_en,
        "title_he": title_he,
        "level_min": level_min,
        "body_en_md": body_en_md,
        "body_he_md": body_he_md,
    }


def _mcq(qid, body_en, body_he, options, expl_en, expl_he):
    return {
        "id": qid,
        "type": "mcq",
        "body_en": body_en,
        "body_he": body_he,
        "options": options,
        "explanation_en": expl_en,
        "explanation_he": expl_he,
    }


def _opts(items):
    return [{"id": oid, "text_en": en, "text_he": he, "correct": ok} for oid, en, he, ok in items]


INDEX_ENTRIES = {
    "sample_space": {
        "title_en": "Sample Space, Events & Probability Axioms",
        "title_he": "מרחב מדגם, אירועים ואקסיומות ההסתברות",
        "duration_min": 30,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "random_variables": {
        "title_en": "Random Variables & Probability Distributions",
        "title_he": "משתנים מקריים והתפלגויות",
        "duration_min": 35,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "sampling_estimation": {
        "title_en": "Sampling, Point Estimation & Confidence Intervals",
        "title_he": "דגימה, אמידת נקודה ורווח בר-סמך",
        "duration_min": 35,
        "subject": "statistics_probability",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "mechanics_makhina": {
        "title_en": "Mechanics: Motion, Forces & Newton's Laws",
        "title_he": "מכניקה: תנועה, כוחות וחוקי ניוטון",
        "duration_min": 35,
        "subject": "makhina_physics",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "energy_work_makhina": {
        "title_en": "Energy, Work & Power",
        "title_he": "אנרגיה, עבודה והספק",
        "duration_min": 30,
        "subject": "makhina_physics",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
}


LESSONS: list[dict] = [
    {
        "id": "sample_space",
        "type": "interactive",
        "subject": "statistics_probability",
        "title_en": INDEX_ENTRIES["sample_space"]["title_en"],
        "title_he": INDEX_ENTRIES["sample_space"]["title_he"],
        "duration_min": 30,
        "level_min": "university",
        "agent_hints": (
            "Students confuse 'equally likely' with 'any subset has probability |A|/|Omega|'. "
            "Emphasise that classical probability requires a symmetry argument. "
            "The complement rule P(A^c)=1-P(A) is the standard tool for 'at least one' problems. "
            "De Morgan's laws bridge set operations and probability — draw Venn diagrams first. "
            "Preview combinatorics: hypergeometric sampling without replacement needs careful counting."
        ),
        "sections": [
            _section(
                "random_experiment",
                "Random Experiment & Sample Space",
                "ניסוי מקרי ומרחב מדגם",
                (
                    "A **random experiment** is a procedure whose outcome is uncertain before it is performed.\n\n"
                    "The **sample space** $\\Omega$ is the set of all possible outcomes.\n\n"
                    "**Examples:**\n"
                    "- Flip a coin: $\\Omega = \\{H, T\\}$\n"
                    "- Roll a die: $\\Omega = \\{1, 2, 3, 4, 5, 6\\}$\n"
                    "- Two dice (ordered pairs): $\\Omega = \\{(i,j) : 1 \\leq i,j \\leq 6\\}$, so $|\\Omega| = 36$\n"
                    "- Component lifetime (continuous): $\\Omega = [0, \\infty)$\n\n"
                    "Each **outcome** $\\omega \\in \\Omega$ is one complete result of the experiment. "
                    "For two dice, $(3,5)$ and $(5,3)$ are different outcomes if order matters."
                ),
                (
                    "**ניסוי מקרי** הוא תהליך שתוצאתו אינה ידועה לפני ביצועו.\n\n"
                    "**מרחב המדגם** $\\Omega$ הוא קבוצת כל התוצאות האפשריות.\n\n"
                    "**דוגמאות:**\n"
                    "- הטלת מטבע: $\\Omega = \\{H, T\\}$\n"
                    "- הטלת קובייה: $\\Omega = \\{1, \\ldots, 6\\}$\n"
                    "- שתי קוביות (זוגות מסודרים): $|\\Omega| = 36$\n"
                    "- זמן חיים של רכיב (רציף): $\\Omega = [0, \\infty)$\n\n"
                    "כל **תוצאה** $\\omega \\in \\Omega$ היא תוצאה מלאה אחת. "
                    "בשתי קוביות, $(3,5)$ ו-$(5,3)$ שונות אם הסדר חשוב."
                ),
                "university",
            ),
            _section(
                "events",
                "Events & Set Operations",
                "אירועים ופעולות קבוצות",
                (
                    "An **event** $A$ is a subset of $\\Omega$: $A \\subseteq \\Omega$.\n\n"
                    "- **Simple event:** one outcome, e.g. $A = \\{6\\}$ on a die.\n"
                    "- **Compound event:** several outcomes, e.g. $B = \\{2,4,6\\}$ (even roll).\n\n"
                    "**Operations:**\n"
                    "- Union: $A \\cup B$ — $A$ **or** $B$ (or both)\n"
                    "- Intersection: $A \\cap B$ — $A$ **and** $B$\n"
                    "- Complement: $A^c = \\Omega \\setminus A$\n\n"
                    "**Mutually exclusive (disjoint):** $A \\cap B = \\emptyset$\n\n"
                    "**Exhaustive:** $A \\cup B = \\Omega$\n\n"
                    "**De Morgan's laws:**\n"
                    "$$(A \\cup B)^c = A^c \\cap B^c, \\qquad (A \\cap B)^c = A^c \\cup B^c$$\n\n"
                    "Draw Venn diagrams — they prevent sign errors in inclusion–exclusion."
                ),
                (
                    "**אירוע** $A$ הוא תת-קבוצה של $\\Omega$: $A \\subseteq \\Omega$.\n\n"
                    "- **אירוע פשוט:** תוצאה אחת, למשל $A = \\{6\\}$.\n"
                    "- **אירוע מורכב:** כמה תוצאות, למשל $B = \\{2,4,6\\}$ (זוגי).\n\n"
                    "**פעולות:**\n"
                    "- איחוד: $A \\cup B$ — $A$ **או** $B$\n"
                    "- חיתוך: $A \\cap B$ — $A$ **וגם** $B$\n"
                    "- משלים: $A^c = \\Omega \\setminus A$\n\n"
                    "**זרים (disjoint):** $A \\cap B = \\emptyset$\n\n"
                    "**מכסים (exhaustive):** $A \\cup B = \\Omega$\n\n"
                    "**חוקי דה-מורגן:**\n"
                    "$$(A \\cup B)^c = A^c \\cap B^c, \\qquad (A \\cap B)^c = A^c \\cup B^c$$"
                ),
                "university",
            ),
            _section(
                "kolmogorov_axioms",
                "Probability Function & Kolmogorov Axioms",
                "פונקציית הסתברות ואקסיומות קולמוגורוב",
                (
                    "A **probability function** $P$ assigns to each event $A$ a number $P(A) \\in [0,1]$.\n\n"
                    "**Kolmogorov's three axioms:**\n"
                    "1. $P(A) \\geq 0$ for every event $A$\n"
                    "2. $P(\\Omega) = 1$\n"
                    "3. **Countable additivity:** if $A \\cap B = \\emptyset$, then $P(A \\cup B) = P(A) + P(B)$ "
                    "(extended to countable disjoint unions)\n\n"
                    "**Consequences (prove from axioms):**\n"
                    "- $P(\\emptyset) = 0$\n"
                    "- $P(A^c) = 1 - P(A)$\n"
                    "- $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$ (inclusion–exclusion)\n\n"
                    "If $A \\subseteq B$, then $P(A) \\leq P(B)$."
                ),
                (
                    "**פונקציית הסתברות** $P$ מקצה לכל אירוע $A$ מספר $P(A) \\in [0,1]$.\n\n"
                    "**שלוש אקסיומות קולמוגורוב:**\n"
                    "1. $P(A) \\geq 0$\n"
                    "2. $P(\\Omega) = 1$\n"
                    "3. **אדיטיביות:** אם $A \\cap B = \\emptyset$, אז $P(A \\cup B) = P(A) + P(B)$\n\n"
                    "**מסקנות:**\n"
                    "- $P(\\emptyset) = 0$\n"
                    "- $P(A^c) = 1 - P(A)$\n"
                    "- $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$\n\n"
                    "אם $A \\subseteq B$, אז $P(A) \\leq P(B)$."
                ),
                "university",
            ),
            _section(
                "classical_probability",
                "Classical Probability (Equally Likely Outcomes)",
                "הסתברות קלאסית (תוצאות שוות-הסתברות)",
                (
                    "When all outcomes in a **finite** $\\Omega$ are equally likely:\n"
                    "$$\\boxed{P(A) = \\frac{|A|}{|\\Omega|}}$$\n\n"
                    "**Die problems:** $P(\\text{even}) = 3/6 = 1/2$.\n\n"
                    "**At least one 6 in two dice:** use complement.\n"
                    "$P(\\text{no six on either die}) = (5/6)^2 = 25/36$, so\n"
                    "$$P(\\text{at least one 6}) = 1 - 25/36 = 11/36.$$\n\n"
                    "**Two aces from a 52-card deck (without replacement):**\n"
                    "$$P = \\frac{4}{52} \\cdot \\frac{3}{51} = \\frac{12}{2652} \\approx 0.0045.$$\n\n"
                    "Classical probability requires **careful counting** — the next lesson on combinatorics makes this systematic."
                ),
                (
                    "כאשר כל התוצאות ב-$\\Omega$ **סופי** שוות-הסתברות:\n"
                    "$$\\boxed{P(A) = \\frac{|A|}{|\\Omega|}}$$\n\n"
                    "**קובייה:** $P(\\text{זוגי}) = 3/6 = 1/2$.\n\n"
                    "**לפחות 6 אחת בשתי קוביות:** משלים.\n"
                    "$P(\\text{אין 6}) = (5/6)^2 = 25/36$, לכן\n"
                    "$$P(\\text{לפחות 6 אחת}) = 1 - 25/36 = 11/36.$$\n\n"
                    "**שני אסים מחפיסה (ללא החזרה):**\n"
                    "$$P = \\frac{4}{52} \\cdot \\frac{3}{51} \\approx 0.0045.$$\n\n"
                    "הסתברות קלאסית דורשת **ספירה זהירה** — שיעור הקומבינטוריקה הבא."
                ),
                "university",
            ),
            _section(
                "quality_control_example",
                "Worked Example: Quality Control Sampling",
                "דוגמה מלאה: דגימת בקרת איכות",
                (
                    "**Setup:** A factory produces 1000 items per day; 50 are defective. "
                    "An inspector randomly selects 20 items **without replacement**.\n\n"
                    "Let $A$ = \"at least 2 defective items in the sample.\"\n\n"
                    "**Strategy:** compute $P(A^c) = P(0 \\text{ or } 1 \\text{ defective})$.\n\n"
                    "Total equally likely samples: $\\binom{1000}{20}$.\n\n"
                    "$$P(0 \\text{ defective}) = \\frac{\\binom{50}{0}\\binom{950}{20}}{\\binom{1000}{20}}$$\n\n"
                    "$$P(1 \\text{ defective}) = \\frac{\\binom{50}{1}\\binom{950}{19}}{\\binom{1000}{20}}$$\n\n"
                    "$$P(A) = 1 - P(A^c) = 1 - \\bigl[P(0) + P(1)\\bigr]$$\n\n"
                    "This is a **hypergeometric** setting — common in engineering quality control. "
                    "For large populations, the binomial approximation works well. "
                    "Connection: `concept:combinatorics` unlocks efficient counting for such problems."
                ),
                (
                    "**הגדרה:** מפעל מייצר 1000 פריטים ביום; 50 פגומים. "
                    "מפקח בוחר 20 פריטים **ללא החזרה**.\n\n"
                    "נגדיר $A$ = \"לפחות 2 פגומים במדגם.\"\n\n"
                    "**אסטרטגיה:** נחשב $P(A^c) = P(0 \\text{ או } 1 \\text{ פגום})$.\n\n"
                    "סך המדגמים: $\\binom{1000}{20}$.\n\n"
                    "$$P(0 \\text{ פגומים}) = \\frac{\\binom{50}{0}\\binom{950}{20}}{\\binom{1000}{20}}$$\n\n"
                    "$$P(1 \\text{ פגום}) = \\frac{\\binom{50}{1}\\binom{950}{19}}{\\binom{1000}{20}}$$\n\n"
                    "$$P(A) = 1 - \\bigl[P(0) + P(1)\\bigr]$$\n\n"
                    "זהו מודל **היפר-גיאומטרי** — נפוץ בבקרת איכות הנדסית."
                ),
                "university",
            ),
        ],
        "questions": [
            _mcq(
                "q1",
                "A fair coin is flipped twice. Which is the correct sample space $\\Omega$?",
                "מטבע הוגן מוטל פעמיים. מהו מרחב המדגם $\\Omega$ הנכון?",
                _opts([
                    ("a", "$\\{H, T\\}$", "$\\{H, T\\}$", False),
                    ("b", "$\\{HH, HT, TH, TT\\}$", "$\\{HH, HT, TH, TT\\}$", True),
                    ("c", "$\\{0, 1, 2\\}$ (number of heads)", "$\\{0, 1, 2\\}$ (מספר ראשים)", False),
                    ("d", "$\\{H, T, HH, TT\\}$", "$\\{H, T, HH, TT\\}$", False),
                ]),
                "Two flips produce ordered outcomes; there are $2 \\times 2 = 4$ equally likely results.",
                "שתי הטלות נותנות 4 תוצאות מסודרות שוות-הסתברות.",
            ),
            _mcq(
                "q2",
                "If $P(A) = 0.35$, what is $P(A^c)$?",
                "אם $P(A) = 0.35$, מהו $P(A^c)$?",
                _opts([
                    ("a", "$0.35$", "$0.35$", False),
                    ("b", "$0.65$", "$0.65$", True),
                    ("c", "$1.35$", "$1.35$", False),
                    ("d", "$0$", "$0$", False),
                ]),
                "By the complement rule: $P(A^c) = 1 - P(A) = 1 - 0.35 = 0.65$.",
                "לפי כלל המשלים: $P(A^c) = 1 - 0.35 = 0.65$.",
            ),
            _mcq(
                "q3",
                "For events $A$ and $B$ with $P(A)=0.4$, $P(B)=0.5$, $P(A \\cap B)=0.2$, find $P(A \\cup B)$.",
                "למאורעות $A$, $B$ עם $P(A)=0.4$, $P(B)=0.5$, $P(A \\cap B)=0.2$, מצאו $P(A \\cup B)$.",
                _opts([
                    ("a", "$0.9$", "$0.9$", False),
                    ("b", "$0.7$", "$0.7$", True),
                    ("c", "$0.1$", "$0.1$", False),
                    ("d", "$0.6$", "$0.6$", False),
                ]),
                "Inclusion–exclusion: $P(A \\cup B) = 0.4 + 0.5 - 0.2 = 0.7$.",
                "כלל החיבור: $P(A \\cup B) = 0.4 + 0.5 - 0.2 = 0.7$.",
            ),
            _mcq(
                "q4",
                "Two fair dice are rolled. What is $P(\\text{sum} = 7)$?",
                "שתי קוביות הוגנות. מה $P(\\text{סכום} = 7)$?",
                _opts([
                    ("a", "$1/36$", "$1/36$", False),
                    ("b", "$1/6$", "$1/6$", True),
                    ("c", "$7/36$", "$7/36$", False),
                    ("d", "$1/12$", "$1/12$", False),
                ]),
                "Six favorable ordered pairs out of 36: $6/36 = 1/6$.",
                "6 זוגות מתוך 36: $6/36 = 1/6$.",
            ),
            _mcq(
                "q5",
                "Which identity expresses De Morgan's law for complements?",
                "איזו זהות מבטאת את חוק דה-מורגן למשלימים?",
                _opts([
                    ("a", "$(A \\cup B)^c = A^c \\cap B^c$", "$(A \\cup B)^c = A^c \\cap B^c$", True),
                    ("b", "$(A \\cup B)^c = A^c \\cup B^c$", "$(A \\cup B)^c = A^c \\cup B^c$", False),
                    ("c", "$P(A \\cup B) = P(A) + P(B)$", "$P(A \\cup B) = P(A) + P(B)$", False),
                    ("d", "$P(A^c) = P(A) - 1$", "$P(A^c) = P(A) - 1$", False),
                ]),
                "De Morgan: complement of a union equals intersection of complements.",
                "דה-מורגן: משלים של איחוד = חיתוך של משלימים.",
            ),
        ],
    },
]


def write_lesson_files(lessons: list[dict]) -> None:
    for lesson in lessons:
        path = LESSONS_DIR / f"{lesson['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[write] {path.relative_to(ROOT)}")


def update_lessons_index() -> None:
    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)
    for entry in index:
        lid = entry.get("id")
        if lid not in INDEX_ENTRIES:
            continue
        meta = INDEX_ENTRIES[lid]
        entry.update(
            {
                "title_en": meta["title_en"],
                "title_he": meta["title_he"],
                "est_minutes": meta["duration_min"],
                "math_track": meta["math_track"],
                "subject": meta["subject"],
                "duration_min": meta["duration_min"],
                "type": "interactive",
                "level_min": meta["level_min"],
            }
        )
    index.sort(key=lambda e: e["id"])
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[index] updated {INDEX_PATH.relative_to(ROOT)}")


def main() -> int:
    assert len(LESSONS) == 1
    write_lesson_files(LESSONS)
    update_lessons_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
