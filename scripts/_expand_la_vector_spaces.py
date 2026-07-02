#!/usr/bin/env python3
"""Expand la_vector_spaces.json — bilingual MIN_WORDS + 80-word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/la_vector_spaces.json"

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


def he_ratio(text: str) -> float:
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def he_weak(he: str, en: str) -> bool:
    he, en = (he or "").strip(), (en or "").strip()
    if not he:
        return True
    if wc(he) / max(wc(en), 1) < 0.55:
        return True
    if he_ratio(he) < 0.15 and wc(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


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


SECTION_BODIES = {
    "intro": {
        "body_en_md": """So far, vectors have been $n$-tuples in $\\mathbb{R}^n$. But **matrices**, **polynomials**, and **continuous functions** share the same key algebraic properties: you can add them, scale them, and get another object of the same type. The **vector space axioms** abstract exactly those shared properties into a single definition that applies across all these settings.

This abstraction is powerful: every theorem we prove for abstract vector spaces applies simultaneously to $\\mathbb{R}^n$, to function spaces, to solution spaces of differential equations, and to subspaces hidden inside matrix problems. Once you recognize a set as a vector space (or subspace), you inherit dimension, basis, and linear independence tools without re-deriving them.

**Connection to previous material:** Row spaces and null spaces of matrices are examples of subspaces; Gaussian elimination computes their dimensions. This lesson formalizes what you have already been using computationally and prepares you for `concept:la_eigenvalues`, bases, and inner product spaces.""",
        "body_he_md": """עד כה, וקטורים היו $n$-יות ב-$\\mathbb{R}^n$. אבל **מטריצות**, **פולינומים** ו**פונקציות רציפות** חולקים את אותן תכונות אלגבריות מפתח: אפשר לחבר אותם, לסלול אותם, ולקבל אובייקט מאותו סוג. **אקסיומות מרחב וקטורי** מפשטות בדיוק את התכונות המשותפות הללו להגדרה אחת החלה על כל ההקשרים.

הפשטה זו עוצמתית: כל משפט שנוכיח למרחב וקטורי מופשט חל בו-זמנית על $\\mathbb{R}^n$, על מרחבי פונקציות, על מרחבי פתרונות של משוואות דיפרנציאליות, ועל תת-מרחבים בתוך בעיות מטריצות. ברגע שמזהים קבוצה כמרחב וקטורי (או תת-מרחב), יורשים כלים של ממד, בסיס ובלתי-תלות לינארית בלי לגזור מחדש.

**קשר לחומר קודם:** מרחבי שורה וגרעין של מטריצות הם דוגמאות לתת-מרחבים; אלימינציית גאוס מחשבת את ממדיהם. שיעור זה מנסח באופן פורמלי מה שכבר השתמשתם בו חישובית ומכין ל-`concept:la_eigenvalues`, בסיסים ומרחבי מכפלה פנימית.""",
    },
    "definition": {
        "body_en_md": """**Definition (Vector Space).** A **vector space** over $\\mathbb{R}$ is a set $V$ with two operations (addition $+$ and scalar multiplication $\\cdot$) satisfying 10 axioms:
1. Closure: $\\vec{u}+\\vec{v}\\in V$; $c\\vec{u}\\in V$.
2. Commutativity: $\\vec{u}+\\vec{v}=\\vec{v}+\\vec{u}$.
3. Associativity: $(\\vec{u}+\\vec{v})+\\vec{w}=\\vec{u}+(\\vec{v}+\\vec{w})$.
4. Zero vector: $\\exists\\vec{0}\\in V$ with $\\vec{u}+\\vec{0}=\\vec{u}$.
5. Additive inverses: $\\exists(-\\vec{u})$ with $\\vec{u}+(-\\vec{u})=\\vec{0}$.
6–10. Distributivity and compatibility of scalar multiplication.

**Examples:** $\\mathbb{R}^n$; $P_n$ (polynomials of degree $\\leq n$); $M_{m\\times n}$ (all $m\\times n$ matrices); $C[a,b]$ (continuous functions on $[a,b]$).

**Counterexample:** The first quadrant $\\{(x,y): x\\geq0, y\\geq0\\}$ is **not** a vector space — negative scalars push vectors outside the set.

**Subspace Criterion.** $W\\subseteq V$ is a **subspace** of $V$ iff:
1. $\\vec{0}\\in W$.
2. $\\vec{u},\\vec{v}\\in W \\Rightarrow \\vec{u}+\\vec{v}\\in W$.
3. $\\vec{u}\\in W,\\;c\\in\\mathbb{R} \\Rightarrow c\\vec{u}\\in W$.

**One-step version:** $W$ is a subspace iff $\\vec{0}\\in W$ and $a\\vec{u}+b\\vec{v}\\in W$ for all $\\vec{u},\\vec{v}\\in W$ and $a,b\\in\\mathbb{R}$.

**Span:** $\\text{span}\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\} = \\{c_1\\vec{v}_1+\\cdots+c_k\\vec{v}_k : c_i\\in\\mathbb{R}\\}$ — always a subspace.

**Linear independence:** $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ is **linearly independent** if $c_1\\vec{v}_1+\\cdots+c_k\\vec{v}_k=\\vec{0} \\Rightarrow c_i=0$ for all $i$.""",
        "body_he_md": """**הגדרה (מרחב וקטורי).** **מרחב וקטורי** מעל $\\mathbb{R}$ הוא קבוצה $V$ עם שתי פעולות (חיבור $+$ וכפל בסקלר $\\cdot$) המקיימות 10 אקסיומות:
1. סגירות: $\\vec{u}+\\vec{v}\\in V$; $c\\vec{u}\\in V$.
2. קומוטטיביות: $\\vec{u}+\\vec{v}=\\vec{v}+\\vec{u}$.
3. אסוציאטיביות: $(\\vec{u}+\\vec{v})+\\vec{w}=\\vec{u}+(\\vec{v}+\\vec{w})$.
4. וקטור אפס: $\\exists\\vec{0}\\in V$ עם $\\vec{u}+\\vec{0}=\\vec{u}$.
5. הופכיים: $\\exists(-\\vec{u})$ עם $\\vec{u}+(-\\vec{u})=\\vec{0}$.
6–10. דיסטריבוטיביות ותאימות כפל בסקלר.

**דוגמאות:** $\\mathbb{R}^n$; $P_n$ (פולינומים מדרגה $\\leq n$); $M_{m\\times n}$; $C[a,b]$ (פונקציות רציפות).

**דוגמת-נגד:** הרביע הראשון $\\{(x,y): x\\geq0, y\\geq0\\}$ **אינו** מרחב וקטורי — כפל בסקלר שלילי דוחף וקטורים מחוץ לקבוצה.

**קריטריון תת-מרחב.** $W\\subseteq V$ הוא **תת-מרחב** אם ורק אם:
1. $\\vec{0}\\in W$.
2. $\\vec{u},\\vec{v}\\in W \\Rightarrow \\vec{u}+\\vec{v}\\in W$.
3. $\\vec{u}\\in W,\\;c\\in\\mathbb{R} \\Rightarrow c\\vec{u}\\in W$.

**גרסה בצעד אחד:** $W$ תת-מרחב אם $\\vec{0}\\in W$ ו-$a\\vec{u}+b\\vec{v}\\in W$ לכל $\\vec{u},\\vec{v}\\in W$ ו-$a,b\\in\\mathbb{R}$.

