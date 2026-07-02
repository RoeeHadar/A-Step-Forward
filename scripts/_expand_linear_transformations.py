#!/usr/bin/env python3
"""Expand linear_transformations_kernel_image.json — bilingual MIN_WORDS + 80-word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/linear_transformations_kernel_image.json"

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
        "body_en_md": """A **linear transformation** (linear map) $T:V\\to W$ between vector spaces is a function that preserves the two algebraic operations: vector addition and scalar multiplication. Formally,
$$T(\\vec{u}+\\vec{v})=T(\\vec{u})+T(\\vec{v}), \\qquad T(\\alpha\\vec{v})=\\alpha T(\\vec{v}).$$
Equivalently, $T(a\\vec{u}+b\\vec{v})=aT(\\vec{u})+bT(\\vec{v})$ for all scalars $a,b$ and vectors $\\vec{u},\\vec{v}$.

**Examples you already know:** rotation and reflection in $\\mathbb{R}^2$; projection onto a line or plane; differentiation $D(p)=p'$ on polynomial spaces; matrix multiplication $T(\\vec{x})=A\\vec{x}$.

Every linear map has two companion subspaces that encode its global behavior:
- **Kernel (null space)** $\\ker(T)=\\{\\vec{v}\\in V : T(\\vec{v})=\\mathbf{0}\\}$ — inputs crushed to zero.
- **Image (range)** $\\text{Im}(T)=\\{T(\\vec{v}) : \\vec{v}\\in V\\}$ — all outputs actually reachable.

These objects connect directly to solving $A\\vec{x}=\\vec{0}$, column spaces, rank, and the rank-nullity theorem — the backbone of university linear algebra and engineering system analysis.""",
        "body_he_md": """**טרנספורמציה לינארית** (העתקה לינארית) $T:V\\to W$ בין מרחבי וקטורים היא פונקציה ששומרת על שתי הפעולות האלגבריות: חיבור וקטורים וכפל בסקלר. באופן פורמלי,
$$T(\\vec{u}+\\vec{v})=T(\\vec{u})+T(\\vec{v}), \\qquad T(\\alpha\\vec{v})=\\alpha T(\\vec{v}).$$
שקול לכך: $T(a\\vec{u}+b\\vec{v})=aT(\\vec{u})+bT(\\vec{v})$ לכל $a,b\\in\\mathbb{R}$ ווקטורים $\\vec{u},\\vec{v}\\in V$.

**דוגמאות מוכרות:** סיבוב והשתקפות ב-$\\mathbb{R}^2$; הטלה על ישר או מישור; נגזרת $D(p)=p'$ במרחבי פולינומים; כפל מטריצה $T(\\vec{x})=A\\vec{x}$.

לכל העתקה לינארית יש שני תת-מרחבים מלווים שמתארים את ההתנהגות הגלובלית:
- **גרעין (מרחב אפסי)** $\\ker(T)=\\{\\vec{v}\\in V : T(\\vec{v})=\\mathbf{0}\\}$ — קלטים שנמחצים לאפס.
- **תמונה (טווח)** $\\text{Im}(T)=\\{T(\\vec{v}) : \\vec{v}\\in V\\}$ — כל הפלטים שניתן להשיג בפועל.

האובייקטים האלה קשורים ישירות לפתרון $A\\vec{x}=\\vec{0}$, מרחב עמודות, דרגה ומשפט הדרגה-אפסיות — עמוד השדרה של אלגברה לינארית באוניברסיטה וניתוח מערכות הנדסיות.""",
    },
    "definition": {
        "body_en_md": """**Kernel (null space).** For a linear map $T:V\\to W$,
$$\\ker(T)=\\{ \\vec{v}\\in V : T(\\vec{v})=\\mathbf{0} \\}.$$
The kernel is always a **subspace** of $V$: it contains $\\mathbf{0}$, and is closed under addition and scalar multiplication (because $T$ is linear).

**Image (range / column space).**
$$\\text{Im}(T)=\\{ T(\\vec{v}) : \\vec{v}\\in V \\}.$$
The image is always a **subspace** of $W$. When $T(\\vec{x})=A\\vec{x}$, $\\text{Im}(T)$ equals the column space of $A$.

**Rank and nullity.**
$$\\text{rank}(T)=\\dim(\\text{Im}(T)), \\qquad \\text{nullity}(T)=\\dim(\\ker(T)).$$

**Rank-Nullity Theorem.** If $V$ is finite-dimensional,
$$\\text{rank}(T)+\\text{nullity}(T)=\\dim(V).$$
Intuition: every input direction either contributes to the output (rank) or is collapsed to zero (nullity).

**Injectivity, surjectivity, bijectivity.**
- **Injective (one-to-one):** $\\ker(T)=\\{\\mathbf{0}\\}$ — distinct inputs never collide.
- **Surjective (onto):** $\\text{Im}(T)=W$ — every target vector is hit.
- **Bijective (invertible):** injective **and** surjective. For square matrices $A_{n\\times n}$, bijective $\\Leftrightarrow$ $\\det(A)\\ne0$ $\\Leftrightarrow$ rank $=n$.""",
        "body_he_md": """**גרעין (מרחב אפסי).** עבור העתקה לינארית $T:V\\to W$,
$$\\ker(T)=\\{ \\vec{v}\\in V : T(\\vec{v})=\\mathbf{0} \\}.$$
הגרעין הוא תמיד **תת-מרחב** של $V$: מכיל $\\mathbf{0}$, וסגור לחיבור ולכפל בסקלר (כי $T$ לינארית).

**תמונה (טווח / מרחב עמודות).**
$$\\text{Im}(T)=\\{ T(\\vec{v}) : \\vec{v}\\in V \\}.$$
התמונה היא תמיד **תת-מרחב** של $W$. כאשר $T(\\vec{x})=A\\vec{x}$, $\\text{Im}(T)$ שווה למרחב העמודות של $A$.

**דרגה ואפסיות.**
$$\\text{rank}(T)=\\dim(\\text{Im}(T)), \\qquad \\text{nullity}(T)=\\dim(\\ker(T)).$$

**משפט הדרגה-אפסיות.** אם $V$ בעל ממד סופי,
$$\\text{rank}(T)+\\text{nullity}(T)=\\dim(V).$$
אינטואיציה: כל כיוון קלט או תורם לפלט (דרגה) או נמחץ לאפס (אפסיות).

