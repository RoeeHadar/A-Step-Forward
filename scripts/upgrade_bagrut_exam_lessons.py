#!/usr/bin/env python3
"""Upgrade HS math/physics/makhina lesson JSON with Bagrut exam sections and open questions."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "scripts" / "seed_data" / "lessons"

EXAM_INTRO_EN = """### How to approach Bagrut-style questions

In the Bagrut exam, you will see multi-part questions (a, b, c) where each part builds on the previous. You must:
- **Show all steps** — the examiner grades your process, not just the answer
- **Write complete sentences** for proofs and justifications
- **Check your answer** makes sense before moving on"""

EXAM_INTRO_HE = """### איך לגשת לשאלות בסגנון בגרות

בבחינת הבגרות תראו שאלות רב-סעיפיות (א, ב, ג) שכל סעיף נשען על הקודם. חובה:
- **להראות את כל השלבים** — הבוחן מדרג את הדרך, לא רק את התשובה
- **לכתוב משפטים מלאים** בהוכחות ובנימוקים
- **לבדוק שהתשובה הגיונית** לפני שממשיכים"""


def categorize(name: str, data: dict) -> list[str]:
    cats: list[str] = []
    n = name.lower()
    subj = str(data.get("subject", ""))
    if re.search(r"3pt|bagrut_3|hs_math_3", n) or subj == "high_school_math_3pt":
        cats.append("3pt")
    if re.search(r"4pt|bagrut_4|hs_math_4", n) or subj == "high_school_math_4pt":
        cats.append("4pt")
    if re.search(r"5pt|bagrut_5|hs_math_5", n) or subj == "high_school_math_5pt":
        cats.append("5pt")
    if re.search(r"physics_hs|hs_physics|bagrut_physics", n):
        cats.append("physics")
    blob = json.dumps(data, ensure_ascii=False)[:12000]
    if "hs_physics" in blob and "physics" not in cats:
        cats.append("physics")
    if re.search(r"makhina|preuni|pre_uni", n) or "makhina" in subj:
        cats.append("makhina")
    return cats


def primary_cat(cats: list[str]) -> str:
    for c in ("makhina", "3pt", "4pt", "5pt", "physics"):
        if c in cats:
            return c
    return cats[0] if cats else "3pt"


def exam_body(cat: str, stem: str) -> tuple[str, str]:
    """Return (body_en_md, body_he_md) with two practice problems for the lesson topic."""
    s = stem.lower()

    # ── 3pt math ──
    if cat == "3pt":
        if "probability" in s or "statistics" in s or "regression" in s or "data" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

(a) A bag has 5 red and 3 blue balls. Two balls are drawn **without replacement**. Find the probability both are the same color.

(b) Given that the first ball drawn was red, find the probability the second is also red.

**Complete Solution:**

(a) Same color = both red OR both blue.
$P(RR) = \\frac{5}{8}\\cdot\\frac{4}{7} = \\frac{20}{56}$, $P(BB) = \\frac{3}{8}\\cdot\\frac{2}{7} = \\frac{6}{56}$.
$P(\\text{same}) = \\frac{26}{56} = \\frac{13}{28}$.

(b) After one red remains 4 red of 7: $P(R_2|R_1) = \\frac{4}{7}$.

---

**Practice Problem 2:**

(a) A fair coin is flipped three times. Find $P(\\text{at least two heads})$.

(b) Use the complement rule to verify your answer.

**Complete Solution:**

(a) Favorable: HHH, HHT, HTH, THH → $P = \\frac{4}{8} = \\frac{1}{2}$.

(b) Complement = 0 or 1 head: TTT, HTT, THT, TTH → $\\frac{4}{8} = \\frac{1}{2}$ ✓"""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

(א) בשק 5 כדורים אדומים ו-3 כחולים. שולפים **ללא החזרה** 2 כדורים. מצאו את ההסתברות ששניהם באותו צבע.

(ב) ידוע שהראשון אדום — מה ההסתברות שגם השני אדום?

**פתרון מלא:**

(א) $P(RR)=\\frac{5}{8}\\cdot\\frac{4}{7}=\\frac{20}{56}$, $P(BB)=\\frac{3}{8}\\cdot\\frac{2}{7}=\\frac{6}{56}$ → $P=\\frac{13}{28}$.

(ב) $P(R_2|R_1)=\\frac{4}{7}$.

---

**שאלת תרגול 2:**

(א) מטבע הוגן נזרק 3 פעמים. מצאו $P(\\text{לפחות 2 עצים})$.

(ב) אמתו עם כלל המשלים.

**פתרון מלא:**