**קבוצת פרישה:** $\\text{span}\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ — תמיד תת-מרחב.

**בלתי-תלות לינארית:** $c_1\\vec{v}_1+\\cdots+c_k\\vec{v}_k=\\vec{0} \\Rightarrow c_i=0$ לכל $i$.""",
    },
    "theory": {
        "body_en_md": """**Theorem 1.** The zero vector $\\vec{0}$ is unique in any vector space.

**Theorem 2.** The span of any set of vectors is a subspace.
*Proof:* Let $W=\\text{span}\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$. (1) $\\vec{0} = 0\\vec{v}_1+\\cdots+0\\vec{v}_k\\in W$. (2) If $\\vec{u},\\vec{w}\\in W$, write them as linear combinations; their sum is also a linear combination. (3) Scaling a linear combination gives another linear combination. $\\blacksquare$

**Theorem 3.** Any set containing $\\vec{0}$ is linearly **dependent**.
*Proof:* Take $c=1$ on $\\vec{0}$ and $0$ on all others: non-trivial combination summing to $\\vec{0}$.

**Theorem 4.** If $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ is linearly dependent, at least one vector is a linear combination of the others.

**Theorem 5 (Intersection of subspaces).** If $W_1$ and $W_2$ are subspaces of $V$, then $W_1\\cap W_2$ is also a subspace of $V$.
*Proof:* (1) $\\vec{0}\\in W_1\\cap W_2$. (2) If $\\vec{u},\\vec{v}\\in W_1\\cap W_2$, then $\\vec{u}+\\vec{v}\\in W_1$ and $\\vec{u}+\\vec{v}\\in W_2$, so $\\vec{u}+\\vec{v}\\in W_1\\cap W_2$. (3) Similarly for scalar multiplication. $\\blacksquare$

**Theorem 6 (Sum of subspaces).** $W_1+W_2=\\{\\vec{w}_1+\\vec{w}_2:\\vec{w}_i\\in W_i\\}$ is a subspace of $V$.

**Note:** $W_1\\cup W_2$ is generally **NOT** a subspace unless one subspace contains the other.""",
        "body_he_md": """**משפט 1.** וקטור האפס $\\vec{0}$ יחיד בכל מרחב וקטורי.

**משפט 2.** קבוצת הפרישה של כל קבוצת וקטורים היא תת-מרחב.
*הוכחה:* יהי $W=\\text{span}\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$. (1) $\\vec{0}=0\\vec{v}_1+\\cdots+0\\vec{v}_k\\in W$. (2) סכום שתי קומבינציות לינאריות הוא קומבינציה לינארית. (3) כפל בסקלר שומר על קומבינציה לינארית. $\\blacksquare$

**משפט 3.** כל קבוצה המכילה $\\vec{0}$ תלויה לינארית.
*הוכחה:* קחו $c=1$ על $\\vec{0}$ ו-$0$ על השאר — קומבינציה לא-טריוויאלית השווה $\\vec{0}$.

**משפט 4.** אם $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ תלויים לינארית, לפחות וקטור אחד הוא קומבינציה לינארית של האחרים.

**משפט 5 (חיתוך תת-מרחבים).** אם $W_1$ ו-$W_2$ תת-מרחבים של $V$, אז $W_1\\cap W_2$ גם כן תת-מרחב.
*הוכחה:* (1) $\\vec{0}\\in W_1\\cap W_2$. (2) סגירות לחיבור. (3) סגירות לכפל. $\\blacksquare$

**משפט 6 (סכום תת-מרחבים).** $W_1+W_2=\\{\\vec{w}_1+\\vec{w}_2:\\vec{w}_i\\in W_i\\}$ הוא תת-מרחב של $V$.

**הערה:** $W_1\\cup W_2$ בכלל **אינו** תת-מרחב, אלא אם כן תת-מרחב אחד מכיל את השני.""",
    },
    "worked_example_1": {
        "body_en_md": """**Is $W = \\{(x,y,z)\\in\\mathbb{R}^3 : x+y+z=0\\}$ a subspace of $\\mathbb{R}^3$?**

This is a **homogeneous** linear constraint (right-hand side $0$), which strongly suggests a subspace — but we must verify all three conditions explicitly.

### Move 1 — Zero vector
$(0,0,0)$: $0+0+0=0$. ✓ $\\vec{0}\\in W$.

### Move 2 — Closure under addition
Let $\\vec{u}=(x_1,y_1,z_1)$ and $\\vec{v}=(x_2,y_2,z_2)$ both in $W$, so $x_1+y_1+z_1=0$ and $x_2+y_2+z_2=0$. Then
$$\\vec{u}+\\vec{v}=(x_1+x_2,y_1+y_2,z_1+z_2), \\quad (x_1+x_2)+(y_1+y_2)+(z_1+z_2)=0+0=0.$$
So $\\vec{u}+\\vec{v}\\in W$. ✓

### Move 3 — Closure under scalar multiplication
$c\\vec{u}=(cx_1,cy_1,cz_1)$; $cx_1+cy_1+cz_1=c\\cdot0=0$. ✓

**Conclusion: $W$ is a subspace of $\\mathbb{R}^3$.** Geometrically, it is the plane through the origin with normal vector $(1,1,1)$.

**Geometric note:** Vectors in $W$ are perpendicular to $(1,1,1)$, so $W$ is a plane through the origin — a classic two-dimensional subspace inside $\\mathbb{R}^3$.

**Exam tip:** Homogeneous equations $ax+by+cz=0$ almost always define subspaces; non-homogeneous $=1$ fail at $\\vec{0}$ immediately.""",
        "body_he_md": """**האם $W = \\{(x,y,z)\\in\\mathbb{R}^3 : x+y+z=0\\}$ תת-מרחב של $\\mathbb{R}^3$?**

זו **הומוגנית** (צד ימני $0$), מה שמרמז על תת-מרחב — אך חובה לאמת את שלושת התנאים במפורש.

### צעד 1 — וקטור אפס
$(0,0,0)$: $0+0+0=0$. ✓ $\\vec{0}\\in W$.

### צעד 2 — סגירות לחיבור
יהיו $\\vec{u}=(x_1,y_1,z_1)$ ו-$\\vec{v}=(x_2,y_2,z_2)$ ב-$W$, כלומר $x_1+y_1+z_1=0$ ו-$x_2+y_2+z_2=0$. אז
$$\\vec{u}+\\vec{v}=(x_1+x_2,y_1+y_2,z_1+z_2), \\quad (x_1+x_2)+(y_1+y_2)+(z_1+z_2)=0.$$
לכן $\\vec{u}+\\vec{v}\\in W$. ✓

### צעד 3 — סגירות לכפל
$c\\vec{u}=(cx_1,cy_1,cz_1)$; $cx_1+cy_1+cz_1=c\\cdot0=0$. ✓

**מסקנה: $W$ הוא תת-מרחב** (מישור דרך הראשית עם נורמל $(1,1,1)$).

**הערה גיאומטרית:** וקטורים ב-$W$ ניצבים ל-$(1,1,1)$, ולכן $W$ הוא מישור דרך הראשית — תת-מרחב דו-ממדי קלאסי בתוך $\\mathbb{R}^3$.

**טיפ לבחינה:** משוואות הומוגניות $ax+by+cz=0$ כמעט תמיד מגדירות תת-מרחב; לא-הומוגניות $=1$ נכשלות ב-$\\vec{0}$ מיד.""",
    },
    "worked_example_2": {
        "body_en_md": """**Is $\\{\\vec{v}_1,\\vec{v}_2,\\vec{v}_3\\} = \\{(1,2,1),(2,3,1),(0,1,1)\\}$ linearly independent?**

