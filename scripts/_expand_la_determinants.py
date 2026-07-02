#!/usr/bin/env python3
"""Expand la_determinants.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/la_determinants.json"

MIN = {
    "intro": (110, 90),
    "definition": (130, 110),
    "theory": (160, 130),
    "worked_example": (130, 110),
    "pitfall": (100, 85),
    "why_matters": (90, 75),
    "method_guide": (100, 85),
    "before_exam": (90, 75),
    "summary": (70, 60),
}


def wc(text: str) -> int:
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he) -> tuple[str, str]:
    en = (
        f"**Why this is correct:**\n{why_en}\n\n"
        f"**How to think about it:**\n{how_en}\n\n"
        f"**Common slip:**\n{slip_en}\n\n"
        f"**Exam tip:**\n{tip_en}"
    )
    he = (
        f"**למה זה נכון:**\n{why_he}\n\n"
        f"**איך לחשוב על זה:**\n{how_he}\n\n"
        f"**טעות נפוצה:**\n{slip_he}\n\n"
        f"**טיפ לבחינה:**\n{tip_he}"
    )
    return en, he


PATCHES = {
    "intro": {
        "body_en_md": """The **determinant** assigns to every square matrix $A$ a single scalar $\\det(A)$ that encodes far more than a mere number: it tells you whether $A$ is invertible, how much the linear map $A\\vec{x}$ scales signed area (in $\\mathbb{R}^2$) or volume (in $\\mathbb{R}^3$), and — through Cramer's rule — gives closed-form solutions to linear systems when the coefficient matrix is nonsingular.

Geometrically, if the columns of $A$ are vectors $\\vec{v}_1,\\ldots,\\vec{v}_n$ in $\\mathbb{R}^n$, then $|\\det(A)|$ equals the $n$-dimensional volume of the parallelepiped they span. A negative determinant indicates that the orientation of the basis is reversed — the map "flips" space.

Determinants appear throughout the course: the characteristic polynomial $\\det(A-\\lambda I)=0$ yields eigenvalues; the Jacobian determinant changes variables in multiple integrals; and in $\\mathbb{R}^3$, the cross product magnitude relates to a $3\\times3$ determinant. Mastering determinant properties now pays dividends in eigenvalue theory, matrix inversion, and applied linear algebra.