(א) 4 מתוך 8 → $\\frac{1}{2}$. (ב) משלים = 0 או 1 עץ → $\\frac{1}{2}$ ✓"""
            return en, he
        en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

(a) Find the vertex of $f(x)=x^2-6x+8$ and sketch the parabola.

(b) Find the $x$-intercepts and state the axis of symmetry.

**Complete Solution:**

(a) Complete the square: $f(x)=(x-3)^2-1$ → vertex $(3,-1)$, opens upward.

(b) $(x-3)^2=1$ → $x=2,4$. Axis: $x=3$.

---

**Practice Problem 2:**

An arithmetic sequence has $a_1=3$ and $a_{n+1}=a_n+4$.

(a) Find $a_{10}$.

(b) Find $\\sum_{k=1}^{10} a_k$.

**Complete Solution:**

(a) $a_{10}=3+9\\cdot4=39$.

(b) $S_{10}=\\frac{10}{2}(3+39)=210$."""
        he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

(א) מצאו את קודקוד $f(x)=x^2-6x+8$ ושרטטו.

(ב) מצאו חיתוכי $x$ וציר סימטריה.

**פתרון מלא:**

(א) $f(x)=(x-3)^2-1$ → קודקוד $(3,-1)$.

(ב) $x=2,4$, ציר $x=3$.

---

**שאלת תרגול 2:**

סדרה חשבונית: $a_1=3$, $a_{n+1}=a_n+4$.

(א) $a_{10}=39$. (ב) $\\sum_{k=1}^{10} a_k = 210$."""
        return en, he

    # ── 4pt math ──
    if cat == "4pt":
        if "geometry" in s or "vector" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Triangle $ABC$ has $A(1,0)$, $B(7,4)$. Point $C$ is on the $x$-axis. $CE$ is a median with $BC/EB=2$. Find $C$, then the area of $\\triangle ABC$.

**Complete Solution:**

Midpoint of $AB$: $M(4,2)$. Median from $C$ meets $AB$ at $E$ with $BE:EA=1:2$ → $E(3,\\frac{4}{3})$.
Line $CE$ through $E$ with $C$ on $x$-axis: solve to get $C(5,0)$.
Area $= \\frac{1}{2}|(7-1)(0-4)-(5-1)(4-0)| = 12$.

---

**Practice Problem 2:**

Find the distance from $P(2,-1)$ to the line $3x+4y-5=0$.

**Complete Solution:**

$d = \\frac{|3(2)+4(-1)-5|}{\\sqrt{9+16} = \\frac{1}{5}$."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

$ABC$: $A(1,0)$, $B(7,4)$, $C$ על ציר $x$. $CE$ חוצה — מצאו $C$ ושטח המשולש.

**פתרון:** $C(5,0)$, שטח $=12$.

---

**שאלת תרגול 2:**

מרחק מ-$P(2,-1)$ לישר $3x+4y-5=0$.

**פתרון:** $d=\\frac{1}{5}$."""
            return en, he
        if "integral" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Given $f(x)=x^3-6x^2+9x$, find the area between $f$ and the $x$-axis from $x=0$ to $x=3$.

**Complete Solution:**

$f(x)=x(x-3)^2$. On $[0,3]$, $f\\ge0$.
$\\int_0^3 (x^3-6x^2+9x)\\,dx = \\left[\\frac{x^4}{4}-2x^3+\\frac{9x^2}{2}\\right]_0^3 = \\frac{81}{4}-54+\\frac{81}{2} = \\frac{27}{4}$.

---

**Practice Problem 2:**

Evaluate $\\int_1^2 \\frac{2x+1}{x^2+x}\\,dx$.

**Complete Solution:**

Let $u=x^2+x$, $du=(2x+1)dx$ → $\\int \\frac{du}{u} = \\ln|u| = \\ln(x^2+x)|_1^2 = \\ln 6 - \\ln 2 = \\ln 3$."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

$f(x)=x^3-6x^2+9x$. שטח בין $f$ לציר $x$ ב-$[0,3]$.

**פתרון:** $\\frac{27}{4}$.

---

**שאלת תרגול 2:**

$\\int_1^2 \\frac{2x+1}{x^2+x}\\,dx = \\ln 3$."""
            return en, he
        en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Given $f(x)=x^3-6x^2+9x$:

(a) Find domain, zeros, and local extrema.

(b) Sketch the graph.

(c) Find the area between $f$ and the $x$-axis from $x=0$ to $x=3$.

**Complete Solution:**

(a) Domain $\\mathbb{R}$. $f(x)=x(x-3)^2$ → zeros $0,3$ (double). $f'=3(x-1)(x-3)$ → max at $(1,4)$, min at $(3,0)$.

(b) Crosses origin, peaks at $(1,4)$, touches $x$-axis at 3.

(c) $\\int_0^3 f(x)\\,dx = \\frac{27}{4}$.

---

**Practice Problem 2:**

$P(\\text{drawing 2 apples without replacement})=\\frac{1}{36}$ from a bag with 2 apples and $n$ peaches. Find $n$, then $P(\\text{same type}\\mid\\text{2 drawn})$.

**Complete Solution:**

$\\frac{2}{n+2}\\cdot\\frac{1}{n+1}=\\frac{1}{36}$ → $(n+2)(n+1)=72$ → $n=7$.
$P(\\text{same})=P(AA)+P(PP)=\\frac{1}{36}+\\frac{7\\cdot6}{9\\cdot8}=\\frac{43}{144}$."""
        he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

