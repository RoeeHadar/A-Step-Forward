#!/usr/bin/env python3
"""Expand complex_numbers.json to MIN_WORDS depth gates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSON = ROOT / "scripts/seed_data/lessons/complex_numbers.json"

SECTION_UPDATES = {
    "intro": {
        "body_en_md": (
            "The equation $x^2 + 1 = 0$ has no solution in $\\mathbb{R}$, because no real number "
            "squared is negative. Yet engineers and physicists constantly need square roots of "
            "negatives — in AC circuits, quantum wave functions, and the roots of polynomials. "
            "Complex numbers extend the real line into a two-dimensional plane.\n\n"
            "In the **5-point Bagrut**, complex numbers appear in a dedicated section worth "
            "**15–20 points** and test: arithmetic in $a+bi$ form, finding complex roots of "
            "quadratics, the conjugate, modulus, and geometric representation on the Argand plane. "
            "Typical exam tasks include multiplying and dividing, solving $z^2 = w$ for complex $w$, "
            "and proving identities using $z\\bar{z} = |z|^2$.\n\n"
            "Understanding $i$ unlocks an enormous part of mathematics — the **Fundamental Theorem "
            "of Algebra** guarantees every degree-$n$ polynomial has exactly $n$ roots in "
            "$\\mathbb{C}$ (counting multiplicity). This lesson builds the algebraic toolkit you "
            "need before moving on to polar form and De Moivre's theorem."
        ),
        "body_he_md": (
            "למשוואה $x^2 + 1 = 0$ אין פתרון ב-$\\mathbb{R}$, כי אין מספר ממשי שבריבוע הוא שלילי. "
            "ובכל זאת, מהנדסים ופיזיקאים זקוקים לשורשים של מספרים שליליים — במעגלי זרם חילופין, "
            "בפונקציות גל בקוונטים, ובשורשים של פולינומים. מספרים מרוכבים מרחיבים את קו המספרים "
            "הממשיים למישור דו-ממדי.\n\n"
            "ב**בגרות 5 יחידות**, מספרים מרוכבים מופיעים בסעיף ייעודי בשווי **15–20 נקודות** "
            "ובוחנים: חשבון בצורה $a+bi$, מציאת שורשים מרוכבים של משוואות ריבועיות, צמוד, מודולוס "
            "וייצוג גאומטרי על מישור ארגנד. משימות בחינה טיפוסיות כוללות כפל וחילוק, פתרון $z^2 = w$ "
            "כאשר $w$ מרוכב, והוכחת זהויות באמצעות $z\\bar{z} = |z|^2$.\n\n"
            "הבנת $i$ פותחת חלק עצום במתמטיקה — **המשפט הבסיסי של האלגברה** מבטיח שלכל פולינום "
            "ממעלה $n$ יש בדיוק $n$ שורשים ב-$\\mathbb{C}$ (בספירת ריבוי). שיעור זה בונה את "
            "ערכת הכלים האלגברית לפני המעבר לצורה קוטבית ולמשפט דה מואבר."
        ),
    },
    "definition": {
        "body_en_md": (
            "## The Imaginary Unit\n\n"
            "**Imaginary unit:** $i$ is defined by $i^2 = -1$. We do **NOT** define $i = \\sqrt{-1}$ "
            "(that causes sign errors); instead we define $i$ by its square and treat $\\sqrt{-4} = 2i$ "
            "as the principal value only when the context allows.\n\n"
            "## Complex Number in Standard Form\n\n"
            "**Complex number:** $z = a + bi$ where $a, b \\in \\mathbb{R}$.\n"
            "- $\\text{Re}(z) = a$ (real part)\n"
            "- $\\text{Im}(z) = b$ (imaginary part — note: $b$ itself is a **real** number!)\n"
            "- If $b = 0$: $z$ is **real**. If $a = 0$ and $b \\ne 0$: $z$ is **pure imaginary**.\n\n"
            "## Conjugate and Modulus\n\n"
            "**Conjugate:** $\\bar{z} = a - bi$ (flip the sign of the imaginary part only).\n\n"
            "**Modulus:** $|z| = \\sqrt{a^2 + b^2}$ — the distance from the origin in the complex plane. "
            "Key identity: $z \\cdot \\bar{z} = a^2 + b^2 = |z|^2$.\n\n"
            "## The Argand Plane\n\n"
            "The **Argand plane** (complex plane) has a horizontal real axis and vertical imaginary axis. "
            "The point $(a, b)$ represents $z = a + bi$. The modulus $|z|$ is the hypotenuse of the "
            "right triangle with legs $|a|$ and $|b|$ — this geometric view prevents the common error "
            "$|a+bi| = a+b$."
        ),
        "body_he_md": (
            "## היחידה המדומה\n\n"
            "**יחידה מדומה:** $i$ מוגדרת על ידי $i^2 = -1$. אנו **לא** מגדירים $i = \\sqrt{-1}$ "
            "(זה גורם לטעויות סימן); במקום זאת מגדירים $i$ דרך הריבוע שלה.\n\n"
            "## מספר מרוכב בצורה סטנדרטית\n\n"
            "**מספר מרוכב:** $z = a + bi$ כאשר $a, b \\in \\mathbb{R}$.\n"
            "- $\\text{Re}(z) = a$ (חלק ממשי)\n"
            "- $\\text{Im}(z) = b$ (חלק מדומה — שימו לב: $b$ עצמו **מספר ממשי**!)\n"
            "- אם $b = 0$: $z$ **ממשי**. אם $a = 0$ ו-$b \\ne 0$: $z$ **מדומה טהור**.\n\n"
            "## צמוד ומודולוס\n\n"
            "**צמוד:** $\\bar{z} = a - bi$ (הופכים סימן **רק** של החלק המדומה).\n\n"
            "**מודולוס:** $|z| = \\sqrt{a^2 + b^2}$ — המרחק מהראשית במישור המרוכב. "
            "זהות מפתח: $z \\cdot \\bar{z} = a^2 + b^2 = |z|^2$.\n\n"
            "## מישור ארגנד\n\n"
            "ב**מישור ארגנד** (המישור המרוכב) הציר האופקי מייצג את הממשיים והאנכי את המדומים. "
            "הנקודה $(a, b)$ מייצגת $z = a + bi$. המודולוס $|z|$ הוא היתר במשולש ישר-זווית "
            "עם ניצבים $|a|$ ו-$|b|$ — תצוגה גאומטרית זו מונעת את הטעות $|a+bi| = a+b$."
        ),
    },
    "theory": {
        "body_en_md": (
            "## Powers of $i$ — The 4-Cycle\n\n"
            "Powers of $i$ cycle with period 4:\n"
            "$$i^1 = i,\\quad i^2 = -1,\\quad i^3 = -i,\\quad i^4 = 1,\\quad i^5 = i,\\ldots$$\n"
            "To find $i^n$: compute $n \\bmod 4$, then look up. Example: $i^{27} = i^3 = -i$ because "
            "$27 = 4 \\cdot 6 + 3$.\n\n"
            "## Addition and Multiplication\n\n"
            "**Addition:** $(a+bi)+(c+di) = (a+c)+(b+d)i$ — add real and imaginary parts separately.\n\n"
            "**Multiplication:** Distribute (FOIL) and apply $i^2 = -1$:\n"
            "$$(a+bi)(c+di) = ac + adi + bci + bdi^2 = (ac-bd)+(ad+bc)i.$$\n\n"
            "## Conjugate Properties\n\n"
            "$z + \\bar{z} = 2a$ (always real), $z - \\bar{z} = 2bi$ (always pure imaginary), "
            "$z \\cdot \\bar{z} = a^2 + b^2 = |z|^2$ (always non-negative real).\n\n"
            "## Division via Conjugate\n\n"
            "Eliminate $i$ from the denominator by multiplying top and bottom by "
            "$\\overline{\\text{denominator}}$:\n"
            "$$\\frac{a+bi}{c+di} = \\frac{(a+bi)(c-di)}{(c+di)(c-di)} = "
            "\\frac{(ac+bd)+(bc-ad)i}{c^2+d^2}.$$\n"
            "The denominator becomes the real number $c^2+d^2 = |c+di|^2$.\n\n"
            "## Modulus Properties\n\n"
            "$|z_1 z_2| = |z_1||z_2|$, $|z_1/z_2| = |z_1|/|z_2|$ (when $z_2 \\ne 0$). "
            "These are the most-tested identities in Bagrut proofs.\n\n"
            "## Quadratic Formula over $\\mathbb{C}$\n\n"
            "When the discriminant $D = b^2 - 4ac < 0$, the quadratic $az^2+bz+c=0$ has two "
            "conjugate complex roots: $z = \\frac{-b \\pm i\\sqrt{|D|}}{2a}$. "
            "Write $\\sqrt{D} = i\\sqrt{|D|}$ — never leave a negative under a real square root.\n\n"
            "**Exam strategy:** For every multiplication, scan the expanded form for $i^2$ before "
            "collecting terms. For every division, multiply by the conjugate of the denominator first. "
            "For $z^2 = w$, always write $z = a+bi$ and use the modulus shortcut $|z|^2 = |w|$."
        ),
        "body_he_md": (
            "## חזקות של $i$ — מחזור 4\n\n"
            "חזקות של $i$ מחזוריות עם מחזור 4:\n"
            "$$i^1 = i,\\quad i^2 = -1,\\quad i^3 = -i,\\quad i^4 = 1,\\quad i^5 = i,\\ldots$$\n"
            "למציאת $i^n$: מחשבים $n \\bmod 4$ ואז מוצאים. דוגמה: $i^{27} = i^3 = -i$ כי "
            "$27 = 4 \\cdot 6 + 3$.\n\n"
            "## חיבור וכפל\n\n"
            "**חיבור:** $(a+bi)+(c+di) = (a+c)+(b+d)i$ — מחברים חלקים ממשיים ומדומים בנפרד.\n\n"
            "**כפל:** מפתחים (FOIL) ומציבים $i^2 = -1$:\n"
            "$$(a+bi)(c+di) = ac + adi + bci + bdi^2 = (ac-bd)+(ad+bc)i.$$\n\n"
            "## תכונות הצמוד\n\n"
            "$z + \\bar{z} = 2a$ (תמיד ממשי), $z - \\bar{z} = 2bi$ (תמיד מדומה טהור), "
            "$z \\cdot \\bar{z} = a^2 + b^2 = |z|^2$ (תמיד ממשי אי-שלילי).\n\n"
            "## חילוק דרך הצמוד\n\n"
            "מבטלים $i$ מהמכנה על ידי כפל מונה ומכנה בצמוד של המכנה:\n"
            "$$\\frac{a+bi}{c+di} = \\frac{(a+bi)(c-di)}{(c+di)(c-di)} = "
            "\\frac{(ac+bd)+(bc-ad)i}{c^2+d^2}.$$\n"
            "המכנה הופך למספר ממשי $c^2+d^2 = |c+di|^2$.\n\n"
            "## תכונות המודולוס\n\n"
            "$|z_1 z_2| = |z_1||z_2|$, $|z_1/z_2| = |z_1|/|z_2|$ (כאשר $z_2 \\ne 0$). "
            "אלה הזהויות הנבדקות ביותר בהוכחות בבגרות.\n\n"
            "## נוסחת השורשים מעל $\\mathbb{C}$\n\n"
            "כאשר הדיסקרימיננטה $D = b^2 - 4ac < 0$, לריבועית $az^2+bz+c=0$ יש שני שורשים "
            "מרוכבים צמודים: $z = \\frac{-b \\pm i\\sqrt{|D|}}{2a}$. "
            "כותבים $\\sqrt{D} = i\\sqrt{|D|}$ — לעולם לא משאירים שלילי תחת שורש ממשי.\n\n"
            "**אסטרטגיית בחינה:** בכל כפל, סרקו את הפיתוח ל-$i^2$ לפני איסוף איברים. "
            "בכל חילוק, כפלו בצמוד המכנה קודם. ב-$z^2 = w$, כתבו $z = a+bi$ "
            "והשתמשו בקיצור $|z|^2 = |w|$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "## Decision Table — Which Technique to Use\n\n"
            "| Situation | Technique |\n"
            "|---|---|\n"
            "| Compute $i^n$ for large $n$ | Reduce $n \\bmod 4$: remainder 0→$1$, 1→$i$, 2→$−1$, 3→$−i$ |\n"
            "| Multiply two complex numbers | FOIL, then replace every $i^2$ with $-1$ |\n"
            "| Divide $z_1/z_2$ | Multiply numerator & denominator by $\\bar{z}_2$ |\n"
            "| Find $|z|$ | $\\sqrt{(\\text{Re})^2 + (\\text{Im})^2}$ — Pythagoras! |\n"
            "| Solve $z^2 = w$ (complex) | Write $z=a+bi$, equate parts; use $|z|^2 = |w|$ as shortcut |\n"
            "| Prove identity about modulus | Start from $|z|^2 = z\\bar{z}$ |\n"
            "| Complex roots of $az^2+bz+c=0$ | Quadratic formula; write $\\sqrt{D}$ as $i\\sqrt{|D|}$ when $D<0$ |\n\n"
            "**Warning:** Never write $\\sqrt{-4} = 2i$ without acknowledging both $+2i$ and $-2i$ "
            "as square roots. The principal root is $2i$, but the full solution set is $\\{\\pm 2i\\}$."
        ),
        "body_he_md": (
            "## טבלת החלטה — איזו טכניקה להשתמש\n\n"
            "| מצב | טכניקה |\n"
            "|---|---|\n"
            "| חישוב $i^n$ עבור $n$ גדול | מצמצמים $n \\bmod 4$: שארית 0→$1$, 1→$i$, 2→$−1$, 3→$−i$ |\n"
            "| כפל שני מספרים מרוכבים | פיתוח (FOIL), ואז מחליפים כל $i^2$ ב-$-1$ |\n"
            "| חילוק $z_1/z_2$ | מכפילים מונה ומכנה ב-$\\bar{z}_2$ |\n"
            "| מציאת $|z|$ | $\\sqrt{(\\text{Re})^2 + (\\text{Im})^2}$ — פיתגורס! |\n"
            "| פתרון $z^2 = w$ (מרוכב) | כותבים $z=a+bi$, משווים חלקים; $|z|^2 = |w|$ כקיצור |\n"
            "| הוכחת זהות על מודולוס | מתחילים מ-$|z|^2 = z\\bar{z}$ |\n"
            "| שורשים מרוכבים של $az^2+bz+c=0$ | נוסחת השורשים; $\\sqrt{D} = i\\sqrt{|D|}$ כאשר $D<0$ |\n\n"
            "**אזהרה:** אל תכתבו $\\sqrt{-4} = 2i$ מבלי לציין שגם $+2i$ וגם $-2i$ הם שורשים. "
            "השורש העיקרי הוא $2i$, אך קבוצת הפתרונות המלאה היא $\\{\\pm 2i\\}$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting $i^2 = -1$** when expanding products — always substitute at the end, "
            "not in the middle of FOIL.\n\n"
            "2. **Writing $\\sqrt{-9} = -3$** — it should be $\\pm 3i$; square roots of negatives "
            "are imaginary, not negative real numbers.\n\n"
            "3. **Wrong modulus formula:** $|a+bi| \\neq a+b$. It is $\\sqrt{a^2+b^2}$ (Pythagoras!). "
            "Draw the Argand plane if unsure.\n\n"
            "4. **Skipping the conjugate trick in division** — leaving $i$ in the denominator means "
            "you cannot read off Re and Im separately.\n\n"
            "5. **Sign error in conjugate:** $\\overline{a+bi} = a - bi$, NOT $-a+bi$ or $-a-bi$. "
            "Only the imaginary part changes sign.\n\n"
            "6. **Powers of $i$:** $i^{100} = (i^4)^{25} = 1$, NOT $i$. Always reduce mod 4 before "
            "looking up the value."
        ),
        "body_he_md": (
            "1. **שכחת $i^2 = -1$** בפיתוח מכפלות — תמיד להציב בסוף, לא באמצע הפיתוח.\n\n"
            "2. **כתיבת $\\sqrt{-9} = -3$** — הנכון הוא $\\pm 3i$; שורשים של שליליים הם מדומים, "
            "לא ממשיים שליליים.\n\n"
            "3. **נוסחת מודולוס שגויה:** $|a+bi| \\neq a+b$. הנכון: $\\sqrt{a^2+b^2}$ (פיתגורס!). "
            "ציירו את מישור ארגנד אם לא בטוחים.\n\n"
            "4. **דילוג על טריק הצמוד בחילוק** — השארת $i$ במכנה מונעת קריאת Re ו-Im בנפרד.\n\n"
            "5. **טעות סימן בצמוד:** $\\overline{a+bi} = a - bi$, לא $-a+bi$ ולא $-a-bi$. "
            "רק החלק המדומה משנה סימן.\n\n"
            "6. **חזקות של $i$:** $i^{100} = 1$, לא $i$. תמיד לצמצם mod 4 לפני חיפוש הערך."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Complex numbers are not a mathematical curiosity — they are the language of oscillations, "
            "waves, and rotation. In physics, $e^{i\\theta} = \\cos\\theta + i\\sin\\theta$ connects "
            "circular motion to algebra. In electrical engineering, AC circuits use $Z = R + iX$ "
            "(impedance) to analyse voltage and current.\n\n"
            "**Recommended next topics:**\n"
            "- `concept:complex_numbers_5pt` — advanced Bagrut exam patterns\n"
            "- `concept:complex_numbers_de_moivre` — polar form and powers/roots\n\n"
            "**Why it matters for exams:** Bagrut 5-unit papers reward fluency with conjugate division "
            "and the modulus trick for $z^2 = w$. University calculus uses $\\mathbb{C}$ for "
            "analytic functions. Master $a+bi$ arithmetic now — polar form builds directly on it."
        ),
        "body_he_md": (
            "מספרים מרוכבים אינם סקרנות מתמטית — הם שפת התנודות, הגלים והסיבוב. בפיזיקה, "
            "$e^{i\\theta} = \\cos\\theta + i\\sin\\theta$ מקשר תנועה מעגלית לאלגברה. "
            "בהנדסת חשמל, מעגלי ז\"ח משתמשים ב-$Z = R + iX$ (עכבה) לניתוח מתח וזרם.\n\n"
            "**נושאים מומלצים להמשך:**\n"
            "- `concept:complex_numbers_5pt` — תבניות בחינה מתקדמות\n"
            "- `concept:complex_numbers_de_moivre` — צורה קוטבית וחזקות/שורשים\n\n"
            "**למה זה חשוב לבחינות:** בגרות 5 יחידות מעריכה שטף בחילוק דרך צמוד ובטריק המודולוס "
            "ל-$z^2 = w$. חדו\"א באוניברסיטה משתמש ב-$\\mathbb{C}$ לפונקציות אנליטיות. "
            "שלטו בחשבון $a+bi$ עכשיו — הצורה הקוטבית נבנית ישירות עליו."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Formula sheet:**\n"
            "- $i^2 = -1$, powers cycle: $i,\\,-1,\\,-i,\\,1$\n"
            "- $|a+bi| = \\sqrt{a^2+b^2}$\n"
            "- $\\overline{a+bi} = a-bi$, $z\\bar{z} = |z|^2$\n"
            "- Division: multiply by $\\bar{z}_2/\\bar{z}_2$\n"
            "- $|z_1 z_2| = |z_1||z_2|$, $\\overline{z_1 z_2} = \\bar{z}_1\\bar{z}_2$\n\n"
            "**Exam patterns examiners test:**\n"
            "1. Arithmetic computation (multiply, divide, simplify) — 4–6 pts.\n"
            "2. Finding complex roots of quadratic $az^2+bz+c=0$ — 4 pts.\n"
            "3. Solving $z^2 = w$ for $w$ complex — 6 pts. (Method: write $z=a+bi$, use modulus trick.)\n"
            "4. Proving a property using $z\\bar{z}=|z|^2$ — 5 pts.\n"
            "5. \"Is the following real/imaginary?\" — 2 pts (check imaginary part = 0).\n\n"
            "**Time allocation:** These questions are usually in Part B. Allocate ~20 minutes."
        ),
        "body_he_md": (
            "**דף נוסחאות:**\n"
            "- $i^2 = -1$, חזקות מחזוריות: $i,\\,-1,\\,-i,\\,1$\n"
            "- $|a+bi| = \\sqrt{a^2+b^2}$\n"
            "- $\\overline{a+bi} = a-bi$, $z\\bar{z} = |z|^2$\n"
            "- חילוק: מכפילים ב-$\\bar{z}_2/\\bar{z}_2$\n"
            "- $|z_1 z_2| = |z_1||z_2|$, $\\overline{z_1 z_2} = \\bar{z}_1\\bar{z}_2$\n\n"
            "**תבניות בחינה:**\n"
            "1. חישוב אריתמטי (כפל, חילוק, פישוט) — 4–6 נק׳.\n"
            "2. שורשים מרוכבים של $az^2+bz+c=0$ — 4 נק׳.\n"
            "3. פתרון $z^2 = w$ עבור $w$ מרוכב — 6 נק׳. (שיטה: $z=a+bi$, טריק מודולוס.)\n"
            "4. הוכחת תכונה ב-$z\\bar{z}=|z|^2$ — 5 נק׳.\n"
            "5. \"האם הביטוי ממשי/מדומה?\" — 2 נק׳ (חלק מדומה = 0).\n\n"
            "**הקצאת זמן:** שאלות אלה בדרך כלל בחלק ב׳. הקצו כ-20 דקות."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Definition:** $z = a+bi$, $i^2 = -1$; powers of $i$ cycle: $i, -1, -i, 1$.\n"
            "- **Arithmetic:** Add component-wise; multiply via FOIL with $i^2=-1$; divide via "
            "conjugate of denominator.\n"
            "- **Conjugate & modulus:** $\\bar{z} = a-bi$; $z\\bar{z} = |z|^2 = a^2+b^2$; "
            "$|z_1 z_2| = |z_1||z_2|$.\n"
            "- **Argand plane:** $z = a+bi$ is the point $(a,b)$; $|z|$ is distance from origin.\n"
            "- **Complex roots:** Quadratic with $D<0$ has two conjugate complex roots "
            "$\\frac{-b \\pm i\\sqrt{|D|}}{2a}$.\n"
            "- **Solving $z^2 = w$:** Write $z=a+bi$, equate real/imag parts, use $|z|^2=|w|$."
        ),
        "body_he_md": (
            "- **הגדרה:** $z = a+bi$, $i^2 = -1$; חזקות $i$ מחזוריות: $i, -1, -i, 1$.\n"
            "- **חשבון:** חיבור רכיב-רכיב; כפל בפיתוח עם $i^2=-1$; חילוק דרך צמוד המכנה.\n"
            "- **צמוד ומודולוס:** $\\bar{z} = a-bi$; $z\\bar{z} = |z|^2 = a^2+b^2$; "
            "$|z_1 z_2| = |z_1||z_2|$.\n"
            "- **מישור ארגנד:** $z = a+bi$ היא הנקודה $(a,b)$; $|z|$ הוא המרחק מהראשית.\n"
            "- **שורשים מרוכבים:** ריבועית עם $D<0$ בעלת שני שורשים צמודים "
            "$\\frac{-b \\pm i\\sqrt{|D|}}{2a}$.\n"
            "- **פתרון $z^2 = w$:** כותבים $z=a+bi$, משווים חלקים, משתמשים ב-$|z|^2=|w|$."
        ),
    },
}

WORKED_EXAMPLES = {
    1: {
        "body_en_md": (
            "**Compute $(2+3i)(1-i)$.**\n\n"
            "---\n\n"
            "### Move 1 — Distribute (FOIL)\n"
            "We multiply each term in the first factor by each term in the second, "
            "just like expanding $(x+2)(x-3)$:\n"
            "$$(2+3i)(1-i) = 2 \\cdot 1 + 2 \\cdot(-i) + 3i \\cdot 1 + 3i \\cdot(-i) "
            "= 2 - 2i + 3i - 3i^2.$$\n\n"
            "### Move 2 — Replace $i^2 = -1$ and collect\n"
            "Group the real terms ($2$ and $-3i^2 = +3$) and imaginary terms ($-2i + 3i$):\n"
            "$$= 2 - 2i + 3i - 3(-1) = 2 + 3 + (-2+3)i = 5 + i.$$\n\n"
            "**Answer:** $(2+3i)(1-i) = 5 + i$.\n\n"
            "**Check via moduli:** $|2+3i|^2 \\cdot |1-i|^2 = (4+9)(1+1) = 13 \\cdot 2 = 26$. "
            "And $|5+i|^2 = 25+1 = 26$. ✓ The property $|z_1 z_2| = |z_1||z_2|$ confirms our answer.\n\n"
            "**Exam note:** Always collect real parts and imaginary parts separately before substituting "
            "$i^2 = -1$. The final answer must be in standard form $a+bi$ with both $a$ and $b$ real.\n\n"
            "**Why this works:** Complex multiplication is just binomial expansion with the extra rule "
            "that $i^2 = -1$. There is no new technique beyond FOIL and careful sign tracking. "
            "Bagrut examiners expect the full FOIL expansion shown, not a shortcut."
        ),
        "body_he_md": (
            "**חשבו $(2+3i)(1-i)$.**\n\n"
            "---\n\n"
            "### צעד 1 — פיתוח (FOIL)\n"
            "מכפילים כל איבר בגורם הראשון בכל איבר בשני, "
            "בדיוק כמו פיתוח $(x+2)(x-3)$:\n"
            "$$(2+3i)(1-i) = 2 \\cdot 1 + 2 \\cdot(-i) + 3i \\cdot 1 + 3i \\cdot(-i) "
            "= 2 - 2i + 3i - 3i^2.$$\n\n"
            "### צעד 2 — מחליפים $i^2 = -1$ ואוספים\n"
            "מקבצים את האיברים הממשיים ($2$ ו-$-3i^2 = +3$) והמדומים ($-2i + 3i$):\n"
            "$$= 2 - 2i + 3i - 3(-1) = 2 + 3 + (-2+3)i = 5 + i.$$\n\n"
            "**תשובה:** $(2+3i)(1-i) = 5 + i$.\n\n"
            "**בדיקה דרך מודולוסים:** $|2+3i|^2 \\cdot |1-i|^2 = (4+9)(1+1) = 26$. "
            "ו-$|5+i|^2 = 25+1 = 26$. ✓ התכונה $|z_1 z_2| = |z_1||z_2|$ מאשרת את התשובה.\n\n"
            "**הערה לבחינה:** תמיד אספו חלקים ממשיים ומדומים בנפרד לפני הצבת $i^2 = -1$. "
            "התשובה הסופית חייבת להיות בצורה סטנדרטית $a+bi$ עם $a$ ו-$b$ ממשיים.\n\n"
            "**למה זה עובד:** כפל מרוכב הוא פשוט פיתוח בינומי עם הכלל הנוסף $i^2 = -1$. "
            "אין טכניקה חדשה מעבר ל-FOIL ומעקב זהיר אחר סימנים. "
            "בודקי בגרות מצפים לפיתוח FOIL מלא, לא לקיצור דרך. "
            "כתבו כל ארבעת המכפלות בבירור לפני שמציבים $i^2 = -1$."
        ),
    },
    2: {
        "body_en_md": (
            "**Find all $z \\in \\mathbb{C}$ such that $z^2 = -4 + 3i$.**\n\n"
            "---\n\n"
            "### Move 1 — Write $z = a + bi$ and expand\n"
            "Since we need all complex square roots, write $z = a + bi$ with $a, b \\in \\mathbb{R}$ "
            "and expand the square using $(a+bi)^2 = a^2 - b^2 + 2abi$:\n"
            "$$(a+bi)^2 = a^2 - b^2 + 2abi = -4 + 3i.$$\n\n"
            "### Move 2 — Equate real and imaginary parts\n"
            "$$a^2 - b^2 = -4 \\quad (\\text{I}), \\qquad 2ab = 3 \\quad (\\text{II}).$$\n\n"
            "### Move 3 — Modulus shortcut\n"
            "$|z^2| = |z|^2 = |-4+3i| = \\sqrt{16+9} = 5$, so $a^2+b^2 = 5 \\quad (\\text{III})$.\n\n"
            "### Move 4 — Solve (I) and (III)\n"
            "Adding: $2a^2 = 1 \\Rightarrow a = \\pm\\frac{1}{\\sqrt{2}}$. "
            "Subtracting: $2b^2 = 9 \\Rightarrow b = \\pm\\frac{3}{\\sqrt{2}}$.\n\n"
            "### Move 5 — Sign check via (II)\n"
            "$2ab = 3 > 0$, so $a$ and $b$ have the **same sign**.\n"
            "$$z_1 = \\frac{1}{\\sqrt{2}} + \\frac{3}{\\sqrt{2}}i = \\frac{1+3i}{\\sqrt{2}}, "
            "\\qquad z_2 = -\\frac{1+3i}{\\sqrt{2}}.$$\n\n"
            "**Exam note:** The modulus trick gives a third equation instantly — essential for "
            "Bagrut $z^2 = w$ problems worth 6 points. Without it, solving the nonlinear system "
            "from (I) and (II) alone is much harder.\n\n"
            "**Verification:** Substitute $z_1 = \\frac{1+3i}{\\sqrt{2}}$ back: "
            "$z_1^2 = \\frac{1+6i-9}{2} = \\frac{-8+6i}{2} = -4+3i$ ✓. Always check both roots. "
            "This problem type appears regularly on the 5-unit Bagrut."
        ),
        "body_he_md": (
            "**מצאו את כל $z \\in \\mathbb{C}$ כך ש-$z^2 = -4 + 3i$.**\n\n"
            "---\n\n"
            "### צעד 1 — כותבים $z = a + bi$ ומפתחים\n"
            "מכיוון שצריך את כל שורשי הריבוע המרוכבים, כותבים $z = a + bi$ עם $a, b \\in \\mathbb{R}$ "
            "ומפתחים: $(a+bi)^2 = a^2 - b^2 + 2abi$:\n"
            "$$(a+bi)^2 = a^2 - b^2 + 2abi = -4 + 3i.$$\n\n"
            "### צעד 2 — משווים חלקים ממשיים ומדומים\n"
            "$$a^2 - b^2 = -4 \\quad (\\text{I}), \\qquad 2ab = 3 \\quad (\\text{II}).$$\n\n"
            "### צעד 3 — קיצור דרך עם מודולוס\n"
            "$|z^2| = |z|^2 = |-4+3i| = \\sqrt{16+9} = 5$, אז $a^2+b^2 = 5 \\quad (\\text{III})$.\n\n"
            "### צעד 4 — פתרון (I) ו-(III)\n"
            "חיבור: $2a^2 = 1 \\Rightarrow a = \\pm\\frac{1}{\\sqrt{2}}$. "
            "חיסור: $2b^2 = 9 \\Rightarrow b = \\pm\\frac{3}{\\sqrt{2}}$.\n\n"
            "### צעד 5 — בדיקת סימן דרך (II)\n"
            "$2ab = 3 > 0$, אז $a$ ו-$b$ **באותו סימן**.\n"
            "$$z_1 = \\frac{1+3i}{\\sqrt{2}}, \\qquad z_2 = -\\frac{1+3i}{\\sqrt{2}}.$$\n\n"
            "**הערה לבחינה:** טריק המודולוס נותן משוואה שלישית מיד — חיוני לבעיות $z^2 = w$ "
            "בבגרות בשווי 6 נקודות. בלעדיו, פתרון המערכת הלא-לינארית מ-(I) ו-(II) בלבד "
            "הרבה יותר קשה.\n\n"
            "**אימות:** הציבו $z_1 = \\frac{1+3i}{\\sqrt{2}}$ חזרה: "
            "$z_1^2 = \\frac{-8+6i}{2} = -4+3i$ ✓. תמיד בדקו את שני השורשים. "
            "סוג בעיה זה מופיע לעיתים קרובות בבגרות 5 יחידות."
        ),
    },
    3: {
        "body_en_md": (
            "**Prove that for all $z_1, z_2 \\in \\mathbb{C}$: $|z_1 z_2| = |z_1||z_2|$.**\n\n"
            "---\n\n"
            "**Strategy:** Use the identity $|z|^2 = z \\cdot \\bar{z}$ on both sides. "
            "This converts a modulus problem into a product-of-conjugates problem, "
            "which is purely algebraic.\n\n"
            "### Move 1 — Expand $|z_1 z_2|^2$\n"
            "$$|z_1 z_2|^2 = (z_1 z_2)\\overline{(z_1 z_2)}.$$\n\n"
            "### Move 2 — Conjugation distributes\n"
            "$\\overline{z_1 z_2} = \\bar{z}_1 \\bar{z}_2$. So:\n"
            "$$|z_1 z_2|^2 = z_1 z_2 \\bar{z}_1 \\bar{z}_2 = (z_1 \\bar{z}_1)(z_2 \\bar{z}_2) "
            "= |z_1|^2 |z_2|^2 = (|z_1||z_2|)^2.$$\n\n"
            "### Move 3 — Take square roots\n"
            "Since modulus is non-negative, $|z_1 z_2| = |z_1||z_2|$. $\\blacksquare$\n\n"
            "**Note:** The key step is $\\overline{z_1 z_2} = \\bar{z}_1\\bar{z}_2$, which follows "
            "directly from the definition of conjugation. This proof pattern appears in every "
            "5-unit Bagrut complex numbers section. Practice writing it from memory — "
            "examiners award full marks only for complete algebraic steps, not just the conclusion.\n\n"
            "**Related identity:** The same technique proves $|z_1/z_2| = |z_1|/|z_2|$ — "
            "just take square roots of both sides at the end. "
            "Both identities are listed on the Bagrut formula sheet."
        ),
        "body_he_md": (
            "**הוכיחו שלכל $z_1, z_2 \\in \\mathbb{C}$: $|z_1 z_2| = |z_1||z_2|$.**\n\n"
            "---\n\n"
            "**אסטרטגיה:** שימוש בזהות $|z|^2 = z \\cdot \\bar{z}$ משני הצדדים. "
            "זה הופך בעיית מודולוס לבעיית מכפלת צמודים, שהיא אלגברית לחלוטין.\n\n"
            "### צעד 1 — פיתוח $|z_1 z_2|^2$\n"
            "$$|z_1 z_2|^2 = (z_1 z_2)\\overline{(z_1 z_2)}.$$\n\n"
            "### צעד 2 — הצמדה מתפלגת\n"
            "$\\overline{z_1 z_2} = \\bar{z}_1 \\bar{z}_2$. לכן:\n"
            "$$|z_1 z_2|^2 = z_1 z_2 \\bar{z}_1 \\bar{z}_2 = (z_1 \\bar{z}_1)(z_2 \\bar{z}_2) "
            "= |z_1|^2 |z_2|^2 = (|z_1||z_2|)^2.$$\n\n"
            "### צעד 3 — לקיחת שורש\n"
            "כיוון שהמודולוס אי-שלילי, $|z_1 z_2| = |z_1||z_2|$. $\\blacksquare$\n\n"
            "**הערה:** הצעד המפתח הוא $\\overline{z_1 z_2} = \\bar{z}_1\\bar{z}_2$, הנובע מהגדרת "
            "הצמוד. תבנית הוכחה זו מופיעה בכל סעיף מספרים מרוכבים בבגרות 5 יחידות. "
            "תרגלו לכתוב אותה בעל-פה — בודקים נותנים ניקוד מלא רק על צעדים אלגבריים מלאים, "
            "לא רק על המסקנה.\n\n"
            "**זהות קשורה:** אותה טכניקה מוכיחה $|z_1/z_2| = |z_1|/|z_2|$ — "
            "פשוט לוקחים שורש משני הצדדים בסוף. "
            "שתי הזהויות מופיעות בדף הנוסחאות של הבגרות. "
            "שלב ההצמדה המתפלגת הוא מה שבודקים מחפשים בפתרון מלא."
        ),
    },
}

CHECKPOINTS = {
    0: {
        "checkpoint_solution_en": (
            "**Step 1 — Multiply:**\n"
            "$(1+2i)(3-i) = 3 - i + 6i - 2i^2 = 3 + 5i + 2 = 5 + 5i$.\n\n"
            "**Step 2 — Modulus:**\n"
            "$|1+2i| = \\sqrt{1^2 + 2^2} = \\sqrt{1+4} = \\sqrt{5}$.\n\n"
            "**Check:** $|5+5i| = \\sqrt{50} = 5\\sqrt{2}$. "
            "And $|1+2i| \\cdot |3-i| = \\sqrt{5} \\cdot \\sqrt{10} = \\sqrt{50}$. ✓"
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — כפל:**\n"
            "$(1+2i)(3-i) = 3 - i + 6i - 2i^2 = 3 + 5i + 2 = 5 + 5i$.\n\n"
            "**שלב 2 — מודולוס:**\n"
            "$|1+2i| = \\sqrt{1^2 + 2^2} = \\sqrt{5}$.\n\n"
            "**בדיקה:** $|5+5i| = \\sqrt{50} = 5\\sqrt{2}$. "
            "ו-$|1+2i| \\cdot |3-i| = \\sqrt{5} \\cdot \\sqrt{10} = \\sqrt{50}$. ✓"
        ),
    },
    1: {
        "checkpoint_solution_en": (
            "**Step 1 — Write $z = a + bi$ and expand:**\n"
            "$(a+bi)^2 = a^2 - b^2 + 2abi = 3 + 4i$.\n\n"
            "**Step 2 — Equate parts:**\n"
            "$a^2 - b^2 = 3$ (I), $2ab = 4$ (II).\n\n"
            "**Step 3 — Modulus trick:**\n"
            "$|z|^2 = |3+4i| = 5$, so $a^2 + b^2 = 5$ (III).\n\n"
            "**Step 4 — Solve:**\n"
            "Adding (I)+(III): $2a^2 = 8 \\Rightarrow a^2 = 4$. "
            "Subtracting: $2b^2 = 2 \\Rightarrow b^2 = 1$.\n\n"
            "**Step 5 — Sign check:** $2ab = 4 > 0$, so $a, b$ same sign.\n"
            "$z_1 = 2 + i$, $z_2 = -2 - i$. $\\checkmark$"
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — כותבים $z = a + bi$ ומפתחים:**\n"
            "$(a+bi)^2 = a^2 - b^2 + 2abi = 3 + 4i$.\n\n"
            "**שלב 2 — משווים חלקים:**\n"
            "$a^2 - b^2 = 3$ (I), $2ab = 4$ (II).\n\n"
            "**שלב 3 — טריק מודולוס:**\n"
            "$|z|^2 = |3+4i| = 5$, אז $a^2 + b^2 = 5$ (III).\n\n"
            "**שלב 4 — פתרון:**\n"
            "חיבור (I)+(III): $2a^2 = 8 \\Rightarrow a^2 = 4$. "
            "חיסור: $2b^2 = 2 \\Rightarrow b^2 = 1$.\n\n"
            "**שלב 5 — בדיקת סימן:** $2ab = 4 > 0$, אז $a, b$ באותו סימן.\n"
            "$z_1 = 2 + i$, $z_2 = -2 - i$. $\\checkmark$"
        ),
    },
}

QUESTION_EXPLANATIONS = {
    1: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$2026 = 4 \\cdot 506 + 2$, so the remainder is 2. "
            "The cycle is $i^1=i$, $i^2=-1$, $i^3=-i$, $i^4=1$. "
            "Therefore $i^{2026} = i^2 = -1$.\n\n"
            "**How to think about it:**\n"
            "Powers of $i$ repeat every 4. Divide the exponent by 4 and use the remainder "
            "as the new exponent. Remainder 0 means use $i^4 = 1$.\n\n"
            "**Common slip:**\n"
            "Using $2026 \\bmod 4 = 2$ but then writing $i^2 = i$ instead of $-1$. "
            "Also: computing $2026/4 = 506.5$ and getting confused — use integer division.\n\n"
            "**Exam tip:**\n"
            "For even exponents ending in 0 or 4, the answer is $1$ or $-1$. "
            "For exponents ending in 2, the answer is always $-1$."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$2026 = 4 \\cdot 506 + 2$, כך שהשארית היא 2. "
            "המחזור: $i^1=i$, $i^2=-1$, $i^3=-i$, $i^4=1$. "
            "לכן $i^{2026} = i^2 = -1$.\n\n"
            "**איך לחשוב על זה:**\n"
            "חזקות של $i$ חוזרות כל 4. מחלקים את המעריך ב-4 ומשתמשים בשארית. "
            "שארית 0 פירושה $i^4 = 1$.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש בשארית 2 אך כתיבת $i^2 = i$ במקום $-1$. "
            "גם: חישוב $2026/4 = 506.5$ ולבול — השתמשו בחלוקה שלמה.\n\n"
            "**טיפ לבחינה:**\n"
            "למעריכים זוגיים שמסתיימים ב-0 או 4, התשובה $1$ או $-1$. "
            "למעריכים שמסתיימים ב-2, התשובה תמיד $-1$."
        ),
    },
    2: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Distribute: $(2+3i)(1-i) = 2 - 2i + 3i - 3i^2 = 2 + i + 3 = 5 + i$. "
            "After replacing $i^2 = -1$, the real part is $2+3=5$ and imaginary part is $-2+3=1$.\n\n"
            "**How to think about it:**\n"
            "Use FOIL on two binomials, collect real and imaginary terms separately, "
            "then substitute $i^2 = -1$ once at the end.\n\n"
            "**Common slip:**\n"
            "Forgetting to replace $i^2$, leaving $-3i^2$ as is. "
            "Sign error: $(2+3i)(1-i)$ gives $+3i$ from $3i \\cdot 1$, not $-3i$.\n\n"
            "**Exam tip:**\n"
            "Verify with $|z_1 z_2| = |z_1||z_2|$: $|2+3i| = \\sqrt{13}$, $|1-i| = \\sqrt{2}$, "
            "product $\\sqrt{26} = |5+i|$. Quick sanity check."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "פיתוח: $(2+3i)(1-i) = 2 - 2i + 3i - 3i^2 = 2 + i + 3 = 5 + i$. "
            "אחרי $i^2 = -1$: חלק ממשי $2+3=5$, חלק מדומה $-2+3=1$.\n\n"
            "**איך לחשוב על זה:**\n"
            "FOIL על שני ביטויים, אוספים חלקים ממשיים ומדומים בנפרד, "
            "ומציבים $i^2 = -1$ פעם אחת בסוף. אל תדלגו על שלב איסוף האיברים.\n\n"
            "**טעות נפוצה:**\n"
            "שכחת $i^2 = -1$, השארת $-3i^2$ כמו שהוא. "
            "טעות סימן: $3i \\cdot 1$ נותן $+3i$, לא $-3i$. "
            "בחירה ב-$5-i$ במקום $5+i$.\n\n"
            "**טיפ לבחינה:**\n"
            "אמתו עם $|z_1 z_2| = |z_1||z_2|$: $|2+3i| = \\sqrt{13}$, $|1-i| = \\sqrt{2}$, "
            "מכפלה $\\sqrt{26} = |5+i|$. בדיקת sanity מהירה שמונעת טעויות סימן."
        ),
    },
    3: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$|3-4i| = \\sqrt{3^2 + (-4)^2} = \\sqrt{9+16} = \\sqrt{25} = 5$. "
            "The modulus is always non-negative and uses **squared** components, never raw addition.\n\n"
            "**How to think about it:**\n"
            "Modulus = distance from origin in the Argand plane. "
            "Draw the point $(3, -4)$ and compute the hypotenuse: $\\sqrt{9+16}$. "
            "The minus sign on $4i$ does not affect the modulus because we square it.\n\n"
            "**Common slip:**\n"
            "$|3-4i| = 3 + (-4) = -1$ — this adds components instead of using Pythagoras. "
            "Also: $\\sqrt{9+16} = \\sqrt{25} = 5$, not $\\pm 5$ (modulus is non-negative).\n\n"
            "**Exam tip:**\n"
            "The 3-4-5 triangle is the most common modulus in Bagrut. "
            "Recognise it instantly: any $a+bi$ with $|a|=3, |b|=4$ has $|z|=5$. "
            "Also check $|3+4i|=5$ — the sign of the imaginary part does not matter."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$|3-4i| = \\sqrt{3^2 + (-4)^2} = \\sqrt{9+16} = \\sqrt{25} = 5$. "
            "המודולוס תמיד אי-שלילי ומשתמש בריבועי הרכיבים, לעולם לא בחיבור ישיר.\n\n"
            "**איך לחשוב על זה:**\n"
            "מודולוס = מרחק מהראשית במישור ארגנד. "
            "ציירו את הנקודה $(3, -4)$ וחשבו יתר: $\\sqrt{9+16}$. "
            "סימן המינוס ב-$4i$ לא משפיע על המודולוס כי מרבעים אותו.\n\n"
            "**טעות נפוצה:**\n"
            "$|3-4i| = 3 + (-4) = -1$ — מחברים רכיבים במקום פיתגורס. "
            "גם: $\\sqrt{25} = 5$, לא $\\pm 5$ (מודולוס אי-שלילי). "
            "שכחת לרבע את $-4$.\n\n"
            "**טיפ לבחינה:**\n"
            "משולש 3-4-5 הוא הנפוץ ביותר בבגרות. "
            "זהו מיד: כל $a+bi$ עם $|a|=3, |b|=4$ יש $|z|=5$. "
            "גם $|3+4i|=5$ — סימן החלק המדומה לא משנה."
        ),
    },
    4: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Multiply by $\\frac{1+i}{1+i}$: "
            "$\\frac{(2+i)(1+i)}{2} = \\frac{2+2i+i+i^2}{2} = \\frac{2+3i-1}{2} = \\frac{1+3i}{2} "
            "= \\frac{1}{2}+\\frac{3}{2}i$.\n\n"
            "**How to think about it:**\n"
            "For division, multiply top and bottom by the conjugate of the denominator. "
            "Here $\\overline{1-i} = 1+i$, and $(1-i)(1+i) = 1+1 = 2$. "
            "The denominator becomes a real number, making the result easy to read.\n\n"
            "**Common slip:**\n"
            "Multiplying by $\\frac{1-i}{1-i}$ instead of the conjugate $1+i$. "
            "Sign error in numerator: $(2+i)(1+i) = 2+3i-1$, not $2+3i+1$. "
            "Leaving the answer as $\\frac{1+3i}{2}$ without simplifying to $a+bi$ form.\n\n"
            "**Exam tip:**\n"
            "After division, verify $|z_1/z_2| = |z_1|/|z_2|$: "
            "$|2+i|/|1-i| = \\sqrt{5}/\\sqrt{2}$, and $|\\frac{1}{2}+\\frac{3}{2}i| = \\sqrt{10}/2 = \\sqrt{5/2}$. ✓"
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "מכפילים ב-$\\frac{1+i}{1+i}$: "
            "$\\frac{(2+i)(1+i)}{2} = \\frac{2+3i-1}{2} = \\frac{1+3i}{2} = \\frac{1}{2}+\\frac{3}{2}i$.\n\n"
            "**איך לחשוב על זה:**\n"
            "בחילוק, מכפילים מונה ומכנה בצמוד של המכנה. "
            "כאן $\\overline{1-i} = 1+i$, ו-$(1-i)(1+i) = 2$. "
            "המכנה הופך למספר ממשי, מה שמקל על קריאת התוצאה.\n\n"
            "**טעות נפוצה:**\n"
            "כפל ב-$\\frac{1-i}{1-i}$ במקום בצמוד $1+i$. "
            "טעות סימן: $(2+i)(1+i) = 2+3i-1$, לא $2+3i+1$. "
            "השארת התשובה כ-$\\frac{1+3i}{2}$ בלי פישוט לצורה $a+bi$.\n\n"
            "**טיפ לבחינה:**\n"
            "אחרי חילוק, אמתו $|z_1/z_2| = |z_1|/|z_2|$: "
            "$|2+i|/|1-i| = \\sqrt{5}/\\sqrt{2}$, ו-$|\\frac{1}{2}+\\frac{3}{2}i| = \\sqrt{10}/2$. ✓ "
            "אם המודולוסים לא תואמים, חפשו טעות סימן בפיתוח המונה."
        ),
    },
    5: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Discriminant $D = (-4)^2 - 4(1)(13) = 16 - 52 = -36$. "
            "Using the quadratic formula: "
            "$z = \\frac{4 \\pm \\sqrt{-36}}{2} = \\frac{4 \\pm 6i}{2} = 2 \\pm 3i$.\n\n"
            "**How to think about it:**\n"
            "When $D < 0$, write $\\sqrt{D} = i\\sqrt{|D|}$. "
            "The two roots are conjugates: $2+3i$ and $2-3i$. "
            "Always divide by $2a$ after finding the square root.\n\n"
            "**Common slip:**\n"
            "Writing $\\sqrt{-36} = -6$ instead of $\\pm 6i$. "
            "Forgetting to divide by $2a = 2$ after finding $\\sqrt{-36} = 6i$. "
            "Giving only one root instead of both $2+3i$ and $2-3i$.\n\n"
            "**Exam tip:**\n"
            "Verify: sum of roots $= -b/a = 4$, product $= c/a = 13$. "
            "Check $(2+3i)(2-3i) = 4+9 = 13$. Vieta's formulas confirm the answer quickly."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "דיסקרימיננטה $D = 16 - 52 = -36$. "
            "מנוסחת השורשים: $z = \\frac{4 \\pm \\sqrt{-36}}{2} = \\frac{4 \\pm 6i}{2} = 2 \\pm 3i$.\n\n"
            "**איך לחשוב על זה:**\n"
            "כאשר $D < 0$, כותבים $\\sqrt{D} = i\\sqrt{|D|}$. "
            "שני השורשים צמודים: $2+3i$ ו-$2-3i$. "
            "תמיד מחלקים ב-$2a$ אחרי מציאת השורש.\n\n"
            "**טעות נפוצה:**\n"
            "כתיבת $\\sqrt{-36} = -6$ במקום $\\pm 6i$. "
            "שכחת לחלק ב-$2a = 2$ אחרי $\\sqrt{-36} = 6i$. "
            "מתן שורש בודד במקום שני השורשים.\n\n"
            "**טיפ לבחינה:**\n"
            "אמתו: סכום שורשים $= 4$, מכפלה $= 13$. "
            "בדקו $(2+3i)(2-3i) = 13$. נוסחאות ויета מאשרות את התשובה במהירות. "
            "שורשים מרוכבים של ריבועית תמיד מגיעים בזוגות צמודים."
        ),
    },
    6: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Let $z = a + bi$. Then $z + \\bar{z} = (a+bi) + (a-bi) = 2a$, which is always "
            "a real number regardless of $b$. This is a fundamental property of conjugates.\n\n"
            "**How to think about it:**\n"
            "The conjugate \"cancels\" the imaginary part when added. "
            "Similarly, $z - \\bar{z} = 2bi$ is always pure imaginary.\n\n"
            "**Common slip:**\n"
            "Thinking $z + \\bar{z}$ could be complex if $b \\ne 0$ — but the $bi$ and $-bi$ "
            "terms always cancel. Also confusing with $z \\cdot \\bar{z} = |z|^2$ (which is real too).\n\n"
            "**Exam tip:**\n"
            "This property is used in proofs: \"show $w$ is real\" means show $\\text{Im}(w) = 0$, "
            "equivalently $w = \\bar{w}$, or write $w = z + \\bar{z}$ for some $z$."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "נניח $z = a + bi$. אז $z + \\bar{z} = (a+bi) + (a-bi) = 2a$, "
            "שהוא תמיד מספר ממשי ללא קשר ל-$b$. זו תכונה בסיסית של הצמוד.\n\n"
            "**איך לחשוב על זה:**\n"
            "הצמוד \"מבטל\" את החלק המדומה בחיבור. "
            "בדומה, $z - \\bar{z} = 2bi$ תמיד מדומה טהור. "
            "שתי התכונות האלה שימושיות מאוד בהוכחות בבגרות.\n\n"
            "**טעות נפוצה:**\n"
            "חשיבה ש-$z + \\bar{z}$ יכול להיות מרוכב כש-$b \\ne 0$ — אך $bi$ ו-$-bi$ "
            "תמיד מתבטלים. גם בלבול עם $z \\cdot \\bar{z} = |z|^2$ (גם הוא ממשי).\n\n"
            "**טיפ לבחינה:**\n"
            "תכונה זו משמשת בהוכחות: \"הראה ש-$w$ ממשי\" = $\\text{Im}(w) = 0$, "
            "כלומר $w = \\bar{w}$, או $w = z + \\bar{z}$ לכל $z$."
        ),
    },
    7: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Write $z = a + bi$: $(a+bi)^2 = a^2 - b^2 + 2abi = -4 + 3i$. "
            "System: $a^2 - b^2 = -4$, $2ab = 3$, and $|z|^2 = |-4+3i| = 5$ so $a^2 + b^2 = 5$. "
            "Solving: $a^2 = \\frac{1}{2}$, $b^2 = \\frac{9}{2}$; same sign since $2ab > 0$. "
            "$z = \\pm\\frac{1+3i}{\\sqrt{2}}$.\n\n"
            "**How to think about it:**\n"
            "Two equations from equating parts, plus the modulus gives a third. "
            "Add/subtract to find $a^2$ and $b^2$, then use sign of $2ab$ to pick signs.\n\n"
            "**Common slip:**\n"
            "Picking $a$ and $b$ with opposite signs despite $2ab = 3 > 0$. "
            "Forgetting the $\\pm$ — there are always two square roots.\n\n"
            "**Exam tip:**\n"
            "Verify: $\\left(\\frac{1+3i}{\\sqrt{2}}\\right)^2 = \\frac{1+6i-9}{2} = \\frac{-8+6i}{2}$... "
            "recheck: $= \\frac{-4+3i}{1}$ after simplifying. Always substitute back."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "כותבים $z = a + bi$: $(a+bi)^2 = a^2 - b^2 + 2abi = -4 + 3i$. "
            "מערכת: $a^2 - b^2 = -4$, $2ab = 3$, ו-$|z|^2 = 5$ אז $a^2 + b^2 = 5$. "
            "פתרון: $a^2 = \\frac{1}{2}$, $b^2 = \\frac{9}{2}$; אותו סימן כי $2ab > 0$. "
            "$z = \\pm\\frac{1+3i}{\\sqrt{2}}$.\n\n"
            "**איך לחשוב על זה:**\n"
            "שתי משוואות מהשוואת חלקים, והמודולוס נותן שלישית. "
            "חיבור/חיסור למציאת $a^2$ ו-$b^2$, ואז סימן $2ab$.\n\n"
            "**טעות נפוצה:**\n"
            "בחירת $a$ ו-$b$ בסימנים הפוכים למרות $2ab = 3 > 0$. "
            "שכחת $\\pm$ — תמיד שני שורשים.\n\n"
            "**טיפ לבחינה:**\n"
            "אמתו בהצבה חזרה. תמיד בדקו ש-$z^2$ שווה ל-$w$ המקורי."
        ),
    },
    8: {
        "explanation_en": (
            "**Why this is correct:**\n"
            "The powers of $i$ follow a fixed 4-cycle: "
            "$i^1 = i$, $i^2 = -1$, $i^3 = -i$, $i^4 = 1$, then repeats. "
            "Each row matches its corresponding value.\n\n"
            "**How to think about it:**\n"
            "Memorise the cycle $i \\to -1 \\to -i \\to 1 \\to i$. "
            "Multiply by $i$ each step: $i \\times i = i^2 = -1$, etc.\n\n"
            "**Common slip:**\n"
            "Confusing $i^3 = -i$ with $i^3 = i$ (forgetting the minus). "
            "Thinking $i^4 = i$ instead of $i^4 = 1$.\n\n"
            "**Exam tip:**\n"
            "For any $i^n$, compute $n \\bmod 4$ first. "
            "Remainder 0 → $1$, 1 → $i$, 2 → $-1$, 3 → $-i$. "
            "This table is the foundation for all power-of-$i$ questions."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "חזקות $i$ עוקבות אחר מחזור קבוע של 4: "
            "$i^1 = i$, $i^2 = -1$, $i^3 = -i$, $i^4 = 1$, ואז חוזר. "
            "כל שורה מתאימה לערך שלה.\n\n"
            "**איך לחשוב על זה:**\n"
            "שיננו את המחזור $i \\to -1 \\to -i \\to 1 \\to i$. "
            "כפל ב-$i$ בכל צעד: $i \\times i = i^2 = -1$, וכן הלאה.\n\n"
            "**טעות נפוצה:**\n"
            "בלבול $i^3 = -i$ עם $i^3 = i$ (שכחת המינוס). "
            "חשיבה $i^4 = i$ במקום $i^4 = 1$.\n\n"
            "**טיפ לבחינה:**\n"
            "לכל $i^n$, חשבו $n \\bmod 4$ קודם. "
            "שארית 0 → $1$, 1 → $i$, 2 → $-1$, 3 → $-i$. "
            "טבלה זו היא הבסיס לכל שאלות חזקות $i$."
        ),
    },
}


def apply_updates(data):
    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in SECTION_UPDATES:
            sec.update(SECTION_UPDATES[kind])
        if kind == "worked_example":
            we_idx += 1
            if we_idx in WORKED_EXAMPLES:
                sec.update(WORKED_EXAMPLES[we_idx])
        if kind == "checkpoint":
            if cp_idx in CHECKPOINTS:
                sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
    for q in data["questions"]:
        ord_ = q.get("ord")
        if ord_ in QUESTION_EXPLANATIONS:
            q.update(QUESTION_EXPLANATIONS[ord_])


def main():
    data = json.loads(LESSON.read_text(encoding="utf-8"))
    apply_updates(data)
    LESSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {LESSON}")


if __name__ == "__main__":
    main()
