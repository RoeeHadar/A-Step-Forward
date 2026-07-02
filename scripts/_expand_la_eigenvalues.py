#!/usr/bin/env python3
"""Expand la_eigenvalues.json — bilingual MIN_WORDS + 80-word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/la_eigenvalues.json"

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
        "body_en_md": """A linear map $A:\\mathbb{R}^n\\to\\mathbb{R}^n$ typically moves vectors in complicated ways — stretching, shearing, and rotating them simultaneously. Yet certain special directions are **preserved**: the map simply **scales** the vector without changing its direction. These directions are the **eigenvectors**, and the scale factors are the **eigenvalues**.

Eigenvalues are fundamental across mathematics and applications: diagonalisation (computing $A^n$ efficiently), stability of differential equations, principal component analysis in statistics, quantum energy levels, vibration modes in engineering, and the PageRank algorithm. Understanding eigenvalues is one of the most important milestones in a linear algebra course.

**Connection to previous material:** Finding eigenvalues requires determinants (the characteristic polynomial $\\det(A-\\lambda I)=0$) and solving homogeneous linear systems (finding eigenvectors in $\\ker(A-\\lambda I)$). You should be comfortable with both before proceeding.""",
        "body_he_md": """העתקה לינארית $A:\\mathbb{R}^n\\to\\mathbb{R}^n$ בדרך כלל מזיזה וקטורים בדרכים מורכבות — מתיחה, גזירה וסיבוב בו-זמנית. ובכל זאת, כיוונים מיוחדים מסוימים **נשמרים**: ההעתקה פשוט **מכפילה** את הוקטור מבלי לשנות את כיוונו. כיוונים אלה הם **וקטורים עצמיים**, וגורמי הכפל הם **ערכים עצמיים**.

ערכים עצמיים הם בסיסיים במתמטיקה וביישומים: אלכסון (חישוב $A^n$ ביעילות), יציבות משוואות דיפרנציאליות, ניתוח רכיבים ראשיים (PCA) בסטטיסטיקה, רמות אנרגיה בקוונטים, מodes רטט בהנדסה, ואלגוריתם PageRank. הבנת ערכים עצמיים היא אחת האבני-דרך החשובות ביותר בקורס אלגברה לינארית.

**קשר לחומר קודם:** מציאת ערכים עצמיים דורשת דטרמיננטות (הפולינום האופייני $\\det(A-\\lambda I)=0$) ופתרון מערכות הומוגניות (מציאת וקטורים עצמיים ב-$\\ker(A-\\lambda I)$). ודאו שאתם בנוחים עם שניהם לפני שממשיכים.""",
    },
    "definition": {
        "body_en_md": """**Definition.** Let $A$ be an $n\\times n$ matrix. A non-zero vector $\\vec{v}\\in\\mathbb{R}^n$ is an **eigenvector** of $A$ with **eigenvalue** $\\lambda\\in\\mathbb{R}$ if
$$A\\vec{v} = \\lambda\\vec{v}.$$
Geometrically, $A$ acts on $\\vec{v}$ by pure scaling — no rotation component along that direction.

**Note:** $\\vec{v}\\neq\\vec{0}$ is required by definition. The zero vector trivially satisfies $A\\vec{0}=\\lambda\\vec{0}$ for any $\\lambda$, so it is excluded. $\\lambda=0$ **is** allowed; a zero eigenvalue means $A$ is singular (not invertible).

**Characteristic polynomial.** $\\lambda$ is an eigenvalue if and only if $(A-\\lambda I)\\vec{v}=\\vec{0}$ has a non-trivial solution, i.e., if and only if $\\det(A-\\lambda I)=0$. The polynomial
$$p(\\lambda) = \\det(A-\\lambda I)$$
is the **characteristic polynomial** of $A$; its degree is $n$ and its roots (over $\\mathbb{R}$ or $\\mathbb{C}$) are the eigenvalues.

**Eigenspace.** For eigenvalue $\\lambda$, the **eigenspace** is
$$E_\\lambda = \\ker(A-\\lambda I) = \\{\\vec{v}: A\\vec{v}=\\lambda\\vec{v}\\}.$$
$E_\\lambda$ is a non-zero subspace whenever $\\lambda$ is an eigenvalue.

**Algebraic multiplicity** $a_\\lambda$ = multiplicity of $\\lambda$ as a root of $p(\\lambda)$.

**Geometric multiplicity** $g_\\lambda = \\dim(E_\\lambda)$.

**Theorem:** $1\\leq g_\\lambda\\leq a_\\lambda$ always.""",
        "body_he_md": """**הגדרה.** יהי $A$ מטריצה $n\\times n$. וקטור לא-אפסי $\\vec{v}\\in\\mathbb{R}^n$ הוא **וקטור עצמי** של $A$ עם **ערך עצמי** $\\lambda\\in\\mathbb{R}$ אם
$$A\\vec{v} = \\lambda\\vec{v}.$$
גיאומטרית, $A$ פועלת על $\\vec{v}$ בכפל טהור — ללא רכיב סיבוב לאורך כיוון זה.

**הערה:** $\\vec{v}\\neq\\vec{0}$ נדרש בהגדרה. הוקטור האפס מקיים $A\\vec{0}=\\lambda\\vec{0}$ לכל $\\lambda$, ולכן אינו נכלל. $\\lambda=0$ **מותר**; ערך עצמי אפס פירושו $A$ סינגולרית (לא הפיכה).

**פולינום אופייני.** $\\lambda$ ערך עצמי אם ורק אם $\\det(A-\\lambda I)=0$. הפולינום
$$p(\\lambda) = \\det(A-\\lambda I)$$
הוא ה**פולינום האופייני** של $A$; מעלתו $n$ ושורשיו (מעל $\\mathbb{R}$ או $\\mathbb{C}$) הם הערכים העצמיים.

**מרחב עצמי.** לערך עצמי $\\lambda$, ה**מרחב העצמי** הוא
$$E_\\lambda = \\ker(A-\\lambda I) = \\{\\vec{v}: A\\vec{v}=\\lambda\\vec{v}\\}.$$
$E_\\lambda$ הוא תת-מרחב לא-אפסי בכל פעם ש-$\\lambda$ ערך עצמי.

**ריבוי אלגברי** $a_\\lambda$ = ריבוי $\\lambda$ כשורש של $p(\\lambda)$.

**ריבוי גיאומטרי** $g_\\lambda = \\dim(E_\\lambda)$.

**משפט:** $1\\leq g_\\lambda\\leq a_\\lambda$ תמיד.""",
    },
    "theory": {
        "body_en_md": """**Theorem 1 (Triangular matrices).** The eigenvalues of a triangular matrix (upper or lower) are its diagonal entries. Proof: for upper triangular $A$, $A-\\lambda I$ is also upper triangular, so $\\det(A-\\lambda I)=\\prod_i(a_{ii}-\\lambda_i)$.

**Theorem 2 (Similar matrices).** If $B=P^{-1}AP$ (similar matrices), then $B$ and $A$ have the same characteristic polynomial and hence the same eigenvalues. Eigenvectors transform as $\\vec{w}=P^{-1}\\vec{v}$.

**Theorem 3 (Zero eigenvalue).** $\\lambda=0$ is an eigenvalue of $A$ if and only if $A$ is singular (not invertible), i.e., $\\det(A)=0$.

**Theorem 4 (Trace and determinant).** For an $n\\times n$ matrix with eigenvalues $\\lambda_1,\\ldots,\\lambda_n$ (counting algebraic multiplicity):
$$\\text{tr}(A) = \\sum_{i=1}^n \\lambda_i, \\qquad \\det(A) = \\prod_{i=1}^n \\lambda_i.$$
These identities hold even when eigenvalues are complex.

**Theorem 5 (Independence of eigenvectors for distinct eigenvalues).**
If $\\lambda_1,\\ldots,\\lambda_k$ are **distinct** eigenvalues of $A$ with corresponding eigenvectors $\\vec{v}_1,\\ldots,\\vec{v}_k$, then $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ is linearly independent.