$f(x)=x^3-6x^2+9x$: (א) תחום, אפסים, קיצון. (ב) סקיצה. (ג) שטח ב-$[0,3]$.

**פתרון:** מקס $(1,4)$, מין $(3,0)$, שטח $\\frac{27}{4}$.

---

**שאלת תרגול 2:**

$P(2\\ \\text{תפוחים})=\\frac{1}{36}$, 2 תפוחים ו-$n$ אפרסקים. מצאו $n$ ו-$P(\\text{אותו סוג})$.

**פתרון:** $n=7$, $P=\\frac{43}{144}$."""
        return en, he

    # ── 5pt math ──
    if cat == "5pt":
        if "induction" in s or "sequence" in s or "combinator" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Prove by induction: $\\sum_{k=1}^n k^2 = \\frac{n(n+1)(2n+1)}{6}$.

**Complete Solution:**

Base $n=1$: LHS $=1$, RHS $=1$ ✓.
Assume true for $n$. For $n+1$:
$\\sum_{k=1}^{n+1} k^2 = \\frac{n(n+1)(2n+1)}{6} + (n+1)^2 = \\frac{(n+1)(2n^2+7n+6)}{6} = \\frac{(n+1)(n+2)(2n+3)}{6}$ ✓

---

**Practice Problem 2:**

Given $a_{n+1}=\\sqrt{a_n+2}$, $a_1=2$. Prove bounded and monotone, find the limit.

**Complete Solution:**

$0<a_n<2$ by induction. $a_{n+1}>a_n$ since $\\sqrt{a_n+2}>\\sqrt{a_n}$ when $a_n>0$.
Limit $L$ satisfies $L=\\sqrt{L+2}$ → $L=2$."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

הוכיחו באינדוקציה: $\\sum k^2 = \\frac{n(n+1)(2n+1)}{6}$.

**פתרון:** בסיס + צעד אינדוקציה (ראו למעלה).

---

**שאלת תרגול 2:**

$a_{n+1}=\\sqrt{a_n+2}$, $a_1=2$. הוכיחו חסומה ומונוטונית, מצאו גבול.

**פתרון:** $0<a_n<2$, עולה, $L=2$."""
            return en, he
        if "complex" in s or "trig" in s or "implicit" in s or "derivative" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Find all $x\\in[0,2\\pi]$ where $2\\sin^2 x - \\sin x - 1 = 0$.

**Complete Solution:**

Let $u=\\sin x$: $2u^2-u-1=0$ → $(2u+1)(u-1)=0$ → $u=1$ or $u=-\\frac{1}{2}$.
$\\sin x=1$ → $x=\\frac{\\pi}{2}$. $\\sin x=-\\frac{1}{2}$ → $x=\\frac{7\\pi}{6},\\frac{11\\pi}{6}$.

---

**Practice Problem 2:**

Find $\\frac{dy}{dx}$ if $x^2+y^2=25$ at $(3,4)$.

**Complete Solution:**

$2x+2y\\frac{dy}{dx}=0$ → $\\frac{dy}{dx}=-\\frac{x}{y}=-\\frac{3}{4}$."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

כל $x\\in[0,2\\pi]$: $2\\sin^2 x-\\sin x-1=0$.

**פתרון:** $x=\\frac{\\pi}{2},\\frac{7\\pi}{6},\\frac{11\\pi}{6}$.

---

**שאלת תרגול 2:**

$x^2+y^2=25$ ב-$(3,4)$: $\\frac{dy}{dx}=-\\frac{3}{4}$."""
            return en, he
        en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Prove by induction: $\\sum_{k=1}^n k^2 = \\frac{n(n+1)(2n+1)}{6}$.

**Complete Solution:**

Base and inductive step as in standard 5pt induction template (see above).

---

**Practice Problem 2:**

Find all $x\\in[0,2\\pi]$ where $2\\sin^2 x - \\sin x - 1 = 0$.

**Complete Solution:**

$x=\\frac{\\pi}{2},\\frac{7\\pi}{6},\\frac{11\\pi}{6}$."""
        he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:** הוכחה באינדוקציה ל-$\\sum k^2$.