**Method:** Solve $c_1(1,2,1)+c_2(2,3,1)+c_3(0,1,1)=\\vec{0}$.

### Move 1 — Set up the matrix
Place these vectors as **columns** (not rows) and row-reduce:
$$\\begin{pmatrix}1&2&0\\\\2&3&1\\\\1&1&1\\end{pmatrix} \\xrightarrow{R_2-2R_1,\\;R_3-R_1} \\begin{pmatrix}1&2&0\\\\0&-1&1\\\\0&-1&1\\end{pmatrix} \\xrightarrow{R_3-R_2} \\begin{pmatrix}1&2&0\\\\0&-1&1\\\\0&0&0\\end{pmatrix}.$$

### Move 2 — Read rank
**Rank = 2 < 3 vectors**, so there is a free variable $\\Rightarrow$ the homogeneous system has non-trivial solutions $\\Rightarrow$ the vectors are **linearly dependent**.

### Move 3 — Find a dependency
From the reduced system: $c_2 = c_3$; $c_1 = -2c_2$. Setting $c_3=1$: $c_1=-2$, $c_2=1$. Verify: $-2(1,2,1)+1(2,3,1)+1(0,1,1)=(0,0,0)$. ✓

### Move 4 — Alternative check
Since $k=n=3$, you could compute $\\det\\begin{pmatrix}1&2&0\\\\2&3&1\\\\1&1&1\\end{pmatrix}=0$ instead — zero determinant confirms dependence for square matrices.

**Interpretation:** Only two directions are independent; the third vector lies in the plane spanned by the first two — typical when rank $<k$.

**Exam tip:** For $k$ vectors in $\\mathbb{R}^n$, form an $n\\times k$ matrix with vectors as columns; independent iff rank $=k$.""",
        "body_he_md": """**האם $\\{(1,2,1),(2,3,1),(0,1,1)\\}$ בלתי-תלויים לינארית?**

**שיטה:** פתרו $c_1(1,2,1)+c_2(2,3,1)+c_3(0,1,1)=\\vec{0}$.

### צעד 1 — בניית המטריצה
הציבו את הוקטורים כ**עמודות** (לא שורות) ודרגו:
$$\\begin{pmatrix}1&2&0\\\\2&3&1\\\\1&1&1\\end{pmatrix} \\to \\begin{pmatrix}1&2&0\\\\0&-1&1\\\\0&0&0\\end{pmatrix}.$$

### צעד 2 — קריאת דרגה
**דרגה = 2 < 3 וקטורים** $\\Rightarrow$ יש משתנה חופשי $\\Rightarrow$ המערכת ההומוגנית בעלת פתרונות לא-טריוויאליים $\\Rightarrow$ הוקטורים **תלויים לינארית**.

### צעד 3 — מציאת תלות
מהמערכת המדרגת: $c_2=c_3$, $c_1=-2c_2$. עם $c_3=1$: $c_1=-2$, $c_2=1$. אימות: $-2(1,2,1)+(2,3,1)+(0,1,1)=(0,0,0)$. ✓

### צעד 4 — בדיקה חלופית
מכיוון $k=n=3$, אפשר גם $\\det\\begin{pmatrix}1&2&0\\\\2&3&1\\\\1&1&1\\end{pmatrix}=0$ — דטרמיננטה אפסית מאשרת תלות.

**פרשנות:** רק שני כיוונים בלתי-תלויים; הוקטור השלישי במישור שמפרשים הראשונים — טיפוסי כשדרגה $<k$.

**טיפ לבחינה:** ל-$k$ וקטורים ב-$\\mathbb{R}^n$, בנו מטריצה $n\\times k$ עם וקטורים כעמודות; בלתי-תלויים אם דרגה $=k$.""",
    },
    "worked_example_3": {
        "body_en_md": """**Claim:** If $W_1$ and $W_2$ are subspaces of a vector space $V$, then $W_1\\cap W_2$ is also a subspace of $V$.

**Proof:**

### Move 1 — Zero vector
Since $W_1$ is a subspace, $\\vec{0}\\in W_1$. Since $W_2$ is a subspace, $\\vec{0}\\in W_2$. Therefore $\\vec{0}\\in W_1\\cap W_2$. ✓

### Move 2 — Closure under addition
Let $\\vec{u},\\vec{v}\\in W_1\\cap W_2$. This means:
- $\\vec{u},\\vec{v}\\in W_1$, so $\\vec{u}+\\vec{v}\\in W_1$ (since $W_1$ is a subspace).
- $\\vec{u},\\vec{v}\\in W_2$, so $\\vec{u}+\\vec{v}\\in W_2$ (since $W_2$ is a subspace).

Therefore $\\vec{u}+\\vec{v}\\in W_1\\cap W_2$. ✓

### Move 3 — Closure under scalar multiplication
Let $\\vec{u}\\in W_1\\cap W_2$ and $c\\in\\mathbb{R}$:
- $\\vec{u}\\in W_1\\Rightarrow c\\vec{u}\\in W_1$.
- $\\vec{u}\\in W_2\\Rightarrow c\\vec{u}\\in W_2$.

Therefore $c\\vec{u}\\in W_1\\cap W_2$. ✓

All three conditions hold, so $W_1\\cap W_2$ is a subspace of $V$. $\\blacksquare$

**Remark:** This proof generalises to arbitrary intersections $\\bigcap_{\\alpha} W_\\alpha$. Contrast with $W_1\\cup W_2$, which fails closure under addition unless one subspace contains the other.

**Exam tip:** Intersection proofs are template arguments — copy the three subspace conditions and apply membership in both $W_1$ and $W_2$ at each step.""",
        "body_he_md": """**טענה:** אם $W_1$ ו-$W_2$ תת-מרחבים של $V$, אז $W_1\\cap W_2$ גם כן תת-מרחב.

**הוכחה:**

### צעד 1 — וקטור אפס
$\\vec{0}\\in W_1$ ו-$\\vec{0}\\in W_2$ (כי $W_1,W_2$ תת-מרחבים). לכן $\\vec{0}\\in W_1\\cap W_2$. ✓

### צעד 2 — סגירות לחיבור
יהיו $\\vec{u},\\vec{v}\\in W_1\\cap W_2$. אז $\\vec{u},\\vec{v}\\in W_1$ ולכן $\\vec{u}+\\vec{v}\\in W_1$. אנלוגית $\\vec{u}+\\vec{v}\\in W_2$. לכן $\\vec{u}+\\vec{v}\\in W_1\\cap W_2$. ✓

### צעד 3 — סגירות לכפל
$\\vec{u}\\in W_1\\cap W_2$, $c\\in\\mathbb{R}$. אז $c\\vec{u}\\in W_1$ ו-$c\\vec{u}\\in W_2$. לכן $c\\vec{u}\\in W_1\\cap W_2$. ✓

כל שלושת התנאים מתקיימים, ולכן $W_1\\cap W_2$ הוא תת-מרחב של $V$. $\\blacksquare$

**הערה:** ההוכחה מתכללת לחיתוך שרירותי $\\bigcap_{\\alpha} W_\\alpha$. לעומת זאת, $W_1\\cup W_2$ נכשל בסגירות לחיבור אלא אם תת-מרחב אחד מכיל את השני.

