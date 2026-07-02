# -*- coding: utf-8 -*-
"""Content payload for _expand_inner_product_gram_schmidt.py"""

SECTION_BODIES = {
    "intro": {
        "body_en_md": """The dot product on $\\mathbb{R}^n$ gave us a way to measure angles, lengths, and orthogonality. An **inner product space** generalises this notion to abstract vector spaces — allowing us to talk about perpendicularity in spaces of functions, polynomials, and infinite-dimensional settings, not just columns of numbers.

Once you have an inner product, you can define **norms**, **angles**, **orthogonal projections**, and **orthonormal bases**. The **Gram–Schmidt process** converts any linearly independent set into an orthonormal basis spanning the same subspace. This algorithm is the computational backbone of QR decomposition, least-squares regression, and numerical linear algebra libraries used in engineering and data science.

**Connection to previous material:** This lesson builds directly on `concept:la_vector_spaces` (subspaces, linear independence, span) and the standard dot product on $\\mathbb{R}^n$. It feeds forward into `concept:la_orthogonality`, orthogonal matrices, and spectral methods. Master the axioms first, then projection, then Gram–Schmidt — that order mirrors how university courses and Israeli exams structure the material.""",
        "body_he_md": """המכפלה הפנימית ב-$\\mathbb{R}^n$ נתנה לנו דרך למדוד זוויות, אורכים ואורתוגונליות. **מרחב מכפלה פנימית** מכליל מושג זה למרחבים וקטוריים מופשטים — ומאפשר לדבר על ניצבות במרחבי פונקציות, פולינומים ומרחבים אינסופיים-ממדיים, לא רק בעמודות מספרים.

ברגע שיש מכפלה פנימית, אפשר להגדיר **נורמות**, **זוויות**, **הטלות אורתוגונליות** ו**בסיסים אורתונורמליים**. **תהליך גרם–שמידט** ממיר כל קבוצה בלתי-תלויה לבסיס אורתונורמלי עם אותה פרישה. אלגוריתם זה הוא עמוד השדרה של פירוק QR, רגרסיה בריבועים פחותים וספריות אלגברה לינארית נומרית בהנדסה ובמדעי הנתונים.

**קשר לחומר קודם:** שיעור זה בנוי ישירות על `concept:la_vector_spaces` (תת-מרחבים, בלתי-תלות, פרישה) ועל המכפלה הסטנדרטית ב-$\\mathbb{R}^n$. הוא מוביל ל-`concept:la_orthogonality`, מטריצות אורתוגונליות ושיטות ספקטרליות. שלטו תחילה באקסיומות, אחר כך בהטלה, ולבסוף בגרם–שמידט — סדר זה משקף את מבנה הקורסים והבחינות בישראל.""",
    },
    "definition": {
        "body_en_md": """**Definition (Inner product).** An **inner product** on a real vector space $V$ is a function $\\langle\\cdot,\\cdot\\rangle: V\\times V\\to\\mathbb{R}$ satisfying:
1. **Symmetry:** $\\langle\\vec{u},\\vec{v}\\rangle = \\langle\\vec{v},\\vec{u}\\rangle$.
2. **Linearity in the first argument:** $\\langle c\\vec{u}+\\vec{w},\\vec{v}\\rangle = c\\langle\\vec{u},\\vec{v}\\rangle+\\langle\\vec{w},\\vec{v}\\rangle$.
3. **Positive definiteness:** $\\langle\\vec{v},\\vec{v}\\rangle \\geq 0$, with equality if and only if $\\vec{v}=\\vec{0}$.

**Standard inner product on $\\mathbb{R}^n$:** $\\langle\\vec{u},\\vec{v}\\rangle = \\vec{u}\\cdot\\vec{v}=\\sum u_iv_i$.

**Inner product on $C[a,b]$:** $\\langle f,g\\rangle = \\int_a^b f(x)g(x)\\,dx$ (continuous functions on $[a,b]$).

**Norm:** $\\|\\vec{v}\\| = \\sqrt{\\langle\\vec{v},\\vec{v}\\rangle}$. A **unit vector** satisfies $\\|\\vec{v}\\|=1$.

**Orthogonality:** $\\vec{u}\\perp\\vec{v}$ iff $\\langle\\vec{u},\\vec{v}\\rangle=0$.

**Orthonormal set (ONB):** $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ is **orthonormal** if $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$ (Kronecker delta: 1 if $i=j$, 0 otherwise).

**Orthogonal projection onto a subspace:** If $W=\\text{span}\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ with orthonormal basis $\\{\\vec{q}_i\\}$, then
$$\\text{proj}_W\\vec{v} = \\sum_{i=1}^k\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i.$$
For a single non-zero vector $\\vec{u}$: $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$.

**Gram–Schmidt process:** Given linearly independent $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$, construct orthonormal $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ spanning the same subspace:
$$\\vec{u}_j = \\vec{a}_j - \\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i, \\qquad \\vec{q}_j = \\frac{\\vec{u}_j}{\\|\\vec{u}_j\\|}.$$
The process requires linear independence so that each $\\vec{u}_j\\neq\\vec{0}$ and normalization is defined.""",
        "body_he_md": """**הגדרה (מכפלה פנימית).** **מכפלה פנימית** על מרחב ממשי $V$ היא פונקציה $\\langle\\cdot,\\cdot\\rangle: V\\times V\\to\\mathbb{R}$ המקיימת:
1. **סימטריה:** $\\langle\\vec{u},\\vec{v}\\rangle = \\langle\\vec{v},\\vec{u}\\rangle$.
2. **לינאריות בארגומנט הראשון:** $\\langle c\\vec{u}+\\vec{w},\\vec{v}\\rangle = c\\langle\\vec{u},\\vec{v}\\rangle+\\langle\\vec{w},\\vec{v}\\rangle$.
3. **חיוביות מוגדרת:** $\\langle\\vec{v},\\vec{v}\\rangle \\geq 0$, שוויון אם ורק אם $\\vec{v}=\\vec{0}$.

**מכפלה סטנדרטית ב-$\\mathbb{R}^n$:** $\\langle\\vec{u},\\vec{v}\\rangle = \\sum u_iv_i$.

**ב-$C[a,b]$:** $\\langle f,g\\rangle = \\int_a^b f(x)g(x)\\,dx$ (פונקציות רציפות).

**נורמה:** $\\|\\vec{v}\\| = \\sqrt{\\langle\\vec{v},\\vec{v}\\rangle}$. **וקטור יחידה** מקיים $\\|\\vec{v}\\|=1$.

**אורתוגונליות:** $\\vec{u}\\perp\\vec{v}$ אם ורק אם $\\langle\\vec{u},\\vec{v}\\rangle=0$.

**קבוצה אורתונורמלית (ONB):** $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ **אורתונורמלית** אם $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$ (1 כש-$i=j$, 0 אחרת).

**הטלה אורתוגונלית על תת-מרחב:** אם $W=\\text{span}\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ עם בסיס אורתונורמלי, אז
$$\\text{proj}_W\\vec{v} = \\sum_{i=1}^k\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i.$$
על וקטור בודד $\\vec{u}\\neq\\vec{0}$: $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$.

**תהליך גרם–שמידט:** נתונה קבוצה בלתי-תלויה $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$, בונים $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ אורתונורמלית עם אותה פרישה:
$$\\vec{u}_j = \\vec{a}_j - \\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i, \\qquad \\vec{q}_j = \\frac{\\vec{u}_j}{\\|\\vec{u}_j\\|}.$$
התהליך דורש בלתי-תלות כדי ש-$\\vec{u}_j\\neq\\vec{0}$ בכל שלב והנרמול מוגדר.""",
    },
    "theory": {
        "body_en_md": """**Theorem 1 (Gram–Schmidt terminates).** If $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$ is linearly independent, then in the Gram–Schmidt process $\\vec{u}_j\\neq\\vec{0}$ for all $j$, so normalization is always defined and the process produces an orthonormal set with the same span at each step.

**Theorem 2 (Orthonormal implies independent).** An orthonormal set is linearly independent. Proof sketch: if $\\sum c_i\\vec{q}_i=\\vec{0}$, take $\\langle\\cdot,\\vec{q}_j\\rangle$ to get $c_j=0$ for all $j$.

**Theorem 3 (Best approximation / projection theorem).** The projection $\\text{proj}_W\\vec{v}$ is the unique vector in $W$ closest to $\\vec{v}$:
$$\\|\\vec{v}-\\text{proj}_W\\vec{v}\\| \\leq \\|\\vec{v}-\\vec{w}\\| \\quad \\forall\\,\\vec{w}\\in W.$$
Equivalently, the residual $\\vec{v}-\\text{proj}_W\\vec{v}$ is orthogonal to every vector in $W$. This is the geometric foundation of least-squares fitting.

**Theorem 4 (Parseval's identity).** If $\\{\\vec{q}_i\\}_{i=1}^n$ is an orthonormal basis for $V$:
$$\\|\\vec{v}\\|^2 = \\sum_{i=1}^n |\\langle\\vec{v},\\vec{q}_i\\rangle|^2.$$
The coefficients $\\langle\\vec{v},\\vec{q}_i\\rangle$ are **Fourier coefficients** in the ONB.

**Theorem 5 (Bessel's inequality).** For any orthonormal set (not necessarily a full basis):
$$\\sum_{i=1}^k |\\langle\\vec{v},\\vec{q}_i\\rangle|^2 \\leq \\|\\vec{v}\\|^2.$$
Equality holds for all $\\vec{v}$ iff the set is a complete ONB for the subspace (or space) in question.

**Cauchy–Schwarz:** $|\\langle\\vec{u},\\vec{v}\\rangle|\\leq\\|\\vec{u}\\|\\|\\vec{v}\\|$. Used to bound projection coefficients and prove the triangle inequality for the induced norm.""",
        "body_he_md": """**משפט 1 (גרם–שמידט מסתיים).** אם $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$ בלתי-תלויה, אז $\\vec{u}_j\\neq\\vec{0}$ לכל $j$ בתהליך גרם–שמידט, ולכן הנרמול מוגדר תמיד והתהליך מייצר קבוצה אורתונורמלית עם אותה פרישה בכל שלב.

**משפט 2 (אורתונורמלי ⇒ בלתי-תלוי).** קבוצה אורתונורמלית בלתי-תלויה לינארית. רעיון הוכחה: אם $\\sum c_i\\vec{q}_i=\\vec{0}$, לקחת $\\langle\\cdot,\\vec{q}_j\\rangle$ נותן $c_j=0$ לכל $j$.

**משפט 3 (קירוב מיטבי / משפט ההטלה).** $\\text{proj}_W\\vec{v}$ הוא הוקטור היחיד ב-$W$ הקרוב ביותר ל-$\\vec{v}$:
$$\\|\\vec{v}-\\text{proj}_W\\vec{v}\\| \\leq \\|\\vec{v}-\\vec{w}\\| \\quad \\forall\\,\\vec{w}\\in W.$$
שקול לכך: השארית $\\vec{v}-\\text{proj}_W\\vec{v}$ אורתוגונלית לכל וקטור ב-$W$. זה הבסיס הגאומטרי של התאמת ריבועים פחותים.

**משפט 4 (זהות פרסבל).** אם $\\{\\vec{q}_i\\}_{i=1}^n$ בסיס אורתונורמלי ל-$V$:
$$\\|\\vec{v}\\|^2 = \\sum_{i=1}^n |\\langle\\vec{v},\\vec{q}_i\\rangle|^2.$$
המקדמים $\\langle\\vec{v},\\vec{q}_i\\rangle$ הם **מקדמי פourier** בבסיס האורתונורמלי.

**משפט 5 (אי-שוויון בסל).** לכל קבוצה אורתונורמלית (לא בהכרח בסיס מלא):
$$\\sum_{i=1}^k |\\langle\\vec{v},\\vec{q}_i\\rangle|^2 \\leq \\|\\vec{v}\\|^2.$$
שוויון לכל $\\vec{v}$ אם ורק אם הקבוצה בסיס ONB מלא לתת-מרחב (או למרחב).

**קושי–שוורץ:** $|\\langle\\vec{u},\\vec{v}\\rangle|\\leq\\|\\vec{u}\\|\\|\\vec{v}\\|$. משמש לחסימת מקדמי הטלה ולהוכחת אי-שוויון המשולש לנורמה.""",
    },
    "worked_example_1": {
        "body_en_md": """**Project** $\\vec{v}=(1,1,1)$ onto $\\vec{u}=(1,0,0)$.

### Move 1: Choose the formula
For projection onto a line spanned by a non-unit vector $\\vec{u}$:
$$\\text{proj}_{\\vec{u}}\\vec{v} = \\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\langle\\vec{u},\\vec{u}\\rangle}\\vec{u}.$$

### Move 2: Compute inner products
$$\\langle\\vec{v},\\vec{u}\\rangle = 1\\cdot1+1\\cdot0+1\\cdot0 = 1, \\quad \\langle\\vec{u},\\vec{u}\\rangle = 1.$$

### Move 3: Apply
$$\\text{proj}_{\\vec{u}}\\vec{v} = \\frac{1}{1}(1,0,0) = (1,0,0).$$

### Move 4: Residual and verification
**Residual:** $\\vec{v}-\\text{proj}_{\\vec{u}}\\vec{v} = (0,1,1)$. Check orthogonality: $(0,1,1)\\cdot(1,0,0)=0$. ✓

**Interpretation:** We extracted the $x$-component of $(1,1,1)$. The residual $(0,1,1)$ lies in the $yz$-plane, perpendicular to the $x$-axis. By Pythagoras, $\\|\\vec{v}\\|^2=\\|\\text{proj}\\|^2+\\|(0,1,1)\\|^2$, confirming the decomposition into parallel and perpendicular parts.

**Exam tip:** Always verify $b-\\hat{b}\\perp u$ — examiners award credit for the orthogonality check even if projection arithmetic was partially wrong.

**Distance check:** The distance from $\\vec{v}$ to the line spanned by $\\vec{u}$ equals $\\|(0,1,1)\\|=\\sqrt{2}$, which you can report as the length of the perpendicular component removed by projection.

**Pythagorean check:** $\\|\\vec{v}\\|^2=3=\\|\\text{proj}\\|^2+\\|(0,1,1)\\|^2=1+2$. ✓

This example illustrates the general pattern: projection onto a coordinate axis is equivalent to zeroing all other coordinates. In exam problems, always write the formula before substituting numbers, and label the residual vector explicitly so the grader can follow your orthogonality verification.""",
        "body_he_md": """**הטל** $\\vec{v}=(1,1,1)$ על $\\vec{u}=(1,0,0)$.

### צעד 1: בחירת הנוסחה
להטלה על קו הנפרש על ידי וקטור $\\vec{u}$ שאינו יחידה:
$$\\text{proj}_{\\vec{u}}\\vec{v} = \\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\langle\\vec{u},\\vec{u}\\rangle}\\vec{u}.$$

### צעד 2: חישוב מכפלות פנימיות
$$\\langle\\vec{v},\\vec{u}\\rangle = 1, \\quad \\langle\\vec{u},\\vec{u}\\rangle = 1.$$

### צעד 3: יישום
$$\\text{proj}_{\\vec{u}}\\vec{v} = (1,0,0).$$

### צעד 4: שארית ואימות
**שארית:** $(0,1,1)$. בדיקת אורתוגונליות: $(0,1,1)\\cdot(1,0,0)=0$. ✓

**פרשנות:** חילצנו את הרכיב ב-$x$ של $(1,1,1)$. השארית $(0,1,1)$ שוכבת במישור $yz$, ניצב לציר $x$. לפי פיתגורס, $\\|\\vec{v}\\|^2=\\|\\text{proj}\\|^2+\\|(0,1,1)\\|^2$, מה שמאשר פירוק לרכיב מקביל וניצב.

**טיפ לבחינה:** תמיד אמתו $b-\\hat{b}\\perp u$ — בוחנים נותנים נקודות על בדיקת אורתוגונליות גם אם החישוב היה חלקית שגוי.

**בדיקת מרחק:** המרחק מ-$\\vec{v}$ לקו הנפרש על $\\vec{u}$ שווה $\\|(0,1,1)\\|=\\sqrt{2}$ — אורך הרכיב הניצב שההטלה מסירה.

**בדיקת פיתגורס:** $\\|\\vec{v}\\|^2=3=\\|\\text{proj}\\|^2+\\|(0,1,1)\\|^2=1+2$. ✓

דוגמה זו ממחישה את הדפוס הכללי: הטלה על ציר קואורדינטות שקולה לאפס כל קואורדינטה אחרת. בבחינות, כתבו תמיד את הנוסחה לפני הצבה, וסמנו את וקטור השארית במפורש כדי שהבודק יוכל לעקוב אחרי אימות האורתוגונליות.""",
    },
    "worked_example_2": {
        "body_en_md": """**Apply Gram–Schmidt** to $\\{\\vec{a}_1,\\vec{a}_2,\\vec{a}_3\\} = \\{(1,1,0),(1,0,1),(0,1,1)\\}$.

### Move 1
$$\\vec{u}_1=(1,1,0), \\quad \\|\\vec{u}_1\\|=\\sqrt{2}, \\quad \\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0).$$

### Move 2
$$\\langle\\vec{a}_2,\\vec{q}_1\\rangle = (1,0,1)\\cdot\\frac{1}{\\sqrt{2}}(1,1,0) = \\frac{1}{\\sqrt{2}}.$$
$$\\vec{u}_2 = \\vec{a}_2 - \\langle\\vec{a}_2,\\vec{q}_1\\rangle\\vec{q}_1 = (1,0,1)-\\frac{1}{2}(1,1,0) = \\left(\\frac{1}{2},-\\frac{1}{2},1\\right).$$
$$\\|\\vec{u}_2\\|=\\sqrt{\\frac{3}{2}}, \\quad \\vec{q}_2=\\frac{1}{\\sqrt{6}}(1,-1,2).$$

### Move 3
$$\\langle\\vec{a}_3,\\vec{q}_1\\rangle=\\frac{1}{\\sqrt{2}}, \\quad \\langle\\vec{a}_3,\\vec{q}_2\\rangle=\\frac{1}{\\sqrt{6}}.$$
$$\\vec{u}_3=(0,1,1)-\\frac{1}{2}(1,1,0)-\\frac{1}{6}(1,-1,2)=\\frac{2}{3}(-1,1,1), \\quad \\vec{q}_3 = \\frac{1}{\\sqrt{3}}(-1,1,1).$$

### Move 4: Verify
Check $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ for $i\\neq j$ and $\\|\\vec{q}_i\\|=1$. The three $\\vec{q}_i$ span $\\mathbb{R}^3$ since the input was independent.

**Result:** $\\left\\{\\frac{1}{\\sqrt{2}}(1,1,0),\\;\\frac{1}{\\sqrt{6}}(1,-1,2),\\;\\frac{1}{\\sqrt{3}}(-1,1,1)\\right\\}$ is an orthonormal basis.

**Exam tip:** Compute $\\vec{u}_j$ before normalizing. Never divide $\\vec{a}_j$ by its norm before subtracting all prior projections.

### Move 5: QR connection
Stack $Q=[\\vec{q}_1|\\vec{q}_2|\\vec{q}_3]$; the upper-triangular $R$ has entries $R_{ij}=\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ for $i\\leq j$, giving $A=QR$ for $A=[\\vec{a}_1|\\vec{a}_2|\\vec{a}_3]$. This factorization is used in every numerical linear algebra library for solving least-squares problems efficiently.

**Common exam pattern:** You will often be given three vectors in $\\mathbb{R}^3$ and asked for the full ONB — show every $\\vec{u}_j$ before $\\vec{q}_j$, and verify $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ at the end for partial credit.""",
        "body_he_md": """**הפעל גרם–שמידט** על $\\{(1,1,0),(1,0,1),(0,1,1)\\}$.

### צעד 1
$$\\vec{u}_1=(1,1,0), \\quad \\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0).$$

### צעד 2
$$\\langle\\vec{a}_2,\\vec{q}_1\\rangle = \\frac{1}{\\sqrt{2}}, \\quad \\vec{u}_2 = \\left(\\frac{1}{2},-\\frac{1}{2},1\\right), \\quad \\vec{q}_2=\\frac{1}{\\sqrt{6}}(1,-1,2).$$

### צעד 3
$$\\vec{u}_3=\\frac{2}{3}(-1,1,1), \\quad \\vec{q}_3 = \\frac{1}{\\sqrt{3}}(-1,1,1).$$

### צעד 4: אימות
בדקו $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ ל-$i\\neq j$ ו-$\\|\\vec{q}_i\\|=1$. שלושת $\\vec{q}_i$ פורשים את $\\mathbb{R}^3$ כי הקלט היה בלתי-תלוי.

**תוצאה:** $\\left\\{\\frac{1}{\\sqrt{2}}(1,1,0),\\frac{1}{\\sqrt{6}}(1,-1,2),\\frac{1}{\\sqrt{3}}(-1,1,1)\\right\\}$ — בסיס אורתונורמלי.

**טיפ לבחינה:** חשבו $\\vec{u}_j$ לפני נרמול. לעולם אל תחלקו $\\vec{a}_j$ בנורמה לפני חיסור כל ההטלות הקודמות.

### צעד 5: קשר ל-QR
ערמו $Q=[\\vec{q}_1|\\vec{q}_2|\\vec{q}_3]$; $R$ משולשת עליונה עם $R_{ij}=\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ ל-$i\\leq j$, ומתקבל $A=QR$ עבור $A=[\\vec{a}_1|\\vec{a}_2|\\vec{a}_3]$. פירוק זה משמש בכל ספרייה נומרית לפתרון יעיל של בעיות ריבועים פחותים.

**דפוס בחינה נפוץ:** לעיתים קרובות נותנים שלושה וקטורים ב-$\\mathbb{R}^3$ ומבקשים ONB מלא — הציגו כל $\\vec{u}_j$ לפני $\\vec{q}_j$, ואמתו $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ בסוף לנקודות חלקיות.""",
    },
    "worked_example_3": {
        "body_en_md": """**Claim:** If $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$ is linearly independent, Gram–Schmidt produces an orthonormal set $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ with the same span at each step.

**Proof by induction on $k$:**

**Base case ($k=1$):** $\\vec{q}_1 = \\vec{a}_1/\\|\\vec{a}_1\\|$. Since $\\vec{a}_1\\neq\\vec{0}$ (independent), $\\|\\vec{a}_1\\|>0$. Clearly $\\|\\vec{q}_1\\|=1$. ✓

**Inductive step.** Assume $\\{\\vec{q}_1,\\ldots,\\vec{q}_{j-1}\\}$ is orthonormal with $\\text{span}\\{\\vec{q}_1,\\ldots,\\vec{q}_{j-1}\\}=\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_{j-1}\\}$. Define
$$\\vec{u}_j = \\vec{a}_j - \\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i.$$

**Step A: $\\vec{u}_j\\neq\\vec{0}$.** The sum lies in $\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_{j-1}\\}$. If $\\vec{u}_j=\\vec{0}$, then $\\vec{a}_j$ is a linear combination of earlier $\\vec{a}_i$, contradicting independence.

**Step B: $\\vec{q}_j\\perp\\vec{q}_l$ for $l<j$.** Using orthonormality of prior $\\vec{q}_i$:
$$\\langle\\vec{u}_j,\\vec{q}_l\\rangle = \\langle\\vec{a}_j,\\vec{q}_l\\rangle - \\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\langle\\vec{q}_i,\\vec{q}_l\\rangle.$$
Since $\\langle\\vec{q}_i,\\vec{q}_l\\rangle=\\delta_{il}$, the sum collapses to $\\langle\\vec{a}_j,\\vec{q}_l\\rangle$, giving $\\langle\\vec{u}_j,\\vec{q}_l\\rangle=0$. Since $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$, we get $\\langle\\vec{q}_j,\\vec{q}_l\\rangle=0$. ✓

**Step C: $\\|\\vec{q}_j\\|=1$** by construction ($\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$ and $\\vec{u}_j\\neq\\vec{0}$ from Step A).

**Step D (span preserved):** $\\vec{q}_j$ is a non-zero linear combination of $\\vec{a}_j$ and $\\vec{q}_1,\\ldots,\\vec{q}_{j-1}$, each of which lies in $\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_j\\}$. Hence adding $\\vec{q}_j$ does not enlarge the span beyond $\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_j\\}$, and conversely $\\vec{a}_j\\in\\text{span}\\{\\vec{q}_1,\\ldots,\\vec{q}_j\\}$.

By induction, $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ is orthonormal. $\\blacksquare$

**Exam tip:** Step A (why $\\vec{u}_j\\neq\\vec{0}$) is the key link between linear independence and successful Gram–Schmidt — state it explicitly on every proof question.

**Corollary:** If the input is dependent, some $\\vec{u}_j=\\vec{0}$ and the algorithm signals which vector is redundant — drop it and continue with the remaining independent set.

**Why induction works:** Each step adds exactly one new orthonormal direction while preserving the span of all vectors processed so far — the inductive hypothesis matches the algorithm structure perfectly.""",
        "body_he_md": """**טענה:** אם $\\{\\vec{a}_1,\\ldots,\\vec{a}_k\\}$ בלתי-תלויה, גרם–שמידט מייצר קבוצה אורתונורמלית $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ עם אותה פרישה בכל שלב.

**הוכחה באינדוקציה על $k$:**

**בסיס ($k=1$):** $\\vec{q}_1=\\vec{a}_1/\\|\\vec{a}_1\\|$. מכיוון $\\vec{a}_1\\neq\\vec{0}$, $\\|\\vec{a}_1\\|>0$ ו-$\\|\\vec{q}_1\\|=1$. ✓

**שלב אינדוקציה.** נניח $\\{\\vec{q}_1,\\ldots,\\vec{q}_{j-1}\\}$ אורתונורמלית עם אותה פרישה. הגדר $\\vec{u}_j = \\vec{a}_j - \\sum_{i<j}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i$.

**A: $\\vec{u}_j\\neq\\vec{0}$.** הסכום ב-$\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_{j-1}\\}$. אם $\\vec{u}_j=\\vec{0}$, אז $\\vec{a}_j$ קומבינציה לינארית של $\\vec{a}_i$ קודמים — סתירה לבלתי-תלות.

**B: $\\langle\\vec{q}_j,\\vec{q}_l\\rangle=0$ לכל $l<j$.** מניצול אורתונורמליות:
$$\\langle\\vec{u}_j,\\vec{q}_l\\rangle = \\langle\\vec{a}_j,\\vec{q}_l\\rangle - \\sum_{i<j}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\langle\\vec{q}_i,\\vec{q}_l\\rangle.$$
מכיוון $\\langle\\vec{q}_i,\\vec{q}_l\\rangle=\\delta_{il}$, הסכום מתכווץ ל-$\\langle\\vec{a}_j,\\vec{q}_l\\rangle$, ולכן $\\langle\\vec{u}_j,\\vec{q}_l\\rangle=0$. מכיוון $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$, מתקבל $\\langle\\vec{q}_j,\\vec{q}_l\\rangle=0$. ✓

**C: $\\|\\vec{q}_j\\|=1$** לפי ההגדרה ($\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$ ו-$\\vec{u}_j\\neq\\vec{0}$ משלב A).

**D (פרישה נשמרת):** $\\vec{q}_j$ הוא קומבינציה לא-אפסית של $\\vec{a}_j$ ו-$\\vec{q}_1,\\ldots,\\vec{q}_{j-1}$, ולכן $\\text{span}\\{\\vec{q}_1,\\ldots,\\vec{q}_j\\}=\\text{span}\\{\\vec{a}_1,\\ldots,\\vec{a}_j\\}$.

באינדוקציה, $\\{\\vec{q}_1,\\ldots,\\vec{q}_k\\}$ אורתונורמלית. $\\blacksquare$

**טיפ לבחינה:** שלב A (למה $\\vec{u}_j\\neq\\vec{0}$) הוא הקשר בין בלתי-תלות לגרם–שמידט מוצלח — הציגו אותו במפורש בכל שאלת הוכחה.

**מסקנה:** אם הקלט תלוי, $\\vec{u}_j=\\vec{0}$ לשלב כלשהו — האלגוריתם מסמן איזה וקטור מיותר; הורידו אותו והמשיכו עם השאר.

**למה אינדוקציה עובדת:** כל שלב מוסיף כיוון אורתונורמלי חדש אחד תוך שמירה על פרישת כל הוקטורים שעובדו — ההנחה האינדוקטיבית תואמת את מבנה האלגוריתם.""",
    },
    "method_guide": {
        "body_en_md": """**Gram–Schmidt algorithm:**
1. $\\vec{u}_1=\\vec{a}_1$; $\\vec{q}_1=\\vec{u}_1/\\|\\vec{u}_1\\|$.
2. For $j=2,\\ldots,k$: $\\vec{u}_j=\\vec{a}_j-\\displaystyle\\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i$; $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$.

**Projection onto subspace with ONB $\\{\\vec{q}_1,\\ldots,\\vec{q}_m\\}$:**
$$\\text{proj}_W\\vec{v}=\\sum_{i=1}^m\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i.$$

| Goal | Method | Key check |
|---|---|---|
| Project onto a single vector | $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$ | Residual $\\perp \\vec{u}$ |
| Project onto subspace with ONB | Sum of scalar projections | Need orthonormal basis first |
| Orthonormal basis from independent set | Gram–Schmidt | Subtract ALL prior $q_i$ before normalizing |
| Verify orthonormality | Check $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$ | Both dot products and norms |
| QR decomposition | $Q=[\\vec{q}_1,\\ldots,\\vec{q}_n]$; $R_{ij}=\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ for $i\\leq j$ | $A=QR$, $R$ upper triangular |

**Decision tree:** One direction → line formula. Subspace from basis → Gram–Schmidt if not already ON. Function space → use the given inner product (integral).""",
        "body_he_md": """**אלגוריתם גרם–שמידט:**
1. $\\vec{u}_1=\\vec{a}_1$; $\\vec{q}_1=\\vec{u}_1/\\|\\vec{u}_1\\|$.
2. ל-$j=2,\\ldots,k$: $\\vec{u}_j=\\vec{a}_j-\\sum_{i=1}^{j-1}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i$; $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$.

**הטלה על תת-מרחב עם ONB $\\{\\vec{q}_1,\\ldots,\\vec{q}_m\\}$:**
$$\\text{proj}_W\\vec{v}=\\sum_{i=1}^m\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i.$$

| מטרה | שיטה | בדיקה |
|---|---|---|
| הטלה על וקטור בודד | $\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$ | שארית $\\perp \\vec{u}$ |
| הטלה על תת-מרחב עם ONB | סכום הטלות סקלריות | צריך בסיס אורתונורמלי |
| בסיס-ON מקבוצה בלתי-תלויה | גרם–שמידט | חסרו **כל** $q_i$ קודם לפני נרמול |
| אימות אורתונורמליות | $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$ | גם מכפלות וגם נורמות |
| פירוק QR | $Q=[\\vec{q}_1,\\ldots,\\vec{q}_n]$; $R_{ij}=\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ | $A=QR$, $R$ משולשת עליונה |

**עץ החלטות:** כיוון יחיד → נוסחת קו. תת-מרחב מבסיס → גרם–שמידט אם לא ON. מרחב פונקציות → השתמשו במכפלה הפנימית הנתונה (אינטגרל).""",
    },
    "pitfall": {
        "body_en_md": """1. **Projecting onto a non-normalised vector.** Use $\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$, NOT $\\langle\\vec{v},\\vec{u}\\rangle\\vec{u}$ unless $\\|\\vec{u}\\|=1$. Forgetting the denominator is the single most common projection error on exams.

2. **Forgetting to subtract all previous projections.** In step $j$, subtract projections onto ALL of $\\vec{q}_1,\\ldots,\\vec{q}_{j-1}$, not just the most recent one. Skipping an earlier $\\vec{q}_i$ breaks orthogonality silently.

3. **Normalizing before orthogonalizing.** Gram–Schmidt requires: first subtract, then divide by $\\|\\vec{u}_j\\|$. Dividing $\\vec{a}_j$ first and then subtracting produces a set that is not orthogonal.

4. **Projecting onto a subspace without an ONB.** The formula $\\sum\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$ requires orthonormal $\\vec{q}_i$. For a general (non-ON) basis, run Gram–Schmidt first or solve a linear system.

5. **Applying Gram–Schmidt to a dependent set.** If some $\\vec{u}_j=\\vec{0}$, the input was linearly dependent. Drop that vector — continuing produces division by zero. Always check independence before starting.""",
        "body_he_md": """1. **הטלה על וקטור לא-מנורמל.** השתמשו ב-$\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$, לא $\\langle\\vec{v},\\vec{u}\\rangle\\vec{u}$ אלא אם $\\|\\vec{u}\\|=1$. שכחת המכנה היא טעות ההטלה הנפוצה ביותר בבחינות.

2. **שכחת חיסור כל ההטלות הקודמות.** בשלב $j$, חסרו הטלות על **כל** $\\vec{q}_1,\\ldots,\\vec{q}_{j-1}$, לא רק על האחרון. דילוג על $\\vec{q}_i$ קודם שובר אורתוגונליות בשקט.

3. **נרמול לפני אורתוגונליזציה.** גרם–שמידט דורש: קודם חיסור, אחר כך חלוקה ב-$\\|\\vec{u}_j\\|$. חלוקת $\\vec{a}_j$ תחילה ואז חיסור מייצרת קבוצה שאינה אורתוגונלית.

4. **הטלה על תת-מרחב ללא ONB.** הנוסחה $\\sum\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$ דורשת $\\vec{q}_i$ אורתונורמליים. לבסיס כללי — הריצו גרם–שמידט קודם או פתרו מערכת.

5. **גרם–שמידט על קבוצה תלויה.** אם $\\vec{u}_j=\\vec{0}$, הקלט תלוי לינארית. הורידו את הוקטור — המשך יגרום לחלוקה באפס. בדקו בלתי-תלות לפני שמתחילים.""",
    },
    "why_matters": {
        "body_en_md": """Inner product spaces unify geometry across all of linear algebra — from $\\mathbb{R}^n$ to function spaces used in physics and signal processing. Gram–Schmidt is the standard tool for building orthonormal bases, which turn hard projection problems into simple dot products.

**Connections in the knowledge graph:**
- `concept:la_vector_spaces` — independence ensures Gram–Schmidt succeeds.
- `concept:la_orthogonality` — orthogonal complements and QR decomposition.
- Least-squares regression — projecting data onto a model subspace.
- Fourier analysis — orthonormal trigonometric bases in $C[-\\pi,\\pi]$.

**Why it matters for exams:** Israeli university linear algebra courses routinely assign full Gram–Schmidt computations on 2–3 vectors, projection onto subspaces, and short proofs (Bessel, residual orthogonality). These problems test both computation and conceptual understanding of best approximation.""",
        "body_he_md": """מרחבי מכפלה פנימית מאחדים גאומטריה בכל האלגברה הלינארית — מ-$\\mathbb{R}^n$ ועד מרחבי פונקציות בפיזיקה ובעיבוד אותות. גרם–שמידט הוא הכלי הסטנדרטי לבניית בסיסים אורתונורמליים, שהופכים בעיות הטלה קשות למכפלות פנימיות פשוטות.

**קשרים בגרף הידע:**
- `concept:la_vector_spaces` — בלתי-תלות מבטיחה הצלחת גרם–שמידט.
- `concept:la_orthogonality` — משלימים אורתוגונליים ופירוק QR.
- רגרסיה בריבועים פחותים — הטלת נתונים על תת-מרחב מודל.
- אנליזת Fourier — בסיסים טrigonometric אורתונורמליים ב-$C[-\\pi,\\pi]$.

**למה זה חשוב לבחינות:** קורסי אלגברה לינארית באוניברסיטאות בישראל נותנים שגרה חישובי גרם–שמידט מלא על 2–3 וקטורים, הטלה על תת-מרחבים והוכחות קצרות (בסל, אורתוגונליות שארית). תרגילים אלה בודקים חישוב והבנה של קירוב מיטבי.""",
    },
    "before_exam": {
        "body_en_md": """**Formula sheet:**
- $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$ (single vector)
- $\\text{proj}_W\\vec{v}=\\sum_{i=1}^m\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$ (ONB for $W$)
- Gram–Schmidt: $\\vec{u}_j=\\vec{a}_j-\\sum_{i<j}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i$; $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$
- Bessel: $\\sum|\\langle\\vec{v},\\vec{q}_i\\rangle|^2\\leq\\|\\vec{v}\\|^2$; Parseval = equality for full ONB
- Cauchy–Schwarz: $|\\langle u,v\\rangle|\\leq\\|u\\|\\|v\\|$

**What Israeli university exams emphasise:**
- Full Gram–Schmidt on 2 or 3 vectors in $\\mathbb{R}^3$.
- Projecting onto a subspace given by a spanning set (Gram–Schmidt first).
- Proving orthonormality of a given set (integrals in function spaces).
- Short proofs: residual is orthogonal, Bessel inequality, Gram–Schmidt termination.

**Exam tip:** After each Gram–Schmidt step, verify $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ — catches sign errors early.""",
        "body_he_md": """**גיליון נוסחאות:**
- $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$ (וקטור בודד)
- $\\text{proj}_W\\vec{v}=\\sum\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$ (ONB ל-$W$)
- גרם–שמידט: $\\vec{u}_j=\\vec{a}_j-\\sum_{i<j}\\langle\\vec{a}_j,\\vec{q}_i\\rangle\\vec{q}_i$; $\\vec{q}_j=\\vec{u}_j/\\|\\vec{u}_j\\|$
- בסל: $\\sum|\\langle\\vec{v},\\vec{q}_i\\rangle|^2\\leq\\|\\vec{v}\\|^2$; פרסבל = שוויון ל-ONB מלא
- קושי–שוורץ: $|\\langle u,v\\rangle|\\leq\\|u\\|\\|v\\|$

**מה בחינות ישראליות מדגישות:**
- גרם–שמידט מלא על 2–3 וקטורים ב-$\\mathbb{R}^3$.
- הטלה על תת-מרחב מקבוצת פרישה (גרם–שמידט קודם).
- הוכחת אורתונורמליות (אינטגרלים במרחבי פונקציות).
- הוכחות קצרות: שארית אורתוגונלית, בסל, סיום גרם–שמידט.

**טיפ:** לאחר כל שלב גרם–שמידט, אמתו $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ — תופס טעויות סימן מוקדם.""",
    },
    "summary": {
        "body_en_md": """- An **inner product space** generalises angle and length via symmetry, linearity, and positive definiteness.
- An **orthonormal set** satisfies $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$ and is always linearly independent.
- **Projection:** $\\text{proj}_W\\vec{v}=\\sum\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$ with ONB; the residual is $\\perp W$ and gives best approximation.
- **Gram–Schmidt:** converts any independent set to orthonormal with the same span; terminates because $\\vec{u}_j\\neq\\vec{0}$.
- **Bessel / Parseval:** $\\sum|\\langle\\vec{v},\\vec{q}_i\\rangle|^2\\leq\\|\\vec{v}\\|^2$; equality for full ONB.

**Takeaway:** Given vectors or a spanning set, you should now project, run Gram–Schmidt, verify orthonormality, and prove key projection identities.""",
        "body_he_md": """- **מרחב מכפלה פנימית** — מושג מוכלל של זווית ואורך: סימטריה, לינאריות, חיוביות.
- **קבוצה אורתונורמלית:** $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=\\delta_{ij}$; תמיד בלתי-תלויה.
- **הטלה:** $\\text{proj}_W\\vec{v}=\\sum\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$; השארית $\\perp W$ ונותנת קירוב מיטבי.
- **גרם–שמידט:** ממיר קבוצה בלתי-תלויה לאורתונורמלית עם אותה פרישה; $\\vec{u}_j\\neq\\vec{0}$ מבטיח סיום.
- **בסל / פרסבל:** $\\sum|\\langle\\vec{v},\\vec{q}_i\\rangle|^2\\leq\\|\\vec{v}\\|^2$; שוויון ל-ONB מלא.

**מסקנה:** נתונים וקטורים או קבוצת פרישה — אתם אמורים להטיל, להריץ גרם–שמידט, לאמת אורתונורמליות ולהוכיח זהויות הטלה מרכזיות.""",
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": """### Move 1: Formula
$\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\langle\\vec{u},\\vec{u}\\rangle}\\vec{u}$ with $\\vec{v}=(2,3,1)$, $\\vec{u}=(1,1,0)$.

### Move 2: Inner products
$\\langle\\vec{v},\\vec{u}\\rangle=2+3+0=5$, $\\langle\\vec{u},\\vec{u}\\rangle=1+1=2$.

### Move 3: Result
$$\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{5}{2}(1,1,0)=\\left(\\frac{5}{2},\\frac{5}{2},0\\right).$$

### Move 4: Verify
Residual $(2,3,1)-\\frac{5}{2}(1,1,0)=(-\\frac{1}{2},\\frac{1}{2},1)$. Dot with $\\vec{u}$: $-\\frac{1}{2}+\\frac{1}{2}+0=0$. ✓""",
        "checkpoint_solution_he": """### צעד 1: נוסחה
$\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\langle\\vec{u},\\vec{u}\\rangle}\\vec{u}$ עם $\\vec{v}=(2,3,1)$, $\\vec{u}=(1,1,0)$.