**שאלת תרגול 2:** $2\\sin^2 x-\\sin x-1=0$ → $x=\\frac{\\pi}{2},\\frac{7\\pi}{6},\\frac{11\\pi}{6}$."""
        return en, he

    # ── physics ──
    if cat == "physics":
        if "circuit" in s or "kirchhoff" in s or "electric" in s or "electro" in s or "magnet" in s or "ac_" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

A 12 V battery connects $R_1=4\\,\\Omega$ in series with parallel $R_2=6\\,\\Omega$ and $R_3=3\\,\\Omega$. Find current through each resistor.

**Complete Solution:**

$R_{23}=\\frac{6\\cdot3}{6+3}=2\\,\\Omega$. Total $R=6\\,\\Omega$. $I=2$ A through $R_1$.
$V_{23}=8$ V → $I_2=\\frac{4}{3}$ A, $I_3=\\frac{8}{3}$ A.

---

**Practice Problem 2:**

Two resistors $3\\,\\Omega$ and $6\\,\\Omega$ in parallel on 9 V. Find power in each.

**Complete Solution:**

$I_1=3$ A, $P_1=27$ W; $I_2=1.5$ A, $P_2=13.5$ W."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

12V, $R_1=4\\Omega$ בטור עם $R_2=6\\Omega$ ו-$R_3=3\\Omega$ במקביל. זרמים?

**פתרון:** $I_1=2$ A, $I_2=\\frac{4}{3}$ A, $I_3=\\frac{8}{3}$ A.

---

**שאלת תרגול 2:**

$3\\Omega$ ו-$6\\Omega$ במקביל על 9V — הספקים?

**פתרון:** 27W ו-13.5W."""
            return en, he
        if "projectile" in s or "kinematic" in s or "motion" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

A ball is launched horizontally at 15 m/s from height 20 m ($g=10$ m/s²).

(a) Time to hit ground. (b) Horizontal distance. (c) Impact speed (magnitude and direction).

**Complete Solution:**

(a) $20=\\frac{1}{2}(10)t^2$ → $t=2$ s.

(b) $x=15\\cdot2=30$ m.

(c) $v_x=15$, $v_y=-20$ → $|\\vec{v}|=25$ m/s, angle $\\arctan(20/15)$ below horizontal.

---

**Practice Problem 2:**

Projectile at $30°$, $v_0=40$ m/s. Find range and max height ($g=10$).

**Complete Solution:**

$R=\\frac{v_0^2\\sin60°}{g}\\approx138$ m. $H=\\frac{(v_0\\sin30°)^2}{2g}=20$ m."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

כדור 15 מ\"ש אופקית מגובה 20 מ'. (א) זמן (ב) מרחק (ג) מהירות פגיעה.

**פתרון:** $t=2$ ש', $x=30$ מ', $|\\vec{v}|=25$ מ\"ש.

---

**שאלת תרגול 2:**

$v_0=40$ מ\"ש, $30°$: $R\\approx138$ מ', $H=20$ מ'."""
            return en, he
        if "newton" in s or "friction" in s or "force" in s or "momentum" in s or "collision" in s:
            en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Mass $m$ on incline angle $\\theta$ with friction $\\mu$. Find acceleration and friction force.

**Complete Solution:**

Along incline: $ma = mg\\sin\\theta - \\mu mg\\cos\\theta$ → $a = g(\\sin\\theta - \\mu\\cos\\theta)$.
Friction $f = \\mu mg\\cos\\theta$.

---

**Practice Problem 2:**

Two blocks $m_1=4$ kg, $m_2=2$ kg connected on frictionless table, $F=18$ N on $m_1$. Find $a$ and tension.

**Complete Solution:**

$a = F/(m_1+m_2) = 3$ m/s². $T = m_2 a = 6$ N."""
            he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

מסה על משופע $\\theta$ עם חיכוך $\\mu$ — תאוצה וכוח חיכוך.

**פתרון:** $a=g(\\sin\\theta-\\mu\\cos\\theta)$, $f=\\mu mg\\cos\\theta$.

---

**שאלת תרגול 2:**

$m_1=4$ kg, $m_2=2$ kg, $F=18$ N — $a=3$ מ/ש², $T=6$ N."""
            return en, he
        en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

A ball is launched horizontally at 15 m/s from height 20 m ($g=10$).

(a) Time to ground. (b) Horizontal distance. (c) Impact velocity.

**Complete Solution:**

(a) $t=2$ s. (b) 30 m. (c) $|\\vec{v}|=25$ m/s.

---

**Practice Problem 2:**

Mass on incline: find $a = g\\sin\\theta$ (no friction) and explain with free-body diagram.

**Complete Solution:**

