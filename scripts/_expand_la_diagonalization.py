#!/usr/bin/env python3
"""Expand la_diagonalization.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/la_diagonalization.json"

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


def wc(text):
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def he_ratio(text):
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def he_weak(he, en):
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


def fmt(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he):
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


SECTION_BODIES = {}

SECTION_BODIES["intro"] = {
    "body_en_md": (
        "Working with a **diagonal matrix** is trivially easy: matrix multiplication, powers, "
        "exponentials $e^{tD}$, and even functions $f(D)$ are computed **entry by entry** on the "
        "diagonal. **Diagonalization** asks a powerful question: can we rewrite a complicated "
        "matrix $A$ in a simpler form $A = PDP^{-1}$, where $D$ is diagonal?\n\n"
        "If yes, then $A^n = PD^nP^{-1}$ — an $n$th power of an $n\\times n$ matrix reduces to "
        "$n$ scalar exponentiations. This is how population projection matrices, Markov transition "
        "matrices, and discrete dynamical systems are analyzed at scale.\n\n"
        "Applications extend far beyond powers: solving systems of linear ODEs $\\vec{x}'=A\\vec{x}$ "
        "via $e^{tA}=Pe^{tD}P^{-1}$, quantum observables in diagonal bases, and spectral graph "
        "theory (eigenvalues of adjacency/Laplacian matrices).\n\n"
        "**Prerequisites from this course:** diagonalization depends entirely on eigenvalues, "
        "eigenvectors, and the criterion $g_\\lambda=a_\\lambda$ from `concept:la_eigenvalues`. "
        "If you cannot find eigenvectors reliably, pause and review that lesson before continuing."
    ),
    "body_he_md": (
        "עבודה עם **מטריצה אלכסונית** פשוטה מאוד: כפל מטריצות, חזקות, אקספוננציאל $e^{tD}$ "
        "ופונקציות $f(D)$ מחושבים **כניסה-כניסה** על האלכסון. **אלכסון** שואל שאלה חזקה: "
        "האם אפשר לכתוב מטריצה מורכבת $A$ בצורה $A=PDP^{-1}$, כאשר $D$ אלכסונית?\n\n"
        "אם כן, אז $A^n=PD^nP^{-1}$ — חזקה $n$-ית של מטריצה $n\\times n$ מתמצת ל-$n$ "
        "חזקות סקלריות. כך מנתחים מטריצות הקרנה של אוכלוסיות, מטריצות מעבר של שרשראות "
        "מרקוב ומערכות דינמיות בדידות.\n\n"
        "היישומים חורגים מחזקות: פתרון מערכות ODE לינאריות $\\vec{x}'=A\\vec{x}$ דרך "
        "$e^{tA}=Pe^{tD}P^{-1}$, תצפיות קוונטיות בבסיסים אלכסוניים, ותורת גרפים ספקטרלית "
        "(ע\"ע של מטריצות שכנות/לaplacian).\n\n"
        "**דרישות קדם:** אלכסון תלוי לחלוטין בע\"ע, בו\"ע ובקריטריון $g_\\lambda=a_\\lambda$ "
        "מ-`concept:la_eigenvalues`. אם מציאת ו\"ע אינה יציבה — חזרו לשיעור ההוא לפני שממשיכים."
    ),
}

SECTION_BODIES["definition"] = {
    "body_en_md": (
        "**Definition.** An $n\\times n$ matrix $A$ is **diagonalizable** if there exist an "
        "invertible matrix $P$ and a diagonal matrix $D$ such that\n"
        "$$A = PDP^{-1}, \\qquad \\text{equivalently}\\qquad AP = PD.$$\n\n"
        "**Structure of $P$ and $D$:** The columns of $P$ are eigenvectors of $A$; the diagonal "
        "entries of $D$ are the corresponding eigenvalues (same column order):\n"
        "$$P = [\\vec{v}_1 \\;\\cdots\\; \\vec{v}_n], \\qquad "
        "D = \\mathrm{diag}(\\lambda_1,\\ldots,\\lambda_n).$$\n\n"
        "**Diagonalizability criterion (central theorem):** $A$ is diagonalizable iff it has "
        "$n$ linearly independent eigenvectors iff $g_\\lambda = a_\\lambda$ for **every** "
        "eigenvalue $\\lambda$ (geometric multiplicity equals algebraic multiplicity).\n\n"
        "**Sufficient condition:** If $A$ has $n$ **distinct** eigenvalues, it is automatically "
        "diagonalizable (Theorem 5 from eigenvalues — independent eigenvectors for distinct "
        "eigenvalues).\n\n"
        "**Power formula:** If $A = PDP^{-1}$, then for every positive integer $k$,\n"
        "$$A^k = PD^kP^{-1}, \\qquad D^k = \\mathrm{diag}(\\lambda_1^k,\\ldots,\\lambda_n^k).$$\n"
        "Similarly $A^{-1}=PD^{-1}P^{-1}$ when all $\\lambda_i\\neq 0$.\n\n"
        "**Similarity invariance:** If $A=PDP^{-1}$, then $A$ and $D$ share the same "
        "characteristic polynomial, trace, and determinant — diagonalization reveals these "
        "invariants on the diagonal of $D$."
    ),
    "body_he_md": (
        "**הגדרה.** מטריצה $n\\times n$ $A$ **ניתנת לאלכסון** אם קיימות $P$ הפיכה ו-$D$ "
        "אלכסונית כך ש-\n"
        "$$A = PDP^{-1}, \\qquad \\text{שקול ל}\\qquad AP = PD.$$\n\n"
        "**מבנה $P$ ו-$D$:** עמודות $P$ הן ו\"ע של $A$; כניסות האלכסון של $D$ הן הע\"ע "
        "המתאימים (באותו סדר עמודות):\n"
        "$$P = [\\vec{v}_1 \\;\\cdots\\; \\vec{v}_n], \\qquad "
        "D = \\mathrm{diag}(\\lambda_1,\\ldots,\\lambda_n).$$\n\n"
        "**קריטריון אלכסוניות (משפט מרכזי):** $A$ ניתנת לאלכסון אם ורק אם יש לה $n$ ו\"ע "
        "בלתי-תלויים אם ורק אם $g_\\lambda = a_\\lambda$ ל**כל** $\\lambda$ (ריבוי גיאומטרי "
        "שווה לריבוי אלגברי).\n\n"
        "**תנאי מספיק:** $n$ ע\"ע **שונים** $\\Rightarrow$ ניתנת לאלכסון (משפט 5 משיעור "
        "הע\"ע — בלתי-תלות של ו\"ע לערכים שונים).\n\n"
        "**נוסחת חזקה:** אם $A=PDP^{-1}$, אז לכל $k\\in\\mathbb{N}$,\n"
        "$$A^k = PD^kP^{-1}, \\qquad D^k = \\mathrm{diag}(\\lambda_1^k,\\ldots,\\lambda_n^k).$$\n"
        "בדומה $A^{-1}=PD^{-1}P^{-1}$ כשכל $\\lambda_i\\neq 0$.\n\n"
        "**אינווריאנטיות דמיון:** אם $A=PDP^{-1}$, אז ל-$A$ ול-$D$ אותו פולינום אופייני, "
        "עקבה ודטרמיננטה — אלכסון חושף את האינווריאנטים האלה על האלכסון של $D$."
    ),
}

SECTION_BODIES["theory"] = {
    "body_en_md": (
        "**Theorem 1 (Eigenvector basis criterion).** $A$ is diagonalizable iff it has "
        "$n$ linearly independent eigenvectors.\n\n"
        "*Proof sketch:* $AP=PD$ expands column-by-column as $A\\vec{v}_j=\\lambda_j\\vec{v}_j$. "
        "Thus columns of $P$ are eigenvectors. $P$ is invertible iff its columns are independent. "
        "$\\blacksquare$\n\n"
        "**Theorem 2 (Spectral Theorem — symmetric matrices).** If $A^T=A$ (real symmetric), then:\n"
        "- All eigenvalues are real.\n"
        "- Eigenvectors for distinct eigenvalues are orthogonal.\n"
        "- $A$ is diagonalizable over $\\mathbb{R}$ with an **orthogonal** matrix $P$ "
        "($A=PDP^T$, $P^T=P^{-1}$).\n\n"
        "**Theorem 3 (Non-diagonalizable $2\\times2$ over $\\mathbb{R}$).** A real $2\\times2$ "
        "matrix $A$ is **not** diagonalizable over $\\mathbb{R}$ iff one of:\n"
        "- **(Type 1 — defective)** repeated real eigenvalue $\\lambda$ with $g_\\lambda=1<a_\\lambda=2$;\n"
        "- **(Type 2 — no real eigenvalues)** $p(\\lambda)$ has negative discriminant (complex roots).\n\n"
        "**Examples:** Type 1: $A=\\begin{pmatrix}\\lambda&1\\\\0&\\lambda\\end{pmatrix}$ (Jordan block). "
        "Type 2: $A=\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix}$ (rotation by $90°$, "
        "$p(\\lambda)=\\lambda^2+1$).\n\n"
        "**Remark:** A matrix may be diagonalizable over $\\mathbb{C}$ but not over $\\mathbb{R}$ "
        "(Type 2). Always specify the field."
    ),
    "body_he_md": (
        "**משפט 1 (קריטריון בסיס ו\"ע).** $A$ ניתנת לאלכסון אם ורק אם יש לה $n$ ו\"ע "
        "בלתי-תלויים.\n\n"
        "*סקיצת הוכחה:* $AP=PD$ מתפרק עמודה-עמודה: $A\\vec{v}_j=\\lambda_j\\vec{v}_j$. "
        "עמודות $P$ הן ו\"ע. $P$ הפיכה אם ורק אם העמודות בלתי-תלויות. $\\blacksquare$\n\n"
        "**משפט 2 (ספקטרלי — סימטריה).** אם $A^T=A$ (סימטרית ממשית):\n"
        "- כל ע\"ע ממשיים.\n"
        "- ו\"ע לערכים שונים אורתוגונלים.\n"
        "- $A$ ניתנת לאלכסון מעל $\\mathbb{R}$ עם $P$ **אורתוגונלית** ($A=PDP^T$).\n\n"
        "**משפט 3 (אי-אלכסוניות $2\\times2$ מעל $\\mathbb{R}$).** מטריצה $2\\times2$ ממשית "
        "**אינה** ניתנת לאלכסון מעל $\\mathbb{R}$ אם ורק אם:\n"
        "- **(סוג 1 — פגומה)** ע\"ע ממשי חוזר $\\lambda$ עם $g_\\lambda=1<a_\\lambda=2$;\n"
        "- **(סוג 2 — אין ע\"ע ממשיים)** ל-$p(\\lambda)$ דיסקרימיננטה שלילית (שורשים מרוכבים).\n\n"
        "**דוגמאות:** סוג 1: $A=\\begin{pmatrix}\\lambda&1\\\\0&\\lambda\\end{pmatrix}$ (גוש "
        "ירדן). סוג 2: $A=\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix}$ (סיבוב $90°$, "
        "$p(\\lambda)=\\lambda^2+1$).\n\n"
        "**הערה:** מטריצה יכולה להיות ניתנת לאלכסון מעל $\\mathbb{C}$ אך לא מעל $\\mathbb{R}$ "
        "(סוג 2). תמיד ציינו את השדה."
    ),
}

SECTION_BODIES["worked_example_1"] = {
    "body_en_md": (
        "**Diagonalize** $A = \\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}$ and compute $A^{2024}$.\n\n"
        "This is the baseline case: $A$ is **already diagonal**, so diagonalization is trivial but "
        "still requires naming $P$, $D$, and verifying the eigenstructure.\n\n"
        "### Move 1 — Recognize diagonal form\n"
        "$A$ is diagonal, so eigenvalues are diagonal entries: $\\lambda_1=1$, $\\lambda_2=-1$.\n\n"
        "### Move 2 — Standard eigenvectors\n"
        "$E_1=\\text{span}\\{(1,0)^T\\}$, $E_2=\\text{span}\\{(0,1)^T\\}$ — coordinate directions.\n\n"
        "### Move 3 — Write $A=PDP^{-1}$\n"
        "$$P = I = \\begin{pmatrix}1&0\\\\0&1\\end{pmatrix}, \\quad "
        "D = A = \\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}.$$\n\n"
        "### Move 4 — Power via $D^{2024}$\n"
        "$$A^{2024} = PD^{2024}P^{-1} = \\begin{pmatrix}1^{2024}&0\\\\0&(-1)^{2024}\\end{pmatrix}"
        " = \\begin{pmatrix}1&0\\\\0&1\\end{pmatrix} = I.$$\n\n"
        "**Answer:** $P=I$, $D=A$; $A^{2024}=I$ because $(-1)^{2024}=1$.\n\n"
        "**Takeaway:** Even when $A$ is diagonal, writing $P$ and $D$ explicitly trains the "
        "pattern for non-diagonal matrices.\n\n"
        "**Check:** Verify $(-1)^{2024}=1$ using even exponent — a common sign trap when "
        "eigenvalues are negative.\n\n"
        "**Connection:** This matrix represents reflection across the $x$-axis combined with "
        "identity on the $y$-axis — two independent eigen-directions."
    ),
    "body_he_md": (
        "**אלכסן** $A = \\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}$ וחשב $A^{2024}$.\n\n"
        "זה מקרה הבסיס: $A$ **כבר אלכסונית**, ולכן האלכסון טריוויאלי — אך עדיין צריך לתת "
        "שמות ל-$P$, $D$ ולאמת את מבנה הע\"ע.\n\n"
        "### צעד 1 — זיהוי צורה אלכסונית\n"
        "ע\"ע = כניסות אלכסון: $\\lambda_1=1$, $\\lambda_2=-1$.\n\n"
        "### צעד 2 — ו\"ע סטנדרטיים\n"
        "$E_1=\\text{span}\\{(1,0)^T\\}$, $E_2=\\text{span}\\{(0,1)^T\\}$ — כיווני ציר.\n\n"
        "### צעד 3 — כתיבת $A=PDP^{-1}$\n"
        "$$P=I, \\quad D=A=\\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}.$$\n\n"
        "### צעד 4 — חזקה דרך $D^{2024}$\n"
        "$$A^{2024}=PD^{2024}P^{-1}=\\begin{pmatrix}1&0\\\\0&(-1)^{2024}\\end{pmatrix}"
        "=\\begin{pmatrix}1&0\\\\0&1\\end{pmatrix}=I.$$\n\n"
        "**תשובה:** $P=I$, $D=A$; $A^{2024}=I$ כי $(-1)^{2024}=1$.\n\n"
        "**מסקנה:** גם כש-$A$ אלכסונית, כתיבה מפורשת של $P$ ו-$D$ מאמנת את הדפוס "
        "למטריצות שאינן אלכסוניות.\n\n"
        "**בדיקה:** אמתו $(-1)^{2024}=1$ — מלכודת סימן נפוצה כשע\"ע שליליים.\n\n"
        "**קשר:** המטריצה מייצגת שיקוף סביב ציר $x$ עם זהות על ציר $y$ — "
        "שני כיווני ע\"ע עצמאיים."
    ),
}

SECTION_BODIES["worked_example_2"] = {
    "body_en_md": (
        "**Diagonalize** $A = \\begin{pmatrix}4&1\\\\2&3\\end{pmatrix}$ and compute $A^5$.\n\n"
        "### Move 1 — Characteristic polynomial\n"
        "$$p(\\lambda)=(4-\\lambda)(3-\\lambda)-2=\\lambda^2-7\\lambda+10=(\\lambda-2)(\\lambda-5).$$\n"
        "Eigenvalues: $\\lambda_1=2$, $\\lambda_2=5$ (distinct $\\Rightarrow$ diagonalizable).\n\n"
        "### Move 2 — Eigenspaces\n"
        "$E_2$: $(A-2I)\\vec{v}=0$ gives $\\vec{v}_1=(-1,2)^T$. "
        "$E_5$: $(A-5I)\\vec{v}=0$ gives $\\vec{v}_2=(1,1)^T$.\n\n"
        "### Move 3 — Form $P$ and $D$\n"
        "$$P = \\begin{pmatrix}-1&1\\\\2&1\\end{pmatrix}, \\quad "
        "D = \\begin{pmatrix}2&0\\\\0&5\\end{pmatrix}.$$\n\n"
        "### Move 4 — Compute $P^{-1}$\n"
        "$\\det P = -1-2=-3$. "
        "$$P^{-1}=\\frac{1}{3}\\begin{pmatrix}-1&1\\\\2&1\\end{pmatrix}.$$\n\n"
        "### Move 5 — Power formula\n"
        "$$D^5=\\begin{pmatrix}32&0\\\\0&3125\\end{pmatrix}.$$\n"
        "Compute $PD^5$ first, then multiply by $P^{-1}$:\n"
        "$$PD^5=\\begin{pmatrix}-32&3125\\\\64&3125\\end{pmatrix}, \\quad "
        "A^5=\\frac{1}{3}\\begin{pmatrix}2094&1031\\\\2062&1063\\end{pmatrix}.$$\n\n"
        "**Sanity check:** tr$(A^5)=2^5+5^5=32+3125=3157$; trace of answer $=2094+1063=3157$ ✓.\n\n"
        "**Alternative:** Expand $A^5$ as $\\lambda_1^5\\vec{v}_1(P^{-1})_{1,:}+\\lambda_2^5\\vec{v}_2(P^{-1})_{2,:}$ "
        "to avoid a full $3\\times3$ multiply — useful for larger powers.\n\n"
        "**Pattern:** Distinct eigenvalues guaranteed diagonalizability — always verify $AP=PD$ "
        "before computing $A^k$ to catch eigenvector ordering errors early.\n\n"
        "**Exam note:** Israeli finals often ask for $A^{100}$ from a $2\\times2$ matrix — "
        "the diagonalization method scales cleanly while direct multiplication does not."
    ),
    "body_he_md": (
        "**אלכסן** $A = \\begin{pmatrix}4&1\\\\2&3\\end{pmatrix}$ וחשב $A^5$.\n\n"
        "### צעד 1 — פולינום אופייני\n"
        "$$p(\\lambda)=(\\lambda-2)(\\lambda-5). \\quad \\lambda_1=2,\\;\\lambda_2=5 "
        "(שונים $\\Rightarrow$ ניתנת לאלכסון).$$\n\n"
        "### צעד 2 — מרחבים עצמיים\n"
        "$E_2$: $(A-2I)\\vec{v}=0$ $\\Rightarrow$ $\\vec{v}_1=(-1,2)^T$. "
        "$E_5$: $(A-5I)\\vec{v}=0$ $\\Rightarrow$ $\\vec{v}_2=(1,1)^T$.\n\n"
        "### צעד 3 — $P$ ו-$D$\n"
        "$$P=\\begin{pmatrix}-1&1\\\\2&1\\end{pmatrix}, \\quad D=\\begin{pmatrix}2&0\\\\0&5\\end{pmatrix}.$$\n\n"
        "### צעד 4 — $P^{-1}$\n"
        "$\\det P=-3$, "
        "$$P^{-1}=\\frac{1}{3}\\begin{pmatrix}-1&1\\\\2&1\\end{pmatrix}.$$\n\n"
        "### צעד 5 — נוסחת חזקה\n"
        "$$D^5=\\begin{pmatrix}32&0\\\\0&3125\\end{pmatrix}.$$\n"
        "חשבו $PD^5$ ואז כפלו ב-$P^{-1}$:\n"
        "$$PD^5=\\begin{pmatrix}-32&3125\\\\64&3125\\end{pmatrix}, \\quad "
        "A^5=\\frac{1}{3}\\begin{pmatrix}2094&1031\\\\2062&1063\\end{pmatrix}.$$\n\n"
        "**בדיקה:** tr$(A^5)=2^5+5^5=3157$; עקבה של התשובה $=2094+1063=3157$ ✓.\n\n"
        "**חלופה:** פתחו $A^5$ כ-$\\lambda_1^5\\vec{v}_1(P^{-1})_{1,:}+\\lambda_2^5\\vec{v}_2(P^{-1})_{2,:}$ "
        "כדי להימנע מכפל $3\\times3$ מלא — שימושי לחזקות גדולות.\n\n"
        "**דפוס:** ע\"ע שונים מבטיחים אלכסוניות — אמתו $AP=PD$ לפני $A^k$ "
        "לתפיסת טעויות סדר ו\"ע מוקדם.\n\n"
        "**הערת בחינה:** בגמרים שואלים לעיתים $A^{100}$ מ-$2\\times2$ — "
        "אלכסון מתקדם בקלות; כפל ישיר לא — השתמשו ב-$D^n$."
    ),
}

SECTION_BODIES["worked_example_3"] = {
    "body_en_md": (
        "**Claim:** A real $2\\times2$ matrix $A$ is **not** diagonalizable over $\\mathbb{R}$ "
        "iff Type 1 (defective repeated eigenvalue) or Type 2 (no real eigenvalues).\n\n"
        "**Proof — necessity:** $p(\\lambda)$ has degree 2.\n"
        "*Case A:* two distinct real eigenvalues $\\Rightarrow$ two independent eigenvectors "
        "$\\Rightarrow$ diagonalizable — contradiction.\n"
        "*Case B:* one repeated real $\\lambda$, $a_\\lambda=2$. If $g_\\lambda=2$ then "
        "$A=\\lambda I$ (diagonal) — contradiction. So $g_\\lambda=1$ (Type 1).\n"
        "*Case C:* no real roots (Type 2).\n\n"
        "**Proof — sufficiency:**\n"
        "Type 1: at most one independent eigenvector for $\\lambda$, so fewer than 2 total "
        "independent eigenvectors in $\\mathbb{R}^2$.\n"
        "Type 2: no real eigenvectors at all.\n\n"
        "**Examples:** Type 1: $\\begin{pmatrix}2&1\\\\0&2\\end{pmatrix}$. "
        "Type 2: $\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix}$ with $p(\\lambda)=\\lambda^2+1$. "
        "$\\blacksquare$\n\n"
        "**Exam use:** For any $2\\times2$ \"is it diagonalizable?\" question, compute "
        "$p(\\lambda)$ first — the discriminant and root multiplicities decide in under a minute.\n\n"
        "**Jordan preview:** When Type 1 occurs, the missing eigenvector direction is filled by "
        "a **generalized eigenvector** — the topic of Jordan normal form in advanced courses.\n\n"
        "**Memorize:** The two-type classification applies **only** over $\\mathbb{R}$ for "
        "$2\\times2$ matrices; always state the field in your answer.\n\n"
        "**Quick test:** Compute $p(\\lambda)$, list roots with multiplicities, then find "
        "$\\dim\\ker(A-\\lambda I)$ for each repeated root — if any $g<a$, answer \"no.\"\n\n"
        "**Decision flowchart:** (1) real distinct roots $\\Rightarrow$ yes; (2) repeated real root "
        "$\\Rightarrow$ check $g=a$; (3) complex roots $\\Rightarrow$ no over $\\mathbb{R}$."
    ),
    "body_he_md": (
        "**טענה:** מטריצה $2\\times2$ ממשית **אינה** ניתנת לאלכסון מעל $\\mathbb{R}$ אם ורק "
        "אם סוג 1 (ע\"ע חוזר פגום) או סוג 2 (אין ע\"ע ממשיים).\n\n"
        "**הוכחה — הכרחיות:** $p(\\lambda)$ ממעלה 2.\n"
        "*מקרה א':* שני ע\"ע ממשיים שונים $\\Rightarrow$ שני ו\"ע בלתי-תלויים $\\Rightarrow$ "
        "ניתנת לאלכסון — סתירה.\n"
        "*מקרה ב':* ע\"ע ממשי חוזר $\\lambda$, $a_\\lambda=2$. אם $g_\\lambda=2$ אז "
        "$A=\\lambda I$ — סתירה. לכן $g_\\lambda=1$ (סוג 1).\n"
        "*מקרה ג':* אין שורשים ממשיים (סוג 2).\n\n"
        "**הוכחה — מספיקות:**\n"
        "סוג 1: לכל היותר ו\"ע אחד בלתי-תלוי ל-$\\lambda$ — פחות מ-2 בסך הכל ב-$\\mathbb{R}^2$.\n"
        "סוג 2: אין ו\"ע ממשיים כלל — לא ניתן לבנות $P$ עם עמודות ממשיות.\n\n"
        "**דוגמאות:** סוג 1: $\\begin{pmatrix}2&1\\\\0&2\\end{pmatrix}$. "
        "סוג 2: $\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix}$, $p(\\lambda)=\\lambda^2+1$. "
        "$\\blacksquare$\n\n"
        "**שימוש בבחינה:** חשבו $p(\\lambda)$ תחילה; הדיסקרימיננטה וריבוי השורשים מכריעים.\n\n"
        "**ציפייה לירדן:** בסוג 1, הכיוון החסר מתמלא ב**ו\"ע מוכלל**.\n\n"
        "**לשינון:** הסיווג לשני סוגים חל **רק** מעל $\\mathbb{R}$ — ציינו את השדה.\n\n"
        "**בדיקה מהירה:** רשמו שורשים עם ריבויים, מצאו $\\dim\\ker(A-\\lambda I)$ "
        "לכל שורש חוזר — אם $g<a$, התשובה \"לא\".\n\n"
        "**תרשים החלטה:** (1) שורשים ממשיים שונים $\\Rightarrow$ כן; (2) שורש חוזר "
        "$\\Rightarrow$ בדקו $g=a$; (3) שורשים מרוכבים $\\Rightarrow$ לא מעל $\\mathbb{R}$."
    ),
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "**Step 1 — Diagonalizability:** $A=\\begin{pmatrix}2&0\\\\0&5\\end{pmatrix}$ is "
            "already diagonal with distinct eigenvalues $2$ and $5$, so it is diagonalizable.\n\n"
            "**Step 2 — Write $A=PDP^{-1}$:** Take $P=I$ and $D=A$ (eigenvectors are "
            "$\\vec{e}_1,\\vec{e}_2$).\n\n"
            "**Step 3 — Compute $A^3$:** $A^3=D^3=\\begin{pmatrix}2^3&0\\\\0&5^3\\end{pmatrix}"
            "=\\begin{pmatrix}8&0\\\\0&125\\end{pmatrix}$.\n\n"
            "**Answer:** Yes, diagonalizable; $P=I$, $D=A$; $A^3=\\begin{pmatrix}8&0\\\\0&125\\end{pmatrix}$."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — אלכסוניות:** $A=\\begin{pmatrix}2&0\\\\0&5\\end{pmatrix}$ כבר אלכסונית "
            "עם ע\"ע שונים $2$ ו-$5$ — ניתנת לאלכסון.\n\n"
            "**שלב 2 — $A=PDP^{-1}$:** $P=I$, $D=A$ (ו\"ע: $\\vec{e}_1,\\vec{e}_2$).\n\n"
            "**שלב 3 — $A^3$:** $A^3=D^3=\\begin{pmatrix}8&0\\\\0&125\\end{pmatrix}$.\n\n"
            "**תשובה:** כן; $P=I$, $D=A$; $A^3=\\begin{pmatrix}8&0\\\\0&125\\end{pmatrix}$."
        ),
    },
    {
        "checkpoint_solution_en": (
            "**Step 1 — Characteristic polynomial:** "
            "$p(\\lambda)=(3-\\lambda)^2$, so $\\lambda=3$ is the only eigenvalue with "
            "$a_\\lambda=2$.\n\n"
            "**Step 2 — Geometric multiplicity:** "
            "$(A-3I)=\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix}$ has rank 1, so "
            "$g_\\lambda=\\dim\\ker=1<2=a_\\lambda$.\n\n"
            "**Step 3 — Conclusion:** Since $g<a$ for $\\lambda=3$, $A$ has only one "
            "independent eigenvector in $\\mathbb{R}^2$. **Not diagonalizable** (Type 1 defective "
            "Jordan block).\n\n"
            "**Answer:** No — repeated eigenvalue with insufficient eigenvectors."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — פולינום אופייני:** $p(\\lambda)=(3-\\lambda)^2$, ע\"ע יחיד $\\lambda=3$ "
            "עם $a_\\lambda=2$.\n\n"
            "**שלב 2 — ריבוי גיאומטרי:** $(A-3I)=\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix}$ "
            "בדרגה 1, לכן $g_\\lambda=1<2$.\n\n"
            "**שלב 3 — מסקנה:** $g<a$ $\\Rightarrow$ רק ו\"ע אחד בלתי-תלוי ב-$\\mathbb{R}^2$. "
            "**אינה ניתנת לאלכסון** (סוג 1 — גוש ירדן פגום).\n\n"
            "**תשובה:** לא — ע\"ע חוזר ללא מספיק ו\"ע."
        ),
    },
]

SECTION_BODIES["method_guide"] = {
    "body_en_md": (
        "**Step 1:** Compute $p(\\lambda)=\\det(A-\\lambda I)$ and find all eigenvalues "
        "$\\lambda_1,\\ldots,\\lambda_k$.\n\n"
        "**Step 2:** For each $\\lambda_i$, row-reduce $A-\\lambda_i I$ and record "
        "$g_{\\lambda_i}=\\dim E_{\\lambda_i}$ and $a_{\\lambda_i}$ from $p$.\n\n"
        "**Step 3 — Diagonalizability gate:** If **every** $g_{\\lambda_i}=a_{\\lambda_i}$, "
        "continue. Otherwise STOP — $A$ is not diagonalizable (use Jordan form instead).\n\n"
        "**Step 4:** Form $P=[\\vec{v}_1\\;\\cdots\\;\\vec{v}_n]$ with eigenvectors as columns "
        "(order must match $D$).\n\n"
        "**Step 5:** Form $D=\\mathrm{diag}(\\lambda_1,\\ldots,\\lambda_n)$.\n\n"
        "**Step 6 — Verify:** Check $AP=PD$ or $A=PDP^{-1}$ before computing powers.\n\n"
        "**Step 7 — Powers:** $A^k=PD^kP^{-1}$ with $D^k=\\mathrm{diag}(\\lambda_1^k,\\ldots)$.\n\n"
        "| Shortcut | When |\n|---|---|\n"
        "| $n$ distinct eigenvalues | Automatically diagonalizable |\n"
        "| $A$ symmetric | Always diagonalizable; optional Gram–Schmidt for orthogonal $P$ |\n"
        "| $A$ triangular | Eigenvalues on diagonal; check $g=a$ only for repeated entries |"
    ),
    "body_he_md": (
        "**שלב 1:** חשבו $p(\\lambda)=\\det(A-\\lambda I)$ ומצאו את כל הע\"ע "
        "$\\lambda_1,\\ldots,\\lambda_k$.\n\n"
        "**שלב 2:** לכל $\\lambda_i$, דרגו $A-\\lambda_i I$ ורשמו "
        "$g_{\\lambda_i}=\\dim E_{\\lambda_i}$ ו-$a_{\\lambda_i}$ מ-$p$.\n\n"
        "**שלב 3 — שער אלכסוניות:** אם **לכל** $i$ מתקיים $g_{\\lambda_i}=a_{\\lambda_i}$ — "
        "המשיכו. אחרת עצרו — $A$ **אינה** ניתנת לאלכסון (עברו לצורת ירדן).\n\n"
        "**שלב 4:** $P=[\\vec{v}_1\\;\\cdots\\;\\vec{v}_n]$ — ו\"ע כעמודות (סדר תואם ל-$D$).\n\n"
        "**שלב 5:** $D=\\mathrm{diag}(\\lambda_1,\\ldots,\\lambda_n)$.\n\n"
        "**שלב 6 — אימות:** בדקו $AP=PD$ או $A=PDP^{-1}$ לפני חישוב חזקות.\n\n"
        "**שלב 7 — חזקות:** $A^k=PD^kP^{-1}$, $D^k=\\mathrm{diag}(\\lambda_1^k,\\ldots)$.\n\n"
        "| קיצור | מתי |\n|---|---|\n"
        "| $n$ ע\"ע שונים | אלכסוניות אוטומטית |\n"
        "| $A$ סימטרית | תמיד ניתנת; אופציונלי Gram–Schmidt ל-$P$ אורתוגונלית |\n"
        "| $A$ משולשת | ע\"ע על האלכסון; בדקו $g=a$ רק לכניסות חוזרות |"
    ),
}

SECTION_BODIES["pitfall"] = {
    "body_en_md": (
        "1. **Skipping the $g=a$ check.** Distinct eigenvalues guarantee diagonalizability, "
        "but repeated eigenvalues require verifying $g_\\lambda=a_\\lambda$ for each one.\n\n"
        "2. **Column–diagonal mismatch.** The $j$th column of $P$ must be an eigenvector for "
        "the $j$th diagonal entry of $D$. Swapping order without swapping both breaks $AP=PD$.\n\n"
        "3. **Non-invertible $P$.** If chosen eigenvectors are dependent, $P$ is singular — "
        "this happens exactly when some $g_\\lambda<a_\\lambda$.\n\n"
        "4. **Wrong product order.** $A=PDP^{-1}$, not $P^{-1}DP$. Matrix multiplication is "
        "not commutative.\n\n"
        "5. **Forgetting $\\det(P)$ when inverting.** For $2\\times2$, use the adjugate formula "
        "and divide by $\\det P$ — sign errors here propagate through every power computation.\n\n"
        "6. **Claiming non-diagonalizability over $\\mathbb{C}$ from Type 2 over $\\mathbb{R}$.** "
        "Rotation matrices are not diagonalizable over $\\mathbb{R}$ but are over $\\mathbb{C}$."
    ),
    "body_he_md": (
        "1. **דילוג על בדיקת $g=a$.** ע\"ע שונים מבטיחים אלכסוניות, אך ע\"ע חוזרים דורשים "
        "אימות $g_\\lambda=a_\\lambda$ לכל $\\lambda$.\n\n"
        "2. **אי-התאמה עמודה–אלכסון.** העמודה ה-$j$-ית של $P$ חייבת להיות ו\"ע לכניסה "
        "ה-$j$-ית של $D$. החלפת סדר בלי לשנות את שניהם שוברת $AP=PD$.\n\n"
        "3. **$P$ לא הפיכה.** אם הו\"ע שנבחרו תלויים — $P$ סינגולרית; זה קורה בדיוק כש-$g<a$.\n\n"
        "4. **סדר כפל שגוי.** $A=PDP^{-1}$, לא $P^{-1}DP$. כפל מטריצות לא קומוטטיבי.\n\n"
        "5. **שכחת $\\det(P)$ בהיפוך.** ב-$2\\times2$ השתמשו בנוסחת השלמה וחלקו ב-$\\det P$ — "
        "טעויות סימן מסתננות לכל חישוב חזקה.\n\n"
        "6. **טענה על אי-אלכסוניות מעל $\\mathbb{C}$ מסוג 2 מעל $\\mathbb{R}$.** מטריצות "
        "סיבוב אינן ניתנות לאלכסון מעל $\\mathbb{R}$ אך כן מעל $\\mathbb{C}$."
    ),
}

SECTION_BODIES["why_matters"] = {
    "body_en_md": (
        "Diagonalization is the computational heart of linear algebra beyond $\\mathbb{R}^2$.\n\n"
        "**Links in the knowledge graph:**\n"
        "- `concept:la_eigenvalues` — supplies eigenvalues, eigenspaces, and $g$ vs $a$.\n"
        "- `concept:la_diagonalization` feeds into ODE systems, matrix functions, and PCA.\n"
        "- Symmetric diagonalization connects to `concept:la_orthogonality` (orthogonal eigenbases).\n\n"
        "**Why exams care:** Israeli university linear algebra finals routinely ask you to "
        "(i) decide diagonalizability, (ii) construct $P$ and $D$, (iii) compute $A^n$, and "
        "(iv) prove power formulas. These skills also appear in discrete dynamical systems "
        "and numerical linear algebra courses.\n\n"
        "Mastering the $g=a$ gate prevents wasted time trying to invert a dependent eigenvector "
        "matrix — a mistake that costs 10+ minutes on a timed exam."
    ),
    "body_he_md": (
        "אלכסון הוא לב החישובי של אלגברה לינארית מעבר ל-$\\mathbb{R}^2$.\n\n"
        "**קשרים בגרף הידע:**\n"
        "- `concept:la_eigenvalues` — מספק ע\"ע, מרחבים עצמיים ו-$g$ מול $a$.\n"
        "- `concept:la_diagonalization` מזין מערכות ODE, פונקציות מטריצה ו-PCA.\n"
        "- אלכסון סימטרי קשור ל-`concept:la_orthogonality` (בסיסי ו\"ע אורתוגונליים).\n\n"
        "**למה בחינות דורשות זאת:** בגמרי אלגברה לינארית באוניברסיטה שואלים לעיתים קרובות "
        "(א) האם ניתנת לאלכסון, (ב) בניית $P$ ו-$D$, (ג) חישוב $A^n$, (ד) הוכחת נוסחת חזקה. "
        "המיומנויות מופיעות גם במערכות דינמיות בדידות ואלגברה נומרית.\n\n"
        "שליטה בשער $g=a$ מונעת בזבוז זמן על היפוך מטריצת ו\"ע תלויים — טעות שעולה "
        "10+ דקות בבחינה בזמן."
    ),
}

SECTION_BODIES["before_exam"] = {
    "body_en_md": (
        "**Formula sheet essentials:**\n"
        "- $A=PDP^{-1}$: columns of $P$ = eigenvectors; diagonal of $D$ = eigenvalues (matched order)\n"
        "- $A^n=PD^nP^{-1}$, $A^{-1}=PD^{-1}P^{-1}$ (when invertible)\n"
        "- Diagonalizable iff $g_\\lambda=a_\\lambda$ for all $\\lambda$\n"
        "- $n$ distinct eigenvalues $\\Rightarrow$ diagonalizable (sufficient, not necessary)\n"
        "- Symmetric $\\Rightarrow$ always diagonalizable over $\\mathbb{R}$\n\n"
        "**Typical exam tasks:** full diagonalization of $2\\times2$ or $3\\times3$; compute "
        "$A^{100}$; prove $A^n=PD^nP^{-1}$ by induction; classify non-diagonalizable matrices.\n\n"
        "**Strategy:** Always compute $p(\\lambda)$ and all $g_\\lambda$ before building $P$. "
        "For powers, compute $D^n$ first (trivial), then one multiply $PD^nP^{-1}$."
    ),
    "body_he_md": (
        "**גיליון נוסחאות:**\n"
        "- $A=PDP^{-1}$: עמודות $P$ = ו\"ע; אלכסון $D$ = ע\"ע (סדר תואם)\n"
        "- $A^n=PD^nP^{-1}$, $A^{-1}=PD^{-1}P^{-1}$ (כשהמטריצה הפיכה)\n"
        "- ניתנת לאלכסון אם ורק אם $g_\\lambda=a_\\lambda$ לכל $\\lambda$\n"
        "- $n$ ע\"ע שונים $\\Rightarrow$ ניתנת (מספיק, לא הכרחי)\n"
        "- סימטרית $\\Rightarrow$ תמיד ניתנת מעל $\\mathbb{R}$\n\n"
        "**משימות בחינה טיפוסיות:** אלכסון מלא $2\\times2$ או $3\\times3$; חישוב $A^{100}$; "
        "הוכחת $A^n=PD^nP^{-1}$; סיווג מטריצות שאינן ניתנות לאלכסון.\n\n"
        "**אסטרטגיה:** תמיד חשבו $p(\\lambda)$ וכל $g_\\lambda$ לפני בניית $P$. "
        "בחזקות — $D^n$ קודם, אחר כך $PD^nP^{-1}$."
    ),
}

SECTION_BODIES["summary"] = {
    "body_en_md": (
        "- **Diagonalizable:** $A=PDP^{-1}$ with eigenvector columns in $P$ and eigenvalues on $D$.\n"
        "- **Criterion:** $g_\\lambda=a_\\lambda$ for every eigenvalue (equivalently, $n$ independent eigenvectors).\n"
        "- **Distinct eigenvalues** $\\Rightarrow$ diagonalizable (sufficient condition).\n"
        "- **Power formula:** $A^n=PD^nP^{-1}$ — reduces matrix powers to scalar powers.\n"
        "- **Non-diagonalizable $2\\times2$ over $\\mathbb{R}$:** defective repeated $\\lambda$ or no real eigenvalues.\n"
        "- **Symmetric matrices** are always diagonalizable (Spectral Theorem); optional orthogonal $P$.\n"
        "- **Next:** Jordan normal form when $g<a$; matrix exponentials via $Pe^{tD}P^{-1}$."
    ),
    "body_he_md": (
        "- **ניתנת לאלכסון:** $A=PDP^{-1}$; עמודות $P$ = ו\"ע; $D$ = ע\"ע.\n"
        "- **קריטריון:** $g_\\lambda=a_\\lambda$ לכל ע\"ע (שקול ל-$n$ ו\"ע בלתי-תלויים).\n"
        "- **ע\"ע שונים** $\\Rightarrow$ ניתנת (תנאי מספיק).\n"
        "- **נוסחת חזקה:** $A^n=PD^nP^{-1}$ — חזקות מטריצה לחזקות סקלריות.\n"
        "- **אי-אלכסוניות $2\\times2$ מעל $\\mathbb{R}$:** ע\"ע חוזר פגום או אין ע\"ע ממשיים.\n"
        "- **מטריצות סימטריות** תמיד ניתנות (משפט ספקטרלי); $P$ אורתוגונלית אופציונלית.\n"
        "- **המשך:** צורת ירדן כש-$g<a$; אקספוננציאל מטריצה דרך $Pe^{tD}P^{-1}$."
    ),
}

EXPLANATIONS = [
    fmt(
        "$A=\\begin{pmatrix}3&0\\\\0&7\\end{pmatrix}$ is already diagonal, so $P=I$ and $D=A$. "
        "Powers act entry-wise: $A^{10}=\\mathrm{diag}(3^{10},7^{10})="
        "\\begin{pmatrix}59049&0\\\\0&282475249\\end{pmatrix}$.",
        "Diagonal matrix $\\Rightarrow$ eigenvalues on the diagonal, standard basis vectors as "
        "eigenvectors. No need to invert $P$ when $P=I$. Verify: $3^{10}=59049$, $7^{10}=282475249$.",
        "Trying to find nontrivial $P$ when $A$ is already diagonal — wastes time. "
        "Forgetting that off-diagonal entries stay zero in $A^n$.",
        "On exams, spot diagonal form immediately — write $P=I$, $D=A$, then raise diagonal entries.",
        "$A=\\begin{pmatrix}3&0\\\\0&7\\end{pmatrix}$ כבר אלכסונית, $P=I$, $D=A$. "
        "חזקות כניסה-כניסה: $A^{10}=\\mathrm{diag}(3^{10},7^{10})$.",
        "מטריצה אלכסונית $\\Rightarrow$ ע\"ע על האלכסון, ו\"ע = בסיס סטנדרטי. "
        "כש-$P=I$ אין צורך בהיפוך. אימות: $3^{10}=59049$, $7^{10}=282475249$. "
        "זו הדרך המהירה ביותר לחזקות של מטריצה אלכסונית.",
        "חיפוש $P$ לא טriviial כש-$A$ כבר אלכסונית — בזבוז זמן. "
        "שכחה שמחוץ לאלכסון נשאר 0 ב-$A^n$.",
        "בבחינה — זיהוי אלכסון מיידי: $P=I$, $D=A$, העלאת כניסות האלכסון. "
        "כתבו במפורש $A^{10}=\\mathrm{diag}(59049,282475249)$.",
    ),
    fmt(
        "$A=I$ is the identity — already diagonal with eigenvalue $1$ (repeated, but $g=a=2$). "
        "Every vector is an eigenvector; take $P=I$, $D=I$. Therefore **diagonalizable**.",
        "Identity is the degenerate case: one eigenvalue with full geometric multiplicity. "
        "Do not confuse \"diagonal\" with \"distinct eigenvalues only.\"",
        "Answering \"not diagonalizable\" because eigenvalues repeat. Repeated $\\lambda=1$ "
        "with $g=2=a=2$ is perfectly fine.",
        "Repeated eigenvalues are OK when $g=a$. Only defective blocks ($g<a$) block diagonalization.",
        "$A=I$ היא מטריצת יחידה — אלכסונית עם $\\lambda=1$ (חוזר, אך $g=a=2$). "
        "$P=I$, $D=I$ — **ניתנת לאלכסון**.",
        "מטריצת יחידה: ע\"ע אחד עם ריבוי גיאומטרי מלא ($g=a=n$). "
        "אל תבלבלו \"אלכסונית\" עם \"רק ע\"ע שונים\" — חזרה מותרת כשיש מספיק ו\"ע.",
        "תשובה \"לא ניתנת\" כי ע\"ע חוזר — שגוי. $\\lambda=1$ עם $g=2=a=2$ תקין.",
        "ע\"ע חוזרים בסדר כש-$g=a$. רק $g<a$ (פגום) חוסם אלכסון. "
        "כאן $E_1=\\mathbb{R}^2$ ולכן יש בסיס מלא של ו\"ע.",
    ),
    fmt(
        "$B=I$ is diagonalizable (diagonal). For $C=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$: "
        "only $\\lambda=1$ with $a=2$ but $(C-I)$ has rank 1, so $g=1<2$ — **not diagonalizable**.",
        "Compare two matrices with the same eigenvalues: $B$ has full eigenspace; $C$ is a "
        "Jordan block (shear) — classic Type 1 non-diagonalizable example.",
        "Declaring both diagonalizable because they share eigenvalue 1. Missing the $g<a$ test on $C$.",
        "Side-by-side $I$ vs Jordan block questions appear often — always compute $g$ for repeated roots.",
        "$B=I$ ניתנת (אלכסונית). ל-$C=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$: "
        "$\\lambda=1$, $a=2$, $(C-I)$ בדרגה 1 $\\Rightarrow$ $g=1<2$ — **אינה ניתנת**.",
        "השוו שתי מטריצות עם אותם ע\"ע: $B$ עם מרחב עצמי מלא; $C$ גוש ירדן — "
        "דוגמת סוג 1 קלאסית.",
        "להכריז ששתיהן ניתנות כי $\\lambda=1$ — בלי בדיקת $g$ על $C$.",
        "שאלות $I$ מול גוש ירדן נפוצות — תמיד חשבו $g$ לשורשים חוזרים. "
        "$C-I$ מדרגת ל-$\\begin{pmatrix}0&1\\\\0&0\\end{pmatrix}$ — רק כיוון אחד.",
    ),
    fmt(
        "For rotation $A=\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\\\sin\\theta&\\cos\\theta\\end{pmatrix}$, "
        "$p(\\lambda)=\\lambda^2-2\\cos\\theta\\,\\lambda+1$. Discriminant "
        "$\\Delta=4(\\cos^2\\theta-1)\\le0$, strictly $<0$ for $\\theta\\neq0,\\pi$ — no real roots.",
        "Geometrically, a non-trivial rotation has no axis of scaling in $\\mathbb{R}^2$ — "
        "hence no real eigenvectors. This is Type 2 non-diagonalizability over $\\mathbb{R}$.",
        "Setting $\\det(A-\\lambda I)=0$ but not checking the discriminant sign. "
        "Claiming complex eigenvalues still allow real diagonalization.",
        "Rotation matrices: compute $\\Delta=4(\\cos^2\\theta-1)$; if negative, state "
        "\"not diagonalizable over $\\mathbb{R}$\" explicitly.",
        "לסיבוב $A=\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\\\sin\\theta&\\cos\\theta\\end{pmatrix}$, "
        "$p(\\lambda)=\\lambda^2-2\\cos\\theta\\,\\lambda+1$, $\\Delta=4(\\cos^2\\theta-1)<0$ "
        "ל-$\\theta\\neq0,\\pi$ — אין שורשים ממשיים.",
        "גיאומטרית: סיבוב לא טriviial אין לו ציר כיוון ב-$\\mathbb{R}^2$ — "
        "אין ו\"ע ממשיים. סוג 2 מעל $\\mathbb{R}$. מעל $\\mathbb{C}$ המטריצה כן ניתנת לאלכסון.",
        "פתרון $\\det(A-\\lambda I)=0$ בלי סימן דיסקרימיננטה. "
        "טענה שע\"ע מרוכבים מאפשרים אלכסון ממשי.",
        "מטריצות סיבוב: $\\Delta=4(\\cos^2\\theta-1)$; שלילי $\\Rightarrow$ "
        "\"אינה ניתנת מעל $\\mathbb{R}$\" במפורש — אך כן מעל $\\mathbb{C}$ "
        "עם ע\"ע $e^{\\pm i\\theta}$.",
    ),
    fmt(
        "Triangular $A=\\begin{pmatrix}1&2\\\\0&3\\end{pmatrix}$ has eigenvalues $1,3$ on the diagonal. "
        "Eigenvectors: $\\vec{v}_1=(1,0)^T$ for $\\lambda=1$; from $(A-3I)\\vec{v}=0$ get $\\vec{v}_2=(1,1)^T$. "
        "With $P=\\begin{pmatrix}1&1\\\\0&1\\end{pmatrix}$ and $D=\\mathrm{diag}(1,81)$, "
        "$A^4=PD^4P^{-1}=\\begin{pmatrix}1&80\\\\0&81\\end{pmatrix}$.",
        "Upper triangular $\\Rightarrow$ eigenvalues on diagonal. Find $E_3$ from $(A-3I)\\vec{v}=0$. "
        "Use $A^k=PD^kP^{-1}$; for this $P$, $P^{-1}=\\begin{pmatrix}1&-1\\\\0&1\\end{pmatrix}$.",
        "Arithmetic errors in $P^{-1}$ or matrix multiply. Computing $A^4$ by brute force "
        "instead of $D^4=\\mathrm{diag}(1,81)$.",
        "After finding $P$, verify $AP=PD$ once — catches column-order bugs before the power step.",
        "$A=\\begin{pmatrix}1&2\\\\0&3\\end{pmatrix}$ משולשת: ע\"ע $1,3$ על האלכסון. "
        "$\\vec{v}_1=(1,0)^T$ ל-$\\lambda=1$; מ-$(A-3I)\\vec{v}=0$ נובע $\\vec{v}_2=(1,1)^T$. "
        "לכן $A^4=\\begin{pmatrix}1&80\\\\0&81\\end{pmatrix}$.",
        "משולשת עליונה $\\Rightarrow$ ע\"ע על האלכסון. $E_3$ מ-$(A-3I)\\vec{v}=0$ נותן $v_1=v_2$. "
        "$A^k=PD^kP^{-1}$; $P^{-1}=\\begin{pmatrix}1&-1\\\\0&1\\end{pmatrix}$ לכפל מהיר.",
        "שגיאות ב-$P^{-1}$ או בכפל מטריצות. חישוב $A^4$ ישיר במקום $D^4=\\mathrm{diag}(1,81)$ — "
        "מיותר ומסוכן לשגיאות.",
        "אחרי $P$ — אמתו $AP=PD$ פעם אחת לפני החזקה. "
        "הכניסה $(1,2)$ ב-$A^4$ נובעת מ-$81-1=80$ — בדקו ש-$D^4=\\mathrm{diag}(1,81)$ לפני הכפל.",
    ),
    fmt(
        "Eigenvalues: $\\lambda=2$ ($a=2$) and $\\lambda=3$ ($a=1$). For $\\lambda=2$, "
        "$A-2I=\\begin{pmatrix}0&1&0\\\\0&0&0\\\\0&0&1\\end{pmatrix}$ has rank 2, "
        "so $g=1<2=a$ — **not diagonalizable** (Jordan block in top-left).",
        "Upper block $\\begin{pmatrix}2&1\\\\0&2\\end{pmatrix}$ is defective even though "
        "$\\lambda=3$ is fine. One bad eigenvalue is enough to fail diagonalizability.",
        "Checking only $\\lambda=3$ or assuming triangular $\\Rightarrow$ always diagonalizable. "
        "Ignoring the repeated 2 on the diagonal.",
        "For block-triangular matrices, test $g=a$ at **each** eigenvalue — especially repeated ones.",
        "ע\"ע: $\\lambda=2$ ($a=2$), $\\lambda=3$ ($a=1$). ל-$\\lambda=2$: "
        "$A-2I$ בדרגה 2 $\\Rightarrow$ $g=1<2$ — **אינה ניתנת** (גוש ירדן).",
        "הגוש $\\begin{pmatrix}2&1\\\\0&2\\end{pmatrix}$ פגום גם כש-$\\lambda=3$ תקין עם $g=a=1$. "
        "ע\"ע אחד \"רע\" מספיק לכישלון אלכסון ב-$\\mathbb{R}^3$.",
        "בדיקה רק של $\\lambda=3$ או הנחה שמשולשת $\\Rightarrow$ תמיד ניתנת — "
        "שגוי כשיש ע\"ע חוזר $2$ עם $g=1$.",
        "במטריצות בלוק-משולש — בדקו $g=a$ ל**כל** ע\"ע, במיוחד חוזרים. "
        "הגוש העליון $\\begin{pmatrix}2&1\\\\0&2\\end{pmatrix}$ הוא גוש ירדן קלאסי.",
    ),
    fmt(
        "$p(\\lambda)=\\lambda^2-3\\lambda+2=(\\lambda-1)(\\lambda-2)$ gives distinct eigenvalues, "
        "so $A$ is diagonalizable. With $\\vec{v}_1=(1,1)^T$, $\\vec{v}_2=(2,1)^T$, "
        "$P=\\begin{pmatrix}1&2\\\\1&1\\end{pmatrix}$, $P^{-1}=\\begin{pmatrix}-1&2\\\\1&-1\\end{pmatrix}$, "
        "and $D^n=\\mathrm{diag}(1,2^n)$, simplifying $PD^nP^{-1}$ yields "
        "$A^n=\\begin{pmatrix}2^{n+1}-1&2-2^{n+1}\\\\2^n-1&2-2^n\\end{pmatrix}$.",
        "Closed form comes from outer products of eigenvectors weighted by $\\lambda_i^n$. "
        "Verify $n=1$ returns $A=\\begin{pmatrix}3&-2\\\\1&0\\end{pmatrix}$ and $n=2$ gives "
        "$A^2=\\begin{pmatrix}7&-6\\\\3&-2\\end{pmatrix}$ before submitting on an exam.",
        "Using the wrong formula from a table without deriving from your $P$. "
        "Sign errors in $P^{-1}=\\begin{pmatrix}-1&2\\\\1&-1\\end{pmatrix}$.",
        "When asked for $A^n$ formula, diagonalize cleanly first — exam graders check $n=1,2$ special cases.",
        "$p(\\lambda)=(\\lambda-1)(\\lambda-2)$ — ע\"ע שונים, ניתנת לאלכסון. "
        "$P=\\begin{pmatrix}1&2\\\\1&1\\end{pmatrix}$, "
        "$A^n=\\begin{pmatrix}2^{n+1}-1&2-2^{n+1}\\\\2^n-1&2-2^n\\end{pmatrix}$ לאחר פישוט $PD^nP^{-1}$.",
        "נוסחה סגורה מכפלות חיצוניות של ו\"ע משוקללות ב-$\\lambda_i^n$. "
        "בדקו $n=1$ מחזיר $A=\\begin{pmatrix}3&-2\\\\1&0\\end{pmatrix}$ ו-$n=2$ מחזיר $A^2$.",
        "נוסחה שגויה מטבלה בלי גזירה מ-$P$ שלכם. טעויות סימן ב-$P^{-1}=\\begin{pmatrix}-1&2\\\\1&-1\\end{pmatrix}$ "
        "משנות את כל הנוסחה הסגורה.",
        "בנוסחת $A^n$ — אלכסנו נכון; בודקים $n=1,2$ לפני הגשה. "
        "הנוסחה נגזרת מ-$PD^nP^{-1}$ עם $P^{-1}=\\begin{pmatrix}-1&2\\\\1&-1\\end{pmatrix}$ — "
        "אמתו $n=2$ לפני הגשה.",
    ),
    fmt(
        "If $A=PDP^{-1}$ with invertible $D$, multiply $A$ on the right by $PD^{-1}P^{-1}$: "
        "$A\\cdot(PD^{-1}P^{-1})=PDP^{-1}PD^{-1}P^{-1}=PD(D^{-1}D)P^{-1}=PIP^{-1}=I$. "
        "By uniqueness of the matrix inverse, $A^{-1}=PD^{-1}P^{-1}$.",
        "This mirrors the power proof: similarity transforms turn matrix inverse into "
        "entry-wise inverse on $D$. Requires every eigenvalue $\\lambda_i\\neq 0$ so $D^{-1}$ exists.",
        "Writing $A^{-1}=P^{-1}DP^{-1}$ (wrong order). Forgetting invertibility requires $\\lambda_i\\neq0$.",
        "Inverse proof is one line if you already accept $A^n=PD^nP^{-1}$ — reuse the $P^{-1}P=I$ cancellation.",
        "$A\\cdot(PD^{-1}P^{-1})=PDP^{-1}PD^{-1}P^{-1}=PDD^{-1}P^{-1}=I$. "
        "מייחודיות ההופכית: $A^{-1}=PD^{-1}P^{-1}$ כש-$D$ הפיכה (כל $\\lambda_i\\neq0$).",
        "אותו דפוס כמו $A^n$: דמיון שומר כפל; היפוך אלכסוני כניסה-כניסה. "
        "הוכחה קצרה: כפלו $A$ ב-$PD^{-1}P^{-1}$ וקבלו $I$.",
        "כתיבה $A^{-1}=P^{-1}DP^{-1}$ (סדר שגוי). שכחת $\\lambda_i\\neq0$ — "
        "אם $\\lambda=0$ ע\"ע, $A$ סינגולרית ואין הופכית.",
        "הוכחת היפוך — שורה אחת אם $A^n=PD^nP^{-1}$ מוכח; השתמשו ב-$P^{-1}P=I$. "
        "דורש $\\lambda_i\\neq 0$ — אחרת $A$ סינגולרית ואין $A^{-1}$. "
        "אותה טכניקה מוכיחה גם $A^n=PD^nP^{-1}$.",
    ),
]


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
    we_idx = cp_idx = 0
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

    # Fix rotation matrix LaTeX in stems (missing row break)
    rot = "\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\\\\\sin\\theta&\\cos\\theta\\end{pmatrix}"
    bad = "\\begin{pmatrix}\\cos\\theta&-\\sin\\theta\\sin\\theta&\\cos\\theta\\end{pmatrix}"
    for q in data["questions"]:
        if q["ord"] == 4:
            q["stem_en"] = q["stem_en"].replace(bad, rot)
            q["stem_he"] = q["stem_he"].replace(bad, rot)
    for s in data["sections"]:
        if s["kind"] == "exercise_set":
            for ex in s.get("exercises", []):
                if ex["id"] == "e4":
                    ex["body_en"] = ex["body_en"].replace(bad, rot)
                    ex["body_he"] = ex["body_he"].replace(bad, rot)

    data["version"] = 2
    data["author"] = "cursor-claude-2026"

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    errs = []
    for s in data["sections"]:
        k = s["kind"]
        if k not in MIN:
            continue
        en, he = wc(s["body_en_md"]), wc(s["body_he_md"])
        en_min, he_min = MIN[k]
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
