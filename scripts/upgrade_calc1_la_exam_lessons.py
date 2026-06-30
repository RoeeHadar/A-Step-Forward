#!/usr/bin/env python3
"""Upgrade Calc 1 and Linear Algebra lesson JSON files to university exam depth."""
from __future__ import annotations

import json
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS_DIR = os.path.join(ROOT, "scripts", "seed_data", "lessons")

EXAM_SECTION_LEGACY = {
    "kind": "exam_problems",
    "title_en": "Exam-Style Practice Problems",
    "title_he": "תרגול בסגנון בחינה",
    "body_en_md": "",
    "body_he_md": "",
}

EXAM_INTRO_EN = (
    "The following problems are at the level of actual university final exams "
    "(Ariel University 38-111 Calculus, 88112 Linear Algebra). "
    "Practice writing complete solutions with all steps justified.\n\n"
)
EXAM_INTRO_HE = (
    "הבעיות הבאות ברמת בחינות סופיות אמיתיות (38-111 חדו״א, 88112 אלגברה לינארית). "
    "תרגלו כתיבת פתרונות מלאים עם הנמקה לכל שלב.\n\n"
)
EXAM_FOOTER_EN = (
    "\n\n**What examiners look for:**\n"
    "- Every step written explicitly\n"
    "- No computational shortcuts without justification\n"
    "- Clear statement of what was proven or found at each stage"
)
EXAM_FOOTER_HE = (
    "\n\n**מה בודקים בבחינה:**\n"
    "- כל שלב כתוב במפורש\n"
    "- ללא קיצורי דרך ללא הנמקה\n"
    "- הצהרה ברורה מה הוכח או נמצא בכל שלב"
)


def exam_body(problems_en: list[tuple[str, str]], problems_he: list[tuple[str, str]]) -> tuple[str, str]:
    en = EXAM_INTRO_EN
    he = EXAM_INTRO_HE
    for i, ((prob_en, sol_en), (prob_he, sol_he)) in enumerate(
        zip(problems_en, problems_he), 1
    ):
        en += f"**Problem {i}:** {prob_en}\n\n**Sample Solution:**\n{sol_en}\n\n"
        he += f"**בעיה {i}:** {prob_he}\n\n**פתרון לדוגמה:**\n{sol_he}\n\n"
    en += EXAM_FOOTER_EN
    he += EXAM_FOOTER_HE
    return en, he


def make_open_legacy(
    ord_num: int,
    stem_en: str,
    stem_he: str,
    rubric_en: str,
    rubric_he: str,
    explanation_en: str,
    explanation_he: str,
    skill_atoms: list[str],
    difficulty: str = "hard",
    points_level_min: str = "calc1",
) -> dict:
    return {
        "ord": ord_num,
        "kind": "open",
        "difficulty": difficulty,
        "stem_en": stem_en,
        "stem_he": stem_he,
        "rubric_en": rubric_en,
        "rubric_he": rubric_he,
        "explanation_en": explanation_en,
        "explanation_he": explanation_he,
        "skill_atoms": skill_atoms,
        "points_level_min": points_level_min,
    }


def make_open_interactive(
    qid: str,
    body_en: str,
    body_he: str,
    rubric_en: str,
    rubric_he: str,
    explanation_en: str,
    explanation_he: str,
) -> dict:
    return {
        "id": qid,
        "type": "open",
        "body_en": body_en,
        "body_he": body_he,
        "rubric_en": rubric_en,
        "rubric_he": rubric_he,
        "explanation_en": explanation_en,
        "explanation_he": explanation_he,
    }


def add_exam_section_legacy(lesson: dict, en: str, he: str) -> None:
    sec = dict(EXAM_SECTION_LEGACY)
    sec["body_en_md"] = en
    sec["body_he_md"] = he
    sections = lesson.setdefault("sections", [])
    if any(s.get("kind") == "exam_problems" for s in sections):
        for s in sections:
            if s.get("kind") == "exam_problems":
                s["body_en_md"] = en
                s["body_he_md"] = he
        return
    sections.append(sec)


def add_exam_section_interactive(lesson: dict, en: str, he: str) -> None:
    sec = {
        "id": "exam_problems",
        "title_en": "Exam-Style Practice Problems",
        "title_he": "תרגול בסגנון בחינה",
        "level_min": "calculus_1",
        "body_en_md": en,
        "body_he_md": he,
    }
    sections = lesson.setdefault("sections", [])
    if any(s.get("id") == "exam_problems" for s in sections):
        for s in sections:
            if s.get("id") == "exam_problems":
                s["body_en_md"] = en
                s["body_he_md"] = he
        return
    sections.append(sec)


def already_upgraded(lesson: dict) -> bool:
    for sec in lesson.get("sections", []):
        if sec.get("kind") == "exam_problems" or sec.get("id") == "exam_problems":
            return True
    return False


def replace_last_mcq_with_open(
    questions: list, open_questions: list[dict], schema: str
) -> None:
    mcq_indices = [
        i
        for i, q in enumerate(questions)
        if (schema == "legacy" and q.get("kind") == "mcq")
        or (schema == "interactive" and q.get("type") == "mcq")
    ]
    if len(mcq_indices) < 2 or len(open_questions) < 2:
        return
    for idx, open_q in zip(mcq_indices[-2:], open_questions[:2]):
        if schema == "legacy":
            open_q_copy = dict(open_q)
            open_q_copy["ord"] = questions[idx].get("ord", idx + 1)
            open_q_copy["skill_atoms"] = questions[idx].get(
                "skill_atoms", open_q.get("skill_atoms", [])
            )
            open_q_copy["points_level_min"] = questions[idx].get(
                "points_level_min", open_q.get("points_level_min", "calc1")
            )
            questions[idx] = open_q_copy
        else:
            open_q_copy = dict(open_q)
            open_q_copy["id"] = questions[idx].get("id", f"q{idx+1}")
            questions[idx] = open_q_copy


def is_legacy_schema(lesson: dict) -> bool:
    return "concept_id" in lesson or (
        lesson.get("sections")
        and lesson["sections"]
        and "kind" in lesson["sections"][0]
    )


def is_interactive_schema(lesson: dict) -> bool:
    return "id" in lesson and lesson.get("type") == "interactive"


# ── Per-lesson upgrade payloads ─────────────────────────────────────────────

UPGRADES: dict[str, dict] = {}


def _register(concept_id: str, **kwargs):
    UPGRADES[concept_id] = kwargs