FBD: $mg\\sin\\theta = ma$ → $a=g\\sin\\theta$. Weight component along slope causes acceleration."""
        he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:** זריקה אופקית 15 מ\"ש מ-20 מ' — זמן, מרחק, מהירות.

**פתרון:** $t=2$ ש', 30 מ', 25 מ\"ש.

---

**שאלת תרגול 2:** משופע ללא חיכוך: $a=g\\sin\\theta$ עם FBD."""
        return en, he

    # ── makhina ──
    en = EXAM_INTRO_EN + """

---

**Practice Problem 1:**

Prove or disprove: $\\sqrt{a+b}\\leq\\sqrt{a}+\\sqrt{b}$ for $a,b\\geq0$.

**Complete Solution:**

Square both sides (non-negative): $a+b\\leq a+b+2\\sqrt{ab}$ → $0\\leq2\\sqrt{ab}$ ✓ **True**.

Counterexample for negative? Not in domain. Inequality holds for $a,b\\geq0$.

---

**Practice Problem 2:**

Find $\\lim_{x\\to2}\\frac{x^2-4}{x-2}$ from first principles (factor, no L'Hôpital).

**Complete Solution:**

$\\frac{x^2-4}{x-2}=\\frac{(x-2)(x+2)}{x-2}=x+2$ for $x\\neq2$. Limit $=4$.

---

**Practice Problem 3 (physics):**

Projectile at $30°$, speed $v_0$. Express max height and range in terms of $v_0$ and $g$.

**Complete Solution:**

$H=\\frac{v_0^2\\sin^2\\theta}{2g}=\\frac{v_0^2}{8g}$. $R=\\frac{v_0^2\\sin2\\theta}{g}=\\frac{v_0^2\\sqrt3}{2g}$."""
    he = EXAM_INTRO_HE + """

---

**שאלת תרגול 1:**

הוכיחו או הפריכו: $\\sqrt{a+b}\\leq\\sqrt{a}+\\sqrt{b}$ ל-$a,b\\geq0$.

**פתרון:** נכון — $0\\leq2\\sqrt{ab}$.

---

**שאלת תרגול 2:**

$\\lim_{x\\to2}\\frac{x^2-4}{x-2}$ מעקרונות ראשונים.

**פתרון:** $x+2\\to4$.

---

**שאלת תרגול 3:**

זריקה ב-$30°$, מהירות $v_0$: גובה מקסימלי וטווח.

**פתרון:** $H=\\frac{v_0^2}{8g}$, $R=\\frac{v_0^2\\sqrt3}{2g}$."""
    return en, he


