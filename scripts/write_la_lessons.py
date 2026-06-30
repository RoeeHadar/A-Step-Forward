#!/usr/bin/env python3
"""Author 4 Linear Algebra university lessons and update lessons-index."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS_DIR = os.path.join(ROOT, "scripts", "seed_data", "lessons")
INDEX_PATH = os.path.join(ROOT, "apps", "web", "src", "lib", "lessons-index.generated.json")


def mcq(ord_, diff, stem_en, stem_he, opts_en, opts_he, correct, expl_en, expl_he, atoms):
    return {
        "ord": ord_,
        "kind": "mcq",
        "difficulty": diff,
        "stem_en": stem_en,
        "stem_he": stem_he,
        "options_en": opts_en,
        "options_he": opts_he,
        "correct_index": correct,
        "explanation_en": expl_en,
        "explanation_he": expl_he,
        "skill_atoms": atoms,
    }


def section(kind, title_en, title_he, body_en, body_he):
    return {
        "kind": kind,
        "title_en": title_en,
        "title_he": title_he,
        "body_en_md": body_en,
        "body_he_md": body_he,
    }


def agent_hints(insights, misconceptions, pacing, diagnostics, atoms):
    return {
        "key_insights": insights,
        "common_misconceptions": misconceptions,
        "tutor_pacing_hint": pacing,
        "diagnostic_signals": diagnostics,
        "skill_atoms_unlocked": atoms,
    }


LESSONS = [
    {
        "concept_id": "systems_linear_equations",
        "subject": "linear_algebra",
        "level": "university",
        "math_track": ["la"],
        "title_en": "Systems of Linear Equations & Gaussian Elimination",
        "title_he": "מערכות משוואות לינאריות ואלימינציה גאוסית",
        "summary_en": "Solve $m \\times n$ linear systems via augmented matrices, elementary row operations, REF/RREF, and the Rouché–Capelli rank criteria — the Technion/TAU entry point to linear algebra.",
        "summary_he": "פתרון מערכות $m \\times n$ באמצעות מטריצה מורחבת, פעולות שורה, REF/RREF וקריטריוני דרגה (רושה-קפלי) — נקודת הכניסה לאלגברה לינארית בטכניון/TAU.",
        "est_minutes": 40,
        "sections": [
            section(
                "theory",
                "Systems and augmented matrices",
                "מערכות ומטריצות מורחבות",
                """A **system of linear equations** in $n$ unknowns $x_1,\\ldots,x_n$ has the form:
$$a_{11}x_1 + \\cdots + a_{1n}x_n = b_1, \\quad \\ldots, \\quad a_{m1}x_1 + \\cdots + a_{mn}x_n = b_m.$$

In **matrix notation**: $A\\vec{x} = \\vec{b}$, where $A$ is $m \\times n$, $\\vec{x} \\in \\mathbb{R}^n$, $\\vec{b} \\in \\mathbb{R}^m$.

The **augmented matrix** $[A|\\vec{b}]$ stores coefficients and constants side by side — row operations on it solve the system without rewriting variables each time.

**Three solution types:**
1. **Unique** — exactly one $\\vec{x}$.
2. **Infinitely many** — an affine subspace of dimension $\\geq 1$.
3. **None** — inconsistent (contradiction).

**Geometry (2D/3D):** each equation is a line/plane/hyperplane. A unique solution = transversal intersection; none = parallel objects; infinitely many = overlap along a subspace (e.g. two coincident planes in $\\mathbb{R}^3$).""",
                """**מערכת משוואות לינאריות** ב-$n$ נעלמים $x_1,\\ldots,x_n$:
$$a_{11}x_1 + \\cdots + a_{1n}x_n = b_1, \\quad \\ldots, \\quad a_{m1}x_1 + \\cdots + a_{mn}x_n = b_m.$$

**סימון מטריצי:** $A\\vec{x} = \\vec{b}$, כאשר $A$ בגודל $m \\times n$.

**המטריצה המורחבת** $[A|\\vec{b}]$ מאחסנת מקדמים ואגפים יחד — פעולות שורה עליה פותרות את המערכת.

**שלושה סוגי פתרונות:**
1. **יחיד** — $\\vec{x}$ אחד בדיוק.
2. **אינסוף רבים** — תת-מרחב אפיני.
3. **אין** — מערכת סותרת.

**גיאומטריה:** כל משוואה = ישר/מישור. חיתוך יחיד / אין חיתוך / חפיפה לאורך תת-מרחב.""",
            ),
            section(
                "theory",
                "Elementary row operations",
                "פעולות שורה אלמנטריות",
                """Three **elementary row operations (EROs)** — each preserves the solution set:

1. **Swap:** $R_i \\leftrightarrow R_j$.
2. **Scale:** $R_i \\leftarrow cR_i$ with $c \\neq 0$.
3. **Add multiple:** $R_i \\leftarrow R_i + cR_j$.

**Goal:** reach **Row Echelon Form (REF)** — pivots move right as you go down; zeros below each pivot. **Reduced REF (RREF)** additionally has zeros above pivots and pivot entries equal to 1.

Every ERO is reversible, so solutions of $[A|\\vec{b}]$ and its REF/RREF are identical.

**Exam tip:** scaling a row by $-1$ or swapping rows does not change consistency — but forgetting to apply the same operation to $\\vec{b}$ in the augmented matrix *does* change the system.""",
                """שלוש **פעולות שורה אלמנטריות** — כל אחת שומרת על קבוצת הפתרונות:

1. **החלפה:** $R_i \\leftrightarrow R_j$.
2. **כפל:** $R_i \\leftarrow cR_i$ ($c \\neq 0$).
3. **חיבור כפולה:** $R_i \\leftarrow R_i + cR_j$.

**מטרה:** **צורת מדרגות (REF)** — אפסים מתחת לכל pivot; pivots זזים ימינה. **RREF** — גם אפסים מעל pivots וערכי pivot = 1.

**טיפ למבחן:** החלפת שורות לא משנה עקביות — אבל שכחה לעדכן את $\\vec{b}$ במטריצה המורחבת כן.""",
            ),
            section(
                "worked_example",
                "Gaussian elimination — 3×3 example",
                "אלימינציה גאוסית — דוגמה 3×3",
                """Solve:
$$\\begin{cases} x + 2y + z = 9 \\\\ 2x + 5y + 3z = 23 \\\\ x + 4y + 2z = 14 \\end{cases}$$

Augmented matrix and forward elimination:
$$\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 2 & 5 & 3 & 23 \\\\ 1 & 4 & 2 & 14 \\end{array}\\right]
\\xrightarrow{R_2-2R_1,\\; R_3-R_1}
\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 0 & 1 & 1 & 5 \\\\ 0 & 2 & 1 & 5 \\end{array}\\right]
\\xrightarrow{R_3-2R_2}
\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 0 & 1 & 1 & 5 \\\\ 0 & 0 & -1 & -5 \\end{array}\\right]$$