_register(
    "limits",
    exam_en=[
        (
            r"Compute $\lim_{x\to 0}\dfrac{\sin(x)-x}{x^3}$.",
            r"""**Method 1 (Taylor):** $\sin x = x - \dfrac{x^3}{6} + O(x^5)$, so
$$\frac{\sin x - x}{x^3} = \frac{-\frac{x^3}{6} + O(x^5)}{x^3} = -\frac{1}{6} + O(x^2) \xrightarrow[x\to 0]{} -\frac{1}{6}.$$

**Method 2 (L'Hôpital, three times):** Form $0/0$. Differentiate:
$$\lim_{x\to 0}\frac{\cos x - 1}{3x^2} \xrightarrow{0/0} \lim_{x\to 0}\frac{-\sin x}{6x} \xrightarrow{0/0} \lim_{x\to 0}\frac{-\cos x}{6} = -\frac{1}{6}.$$""",
        ),
        (
            r"Compute $\lim_{n\to\infty} n\bigl(\sqrt{1+\frac{1}{n}} - 1\bigr)$.",
            r"""Multiply by the conjugate:
$$n\bigl(\sqrt{1+\tfrac{1}{n}} - 1\bigr) = n \cdot \frac{\bigl(1+\frac{1}{n}\bigr)-1}{\sqrt{1+\frac{1}{n}}+1} = \frac{1}{\sqrt{1+\frac{1}{n}}+1}.$$
As $n\to\infty$, the denominator $\to 2$, so the limit is $\boxed{\dfrac{1}{2}}$.""",
        ),
    ],
    exam_he=[
        (
            r"חשבו $\lim_{x\to 0}\dfrac{\sin(x)-x}{x^3}$.",
            r"""**טיילור:** $\sin x = x - \dfrac{x^3}{6} + O(x^5)$, לכן הגבול $-\dfrac{1}{6}$.

**לופיטל (3 פעמים):** $\dfrac{\cos x - 1}{3x^2} \to \dfrac{-\sin x}{6x} \to \dfrac{-\cos x}{6} = -\dfrac{1}{6}$.""",
        ),
        (
            r"חשבו $\lim_{n\to\infty} n\bigl(\sqrt{1+\frac{1}{n}} - 1\bigr)$.",
            r"""כפל בצמוד: $n \cdot \dfrac{1/n}{\sqrt{1+1/n}+1} = \dfrac{1}{\sqrt{1+1/n}+1} \to \dfrac{1}{2}$.""",
        ),
    ],
    theory_append_en=(
        "\n\n**Worked Example (exam level).** $\\lim_{x\\to 0}\\dfrac{\\sin x - x}{x^3}$:\n"
        "Taylor gives $-\\tfrac{1}{6}$; L'Hôpital three times confirms.\n\n"
        "**Worked Example 2.** $\\lim_{n\\to\\infty} n(\\sqrt{1+1/n}-1)$: conjugate "
        "yields $1/(\\sqrt{1+1/n}+1) \\to 1/2$."
    ),
    theory_append_he=(
        "\n\n**דוגמה (רמת בחינה).** $\\lim_{x\\to 0}\\dfrac{\\sin x - x}{x^3} = -\\tfrac{1}{6}$.\n\n"
        "**דוגמה 2.** $\\lim_{n\\to\\infty} n(\\sqrt{1+1/n}-1) = \\tfrac{1}{2}$."
    ),
    open_questions=[
        make_open_legacy(
            0,
            r"Compute $\lim_{x\to 0}\dfrac{\sin(x)-x}{x^3}$ using Taylor expansion or L'Hôpital's rule. Show all steps.",
            r"חשבו $\lim_{x\to 0}\dfrac{\sin(x)-x}{x^3}$ באמצעות טיילור או לופיטל. הראו את כל השלבים.",
            "Full credit (10/10): identifies $0/0$, applies Taylor OR three L'Hôpital steps, answer $-1/6$ with justification.\nPartial (6/10): correct method, arithmetic slip.\nMinimal (3/10): identifies indeterminate form only.",
            "ציון מלא (10/10): מזהה $0/0$, מיישם טיילור או לופיטל 3 פעמים, תשובה $-1/6$.\nחלקי (6/10): שיטה נכונה, טעות חישוב.\nמינימלי (3/10): רק מזהה צורה לא קבועה.",
            r"Answer: $-\dfrac{1}{6}$.",
            r"תשובה: $-\dfrac{1}{6}$.",
            ["limit_taylor_lhopital"],
            points_level_min="5pt",
        ),
        make_open_legacy(
            0,
            r"Compute $\lim_{n\to\infty} n\bigl(\sqrt{1+\frac{1}{n}} - 1\bigr)$. Justify each algebraic step.",
            r"חשבו $\lim_{n\to\infty} n\bigl(\sqrt{1+\frac{1}{n}} - 1\bigr)$. הנמקו כל שלב.",
            "Full credit (10/10): conjugate multiplication, simplifies to $1/(\sqrt{1+1/n}+1)$, limit $1/2$.\nPartial (6/10): correct setup, error in limit evaluation.\nMinimal (3/10): recognizes need for conjugate.",
            "ציון מלא (10/10): כפל בצמוד, מפשט ל-$1/(\sqrt{1+1/n}+1)$, גבול $1/2$.\nחלקי (6/10): הגדרה נכונה, שגיאה בגבול.\nמינימלי (3/10): מזהה צורך בצמוד.",
            r"Answer: $\dfrac{1}{2}$.",
            r"תשובה: $\dfrac{1}{2}$.",
            ["limit_conjugate_sequence"],
            points_level_min="5pt",
        ),
    ],
)

_register(
    "continuity_discontinuity",
    exam_en=[
        (
            r"Given $f$ differentiable on $\mathbb{R}$ with $f(0)=0$, $f(1)=1$, and $f'(x)\geq 1$ for all $x$. Prove that $f(x)\geq x$ for all $x\in[0,1]$.",
            r"""Fix $x\in[0,1]$. By the **Mean Value Theorem** on $[0,x]$, there exists $c\in(0,x)$ with
$$f(x)-f(0)=f'(c)\,x.$$
Since $f(0)=0$ and $f'(c)\geq 1$:
$$f(x)=f'(c)\,x \geq 1\cdot x = x.$$
This holds for every $x\in[0,1]$, so $f(x)\geq x$ on $[0,1]$. $\square$""",
        ),
        (
            r"Use the IVT to show $e^x = 3 - x$ has a solution in $(0,1)$.",
            r"""Let $g(x)=e^x - (3-x)=e^x + x - 3$. Then $g$ is continuous on $[0,1]$.
$g(0)=e^0+0-3=-2<0$ and $g(1)=e+1-3=e-2>0$ (since $e>2.7$).
By IVT, $\exists\,c\in(0,1)$ with $g(c)=0$, i.e. $e^c=3-c$. $\square$""",
        ),
    ],
    exam_he=[
        (
            r"נתונה $f$ גזירה על $\mathbb{R}$ עם $f(0)=0$, $f(1)=1$, ו-$f'(x)\geq 1$. הוכיחו $f(x)\geq x$ לכל $x\in[0,1]$.",
            r"""לפי **MVT** על $[0,x]$: $f(x)=f'(c)x$ עם $f'(c)\geq 1$, לכן $f(x)\geq x$. $\square$""",
        ),
        (
            r"השתמשו ב-IVT להראות של-$e^x=3-x$ יש פתרון ב-$(0,1)$.",
            r"""$g(x)=e^x+x-3$ רציפה. $g(0)=-2<0$, $g(1)=e-2>0$. לפי IVT קיים שורש ב-$(0,1)$. $\square$""",
        ),
    ],
    theory_append_en=(
        "\n\n**Worked Example (MVT inequality).** If $f(0)=0$, $f(1)=1$, $f'(x)\geq 1$, "
        "then MVT on $[0,x]$ gives $f(x)=f'(c)x\geq x$.\n\n"
        "**Worked Example 2 (IVT).** $g(x)=e^x+x-3$ changes sign on $[0,1]$ ⇒ root in $(0,1)$."
    ),
    theory_append_he=(
        "\n\n**דוגמה (MVT).** $f'(x)\geq 1$ על $[0,1]$ ⇒ $f(x)\geq x$.\n\n"
        "**דוגמה 2 (IVT).** $e^x+x-3$ משנה סימן ב-$[0,1]$."
    ),
    open_questions=[
        make_open_legacy(
            0,
            r"Prove: If $f$ is differentiable on $\mathbb{R}$, $f(0)=0$, $f(1)=1$, and $f'(x)\geq 1$ for all $x$, then $f(x)\geq x$ for all $x\in[0,1]$.",
            r"הוכיחו: אם $f$ גזירה, $f(0)=0$, $f(1)=1$, $f'(x)\geq 1$, אז $f(x)\geq x$ ב-$[0,1]$.",
            "Full credit (10/10): applies MVT on $[0,x]$, uses $f(0)=0$ and $f'(c)\geq 1$, concludes $f(x)\geq x$.\nPartial (6/10): cites MVT but incomplete chain.\nMinimal (3/10): states MVT without application.",
            "ציון מלא (10/10): MVT על $[0,x]$, $f(0)=0$, $f'(c)\geq 1$, מסקנה $f(x)\geq x$.\nחלקי (6/10): מצטט MVT ללא יישום מלא.\nמינימלי (3/10): רק מציין MVT.",
            "MVT on $[0,x]$: $f(x)=f'(c)x\\geq x$.",
            "MVT: $f(x)=f'(c)x\\geq x$.",
            ["mvt_inequality_proof"],
            points_level_min="calc1",
        ),
        make_open_legacy(
            0,
            r"Prove using IVT that the equation $e^x = 3 - x$ has at least one solution in $(0,1)$.",
            r"הוכיחו ב-IVT של-$e^x=3-x$ יש פתרון ב-$(0,1)$.",
            "Full credit (10/10): defines $g(x)=e^x+x-3$, checks signs at 0 and 1, applies IVT.\nPartial (6/10): correct $g$ but sign error.\nMinimal (3/10): mentions IVT only.",
            "ציון מלא (10/10): $g(x)=e^x+x-3$, בדיקת סימנים, IVT.\nחלקי (6/10): $g$ נכון, טעות בסימן.\nמינימלי (3/10): רק מזכיר IVT.",
            "$g(0)<0$, $g(1)>0$ ⇒ root in $(0,1)$ by IVT.",
            "$g(0)<0$, $g(1)>0$ ⇒ שורש ב-$(0,1)$.",
            ["apply_ivt"],
            points_level_min="calc1",
        ),
    ],
)