**חד-חד-ערכיות, על, הפיכות.**
- **חד-חד-ערכית (חח\"ע):** $\\ker(T)=\\{\\mathbf{0}\\}$ — קלטים שונים לא מתנגשים.
- **על:** $\\text{Im}(T)=W$ — כל וקטור ב-$W$ מושג.
- **חד-חד-ערכית ועל (הפיכה):** חח\"ע **וגם** על. למטריצות ריבועיות $A_{n\\times n}$: הפיכה $\\Leftrightarrow$ $\\det(A)\\ne0$ $\\Leftrightarrow$ rank $=n$.""",
    },
    "theory": {
        "body_en_md": """Every linear map $T:\\mathbb{R}^n\\to\\mathbb{R}^m$ can be represented by an $m\\times n$ matrix $A$ via $T(\\vec{x})=A\\vec{x}$. Kernel and image then reduce to familiar matrix algorithms.

**Finding the kernel.** Solve the homogeneous system $A\\vec{x}=\\mathbf{0}$ by row reduction to RREF. Each **free variable** produces one basis vector of $\\ker(A)$: set one free variable to $1$, others to $0$, back-substitute. Nullity equals the number of free variables.

**Finding the image.** $\\text{Im}(A)$ is the span of the **columns** of $A$. After RREF, the **pivot column positions** identify which **original** columns (before row ops) form a basis. Never take pivot columns from the RREF matrix itself — row operations change column space.

**Rank.** Number of pivot columns $=$ rank $=\\dim(\\text{Im}(T))$. Also equals the number of linearly independent rows.

**Nullity.** $\\text{nullity}=n-\\text{rank}$ by rank-nullity, where $n=\\dim(\\mathbb{R}^n)$ is the number of columns (domain dimension).

**Injectivity test.** $T$ is injective iff $\\ker(T)=\\{\\mathbf{0}\\}$ iff nullity $=0$ iff every column of $A$ is pivot (full column rank when $n\\le m$).

**Surjectivity test.** $T$ is surjective iff $\\text{Im}(T)=\\mathbb{R}^m$ iff rank $=m$ (full row rank when $m\\le n$).

For non-square maps, injectivity and surjectivity are independent — a map can be one without the other.""",
        "body_he_md": """כל העתקה לינארית $T:\\mathbb{R}^n\\to\\mathbb{R}^m$ ניתנת לייצוג על ידי מטריצה $m\\times n$ דרך $T(\\vec{x})=A\\vec{x}$. גרעין ותמונה מתרגמים לאלגוריתמים מטריציוניים מוכרים.

**מציאת הגרעין.** פתרו את המערכת ההומогנית $A\\vec{x}=\\mathbf{0}$ בדירוג שורות ל-RREF. כל **משתנה חופשי** מייצר וקטור בסיס אחד ב-$\\ker(A)$: קבעו משתנה חופשי אחד ל-$1$, השאר ל-$0$, והציבו בחזרה. האפסיות שווה למספר המשתנים החופשיים.

**מציאת התמונה.** $\\text{Im}(A)$ הוא הפרישה של **עמודות** $A$. אחרי RREF, **מיקומי עמודות הציר** מזהים אילו עמודות **מקוריות** (לפני פעולות שורה) יוצרות בסיס. לעולם אל תיקחו עמודות ציר מה-RREF עצמו — פעולות שורה משנות את מרחב העמודות.

**דרגה.** מספר עמודות הציר $=$ rank $=\\dim(\\text{Im}(T))$. גם שווה למספר השורות הבלתי-תלויות.

**אפסיות.** $\\text{nullity}=n-\\text{rank}$ לפי משפט הדרגה-אפסיות, כאשר $n=\\dim(\\mathbb{R}^n)$ הוא מספר העמודות (ממד התחום).

**בדיקת חח\"ע.** $T$ חח\"ע אמ\"מ $\\ker(T)=\\{\\mathbf{0}\\}$ אמ\"מ nullity $=0$ אמ\"מ כל עמודה של $A$ היא ציר (דרגת עמודות מלאה כש-$n\\le m$).

**בדיקת על.** $T$ על אמ\"מ $\\text{Im}(T)=\\mathbb{R}^m$ אמ\"מ rank $=m$ (דרגת שורות מלאה כש-$m\\le n$).

בהעתקות לא-ריבועיות, חח\"ע ועל **בלתי-תלויים** — העתקה יכולה להיות אחת בלי השנייה.""",
    },
    "worked_example_1": {
        "body_en_md": """**Find $\\ker(T)$** for $T:\\mathbb{R}^2\\to\\mathbb{R}^2$ defined by $T(x,y)=(x+y,\\,2x+2y)$.

**Matrix form:** $A=\\begin{pmatrix}1&1\\\\2&2\\end{pmatrix}$, so $T(\\vec{x})=A\\vec{x}$.

### Move 1: Set up $A\\vec{x}=\\mathbf{0}$
Row-reduce:
$$\\begin{pmatrix}1&1\\\\2&2\\end{pmatrix} \\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&1\\\\0&0\\end{pmatrix}.$$
One pivot column, one free variable.

### Move 2: Parametrize solutions
From $x+y=0$ we get $x=-y$. Let $y=t$:
$$\\vec{x}=\\begin{pmatrix}-t\\\\t\\end{pmatrix}=t\\begin{pmatrix}-1\\\\1\\end{pmatrix}.$$

### Move 3: State the kernel
$$\\ker(T)=\\text{span}\\left\\{\\begin{pmatrix}-1\\\\1\\end{pmatrix}\\right\\}, \\qquad \\text{nullity}=1.$$

**Rank-nullity check:** rank $=1$ (one pivot), nullity $=1$, and $1+1=2=\\dim(\\mathbb{R}^2)$ ✓. The map collapses every vector onto the line $y=-x$ in the input before doubling in the output.

**Geometric reading:** Vectors on the line $y=-x$ are sent to $\\mathbf{0}$; vectors off that line are scaled onto the output line $\\text{span}\\{(1,2)^T\\}$. This preview connects kernel geometry to injectivity failures on the next checkpoint.

**Alternative basis:** $\\text{span}\\{(1,-1)^T\\}$ describes the same line — any nonzero scalar multiple is valid in a basis for a 1-dimensional kernel.""",
        "body_he_md": """**מצאו $\\ker(T)$** עבור $T:\\mathbb{R}^2\\to\\mathbb{R}^2$ המוגדרת על ידי $T(x,y)=(x+y,\\,2x+2y)$.

**צורה מטריציונית:** $A=\\begin{pmatrix}1&1\\\\2&2\\end{pmatrix}$, כלומר $T(\\vec{x})=A\\vec{x}$.

### צעד 1: הציבו $A\\vec{x}=\\mathbf{0}$
דרגו שורות:
$$\\begin{pmatrix}1&1\\\\2&2\\end{pmatrix} \\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&1\\\\0&0\\end{pmatrix}.$$
עמודת ציר אחת, משתנה חופשי אחד.

### צעד 2: פרמטריזציה של הפתרונות
מ-$x+y=0$ מתקבל $x=-y$. נסמן $y=t$:
$$\\vec{x}=\\begin{pmatrix}-t\\\\t\\end{pmatrix}=t\\begin{pmatrix}-1\\\\1\\end{pmatrix}.$$

### צעד 3: הציגו את הגרעין
$$\\ker(T)=\\text{span}\\left\\{\\begin{pmatrix}-1\\\\1\\end{pmatrix}\\right\\}, \\qquad \\text{nullity}=1.$$

**בדיקת משפט דרגה-אפסיות:** rank $=1$ (ציר אחד), nullity $=1$, ו-$1+1=2=\\dim(\\mathbb{R}^2)$ ✓. ההעתקה מכווצת כל וקטור על הישר $y=-x$ בקלט לפני ההכפלה בפלט.

**קריאה גיאומטרית:** וקטורים על הישר $y=-x$ נשלחים ל-$\\mathbf{0}$; וקטורים מחוץ לישר מוכפלים על ישר הפלט $\\text{span}\\{(1,2)^T\\}$. זה מקשר את גיאומטריית הגרעין לכשל חח\"ע בנקודת הביקורת הבאה.

**בסיס חלופי:** $\\text{span}\\{(1,-1)^T\\}$ מתאר את אותו ישר — כל כפולה במספר לא-אפס תקפה בבסיס לגרעין חד-ממדי.""",
    },
    "worked_example_2": {
        "body_en_md": """**Find a basis for $\\text{Im}(T)$** where
$$A=\\begin{pmatrix}1&0&2\\\\2&1&3\\\\0&1&-1\\end{pmatrix}.$$

### Move 1: Row-reduce $A$
$$\\begin{pmatrix}1&0&2\\\\2&1&3\\\\0&1&-1\\end{pmatrix} \\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&0&2\\\\0&1&-1\\\\0&1&-1\\end{pmatrix} \\xrightarrow{R_3-R_2} \\begin{pmatrix}1&0&2\\\\0&1&-1\\\\0&0&0\\end{pmatrix}.$$
Pivot columns: positions 1 and 2. Rank $=2$.

### Move 2: Extract basis from **original** columns
Pivot columns of the **original** $A$:
$$\\vec{v}_1=\\begin{pmatrix}1\\\\2\\\\0\\end{pmatrix}, \\qquad \\vec{v}_2=\\begin{pmatrix}0\\\\1\\\\1\\end{pmatrix}.$$
These span $\\text{Im}(T)$ — a plane through the origin in $\\mathbb{R}^3$.

### Move 3: Kernel dimension via rank-nullity
Domain dimension $n=3$, so nullity $=3-2=1$. One free variable in $Ax=0$: from RREF, $x_1=-2x_3$, $x_2=x_3$, so $\\ker(T)=\\text{span}\\{( -2,1,1)^T\\}$.

**Verify:** $A(-2,1,1)^T=(-2+2,\\,-4+1+3,\\,1-1)^T=(0,0,0)^T$ ✓.

**Why original columns?** Row operations such as $R_2\\leftarrow R_2-2R_1$ replace column 2 with a linear combination — the RREF column $(0,1,0)^T$ is **not** generally in $\\text{Im}(A)$. Pivot **positions** from RREF, columns from $A$: that rule prevents the most common exam error in image problems.

**Dimension summary:** $\\dim(\\ker)=1$, $\\dim(\\text{Im})=2$, and $1+2=3=n$ confirms rank-nullity for this $3\\times3$ example.""",
        "body_he_md": """**מצאו בסיס ל-$\\text{Im}(T)$** כאשר
$$A=\\begin{pmatrix}1&0&2\\\\2&1&3\\\\0&1&-1\\end{pmatrix}.$$

### צעד 1: דרגו את $A$
$$\\begin{pmatrix}1&0&2\\\\2&1&3\\\\0&1&-1\\end{pmatrix} \\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&0&2\\\\0&1&-1\\\\0&1&-1\\end{pmatrix} \\xrightarrow{R_3-R_2} \\begin{pmatrix}1&0&2\\\\0&1&-1\\\\0&0&0\\end{pmatrix}.$$
עמודות ציר: מיקומים 1 ו-2. rank $=2$.

### צעד 2: שליפת בסיס מעמודות **מקוריות**
עמודות הציר של $A$ **המקורית**:
$$\\vec{v}_1=\\begin{pmatrix}1\\\\2\\\\0\\end{pmatrix}, \\qquad \\vec{v}_2=\\begin{pmatrix}0\\\\1\\\\1\\end{pmatrix}.$$
אלה פורשים את $\\text{Im}(T)$ — מישור דרך הראשית ב-$\\mathbb{R}^3$.

### צעד 3: ממד הגרעין דרך משפט דרגה-אפסיות
ממד התחום $n=3$, לכן nullity $=3-2=1$. משתנה חופשי אחד ב-$Ax=0$: מ-RREF, $x_1=-2x_3$, $x_2=x_3$, ולכן $\\ker(T)=\\text{span}\\{(-2,1,1)^T\\}$.

**אימות:** $A(-2,1,1)^T=(0,0,0)^T$ ✓.

**למה עמודות מקוריות?** פעולות שורה כמו $R_2\\leftarrow R_2-2R_1$ מחליפות עמודה 2 בקומבינציה לינארית — עמודת RREF $(0,1,0)^T$ בכלל **לא** ב-$\\text{Im}(A)$. מיקומי ציר מ-RREF, עמודות מ-$A$: כלל זה מונע את טעות הבחינה הנפוצה ביותר בבעיות תמונה.

**סיכום ממדים:** $\\dim(\\ker)=1$, $\\dim(\\text{Im})=2$, ו-$1+2=3=n$ מאמת משפט דרגה-אפסיות לדוגמה $3\\times3$ זו.""",
    },
    "worked_example_3": {
        "body_en_md": """**Analyze $T:\\mathbb{R}^3\\to\\mathbb{R}^3$** with
$$A=\\begin{pmatrix}1&2&3\\\\0&1&4\\\\0&0&0\\end{pmatrix}.$$

### Move 1: Rank and nullity
RREF equals $A$ (already upper triangular). Two pivot columns → rank $=2$. Rank-nullity: nullity $=3-2=1$.

### Move 2: Kernel — solve $A\\vec{x}=\\mathbf{0}$
Row 2: $x_2+4x_3=0 \\Rightarrow x_2=-4x_3$. Row 1: $x_1+2x_2+3x_3=0 \\Rightarrow x_1-5x_3=0 \\Rightarrow x_1=5x_3$.
With $x_3=t$: $\\ker(T)=\\text{span}\\{(5,-4,1)^T\\}$. Since $\\ker\\ne\\{\\mathbf{0}\\}$, $T$ is **not injective**.

### Move 3: Image and surjectivity
Pivot columns 1 and 2 of the original $A$ give a basis: $\\{(1,0,0)^T,\\,(2,1,0)^T\\}$. $\\dim(\\text{Im})=2<3=\\dim(\\mathbb{R}^3)$, so $T$ is **not surjective** — vectors with a nonzero third component (e.g. $(0,0,1)^T$) are unreachable.

**Summary:** rank $=2$, nullity $=1$, neither injective nor surjective, hence not invertible.

**Exam pattern:** Upper-triangular matrices expose rank instantly (count nonzero rows on the diagonal chain). Always finish by stating injectivity, surjectivity, and whether an inverse exists — three separate conclusions from one RREF pass.""",
        "body_he_md": """**נתחו $T:\\mathbb{R}^3\\to\\mathbb{R}^3$** עם
$$A=\\begin{pmatrix}1&2&3\\\\0&1&4\\\\0&0&0\\end{pmatrix}.$$

### צעד 1: דרגה ואפסיות
RREF שווה ל-$A$ (כבר משולש עליון). שתי עמודות ציר → rank $=2$. משפט דרגה-אפסיות: nullity $=3-2=1$.

### צעד 2: גרעין — פתרו $A\\vec{x}=\\mathbf{0}$
שורה 2: $x_2+4x_3=0 \\Rightarrow x_2=-4x_3$. שורה 1: $x_1+2x_2+3x_3=0 \\Rightarrow x_1=5x_3$.
עם $x_3=t$: $\\ker(T)=\\text{span}\\{(5,-4,1)^T\\}$. מכיוון $\\ker\\ne\\{\\mathbf{0}\\}$, $T$ **אינה חח\"ע**.

### צעד 3: תמונה ועל
עמודות ציר 1 ו-2 של $A$ המקורית נותנות בסיס: $\\{(1,0,0)^T,\\,(2,1,0)^T\\}$. $\\dim(\\text{Im})=2<3$, ולכן $T$ **אינה על** — וקטורים עם רכיב שלישי שונה מאפס (למשל $(0,0,1)^T$) אינם ניתנים להשגה.

**סיכום:** rank $=2$, nullity $=1$, לא חח\"ע ולא על, ולכן לא הפיכה.

**דפוס בחינה:** מטריצות משולשות עליונות חושפות rank מיד (ספירת שורות לא-אפס בשרשרת האלכסון). סיימו תמיד בהצהרה על חח\"ע, על והאם קיימת הופכית — שלוש מסקנות נפרדות מדריגה אחת.""",
    },
    "method_guide": {
        "body_en_md": """| Goal | Method |
|---|---|
| Find $\\ker(T)$ | Row-reduce $A$; solve $A\\vec{x}=\\mathbf{0}$; free variables → basis vectors |
| Find $\\text{Im}(T)$ | Identify pivot column positions; take those columns from **original** $A$ |
| Compute rank | Count pivot columns in RREF |
| Compute nullity | $n - \\text{rank}$ or count free variables |
| Test injectivity | nullity $=0$ $\\Leftrightarrow$ $\\ker=\\{\\mathbf{0}\\}$ |
| Test surjectivity | rank $=\\dim(W)$ $\\Leftrightarrow$ $\\text{Im}=W$ |
| Test bijectivity (square) | rank $=n$ and nullity $=0$ $\\Leftrightarrow$ $\\det(A)\\ne0$ |

**Workflow:** (1) Write the matrix. (2) RREF once. (3) Read off rank and pivot positions. (4) Kernel from free variables; image from original pivot columns. (5) Apply rank-nullity as a consistency check.

**When to use:** Any problem asking about null space, column space, dimension, or whether a linear map is one-to-one / onto starts with this table.""",
        "body_he_md": """| מטרה | שיטה |
|---|---|
| מציאת $\\ker(T)$ | דרגו $A$; פתרו $A\\vec{x}=\\mathbf{0}$; משתנים חופשיים → וקטורי בסיס |
| מציאת $\\text{Im}(T)$ | זהו מיקומי עמודות ציר; קחו עמודות אלה מ-$A$ **המקורית** |
| חישוב rank | ספרו עמודות ציר ב-RREF |
| חישוב nullity | $n - \\text{rank}$ או ספירת משתנים חופשיים |
| בדיקת חח\"ע | nullity $=0$ $\\Leftrightarrow$ $\\ker=\\{\\mathbf{0}\\}$ |
| בדיקת על | rank $=\\dim(W)$ $\\Leftrightarrow$ $\\text{Im}=W$ |
| בדיקת הפיכות (ריבועית) | rank $=n$ ו-nullity $=0$ $\\Leftrightarrow$ $\\det(A)\\ne0$ |

**תהליך עבודה:** (1) כתבו את המטריצה. (2) RREF פעם אחת. (3) קראו rank ומיקומי ציר. (4) גרעין ממשתנים חופשיים; תמונה מעמודות ציר מקוריות. (5) אמתו עם משפט דרגה-אפסיות.

**מתי להשתמש:** כל בעיה על מרחב אפסי, מרחב עמודות, ממד, או חח\"ע/על מתחילה בטבלה זו.""",
    },
    "pitfall": {
        "body_en_md": """1. **Kernel basis from pivot columns.** Pivot columns span the **image**, not the kernel. Kernel vectors come from **free variables** in $A\\vec{x}=\\mathbf{0}$.

2. **Image basis from RREF columns.** Row operations alter column space. Always return to the **original** matrix for pivot-column bases.

3. **Confusing injectivity and surjectivity.** For $T:\\mathbb{R}^n\\to\\mathbb{R}^m$ with $n\\ne m$, one property does not imply the other. A wide matrix can be surjective but not injective; a tall matrix can be injective but not surjective.

4. **Rank-nullity domain vs codomain.** The theorem uses $\\dim(V)$ (domain), **not** $\\dim(W)$. Using $m$ instead of $n$ is a frequent exam deduction.

5. **Declaring bijective without checking both.** Full rank alone on a non-square matrix is impossible for bijectivity.

**Example misconception:** Taking columns $\\{(1,0,0)^T,(0,1,0)^T\\}$ from RREF as the image basis when the original pivot columns differ.

**Fix:** Mark pivot **positions**, then copy those columns from the starting matrix.""",
        "body_he_md": """1. **בסיס גרעין מעמודות ציר.** עמודות ציר פורשות את **התמונה**, לא את הגרעין. וקטורי גרעין מגיעים מ**משתנים חופשיים** ב-$A\\vec{x}=\\mathbf{0}$.

2. **בסיס תמונה מעמודות RREF.** פעולות שורה משנות את מרחב העמודות. חזרו תמיד ל**מטריצה המקורית** לבסיס עמודות ציר.

3. **בלבול חח\"ע ועל.** עבור $T:\\mathbb{R}^n\\to\\mathbb{R}^m$ כש-$n\\ne m$, תכונה אחת לא מרמזת על השנייה. מטריצה רחבה יכולה להיות על אך לא חח\"ע; גבוהה — חח\"ע אך לא על.

4. **תחום מול טווח במשפט דרגה-אפסיות.** המשפט משתמש ב-$\\dim(V)$ (תחום), **לא** ב-$\\dim(W)$. שימוש ב-$m$ במקום $n$ גורם לניכוי נקודות.

5. **הכרזה על הפיכות בלי שני תנאים.** דרגה מלאה במטריצה לא-ריבועית לא מספיקה להפיכות.

**דוגמת טעות:** לקיחת עמודות מ-RREF כבסיס תמונה כשעמודות המקור שונות.

**תיקון:** סמנו **מיקומי** ציר, והעתיקו עמודות אלה מהמטריצה ההתחלתית.""",
    },
    "why_matters": {
        "body_en_md": """Kernel and image are not abstract labels — they answer concrete questions in science and engineering.

**Systems of equations:** $\\ker(A)$ is the solution space of $A\\vec{x}=\\mathbf{0}$; $\\text{Im}(A)$ is the set of reachable right-hand sides for $A\\vec{x}=\\vec{b}$.

**Control and signals:** Unobservable states lie in the kernel of an output map; controllable outputs span the image of an input map.

**Data science:** The null space of a design matrix explains redundant features; the column space is the subspace your model can actually fit.

**Recommended next topics:**
- `concept:la_vector_spaces` **Vector Spaces** — subspace proofs underpin kernel/image theorems.
- `concept:la_matrices` **Matrices & Linear Systems** — RREF skills used here.

**Exam transfer:** University courses expect you to move fluently between map language ($T$, $\\ker$, $\\text{Im}$) and matrix language ($A$, null space, column space) without hesitation.""",
        "body_he_md": """גרעין ותמונה אינם תוויות מופשטות — הם עונים על שאלות קונקרטיות במדע והנדסה.

**מערכות משוואות:** $\\ker(A)$ הוא מרחב הפתרונות של $A\\vec{x}=\\mathbf{0}$; $\\text{Im}(A)$ הוא קבוצת צדדים ימניים ניתנים להשגה עבור $A\\vec{x}=\\vec{b}$.

**בקרה ואותות:** מצבים לא-נצפים שוכנים בגרעין של מפת פלט; פלטים נשלטים פורשים את תמונת מפת קלט.

**מדע נתונים:** מרחב האפס של מטריצת עיצוב מסביר תכונות עודפות; מרחב העמודות הוא תת-המרחב שהמודל יכול להתאים.

**נושאים מומלצים להמשך:**
- `concept:la_vector_spaces` **מרחבי וקטורים** — הוכחות תת-מרחב תומכות במשפטי גרעין/תמונה.
- `concept:la_matrices` **מטריצות ומערכות לינאריות** — מיומנויות RREF בשימוש כאן.

**העברה לבחינה:** קורסים באוניברסיטה מצפים למעבר חלק בין שפת העתקות ($T$, $\\ker$, $\\text{Im}$) לשפת מטריצות ($A$, מרחב אפס, מרחב עמודות).""",
    },
    "before_exam": {
        "body_en_md": """**Quick checklist before the exam:**
- **Kernel:** row-reduce $A$; solve $A\\vec{x}=\\mathbf{0}$; each free variable → one basis vector.
- **Image:** pivot positions in RREF → corresponding columns of **original** $A$.
- **Rank** $=\\dim(\\text{Im})$ $=$ number of pivots. **Nullity** $=\\dim(\\ker)$ $=n-\\text{rank}$.
- **Rank-nullity:** $\\text{rank}+\\text{nullity}=\\dim(V)$ — always use domain dimension $n$.
- **Injective** iff nullity $=0$. **Surjective** iff rank $=\\dim(W)$. **Bijective** (square) iff both.
- **Non-square maps:** injectivity and surjectivity are separate checks — do not assume one from the other.

**Last review:** State each criterion aloud once, then solve one $3\\times4$ example computing $\\ker$, $\\text{Im}$, rank, and nullity without notes.""",
        "body_he_md": """**רשימת בדיקה מהירה לפני הבחינה:**
- **גרעין:** דרגו $A$; פתרו $A\\vec{x}=\\mathbf{0}$; כל משתנה חופשי → וקטור בסיס.
- **תמונה:** מיקומי ציר ב-RREF → עמודות מתאימות של $A$ **המקורית**.
- **Rank** $=\\dim(\\text{Im})$ $=$ מספר צירים. **Nullity** $=\\dim(\\ker)$ $=n-\\text{rank}$.
- **משפט דרגה-אפסיות:** $\\text{rank}+\\text{nullity}=\\dim(V)$ — תמיד ממד התחום $n$.
- **חח\"ע** אמ\"מ nullity $=0$. **על** אמ\"מ rank $=\\dim(W)$. **הפיכה** (ריבועית) אמ\"מ שניהם.
- **העתקות לא-ריבועיות:** בדקו חח\"ע ועל בנפרד — אל תניחו אחד מהשני.

**חזרה אחרונה:** אמרו כל קריטריון בקול פעם אחת, ואז פתרו דוגמה $3\\times4$ — $\\ker$, $\\text{Im}$, rank, nullity — בלי רשימות.""",
    },
    "summary": {
        "body_en_md": """- $\\ker(T)$ and $\\text{Im}(T)$ are subspaces of domain and codomain; compute them via $A\\vec{x}=\\mathbf{0}$ and pivot columns of $A$.
- **Rank-nullity:** $\\text{rank}+\\text{nullity}=\\dim(V)$ links output dimension to collapsed directions.
- **Injective:** trivial kernel (nullity $=0$). **Surjective:** full image (rank $=\\dim(W)$). **Bijective:** both (for square $A$, $\\det\\ne0$).
- Image bases come from **original** pivot columns; kernel bases from **free variables**.

**Takeaway:** Given any matrix, you should now produce kernel basis, image basis, rank, nullity, and injectivity/surjectivity verdict in one organized pass.""",
        "body_he_md": """- $\\ker(T)$ ו-$\\text{Im}(T)$ הם תת-מרחבים של תחום וטווח; מחשבים דרך $A\\vec{x}=\\mathbf{0}$ ועמודות ציר של $A$.
- **משפט דרגה-אפסיות:** $\\text{rank}+\\text{nullity}=\\dim(V)$ מקשר ממד פלט לכיוונים שנמחצו.
- **חח\"ע:** גרעין טריוויאלי (nullity $=0$). **על:** תמונה מלאה (rank $=\\dim(W)$). **הפיכה:** שניהם (למטריצה ריבועית, $\\det\\ne0$).
- בסיס תמונה מעמודות ציר **מקוריות**; בסיס גרעין מ**משתנים חופשיים**.

**מסקנה:** עבור כל מטריצה, אתם אמורים להפיק בסיס גרעין, בסיס תמונה, rank, nullity ופסק דין חח\"ע/על במעבר מסודר אחד.""",
    },
}