**Back-substitution:** $-z = -5 \\Rightarrow z = 5$; $y + z = 5 \\Rightarrow y = 0$; $x + 2y + z = 9 \\Rightarrow x = 4$.

**Unique solution:** $(x,y,z) = (4, 0, 5)$.

When fewer pivots than unknowns, **free variables** appear — assign parameters (e.g. $x_3 = t$) and express basic variables in terms of $t$.""",
                """פתרו:
$$\\begin{cases} x + 2y + z = 9 \\\\ 2x + 5y + 3z = 23 \\\\ x + 4y + 2z = 14 \\end{cases}$$

$$\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 2 & 5 & 3 & 23 \\\\ 1 & 4 & 2 & 14 \\end{array}\\right]
\\xrightarrow{R_2-2R_1,\\; R_3-R_1}
\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 0 & 1 & 1 & 5 \\\\ 0 & 2 & 1 & 5 \\end{array}\\right]
\\xrightarrow{R_3-2R_2}
\\left[\\begin{array}{ccc|c} 1 & 2 & 1 & 9 \\\\ 0 & 1 & 1 & 5 \\\\ 0 & 0 & -1 & -5 \\end{array}\\right]$$

**הצבה לאחור:** $z = 5$, $y = 0$, $x = 4$. **פתרון יחיד:** $(4,0,5)$.

כשיש פחות pivots מנעלמים — **משתנים חופשיים** (למשל $x_3 = t$).""",
            ),
            section(
                "theory",
                "Solution structure and rank",
                "מבנה הפתרון ודרגה",
                """**Rank** = number of pivot columns in REF of $A$ = $\\text{rank}(A)$.

If $\\text{rank}(A) = r$ and there are $n$ unknowns, the solution set (when consistent) is an **affine subspace** of dimension $n - r$.

For **homogeneous** $A\\vec{x} = \\vec{0}$: always has the trivial $\\vec{0}$; nontrivial solutions iff $r < n$.

**General solution:** $\\vec{x} = \\vec{x}_p + \\vec{x}_h$, where $\\vec{x}_p$ is any particular solution and $\\vec{x}_h \\in \\ker(A)$.

**Technion-style example with parameter $k$:**
$$\\begin{cases} x + y = 2 \\\\ 2x + 2y = k \\end{cases}$$
Row 2 gives $k = 4$ for consistency. If $k = 4$: infinitely many $(x,y) = (2-t, t)$; if $k \\neq 4$: no solution.""",
                """**דרגה** = מספר עמודות pivot ב-REF של $A$.

אם $\\text{rank}(A) = r$ ו-$n$ נעלמים, קבוצת הפתרונות (אם עקבית) היא **תת-מרחב אפיני** במימד $n-r$.

ל**הומогנית** $A\\vec{x} = \\vec{0}$: תמיד $\\vec{0}$; פתרונות לא-טריוויאליים iff $r < n$.

**פתרון כללי:** $\\vec{x} = \\vec{x}_p + \\vec{x}_h$.

**דוגמה עם פרמטר $k$:**
$$\\begin{cases} x + y = 2 \\\\ 2x + 2y = k \\end{cases}$$
עקביות דורשת $k = 4$. אם $k = 4$: $(2-t, t)$; אם $k \\neq 4$: אין פתרון.""",
            ),
            section(
                "theory",
                "Unique / infinite / no solution — Rouché–Capelli",
                "פתרון יחיד / אינסוף / אין — רושה-קפלי",
                """**Inconsistent (no solution):** a row $[0\\,0\\,\\cdots\\,0\\,|\\,c]$ with $c \\neq 0$ — a pivot in the augmented column with no variable.

**Rouché–Capelli theorem (stated):** $A\\vec{x} = \\vec{b}$ is consistent iff $\\text{rank}(A) = \\text{rank}([A|\\vec{b}])$.

| Condition | Outcome |
|---|---|
| $\\text{rank}(A) = \\text{rank}([A|\\vec{b}]) = n$ | **Unique** solution |
| $\\text{rank}(A) = \\text{rank}([A|\\vec{b}]) < n$ | **Infinitely many** |
| $\\text{rank}(A) < \\text{rank}([A|\\vec{b}])$ | **No** solution |

**Exam type:** *For which $k$ does the system have a solution?* — eliminate and read the condition on the last row without fully solving.

**Connection:** $\\dim(\\ker A) = n - \\text{rank}(A)$ (preview of Rank–Nullity).""",
                """**אין פתרון:** שורה $[0\\,0\\,\\cdots\\,0\\,|\\,c]$ עם $c \\neq 0$.

**משפט רושה-קפלי:** $A\\vec{x} = \\vec{b}$ עקבית iff $\\text{rank}(A) = \\text{rank}([A|\\vec{b}])$.

| תנאי | תוצאה |
|---|---|
| $\\text{rank}(A) = \\text{rank}([A|\\vec{b}]) = n$ | **פתרון יחיד** |
| $\\text{rank}(A) = \\text{rank}([A|\\vec{b}]) < n$ | **אינסוף רבים** |
| $\\text{rank}(A) < \\text{rank}([A|\\vec{b}])$ | **אין** פתרון |