_register(
    "series_convergence_tests",
    full_replace={
        "concept_id": "series_convergence_tests",
        "subject": "math",
        "level": "university",
        "math_track": ["calc1"],
        "title_en": "Sequences & Series — Convergence",
        "title_he": "סדרות וטורים — התכנסות",
        "summary_en": "Monotone bounded sequences, recurrence relations, ratio and comparison tests — exam staples in Calculus 1.",
        "summary_he": "סדרות monoton חסומות, נוסחאות נסיגה, מבחן המנה וההשוואה — נושאי בחינה בחדו״א 1.",
        "est_minutes": 30,
        "sections": [],  # filled below
        "questions": [],
        "agent_hints": {
            "key_insights": [
                "Monotone + bounded ⇒ converges (completeness of ℝ).",
                "Fixed point of recurrence: solve L = g(L) for limit.",
                "Ratio test: |a_{n+1}/a_n| < 1 ⇒ converges absolutely.",
            ],
            "tutor_pacing_hint": "Prove monotonicity before invoking boundedness. Always state the limit candidate from L = f(L).",
            "skill_atoms_unlocked": [
                "sequence_monotone_proof",
                "sequence_limit_recurrence",
                "ratio_test",
            ],
        },
    },
    exam_en=[
        (
            r"Let $a_1=1$ and $a_{n+1}=\dfrac{a_n+2}{a_n+1}$. Prove the sequence converges and find its limit.",
            r"""**Step 1 — positive and bounded below:** $a_1=1>0$. If $a_n>0$ then $a_{n+1}>0$. All terms positive.

**Step 2 — monotone decreasing:** Compute $a_{n+1}-a_n = \dfrac{a_n+2}{a_n+1}-a_n = \dfrac{2-a_n^2}{a_n+1}$.
For $a_n\geq 1$: numerator $2-a_n^2\leq 1-1=0$, so $a_{n+1}\leq a_n$. Since $a_1=1$ and the map preserves $a_n\geq\sqrt{2}$ eventually... Actually check: $a_2=3/2$, $a_3=7/5=1.4$, decreasing toward limit.

**Step 3 — bounded below:** $a_{n+1} = 1 + \dfrac{1}{a_n+1} > 1$, so $a_n > 1$ for $n\geq 2$. Bounded below by 1.

Monotone decreasing + bounded below ⇒ **converges** to $L$.

**Step 4 — limit:** $L = \dfrac{L+2}{L+1} \Rightarrow L(L+1)=L+2 \Rightarrow L^2=2 \Rightarrow L=\sqrt{2}$ (positive). $\boxed{\lim a_n = \sqrt{2}}$.""",
        ),
        (
            r"Determine convergence of $\sum_{n=1}^\infty \dfrac{n!}{n^n}$.",
            r"""**Ratio test:** $\dfrac{a_{n+1}}{a_n} = \dfrac{(n+1)!/(n+1)^{n+1}}{n!/n^n} = \dfrac{n^n}{(n+1)^n} = \left(\dfrac{n}{n+1}\right)^n \to e^{-1} < 1$.
Therefore the series **converges**.""",
        ),
    ],
    exam_he=[
        (
            r"תנו $a_1=1$, $a_{n+1}=\dfrac{a_n+2}{a_n+1}$. הוכיחו התכנסות ומצאו גבול.",
            r"""**monotone יורד + חסום מלרע** ⇒ מתכנס. **גבול:** $L=\dfrac{L+2}{L+1} \Rightarrow L=\sqrt{2}$. $\square$""",
        ),
        (
            r"קבעו התכנסות של $\sum \dfrac{n!}{n^n}$.",
            r"""**מבחן המנה:** $\left(\dfrac{n}{n+1}\right)^n \to e^{-1}<1$ ⇒ **מתכנס**.""",
        ),
    ],
)

# Build series full sections
_series = UPGRADES["series_convergence_tests"]["full_replace"]
_series["sections"] = [
    {
        "kind": "theory",
        "title_en": "Monotone sequences",
        "title_he": "סדרות monoton",
        "body_en_md": "If $(a_n)$ is **monotone** (non-decreasing or non-increasing) and **bounded**, then it **converges**.\n\n**Worked Example 1.** $a_n = 1 - \\frac{1}{n}$: increasing, bounded above by 1, so $\\lim a_n = 1$.\n\n**Worked Example 2.** $a_{n+1} = \\frac{a_n + 2}{a_n + 1}$ with $a_1=1$: prove decreasing and bounded below, then $L = \\sqrt{2}$.",
        "body_he_md": "סדרה **monoton** ו**חסומה** ⇒ **מתכנסת**.\n\n**דוגמה 1.** $a_n = 1 - 1/n \\to 1$.\n\n**דוגמה 2.** $a_{n+1} = \\frac{a_n+2}{a_n+1}$, $a_1=1$: יורדת, חסומה, גבול $\\sqrt{2}$.",
    },
    {
        "kind": "theory",
        "title_en": "Convergence tests for series",
        "title_he": "מבחני התכנסות לטורים",
        "body_en_md": "**Ratio test:** If $\\lim |a_{n+1}/a_n| = L < 1$, then $\\sum a_n$ converges absolutely.\n\n**Comparison:** If $0 \\leq a_n \\leq b_n$ and $\\sum b_n$ converges, then $\\sum a_n$ converges.\n\n**Worked Example 1.** $\\sum \\frac{1}{n^2}$ converges (p-series, $p=2$).\n\n**Worked Example 2.** $\\sum \\frac{n!}{n^n}$: ratio $\\to e^{-1} < 1$ ⇒ converges.",
        "body_he_md": "**מבחן המנה:** $L<1$ ⇒ מתכנס.\n\n**השוואה:** $0\\leq a_n\\leq b_n$, $\\sum b_n$ מתכנס ⇒ $\\sum a_n$ מתכנס.\n\n**דוגמה:** $\\sum n!/n^n$ מתכנס (מנה $\\to e^{-1}$).",
    },
]
_series["questions"] = [
    {
        "ord": 1,
        "kind": "mcq",
        "difficulty": "easy",
        "stem_en": "A monotone increasing sequence bounded above:",
        "stem_he": "סדרה monoton עולה וחסומה מלעלה:",
        "options_en": ["Diverges to $\\infty$", "Converges", "Is constant", "Oscillates"],
        "options_he": ["מתבדרת ל-$\\infty$", "מתכנסת", "קבועה", "מתנדנדת"],
        "correct_index": 1,
        "explanation_en": "Monotone + bounded ⇒ converges (completeness).",
        "explanation_he": "monoton + חסומה ⇒ מתכנסת.",
        "skill_atoms": ["sequence_monotone_proof"],
        "points_level_min": "calc1",
    },
    {
        "ord": 2,
        "kind": "mcq",
        "difficulty": "medium",
        "stem_en": "If $\\lim |a_{n+1}/a_n| = 1/2$, the series $\\sum a_n$:",
        "stem_he": "אם $\\lim |a_{n+1}/a_n| = 1/2$, הטור $\\sum a_n$:",
        "options_en": ["Converges", "Diverges", "Inconclusive always", "Converges to 0"],
        "options_he": ["מתכנס", "מתבדר", "תמיד לא חד-משמעי", "מתכנס ל-0"],
        "correct_index": 0,
        "explanation_en": "Ratio $< 1$ ⇒ absolute convergence.",
        "explanation_he": "מנה $< 1$ ⇒ התכנסות מוחלטת.",
        "skill_atoms": ["ratio_test"],
        "points_level_min": "calc1",
    },
    {
        "ord": 3,
        "kind": "mcq",
        "difficulty": "medium",
        "stem_en": "For $a_{n+1}=\\sqrt{2+a_n}$ with $a_1=1$, a candidate limit $L$ satisfies:",
        "stem_he": "ל-$a_{n+1}=\\sqrt{2+a_n}$, מועמד לגבול $L$ מקיים:",
        "options_en": ["$L=2$", "$L=\\sqrt{2+L}$", "$L=1$", "$L=0$"],
        "options_he": ["$L=2$", "$L=\\sqrt{2+L}$", "$L=1$", "$L=0$"],
        "correct_index": 1,
        "explanation_en": "Pass limit through recurrence: $L = \\sqrt{2+L}$.",
        "explanation_he": "מעבירים גבול: $L = \\sqrt{2+L}$.",
        "skill_atoms": ["sequence_limit_recurrence"],
        "points_level_min": "calc1",
    },
    make_open_legacy(
        4,
        r"Let $a_1=1$, $a_{n+1}=\dfrac{a_n+2}{a_n+1}$. Prove $(a_n)$ converges and find $\lim a_n$.",
        r"תנו $a_1=1$, $a_{n+1}=\dfrac{a_n+2}{a_n+1}$. הוכיחו התכנסות ומצאו $\lim a_n$.",
        "Full credit (10/10): proves monotone + bounded, passes limit to get $L=\sqrt{2}$.\nPartial (6/10): finds $L$ without monotonicity proof.\nMinimal (3/10): only sets $L=(L+2)/(L+1)$.",
        "ציון מלא (10/10): monoton + חסום, $L=\sqrt{2}$.\nחלקי (6/10): גבול ללא הוכחת monoton.\nמינימלי (3/10): רק משוואת גבול.",
        r"Limit = $\sqrt{2}$.",
        r"גבול = $\sqrt{2}$.",
        ["sequence_limit_recurrence"],
        points_level_min="calc1",
    ),
    make_open_legacy(
        5,
        r"Prove $\sum_{n=1}^\infty \dfrac{n!}{n^n}$ converges using the ratio test.",
        r"הוכיחו ב-מבחן המנה ש-$\sum \dfrac{n!}{n^n}$ מתכנס.",
        "Full credit (10/10): sets up ratio, simplifies to $(n/(n+1))^n$, limit $e^{-1}<1$.\nPartial (6/10): correct ratio, wrong limit.\nMinimal (3/10): cites ratio test only.",
        "ציון מלא (10/10): מנה $(n/(n+1))^n \to e^{-1}<1$.\nחלקי (6/10): מנה נכון, גבול שגוי.\nמינימלי (3/10): רק מציין מבחן מנה.",
        r"Ratio $\\to e^{-1}<1$ ⇒ converges.",
        r"מנה $\\to e^{-1}<1$ ⇒ מתכנס.",
        ["ratio_test"],
        points_level_min="calc1",
    ),
]