def open_questions_interactive(cat: str, stem: str, q_ids: tuple[str, str]) -> list[dict]:
    """Build two open questions for interactive format."""
    s = stem.lower()
    q4_id, q5_id = q_ids

    if cat == "3pt":
        return [
            {
                "id": q4_id,
                "type": "open",
                "body_en": "A bag contains 5 red and 3 blue balls. Two balls are drawn without replacement.\n\n(a) Find the probability both are the same color.\n(b) Given the first ball was red, find P(second is red).",
                "body_he": "שק עם 5 כדורים אדומים ו-3 כחולים. שולפים 2 ללא החזרה.\n\n(א) הסתברות ששניהם באותו צבע.\n(ב) ידוע שהראשון אדום — P(שני אדום).",
                "points": 10,
                "expected_steps_en": [
                    "Compute P(both red) = (5/8)(4/7) and P(both blue) = (3/8)(2/7)",
                    "Add for same color: 13/28",
                    "Conditional: P(R2|R1) = 4/7",
                ],
                "expected_steps_he": [
                    "חשב P(RR) ו-P(BB)",
                    "סכום: 13/28",
                    "מותנית: 4/7",
                ],
                "sample_solution_en": "(a) P(same) = 20/56 + 6/56 = 13/28. (b) P(R2|R1) = 4/7.",
                "sample_solution_he": "(א) 13/28. (ב) 4/7.",
                "rubric_en": "4pts correct same-color probability with work; 3pts conditional probability; 3pts clear notation.",
                "rubric_he": "4 נק' הסתברות אותו צבע; 3 נק' מותנית; 3 נק' סימון ברור.",
            },
            {
                "id": q5_id,
                "type": "open",
                "body_en": "For $f(x)=x^2-6x+8$:\n\n(a) Find the vertex by completing the square.\n(b) Find x-intercepts.\n(c) Sketch the parabola showing vertex and intercepts.",
                "body_he": "עבור $f(x)=x^2-6x+8$:\n\n(א) קודקוד בשלמות ריבוע.\n(ב) חיתוכי x.\n(ג) סקיצה.",
                "points": 10,
                "expected_steps_en": [
                    "Complete square: (x-3)²-1, vertex (3,-1)",
                    "Set f(x)=0 → x=2,4",
                    "Sketch upward parabola with labeled points",
                ],
                "expected_steps_he": [
                    "שלמות ריבוע: (x-3)²-1",
                    "אפסים: x=2,4",
                    "סקיצה עם קודקוד וחיתוכים",
                ],
                "sample_solution_en": "Vertex (3,-1), zeros x=2,4, opens up.",
                "sample_solution_he": "קודקוד (3,-1), אפסים 2,4, פותח למעלה.",
                "rubric_en": "3pts vertex; 3pts intercepts; 4pts sketch with labels.",
                "rubric_he": "3 נק' קודקוד; 3 נק' חיתוכים; 4 נק' סקיצה.",
            },
        ]

    if cat == "4pt":
        return [
            {
                "id": q4_id,
                "type": "open",
                "body_en": "Investigate $f(x)=x^3-6x^2+9x$:\n\n(a) Domain and zeros.\n(b) Monotonicity and local extrema.\n(c) Area between $f$ and the x-axis on $[0,3]$.",
                "body_he": "חקור $f(x)=x^3-6x^2+9x$:\n\n(א) תחום ואפסים.\n(ב) מונוטוניות וקיצון.\n(ג) שטח ב-$[0,3]$.",
                "points": 10,
                "expected_steps_en": [
                    "Factor: x(x-3)², zeros 0 and 3",
                    "f'=3(x-1)(x-3), max at (1,4), min at (3,0)",
                    "∫₀³ f(x)dx = 27/4",
                ],
                "expected_steps_he": [
                    "אפסים 0,3",
                    "קיצון: מקס (1,4), מין (3,0)",
                    "שטח 27/4",
                ],
                "sample_solution_en": "Zeros 0,3; max (1,4); area 27/4.",
                "sample_solution_he": "אפסים 0,3; מקס (1,4); שטח 27/4.",
                "rubric_en": "3pts domain/zeros; 4pts derivative analysis; 3pts integral.",
                "rubric_he": "3 נק' תחום/אפסים; 4 נק' נגזרת; 3 נק' אינטגרל.",
            },
            {
                "id": q5_id,
                "type": "open",
                "body_en": "Bag: 2 apples and $n$ peaches. P(two apples without replacement) = 1/36.\n\n(a) Find $n$.\n(b) Find P(both same type | two drawn).",
                "body_he": "2 תפוחים ו-$n$ אפרסקים. P(2 תפוחים)=1/36.\n\n(א) מצא $n$.\n(ב) P(אותו סוג | 2 נשלפו).",
                "points": 10,
                "expected_steps_en": [
                    "Set (2/(n+2))(1/(n+1)) = 1/36",
                    "Solve (n+2)(n+1)=72 → n=7",
                    "P(same)=1/36 + P(two peaches)",
                ],
                "expected_steps_he": [
                    "הצבה: (n+2)(n+1)=72",
                    "n=7",
                    "P(אותו סוג)=43/144",
                ],
                "sample_solution_en": "n=7. P(same type)=43/144.",
                "sample_solution_he": "n=7. P=43/144.",
                "rubric_en": "5pts find n with algebra; 5pts conditional/total probability.",
                "rubric_he": "5 נק' מציאת n; 5 נק' הסתברות.",
            },
        ]

    if cat == "5pt":
        return [
            {
                "id": q4_id,
                "type": "open",
                "body_en": "Prove by mathematical induction:\n$$\\sum_{k=1}^{n} k^2 = \\frac{n(n+1)(2n+1)}{6}$$",
                "body_he": "הוכיחו באינדוקציה:\n$$\\sum_{k=1}^{n} k^2 = \\frac{n(n+1)(2n+1)}{6}$$",
                "points": 10,
                "expected_steps_en": [
                    "Verify base case n=1",
                    "State induction hypothesis",
                    "Add (n+1)² and algebra to get (n+1)(n+2)(2n+3)/6",
                ],
                "expected_steps_he": [
                    "בסיס n=1",
                    "הנחת אינדוקציה",
                    "צעד אלגברי ל-n+1",
                ],
                "sample_solution_en": "Standard induction: base OK; inductive step factors to required form.",
                "sample_solution_he": "אינדוקציה סטנדרטית — בסיס וצעד.",
                "rubric_en": "2pts base; 3pts hypothesis; 5pts inductive algebra.",
                "rubric_he": "2 נק' בסיס; 3 נק' הנחה; 5 נק' צעד.",
            },
            {
                "id": q5_id,
                "type": "open",
                "body_en": "Find all $x\\in[0,2\\pi]$ satisfying $2\\sin^2 x - \\sin x - 1 = 0$. Show all work.",
                "body_he": "מצאו כל $x\\in[0,2\\pi]$: $2\\sin^2 x - \\sin x - 1 = 0$. הראו שלבים.",
                "points": 10,
                "expected_steps_en": [
                    "Substitute u=sin x, solve quadratic",
                    "sin x=1 → π/2",
                    "sin x=-1/2 → 7π/6, 11π/6",
                ],
                "expected_steps_he": [
                    "u=sin x, משוואה ריבועית",
                    "sin x=1 → π/2",
                    "sin x=-1/2 → 7π/6, 11π/6",
                ],
                "sample_solution_en": "x = π/2, 7π/6, 11π/6.",
                "sample_solution_he": "x = π/2, 7π/6, 11π/6.",
                "rubric_en": "3pts substitution; 4pts solving trig; 3pts all solutions in interval.",
                "rubric_he": "3 נק' הצבה; 4 נק' טrig; 3 נק' כל הפתרונות.",
            },
        ]

    if cat == "physics":
        return [
            {
                "id": q4_id,
                "type": "open",
                "body_en": "A ball is launched horizontally at 15 m/s from a height of 20 m ($g=10$ m/s²).\n\n(a) Time until it hits the ground.\n(b) Horizontal distance traveled.\n(c) Speed at impact (magnitude and direction).",
                "body_he": "כדור נזרק אופקית ב-15 מ\"ש מגובה 20 מ' ($g=10$).\n\n(א) זמן עד פגיעה.\n(ב) מרחק אופקי.\n(ג) מהירות בפגיעה.",
                "points": 10,
                "expected_steps_en": [
                    "Vertical: 20 = 5t² → t=2 s",
                    "Horizontal: x = 15·2 = 30 m",
                    "v_x=15, v_y=-20, |v|=25 m/s",
                ],
                "expected_steps_he": [
                    "t=2 ש'",
                    "x=30 מ'",
                    "|v|=25 מ\"ש",
                ],
                "sample_solution_en": "(a) 2 s (b) 30 m (c) 25 m/s at arctan(4/3) below horizontal.",
                "sample_solution_he": "(א) 2 ש' (ב) 30 מ' (ג) 25 מ\"ש.",
                "rubric_en": "3pts time; 3pts distance; 4pts velocity components and magnitude.",
                "rubric_he": "3 נק' זמן; 3 נק' מרחק; 4 נק' מהירות.",
            },
            {
                "id": q5_id,
                "type": "open",
                "body_en": "A mass $m$ on an incline at angle $\\theta$ with coefficient of friction $\\mu$.\n\n(a) Draw a free-body diagram.\n(b) Find acceleration down the slope.\n(c) Find the friction force.",
                "body_he": "מסה $m$ על משופע $\\theta$ עם $\\mu$.\n\n(א) FBD.\n(ב) תאוצה.\n(ג) חיכוך.",
                "points": 10,
                "expected_steps_en": [
                    "FBD: mg, N, f along/perpendicular to slope",
                    "ΣF_parallel: mg sinθ - μmg cosθ = ma",
                    "a = g(sinθ - μ cosθ), f = μmg cosθ",
                ],
                "expected_steps_he": [
                    "FBD עם כוחות",
                    "חוק שני לאורך המדרון",
                    "a ו-f",
                ],
                "sample_solution_en": "a = g(sinθ - μcosθ), f = μmg cosθ.",
                "sample_solution_he": "a = g(sinθ - μcosθ), f = μmg cosθ.",
                "rubric_en": "3pts FBD; 4pts Newton's 2nd; 3pts friction formula.",
                "rubric_he": "3 נק' FBD; 4 נק' F=ma; 3 נק' חיכוך.",
            },
        ]

    # makhina default
    return [
        {
            "id": q4_id,
            "type": "open",
            "body_en": "Prove or disprove: $\\sqrt{a+b}\\leq\\sqrt{a}+\\sqrt{b}$ for all $a,b\\geq 0$. Justify every step.",
            "body_he": "הוכיחו או הפריכו: $\\sqrt{a+b}\\leq\\sqrt{a}+\\sqrt{b}$ ל-$a,b\\geq 0$.",
            "points": 10,
            "expected_steps_en": [
                "Note both sides non-negative for a,b≥0",
                "Square inequality → 0 ≤ 2√(ab)",
                "Conclude inequality holds",
            ],
            "expected_steps_he": [
                "שני האגפים אינשליים",
                "בריבוע: 0 ≤ 2√(ab)",
                "האי-שוויון נכון",
            ],
            "sample_solution_en": "True. Squaring gives 0 ≤ 2√(ab), always valid for a,b≥0.",
            "sample_solution_he": "נכון — 0 ≤ 2√(ab).",
            "rubric_en": "4pts domain; 4pts algebraic proof; 2pts conclusion.",
            "rubric_he": "4 נק' תחום; 4 נק' הוכחה; 2 נק' מסקנה.",
        },
        {
            "id": q5_id,
            "type": "open",
            "body_en": "Find $\\lim_{x\\to 2}\\frac{x^2-4}{x-2}$ using factorization (first principles, not L'Hôpital).",
            "body_he": "מצאו $\\lim_{x\\to 2}\\frac{x^2-4}{x-2}$ בפירוק (ללא L'Hôpital).",
            "points": 10,
            "expected_steps_en": [
                "Factor numerator (x-2)(x+2)",
                "Cancel (x-2) for x≠2",
                "Substitute x=2 → limit 4",
            ],
            "expected_steps_he": [
                "פירוק (x-2)(x+2)",
                "צמצום",
                "x→2 נותן 4",
            ],
            "sample_solution_en": "Limit = 4.",
            "sample_solution_he": "הגבול = 4.",
            "rubric_en": "4pts factorization; 3pts cancellation justification; 3pts limit value.",
            "rubric_he": "4 נק' פירוק; 3 נק' צמצום; 3 נק' ערך.",
        },
    ]