CHECKPOINTS = {
    0: {
        "checkpoint_solution_en": """**Injective?** No. $\\ker(T)=\\text{span}\\{(-1,1)^T\\}\\ne\\{\\mathbf{0}\\}$, so nullity $=1$. Two different inputs (e.g. $(1,-1)^T$ and $(2,-2)^T$) both map to $(0,0)^T$ — the map is not one-to-one.

**Surjective?** No. $\\text{Im}(T)$ is the line $\\text{span}\\{(1,2)^T\\}$ in $\\mathbb{R}^2$, a 1-dimensional subspace. Vectors not on that line (e.g. $(1,0)^T$) are never outputs. Rank $=1<2=\\dim(\\mathbb{R}^2)$.

**Rank-nullity confirmation:** $1+1=2=\\dim(\\mathbb{R}^2)$ ✓.""",
        "checkpoint_solution_he": """**חח\"ע?** לא. $\\ker(T)=\\text{span}\\{(-1,1)^T\\}\\ne\\{\\mathbf{0}\\}$, ולכן nullity $=1$. שני קלטים שונים (למשל $(1,-1)^T$ ו-$(2,-2)^T$) שניהם ממופים ל-$(0,0)^T$ — ההעתקה אינה חד-חד-ערכית.

**על?** לא. $\\text{Im}(T)$ הוא הישר $\\text{span}\\{(1,2)^T\\}$ ב-$\\mathbb{R}^2$, תת-מרחב חד-ממדי. וקטורים שלא על הישר (למשל $(1,0)^T$) אינם פלטים. rank $=1<2$.

**אימות משפט דרגה-אפסיות:** $1+1=2=\\dim(\\mathbb{R}^2)$ ✓.""",
    },
    1: {
        "checkpoint_solution_en": """Apply the **rank-nullity theorem** with domain dimension $n=5$ (five columns of a $4\\times5$ matrix):
$$\\text{rank}(A)+\\text{nullity}(A)=\\dim(\\mathbb{R}^5)=5.$$
Given rank $=3$:
$$\\text{nullity}(A)=5-3=2.$$
So $\\ker(A)$ is a 2-dimensional plane through the origin in $\\mathbb{R}^5$, and exactly two free variables appear when solving $A\\vec{x}=\\mathbf{0}$.""",
        "checkpoint_solution_he": """יישמו את **משפט הדרגה-אפסיות** עם ממד תחום $n=5$ (חמש עמודות במטריצה $4\\times5$):
$$\\text{rank}(A)+\\text{nullity}(A)=\\dim(\\mathbb{R}^5)=5.$$
נתון rank $=3$:
$$\\text{nullity}(A)=5-3=2.$$
לכן $\\ker(A)$ הוא מישור דו-ממדי דרך הראשית ב-$\\mathbb{R}^5$, ושני משתנים חופשיים מופיעים בפתרון $A\\vec{x}=\\mathbf{0}$.""",
    },
}