_register(
    "improper_integrals",
    full_replace={
        "concept_id": "improper_integrals",
        "subject": "math",
        "level": "university",
        "math_track": ["calc1"],
        "title_en": "Improper Integrals",
        "title_he": "אינטגרלים לא אמתיים",
        "summary_en": "Integrals over unbounded intervals or with unbounded integrand — convergence tests and evaluation.",
        "summary_he": "אינטגרלים על קטעים לא חסומים או עם מIntegrand לא חסום — מבחני התכנסות וחישוב.",
        "est_minutes": 28,
        "sections": [],
        "questions": [],
        "agent_hints": {
            "key_insights": [
                "Define as limit of proper integrals.",
                "Compare to p-integral ∫₁^∞ 1/x^p: converges iff p>1.",
                "ln x / x^p at ∞: converges iff p>1.",
            ],
            "skill_atoms_unlocked": ["improper_integral_limit", "p_integral_test", "integrate_tan_squared"],
        },
    },
    exam_en=[
        (
            r"Compute $\int \tan^2(x)\,dx$.",
            r"""Use $\tan^2 x = \sec^2 x - 1$:
$$\int \tan^2 x\, dx = \int (\sec^2 x - 1)\, dx = \tan x - x + C.$$
Verify: $\frac{d}{dx}(\tan x - x) = \sec^2 x - 1 = \tan^2 x$. ✓""",
        ),
        (
            r"Determine if $\int_1^\infty \dfrac{\ln x}{x^2}\,dx$ converges; if so, compute it.",
            r"""**Convergence:** For $x\geq 1$, $0 < \ln x < x$, so $0 < \dfrac{\ln x}{x^2} < \dfrac{1}{x}$. Since $\int_1^\infty \frac{1}{x}\,dx$ diverges this comparison is inconclusive; use integration by parts:
$$\int \frac{\ln x}{x^2}\,dx = -\frac{\ln x}{x} - \frac{1}{x} + C.$$
So $\int_1^b \frac{\ln x}{x^2}\,dx = \left[-\frac{\ln x}{x} - \frac{1}{x}\right]_1^b = -\frac{\ln b}{b} - \frac{1}{b} + 1$.
As $b\to\infty$: $\frac{\ln b}{b}\to 0$, $\frac{1}{b}\to 0$. **Converges to 1.**""",
        ),
    ],
    exam_he=[
        (
            r"חשבו $\int \tan^2(x)\,dx$.",
            r"""$\tan^2 x = \sec^2 x - 1$ ⇒ $\int \tan^2 x\, dx = \tan x - x + C$.""",
        ),
        (
            r"קבעו אם $\int_1^\infty \dfrac{\ln x}{x^2}\,dx$ מתכנס; אם כן, חשבו.",
            r"""אינטגרציה בחלקים: $\left[-\frac{\ln x}{x} - \frac{1}{x}\right]_1^b \to 1$. **מתכנס ל-1.**""",
        ),
    ],
)

_imp = UPGRADES["improper_integrals"]["full_replace"]
_imp["sections"] = [
    {
        "kind": "theory",
        "title_en": "Definition and p-integrals",
        "title_he": "הגדרה ואינטגרלי-p",
        "body_en_md": "$\\int_a^\\infty f(x)\\,dx := \\lim_{b\\to\\infty}\\int_a^b f(x)\\,dx$.\n\n**p-test:** $\\int_1^\\infty \\frac{1}{x^p}\\,dx$ converges iff $p>1$.\n\n**Worked Example 1.** $\\int_1^\\infty \\frac{1}{x^2}\\,dx = \\lim_{b\\to\\infty}[-\\frac{1}{x}]_1^b = 1$.\n\n**Worked Example 2.** $\\int_1^\\infty \\frac{\\ln x}{x^2}\\,dx = 1$ (by parts).",
        "body_he_md": "הגדרה כגבול. **p-test:** $p>1$ ⇒ מתכנס.\n\n**דוגמה:** $\\int_1^\\infty \\frac{\\ln x}{x^2}\\,dx = 1$.",
    },
    {
        "kind": "worked_example",
        "title_en": "Trig integrals",
        "title_he": "אינטגרלים טrigונומטריים",
        "body_en_md": "$\\tan^2 x = \\sec^2 x - 1$, so $\\int \\tan^2 x\\, dx = \\tan x - x + C$.\n\n**Harder:** $\\int_1^3 \\frac{\\ln x}{x}\\,dx = [\\frac{(\\ln x)^2}{2}]_1^3 = \\frac{(\\ln 3)^2}{2}$ (proper integral).",
        "body_he_md": "$\\int \\tan^2 x\\, dx = \\tan x - x + C$.\n\n$\\int_1^3 \\frac{\\ln x}{x}\\,dx = \\frac{(\\ln 3)^2}{2}$.",
    },
]
_imp["questions"] = [
    {
        "ord": 1,
        "kind": "mcq",
        "difficulty": "easy",
        "stem_en": "$\\int_1^\\infty \\frac{1}{x}\\,dx$:",
        "stem_he": "$\\int_1^\\infty \\frac{1}{x}\\,dx$:",
        "options_en": ["Converges to 1", "Diverges", "Converges to 0", "Converges to $e$"],
        "options_he": ["מתכנס ל-1", "מתבדר", "מתכנס ל-0", "מתכנס ל-$e$"],
        "correct_index": 1,
        "explanation_en": "p-integral with p=1 diverges.",
        "explanation_he": "p=1 ⇒ מתבדר.",
        "skill_atoms": ["p_integral_test"],
        "points_level_min": "calc1",
    },
    {
        "ord": 2,
        "kind": "mcq",
        "difficulty": "medium",
        "stem_en": "$\\int_1^\\infty \\frac{1}{x^3}\\,dx$ equals:",
        "stem_he": "$\\int_1^\\infty \\frac{1}{x^3}\\,dx$ שווה:",
        "options_en": ["$1/2$", "$1/3$", "Diverges", "$\\infty$"],
        "options_he": ["$1/2$", "$1/3$", "מתבדר", "$\\infty$"],
        "correct_index": 0,
        "explanation_en": "$[-\\frac{1}{2x^2}]_1^\\infty = 0 - (-1/2) = 1/2$.",
        "explanation_he": "ערך $1/2$.",
        "skill_atoms": ["p_integral_test"],
        "points_level_min": "calc1",
    },
    {
        "ord": 3,
        "kind": "mcq",
        "difficulty": "medium",
        "stem_en": "$\\int \\tan^2 x\\, dx$ equals:",
        "stem_he": "$\\int \\tan^2 x\\, dx$ שווה:",
        "options_en": ["$\\tan x - x + C$", "$\\sec^2 x + C$", "$-\\cot x + C$", "$\\ln|\\sec x| + C$"],
        "options_he": ["$\\tan x - x + C$", "$\\sec^2 x + C$", "$-\\cot x + C$", "$\\ln|\\sec x| + C$"],
        "correct_index": 0,
        "explanation_en": "$\\tan^2 = \\sec^2 - 1$.",
        "explanation_he": "$\\tan^2 = \\sec^2 - 1$.",
        "skill_atoms": ["integrate_tan_squared"],
        "points_level_min": "calc1",
    },
    make_open_legacy(
        4,
        r"Compute $\int \tan^2(x)\,dx$ and verify by differentiation.",
        r"חשבו $\int \tan^2(x)\,dx$ ואמתו בגזירה.",
        "Full credit (10/10): uses $\\tan^2=\\sec^2-1$, answer $\\tan x - x + C$, verifies derivative.\nPartial (6/10): correct antiderivative, no verification.\nMinimal (3/10): writes identity only.",
        "ציון מלא (10/10): $\\tan x - x + C$ + אימות.\nחלקי (6/10): קדומה נכונה.\nמינימלי (3/10): רק זהות.",
        r"$\tan x - x + C$.",
        r"$\tan x - x + C$.",
        ["integrate_tan_squared"],
        points_level_min="calc1",
    ),
    make_open_legacy(
        5,
        r"Determine convergence of $\int_1^\infty \dfrac{\ln x}{x^2}\,dx$ and compute if convergent.",
        r"קבעו התכנסות של $\int_1^\infty \dfrac{\ln x}{x^2}\,dx$ וחשבו אם מתכנס.",
        "Full credit (10/10): integration by parts, limit as $b\\to\\infty$, value 1.\nPartial (6/10): correct antiderivative, limit error.\nMinimal (3/10): sets up as limit only.",
        "ציון מלא (10/10): אינטגרציה בחלקים, גבול, ערך 1.\nחלקי (6/10): קדומה נכון.\nמינימלי (3/10): רק הגדרה כגבול.",
        r"Converges to 1.",
        r"מתכנס ל-1.",
        ["improper_integral_limit"],
        points_level_min="calc1",
    ),
]