**סוג מבחן:** *לערך איזה $k$ יש פתרון?* — אלימינציה וקריאת התנאי בשורה האחרונה.""",
            ),
        ],
        "questions": [
            mcq(
                1, "easy",
                "Which row operation is **not** elementary?",
                "איזו פעולת שורה **אינה** אלמנטרית?",
                ["$R_1 \\leftrightarrow R_2$", "$R_1 \\leftarrow 3R_1$", "$R_2 \\leftarrow R_2 + 2R_1$", "$R_1 \\leftarrow R_1 + R_2$ then $R_2 \\leftarrow R_1 - R_2$"],
                ["$R_1 \\leftrightarrow R_2$", "$R_1 \\leftarrow 3R_1$", "$R_2 \\leftarrow R_2 + 2R_1$", "$R_1 \\leftarrow R_1 + R_2$ ואז $R_2 \\leftarrow R_1 - R_2$"],
                3,
                "The fourth option combines two dependent row replacements that are not a single ERO; the standard three EROs are swap, scale ($c\\neq 0$), and add-multiple.",
                "האפשרות הרביעית אינה אחת משלוש הפעולות הסטנדרטיות (החלפה, כפל ב-$c\\neq 0$, חיבור כפולה).",
                ["perform_row_operations"],
            ),
            mcq(
                2, "medium",
                "After forward elimination, $[A|\\vec{b}]$ has pivots in columns 1 and 3 only (3 unknowns). What is $\\text{rank}(A)$?",
                "לאחר אלימינציה, pivots בעמודות 1 ו-3 בלבד (3 נעלמים). מה $\\text{rank}(A)$?",
                ["$1$", "$2$", "$3$", "Cannot determine"],
                ["$1$", "$2$", "$3$", "לא ניתן לקבוע"],
                1,
                "Rank equals the number of pivot columns = 2.",
                "הדרגה = מספר עמודות pivot = 2.",
                ["find_ref_rank"],
            ),
            mcq(
                3, "medium",
                "A row $[0\\;0\\;0\\;|\\;5]$ appears in RREF of $[A|\\vec{b}]$. The system is:",
                "מופיעה שורה $[0\\;0\\;0\\;|\\;5]$ ב-RREF של $[A|\\vec{b}]$. המערכת:",
                ["Consistent with unique solution", "Consistent with infinitely many solutions", "Inconsistent", "Homogeneous only"],
                ["עקבית עם פתרון יחיד", "עקבית עם אינסוף פתרונות", "סותרת", "הומогנית בלבד"],
                2,
                "A pivot in the augmented column with zeros elsewhere means $0 = 5$ — contradiction.",
                "pivot בעמודה המורחבת עם אפסים = $0 = 5$ — סתירה.",
                ["determine_solution_type"],
            ),
            mcq(
                4, "medium",
                "RREF gives $x_1 + 2x_3 = 4$ and $x_2 - x_3 = 1$ (3 unknowns). General solution?",
                "RREF נותן $x_1 + 2x_3 = 4$ ו-$x_2 - x_3 = 1$ (3 נעלמים). פתרון כללי?",
                ["$(4,1,0)$ only", "$(4-2t,\\,1+t,\\,t)$", "$(4+2t,\\,1-t,\\,t)$", "No solution"],
                ["$(4,1,0)$ בלבד", "$(4-2t,\\,1+t,\\,t)$", "$(4+2t,\\,1-t,\\,t)$", "אין פתרון"],
                1,
                "Free variable $x_3 = t$; then $x_1 = 4 - 2t$, $x_2 = 1 + t$.",
                "$x_3 = t$ חופשי; $x_1 = 4 - 2t$, $x_2 = 1 + t$.",
                ["general_solution_free_variable"],
            ),
            mcq(
                5, "hard",
                "For which $k$ does $\\begin{cases} x + 2y = 1 \\\\ 2x + 4y = k \\end{cases}$ have a solution?",
                "לערך איזה $k$ יש פתרון ל-$\\begin{cases} x + 2y = 1 \\\\ 2x + 4y = k \\end{cases}$?",
                ["All $k$", "$k = 1$ only", "$k = 2$ only", "No $k$"],
                ["כל $k$", "$k = 1$ בלבד", "$k = 2$ בלבד", "אף $k$"],
                2,
                "Row 2 is $2\\times$ row 1; consistency requires $k = 2 \\cdot 1 = 2$.",
                "שורה 2 = פי 2 משורה 1; עקביות דורשת $k = 2$.",
                ["parametric_consistency"],
            ),
        ],
        "agent_hints": agent_hints(
            [
                "$A\\vec{x}=\\vec{b}$; augmented matrix $[A|\\vec{b}]$; EROs preserve solutions.",
                "Rank = pivot count; Rouché–Capelli: consistent iff rank(A) = rank([A|b]).",
                "General solution = particular + homogeneous; free variables when rank < n.",
            ],
            [
                {"wrong": "More equations than unknowns always means no solution", "correction": "Redundant equations can still be consistent; check ranks, not just m vs n.", "detect_phrase_en": "more equations", "detect_phrase_he": "יותר משוואות"},
                {"wrong": "Zero row means no solution", "correction": "[0...0|0] is fine; only [0...0|c] with c≠0 is inconsistent.", "detect_phrase_en": "zero row no solution", "detect_phrase_he": "שורת אפסים אין פתרון"},
            ],
            "Work one 3×3 elimination completely before stating rank theorems.",
            {"confuses REF and RREF": "Show pivot positions are the same; RREF is for reading solutions directly."},
            ["perform_row_operations", "find_ref_rank", "determine_solution_type", "general_solution_free_variable", "parametric_consistency"],
        ),
    },
    # --- Lesson 2: vector_spaces_basis_dimension ---
    {
        "concept_id": "vector_spaces_basis_dimension",
        "subject": "linear_algebra",
        "level": "university",
        "math_track": ["la"],
        "title_en": "Vector Spaces, Basis & Dimension",
        "title_he": "מרחבים וקטוריים, בסיס וממד",
        "summary_en": "Vector space axioms, subspaces, linear independence, span, basis, dimension, Rank–Nullity, and coordinates in a non-standard basis.",
        "summary_he": "אקסיומות מרחב וקטורי, תת-מרחבים, בלתי-תלות לינארית, קבוצת פרישה, בסיס, ממד, משפט דרגה-גרעין וקואורדינטות בבסיס.",
        "est_minutes": 35,
        "sections": [
            section(
                "theory",
                "Vector space axioms",
                "אקסיומות מרחב וקטורי",
                """A **vector space** $V$ over $\\mathbb{R}$ satisfies 10 axioms (closure under $+$ and scalar multiply; associativity, commutativity; zero vector; additive inverses; distributivity).

**Examples:** $\\mathbb{R}^n$; polynomials $P_n$ of degree $\\leq n$; matrices $M_{m\\times n}$; continuous functions $C[a,b]$.

**Zero vector** $\\vec{0}$ is unique. **Counterexample:** the half-plane $\\{(x,y): x \\geq 0\\}$ is **not** a vector space — no additive inverses for most vectors.""",
                """**מרחב וקטורי** $V$ מעל $\\mathbb{R}$ מקיים 10 אקסיומות (סגירות, אסוצiativיות, $\\vec{0}$, הופכים, דistributivיות).

**דוגמאות:** $\\mathbb{R}^n$; פולינומים $P_n$; מטריצות $M_{m\\times n}$; פונקציות רציפות $C[a,b]$.

**וקטור האפס** $\\vec{0}$ יחיד. **דוגמת נגד:** חצי-מישור $\\{(x,y): x \\geq 0\\}$ **אינו** מרחב וקטורי — אין הופכים.""",
            ),
            section(
                "theory",
                "Subspaces",
                "תת-מרחבים",
                """$W \\subseteq V$ is a **subspace** iff:
1. $\\vec{0} \\in W$
2. Closed under addition: $\\vec{u},\\vec{v} \\in W \\Rightarrow \\vec{u}+\\vec{v} \\in W$
3. Closed under scalar multiplication: $c\\vec{v} \\in W$ for all scalars $c$

**Examples (subspaces):** $\\text{span}\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$; $\\ker(A) = \\{\\vec{x}: A\\vec{x}=\\vec{0}\\}$; solution space of $A\\vec{x}=\\vec{0}$.

**NOT a subspace:** $\\{(x,y): x+y=1\\}$ — does not contain $\\vec{0}$.

**Subspace test:** verify all three conditions (or the one-step: $c\\vec{u}+d\\vec{v} \\in W$).""",
                """$W \\subseteq V$ הוא **תת-מרחב** iff:
1. $\\vec{0} \\in W$
2. סגור לחיבור
3. סגור לכפל בסקalar

**דוגמאות:** $\\text{span}$; $\\ker(A)$; מרחב פתרונות של $A\\vec{x}=\\vec{0}$.