### צעד 2: מכפלות פנימיות
$\\langle\\vec{v},\\vec{u}\\rangle=5$, $\\langle\\vec{u},\\vec{u}\\rangle=2$.

### צעד 3: תוצאה
$$\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{5}{2}(1,1,0)=\\left(\\frac{5}{2},\\frac{5}{2},0\\right).$$

### צעד 4: אימות
שארית $(-\\frac{1}{2},\\frac{1}{2},1)$. מכפלה עם $\\vec{u}$: $0$. ✓""",
    },
    {
        "checkpoint_solution_en": """### Move 1: $q_1$
$\\vec{a}_1=(1,0)$ is already a unit vector: $\\vec{q}_1=(1,0)$.

### Move 2: Orthogonalize $\\vec{a}_2$
$\\langle(1,1),(1,0)\\rangle=1$. $\\vec{u}_2=(1,1)-1\\cdot(1,0)=(0,1)$. $\\vec{q}_2=(0,1)$.

### Move 3: Result
ONB: $\\{(1,0),(0,1)\\}$ — the standard basis of $\\mathbb{R}^2$.

**Note:** When the first vector is already unit length, skip normalization in step 1 but still subtract its projection in step 2.""",
        "checkpoint_solution_he": """### צעד 1: $q_1$
$\\vec{a}_1=(1,0)$ כבר באורך 1: $\\vec{q}_1=(1,0)$.