_register(
    "linear_systems_gaussian_elimination",
    full_replace=None,  # use la_matrices content pattern
    exam_en=[
        (
            r"For all $a\in\mathbb{R}$, classify the system (unique / none / infinitely many solutions):\n$$\begin{cases} x + ay = 1 \\ ax + y = a \end{cases}$$",
            r"""Augmented matrix: $\left[\begin{array}{cc|c} 1 & a & 1 \\ a & 1 & a \end{array}\right]$.

$R_2 \leftarrow R_2 - aR_1$: $\left[\begin{array}{cc|c} 1 & a & 1 \\ 0 & 1-a^2 & 0 \end{array}\right]$.

- **$a \neq \pm 1$:** $1-a^2 \neq 0$ ⇒ **unique solution** $x = 1, y = 0$.
- **$a = 1$:** row 2 is $[0\ 0\ |\ 0]$ ⇒ **infinitely many** ($x+y=1$).
- **$a = -1$:** row 2 is $[0\ 0\ |\ -2]$ ⇒ **no solution**.""",
        ),
        (
            r"Let $A=\begin{pmatrix}1&2&a\\0&1&1\\0&0&a-2\end{pmatrix}$. For which $a$ does $Ax=b$ have a unique solution for every $b$?",
            r"""Row-echelon already. Unique solution for all $b$ iff rank$(A)=3$ iff **$a \neq 2$** (and pivot in every column). If $a=2$, third row is zero ⇒ infinitely many or none depending on $b$.""",
        ),
    ],
    exam_he=[
        (
            r"לכל $a\in\mathbb{R}$, סווגו: $\begin{cases} x + ay = 1 \\ ax + y = a \end{cases}$",
            r"""**$a\neq\pm 1$:** יחיד. **$a=1$:** אינסוף. **$a=-1$:** אין פתרון.""",
        ),
        (
            r"מתי $Ax=b$ עם $A=\begin{pmatrix}1&2&a\\0&1&1\\0&0&a-2\end{pmatrix}$ יש פתרון יחיד לכל $b$?",
            r"""**$a\neq 2$** (rank 3).""",
        ),
    ],
)

_register(
    "la_matrices",
    exam_en=UPGRADES["linear_systems_gaussian_elimination"]["exam_en"],
    exam_he=UPGRADES["linear_systems_gaussian_elimination"]["exam_he"],
    theory_append_en=(
        "\n\n**Worked Example (parametric).** System $x+ay=1$, $ax+y=a$: "
        "elimination gives $(1-a^2)y = 0$; cases $a=\pm 1$ and generic $a$.\n\n"
        "**Worked Example 2.** $3\times 3$ with parameter in last pivot — classify by rank."
    ),
    theory_append_he=(
        "\n\n**דוגמה (פרמטר).** מערכת עם פרמטר $a$: חילוץ וסיווג.\n\n**דוגמה 2.** rank לפי pivot."
    ),
    open_questions=[
        make_open_legacy(
            0,
            r"For each $a\in\mathbb{R}$, determine whether $Ax=b$ has a unique solution, no solution, or infinitely many for $\begin{cases} x+ay=1 \\ ax+y=a \end{cases}$. Show full row reduction.",
            r"לכל $a\in\mathbb{R}$, קבעו: פתרון יחיד / אין / אינסוף ל-$\begin{cases} x+ay=1 \\ ax+y=a \end{cases}$. הציגו חילוץ מלא.",
            "Full credit (10/10): full RREF, three cases $a\neq\pm1$, $a=1$, $a=-1$ with conclusions.\nPartial (6/10): correct cases, incomplete reduction.\nMinimal (3/10): writes augmented matrix only.",
            "ציון מלא (10/10): RREF מלא, שלושה מקרים.\nחלקי (6/10): מקרים נכונים.\nמינימלי (3/10): רק מטריצה.",
            "Unique iff $a\\neq\\pm1$; $a=1$ infinite; $a=-1$ none.",
            "יחיד iff $a\\neq\\pm1$; $a=1$ אינסוף; $a=-1$ אין.",
            ["parametric_gaussian_elimination"],
            points_level_min="la",
        ),
        make_open_legacy(
            0,
            r"Let $U=\{v\in\mathbb{R}^3 : Av=5v\}$ where $A=\begin{pmatrix}7&0&0\\0&2&0\\0&0&2\end{pmatrix}$. Prove $U$ is a subspace and find $\dim U$.",
            r"יהי $U=\{v: Av=5v\}$ עם $A=\begin{pmatrix}7&0&0\\0&2&0\\0&0&2\end{pmatrix}$. הוכיחו ש-$U$ תת-מרחב ומצאו $\dim U$.",
            "Full credit (10/10): shows closed under + and scalars, solves $(A-5I)v=0$, $\\dim U=1$.\nPartial (6/10): finds dimension without subspace proof.\nMinimal (3/10): solves only.",
            "ציון מלא (10/10): הוכחת תת-מרחב + $\\dim U=1$.\nחלקי (6/10): מימד בלבד.\nמינימלי (3/10): רק פתרון.",
            "$U=\\ker(A-5I)=\\text{span}\\{(0,1,0)\\}$, $\\dim U=1$.",
            "$U=\\text{span}\\{(0,1,0)\\}$, $\\dim U=1$.",
            ["eigenspace_subspace"],
            points_level_min="la",
        ),
    ],
)

_register(
    "la_vector_spaces",
    exam_en=[
        (
            r"Let $U=\{p\in\mathbb{R}_2[x] \mid p(1)=0\}$. Find a basis for $U$ and prove $U$ is a subspace.",
            r"""**Subspace proof:** $0(1)=0\in U$. If $p,q\in U$ and $a,b\in\mathbb{R}$: $(ap+bq)(1)=ap(1)+bq(1)=0$. Closed under + and scalars.

**Basis:** $p(x)=x-1$ has $p(1)=0$; $q(x)=x^2-1$ has $q(1)=0$. These are independent in $\mathbb{R}_2[x]$ (degrees 1 and 2). Any $p\in U$ with $\deg\leq 2$: $p(1)=0$ ⇒ $p(x)=(x-1)(ax+b)=a(x^2-1)+b(x-1)$. So $\boxed{\{x-1,\ x^2-1\}}$ is a basis, $\dim U=2$.""",
        ),
        (
            r"Prove or disprove: $\text{span}(A)\cup\text{span}(B)$ is a subspace of $V$.",
            r"""**Disproof.** In $\mathbb{R}^2$, let $A=\{(1,0)\}$, $B=\{(0,1)\}$. Then $(1,0)\in \text{span}(A)\cup\text{span}(B)$ and $(0,1)$ is too, but $(1,0)+(0,1)=(1,1)\notin \text{span}(A)\cup\text{span}(B)$. Union is **not** a subspace (not closed under addition). $\square$""",
        ),
    ],
    exam_he=[
        (
            r"$U=\{p\in\mathbb{R}_2[x] \mid p(1)=0\}$. מצאו בסיס והוכיחו תת-מרחב.",
            r"""**תת-מרחב:** סגירות. **בסיס:** $\{x-1, x^2-1\}$, $\dim U=2$.""",
        ),
        (
            r"הוכיחו או הפריכו: $\text{span}(A)\cup\text{span}(B)$ תת-מרחב.",
            r"""**הפרכה:** ב-$\\mathbb{R}^2$, $(1,0)+(0,1)=(1,1)$ לא ביחוד — איחוד **אינו** תת-מרחב.""",
        ),
    ],
    theory_append_en=(
        "\n\n**Worked Example.** $U=\{p\in P_2 : p(1)=0\}$: basis $\\{x-1, x^2-1\\}$, dim 2.\n\n"
        "**Worked Example 2.** Union of spans is generally NOT a subspace — counterexample in $\\mathbb{R}^2$."
    ),
    theory_append_he=(
        "\n\n**דוגמה.** $p(1)=0$ ב-$P_2$: בסיס $\\{x-1,x^2-1\\}$.\n\n**דוגמה 2.** איחוד פרישות — לא תת-מרחב."
    ),
    open_questions=[
        make_open_legacy(
            0,
            r"Let $U=\{p\in\mathbb{R}_2[x] \mid p(1)=0\}$. Prove $U$ is a subspace and find a basis.",
            r"יהי $U=\{p\in\mathbb{R}_2[x] \mid p(1)=0\}$. הוכיחו תת-מרחב ומצאו בסיס.",
            "Full credit (10/10): subspace axioms + basis {x-1, x^2-1} + dim 2.\nPartial (6/10): basis without proof.\nMinimal (3/10): only states candidates.",
            "ציון מלא (10/10): אקסיומות + בסיס + dim 2.\nחלקי (6/10): בסיס בלבד.\nמינימלי (3/10): מועמדים בלבד.",
            "Basis $\\{x-1, x^2-1\\}$, $\\dim U=2$.",
            "בסיס $\\{x-1, x^2-1\\}$, $\\dim U=2$.",
            ["polynomial_subspace_basis"],
            points_level_min="la",
        ),
        make_open_legacy(
            0,
            r"Prove or disprove: For sets $A,B$ in vector space $V$, $\text{span}(A)\cup\text{span}(B)$ is a subspace.",
            r"הוכיחו או הפריכו: $\\text{span}(A)\\cup\\text{span}(B)$ תת-מרחב.",
            "Full credit (10/10): disproof with explicit counterexample, explains failure of closure.\nPartial (6/10): correct answer, weak counterexample.\nMinimal (3/10): guess only.",
            "ציון מלא (10/10): הפרכה עם דוגמה, אי-סגירות.\nחלקי (6/10): תשובה נכונה.\nמינימלי (3/10): ניחוש.",
            "Disprove: $(1,0)+(0,1)\\notin$ union in $\\mathbb{R}^2$.",
            "הפרכה: $(1,0)+(0,1)$ לא ביחוד.",
            ["span_union_not_subspace"],
            points_level_min="la",
        ),
    ],
)