**לא תת-מרחב:** $\\{(x,y): x+y=1\\}$ — אין $\\vec{0}$.""",
            ),
            section(
                "worked_example",
                "Linear independence",
                "בלתי-תלות לינארית",
                """Vectors $\\vec{v}_1,\\ldots,\\vec{v}_k$ are **linearly independent** if
$$c_1\\vec{v}_1 + \\cdots + c_k\\vec{v}_k = \\vec{0} \\Rightarrow c_i = 0 \\text{ for all } i.$$

**Span:** $\\text{span}(\\vec{v}_1,\\ldots,\\vec{v}_k) = \\{c_1\\vec{v}_1+\\cdots+c_k\\vec{v}_k\\}$ — always a subspace.

**Test via Gaussian elimination:** form matrix with vectors as columns; independent iff no free columns.

**Worked example:** Are $(1,2,3), (0,1,2), (1,1,1)$ independent?
$$\\left[\\begin{array}{ccc} 1 & 0 & 1 \\\\ 2 & 1 & 1 \\\\ 3 & 2 & 1 \\end{array}\\right] \\to \\text{REF: 3 pivots} \\Rightarrow \\text{independent}.$$""",
                """$\\vec{v}_1,\\ldots,\\vec{v}_k$ **בלתי-תלויים לינארית** אם
$$c_1\\vec{v}_1 + \\cdots + c_k\\vec{v}_k = \\vec{0} \\Rightarrow c_i = 0.$$

**קבוצת פרישה (span):** כל הקומבינציות הלינאריות — תמיד תת-מרחב.

**בדיקה:** מטריצה עם הוקטורים כעמודות; בלתי-תלויים iff 3 pivots.

**דוגמה:** $(1,2,3), (0,1,2), (1,1,1)$ — 3 pivots ⇒ **בלתי-תלויים**.""",
            ),
            section(
                "theory",
                "Basis and dimension",
                "בסיס וממד",
                """A **basis** of $V$ is a linearly independent spanning set. **Dimension** $\\dim(V)$ = number of vectors in any basis.

**Standard basis** of $\\mathbb{R}^n$: $\\vec{e}_1,\\ldots,\\vec{e}_n$.

**Exchange lemma (stated):** in a finite-dimensional space, every linearly independent set can be extended to a basis; every basis has the same size.

**Rank–Nullity:** for $A$ with $n$ columns,
$$\\dim(\\ker A) + \\dim(\\text{col}(A)) = n.$$

Example: $3\\times 3$ matrix with rank 2 has nullity 1.""",
                """**בסיס** = קבוצה בלתי-תלויה וסוגרת. **ממד** = גודל כל בסיס.

**בסיס סטנדרטי** ב-$\\mathbb{R}^n$: $\\vec{e}_1,\\ldots,\\vec{e}_n$.

**למת החלפה (נוסח):** כל קבוצה בלתי-תלויה ניתנת להרחבה לבסיס; כל הבסיסים באותו גודל.

**דרגה-גרעין:** $\\dim(\\ker A) + \\dim(\\text{col}(A)) = n$.""",
            ),
            section(
                "worked_example",
                "Coordinates in a basis",
                "קואורדינטות בבסיס",
                """Every $\\vec{v}$ in a basis $B = \\{\\vec{b}_1,\\ldots,\\vec{b}_n\\}$ has **unique** representation $\\vec{v} = c_1\\vec{b}_1 + \\cdots + c_n\\vec{b}_n$. The **coordinate vector** is $[\\vec{v}]_B = (c_1,\\ldots,c_n)^T$.

**Technion-style problem:** Find coordinates of $(3,5,1)$ in $B = \\{(1,1,0), (0,1,1), (1,0,1)\\}$.

Solve $c_1(1,1,0) + c_2(0,1,1) + c_3(1,0,1) = (3,5,1)$:
$$\\begin{cases} c_1 + c_3 = 3 \\\\ c_1 + c_2 = 5 \\\\ c_2 + c_3 = 1 \\end{cases} \\Rightarrow c_1 = 2,\\; c_2 = 3,\\; c_3 = 1.$$
So $[(3,5,1)]_B = (2,3,1)^T$.""",
                """ייצוג **יחיד:** $\\vec{v} = c_1\\vec{b}_1 + \\cdots + c_n\\vec{b}_n$; $[\\vec{v}]_B = (c_1,\\ldots,c_n)^T$.

**בעיה:** קואורדינטות של $(3,5,1)$ ב-$B = \\{(1,1,0), (0,1,1), (1,0,1)\\}$.