**Connection to previous material:** You have computed $2\\times2$ determinants as $ad-bc$. Here we systematise the definition for any $n\\times n$ matrix via cofactor (Laplace) expansion and develop the algebraic toolkit — row-operation effects, multiplicativity, and Cramer's rule — that makes determinants practical on exams.""",
        "body_he_md": """ה**דטרמיננטה** מקצה לכל מטריצה ריבועית $A$ סקalar יחיד $\\det(A)$ שמקודד הרבה יותר ממספר: היא אומרת האם $A$ הפיכה, כמה ההעתקה $A\\vec{x}$ מכפילה שטח מכוון (ב-$\\mathbb{R}^2$) או נפח (ב-$\\mathbb{R}^3$), ו — דרך כלל קרמר — נותנת פתרון סגור למערכות לינאריות כשמטריצת המקדמים אינה סינגולרית.

גיאומטרית, אם העמודות של $A$ הן $\\vec{v}_1,\\ldots,\\vec{v}_n$ ב-$\\mathbb{R}^n$, אז $|\\det(A)|$ שווה לנפח $n$-ממדי של המקבילון שהן span-ות. דטרמיננטה שלילית מציינת שהכיוון של הבסיס מתהפך — ההעתקה "הופכת" את המרחב.

דטרמיננטות מופיעות בכל הקורס: הפולינום האופייני $\\det(A-\\lambda I)=0$ נותן ערכים עצמיים; דטרמיננטת היעקוביאן מחליפה משתנים באינטגרלים מרובי; וב-$\\mathbb{R}^3$, גודל המכפלה הווקטורית קשור לדטרמיננטה $3\\times3$. שליטה בתכונות הדטרמיננטה משתלמת עכשיו בתורת ערכים עצמיים, הופכיות ואלגברה לינארית יישומית.

**קשר לחומר קודם:** חישבתם דטרמיננטות $2\\times2$ כ-$ad-bc$. כאן אנו ממסדים את ההגדרה לכל $n\\times n$ דרך פיתוח לפי מינורים (לפלס) ומפתחים את ארגז הכלים — השפעת פעולות שורה, כפליות וכלל קרמר — שהופך דטרמיננטות לפרקטיות בבחינה.""",
    },
    "definition": {
        "body_en_md": """**Base case ($1\\times1$):** $\\det(a) = a$ for the scalar $a$.

**$2\\times2$ formula:** For $A=\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}$,
$$\\det(A) = ad - bc.$$
This is the signed area of the parallelogram spanned by columns $(a,c)^T$ and $(b,d)^T$.

**Cofactor expansion (Laplace) along row $i$:**
$$\\det(A) = \\sum_{j=1}^n (-1)^{i+j}\\, a_{ij}\\, M_{ij},$$
where $M_{ij}$ is the **minor** — the determinant of the $(n-1)\\times(n-1)$ submatrix obtained by deleting row $i$ and column $j$.

The **cofactor** is $C_{ij} = (-1)^{i+j}M_{ij}$. Then $\\det(A)=\\sum_j a_{ij}C_{ij}$ (row expansion) or $\\det(A)=\\sum_i a_{ij}C_{ij}$ (column expansion).

**Sign checkerboard for $3\\times3$:** $(-1)^{i+j}$ gives the pattern $+ - +$ / $- + -$ / $+ - +$ when expanding along any row or column.

**Example ($3\\times3$, row 1):**
$$\\det\\begin{pmatrix}a&b&c\\\\d&e&f\\\\g&h&i\\end{pmatrix} = a(ei-fh) - b(di-fg) + c(dh-eg).$$

**Key fact:** Expansion along **any** row or column yields the same value — choose the one with the most zeros to minimise arithmetic. For exam speed, always scan before expanding.""",
        "body_he_md": """**מקרה בסיס ($1\\times1$):** $\\det(a) = a$ עבור הסקalar $a$.

**נוסחת $2\\times2$:** עבור $A=\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}$,
$$\\det(A) = ad - bc.$$
זהו השטח המכוון של מקבילית שspan-ות העמודות $(a,c)^T$ ו-$(b,d)^T$.

**פיתוח לפי מינורים (לפלס) לאורך שורה $i$:**
$$\\det(A) = \\sum_{j=1}^n (-1)^{i+j}\\, a_{ij}\\, M_{ij},$$
כאשר $M_{ij}$ הוא ה**מינור** — הדטרמיננטה של תת-המטריצה $(n-1)\\times(n-1)$ המתקבלת בהוצאת שורה $i$ ועמודה $j$.

ה**קופקטור** הוא $C_{ij} = (-1)^{i+j}M_{ij}$. אז $\\det(A)=\\sum_j a_{ij}C_{ij}$ (פיתוח שורה) או $\\det(A)=\\sum_i a_{ij}C_{ij}$ (פיתוח עמודה).

**לוח סימנים ל-$3\\times3$:** $(-1)^{i+j}$ נותן $+ - +$ / $- + -$ / $+ - +$ בפיתוח לפי כל שורה או עמודה.

**דוגמה ($3\\times3$, שורה 1):**
$$\\det\\begin{pmatrix}a&b&c\\\\d&e&f\\\\g&h&i\\end{pmatrix} = a(ei-fh) - b(di-fg) + c(dh-eg).$$

**עובדה מרכזית:** פיתוח לפי **כל** שורה או עמודה נותן אותה תוצאה — בחרו את זו עם הכי הרבה אפסים. לבחינה, סרקו תמיד לפני שמתחילים לפתח.""",
    },
    "theory": {
        "body_en_md": """**Theorem 1 (Row operation effects).** Elementary row operations change $\\det(A)$ predictably:
1. **Swap two rows:** $\\det \\to -\\det$.
2. **Scale a row by $c$:** $\\det \\to c\\cdot\\det$.
3. **Add a multiple of one row to another:** $\\det$ **unchanged**.

*Why (3) matters:* You can row-reduce to upper triangular form **without changing** the determinant (using only operation 3), then read off the product of diagonal entries — after accounting for any swaps and scalings.

**Corollary:** $\\det(A)=0$ if two rows (or columns) are identical, or if any row is all zeros — because such a matrix row-reduces to one with a zero row.

**Theorem 2 (Multiplicativity):** For $n\\times n$ matrices $A,B$,
$$\\det(AB) = \\det(A)\\cdot\\det(B).$$

**Corollary:** If $A$ is invertible, $\\det(A^{-1}) = 1/\\det(A)$. *Proof sketch:* From $AA^{-1}=I$ and $\\det(I)=1$: $\\det(A)\\det(A^{-1})=1$.

**Theorem 3:** $\\det(A^T) = \\det(A)$ — so every row property applies to columns too.

**Theorem 4 (Invertibility criterion):** $A$ is invertible $\\Leftrightarrow$ $\\det(A)\\neq 0$. Equivalently, $\\det(A)=0$ iff the rows (or columns) are linearly dependent.

**Adjugate (classical adjoint) formula for the inverse:**
$$A^{-1} = \\frac{1}{\\det(A)}\\text{adj}(A), \\quad (\\text{adj}(A))_{ij} = C_{ji}.$$

**Cramer's rule** (for $A\\vec{x}=\\vec{b}$, $A$ invertible):
$$x_i = \\frac{\\det(A_i)}{\\det(A)},$$
where $A_i$ is $A$ with column $i$ replaced by $\\vec{b}$. Useful for $2\\times2$ and $3\\times3$ systems on exams; Gaussian elimination is faster for large $n$.""",
        "body_he_md": """**משפט 1 (השפעת פעולות שורה).** פעולות שורה אלמנטריות משנות את $\\det(A)$ בצורה צפויה:
1. **החלפת שתי שורות:** $\\det \\to -\\det$.
2. **הכפלת שורה ב-$c$:** $\\det \\to c\\cdot\\det$.
3. **הוספת כפולה של שורה לאחרת:** $\\det$ **לא משתנה**.

*למה (3) חשוב:* אפשר לדרג לצורה משולשת עליונה **בלי לשנות** דטרמיננטה (רק פעולה 3), ואז לקרוא מכפלת האלכסון — אחרי חשבון החלפות והכפלות.

**מסקנה:** $\\det(A)=0$ אם שתי שורות (או עמודות) זהות, או אם שורה כולה אפסית — כי מטריצה כזו נדרגת לשורת אפס.

**משפט 2 (כפליות):** למטריצות $n\\times n$ $A,B$,
$$\\det(AB) = \\det(A)\\cdot\\det(B).$$

**מסקנה:** אם $A$ הפיכה, $\\det(A^{-1}) = 1/\\det(A)$. *סקיצת הוכחה:* מ-$AA^{-1}=I$ ו-$\\det(I)=1$: $\\det(A)\\det(A^{-1})=1$.

**משפט 3:** $\\det(A^T) = \\det(A)$ — כל תכונת שורה חלה גם על עמודות.

**משפט 4 (קריטריון הפיכות):** $A$ הפיכה $\\Leftrightarrow$ $\\det(A)\\neq 0$. שקivalent: $\\det(A)=0$ אם ורק אם השורות (או העמודות) תלויות לינארית.

**נוסחת הנלווה (adjugate) להופכי:**
$$A^{-1} = \\frac{1}{\\det(A)}\\text{adj}(A), \\quad (\\text{adj}(A))_{ij} = C_{ji}.$$

**כלל קרמר** ($A\\vec{x}=\\vec{b}$, $A$ הפיכה):
$$x_i = \\frac{\\det(A_i)}{\\det(A)},$$
כאשר $A_i$ הוא $A$ עם עמודה $i$ מוחלפת ב-$\\vec{b}$. שימושי ל-$2\\times2$ ו-$3\\times3$ בבחינה; דירוג גausי מהיר יותר ל-$n$ גדול.""",
    },
}


