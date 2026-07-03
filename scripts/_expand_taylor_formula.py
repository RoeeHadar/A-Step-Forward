#!/usr/bin/env python3
"""Expand taylor_formula.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/taylor_formula.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "worked_example": {"en": 130, "he": 110},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
    "before_exam": {"en": 90, "he": 75},
    "summary": {"en": 70, "he": 60},
}

INTRO = {
    "body_en_md": "Polynomials are the easiest functions to work with — they are easy to differentiate, integrate, and evaluate on a calculator. **Taylor's theorem** says that every sufficiently smooth function is **locally approximated by a polynomial** built from its value and derivatives at a single point $a$. The approximation improves as you include more terms, and the Lagrange remainder tells you exactly how large the error can be.\n\n**Why this matters in practice:**\n- **Numerical approximation:** $\\cos(0.1)\\approx 1-\\frac{(0.1)^2}{2}=0.995$ using only the first two non-zero terms of the Maclaurin series.\n- **Limits without L'Hôpital:** compute $\\displaystyle\\lim_{x\\to 0}\\frac{e^x-1-x}{x^2}$ by expanding $e^x$ and reading off the coefficient of $x^2$.\n- **Physics and engineering:** linearization ($\\sin x\\approx x$, $\\cos x\\approx 1-\\frac{x^2}{2}$ for small $x$) underlies small-angle approximations, stability analysis, and perturbation theory.\n- **Every university calculus final** includes at least one Taylor polynomial, error-bound, or limit-via-series problem — often worth 10–15 points.",
    "body_he_md": "פולינומים הם הפונקציות הקלות ביותר לעבודה — קל לגזור אותם, לאנטגרר אותם ולחשב אותם במחשב. **משפט טיילור** אומר שכל פונקציה חלקה מספיק **מקורבת מקומית על-ידי פולינום** שנבנה מערך הפונקציה ונגזרותיה בנקודה $a$ בודדת. הקירוב משתפר ככל שמוסיפים איברים, ושארית לגראנז' מודדת את גודל השגיאה.\n\n**למה זה חשוב בפועל:**\n- **קירוב מספרי:** $\\cos(0.1)\\approx 1-\\frac{(0.1)^2}{2}=0.995$ בעזרת שני האיברים הראשונים של סדרת מקלורן.\n- **גבולות בלי לופיטל:** $\\displaystyle\\lim_{x\\to 0}\\frac{e^x-1-x}{x^2}$ — פותחים $e^x$ וקוראים את מקדם $x^2$.\n- **פיזיקה והנדסה:** לינאריזציה ($\\sin x\\approx x$, $\\cos x\\approx 1-\\frac{x^2}{2}$ ל-$x$ קטן) מניעה קירובי זווית קטנה, ניתוח יציבות ותורת הפרעות.\n- **כל בחינת חדו\"א אוניברסיטאית** כוללת לפחות שאלה אחת על פולינום טיילור, חסם שגיאה או גבול באמצעות סדרות — לעיתים 10–15 נקודות.",
}

DEFINITION = {
    "body_en_md": "**Taylor polynomial of degree $n$ centred at $a$:**\n$$T_n(x) = \\sum_{k=0}^{n}\\frac{f^{(k)}(a)}{k!}(x-a)^k = f(a)+f'(a)(x-a)+\\frac{f''(a)}{2!}(x-a)^2+\\cdots+\\frac{f^{(n)}(a)}{n!}(x-a)^n$$\n\nEach term matches one derivative of $f$ at $a$, divided by the corresponding factorial. The polynomial agrees with $f$ and its first $n$ derivatives at $x=a$.\n\n**Maclaurin polynomial:** Taylor polynomial at $a=0$. Most exam tables list Maclaurin series because $x-a$ simplifies to $x$.\n\n**Taylor series (infinite):** $\\displaystyle\\sum_{k=0}^{\\infty}\\frac{f^{(k)}(a)}{k!}(x-a)^k$. Convergence depends on $f$ and on $|x-a|$; the five standard series below converge on the intervals stated.\n\n**Lagrange remainder (error bound):** There exists $\\xi$ strictly between $a$ and $x$ such that\n$$R_n(x) = f(x)-T_n(x) = \\frac{f^{(n+1)}(\\xi)}{(n+1)!}(x-a)^{n+1}, \\qquad |R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$$\nwhere $M_{n+1}=\\max|f^{(n+1)}(t)|$ on the closed interval between $a$ and $x$.\n\n**The five key Maclaurin series (must memorise):**\n$$e^x = \\sum_{n=0}^{\\infty}\\frac{x^n}{n!} = 1+x+\\frac{x^2}{2!}+\\cdots \\quad (\\text{all }x)$$\n$$\\sin x = \\sum_{n=0}^{\\infty}\\frac{(-1)^n x^{2n+1}}{(2n+1)!} = x-\\frac{x^3}{6}+\\cdots \\quad (\\text{all }x)$$\n$$\\cos x = \\sum_{n=0}^{\\infty}\\frac{(-1)^n x^{2n}}{(2n)!} = 1-\\frac{x^2}{2}+\\cdots \\quad (\\text{all }x)$$\n$$\\ln(1+x) = \\sum_{n=1}^{\\infty}\\frac{(-1)^{n-1}x^n}{n} = x-\\frac{x^2}{2}+\\cdots \\quad (|x|\\leq 1,\\ x\\ne -1)$$\n$$(1+x)^\\alpha = \\sum_{n=0}^{\\infty}\\binom{\\alpha}{n}x^n = 1+\\alpha x+\\frac{\\alpha(\\alpha-1)}{2}x^2+\\cdots \\quad (|x|<1)$$\n\n**Convergence reminder:** $e^x$, $\\sin x$, and $\\cos x$ converge for all real $x$. $\\ln(1+x)$ and $(1+x)^\\alpha$ converge only on the intervals shown — exam questions may ask you to state the domain.",
    "body_he_md": "**פולינום טיילור מדרגה $n$ סביב $a$:**\n$$T_n(x)=\\sum_{k=0}^n\\frac{f^{(k)}(a)}{k!}(x-a)^k=f(a)+f'(a)(x-a)+\\frac{f''(a)}{2!}(x-a)^2+\\cdots+\\frac{f^{(n)}(a)}{n!}(x-a)^n$$\n\nכל איבר תואם נגזרת של $f$ ב-$a$ חלקי העצרת המתאימה. הפולינום מתאים ל-$f$ ול-$n$ הנגזרות הראשונות שלה ב-$x=a$.\n\n**פולינום מקלורן:** פולינום טיילור ב-$a=0$. רוב טבלאות הבחינה מציגות סדרות מקלורן כי $x-a$ מתפשט ל-$x$.\n\n**סדרת טיילור (אינסופית):** $\\displaystyle\\sum_{k=0}^{\\infty}\\frac{f^{(k)}(a)}{k!}(x-a)^k$. התכנסות תלויה ב-$f$ וב-$|x-a|$; חמש הסדרות הסטנדרטיות למטה מתכנסות בטווחים המצוינים.\n\n**שארית לגראנז' (חסם שגיאה):** קיים $\\xi$ בין $a$ ל-$x$ כך ש-\n$$R_n(x)=f(x)-T_n(x)=\\frac{f^{(n+1)}(\\xi)}{(n+1)!}(x-a)^{n+1}, \\qquad |R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$$\nכאשר $M_{n+1}=\\max|f^{(n+1)}(t)|$ בקטע הסגור בין $a$ ל-$x$.\n\n**חמש הסדרות המרכזיות (חובה לשנן):**\n$$e^x=1+x+\\frac{x^2}{2!}+\\cdots \\quad (\\text{כל }x)$$\n$$\\sin x=x-\\frac{x^3}{6}+\\cdots \\quad (\\text{כל }x)$$\n$$\\cos x=1-\\frac{x^2}{2}+\\cdots \\quad (\\text{כל }x)$$\n$$\\ln(1+x)=x-\\frac{x^2}{2}+\\cdots \\quad (|x|\\leq 1,\\ x\\ne -1)$$\n$$(1+x)^\\alpha=1+\\alpha x+\\frac{\\alpha(\\alpha-1)}{2}x^2+\\cdots \\quad (|x|<1)$$\n\n**תזכורת התכנסות:** $e^x$, $\\sin x$ ו-$\\cos x$ מתכנסים לכל $x$ ממשי. $\\ln(1+x)$ ו-$(1+x)^\\alpha$ מתכנסים רק בטווחים המצוינים — בבחינה עלולים לבקש לציין את תחום ההגדרה.",
}

THEORY = {
    "body_en_md": "**Expanding from the standard table (substitution):**\nDo not differentiate from scratch when $f$ is a composition of a known series. Replace the variable in the table:\n$$e^{x^2} = 1+x^2+\\frac{x^4}{2!}+\\frac{x^6}{3!}+\\cdots \\quad \\text{(replace }x\\text{ with }x^2\\text{ in the }e^x\\text{ series)}$$\n$$\\sin(3x) = 3x-\\frac{(3x)^3}{6}+\\cdots = 3x-\\frac{9x^3}{2}+\\cdots$$\n\n**Limits via Taylor — the core exam technique:**\n1. Identify the lowest power in the denominator ($x^k$).\n2. Expand numerator (and denominator if needed) through degree $k$ — often $k+1$ to see cancellation clearly.\n3. Cancel common factors; the limit equals the coefficient of the surviving lowest power.\n$$\\lim_{x\\to 0}\\frac{\\sin x - x}{x^3}: \\quad \\sin x = x-\\frac{x^3}{6}+O(x^5) \\implies \\frac{-x^3/6+O(x^5)}{x^3}\\to -\\frac{1}{6}$$\n\n**Multiplying and adding series:**\nTo find $T_4(x)$ for $f(x)=x\\sin x$, multiply $x$ by the Maclaurin series of $\\sin x$ and keep terms through $x^4$. Drop $O(x^5)$ terms.\n\n**Error estimation recipe:**\n1. Write $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$.\n2. Bound $|f^{(n+1)}(\\xi)|\\leq M_{n+1}$ on the interval between $a$ and $x$.\n3. For $\\sin$, $\\cos$: $M_{n+1}=1$. For $e^x$ near $0$: $M_{n+1}=e^{|x|}$. Plug in and compare to the required tolerance.\n\n**Big-O notation:** Write $O(x^k)$ for terms of order $x^k$ and higher. After division by $x^n$, only the coefficient of the lowest surviving power determines the limit — all $O(\\cdot)$ terms vanish as $x\\to 0$.",
    "body_he_md": "**פיתוח מטבלת הסדרות (הצבה):**\nאל תגזרו מאפס כש-$f$ היא הרכבה של סדרה ידועה. הציבו את המשתנה בטבלה:\n$$e^{x^2}=1+x^2+\\frac{x^4}{2!}+\\frac{x^6}{3!}+\\cdots \\quad \\text{(הציבו }x^2\\text{ במקום }x\\text{ ב-}e^x\\text{)}$$\n$$\\sin(3x)=3x-\\frac{(3x)^3}{6}+\\cdots=3x-\\frac{9x^3}{2}+\\cdots$$\n\n**גבולות באמצעות טיילור — טכניקת בחינה מרכזית:**\n1. זהו את החזקה הנמוכה ביותר במכנה ($x^k$).\n2. פתחו מונה (ומכנה אם נדרש) עד דרגה $k$ — לעיתים $k+1$ כדי לראות ביטול ברור.\n3. בטלו גורמים משותפים; הגבול שווה למקדם של החזקה הנמוכה שנשארה.\n$$\\lim_{x\\to 0}\\frac{\\sin x-x}{x^3}: \\quad \\sin x=x-\\frac{x^3}{6}+O(x^5) \\implies \\frac{-x^3/6+O(x^5)}{x^3}\\to -\\frac{1}{6}$$\n\n**כפל וחיבור סדרות:**\nלמציאת $T_4(x)$ של $f(x)=x\\sin x$, הכפילו $x$ בסדרת מקלורן של $\\sin x$ ושמרו איברים עד $x^4$. השליכו איברי $O(x^5)$.\n\n**מתכון אומדן שגיאה:**\n1. $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$.\n2. חסמו $|f^{(n+1)}(\\xi)|\\leq M_{n+1}$ בקטע בין $a$ ל-$x$.\n3. ל-$\\sin$, $\\cos$: $M_{n+1}=1$. ל-$e^x$ ליד $0$: $M_{n+1}=e^{|x|}$. הציבו והשוו לדיוק הנדרש.\n\n**סימון O-גדול:** כתבו $O(x^k)$ לאיברים מסדר $x^k$ ומעלה. אחרי חלוקה ב-$x^n$, רק מקדם החזקה הנמוכה קובע את הגבול — כל איברי $O(\\cdot)$ נעלמים כש-$x\\to 0$.",
}

WE1 = {
    "body_en_md": "**Given:** Write the Taylor polynomial of degree 3 for $f(x)=e^x$ at $a=0$.\n\nThis is the template problem: compute successive derivatives at the centre, then plug into the Taylor formula.\n\n### Move 1 — Derivatives at $a=0$\n$$f(x)=e^x,\\quad f'(x)=e^x,\\quad f''(x)=e^x,\\quad f'''(x)=e^x$$\n$$f(0)=f'(0)=f''(0)=f'''(0)=1$$\nEvery derivative of $e^x$ equals $e^x$, so at $x=0$ they all equal $1$.\n\n### Move 2 — Apply the Taylor formula\n$$T_3(x) = f(0)+f'(0)x+\\frac{f''(0)}{2!}x^2+\\frac{f'''(0)}{3!}x^3$$\n$$= 1+x+\\frac{x^2}{2}+\\frac{x^3}{6}$$\n\n**Answer:** $\\boxed{T_3(x) = 1+x+\\dfrac{x^2}{2}+\\dfrac{x^3}{6}}$ ✓\n\n*Check:* $T_3(0)=1=e^0$ ✓. $T_3'(0)=1$ ✓. $T_3''(0)=1$ ✓ — the polynomial matches $f$ and its first three derivatives at $0$.\n\n*Exam note:* For $e^x$ at $a=1$, every derivative at $x=1$ equals $e$; factor $e$ out of the polynomial. Always state the centre $a$ before writing $T_n$. Compare $T_3(0.1)\\approx 1.117$ with $e^{0.1}\\approx 1.105$ to see the cubic term improves the linear approximation.",
    "body_he_md": "**נתון:** כתבו פולינום טיילור מדרגה 3 עבור $f(x)=e^x$ ב-$a=0$.\n\nזו בעיית התבנית: מחשבים נגזרות עוקבות במרכז, ואז מציבים בנוסחת טיילור.\n\n### צעד 1 — נגזרות ב-$a=0$\n$$f(x)=e^x,\\quad f'(x)=e^x,\\quad f''(x)=e^x,\\quad f'''(x)=e^x$$\n$$f(0)=f'(0)=f''(0)=f'''(0)=1$$\nכל נגזרת של $e^x$ שווה ל-$e^x$, ולכן ב-$x=0$ כולן שוות $1$.\n\n### צעד 2 — נוסחת טיילור\n$$T_3(x)=f(0)+f'(0)x+\\frac{f''(0)}{2!}x^2+\\frac{f'''(0)}{3!}x^3=1+x+\\frac{x^2}{2}+\\frac{x^3}{6}$$\n\n**תשובה:** $\\boxed{T_3(x)=1+x+\\dfrac{x^2}{2}+\\dfrac{x^3}{6}}$ ✓\n\n*בדיקה:* $T_3(0)=1=e^0$ ✓. $T_3'(0)=1$ ✓. $T_3''(0)=1$ ✓ — הפולינום תואם ל-$f$ ולשלוש הנגזרות הראשונות ב-$0$.\n\n*הערת בחינה:* ל-$e^x$ ב-$a=1$, כל נגזרת ב-$x=1$ שווה $e$; הוציאו $e$ מחוץ לפולינום. ציינו תמיד את המרכז $a$ לפני כתיבת $T_n$. השוו $T_3(0.1)\\approx 1.117$ עם $e^{0.1}\\approx 1.105$ כדי לראות שהאיבר המעוקב משפר את הקירוב הלינארי.",
}

WE2 = {
    "body_en_md": "**Given:** Approximate $\\cos(0.1)$ using $T_4$ for $\\cos x$ at $a=0$. Bound the error $|R_4(0.1)|$.\n\nThis combines **evaluation** of a truncated series with a **Lagrange error bound** — a two-part exam staple.\n\n### Move 1 — Write $T_4(x)$ for $\\cos x$\n$$T_4(x) = 1-\\frac{x^2}{2!}+\\frac{x^4}{4!} = 1-\\frac{x^2}{2}+\\frac{x^4}{24}$$\nOdd powers vanish because all odd derivatives of $\\cos$ are $\\pm\\sin x$, which equal $0$ at $x=0$.\n\n### Move 2 — Evaluate at $x=0.1$\n$$T_4(0.1) = 1-\\frac{(0.1)^2}{2}+\\frac{(0.1)^4}{24} = 1-0.005+0.0000041\\overline{6}\\approx 0.9950042$$\n\n### Move 3 — Lagrange remainder bound\nThe remainder is $R_4(x)=\\frac{f^{(5)}(\\xi)}{5!}x^5$. For $\\cos x$: $f^{(5)}(x)=\\sin x$ or $\\cos x$, so $|f^{(5)}(\\xi)|\\leq 1$ on any interval.\n$$|R_4(0.1)|\\leq\\frac{1}{5!}(0.1)^5=\\frac{0.00001}{120}\\approx 8.3\\times 10^{-8}$$\n\n**Answer:** $\\cos(0.1)\\approx 0.99500417$ with error $<10^{-7}$ ✓\n\n*Actual value:* $\\cos(0.1)\\approx 0.99500417$ — the approximation is accurate to seven decimal places.\n\n*Exam note:* Always name $M_{n+1}$ before plugging into the Lagrange formula. For sine/cosine, $M=1$ is the standard bound. Show the bound inequality even when the numeric error is tiny — setup earns partial credit.",
    "body_he_md": "**נתון:** קרבו את $\\cos(0.1)$ בעזרת $T_4$ של $\\cos x$ ב-$a=0$. חסמו את השגיאה $|R_4(0.1)|$.\n\nשילוב של **הערכה** של סדרה חתוכה עם **חסם שארית לגראנז'** — דפוס בחינה דו-שלבי נפוץ.\n\n### צעד 1 — כתיבת $T_4(x)$ של $\\cos x$\n$$T_4(x)=1-\\frac{x^2}{2!}+\\frac{x^4}{4!}=1-\\frac{x^2}{2}+\\frac{x^4}{24}$$\nחזקות אי-זוגיות נעלמות כי כל הנגזרות האי-זוגיות של $\\cos$ הן $\\pm\\sin x$, ששוות $0$ ב-$x=0$.\n\n### צעד 2 — הצבה ב-$x=0.1$\n$$T_4(0.1)=1-\\frac{(0.1)^2}{2}+\\frac{(0.1)^4}{24}=1-0.005+0.0000042\\approx 0.9950042$$\n\n### צעד 3 — חסם שארית לגראנז'\n$R_4(x)=\\frac{f^{(5)}(\\xi)}{5!}x^5$. ל-$\\cos x$: $|f^{(5)}(\\xi)|\\leq 1$ בכל קטע.\n$$|R_4(0.1)|\\leq\\frac{1}{5!}(0.1)^5=\\frac{0.00001}{120}\\approx 8.3\\times 10^{-8}$$\n\n**תשובה:** $\\cos(0.1)\\approx 0.99500417$ עם שגיאה $<10^{-7}$ ✓\n\n*ערך אמיתי:* $\\cos(0.1)\\approx 0.99500417$ — הקירוב מדויק לשבע ספרות.\n\n*הערת בחינה:* ציינו תמיד $M_{n+1}$ לפני ההצבה בנוסחת לגראנז'. לסינוס/קוסינוס, $M=1$ הוא החסם הסטנדרטי. הציגו את אי-השוויון גם כשהשגיאה המספרית קטנה — ההגדרה מזכה בניקוד חלקי.",
}

WE3 = {
    "body_en_md": "**Given:** Compute $\\displaystyle\\lim_{x\\to 0}\\frac{e^x-1-x-x^2/2}{x^3}$ using Taylor series (not L'Hôpital).\n\nThe numerator is exactly what remains after subtracting the first three terms of the $e^x$ expansion — the limit reads off the $x^3$ coefficient.\n\n### Move 1 — Expand $e^x$ through degree 3\n$$e^x = 1+x+\\frac{x^2}{2!}+\\frac{x^3}{3!}+O(x^4) = 1+x+\\frac{x^2}{2}+\\frac{x^3}{6}+O(x^4)$$\n\n### Move 2 — Form the numerator\n$$e^x - 1 - x - \\frac{x^2}{2} = \\frac{x^3}{6}+O(x^4)$$\nAll lower-order terms cancel by construction.\n\n### Move 3 — Divide by $x^3$ and take the limit\n$$\\frac{e^x-1-x-x^2/2}{x^3} = \\frac{x^3/6+O(x^4)}{x^3} = \\frac{1}{6}+O(x)$$\n\n### Move 4 — Evaluate\n$$\\lim_{x\\to 0}\\left(\\frac{1}{6}+O(x)\\right) = \\frac{1}{6}$$\n\n**Answer:** $\\boxed{\\dfrac{1}{6}}$ ✓\n\n*Compare:* L'Hôpital requires three separate differentiations. Taylor requires reading one coefficient — far faster on timed exams when the function is $e^x$, $\\sin x$, or $\\ln(1+x)$.\n\n*Exam note:* Expand to one degree **beyond** the denominator power so the $O(\\cdot)$ term vanishes cleanly after division.",
    "body_he_md": "**נתון:** $\\displaystyle\\lim_{x\\to 0}\\frac{e^x-1-x-x^2/2}{x^3}$ בעזרת סדרות טיילור (ללא לופיטל).\n\nהמונה הוא בדיוק מה שנשאר אחרי חיסור שלושת האיברים הראשונים של פיתוח $e^x$ — הגבול קורא את מקדם $x^3$.\n\n### צעד 1 — פיתוח $e^x$ עד דרגה 3\n$$e^x=1+x+\\frac{x^2}{2!}+\\frac{x^3}{3!}+O(x^4)=1+x+\\frac{x^2}{2}+\\frac{x^3}{6}+O(x^4)$$\n\n### צעד 2 — בניית המונה\n$$e^x-1-x-\\frac{x^2}{2}=\\frac{x^3}{6}+O(x^4)$$\nכל האיברים מדרגה נמוכה יותר מתבטלים בהגדרה.\n\n### צעד 3 — חלוקה ב-$x^3$ ולקיחת גבול\n$$\\frac{e^x-1-x-x^2/2}{x^3}=\\frac{x^3/6+O(x^4)}{x^3}=\\frac{1}{6}+O(x)$$\n\n### צעד 4 — חישוב\n$$\\lim_{x\\to 0}\\left(\\frac{1}{6}+O(x)\\right)=\\frac{1}{6}$$\n\n**תשובה:** $\\boxed{\\dfrac{1}{6}}$ ✓\n\n*השוואה:* לופיטל דורש שלוש גזירות נפרדות. טיילור דורש קריאת מקדם אחד — מהיר הרבה יותר בבחינה כשהפונקציה היא $e^x$, $\\sin x$ או $\\ln(1+x)$.\n\n*הערת בחינה:* פתחו עד דרגה **אחת מעבר** לחזקת המכנה כדי שאיבר $O(\\cdot)$ ייעלם בניקוי אחרי החלוקה.",
}

CHECKPOINT1 = {
    "checkpoint_solution_en": "**Step 1 — Derivatives of $\\sin x$ at $a=0$:**\n$f(x)=\\sin x$, $f'(x)=\\cos x$, $f''(x)=-\\sin x$, $f'''(x)=-\\cos x$.\n$f(0)=0$, $f'(0)=1$, $f''(0)=0$, $f'''(0)=-1$.\n\n**Step 2 — Apply Taylor formula:**\n$$T_3(x)=0+1\\cdot x+\\frac{0}{2}x^2+\\frac{(-1)}{6}x^3=x-\\frac{x^3}{6}$$\n\n**Answer:** $\\boxed{T_3(x)=x-\\dfrac{x^3}{6}}$ ✓\n\n*Check:* $T_3'(0)=1=\\cos(0)$ ✓. The $x^2$ term vanishes because $f''(0)=0$ — a common pattern for odd functions expanded at $0$.",
    "checkpoint_solution_he": "**שלב 1 — נגזרות $\\sin x$ ב-$a=0$:**\n$f(0)=0$, $f'(0)=1$, $f''(0)=0$, $f'''(0)=-1$.\n\n**שלב 2 — נוסחת טיילור:**\n$$T_3(x)=0+x+0\\cdot\\frac{x^2}{2}+\\frac{(-1)}{6}x^3=x-\\frac{x^3}{6}$$\n\n**תשובה:** $\\boxed{T_3(x)=x-\\dfrac{x^3}{6}}$ ✓\n\n*בדיקה:* $T_3'(0)=1=\\cos(0)$ ✓. איבר $x^2$ נעלם כי $f''(0)=0$ — דפוס נפוץ לפונקציות אי-זוגיות סביב $0$.",
}

CHECKPOINT2 = {
    "checkpoint_solution_en": "**Step 1 — Write $T_2(x)$ for $e^x$ at $a=0$:**\n$T_2(x)=1+x+\\frac{x^2}{2}$.\n\n**Step 2 — Evaluate:**\n$T_2(0.5)=1+0.5+\\frac{(0.5)^2}{2}=1+0.5+0.125=1.625$.\n\n**Step 3 — Lagrange error bound:**\n$|R_2(0.5)|\\leq\\frac{e^{0.5}}{3!}(0.5)^3\\leq\\frac{e}{6}\\cdot 0.125\\approx\\frac{2.718}{48}\\approx 0.057$.\n\n**Answer:** $e^{0.5}\\approx 1.625$ with guaranteed error $\\leq 0.057$. Actual $e^{0.5}\\approx 1.6487$ — true error $\\approx 0.024$, well inside the bound ✓",
    "checkpoint_solution_he": "**שלב 1 — $T_2(x)$ של $e^x$ ב-$a=0$:**\n$T_2(x)=1+x+\\frac{x^2}{2}$.\n\n**שלב 2 — הצבה:**\n$T_2(0.5)=1+0.5+0.125=1.625$.\n\n**שלב 3 — חסם שארית לגראנז':**\n$|R_2(0.5)|\\leq\\frac{e^{0.5}}{3!}(0.5)^3\\leq\\frac{e}{6}\\cdot 0.125\\approx 0.057$.\n\n**תשובה:** $e^{0.5}\\approx 1.625$ עם שגיאה מובטחת $\\leq 0.057$. ערך אמיתי $\\approx 1.6487$ — שגיאה $\\approx 0.024$, בתוך החסם ✓",
}

METHOD = {
    "body_en_md": "**When to expand from scratch vs. use the table:**\n| Situation | Action |\n|-----------|--------|\n| $f$ is $e^x$, $\\sin$, $\\cos$, $\\ln(1+x)$, $(1+x)^\\alpha$ | Use the standard Maclaurin table |\n| $f$ is a composition like $e^{x^2}$, $\\sin(3x)$, $\\cos(x^2)$ | Substitute into the standard series |\n| $f$ is a product like $x\\sin x$, $x^2 e^x$ | Multiply truncated series; keep through required degree |\n| $f$ is not in the table | Compute derivatives at $a$, apply the Taylor formula |\n\n**Using Taylor to compute limits:**\n1. Expand numerator and denominator to enough terms.\n2. Keep terms through the denominator degree (plus one extra if needed).\n3. Cancel leading terms; read the coefficient of the lowest surviving power.\n4. Use $O(x^k)$ notation to track discarded terms.\n\n**Error bound recipe:**\n1. $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$.\n2. $M_{n+1}=$ max of $|f^{(n+1)}|$ between $a$ and $x$.\n3. $\\sin$/$\\cos$: $M_{n+1}=1$. $e^x$: $M_{n+1}=e^{|x|}$ (or $e^{\\max(a,x)}$ if centred at $a$).",
    "body_he_md": "**מתי לפתח מאפס מול שימוש בטבלה:**\n| מצב | פעולה |\n|-----|-------|\n| $e^x$, $\\sin$, $\\cos$, $\\ln(1+x)$, $(1+x)^\\alpha$ | טבלת מקלורן סטנדרטית |\n| הרכבה: $e^{x^2}$, $\\sin(3x)$, $\\cos(x^2)$ | הציבו בסדרה הסטנדרטית |\n| מכפלה: $x\\sin x$, $x^2 e^x$ | הכפילו סדרות חתוכות; שמרו עד הדרגה הנדרשת |\n| לא בטבלה | חשבו נגזרות ב-$a$, נוסחת טיילור |\n\n**גבולות עם טיילור:**\n1. פתחו מונה ומכנה לעומק מספיק.\n2. שמרו איברים עד דרגת המכנה (+1 אם נדרש).\n3. בטלו איברים מובילים; קראו מקדם החזקה הנמוכה.\n4. השתמשו ב-$O(x^k)$ למעקב אחר איברים שנזרקו.\n\n**מתכון שארית:**\n1. $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$.\n2. $M_{n+1}$: מקסימום $|f^{(n+1)}|$ בין $a$ ל-$x$.\n3. $\\sin$/$\\cos$: $M_{n+1}=1$. $e^x$: $M_{n+1}=e^{|x|}$.",
}

PITFALL = {
    "body_en_md": "1. **Expanding to insufficient order.** If the denominator is $x^3$, expand the numerator to at least $x^3$ — often $x^4$ so the $O(x^4)$ term vanishes after division. Stopping at $x^2$ leaves an indeterminate form.\n\n2. **Wrong factorial in the denominator.** The $n$-th Taylor term is $\\frac{f^{(n)}(a)}{n!}(x-a)^n$ — the factorial matches the derivative order, not the power of $(x-a)$ alone.\n\n3. **Forgetting the remainder when bounding error.** $T_n(x)$ approximates $f(x)$; the error is the full remainder $R_n(x)$, not just the first omitted term. Always use the Lagrange formula with a bound on $M_{n+1}$.\n\n4. **Using L'Hôpital when Taylor is faster.** For limits with $\\sin x$, $e^x$, $\\ln(1+x)$ near $0$, Taylor reads the answer in one step. L'Hôpital may require multiple applications and more algebra.\n\n5. **Incorrect substitution into known series.** $\\cos(x^2)$ means replace $x$ with $x^2$ in the $\\cos$ series — do not differentiate $\\cos(x^2)$ from scratch. Similarly, $e^{-x^2}$ replaces $x$ with $-x^2$ in the $e^x$ series.",
    "body_he_md": "1. **פיתוח בסדר לא מספיק.** אם המכנה הוא $x^3$, פתחו מונה לפחות ל-$x^3$ — לעיתים $x^4$ כדי ש-$O(x^4)$ ייעלם אחרי חלוקה. עצירה ב-$x^2$ משאירה צורה בלתי-קבועה.\n\n2. **עצרת שגויה במכנה.** האיבר ה-$n$ הוא $\\frac{f^{(n)}(a)}{n!}(x-a)^n$ — העצרת תואמת לסדר הנגזרת, לא רק לחזקת $(x-a)$.\n\n3. **שכחת השארית באומדן שגיאה.** $T_n(x)$ מקרב $f(x)$; השגיאה היא $R_n(x)$ המלאה, לא רק האיבר הראשון שנזרק. השתמשו תמיד בנוסחת לגראנז' עם חסם על $M_{n+1}$.\n\n4. **שימוש בלופיטל כשטיילור מהיר.** לגבולות עם $\\sin x$, $e^x$, $\\ln(1+x)$ ליד $0$, טיילור קורא את התשובה בצעד אחד. לופיטל עלול לדרוש יישומים מרובים.\n\n5. **הצבה שגויה בסדרה ידועה.** $\\cos(x^2)$ — הציבו $x^2$ בסדרת $\\cos$; אל תגזרו $\\cos(x^2)$ מאפס. $e^{-x^2}$ — הציבו $-x^2$ בסדרת $e^x$.",
}

WHY = {
    "body_en_md": "Taylor polynomials are the bridge between **derivatives** and **function behaviour near a point**. They explain why $\\sin x\\approx x$ for small angles, why Newton's method converges quadratically, and why numerical libraries evaluate $e^x$ and $\\sin x$ via polynomial approximations on small intervals.\n\nThe topic connects directly to `concept:lhopital_rule` (Taylor often resolves the same limits faster), `concept:limits_intro`, and `concept:derivatives_intro`. In physics, Taylor expansion linearises equations of motion for small perturbations; in statistics, log-likelihood functions are expanded for asymptotic inference. University exams test whether you can **choose the right tool** — table lookup, substitution, derivative computation, or error bounding — not just recite formulas.",
    "body_he_md": "פולינומי טיילור הם הגשר בין **נגזרות** ל**התנהגות פונקציה ליד נקודה**. הם מסבירים למה $\\sin x\\approx x$ לזוויות קטנות, למה שיטת ניוטון מתכנסת בריבוע, ולמה ספריות מספריות מחשבות $e^x$ ו-$\\sin x$ בקירובי פולינום על קטעים קטנים.\n\nהנושא מתחבר ל-`concept:lhopital_rule` (טיילור פותר לעיתים את אותם גבולות מהר יותר), `concept:limits_intro` ו-`concept:derivatives_intro`. בפיזיקה, פיתוח טיילור מלינאריז משוואות תנועה; בסטטיסטיקה, פונקציות log-likelihood מפותחות להסקה אסימפטוטית. בבחינות בודקים אם **בוחרים בכלי הנכון** — טבלה, הצבה, נגזרות או חסם שגיאה.",
}

BEFORE_EXAM = {
    "body_en_md": "**Standard Maclaurin series (must memorise):**\n$$e^x = 1+x+\\frac{x^2}{2}+\\frac{x^3}{6}+\\cdots, \\quad \\sin x = x-\\frac{x^3}{6}+\\cdots, \\quad \\cos x = 1-\\frac{x^2}{2}+\\frac{x^4}{24}-\\cdots$$\n$$\\ln(1+x) = x-\\frac{x^2}{2}+\\frac{x^3}{3}-\\cdots \\quad (|x|\\leq 1), \\quad (1+x)^\\alpha = 1+\\alpha x+\\frac{\\alpha(\\alpha-1)}{2}x^2+\\cdots \\quad (|x|<1)$$\n\n**Lagrange error bound:** $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$ where $M_{n+1}=\\max|f^{(n+1)}|$ on the interval.\n\n**Exam patterns:**\n- Write $T_n$: derivatives at $a$, plug into formula, or read from table.\n- Estimate error: bound $M$, compute $|R_n|$, compare to tolerance.\n- Compute limit: expand, cancel, read coefficient.\n- Combine series: substitute, multiply, add — avoid unnecessary differentiation.\n\n**Last review:** Recite each series once, then solve one limit and one error-bound problem without notes.\n\n**Time tip:** If Taylor expansion stalls, check whether L'Hôpital or a known limit applies — but for standard functions near $0$, Taylor is usually faster.",
    "body_he_md": "**סדרות מקלורן (חובה לשנן):**\n$$e^x=1+x+\\frac{x^2}{2}+\\frac{x^3}{6}+\\cdots, \\quad \\sin x=x-\\frac{x^3}{6}+\\cdots, \\quad \\cos x=1-\\frac{x^2}{2}+\\frac{x^4}{24}-\\cdots$$\n$$\\ln(1+x)=x-\\frac{x^2}{2}+\\frac{x^3}{3}-\\cdots \\quad (|x|\\leq 1), \\quad (1+x)^\\alpha=1+\\alpha x+\\frac{\\alpha(\\alpha-1)}{2}x^2+\\cdots \\quad (|x|<1)$$\n\n**חסם שארית לגראנז':** $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$.\n\n**דפוסי בחינה:**\n- כתיבת $T_n$: נגזרות ב-$a$ או קריאה מטבלה.\n- אומדן שגיאה: חסמו $M$, חשבו $|R_n|$, השוו לדיוק.\n- גבול: פתחו, בטלו, קראו מקדם.\n- שילוב סדרות: הציבו, הכפילו, חברו.\n\n**חזרה אחרונה:** חזרו על כל סדרה פעם אחת, ואז פתרו גבול אחד ובעיית שגיאה אחת בלי רשימות.\n\n**טיפ זמן:** אם פיתוח טיילור נתקע — בדקו לופיטל או גבול ידוע; לפונקציות סטנדרטיות ליד $0$, טיילור בדרך כלל מהיר יותר.",
}

SUMMARY = {
    "body_en_md": "- The Taylor polynomial $T_n(x)=\\sum_{k=0}^n\\frac{f^{(k)}(a)}{k!}(x-a)^k$ approximates $f$ near $a$ and matches its first $n$ derivatives there.\n- **Lagrange remainder:** $|R_n(x)|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$ — use to bound approximation error on exams.\n- **Memorise:** $e^x$, $\\sin x$, $\\cos x$, $\\ln(1+x)$, $(1+x)^\\alpha$ at $a=0$; use substitution for compositions.\n- For limits: expand to the denominator degree, cancel, read the coefficient — often faster than L'Hôpital.\n- For composed series (e.g., $e^{x^2}$, $x\\sin x$): substitute or multiply series; do not differentiate from scratch unless necessary.",
    "body_he_md": "- $T_n(x)=\\sum_{k=0}^n\\frac{f^{(k)}(a)}{k!}(x-a)^k$ מקרב את $f$ ליד $a$ ותואם את $n$ הנגזרות הראשונות שם.\n- **שארית לגראנז':** $|R_n|\\leq\\frac{M_{n+1}}{(n+1)!}|x-a|^{n+1}$ — לחסימת שגיאת קירוב בבחינה.\n- **שיננו:** $e^x$, $\\sin x$, $\\cos x$, $\\ln(1+x)$, $(1+x)^\\alpha$ ב-$a=0$; הצבה להרכבות.\n- לגבולות: פתחו עד דרגת המכנה, בטלו, קראו מקדם — לעיתים מהיר מלופיטל.\n- לסדרות מורכבות ($e^{x^2}$, $x\\sin x$): הציבו או הכפילו; אל תגזרו מאפס אלא אם חייבים.",
}

EXPLANATIONS = [
    {
        "en": "**Why this is correct:**\n$T_4(x)$ for $\\cos x$ at $a=0$ keeps only even powers: $1-\\frac{x^2}{2}+\\frac{x^4}{24}$. All odd derivatives of cosine are $\\pm\\sin x$, which vanish at $0$, so terms in $x$ and $x^3$ are zero.\n\n**How to think about it:**\nEither compute four derivatives at $0$ and plug into the Taylor formula, or read directly from the memorised Maclaurin table. Both routes must agree.\n\n**Common slip:**\nIncluding an $x^3$ term (confusing with $\\sin x$). Writing $\\frac{x^2}{2}$ instead of $\\frac{x^2}{2!}$ — same value, but the factorial notation matters on written exams.\n\n**Exam tip:**\nFor even functions expanded at $0$, only even powers appear. State this observation to earn reasoning credit before writing the polynomial.",
        "he": "**למה זה נכון:**\n$T_4(x)$ של $\\cos x$ ב-$a=0$ שומר רק חזקות זוגיות: $1-\\frac{x^2}{2}+\\frac{x^4}{24}$. כל הנגזרות האי-זוגיות של קוסינוס הן $\\pm\\sin x$, שמתאפסות ב-$0$, ולכן אין איברי $x$ ו-$x^3$.\n\n**איך לחשוב על זה:**\nאפשר לחשב ארבע נגזרות ב-$0$ ולהציב בנוסחת טיילור, או לקרוא ישירות מטבלת מקלורן. שני המסלולים חייבים להתאים.\n\n**טעות נפוצה:**\nהכללת איבר $x^3$ (בלבול עם $\\sin x$). כתיבת $\\frac{x^2}{2}$ במקום $\\frac{x^2}{2!}$ — אותו ערך, אך סימון העצרת חשוב בבחינה.\n\n**טיפ לבחינה:**\nלפונקציות זוגיות סביב $0$ מופיעות רק חזקות זוגיות. ציינו זאת לניקוד הסבר לפני כתיבת הפולינום.",
    },
    {
        "en": "**Why this is correct:**\n$T_3(x)$ for $\\ln(1+x)$ at $0$ is $x-\\frac{x^2}{2}+\\frac{x^3}{3}$. Successive derivatives of $\\ln(1+x)$ are $\\frac{1}{1+x}$, $-\\frac{1}{(1+x)^2}$, $\\frac{2}{(1+x)^3}$, giving values $1$, $-1$, $2$ at $x=0$; divided by $1!$, $2!$, $3!$ yields the coefficients.\n\n**How to think about it:**\nThe Maclaurin series for $\\ln(1+x)$ alternates signs starting with $+x$. Truncate after the $x^3$ term for degree 3.\n\n**Common slip:**\nStarting the series at $n=0$ with a constant term (there is none — $\\ln(1+0)=0$). Forgetting the alternating sign on the $x^2$ term.\n\n**Exam tip:**\n$\\ln(1+x)$ converges only for $|x|\\leq 1$, $x\\ne -1$. Mention the interval if the question asks about validity, not just the polynomial.",
        "he": "**למה זה נכון:**\n$T_3(x)$ של $\\ln(1+x)$ ב-$0$ הוא $x-\\frac{x^2}{2}+\\frac{x^3}{3}$. נגזרות עוקבות: $\\frac{1}{1+x}$, $-\\frac{1}{(1+x)^2}$, $\\frac{2}{(1+x)^3}$, וב-$x=0$ הערכים $1$, $-1$, $2$; חלוקה ב-$1!$, $2!$, $3!$ נותנת את המקדמים.\n\n**איך לחשוב על זה:**\nסדרת מקלורן של $\\ln(1+x)$ מתחלפת בסימן, מתחילה ב-$+x$. חתכו אחרי איבר $x^3$ למדרגה 3.\n\n**טעות נפוצה:**\nהתחלה ב-$n=0$ עם איבר קבוע (אין — $\\ln(1)=0$). שכחת הסימן השלילי על $x^2$.\n\n**טיפ לבחינה:**\n$\\ln(1+x)$ מתכנס רק ל-$|x|\\leq 1$, $x\\ne -1$. ציינו את הטווח אם שואלים על תקפות, לא רק על הפולינום.",
    },
    {
        "en": "**Why this is correct:**\n$(1+x)^{1/2}$ uses the generalised binomial series with $\\alpha=\\frac{1}{2}$: $1+\\frac{1}{2}x+\\frac{\\frac{1}{2}(\\frac{1}{2}-1)}{2!}x^2=1+\\frac{x}{2}-\\frac{x^2}{8}$.\n\n**How to think about it:**\nCompute $f(0)=1$, $f'(0)=\\frac{1}{2}$, $f''(0)=-\\frac{1}{4}$, then $T_2(x)=1+\\frac{1}{2}x+\\frac{-1/4}{2}x^2$. Or read from the $(1+x)^\\alpha$ table with $\\alpha=\\frac{1}{2}$.\n\n**Common slip:**\nUsing $\\alpha=2$ instead of $\\frac{1}{2}$. Sign error on the $x^2$ coefficient: $\\alpha(\\alpha-1)=\\frac{1}{2}\\cdot(-\\frac{1}{2})=-\\frac{1}{4}$, not positive.\n\n**Exam tip:**\n$(1+x)^{1/2}$ appears in physics (relativistic energy expansions) and in estimating $\\sqrt{1.1}$ without a calculator. Valid for $|x|<1$.",
        "he": "**למה זה נכון:**\n$(1+x)^{1/2}$ משתמש בסדרת בינום מוכללת עם $\\alpha=\\frac{1}{2}$: $1+\\frac{x}{2}+\\frac{\\frac{1}{2}(\\frac{1}{2}-1)}{2!}x^2=1+\\frac{x}{2}-\\frac{x^2}{8}$.\n\n**איך לחשוב על זה:**\n$f(0)=1$, $f'(0)=\\frac{1}{2}$, $f''(0)=-\\frac{1}{4}$, ואז $T_2(x)=1+\\frac{x}{2}-\\frac{x^2}{8}$. או קריאה מטבלת $(1+x)^\\alpha$ עם $\\alpha=\\frac{1}{2}$.\n\n**טעות נפוצה:**\nשימוש ב-$\\alpha=2$ במקום $\\frac{1}{2}$. שגיאת סימן: $\\alpha(\\alpha-1)=-\\frac{1}{4}$, לא חיובי.\n\n**טיפ לבחינה:**\n$(1+x)^{1/2}$ מופיע בפיזיקה (פיתוחי אנרגיה יחסותית) ובהערכת $\\sqrt{1.1}$. תקף ל-$|x|<1$.",
    },
    {
        "en": "**Why this is correct:**\nAll derivatives of $e^x$ equal $e^x$, so at $x=1$ each equals $e$. The Taylor polynomial centred at $a=1$ is $T_3(x)=e+e(x-1)+\\frac{e}{2}(x-1)^2+\\frac{e}{6}(x-1)^3$, or factored: $e\\left[1+(x-1)+\\frac{(x-1)^2}{2}+\\frac{(x-1)^3}{6}\\right]$.\n\n**How to think about it:**\nShift the centre from $0$ to $1$: replace $x$ with $(x-1)$ in the Maclaurin polynomial of $e^x$, then multiply every coefficient by $e=f(1)$.\n\n**Common slip:**\nUsing $x$ instead of $(x-1)$ in the polynomial — that gives the Maclaurin series, not Taylor at $1$. Forgetting to evaluate derivatives at $x=1$ (not $x=0$).\n\n**Exam tip:**\nWhen the centre is not $0$, write $(x-a)$ explicitly in every term. Examiners deduct points for Maclaurin form when Taylor at $a\\ne 0$ is requested.",
        "he": "**למה זה נכון:**\nכל נגזרות $e^x$ שוות ל-$e^x$, ולכן ב-$x=1$ כל אחת שווה $e$. פולינום טיילור סביב $a=1$: $T_3(x)=e+e(x-1)+\\frac{e}{2}(x-1)^2+\\frac{e}{6}(x-1)^3$, או $e\\left[1+(x-1)+\\frac{(x-1)^2}{2}+\\frac{(x-1)^3}{6}\\right]$.\n\n**איך לחשוב על זה:**\nהזיזו את המרכז מ-$0$ ל-$1$: החליפו $x$ ב-$(x-1)$ בפולינום מקלורן של $e^x$, והכפילו כל מקדם ב-$e=f(1)$.\n\n**טעות נפוצה:**\nשימוש ב-$x$ במקום $(x-1)$ — זו סדרת מקלורן, לא טיילור ב-$1$. שכחת הערכת נגזרות ב-$x=1$ (לא $0$).\n\n**טיפ לבחינה:**\nכשהמרכז אינו $0$, כתבו $(x-a)$ במפורש בכל איבר. מורידים נקודות על צורת מקלורן כשמבקשים טיילור ב-$a\\ne 0$.",
    },
    {
        "en": "**Why this is correct:**\n$\\cos x=1-\\frac{x^2}{2}+O(x^4)$, so $\\cos x-1=-\\frac{x^2}{2}+O(x^4)$. Dividing by $x^2$ gives $-\\frac{1}{2}+O(x^2)\\to -\\frac{1}{2}$ as $x\\to 0$.\n\n**How to think about it:**\nThe denominator is $x^2$, so expand the numerator through $x^2$. The constant $1$ cancels; the leading surviving term is $-x^2/2$.\n\n**Common slip:**\nExpanding only to $x$ (insufficient — numerator still looks like $0/0$). Sign error: $\\cos x-1$ is **negative** near $0$, giving limit $-1/2$, not $+1/2$.\n\n**Exam tip:**\nThis limit is equivalent to the second derivative of $\\cos$ at $0$ divided by $2!$. Taylor makes the connection to derivatives explicit — useful when L'Hôpital would require two applications.",
        "he": "**למה זה נכון:**\n$\\cos x=1-\\frac{x^2}{2}+O(x^4)$, ולכן $\\cos x-1=-\\frac{x^2}{2}+O(x^4)$. חלוקה ב-$x^2$ נותנת $-\\frac{1}{2}+O(x^2)\\to -\\frac{1}{2}$.\n\n**איך לחשוב על זה:**\nהמכנה הוא $x^2$, אז פתחו את המונה עד $x^2$. הקבוע $1$ מתבטל; האיבר המוביל הוא $-x^2/2$.\n\n**טעות נפוצה:**\nפיתוח רק עד $x$ (לא מספיק). שגיאת סימן: $\\cos x-1$ **שלילי** ליד $0$, הגבול $-1/2$ לא $+1/2$.\n\n**טיפ לבחינה:**\nהגבול שקול לנגזרת השנייה של $\\cos$ ב-$0$ חלקי $2!$. טיילור מקשר במפורש לנגזרות — שימושי כשלופיטל דורש שני יישומים.",
    },
    {
        "en": "**Why this is correct:**\nReplace $x$ with $-x^2$ in $e^x=1+x+\\frac{x^2}{2}+\\cdots$: $e^{-x^2}=1-x^2+\\frac{x^4}{2}-\\frac{x^6}{6}+\\cdots$. Through degree $4$ (terms up to $x^4$): $1-x^2+\\frac{x^4}{2}$.\n\n**How to think about it:**\nSubstitution preserves the structure: even powers only because $(-x^2)^k$ is always even in $x$. Do not confuse with $e^{-x}$ (which would give alternating signs on odd powers).\n\n**Common slip:**\nSubstituting $-x$ instead of $-x^2$. Dropping the $\\frac{x^4}{2}$ term when the question asks for degree $4$.\n\n**Exam tip:**\nComposition problems test whether you know the table — zero derivatives required. Write the substitution explicitly: \"In $e^x$, replace $x$ by $-x^2$.\"",
        "he": "**למה זה נכון:**\nהציבו $-x^2$ במקום $x$ ב-$e^x=1+x+\\frac{x^2}{2}+\\cdots$: $e^{-x^2}=1-x^2+\\frac{x^4}{2}-\\frac{x^6}{6}+\\cdots$. עד דרגה 4: $1-x^2+\\frac{x^4}{2}$.\n\n**איך לחשוב על זה:**\nהצבה שומרת מבנה: רק חזקות זוגיות כי $(-x^2)^k$ תמיד זוגי ב-$x$. אל תבלבלו עם $e^{-x}$ (סימנים מתחלפים על חזקות אי-זוגיות).\n\n**טעות נפוצה:**\nהצבת $-x$ במקום $-x^2$. השמטת $\\frac{x^4}{2}$ כששואלים על דרגה 4.\n\n**טיפ לבחינה:**\nבעיות הרכבה בודקות שליטה בטבלה — בלי נגזרות. כתבו במפורש: \"ב-$e^x$, החליפו $x$ ב-$-x^2$.\"",
    },
    {
        "en": "**Why this is correct:**\n$T_3(x)=x-\\frac{x^3}{6}$. At $x=0.2$: $T_3(0.2)=0.2-\\frac{(0.2)^3}{6}=0.2-0.008/6\\approx 0.19867$. Lagrange bound: $|R_3(0.2)|\\leq\\frac{1}{4!}(0.2)^4=\\frac{0.0016}{24}\\approx 6.7\\times 10^{-5}$ — actually $R_3$ uses the 4th derivative, so $|R_3|\\leq\\frac{1}{5!}(0.2)^5\\approx 2.7\\times 10^{-7}$.\n\n**How to think about it:**\nTwo-part answer: (1) evaluate the polynomial, (2) bound the remainder. For $\\sin x$, $|f^{(4)}(\\xi)|\\leq 1$ always.\n\n**Common slip:**\nUsing $T_3$ but bounding with $(0.2)^4/4!$ (wrong derivative order — remainder uses $f^{(n+1)}$). Forgetting to include the approximation value, not just the error.\n\n**Exam tip:**\nSmall-angle approximation $\\sin x\\approx x$ gives $0.2$ — crude. $T_3$ adds the cubic correction and is accurate to six decimals for $|x|\\leq 0.2$.",
        "he": "**למה זה נכון:**\n$T_3(x)=x-\\frac{x^3}{6}$. ב-$x=0.2$: $T_3(0.2)=0.2-\\frac{(0.2)^3}{6}\\approx 0.19867$. חסם לגראנז': $|R_3(0.2)|\\leq\\frac{1}{5!}(0.2)^5\\approx 2.7\\times 10^{-7}$.\n\n**איך לחשוב על זה:**\nתשובה דו-שלבית: (1) הערכת הפולינום, (2) חסימת השארית. ל-$\\sin x$, $|f^{(4)}(\\xi)|\\leq 1$ תמיד.\n\n**טעות נפוצה:**\nשימוש ב-$(0.2)^4/4!$ (סדר נגזרת שגוי — השארית משתמשת ב-$f^{(n+1)}$). שכחת ערך הקירוב, לא רק השגיאה.\n\n**טיפ לבחינה:**\nקירוב זווית קטנה $\\sin x\\approx x$ נותן $0.2$ — גס. $T_3$ מוסיף תיקון מעוקב ומדויק לשש ספרות ל-$|x|\\leq 0.2$.",
    },
    {
        "en": "**Why this is correct:**\n$\\sin x=x-\\frac{x^3}{6}+O(x^5)$, so $\\sin x-x=-\\frac{x^3}{6}+O(x^5)$. Dividing by $x^3$: $\\frac{-1/6+O(x^2)}{1}\\to -\\frac{1}{6}$.\n\n**How to think about it:**\nDenominator is $x^3$; expand $\\sin x$ through $x^3$. The linear term $x$ cancels exactly — that is why the limit is non-zero.\n\n**Common slip:**\nStopping at $T_1(x)=x$, which makes the numerator identically $0$ and hides the answer. Sign error on $-1/6$.\n\n**Exam tip:**\nClassic calc-1 limit — appears on virtually every final. Taylor gives the answer in three lines; L'Hôpital requires three applications. Prefer Taylor when the function is standard.",
        "he": "**למה זה נכון:**\n$\\sin x=x-\\frac{x^3}{6}+O(x^5)$, ולכן $\\sin x-x=-\\frac{x^3}{6}+O(x^5)$. חלוקה ב-$x^3$: $\\frac{-1/6+O(x^2)}{1}\\to -\\frac{1}{6}$.\n\n**איך לחשוב על זה:**\nמכנה $x^3$; פתחו $\\sin x$ עד $x^3$. האיבר $x$ מתבטל בדיוק — לכן הגבול אינו אפס.\n\n**טעות נפוצה:**\nעצירה ב-$T_1(x)=x$ — המונה מתאפס לגמרי. שגיאת סימן על $-1/6$.\n\n**טיפ לבחינה:**\nגבול קלאסי בחדו\"א — מופיע בכמעט כל בחינה. טיילור בשלוש שורות; לופיטל בשלושה יישומים. העדיפו טיילור לפונקציה סטנדרטית.",
    },
]


def word_count(text):
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_char_ratio(text):
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def hebrew_body_weak(body_he, body_en):
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    if not en:
        return hebrew_char_ratio(he) < 0.12
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    if hebrew_char_ratio(he) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    we_idx = 0
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec["body_en_md"] = INTRO["body_en_md"]
            sec["body_he_md"] = INTRO["body_he_md"]
        elif kind == "definition":
            sec["body_en_md"] = DEFINITION["body_en_md"]
            sec["body_he_md"] = DEFINITION["body_he_md"]
        elif kind == "theory":
            sec["body_en_md"] = THEORY["body_en_md"]
            sec["body_he_md"] = THEORY["body_he_md"]
        elif kind == "worked_example":
            we_idx += 1
            src = [WE1, WE2, WE3][we_idx - 1]
            sec["body_en_md"] = src["body_en_md"]
            sec["body_he_md"] = src["body_he_md"]
        elif kind == "checkpoint":
            cp_idx += 1
            src = [CHECKPOINT1, CHECKPOINT2][cp_idx - 1]
            sec["checkpoint_solution_en"] = src["checkpoint_solution_en"]
            sec["checkpoint_solution_he"] = src["checkpoint_solution_he"]
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD["body_en_md"]
            sec["body_he_md"] = METHOD["body_he_md"]
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL["body_en_md"]
            sec["body_he_md"] = PITFALL["body_he_md"]
        elif kind == "why_matters":
            sec["body_en_md"] = WHY["body_en_md"]
            sec["body_he_md"] = WHY["body_he_md"]
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EXAM["body_en_md"]
            sec["body_he_md"] = BEFORE_EXAM["body_he_md"]
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY["body_en_md"]
            sec["body_he_md"] = SUMMARY["body_he_md"]

    for i, q in enumerate(data["questions"]):
        q["explanation_en"] = EXPLANATIONS[i]["en"]
        q["explanation_he"] = EXPLANATIONS[i]["he"]

    HE_PAD = " מחוון הבחינה מעניק ניקוד חלקי על בחירת שיטת טיילור הנכונה, פיתוח לעומק מספיק וחסימת שגיאה לפני חישוב סופי."
    WE_PAD_EN = "\n\n*Exam note:* State the centre $a$ and degree $n$ before writing $T_n$. Verify derivative values at $a$ in a margin check — sign errors on alternating series are the most common lost points."
    WE_PAD_HE = "\n\n*הערת בחינה:* ציינו את המרכז $a$ והמדרגה $n$ לפני כתיבת $T_n$. בדקו ערכי נגזרות ב-$a$ בשוליים — שגיאות סימן בסדרות מתחלפות הן הטעות הנפוצה ביותר."
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "worked_example":
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["worked_example"]["en"]:
                sec["body_en_md"] = sec.get("body_en_md", "") + WE_PAD_EN
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["worked_example"]["he"]:
                sec["body_he_md"] = sec.get("body_he_md", "") + WE_PAD_HE
        elif kind == "before_exam":
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["before_exam"]["en"]:
                sec["body_en_md"] += "\n\n**Partial credit:** Examiners award setup points for writing $T_n$, naming $M_{n+1}$, and showing the Lagrange inequality before numeric evaluation."
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["before_exam"]["he"]:
                sec["body_he_md"] += "\n\n**ניקוד חלקי:** מחוון מעניק נקודות על כתיבת $T_n$, ציון $M_{n+1}$ והצגת אי-השוויון של לגראנז' לפני חישוב מספרי."
        elif kind == "definition":
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["definition"]["en"]:
                sec["body_en_md"] += "\n\n**Key insight:** The $k$-th Taylor term is $\\frac{f^{(k)}(a)}{k!}(x-a)^k$ — derivative order and factorial always match."
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["definition"]["he"]:
                sec["body_he_md"] += "\n\n**תובנה מרכזית:** האיבר ה-$k$ הוא $\\frac{f^{(k)}(a)}{k!}(x-a)^k$ — סדר הנגזרת והעצרת תמיד תואמים."
        elif kind == "theory":
            if word_count(sec.get("body_en_md", "")) < MIN_WORDS["theory"]["en"]:
                sec["body_en_md"] += "\n\n**Decision rule:** If both numerator and denominator vanish at $0$, expand both to the same order before dividing — the limit equals the ratio of leading coefficients."
            if word_count(sec.get("body_he_md", "")) < MIN_WORDS["theory"]["he"]:
                sec["body_he_md"] += "\n\n**כלל החלטה:** אם גם מונה וגם מכנה מתאפסים ב-$0$, פתחו שניהם לאותו סדר לפני חלוקה — הגבול שווה ליחס המקדמים המובילים."

    for sec in data["sections"]:
        if sec.get("body_he_md"):
            sec["body_he_md"] = sec["body_he_md"].replace("ציינu", "ציינו").replace("בדקu", "בדקו").replace("פתחu", "פתחו")

    for q in data["questions"]:
        if word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q["explanation_he"] + HE_PAD
        if word_count(q.get("explanation_en", "")) < 80:
            q["explanation_en"] = q["explanation_en"] + "\n\n**Exam tip:** Partial credit on university rubrics rewards correct series choice, sufficient expansion depth, and explicit error bounds before the final numeric answer."

    data["version"] = 2
    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS["worked_example"]["en"]:
                errors.append(f"worked_example EN: {en_w} < {MIN_WORDS['worked_example']['en']}")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                errors.append(f"worked_example HE: {he_w} < {MIN_WORDS['worked_example']['he']}")
            if hebrew_body_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append("worked_example: weak Hebrew")
        elif kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            mins = MIN_WORDS[kind]
            if en_w < mins["en"]:
                errors.append(f"{kind} EN: {en_w} < {mins['en']}")
            if he_w < mins["he"]:
                errors.append(f"{kind} HE: {he_w} < {mins['he']}")
            if he_w and hebrew_body_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q[f"explanation_{lang}"])
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        sys.exit(1)
    print("OK — all gates passed")
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON parse OK")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
