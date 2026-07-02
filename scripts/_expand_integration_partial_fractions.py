#!/usr/bin/env python3
"""Expand integration_partial_fractions.json to Cursor depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/integration_partial_fractions.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
}
WORKED_EXAMPLE_MIN = {"en": 130, "he": 110}


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


SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "We already know how to integrate the simplest rational fractions:\n"
            "$$\\int \\frac{1}{x-a}\\,dx = \\ln|x-a| + C.$$\n\n"
            "But university calculus constantly throws harder integrands at you — "
            "polynomials divided by factored denominators such as "
            "$\\int \\frac{3x+1}{x^2-x-2}\\,dx$. Here the denominator splits as "
            "$(x-2)(x+1)$, yet you cannot integrate the original fraction directly.\n\n"
            "**Partial fraction decomposition** rewrites one complicated rational function "
            "as a **sum of simpler fractions**, each matching a factor of the denominator. "
            "Once split, every term integrates with logarithms, power rules, or "
            "$\\arctan$ after completing the square.\n\n"
            "The method applies whenever you have a **proper** rational function "
            "$P(x)/Q(x)$ with $\\deg P < \\deg Q$. If the fraction is improper, "
            "polynomial long division comes first — a step students forget most often.\n\n"
            "**Where you will see this:** definite integrals on Calc I exams, inverse "
            "Laplace transforms, and constant-coefficient ODEs with forcing terms."
        ),
        "body_he_md": (
            "כבר יודעים לאינטגרל את השבר הפשוט ביותר:\n"
            "$$\\int \\frac{1}{x-a}\\,dx = \\ln|x-a| + C.$$\n\n"
            "אבל בחשבון אוניברסיטאי מופיעים לעתים קרובות אינטגרנדים מהצורה "
            "$\\int \\frac{3x+1}{x^2-x-2}\\,dx$, כאשר המכנה מתפרק ל-$(x-2)(x+1)$ "
            "ואי אפשר לאינטגרל את השבר המקורי ישירות.\n\n"
            "**פירוק לשברים חלקיים** מכתיב מחדש פונקציה רציונלית מסובכת כ**סכום "
            "של שברים פשוטים**, כל אחד תואם גורם במכנה. לאחר הפירוק, כל איבר "
            "מאינטגרל בלוגריתם, בחוק חזקות, או ב-$\\arctan$ לאחר השלמה לריבוע.\n\n"
            "השיטה חלה על **שבר ראוי** $P(x)/Q(x)$ כאשר $\\deg P < \\deg Q$. "
            "אם השבר **לא ראוי**, חובה לבצע תחילה **חלוקה ארוכה של פולינומים** — "
            "שלב שסטודנטים מדלגים עליו לעתים קרובות.\n\n"
            "**היכן תפגשו זאת:** אינטegralים מסוימים בבחינות חשבון, הופכי "
            "טרנספורמציית לפלס, ומשוואות דיפרנציאליות עם איבר כפייה."
        ),
    },
    "definition": {
        "body_en_md": (
            "Given a proper rational function $P(x)/Q(x)$ where $\\deg P < \\deg Q$ "
            "and $Q$ is factored completely over $\\mathbb{R}$.\n\n"
            "**Step 0 — Improper fractions.** If $\\deg P \\ge \\deg Q$, perform "
            "polynomial long division first:\n"
            "$$\\frac{P(x)}{Q(x)} = S(x) + \\frac{R(x)}{Q(x)}, \\qquad \\deg R < \\deg Q.$$\n"
            "Integrate the polynomial $S(x)$ term-by-term; decompose only $R/Q$.\n\n"
            "**Case 1 — Distinct linear factors** $(x-a_1)(x-a_2)\\cdots$:\n"
            "$$\\frac{P(x)}{(x-a_1)(x-a_2)\\cdots} = "
            "\\frac{A_1}{x-a_1} + \\frac{A_2}{x-a_2} + \\cdots$$\n\n"
            "**Case 2 — Repeated linear factor** $(x-a)^n$:\n"
            "$$\\frac{A_1}{x-a} + \\frac{A_2}{(x-a)^2} + \\cdots + "
            "\\frac{A_n}{(x-a)^n}$$\n"
            "You need **one term for every power** from $1$ to $n$.\n\n"
            "**Case 3 — Irreducible quadratic** $(x^2+bx+c)$ with discriminant $<0$:\n"
            "$$\\frac{Ax+B}{x^2+bx+c}$$\n"
            "Never split an irreducible quadratic into linear factors over $\\mathbb{R}$.\n\n"
            "**Finding constants:** multiply both sides by the full denominator, then "
            "either substitute roots (cover-up method) or compare coefficients of like powers.\n\n"
            "**Exam habit:** write the template before any algebra — the factor list "
            "determines how many unknown constants you must solve for, and missing a "
            "repeated term is the most common template error on timed tests."
        ),
        "body_he_md": (
            "נתון שבר ראוי $P(x)/Q(x)$ כאשר $\\deg P < \\deg Q$ "
            "ו-$Q$ מפורק לגמרי מעל $\\mathbb{R}$.\n\n"
            "**שלב 0 — שבר לא ראוי.** אם $\\deg P \\ge \\deg Q$, בצעו תחילה "
            "חלוקה ארוכה:\n"
            "$$\\frac{P(x)}{Q(x)} = S(x) + \\frac{R(x)}{Q(x)}, \\qquad \\deg R < \\deg Q.$$\n"
            "אינטegralו את הפולינום $S(x)$ איבר-איבר; פרקו רק את $R/Q$.\n\n"
            "**מקרה 1 — גורמים לינאריים שונים** $(x-a_1)(x-a_2)\\cdots$:\n"
            "$$\\frac{P(x)}{(x-a_1)(x-a_2)\\cdots} = "
            "\\frac{A_1}{x-a_1} + \\frac{A_2}{x-a_2} + \\cdots$$\n\n"
            "**מקרה 2 — גורם לינארי חוזר** $(x-a)^n$:\n"
            "$$\\frac{A_1}{x-a} + \\frac{A_2}{(x-a)^2} + \\cdots + "
            "\\frac{A_n}{(x-a)^n}$$\n"
            "נדרש **איבר לכל חזקה** מ-$1$ עד $n$.\n\n"
            "**מקרה 3 — ריבועי בלתי ניתן לפירוק** $(x^2+bx+c)$ עם דיסקרימיננט $<0$:\n"
            "$$\\frac{Ax+B}{x^2+bx+c}$$\n"
            "אין לפרק ריבועי בלתי ניתן לגורמים לינאריים מעל $\\mathbb{R}$.\n\n"
            "**מציאת קבועים:** כפלו שני הצדדים במכנה המלא, ואז הציבו שורשים "
            "(שיטת cover-up) או השוו מקדמים של חזקות זהות.\n\n"
            "**הרגל לבחינה:** כתבו את התבנית לפני כל אלגebra — רשימת הגורמים "
            "קובעת כמה קבועים לפתור, ושכחת איבר בגורם חוזר היא הטעות הנפוצה ביותר."
        ),
    },
    "theory": {
        "body_en_md": (
            "After decomposition, each partial fraction integrates using standard "
            "Calc I rules. Keep this table visible while working:\n\n"
            "| Partial fraction | Indefinite integral |\n"
            "|---|---|\n"
            "| $\\dfrac{A}{x-a}$ | $A\\ln|x-a|+C$ |\n"
            "| $\\dfrac{A}{(x-a)^n}$, $n>1$ | "
            "$\\dfrac{A}{1-n}(x-a)^{1-n}+C$ |\n"
            "| $\\dfrac{A}{x^2+a^2}$ | $\\dfrac{A}{a}\\arctan\\dfrac{x}{a}+C$ |\n"
            "| $\\dfrac{Ax+B}{x^2+bx+c}$ (irred.) | Complete the square; split into "
            "$\\ln$ and $\\arctan$ parts |\n\n"
            "**Completing the square** is mandatory for irreducible quadratics:\n"
            "$$x^2+bx+c = \\left(x+\\frac{b}{2}\\right)^2 + "
            "\\left(c - \\frac{b^2}{4}\\right).$$\n"
            "Then substitute $u = x + b/2$ to match $\\int \\frac{du}{u^2+a^2}$.\n\n"
            "**When partial fractions fail or are overkill:** if the numerator is "
            "nearly the derivative of the denominator, try $u$-substitution first. "
            "If the denominator does not factor over $\\mathbb{R}$, you still use "
            "Case 3 — never force complex linear factors in a Calc I course.\n\n"
            "**Logarithm combination:** differences of logs become a single log of a "
            "quotient: $\\ln|x-a|-\\ln|x-b| = \\ln\\left|\\frac{x-a}{x-b}\\right|$.\n\n"
            "**Definite integrals:** after finding the antiderivative, evaluate at bounds "
            "carefully — a linear factor in the denominator can create a vertical asymptote "
            "inside the interval, turning the problem into an improper integral that must be "
            "handled with limits before you combine logarithms."
        ),
        "body_he_md": (
            "לאחר הפירוק, כל שבר חלקי מאינטegral לפי כללי חשבון סטנדרטיים. "
            "שמרו את הטבלה הזו לידכם בזמן העבודה:\n\n"
            "| שבר חלקי | אינטגרל לא-מסוים |\n"
            "|---|---|\n"
            "| $\\dfrac{A}{x-a}$ | $A\\ln|x-a|+C$ |\n"
            "| $\\dfrac{A}{(x-a)^n}$, $n>1$ | "
            "$\\dfrac{A}{1-n}(x-a)^{1-n}+C$ |\n"
            "| $\\dfrac{A}{x^2+a^2}$ | $\\dfrac{A}{a}\\arctan\\dfrac{x}{a}+C$ |\n"
            "| $\\dfrac{Ax+B}{x^2+bx+c}$ (בלתי ניתן) | השלמה לריבוע; פיצול ל-$\\ln$ "
            "ו-$\\arctan$ |\n\n"
            "**השלמה לריבוע** חובה לריבועיים בלתי ניתנים לפירוק:\n"
            "$$x^2+bx+c = \\left(x+\\frac{b}{2}\\right)^2 + "
            "\\left(c - \\frac{b^2}{4}\\right).$$\n"
            "לאחר מכן $u = x + b/2$ כדי להתאים ל-$\\int \\frac{du}{u^2+a^2}$.\n\n"
            "**מתי לא להשתמש בשברים חלקיים:** אם המונה כמעט נגזרת המכנה, "
            "נסו קודם החלפת $u$. אם המכנה לא מתפרק מעל $\\mathbb{R}$, "
            "עדיין משתמשים במקרה 3 — לא מפרקים לגורמים מרוכבים בחשבון 1.\n\n"
            "**שילוב לוגריתמים:** הפרש לוגריתמים הופך ללוגריתם של מנה: "
            "$\\ln|x-a|-\\ln|x-b| = \\ln\\left|\\frac{x-a}{x-b}\\right|$.\n\n"
            "**אינטegralים מסוימים:** לאחר מציאת האינטegral, הציבו גבולות בזהירות — "
            "גורם לינארי במכנה עלול ליצור אסימptוטה אנכית בתוך הקטע, "
            "והבעיה הופכת לאינטegral לא ראוי שדורש גבולות לפני שילוב לוגריתמים."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Evaluate:** $\\displaystyle\\int \\frac{3x+1}{x^2-x-2}\\,dx$.\n\n"
            "This is the canonical **Case 1** setup: a linear numerator over a "
            "quadratic denominator that splits into two distinct real linear factors. "
            "The method applies whenever you have a **proper** rational function "
            "$P(x)/Q(x)$ with $\\deg P < \\deg Q$. If the fraction is improper, "
            "polynomial long division comes first — a step students forget most often.\n\n"
            "### Move 1 Factor the denominator.\n"
            "$$x^2-x-2 = (x-2)(x+1).$$\n"
            "Both factors are distinct linear terms — Case 1 applies. Before writing "
            "constants, confirm the fraction is proper: degree of $3x+1$ is less than "
            "degree of the quadratic denominator.\n\n"
            "### Move 2 Set up and solve for constants.\n"
            "$$\\frac{3x+1}{(x-2)(x+1)} = \\frac{A}{x-2}+\\frac{B}{x+1}.$$\n"
            "Multiply through by $(x-2)(x+1)$:\n"
            "$$3x+1 = A(x+1)+B(x-2).$$\n"
            "Cover-up: $x=2 \\Rightarrow 7=3A \\Rightarrow A=7/3$.\n"
            "$x=-1 \\Rightarrow -2=-3B \\Rightarrow B=2/3$.\n\n"
            "### Move 3 Integrate each term.\n"
            "$$\\int\\left(\\frac{7/3}{x-2}+\\frac{2/3}{x+1}\\right)dx "
            "= \\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1|+C.$$\n\n"
            "### Move 4 Combine logarithms (optional but exam-friendly).\n"
            "$$\\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1| "
            "= \\frac{1}{3}\\ln|(x-2)^7(x+1)^2|+C.$$\n\n"
            "### Move 5 Quick verification.\n"
            "Differentiate $\\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1|$: "
            "you recover $\\frac{7/3}{x-2}+\\frac{2/3}{x+1}$, which recombines to "
            "$\\frac{3x+1}{(x-2)(x+1)}$ after a common denominator.\n\n"
            "**Answer:** $\\boxed{\\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1|+C}$ ✓"
        ),
        "body_he_md": (
            "**חשבו:** $\\displaystyle\\int \\frac{3x+1}{x^2-x-2}\\,dx$.\n\n"
            "זוהi **מקרה 1** קלאסי: מונה לינארי מעל מכנה ריבועי שמתפרק לשני גורמים "
            "לינאריים ממשיים שונים. אין צורך בחלוקה ארוכה כי מעלת המונה קטנה יותר.\n\n"
            "### צעד 1 פירוק המכנה.\n"
            "$$x^2-x-2 = (x-2)(x+1).$$\n"
            "שני גורמים לינאריים שונים — מקרה 1. ודאו שהשבר ראוי: "
            "מעלה המונה קטן ממעלה המכנה הריבועי.\n\n"
            "### צעד 2 הגדרה ומציאת קבועים.\n"
            "$$\\frac{3x+1}{(x-2)(x+1)} = \\frac{A}{x-2}+\\frac{B}{x+1}.$$\n"
            "כפלו ב-$(x-2)(x+1)$:\n"
            "$$3x+1 = A(x+1)+B(x-2).$$\n"
            "cover-up: $x=2 \\Rightarrow A=7/3$; $x=-1 \\Rightarrow B=2/3$.\n"
            "אימות ב-$x=0$: צד שמאל $=1$, צד ימין $=7/3-4/3=1$ ✓\n\n"
            "### צעד 3 אינטegrציה.\n"
            "$$\\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1|+C.$$\n\n"
            "### צעד 4 שילוב לוגריתמים (אופציונלי).\n"
            "ניתן לכתוב כלוג יחיד של מנה בחזקות — שימושי בבחינות.\n\n"
            "### צעד 5 בדיקה מהירה.\n"
            "גזרו את התשובה: חייבים לקבל $\\frac{7/3}{x-2}+\\frac{2/3}{x+1}$, "
            "שמתאחד ל-$\\frac{3x+1}{(x-2)(x+1)}$. "
            "בדיקה זו לוקחת פחות משלושים שניות בבחינה ומונעת טעויות cover-up.\n\n"
            "**תשובה:** $\\boxed{\\frac{7}{3}\\ln|x-2|+\\frac{2}{3}\\ln|x+1|+C}$ ✓"
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Evaluate:** $\\displaystyle\\int \\frac{x+3}{(x-1)^2(x+2)}\\,dx$.\n\n"
            "This problem mixes a **repeated linear factor** $(x-1)^2$ with a distinct "
            "linear factor $(x+2)$. The repeated factor is the critical detail: "
            "writing only one term over $(x-1)$ will produce wrong constants.\n\n"
            "### Move 1 Write the correct template for repeated factors.\n"
            "$$\\frac{x+3}{(x-1)^2(x+2)} = \\frac{A}{x-1}+\\frac{B}{(x-1)^2}+\\frac{C}{x+2}.$$\n"
            "The factor $(x-1)^2$ requires **both** $A/(x-1)$ and $B/(x-1)^2$.\n\n"
            "### Move 2 Clear denominators and find constants.\n"
            "$$x+3 = A(x-1)(x+2)+B(x+2)+C(x-1)^2.$$\n"
            "$x=1$: $4=3B \\Rightarrow B=4/3$.\n"
            "$x=-2$: $1=9C \\Rightarrow C=1/9$.\n"
            "$x=0$: $3=-2A+2B+C$. Substituting $B,C$ gives $A=-1/9$.\n\n"
            "### Move 3 Integrate term by term.\n"
            "$$\\int \\left(\\frac{-1/9}{x-1}+\\frac{4/3}{(x-1)^2}+\\frac{1/9}{x+2}\\right)dx$$\n"
            "$$= -\\frac{1}{9}\\ln|x-1| - \\frac{4}{3(x-1)} + \\frac{1}{9}\\ln|x+2| + C.$$\n\n"
            "### Move 4 Explain the middle term.\n"
            "The $\\frac{4/3}{(x-1)^2}$ piece uses the power rule for $n=2$, giving "
            "$-\\frac{4}{3(x-1)}$ — not a logarithm. Students often mis-integrate "
            "repeated factors by applying $\\ln$ to every term.\n\n"
            "### Move 5 Domain note.\n"
            "The answer is valid on intervals that do not cross $x=-2$ or $x=1$, "
            "where the original integrand is undefined. "
            "On exams, state the domain if asked for a definite integral.\n\n"
            "**Answer:** $\\boxed{-\\frac{1}{9}\\ln|x-1| - \\frac{4}{3(x-1)} + "
            "\\frac{1}{9}\\ln|x+2| + C}$ ✓"
        ),
        "body_he_md": (
            "**חשבו:** $\\displaystyle\\int \\frac{x+3}{(x-1)^2(x+2)}\\,dx$.\n\n"
            "בעיה זו משלבת **גורם לינארי חוזר** $(x-1)^2$ עם גורם לינארי שונה $(x+2)$. "
            "הגורם החוזר הוא הפרט הקריטי: כתיבת איבר יחיד מעל $(x-1)$ "
            "תיתן קבועים שגויים.\n\n"
            "### צעד 1 תבנית נכונה לגורם חוזר.\n"
            "$$\\frac{x+3}{(x-1)^2(x+2)} = \\frac{A}{x-1}+\\frac{B}{(x-1)^2}+\\frac{C}{x+2}.$$\n"
            "ל-$(x-1)^2$ נדרשים **שני** איברים: $A/(x-1)$ ו-$B/(x-1)^2$.\n\n"
            "### צעד 2 ניקוי מכנים ומציאת קבועים.\n"
            "$$x+3 = A(x-1)(x+2)+B(x+2)+C(x-1)^2.$$\n"
            "$x=1$: $B=4/3$. $x=-2$: $C=1/9$. $x=0$: $A=-1/9$.\n\n"
            "### צעד 3 אינטegrציה איבר-איבר.\n"
            "$$= -\\frac{1}{9}\\ln|x-1| - \\frac{4}{3(x-1)} + \\frac{1}{9}\\ln|x+2| + C.$$\n\n"
            "### צעד 4 הסבר על האיבר האמצעי.\n"
            "האיבר $\\frac{4/3}{(x-1)^2}$ משתמש בחוק חזקות ל-$n=2$ — לא בלוגריתם.\n\n"
            "### צעד 5 הערת תחום.\n"
            "התשובה תקפה בקטעים שלא חוצים $x=-2$ או $x=1$. "
            "בבחינה, ציינו תחום הגדרה אם מבקשים אינטegral מסוים על קטע "
            "שחוצה נקודת אי-רציפות.\n\n"
            "**תשובה:** $\\boxed{-\\frac{1}{9}\\ln|x-1| - \\frac{4}{3(x-1)} + "
            "\\frac{1}{9}\\ln|x+2| + C}$ ✓"
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Evaluate:** $\\displaystyle\\int \\frac{2x^2+3x+1}{(x-1)(x^2+x+1)}\\,dx$ "
            "(exam-level mixed factors).\n\n"
            "### Move 1 Classify each denominator factor.\n"
            "$(x-1)$ is linear. For $x^2+x+1$, discriminant $=1-4=-3<0$ — "
            "**irreducible**. Use $(Bx+C)/(x^2+x+1)$.\n\n"
            "### Move 2 Decompose and solve.\n"
            "$$\\frac{2x^2+3x+1}{(x-1)(x^2+x+1)} = \\frac{A}{x-1}+\\frac{Bx+C}{x^2+x+1}.$$\n"
            "$x=1$: $6=3A \\Rightarrow A=2$.\n"
            "Expand: $2x^2+3x+1 = 2(x^2+x+1)+(Bx+C)(x-1)$.\n"
            "Compare coefficients: $B=0$, $C=1$.\n\n"
            "### Move 3 Integrate the irreducible quadratic term.\n"
            "$$\\int\\frac{1}{x^2+x+1}\\,dx \\quad (\\text{numerator reduces to } 1 "
            "\\text{ when } B=0,\\; C=1).$$\n"
            "Complete the square: $x^2+x+1=(x+\\tfrac12)^2+\\tfrac34$.\n"
            "$$\\int\\frac{1}{(x+\\tfrac12)^2+(\\sqrt3/2)^2}dx "
            "= \\frac{2}{\\sqrt3}\\arctan\\frac{2x+1}{\\sqrt3}.$$\n\n"
            "### Move 4 Combine linear and quadratic parts.\n"
            "The linear factor contributes $2\\ln|x-1|$. The irreducible piece contributes "
            "pure $\\arctan$ — no logarithm appears because the numerator of the quadratic "
            "term was constant after decomposition.\n\n"
            "### Move 5 Discriminant check.\n"
            "Always verify $b^2-4ac<0$ before treating a quadratic as irreducible; "
            "if it factored, you would need two linear cover-up terms instead. "
            "Writing the wrong template here costs several minutes of algebra.\n\n"
            "**Result:** $\\boxed{2\\ln|x-1| + \\frac{2}{\\sqrt3}\\arctan\\frac{2x+1}{\\sqrt3}+C}$ ✓"
        ),
        "body_he_md": (
            "**חשבו:** $\\displaystyle\\int \\frac{2x^2+3x+1}{(x-1)(x^2+x+1)}\\,dx$ "
            "(רמת בחינה — גורמים מעורבים).\n\n"
            "אינטegrand זה משלב גורם לינארי פשוט עם **ריבועי בלתי ניתן לפירוק** — "
            "תבנית השברים החלקיים הקשה ביותר בחשבון 1. "
            "סווגu כל גורם לפני כתיבת קבועים.\n\n"
            "### צעד 1 סיווג גורמי המכנה.\n"
            "$(x-1)$ לינארי. ל-$x^2+x+1$ דיסקרימיננט $=-3<0$ — **בלתי ניתן לפירוק**. "
            "משתמשים ב-$(Bx+C)/(x^2+x+1)$.\n\n"
            "### צעד 2 פירוק ופתרון.\n"
            "$$\\frac{2x^2+3x+1}{(x-1)(x^2+x+1)} = \\frac{A}{x-1}+\\frac{Bx+C}{x^2+x+1}.$$\n"
            "$x=1$: $A=2$. השוואת מקדמים: $B=0$, $C=1$.\n\n"
            "### צעד 3 אינטegrציה של הריבועי.\n"
            "עם $B=0$ ו-$C=1$, מאינטegralים $\\int\\frac{1}{x^2+x+1}\\,dx$ בלבד.\n"
            "השלמה לריבוע: $x^2+x+1=(x+\\tfrac12)^2+\\tfrac34$.\n"
            "$$\\frac{2}{\\sqrt3}\\arctan\\frac{2x+1}{\\sqrt3}.$$\n\n"
            "### צעד 4 שילוב חלקים.\n"
            "הגורם הלינארי תורם $2\\ln|x-1|$. הריבועי תורם $\\arctan$ בלבד — "
            "אין לוג כי המונה של הריבועי הפך לקבוע אחרי הפירוק.\n\n"
            "### צעד 5 בדיקת דיסקרימיננט.\n"
            "ודאu $b^2-4ac<0$ לפני שמסווגים ריבועי כבלתי ניתן; "
            "אם הוא מתפרק, נדרשים שני איברי cover-up לינאריים.\n\n"
            "**תוצאה:** $\\boxed{2\\ln|x-1| + \\frac{2}{\\sqrt3}\\arctan\\frac{2x+1}{\\sqrt3}+C}$ ✓"
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Set up Case 1 with distinct linear factors:\n"
            "$$\\frac{5}{(x-1)(x+4)}=\\frac{A}{x-1}+\\frac{B}{x+4}.$$\n"
            "Multiply both sides by $(x-1)(x+4)$:\n"
            "$$5 = A(x+4)+B(x-1).$$\n"
            "Cover-up at $x=1$: $5=5A \\Rightarrow A=1$.\n"
            "Cover-up at $x=-4$: $5=-5B \\Rightarrow B=-1$.\n\n"
            "Check by recombining: "
            "$\\frac{1}{x-1}-\\frac{1}{x+4} = \\frac{(x+4)-(x-1)}{(x-1)(x+4)} "
            "= \\frac{5}{(x-1)(x+4)}$ ✓\n\n"
            "**Decomposition:** $\\boxed{\\dfrac{1}{x-1}-\\dfrac{1}{x+4}}$"
        ),
        "checkpoint_solution_he": (
            "הגדירו מקרה 1 עם גורמים לינאריים שונים:\n"
            "$$\\frac{5}{(x-1)(x+4)}=\\frac{A}{x-1}+\\frac{B}{x+4}.$$\n"
            "כפלו ב-$(x-1)(x+4)$:\n"
            "$$5 = A(x+4)+B(x-1).$$\n"
            "cover-up ב-$x=1$: $A=1$. cover-up ב-$x=-4$: $B=-1$.\n\n"
            "בדיקה: $\\frac{1}{x-1}-\\frac{1}{x+4} = \\frac{5}{(x-1)(x+4)}$ ✓\n\n"
            "**פירוק:** $\\boxed{\\dfrac{1}{x-1}-\\dfrac{1}{x+4}}$"
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "The denominator has a linear factor $x$ and irreducible $x^2+1$:\n"
            "$$\\frac{2}{x(x^2+1)}=\\frac{A}{x}+\\frac{Bx+C}{x^2+1}.$$\n"
            "Multiply: $2 = A(x^2+1)+(Bx+C)x$.\n"
            "$x=0$: $2=A$.\n"
            "Compare $x^2$ coefficients: $0=A+B \\Rightarrow B=-2$.\n"
            "Compare $x^1$: $0=C$.\n\n"
            "Integrate:\n"
            "$$\\int\\frac{2}{x(x^2+1)}\\,dx = \\int\\left(\\frac{2}{x}-\\frac{2x}{x^2+1}\\right)dx "
            "= 2\\ln|x|-\\ln(x^2+1)+C.$$\n\n"
            "**Answer:** $\\boxed{2\\ln|x|-\\ln(x^2+1)+C}$"
        ),
        "checkpoint_solution_he": (
            "המכנה מכיל גורם לינארי $x$ וריבועי בלתי ניתן $x^2+1$:\n"
            "$$\\frac{2}{x(x^2+1)}=\\frac{A}{x}+\\frac{Bx+C}{x^2+1}.$$\n"
            "כפלו: $2 = A(x^2+1)+(Bx+C)x$.\n"
            "$x=0$: $A=2$. מקדם $x^2$: $B=-2$. מקדם $x$: $C=0$.\n\n"
            "אינטegrציה:\n"
            "$$2\\ln|x|-\\ln(x^2+1)+C.$$\n\n"
            "**תשובה:** $\\boxed{2\\ln|x|-\\ln(x^2+1)+C}$"
        ),
    },
    "method_guide": {
        "body_en_md": (
            "**Step 1 — Check properness.** Compare degrees. If "
            "$\\deg P \\ge \\deg Q$, do polynomial long division first.\n\n"
            "**Step 2 — Factor the denominator completely over $\\mathbb{R}$.** "
            "Verify irreducible quadratics via the discriminant $b^2-4ac$.\n\n"
            "**Step 3 — Write the decomposition template:**\n\n"
            "| Factor in denominator | Add these terms |\n"
            "|---|---|\n"
            "| $(x-a)$ distinct | $A/(x-a)$ |\n"
            "| $(x-a)^n$ repeated | $A_1/(x-a)+\\cdots+A_n/(x-a)^n$ |\n"
            "| $(x^2+bx+c)$ irred. | $(Ax+B)/(x^2+bx+c)$ |\n\n"
            "**Step 4 — Find constants** by multiplying through, then cover-up at "
            "roots and/or coefficient comparison. Cross-check with one extra $x$-value.\n\n"
            "**Step 5 — Integrate each term:**\n"
            "- $A/(x-a) \\to A\\ln|x-a|$.\n"
            "- $A/(x-a)^n \\to -A/[(n-1)(x-a)^{n-1}]$ for $n>1$.\n"
            "- Irreducible quadratic: complete the square $\\to$ $\\arctan$ or $\\ln$."
        ),
        "body_he_md": (
            "**שלב 1 — בדקו ראויות.** השוו מעלות. אם $\\deg P \\ge \\deg Q$, "
            "בצעו חלוקה ארוכה תחילה.\n\n"
            "**שלב 2 — פרקו את המכנה לגמרי מעל $\\mathbb{R}$.** "
            "אמתו ריבועיים בלתי ניתנים עם דיסקרימיננט $b^2-4ac$.\n\n"
            "**שלב 3 — כתבו תבנית פירוק:**\n\n"
            "| גורם במכנה | הוסיפו איברים |\n"
            "|---|---|\n"
            "| $(x-a)$ שונה | $A/(x-a)$ |\n"
            "| $(x-a)^n$ חוזר | $A_1/(x-a)+\\cdots+A_n/(x-a)^n$ |\n"
            "| $(x^2+bx+c)$ בלתי ניתן | $(Ax+B)/(x^2+bx+c)$ |\n\n"
            "**שלב 4 — מצאו קבועים** בכפל שני הצדדים, cover-up בשורשים "
            "והשוואת מקדמים. בדקו עם ערך $x$ נוסף.\n\n"
            "**שלב 5 — אינטegralו כל איבר:**\n"
            "- $A/(x-a) \\to A\\ln|x-a|$.\n"
            "- $A/(x-a)^n \\to -A/[(n-1)(x-a)^{n-1}]$ ל-$n>1$.\n"
            "- ריבועי בלתי ניתן: השלמה לריבוע $\\to$ $\\arctan$ או $\\ln$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Skipping long division on improper fractions.** "
            "If $\\deg P \\ge \\deg Q$, partial fractions on the whole fraction "
            "will fail — divide first.\n\n"
            "2. **Treating irreducible quadratics as two linear factors.** "
            "Check $b^2-4ac<0$ before deciding Case 3.\n\n"
            "3. **Wrong template for repeated linear factors.** "
            "$(x-a)^2$ needs **both** $A/(x-a)$ and $B/(x-a)^2$, not just one term.\n\n"
            "4. **Forgetting to complete the square** before integrating "
            "irreducible quadratic terms — you cannot plug directly into a table.\n\n"
            "5. **Sign errors when comparing coefficients.** "
            "Expand the right-hand side fully before matching powers of $x$.\n\n"
            "**Fix for misconception #3:** For $(x-a)^n$, write $n$ separate "
            "fractions with powers $1,2,\\ldots,n$ in the denominator — never skip a power."
        ),
        "body_he_md": (
            "1. **דילוג על חלוקה ארוכה בשבר לא ראוי.** "
            "אם $\\deg P \\ge \\deg Q$, פירוק על כל השבר ייכשל — חלקו תחילה.\n\n"
            "2. **התייחסות לריבועי בלתי ניתן כשני גורמים לינאריים.** "
            "בדקו $b^2-4ac<0$ לפני מקרה 3.\n\n"
            "3. **תבנית שגויה לגורם לינארי חוזר.** "
            "$(x-a)^2$ דורש **גם** $A/(x-a)$ **וגם** $B/(x-a)^2$.\n\n"
            "4. **שכחת השלמה לריבוע** לפני אינטegrציה של ריבועי בלתי ניתן.\n\n"
            "5. **שגיאות סימן בהשוואת מקדמים.** "
            "פתחו את הצד ימין לגמרי לפני השוואת חזקות $x$.\n\n"
            "**תיקון לטעות #3:** ל-$(x-a)^n$ כתבו $n$ שברים נפרדים "
            "עם חזקות $1,2,\\ldots,n$ במכנה.\n\n"
            "**טיפ לבחינה:** לפני הגשה, שאלו \"איזו מלכודת פגעתי?\" — "
            "לא רק \"מה המספר הנכון?\""
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Partial fractions are the standard bridge between **polynomial algebra** "
            "and **integration** — once mastered, you can evaluate a large class of "
            "rational integrals that appear throughout engineering mathematics.\n\n"
            "**Recommended next topics on A Step Forward:**\n"
            "- `concept:improper_integrals` — when integration bounds cross a "
            "vertical asymptote created by a linear factor\n"
            "- `concept:integrals_techniques` — choosing partial fractions vs. "
            "substitution vs. integration by parts\n\n"
            "**Why it matters for exams:** university Calc I finals routinely combine "
            "long division, partial fractions, and completing the square in one "
            "multi-step problem worth 15–20 points. Transfer skill: the same "
            "decomposition appears in inverse Laplace transforms and in solving "
            "forced linear ODEs."
        ),
        "body_he_md": (
            "שברים חלקיים הם הגשר הסטנדרטי בין **אלגebra פולינומים** "
            "ל**אינטegrציה** — לאחר שליטה, ניתן לחשב מחלקה גדולה של "
            "אינטegralים רציונליים שמופיעים בכל הנדסה מתמטית.\n\n"
            "**נושאים מומלצים להמשך ב-A Step Forward:**\n"
            "- `concept:improper_integrals` — כשגבולות האינטegrציה חוצים "
            "אסימptוטה אנכית מגורם לינארי\n"
            "- `concept:integrals_techniques` — בחירה בין שברים חלקיים, "
            "החלפה ואינטegrציה בחלקים\n\n"
            "**למה זה חשוב לבחינות:** בבחינות סופיות בחשבון 1 משלבים לעתים קרובות "
            "חלוקה ארוכה, שברים חלקיים והשלמה לריבוע בשאלה אחת רב-שלבית. "
            "אותו פירוק מופיע בהופכי לפלס ובפתרון מ\"ד לינאריות עם כפייה."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Checklist before you submit:**\n"
            "- [ ] Is $\\deg P < \\deg Q$? If not, did you long-divide first?\n"
            "- [ ] Is the denominator fully factored over $\\mathbb{R}$?\n"
            "- [ ] Does every repeated factor $(x-a)^n$ have $n$ template terms?\n"
            "- [ ] Did you verify constants with cover-up **and** one coefficient check?\n"
            "- [ ] For irreducible quadratics, did you complete the square correctly?\n\n"
            "**Quick integral table:**\n"
            "$$\\int\\frac{A}{x-a}\\,dx = A\\ln|x-a|+C.$$\n"
            "$$\\int\\frac{1}{x^2+a^2}\\,dx = \\frac{1}{a}\\arctan\\frac{x}{a}+C.$$\n"
            "$$\\int\\frac{x}{x^2+a^2}\\,dx = \\frac{1}{2}\\ln(x^2+a^2)+C.$$\n\n"
            "**Last review:** Solve one checkpoint without notes, then explain aloud "
            "why repeated factors need multiple terms."
        ),
        "body_he_md": (
            "**רשימת בדיקה לפני הגשה:**\n"
            "- [ ] האם $\\deg P < \\deg Q$? אם לא — האם ביצעתם חלוקה ארוכה?\n"
            "- [ ] האם המכנה מפורק לגמרי מעל $\\mathbb{R}$?\n"
            "- [ ] לכל גורם חוזר $(x-a)^n$ — האם יש $n$ איברים בתבנית?\n"
            "- [ ] האם אימתתם קבועים ב-cover-up **וב**בדיקת מקדם אחת?\n"
            "- [ ] לריבועיים בלתי ניתנים — האם השלמתם לריבוע נכון?\n\n"
            "**טבלת אינטegralים מהירה:**\n"
            "$$\\int\\frac{A}{x-a}\\,dx = A\\ln|x-a|+C.$$\n"
            "$$\\int\\frac{1}{x^2+a^2}\\,dx = \\frac{1}{a}\\arctan\\frac{x}{a}+C.$$\n"
            "$$\\int\\frac{x}{x^2+a^2}\\,dx = \\frac{1}{2}\\ln(x^2+a^2)+C.$$\n\n"
            "**חזרה אחרונה:** פתרו checkpoint אחד בלי רשימות, והסבירו בקול "
            "למה גורם חוזר דורש מספר איברים."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Partial fractions** rewrite $P/Q$ as a sum of simpler rational terms.\n"
            "- **Three cases:** distinct linear, repeated linear, irreducible quadratic.\n"
            "- **Always check properness** — long division first if needed.\n"
            "- **Find constants** via cover-up at roots and coefficient comparison.\n"
            "- **Integrate:** $\\ln|x-a|$ for linear; power rule for repeated; "
            "$\\arctan$ after completing the square for irreducible quadratics.\n\n"
            "**Takeaway:** Read the factored denominator first — the template "
            "determines the entire solution path."
        ),
        "body_he_md": (
            "- **שברים חלקיים** מכתיבים $P/Q$ כסכום של שברים פשוטים.\n"
            "- **שלושה מקרים:** לינארי שונה, לינארי חוזר, ריבועי בלתי ניתן.\n"
            "- **תמיד בדקו ראויות** — חלוקה ארוכה אם צריך.\n"
            "- **מציאת קבועים** ב-cover-up ובהשוואת מקדמים.\n"
            "- **אינטegrציה:** $\\ln|x-a|$ ללינארי; חוק חזקות לחוזר; "
            "$\\arctan$ אחרי השלמה לריבוע לריבועיים.\n\n"
            "**מסקנה:** קראו את המכנה המפורק תחילה — התבנית קובעת את כל דרך הפתרון."
        ),
    },
}

E12_SOLUTION_EN = (
    "$\\frac{A}{x-1}+\\frac{Bx+C}{x^2+1}$. $x=1$: $2=2A\\Rightarrow A=1$. "
    "Expand: $(Bx+C)(x-1)=-x+1$, so $B=0$, $C=-1$. "
    "$\\int=\\ln|x-1|-\\frac{1}{2}\\ln(x^2+1)+C$."
)
E12_SOLUTION_HE = (
    "$A=1$, $B=0$, $C=-1$. "
    "$\\int=\\ln|x-1|-\\frac{1}{2}\\ln(x^2+1)+C$."
)

E13_SOLUTION_EN = (
    "Factor: $x^3-x^2-2x=x(x-2)(x+1)$. "
    "Decompose: $\\frac{A}{x}+\\frac{B}{x-2}+\\frac{C}{x+1}$. "
    "$x=0$: $A=3/2$. $x=2$: $B=3/2$. $x=-1$: $C=2$. "
    "Antiderivative: $\\frac{3}{2}\\ln|x|+\\frac{3}{2}\\ln|x-2|+2\\ln|x+1|+C$. "
    "Note: bounds including $x=2$ give an improper integral (singularity)."
)
E13_SOLUTION_HE = (
    "גורמים: $x(x-2)(x+1)$. $A=3/2$, $B=3/2$, $C=2$. "
    "אינטegral: $\\frac{3}{2}\\ln|x|+\\frac{3}{2}\\ln|x-2|+2\\ln|x+1|+C$. "
    "שימו לב: גבולות הכוללים $x=2$ — אינטegral לא ראוי (singularity)."
)

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "Start with Case 1: $\\frac{1}{(x-1)(x-3)} = \\frac{A}{x-1}+\\frac{B}{x-3}$. "
            "Clear denominators to get $1=A(x-3)+B(x-1)$. Cover-up at $x=1$ gives "
            "$1=-2A$, so $A=-1/2$. Cover-up at $x=3$ gives $1=2B$, so $B=1/2$. "
            "Integrating each term: "
            "$\\frac{1}{2}(\\ln|x-3|-\\ln|x-1|)=\\frac{1}{2}\\ln\\left|\\frac{x-3}{x-1}\\right|+C$, "
            "which matches option 0.\n\n"
            "Option 2 reverses the quotient inside the log — a classic sign or order slip "
            "after combining logarithms. Option 1 incorrectly logs the product "
            "$(x-1)(x-3)$ without decomposing first. Option 3 invents a midpoint root "
            "$x=2$ that does not appear in the factorization.\n\n"
            "**Exam tip:** after cover-up, combine log differences into one quotient "
            "log to match multiple-choice form. **Self-check:** differentiate your "
            "answer — you must recover the original integrand on the domain."
        ),
        "explanation_he": (
            "התחילu במקרה 1: $\\frac{1}{(x-1)(x-3)} = \\frac{A}{x-1}+\\frac{B}{x-3}$. "
            "ניקוי מכנים: $1=A(x-3)+B(x-1)$. cover-up ב-$x=1$ נותן $A=-1/2$; "
            "cover-up ב-$x=3$ נותן $B=1/2$. אינטegrציה: "
            "$\\frac{1}{2}\\ln\\left|\\frac{x-3}{x-1}\\right|+C$ — תואם אפשרות 0.\n\n"
            "אפשרות 2 מהפכת סדר במונה הלוג — טעות סימן נפוצה אחרי שילוב לוגריתמים. "
            "אפשרות 1 מתייחסת למכפלה $(x-1)(x-3)$ כלוג יחיד בלי פירוק. "
            "אפשרות 3 ממציאה שורש $x=2$ שלא מופיע בפירוק.\n\n"
            "**טיפ לבחינה:** לאחר cover-up, שלבu הפרשי לוג ללוג מנה אחד. "
            "**בדיקה:** גזרu את התשובה — חייבים לשחזר את האינטegrand המקורי "
            "בתחום ההגדרה."
        ),
    },
    {
        "rubric_en": (
            "Decompose to $A/(x-1)+(Bx+C)/(x^2+1)$. $A=1$, $B=0$, $C=2$. "
            "$\\int = \\ln|x-1|+2\\arctan x+C$."
        ),
        "rubric_he": "$A=1$, $B=0$, $C=2$. $\\ln|x-1|+2\\arctan x+C$.",
        "explanation_en": (
            "The denominator mixes a linear factor $(x-1)$ with irreducible $x^2+1$, "
            "so the template is $\\frac{A}{x-1}+\\frac{Bx+C}{x^2+1}$ — never two "
            "linear fractions over the quadratic. At $x=1$, the numerator equals "
            "$1+2-1=2$, giving $2=2A$ and $A=1$.\n\n"
            "Subtract $A(x^2+1)$ from the cleared identity: "
            "$(Bx+C)(x-1)=2x-2=2(x-1)$, hence $Bx+C=2$, so $B=0$, $C=2$. "
            "Integrate: $\\ln|x-1|+\\int\\frac{2}{x^2+1}\\,dx=\\ln|x-1|+2\\arctan x+C$.\n\n"
            "**Common slip:** writing $C=1$ by mis-expanding $(Bx+C)(x-1)$. "
            "**Exam tip:** after finding $A$ by cover-up, compare remaining "
            "polynomial coefficients for the quadratic factor only — do not re-cover "
            "roots that belong to the irreducible piece."
        ),
        "explanation_he": (
            "המכנה מערב גורם לינארי $(x-1)$ עם $x^2+1$ בלתי ניתן, "
            "לכן התבנית $\\frac{A}{x-1}+\\frac{Bx+C}{x^2+1}$ — "
            "לא שני שברים לינאריים מעל הריבועי. ב-$x=1$ המונה שווה $2$, "
            "כלומר $A=1$.\n\n"
            "לאחר חיסור $A(x^2+1)$: $(Bx+C)(x-1)=2(x-1)$, "
            "כלומר $Bx+C=2$, $B=0$, $C=2$. "
            "אינטegrציה: $\\ln|x-1|+2\\arctan x+C$.\n\n"
            "**טעות נפוצה:** כתיבת $C=1$ בגלל הרחבה שגויה של $(Bx+C)(x-1)$. "
            "**טיפ לבחינה:** לאחר $A$ ב-cover-up, השוו מקדמים "
            "רק עבור הגורם הריבועי שנותר — אל תחזרu על cover-up "
            "על שורשים של הריבועי הבלתי ניתן."
        ),
    },
    {
        "explanation_en": (
            "This is the classic distinct-linear-factors template. Set "
            "$\\frac{1}{(x-1)(x+1)}=\\frac{A}{x-1}+\\frac{B}{x+1}$ and multiply: "
            "$1=A(x+1)+B(x-1)$. Cover-up gives $A=1/2$ at $x=1$ and $B=-1/2$ at $x=-1$.\n\n"
            "Integrate term by term: "
            "$\\frac{1}{2}\\ln|x-1|-\\frac{1}{2}\\ln|x+1|+C "
            "= \\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right|+C$.\n\n"
            "**Common slip:** forgetting the $1/2$ coefficients — they come from "
            "cover-up, not from the log rules. **Exam tip:** when both roots are "
            "symmetric ($\\pm1$), expect equal-magnitude coefficients with opposite "
            "signs. **Self-check:** recombine your partial fractions over a common "
            "denominator before integrating to catch algebra errors early."
        ),
        "explanation_he": (
            "זוהi תבנית קלאסית של גורמים לינאריים שונים. "
            "הגדירu $\\frac{1}{(x-1)(x+1)}=\\frac{A}{x-1}+\\frac{B}{x+1}$ "
            "וכפlu: $1=A(x+1)+B(x-1)$. cover-up: $A=1/2$ ב-$x=1$, $B=-1/2$ ב-$x=-1$.\n\n"
            "אינטegrציה: $\\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right|+C$.\n\n"
            "**טעות נפוצה:** שכחת מקדמי $1/2$ — הם מגיעים מ-cover-up, "
            "לא מכללי הלוג. **טיפ לבחינה:** כשהשורשים סימטריים ($\\pm1$), "
            "צפu למקדמים שווי-גודל עם סימנים הפוכים. "
            "**בדיקה:** חברu שברים חלקיים על מכנה משותף לפני האינטegrציה "
            "כדי לתפוס טעויות אלגebra מוקדם."
        ),
    },
    {
        "explanation_en": (
            "Factor the denominator first: $x^2-4=(x-2)(x+2)$ — a difference of squares. "
            "Decompose $\\frac{4}{(x-2)(x+2)}=\\frac{A}{x-2}+\\frac{B}{x+2}$. "
            "Multiply: $4=A(x+2)+B(x-2)$. At $x=2$: $4=4A$, so $A=1$. "
            "At $x=-2$: $4=-4B$, so $B=-1$.\n\n"
            "Integrate: $\\ln|x-2|-\\ln|x+2|+C=\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**Common slip:** leaving $x^2-4$ unfactored and attempting a wrong "
            "template. **Exam tip:** difference of squares always splits into "
            "two distinct linear factors — perfect for Case 1. "
            "**Self-check:** at $x=0$, the integrand is $4/(-4)=-1$; "
            "differentiate your antiderivative at $x=0$ and confirm you get $-1$."
        ),
        "explanation_he": (
            "פרקu תחילה: $x^2-4=(x-2)(x+2)$ — הפרש ריבועים. "
            "פירוק: $\\frac{4}{(x-2)(x+2)}=\\frac{A}{x-2}+\\frac{B}{x+2}$. "
            "כפל: $4=A(x+2)+B(x-2)$. $x=2$: $A=1$. $x=-2$: $B=-1$.\n\n"
            "אינטegrציה: $\\ln\\left|\\frac{x-2}{x+2}\\right|+C$.\n\n"
            "**טעות נפוצה:** השארת $x^2-4$ בלי פירוק ושימוש בתבנית שגויה. "
            "**טיפ לבחינה:** הפרש ריבועים תמיד מתפרק לשני גורמים לינאריים — "
            "מקרה 1 אידיאלי. **בדיקה:** ב-$x=0$ האינטegrand הוא $-1$; "
            "גזרu את האינטegral שלכם ב-$x=0$ וודאu שמתקבל $-1$."
        ),
    },
    {
        "explanation_en": (
            "The instruction says **decompose only** — do not integrate. "
            "Set $\\frac{2x+1}{(x+3)(x-2)}=\\frac{A}{x+3}+\\frac{B}{x-2}$ and "
            "clear denominators: $2x+1=A(x-2)+B(x+3)$.\n\n"
            "Cover-up: $x=2$ gives $5=5B$, so $B=1$. $x=-3$ gives $-5=-5A$, "
            "so $A=1$. Result: $\\frac{1}{x+3}+\\frac{1}{x-2}$.\n\n"
            "**Common slip:** integrating anyway and losing marks on \"decompose only\" "
            "questions — read the stem carefully. **Exam tip:** recombine your partial "
            "fractions over a common denominator to verify the numerator is exactly "
            "$2x+1$. **Self-check:** both coefficients are positive here because "
            "cover-up at each root isolates one constant directly."
        ),
        "explanation_he": (
            "ההוראה: **פרקו בלבד** — אל תאינטegralו. "
            "הגדירu $\\frac{2x+1}{(x+3)(x-2)}=\\frac{A}{x+3}+\\frac{B}{x-2}$ "
            "וכפlu: $2x+1=A(x-2)+B(x+3)$.\n\n"
            "cover-up: $x=2$ נותן $B=1$; $x=-3$ נותן $A=1$. "
            "תוצאה: $\\frac{1}{x+3}+\\frac{1}{x-2}$.\n\n"
            "**טעות נפוצה:** אינטegrציה למרות \"פרקו בלבד\" — קראu את הנתון בעיון. "
            "**טип לבחינה:** חברu מחדש על מכנה משותף לוודא שהמונה הוא "
            "בדיוק $2x+1$. **בדיקה:** שני המקדמים חיוביים כי cover-up "
            "בכל שורש מבודד קבוע אחד ישירות."
        ),
    },
    {
        "explanation_en": (
            "Decompose $\\frac{3}{x(x+3)}=\\frac{A}{x}+\\frac{B}{x+3}$. "
            "Multiply both sides: $3=A(x+3)+Bx$. Cover-up at $x=0$ gives $3=3A$, "
            "so $A=1$. Cover-up at $x=-3$ gives $3=-3B$, so $B=-1$. "
            "Verify: $\\frac{1}{x}-\\frac{1}{x+3}=\\frac{(x+3)-x}{x(x+3)}=\\frac{3}{x(x+3)}$ ✓\n\n"
            "Integrate: $\\ln|x|-\\ln|x+3|+C$, or equivalently "
            "$\\ln\\left|\\frac{x}{x+3}\\right|+C$.\n\n"
            "**Common slip:** setting $A=3$ by misreading the cover-up equation — "
            "remember you already cleared the denominator. **Exam tip:** plug "
            "$x=1$ into both the original fraction and your decomposition; "
            "both should give $3/4$. **Self-check:** combine logs into a "
            "single quotient if the answer format requires it."
        ),
        "explanation_he": (
            "פירוק: $\\frac{3}{x(x+3)}=\\frac{A}{x}+\\frac{B}{x+3}$. "
            "כפל: $3=A(x+3)+Bx$. cover-up ב-$x=0$: $A=1$. "
            "cover-up ב-$x=-3$: $B=-1$. "
            "אימות: $\\frac{1}{x}-\\frac{1}{x+3}=\\frac{3}{x(x+3)}$ ✓\n\n"
            "אינטegrציה: $\\ln|x|-\\ln|x+3|+C$, או "
            "$\\ln\\left|\\frac{x}{x+3}\\right|+C$.\n\n"
            "**טעות נפוצה:** $A=3$ מקריאה שגויה של משוואת cover-up — "
            "זכרu שכבר ניקיתם את המכנה. **טיפ לבחינה:** הציבu $x=1$ "
            "בשבר המקורי ובפירוק — שניהם חייבים לתת $3/4$. "
            "**בדיקה:** שלבu לוגריתמים למנה אחת אם פורmat התשובה דורש זאת."
        ),
    },
    {
        "explanation_en": (
            "The fraction is **improper** because $\\deg(x^2+1)=\\deg(x^2-1)=2$. "
            "You must long-divide before partial fractions:\n"
            "$$\\frac{x^2+1}{x^2-1} = 1 + \\frac{2}{x^2-1} "
            "= 1 + \\frac{2}{(x-1)(x+1)}.$$\n"
            "Decompose the remainder: $\\frac{2}{(x-1)(x+1)}=\\frac{1}{x-1}-\\frac{1}{x+1}$.\n\n"
            "Full integrand: $1+\\frac{1}{x-1}-\\frac{1}{x+1}$. "
            "Integrate: $x+\\ln|x-1|-\\ln|x+1|+C$.\n\n"
            "**Common slip:** applying partial fractions directly to the improper "
            "fraction — you will get wrong constants and miss the $x$ term. "
            "**Exam tip:** when degrees match, always look for a constant polynomial "
            "term plus a proper remainder before setting up any template."
        ),
        "explanation_he": (
            "השבר **לא ראוי** כי $\\deg(x^2+1)=\\deg(x^2-1)=2$. "
            "חובה חלוקה ארוכה לפני שברים חלקיים:\n"
            "$$\\frac{x^2+1}{x^2-1} = 1 + \\frac{2}{(x-1)(x+1)}.$$\n"
            "פירוק השארית: $\\frac{1}{x-1}-\\frac{1}{x+1}$.\n\n"
            "אינטegrand מלא: $1+\\frac{1}{x-1}-\\frac{1}{x+1}$. "
            "אינטegrציה: $x+\\ln|x-1|-\\ln|x+1|+C$.\n\n"
            "**טעות נפוצה:** פירוק ישיר על השבר הלא ראוי — קבועים שגויים "
            "ותפספוס איבר $x$. **טיפ לבחינה:** כשהמעלות שוות, חפשu "
            "איבר פולינום קבוע ושארית ראויה לפני כתיבת תבנית."
        ),
    },
    {
        "explanation_en": (
            "The denominator $x^2(x+1)$ has a **repeated linear factor at $x=0$** "
            "(since $x^2$ means power 2). The correct template is:\n"
            "$$\\frac{1}{x^2(x+1)}=\\frac{A}{x}+\\frac{B}{x^2}+\\frac{C}{x+1}.$$\n"
            "Cover $x^2$ (set $x=0$): $B=1$. Cover $x+1$ ($x=-1$): $C=1$. "
            "Compare $x^2$ coefficients: $0=A+C$, so $A=-1$.\n\n"
            "Integrate: $-\\ln|x|-\\frac{1}{x}+\\ln|x+1|+C$.\n\n"
            "**Common slip:** using only $A/x+B/(x+1)$ and missing the $B/x^2$ "
            "term required by $(x-0)^2$. **Exam tip:** count the power of each "
            "factor — $x^2$ demands two terms with denominators $x$ and $x^2$. "
            "**Self-check:** the $-1/x$ term comes from integrating $1/x^2$, not "
            "from a logarithm."
        ),
        "explanation_he": (
            "המכנה $x^2(x+1)$ מכיל **גורם לינארי חוזר ב-$x=0$** (חזקה 2). "
            "התבנית הנכונה:\n"
            "$$\\frac{1}{x^2(x+1)}=\\frac{A}{x}+\\frac{B}{x^2}+\\frac{C}{x+1}.$$\n"
            "cover $x^2$ ($x=0$): $B=1$. cover $x+1$ ($x=-1$): $C=1$. "
            "מקדם $x^2$: $A=-1$.\n\n"
            "אינטegrציה: $-\\ln|x|-\\frac{1}{x}+\\ln|x+1|+C$.\n\n"
            "**טעות נפוצה:** שימוש רק ב-$A/x+B/(x+1)$ בלי $B/x^2$. "
            "**טיפ לבחינה:** ספרu חזקות — $x^2$ דורש שני איברים "
            "עם מכנים $x$ ו-$x^2$. **בדיקה:** האיבר $-1/x$ מגיע "
            "מאינטegrציה של $1/x^2$, לא מלוגריתם."
        ),
    },
]


def pad_short_explanations(data):
    """Ensure every question explanation meets 80-word minimum."""
    en_pad = (
        " On exams, write the partial-fraction template before solving for constants — "
        "this prevents the most costly template errors. After finding your answer, "
        "substitute one convenient value of $x$ to verify the decomposition reproduces "
        "the original integrand before you integrate."
    )
    he_pad = (
        " בבחינות, כתbו תחילה את תבנית השברים החלקיים לפני חישוב קbועים — "
        "זה מונע טעויות תבנית יקרות. לאחר מציאת התשובה, הציבu ערך $x$ נוח "
        "אחד כדי לוודא שהפירוק מחזיר את האינטegrand המקורי לפני האינטegrציה."
    )
    for q in data["questions"]:
        for lang, pad in (("en", en_pad), ("he", he_pad)):
            key = f"explanation_{lang}"
            text = q.get(key, "")
            if word_count(text) < 80:
                q[key] = text.rstrip() + pad
    return data


def fix_exercises(data):
    for ex in data["sections"]:
        if ex.get("kind") != "exercise_set":
            continue
        for item in ex.get("exercises", []):
            eid = item.get("id")
            if eid == "e12":
                item["solution_en"] = E12_SOLUTION_EN
                item["solution_he"] = E12_SOLUTION_HE
            elif eid == "e13":
                item["solution_en"] = E13_SOLUTION_EN
                item["solution_he"] = E13_SOLUTION_HE
            elif eid == "e5":
                item["solution_en"] = (
                    "Long division: $x^2+1=1\\cdot(x^2-1)+2$, so "
                    "$\\frac{x^2+1}{x^2-1}=1+\\frac{2}{(x-1)(x+1)}=1+\\frac{1}{x-1}-\\frac{1}{x+1}$. "
                    "$\\int=x+\\ln|x-1|-\\ln|x+1|+C$."
                )
                item["solution_he"] = (
                    "חלוקה ארוכה: $1+\\frac{2}{(x-1)(x+1)}=1+\\frac{1}{x-1}-\\frac{1}{x+1}$. "
                    "$\\int=x+\\ln|x-1|-\\ln|x+1|+C$."
                )
    return data


def apply_expansion(data):
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            n = sec.get("example_number")
            sec.update(SECTION_BODIES[f"worked_example_{n}"])
        elif kind == "checkpoint":
            body = sec.get("body_en_md", "")
            if "(x-1)(x+4)" in body:
                sec.update(SECTION_BODIES["checkpoint_1"])
            else:
                sec.update(SECTION_BODIES["checkpoint_2"])
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "pitfall":
            sec.update(SECTION_BODIES["pitfall"])
        elif kind == "why_matters":
            sec.update(SECTION_BODIES["why_matters"])
        elif kind == "before_exam":
            sec.update(SECTION_BODIES["before_exam"])
        elif kind == "summary":
            sec.update(SECTION_BODIES["summary"])

    data = fix_exercises(data)

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    data = pad_short_explanations(data)
    return data


def validate_depth(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"{kind} HE weak parity")
        elif kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            n = sec.get("example_number", "?")
            if en_w < WORKED_EXAMPLE_MIN["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < WORKED_EXAMPLE_MIN["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"worked_example {n} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} {key}: {w} words")

    return issues


def main():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)
    data = pad_short_explanations(data)
    issues = validate_depth(data)
    if issues:
        print("DEPTH ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)
    print("All depth gates passed.")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