def patch_sections(data: dict) -> None:
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in PATCHES:
            sec.update(PATCHES[kind])

    # worked examples
    for sec in data["sections"]:
        if sec.get("kind") != "worked_example":
            continue
        n = sec.get("example_number")
        if n == 1:
            sec["body_en_md"] = """**Compute** $\\det\\begin{pmatrix}2&1\\\\3&4\\end{pmatrix}$ and interpret the result.

### Move 1 — Apply the $2\\times2$ formula
$$\\det(A) = (2)(4) - (1)(3) = 8 - 3 = 5.$$

### Move 2 — Invertibility
Since $\\det(A)=5\\neq 0$, the matrix is **invertible** (nonsingular). The columns $(2,3)^T$ and $(1,4)^T$ are linearly independent and span a parallelogram of signed area $5$. If $\\det$ were zero, the columns would be parallel.

### Move 3 — Inverse via adjugate
For $2\\times2$, $A^{-1}=\\frac{1}{\\det A}\\begin{pmatrix}d&-b\\\\-c&a\\end{pmatrix}$:
$$A^{-1} = \\frac{1}{5}\\begin{pmatrix}4&-1\\\\-3&2\\end{pmatrix}.$$

### Move 4 — Verify
$$AA^{-1} = \\frac{1}{5}\\begin{pmatrix}2&1\\\\3&4\\end{pmatrix}\\begin{pmatrix}4&-1\\\\-3&2\\end{pmatrix} = \\frac{1}{5}\\begin{pmatrix}5&0\\\\0&5\\end{pmatrix} = I. \\quad \\checkmark$$

**Geometric note:** $|\\det(A)|=5$ is the area of the parallelogram spanned by the column vectors. The inverse scales area by $1/5$. If $\\det$ were zero, the columns would be parallel and no inverse would exist.

**Takeaway:** A quick $2\\times2$ determinant check tells you invertibility before you invest time in finding $A^{-1}$. On exams, compute $\\det$ first whenever a problem asks about singularity or inverse existence."""
            sec["body_he_md"] = """**חשבו** $\\det\\begin{pmatrix}2&1\\\\3&4\\end{pmatrix}$ ופרשו את התוצאה.

### צעד 1 — נוסחת $2\\times2$
$$\\det(A) = (2)(4) - (1)(3) = 8 - 3 = 5.$$

### צעד 2 — הפיכות
מכיוון $\\det(A)=5\\neq 0$, המטריצה **הפיכה** (לא סינגולרית). העמודות $(2,3)^T$ ו-$(1,4)^T$ בלתי-תלויות לינארית וspan-ות מקבילית בשטח מכוון $5$. אם $\\det$ היה אפס, העמודות היו מקבילות.

### צעד 3 — הופכי דרך הנלווה
ל-$2\\times2$, הנוסחה $A^{-1}=\\frac{1}{\\det A}\\begin{pmatrix}d&-b\\\\-c&a\\end{pmatrix}$ נותנת:
$$A^{-1} = \\frac{1}{5}\\begin{pmatrix}4&-1\\\\-3&2\\end{pmatrix}.$$

### צעד 4 — אימות
$$AA^{-1} = \\frac{1}{5}\\begin{pmatrix}2&1\\\\3&4\\end{pmatrix}\\begin{pmatrix}4&-1\\\\-3&2\\end{pmatrix} = I. \\quad \\checkmark$$

**הערה גיאומטרית:** $|\\det(A)|=5$ הוא שטח המקבילית שspan-ות העמודות. ההופכי מכפיל שטח ב-$1/5$. אם $\\det$ היה אפס, העמודות היו מקבילות ולא היה הופכי.

**מסקנה:** בדיקת דטרמיננטה $2\\times2$ מהירה אומרת אם המטריצה הפיכה לפני שמשקיעים זמן ב-$A^{-1}$. בבחינה, חשבו $\\det$ תחילה כששואלים על סינגולריות או על קיום הופכי."""
        elif n == 2:
            sec["body_en_md"] = """**Compute** $\\det\\begin{pmatrix}1&2&3\\\\0&4&5\\\\1&0&6\\end{pmatrix}$.

### Move 1 — Choose the expansion row
Row 2 has a zero at $(2,1)$; row 1 is also efficient. We expand along **row 1** (signs $+ - +$):
$$\\det = 1\\cdot\\det\\begin{pmatrix}4&5\\\\0&6\\end{pmatrix} - 2\\cdot\\det\\begin{pmatrix}0&5\\\\1&6\\end{pmatrix} + 3\\cdot\\det\\begin{pmatrix}0&4\\\\1&0\\end{pmatrix}.$$

### Move 2 — Evaluate $2\\times2$ minors
$$= 1(24-0) - 2(0-5) + 3(0-4) = 24 + 10 - 12 = 22.$$

### Move 3 — Cross-check via row 2
Along row 2 (zero at $(2,1)$): only $(2,2)=4$ and $(2,3)=5$ contribute:
$$= +4\\cdot\\det\\begin{pmatrix}1&3\\\\1&6\\end{pmatrix} - 5\\cdot\\det\\begin{pmatrix}1&2\\\\1&0\\end{pmatrix} = +4(3) - 5(-2) = 12 + 10 = 22. \\quad \\checkmark$$

### Move 4 — Interpret
$\\det=22\\neq 0$, so the matrix is invertible. The three column vectors span a full $3$-dimensional volume of signed magnitude $22$. You could also row-reduce to triangular form (using only type-3 row ops) as an alternative check.

**Strategy tip:** When a row/column has zeros, expand there. Mark the checkerboard $(-1)^{i+j}$ before computing minors — sign errors are the #1 cause of wrong $3\\times3$ answers. Both row 1 and row 2 expansions confirm **22**."""
            sec["body_he_md"] = """**חשבו** $\\det\\begin{pmatrix}1&2&3\\\\0&4&5\\\\1&0&6\\end{pmatrix}$.

### צעד 1 — בחירת שורת פיתוח
לשורה 2 יש אפס ב-$(2,1)$, אך נפתח לפי **שורה 1** לתרגול מלא של לוח הסימנים:
$$\\det = 1\\cdot\\det\\begin{pmatrix}4&5\\\\0&6\\end{pmatrix} - 2\\cdot\\det\\begin{pmatrix}0&5\\\\1&6\\end{pmatrix} + 3\\cdot\\det\\begin{pmatrix}0&4\\\\1&0\\end{pmatrix}.$$

### צעד 2 — חישוב מינורים $2\\times2$
$$= 1(24) - 2(-5) + 3(-4) = 24 + 10 - 12 = 22.$$
**זהירות:** סימן $(1,2)$ הוא $(-1)^{1+2}=-1$, ולכן $-2\\cdot(-5)=+10$, לא $-10$.

### צעד 3 — בדיקה לפי שורה 2
לפי שורה 2 (אפס ב-$(2,1)$): רק $(2,2)=4$ ו-$(2,3)=5$ תורמים:
$$= +4(6-3) - 5(0-2) = 12 + 10 = 22. \\quad \\checkmark$$

### צעד 4 — פרשנות
$\\det=22\\neq 0$, ולכן המטריצה הפיכה לחלוטין. שלוש העמודות span-ות נפח $3$-ממדי מלא בגודל $22$. אפשר גם לדרג לצורה משולשת (רק פעולות מסוג 3) כבדיקה חלופית.

**עצה:** כשיש אפסים, פתחו לפי אותה שורה/עמודה. סמנו לוח $(-1)^{i+j}$ לפני חישוב — טעויות סימן הן הסיבה #1 לתשובות שגויות בבחינה. שני הפיתוחים השונים מאשרים תמיד **22**."""
        elif n == 3:
            sec["body_en_md"] = sec["body_en_md"]  # keep EN, already OK length
            sec["body_he_md"] = """**טענה:** אם $A$ מטריצה $n\\times n$ הפיכה, אז $\\det(A^{-1}) = \\dfrac{1}{\\det(A)}$.

**הוכחה:**

### צעד 1 — הגדרת ההופכי
מכיוון $A$ הפיכה, קיים $A^{-1}$ עם $AA^{-1}=I_n$.

### צעד 2 — כפליות
$$\\det(AA^{-1}) = \\det(A)\\cdot\\det(A^{-1}).$$
לפי משפט 2, כפל הדטרמיננטות שווה לדטרמיננטה של המכפלה.

### צעד 3 — דטרמיננטת היחידה
$\\det(I_n)=1$ — מכפלת הכניסות האלכסוניות של מטריצת היחידה.

### צעד 4 — הצבה
$\\det(A)\\cdot\\det(A^{-1}) = 1$.

### צעד 5 — מסקנה
מכיוון $A$ הפיכה, $\\det(A)\\neq 0$. מחלקים:
$$\\det(A^{-1}) = \\frac{1}{\\det(A)}. \\quad \\blacksquare$$

**מסקנה (אינדוקציה):** $\\det(A^n)=(\\det A)^n$ לכל $n$ טבעי. בסיס $n=1$ טריוויאלי; השלב משתמש ב-$\\det(A^{n+1})=\\det(A^n)\\det(A)$. יחד עם $\\det(A^{-1})=1/\\det A$, אפשר לפשט כל ביטוי עם חזקות והופכים.

**למה זה חשוב:** שאלות על $\\det(AB^{-1}A^T)$ לא דורשות כפל מטריצות — רק כפליות ו-$\\det(A^T)=\\det A$. תבנית הוכחה זו מופיעה בכמעט כל בחינת אלגברה לינארית באוניברסיטה בישראל."""
            if wc(sec["body_en_md"]) < 130:
                sec["body_en_md"] = """**Claim:** If $A$ is an invertible $n\\times n$ matrix, then $\\det(A^{-1}) = \\dfrac{1}{\\det(A)}$.

**Proof:**

### Move 1 — Definition of inverse
Since $A$ is invertible, there exists $A^{-1}$ with $AA^{-1}=I_n$.

### Move 2 — Apply multiplicativity (Theorem 2)
$$\\det(AA^{-1}) = \\det(A)\\cdot\\det(A^{-1}).$$
Multiplicativity lets us split the determinant of a product into a product of determinants.

### Move 3 — Determinant of identity
$\\det(I_n)=1$ because $I_n$ is diagonal with ones on the diagonal.

### Move 4 — Substitute
$\\det(A)\\cdot\\det(A^{-1}) = \\det(I_n) = 1$.

### Move 5 — Conclude
Since $A$ is invertible, $\\det(A)\\neq 0$ (Theorem 4). Divide both sides:
$$\\det(A^{-1}) = \\frac{1}{\\det(A)}. \\quad \\blacksquare$$

**Corollary (by induction):** $\\det(A^n)=(\\det A)^n$ for every positive integer $n$. Base $n=1$ is trivial; the step uses $\\det(A^{n+1})=\\det(A^n)\\det(A)$. Combined with $\\det(A^{-1})=1/\\det A$, you can simplify any expression involving powers and inverses.

**Why it matters:** Questions asking for $\\det(AB^{-1}A^T)$ never require explicit matrix multiplication — only multiplicativity and $\\det(A^T)=\\det A$. This proof template appears on virtually every university linear algebra exam."""

    # checkpoints
    cp_idx = 0
    for sec in data["sections"]:
        if sec.get("kind") != "checkpoint":
            continue
        cp_idx += 1
        if cp_idx == 1:
            sec["checkpoint_solution_en"] = """### Move 1 — Determinant
$$\\det\\begin{pmatrix}5&-2\\\\3&1\\end{pmatrix} = (5)(1) - (-2)(3) = 5 + 6 = 11.$$

### Move 2 — Invertibility
$\\det=11\\neq 0$, so $A$ is invertible.

### Move 3 — Inverse
$$A^{-1} = \\frac{1}{11}\\begin{pmatrix}1&2\\\\-3&5\\end{pmatrix}.$$

**Verify:** $(5)(1/11)+(-2)(-3/11)=5/11+6/11=11/11=1$ ✓"""
            sec["checkpoint_solution_he"] = """### צעד 1 — דטרמיננטה
$$\\det = (5)(1) - (-2)(3) = 5 + 6 = 11.$$

### צעד 2 — הפיכות
$\\det=11\\neq 0$, ולכן $A$ הפיכה.

### צעד 3 — הופכי
$$A^{-1} = \\frac{1}{11}\\begin{pmatrix}1&2\\\\-3&5\\end{pmatrix}.$$

**אימות:** $(5)(1/11)+(-2)(-3/11)=1$ ✓"""
        elif cp_idx == 2:
            sec["checkpoint_solution_en"] = """**Best choice:** Expand along row 1 (contains a zero at $(1,2)$).

$$\\det = 2\\cdot\\det\\begin{pmatrix}1&-1\\\\2&4\\end{pmatrix} - 0 + 1\\cdot\\det\\begin{pmatrix}3&1\\\\0&2\\end{pmatrix}.$$

$$= 2(4+2) + 1(6-0) = 12 + 6 = 18.$$

**Check:** Row 3 has no zeros, so row 1 is more efficient. Sign on $(1,3)$: $(-1)^{1+3}=+1$. ✓"""
            sec["checkpoint_solution_he"] = """**בחירה:** פיתוח לפי שורה 1 (יש אפס ב-$(1,2)$).

$$\\det = 2(4+2) + 1(6-0) = 12 + 6 = 18.$$

**בדיקה:** סימן $(1,3)$: $(-1)^{1+3}=+1$. שורה 3 ללא אפסים — שורה 1 יעילה יותר. ✓"""

    # method_guide, pitfall, why_matters, before_exam, summary
    for sec in data["sections"]:
        k = sec.get("kind")
        if k == "method_guide":
            sec["body_en_md"] = """**Step 1 — Size check:** Confirm the matrix is square ($n\\times n$). Determinants are undefined for non-square matrices.

**Step 2 — Choose your tool:**

| Goal | Method |
|---|---|
| $2\\times2$ det | $ad-bc$ directly |
| $3\\times3$ det | Cofactor expansion; pick row/col with most zeros |
| $n\\times n$ with structure | Row-reduce to triangular (track swaps & scalings) |
| Show $A$ invertible | Prove $\\det(A)\\neq 0$ |
| $\\det(AB)$, $\\det(A^{-1})$ | Multiplicativity — never expand full matrices |
| $\\det(cA)$ for $n\\times n$ | $c^n\\det(A)$, **not** $c\\det(A)$ |
| Solve $A\\vec{x}=\\vec{b}$ (small) | Cramer's rule: $x_i=\\det(A_i)/\\det(A)$ |

**Step 3 — Row-operation shortcuts:** Swap $\\Rightarrow$ multiply det by $-1$. Scale row by $c$ $\\Rightarrow$ multiply det by $c$. Add multiple of row $\\Rightarrow$ det unchanged.

**Step 4 — Sanity checks:** Upper/lower triangular $\\Rightarrow$ det = product of diagonal. Two equal rows $\\Rightarrow$ det $=0$. Verify $\\det(A^T)=\\det(A)$ when recomputing."""
            sec["body_he_md"] = """**צעד 1 — בדיקת גודל:** ודאו שהמטריצה ריבועית ($n\\times n$). דטרמיננטות לא מוגדרות למטריצות לא-ריבועיות.

**צעד 2 — בחרו כלי:**

| מטרה | שיטה |
|---|---|
| דט' $2\\times2$ | $ad-bc$ ישירות |
| דט' $3\\times3$ | פיתוח מינורים; שורה/עמודה עם הכי הרבה אפסים |
| $n\\times n$ עם מבנה | דירוג למשולש (עקבו החלפות והכפלות) |
| הראה $A$ הפיכה | הוכיחו $\\det(A)\\neq 0$ |
| $\\det(AB)$, $\\det(A^{-1})$ | כפליות — אל תפתחו מטריצות מלאות |
| $\\det(cA)$ | $c^n\\det(A)$, **לא** $c\\det(A)$ |
| פתרון $A\\vec{x}=\\vec{b}$ (קטן) | כלל קרמר: $x_i=\\det(A_i)/\\det(A)$ |

**צעד 3 — קיצורי פעולות שורה:** החלפה $\\Rightarrow$ כפל ב-$-1$. הכפלת שורה ב-$c$ $\\Rightarrow$ כפל ב-$c$. הוספת כפולה $\\Rightarrow$ ללא שינוי.

**צעד 4 — בדיקות שפיות:** משולש $\\Rightarrow$ דט' = מכפלת אלכסון. שתי שורות שוות $\\Rightarrow$ דט'$=0$. $\\det(A^T)=\\det(A)$."""
        elif k == "pitfall":
            sec["body_en_md"] = """1. **Sign errors in cofactor expansion.** The checkerboard $(-1)^{i+j}$ is non-negotiable. For $3\\times3$ along row 1: $+ - +$. A single sign flip changes the entire answer.

2. **$\\det(A+B) \\neq \\det(A)+\\det(B)$.** Determinants are multiplicative, not additive. This false rule is the most common conceptual error on exams.

3. **$\\det(cA) = c\\det(A)$ is WRONG for $n>1$.** Correct: $\\det(cA) = c^n\\det(A)$ because each of $n$ rows is scaled by $c$, contributing a factor $c$ per row.

4. **Forgetting sign flips when swapping rows.** Every row swap multiplies $\\det$ by $-1$. When row-reducing to triangular form, count swaps explicitly.

5. **Using Cramer's rule when $\\det(A)=0$.** Cramer's rule requires an invertible matrix. If $\\det(A)=0$, the system is either inconsistent or has infinitely many solutions — use RREF instead.

6. **Expanding along the wrong row.** Always scan for the row or column with the most zeros before committing to arithmetic."""
            sec["body_he_md"] = """1. **שגיאות סימן בפיתוח מינורים.** לוח השחמט $(-1)^{i+j}$ אינו ניתן לפשרה. ל-$3\\times3$ לאורך שורה 1: $+ - +$. טעות סימן אחת משנה את כל התשובה.

2. **$\\det(A+B) \\neq \\det(A)+\\det(B)$.** דטרמיננטות כפליות, לא אדיטיביות. זו הטעות הקונסепטואלית הנפוצה ביותר בבחינה.

3. **$\\det(cA) = c\\det(A)$ — שגוי ל-$n>1$.** נכון: $\\det(cA) = c^n\\det(A)$ כי כל $n$ שורות מוכפלות ב-$c$.

4. **שכחת שינוי סימן בהחלפת שורות.** כל החלפת שורות מכפילה $\\det$ ב-$-1$. בדירוג למשולש, ספרו החלפות במפורש.

5. **שימוש בכלל קרמר כש-$\\det(A)=0$.** כלל קרמר דורש מטריצה הפיכה. אם $\\det(A)=0$, השתמשו ב-RREF.

6. **פיתוח לפי שורה לא נכונה.** סרקו תמיד את השורה/עמודה עם הכי הרבה אפסים לפני שמתחילים."""
        elif sec.get("id") == "why_matters" or (k == "why_matters"):
            sec["body_en_md"] = """Determinants are the bridge between **geometry** and **algebra** in linear algebra — they quantify how a matrix transforms volume and orientation.

**Eigenvalues:** The characteristic equation $\\det(A-\\lambda I)=0$ is the standard route to eigenvalues. Every diagonalization problem starts with a determinant.

**Invertibility:** $\\det(A)\\neq 0$ is the fastest invertibility test for small matrices and underpins the rank-nullity connection.

**Builds on:** `concept:la_matrices` **Matrices** and `concept:la_vectors` **Vectors**.

**Unlocks:** `concept:la_eigenvalues` **Eigenvalues**, `concept:la_diagonalization` **Diagonalization**, and multivariable calculus (Jacobian determinants).

**Exam transfer:** Israeli university linear algebra exams routinely ask for $3\\times3$ determinant computation, multiplicativity proofs, and Cramer's rule on $2\\times2$ systems — often under time pressure."""
            sec["body_he_md"] = """דטרמיננטות הן הגשר בין **גיאומטריה** ל**אלגברה** באלגברה לינארית — הן מכמתות כיצד מטריצה משנה נפח וכיוון.

**ערכים עצמיים:** המשוואה $\\det(A-\\lambda I)=0$ היא הנתיב הסטנדרטי לערכים עצמיים. כל בעיית אלכסון מתחילה בדטרמיננטה.

**הפיכות:** $\\det(A)\\neq 0$ הוא בדיקת ההפיכות המהירה ביותר למטריצות קטנות ותומך בקשר rank-nullity.

**מבוסס על:** `concept:la_matrices` **מטריצות** ו-`concept:la_vectors` **וקטורים**.

**פותח:** `concept:la_eigenvalues` **ערכים עצמיים**, `concept:la_diagonalization` **אלכסון**, וחדו-משתני (דטרמיננטות יעקוביאן).

**העברה לבחינה:** בחינות אלגברה לינארית באוניברסיטה בישראל שואלות שגרתית על דטרמיננטות $3\\times3$, הוכחות כפליות וכלל קרמר על מערכות $2\\times2$ — לעיתים תחת לחץ זמן."""
        elif k == "before_exam":
            sec["body_he_md"] = """**גיליון נוסחאות:**
- $2\\times2$: $\\det = ad-bc$
- $3\\times3$: פיתוח לפי שורה עם אפסים; סימנים $(-1)^{i+j}$
- $\\det(AB)=\\det A\\cdot\\det B$
- $\\det(A^T)=\\det A$
- $\\det(A^{-1})=1/\\det A$
- $\\det(cA)=c^n\\det A$ (לא $c\\det A$!)
- החלפת שורות: $\\det\\to-\\det$; הכפלת שורה ב-$c$: $\\det\\to c\\cdot\\det$; הוספת כפולה: ללא שינוי
- כלל קרמר: $x_i=\\det(A_i)/\\det(A)$

**מה בחינות אוניברסיטאיות ישראליות מדגישות:**
- חישוב דטרמיננטות $3\\times3$ עם פרמטרים.
- הוכחת תכונות דרך כפליות ($\\det(A^n)$, $\\det(A^{-1})$).
- מציאת ערכים עצמיים מ-$\\det(A-\\lambda I)=0$.
- קביעת הפיכות ופתרון מערכות בכלל קרמר.

**טיפ לבחינה:** כשיש כניסת אפס, פתחו לפי אותה שורה/עמודה — חוסך שליש מהחישוב. סמנו לוח סימנים לפני שמתחילים."""
        elif k == "summary":
            sec["body_en_md"] = """- **Definition:** $\\det(A)$ via cofactor expansion along any row/column; $2\\times2$: $ad-bc$.
- **Row operations:** swap $\\Rightarrow$ sign flip; scale by $c$ $\\Rightarrow$ multiply det by $c$; add multiple $\\Rightarrow$ unchanged.
- **Multiplicativity:** $\\det(AB)=\\det A\\cdot\\det B$; $\\det(A^{-1})=1/\\det A$; $\\det(A^T)=\\det A$; $\\det(cA)=c^n\\det A$.
- **Invertibility:** $A$ invertible $\\Leftrightarrow$ $\\det(A)\\neq 0$.
- **Cramer's rule:** $x_i=\\det(A_i)/\\det(A)$ for invertible $A$.
- **Adjugate inverse:** $A^{-1}=\\frac{1}{\\det A}\\text{adj}(A)$.

**Takeaway:** For any square matrix, you should compute its determinant efficiently, use properties to simplify products like $\\det(2AB^{-1}A^T)$ without expanding, and apply Cramer's rule when appropriate."""
            sec["body_he_md"] = """- **הגדרה:** $\\det(A)$ דרך פיתוח מינורים; $2\\times2$: $ad-bc$.
- **פעולות שורה:** החלפה $\\Rightarrow$ שינוי סימן; הכפלה ב-$c$ $\\Rightarrow$ כפל ב-$c$; הוספת כפולה $\\Rightarrow$ ללא שינוי.
- **כפליות:** $\\det(AB)=\\det A\\cdot\\det B$; $\\det(A^{-1})=1/\\det A$; $\\det(A^T)=\\det A$; $\\det(cA)=c^n\\det A$.
- **הפיכות:** $A$ הפיכה $\\Leftrightarrow$ $\\det(A)\\neq 0$.
- **כלל קרמר:** $x_i=\\det(A_i)/\\det(A)$.
- **הופכי נלווה:** $A^{-1}=\\frac{1}{\\det A}\\text{adj}(A)$.

**מסקנה:** לכל מטריצה ריבועית, אתם אמורים לחשב דטרמיננטה ביעילות, להשתמש בתכונות לפישוט $\\det(2AB^{-1}A^T)$ בלי פיתוח, וליישם כלל קרמר כשמתאים."""