### צעד 2: אורתוגונליזציה של $\\vec{a}_2$
$\\langle(1,1),(1,0)\\rangle=1$. $\\vec{u}_2=(0,1)$. $\\vec{q}_2=(0,1)$.

### צעד 3: תוצאה
ONB: $\\{(1,0),(0,1)\\}$ — הבסיס הסטנדרטי של $\\mathbb{R}^2$.

**הערה:** כשהוקטור הראשון כבר יחידה, דלגו על נרמול בשלב 1 אך חסרו את ההטלה שלו בשלב 2.""",
    },
]

EXERCISE_SET_BODY = {
    "body_en_md": """Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.

These drills cover projection onto lines and subspaces, verifying orthonormality (including function spaces with integrals), full Gram–Schmidt computations, and short proofs (Bessel, residual orthogonality, isometry). After each projection, check that the residual is orthogonal to the subspace.""",
    "body_he_md": """פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.

התרגילים מכסים הטלה על קווים ותת-מרחבים, אימות אורתונורמליות (כולל מרחבי פונקציות עם אינטגרלים), חישובי גרם–שמידט מלאים והוכחות קצרות (בסל, אורתוגונליות שארית, אizometry). אחרי כל הטלה, בדקו שהשארית אורתוגונלית לתת-מרחב.""",
}

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1:** $\\langle\\vec{v},\\vec{u}\\rangle=3$, $\\|\\vec{u}\\|^2=1$.\n\n**Step 2:** $\\text{proj}_{\\vec{u}}\\vec{v}=3(1,0)=(3,0)$.\n\n**Verify:** $(3,4)-(3,0)=(0,4)\\perp(1,0)$. ✓",
        "solution_he": "**צעד 1:** $\\langle\\vec{v},\\vec{u}\\rangle=3$, $\\|\\vec{u}\\|^2=1$.\n\n**צעד 2:** $\\text{proj}_{\\vec{u}}\\vec{v}=(3,0)$.\n\n**אימות:** $(0,4)\\perp(1,0)$. ✓",
    },
    "e2": {
        "solution_en": "**Step 1:** Dot product: $\\frac{1}{2}-\\frac{1}{2}=0$ ✓.\n\n**Step 2:** Each norm: $\\sqrt{1/2+1/2}=1$ ✓.\n\n**Conclusion:** The set is orthonormal.",
        "solution_he": "**צעד 1:** מכפלה פנימית: $\\frac{1}{2}-\\frac{1}{2}=0$ ✓.\n\n**צעד 2:** כל נורמה: $\\sqrt{1/2+1/2}=1$ ✓.\n\n**מסקנה:** הקבוצה אורתונורמלית.",
    },
    "e3": {
        "solution_en": "**Step 1:** Single vector: $\\vec{u}_1=(3,4)$, $\\|\\vec{u}_1\\|=5$.\n\n**Step 2:** $\\vec{q}_1=(3/5,4/5)$.\n\n**Verify:** $\\|\\vec{q}_1\\|=\\sqrt{9/25+16/25}=1$. ✓",
        "solution_he": "**צעד 1:** וקטור בודד: $\\|\\vec{u}_1\\|=5$.\n\n**צעד 2:** $\\vec{q}_1=(3/5,4/5)$.\n\n**אימות:** $\\|\\vec{q}_1\\|=1$. ✓",
    },
    "e4": {
        "solution_en": "**Step 1:** $(1,0,0)$ and $(0,1,0)$ are already orthonormal.\n\n**Step 2:** $\\text{proj}_W\\vec{v}=1\\cdot(1,0,0)+2\\cdot(0,1,0)+0\\cdot(\\ldots)=(1,2,0)$.\n\n**Verify:** Residual $(0,0,3)\\perp$ both basis vectors. ✓",
        "solution_he": "**צעד 1:** $(1,0,0)$ ו-$(0,1,0)$ כבר אורתונורמליים.\n\n**צעד 2:** $\\text{proj}_W\\vec{v}=(1,2,0)$.\n\n**אימות:** שארית $(0,0,3)$ ניצבת לשני וקטורי הבסיס. ✓",
    },
    "e5": {
        "solution_en": "**Step 1:** $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1)$.\n\n**Step 2:** $\\langle(1,-1),\\vec{q}_1\\rangle=0$ already — no subtraction needed.\n\n**Step 3:** $\\vec{q}_2=\\frac{1}{\\sqrt{2}}(1,-1)$. ONB complete.",
        "solution_he": "**צעד 1:** $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1)$.\n\n**צעד 2:** $\\langle(1,-1),\\vec{q}_1\\rangle=0$ — אין צורך בחיסור.\n\n**צעד 3:** $\\vec{q}_2=\\frac{1}{\\sqrt{2}}(1,-1)$. ONB הושלם.",
    },
    "e6": {
        "solution_en": "**Step 1:** Gram–Schmidt on $W$: $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0)$, $\\vec{q}_2=\\frac{1}{\\sqrt{6}}(-1,1,2)$.\n\n**Step 2:** $\\text{proj}_W\\vec{b}=\\langle\\vec{b},\\vec{q}_1\\rangle\\vec{q}_1+\\langle\\vec{b},\\vec{q}_2\\rangle\\vec{q}_2=(2/3,4/3,2/3)$.",
        "solution_he": "**צעד 1:** גרם–שמידט על $W$: $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0)$, $\\vec{q}_2=\\frac{1}{\\sqrt{6}}(-1,1,2)$.\n\n**צעד 2:** $\\text{proj}_W\\vec{b}=(2/3,4/3,2/3)$.",
    },
    "e7": {
        "solution_en": "**Step 1:** With $f_0=1/\\sqrt{2\\pi}$: $\\|f_0\\|^2=\\int_{-\\pi}^\\pi \\frac{1}{2\\pi}dx=1$.\n\n**Step 2:** Cross terms: $\\langle f_0,\\cos/\\sqrt\\pi\\rangle=0$ (odd integrand), $\\langle\\cos,\\sin\\rangle/\\pi=0$.\n\n**Step 3:** Norms of $\\cos/\\sqrt\\pi$ and $\\sin/\\sqrt\\pi$ both equal 1. ✓",
        "solution_he": "**צעד 1:** $f_0=1/\\sqrt{2\\pi}$: $\\|f_0\\|^2=1$.\n\n**צעד 2:** מכפלות צולבות: $\\langle f_0,\\cos/\\sqrt\\pi\\rangle=0$, $\\langle\\cos,\\sin\\rangle=0$.\n\n**צעד 3:** נורמות של $\\cos/\\sqrt\\pi$ ו-$\\sin/\\sqrt\\pi$ שוות 1. ✓",
    },
    "e8": {
        "solution_en": "**Step 1:** $q_1=1/\\sqrt{2}$. $\\langle x,q_1\\rangle=0$ (odd), so $q_2=\\sqrt{3/2}\\,x$.\n\n**Step 2:** $u_3=x^2-1/3$, $\\|u_3\\|^2=8/45$, $q_3=\\sqrt{45/8}(x^2-1/3)$.\n\n**Note:** Proportional to Legendre polynomials $P_0,P_1,P_2$.",
        "solution_he": "**צעד 1:** $q_1=1/\\sqrt{2}$. $\\langle x,q_1\\rangle=0$, $q_2=\\sqrt{3/2}\\,x$.\n\n**צעד 2:** $u_3=x^2-1/3$, $q_3=\\sqrt{45/8}(x^2-1/3)$.\n\n**הערה:** פרופורציונלי לפולינומי לז'נדר $P_0,P_1,P_2$.",
    },
    "e9": {
        "solution_en": "**Step 1:** Let $\\vec{p}=\\sum_i\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$.\n\n**Step 2:** By Pythagoras: $\\|\\vec{v}\\|^2=\\|\\vec{p}\\|^2+\\|\\vec{v}-\\vec{p}\\|^2\\geq\\|\\vec{p}\\|^2=\\sum_i|\\langle\\vec{v},\\vec{q}_i\\rangle|^2$. $\\blacksquare$",
        "solution_he": "**צעד 1:** $\\vec{p}=\\sum_i\\langle\\vec{v},\\vec{q}_i\\rangle\\vec{q}_i$.\n\n**צעד 2:** פיתגורס: $\\|\\vec{v}\\|^2=\\|\\vec{p}\\|^2+\\|\\vec{v}-\\vec{p}\\|^2\\geq\\|\\vec{p}\\|^2=\\sum|\\langle\\vec{v},\\vec{q}_i\\rangle|^2$. $\\blacksquare$",
    },
    "e10": {
        "solution_en": "**Step 1:** For $\\vec{w}=\\sum_j c_j\\vec{q}_j\\in W$:\n\n**Step 2:** $\\langle\\vec{v}-\\text{proj}_W\\vec{v},\\vec{w}\\rangle=\\sum_j c_j(\\langle\\vec{v},\\vec{q}_j\\rangle-\\langle\\vec{v},\\vec{q}_j\\rangle)=0$. $\\blacksquare$",
        "solution_he": "**צעד 1:** לכל $\\vec{w}=\\sum c_j\\vec{q}_j\\in W$:\n\n**צעד 2:** $\\langle\\vec{v}-\\text{proj}_W\\vec{v},\\vec{w}\\rangle=\\sum c_j(\\langle\\vec{v},\\vec{q}_j\\rangle-\\langle\\vec{v},\\vec{q}_j\\rangle)=0$. $\\blacksquare$",
    },
    "e11": {
        "solution_en": "**Step 1:** $\\|A\\vec{x}\\|^2=(A\\vec{x})^T(A\\vec{x})=\\vec{x}^TA^TA\\vec{x}$.\n\n**Step 2:** Since $A^TA=I$: $\\|A\\vec{x}\\|^2=\\vec{x}^T\\vec{x}=\\|\\vec{x}\\|^2$. Take square roots. $\\blacksquare$",
        "solution_he": "**צעד 1:** $\\|A\\vec{x}\\|^2=\\vec{x}^TA^TA\\vec{x}$.\n\n**צעד 2:** מכיוון $A^TA=I$: $\\|A\\vec{x}\\|^2=\\|\\vec{x}\\|^2$. שורשים. $\\blacksquare$",
    },
    "e12": {
        "solution_en": "**Step 1:** $(\\det Q)^2=\\det(Q^TQ)=\\det(I)=1$, so $\\det Q=\\pm1$.\n\n**Step 2:** $\\langle Q\\vec{u},Q\\vec{v}\\rangle=\\vec{u}^TQ^TQ\\vec{v}=\\langle\\vec{u},\\vec{v}\\rangle$. $\\blacksquare$",
        "solution_he": "**צעד 1:** $(\\det Q)^2=1$, $\\det Q=\\pm1$.\n\n**צעד 2:** $\\langle Q\\vec{u},Q\\vec{v}\\rangle=\\vec{u}^TQ^TQ\\vec{v}=\\langle\\vec{u},\\vec{v}\\rangle$. $\\blacksquare$",
    },
}

EXPLANATIONS = [
    (
        "**Why this is correct:**\nProject $\\vec{v}=(3,4)$ onto $\\vec{u}=(1,0)$ using $\\text{proj}_{\\vec{u}}\\vec{v}=\\frac{\\langle\\vec{v},\\vec{u}\\rangle}{\\|\\vec{u}\\|^2}\\vec{u}$. Here $\\langle\\vec{v},\\vec{u}\\rangle=3$ and $\\|\\vec{u}\\|^2=1$, giving $(3,0)$. The $x$-component of $\\vec{v}$ is extracted; the $y$-component $(0,4)$ is orthogonal to $\\vec{u}$.\n\n**How to think about it:**\nProjection onto a coordinate axis is the simplest case: dot with the axis vector, divide by its squared length, multiply back. When $\\vec{u}$ is already a unit vector on an axis, the answer is just the corresponding coordinate.\n\n**Common slip:**\nUsing $\\langle\\vec{v},\\vec{u}\\rangle\\vec{u}$ without dividing by $\\|\\vec{u}\\|^2$, or projecting onto $(0,1)$ instead of $(1,0)$ and getting $(0,4)$.\n\n**Exam tip:**\nAfter computing the projection, subtract it from $\\vec{v}$ and verify the residual is orthogonal to $\\vec{u}$ — one dot product catches most errors.",
        "**למה זה נכון:**\nהטלת $\\vec{v}=(3,4)$ על $\\vec{u}=(1,0)$: $\\langle\\vec{v},\\vec{u}\\rangle=3$, $\\|\\vec{u}\\|^2=1$, ולכן $(3,0)$. רכיב $x$ נחלץ; $(0,4)$ ניצב ל-$\\vec{u}$.\n\n**איך לחשוב על זה:**\nהטלה על ציר קואורדינטות היא המקרה הפשוט: מכפלה פנימית, חלוקה ב-$\\|\\vec{u}\\|^2$, כפל חזרה. כש-$\\vec{u}$ יחידה על ציר, התשובה היא הקואורדינטה המתאימה.\n\n**טעות נפוצה:**\nשימוש ב-$\\langle\\vec{v},\\vec{u}\\rangle\\vec{u}$ בלי חלוקה, או הטלה על $(0,1)$ במקום $(1,0)$.\n\n**טיפ לבחינה:**\nאחרי ההטלה, חסרו מ-$\\vec{v}$ ואמתו שהשארית ניצבת ל-$\\vec{u}$ — מכפלה פנימית אחת תופסת רוב הטעויות.",
    ),
    (
        "**Why this is correct:**\nAn orthonormal set requires $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ for $i\\neq j$ and $\\|\\vec{q}_i\\|=1$. Dot product: $\\frac{1}{2}-\\frac{1}{2}=0$ ✓. Each norm: $\\sqrt{1/2+1/2}=1$ ✓. Both conditions hold, so the set is orthonormal.\n\n**How to think about it:**\nVerification problems always check two things separately: all cross inner products are zero, and each vector has unit length. Do not stop after checking only one pair or only the norms.\n\n**Common slip:**\nChecking only orthogonality and forgetting unit length, or computing $\\langle\\vec{q}_1,\\vec{q}_2\\rangle$ incorrectly by expanding $(1/\\sqrt{2})^2+(1/\\sqrt{2})(-1/\\sqrt{2})$ with a sign error.\n\n**Exam tip:**\nWrite a small table: row for dot products (off-diagonal = 0), row for norms (= 1). Examiners expect both checks explicitly stated.",
        "**למה זה נכון:**\nקבוצה אורתונורמלית דורשת $\\langle\\vec{q}_i,\\vec{q}_j\\rangle=0$ ל-$i\\neq j$ ו-$\\|\\vec{q}_i\\|=1$ לכל $i$. כאן מכפלה פנימית: $\\frac{1}{2}-\\frac{1}{2}=0$ ✓. כל נורמה: $\\sqrt{1/2+1/2}=\\sqrt{1}=1$ ✓. שני התנאים מתקיימים, ולכן הקבוצה אורתונורמלית.\n\n**איך לחשוב על זה:**\nבאימות בודקים שני דברים בנפרד: מכפלות צולבות שוות לאפס, וכל וקטור באורך יחידה. אל תעצרו אחרי בדיקה של זוג אחד בלבד או אחרי נורמות בלבד.\n\n**טעות נפוצה:**\nבדיקת אורתוגונליות בלבד בלי נורמות, או טעות סימן בחישוב $\\langle\\vec{q}_1,\\vec{q}_2\\rangle$ כשמרחיבים $(1/\\sqrt{2})^2+(1/\\sqrt{2})(-1/\\sqrt{2})$.\n\n**טיפ לבחינה:**\nכתבו טבלה קצרה: שורה למכפלות (מחוץ לאלכסון = 0), שורה לנורמות (= 1). בוחנים מצפים לשתי הבדיקות מפורשות.",
    ),
    (
        "**Why this is correct:**\nGram–Schmidt on a single vector $\\{(3,4)\\}$ has only step 1: normalize. $\\|(3,4)\\|=5$, so $\\vec{q}_1=(3/5,4/5)$. No subtraction is needed because there are no prior directions.\n\n**How to think about it:**\nGram–Schmidt with one vector degenerates to \"divide by the norm.\" The output is always a unit vector pointing in the same direction as the input. Verify $\\|\\vec{q}_1\\|=1$ by computing $(3/5)^2+(4/5)^2=1$.\n\n**Common slip:**\nReturning $(3,4)$ without normalizing, or dividing by 5 incorrectly (e.g., $(3/25,4/25)$). Another error: trying to subtract a projection when there is no prior $\\vec{q}_i$.\n\n**Exam tip:**\nWhen the input is a single vector, write \"Step 1 only: normalize\" — this signals you understand the algorithm structure and saves time.",
        "**למה זה נכון:**\nגרם–שמידט על $\\{(3,4)\\}$ כולל רק שלב 1: נרמול. $\\|(3,4)\\|=\\sqrt{9+16}=5$, ולכן $\\vec{q}_1=(3/5,4/5)$. אין צורך בחיסור הטלות כי אין כיוונים $\\vec{q}_i$ קודמים שעליהם לחסר.\n\n**איך לחשוב על זה:**\nגרם–שמידט עם וקטור יחיד מתכווץ ל\"חלק בנורמה\". הפלט תמיד וקטור יחידה באותו כיוון. אמתו $\\|\\vec{q}_1\\|=1$ על ידי $(3/5)^2+(4/5)^2=9/25+16/25=1$.\n\n**טעות נפוצה:**\nהחזרת $(3,4)$ בלי נרמול, חלוקה שגויה (למשל $(3/25,4/25)$), או ניסיון לחסר הטלה כשאין $\\vec{q}_i$ קודם.\n\n**טיפ לבחינה:**\nכשיש וקטור יחיד, כתבו \"שלב 1 בלבד: נרמול\" — מראה שאתם מבינים את מבנה האלגוריתם וחוסך זמן יקר בבחינה.",
    ),
    (
        "**Why this is correct:**\nThe spanning vectors $(1,0,0)$ and $(0,1,0)$ are already an orthonormal basis for the $xy$-plane. Projection is $\\text{proj}_W\\vec{v}=\\langle\\vec{v},(1,0,0)\\rangle(1,0,0)+\\langle\\vec{v},(1,0,0)\\rangle(0,1,0)=1\\cdot(1,0,0)+2\\cdot(0,1,0)=(1,2,0)$. The $z$-component drops out.\n\n**How to think about it:**\nBefore running Gram–Schmidt, check whether the given basis is already orthonormal. Standard basis vectors (or obvious permutations) let you project by reading off coordinates directly.\n\n**Common slip:**\nRunning unnecessary Gram–Schmidt and introducing arithmetic errors, or projecting onto $(0,0,1)$ and including the $z$-component in the answer.\n\n**Exam tip:**\nWhen the subspace is $\\text{span}\\{e_1,e_2\\}$ or similar, the projection keeps the first two coordinates and zeros the rest — state this pattern explicitly.",
        "**למה זה נכון:**\nוקטורי הפרישה $(1,0,0)$ ו-$(0,1,0)$ כבר מהווים ONB למישור $xy$. ההטלה: $\\text{proj}_W\\vec{v}=\\langle\\vec{v},(1,0,0)\\rangle(1,0,0)+\\langle\\vec{v},(0,1,0)\\rangle(0,1,0)=1\\cdot(1,0,0)+2\\cdot(0,1,0)=(1,2,0)$. רכיב $z$ של $\\vec{v}=(1,2,3)$ נופל — הוא ניצב למישור.\n\n**איך לחשוב על זה:**\nלפני גרם–שמידט, בדקו אם הבסיס הנתון כבר אורתונורמלי. וקטורי בסיס סטנדרטיים (או תמורות ברורות) מאפשרים הטלה ישירה על ידי קריאת קואורדינטות.\n\n**טעות נפוצה:**\nהרצת גרם–שמידט מיותרת עם טעויות חישוב, או הכללת רכיב $z$ בתשובה כשההטלה על מישור $xy$.\n\n**טיפ לבחינה:**\nכש-$W=\\text{span}\\{e_1,e_2\\}$ או דומה, ההטלה שומרת שני קואורדינטות ראשונות ומאפסת את השאר — ציינו דפוס זה במפורש לפני שמחשבים.",
    ),
    (
        "**Why this is correct:**\n$\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1)$. For $\\vec{a}_2=(1,-1)$: $\\langle\\vec{a}_2,\\vec{q}_1\\rangle=\\frac{1-1}{\\sqrt{2}}=0$, so $\\vec{u}_2=(1,-1)$ unchanged. Then $\\vec{q}_2=\\frac{1}{\\sqrt{2}}(1,-1)$. The input vectors were already orthogonal — Gram–Schmidt only normalizes.\n\n**How to think about it:**\nWhen $\\langle\\vec{a}_2,\\vec{q}_1\\rangle=0$, the subtraction step is trivial. Recognizing pre-orthogonal inputs saves computation and reduces error risk. Always compute the inner product before subtracting.\n\n**Common slip:**\nSubtracting a non-zero projection when the vectors are already orthogonal, or forgetting to normalize $\\vec{u}_2$ after finding it equals $(1,-1)$.\n\n**Exam tip:**\nIf the dot product $\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ equals zero, write \"already orthogonal — skip subtraction\" and proceed directly to normalization.",
        "**למה זה נכון:**\n$\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1)$. עבור $\\vec{a}_2=(1,-1)$: $\\langle\\vec{a}_2,\\vec{q}_1\\rangle=\\frac{1-1}{\\sqrt{2}}=0$, ולכן $\\vec{u}_2=(1,-1)$ ללא שינוי. אז $\\vec{q}_2=\\frac{1}{\\sqrt{2}}(1,-1)$. הקלט כבר אורתוגונלי — גרם–שמידט רק מנרמל.\n\n**איך לחשוב על זה:**\nכש-$\\langle\\vec{a}_2,\\vec{q}_1\\rangle=0$, שלב החיסור trivial. זיהוי קלט אורתוגונלי חוסך חישוב ומפחית סיכון לטעויות. תמיד חשבו את המכפלה הפנימית לפני שמחסרים.\n\n**טעות נפוצה:**\nחיסור הטלה לא-אפסית כשהוקטורים כבר ניצבים, או שכחת נרמול $\\vec{u}_2=(1,-1)$ לאחר שמצאתם אותו.\n\n**טיפ לבחינה:**\nאם $\\langle\\vec{a}_j,\\vec{q}_i\\rangle=0$, כתבו \"כבר אורתוגונלי — דלגו על חיסור\" והמשיכו ישירות לנרמול — זה מראה הבנה ולא מבזבז זמן.",
    ),
    (
        "**Why this is correct:**\nThe spanning set is not orthonormal, so Gram–Schmidt first: $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0)$, $\\vec{q}_2=\\frac{1}{\\sqrt{6}}(-1,1,2)$. Then $\\text{proj}_W\\vec{b}=\\langle\\vec{b},\\vec{q}_1\\rangle\\vec{q}_1+\\langle\\vec{b},\\vec{q}_2\\rangle\\vec{q}_2=(2/3,4/3,2/3)$. This is the closest point in $W$ to $(1,1,1)$.\n\n**How to think about it:**\nSubspace projection always follows: (1) build ONB via Gram–Schmidt if needed, (2) sum $\\langle\\vec{b},\\vec{q}_i\\rangle\\vec{q}_i$. Never apply the sum formula to a non-ON basis.\n\n**Common slip:**\nUsing the raw spanning vectors in the projection sum without normalizing or orthogonalizing first. Another error: arithmetic mistakes in the Gram–Schmidt step that propagate to the final projection.\n\n**Exam tip:**\nLabel your work \"Step A: ONB\" and \"Step B: project\" — examiners award separate marks for each phase.",
        "**למה זה נכון:**\nקבוצת הפרישה $\\{(1,1,0),(0,1,1)\\}$ אינה ON — קודם גרם–שמידט: $\\vec{q}_1=\\frac{1}{\\sqrt{2}}(1,1,0)$, $\\vec{q}_2=\\frac{1}{\\sqrt{6}}(-1,1,2)$. אז $\\text{proj}_W\\vec{b}=\\langle\\vec{b},\\vec{q}_1\\rangle\\vec{q}_1+\\langle\\vec{b},\\vec{q}_2\\rangle\\vec{q}_2=(2/3,4/3,2/3)$ — הנקודה הקרובה ביותר ב-$W$ ל-$(1,1,1)$.\n\n**איך לחשוב על זה:**\nהטלה על תת-מרחב תמיד: (1) בניית ONB בגרם–שמידט אם צריך, (2) סכום $\\langle\\vec{b},\\vec{q}_i\\rangle\\vec{q}_i$. לעולם אל תשתמשו בנוסחת הסכום על בסיס לא-אורתונורמלי.\n\n**טעות נפוצה:**\nסכום הטלות על וקטורי פרישה גולמיים, או טעויות חישוב בגרם–שמידט שמסתננות לתשובה הסופית.\n\n**טיפ לבחינה:**\nסמנו \"שלב א: ONB\" ו\"שלב ב: הטלה\" — בוחנים נותנים נקודות נפרדות לכל שלב, וסימון ברור עוזר לקבל נקודות חלקיות.",
    ),
    (
        "**Why this is correct:**\nWith $f_0=1/\\sqrt{2\\pi}$: $\\|f_0\\|^2=\\int_{-\\pi}^\\pi \\frac{1}{2\\pi}dx=1$. Cross terms like $\\langle f_0,\\cos/\\sqrt\\pi\\rangle$ vanish because $\\int_{-\\pi}^\\pi\\cos x\\,dx=0$. Similarly $\\int_{-\\pi}^\\pi\\sin x\\cos x\\,dx=0$ (odd integrand). Norms of $\\cos/\\sqrt\\pi$ and $\\sin/\\sqrt\\pi$ both equal 1 via $\\int_{-\\pi}^\\pi\\cos^2 x\\,dx=\\pi$.\n\n**How to think about it:**\nIn function spaces, orthonormality is verified by integrals. Exploit symmetry: even/odd integrands over $[-\\pi,\\pi]$, and standard integrals of $\\sin^2$ and $\\cos^2$.\n\n**Common slip:**\nWrong normalization constant (using $1/\\sqrt{2}$ instead of $1/\\sqrt{2\\pi}$ for the constant function), or forgetting to divide by $\\pi$ when computing $\\|\\cos/\\sqrt\\pi\\|$.\n\n**Exam tip:**\nMemorize $\\int_{-\\pi}^\\pi 1\\,dx=2\\pi$ and $\\int_{-\\pi}^\\pi\\cos^2 x\\,dx=\\pi$ — they appear in every Fourier orthonormality problem.",
        "**למה זה נכון:**\n$f_0=1/\\sqrt{2\\pi}$: $\\|f_0\\|^2=\\int_{-\\pi}^\\pi \\frac{1}{2\\pi}dx=1$. מכפלות צולבות כמו $\\langle f_0,\\cos/\\sqrt\\pi\\rangle$ מתאפסות כי $\\int_{-\\pi}^\\pi\\cos x\\,dx=0$. גם $\\int_{-\\pi}^\\pi\\sin x\\cos x\\,dx=0$ (אינטגרנד אי-זוגי). נורמות $\\cos/\\sqrt\\pi$ ו-$\\sin/\\sqrt\\pi$ שוות 1.\n\n**איך לחשוב על זה:**\nבמרחבי פונקציות, אורתונורמליות = אינטגרלים. נצלו סימטריה: אינטגרנדים זוגיים/אי-זוגיים על $[-\\pi,\\pi]$, ואינטגרלים סטנדרטיים של $\\sin^2,\\cos^2$.\n\n**טעות נפוצה:**\nקבוע נרמול שגוי ($1/\\sqrt{2}$ במקום $1/\\sqrt{2\\pi}$), או שכחת חלוקה ב-$\\pi$ בחישוב $\\|\\cos/\\sqrt\\pi\\|$.\n\n**טיפ לבחינה:**\nשיננו $\\int_{-\\pi}^\\pi 1\\,dx=2\\pi$ ו-$\\int_{-\\pi}^\\pi\\cos^2 x\\,dx=\\pi$ — מופיע בכל בעיית אורתונורמליות של Fourier בבחינות אוניברסיטאיות בישראל.",
    ),
    (
        "**Why this is correct:**\n$q_1=1/\\sqrt{2}$ (constant on $[-1,1]$). $\\langle x,q_1\\rangle=0$ since $x$ is odd. So $q_2=\\sqrt{3/2}\\,x$. For $x^2$: subtract its projection onto $q_1$ to get $u_3=x^2-1/3$, then normalize to $q_3=\\sqrt{45/8}(x^2-1/3)$. These match Legendre polynomials — orthogonal by construction.\n\n**How to think about it:**\nGram–Schmidt on polynomials with $\\langle p,q\\rangle=\\int_{-1}^1 pq\\,dx$ exploits parity: odd × even integrals are zero. Compute each $\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ as a definite integral carefully.\n\n**Common slip:**\nEvaluating $\\int_{-1}^1 x\\,dx$ as non-zero, or arithmetic errors in $\\int_{-1}^1 x^2/\\sqrt{2}\\,dx=2/(3\\sqrt{2})$. Another trap: normalizing before subtracting all prior projections.\n\n**Exam tip:**\nOn polynomial Gram–Schmidt with this inner product, the results are always proportional to $P_0,P_1,P_2$ — use this as a sanity check on your final $q_3$.",
        "**למה זה נכון:**\n$q_1=1/\\sqrt{2}$ (קבוע על $[-1,1]$). $\\langle x,q_1\\rangle=0$ כי $x$ אי-זוגי. $q_2=\\sqrt{3/2}\\,x$. ל-$x^2$: חסרו הטלה על $q_1$ → $u_3=x^2-1/3$, נרמול → $q_3=\\sqrt{45/8}(x^2-1/3)$. אלה פרופורציונליים לפולינומי לז'נדר — אורתוגונליים בבנייה.\n\n**איך לחשוב על זה:**\nגרם–שמידט על פולינומים עם $\\langle p,q\\rangle=\\int_{-1}^1 pq\\,dx$ — נצלו זוגיות: אינטגרל של זוגי×אי-זוגי = 0. חשבו כל $\\langle\\vec{a}_j,\\vec{q}_i\\rangle$ כאינטגרל מסוים בזהירות.\n\n**טעות נפוצה:**\n$\\int_{-1}^1 x\\,dx\\neq 0$, טעויות ב-$\\int_{-1}^1 x^2/\\sqrt{2}\\,dx$, או נרמול לפני חיסור כל ההטלות הקודמות.\n\n**טיפ לבחינה:**\nעם מכפלה פנימית זו, התוצאות פרופורציונליות ל-$P_0,P_1,P_2$ — השתמשו בזה לבדיקת $q_3$ לפני שמסיימים.",
    ),
]