EXPLANATIONS = [
    fmt_expl(
        "A map is **injective** (one-to-one) precisely when no two distinct inputs share the same output. For linear maps this is equivalent to $\\ker(T)=\\{\\mathbf{0}\\}$: any nonzero vector in the kernel would create a collision with $\\mathbf{0}$. Option B states exactly this criterion.",
        "When you see \"injective iff\", translate immediately to kernel language. Scan the options for $\\ker(T)=\\{\\mathbf{0}\\}$ versus conditions about the image or rank alone.",
        "Choosing Im$(T)=W$ (surjectivity) or $\\ker(T)=V$ (everything maps to zero — only the zero map). Another trap: rank $=0$, which means the map sends everything to zero, the opposite of injectivity.",
        "Write on scratch paper: injective $\\Leftrightarrow$ nullity $=0$. Cross out any option mentioning the codomain dimension before checking the kernel.",
        "העתקה **חח\"ע** (חד-חד-ערכית) בדיוק כשאין שני קלטים שונים עם אותו פלט. בהעתקות לינאריות זה שקול ל-$\\ker(T)=\\{\\mathbf{0}\\}$: כל וקטור לא-אפס בגרעין יוצר התנגשות עם $\\mathbf{0}$. אפשרות ב' מציינת בדיוק קריטריון זה.",
        "כשמופיע \"חח\"ע אמ\"מ\", תרגמו מיד לשפת גרעין. חפשו $\\ker(T)=\\{\\mathbf{0}\\}$ לעומת תנאים על תמונה או rank בלבד.",
        "בחירה ב-Im$(T)=W$ (על) או $\\ker(T)=V$ (הכל מתאפס — רק העתקת האפס). מלכודת נוספת: rank $=0$, הפכי לחח\"ע.",
        "כתבו: חח\"ע $\\Leftrightarrow$ nullity $=0$. סמנו אפשרויות שמדברות על ממד הטווח לפני בדיקת הגרעין.",
    ),
    fmt_expl(
        "The map $T(x,y)=(x+y,x+y)$ satisfies linearity: $T((x_1,y_1)+(x_2,y_2))=((x_1+x_2)+(y_1+y_2),\\ldots)=T(x_1,y_1)+T(x_2,y_2)$, and $T(\\alpha(x,y))=\\alpha T(x,y)$ because both coordinates scale equally. A map can be linear yet have a nontrivial kernel — linearity does not mean injective.",
        "Test linearity by checking whether $T$ respects addition and scalar multiplication, or equivalently whether $T(a\\vec{u}+b\\vec{v})=aT(\\vec{u})+bT(\\vec{v})$. Do not confuse \"looks like a formula\" with \"preserves structure\".",
        "Answering \"no\" because both output coordinates are equal — that is a property of this particular map, not a violation of linearity. Another error: checking one point numerically instead of the general identity.",
        "Bagrut and first-year linear algebra often pair \"is it linear?\" with \"find the kernel\" in consecutive parts — master the definition before computing subspaces.",
        "ההעתקה $T(x,y)=(x+y,x+y)$ מקיימת לינאריות: $T((x_1,y_1)+(x_2,y_2))=T(x_1,y_1)+T(x_2,y_2)$, ו-$T(\\alpha(x,y))=\\alpha T(x,y)$ כי שני הרכיבים מוכפלים באותו אופן. העתקה יכולה להיות לינארית ועדיין עם גרעין לא-טריוויאלי.",
        "בדקו לינאריות: האם $T$ שומרת חיבור וכפל בסקלר, או שקול ל-$T(a\\vec{u}+b\\vec{v})=aT(\\vec{u})+bT(\\vec{v})$. אל תבלבלו \"נראה כמו נוסחה\" עם \"שומר מבנה\".",
        "תשובה \"לא\" כי שני רכיבי הפלט שווים — זו תכונה של העתקה זו, לא הפרת לינאריות. טעות נוספת: בדיקה נקודתית במקום זהות כללית.",
        "בבגרות ובשנה א' לינארית לעיתים \"האם לינארית?\" ו\"מצא גרעין\" ברצף — שלוטו בהגדרה לפני חישוב תת-מרחבים.",
    ),
    fmt_expl(
        "Both output equations $x+y=0$ and $2x+2y=0$ reduce to the same constraint, giving $x=-y$. Parameterizing with $y=t$ yields $\\ker(T)=\\text{span}\\{(-1,1)^T\\}$. Any nonzero scalar multiple is an equivalent basis description.",
        "For kernel problems, write $T(\\vec{x})=\\mathbf{0}$ as a linear system, row-reduce, and express pivot variables in terms of free ones. One free variable in $\\mathbb{R}^2$ means a 1-dimensional kernel (a line through the origin).",
        "Using only the first equation and forgetting the second is OK here because they are dependent — but in general you must satisfy **all** rows. Another slip: writing $\\ker=\\{(1,-1)^T\\}$ without span notation when infinitely many multiples exist.",
        "Always verify: plug a proposed kernel vector back into $T$ and confirm the output is $\\mathbf{0}$. One substitution catches sign errors instantly.",
        "שתי משוואות הפלט $x+y=0$ ו-$2x+2y=0$ מתמצות לאותו אילוץ, $x=-y$. עם $y=t$ מתקבל $\\ker(T)=\\text{span}\\{(-1,1)^T\\}$. כל כפולה סקלרית לא-אפס היא תיאור בסיס שקול.",
        "בבעיות גרעין, כתבו $T(\\vec{x})=\\mathbf{0}$ כמערכת, דרגו, והביעו משתני ציר במונחי חופשיים. משתנה חופשי אחד ב-$\\mathbb{R}^2$ ⇒ גרעין חד-ממדי (ישר דרך הראשית).",
        "שימוש רק במשוואה הראשונה — כאן זה מספיק כי הן תלויות, אבל בכלל צריך לספק **כל** השורות. טעות: $\\ker=\\{(1,-1)^T\\}$ בלי span כשיש אינסוף כפולות.",
        "אמתו: הציבו וקטור גרעין מוצע ב-$T$ וודאו פלט $\\mathbf{0}$. הצבה אחת תופסת טעויות סימן.",
    ),
    fmt_expl(
        "The identity matrix $I$ satisfies $I\\vec{x}=\\vec{x}$, so $I\\vec{x}=\\mathbf{0}$ forces $\\vec{x}=\\mathbf{0}$. Therefore $\\ker(I)=\\{\\mathbf{0}\\}$, nullity $=0$, and the identity map is injective (in fact bijective on $\\mathbb{R}^2$).",
        "Recognize standard maps quickly: $I$ (only zero in kernel), projection matrices (large kernel), rotation matrices (trivial kernel). For $\\ker(I)$, no row reduction is needed — the answer is immediate from the definition of identity.",
        "Answering \"all of $\\mathbb{R}^2$\" by confusing kernel with image. Another error: $\\ker(I)=\\{1\\}$ or listing basis vectors when the only element is the zero vector.",
        "Memorize: $\\ker(I)=\\{\\mathbf{0}\\}$, $\\text{Im}(I)=\\mathbb{R}^n$, rank $=n$, nullity $=0$. These four facts appear as quick-check questions on every exam.",
        "מטריצת היחידה $I$ מקיימת $I\\vec{x}=\\vec{x}$, ולכן $I\\vec{x}=\\mathbf{0}$ מכריח $\\vec{x}=\\mathbf{0}$. לכן $\\ker(I)=\\{\\mathbf{0}\\}$, nullity $=0$, והעתקת היחידה חח\"ע (ואף הפיכה על $\\mathbb{R}^2$).",
        "זהו העתקות סטנדרטיות: $I$ (רק אפס בגרעין), מטריצות הטלה (גרעין גדול), סיבוב (גרעין טריוויאלי). ל-$\\ker(I)$ אין צורך בדירוג — התשובה מיד מההגדרה.",
        "תשובה \"כל $\\mathbb{R}^2$\" — בלבול גרעין ותמונה. טעות נוספת: $\\ker(I)=\\{1\\}$ או רשימת בסיס כשהאיבר היחיד הוא $\\mathbf{0}$.",
        "שיננו: $\\ker(I)=\\{\\mathbf{0}\\}$, $\\text{Im}(I)=\\mathbb{R}^n$, rank $=n$, nullity $=0$. ארבעת העובדות האלה חוזרות בכל בחינה.",
    ),
    fmt_expl(
        "Rank-nullity states $\\text{rank}+\\text{nullity}=\\dim(V)$ where $V$ is the **domain**. A $3\\times4$ matrix maps $\\mathbb{R}^4\\to\\mathbb{R}^3$, so $n=4$ (column count), not $3$. With rank $=2$: nullity $=4-2=2$.",
        "Before computing nullity, identify $n$ = number of columns = $\\dim(\\text{domain})$. Row count $m$ governs surjectivity (rank $=m$?), not the rank-nullity sum's right-hand side.",
        "Using $n=3$ (row count) and getting nullity $=1$. Another trap: subtracting rank from $m$ instead of from the domain dimension.",
        "On every rank-nullity problem, write \"$n=$ ___ columns\" first. Examiners deliberately use non-square matrices to test whether you know which dimension enters the theorem.",
        "משפט דרגה-אפסיות: $\\text{rank}+\\text{nullity}=\\dim(V)$ כאשר $V$ הוא **התחום**. מטריצה $3\\times4$ ממפה $\\mathbb{R}^4\\to\\mathbb{R}^3$, ולכן $n=4$ (מספר עמודות), לא $3$. עם rank $=2$: nullity $=4-2=2$.",
        "לפני חישוב nullity, זהו $n$ = מספר עמודות = $\\dim(\\text{תחום})$. מספר שורות $m$ קובע על (rank $=m$?), לא את צד ימין של המשפט.",
        "שימוש ב-$n=3$ (שורות) ו-nullity $=1$. מלכודת: חיסור rank מ-$m$ במקום ממד התחום.",
        "בכל בעיית דרגה-אפסיות, כתבו \"$n=$ ___ עמודות\" קודם. מרצים משתמשים במטריצות לא-ריבועיות כדי לבדוק איזה ממד נכנס למשפט.",
    ),
    fmt_expl(
        "RREF of $\\begin{pmatrix}1&-1\\\\-1&1\\end{pmatrix}$ is $\\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}$: one pivot, one free variable. Kernel: $x=y=t$, so $\\ker=\\text{span}\\{(1,1)^T\\}$. Image: pivot column 1 of the original matrix gives $\\text{span}\\{(1,-1)^T\\}$. Rank $=1$, nullity $=1$, and $1+1=2$.",
        "One RREF pass yields rank, pivot positions, kernel parametrization, and image basis. Read pivot **positions**, then fetch those columns from the **original** $A$ for the image.",
        "Taking RREF columns as the image basis — here they happen to match, but the method is wrong in general. Reporting rank $=2$ by counting rows instead of pivots.",
        "After finding $\\ker$ and $\\text{Im}$, always verify rank-nullity as a free consistency check — it catches arithmetic slips before you move on.",
        "RREF של $\\begin{pmatrix}1&-1\\\\-1&1\\end{pmatrix}$ הוא $\\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}$: ציר אחד, משתנה חופשי. גרעין: $x=y=t$, $\\ker=\\text{span}\\{(1,1)^T\\}$. תמונה: עמודת ציר 1 מהמקור $\\text{span}\\{(1,-1)^T\\}$. rank $=1$, nullity $=1$, $1+1=2$.",
        "דריגה אחת נותנת rank, מיקומי ציר, פרמטריזציית גרעין ובסיס תמונה. קראו **מיקומי** ציר, ושלפו עמודות אלה מ-$A$ **המקורית** לתמונה.",
        "לקיחת עמודות RREF כבסיס תמונה — כאן זה מקרה, אבל השיטה שגויה בכלל. rank $=2$ מספירת שורות.",
        "אחרי $\\ker$ ו-$\\text{Im}$, אמתו משפט דרגה-אפסיות — זה תופס טעויות חישוב לפני שממשיכים.",
    ),
    fmt_expl(
        "For the matrix in exercise e5, rank $=1$ and nullity $=1$. Domain $\\mathbb{R}^2$ has dimension $2$, so rank $+$ nullity $=1+1=2=\\dim(\\mathbb{R}^2)$ — the rank-nullity theorem is satisfied. This confirms your kernel and image dimensions are consistent.",
        "Verification problems test whether you understand the theorem as a balance law, not just a formula to plug numbers into. Identify rank and nullity separately, then check their sum against $\\dim(V)$.",
        "Using $\\dim(\\mathbb{R}^3)$ or the row count on the right-hand side. Another slip: verifying $1+1=3$ and moving on without re-checking rank computation.",
        "When a problem says \"verify rank-nullity\", write the three quantities explicitly: rank __, nullity __, $\\dim(V)$ __, then the sum. Partial credit often requires showing the setup even if earlier parts had errors.",
        "למטריצה בתרגיל e5, rank $=1$ ו-nullity $=1$. התחום $\\mathbb{R}^2$ בממד $2$, ולכן rank $+$ nullity $=1+1=2=\\dim(\\mathbb{R}^2)$ — משפט דרגה-אפסיות מתקיים. זה מאשר שממדי הגרעין והתמונה עקביים.",
        "בעיות אימות בודקות הבנה של המשפט כחוק balance, לא רק נוסחה. זהו rank ו-nullity בנפרד, ובדקו סכום מול $\\dim(V)$.",
        "שימוש ב-$\\dim(\\mathbb{R}^3)$ או במספר שורות בצד ימין. אימות $1+1=3$ בלי לבדוק מחדש את rank.",
        "כש\"אמתו משפט דרגה-אפסיות\", כתבו שלושה: rank __, nullity __, $\\dim(V)$ __, ואז סכום. נקודות חלקיות דורשות הצגת ההכנה.",
    ),
    fmt_expl(
        "RREF of $\\begin{pmatrix}1&0\\\\0&1\\\\1&1\\end{pmatrix}$ is $\\begin{pmatrix}1&0\\\\0&1\\\\0&0\\end{pmatrix}$: two pivots, no free variables. The only solution to $A\\vec{x}=\\mathbf{0}$ is $\\vec{x}=\\mathbf{0}$, so $\\ker(A)=\\{\\mathbf{0}\\}$ and $T$ is **injective**. Note $T:\\mathbb{R}^2\\to\\mathbb{R}^3$ cannot be surjective (rank $\\le2<3$).",
        "Injectivity is a property of the domain — ask whether anything besides zero collapses. Full column rank (all columns pivot) on an $m\\times n$ matrix with $n\\le m$ signals injectivity.",
        "Concluding surjective because RREF has no zero rows — the codomain is $\\mathbb{R}^3$, so surjectivity requires rank $=3$, impossible from two columns. Another error: confusing \"consistent system\" with \"onto map\".",
        "For non-square maps, answer injectivity and surjectivity in **separate sentences**. Examiners love $2\\to3$ embeddings that are injective but not surjective.",
        "RREF של $\\begin{pmatrix}1&0\\\\0&1\\\\1&1\\end{pmatrix}$ הוא $\\begin{pmatrix}1&0\\\\0&1\\\\0&0\\end{pmatrix}$: שני צירים, אין משתנים חופשיים. הפתרון היחיד ל-$A\\vec{x}=\\mathbf{0}$ הוא $\\vec{x}=\\mathbf{0}$, $\\ker=\\{\\mathbf{0}\\}$, $T$ **חח\"ע**. שימו לב: $T:\\mathbb{R}^2\\to\\mathbb{R}^3$ לא יכולה להיות על (rank $\\le2<3$).",
        "חח\"ע הוא תכונה של התחום — האם משהו מלבד אפס מתכווץ. דרגת עמודות מלאה (כל העמודות ציר) ב-$m\\times n$ עם $n\\le m$ ⇒ חח\"ע.",
        "מסקנה \"על\" כי אין שורות אפס — הטווח $\\mathbb{R}^3$, על דורש rank $=3$, בלתי אפשרי משני עמודות. בלבול \"מערכת עקבית\" עם \"העתקה על\".",
        "בהעתקות לא-ריבועיות, ענו חח\"ע ועל ב**משפטים נפרדים**. מרצים אוהבים שיכונים $2\\to3$ חח\"ע אך לא על.",
    ),
    fmt_expl(
        "The projection $P(x,y,z)=(x,y,0)$ maps every vector to the $xy$-plane. $\\text{Im}(P)=\\{(x,y,0):x,y\\in\\mathbb{R}\\}$ is a 2-dimensional subspace of $\\mathbb{R}^3$, strictly smaller than the codomain. Vector $(0,0,1)$ is not in the image, so $P$ is **not surjective**. It is also not injective: $P(0,0,1)=P(0,0,2)=(0,0,0)$.",
        "Surjectivity asks whether **every** target vector is hit. Exhibit one concrete vector outside the image to disprove surjectivity — here any nonzero $z$-direction vector works.",
        "Answering \"yes\" because $P$ feels like it covers \"most\" of space — the image misses an entire dimension. Another slip: checking surjectivity by counting equations instead of comparing rank to $\\dim(W)$.",
        "Projection maps are the standard counterexample for \"linear but not invertible.\" Link rank $=2$, nullity $=1$, not injective, not surjective in one sentence for full credit.",
        "ההטלה $P(x,y,z)=(x,y,0)$ ממפה כל וקטור למישור $xy$. $\\text{Im}(P)=\\{(x,y,0)\\}$ הוא תת-מרחב דו-ממדי ב-$\\mathbb{R}^3$, קטן מהטווח. $(0,0,1)$ לא בתמונה, ולכן $P$ **אינה על**. גם לא חח\"ע: $P(0,0,1)=P(0,0,2)=(0,0,0)$.",
        "על שואל האם **כל** וקטור בטווח מושג. הציגו וקטור קונקרטי מחוץ לתמונה — כאן כל וקטור בכיוון $z$.",
        "תשובה \"כן\" כי $P$ \"מכסה רוב\" המרחב — התמונה מפספסת ממד שלם. בדיקת על ע\"י ספירת משוואות במקום rank מול $\\dim(W)$.",
        "הטלות הן דוגמת-נגד סטנדרטית ל\"לינארית אך לא הפיכה\". קשרו rank $=2$, nullity $=1$, לא חח\"ע, לא על במשפט אחד לניקוד מלא.",
    ),
]