EXPL = [
    fmt_expl(
        "Apply the $2\\times2$ formula: $\\det = (6)(1)-(2)(3)=6-6=0$. By Theorem 4, $\\det(A)=0$ means $A$ is **singular** (not invertible). The columns $(6,3)^T$ and $(2,1)^T$ are parallel — one is $2$ times the other — so the parallelogram they span has zero area.",
        "For a $2\\times2$ determinant question, compute $ad-bc$ first, then immediately state invertibility: $\\det\\neq 0$ $\\Leftrightarrow$ invertible. Do not stop at the number alone when the question asks about invertibility.",
        "Computing $6-2=4$ or $6+6=12$ by mixing up the formula as $ad+bc$. Another slip: saying 'invertible' when $\\det=0$.",
        "On $2\\times2$ problems, write 'det = ad-bc = ...' as your first line — examiners award method marks before the final number.",
        "נוסחת $2\\times2$: $\\det = (6)(1)-(2)(3)=6-6=0$. לפי משפט 4, $\\det(A)=0$ פירושו **סינגולרית** (לא הפיכה). העמודות $(6,3)^T$ ו-$(2,1)^T$ מקבילות — אחת כפולה של השנייה — ולכן שטח המקבילית אפס.",
        "בשאלת דטרמיננטה $2\\times2$, חשבו $ad-bc$ ומיד ציינו הפיכות: $\\det\\neq 0$ $\\Leftrightarrow$ הפיכה. אל תעצרו במספר כששואלים על הפיכות.",
        "חישוב $6-2=4$ או $6+6=12$ בגלל נוסחה שגויה $ad+bc$. טעות: 'הפיכה' כש-$\\det=0$.",
        "ב-$2\\times2$, כתבו 'דט' = ad-bc = ...' כשורה ראשונה — נקודות שיטה לפני המספר הסופי.",
    ),
    fmt_expl(
        "Rows satisfy $R_2-R_1=(3,3,3)$ and $R_3-R_2=(3,3,3)$, so $R_3=2R_2-R_1$. The three rows are linearly dependent, meaning the column vectors do not span a full $3$-dimensional volume. By Theorem 4, a dependent set of rows forces $\\det(A)=0$ — no full cofactor expansion needed.",
        "Before expanding a $3\\times3$ determinant, scan for linear relations among rows. Row differences that are proportional reveal dependence instantly. This 'structural zero' shortcut saves minutes on exams.",
        "Attempting full cofactor expansion and making arithmetic errors along the way, when a one-line dependence argument suffices. Another slip: claiming two rows are equal when they are only proportional.",
        "When a problem says 'without computing the full determinant,' they reward structural reasoning — write the row relation explicitly: $R_3=2R_2-R_1$ $\\Rightarrow$ $\\det=0$.",
        "השורות מקיימות $R_2-R_1=(3,3,3)$ ו-$R_3-R_2=(3,3,3)$, ולכן $R_3=2R_2-R_1$. שלוש השורות תלויות לינארית, כלומר העמודות לא span-ות נפח $3$-ממדי מלא. לפי משפט 4, תלות שורות $\\Rightarrow$ $\\det(A)=0$ — בלי פיתוח מינורים מלא.",
        "לפני פיתוח $3\\times3$, סרקו יחסים לינאריים בין שורות. הפרשי שורות פרופורציונליים חושפים תלות מיד. קיצור 'אפס מבני' חוסך דקות בבחינה.",
        "פיתוח מינורים מלא עם טעויות חשבון, כשטיעון תלות בשורה אחת מספיק. טעות: 'שורות שוות' כשהן רק פרופורציונליות.",
        "כש'מבלי לחשב את הדטרמיננטה במלואה', מעריכים היגיון מבני — כתבו $R_3=2R_2-R_1$ $\\Rightarrow$ $\\det=0$.",
    ),
    fmt_expl(
        "For an $n\\times n$ matrix, scaling every entry by $c$ scales each of $n$ rows by $c$. By Theorem 1(2), each row scaling multiplies $\\det$ by $c$, giving $\\det(cA)=c^n\\det(A)$. Here $n=3$ and $\\det(A)=3$: $\\det(2A)=2^3\\cdot 3=8\\cdot 3=24$.",
        "Identify the scalar factor outside the matrix and the dimension $n$ first. The exponent on the scalar is always the matrix size — this is the single most tested determinant property after the $2\\times2$ formula.",
        "Using $\\det(2A)=2\\det(A)=6$ (forgetting the exponent $n$). This error is especially common when students confuse $\\det(cA)$ with $\\det(cI)=c^n$.",
        "Write the template $\\det(cA)=c^n\\det(A)$ before substituting numbers — one line prevents the $c$ vs $c^n$ trap.",
        "למטריצה $n\\times n$, הכפלת כל כניסה ב-$c$ מכפילה כל $n$ שורות ב-$c$. לפי משפט 1(2), $\\det(cA)=c^n\\det(A)$. כאן $n=3$ ו-$\\det(A)=3$: $\\det(2A)=2^3\\cdot 3=24$.",
        "זהו תחילה את גורם הכפל ואת $n$. המעריך על הסקalar תמיד גודל המטריצה — התכונה הנבחנת ביותר אחרי נוסחת $2\\times2$.",
        "$\\det(2A)=2\\det(A)=6$ (שכחת המעריך $n$). טעות נפוצה במיוחד.",
        "כתבו $\\det(cA)=c^n\\det(A)$ לפני הצבה — שורה אחת מונעת מלכודת $c$ לעומת $c^n$.",
    ),
    fmt_expl(
        "Write the system as $A\\vec{x}=\\vec{b}$ with $A=\\begin{pmatrix}3&1\\\\1&2\\end{pmatrix}$, $\\vec{b}=(7,4)^T$. $\\det A=6-1=5\\neq 0$. Replace column 1 with $\\vec{b}$: $\\det A_1=14-4=10$, so $x=10/5=2$. Replace column 2: $\\det A_2=12-7=5$, so $y=5/5=1$.",
        "Cramer's rule requires three determinants for a $2\\times2$ system: $\\det A$, $\\det A_1$ (column 1 replaced by $\\vec{b}$), and $\\det A_2$. Build each matrix explicitly before computing — do not confuse which column to replace.",
        "Replacing the wrong column when forming $A_i$. Another slip: computing $\\det A$ correctly but forgetting to check $\\det A\\neq 0$ before applying Cramer's rule.",
        "Verify by substitution: $3(2)+1=7$ ✓ and $2+2(1)=4$ ✓. Always substitute back — catches sign errors in $\\det A_i$.",
        "כתבו $A\\vec{x}=\\vec{b}$ עם $A=\\begin{pmatrix}3&1\\\\1&2\\end{pmatrix}$, $\\vec{b}=(7,4)^T$. $\\det A=6-1=5\\neq 0$, ולכן כלל קרמר חל. $\\det A_1=\\det\\begin{pmatrix}7&1\\\\4&2\\end{pmatrix}=14-4=10$, ולכן $x=10/5=2$. $\\det A_2=\\det\\begin{pmatrix}3&7\\\\1&4\\end{pmatrix}=12-7=5$, ולכן $y=5/5=1$.",
        "כלל קרמר דורש שלוש דטרמיננטות ל-$2\\times2$: $\\det A$, $\\det A_1$ (עמודה 1 מוחלפת ב-$\\vec{b}$), $\\det A_2$ (עמודה 2 מוחלפת). בנו כל מטריצה במפורש לפני חישוב — אל תבלבלו איזו עמודה להחליף.",
        "החלפת עמודה שגויה ב-$A_i$ — למשל החלפת שורה במקום עמודה. טעות נוספת: $\\det A$ נכון אבל שימוש בקרמר כש-$\\det A=0$.",
        "אמתו בהצבה: $3(2)+1(1)=7$ ✓ ו-$1(2)+2(1)=4$ ✓. הצבה חוזרת תופסת טעויות סימן ב-$\\det A_i$ ומבטיחה נקודות מלאות.",
    ),
    fmt_expl(
        "Row 1 has a zero at $(1,3)$, making it the best expansion row. $\\det = 2\\cdot\\det\\begin{pmatrix}3&-1\\\\2&1\\end{pmatrix} -(-1)\\cdot\\det\\begin{pmatrix}1&-1\\\\0&1\\end{pmatrix}+0 = 2(3+2)+1(1-0)=10+1=11$.",
        "Scan all rows and columns for zeros before expanding. Each zero eliminates one $2\\times2$ minor computation. Mark the sign pattern $+ - +$ along your chosen row before evaluating minors.",
        "Sign error on the $(1,2)$ term: using $-(-1)\\cdot(...)=-1$ instead of $+1$. Another slip: expanding along row 3 (no zeros) and doing three times the work.",
        "For $3\\times3$ determinants, write 'expand along row $i$ (has zero at ...)' as your first line — shows the examiner you chose efficiently.",
        "לשורה 1 יש אפס ב-$(1,3)$ — שורת הפיתוח הטובה ביותר. $\\det = 2\\cdot\\det\\begin{pmatrix}3&-1\\\\2&1\\end{pmatrix} + 1\\cdot\\det\\begin{pmatrix}1&-1\\\\0&1\\end{pmatrix} = 2(3+2)+1(1-0)=10+1=11$. סימן $(1,2)$: $(-1)^{1+2}=-1$, ולכן $-(-1)(1)=+1$.",
        "סרקו כל שורות ועמודות לאפסים לפני פיתוח. כל אפס מבטל חישוב מינור $2\\times2$ אחד וחוסך זמן. סמנו לוח סימנים $+ - +$ לאורך השורה הנבחרת לפני שמתחילים לחשב.",
        "טעות סימן על $(1,2)$: כתיבת $-(-1)(\\ldots)=-1$ במקום $+1$. טעות נוספת: פיתוח לפי שורה 3 (ללא אפסים) ושלושה מינורים במקום שניים.",
        "ב-$3\\times3$, כתבו 'פיתוח לפי שורה $i$ (אפס ב-$(i,j)$)' כשורה ראשונה — מראה לבוחן שבחרתם ביעילות ומזכה בנקודות שיטה.",
    ),
    fmt_expl(
        "Apply $\\det(cA)=c^n\\det(A)$, multiplicativity, $\\det(A^{-1})=1/\\det(A)$, and $\\det(A^T)=\\det(A)$ step by step: $\\det(2AB^{-1}A^T)=2^3\\cdot\\det(A)\\cdot\\det(B^{-1})\\cdot\\det(A^T)=8\\cdot 4\\cdot(1/3)\\cdot 4=128/3$.",
        "Never expand $AB^{-1}A^T$ as a single matrix. Decompose into scalar power ($2^3$), then each factor's determinant. Order does not matter for multiplication of scalars.",
        "Using $\\det(B^{-1})=\\det(B)=3$ instead of $1/3$. Forgetting $2^3$ and writing $2\\cdot 4\\cdot(1/3)\\cdot 4=32/3$. Confusing $\\det(A^T)$ with $1/\\det(A)$.",
        "Write a chain: $\\det(2AB^{-1}A^T)=2^3\\det(A)\\det(B^{-1})\\det(A^T)=...$ — each step is one line, easy to spot errors.",
        "יישמו $\\det(cA)=c^n\\det(A)$, כפליות, $\\det(A^{-1})=1/\\det(A)$ ו-$\\det(A^T)=\\det(A)$: $\\det(2AB^{-1}A^T)=2^3\\cdot\\det(A)\\cdot\\det(B^{-1})\\cdot\\det(A^T)=8\\cdot 4\\cdot(1/3)\\cdot 4=128/3$. כל שלב הוא כפל סקalars — אין צורך לחשב $B^{-1}$ במפורש.",
        "אל תפתחו $AB^{-1}A^T$ כמטריצה $3\\times3$ אחת. פרקו לגורם $2^3$, ואז דטרמיננטה של כל גורם בנפרד. סדר הכפל לא משנה כי מדובר בכפל מספרים.",
        "$\\det(B^{-1})=\\det(B)=3$ במקום $1/3$ — הטעות הנפוצה ביותר. שכחת $2^3$ וכתיבת $2\\cdot 4\\cdot(1/3)\\cdot 4=32/3$. בלבול $\\det(A^T)$ עם $1/\\det(A)$.",
        "כתבו שרשרת: $\\det(2AB^{-1}A^T)=2^3\\det(A)\\det(B^{-1})\\det(A^T)=8\\cdot 4\\cdot(1/3)\\cdot 4=128/3$ — כל שלב בשורה, קל לזהות טעויות לפני שמסיימים.",
    ),
    fmt_expl(
        "Form $A-\\lambda I=\\begin{pmatrix}3-\\lambda&1\\\\1&3-\\lambda\\end{pmatrix}$. $\\det(A-\\lambda I)=(3-\\lambda)^2-1=\\lambda^2-6\\lambda+8=(\\lambda-2)(\\lambda-4)=0$. Roots: $\\lambda=2$ and $\\lambda=4$. These are eigenvalues — the topic where determinants become polynomials.",
        "Setting $\\det(A-\\lambda I)=0$ converts a matrix problem into a quadratic (for $2\\times2$). Expand carefully: $(3-\\lambda)^2-1$, not $(3-\\lambda)^2+1$.",
        "Sign error: $(3-\\lambda)^2+1$ instead of $-1$. Finding only one root and stopping. Forgetting this equation defines eigenvalues, not just 'solve for lambda'.",
        "After factoring, verify: tr$(A)=6=2+4$ ✓ and $\\det(A)=8=2\\cdot 4$ ✓. Trace and determinant checks catch polynomial errors instantly.",
        "בנו $A-\\lambda I=\\begin{pmatrix}3-\\lambda&1\\\\1&3-\\lambda\\end{pmatrix}$. $\\det(A-\\lambda I)=(3-\\lambda)^2-1=\\lambda^2-6\\lambda+8=(\\lambda-2)(\\lambda-4)=0$. שורשים: $\\lambda=2$ ו-$\\lambda=4$. אלו ערכים עצמיים — הנושא שבו דטרמיננטות הופכות לפולינום ב-$\\lambda$.",
        "הצבת $\\det(A-\\lambda I)=0$ הופכת בעיית מטריצה לריבועית (ב-$2\\times2$). פתחו $(3-\\lambda)^2-1$ בזהירות — לא $(3-\\lambda)^2+1$. זהו הפולינום האופייני $p(\\lambda)$.",
        "סימן שגוי: $(3-\\lambda)^2+1$ במקום $-1$. מציאת שורש אחד בלבד והפסקה. שכחה שמשוואה זו מגדירה ערכים עצמיים, לא רק 'פתרון ל-$\\lambda$'.",
        "אחרי פירוק, אמתו: tr$(A)=6=2+4$ ✓ ו-$\\det(A)=8=2\\cdot 4$ ✓. בדיקות עקבה ודטרמיננטה תופסות טעויות בפולינום מיד.",
    ),
    fmt_expl(
        "The matrix is almost upper triangular with a single off-diagonal entry $5$ at $(1,4)$. Expand along column 1 (one nonzero entry): $\\det = 1\\cdot\\det\\begin{pmatrix}2&0&0\\\\0&3&0\\\\0&0&4\\end{pmatrix}=1\\cdot 2\\cdot 3\\cdot 4=24$. The $(1,4)$ entry contributes via row 1: $5\\cdot(-1)^{1+4}M_{14}$, but $M_{14}$ has a zero column so its det is $0$. Answer: **24**.",
        "For nearly-triangular matrices, expand along the sparsest row or column. Do not assume 'almost triangular' means product of diagonal — off-diagonal entries matter only if their minor is nonzero.",
        "Getting $-96$ by mishandling column-4 expansion signs. Assuming $\\det=1\\cdot 2\\cdot 3\\cdot 4=24$ without checking whether off-diagonal entries contribute (here the $(1,4)$ minor vanishes, so $24$ is correct).",
        "When you see mostly zeros, identify the row/column with fewest nonzeros first. Write which entries contribute before computing — prevents sign and minor errors.",
        "המטריצה כמעט משולשת עליונה עם כניסה $5$ ב-$(1,4)$. פיתוח לפי עמודה 1: $\\det = 1\\cdot 2\\cdot 3\\cdot 4=24$. תרומת $(1,4)$ דרך $M_{14}$ עם עמודת אפס — דטרמיננטה $0$. תשובה: **24**.",
        "למטריצות כמעט-משולשות, פתחו לפי השורה/עמודה הדלילה ביותר. 'כמעט משולש' לא אומר מכפלת אלכסון — כניסות מחוץ לאלכסון משפיעות רק אם המינור לא אפס.",
        "קבלת $-96$ בטעות סימן. הנחה $\\det=24$ בלי לבדוק תרומת $(1,4)$ (כאן המינור מתאפס — $24$ נכון).",
        "כשיש בעיקר אפסים, זהו שורה/עמודה עם הכי מעט כניסות. כתבו אילו כניסות תורמות לפני חישוב.",
    ),
]