**טיפ לבחינה:** הוכחות חיתוך הן תבנית קבועה — העתיקו את שלושת תנאי התת-מרחב והשתמשו בשייכות ל-$W_1$ ול-$W_2$ בכל שלב.""",
    },
    "method_guide": {
        "body_en_md": """**Subspace test (3 conditions):**
1. $\\vec{0}\\in W$
2. Closed under $+$
3. Closed under scalar multiplication $\\cdot$

**One-step shortcut:** $W$ is a subspace iff $\\vec{0}\\in W$ and $a\\vec{u}+b\\vec{v}\\in W$ for all $\\vec{u},\\vec{v}\\in W$, $a,b\\in\\mathbb{R}$.

| Goal | Method | Key check |
|---|---|---|
| Is $W$ a subspace? | Verify 3 conditions (or one-step) | Homogeneous $=0$ usually passes; $=1$ fails at $\\vec{0}$ |
| Show $W$ is NOT a subspace | Find ONE violation | $\\vec{0}\\notin W$ is fastest for affine sets |
| Is $\\text{span}\\{\\vec{v}_i\\}$ a subspace? | Always yes | Span is always a subspace by Theorem 2 |
| Linear independence? | Matrix with vectors as **columns**; row-reduce | Independent iff rank $=k$ |
| Find dependency | Solve homogeneous system from RREF | Free variable $\\Rightarrow$ dependent |
| Is $\\vec{b}\\in\\text{span}$? | Row-reduce $[\\vec{v}_1\\,|\\,\\ldots\\,|\\,\\vec{v}_k\\,|\\,\\vec{b}]$ | Consistent $\\Leftrightarrow$ $\\vec{b}\\in\\text{span}$ |

**Decision tree:** Constraint through origin $\\Rightarrow$ likely subspace. First quadrant / upper half-plane $\\Rightarrow$ check scalar multiplication with negative $c$.""",
        "body_he_md": """**בדיקת תת-מרחב (3 תנאים):**
1. $\\vec{0}\\in W$
2. סגור לחיבור $+$
3. סגור לכפל בסקלר $\\cdot$

**קיצור בצעד אחד:** $W$ תת-מרחב אם $\\vec{0}\\in W$ ו-$a\\vec{u}+b\\vec{v}\\in W$ לכל $\\vec{u},\\vec{v}\\in W$, $a,b\\in\\mathbb{R}$.

| מטרה | שיטה | בדיקה |
|---|---|---|
| האם $W$ תת-מרחב? | אמת 3 תנאים (או צעד אחד) | הומוגנית $=0$ בדרך כלל עוברת; $=1$ נכשלת ב-$\\vec{0}$ |
| הראה ש-$W$ אינו תת-מרחב | מצא הפרה אחת | $\\vec{0}\\notin W$ מהיר לקבוצות אפיניות |
| האם $\\text{span}\\{\\vec{v}_i\\}$ תת-מרחב? | תמיד כן | פרישה תמיד תת-מרחב (משפט 2) |
| בלתי-תלות? | מטריצה עם וקטורים כ**עמודות**; דרג | בלתי-תלויים אם דרגה $=k$ |
| מצא תלות | פתור מערכת הומוגנית מ-RREF | משתנה חופשי $\\Rightarrow$ תלויים |
| האם $\\vec{b}\\in\\text{span}$? | דרג $[\\vec{v}_1\\,|\\,\\ldots\\,|\\,\\vec{b}]$ | עקבי $\\Leftrightarrow$ $\\vec{b}\\in\\text{span}$ |

**עץ החלטות:** אילוץ דרך הראשית $\\Rightarrow$ כנראה תת-מרחב. רביע ראשון / חצי-מישור עליון $\\Rightarrow$ בדקו כפל בסקלר שלילי.""",
    },
    "pitfall": {
        "body_en_md": """1. **Forgetting to check $\\vec{0}\\in W$.** This is often the easiest condition to verify and the first failure for affine sets like $\\{x+y=1\\}$. Always test the origin before checking closure.

2. **Thinking $W_1\\cup W_2$ is a subspace.** It is NOT unless one subspace contains the other. The coordinate axes in $\\mathbb{R}^2$ are the classic counterexample: $(1,0)+(0,1)=(1,1)$ leaves the union.

3. **Confusing span with linear independence.** A set can span a large space and still be dependent (redundant vectors). Span measures how much space is covered; independence measures whether any vector is redundant.

4. **Forming the matrix with vectors as rows vs. columns.** When testing independence of $k$ vectors in $\\mathbb{R}^n$, form an $n\\times k$ matrix with vectors as **columns**. Row rank equals column rank, but the standard algorithm expects columns for the homogeneous system $A\\vec{c}=\\vec{0}$.

5. **Declaring dependence based on zero determinant when $k\\neq n$.** The determinant test only applies when $k=n$ (square matrix). For $k\\neq n$, use row reduction and compare rank to $k$.""",
        "body_he_md": """1. **שכחה לבדוק $\\vec{0}\\in W$.** זהו לעתים קרובות התנאי הקל ביותר לבדיקה והכישלון הראשון לקבוצות אפיניות כמו $\\{x+y=1\\}$. תמיד בדקו את הראשית לפני סגירות.

2. **מחשבה ש-$W_1\\cup W_2$ הוא תת-מרחב.** זה **לא** נכון, אלא אם כן אחד מכיל את השנi. צירי הקואורדינטות ב-$\\mathbb{R}^2$ הם דוגמת-נגד קלאסית: $(1,0)+(0,1)=(1,1)$ יוצא מהאיחוד.

3. **בלבול בין span ובלתי-תלות.** קבוצה יכולה לפרוש מרחב גדול ועדיין להיות תלויה (וקטורים מיותרים). פרישה מודדת כיסוי; בלתי-תלות מודדת מיותרות.

4. **הצבת הוקטורים כשורות במקום עמודות.** לבדיקת בלתי-תלות של $k$ וקטורים ב-$\\mathbb{R}^n$, בנה מטריצה $n\\times k$ עם הוקטורים כ**עמודות**. האלגוריתם הסטנדרטי מצפה לעמודות עבור $A\\vec{c}=\\vec{0}$.

5. **הכרזת תלות בהתבסס על דטרמיננטה אפסית כש-$k\\neq n$.** בדיקת דטרמיננטה חלה רק כש-$k=n$ (מטריצה ריבועית). אחרת, דרג והשוו דרגה ל-$k$.""",
    },
    "why_matters": {
        "body_en_md": """Vector spaces are the language of linear algebra — every later topic (bases, dimension, eigenvalues, inner products) lives inside this framework.

**You will use this to unlock:**
- `concept:la_eigenvalues` **Eigenvalues & Eigenvectors** (prereq)
- `concept:inner_product_gram_schmidt` **Inner Product & Gram–Schmidt**
- `concept:la_orthogonality` **Orthogonality**

**Builds on:**
- `concept:la_matrices` **Matrices & Linear Systems**