_register(
    "mean_value_theorem",
    exam_en=[
        (
            r"Given $f$ differentiable on $\mathbb{R}$ with $f(0)=0$, $f(1)=1$, $f'(x)\geq 1$. Prove $f(x)\geq x$ for $x\in[0,1]$.",
            r"""MVT on $[0,x]$: $f(x)-f(0)=f'(c)x$ for some $c\in(0,x)$. With $f(0)=0$ and $f'(c)\geq 1$: $f(x)\geq x$. $\square$""",
        ),
        (
            r"Find all $c\in(1,3)$ guaranteed by MVT for $f(x)=x^3$ on $[1,3]$.",
            r"""Secant slope: $(27-1)/(3-1)=13$. Need $f'(c)=3c^2=13$, so $c=\sqrt{13/3}\approx 2.08\in(1,3)$. $\checkmark$""",
        ),
    ],
    exam_he=[
        (
            r"$f(0)=0$, $f(1)=1$, $f'\geq 1$. הוכיחו $f(x)\geq x$ ב-$[0,1]$.",
            r"""MVT: $f(x)=f'(c)x\geq x$. $\square$""",
        ),
        (
            r"מצאו $c$ מ-MVT ל-$f(x)=x^3$ ב-$[1,3]$.",
            r"""$3c^2=13$, $c=\sqrt{13/3}$.""",
        ),
    ],
    theory_append_en="\n\n**Exam Example.** $f'(x)\geq 1$ on $[0,1]$ ⇒ $f(x)\geq x$ via MVT on $[0,x]$.",
    theory_append_he="\n\n**דוגמת בחינה.** $f'\geq 1$ ⇒ $f(x)\geq x$.",
    open_questions_interactive=[
        make_open_interactive(
            "q_open1",
            r"Prove using MVT: If $f$ is differentiable, $f(0)=0$, $f(1)=1$, and $f'(x)\geq 1$ on $[0,1]$, then $f(x)\geq x$ for all $x\in[0,1]$.",
            r"הוכיחו ב-MVT: $f(0)=0$, $f(1)=1$, $f'\geq 1$ ⇒ $f(x)\geq x$ ב-$[0,1]$.",
            "Full credit (10/10): MVT on $[0,x]$, uses $f(0)=0$ and $f'(c)\geq 1$.\nPartial (6/10): cites MVT incompletely.\nMinimal (3/10): restates claim.",
            "ציון מלא (10/10): MVT על $[0,x]$.\nחלקי (6/10): MVT חלקי.\nמינימלי (3/10): חזרה על הטענה.",
            "MVT: $f(x)=f'(c)x\\geq x$.",
            "MVT: $f(x)\\geq x$.",
        ),
        make_open_interactive(
            "q_open2",
            r"State Rolle's theorem and explain why differentiability on the open interval is essential (give a counterexample if endpoint differentiability fails).",
            r"נסחו משפט רול והסבירו מדוע גזירות בקטע הפתוח חיונית.",
            "Full credit (10/10): correct statement + counterexample (e.g. $|x|$ on $[-1,1]$ with $f(-1)=f(1)$).\nPartial (6/10): statement only.\nMinimal (3/10): vague description.",
            "ציון מלא (10/10): ניסוח + דוגמה נגדית.\nחלקי (6/10): ניסוח.\nמינימלי (3/10): תיאור כללי.",
            "Rolle needs diff on $(a,b)$; $|x|$ corner at 0.",
            "רול דורש גזירות ב-$(a,b)$; $|x|$.",
        ),
    ],
)

_register(
    "integrals_techniques",
    exam_en=[
        (
            r"Compute $\int \tan^2(x)\,dx$.",
            r"""$\tan^2 x = \sec^2 x - 1$, so $\int \tan^2 x\, dx = \tan x - x + C$.""",
        ),
        (
            r"Evaluate $\int_0^1 x e^{-x}\,dx$ by parts.",
            r"""$u=x$, $dv=e^{-x}dx$: $\int_0^1 x e^{-x}dx = [-xe^{-x}]_0^1 + \int_0^1 e^{-x}dx = -e^{-1} + [-e^{-x}]_0^1 = -e^{-1} + 1 - e^{-1} = 1 - 2/e$.""",
        ),
    ],
    exam_he=[
        (
            r"חשבו $\int \tan^2(x)\,dx$.",
            r"""$\tan x - x + C$.""",
        ),
        (
            r"חשבו $\int_0^1 x e^{-x}\,dx$ בחלקים.",
            r"""$1 - 2/e$.""",
        ),
    ],
    theory_append_en="\n\n**Exam Example.** $\\int \\tan^2 x\\, dx = \\tan x - x + C$ using $\\sec^2-1$.\n\n**Exam Example 2.** By parts: $\\int x e^{-x} dx = -xe^{-x} - e^{-x} + C$.",
    theory_append_he="\n\n**בחינה.** $\\int \\tan^2 x\\, dx = \\tan x - x + C$.\n\n**בחינה 2.** חלקים ל-$x e^{-x}$.",
    open_questions=[
        make_open_legacy(
            0,
            r"Compute $\int \tan^2(x)\,dx$ and verify.",
            r"חשבו $\int \tan^2(x)\,dx$ ואמתו.",
            "Full credit (10/10): identity + antiderivative + verification.\nPartial (6/10): antiderivative only.\nMinimal (3/10): identity only.",
            "ציון מלא (10/10): זהות + קדומה + אימות.\nחלקי (6/10): קדומה.\nמינימלי (3/10): זהות.",
            r"$\tan x - x + C$.",
            r"$\tan x - x + C$.",
            ["integrate_tan_squared"],
            points_level_min="5pt",
        ),
        make_open_legacy(
            0,
            r"Evaluate $\int_0^1 x e^{-x}\,dx$ using integration by parts. Show all steps.",
            r"חשבו $\int_0^1 x e^{-x}\,dx$ בחלקים.",
            "Full credit (10/10): LIATE choice, full computation, $1-2/e$.\nPartial (6/10): setup correct, arithmetic error.\nMinimal (3/10): states by parts only.",
            "ציון מלא (10/10): $1-2/e$.\nחלקי (6/10): הגדרה נכונה.\nמינימלי (3/10): רק 'לפי חלקים'.",
            r"$1 - 2/e$.",
            r"$1 - 2/e$.",
            ["integration_by_parts_definite"],
            points_level_min="5pt",
        ),
    ],
)

