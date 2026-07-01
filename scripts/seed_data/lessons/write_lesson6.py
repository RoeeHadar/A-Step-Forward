"""Write Lesson 6: integration_by_parts"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))

lesson = {
  "id": "integration_by_parts",
  "type": "interactive",
  "subject": "calculus_2",
  "title_en": "Integration Techniques \u2014 By Parts & Partial Fractions",
  "title_he": "\u05e9\u05d9\u05d8\u05d5\u05ea \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u2014 \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u05d5\u05e9\u05d1\u05e8\u05d9\u05dd \u05d7\u05dc\u05e7\u05d9\u05d9\u05dd",
  "duration_min": 25,
  "level_min": "calculus_1",
  "agent_hints": "Technion 104032 students must master both by-parts and partial fractions fluently. For by-parts: the LIATE mnemonic is a reliable heuristic; the cyclic case (e^x cos x) requires recognizing the same integral reappears and solving algebraically. For partial fractions: the key is the correct setup (number of unknowns equals the degree of the denominator), and then using the Heaviside cover-up trick or comparing coefficients to find A, B, C. Repeated linear factors need one constant per power; irreducible quadratics need a linear numerator (Ax+B).",
  "sections": [
    {
      "id": "by_parts_formula",
      "title_en": "Integration by Parts \u2014 Formula and LIATE",
      "title_he": "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u2014 \u05e0\u05d5\u05e1\u05d7\u05d0 \u05d5\u05d0\u05e1\u05d8\u05e8\u05d8\u05d2\u05d9\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "**Integration by Parts** is derived from the product rule $(uv)' = u'v + uv'$:\n$$\\int u\\,dv = uv - \\int v\\,du.$$\n\n**How to choose $u$ and $dv$:** Use the **LIATE** mnemonic (higher priority = better choice for $u$):\n\n| Priority | Category | Examples |\n|---|---|---|\n| 1 (highest) | **L**ogarithms | $\\ln x$, $\\log x$ |\n| 2 | **I**nverse trig | $\\arctan x$, $\\arcsin x$ |\n| 3 | **A**lgebraic | $x^n$, polynomials |\n| 4 | **T**rigonometric | $\\sin x$, $\\cos x$ |\n| 5 (lowest) | **E**xponential | $e^x$, $a^x$ |\n\nChoose $u$ = the higher-priority function; $dv$ = everything else.\n\n**When to use by parts:** Integrals of the form $\\int p(x)e^x\\,dx$, $\\int p(x)\\sin x\\,dx$, $\\int \\ln x \\cdot p(x)\\,dx$, etc.",
      "body_he_md": "**אינטגרציה בחלקים** נגזרת מכלל המכפלה $(uv)' = u'v + uv'$:\n$$\\int u\\,dv = uv - \\int v\\,du.$$\n\n**כיצד לבחור $u$ ו-$dv$:** משתמשים בסיכרון **LIATE** (עדיפות גבוהה יותר = בחירה טובה יותר כ-$u$):\n\n| עדיפות | קטגוריה | דוגמאות |\n|---|---|---|\n| 1 (גבוהה) | לוגריתמים | $\\ln x$, $\\log x$ |\n| 2 | טריגונומטריה הפוכה | $\\arctan x$, $\\arcsin x$ |\n| 3 | אלגבריים | $x^n$, פולינומים |\n| 4 | טריגונומטריים | $\\sin x$, $\\cos x$ |\n| 5 (נמוכה) | מעריכיים | $e^x$, $a^x$ |\n\nבוחרים $u$ = הפונקציה בעדיפות גבוהה יותר; $dv$ = השאר."
    },
    {
      "id": "by_parts_examples",
      "title_en": "By Parts \u2014 Worked Examples",
      "title_he": "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u2014 \u05d3\u05d5\u05d2\u05de\u05d0\u05d5\u05ea \u05de\u05dc\u05d0\u05d5\u05ea",
      "level_min": "calculus_1",
      "body_en_md": "**Example 1.** $\\int x e^x\\,dx$.\n\nLIATE: $u = x$ (algebraic), $dv = e^x\\,dx$ (exponential).\n$du = dx$, $v = e^x$.\n$$\\int xe^x\\,dx = xe^x - \\int e^x\\,dx = xe^x - e^x + C = e^x(x-1) + C.$$\n\n**Example 2.** $\\int \\ln x\\,dx$.\n\nLet $u = \\ln x$ (log), $dv = dx$. Then $du = dx/x$, $v = x$.\n$$\\int \\ln x\\,dx = x\\ln x - \\int x \\cdot \\frac{1}{x}\\,dx = x\\ln x - x + C.$$\n\n**Example 3.** $\\int x^2 \\sin x\\,dx$ (apply by parts twice).\n\nFirst: $u = x^2$, $dv = \\sin x\\,dx$ gives $-x^2\\cos x + 2\\int x\\cos x\\,dx$.\nSecond: $u = x$, $dv = \\cos x\\,dx$ gives $2(x\\sin x + \\cos x)$.\n$$\\int x^2\\sin x\\,dx = -x^2\\cos x + 2x\\sin x + 2\\cos x + C.$$",
      "body_he_md": "**דוגמה 1.** $\\int x e^x\\,dx$.\n\n$u = x$, $dv = e^x\\,dx$. $du = dx$, $v = e^x$.\n$$\\int xe^x\\,dx = xe^x - e^x + C = e^x(x-1) + C.$$\n\n**דוגמה 2.** $\\int \\ln x\\,dx$.\n\n$u = \\ln x$, $dv = dx$. $du = dx/x$, $v = x$.\n$$\\int \\ln x\\,dx = x\\ln x - x + C.$$\n\n**דוגמה 3.** $\\int x^2 \\sin x\\,dx$ (שני שלבים).\n\nשלב א': $u = x^2$, $dv = \\sin x\\,dx$: נותן $-x^2\\cos x + 2\\int x\\cos x\\,dx$.\nשלב ב': $u = x$, $dv = \\cos x\\,dx$.\n$$\\int x^2\\sin x\\,dx = -x^2\\cos x + 2x\\sin x + 2\\cos x + C.$$"
    },
    {
      "id": "cyclic_by_parts",
      "title_en": "Cyclic By Parts \u2014 $\\int e^x \\cos x\\,dx$",
      "title_he": "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u05de\u05d7\u05d6\u05d5\u05e8\u05d9\u05ea \u2014 $\\int e^x \\cos x\\,dx$",
      "level_min": "calculus_1",
      "body_en_md": "When neither function simplifies under repeated by-parts (e.g., $e^x\\cos x$), apply by parts twice and solve algebraically.\n\n**Example.** $I = \\int e^x \\cos x\\,dx$.\n\n*First application:* $u = e^x$, $dv = \\cos x\\,dx \\Rightarrow v = \\sin x$.\n$$I = e^x\\sin x - \\int e^x\\sin x\\,dx.$$\n\n*Second application* on $\\int e^x\\sin x\\,dx$: $u = e^x$, $dv = \\sin x\\,dx \\Rightarrow v = -\\cos x$.\n$$\\int e^x\\sin x\\,dx = -e^x\\cos x + \\int e^x\\cos x\\,dx = -e^x\\cos x + I.$$\n\nSubstituting back:\n$$I = e^x\\sin x - (-e^x\\cos x + I) = e^x\\sin x + e^x\\cos x - I.$$\n$$2I = e^x(\\sin x + \\cos x) \\quad\\Rightarrow\\quad I = \\frac{e^x(\\sin x + \\cos x)}{2} + C.$$\n\n**Key insight:** The same integral $I$ reappears. Treat it as an unknown and solve for $I$.",
      "body_he_md": "כאשר אף פונקציה לא מתפשטת תחת אינטגרציה חוזרת (כמו $e^x\\cos x$), מפעילים שני שלבים ופותרים אלגברית.\n\n**דוגמה.** $I = \\int e^x \\cos x\\,dx$.\n\n*שלב א':* $u = e^x$, $dv = \\cos x\\,dx$:\n$$I = e^x\\sin x - \\int e^x\\sin x\\,dx.$$\n\n*שלב ב'* על $\\int e^x\\sin x\\,dx$: $u = e^x$, $dv = \\sin x\\,dx$:\n$$\\int e^x\\sin x\\,dx = -e^x\\cos x + I.$$\n\nמציבים חזרה:\n$$I = e^x\\sin x + e^x\\cos x - I \\quad\\Rightarrow\\quad 2I = e^x(\\sin x + \\cos x).$$\n$$I = \\frac{e^x(\\sin x + \\cos x)}{2} + C.$$\n\n**תובנה מרכזית:** האינטגרל $I$ מופיע שוב. מתייחסים אליו כאל נעלם ופותרים."
    },
    {
      "id": "partial_fractions_setup",
      "title_en": "Partial Fractions \u2014 Setup and Cases",
      "title_he": "\u05e9\u05d1\u05e8\u05d9\u05dd \u05d7\u05dc\u05e7\u05d9\u05d9\u05dd \u2014 \u05d4\u05ea\u05e7\u05e0\u05d5\u05ea \u05d5\u05de\u05e7\u05e8\u05d9\u05dd",
      "level_min": "calculus_1",
      "body_en_md": "**Goal:** integrate a rational function $\\dfrac{P(x)}{Q(x)}$ where $\\deg P < \\deg Q$.\n\n**Method:** Factor $Q(x)$, then decompose into partial fractions.\n\n### Case 1: Distinct linear factors\n$$\\frac{P(x)}{(ax+b)(cx+d)} = \\frac{A}{ax+b} + \\frac{B}{cx+d}.$$\nMultiply both sides by $Q(x)$ and compare coefficients (or substitute convenient $x$ values \u2014 Heaviside cover-up).\n\n### Case 2: Repeated linear factor\n$$\\frac{P(x)}{(ax+b)^2} = \\frac{A}{ax+b} + \\frac{B}{(ax+b)^2}.$$\nOne constant per power.\n\n### Case 3: Irreducible quadratic factor\n$$\\frac{P(x)}{(x^2+px+q)} = \\frac{Ax+B}{x^2+px+q}$$\nwhere $x^2+px+q$ has no real roots (discriminant $< 0$). The numerator must be linear.\n\n**If $\\deg P \\geq \\deg Q$:** Do polynomial long division first to write $P/Q = $ (polynomial) $+$ (proper fraction).",
      "body_he_md": "**מטרה:** לאנטגרל פונקציה רציונלית $\\dfrac{P(x)}{Q(x)}$ כאשר $\\deg P < \\deg Q$.\n\n**שיטה:** מפרקים את $Q(x)$ לגורמים, ואחר כך מפרקים לשברים חלקיים.\n\n### מקרה 1: גורמים לינאריים נבדלים\n$$\\frac{P(x)}{(ax+b)(cx+d)} = \\frac{A}{ax+b} + \\frac{B}{cx+d}.$$\n\n### מקרה 2: גורם לינארי חוזר\n$$\\frac{P(x)}{(ax+b)^2} = \\frac{A}{ax+b} + \\frac{B}{(ax+b)^2}.$$\n\n### מקרה 3: גורם ריבועי בלתי-פריק\n$$\\frac{P(x)}{x^2+px+q} = \\frac{Ax+B}{x^2+px+q}$$\n(מכנה ללא שורשים ממשיים; מונה לינארי).\n\n**אם $\\deg P \\geq \\deg Q$:** מחלקים פולינומים תחילה."
    },
    {
      "id": "partial_fractions_examples",
      "title_en": "Partial Fractions \u2014 Worked Examples",
      "title_he": "\u05e9\u05d1\u05e8\u05d9\u05dd \u05d7\u05dc\u05e7\u05d9\u05d9\u05dd \u2014 \u05d3\u05d5\u05d2\u05de\u05d0\u05d5\u05ea \u05de\u05dc\u05d0\u05d5\u05ea",
      "level_min": "calculus_1",
      "body_en_md": "**Example 1.** $\\int \\dfrac{1}{x^2-1}\\,dx$.\n\n$x^2-1 = (x-1)(x+1)$. Partial fractions: $\\dfrac{1}{(x-1)(x+1)} = \\dfrac{A}{x-1} + \\dfrac{B}{x+1}$.\n\nCover-up: $A = \\frac{1}{1+1} = \\frac{1}{2}$, $B = \\frac{1}{-1-1} = -\\frac{1}{2}$.\n$$\\int \\frac{1}{x^2-1}\\,dx = \\frac{1}{2}\\ln|x-1| - \\frac{1}{2}\\ln|x+1| + C = \\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right| + C.$$\n\n**Example 2.** $\\int \\dfrac{x}{(x-1)^2}\\,dx$.\n\n$\\dfrac{x}{(x-1)^2} = \\dfrac{A}{x-1} + \\dfrac{B}{(x-1)^2}$. Multiply: $x = A(x-1) + B$.\n\n$x=1$: $B=1$. Compare $x$: $A=1$.\n$$\\int\\frac{x}{(x-1)^2}\\,dx = \\int\\frac{dx}{x-1} + \\int\\frac{dx}{(x-1)^2} = \\ln|x-1| - \\frac{1}{x-1} + C.$$\n\n**Example 3.** $\\int \\dfrac{3x+5}{x^2-x-2}\\,dx$.\n\n$x^2-x-2=(x-2)(x+1)$. $\\dfrac{3x+5}{(x-2)(x+1)} = \\dfrac{A}{x-2}+\\dfrac{B}{x+1}$.\n\n$x=2$: $A = 11/3$. $x=-1$: $B = 2/3$.\n$$\\int\\frac{3x+5}{x^2-x-2}\\,dx = \\frac{11}{3}\\ln|x-2| + \\frac{2}{3}\\ln|x+1| + C.$$",
      "body_he_md": "**דוגמה 1.** $\\int \\dfrac{1}{x^2-1}\\,dx$.\n\n$(x-1)(x+1)$: $A=1/2$, $B=-1/2$.\n$$\\int \\frac{dx}{x^2-1} = \\frac{1}{2}\\ln\\left|\\frac{x-1}{x+1}\\right| + C.$$\n\n**דוגמה 2.** $\\int \\dfrac{x}{(x-1)^2}\\,dx$. $A=1$, $B=1$.\n$$= \\ln|x-1| - \\frac{1}{x-1} + C.$$\n\n**דוגמה 3.** $\\int \\dfrac{3x+5}{x^2-x-2}\\,dx$. $A=11/3$, $B=2/3$.\n$$= \\frac{11}{3}\\ln|x-2| + \\frac{2}{3}\\ln|x+1| + C.$$"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "To compute $\\int x^3 \\ln x\\,dx$ by parts, the LIATE rule suggests choosing:",
      "body_he": "\u05dc\u05d7\u05d9\u05e9\u05d5\u05d1 $\\int x^3 \\ln x\\,dx$ \u05d1\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd, \u05db\u05dc\u05dc LIATE \u05de\u05e6\u05d9\u05e2 \u05dc\u05d1\u05d7\u05d5\u05e8:",
      "options": [
        {"id": "a", "text_en": "$u = x^3$, $dv = \\ln x\\,dx$", "text_he": "$u = x^3$, $dv = \\ln x\\,dx$", "correct": False},
        {"id": "b", "text_en": "$u = \\ln x$, $dv = x^3\\,dx$", "text_he": "$u = \\ln x$, $dv = x^3\\,dx$", "correct": True},
        {"id": "c", "text_en": "$u = x^3 \\ln x$, $dv = dx$", "text_he": "$u = x^3 \\ln x$, $dv = dx$", "correct": False},
        {"id": "d", "text_en": "$u = 1$, $dv = x^3\\ln x\\,dx$", "text_he": "$u = 1$, $dv = x^3\\ln x\\,dx$", "correct": False}
      ],
      "explanation_en": "By LIATE, Logarithms have higher priority than Algebraic. So $u = \\ln x$ (L) and $dv = x^3\\,dx$ (A). This gives $du = dx/x$ and $v = x^4/4$, leading to $x^4\\ln x/4 - x^4/16 + C$.",
      "explanation_he": "\u05dc\u05e4\u05d9 LIATE, \u05dc\u05d5\u05d2\u05e8\u05d9\u05ea\u05de\u05d9\u05dd \u05d1\u05e2\u05d3\u05d9\u05e4\u05d5\u05ea \u05d2\u05d1\u05d5\u05d4\u05d4 \u05d9\u05d5\u05ea\u05e8 \u05de\u05d0\u05dc\u05d2\u05d1\u05e8\u05d0\u05d9\u05d9\u05dd. \u05dc\u05db\u05df $u = \\ln x$ (L) \u05d5-$dv = x^3\\,dx$ (A). \u05ea\u05d5\u05e6\u05d0\u05d4: $x^4\\ln x/4 - x^4/16 + C$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "Compute $\\int x e^{2x}\\,dx$.",
      "body_he": "\u05d7\u05e9\u05d1 $\\int x e^{2x}\\,dx$.",
      "options": [
        {"id": "a", "text_en": "$\\dfrac{xe^{2x}}{2} - \\dfrac{e^{2x}}{4} + C$", "text_he": "$\\dfrac{xe^{2x}}{2} - \\dfrac{e^{2x}}{4} + C$", "correct": True},
        {"id": "b", "text_en": "$\\dfrac{xe^{2x}}{2} - \\dfrac{e^{2x}}{2} + C$", "text_he": "$\\dfrac{xe^{2x}}{2} - \\dfrac{e^{2x}}{2} + C$", "correct": False},
        {"id": "c", "text_en": "$xe^{2x} - \\dfrac{e^{2x}}{2} + C$", "text_he": "$xe^{2x} - \\dfrac{e^{2x}}{2} + C$", "correct": False},
        {"id": "d", "text_en": "$\\dfrac{x^2 e^{2x}}{2} + C$", "text_he": "$\\dfrac{x^2 e^{2x}}{2} + C$", "correct": False}
      ],
      "explanation_en": "$u=x$, $dv=e^{2x}dx$, $du=dx$, $v=e^{2x}/2$. So $\\int xe^{2x}\\,dx = \\frac{x e^{2x}}{2} - \\int \\frac{e^{2x}}{2}\\,dx = \\frac{xe^{2x}}{2} - \\frac{e^{2x}}{4} + C$.",
      "explanation_he": "$u=x$, $dv=e^{2x}dx$, $v=e^{2x}/2$. \u05d0\u05d6: $\\frac{xe^{2x}}{2} - \\int\\frac{e^{2x}}{2}dx = \\frac{xe^{2x}}{2} - \\frac{e^{2x}}{4} + C$."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "When computing $\\int e^x \\cos x\\,dx$ by parts twice, what happens?",
      "body_he": "\u05d1\u05e2\u05ea \u05d7\u05d9\u05e9\u05d5\u05d1 $\\int e^x \\cos x\\,dx$ \u05e2\u05dd \u05e9\u05e0\u05d9 \u05e9\u05dc\u05d1\u05d9 \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd, \u05de\u05d4 \u05e7\u05d5\u05e8\u05d4?",
      "options": [
        {"id": "a", "text_en": "The integral reduces to zero", "text_he": "\u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05de\u05ea\u05e7\u05d6\u05e8 \u05dc\u05d0\u05e4\u05e1", "correct": False},
        {"id": "b", "text_en": "The original integral $I$ reappears on the right side; we solve $2I = e^x(\\sin x + \\cos x)$", "text_he": "\u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc $I$ \u05de\u05d5\u05e4\u05d9\u05e2 \u05e9\u05d5\u05d1 \u05d1\u05e6\u05d3 \u05d9\u05de\u05d9\u05df; \u05e4\u05d5\u05ea\u05e8\u05d9\u05dd $2I = e^x(\\sin x + \\cos x)$", "correct": True},
        {"id": "c", "text_en": "We get $\\int e^x\\cos x\\,dx = e^x\\sin x + C$ after two steps", "text_he": "\u05de\u05e7\u05d1\u05dc\u05d9\u05dd $\\int e^x\\cos x\\,dx = e^x\\sin x + C$ \u05dc\u05d0\u05d7\u05e8 \u05e9\u05e0\u05d9 \u05e9\u05dc\u05d1\u05d9\u05dd", "correct": False},
        {"id": "d", "text_en": "By-parts cannot be applied because $e^x\\cos x$ has no antiderivative", "text_he": "\u05d0\u05d9 \u05d0\u05e4\u05e9\u05e8 \u05dc\u05d4\u05e4\u05e2\u05d9\u05dc \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u05db\u05d9 \u05dc-$e^x\\cos x$ \u05d0\u05d9\u05df \u05e4\u05d9\u05e6\u05d5\u05d7", "correct": False}
      ],
      "explanation_en": "After two by-parts steps with $u=e^x$ each time, the original integral $I$ reappears: $I = e^x\\sin x + e^x\\cos x - I$. Solving: $2I = e^x(\\sin x + \\cos x)$, so $I = e^x(\\sin x + \\cos x)/2 + C$.",
      "explanation_he": "\u05dc\u05d0\u05d7\u05e8 \u05e9\u05e0\u05d9 \u05e9\u05dc\u05d1\u05d9\u05dd \u05e2\u05dd $u=e^x$: $I = e^x\\sin x + e^x\\cos x - I$. \u05e4\u05d5\u05ea\u05e8\u05d9\u05dd: $I = e^x(\\sin x + \\cos x)/2 + C$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "Set up the partial fractions decomposition for $\\dfrac{2x+3}{x(x-1)^2}$.",
      "body_he": "\u05d4\u05e7\u05dd \u05d0\u05ea \u05e4\u05d9\u05e8\u05d5\u05e7 \u05d4\u05e9\u05d1\u05e8\u05d9\u05dd \u05d4\u05d7\u05dc\u05e7\u05d9\u05d9\u05dd \u05e9\u05dc $\\dfrac{2x+3}{x(x-1)^2}$.",
      "options": [
        {"id": "a", "text_en": "$\\dfrac{A}{x} + \\dfrac{B}{(x-1)^2}$", "text_he": "$\\dfrac{A}{x} + \\dfrac{B}{(x-1)^2}$", "correct": False},
        {"id": "b", "text_en": "$\\dfrac{A}{x} + \\dfrac{B}{x-1} + \\dfrac{C}{(x-1)^2}$", "text_he": "$\\dfrac{A}{x} + \\dfrac{B}{x-1} + \\dfrac{C}{(x-1)^2}$", "correct": True},
        {"id": "c", "text_en": "$\\dfrac{A}{x} + \\dfrac{Bx+C}{(x-1)^2}$", "text_he": "$\\dfrac{A}{x} + \\dfrac{Bx+C}{(x-1)^2}$", "correct": False},
        {"id": "d", "text_en": "$\\dfrac{Ax+B}{x(x-1)^2}$", "text_he": "$\\dfrac{Ax+B}{x(x-1)^2}$", "correct": False}
      ],
      "explanation_en": "The denominator $x(x-1)^2$ has a simple factor $x$ and a repeated factor $(x-1)^2$. For the repeated linear factor, we need one constant per power: $B/(x-1)$ and $C/(x-1)^2$. Total: $A/x + B/(x-1) + C/(x-1)^2$.",
      "explanation_he": "\u05d4\u05de\u05db\u05e0\u05d4 $x(x-1)^2$ \u05e2\u05dd \u05d2\u05d5\u05e8\u05dd \u05e4\u05e9\u05d5\u05d8 $x$ \u05d5\u05d2\u05d5\u05e8\u05dd \u05d7\u05d5\u05d6\u05e8 $(x-1)^2$. \u05e2\u05d1\u05d5\u05e8 \u05d2\u05d5\u05e8\u05dd \u05d7\u05d5\u05d6\u05e8, \u05e6\u05e8\u05d9\u05da \u05e7\u05d1\u05d5\u05e2 \u05d0\u05d7\u05d3 \u05dc\u05db\u05dc \u05d7\u05d6\u05e7\u05d4: $B/(x-1)$ \u05d5-$C/(x-1)^2$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "To compute $\\int \\dfrac{1}{x^2+4}\\,dx$ (irreducible quadratic), the correct approach is:",
      "body_he": "\u05dc\u05d7\u05d9\u05e9\u05d5\u05d1 $\\int \\dfrac{1}{x^2+4}\\,dx$ (ריבועי \u05d1\u05dc\u05ea\u05d9-\u05e4\u05e8\u05d9\u05e7), \u05d4\u05d2\u05d9\u05e9\u05d4 \u05d4\u05e0\u05db\u05d5\u05e0\u05d4:",
      "options": [
        {"id": "a", "text_en": "Decompose $\\frac{1}{x^2+4} = \\frac{A}{x+2i} + \\frac{B}{x-2i}$ using complex roots", "text_he": "\u05e4\u05d9\u05e8\u05d5\u05e7 \u05dc\u05e9\u05d1\u05e8\u05d9\u05dd \u05e2\u05dd \u05e9\u05d5\u05e8\u05e9\u05d9\u05dd \u05de\u05e8\u05d5\u05db\u05d1\u05d9\u05dd", "correct": False},
        {"id": "b", "text_en": "Write $x^2+4 = (x/2)^2 \\cdot 4 + 4$ and use the formula $\\int \\frac{dx}{x^2+a^2} = \\frac{1}{a}\\arctan(x/a)+C$", "text_he": "\u05e9\u05d9\u05de\u05d5\u05e9 \u05d1\u05e0\u05d5\u05e1\u05d7\u05d0 $\\int \\frac{dx}{x^2+a^2} = \\frac{1}{a}\\arctan(x/a)+C$", "correct": True},
        {"id": "c", "text_en": "Apply integration by parts with $u = 1$ and $dv = dx/(x^2+4)$", "text_he": "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4 \u05d1\u05d7\u05dc\u05e7\u05d9\u05dd \u05e2\u05dd $u = 1$", "correct": False},
        {"id": "d", "text_en": "Substitute $x = \\tan\\theta$ to get $\\int \\sec^2\\theta\\,d\\theta$", "text_he": "\u05d4\u05e6\u05d1\u05d4 $x = \\tan\\theta$ \u05dc\u05e7\u05d1\u05dc $\\int \\sec^2\\theta\\,d\\theta$", "correct": False}
      ],
      "explanation_en": "Since $x^2+4 = x^2 + 2^2$ is irreducible (no real roots), use the standard formula with $a=2$: $\\int \\frac{dx}{x^2+4} = \\frac{1}{2}\\arctan(x/2)+C$. Option (d) actually also works but leads to extra steps; option (b) is the direct approach.",
      "explanation_he": "\u05de\u05db\u05d9\u05d5\u05d5\u05df \u05e9-$x^2+4$ \u05d1\u05dc\u05ea\u05d9-\u05e4\u05e8\u05d9\u05e7 (אין \u05e9\u05d5\u05e8\u05e9\u05d9\u05dd \u05de\u05de\u05e9\u05d9\u05d9\u05dd), \u05de\u05e9\u05ea\u05de\u05e9\u05d9\u05dd \u05d1\u05e0\u05d5\u05e1\u05d7\u05d0 \u05e2\u05dd $a=2$: $\\int \\frac{dx}{x^2+4} = \\frac{1}{2}\\arctan(x/2)+C$."
    }
  ]
}

path = os.path.join(BASE, lesson["id"] + ".json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
print(f"Saved {lesson['id']}")