$$c_1 + c_3 = 3,\\; c_1 + c_2 = 5,\\; c_2 + c_3 = 1 \\Rightarrow (2,3,1)^T.$$""",
            ),
        ],
        "questions": [
            mcq(
                1, "easy",
                "Which set is a subspace of $\\mathbb{R}^2$?",
                "איזו קבוצה היא תת-מרחב של $\\mathbb{R}^2$?",
                ["$\\{(x,y): x+y=1\\}$", "$\\{(x,y): x=0\\}$ (the $y$-axis)", "$\\{(x,y): x \\geq 0\\}$", "$\\{(x,y): xy=0\\}$"],
                ["$\\{(x,y): x+y=1\\}$", "$\\{(x,y): x=0\\}$ (ציר $y$)", "$\\{(x,y): x \\geq 0\\}$", "$\\{(x,y): xy=0\\}$"],
                1,
                "The y-axis contains 0, is closed under addition and scaling. The others fail (no 0, or not closed).",
                "ציר $y$ מכיל 0 וסגור לחיבור וכפל. השאר נכשלים.",
                ["verify_subspace"],
            ),
            mcq(
                2, "medium",
                "Are $(1,0,1), (2,0,2), (0,1,0)$ linearly independent in $\\mathbb{R}^3$?",
                "האם $(1,0,1), (2,0,2), (0,1,0)$ בלתי-תלויים ב-$\\mathbb{R}^3$?",
                ["Yes", "No — the first two are dependent", "No — all three are dependent", "Cannot determine"],
                ["כן", "לא — הראשונים תלויים", "לא — כולם תלויים", "לא ניתן לקבוע"],
                1,
                "$(2,0,2) = 2(1,0,1)$, so only 2 independent vectors at most.",
                "$(2,0,2) = 2(1,0,1)$ — לכל היותר 2 בלתי-תלויים.",
                ["test_linear_independence"],
            ),
            mcq(
                3, "medium",
                "$\\text{span}\\{(1,0,0), (0,1,0)\\}$ in $\\mathbb{R}^3$ has dimension:",
                "$\\text{span}\\{(1,0,0), (0,1,0)\\}$ ב-$\\mathbb{R}^3$ במימד:",
                ["$1$", "$2$", "$3$", "$0$"],
                ["$1$", "$2$", "$3$", "$0$"],
                1,
                "Two independent vectors span the $xy$-plane — a 2-dimensional subspace.",
                "שני וקטורים בלתי-תלויים ⇒ מישור — מימד 2.",
                ["dimension_of_span"],
            ),
            mcq(
                4, "medium",
                "$A$ is $4 \\times 6$ with rank 3. What is $\\dim(\\ker A)$?",
                "$A$ בגודל $4 \\times 6$ עם rank 3. מה $\\dim(\\ker A)$?",
                ["$1$", "$2$", "$3$", "$6$"],
                ["$1$", "$2$", "$3$", "$6$"],
                2,
                "Rank–Nullity: nullity = $n - \\text{rank} = 6 - 3 = 3$.",
                "דרגה-גרעין: $6 - 3 = 3$.",
                ["rank_nullity"],
            ),
            mcq(
                5, "hard",
                "Coordinates of $(3,5,1)$ in basis $\\{(1,1,0), (0,1,1), (1,0,1)\\}$ are:",
                "קואורדינטות של $(3,5,1)$ בבסיס $\\{(1,1,0), (0,1,1), (1,0,1)\\}$:",
                ["$(3,5,1)$", "$(2,3,1)$", "$(1,2,3)$", "$(2,1,3)$"],
                ["$(3,5,1)$", "$(2,3,1)$", "$(1,2,3)$", "$(2,1,3)$"],
                1,
                "Solve $c_1(1,1,0)+c_2(0,1,1)+c_3(1,0,1)=(3,5,1)$ to get $(2,3,1)$.",
                "פתרון המערכת נותן $(2,3,1)$.",
                ["coordinates_in_basis"],
            ),
        ],
        "agent_hints": agent_hints(
            [
                "Subspace: contains 0, closed under + and scalar multiply.",
                "Basis = independent + spanning; dim = |basis|.",
                "Rank–Nullity: dim(ker A) + rank(A) = n (columns of A).",
            ],
            [
                {"wrong": "Any subset of R^n is a subspace", "correction": "Must contain 0 and be closed under linear combinations.", "detect_phrase_en": "any subset", "detect_phrase_he": "כל תת-קבוצה"},
            ],
            "Test subspaces with the one-step combination rule before abstract axioms.",
            {"confuses span with basis": "Spanning is not enough — need independence too."},
            ["verify_subspace", "test_linear_independence", "dimension_of_span", "rank_nullity", "coordinates_in_basis"],
        ),
    },
    # --- Lesson 3: linear_transformations_kernel_image ---
    {
        "concept_id": "linear_transformations_kernel_image",
        "subject": "linear_algebra",
        "level": "university",
        "math_track": ["la"],
        "title_en": "Linear Transformations, Kernel & Image",
        "title_he": "העתקות לינאריות, גרעין ותמונה",
        "summary_en": "Define linear maps, matrix representation, kernel (null space), image (column space), Rank–Nullity, and invertibility for $T: \\mathbb{R}^n \\to \\mathbb{R}^n$.",
        "summary_he": "הגדרת העתקות לינאריות, ייצוג מטריצי, גרעין, תמונה, משפט דרגה-גרעין והפיכות.",
        "est_minutes": 35,
        "sections": [
            section(
                "theory",
                "Definition of linear transformation",
                "הגדרת העתקה לינארית",
                """$T: V \\to W$ is **linear** if for all $\\vec{u},\\vec{v} \\in V$ and scalars $a,b$:
$$T(a\\vec{u} + b\\vec{v}) = aT(\\vec{u}) + bT(\\vec{v}).$$

Equivalently: $T(\\vec{u}+\\vec{v}) = T(\\vec{u})+T(\\vec{v})$ and $T(c\\vec{v}) = cT(\\vec{v})$.

**Immediate consequence:** $T(\\vec{0}) = \\vec{0}$.

**Examples:** $T(x,y) = (2x+y, x-3y)$; differentiation on $P_n$; projection onto a line; rotation by $\\theta$ in $\\mathbb{R}^2$.""",
                """$T: V \\to W$ **לינארית** אם:
$$T(a\\vec{u} + b\\vec{v}) = aT(\\vec{u}) + bT(\\vec{v}).$$

**מסקנה:** $T(\\vec{0}) = \\vec{0}$.

**דוגמאות:** $T(x,y) = (2x+y, x-3y)$; גזירה; הטלה; סיבוב בזווית $\\theta$.""",
            ),
            section(
                "theory",
                "Matrix representation",
                "ייצוג מטריצי",
                """Every linear $T: \\mathbb{R}^n \\to \\mathbb{R}^m$ equals $T(\\vec{x}) = A\\vec{x}$ where
$$A = [T(\\vec{e}_1)\\,|\\,T(\\vec{e}_2)\\,|\\,\\cdots\\,|\\,T(\\vec{e}_n)].$$

**Example:** $T(x,y) = (2x+y, x-3y)$ gives $A = \\begin{pmatrix} 2 & 1 \\\\ 1 & -3 \\end{pmatrix}$.

**Composition:** $(T_2 \\circ T_1)(\\vec{x}) = T_2(T_1(\\vec{x}))$ corresponds to $A_2 A_1$ (order matters).

**Rotation:** $R_\\theta = \\begin{pmatrix} \\cos\\theta & -\\sin\\theta \\\\ \\sin\\theta & \\cos\\theta \\end{pmatrix}$.""",
                """כל $T: \\mathbb{R}^n \\to \\mathbb{R}^m$ שווה ל-$A\\vec{x}$ עם
$$A = [T(\\vec{e}_1)\\,|\\,\\cdots\\,|\\,T(\\vec{e}_n)].$$

**דוגמה:** $T(x,y) = (2x+y, x-3y)$ ⇒ $A = \\begin{pmatrix} 2 & 1 \\\\ 1 & -3 \\end{pmatrix}$.

**הרכבה:** $A_2 A_1$. **סיבוב:** $R_\\theta$ עם $\\cos,\\sin$.""",
            ),
            section(
                "worked_example",
                "Kernel (null space)",
                "גרעין (מרחב האפסים)",
                """$\\ker(T) = \\{\\vec{v} \\in V : T(\\vec{v}) = \\vec{0}\\}$ — always a subspace of the **domain**.

Find by solving $A\\vec{x} = \\vec{0}$. **Nullity** = $\\dim(\\ker T)$.

$T$ is **injective** (one-to-one) iff $\\ker(T) = \\{\\vec{0}\\}$.

**Worked example:** $T(x,y,z) = (x+y, y+z, x+z)$.
$$A = \\begin{pmatrix} 1 & 1 & 0 \\\\ 0 & 1 & 1 \\\\ 1 & 0 & 1 \\end{pmatrix} \\Rightarrow \\ker = \\text{span}\\{(1,-1,1)\\},\\; \\text{nullity} = 1.$$""",
                """$\\ker(T) = \\{\\vec{v}: T(\\vec{v}) = \\vec{0}\\}$ — תת-מרחב של **תחום**.

**Nullity** = $\\dim(\\ker T)$. **חד-חד-ערכית** iff $\\ker = \\{\\vec{0}\\}$.

**דוגמה:** $T(x,y,z) = (x+y, y+z, x+z)$ ⇒ $\\ker = \\text{span}\\{(1,-1,1)\\}$, nullity = 1.""",
            ),
            section(
                "theory",
                "Image (range) and Rank–Nullity",
                "תמונה (Range) ודרגה-גרעין",
                """$\\text{Im}(T) = \\{T(\\vec{v}) : \\vec{v} \\in V\\}$ — subspace of the **codomain**.