def open_questions_standard(cat: str, stem: str, base_q: dict, ord_a: int, ord_b: int) -> list[dict]:
    """Build two open questions for standard seed-lessons format."""
    interactive = open_questions_interactive(cat, stem, ("q4", "q5"))
    out = []
    for i, iq in enumerate(interactive):
        ord_n = ord_a if i == 0 else ord_b
        skill = base_q.get("skill_atoms", ["exam_practice"])
        out.append(
            {
                "ord": ord_n,
                "kind": "open",
                "difficulty": "hard",
                "stem_en": iq["body_en"],
                "stem_he": iq["body_he"],
                "rubric_en": iq["rubric_en"],
                "rubric_he": iq["rubric_he"],
                "explanation_en": iq["sample_solution_en"],
                "explanation_he": iq["sample_solution_he"],
                "skill_atoms": skill if isinstance(skill, list) else ["exam_practice"],
                "points_level_min": base_q.get("points_level_min") or cat.replace("pt", "pt"),
            }
        )
        if cat == "physics":
            out[-1]["points_level_min"] = "hs_physics"
        elif cat.endswith("pt"):
            out[-1]["points_level_min"] = f"hs_math_{cat}"
    return out


def is_interactive(data: dict) -> bool:
    if data.get("type") == "interactive":
        return True
    qs = data.get("questions") or []
    return bool(qs and qs[0].get("type") in ("mcq", "open"))


