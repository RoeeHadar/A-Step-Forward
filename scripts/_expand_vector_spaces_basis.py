#!/usr/bin/env python3
"""Expand vector_spaces_basis_dimension.json to MIN_WORDS depth."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parent / "seed_data/lessons/vector_spaces_basis_dimension.json"

SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "Every finite-dimensional vector space has a **basis** — a set of vectors that is simultaneously "
            "minimal (linearly independent, no redundancy) and maximal (spanning, everything is reachable as a "
            "linear combination). The number of vectors in any basis, the **dimension**, is the intrinsic size "
            "of the space and does not depend on which basis you choose.\n\n"
            "Dimension lets us compare spaces on equal footing: a plane in $\\mathbb{R}^3$ is 2-dimensional whether "
            "you describe it with standard coordinates or a skewed basis. The **Rank-Nullity theorem** quantifies "
            "how a linear map $T:\\mathbb{R}^n\\to\\mathbb{R}^m$ partitions the $n$ input dimensions into those "
            "sent to zero (nullity, dimension of $\\ker T$) and those that contribute to the output (rank, dimension "
            "of $\\text{Im}\\,T$). This single identity ties together row reduction, injectivity, surjectivity, and "
            "invertibility.\n\n"
            "**Connection to previous material:** Subspaces, linear independence, and span are the building blocks "
            "of this lesson. You should be comfortable row-reducing matrices and identifying pivot/free variables "
            "before proceeding — every basis computation in this chapter rests on those skills."
        ),
        "body_he_md": (
            "לכל מרחב וקטורי ממדי-סופי יש **בסיס** — קבוצת וקטורים שהיא גם **מינימלית** (בלתי-תלויה לינארית, "
            "ללא עודפות) וגם **מקסימלית** (פורשת, הכל ניתן להשגה כקומבינציה לינארית). מספר הוקטורים בכל בסיס, "
            "ה**ממד**, הוא הגודל הפנימי של המרחב ואינו תלוי באיזה בסיס בחרתם.\n\n"
            "ממד מאפשר להשוות מרחבים על בסיס שווה: מישור ב-$\\mathbb{R}^3$ הוא דו-ממדי בין אם מתארים אותו "
            "בקואורדינטות סטנדרטיות או בבסיס אלכסוני. **משפט דרגה-גרעין** מכמת איך העתקה לינארית "
            "$T:\\mathbb{R}^n\\to\\mathbb{R}^m$ מחלקת את $n$ הממדות לקלט לאלו שנשלחות לאפס (גרעין, "
            "$\\dim(\\ker T$)) ולאלו שתורמות לפלט (דרגה, $\\dim(\\text{Im}\\,T$)). זהות אחת זו קושרת דירוג, "
            "חד-חד-ערכיות, על ואינבירטיביליות.\n\n"
            "**קשר לחומר קודם:** תת-מרחבים, בלתי-תלות לינארית וקבוצת פרישה הם אבני הבניין של שיעור זה. "
            "ודאו שאתם בנוחים עם דירוג מטריצות וזיהוי משתנים ציריים/חופשיים — כל חישוב בסיס בפרק זה נשען עליהם."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Definition (Basis).** A **basis** of a vector space $V$ is a finite set "
            "$B=\\{\\vec{b}_1,\\ldots,\\vec{b}_n\\}\\subseteq V$ that satisfies both:\n"
            "1. **Linear independence** — no vector in $B$ is a combination of the others; and\n"
            "2. **Spanning** — every $\\vec{v}\\in V$ can be written as $\\vec{v}=c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n$.\n\n"
            "Equivalently, $B$ is a **minimal spanning set** or a **maximal independent set**.\n\n"
            "**Theorem (Uniqueness of dimension).** Any two bases of a finite-dimensional space $V$ contain the "
            "same number of vectors. This common count is the **dimension** $\\dim(V)$.\n\n"
            "**Standard basis of $\\mathbb{R}^n$:** $\\{\\vec{e}_1,\\ldots,\\vec{e}_n\\}$ where $\\vec{e}_i$ has $1$ "
            "in position $i$ and $0$ elsewhere; $\\dim(\\mathbb{R}^n)=n$. The same idea extends to polynomial spaces "
            "$P_k$ with basis $\\{1,x,\\ldots,x^k\\}$.\n\n"
            "**Coordinates.** Fix an ordered basis $B$. Every $\\vec{v}\\in V$ has a **unique** representation "
            "$\\vec{v}=c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n$. The **coordinate vector** is "
            "$[\\vec{v}]_B=(c_1,\\ldots,c_n)^T\\in\\mathbb{R}^n$.\n\n"
            "**Kernel and image.** For a linear map $T:V\\to W$:\n"
            "- $\\ker(T)=\\{\\vec{v}\\in V: T(\\vec{v})=\\vec{0}\\}$ — the **null space**;\n"
            "- $\\text{Im}(T)=\\{T(\\vec{v}):\\vec{v}\\in V\\}$ — the **column space** when $T$ is multiplication by $A$.\n\n"
            "**Rank-Nullity Theorem.** If $T:V\\to W$ is linear and $\\dim V=n$:\n"
            "$$\\dim(\\ker T)+\\dim(\\text{Im}\\,T)=n.$$\n"
            "For an $m\\times n$ matrix $A$: $\\text{nullity}(A)+\\text{rank}(A)=n$ where $n$ is the **number of columns**."
        ),
        "body_he_md": (
            "**הגדרה (בסיס).** **בסיס** של מרחב וקטורי $V$ הוא קבוצה סופית "
            "$B=\\{\\vec{b}_1,\\ldots,\\vec{b}_n\\}\\subseteq V$ שמקיימת:\n"
            "1. **בלתי-תלות לינארית** — אף וקטור ב-$B$ אינו קומבינציה של האחרים; ו-\n"
            "2. **פרישה** — כל $\\vec{v}\\in V$ ניתן לכתיבה כ-$\\vec{v}=c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n$.\n\n"
            "בשקילות, $B$ היא **קבוצת פרישה מינימלית** או **קבוצה בלתי-תלויה מקסימלית**.\n\n"
            "**משפט (ייחודיות הממד).** כל שני בסיסים של מרחב ממדי-סופי $V$ מכילים את אותו מספר וקטורים. "
            "מספר זה הוא ה**ממד** $\\dim(V)$.\n\n"
            "**בסיס סטנדרטי של $\\mathbb{R}^n$:** $\\{\\vec{e}_1,\\ldots,\\vec{e}_n\\}$ כאשר $\\vec{e}_i$ מכיל $1$ "
            "במיקום $i$ ו-$0$ בשאר; $\\dim(\\mathbb{R}^n)=n$. אותו רעיון מתרחב למרחבי פולינומים $P_k$ "
            "עם בסיס $\\{1,x,\\ldots,x^k\\}$.\n\n"
            "**קואורדינטות.** קבעו בסיס מסודר $B$. לכל $\\vec{v}\\in V$ יש **ייצוג יחיד** "
            "$\\vec{v}=c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n$. **וקטור הקואורדינטות** הוא "
            "$[\\vec{v}]_B=(c_1,\\ldots,c_n)^T\\in\\mathbb{R}^n$.\n\n"
            "**גרעין ואופי.** להעתקה לינארית $T:V\\to W$:\n"
            "- $\\ker(T)=\\{\\vec{v}\\in V: T(\\vec{v})=\\vec{0}\\}$ — **מרחב האפס**;\n"
            "- $\\text{Im}(T)=\\{T(\\vec{v}):\\vec{v}\\in V\\}$ — **מרחב העמודות** כש-$T$ היא כפל ב-$A$.\n\n"
            "**משפט דרגה-גרעין.** אם $T:V\\to W$ לינארית ו-$\\dim V=n$:\n"
            "$$\\dim(\\ker T)+\\dim(\\text{Im}\\,T)=n.$$\n"
            "למטריצה $m\\times n$: $\\text{nullity}(A)+\\text{rank}(A)=n$ כאשר $n$ הוא **מספר העמודות**."
        ),
    },
    "theory": {
        "body_en_md": (
            "**Theorem 1 (Basis characterisation).** In an $n$-dimensional space, an $n$-element set is a basis "
            "if and only if it is linearly independent — equivalently, if and only if it spans. This shortcut saves "
            "time on exams: verify only one of the two conditions when you already know the count is $n$.\n\n"
            "**Theorem 2 (Extension and reduction).** Any linearly independent set can be **extended** to a basis of "
            "the ambient space; any spanning set can be **reduced** to a basis by discarding redundant vectors. "
            "Row reduction on a matrix whose rows (or columns) are the given vectors implements reduction algorithmically.\n\n"
            "**Theorem 3 (Dimension of subspaces).** If $W\\subseteq V$ and $\\dim V<\\infty$, then "
            "$\\dim W\\leq\\dim V$, with equality if and only if $W=V$. A proper subspace always has strictly smaller dimension.\n\n"
            "**Theorem 4 (Rank-Nullity). Proof sketch:**\n"
            "Let $\\{\\vec{k}_1,\\ldots,\\vec{k}_r\\}$ be a basis of $\\ker T$ ($r=\\dim\\ker T$). Extend to a basis "
            "$\\{\\vec{k}_1,\\ldots,\\vec{k}_r,\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\}$ of $V$. Every output "
            "$T(\\vec{v})$ is a combination of $\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ because "
            "$T(\\vec{k}_i)=\\vec{0}$. These images are independent: if $\\sum a_jT(\\vec{v}_j)=\\vec{0}$, then "
            "$\\sum a_j\\vec{v}_j\\in\\ker T$, forcing all $a_j=0$ by independence of the extended basis. "
            "Hence $\\dim\\text{Im}(T)=n-r$ and $r+(n-r)=n$. $\\blacksquare$\n\n"
            "**Theorem 5 (Grassmann's formula).** For finite-dimensional subspaces $W_1,W_2\\subseteq V$:\n"
            "$$\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2).$$"
        ),
        "body_he_md": (
            "**משפט 1 (אפיון בסיס).** במרחב $n$-ממדי, קבוצה בת $n$ איברים היא בסיס אם ורק אם בלתי-תלויה — "
            "או בשקילות, אם ורק אם פורשת. קיצור דרך זה חוסך זמן בבחינה: אמתו רק תנאי אחד כשכבר יודעים שהגודל הוא $n$.\n\n"
            "**משפט 2 (הרחבה וצמצום).** כל קבוצה בלתי-תלויה ניתנת **להרחבה** לבסיס של המרחב; כל קבוצה פורשת "
            "ניתנת **לצמצום** לבסיס על ידי הסרת וקטורים מיותרים. דירוג מטריצה ששורותיה (או עמודותיה) הם "
            "הוקטורים הנתונים מיישם צמצום אלגוריתמית.\n\n"
            "**משפט 3 (ממד תת-מרחבים).** אם $W\\subseteq V$ ו-$\\dim V<\\infty$, אז $\\dim W\\leq\\dim V$, "
            "שוויון אם ורק אם $W=V$. תת-מרחב ממשי תמיד בעל ממד קטן יותר.\n\n"
            "**משפט 4 (דרגה-גרעין). סקיצת הוכחה:**\n"
            "יהי $\\{\\vec{k}_1,\\ldots,\\vec{k}_r\\}$ בסיס של $\\ker T$ ($r=\\dim\\ker T$). נרחיב לבסיס "
            "$\\{\\vec{k}_1,\\ldots,\\vec{k}_r,\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\}$ של $V$. כל פלט $T(\\vec{v})$ "
            "הוא קומבינציה של $\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ כי $T(\\vec{k}_i)=\\vec{0}$. "
            "התמונות בלתי-תלויות: אם $\\sum a_jT(\\vec{v}_j)=\\vec{0}$, אז $\\sum a_j\\vec{v}_j\\in\\ker T$, "
            "ומכאן $a_j=0$ מבלתי-תלות הבסיס המורחב. לכן $\\dim\\text{Im}(T)=n-r$ ו-$r+(n-r)=n$. $\\blacksquare$\n\n"
            "**משפט 5 (נוסחת גרסמן).** לתת-מרחבים ממדי-סופיים $W_1,W_2\\subseteq V$:\n"
            "$$\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2).$$"
        ),
    },
}

EXPLANATIONS = [
    {  # Q1 span basis
        "explanation_en": (
            "**Why this is correct:**\n"
            "Form a matrix with the three given vectors as rows and row-reduce. The pivot rows correspond to "
            "$(1,2,3)$ and $(0,1,0)$; the vector $(2,4,6)=2(1,2,3)$ is redundant. A basis for the span is "
            "$\\{(1,2,3),(0,1,0)\\}$ and $\\dim W=2$.\n\n"
            "**How to think about it:**\n"
            "To find a basis for a span, row-reduce and keep the **original** vectors whose rows became pivots. "
            "Never keep all three vectors once you spot a dependency.\n\n"
            "**Common slip:**\n"
            "Listing $(1,2,3)$ and $(2,4,6)$ as a basis because both are non-zero, ignoring that they span the "
            "same line. Another error: reporting $\\dim=3$ because there were three input vectors.\n\n"
            "**Exam tip:**\n"
            "After row reduction, state explicitly which vectors are redundant and verify each kept vector is "
            "not a combination of the others."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "בנו מטריצה עם שלושת הוקטורים כשורות ודרגו. השורות הציריות מתאימות ל-$(1,2,3)$ ו-$(0,1,0)$; "
            "הוקטור $(2,4,6)=2(1,2,3)$ מיותר. בסיס ל-span הוא $\\{(1,2,3),(0,1,0)\\}$ ו-$\\dim W=2$.\n\n"
            "**איך לחשוב:**\n"
            "למציאת בסיס ל-span, דרגו ושמרו את ה**וקטורים המקוריים** ששורותיהם הפכו לציריות. "
            "אל תשאירו את כל שלושת הוקטורים אחרי שזיהיתם תלות.\n\n"
            "**טעות נפוצה:**\n"
            "לרשום $(1,2,3)$ ו-$(2,4,6)$ כבסיס כי שניהם לא-אפסיים, תוך התעלמות מכך שהם על אותה ישר. "
            "טעות נוספת: לדווח $\\dim=3$ כי היו שלושה וקטורים.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי דירוג, ציינו במפורש אילו וקטורים מיותרים ואמתו שכל וקטור שנשמר אינו קומבינציה של האחרים."
        ),
    },
    {  # Q2 rank-nullity dim ker
        "explanation_en": (
            "**Why this is correct:**\n"
            "Rank-Nullity states $\\text{rank}(A)+\\text{nullity}(A)=n$ where $n$ is the number of **columns**. "
            "Here $A$ is $5\\times7$, so $n=7$. With rank $=4$, nullity $=7-4=3$, hence $\\dim(\\ker A)=3$.\n\n"
            "**How to think about it:**\n"
            "The $5$ rows describe the codomain dimension bound (rank $\\leq5$), but nullity always uses column "
            "count — the domain dimension of the map $A:\\mathbb{R}^7\\to\\mathbb{R}^5$.\n\n"
            "**Common slip:**\n"
            "Using $5-4=1$ (subtracting rank from row count) or $7+4=11$. Another trap: confusing nullity with "
            "rank or reporting $\\dim(\\ker A)=4$.\n\n"
            "**Exam tip:**\n"
            "Write \"Rank-Nullity: nullity $=n-\\text{rank}$\" and circle $n=\\#$ columns before substituting numbers."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "משפט דרגה-גרעין קובע $\\text{rank}(A)+\\text{nullity}(A)=n$ כאשר $n$ הוא מספר **העמודות**. "
            "כאן $A$ היא $5\\times7$, ולכן $n=7$. עם דרגה $=4$, גרעין $=7-4=3$, כלומר $\\dim(\\ker A)=3$.\n\n"
            "**איך לחשוב:**\n"
            "חמש השורות קובעות גבול על ממד הקודומיין (דרגה $\\leq5$), אך גרעין תמיד משתמש במספר העמודות — "
            "ממד הדומיין של $A:\\mathbb{R}^7\\to\\mathbb{R}^5$.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$5-4=1$ (חיסור דרגה ממספר שורות) או $7+4=11$. מלכודת נוספת: בלבול גרעין עם דרגה "
            "ודיווח $\\dim(\\ker A)=4$.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו \"דרגה-גרעין: גרעין $=n-$דרגה\" והקיפו $n=\\#$ עמודות לפני הצבת מספרים."
        ),
    },
    {  # Q3 coordinates
        "explanation_en": (
            "**Why this is correct:**\n"
            "Coordinates in basis $B=\\{(1,1),(1,-1)\\}$ satisfy $\\vec{v}=c_1(1,1)+c_2(1,-1)=(3,1)$. "
            "This gives $c_1+c_2=3$ and $c_1-c_2=1$. Adding yields $2c_1=4\\Rightarrow c_1=2$; then "
            "$c_2=1$. So $[\\vec{v}]_B=(2,1)^T$.\n\n"
            "**How to think about it:**\n"
            "Set up the linear system with basis vectors as columns (or rows, consistently). The coefficients "
            "are the coordinates — order must match the basis ordering.\n\n"
            "**Common slip:**\n"
            "Swapping $c_1$ and $c_2$ in the final answer, or solving for standard coordinates instead of "
            "$B$-coordinates. Another error: using $(3,1)$ as coordinates without solving.\n\n"
            "**Exam tip:**\n"
            "Verify by recomputing $2(1,1)+1(1,-1)=(3,1)$ — one multiplication catches sign mistakes instantly."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "קואורדינטות בבסיס $B=\\{(1,1),(1,-1)\\}$ מקיימות $\\vec{v}=c_1(1,1)+c_2(1,-1)=(3,1)$. "
            "מכאן $c_1+c_2=3$ ו-$c_1-c_2=1$. חיבור נותן $2c_1=4\\Rightarrow c_1=2$; אז $c_2=1$. "
            "לכן $[\\vec{v}]_B=(2,1)^T$.\n\n"
            "**איך לחשוב:**\n"
            "בנו מערכת לינארית עם וקטורי הבסיס כעמודות (או שורות, בעקביות). המקדמים הם הקואורדינטות — "
            "הסדר חייב להתאים לסדר הבסיס.\n\n"
            "**טעות נפוצה:**\n"
            "החלפת $c_1$ ו-$c_2$ בתשובה הסופית, או פתרון לקואורדינטות סטנדרטיות במקום $B$. "
            "טעות נוספת: שימוש ב-$(3,1)$ כקואורדינטות בלי לפתור.\n\n"
            "**טיפ לבחינה:**\n"
            "אמתו ב-$2(1,1)+1(1,-1)=(3,1)$ — כפל אחד תופס טעויות סימן מיד."
        ),
    },
    {  # Q4 verify standard basis R^3
        "explanation_en": (
            "**Why this is correct:**\n"
            "The set $\\{(1,0,0),(0,1,0),(0,0,1)\\}$ has three vectors in $\\mathbb{R}^3$, which is "
            "3-dimensional. The matrix with these as columns is the identity $I_3$, whose rows are pivot rows — "
            "the vectors are linearly independent and span all of $\\mathbb{R}^3$. Therefore they form a basis.\n\n"
            "**How to think about it:**\n"
            "In an $n$-dimensional space, an $n$-vector set is a basis if you verify **either** independence "
            "**or** spanning (Theorem 1). Here both are immediate from $I_3$.\n\n"
            "**Common slip:**\n"
            "Checking only that each vector is non-zero, or claiming dependence because \"they look standard.\" "
            "Another error: confusing $\\mathbb{R}^2$ with $\\mathbb{R}^3$ dimension.\n\n"
            "**Exam tip:**\n"
            "For the standard basis, one line suffices: \"$3$ independent vectors in $\\dim=3$ space $\\Rightarrow$ basis.\""
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "הקבוצה $\\{(1,0,0),(0,1,0),(0,0,1)\\}$ מכילה שלושה וקטורים ב-$\\mathbb{R}^3$, שהוא 3-ממדי. "
            "המטריצה עם אלה כעמודות היא $I_3$, ששורותיה ציריות — הוקטורים בלתי-תלויים ופורשים את "
            "$\\mathbb{R}^3$. לכן הם מהווים בסיס.\n\n"
            "**איך לחשוב:**\n"
            "במרחב $n$-ממדי, קבוצה בת $n$ וקטורים היא בסיס אם מוכיחים **בלתי-תלות** **או** **פרישה** "
            "(משפט 1). כאן שניהם מיידיים מ-$I_3$.\n\n"
            "**טעות נפוצה:**\n"
            "בדיקה רק שכל וקטור לא-אפסי, או טענה על תלות כי \"זה נראה סטנדרטי\". "
            "טעות נוספת: בלבול $\\mathbb{R}^2$ עם $\\mathbb{R}^3$.\n\n"
            "**טיפ לבחינה:**\n"
            "לבסיס הסטנדרטי, שורה אחת מספיקה: \"3 וקטורים בלתי-תלויים במרחב $\\dim=3$ $\\Rightarrow$ בסיס.\""
        ),
    },
    {  # Q5 ker basis
        "explanation_en": (
            "**Why this is correct:**\n"
            "Row-reduce $A=\\begin{pmatrix}1&-2&1\\\\2&-4&2\\end{pmatrix}$ to $\\begin{pmatrix}1&-2&1\\\\0&0&0\\end{pmatrix}$. "
            "Pivot column is 1; free variables $x_2=s$, $x_3=t$. From row 1: $x_1=2s-t$. The general solution is "
            "$\\vec{x}=s(2,1,0)^T+t(-1,0,1)^T$, giving basis $\\{(2,1,0)^T,(-1,0,1)^T\\}$ and nullity $=2$.\n\n"
            "**How to think about it:**\n"
            "Kernel basis = parametric solution vectors from free variables. Assign $1$ to one free variable and "
            "$0$ to others for each basis vector.\n\n"
            "**Common slip:**\n"
            "Using RREF pivot columns instead of free-variable directions, or forgetting that both rows are "
            "multiples (rank 1, nullity 2). Sign errors in $x_1=2s-t$ are frequent.\n\n"
            "**Exam tip:**\n"
            "Check Rank-Nullity: $n=3$, rank $=1$, nullity $=2$ must match your basis size."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "דרגו $A=\\begin{pmatrix}1&-2&1\\\\2&-4&2\\end{pmatrix}$ ל-$\\begin{pmatrix}1&-2&1\\\\0&0&0\\end{pmatrix}$. "
            "עמודה צירית: 1; משתנים חופשיים $x_2=s$, $x_3=t$. משורה 1: $x_1=2s-t$. הפתרון הכללי "
            "$\\vec{x}=s(2,1,0)^T+t(-1,0,1)^T$, בסיס $\\{(2,1,0)^T,(-1,0,1)^T\\}$, גרעין $=2$.\n\n"
            "**איך לחשוב:**\n"
            "בסיס גרעין = וקטורי הפתרון הפרמטרי ממשתנים חופשיים. הציבו $1$ למשתנה חופשי אחד ו-$0$ לשאר "
            "לכל וקטור בסיס.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש בעמודות ציריות מ-RREF במקום כיווני משתנים חופשיים, או התעלמות מכך ששתי השורות "
            "כפולות (דרגה 1, גרעין 2). טעויות סימן ב-$x_1=2s-t$ נפוצות.\n\n"
            "**טיפ לבחינה:**\n"
            "בדקו דרגה-גרעין: $n=3$, דרגה $=1$, גרעין $=2$ חייב להתאים לגודל הבסיס."
        ),
    },
    {  # Q6 column space
        "explanation_en": (
            "**Why this is correct:**\n"
            "Row-reduce $A$; pivot columns are 1 and 2. A basis for $\\text{col}(A)$ uses the **original** columns "
            "1 and 2 of $A$: $\\{(1,0,1)^T,(2,1,3)^T\\}$. Rank $=2$ because column 3 is a combination of columns 1–2.\n\n"
            "**How to think about it:**\n"
            "Column space basis always comes from pre-reduction columns at pivot positions. Row operations change "
            "the column space — never use reduced columns directly.\n\n"
            "**Common slip:**\n"
            "Taking pivot rows from RREF as a column-space basis, or using $(1,0,0)^T$ from the reduced matrix. "
            "Another error: including column 3 because it has a pivot entry in a wrong reduction.\n\n"
            "**Exam tip:**\n"
            "Label pivot columns on the **original** $A$ before erasing it during row reduction."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "דרגו $A$; עמודות ציריות: 1 ו-2. בסיס ל-$\\text{col}(A)$ משתמש ב**עמודות המקוריות** 1 ו-2 של $A$: "
            "$\\{(1,0,1)^T,(2,1,3)^T\\}$. דרגה $=2$ כי עמודה 3 קומבינציה של 1–2.\n\n"
            "**איך לחשוב:**\n"
            "בסיס מרחב עמודות תמיד מעמודות לפני-דירוג במיקומי ציר. פעולות שורה משנות את מרחב העמודות — "
            "אל תשתמשו בעמודות מדורגות ישירות.\n\n"
            "**טעות נפוצה:**\n"
            "לקיחת שורות ציריות מ-RREF כבסיס לעמודות, או שימוש ב-$(1,0,0)^T$ מהמטריצה המדורגת. "
            "טעות נוספת: הכללת עמודה 3 כי יש בה ציר בדירוג שגוי.\n\n"
            "**טיפ לבחינה:**\n"
            "סמנו עמודות ציריות על $A$ **המקורית** לפני מחיקתה במהלך דירוג."
        ),
    },
    {  # Q7 rank-nullity onto
        "explanation_en": (
            "**Why this is correct:**\n"
            "Rank-Nullity for $T:\\mathbb{R}^5\\to\\mathbb{R}^3$ gives $\\dim(\\text{Im}\\,T)=5-\\dim(\\ker T)=5-3=2$. "
            "Since $\\dim(\\mathbb{R}^3)=3$ but $\\dim(\\text{Im}\\,T)=2<3$, the image is a proper subspace of "
            "$\\mathbb{R}^3$, so $T$ is **not onto** (not surjective).\n\n"
            "**How to think about it:**\n"
            "Onto means $\\text{Im}\\,T=W$ (full codomain). That requires $\\dim(\\text{Im}\\,T)=\\dim W$. "
            "Rank-Nullity computes $\\dim(\\text{Im}\\,T)$ from domain dimension minus nullity.\n\n"
            "**Common slip:**\n"
            "Answering \"yes, onto\" because $3<5$ (confusing domain and codomain dimensions) or because "
            "$\\dim(\\ker T)=3$ \"uses up\" the codomain. Another error: reporting $\\dim(\\text{Im}\\,T)=3$.\n\n"
            "**Exam tip:**\n"
            "After Rank-Nullity, compare $\\dim(\\text{Im}\\,T)$ to $\\dim W$ explicitly — surjectivity is an equality test."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "דרגה-גרעין ל-$T:\\mathbb{R}^5\\to\\mathbb{R}^3$ נותן $\\dim(\\text{Im}\\,T)=5-\\dim(\\ker T)=5-3=2$. "
            "מכיוון $\\dim(\\mathbb{R}^3)=3$ אך $\\dim(\\text{Im}\\,T)=2<3$, האופי הוא תת-מרחב ממשי של "
            "$\\mathbb{R}^3$, ולכן $T$ **אינה על** (לא על).\n\n"
            "**איך לחשוב:**\n"
            "על פירושו $\\text{Im}\\,T=W$ (קודומיין מלא). זה דורש $\\dim(\\text{Im}\\,T)=\\dim W$. "
            "דרגה-גרעין מחשב $\\dim(\\text{Im}\\,T)$ מממד דומיין פחות גרעין.\n\n"
            "**טעות נפוצה:**\n"
            "תשובה \"כן, על\" כי $3<5$ (בלבול ממדי דומיין וקודומיין) או כי $\\dim(\\ker T)=3$ \"ממלא\" "
            "את הקודומיין. טעות נוספת: דיווח $\\dim(\\text{Im}\\,T)=3$.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי דרגה-גרעין, השוו $\\dim(\\text{Im}\\,T)$ ל-$\\dim W$ במפורש — עלות היא בדיקת שוויון."
        ),
    },
    {  # Q8 polynomial coordinates
        "explanation_en": (
            "**Why this is correct:**\n"
            "In $P_2$ with ordered basis $B=\\{1,x,x^2\\}$, coordinates are the coefficients of "
            "$p(x)=3+2x-x^2$ in that order: $[p]_B=(3,2,-1)^T$ because $p=3\\cdot1+2\\cdot x+(-1)\\cdot x^2$.\n\n"
            "**How to think about it:**\n"
            "When the basis matches the standard polynomial form, coordinates are read directly from coefficients — "
            "no system to solve. Non-standard bases (e.g. $\\{1,x,x^2-x\\}$) require solving a linear system.\n\n"
            "**Common slip:**\n"
            "Reversing order to $(-1,2,3)^T$ (ascending vs descending powers) or omitting the minus on $x^2$. "
            "Another error: treating $p$ as a vector in $\\mathbb{R}^3$ without naming the basis.\n\n"
            "**Exam tip:**\n"
            "Write the basis order at the top of your page; coordinate vectors are meaningless without it."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "ב-$P_2$ עם בסיס מסודר $B=\\{1,x,x^2\\}$, הקואורדינטות הן המקדמים של $p(x)=3+2x-x^2$ "
            "באותו סדר: $[p]_B=(3,2,-1)^T$ כי $p=3\\cdot1+2\\cdot x+(-1)\\cdot x^2$.\n\n"
            "**איך לחשוב:**\n"
            "כשהבסיס תואם צורת פולינום סטנדרטית, קואורדינטות נקראות ישירות מהמקדמים — ללא מערכת לפתור. "
            "בסיסים לא-סטנדרטיים (למשל $\\{1,x,x^2-x\\}$) דורשים פתרון מערכת לינארית.\n\n"
            "**טעות נפוצה:**\n"
            "היפוך סדר ל-$(-1,2,3)^T$ (חזקות עולות מול יורדות) או השמטת המינוס על $x^2$. "
            "טעות נוספת: התייחסות ל-$p$ כוקטור ב-$\\mathbb{R}^3$ בלי לציין בסיס.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו את סדר הבסיס בראש הדף; וקטורי קואורדינטות חסרי משמעות בלעדיו."
        ),
    },
]


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_BODIES:
            sec.update(SECTION_BODIES[kind])

        if kind == "worked_example" and sec.get("example_number") == 1:
            sec["body_en_md"] = (
                "**Task:** Find a basis for $W = \\text{span}\\{(1,2),(2,4),(1,0)\\}$ in $\\mathbb{R}^2$.\n\n"
                "We are given three vectors in $\\mathbb{R}^2$, which is itself 2-dimensional. Any spanning set "
                "with more than two vectors must contain redundancy — our goal is to remove it systematically.\n\n"
                "### Move 1\n"
                "Stack the vectors as rows of a matrix and row-reduce to identify pivot positions:\n"
                "$$\\begin{pmatrix}1&2\\\\2&4\\\\1&0\\end{pmatrix} "
                "\\xrightarrow{R_2-2R_1,\\;R_3-R_1} "
                "\\begin{pmatrix}1&2\\\\0&0\\\\0&-2\\end{pmatrix} "
                "\\xrightarrow{\\text{swap }R_2,R_3} "
                "\\begin{pmatrix}1&2\\\\0&-2\\\\0&0\\end{pmatrix}.$$\n\n"
                "The middle row became all zeros — row 2 of the original matrix was a multiple of row 1.\n\n"
                "### Move 2\n"
                "Two non-zero pivot rows remain. For a row-space (span) basis, take the **original** vectors "
                "from rows 1 and 3: $(1,2)$ and $(1,0)$.\n\n"
                "**Basis:** $\\{(1,2),(1,0)\\}$. **Dimension:** $\\dim W = 2$.\n\n"
                "**Check:** $(2,4)=2(1,2)$ confirms the second input vector was redundant. Neither $(1,2)$ nor "
                "$(1,0)$ is a scalar multiple of the other, so the basis is independent. Since $\\dim\\mathbb{R}^2=2$ "
                "and we have two independent vectors, they automatically span $W$ (Theorem 1)."
            )
            sec["body_he_md"] = (
                "**משימה:** מצא בסיס ל-$W = \\text{span}\\{(1,2),(2,4),(1,0)\\}$ ב-$\\mathbb{R}^2$.\n\n"
                "נתונים שלושה וקטורים ב-$\\mathbb{R}^2$, שהוא בעצמו 2-ממדי. כל קבוצת פרישה עם יותר משני "
                "וקטורים חייבת להכיל עודפות — המטרה היא להסיר אותה שיטתית.\n\n"
                "### צעד 1\n"
                "ערמו את הוקטורים כשורות מטריצה ודרגו לזיהוי מיקומי ציר:\n"
                "$$\\begin{pmatrix}1&2\\\\2&4\\\\1&0\\end{pmatrix} "
                "\\xrightarrow{R_2-2R_1,\\;R_3-R_1} "
                "\\begin{pmatrix}1&2\\\\0&0\\\\0&-2\\end{pmatrix} "
                "\\xrightarrow{\\text{החלפת }R_2,R_3} "
                "\\begin{pmatrix}1&2\\\\0&-2\\\\0&0\\end{pmatrix}.$$\n\n"
                "השורה האמצעית הפכה לאפסים — שורה 2 במטריצה המקורית הייתה כפולה של שורה 1.\n\n"
                "### צעד 2\n"
                "נותרו שתי שורות ציריות לא-אפסיות. לבסיס של span (מרחב שורות), קחו את ה**וקטורים המקוריים** "
                "משורות 1 ו-3: $(1,2)$ ו-$(1,0)$.\n\n"
                "**בסיס:** $\\{(1,2),(1,0)\\}$. **ממד:** $\\dim W = 2$.\n\n"
                "**בדיקה:** $(2,4)=2(1,2)$ מאשר שהוקטור השני מיותר. אף אחד מ-$(1,2)$, $(1,0)$ אינו כפולה "
                "סקלארית של השני, ולכן הבסיס בלתי-תלוי. מכיוון $\\dim\\mathbb{R}^2=2$ ויש שני וקטורים "
                "בלתי-תלויים, הם פורשים את $W$ אוטומטית (משפט 1)."
            )

        if kind == "worked_example" and sec.get("example_number") == 2:
            sec["body_en_md"] = (
                "**Task:** Find a basis and the dimension of $\\ker(A)$ for\n"
                "$$A = \\begin{pmatrix}1&2&0&-1\\\\2&4&1&0\\\\0&0&1&2\\end{pmatrix}.$$\n\n"
                "The kernel consists of all $\\vec{x}\\in\\mathbb{R}^4$ with $A\\vec{x}=\\vec{0}$. Row reduction "
                "reveals which variables are pivot (determined) versus free (parametric). A $3\\times4$ matrix "
                "with rank 2 must have nullity 2 by Rank-Nullity.\n\n"
                "### Move 1 — Row reduce $A$\n"
                "$$\\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&2&0&-1\\\\0&0&1&2\\\\0&0&1&2\\end{pmatrix} "
                "\\xrightarrow{R_3-R_2} \\begin{pmatrix}1&2&0&-1\\\\0&0&1&2\\\\0&0&0&0\\end{pmatrix}.$$\n\n"
                "Pivot columns are 1 and 3 (rank $=2$). Columns 2 and 4 are free.\n\n"
                "### Move 2 — Parametric solution\n"
                "Set free variables $x_2=s$, $x_4=t$. From row 2: $x_3+2t=0\\Rightarrow x_3=-2t$. "
                "From row 1: $x_1+2s-t=0\\Rightarrow x_1=-2s+t$.\n\n"
                "**General solution:**\n"
                "$$\\vec{x} = s\\begin{pmatrix}-2\\\\1\\\\0\\\\0\\end{pmatrix} + "
                "t\\begin{pmatrix}1\\\\0\\\\-2\\\\1\\end{pmatrix}.$$\n\n"
                "### Move 3 — Read off the basis\n"
                "**Basis of $\\ker(A)$:** $\\left\\{(-2,1,0,0)^T,\\,(1,0,-2,1)^T\\right\\}$. **Nullity = 2.**\n\n"
                "**Rank-Nullity check:** rank$(A)=2$; nullity $=4-2=2$; $2+2=4=n$. ✓ Substituting either basis "
                "vector into $A\\vec{x}$ yields $\\vec{0}$, confirming the computation.\n\n"
                "**Note:** The two kernel directions are independent because neither parametric vector is a "
                "multiple of the other — this matches nullity $=2$."
            )
            sec["body_he_md"] = (
                "**משימה:** מצא בסיס וממד של $\\ker(A)$ עבור\n"
                "$$A = \\begin{pmatrix}1&2&0&-1\\\\2&4&1&0\\\\0&0&1&2\\end{pmatrix}.$$\n\n"
                "הגרעין מורכב מכל $\\vec{x}\\in\\mathbb{R}^4$ עם $A\\vec{x}=\\vec{0}$. דירוג חושף אילו משתנים "
                "ציריים (נקבעים) לעומת חופשיים (פרמטריים). מטריצה $3\\times4$ עם דרגה 2 חייבת גרעין 2.\n\n"
                "### צעד 1 — דירוג $A$\n"
                "$$\\xrightarrow{R_2-2R_1} \\begin{pmatrix}1&2&0&-1\\\\0&0&1&2\\\\0&0&1&2\\end{pmatrix} "
                "\\xrightarrow{R_3-R_2} \\begin{pmatrix}1&2&0&-1\\\\0&0&1&2\\\\0&0&0&0\\end{pmatrix}.$$\n\n"
                "עמודות ציריות: 1 ו-3 (דרגה $=2$). עמודות 2 ו-4 חופשיות.\n\n"
                "### צעד 2 — פתרון פרמטרי\n"
                "הציבו $x_2=s$, $x_4=t$. משורה 2: $x_3+2t=0\\Rightarrow x_3=-2t$. "
                "משורה 1: $x_1+2s-t=0\\Rightarrow x_1=-2s+t$.\n\n"
                "**פתרון כללי:** $\\vec{x} = s(-2,1,0,0)^T + t(1,0,-2,1)^T$.\n\n"
                "### צעד 3 — קריאת הבסיס\n"
                "**בסיס:** $\\{(-2,1,0,0)^T,\\,(1,0,-2,1)^T\\}$. **גרעין** = 2.\n\n"
                "**בדיקת דרגה-גרעין:** דרגה $=2$; $2+2=4=n$. ✓ הצבת כל וקטור בסיס ב-$A\\vec{x}$ נותנת $\\vec{0}$.\n\n"
                "**הערה:** שני כיווני הגרעין בלתי-תלויים כי אף וקטור פרמטרי אינו כפולה של השני — "
                "בהתאם לגרעין $=2$."
            )

        if kind == "worked_example" and sec.get("example_number") == 3:
            sec["body_en_md"] = (
                "**Claim:** If $T:V\\to W$ is a linear map and $\\dim V=n<\\infty$, then\n"
                "$$\\dim(\\ker T)+\\dim(\\text{Im}\\, T) = n.$$\n\n"
                "**Proof:**\n\n"
                "### Move 1\n"
                "Let $r=\\dim(\\ker T)$. If $r=0$, then $\\ker T=\\{\\vec{0}\\}$ and $T$ is injective, "
                "so $\\dim(\\text{Im}\\, T)=n$. ✓ Assume $r\\geq1$.\n\n"
                "### Move 2\n"
                "Let $\\{\\vec{k}_1,\\ldots,\\vec{k}_r\\}$ be a basis of $\\ker T$. By the extension theorem, "
                "there exist $\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\in V$ such that\n"
                "$$\\mathcal{B}=\\{\\vec{k}_1,\\ldots,\\vec{k}_r,\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\}$$\n"
                "is a basis of $V$.\n\n"
                "### Move 3\n"
                "Any $T(\\vec{v})$ with $\\vec{v}=\\sum_{i=1}^r c_i\\vec{k}_i+\\sum_{j=r+1}^n c_j\\vec{v}_j$ gives "
                "$T(\\vec{v})=\\sum c_jT(\\vec{v}_j)$ (since $T(\\vec{k}_i)=\\vec{0}$). So "
                "$\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ spans $\\text{Im}(T)$.\n\n"
                "### Move 4\n"
                "Suppose $\\sum_{j=r+1}^n a_j T(\\vec{v}_j)=\\vec{0}$. Then $T(\\sum a_j\\vec{v}_j)=\\vec{0}$, "
                "so $\\vec{u}=\\sum a_j\\vec{v}_j\\in\\ker T$. Write $\\vec{u}=\\sum_{i=1}^r b_i\\vec{k}_i$. Then\n"
                "$$\\sum_{i=1}^r b_i\\vec{k}_i - \\sum_{j=r+1}^n a_j\\vec{v}_j = \\vec{0}.$$\n"
                "Since $\\mathcal{B}$ is a basis, all coefficients are zero: $b_i=0$ and $a_j=0$. ✓\n\n"
                "### Move 5\n"
                "$\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ is a basis of $\\text{Im}(T)$, so "
                "$\\dim(\\text{Im}\\,T)=n-r$. Therefore $r + (n-r) = n$. $\\blacksquare$\n\n"
                "**Why this matters:** Rank-Nullity is the bridge between kernel computations (free variables) "
                "and image dimension (rank) — every row-reduction exercise implicitly uses this proof."
            )
            sec["body_he_md"] = (
                "**טענה:** אם $T:V\\to W$ לינארית ו-$\\dim V=n<\\infty$, אז "
                "$\\dim(\\ker T)+\\dim(\\text{Im}\\, T) = n$.\n\n"
                "**הוכחה:**\n\n"
                "### צעד 1\n"
                "יהי $r=\\dim(\\ker T)$. אם $r=0$, $\\ker T=\\{\\vec{0}\\}$ ו-$T$ חד-חד-ערכית, "
                "ולכן $\\dim(\\text{Im}\\,T)=n$. ✓ נניח $r\\geq1$.\n\n"
                "### צעד 2\n"
                "יהי $\\{\\vec{k}_1,\\ldots,\\vec{k}_r\\}$ בסיס של $\\ker T$. לפי משפט ההרחבה, קיימים "
                "$\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\in V$ כך ש\n"
                "$$\\mathcal{B}=\\{\\vec{k}_1,\\ldots,\\vec{k}_r,\\vec{v}_{r+1},\\ldots,\\vec{v}_n\\}$$\n"
                "בסיס של $V$.\n\n"
                "### צעד 3\n"
                "לכל $T(\\vec{v})$ עם $\\vec{v}=\\sum c_i\\vec{k}_i+\\sum c_j\\vec{v}_j$ מתקבל "
                "$T(\\vec{v})=\\sum c_jT(\\vec{v}_j)$ (כי $T(\\vec{k}_i)=\\vec{0}$). לכן "
                "$\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ פורש את $\\text{Im}(T)$.\n\n"
                "### צעד 4\n"
                "נניח $\\sum a_jT(\\vec{v}_j)=\\vec{0}$. אז $T(\\sum a_j\\vec{v}_j)=\\vec{0}$, "
                "כלומר $\\sum a_j\\vec{v}_j\\in\\ker T$. כתיבה כקומבינציה של $\\vec{k}_i$ נותנת\n"
                "$$\\sum b_i\\vec{k}_i - \\sum a_j\\vec{v}_j = \\vec{0}.$$\n"
                "מבלתי-תלות $\\mathcal{B}$: כל המקדמים אפס. ✓\n\n"
                "### צעד 5\n"
                "$\\{T(\\vec{v}_{r+1}),\\ldots,T(\\vec{v}_n)\\}$ בסיס של $\\text{Im}(T)$, "
                "ולכן $\\dim(\\text{Im}\\,T)=n-r$ ו-$r+(n-r)=n$. $\\blacksquare$\n\n"
                "**למה זה חשוב:** דרגה-גרעין הוא הגשר בין חישובי גרעין (משתנים חופשיים) "
                "לבין ממד האופי (דרגה) — כל תרגיל דירוג משתמש בהוכחה זו באופן סמוי."
            )

        if kind == "checkpoint" and "span\\{(1,0,2)" in sec.get("body_en_md", ""):
            sec["checkpoint_solution_en"] = (
                "Row-reduce the matrix with rows $(1,0,2)$, $(0,1,1)$, $(2,1,5)$:\n"
                "$$\\begin{pmatrix}1&0&2\\\\0&1&1\\\\2&1&5\\end{pmatrix}\\to"
                "\\begin{pmatrix}1&0&2\\\\0&1&1\\\\0&0&0\\end{pmatrix}.$$\n\n"
                "Alternatively, observe directly: $(2,1,5)=2(1,0,2)+(0,1,1)$, so the third vector is redundant.\n\n"
                "**Basis:** $\\{(1,0,2),(0,1,1)\\}$. **Dimension:** $\\dim=2$.\n\n"
                "**Verify:** Both kept vectors are independent (not multiples); together they span the plane "
                "containing all three original vectors."
            )
            sec["checkpoint_solution_he"] = (
                "דרגו מטריצה עם שורות $(1,0,2)$, $(0,1,1)$, $(2,1,5)$:\n"
                "$$\\begin{pmatrix}1&0&2\\\\0&1&1\\\\2&1&5\\end{pmatrix}\\to"
                "\\begin{pmatrix}1&0&2\\\\0&1&1\\\\0&0&0\\end{pmatrix}.$$\n\n"
                "לחלופין, שימו לב: $(2,1,5)=2(1,0,2)+(0,1,1)$ — הוקטור השלישי מיותר.\n\n"
                "**בסיס:** $\\{(1,0,2),(0,1,1)\\}$. **ממד:** $\\dim=2$.\n\n"
                "**אימות:** שני הוקטורים שנשמרו בלתי-תלויים; יחד הם spanים את המישור שמכיל את שלושת הוקטורים."
            )

        if kind == "checkpoint" and "rank 3" in sec.get("body_en_md", ""):
            sec["checkpoint_solution_en"] = (
                "Apply Rank-Nullity: $\\text{rank}(A)+\\text{nullity}(A)=n$ where $n$ is the number of columns.\n\n"
                "Here $A$ is $4\\times6$, so $n=6$. With rank $=3$:\n"
                "$$\\text{nullity}(A)=6-3=3.$$\n\n"
                "Since nullity equals $\\dim(\\ker A)$, we have $\\dim(\\ker A)=3$.\n\n"
                "**Interpretation:** Three independent directions in $\\mathbb{R}^6$ map to zero under $A$; "
                "the remaining three dimensions contribute to the column space (rank 3)."
            )
            sec["checkpoint_solution_he"] = (
                "הפעילו דרגה-גרעין: $\\text{rank}(A)+\\text{nullity}(A)=n$ כאשר $n$ מספר העמודות.\n\n"
                "כאן $A$ היא $4\\times6$, ולכן $n=6$. עם דרגה $=3$:\n"
                "$$\\text{nullity}(A)=6-3=3.$$\n\n"
                "מכיוון שגרעין שווה ל-$\\dim(\\ker A)$, מתקבל $\\dim(\\ker A)=3$.\n\n"
                "**פרשנות:** שלושה כיוונים בלתי-תלויים ב-$\\mathbb{R}^6$ מועתקים לאפס תחת $A$; "
                "שלושת הממדים הנותרים תורמים למרחב העמודות (דרגה 3)."
            )

        if kind == "method_guide":
            sec["body_en_md"] = (
                "**Step 1 — Basis of a span:** Form a matrix with the given vectors as **rows**; row-reduce; "
                "keep the original vectors whose rows became pivot rows.\n\n"
                "**Step 2 — Basis of $\\ker A$:** Row-reduce $A$; identify free variables; write the parametric "
                "general solution; read off one basis vector per free variable.\n\n"
                "**Step 3 — Basis of $\\text{col}(A)$:** Row-reduce $A$; mark pivot **column positions** on the "
                "**original** $A$ before reduction; those columns form a basis.\n\n"
                "**Step 4 — Rank and nullity:** rank $=$ pivot count; nullity $=n-$rank where $n=\\#$ columns.\n\n"
                "**Step 5 — Coordinates $[\\vec{v}]_B$:** Solve $c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n=\\vec{v}$.\n\n"
                "| Goal | Method |\n|---|---|\n"
                "| Find basis of span $\\{\\vec{v}_i\\}$ | Rows $\\to$ row-reduce $\\to$ pivot rows from originals |\n"
                "| Find basis of $\\ker A$ | Row-reduce $\\to$ free vars $\\to$ parametric basis |\n"
                "| Find basis of col$(A)$ | Pivot columns of **original** $A$ |\n"
                "| Compute rank$(A)$ | Count pivots in REF |\n"
                "| Compute nullity$(A)$ | $n - \\text{rank}(A)$ |\n"
                "| Verify $B$ is a basis | $|B|=\\dim V$ plus independence OR spanning |\n"
                "| Rank-Nullity check | rank + nullity must equal $\\#$ columns"
            )
            sec["body_he_md"] = (
                "**צעד 1 — בסיס ל-span:** בנו מטריצה עם הוקטורים כ**שורות**; דרגו; שמרו וקטורים מקוריים "
                "ששורותיהם הפכו לציריות.\n\n"
                "**צעד 2 — בסיס ל-$\\ker A$:** דרגו $A$; זהו משתנים חופשיים; כתבו פתרון פרמטרי; "
                "קראו וקטור בסיס לכל משתנה חופשי.\n\n"
                "**צעד 3 — בסיס ל-$\\text{col}(A)$:** דרגו $A$; סמנו **עמודות ציריות** על $A$ **המקורית**; "
                "עמודות אלה מהוות בסיס.\n\n"
                "**צעד 4 — דרגה וגרעין:** דרגה $=$ מספר צירים; גרעין $=n-$דרגה כאשר $n=\\#$ עמודות.\n\n"
                "**צעד 5 — קואורדינטות $[\\vec{v}]_B$:** פתרו $c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n=\\vec{v}$.\n\n"
                "| מטרה | שיטה |\n|---|---|\n"
                "| בסיס ל-span $\\{\\vec{v}_i\\}$ | שורות $\\to$ דירוג $\\to$ שורות ציריות מקוריות |\n"
                "| בסיס ל-$\\ker A$ | דירוג $\\to$ משתנים חופשיים $\\to$ בסיס פרמטרי |\n"
                "| בסיס ל-col$(A)$ | עמודות ציריות של $A$ **המקורית** |\n"
                "| חשב rank$(A)$ | ספור צירים ב-REF |\n"
                "| חשב nullity$(A)$ | $n - \\text{rank}(A)$ |\n"
                "| אמת ש-$B$ בסיס | $|B|=\\dim V$ + בלתי-תלות או פרישה |\n"
                "| בדיקת דרגה-גרעין | דרגה + גרעין = מספר עמודות"
            )

        if kind == "pitfall":
            sec["body_en_md"] = (
                "1. **Keeping the wrong rows/columns after row reduction.** For a basis of the column space, use "
                "the **original** columns (before row reduction) at pivot positions. For a basis of the row space "
                "or a span given as rows, use pivot rows from the reduced form mapped back to original vectors.\n\n"
                "2. **Confusing rank with dimension of the kernel.** rank$(A)=$ number of pivots; "
                "nullity$(A)=n-$rank where $n$ is column count — not row count.\n\n"
                "3. **Using row count in Rank-Nullity.** The theorem uses $n=\\#$ **columns** (domain dimension "
                "of $A:\\mathbb{R}^n\\to\\mathbb{R}^m$). A $6\\times4$ matrix has $n=4$, not $6$.\n\n"
                "4. **Computing coordinates in the wrong order.** $[\\vec{v}]_B=(c_1,c_2,\\ldots)^T$ where "
                "$\\vec{v}=c_1\\vec{b}_1+c_2\\vec{b}_2+\\ldots$ — coefficient order must match basis order.\n\n"
                "5. **Claiming independence for too many vectors.** In an $n$-dimensional space, any set of more "
                "than $n$ vectors is automatically dependent — you cannot have a basis with $n+1$ elements."
            )
            sec["body_he_md"] = (
                "1. **שמירת שורות/עמודות שגויות לאחר דירוג.** לבסיס מרחב עמודות, השתמשו ב**עמודות המקוריות** "
                "(לפני דירוג) במיקומי ציר. לבסיס מרחב שורות או span שנתון כשורות, השתמשו בשורות ציריות "
                "ממופות חזרה לוקטורים מקוריים.\n\n"
                "2. **בלבול בין דרגה לממד הגרעין.** דרגה$(A)=$ מספר צירים; גרעין$(A)=n-$דרגה כאשר $n$ "
                "מספר עמודות — לא שורות.\n\n"
                "3. **שימוש במספר שורות בדרגה-גרעין.** המשפט משתמש ב-$n=\\#$ **עמודות** (ממד דומיין של "
                "$A:\\mathbb{R}^n\\to\\mathbb{R}^m$). מטריצה $6\\times4$ יש לה $n=4$, לא $6$.\n\n"
                "4. **חישוב קואורדינטות בסדר שגוי.** $[\\vec{v}]_B=(c_1,c_2,\\ldots)^T$ — סדר המקדמים "
                "חייב להתאים לסדר הבסיס.\n\n"
                "5. **טענה על בלתי-תלות עם יותר מדי וקטורים.** במרחב $n$-ממדי, כל קבוצה של יותר מ-$n$ "
                "וקטורים תלויה אוטומטית — אי אפשר בסיס עם $n+1$ איברים."
            )

        if sec.get("id") == "why_matters" or (
            kind == "why_matters"
        ):
            sec["body_en_md"] = (
                "Basis and dimension are the vocabulary for **structural** questions in linear algebra: "
                "how large is a subspace? how many degrees of freedom does a solution set have? how does a "
                "linear map split its input?\n\n"
                "**Cross-subject links:** Rank-Nullity connects row reduction (matrices) to kernel/image "
                "(abstract maps). The same counting idea appears in differential equations (dimension of "
                "solution spaces) and statistics (rank of design matrices in regression).\n\n"
                "**Why it matters for exams:** Israeli university linear algebra exams routinely ask for bases "
                "of $\\ker A$, col$(A)$, and spans, then follow with Rank-Nullity proofs about injectivity and "
                "surjectivity. Mastering the row/column distinction here prevents half the errors on midterms."
            )
            sec["body_he_md"] = (
                "בסיס וממד הם אוצר המילים לשאלות **מבניות** באלגברה לינארית: כמה גדול תת-מרחב? "
                "כמה דרגות חופש יש לקבוצת פתרונות? איך העתקה לינארית מחלקת את הקלט?\n\n"
                "**קשרים בין-נושאיים:** דרגה-גרעין מקשר דירוג (מטריצות) לגרעין/אופי (העתקות מופשטות). "
                "אותה ספירה מופיעה במשוואות דיפרנציאליות (ממד מרחבי פתרונות) ובסטטיסטיקה "
                "(דרגת מטריצות עיצוב ברגרסיה).\n\n"
                "**למה זה חשוב לבחינות:** בחינות אלגברה לינארית באוניברסיטאות בישראל שואלות שוב ושוב על "
                "בסיסים ל-$\\ker A$, col$(A)$ ו-span, ואחר כך הוכחות דרגה-גרעין על חד-חד-ערכיות ועל. "
                "שליטה בהבחנה שורה/עמודה כאן מונעת חצי מהטעויות במבחנים."
            )

        if kind == "before_exam":
            sec["body_en_md"] = (
                "**Formula sheet:**\n"
                "- Basis = linearly independent + spanning set\n"
                "- Rank-Nullity: rank$(A)+$nullity$(A)=n$ ($n=\\#$ columns of $A$)\n"
                "- $\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2)$ (Grassmann)\n"
                "- Coordinates: solve $c_1\\vec{b}_1+\\cdots+c_n\\vec{b}_n=\\vec{v}$\n"
                "- In $\\dim V=n$: $n$ independent vectors $\\Leftrightarrow$ basis\n\n"
                "**What Israeli university exams emphasise:**\n"
                "- Finding basis and dimension of $\\ker A$ and col$(A)$ from a given matrix\n"
                "- Applying Rank-Nullity to determine injectivity ($\\ker=\\{0\\}$) and surjectivity ($\\text{Im}=W$)\n"
                "- Coordinate computation in a non-standard basis\n"
                "- Proofs using Grassmann's dimension formula\n\n"
                "**Common proof pattern:** Extend a basis of the kernel/intersection to bases of larger spaces, "
                "then count dimensions."
            )
            sec["body_he_md"] = (
                "**גיליון נוסחאות:**\n"
                "- בסיס = בלתי-תלוי + פורש\n"
                "- דרגה-גרעין: דרגה$(A)+$גרעין$(A)=n$ ($n=\\#$ עמודות של $A$)\n"
                "- $\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2)$ (גרסמן)\n"
                "- קואורדינטות: פתור $c_1\\vec{b}_1+\\cdots=\\vec{v}$\n"
                "- ב-$\\dim V=n$: $n$ וקטורים בלתי-תלויים $\\Leftrightarrow$ בסיס\n\n"
                "**מה בחינות ישראליות מדגישות:**\n"
                "- מציאת בסיס וממד של $\\ker A$ ו-col$(A)$ ממטריצה נתונה\n"
                "- שימוש בדרגה-גרעין לקביעת חד-חד-ערכיות ($\\ker=\\{0\\}$) ועל ($\\text{Im}=W$)\n"
                "- חישוב קואורדינטות בבסיס לא-סטנדרטי\n"
                "- הוכחות עם נוסחת הממד של גרסמן\n\n"
                "**תבנית הוכחה נפוצה:** הרחב בסיס של הגרעין/חיתוך לבסיסים של מרחבים גדולים יותר, ואז ספור ממדים."
            )

        if kind == "summary":
            sec["body_en_md"] = (
                "- A **basis** is a linearly independent spanning set; **dimension** is the number of basis "
                "vectors — the same for every basis of $V$.\n"
                "- In an $n$-dimensional space, any $n$ independent vectors (or any $n$ vectors that span) form a basis.\n"
                "- **Rank-Nullity:** rank$(A)+$nullity$(A)=n$ where $n=\\#$ columns; nullity $=\\dim(\\ker A)$.\n"
                "- Span basis: row-reduce with vectors as rows; keep originals at pivot rows. "
                "Kernel basis: row-reduce $A$, parametrize free variables.\n"
                "- Column space basis: pivot **column positions** on the **original** matrix.\n"
                "- Coordinates $[\\vec{v}]_B$: solve the linear system with basis vectors as columns.\n"
                "- **Grassmann:** $\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2)$."
            )
            sec["body_he_md"] = (
                "- **בסיס** = בלתי-תלוי + פורש; **ממד** = מספר וקטורי בסיס — זהה לכל בסיס של $V$.\n"
                "- במרחב $n$-ממדי, כל $n$ וקטורים בלתי-תלויים (או כל $n$ שפורשים) מהווים בסיס.\n"
                "- **דרגה-גרעין:** דרגה$(A)+$גרעין$(A)=n$ ($n=\\#$ עמודות); גרעין $=\\dim(\\ker A)$.\n"
                "- בסיס ל-span: דירוג עם וקטורים כשורות; שמרו מקוריים בשורות ציריות. "
                "בסיס לגרעין: דרגו $A$, פרמטרו משתנים חופשיים.\n"
                "- בסיס לעמודות: מיקומי עמודות ציריות על המטריצה **המקורית**.\n"
                "- קואורדינטות $[\\vec{v}]_B$: פתרו מערכת עם וקטורי בסיס כעמודות.\n"
                "- **גרסמן:** $\\dim(W_1+W_2)=\\dim W_1+\\dim W_2-\\dim(W_1\\cap W_2)$."
            )

        if kind == "exercise_set":
            sec["body_en_md"] = (
                "Work through every exercise below. **Try each one before opening the solution** — the steps "
                "matter as much as the final answer.\n\n"
                "These drills cover span bases, kernel bases, column spaces, Rank-Nullity, coordinates in standard "
                "and polynomial bases, and short proofs using dimension counting. Always verify Rank-Nullity after "
                "finding $\\ker A$."
            )
            sec["body_he_md"] = (
                "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות "
                "מהתשובה הסופית.\n\n"
                "התרגילים מכסים בסיסי span, בסיסי גרעין, מרחבי עמודות, דרגה-גרעין, קואורדינטות בבסיסים "
                "סטנדרטיים ופולינומיים, והוכחות קצרות בספירת ממדים. תמיד אמתו דרגה-גרעין אחרי מציאת $\\ker A$."
            )

    for i, q in enumerate(data["questions"]):
        if i < len(EXPLANATIONS):
            q["explanation_en"] = EXPLANATIONS[i]["explanation_en"]
            q["explanation_he"] = EXPLANATIONS[i]["explanation_he"]

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {PATH}")


if __name__ == "__main__":
    main()