**Why it matters for exams:** Israeli university courses reward proving or disproving subspace status, testing independence via row reduction, and structural proofs (intersection and sum are subspaces). These appear on nearly every midterm.""",
        "body_he_md": """מרחבים וקטוריים הם שפת האלגברה הלינארית — כל נושא מאוחר (בסיסים, ממד, ערכים עצמיים, מכפלות פנימיות) חי בתוך מסגרת זו.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:la_eigenvalues` **ערכים ווקטורים עצמיים** (prereq)
- `concept:inner_product_gram_schmidt` **מכפלה פנימית וגרם–שמידט**
- `concept:la_orthogonality` **אורתוגונליות**

**מבוסס על:**
- `concept:la_matrices` **מטריצות ומערכות לינאריות**

**למה זה חשוב לבחינות:** קורסים באוניברסיטה בישראל מעריכים הוכחה/הפרכה של תת-מרחב, בדיקת בלתי-תלות בדירוג, והוכחות מבניות (חיתוך וסכום). אלה מופיעים כמעט בכל מבחן אמצע.""",
    },
    "before_exam": {
        "body_en_md": """**Formula sheet:**
- Subspace: $\\vec{0}\\in W$; closed under $+$ and $\\cdot$
- One-step: $a\\vec{u}+b\\vec{v}\\in W$ for all $\\vec{u},\\vec{v}\\in W$
- span is always a subspace
- Independence: form matrix with vectors as columns; independent iff rank $=k$
- $W_1\\cap W_2$ and $W_1+W_2$ are subspaces; $W_1\\cup W_2$ is NOT in general

**What Israeli university exams emphasise:**
- Proving or disproving subspace with 3-condition format.
- Testing linear independence of 3 vectors in $\\mathbb{R}^3$ using row reduction or determinant ($3\\times3$ only).
- Showing/disproving membership in a span.
- Proving structural results (intersection, sum are subspaces).

**Exam tip:** To show something is NOT a subspace, one counterexample suffices — find the fastest-failing condition (usually $\\vec{0}\\notin W$).""",
        "body_he_md": """**גיליון נוסחאות:**
- תת-מרחב: $\\vec{0}\\in W$; סגור ל-$+$ וכפל
- צעד אחד: $a\\vec{u}+b\\vec{v}\\in W$ לכל $\\vec{u},\\vec{v}\\in W$
- span תמיד תת-מרחב
- בלתי-תלות: מטריצה עם וקטורים כעמודות; בלתי-תלויים אם דרגה $=k$
- $W_1\\cap W_2$ ו-$W_1+W_2$ תת-מרחבים; $W_1\\cup W_2$ בדרך כלל לא

**מה בחינות ישראליות מדגישות:**
- הוכחה/הפרכה של תת-מרחב בפורמט 3 תנאים.
- בדיקת בלתי-תלות של 3 וקטורים ב-$\\mathbb{R}^3$.
- שייכות ל-span.
- הוכחת תוצאות מבניות (חיתוך, סכום).

**טיפ:** להראות שמשהו אינו תת-מרחב — דוגמת נגד אחת מספיקה (בדרך כלל $\\vec{0}\\notin W$).""",
    },
    "summary": {
        "body_en_md": """- A **vector space** satisfies 10 axioms; key examples: $\\mathbb{R}^n$, $P_n$, $M_{m\\times n}$, $C[a,b]$.
- **Subspace criterion:** $\\vec{0}\\in W$, closed under addition, closed under scalar multiplication.
- **Span** of any set is always a subspace (Theorem 2).
- **Linear independence:** only the trivial combination equals $\\vec{0}$; test via row reduction (columns!) or determinant when $k=n$.
- **Intersection** and **sum** of subspaces are subspaces; **union** generally is not.
- Any set containing $\\vec{0}$ is automatically dependent.

**Takeaway:** Given any subset of a vector space, you should now decide subspace status, test independence, and compute span membership using the toolkit above.""",
        "body_he_md": """- **מרחב וקטורי** מקיים 10 אקסיומות; דוגמאות: $\\mathbb{R}^n$, $P_n$, $M_{m\\times n}$, $C[a,b]$.
- **קריטריון תת-מרחב:** $\\vec{0}\\in W$, סגור לחיבור, סגור לכפל.
- **Span** של כל קבוצה הוא תמיד תת-מרחב (משפט 2).
- **בלתי-תלות לינארית:** רק קומבינציה טריוויאלית שווה $\\vec{0}$; בדיקה בדירוג (עמודות!) או דטרמיננטה כש-$k=n$.
- **חיתוך** ו**סכום** תת-מרחבים הם תת-מרחבים; **איחוד** בדרך כלל לא.
- כל קבוצה המכילה $\\vec{0}$ תלויה אוטומטית.

**מסקנה:** עבור כל תת-קבוצה, אתם אמורים לקבוע סטטוס תת-מרחב, לבדוק בלתי-תלות, ולחשב שייכות ל-span.""",
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": """### Move 1 — Test $\\vec{0}$
$\\vec{0}=(0,0)$ has $0+0=0\\neq1$, so $\\vec{0}\\notin W$. **Fails condition 1 immediately.**

### Move 2 — Why the other conditions do not matter
Even though $(1,0)\\in W$ and $(0,1)\\in W$, a subspace **must** contain the zero vector. The set $W=\\{(x,y): x+y=1\\}$ is an **affine line** (translated plane) — parallel to the subspace $\\{x+y=0\\}$ but not through the origin.

**Conclusion:** $W$ is **not** a subspace of $\\mathbb{R}^2$.""",
        "checkpoint_solution_he": """### צעד 1 — בדיקת $\\vec{0}$
$\\vec{0}=(0,0)$: $0+0=0\\neq1$, לכן $\\vec{0}\\notin W$. **כשל בתנאי 1 מיד.**

### צעד 2 — למה שאר התנאים לא רלוונטיים
גם אם $(1,0),(0,1)\\in W$, תת-מרחב **חייב** להכיל את וקטור האפס. $W=\\{(x,y): x+y=1\\}$ הוא **קו אפיני** — מקביל ל-$\\{x+y=0\\}$ אך לא דרך הראשית.

**מסקנה:** $W$ **אינו** תת-מרחב של $\\mathbb{R}^2$.""",
    },
    {
        "checkpoint_solution_en": """### Move 1 — Form matrix with vectors as columns
$$A = \\begin{pmatrix}1&0&1\\\\0&1&1\\\\1&1&0\\end{pmatrix}.$$

### Move 2 — Row reduce (or compute determinant)
$\\det(A) = 1(0-1)-0+1(0-1)=-2\\neq0$. Three pivots (or non-zero determinant for $3\\times3$).

### Move 3 — Conclusion
Rank $=3=$ number of vectors, so the only solution to $c_1\\vec{v}_1+c_2\\vec{v}_2+c_3\\vec{v}_3=\\vec{0}$ is trivial. **Linearly independent.**""",
        "checkpoint_solution_he": """### צעד 1 — מטריצה עם וקטורים כעמודות
$$A = \\begin{pmatrix}1&0&1\\\\0&1&1\\\\1&1&0\\end{pmatrix}.$$

### צעד 2 — דירוג (או דטרמיננטה)
$\\det(A)=-2\\neq0$. שלושה צירים (דטרמיננטה לא-אפסית ל-$3\\times3$).

### צעד 3 — מסקנה
דרגה $=3$ = מספר וקטורים, הפתרון היחיד ל-$\\sum c_i\\vec{v}_i=\\vec{0}$ הוא טריוויאלי. **בלתי-תלויים לינארית.**""",
    },
]

EXPLANATIONS = [
    fmt_expl(
        "The set $W=\\{(x,y,z): 2x-y+z=0\\}$ is defined by a **homogeneous** linear equation. Check (1): $\\vec{0}$ satisfies $0-0+0=0$. Check (2): if two points satisfy the equation, their sum does too because $(2x_1-y_1+z_1)+(2x_2-y_2+z_2)=0+0=0$. Check (3): scaling preserves the equation since $c(2x-y+z)=c\\cdot0=0$. All three subspace conditions hold.",
        "Homogeneous constraints $ax+by+cz=0$ almost always define subspaces — the right-hand side being zero ensures the origin lies inside. Contrast with $2x-y+z=1$, which would fail at $\\vec{0}$.",
        "Answering 'no' because the equation looks complicated, or checking only one condition. Another error: verifying addition but forgetting scalar multiplication with negative $c$.",
        "On subspace yes/no questions, write all three checks even when the answer seems obvious — Israeli exams award method marks per condition.",
        "הקבוצה $W=\\{(x,y,z): 2x-y+z=0\\}$ מוגדרת על ידי משוואה **הומוגנית**. (1) $\\vec{0}$ מקיים $0-0+0=0$. (2) סכום שני נקודות מקיים $(2x_1-y_1+z_1)+(2x_2-y_2+z_2)=0$. (3) כפל בסקלר שומר $c(2x-y+z)=0$. כל שלושת התנאים מתקיימים.",
        "אילוצים הומוגניים $ax+by+cz=0$ כמעט תמיד מגדירים תת-מרחב — צד ימני אפס מבטיח שהראשית בפנים. השוו ל-$2x-y+z=1$ שנכשל ב-$\\vec{0}$.",
        "תשובה 'לא' כי המשוואה נראית מסובכת, או בדיקת תנאי אחד בלבד. טעות: אימות חיבור בלי כפל בסקלר שלילי.",
        "בשאלות כן/לא תת-מרחב, כתבו את שלושת הבדיקות — בחינות ישראליות נותנות נקודות שיטה לכל תנאי.",
    ),
    fmt_expl(
        "$W=\\{(x,y): x\\geq0\\}$ is the right half-plane including the $y$-axis. While $(1,0)\\in W$, scalar multiplication fails: $(-1)(1,0)=(-1,0)$ has $x=-1<0$, so $(-1,0)\\notin W$. One counterexample against closure under scalar multiplication is enough to disprove subspace status.",
        "Sets defined by inequalities ($\\geq$, $>$, $\\leq$) are rarely subspaces because negative scalars flip the inequality direction. Always test multiplication by $c=-1$ on a convenient vector in $W$.",
        "Answering 'yes' because the set contains $\\vec{0}$ and is closed under addition — addition alone is insufficient. Another trap: confusing 'contains the origin' with 'is a subspace'.",
        "For inequality-defined sets, your first test should be $c=-1$ on a vector with a positive coordinate — this catches half-planes and quadrants instantly.",
        "$W=\\{(x,y): x\\geq0\\}$ הוא חצי-מישור ימני. $(1,0)\\in W$, אך כפל בסקלר נכשל: $(-1)(1,0)=(-1,0)$ עם $x=-1<0$, לכן $(-1,0)\\notin W$. דוגמת נגד אחת לסגירות כפל מספיקה.",
        "קבוצות עם אי-שוויונות ($\\geq$) לעיתים רחוקות תת-מרחבים — כפל בסקלר שלילי הופך את האי-שוויון. תמיד בדקו $c=-1$ על וקטור נוח ב-$W$.",
        "תשובה 'כן' כי $\\vec{0}\\in W$ וסגור לחיבור — חיבור לבד לא מספיק. מלכודת: בלבול 'מכיל ראשית' עם 'תת-מרחב'.",
        "בקבוצות עם אי-שוויון, הבדיקה הראשונה: $c=-1$ על וקטור עם קואורדינטה חיובית — תופס חצי-מישורים ורביעים.",
    ),
    fmt_expl(
        "Observe directly that $(2,4)=2(1,2)$, so the second vector is a scalar multiple of the first — a non-trivial dependency with $c_1=2$, $c_2=-1$ (or equivalently $(2,4)-2(1,2)=\\vec{0}$). Alternatively, $\\det\\begin{pmatrix}1&2\\\\2&4\\end{pmatrix}=4-4=0$ confirms linear dependence for this $2\\times2$ case.",
        "Before row-reducing, scan for obvious multiples — proportional columns mean dependence immediately. For two vectors in $\\mathbb{R}^2$, the determinant shortcut is valid because $k=n=2$.",
        "Declaring 'independent' because the vectors look different, or computing the determinant as $4+4=8$ (sign error). Another slip: checking only that neither vector is zero.",
        "When $k=2$ in $\\mathbb{R}^2$, write the determinant in one line — if zero, state the explicit multiple relation for full marks.",
        "ישירות: $(2,4)=2(1,2)$, הוקטור השני כפולה סקalarית של הראשון — תלות עם $(2,4)-2(1,2)=\\vec{0}$. לחלופין, $\\det\\begin{pmatrix}1&2\\\\2&4\\end{pmatrix}=0$ מאשר תלות ב-$2\\times2$.",
        "לפני דירוג, סרקו כפולות ברורות — עמודות פרופורציונליות = תלות מיד. לשני וקטורים ב-$\\mathbb{R}^2$, קיצור דרך דטרמיננטה תקף כי $k=n=2$.",
        "הכרזה 'בלתי-תלויים' כי הוקטורים נראים שונים, או $\\det=4+4=8$ (שגיאת סימן). טעות: בדיקה רק שאף וקטור לא אפס.",
        "כש-$k=2$ ב-$\\mathbb{R}^2$, כתבו דטרמיננטה בשורה — אם 0, ציינו את יחס הכפל לניקוד מלא.",
    ),
    fmt_expl(
        "Symmetric matrices form a subspace of $M_{2\\times2}$. (1) Zero matrix: $0^T=0$, so $\\vec{0}\\in W$. (2) If $A^T=A$ and $B^T=B$, then $(A+B)^T=A^T+B^T=A+B$. (3) If $A^T=A$, then $(cA)^T=cA^T=cA$. All three conditions hold — this is a standard 'verify the axioms on a structured subset' proof.",
        "When $W$ is defined by a property (symmetric, trace-zero, upper triangular), translate each subspace condition into that property. Transpose laws: $(A+B)^T=A^T+B^T$ and $(cA)^T=cA^T$ do the heavy lifting.",
        "Checking only $A^T=A$ for one example matrix instead of proving closure. Another error: forgetting that the zero matrix is symmetric.",
        "Matrix-subspace proofs on exams follow the same 3-step template as $\\mathbb{R}^n$ — label steps (1)(2)(3) explicitly for partial credit.",
        "מטריצות סימטריות образуют תת-מרחב ב-$M_{2\\times2}$. (1) $0^T=0$. (2) אם $A^T=A$ ו-$B^T=B$, אז $(A+B)^T=A+B$. (3) $(cA)^T=cA$. כל התנאים מתקיימים — הוכחה סטנדרטית על תת-קבוצה עם תכונה.",
        "כש-$W$ מוגדר בתכונה (סימטרית, עקבה-אפס), תרגמו כל תנאי לתכונה. חוקי טרנספוז: $(A+B)^T$ ו-$(cA)^T$ עושים את העבודה.",
        "בדיקת $A^T=A$ לדוגמה אחת במקום הוכחת סגירות. טעות: שכחה שמטריצת האפס סימטרית.",
        "הוכחות תת-מרחב מטריציוניות עוקבות אחרי תבנית 3 השלבים — סמנו (1)(2)(3) לנקודות חלקיות.",
    ),
    fmt_expl(
        "We need $c_1(1,0,1)+c_2(0,1,1)=(1,2,3)$. From the first two components: $c_1=1$, $c_2=2$. Check the third: $c_1+c_2=1+2=3$ ✓. So $(1,2,3)=1\\cdot(1,0,1)+2\\cdot(0,1,1)$, meaning **yes**, the vector lies in the span.",
        "Span membership is a consistency check: solve for coefficients from the first equations, then verify remaining components. Alternatively, row-reduce $[(1,0,1)^T|(0,1,1)^T|(1,2,3)^T]$ — consistent iff in span.",
        "Finding $c_1=1$, $c_2=2$ from $x,y$ but not verifying $z$. Another error: row-reducing with vectors as rows instead of columns in the augmented matrix.",
        "Always write 'check $z$:' (or the last component) after finding coefficients — one line catches inconsistent systems immediately.",
        "נדרש $c_1(1,0,1)+c_2(0,1,1)=(1,2,3)$. מ-$x,y$: $c_1=1$, $c_2=2$. בדיקת $z$: $1+2=3$ ✓. לכן $(1,2,3)=1\\cdot(1,0,1)+2\\cdot(0,1,1)$ בפרישה — **כן**.",
        "שייכות ל-span היא בדיקת עקביות: פתרו מקדמים מהרכיבים הראשונים, ואז אמתו את הרכיבים הנותרים. לחלופין, דרגו מטריצה מורחבת עם וקטורים כעמודות.",
        "מציאת $c_1,c_2$ מ-$x,y$ בלי אימות $z$. טעות: דירוג עם וקטורים כשורות.",
        "תמיד כתבו 'בדיקת $z$:' אחרי מציאת מקדמים — שורה אחת תופסת מערכות לא-עקביות.",
    ),
    fmt_expl(
        "Form the $3\\times3$ matrix with columns $(1,1,0)^T$, $(1,0,1)^T$, $(0,1,1)^T$. Compute $\\det = 1(0-1)-1(1-1)+0 = -2\\neq0$. Non-zero determinant for a square matrix means rank $=3$, so the only solution to $\\sum c_i\\vec{v}_i=\\vec{0}$ is trivial — the set is **linearly independent**. No dependency exists.",
        "For $k=n=3$ in $\\mathbb{R}^3$, the determinant test is valid and faster than full row reduction. Non-zero $\\det$ implies independence; zero $\\det$ implies dependence (and you should then find the relation).",
        "Computing $\\det=1(-1)-1(1)+0=0$ due to sign error on the middle term. Another trap: row-reducing and seeing three pivots but declaring dependent because 'there are three vectors'.",
        "When the stem asks 'if not, find a dependency' and $\\det\\neq0$, state clearly: 'independent, no dependency' — do not fabricate one.",
        "בנו מטריצה $3\\times3$ עם עמודות $(1,1,0)^T$, $(1,0,1)^T$, $(0,1,1)^T$. $\\det=-2\\neq0$. דטרמיננטה לא-אפסית $\\Rightarrow$ דרגה 3 $\\Rightarrow$ **בלתי-תלויים לינארית**. אין יחס תלות.",
        "ל-$k=n=3$ ב-$\\mathbb{R}^3$, בדיקת דטרמיננטה תקפה ומהירה יותר מדירוג מלא. $\\det\\neq0$ $\\Rightarrow$ בלתי-תלויים; $\\det=0$ $\\Rightarrow$ תלויים (ומצאו יחס מפורש).",
        "$\\det=0$ בגלל שגיאת סימן. מלכודת: שלושה צירים אך הכרזה 'תלויים' כי 'יש שלושה וקטורים'.",
        "כששואלים 'אם לא, מצא תלות' ו-$\\det\\neq0$, כתבו: 'בלתי-תלויים, אין תלות'.",
    ),
    fmt_expl(
        "$W=\\{p(x)\\in P_2 : p(0)=0\\}$ consists of polynomials with zero constant term, i.e., $p(x)=ax+bx^2$ (no constant). (1) $p=0$: $p(0)=0$ ✓. (2) If $p(0)=0$ and $q(0)=0$, then $(p+q)(0)=p(0)+q(0)=0$ ✓. (3) $(cp)(0)=c\\cdot p(0)=0$ ✓. All three subspace conditions hold.",
        "Functional subspaces are tested the same way as $\\mathbb{R}^n$: evaluate the defining condition at $\\vec{0}$ (here, $p(0)$), then check addition and scaling preserve the condition. Recognize $p(0)=0$ as 'no constant term'.",
        "Confusing $P_2$ (degree $\\leq2$) with $P_1$, or checking $p(1)=0$ instead of $p(0)=0$. Another error: claiming failure because not every polynomial is in $W$.",
        "For polynomial subspaces, rewrite the condition algebraically ($p(0)=0$ means $c_0=0$) before proving closure — examiners prefer one line of interpretation.",
        "$W=\\{p\\in P_2: p(0)=0\\}$ = פולינומים ללא איבר קבוע ($p(x)=ax+bx^2$). (1) $p=0$: $p(0)=0$ ✓. (2) $(p+q)(0)=0$ ✓. (3) $(cp)(0)=0$ ✓. כל התנאים מתקיימים.",
        "תת-מרחבי פונקציות נבדקים כמו $\\mathbb{R}^n$: העריכו את התנאי ב-$\\vec{0}$ ($p(0)$), ואז חיבור וכפל. $p(0)=0$ = 'אין איבר קבוע'.",
        "בלבול $P_2$ עם $P_1$, או בדיקת $p(1)=0$ במקום $p(0)=0$. טעות: 'לא תת-מרחב' כי לא כל פולינום ב-$W$.",
        "בתת-מרחבי פולינומים, כתבו פרשנות אלגברית ($c_0=0$) לפני הוכחת סגירות.",
    ),
    fmt_expl(
        "Take $W_1=\\text{span}\\{(1,0)\\}$ (the $x$-axis) and $W_2=\\text{span}\\{(0,1)\\}$ (the $y$-axis). Both are subspaces. Yet $(1,0)\\in W_1\\subseteq W_1\\cup W_2$ and $(0,1)\\in W_2\\subseteq W_1\\cup W_2$, but $(1,0)+(0,1)=(1,1)\\notin W_1\\cup W_2$ because $(1,1)$ lies on neither axis. The union fails closure under addition.",
        "To disprove that a union is a subspace, find two vectors — one from each piece — whose sum falls outside the union. Coordinate axes are the standard example; any two distinct lines through the origin work similarly.",
        "Claiming $W_1\\cup W_2=\\mathbb{R}^2$ is a subspace because it 'covers the plane' — coverage is irrelevant; closure under addition is what matters.",
        "When asked for an example, name $W_1$, $W_2$, give the two vectors, compute the sum, and state which subspace condition fails — four lines earn full marks.",
        "$W_1=\\text{span}\\{(1,0)\\}$ (ציר $x$), $W_2=\\text{span}\\{(0,1)\\}$ (ציר $y$). שני התת-מרחבים תקינים. $(1,0),(0,1)\\in W_1\\cup W_2$, אך $(1,0)+(0,1)=(1,1)\\notin W_1\\cup W_2$ — לא על אף ציר. האיחוד נכשל בסגירות לחיבור.",
        "להפרכת תת-מרחב של איחוד, מצאו שני וקטורים — אחד מכל תת-מרחב — שסכומם מחוץ לאיחוד. צירי הקואורדינטות ב-$\\mathbb{R}^2$ הם הדוגמה הסטנדרטית ביותר.",
        "טענה '$W_1\\cup W_2=\\mathbb{R}^2$ תת-מרחב כי מכסה את המישור' — כיסוי לא רלוונטי; סגירות לחיבור כן.",
        "בבקשת דוגמה, ציינו $W_1,W_2$, הוקטורים, חשבו סכום, וציינו איזה תנאי נכשל.",
    ),
]

EXERCISE_SET_BODY = {
    "body_en_md": """Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.

These drills cover subspace verification (including matrix and polynomial spaces), linear independence via row reduction and determinants, span membership, union counterexamples, and short proofs (adding independent vectors, equal-dimension containment, basis from span, sum of subspaces).""",
    "body_he_md": """פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.

התרגילים מכסים אימות תת-מרחב (כולל מרחבי מטריצות ופולינומים), בלתי-תלות בדירוג ודטרמיננטות, שייכות ל-span, דוגמאות-נגד לאיחוד, והוכחות קצרות (הוספת וקטור, הכלה בממד שווה, בסיס מפרישה, סכום תת-מרחבים).""",
}

EXERCISE_SOLUTIONS = {
    "e6": {
        "solution_en": "**Step 1:** Form matrix with columns $(1,1,0)^T$, $(1,0,1)^T$, $(0,1,1)^T$.\n\n**Step 2:** $\\det = 1(-1)-1(1-1)+0 = -2\\neq0$.\n\n**Answer:** **Linearly independent** (no dependency; $\\det\\neq0$).",
        "solution_he": "**צעד 1:** מטריצה עם עמודות $(1,1,0)^T$, $(1,0,1)^T$, $(0,1,1)^T$.\n\n**צעד 2:** $\\det=-2\\neq0$.\n\n**תשובה:** **בלתי-תלויים** (אין תלות).",
    },
    "e7": {
        "solution_en": "**Step 1:** $p=0$: $p(0)=0$ ✓.\n\n**Step 2:** If $p(0)=0,q(0)=0$: $(p+q)(0)=0$ ✓; $(cp)(0)=0$ ✓.\n\n**Answer:** $W$ is a subspace ($p(0)=0$ means no constant term).",
        "solution_he": "**צעד 1:** $p=0$: $p(0)=0$ ✓.\n\n**צעד 2:** $(p+q)(0)=0$ ✓; $(cp)(0)=0$ ✓.\n\n**תשובה:** $W$ תת-מרחב ($p(0)=0$ = ללא איבר קבוע).",
    },
    "e11": {
        "solution_en": "**Step 1:** Row-reduce matrix with rows $(1,2,3)$, $(2,4,6)$, $(1,0,1)$, $(0,2,2)$.\n\n**Step 2:** $(2,4,6)=2(1,2,3)$ redundant; $(0,2,2)=(1,2,3)-(1,0,1)$ redundant.\n\n**Answer:** Basis $\\{(1,2,3),(1,0,1)\\}$, $\\dim W=2$.",
        "solution_he": "**צעד 1:** דרג מטריצה עם שורות $(1,2,3)$, $(2,4,6)$, $(1,0,1)$, $(0,2,2)$.\n\n**צעד 2:** $(2,4,6)=2(1,2,3)$ מיותר; $(0,2,2)=(1,2,3)-(1,0,1)$ מיותר.\n\n**תשובה:** בסיס $\\{(1,2,3),(1,0,1)\\}$, $\\dim W=2$.",
    },
    "e12": {
        "solution_en": "**Step 1:** $\\vec{0}=\\vec{0}+\\vec{0}\\in W_1+W_2$ ✓.\n\n**Step 2:** $(\\vec{u}_1+\\vec{u}_2)+(\\vec{v}_1+\\vec{v}_2)=(\\vec{u}_1+\\vec{v}_1)+(\\vec{u}_2+\\vec{v}_2)\\in W_1+W_2$ ✓.\n\n**Step 3:** $c(\\vec{w}_1+\\vec{w}_2)=(c\\vec{w}_1)+(c\\vec{w}_2)\\in W_1+W_2$ ✓. $\\blacksquare$",
        "solution_he": "**צעד 1:** $\\vec{0}\\in W_1+W_2$ ✓.\n\n**צעד 2:** סגור לחיבור ✓.\n\n**צעד 3:** סגור לכפל ✓. $\\blacksquare$",
    },
}


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    kind_map = {
        "intro": "intro",
        "definition": "definition",
        "theory": "theory",
        "method_guide": "method_guide",
        "pitfall": "pitfall",
        "why_matters": "why_matters",
        "before_exam": "before_exam",
        "summary": "summary",
    }
    we_idx = 0
    cp_idx = 0
    for s in data["sections"]:
        k = s["kind"]
        if k in kind_map:
            key = kind_map[k]
            s["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
            s["body_he_md"] = SECTION_BODIES[key]["body_he_md"]
        elif k == "worked_example":
            we_idx += 1
            key = f"worked_example_{we_idx}"
            s["body_en_md"] = SECTION_BODIES[key]["body_en_md"]
            s["body_he_md"] = SECTION_BODIES[key]["body_he_md"]
        elif k == "checkpoint":
            sol = CHECKPOINTS[cp_idx]
            s["checkpoint_solution_en"] = sol["checkpoint_solution_en"]
            s["checkpoint_solution_he"] = sol["checkpoint_solution_he"]
            cp_idx += 1

    for i, q in enumerate(data["questions"]):
        q["explanation_en"], q["explanation_he"] = EXPLANATIONS[i]

    for s in data["sections"]:
        if s["kind"] == "exercise_set":
            s["body_en_md"] = EXERCISE_SET_BODY["body_en_md"]
            s["body_he_md"] = EXERCISE_SET_BODY["body_he_md"]
            for ex in s.get("exercises", []):
                sol = EXERCISE_SOLUTIONS.get(ex["id"])
                if sol:
                    ex["solution_en"] = sol["solution_en"]
                    ex["solution_he"] = sol["solution_he"]

    data["version"] = 2
    data["author"] = "cursor-claude-2026"

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    errs = []
    for s in data["sections"]:
        k = s["kind"]
        if k not in MIN:
            continue
        en_min, he_min = MIN[k]
        en, he = wc(s["body_en_md"]), wc(s["body_he_md"])
        if en < en_min:
            errs.append(f"{k}: en={en}<{en_min}")
        if he < he_min:
            errs.append(f"{k}: he={he}<{he_min}")
        if he_weak(s["body_he_md"], s["body_en_md"]):
            errs.append(f"{k}: he-weak")

    for q in data["questions"]:
        en, he = wc(q["explanation_en"]), wc(q["explanation_he"])
        if en < 80:
            errs.append(f"q{q['ord']}: expl-en={en}<80")
        if he < 80:
            errs.append(f"q{q['ord']}: expl-he={he}<80")
        if en > 150:
            errs.append(f"q{q['ord']}: expl-en={en}>150")
        if he > 150:
            errs.append(f"q{q['ord']}: expl-he={he}>150")
        if he_weak(q["explanation_he"], q["explanation_en"]):
            errs.append(f"q{q['ord']}: expl-he-weak")

    if errs:
        print("VALIDATION ERRORS:")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)

    print("Section + explanation validation OK")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(r.returncode)
    print("seed-lessons --dry-run OK")


if __name__ == "__main__":
    main()