For $T(\\vec{x})=A\\vec{x}$: $\\text{Im}(T) = \\text{col}(A)$ (column space). **Rank** = $\\dim(\\text{Im}(T))$.

$T$ is **surjective** onto $\\mathbb{R}^m$ iff $\\text{rank}(A) = m$.

**Rank–Nullity theorem:**
$$\\text{nullity}(T) + \\text{rank}(T) = \\dim(V).$$

For a $3\\times 3$ matrix: rank 2 ⇒ nullity 1.""",
                """$\\text{Im}(T)$ — תת-מרחב של **טווח**. עבור $A\\vec{x}$: $\\text{Im}(T) = \\text{col}(A)$.

**דרגה** = $\\dim(\\text{Im}(T))$. **על** iff rank = $m$.

**דרגה-גרעין:** nullity + rank = $\\dim(V)$.""",
            ),
            section(
                "worked_example",
                "Isomorphisms and invertibility",
                "איזומורפיזמים והפיכות",
                """$T$ is **invertible** iff bijective (injective + surjective). For $T: \\mathbb{R}^n \\to \\mathbb{R}^n$, the following are equivalent:
- $\\ker(T) = \\{\\vec{0}\\}$
- $\\text{rank}(T) = n$
- $A$ is invertible / $\\det(A) \\neq 0$

**Exam problem:** Is $T(x,y) = (x+y, x-y)$ invertible?
$A = \\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}$, $\\det A = -2 \\neq 0$ ⇒ yes.
$$A^{-1} = \\frac{1}{-2}\\begin{pmatrix} -1 & -1 \\\\ -1 & 1 \\end{pmatrix} = \\begin{pmatrix} 1/2 & 1/2 \\\\ 1/2 & -1/2 \\end{pmatrix}.$$
So $T^{-1}(u,v) = (\\frac{u+v}{2}, \\frac{u-v}{2})$.""",
                """$T$ **הפיכה** iff חד-חד-ערכית ועל. ל-$T: \\mathbb{R}^n \\to \\mathbb{R}^n$ שקולים: $\\ker=\\{0\\}$, rank=$n$, $\\det A \\neq 0$.

**מבחן:** $T(x,y)=(x+y,x-y)$, $\\det=-2\\neq 0$ ⇒ כן.
$T^{-1}(u,v) = (\\frac{u+v}{2}, \\frac{u-v}{2})$.""",
            ),
        ],
        "questions": [
            mcq(
                1, "easy",
                "Which map is **not** linear?",
                "איזו העתקה **אינה** לינארית?",
                ["$T(x,y)=(2x,y)$", "$T(x,y)=(x+1,y)$", "$T(x)=3x$", "$T(x,y)=(x-y,0)$"],
                ["$T(x,y)=(2x,y)$", "$T(x,y)=(x+1,y)$", "$T(x)=3x$", "$T(x,y)=(x-y,0)$"],
                1,
                "$T(0,0)=(1,0)\\neq(0,0)$ — constant term breaks linearity.",
                "$T(0,0)=(1,0)\\neq(0,0)$ — איבר קבוע שובר לינאריות.",
                ["verify_linearity"],
            ),
            mcq(
                2, "medium",
                "Matrix of $T(x,y,z)=(x+2z, y-z)$ is:",
                "מטריצה של $T(x,y,z)=(x+2z, y-z)$:",
                ["$\\begin{pmatrix}1&0&2\\\\0&1&-1\\end{pmatrix}$", "$\\begin{pmatrix}1&2&0\\\\0&-1&1\\end{pmatrix}$", "$\\begin{pmatrix}1&0&2\\\\0&1&1\\end{pmatrix}$", "$\\begin{pmatrix}2&0&1\\\\-1&1&0\\end{pmatrix}$"],
                ["$\\begin{pmatrix}1&0&2\\\\0&1&-1\\end{pmatrix}$", "$\\begin{pmatrix}1&2&0\\\\0&-1&1\\end{pmatrix}$", "$\\begin{pmatrix}1&0&2\\\\0&1&1\\end{pmatrix}$", "$\\begin{pmatrix}2&0&1\\\\-1&1&0\\end{pmatrix}$"],
                0,
                "Columns are $T(1,0,0)=(1,0)$, $T(0,1,0)=(0,1)$, $T(0,0,1)=(2,-1)$.",
                "עמודות: $T(e_1), T(e_2), T(e_3)$.",
                ["matrix_of_transformation"],
            ),
            mcq(
                3, "medium",
                "$\\ker(T)$ for $T(x,y)=(2x,2y)$ in $\\mathbb{R}^2$ is:",
                "$\\ker(T)$ עבור $T(x,y)=(2x,2y)$ ב-$\\mathbb{R}^2$:",
                ["$\\{(0,0)\\}$ only", "All of $\\mathbb{R}^2$", "The $x$-axis", "The line $y=x$"],
                ["$\\{(0,0)\\}$ בלבד", "כל $\\mathbb{R}^2$", "ציר $x$", "הישר $y=x$"],
                0,
                "Only (0,0) maps to 0; scaling by 2 is invertible on each coordinate.",
                "רק $(0,0)$ מתאפס — כפל ב-2 הפיך.",
                ["compute_kernel"],
            ),
            mcq(
                4, "medium",
                "$A$ is $3\\times 5$ with rank 2. $\\dim(\\text{Im}(T))$ and nullity are:",
                "$A$ בגודל $3\\times 5$ עם rank 2. $\\dim(\\text{Im}(T))$ ו-nullity:",
                ["$2$ and $3$", "$3$ and $2$", "$5$ and $0$", "$2$ and $2$"],
                ["$2$ ו-$3$", "$3$ ו-$2$", "$5$ ו-$0$", "$2$ ו-$2$"],
                0,
                "rank = dim(Im) = 2; nullity = 5 - 2 = 3.",
                "rank = dim(Im) = 2; nullity = 5 - 2 = 3.",
                ["image_rank"],
            ),
            mcq(
                5, "hard",
                "$T: \\mathbb{R}^2 \\to \\mathbb{R}^2$, $T(x,y)=(x+y,x+y)$. Which is true?",
                "$T: \\mathbb{R}^2 \\to \\mathbb{R}^2$, $T(x,y)=(x+y,x+y)$. מה נכון?",
                ["Invertible", "Rank 1, not invertible", "Surjective", "Kernel is empty"],
                ["הפיכה", "Rank 1, לא הפיכה", "על", "גרעין ריק"],
                1,
                "Image is line $u=v$ — rank 1 < 2; kernel is $\\{(t,-t)\\}$.",
                "תמונה = ישר $u=v$ — rank 1; $\\ker = \\{(t,-t)\\}$.",
                ["rank_nullity_transform"],
            ),
        ],
        "agent_hints": agent_hints(
            [
                "Linear: T(0)=0; matrix columns = T(e_i).",
                "ker(T) in domain; Im(T) in codomain = col(A).",
                "Rank–Nullity: nullity + rank = dim(domain).",
            ],
            [
                {"wrong": "Linear maps can have T(0) ≠ 0", "correction": "T(0) must be 0 for any linear map.", "detect_phrase_en": "T(0) not zero", "detect_phrase_he": "T(0) לא אפס"},
            ],
            "Build matrix from images of basis vectors before computing kernel.",
            {"confuses kernel and image spaces": "Kernel lives in domain; image in codomain."},
            ["verify_linearity", "matrix_of_transformation", "compute_kernel", "image_rank", "rank_nullity_transform"],
        ),
    },
    # --- Lesson 4: matrix_representation ---
    {
        "concept_id": "matrix_representation",
        "subject": "linear_algebra",
        "level": "university",
        "math_track": ["la"],
        "title_en": "Matrices as Linear Transformations & Change of Basis",
        "title_he": "מטריצות כהעתקות לינאריות ומעבר בסיסים",
        "summary_en": "$A\\vec{x}$ as column combinations, matrix of $T$ in non-standard bases, similarity $P^{-1}AP$, diagonalization, and principal axes in engineering.",
        "summary_he": "$A\\vec{x}$ כקומבינציה של עמודות, מטריצת $T$ בבסיסים, דמיון $P^{-1}AP$, אלכסון וצירים ראשיים בהנדסה.",
        "est_minutes": 30,
        "sections": [
            section(
                "theory",
                "Matrix–vector product as transformation",
                "מכפלת מטריצה-וקטור כהעתקה",
                """$A\\vec{x} = x_1\\vec{a}_1 + x_2\\vec{a}_2 + \\cdots$ — linear combination of **columns** of $A$.