*Proof by induction on $k$:* Base $k=1$: single non-zero vector is independent. Inductive step: suppose $\\sum_{i=1}^k c_i\\vec{v}_i=\\vec{0}$ $(*)$. Apply $A$: $\\sum c_i\\lambda_i\\vec{v}_i=\\vec{0}$ $(**)$. Subtract $\\lambda_k$ times $(*)$: $\\sum_{i=1}^{k-1}c_i(\\lambda_i-\\lambda_k)\\vec{v}_i=\\vec{0}$. By induction, $c_i(\\lambda_i-\\lambda_k)=0$; since $\\lambda_i\\neq\\lambda_k$, $c_i=0$. Then $c_k\\vec{v}_k=\\vec{0}\\Rightarrow c_k=0$. $\\blacksquare$""",
        "body_he_md": """**משפט 1 (מטריצות משולשות).** הערכים העצמיים של מטריצה משולשת (עליונה או תחתונה) הם הכניסות האלכסוניות שלה. הוכחה: ל-$A$ משולשת עליונה, גם $A-\\lambda I$ משולשת עליונה, ולכן $\\det(A-\\lambda I)=\\prod_i(a_{ii}-\\lambda_i)$.

**משפט 2 (מטריצות דומות).** אם $B=P^{-1}AP$ (מטריצות דומות), אז ל-$B$ ול-$A$ אותו פולינום אופייני ואותם ערכים עצמיים. וקטורים עצמיים מתהפכים כ-$\\vec{w}=P^{-1}\\vec{v}$.

**משפט 3 (ערך עצמי אפס).** $\\lambda=0$ ערך עצמי של $A$ אם ורק אם $A$ סינגולרית (לא הפיכה), כלומר $\\det(A)=0$.

**משפט 4 (עקבה ודטרמיננטה).** למטריצה $n\\times n$ עם ערכים עצמיים $\\lambda_1,\\ldots,\\lambda_n$ (כולל ריבוי אלגברי):
$$\\text{tr}(A) = \\sum_{i=1}^n \\lambda_i, \\qquad \\det(A) = \\prod_{i=1}^n \\lambda_i.$$
הזהויות נכונות גם כשהערכים העצמיים מרוכבים.

**משפט 5 (בלתי-תלות של ו\"ע לערכים שונים).**
אם $\\lambda_1,\\ldots,\\lambda_k$ **ערכים עצמיים שונים** של $A$ עם ו\"ע $\\vec{v}_1,\\ldots,\\vec{v}_k$, אז $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ בלתי-תלויים.

*הוכחה באינדוקציה על $k$:* בסיס $k=1$: וקטור לא-אפסי בלתי-תלוי. שלב אינדוקציה: נניח $\\sum c_i\\vec{v}_i=\\vec{0}$ $(*)$. הפעל $A$: $\\sum c_i\\lambda_i\\vec{v}_i=\\vec{0}$ $(**)$. חסר $\\lambda_k$ כפול $(*)$: $\\sum_{i<k}c_i(\\lambda_i-\\lambda_k)\\vec{v}_i=\\vec{0}$. מהנחת האינדוקציה $c_i=0$; מכיוון $\\lambda_i\\neq\\lambda_k$, כל $c_i=0$. לכן $c_k=0$. $\\blacksquare$""",
    },
    "worked_example_1": {
        "body_en_md": """**Find the eigenvalues and eigenvectors of** $A = \\begin{pmatrix}3&1\\\\0&2\\end{pmatrix}$.

$A$ is upper triangular, so we could read eigenvalues from the diagonal — but we verify via the characteristic polynomial to practice the full method.

### Move 1
Form $A-\\lambda I$ by subtracting $\\lambda$ from each diagonal entry, then compute the determinant. For an upper triangular matrix the determinant is the product of diagonal entries:
$$p(\\lambda) = \\det(A-\\lambda I) = \\det\\begin{pmatrix}3-\\lambda&1\\\\0&2-\\lambda\\end{pmatrix} = (3-\\lambda)(2-\\lambda).$$

### Move 2
Set $p(\\lambda)=0$:
$$\\lambda_1=3,\\quad \\lambda_2=2.$$

### Move 3
Eigenspace for $\\lambda_1=3$: solve $(A-3I)\\vec{v}=\\vec{0}$:
$$(A-3I)=\\begin{pmatrix}0&1\\\\0&-1\\end{pmatrix}\\to\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix} \\Rightarrow v_2=0,\\; v_1\\text{ free}.$$
$$E_3=\\text{span}\\{(1,0)^T\\}, \\quad g_3=1.$$

### Move 4
Eigenspace for $\\lambda_2=2$: solve $(A-2I)\\vec{v}=\\vec{0}$:
$$(A-2I)=\\begin{pmatrix}1&1\\\\0&0\\end{pmatrix} \\Rightarrow v_1=-v_2.$$
$$E_2=\\text{span}\\{(-1,1)^T\\}, \\quad g_2=1.$$

**Check:** $A(1,0)^T=(3,0)^T=3(1,0)^T$ ✓ and $A(-1,1)^T=(-2,2)^T=2(-1,1)^T$ ✓.

**Multiplicities:** Both eigenvalues are simple roots of $p(\\lambda)$, so $a_\\lambda=g_\\lambda=1$ for each. The matrix is therefore diagonalizable — it has two linearly independent eigenvectors spanning $\\mathbb{R}^2$. This pattern (distinct eigenvalues on a triangular matrix) is the easiest diagonalizability case you will encounter.""",
        "body_he_md": """**מצאו את הערכים העצמיים והוקטורים העצמיים של** $A = \\begin{pmatrix}3&1\\\\0&2\\end{pmatrix}$.

$A$ משולשת עליונה, ולכן אפשר לקרוא ע\"ע מהאלכסון — אך נאמת דרך הפולינום האופייני כדי לתרגל את השיטה המלאה.

### צעד 1
בנו $A-\\lambda I$ על ידי חיסור $\\lambda$ מכל כניסה אלכסונית, ואז חשבו דטרמיננטה. למטריצה משולשת עליונה הדטרמיננטה היא מכפלת הכניסות האלכסוניות:
$$p(\\lambda) = \\det\\begin{pmatrix}3-\\lambda&1\\\\0&2-\\lambda\\end{pmatrix} = (3-\\lambda)(2-\\lambda).$$

### צעד 2
מ-$p(\\lambda)=0$:
$$\\lambda_1=3,\\quad \\lambda_2=2.$$

### צעד 3
מרחב עצמי ל-$\\lambda_1=3$: פתרו $(A-3I)\\vec{v}=\\vec{0}$:
$$(A-3I)=\\begin{pmatrix}0&1\\\\0&-1\\end{pmatrix}\\to\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix} \\Rightarrow v_2=0,\\; v_1\\text{ חופשי}.$$
$$E_3=\\text{span}\\{(1,0)^T\\}, \\quad g_3=1.$$

### צעד 4
מרחב עצמי ל-$\\lambda_2=2$: פתרו $(A-2I)\\vec{v}=\\vec{0}$:
$$(A-2I)=\\begin{pmatrix}1&1\\\\0&0\\end{pmatrix} \\Rightarrow v_1=-v_2.$$
$$E_2=\\text{span}\\{(-1,1)^T\\}, \\quad g_2=1.$$

**בדיקה:** $A(1,0)^T=3(1,0)^T$ ✓ ו-$A(-1,1)^T=2(-1,1)^T$ ✓.