def add_exam_section(data: dict, cat: str, stem: str) -> None:
    body_en, body_he = exam_body(cat, stem)
    sections = data.setdefault("sections", [])

    if any(s.get("id") == "exam_practice" for s in sections):
        return
    if any(
        "Exam-Style" in s.get("title_en", "") or "תרגול בסגנון בחינה" in s.get("title_he", "")
        for s in sections
    ):
        return

    if is_interactive(data):
        level = data.get("level_min", cat)
        sections.append(
            {
                "id": "exam_practice",
                "title_en": "Exam-Style Practice Problems",
                "title_he": "תרגול בסגנון בחינה",
                "level_min": level,
                "body_en_md": body_en,
                "body_he_md": body_he,
            }
        )
    else:
        sections.append(
            {
                "kind": "practice_tip",
                "title_en": "Exam-Style Practice Problems",
                "title_he": "תרגול בסגנון בחינה",
                "body_en_md": body_en,
                "body_he_md": body_he,
            }
        )


def convert_last_two(data: dict, cat: str, stem: str) -> None:
    qs = data.get("questions") or []
    if len(qs) < 2:
        return

    if is_interactive(data):
        q4_id = qs[-2].get("id", "q4")
        q5_id = qs[-1].get("id", "q5")
        new_qs = open_questions_interactive(cat, stem, (q4_id, q5_id))
        qs[-2:] = new_qs
        return

    # Standard format — only replace if last two are mcq
    if qs[-1].get("kind") != "mcq" and qs[-2].get("kind") != "mcq":
        # If only one is mcq, replace mcq ones among last two
        indices = [len(qs) - 2, len(qs) - 1]
        mcq_indices = [i for i in indices if qs[i].get("kind") == "mcq"]
        if not mcq_indices:
            return
    else:
        mcq_indices = [len(qs) - 2, len(qs) - 1]

    base = qs[-1]
    ords = [qs[i].get("ord", i + 1) for i in mcq_indices]
    while len(ords) < 2:
        ords.append(ords[-1] + 1 if ords else 1)
    replacements = open_questions_standard(cat, stem, base, ords[0], ords[1])
    for idx, rep in zip(mcq_indices[:2], replacements[: len(mcq_indices)]):
        qs[idx] = rep


def upgrade_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    cats = categorize(path.name, data)
    if not cats:
        return False

    cat = primary_cat(cats)
    stem = path.stem
    add_exam_section(data, cat, stem)
    convert_last_two(data, cat, stem)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> None:
    upgraded = []
    for path in sorted(LESSONS.glob("*.json")):
        try:
            if upgrade_file(path):
                upgraded.append(path.name)
        except Exception as e:
            print(f"ERROR {path.name}: {e}")
            raise
    print(f"Upgraded {len(upgraded)} files")
    for name in upgraded:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