EXERCISE_SET_BODY = {
    "body_en_md": """Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.

These drills mirror the lesson workflow: verify linearity, compute $\\ker(T)$ and $\\text{Im}(T)$, apply rank-nullity, and decide injectivity/surjectivity. Keep one RREF pass per matrix and always take image bases from **original** pivot columns.""",
    "body_he_md": """פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.

התרגילים חוזרים על תהליך השיעור: אימות לינאריות, חישוב $\\ker(T)$ ו-$\\text{Im}(T)$, יישום משפט דרגה-אפסיות, וקביעת חח\"ע/על. בצעו דירוג RREF אחד לכל מטריצה, וקחו בסיס תמונה מעמודות **מקוריות** של ציר.""",
}

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1:** Check additivity. $T((x_1,y_1)+(x_2,y_2))=T(x_1+x_2,y_1+y_2)=((x_1+x_2)+(y_1+y_2),\\,(x_1+x_2)+(y_1+y_2))=(x_1+y_1,x_1+y_1)+(x_2+y_2,x_2+y_2)=T(x_1,y_1)+T(x_2,y_2)$.\n\n**Step 2:** Check homogeneity. $T(\\alpha(x,y))=(\\alpha x+\\alpha y,\\,\\alpha x+\\alpha y)=\\alpha(x+y,x+y)=\\alpha T(x,y)$.\n\n**Answer:** Yes, $T$ is linear.",
        "solution_he": "**צעד 1:** בדיקת חיבור. $T((x_1,y_1)+(x_2,y_2))=T(x_1+x_2,y_1+y_2)=T(x_1,y_1)+T(x_2,y_2)$.\n\n**צעד 2:** בדיקת כפל בסקלר. $T(\\alpha(x,y))=\\alpha T(x,y)$.\n\n**תשובה:** כן, $T$ לינארית.",
    },
    "e2": {
        "solution_en": "**Step 1:** Set $T(x,y)=(0,0)$. Both coordinates give $x+y=0$, so $x=-y$.\n\n**Step 2:** Parametrize with $y=t$: $\\vec{x}=t(-1,1)^T$.\n\n**Answer:** $\\ker(T)=\\text{span}\\{(-1,1)^T\\}$, nullity $=1$.",
        "solution_he": "**צעד 1:** הציבו $T(x,y)=(0,0)$. משני הרכיבים: $x+y=0$, כלומר $x=-y$.\n\n**צעד 2:** עם $y=t$: $\\vec{x}=t(-1,1)^T$.\n\n**תשובה:** $\\ker(T)=\\text{span}\\{(-1,1)^T\\}$, nullity $=1$.",
    },
    "e3": {
        "solution_en": "**Step 1:** Identity satisfies $I\\vec{x}=\\vec{x}$, so $I\\vec{x}=\\mathbf{0}$ implies $\\vec{x}=\\mathbf{0}$.\n\n**Answer:** $\\ker(I)=\\{\\mathbf{0}\\}$, nullity $=0$. The identity is injective.",
        "solution_he": "**צעד 1:** $I\\vec{x}=\\vec{x}$, ולכן $I\\vec{x}=\\mathbf{0}$ מכריח $\\vec{x}=\\mathbf{0}$.\n\n**תשובה:** $\\ker(I)=\\{\\mathbf{0}\\}$, nullity $=0$. העתקת היחידה חח\"ע.",
    },
    "e4": {
        "solution_en": "**Step 1:** Domain dimension $n=4$ (four columns in a $3\\times4$ matrix).\n\n**Step 2:** Rank-nullity: nullity $=n-\\text{rank}=4-2=2$.\n\n**Answer:** nullity $=2$.",
        "solution_he": "**צעד 1:** ממד תחום $n=4$ (ארבע עמודות במטריצה $3\\times4$).\n\n**צעד 2:** משפט דרגה-אפסיות: nullity $=4-2=2$.\n\n**תשובה:** nullity $=2$.",
    },
    "e5": {
        "solution_en": "**Step 1:** RREF: $\\begin{pmatrix}1&-1\\\\-1&1\\end{pmatrix}\\to\\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}$. Rank $=1$, one free variable.\n\n**Step 2:** Kernel: $x=y=t$, so $\\ker=\\text{span}\\{(1,1)^T\\}$.\n\n**Step 3:** Image: pivot column 1 of original $A$ gives $\\text{Im}=\\text{span}\\{(1,-1)^T\\}$.\n\n**Answer:** rank $=1$, nullity $=1$.",
        "solution_he": "**צעד 1:** RREF: $\\begin{pmatrix}1&-1\\\\-1&1\\end{pmatrix}\\to\\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}$. rank $=1$.\n\n**צעד 2:** גרעין: $x=y=t$, $\\ker=\\text{span}\\{(1,1)^T\\}$.\n\n**צעד 3:** תמונה: עמודת ציר 1 מהמקור $\\text{span}\\{(1,-1)^T\\}$.\n\n**תשובה:** rank $=1$, nullity $=1$.",
    },
    "e6": {
        "solution_en": "**Step 1:** From e5: rank $=1$, nullity $=1$.\n\n**Step 2:** Domain $\\mathbb{R}^2$ has dimension $2$, so rank $+$ nullity $=1+1=2$.\n\n**Answer:** Rank-nullity verified ✓.",
        "solution_he": "**צעד 1:** מ-e5: rank $=1$, nullity $=1$.\n\n**צעד 2:** $\\dim(\\mathbb{R}^2)=2$, ולכן $1+1=2$.\n\n**תשובה:** משפט דרגה-אפסיות מתקיים ✓.",
    },
    "e7": {
        "solution_en": "**Step 1:** RREF of $\\begin{pmatrix}1&0\\\\0&1\\\\1&1\\end{pmatrix}$ is $\\begin{pmatrix}1&0\\\\0&1\\\\0&0\\end{pmatrix}$: two pivots, no free variables.\n\n**Step 2:** Only solution to $A\\vec{x}=\\mathbf{0}$ is $\\vec{x}=\\mathbf{0}$, so $\\ker=\\{\\mathbf{0}\\}$.\n\n**Answer:** $T$ is **injective** (not surjective onto $\\mathbb{R}^3$).",
        "solution_he": "**צעד 1:** RREF: $\\begin{pmatrix}1&0\\\\0&1\\\\0&0\\end{pmatrix}$ — שני צירים, אין משתנים חופשיים.\n\n**צעד 2:** $\\ker=\\{\\mathbf{0}\\}$.\n\n**תשובה:** $T$ **חח\"ע** (לא על $\\mathbb{R}^3$).",
    },
    "e8": {
        "solution_en": "**Step 1:** $\\text{Im}(P)=\\{(x,y,0):x,y\\in\\mathbb{R}\\}$ is the $xy$-plane, a 2D subspace of $\\mathbb{R}^3$.\n\n**Step 2:** Vector $(0,0,1)\\notin\\text{Im}(P)$, so $P$ cannot be surjective.\n\n**Answer:** **Not surjective.**",
        "solution_he": "**צעד 1:** $\\text{Im}(P)=\\{(x,y,0)\\}$ — מישור $xy$, תת-מרחב דו-ממדי ב-$\\mathbb{R}^3$.\n\n**צעד 2:** $(0,0,1)\\notin\\text{Im}(P)$, ולכן $P$ לא על.\n\n**תשובה:** **לא על.**",
    },
    "e9": {
        "solution_en": "**Step 1:** Square $n\\times n$ with rank $=n$ gives nullity $=n-n=0$, so $\\ker=\\{\\mathbf{0}\\}$ (injective).\n\n**Step 2:** Full rank on square matrix means $\\text{Im}=\\mathbb{R}^n$ (surjective).\n\n**Answer:** $T$ is **bijective** (iff $\\det(A)\\ne0$).",
        "solution_he": "**צעד 1:** rank $=n$ ⇒ nullity $=0$ ⇒ $\\ker=\\{\\mathbf{0}\\}$ (חח\"ע).\n\n**צעד 2:** rank מלא במטריצה ריבועית ⇒ $\\text{Im}=\\mathbb{R}^n$ (על).\n\n**תשובה:** $T$ **חד-חד-ערכית ועל** (אמ\"מ $\\det(A)\\ne0$).",
    },
    "e10": {
        "solution_en": "**Injective?** Rank-nullity: rank $+$ nullity $=4$. Injective requires nullity $=0$, so rank $=4$. But $\\dim(\\text{Im})\\le\\dim(\\mathbb{R}^3)=3$, impossible. **Not injective.**\n\n**Surjective?** Possible when rank $=3$ (nullity $=1$).\n\n**Answer:** Never injective; can be surjective.",
        "solution_he": "**חח\"ע?** nullity $=0$ דורש rank $=4$, אבל $\\dim(\\text{Im})\\le3$ — **לא חח\"ע.**\n\n**על?** אפשרי כש-rank $=3$ (nullity $=1$).\n\n**תשובה:** לא חח\"ע; יכולה להיות על.",
    },
    "e11": {
        "solution_en": "**Step 1:** Need rows $\\vec{r}$ with $\\vec{r}\\cdot(1,2,1)^T=0$. Example rows: $(2,-1,0)$ and $(1,0,-1)$.\n\n**Step 2:** $A=\\begin{pmatrix}2&-1&0\\\\1&0&-1\\end{pmatrix}$. Check: $A(1,2,1)^T=(0,0)^T$ ✓.\n\n**Answer:** One valid matrix; nullity $=1$, $\\ker=\\text{span}\\{(1,2,1)^T\\}$.",
        "solution_he": "**צעד 1:** שורות $\\perp$ ל-$(1,2,1)^T$. לדוגמה: $(2,-1,0)$, $(1,0,-1)$.\n\n**צעד 2:** $A=\\begin{pmatrix}2&-1&0\\\\1&0&-1\\end{pmatrix}$, $A(1,2,1)^T=\\mathbf{0}$ ✓.\n\n**תשובה:** מטריצה תקפה; nullity $=1$, $\\ker=\\text{span}\\{(1,2,1)^T\\}$.",
    },
    "e12": {
        "solution_en": "**Step 1:** rank $=1$ means $\\dim(\\text{Im})=1$: a line through the origin in $\\mathbb{R}^3$.\n\n**Step 2:** Rank-nullity: nullity $=3-1=2$, so $\\ker$ is a plane through the origin.\n\n**Answer:** Im is 1D (line); Ker is 2D (plane).",
        "solution_he": "**צעד 1:** rank $=1$ ⇒ $\\dim(\\text{Im})=1$ — קו דרך הראשית.\n\n**צעד 2:** nullity $=3-1=2$ ⇒ $\\ker$ מישור דרך הראשית.\n\n**תשובה:** Im חד-ממדי; Ker דו-ממדי.",
    },
    "e13": {
        "solution_en": "**Step 1:** $T(\\mathbf{0})=\\mathbf{0}$, so $\\mathbf{0}\\in\\ker(T)$.\n\n**Step 2:** If $u,v\\in\\ker$, then $T(u+v)=T(u)+T(v)=\\mathbf{0}$, so $u+v\\in\\ker$.\n\n**Step 3:** If $u\\in\\ker$, $\\alpha\\in\\mathbb{R}$, then $T(\\alpha u)=\\alpha T(u)=\\mathbf{0}$, so $\\alpha u\\in\\ker$.\n\n**Answer:** $\\ker(T)$ is a subspace of $V$ ✓.",
        "solution_he": "**צעד 1:** $T(\\mathbf{0})=\\mathbf{0}$ ⇒ $\\mathbf{0}\\in\\ker$.\n\n**צעד 2:** $u,v\\in\\ker$ ⇒ $T(u+v)=\\mathbf{0}$ ⇒ $u+v\\in\\ker$.\n\n**צעד 3:** $u\\in\\ker$ ⇒ $T(\\alpha u)=\\mathbf{0}$ ⇒ $\\alpha u\\in\\ker$.\n\n**תשובה:** $\\ker(T)$ תת-מרחב של $V$ ✓.",
    },
}

ANSWER_PAYLOADS = {
    2: ["yes", "Yes", "linear", "כן"],
    3: ["span{(-1,1)", "(-1,1)", "x=-y", "x+y=0"],
    4: ["{0}", "zero", "trivial", "nullity=0", "אפס"],
    5: ["2", "nullity=2", "nullity 2"],
    6: ["rank=1", "nullity=1", "span{(1,1)", "span{(1,-1)"],
    7: ["2", "rank+nullity=2", "verified"],
    8: ["injective", "one-to-one", "ker={0}", "חח\"ע"],
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
        if q.get("kind") == "short_answer" and q["ord"] in ANSWER_PAYLOADS:
            q["answer_payload"]["acceptable_answers"] = ANSWER_PAYLOADS[q["ord"]]

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

    # validate
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