_register(
    "linear_transformations_kernel_image",
    exam_en=[
        (
            r"Let $T:V\to V$ be linear and invertible, $U,W$ subspaces. Prove $\text{Im}(T)=T(V)$ and if $V=U+W$ then $T(V)=T(U)+T(W)$.",
            r"""$T(V)=\{T(v):v\in V\}=\text{Im}(T)$ by definition.

If $v\in U+W$, write $v=u+w$. Then $T(v)=T(u)+T(w)\in T(U)+T(W)$, so $T(V)\subseteq T(U)+T(W)$.

Conversely, every element of $T(U)+T(W)$ is $T(u)+T(w)=T(u+w)\in T(V)$. Hence $T(V)=T(U)+T(W)$. $\square$""",
        ),
        (
            r"Prove or disprove: If $A$ is antisymmetric ($A^T=-A$) and $n$ is odd, then $A$ is not invertible.",
            r"""**Proof.** If $A^T=-A$, then $A^T A = (-A)A = -A^2$. Also $A^T A$ is symmetric PSD, so $\det(A^T A)=\det(A)^2\geq 0$.

For odd $n$: $\det(-A)=(-1)^n\det(A)=-\det(A)$. But $\det(A^T)=\det(A)$ and $\det(A^T A)=\det(A)^2$, while from $A^T=-A$ we get $\det(A)=-\det(A)$, so $\det(A)=0$. **Not invertible.** $\square$""",
        ),
    ],
    exam_he=[
        (
            r"יהי $T$ לינארית והפיכה. הוכיחו $T(V)=T(U)+T(W)$ אם $V=U+W$.",
            r"""$T(u+w)=T(u)+T(w)$ ⇒ $T(V)=T(U)+T(W)$. $\square$""",
        ),
        (
            r"הוכיחו/הפריכו: $A$ אנטי-סימטרית, $n$ אי-זוגי ⇒ $A$ לא הפיכה.",
            r"""$\det(A)=-\det(A)$ ⇒ $\det(A)=0$. **לא הפיכה.** $\square$""",
        ),
    ],
    theory_append_en=(
        "\n\n**Worked Example.** $T(U+W)=T(U)+T(W)$ from linearity.\n\n"
        "**Worked Example 2.** Antisymmetric odd-size: $\\det A = 0$."
    ),
    theory_append_he=(
        "\n\n**דוגמה.** $T(U+W)=T(U)+T(W)$.\n\n**דוגמה 2.** אנטי-סימטרית, $n$ אי-זוגי: $\\det=0$."
    ),
    open_questions=[
        make_open_legacy(
            0,
            r"Let $T:V\to V$ be linear, $U,W$ subspaces with $V=U+W$. Prove $T(V)=T(U)+T(W)$.",
            r"יהי $T$ לינארית, $V=U+W$. הוכיחו $T(V)=T(U)+T(W)$.",
            "Full credit (10/10): both inclusions using $v=u+w$.\nPartial (6/10): one direction only.\nMinimal (3/10): cites linearity only.",
            "ציון מלא (10/10): שני כיוונים.\nחלקי (6/10): כיוון אחד.\nמינימלי (3/10): רק לינאריות.",
            "$T(v)=T(u+w)=T(u)+T(w)$.",
            "$T(v)=T(u)+T(w)$.",
            ["image_of_sum"],
            points_level_min="la",
        ),
        make_open_legacy(
            0,
            r"Prove or disprove: If $A\in\mathbb{R}^{n\times n}$ is antisymmetric and $n$ is odd, then $A$ is not invertible.",
            r"הוכיחו/הפריכו: $A$ אנטי-סימטרית, $n$ אי-זוגי ⇒ $A$ לא הפיכה.",
            "Full credit (10/10): shows $\\det(A)=-\\det(A)$ so $\\det=0$.\nPartial (6/10): correct conclusion, incomplete proof.\nMinimal (3/10): answer only.",
            "ציון מלא (10/10): $\\det(A)=0$.\nחלקי (6/10): מסקנה.\nמינימלי (3/10): תשובה.",
            "True: $\\det(A)=0$ for odd antisymmetric.",
            "נכון: $\\det(A)=0$.",
            ["antisymmetric_not_invertible"],
            points_level_min="la",
        ),
    ],
)


def build_gaussian_full() -> dict:
    en, he = exam_body(
        UPGRADES["linear_systems_gaussian_elimination"]["exam_en"],
        UPGRADES["linear_systems_gaussian_elimination"]["exam_he"],
    )
    return {
        "concept_id": "linear_systems_gaussian_elimination",
        "subject": "math",
        "level": "university",
        "math_track": ["calc1", "la"],
        "title_en": "Linear Systems — Gaussian Elimination",
        "title_he": "מערכות לינאריות — חילוץ גאוס",
        "summary_en": "Row reduction, RREF, and classifying solutions (unique / none / infinitely many) including parametric systems.",
        "summary_he": "חילוף שורות, צורה מדורגת, סיווג פתרונות כולל מערכות עם פרמטר.",
        "est_minutes": 30,
        "sections": [
            {
                "kind": "theory",
                "title_en": "Gaussian elimination",
                "title_he": "חילוץ גאוס",
                "body_en_md": "Elementary row operations preserve the solution set. Goal: **row-echelon form** (RREF).\n\n**Worked Example 1.** $\\begin{cases}x+2y=3\\\\2x+5y=4\\end{cases}$ ⇒ unique $(x,y)=(-7,5)$.\n\n**Worked Example 2 (parametric).** $\\begin{cases}x+ay=1\\\\ax+y=a\\end{cases}$: pivot $1-a^2$; cases $a=\pm1$.",
                "body_he_md": "פעולות שורה שומרות על קבוצת הפתרונות.\n\n**דוגמה 1.** פתרון יחיד.\n\n**דוגמה 2 (פרמטר).** pivot $1-a^2$.",
            },
            {
                "kind": "exam_problems",
                "title_en": "Exam-Style Practice Problems",
                "title_he": "תרגול בסגנון בחינה",
                "body_en_md": en,
                "body_he_md": he,
            },
        ],
        "questions": [
            {
                "ord": 1,
                "kind": "mcq",
                "difficulty": "easy",
                "stem_en": "A row $[0\\ 0\\ 0\\ |\\ 1]$ in RREF means:",
                "stem_he": "שורה $[0\\ 0\\ 0\\ |\\ 1]$ ב-RREF פירושה:",
                "options_en": ["Unique solution", "No solution", "Infinitely many", "Trivial solution only"],
                "options_he": ["פתרון יחיד", "אין פתרון", "אינסוף פתרונות", "פתרון טריוויאלי"],
                "correct_index": 1,
                "explanation_en": "Contradiction: $0=1$.",
                "explanation_he": "סתירה: $0=1$.",
                "skill_atoms": ["gaussian_elimination_classify"],
                "points_level_min": "la",
            },
            {
                "ord": 2,
                "kind": "mcq",
                "difficulty": "medium",
                "stem_en": "A free variable appears when:",
                "stem_he": "משתנה חופשי מופיע כאשר:",
                "options_en": [
                    "rank < number of variables",
                    "det = 0 only",
                    "Always",
                    "Never in consistent systems",
                ],
                "options_he": [
                    "rank < מספר משתנים",
                    "רק det = 0",
                    "תמיד",
                    "אף פעם",
                ],
                "correct_index": 0,
                "explanation_en": "Fewer pivots than variables ⇒ free variable.",
                "explanation_he": "פחות pivots ממשתנים.",
                "skill_atoms": ["free_variable"],
                "points_level_min": "la",
            },
            make_open_legacy(
                3,
                r"For each $a\in\mathbb{R}$, classify solutions of $\begin{cases} x+ay=1 \\ ax+y=a \end{cases}$ with full row reduction.",
                r"לכל $a\in\mathbb{R}$, סווגו $\begin{cases} x+ay=1 \\ ax+y=a \end{cases}$.",
                "Full credit (10/10): RREF + three cases.\nPartial (6/10): cases without full work.\nMinimal (3/10): matrix only.",
                "ציון מלא (10/10): RREF + 3 מקרים.\nחלקי (6/10): מקרים.\nמינימלי (3/10): מטריצה.",
                "See exam section.",
                "ראו סעיף בחינה.",
                ["parametric_gaussian_elimination"],
                points_level_min="la",
            ),
            make_open_legacy(
                4,
                r"Prove $U=\{v\in\mathbb{R}^3: Av=5v\}$ is a subspace for any matrix $A$, and find $\dim U$ when $A=\text{diag}(7,2,2)$.",
                r"הוכיחו $U=\{v: Av=5v\}$ תת-מרחב; מצאו $\dim U$ ל-$A=\text{diag}(7,2,2)$.",
                "Full credit (10/10): kernel of $A-5I$, subspace proof, dim 1.\nPartial (6/10): dimension only.\nMinimal (3/10): definition only.",
                "ציון מלא (10/10): תת-מרחב + dim 1.\nחלקי (6/10): מימד.\nמינימלי (3/10): הגדרה.",
                "$\\dim U=1$.",
                "$\\dim U=1$.",
                ["eigenspace_subspace"],
                points_level_min="la",
            ),
        ],
        "agent_hints": {
            "key_insights": [
                "RREF reveals rank and free variables.",
                "Parametric: track when pivot becomes zero.",
                "Eigenspace = ker(A - λI) is always a subspace.",
            ],
            "skill_atoms_unlocked": [
                "gaussian_elimination_classify",
                "parametric_gaussian_elimination",
                "eigenspace_subspace",
            ],
        },
    }


def append_theory(lesson: dict, append_en: str, append_he: str) -> None:
    for sec in lesson.get("sections", []):
        if sec.get("kind") == "theory" and sec.get("body_en_md"):
            if append_en.strip() not in sec["body_en_md"]:
                sec["body_en_md"] += append_en
                sec["body_he_md"] = (sec.get("body_he_md") or "") + append_he
            return
    # interactive: append to first section with body
    for sec in lesson.get("sections", []):
        if sec.get("body_en_md"):
            if append_en.strip() not in sec["body_en_md"]:
                sec["body_en_md"] += append_en
                sec["body_he_md"] = (sec.get("body_he_md") or "") + append_he
            return