def patch_questions(data: dict) -> None:
    for i, q in enumerate(data["questions"]):
        en, he = EXPL[i]
        q["explanation_en"] = en
        q["explanation_he"] = he
    # fix Q8 acceptable answers (det = 24, not -96)
    q8 = data["questions"][7]
    q8["answer_payload"]["acceptable_answers"] = [
        "Expand along column 1: $\\det = 1\\cdot 2\\cdot 3\\cdot 4 = 24$",
        "24",
        "24$",
    ]


def patch_exercises(data: dict) -> None:
    for sec in data["sections"]:
        if sec.get("kind") != "exercise_set":
            continue
        for ex in sec.get("exercises", []):
            if ex["id"] == "e8":
                ex["solution_en"] = "**Step 1:** Expand along column 1 (only one nonzero): $\\det = 1\\cdot\\det\\begin{pmatrix}2&0&0\\\\0&3&0\\\\0&0&4\\end{pmatrix}=24$.\n\n**Step 2:** The off-diagonal entry $5$ at $(1,4)$ has minor with a zero column, contributing $0$.\n\n**Answer:** $\\det=24$."
                ex["solution_he"] = "**צעד 1:** פיתוח לפי עמודה 1: $\\det = 1\\cdot 2\\cdot 3\\cdot 4=24$.\n\n**צעד 2:** הכניסה $5$ ב-$(1,4)$ — מינור עם עמודת אפס, תורם $0$.\n\n**תשובה:** $\\det=24$."


def validate(data: dict) -> list[str]:
    issues = []
    for sec in data["sections"]:
        k = sec.get("kind")
        if k in MIN:
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < MIN[k][0]:
                issues.append(f"{k} EN: {en_w} < {MIN[k][0]}")
            if he_w < MIN[k][1]:
                issues.append(f"{k} HE: {he_w} < {MIN[k][1]}")
        elif k == "worked_example":
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < MIN["worked_example"][0]:
                issues.append(f"worked {sec.get('example_number')} EN: {en_w}")
            if he_w < MIN["worked_example"][1]:
                issues.append(f"worked {sec.get('example_number')} HE: {he_w}")
    for q in data["questions"]:
        en_w, he_w = wc(q.get("explanation_en", "")), wc(q.get("explanation_he", ""))
        if en_w < 80 or en_w > 150:
            issues.append(f"Q{q['ord']} EN: {en_w} words")
        if he_w < 80 or he_w > 150:
            issues.append(f"Q{q['ord']} HE: {he_w} words")
    return issues


def main() -> int:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    patch_sections(data)
    patch_questions(data)
    patch_exercises(data)
    issues = validate(data)
    if issues:
        print("VALIDATION ISSUES:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