**Column space** $\\text{col}(A)$ = image of $L(\\vec{x})=A\\vec{x}$.

**Geometric $2\\times 2$ examples:**
- $\\begin{pmatrix}2&0\\\\0&2\\end{pmatrix}$ — uniform scaling by 2.
- $\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix}$ — rotation $90°$.
- $\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ — shear (fixes $x$-axis, slides $y$).
- $\\begin{pmatrix}1&0\\\\0&0\\end{pmatrix}$ — projection onto $x$-axis.""",
                """$A\\vec{x}$ = קומבינציה לינארית של **עמודות** $A$. $\\text{col}(A)$ = תמונה.

**דוגמאות גיאומטריות 2×2:** scaling, סיבוב 90°, share, הטלה על ציר $x$.""",
            ),
            section(
                "theory",
                "Matrix of T in a non-standard basis",
                "מטריצת T בבסיס לא-סטנדרטי",
                """If $B = \\{\\vec{b}_1,\\ldots,\\vec{b}_n\\}$ is a basis of $V$ and $C$ of $W$, the matrix $[T]_{B,C}$ has columns $[T(\\vec{b}_j)]_C$.

In standard coordinates, if $A$ represents $T$ and $P_B$ has basis vectors as columns:
$$[T]_B = P^{-1} A P_B$$
(change-of-basis between standard and $B$).

**Idea:** express what $T$ does to each basis vector of $B$, then write results in coordinates of $C$.""",
                """$[T]_{B,C}$: עמודה $j$ = $[T(\\vec{b}_j)]_C$.

בקואורדינטות סטנדרטיות: $[T]_B = P^{-1} A P_B$.

**רעיון:** מה $T$ עושה לכל וקטור בסיס $B$, וכתיבת התוצאה בקואורדינטות $C$.""",
            ),
            section(
                "theory",
                "Change of basis and similar matrices",
                "מעבר בסיסים ומטריצות דומות",
                """$P_B = [\\vec{b}_1\\,|\\,\\cdots\\,|\\,\\vec{b}_n]$ — change-of-basis matrix (columns = basis vectors in standard coords).

$$[\\vec{v}]_B = P_B^{-1}\\vec{v}.$$

If $[T]_B = P^{-1} A P$, then $A$ and $[T]_B$ are **similar**. **Similar matrices share eigenvalues** (same characteristic polynomial).

Diagonalization $A = PDP^{-1}$: $D$ = eigenvalues on diagonal, columns of $P$ = eigenvectors — this is $[T]_B$ in the eigenbasis.""",
                """$P_B$ — מטריצת מעבר בסיס. $[\\vec{v}]_B = P_B^{-1}\\vec{v}$.

$A$ ו-$P^{-1}AP$ **דומות** — **אותם ערכים עצמיים**.

$A = PDP^{-1}$: $D$ ערכים עצמיים, $P$ וקטורים עצמיים — $[T]$ בבסיס העצמי.""",
            ),
            section(
                "theory",
                "Diagonalization revisited",
                "אלכסון — חזרה",
                """$A = PDP^{-1}$ where $D = \\text{diag}(\\lambda_1,\\ldots,\\lambda_n)$, $P$ invertible with eigenvector columns.

**When does an eigenbasis exist?**
- $n$ distinct eigenvalues ⇒ $n$ independent eigenvectors.
- Or: enough independent eigenvectors even with repeated $\\lambda$.

**Powers:** $A^k = PD^k P^{-1}$ — easy when $D^k$ is diagonal.

**Application:** decouple coupled systems (physics, differential equations).""",
                """$A = PDP^{-1}$. **מתי קיים בסיס עצמי?** $n$ ערכים שונים, או מספיק וקטורים עצמיים בלתי-תלויים.

**חזקות:** $A^k = PD^k P^{-1}$.""",
            ),
            section(
                "theory",
                "Engineering: principal axes",
                "יישום הנדסי: צירים ראשיים",
                """Symmetric **stress tensor** $\\Sigma$ (materials engineering): eigenvalues = **principal stresses**, eigenvectors = **principal directions**.

Rotate coordinates to the eigenbasis → $\\Sigma$ becomes diagonal (no shear stress in those directions). Brief link to **Mohr's circle** for 2D stress states.

Similarly, the **moment of inertia tensor** diagonalizes in principal axes — simplifying rotational dynamics (links to `concept:angular_momentum`).

**Statistics connection:** least-squares normal equations use $(A^T A)$ — symmetric, often analyzed via eigenvalues for conditioning.""",
                """טנזור **מתח סימטרי** $\\Sigma$: ערכים עצמיים = **מתחים ראשיים**, וקטורים עצמיים = **כיוונים ראשיים**.

סיבוב לבסיס העצמי → $\\Sigma$ אלכסונית (ללא גזירה). קשר ל**מעגל מור** (2D).