**ריבויים:** שני הע\"ע הם שורשים פשוטים של $p(\\lambda)$, ולכן $a_\\lambda=g_\\lambda=1$ לכל אחד. המטריצה ניתנת לאלכסון — יש שני ו\"ע בלתי-תלויים שמspanים את $\\mathbb{R}^2$. דפוס זה (ע\"ע שונים במטריצה משולשת) הוא מקרה האלכסוניות הפשוט ביותר.""",
    },
    "worked_example_2": {
        "body_en_md": """**Find the eigenvalues and eigenvectors of** the symmetric matrix $A = \\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}$.

### Move 1 — Characteristic polynomial
Expand the determinant carefully — for a symmetric matrix the arithmetic is the same as for any $2\\times2$ matrix:
$$p(\\lambda) = \\det\\begin{pmatrix}2-\\lambda&1\\\\1&2-\\lambda\\end{pmatrix} = (2-\\lambda)^2-1 = \\lambda^2-4\\lambda+3 = (\\lambda-1)(\\lambda-3).$$

### Move 2 — Eigenvalues
$$\\lambda_1=1, \\quad \\lambda_2=3.$$

### Move 3 — Eigenspace $E_1$ ($\\lambda=1$)
Row-reduce $(A-I)$ to find all vectors scaled by $\\lambda=1$:
$$(A-I) = \\begin{pmatrix}1&1\\\\1&1\\end{pmatrix} \\to \\begin{pmatrix}1&1\\\\0&0\\end{pmatrix}. \\quad v_1=-v_2. \\quad E_1=\\text{span}\\{(-1,1)^T\\}.$$

### Move 4 — Eigenspace $E_3$ ($\\lambda=3$)
Similarly for $\\lambda=3$, solve $(A-3I)\\vec{v}=\\vec{0}$:
$$(A-3I) = \\begin{pmatrix}-1&1\\\\1&-1\\end{pmatrix} \\to \\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}. \\quad v_1=v_2. \\quad E_3=\\text{span}\\{(1,1)^T\\}.$$

**Observation:** The eigenvectors $(-1,1)^T$ and $(1,1)^T$ are **orthogonal** (dot product $-1+1=0$). This is guaranteed by the **Spectral Theorem** for real symmetric matrices: distinct eigenvalues yield orthogonal eigenspaces.

**Sanity checks:** tr$(A)=2+2=4=1+3$ ✓ and $\\det(A)=4-1=3=1\\cdot3$ ✓. Both multiplicities equal one, so $A$ is diagonalizable with an orthogonal eigenvector matrix $P$ — a preview of the spectral decomposition covered in the orthogonality lesson.""",
        "body_he_md": """**מצאו ערכים ווקטורים עצמיים** של המטריצה הסימטרית $A = \\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}$.

### צעד 1 — פולינום אופייני
פתחו את הדטרמיננטה בזהירות — למטריצה סימטרית החשבון זהה לכל $2\\times2$:
$$p(\\lambda) = (2-\\lambda)^2-1 = \\lambda^2-4\\lambda+3 = (\\lambda-1)(\\lambda-3).$$

### צעד 2 — ערכים עצמיים
$$\\lambda_1=1, \\quad \\lambda_2=3.$$

### צעד 3 — מרחב עצמי $E_1$ ($\\lambda=1$)
דרגו $(A-I)$ כדי למצוא את כל הוקטורים ש-$A$ מכפיל ב-$\\lambda=1$:
$$(A-I) = \\begin{pmatrix}1&1\\\\1&1\\end{pmatrix} \\to \\begin{pmatrix}1&1\\\\0&0\\end{pmatrix}. \\quad v_1=-v_2. \\quad E_1=\\text{span}\\{(-1,1)^T\\}.$$

### צעד 4 — מרחב עצמי $E_3$ ($\\lambda=3$)
באופן דומה ל-$\\lambda=3$, פתרו $(A-3I)\\vec{v}=\\vec{0}$:
$$(A-3I) = \\begin{pmatrix}-1&1\\\\1&-1\\end{pmatrix} \\to \\begin{pmatrix}1&-1\\\\0&0\\end{pmatrix}. \\quad v_1=v_2. \\quad E_3=\\text{span}\\{(1,1)^T\\}.$$

**תצפית:** הו\"ע $(-1,1)^T$ ו-$(1,1)^T$ **אורתוגונליים** (מכפלה סקalarית $-1+1=0$). זה מובטח על ידי **משפט הספקטרום** למטריצות סימטריות ממשיות: ע\"ע שונים נותנים מרחבים עצמיים אורתוגונליים.

**בדיקות שפיות:** tr$(A)=4=1+3$ ✓ ו-$\\det(A)=3=1\\cdot3$ ✓. שני הריבויים שווים ל-1, ולכן $A$ ניתנת לאלכסון עם מטריצת ו\"ע אורתוגונלית $P$ — תצוגה מקדימה של הפירוק הספקטרלי בשיעור האורתוגונליות.""",
    },
    "worked_example_3": {
        "body_en_md": """**Claim:** If $\\lambda_1,\\ldots,\\lambda_k$ are distinct eigenvalues of $A$ with corresponding non-zero eigenvectors $\\vec{v}_1,\\ldots,\\vec{v}_k$, then $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ is linearly independent.

**Proof by induction on $k$:**

**Base case ($k=1$):** $\\{\\vec{v}_1\\}$ is independent since $\\vec{v}_1\\neq\\vec{0}$. ✓

**Inductive step:** Assume the result holds for any $k-1$ eigenvectors with distinct eigenvalues. Suppose
$$c_1\\vec{v}_1+c_2\\vec{v}_2+\\cdots+c_k\\vec{v}_k = \\vec{0}. \\quad (*)$$

**Apply $A$ to $(*)$:**
$$c_1 A\\vec{v}_1+\\cdots+c_k A\\vec{v}_k = \\vec{0} \\Rightarrow c_1\\lambda_1\\vec{v}_1+\\cdots+c_k\\lambda_k\\vec{v}_k=\\vec{0}. \\quad (**)$$

**Compute $(**) - \\lambda_k \\cdot (*)$:**
$$c_1(\\lambda_1-\\lambda_k)\\vec{v}_1+c_2(\\lambda_2-\\lambda_k)\\vec{v}_2+\\cdots+c_{k-1}(\\lambda_{k-1}-\\lambda_k)\\vec{v}_{k-1}=\\vec{0}.$$

**By the induction hypothesis**, $\\{\\vec{v}_1,\\ldots,\\vec{v}_{k-1}\\}$ is independent, so:
$$c_i(\\lambda_i-\\lambda_k)=0 \\quad \\forall i=1,\\ldots,k-1.$$

**Since eigenvalues are distinct**, $\\lambda_i-\\lambda_k\\neq0$, so $c_i=0$ for $i=1,\\ldots,k-1$.

**Substituting back into $(*)$:** $c_k\\vec{v}_k=\\vec{0}$. Since $\\vec{v}_k\\neq\\vec{0}$, $c_k=0$.

All $c_i=0$, so $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ is linearly independent. $\\blacksquare$

**Why this matters:** This theorem guarantees that $k$ distinct eigenvalues produce $k$ independent eigenvectors — the foundation for diagonalisation. When all $n$ eigenvalues of an $n\\times n$ matrix are distinct, diagonalizability follows immediately without checking multiplicities.""",
        "body_he_md": """**טענה:** אם $\\lambda_1,\\ldots,\\lambda_k$ ערכים עצמיים **שונים** של $A$ עם ו\"ע לא-אפסיים $\\vec{v}_1,\\ldots,\\vec{v}_k$, אז $\\{\\vec{v}_1,\\ldots,\\vec{v}_k\\}$ בלתי-תלויים.

**הוכחה באינדוקציה על $k$:**

**בסיס ($k=1$):** $\\{\\vec{v}_1\\}$ בלתי-תלוי כי $\\vec{v}_1\\neq\\vec{0}$. ✓

**שלב האינדוקציה:** נניח נכון ל-$k-1$ ו\"ע עם ע\"ע שונים. נניח
$$\\sum_{i=1}^k c_i\\vec{v}_i=\\vec{0}. \\quad (*)$$

**הפעל $A$ על $(*)$:**
$$\\sum_{i=1}^k c_i\\lambda_i\\vec{v}_i=\\vec{0}. \\quad (**)$$

**חשב $(**) - \\lambda_k \\cdot (*)$:**
$$\\sum_{i=1}^{k-1}c_i(\\lambda_i-\\lambda_k)\\vec{v}_i=\\vec{0}.$$

**מהנחת האינדוקציה:** $c_i(\\lambda_i-\\lambda_k)=0$ לכל $i<k$. מכיוון שהערכים שונים, $\\lambda_i-\\lambda_k\\neq0$, ולכן $c_i=0$.

**הצבה חוזרת ב-$(*)$:** $c_k\\vec{v}_k=\\vec{0}$, ולכן $c_k=0$.

כל $c_i=0$, ולכן הקבוצה בלתי-תלויה. $\\blacksquare$

**למה זה חשוב:** המשפט מבטיח ש-$k$ ע\"ע שונים נותנים $k$ ו\"ע בלתי-תלויים — הבסיס לאלכסון. כשכל $n$ הע\"ע של מטריצה $n\\times n$ שונים, אלכסוניות נובעת מיד ללא בדיקת ריבויים.""",
    },
    "method_guide": {
        "body_en_md": """**Step 1:** Form $A-\\lambda I$ by subtracting $\\lambda$ from each diagonal entry of $A$.

**Step 2:** Compute $p(\\lambda)=\\det(A-\\lambda I)$ — a polynomial of degree $n$ in $\\lambda$.

**Step 3:** Solve $p(\\lambda)=0$ for the eigenvalues $\\lambda_1,\\ldots,\\lambda_n$ (over $\\mathbb{R}$ or $\\mathbb{C}$ as required).

**Step 4:** For each $\\lambda_i$, row-reduce $A-\\lambda_i I$ and find a basis for $\\ker(A-\\lambda_i I)=E_{\\lambda_i}$.

**Step 5:** Record algebraic multiplicity (root order in $p$) and geometric multiplicity ($\\dim E_{\\lambda_i}$).

| Check | Meaning |
|---|---|
| $g_\\lambda < a_\\lambda$ | Matrix is NOT diagonalizable (for this $\\lambda$) |
| $g_\\lambda = a_\\lambda$ for ALL $\\lambda$ | Matrix IS diagonalizable |
| tr$(A)=\\sum\\lambda_i$ | Quick sanity check on eigenvalue sum |
| $\\det(A)=\\prod\\lambda_i$ | Quick sanity check on eigenvalue product |

**Shortcuts:** Triangular/diagonal matrices — eigenvalues are diagonal entries. Symmetric matrices — all real eigenvalues, orthogonal eigenvectors.""",
        "body_he_md": """**צעד 1:** בנו $A-\\lambda I$ על ידי חיסור $\\lambda$ מכל כניסה אלכסונית של $A$.

**צעד 2:** חשבו $p(\\lambda)=\\det(A-\\lambda I)$ — פולינום במעלה $n$ ב-$\\lambda$.

**צעד 3:** פתרו $p(\\lambda)=0$ לערכים העצמיים $\\lambda_1,\\ldots$ (מעל $\\mathbb{R}$ או $\\mathbb{C}$ לפי הדרישה).

**צעד 4:** לכל $\\lambda_i$, דרגו $A-\\lambda_i I$ ומצאו בסיס ל-$\\ker(A-\\lambda_i I)=E_{\\lambda_i}$.

**צעד 5:** רשמו ריבוי אלגברי (ריבוי שורש ב-$p$) וריבוי גיאומטרי ($\\dim E_{\\lambda_i}$).

| בדיקה | משמעות |
|---|---|
| $g_\\lambda < a_\\lambda$ | המטריצה **אינה** ניתנת לאלכסון (לע\"ע זה) |
| $g_\\lambda = a_\\lambda$ לכל $\\lambda$ | המטריצה **ניתנת** לאלכסון |
| tr$(A)=\\sum\\lambda_i$ | בדיקת שפיות — סכום ע\"ע |
| $\\det(A)=\\prod\\lambda_i$ | בדיקת שפיות — מכפלת ע\"ע |

**קיצורי דרך:** מטריצות משולשות/אלכסוניות — ע\"ע = כניסות אלכסון. מטריצות סימטריות — כל ע\"ע ממשיים, ו\"ע אורתוגונליים.""",
    },
    "pitfall": {
        "body_en_md": """1. **Including $\\vec{0}$ as an eigenvector.** By definition, eigenvectors must be non-zero. The zero vector trivially satisfies $A\\vec{0}=\\lambda\\vec{0}$ for any $\\lambda$ — it is excluded to keep eigenvectors meaningful as directions.

2. **Wrong sign in $\\det(A-\\lambda I)$.** It is $A-\\lambda I$, not $\\lambda I - A$. The roots are the same, but the leading coefficient of $p(\\lambda)$ flips — this matters when reading off the polynomial.

3. **Forgetting that eigenspaces have dimension $\\geq1$.** Once $\\lambda$ is confirmed as an eigenvalue, $E_\\lambda$ always contains at least one non-zero vector. You should always find at least one eigenvector.

4. **Confusing algebraic and geometric multiplicity.** Algebraic multiplicity counts how many times $\\lambda$ appears as a root of $p(\\lambda)$; geometric multiplicity is $\\dim(E_\\lambda)$. They need not be equal — when $g<a$, the matrix is defective at that eigenvalue.

5. **Missing complex eigenvalues.** Real matrices may have complex eigenvalues appearing in conjugate pairs. If working over $\\mathbb{R}$ only, state clearly when no real eigenvalues exist.""",
        "body_he_md": """1. **כלילת $\\vec{0}$ כוקטור עצמי.** לפי הגדרה, ו\"ע חייבים להיות לא-אפסיים. הוקטור האפס מקיים $A\\vec{0}=\\lambda\\vec{0}$ לכל $\\lambda$ — הוא מוחרג כדי שו\"ע יישארו כיוונים משמעותיים.

2. **סימן שגוי ב-$\\det(A-\\lambda I)$.** זהו $A-\\lambda I$, לא $\\lambda I-A$. השורשים זהים, אך המקדם המוביל של $p(\\lambda)$ מתהפך — חשוב בקריאת הפולינום.

3. **שכחה שמרחבים עצמיים בממד $\\geq1$.** ברגע ש-$\\lambda$ מאושר כע\"ע, $E_\\lambda$ תמיד מכיל לפחות ו\"ע אחד לא-אפסי.

4. **בלבול ריבוי אלגברי וגיאומטרי.** ריבוי אלגברי = כמה פעמים $\\lambda$ מופיע כשורש ב-$p(\\lambda)$; ריבוי גיאומטרי = $\\dim(E_\\lambda)$. הם לא חייבים להיות שווים — כש-$g<a$, המטריצה פגומה בע\"ע זה.

5. **פספוס ע\"ע מרוכבים.** למטריצות ממשיות ע\"ע מרוכבים מגיעים בזוגות מצומדים. בעבודה מעל $\\mathbb{R}$ בלבד, ציינו במפורש כשאין ע\"ע ממשיים.""",
    },
    "why_matters": {
        "body_en_md": """Eigenvalues are not abstract labels — they encode how a linear system evolves, oscillates, or decays over time.

**Differential equations:** Solutions of $\\dot{\\vec{x}}=A\\vec{x}$ are built from eigenmodes $e^{\\lambda t}\\vec{v}$. The sign of $\\Re(\\lambda)$ determines stability.

**Data science:** PCA finds eigenvectors of the covariance matrix — the directions of maximum variance in a dataset.

**Physics & engineering:** Normal modes of vibration, quantum energy levels, and structural resonance frequencies are all eigenvalue problems.

**Builds on:** `concept:la_determinants` **Determinants** and `concept:la_vector_spaces` **Vector Spaces**.

**Unlocks:** `concept:la_diagonalization` **Diagonalization** and `concept:differential_equations_intro` **Differential Equations Intro**.

**Exam transfer:** Israeli university exams reward computing all eigenvalues/eigenvectors of $2\\times2$ and $3\\times3$ matrices quickly and correctly.""",
        "body_he_md": """ערכים עצמיים אינם תוויות מופשטות — הם מקודדים כיצד מערכת לינארית מתפתחת, מתנודדת או דועכת לאורך זמן.

**משוואות דיפרנציאליות:** פתרונות $\\dot{\\vec{x}}=A\\vec{x}$ נבנים ממodes עצמיים $e^{\\lambda t}\\vec{v}$. הסימן של $\\Re(\\lambda)$ קובע יציבות.

**מדע נתונים:** PCA מוצא ו\"ע של מטריצת השונות — הכיוונים של השונות המקסימלית בנתונים.

**פיזיקה והנדסה:** מodes נורמליים של רטט, רמות אנרגיה קוונטיות, ותדרי תהודה מבניים — כולם בעיות ע\"ע.

**מבוסס על:** `concept:la_determinants` **דטרמיננטות** ו-`concept:la_vector_spaces` **מרחבי וקטורים**.

**פותח:** `concept:la_diagonalization` **אלכסון** ו-`concept:differential_equations_intro` **מבוא למשוואות דיפרנציאליות**.

**העברה לבחינה:** בחינות באוניברסיטה בישראל מעריכות חישוב מהיר ונכון של כל ע\"ע וו\"ע למטריצות $2\\times2$ ו-$3\\times3$.""",
    },
    "before_exam": {
        "body_en_md": """**Formula sheet:**
- $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$
- $p(\\lambda)=\\det(A-\\lambda I)=0$
- $E_\\lambda=\\ker(A-\\lambda I)$
- $1\\leq g_\\lambda\\leq a_\\lambda$
- tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$
- Triangular/diagonal: eigenvalues = diagonal entries

**What Israeli university exams emphasise:**
- Finding all eigenvalues and eigenvectors of a $2\\times2$ or $3\\times3$ matrix (main bulk of marks).
- Distinguishing algebraic vs geometric multiplicity.
- Proving structural properties (eigenvectors of $A^k$, $A^{-1}$).
- Checking diagonalisability: $g_\\lambda=a_\\lambda$ for all $\\lambda$.

**Exam tip:** Always verify eigenvectors by computing $A\\vec{v}-\\lambda\\vec{v}$ and confirming the result is $\\vec{0}$. One substitution catches sign and arithmetic errors instantly.""",
        "body_he_md": """**גיליון נוסחאות:**
- $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$
- $p(\\lambda)=\\det(A-\\lambda I)=0$
- $E_\\lambda=\\ker(A-\\lambda I)$
- $1\\leq g_\\lambda\\leq a_\\lambda$
- tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$
- משולשת/אלכסונית: ע\"ע = כניסות אלכסון

**מה בחינות ישראליות מדגישות:**
- מציאת כל ע\"ע וו\"ע של $2\\times2$ או $3\\times3$ (רוב הניקוד).
- הבחנה ריבוי אלגברי לעומת גיאומטרי.
- הוכחת תכונות (ו\"ע של $A^k$, $A^{-1}$).
- בדיקת אלכסוניות: $g_\\lambda=a_\\lambda$ לכל $\\lambda$.

**טיפ לבחינה:** תמיד אמתו ו\"ע בחישוב $A\\vec{v}-\\lambda\\vec{v}$ וודאו שהתוצאה $\\vec{0}$. הצבה אחת תופסת טעויות סימן וחשבון.""",
    },
    "summary": {
        "body_en_md": """- **Eigenvalue equation:** $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$.
- **Characteristic polynomial:** $p(\\lambda)=\\det(A-\\lambda I)$; roots are eigenvalues.
- **Eigenspace:** $E_\\lambda=\\ker(A-\\lambda I)$, always non-trivial when $\\lambda$ is an eigenvalue.
- **Multiplicities:** $1\\leq g_\\lambda\\leq a_\\lambda$; equality for all $\\lambda$ $\\Leftrightarrow$ diagonalizable.
- **Key identities:** tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$.
- **Triangular matrices:** eigenvalues are diagonal entries.
- **Distinct eigenvalues:** corresponding eigenvectors are linearly independent.

**Takeaway:** Given any square matrix, you should now compute all eigenvalues, find eigenvector bases for each eigenspace, and report both multiplicities.""",
        "body_he_md": """- **משוואת ע\"ע:** $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$.
- **פולינום אופייני:** $p(\\lambda)=\\det(A-\\lambda I)$; שורשים = ע\"ע.
- **מרחב עצמי:** $E_\\lambda=\\ker(A-\\lambda I)$, תמיד לא-טריוויאלי כש-$\\lambda$ ע\"ע.
- **ריבויים:** $1\\leq g_\\lambda\\leq a_\\lambda$; שוויון לכל $\\lambda$ $\\Leftrightarrow$ ניתנת לאלכסון.
- **זהויות:** tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$.
- **מטריצות משולשות:** ע\"ע = כניסות אלכסון.
- **ע\"ע שונים:** הו\"ע המתאימים בלתי-תלויים.

**מסקנה:** עבור כל מטריצה ריבועית, אתם אמורים לחשב כל ע\"ע, למצוא בסיס ו\"ע לכל מרחב עצמי, ולדווח על שני הריבויים.""",
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": """$A=\\begin{pmatrix}4&0\\\\0&-3\\end{pmatrix}$ is **diagonal**, so by Theorem 1 the eigenvalues are the diagonal entries without any computation:
$$\\lambda_1=4, \\quad \\lambda_2=-3.$$

**Eigenvectors:** For $\\lambda_1=4$, solve $(A-4I)\\vec{v}=\\vec{0}$: $\\begin{pmatrix}0&0\\\\0&-7\\end{pmatrix}\\vec{v}=\\vec{0}$ gives $v_2=0$, $v_1$ free, so $\\vec{v}_1=(1,0)^T$.

For $\\lambda_2=-3$, $(A+3I)\\vec{v}=\\vec{0}$ gives $v_1=0$, $v_2$ free, so $\\vec{v}_2=(0,1)^T$.

**Verify:** $A(1,0)^T=(4,0)^T=4(1,0)^T$ ✓ and $A(0,1)^T=(0,-3)^T=-3(0,1)^T$ ✓.""",
        "checkpoint_solution_he": """$A=\\begin{pmatrix}4&0\\\\0&-3\\end{pmatrix}$ **אלכסונית**, ולכן לפי משפט 1 הערכים העצמיים הם הכניסות האלכסוניות ללא חישוב:
$$\\lambda_1=4, \\quad \\lambda_2=-3.$$

**וקטורים עצמיים:** ל-$\\lambda_1=4$, פתרו $(A-4I)\\vec{v}=\\vec{0}$: $v_2=0$, $v_1$ חופשי, $\\vec{v}_1=(1,0)^T$.

ל-$\\lambda_2=-3$, $(A+3I)\\vec{v}=\\vec{0}$ נותן $v_1=0$, $v_2$ חופשי, $\\vec{v}_2=(0,1)^T$.

**אימות:** $A(1,0)^T=4(1,0)^T$ ✓ ו-$A(0,1)^T=-3(0,1)^T$ ✓.""",
    },
    {
        "checkpoint_solution_en": """Compute the characteristic polynomial:
$$p(\\lambda)=\\det\\begin{pmatrix}1-\\lambda&2\\\\2&1-\\lambda\\end{pmatrix}=(1-\\lambda)^2-4=\\lambda^2-2\\lambda-3=(\\lambda-3)(\\lambda+1).$$

**Eigenvalues:** $\\lambda=3$ with algebraic multiplicity $a=1$; $\\lambda=-1$ with $a=1$.

Both roots are simple (multiplicity 1), so $g_\\lambda=a_\\lambda=1$ for each — the matrix is diagonalizable over $\\mathbb{R}$.""",
        "checkpoint_solution_he": """חשבו את הפולינום האופייני:
$$p(\\lambda)=(1-\\lambda)^2-4=\\lambda^2-2\\lambda-3=(\\lambda-3)(\\lambda+1).$$

**ערכים עצמיים:** $\\lambda=3$ עם ריבוי אלגברי $a=1$; $\\lambda=-1$ עם $a=1$.

שני השורשים פשוטים (ריבוי 1), ולכן $g_\\lambda=a_\\lambda=1$ לכל אחד — המטריצה ניתנת לאלכסון מעל $\\mathbb{R}$.""",
    },
]

EXPLANATIONS = [
    fmt_expl(
        "The matrix $A=\\begin{pmatrix}5&0\\\\0&-2\\end{pmatrix}$ is diagonal. By Theorem 1, eigenvalues of a triangular (here, diagonal) matrix equal its diagonal entries: $\\lambda_1=5$ and $\\lambda_2=-2$. No characteristic polynomial computation is needed, though verifying via $\\det(A-\\lambda I)=(5-\\lambda)(-2-\\lambda)$ confirms the answer.",
        "When you see zeros off the diagonal, check whether the matrix is triangular or diagonal first. If yes, read eigenvalues directly from the diagonal — this saves time and reduces arithmetic errors on exams.",
        "Computing the full characteristic polynomial unnecessarily and making a sign error in $\\det(A-\\lambda I)$. Another trap: listing eigenvalues in wrong order or forgetting the negative sign on $-2$.",
        "For diagonal or triangular matrices, write \"eigenvalues = diagonal entries\" as your first line — examiners award method marks even if later eigenvector work has errors.",
        "המטריצה $A=\\begin{pmatrix}5&0\\\\0&-2\\end{pmatrix}$ אלכסונית. לפי משפט 1, ע\"ע של מטריצה משולשת (כאן אלכסונית) שווים לכניסות האלכסון: $\\lambda_1=5$ ו-$\\lambda_2=-2$. אין צורך בפולינום אופייני, אך $\\det(A-\\lambda I)=(5-\\lambda)(-2-\\lambda)$ מאמת.",
        "כשיש אפסים מחוץ לאלכסון, בדקו אם המטריצה משולשת או אלכסונית. אם כן, קראו ע\"ע ישירות מהאלכסון — חוסך זמן וטעויות חשבון בבחינה.",
        "חישוב פולינום אופייני מיותר וטעות סימן ב-$\\det(A-\\lambda I)$. מלכודת נוספת: שכחת הסימן שלילי על $-2$.",
        "במטריצות אלכסוניות/משולשות, כתבו \"ע\"ע = כניסות אלכסון\" כשורה ראשונה — מרצים נותנים נקודות שיטה גם אם חישוב ו\"ע שגוי.",
    ),
    fmt_expl(
        "To test whether $\\vec{v}=(1,2)^T$ is an eigenvector of $A=3I$, compute $A\\vec{v}$ directly: $A\\vec{v}=\\begin{pmatrix}3&0\\\\0&3\\end{pmatrix}\\begin{pmatrix}1\\\\2\\end{pmatrix}=\\begin{pmatrix}3\\\\6\\end{pmatrix}=3\\begin{pmatrix}1\\\\2\\end{pmatrix}=3\\vec{v}$. Since $A\\vec{v}=3\\vec{v}$ with $\\vec{v}\\neq\\vec{0}$, yes — $\\vec{v}$ is an eigenvector with eigenvalue $\\lambda=3$.",
        "An eigenvector test is always one matrix-vector multiplication: form $A\\vec{v}$ and check whether the result is a scalar multiple of $\\vec{v}$. For $A=3I$, every non-zero vector is an eigenvector with $\\lambda=3$.",
        "Answering \"no\" because the matrix is not diagonal in a different basis, or confusing eigenvector with eigenvalue. Another error: computing $\\vec{v}^T A$ instead of $A\\vec{v}$.",
        "When asked \"is $\\vec{v}$ an eigenvector?\", always show the multiplication $A\\vec{v}=\\ldots$ explicitly — partial credit requires visible work, not just yes/no.",
        "כדי לבדוק אם $\\vec{v}=(1,2)^T$ ו\"ע של $A=3I$, חשבו $A\\vec{v}$: $\\begin{pmatrix}3\\\\6\\end{pmatrix}=3\\begin{pmatrix}1\\\\2\\end{pmatrix}=3\\vec{v}$. מכיוון $A\\vec{v}=3\\vec{v}$ ו-$\\vec{v}\\neq\\vec{0}$, כן — $\\vec{v}$ ו\"ע עם $\\lambda=3$.",
        "בדיקת ו\"ע היא תמיד כפל מטריצה-וקטור אחד: חשבו $A\\vec{v}$ ובדקו אם התוצאה כפולה סקalarית של $\\vec{v}$. ל-$A=3I$, כל וקטור לא-אפסי הוא ו\"ע עם $\\lambda=3$.",
        "תשובה \"לא\" בגלל בסיס אחר, או בלבול ו\"ע וע\"ע. טעות: חישוב $\\vec{v}^T A$ במקום $A\\vec{v}$.",
        "כששואלים \"האם $\\vec{v}$ ו\"ע?\", הציגו את $A\\vec{v}=\\ldots$ — נקודות חלקיות דורשות עבודה גלויה.",
    ),
    fmt_expl(
        "Form $A-\\lambda I=\\begin{pmatrix}-\\lambda&1\\\\-2&3-\\lambda\\end{pmatrix}$ and compute $\\det(A-\\lambda I)=-\\lambda(3-\\lambda)+2=\\lambda^2-3\\lambda+2$. Factor: $(\\lambda-1)(\\lambda-2)=0$, giving $\\lambda_1=1$ and $\\lambda_2=2$. Sanity check: tr$(A)=0+3=3=1+2$ ✓ and $\\det(A)=0\\cdot3-1\\cdot(-2)=2=1\\cdot2$ ✓.",
        "For $2\\times2$ matrices, expand $\\det(A-\\lambda I)$ as $(a-\\lambda)(d-\\lambda)-bc$. Always verify via trace and determinant identities — they catch sign errors immediately.",
        "Expanding as $\\lambda(3-\\lambda)+2$ with wrong sign on the $-2$ entry, yielding $\\lambda^2-3\\lambda-2$ instead. Another slip: finding one root and stopping without factoring completely.",
        "After finding eigenvalues, write tr$(A)=\\sum\\lambda_i$ and $\\det(A)=\\prod\\lambda_i$ on your scratch paper — two free checks that take five seconds.",
        "בנו $A-\\lambda I$ וחשבו $\\det(A-\\lambda I)=-\\lambda(3-\\lambda)+2=\\lambda^2-3\\lambda+2$. פירוק: $(\\lambda-1)(\\lambda-2)=0$, $\\lambda_1=1$, $\\lambda_2=2$. בדיקת שפיות: tr$(A)=3=1+2$ ✓, $\\det(A)=2=1\\cdot2$ ✓. שני השורשים פשוטים, ולכן $g_\\lambda=a_\\lambda=1$.",
        "ל-$2\\times2$, פתחו $\\det(A-\\lambda I)=(a-\\lambda)(d-\\lambda)-bc$. אמתו דרך עקבה ודטרמיננטה — תופס טעויות סימן מיד. אחרי מציאת השורשים, המשיכו למרחבים עצמיים.",
        "פתיחה עם סימן שגוי על $-2$, וקבלת $\\lambda^2-3\\lambda-2$. טעות: מציאת שורש אחד ועצירה.",
        "אחרי מציאת ע\"ע, כתבו tr$(A)=\\sum\\lambda_i$ ו-$\\det(A)=\\prod\\lambda_i$ — שתי בדיקות חינם שתופסות טעויות סימן לפני שממשיכים לו\"ע.",
    ),
    fmt_expl(
        "Theorem 4 states that for any square matrix, tr$(A)$ equals the sum of eigenvalues (with algebraic multiplicity) and $\\det(A)$ equals their product. Given eigenvalues $2$ and $5$: tr$(A)=2+5=7$ and $\\det(A)=2\\cdot5=10$. No matrix entries are needed — these are spectral invariants.",
        "When eigenvalues are given directly, trace and determinant questions test whether you know Theorem 4, not whether you can row-reduce. Apply the sum and product formulas immediately.",
        "Adding incorrectly ($2+5=8$) or computing $\\det=2+5=7$ (confusing sum with product). Another trap: using geometric multiplicity instead of algebraic when eigenvalues are repeated.",
        "Memorize the pair tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$ together — exam questions often ask for both in one part.",
        "משפט 4: tr$(A)$ = סכום ע\"ע (עם ריבוי אלגברי), $\\det(A)$ = מכפלתם. נתונים $2$ ו-$5$: tr$(A)=7$, $\\det(A)=10$. אין צורך בכניסות מטריצה — אלה אינוariants ספקטרליים.",
        "כשנותנים ע\"ע ישירות, שאלות עקבה/דטרמיננטה בודקות משפט 4, לא דירוג. יישמו נוסחאות סכום ומכפלה מיד.",
        "חיבור שגוי או $\\det=2+5=7$ (בלבול סכום ומכפלה). מלכודת: שימוש בריבוי גיאומטרי במקום אלגברי.",
        "שיננו tr$(A)=\\sum\\lambda_i$, $\\det(A)=\\prod\\lambda_i$ — בבחינה שואלים לעיתים על שניהם יחד.",
    ),
    fmt_expl(
        "Compute $p(\\lambda)=\\det\\begin{pmatrix}4-\\lambda&-2\\\\1&1-\\lambda\\end{pmatrix}=(4-\\lambda)(1-\\lambda)+2=\\lambda^2-5\\lambda+6=(\\lambda-2)(\\lambda-3)$. For $\\lambda=2$: $(A-2I)\\to\\begin{pmatrix}2&-2\\\\1&-1\\end{pmatrix}$ gives $v_1=v_2$, so $E_2=\\text{span}\\{(1,1)^T\\}$. For $\\lambda=3$: $(A-3I)\\to\\begin{pmatrix}1&-2\\\\1&-2\\end{pmatrix}$ gives $v_1=2v_2$, so $E_3=\\text{span}\\{(2,1)^T\\}$.",
        "Full eigenvalue/eigenvector problems follow a fixed pipeline: characteristic polynomial → roots → null space for each $\\lambda$. Never skip verifying $A\\vec{v}=\\lambda\\vec{v}$ for at least one eigenvector per eigenvalue.",
        "Sign error in $\\det(A-\\lambda I)$: writing $(4-\\lambda)(1-\\lambda)-2$ instead of $+2$. Another common error: finding eigenvalues correctly but solving $(A-\\lambda I)\\vec{v}=\\vec{0}$ with arithmetic mistakes in row reduction.",
        "On $2\\times2$ eigenvector problems, you can often solve $(A-\\lambda I)\\vec{v}=\\vec{0}$ by inspection once one row is redundant — do not over-row-reduce.",
        "חשבו $p(\\lambda)=(4-\\lambda)(1-\\lambda)+2=\\lambda^2-5\\lambda+6=(\\lambda-2)(\\lambda-3)$. ל-$\\lambda=2$: $v_1=v_2$, $E_2=\\text{span}\\{(1,1)^T\\}$. ל-$\\lambda=3$: $v_1=2v_2$, $E_3=\\text{span}\\{(2,1)^T\\}$. אימתו: $A(1,1)^T=2(1,1)^T$ ו-$A(2,1)^T=3(2,1)^T$.",
        "בעיות מלאות: פולינום אופייני → שורשים → מרחב אפס לכל $\\lambda$. אל תדלגו על אימות $A\\vec{v}=\\lambda\\vec{v}$ לפחות לו\"ע אחד מכל ע\"ע.",
        "טעות סימן: $(4-\\lambda)(1-\\lambda)-2$ במקום $+2$. טעות נוספת: ע\"ע נכונים אך דירוג שגוי ב-$(A-\\lambda I)\\vec{v}=\\vec{0}$.",
        "ב-$2\\times2$ אפשר לפתור $(A-\\lambda I)\\vec{v}=\\vec{0}$ בבדיקה ישירה כששורה מיותרת — אל תדרגו יותר מדי. תמיד הציגו את הו\"ע הסופי ואמתו $A\\vec{v}=\\lambda\\vec{v}$.",
    ),
    fmt_expl(
        "Any diagonal matrix with entries $1,-1,2$ on the diagonal has exactly those eigenvalues. One valid answer is $A=\\begin{pmatrix}1&0&0\\\\0&-1&0\\\\0&0&2\\end{pmatrix}$. Permuting the diagonal entries or applying a similarity transform also works, but the simplest construction places the eigenvalues on the diagonal.",
        "Constructing a matrix with prescribed eigenvalues is the reverse of the usual problem. The easiest method: put eigenvalues on the diagonal of a diagonal matrix. For distinct eigenvalues, any ordering on the diagonal is valid.",
        "Writing a matrix whose **trace** or **determinant** matches but whose actual eigenvalues differ — e.g., a non-triangular matrix with correct trace but wrong spectrum. Another error: using $1,-1,2$ off the diagonal.",
        "When asked to \"find a matrix with eigenvalues ...\", the diagonal construction earns full marks in one line — save elaborate methods for problems that require them.",
        "כל מטריצה אלכסונית עם $1,-1,2$ על האלכסון בעלת בדיוק ע\"ע אלה. תשובה: $A=\\begin{pmatrix}1&0&0\\\\0&-1&0\\\\0&0&2\\end{pmatrix}$. גם תמורת כניסות או דמיון עובד, אך הבנייה הפשוטה שמה ע\"ע על האלכסון.",
        "בניית מטריצה עם ע\"ע נתונים היא הפוכה לבעיה הרגילה. השיטה הקלה: שימו ע\"ע על האלכסון. לע\"ע שונים, כל סדר על האלכסון תקף.",
        "מטריצה עם עקבה/דטרמיננטה נכונים אך ע\"ע שגויים. טעות: $1,-1,2$ מחוץ לאלכסון.",
        "כש\"מצאו מטריצה עם ע\"ע ...\", בנייה אלכסונית נותנת ניקוד מלא בשורה — שמרו שיטות מורכבות לבעיות שדורשות.",
    ),
    fmt_expl(
        "The matrix $A=\\begin{pmatrix}1&0&0\\\\2&3&0\\\\1&1&-1\\end{pmatrix}$ is lower triangular. By Theorem 1, eigenvalues equal diagonal entries: $\\lambda_1=1$, $\\lambda_2=3$, $\\lambda_3=-1$. No determinant expansion is required, though you can verify $\\det(A-\\lambda I)=(1-\\lambda)(3-\\lambda)(-1-\\lambda)$.",
        "Identify triangular structure before computing anything. Upper or lower triangular — eigenvalues are on the diagonal. For $3\\times3$ triangular matrices this saves expanding a cubic characteristic polynomial.",
        "Expanding the full $3\\times3$ determinant and making arithmetic errors when the diagonal shortcut was available. Another trap: reading off-diagonal entries as eigenvalues.",
        "On $3\\times3$ triangular problems, write \"triangular → eigenvalues = diagonal\" first — this single sentence often earns a method mark before any computation.",
        "המטריצה $A=\\begin{pmatrix}1&0&0\\\\2&3&0\\\\1&1&-1\\end{pmatrix}$ משולשת תחתונה. לפי משפט 1, ע\"ע = כניסות אלכסון: $\\lambda_1=1$, $\\lambda_2=3$, $\\lambda_3=-1$. אין צורך בפיתוח דטרמיננטה.",
        "זהו מבנה משולש לפני חישוב. משולשת עליונה/תחתונה — ע\"ע על האלכסון. ב-$3\\times3$ זה חוסך פולינום מעלה 3.",
        "פתיחת דטרמיננטה $3\\times3$ מלאה עם טעויות כשיש קיצור. מלכודת: קריאת כניסות מחוץ לאלכסון כע\"ע.",
        "ב-$3\\times3$ משולשת, כתבו \"משולשת → ע\"ע = אלכסון\" — משפט אחד לעיתים נותן נקודת שיטה.",
    ),
    fmt_expl(
        "First show $\\lambda=0$ is an eigenvalue: $\\det(A)=1\\cdot4-2\\cdot2=4-4=0$, so by Theorem 3, $A$ is singular and $0$ is an eigenvalue. The eigenspace $E_0=\\ker(A)$: solve $A\\vec{v}=\\vec{0}$, i.e., $v_1+2v_2=0$ and $2v_1+4v_2=0$ (dependent rows), giving $v_1=-2v_2$. Thus $E_0=\\text{span}\\{(-2,1)^T\\}$ with geometric multiplicity $g_0=1$.",
        "Zero eigenvalue problems split into two parts: (1) show $\\det(A)=0$ or that $A\\vec{v}=\\vec{0}$ has non-trivial solutions; (2) find $\\ker(A)$ explicitly. Do not skip part (2) when asked for the eigenspace.",
        "Showing $\\det(A)=0$ but failing to find the eigenspace, or writing $E_0=\\{(0,0)^T\\}$ (the zero vector alone is not a basis). Another error: confusing $E_0$ with the entire null space description without span notation.",
        "For $\\lambda=0$, the eigenspace equals $\\ker(A)$ — row-reduce $A$ itself (not $A-\\lambda I$ with $\\lambda=0$, which is the same) and parametrize free variables.",
        "ראשית, $\\det(A)=4-4=0$, ולכן לפי משפט 3, $0$ ע\"ע. $E_0=\\ker(A)$: המשוואות $v_1+2v_2=0$ ו-$2v_1+4v_2=0$ תלויות, $v_1=-2v_2$, $E_0=\\text{span}\\{(-2,1)^T\\}$, $g_0=1$. אימתו: $A(-2,1)^T=(0,0)^T$.",
        "בעיות $\\lambda=0$ בשני חלקים: (1) $\\det(A)=0$; (2) מציאת $\\ker(A)$. אל תדלגו על (2) כשמבקשים מרחב עצמי — זה רוב הניקוד.",
        "הוכחת $\\det(A)=0$ בלי מרחב עצמי, או $E_0=\\{(0,0)^T\\}$. בלבול $E_0$ בלי span.",
        "ל-$\\lambda=0$, המרחב העצמי שווה ל-$\\ker(A)$ — דרגו את $A$ עצמה ופרמטרו משתנים חופשיים. וודאו שהו\"ע שמצאתם אינו הוקטור האפס.",
    ),
]

EXERCISE_SET_BODY = {
    "body_en_md": """Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.

These drills cover the full eigenvalue workflow: characteristic polynomial, eigenspaces, trace/determinant identities, structural proofs ($A^k$, $A^{-1}$, idempotent matrices), and the transpose eigenvalue theorem. Verify every eigenvector by computing $A\\vec{v}-\\lambda\\vec{v}$.""",
    "body_he_md": """פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.

התרגילים מכסים את תהליך הע\"ע המלא: פולינום אופייני, מרחבים עצמיים, זהויות עקבה/דטרמיננטה, הוכחות מבניות ($A^k$, $A^{-1}$, אידמפוטנטיות), ומשפט ע\"ע הטרנספוז. אמתו כל ו\"ע ב-$A\\vec{v}-\\lambda\\vec{v}$.""",
}

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1:** $A=\\begin{pmatrix}5&0\\\\0&-2\\end{pmatrix}$ is diagonal.\n\n**Step 2:** By Theorem 1, eigenvalues are diagonal entries.\n\n**Answer:** $\\lambda_1=5$, $\\lambda_2=-2$.",
        "solution_he": "**צעד 1:** $A$ אלכסונית.\n\n**צעד 2:** לפי משפט 1, ע\"ע = כניסות אלכסון.\n\n**תשובה:** $\\lambda_1=5$, $\\lambda_2=-2$.",
    },
    "e2": {
        "solution_en": "**Step 1:** Compute $A\\vec{v}=\\begin{pmatrix}3\\\\6\\end{pmatrix}=3\\begin{pmatrix}1\\\\2\\end{pmatrix}$.\n\n**Step 2:** Since $A\\vec{v}=3\\vec{v}$ with $\\vec{v}\\neq\\vec{0}$, yes.\n\n**Answer:** Yes, eigenvalue $\\lambda=3$.",
        "solution_he": "**צעד 1:** $A\\vec{v}=\\begin{pmatrix}3\\\\6\\end{pmatrix}=3\\vec{v}$.\n\n**צעד 2:** $A\\vec{v}=3\\vec{v}$ ו-$\\vec{v}\\neq\\vec{0}$, כן.\n\n**תשובה:** כן, $\\lambda=3$.",
    },
    "e3": {
        "solution_en": "**Step 1:** $p(\\lambda)=\\det\\begin{pmatrix}-\\lambda&1\\\\-2&3-\\lambda\\end{pmatrix}=-\\lambda(3-\\lambda)+2$.\n\n**Step 2:** $p(\\lambda)=\\lambda^2-3\\lambda+2=(\\lambda-1)(\\lambda-2)$.\n\n**Answer:** $\\lambda_1=1$, $\\lambda_2=2$.",
        "solution_he": "**צעד 1:** $p(\\lambda)=-\\lambda(3-\\lambda)+2$.\n\n**צעד 2:** $p(\\lambda)=(\\lambda-1)(\\lambda-2)$.\n\n**תשובה:** $\\lambda_1=1$, $\\lambda_2=2$.",
    },
    "e4": {
        "solution_en": "**Step 1:** Apply Theorem 4 with eigenvalues $2$ and $5$.\n\n**Step 2:** tr$(A)=2+5=7$, $\\det(A)=2\\cdot5=10$.\n\n**Answer:** tr$(A)=7$, $\\det(A)=10$.",
        "solution_he": "**צעד 1:** יישום משפט 4 עם ע\"ע $2$ ו-$5$.\n\n**צעד 2:** tr$(A)=7$, $\\det(A)=10$.\n\n**תשובה:** tr$(A)=7$, $\\det(A)=10$.",
    },
    "e5": {
        "solution_en": "**Step 1:** $p(\\lambda)=(\\lambda-2)(\\lambda-3)$, so $\\lambda_1=2$, $\\lambda_2=3$.\n\n**Step 2:** $E_2$: $(A-2I)\\vec{v}=0$ gives $v_1=v_2$, so $\\vec{v}=(1,1)^T$.\n\n**Step 3:** $E_3$: $(A-3I)\\vec{v}=0$ gives $v_1=2v_2$, so $\\vec{v}=(2,1)^T$.\n\n**Answer:** $\\lambda=2,3$; eigenvectors $(1,1)^T$, $(2,1)^T$.",
        "solution_he": "**צעד 1:** $p(\\lambda)=(\\lambda-2)(\\lambda-3)$, $\\lambda_1=2$, $\\lambda_2=3$.\n\n**צעד 2:** $E_2$: $v_1=v_2$, $\\vec{v}=(1,1)^T$.\n\n**צעד 3:** $E_3$: $v_1=2v_2$, $\\vec{v}=(2,1)^T$.\n\n**תשובה:** $\\lambda=2,3$; ו\"ע $(1,1)^T$, $(2,1)^T$.",
    },
    "e6": {
        "solution_en": "**Step 1:** Place eigenvalues on the diagonal.\n\n**Answer:** $A=\\begin{pmatrix}1&0&0\\\\0&-1&0\\\\0&0&2\\end{pmatrix}$ (or any similar diagonal matrix).",
        "solution_he": "**צעד 1:** שימו ע\"ע על האלכסון.\n\n**תשובה:** $A=\\begin{pmatrix}1&0&0\\\\0&-1&0\\\\0&0&2\\end{pmatrix}$.",
    },
    "e7": {
        "solution_en": "**Step 1:** $A$ is lower triangular.\n\n**Step 2:** Eigenvalues = diagonal entries.\n\n**Answer:** $\\lambda_1=1$, $\\lambda_2=3$, $\\lambda_3=-1$.",
        "solution_he": "**צעד 1:** $A$ משולשת תחתונה.\n\n**צעד 2:** ע\"ע = כניסות אלכסון.\n\n**תשובה:** $\\lambda_1=1$, $\\lambda_2=3$, $\\lambda_3=-1$.",
    },
    "e8": {
        "solution_en": "**Step 1:** $\\det(A)=4-4=0$, so $\\lambda=0$ is an eigenvalue.\n\n**Step 2:** $E_0=\\ker(A)$: $v_1=-2v_2$.\n\n**Answer:** $E_0=\\text{span}\\{(-2,1)^T\\}$.",
        "solution_he": "**צעד 1:** $\\det(A)=0$, $\\lambda=0$ ע\"ע.\n\n**צעד 2:** $E_0$: $v_1=-2v_2$.\n\n**תשובה:** $E_0=\\text{span}\\{(-2,1)^T\\}$.",
    },
    "e9": {
        "solution_en": "**Step 1:** $A^2\\vec{v}=A(A\\vec{v})=A(\\lambda\\vec{v})=\\lambda A\\vec{v}=\\lambda^2\\vec{v}$.\n\n**Step 2:** By induction on $k$: $A^k\\vec{v}=\\lambda^k\\vec{v}$.\n\n**Answer:** $\\vec{v}$ is an eigenvector of $A^2$ with eigenvalue $\\lambda^2$; generally $\\lambda^k$ for $A^k$. $\\blacksquare$",
        "solution_he": "**צעד 1:** $A^2\\vec{v}=A(\\lambda\\vec{v})=\\lambda^2\\vec{v}$.\n\n**צעד 2:** באינדוקציה: $A^k\\vec{v}=\\lambda^k\\vec{v}$.\n\n**תשובה:** $\\vec{v}$ ו\"ע של $A^2$ עם $\\lambda^2$; בכלל $\\lambda^k$ ל-$A^k$. $\\blacksquare$",
    },
    "e10": {
        "solution_en": "**Step 1:** Let $A\\vec{v}=\\lambda\\vec{v}$ with $\\vec{v}\\neq\\vec{0}$.\n\n**Step 2:** Multiply by $A^{-1}$: $\\vec{v}=\\lambda A^{-1}\\vec{v}$, so $A^{-1}\\vec{v}=(1/\\lambda)\\vec{v}$.\n\n**Answer:** $1/\\lambda$ is an eigenvalue of $A^{-1}$ ($\\lambda\\neq0$ since $A$ invertible). $\\blacksquare$",
        "solution_he": "**צעד 1:** $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$.\n\n**צעד 2:** כפל ב-$A^{-1}$: $A^{-1}\\vec{v}=(1/\\lambda)\\vec{v}$.\n\n**תשובה:** $1/\\lambda$ ע\"ע של $A^{-1}$ ($\\lambda\\neq0$). $\\blacksquare$",
    },
    "e11": {
        "solution_en": "**Step 1:** Let $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$.\n\n**Step 2:** $A^2\\vec{v}=A(\\lambda\\vec{v})=\\lambda^2\\vec{v}$. Also $A^2\\vec{v}=A\\vec{v}=\\lambda\\vec{v}$.\n\n**Step 3:** So $\\lambda^2\\vec{v}=\\lambda\\vec{v}$, hence $\\lambda(\\lambda-1)\\vec{v}=\\vec{0}$, giving $\\lambda=0$ or $\\lambda=1$.\n\n**Answer:** Only eigenvalues are $0$ and $1$. $\\blacksquare$",
        "solution_he": "**צעד 1:** $A\\vec{v}=\\lambda\\vec{v}$, $\\vec{v}\\neq\\vec{0}$.\n\n**צעד 2:** $A^2\\vec{v}=\\lambda^2\\vec{v}$ וגם $=\\lambda\\vec{v}$.\n\n**צעד 3:** $\\lambda(\\lambda-1)\\vec{v}=\\vec{0}$, $\\lambda=0$ או $\\lambda=1$.\n\n**תשובה:** ע\"ע יחידים: $0$ ו-$1$. $\\blacksquare$",
    },
    "e12": {
        "solution_en": "**Step 1:** $\\det(A^T-\\lambda I)=\\det((A-\\lambda I)^T)$.\n\n**Step 2:** Since $\\det(B^T)=\\det(B)$, this equals $\\det(A-\\lambda I)$.\n\n**Answer:** $A$ and $A^T$ share the same characteristic polynomial and eigenvalues. $\\blacksquare$",
        "solution_he": "**צעד 1:** $\\det(A^T-\\lambda I)=\\det((A-\\lambda I)^T)$.\n\n**צעד 2:** $\\det(B^T)=\\det(B)$, שווה ל-$\\det(A-\\lambda I)$.\n\n**תשובה:** ל-$A$ ו-$A^T$ אותו פולינום אופייני ואותם ע\"ע. $\\blacksquare$",
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