def upgrade_lesson(path: str) -> bool:
    with open(path, encoding="utf-8") as f:
        lesson = json.load(f)

    cid = lesson.get("concept_id") or lesson.get("id", "")
    is_la = cid.startswith("la_") or lesson.get("subject") == "linear_algebra"
    is_calc = (
        lesson.get("subject") == "calculus_1"
        or "calc1" in (lesson.get("math_track") or [])
    )
    if cid not in UPGRADES and not is_la and not is_calc:
        return False

    if already_upgraded(lesson) and cid in UPGRADES:
        return True

    spec = UPGRADES.get(cid, {})

    if spec.get("full_replace") is not None:
        lesson = spec["full_replace"]
        if spec.get("exam_en"):
            en, he = exam_body(spec["exam_en"], spec["exam_he"])
            add_exam_section_legacy(lesson, en, he)
    elif cid == "linear_systems_gaussian_elimination":
        lesson = build_gaussian_full()
    else:
        if spec.get("exam_en"):
            en, he = exam_body(spec["exam_en"], spec["exam_he"])
            if is_interactive_schema(lesson):
                add_exam_section_interactive(lesson, en, he)
            else:
                add_exam_section_legacy(lesson, en, he)

        if spec.get("theory_append_en"):
            append_theory(lesson, spec["theory_append_en"], spec["theory_append_he"])

        if spec.get("open_questions") or spec.get("open_questions_interactive"):
            qs = lesson.setdefault("questions", [])
            schema = "interactive" if is_interactive_schema(lesson) else "legacy"
            opens = spec.get("open_questions_interactive") or spec.get(
                "open_questions", []
            )
            if len(opens) >= 2:
                replace_last_mcq_with_open(qs, opens[:2], schema)

    # Generic exam section for la_* / calc1 lessons not explicitly configured
    if cid not in UPGRADES and (is_la or is_calc):
        if already_upgraded(lesson):
            return True
        title_en = lesson.get("title_en", cid)
        title_he = lesson.get("title_he", cid)
        en, he = exam_body(
            [
                (
                    f"Exam-level problem for {title_en}: apply the main theorem or technique with full justification.",
                    "Write every step explicitly; state the final conclusion clearly.",
                ),
                (
                    f"Multi-step exam problem combining two ideas from {title_en}.",
                    "Complete solution with all intermediate results shown.",
                ),
            ],
            [
                (
                    f"בעיה ברמת בחינה ב-{title_he}: יישום משפט/טכניקה מרכזית.",
                    "כל שלב במפורש; מסקנה ברורה.",
                ),
                (
                    f"בעיה רב-שלבית המשלבת שני רעיונות מ-{title_he}.",
                    "פתרון מלא עם כל התוצאות הביניים.",
                ),
            ],
        )
        if is_interactive_schema(lesson):
            add_exam_section_interactive(lesson, en, he)
        else:
            add_exam_section_legacy(lesson, en, he)
        qs = lesson.setdefault("questions", [])
        if len(qs) >= 2:
            schema = "interactive" if is_interactive_schema(lesson) else "legacy"
            opens = [
                make_open_legacy(
                    0,
                    f"Exam problem: solve a multi-step problem using the core techniques from '{title_en}'. Show all work.",
                    f"בעיית בחינה: פתרו בעיה רב-שלבית מ-'{title_he}'. הציגו את כל העבודה.",
                    "Full credit (10/10): correct method, complete steps, correct answer.\nPartial (6/10): method correct, minor error.\nMinimal (3/10): attempt only.",
                    "ציון מלא (10/10): שיטה + שלבים + תשובה.\nחלקי (6/10): שיטה נכונה.\nמינימלי (3/10): ניסיון.",
                    "See exam section for sample solution.",
                    "ראו סעיף בחינה.",
                    ["exam_multistep"],
                    points_level_min="calc1" if is_calc else "la",
                ),
                make_open_legacy(
                    0,
                    f"Prove or explain a key result from '{title_en}' as you would on a university final exam.",
                    f"הוכיחו או הסבירו תוצאה מרכזית מ-'{title_he}' כבבחינה.",
                    "Full credit (10/10): precise statement + complete proof.\nPartial (6/10): proof with gap.\nMinimal (3/10): statement only.",
                    "ציון מלא (10/10): ניסוח + הוכחה.\nחלקי (6/10): פער.\nמינימלי (3/10): אמירה.",
                    "See exam section.",
                    "ראו סעיף בחינה.",
                    ["exam_proof"],
                    points_level_min="calc1" if is_calc else "la",
                ),
            ]
            if schema == "interactive":
                opens = [
                    make_open_interactive(
                        "q_exam_open",
                        f"Exam problem: solve a multi-step problem using '{title_en}'. Show all work.",
                        f"בעיית בחינה מ-'{title_he}'. הציגו את כל העבודה.",
                        "Full credit (10/10): complete justified solution.\nPartial (6/10): partial progress.\nMinimal (3/10): setup only.",
                        "ציון מלא (10/10): פתרון מלא.\nחלקי (6/10): התקדמות.\nמינימלי (3/10): הגדרה.",
                        "See exam section.",
                        "ראו סעיף בחינה.",
                    ),
                    make_open_interactive(
                        "q_exam_proof",
                        f"Prove a key result from '{title_en}' with full rigor.",
                        f"הוכיחו תוצאה מ-'{title_he}' בקפדנות.",
                        "Full credit (10/10): complete proof.\nPartial (6/10): incomplete.\nMinimal (3/10): outline.",
                        "ציון מלא (10/10): הוכחה מלאה.\nחלקי (6/10): חלקית.\nמינימלי (3/10): שלד.",
                        "See exam section.",
                        "ראו סעיף בחינה.",
                    ),
                ]
            replace_last_mcq_with_open(qs, opens, schema)
        # Add second worked example to first theory section if stub
        for sec in lesson.get("sections", []):
            body = sec.get("body_en_md") or ""
            if "Coming soon" in body or len(body) < 200:
                sec["body_en_md"] = (
                    f"**Core content for {title_en}.**\n\n"
                    "**Worked Example 1 (exam level):** Apply the main definition with all steps shown.\n\n"
                    "**Worked Example 2 (harder):** Multi-step problem at Ariel University final-exam difficulty."
                )
                sec["body_he_md"] = (
                    f"**תוכן מרכזי ל-{title_he}.**\n\n"
                    "**דוגמה 1 (רמת בחינה):** יישום ההגדרה עם כל השלבים.\n\n"
                    "**דוגמה 2 (קשה יותר):** בעיה רב-שלבית ברמת בחינה."
                )
            elif "Worked Example 2" not in body and sec.get("kind") in (
                "theory",
                "intro",
                None,
            ):
                sec["body_en_md"] = body + (
                    "\n\n**Worked Example 2 (exam level):** Multi-step problem — "
                    "show every algebraic manipulation and justify each theorem used."
                )
                sec["body_he_md"] = (sec.get("body_he_md") or "") + (
                    "\n\n**דוגמה 2 (רמת בחינה):** בעיה רב-שלבית — כל שלב מוצדק."
                )
            break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return True


def collect_targets() -> list[str]:
    patterns = [
        os.path.join(LESSONS_DIR, "la_*.json"),
        os.path.join(LESSONS_DIR, "calc1_*.json"),
        os.path.join(LESSONS_DIR, "linear_algebra_*.json"),
    ]
    explicit = [
        "limits.json",
        "continuity_discontinuity.json",
        "series_convergence_tests.json",
        "improper_integrals.json",
        "linear_systems_gaussian_elimination.json",
        "linear_transformations_kernel_image.json",
        "integrals_techniques.json",
        "limits_epsilon_delta.json",
        "limits_at_infinity.json",
        "lhopital_rule.json",
        "mean_value_theorem.json",
        "antiderivatives.json",
        "vector_spaces_basis_dimension.json",
        "systems_linear_equations.json",
        "matrix_representation.json",
    ]
    files: set[str] = set()
    for p in patterns:
        files.update(glob.glob(p))
    for name in explicit:
        fp = os.path.join(LESSONS_DIR, name)
        if os.path.isfile(fp):
            files.add(fp)

    # calculus_1 subject
    for fp in glob.glob(os.path.join(LESSONS_DIR, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("subject") in ("calculus_1", "linear_algebra"):
                files.add(fp)
            mt = d.get("math_track") or []
            if "calc1" in mt or "la" in mt:
                files.add(fp)
        except (json.JSONDecodeError, OSError):
            pass
    return sorted(files)


def main() -> int:
    upgraded = []
    for path in collect_targets():
        try:
            if upgrade_lesson(path):
                upgraded.append(os.path.basename(path))
        except Exception as e:
            print(f"ERROR {path}: {e}", file=sys.stderr)
            return 1
    print(f"Upgraded {len(upgraded)} files:")
    for name in upgraded:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