**טנזור מומנט אינרציה** — אלכסון בצירים ראשיים. קשר לרגרסיה: $(A^T A)$ סימטרית.""",
            ),
        ],
        "questions": [
            mcq(
                1, "medium",
                "Columns of $A$ are $(1,0), (1,1)$. $A\\begin{pmatrix}2\\\\-1\\end{pmatrix}$ equals:",
                "עמודות $A$: $(1,0), (1,1)$. $A\\begin{pmatrix}2\\\\-1\\end{pmatrix}$ שווה ל:",
                ["$(1,1)$", "$(2,0)$", "$(0,1)$", "$(3,-1)$"],
                ["$(1,1)$", "$(2,0)$", "$(0,1)$", "$(3,-1)$"],
                0,
                "$2(1,0) + (-1)(1,1) = (2,0) + (-1,-1) = (1,-1)$ — wait recalc: (2-1, 0-1) = (1,-1). None match (1,-1). Fix: use (2,1) -> 2(1,0)+1(1,1)=(3,1).",
                "קומבינציה לינארית של העמודות.",
                ["matrix_vector_transformation"],
            ),
            mcq(
                2, "hard",
                "If $P = \\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ and $A = \\begin{pmatrix}2&0\\\\0&3\\end{pmatrix}$, then $P^{-1}AP$ represents:",
                "אם $P = \\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ ו-$A$ אלכסונית, $P^{-1}AP$ מייצג:",
                ["The same transformation in a sheared basis", "A rotation of A", "Always diagonal", "Always identity"],
                ["אותה העתקה בבסיס מגודר", "סיבוב של A", "תמיד אלכסונית", "תמיד היחידה"],
                0,
                "Similarity change = same linear map, different coordinates (here, a sheared basis).",
                "שינוי דמיון = אותה העתקה, קואורדינטות שונות.",
                ["change_of_basis_matrix"],
            ),
            mcq(
                3, "medium",
                "If $A$ and $B$ are similar, which must be equal?",
                "אם $A$ ו-$B$ דומות, מה חייב להיות שווה?",
                ["All entries", "Determinant and eigenvalues", "Number of zero rows", "First column"],
                ["כל האיברים", "דטרמיננטה וערכים עצמיים", "מספר שורות אפס", "עמודה ראשונה"],
                1,
                "Similar matrices share characteristic polynomial, hence eigenvalues and determinant.",
                "מטריצות דומות חולקות פולינום אופייני — אותם ע\"ע ודטרמיננטה.",
                ["similar_eigenvalues"],
            ),
            mcq(
                4, "medium",
                "$A = \\begin{pmatrix}4&2\\\\1&3\\end{pmatrix}$ has eigenvalues 5 and 2. Which diagonalizes $A$?",
                "ל-$A$ ע\"ע 5 ו-2. מה מאלכסן?",
                ["$P=I$ always", "$P$ with independent eigenvector columns", "Any invertible $P$", "Only orthogonal $P$"],
                ["$P=I$ תמיד", "$P$ עם עמודות וקטור עצמי בלתי-תלוי", "כל $P$ הפיכה", "רק $P$ אורתוגונלית"],
                1,
                "$A = PDP^{-1}$ requires $P$ whose columns are eigenvectors forming a basis.",
                "$P$ עם וקטורים עצמיים בלתי-תלויים כעמודות.",
                ["diagonalization"],
            ),
            mcq(
                5, "medium",
                "Principal stresses are:",
                "מתחים ראשיים הם:",
                ["Off-diagonal entries of $\\Sigma$", "Eigenvalues of the symmetric stress tensor", "Components in standard axes only", "Always zero"],
                ["איברים לא-אלכסוניים", "ערכים עצמיים של טנזור המתח", "רק ברכיבי ציר", "תמיד אפס"],
                1,
                "Eigenvalues of symmetric $\\Sigma$ give extremal normal stresses in principal directions.",
                "ערכים עצמיים של $\\Sigma$ הסימטרי = מתחים נורמליים קיצוניים.",
                ["principal_axes_application"],
            ),
        ],
        "agent_hints": agent_hints(
            [
                "A x = linear combo of columns; col(A) = image.",
                "Similar matrices: P^{-1}AP; same eigenvalues.",
                "Diagonalization: eigenbasis makes T diagonal.",
            ],
            [
                {"wrong": "Change of basis changes the transformation", "correction": "Same T; only coordinate representation changes.", "detect_phrase_en": "changes the map", "detect_phrase_he": "משנה את ההעתקה"},
            ],
            "Show one 2×2 geometric example (rotation/shear) before abstract P^{-1}AP.",
            {"confuses A with P^{-1}AP": "Similarity is same operator, different basis."},
            ["matrix_vector_transformation", "change_of_basis_matrix", "similar_eigenvalues", "diagonalization", "principal_axes_application"],
        ),
    },
]


def fix_q1_matrix_lesson(lesson):
    """Fix question 1 in matrix_representation — correct answer (1,-1)."""
    q = lesson["questions"][0]
    q["options_en"] = ["$(1,-1)$", "$(1,1)$", "$(2,0)$", "$(0,1)$"]
    q["options_he"] = ["$(1,-1)$", "$(1,1)$", "$(2,0)$", "$(0,1)$"]
    q["correct_index"] = 0
    q["explanation_en"] = "$2(1,0) + (-1)(1,1) = (2-1, 0-1) = (1,-1)$."
    q["explanation_he"] = "$2(1,0) + (-1)(1,1) = (1,-1)$."


def write_lessons():
    for lesson in LESSONS:
        if lesson["concept_id"] == "matrix_representation":
            fix_q1_matrix_lesson(lesson)
        path = os.path.join(LESSONS_DIR, f"{lesson['concept_id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
        print(f"Wrote {path}")


def update_index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    meta = {
        "systems_linear_equations": {
            "title_en": "Systems of Linear Equations & Gaussian Elimination",
            "title_he": "מערכות משוואות לינאריות ואלימינציה גאוסית",
            "est_minutes": 40,
            "duration_min": 40,
        },
        "vector_spaces_basis_dimension": {
            "title_en": "Vector Spaces, Basis & Dimension",
            "title_he": "מרחבים וקטוריים, בסיס וממד",
            "est_minutes": 35,
            "duration_min": 35,
        },
        "linear_transformations_kernel_image": {
            "title_en": "Linear Transformations, Kernel & Image",
            "title_he": "העתקות לינאריות, גרעין ותמונה",
            "est_minutes": 35,
            "duration_min": 35,
        },
        "matrix_representation": {
            "title_en": "Matrices as Linear Transformations & Change of Basis",
            "title_he": "מטריצות כהעתקות לינאריות ומעבר בסיסים",
            "est_minutes": 30,
            "duration_min": 30,
        },
    }

    existing = {e["id"]: i for i, e in enumerate(index)}
    for cid, m in meta.items():
        entry = {
            "id": cid,
            "title_en": m["title_en"],
            "title_he": m["title_he"],
            "est_minutes": m["est_minutes"],
            "math_track": ["la"],
            "subject": "linear_algebra",
            "duration_min": m["duration_min"],
            "type": "interactive",
            "level_min": "university",
        }
        if cid in existing:
            index[existing[cid]].update(entry)
            print(f"Updated index: {cid}")
        else:
            index.append(entry)
            print(f"Added index: {cid}")

    index.sort(key=lambda e: e["id"])
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"Index written: {INDEX_PATH}")


if __name__ == "__main__":
    write_lessons()
    update_index()
    print("Done.")
