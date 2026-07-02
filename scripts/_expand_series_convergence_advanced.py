#!/usr/bin/env python3
"""Expand series_convergence_advanced.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/series_convergence_advanced.json"

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
            "In the previous lesson you learned **how to test** whether a series $\\sum a_n$ converges. "
            "This lesson asks a deeper question: **how** does it converge, and what happens when the "
            "terms depend on a variable $x$?\n\n"
            "Two ideas dominate advanced series work:\n\n"
            "1. **Absolute vs. conditional convergence.** A series can converge in a stronger sense "
            "(absolutely) or a weaker sense (conditionally). This distinction is not cosmetic — it "
            "determines whether you may rearrange terms. Absolutely convergent series behave like finite "
            "sums: rearrangement preserves the total. Conditionally convergent series obey **Riemann's "
            "rearrangement theorem**: with clever reordering, the partial sums can be driven toward "
            "**any** real number, or even to $\\pm\\infty$.\n\n"
            "2. **Power series** $\\sum a_n(x-c)^n$ converge on an interval centered at $c$. Finding "
            "the **radius** $R$ and checking **endpoints** $x = c \\pm R$ is the standard exam workflow. "
            "Taylor expansions for $e^x$, $\\ln(1+x)$, and $\\cos x$ all live here — this is where "
            "infinite series become practical tools for calculus."
        ),
        "body_he_md": (
            "בשיעור הקודם למדתם **איך לבדוק** אם טור $\\sum a_n$ מתכנס. בשיעור זה שואלים שאלה עמוקה יותר: "
            "**כיצד** הוא מתכנס, ומה קורה כשהאיברים תלויים במשתנה $x$?\n\n"
            "שני רעיונות שולטים בעבודה מתקדמת עם טורים:\n\n"
            "1. **התכנסות מוחלטת לעומת מותנית.** טור יכול להתכנס בצורה חזקה (מוחלטת) או חלשה (מותנית). "
            "ההבחנה אינה קוסמטית — היא קובעת האם מותר לסדר מחדש. טורים מתכנסים מוחלטית מתנהגים כמו סכומים "
            "סופיים: סידור מחדש שומר על הסכום. טורים מתכנסים מותנית כפופים ל**משפט הסידור מחדש של רימן**: "
            "בסידור חכם, הסכומים החלקיים יכולים להתקרב ל**כל** מספר ממשי, או אפילו ל-$\\pm\\infty$.\n\n"
            "2. **טורי חזקות** $\\sum a_n(x-c)^n$ מתכנסים על קטע ממורכז ב-$c$. מציאת **רדיוס** $R$ "
            "ובדיקת **קצוות** $x=c\\pm R$ היא תבנית העבודה הסטנדרטית בבחינות. "
            "טורי טיילור של $e^x$, $\\ln(1+x)$ ו-$\\cos x$ נמצאים כאן — כאן טורים אינסופיים "
            "הופכים לכלים מעשיים בחשבון."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Absolute convergence:** The series $\\sum_{n=1}^{\\infty} a_n$ converges **absolutely** "
            "if $\\sum_{n=1}^{\\infty} |a_n|$ converges. Intuitively, the series of magnitudes settles "
            "to a finite total — signs cannot cause cancellation.\n\n"
            "**Conditional convergence:** $\\sum a_n$ converges but $\\sum |a_n|$ diverges. The alternating "
            "harmonic series $\\sum (-1)^n/n$ is the canonical example: it sums to $-\\ln 2$, yet "
            "$\\sum 1/n$ diverges.\n\n"
            "**Key theorem:** Absolute convergence $\\Rightarrow$ convergence. The converse fails.\n\n"
            "**Riemann's Rearrangement Theorem:** If $\\sum a_n$ converges conditionally, then for any "
            "$L \\in [-\\infty, \\infty]$, there exists a rearrangement whose partial sums converge to $L$.\n\n"
            "**Power series:**\n"
            "$$\\sum_{n=0}^{\\infty} a_n(x-c)^n = a_0 + a_1(x-c) + a_2(x-c)^2 + \\cdots$$\n\n"
            "**Radius of convergence $R$:** There exists $R \\ge 0$ (possibly $R = \\infty$) such that:\n"
            "- The series converges **absolutely** for $|x-c| < R$.\n"
            "- It **diverges** for $|x-c| > R$.\n"
            "- At $|x-c| = R$ (the endpoints), convergence must be checked separately.\n\n"
            "**Finding $R$:** Often $R = \\lim_{n\\to\\infty} \\left|\\frac{a_n}{a_{n+1}}\\right|$ when the "
            "limit exists (from the ratio test on the coefficients)."
        ),
        "body_he_md": (
            "**התכנסות מוחלטת:** הטור $\\sum_{n=1}^{\\infty} a_n$ מתכנס **מוחלטית** אם "
            "$\\sum_{n=1}^{\\infty} |a_n|$ מתכנס. באינטואיציה, טור הגודלים מתייצב לסכום סופי — "
            "סימנים לא יכולים לגרום לביטול.\n\n"
            "**התכנסות מותנית:** $\\sum a_n$ מתכנס אך $\\sum |a_n|$ מתבדר. "
            "הטור ההרמוני האלטרנטיבי $\\sum (-1)^n/n$ הוא הדוגמה הקלאסית: "
            "הוא מסתכם ל-$-\\ln 2$, אך $\\sum 1/n$ מתבדר.\n\n"
            "**משפט מפתח:** התכנסות מוחלטית $\\Rightarrow$ התכנסות. ההפך אינו נכון.\n\n"
            "**משפט הסידור מחדש של רימן:** אם $\\sum a_n$ מתכנס מותנית, אז לכל "
            "$L \\in [-\\infty, \\infty]$ קיים סידור מחדש שסכומיו החלקיים מתכנסים ל-$L$.\n\n"
            "**טור חזקות:**\n"
            "$$\\sum_{n=0}^{\\infty} a_n(x-c)^n = a_0 + a_1(x-c) + a_2(x-c)^2 + \\cdots$$\n\n"
            "**רדיוס התכנסות $R$:** קיים $R \\ge 0$ (אולי $R=\\infty$) כך ש:\n"
            "- הטור מתכנס **מוחלטית** ל-$|x-c|<R$.\n"
            "- הוא **מתבדר** ל-$|x-c|>R$.\n"
            "- ב-$|x-c|=R$ (הקצוות) יש לבדוק התכנסות בנפרד.\n\n"
            "**מציאת $R$:** לעיתים $R=\\lim_{n\\to\\infty}\\left|\\frac{a_n}{a_{n+1}}\\right|$ "
            "כשהגבול קיים (ממבחן המנה על המקדמים)."
        ),
    },
    "theory": {
        "body_en_md": (
            "**Alternating Series Test (Leibniz):** $\\sum (-1)^n b_n$ with $b_n > 0$ converges if "
            "$b_n$ is decreasing and $b_n \\to 0$. This proves convergence only — not absolute convergence.\n\n"
            "**Absolute convergence check:** Apply the ratio or root test to $\\sum |a_n|$. "
            "If $\\sum |a_n|$ converges, the original series is absolutely convergent.\n\n"
            "**Ratio Test:** $L = \\lim_{n\\to\\infty} \\left|\\frac{a_{n+1}}{a_n}\\right|$.\n"
            "- $L < 1$: converges absolutely.\n"
            "- $L > 1$: diverges.\n"
            "- $L = 1$: inconclusive — try another test (common at endpoints).\n\n"
            "**Root Test:** $L = \\lim_{n\\to\\infty} |a_n|^{1/n}$. Same three-way conclusion.\n\n"
            "**Power series — ratio test for radius:** For $\\sum a_n(x-c)^n$,\n"
            "$$L = \\lim_{n\\to\\infty}\\left|\\frac{a_{n+1}(x-c)^{n+1}}{a_n(x-c)^n}\\right| "
            "= |x-c| \\lim_{n\\to\\infty}\\left|\\frac{a_{n+1}}{a_n}\\right|.$$\n"
            "Convergence requires $L < 1$, i.e. $|x-c| < R$ where "
            "$R = \\lim \\left|\\frac{a_n}{a_{n+1}}\\right|$ when the limit exists.\n\n"
            "**Standard power series (memorise):**\n"
            "- $e^x = \\sum_{n=0}^{\\infty} \\frac{x^n}{n!}$, $R = \\infty$ (factorials dominate).\n"
            "- $\\ln(1+x) = \\sum_{n=1}^{\\infty} \\frac{(-1)^{n+1}x^n}{n}$, $R = 1$.\n"
            "- $\\frac{1}{1-x} = \\sum_{n=0}^{\\infty} x^n$, $R = 1$ (geometric).\n"
            "- $\\cos x = \\sum_{n=0}^{\\infty} \\frac{(-1)^n x^{2n}}{(2n)!}$, $R = \\infty$.\n\n"
            "**Rearrangement principle:** If $\\sum |a_n|$ converges, any reordering of terms converges to the "
            "same sum. If convergence is conditional only, rearrangement is unsafe — this is why absolute "
            "convergence is the preferred hypothesis in analysis and probability."
        ),
        "body_he_md": (
            "**מבחן לייבניץ (טור מתחלף):** $\\sum (-1)^n b_n$ עם $b_n>0$ מתכנס אם "
            "$b_n$ יורד ו-$b_n\\to 0$. המבחן מוכיח התכנסות בלבד — לא התכנסות מוחלטית.\n\n"
            "**בדיקת התכנסות מוחלטת:** הפעילו מבחן מנה או שורש על $\\sum |a_n|$. "
            "אם $\\sum |a_n|$ מתכנס, הטור המקורי מתכנס מוחלטית.\n\n"
            "**מבחן המנה:** $L=\\lim\\left|\\frac{a_{n+1}}{a_n}\\right|$.\n"
            "- $L<1$: מתכנס מוחלטית.\n"
            "- $L>1$: מתבדר.\n"
            "- $L=1$: לא מכריע — נסו מבחן אחר (נפוץ בקצוות).\n\n"
            "**מבחן השורש:** $L=\\lim |a_n|^{1/n}$. אותה מסקנה תלת-כיוונית.\n\n"
            "**טורי חזקות — מבחן מנה לרדיוס:** עבור $\\sum a_n(x-c)^n$,\n"
            "$$L=\\lim\\left|\\frac{a_{n+1}(x-c)^{n+1}}{a_n(x-c)^n}\\right|"
            "=|x-c|\\lim\\left|\\frac{a_{n+1}}{a_n}\\right|.$$\n"
            "התכנסות דורשת $L<1$, כלומר $|x-c|<R$ כאשר "
            "$R=\\lim\\left|\\frac{a_n}{a_{n+1}}\\right|$ כשהגבול קיים.\n\n"
            "**טורי חזקות סטנדרטיים (לשינון):**\n"
            "- $e^x=\\sum \\frac{x^n}{n!}$, $R=\\infty$ (עצרות שולטות).\n"
            "- $\\ln(1+x)=\\sum \\frac{(-1)^{n+1}x^n}{n}$, $R=1$.\n"
            "- $\\frac{1}{1-x}=\\sum x^n$, $R=1$ (הנדסי).\n"
            "- $\\cos x=\\sum \\frac{(-1)^n x^{2n}}{(2n)!}$, $R=\\infty$.\n\n"
            "**עקרון סידור מחדש:** אם $\\sum |a_n|$ מתכנס, כל סידור מחדש של איברים מתכנס לאותו סכום. "
            "אם ההתכנסות מותנית בלבד, סידור מחדש אינו בטוח — לכן התכנסות מוחלטית היא ההנחה המועדפת "
            "באנליזה ובהסתברות."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Determine** whether $\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{n}$ converges absolutely, "
            "conditionally, or diverges.\n\n"
            "### Move 1: Test absolute convergence\n"
            "$$\\sum_{n=1}^{\\infty}\\left|\\frac{(-1)^n}{n}\\right| = \\sum_{n=1}^{\\infty}\\frac{1}{n}.$$\n"
            "This is the **harmonic series** — a p-series with $p = 1$. Since $p \\not> 1$, "
            "the series of absolute values **diverges**. The series is **not** absolutely convergent.\n\n"
            "### Move 2: Test conditional convergence\n"
            "Write as $\\sum (-1)^n b_n$ with $b_n = 1/n > 0$. Check Leibniz conditions:\n"
            "- $b_n = 1/n$ is strictly decreasing (denominator grows).\n"
            "- $\\lim_{n\\to\\infty} b_n = 0$.\n"
            "Both hold, so by the **Alternating Series Test**, the original series **converges**.\n\n"
            "### Move 3: Conclusion\n"
            "The series converges but not absolutely — it is **conditionally convergent**. "
            "This is the alternating harmonic series; its sum is $-\\ln 2 \\approx -0.693$. "
            "Because convergence is conditional, rearranging terms can change the sum — "
            "a dramatic illustration of Riemann's theorem.\n\n"
            "**Exam note:** Always report three-way classification: absolutely convergent, conditionally "
            "convergent, or divergent. Stopping after Leibniz without testing $\\sum |a_n|$ loses half the credit. "
            "The alternating harmonic series appears in every standard calculus textbook as the flagship conditional example."
        ),
        "body_he_md": (
            "**קבעו** האם $\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{n}$ מתכנס מוחלטית, מותנית, או מתבדר.\n\n"
            "### צעד 1: בדיקת התכנסות מוחלטת\n"
            "$$\\sum_{n=1}^{\\infty}\\left|\\frac{(-1)^n}{n}\\right|=\\sum_{n=1}^{\\infty}\\frac{1}{n}.$$\n"
            "זהו **הטור ההרמוני** — טור p עם $p=1$. מכיוון ש-$p \\not> 1$, "
            "טור הערכים המוחלטים **מתבדר**. הטור **אינו** מתכנס מוחלטית.\n\n"
            "### צעד 2: בדיקת התכנסות מותנית\n"
            "כתבו $\\sum (-1)^n b_n$ עם $b_n=1/n>0$. בדקו תנאי לייבניץ:\n"
            "- $b_n=1/n$ יורד קפדנית (המכנה גדל).\n"
            "- $\\lim_{n\\to\\infty} b_n=0$.\n"
            "שניהם מתקיימים, לכן לפי **מבחן לייבניץ** הטור המקורי **מתכנס**.\n\n"
            "### צעד 3: מסקנה\n"
            "הטור מתכנס אך לא מוחלטית — הוא **מתכנס מותנית**. "
            "זהו הטור ההרמוני האלטרנטיבי; סכומו $-\\ln 2\\approx -0.693$. "
            "מכיוון שההתכנסות מותנית, סידור מחדש יכול לשנות את הסכום — "
            "הדגמה דרמטית של משפט רימן.\n\n"
            "**הערה לבחינה:** דווחו תמיד על סיווג תלת-כיווני: מוחלטית, מותנית, או מתבדר. "
            "עצירה אחרי לייבניץ בלי בדיקת $\\sum |a_n|$ מאבדת חצי מהנקודות."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Find** the radius and interval of convergence of "
            "$\\sum_{n=1}^{\\infty} \\frac{x^n}{n}$.\n\n"
            "### Move 1: Apply the Ratio Test\n"
            "$$L = \\lim_{n\\to\\infty}\\left|\\frac{x^{n+1}/(n+1)}{x^n/n}\\right| "
            "= |x| \\lim_{n\\to\\infty}\\frac{n}{n+1} = |x| \\cdot 1 = |x|.$$\n\n"
            "### Move 2: Determine the radius\n"
            "The series converges absolutely when $L < 1$, i.e. $|x| < 1$. "
            "It diverges when $|x| > 1$. Therefore **$R = 1$** and the open interval is $(-1, 1)$.\n\n"
            "### Move 3: Check endpoints\n"
            "- **$x = 1$:** $\\sum_{n=1}^{\\infty} \\frac{1}{n}$ — harmonic series. **Diverges.**\n"
            "- **$x = -1$:** $\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{n}$ — alternating harmonic. "
            "Leibniz applies ($1/n \\searrow 0$). **Converges** (conditionally).\n\n"
            "### Move 4: Conclusion\n"
            "**Interval of convergence:** $[-1, 1)$ — closed at the left endpoint, open at the right. "
            "This pattern (convergence at $x = -R$ but divergence at $x = R$) is common when "
            "the denominator is $n$ rather than $n^2$.\n\n"
            "**Self-check:** At $x = -1$ the endpoint series is the alternating harmonic — conditionally "
            "convergent, not absolute. At $x = 1$ the harmonic series diverges, confirming the half-open interval."
        ),
        "body_he_md": (
            "**מצאו** רדיוס ותחום התכנסות של $\\sum_{n=1}^{\\infty} \\frac{x^n}{n}$.\n\n"
            "### צעד 1: הפעלת מבחן המנה\n"
            "$$L=\\lim\\left|\\frac{x^{n+1}/(n+1)}{x^n/n}\\right|"
            "=|x|\\lim\\frac{n}{n+1}=|x|\\cdot 1=|x|.$$\n\n"
            "### צעד 2: קביעת הרדיוס\n"
            "הטור מתכנס מוחלטית כאשר $L<1$, כלומר $|x|<1$. "
            "הוא מתבדר כאשר $|x|>1$. לכן **$R=1$** והקטע הפתוח הוא $(-1,1)$.\n\n"
            "### צעד 3: בדיקת קצוות\n"
            "- **$x=1$:** $\\sum \\frac{1}{n}$ — טור הרמוני. **מתבדר.**\n"
            "- **$x=-1$:** $\\sum \\frac{(-1)^n}{n}$ — הרמוני אלטרנטיבי. "
            "לייבניץ מתקיים ($1/n\\searrow 0$). **מתכנס** (מותנית).\n\n"
            "### צעד 4: מסקנה\n"
            "**תחום התכנסות:** $[-1,1)$ — סגור בקצה השמאלי, פתוח בימני. "
            "דפוס זה (התכנסות ב-$x=-R$ אך התבדרות ב-$x=R$) נפוץ כשהמכנה הוא $n$ ולא $n^2$.\n\n"
            "**בדיקה עצמית:** ב-$x=-1$ טור הקצה הוא ההרמוני האלטרנטיבי — מותנית, לא מוחלטית. "
            "ב-$x=1$ הטור ההרמוני מתבדר, מאשר את הקטע החצי-פתוח."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Find** the interval of convergence of "
            "$\\sum_{n=0}^{\\infty} \\frac{(-1)^n(x-2)^n}{\\sqrt{n+1}}$.\n\n"
            "### Move 1: Ratio Test for radius\n"
            "$$L = |x-2| \\lim_{n\\to\\infty}\\frac{\\sqrt{n+1}}{\\sqrt{n+2}} "
            "= |x-2| \\cdot 1 = |x-2|.$$\n"
            "Converges when $|x-2| < 1$, i.e. $1 < x < 3$. Diverges when $|x-2| > 1$. "
            "**Radius $R = 1$**, center $c = 2$.\n\n"
            "### Move 2: Check $x = 3$ (right endpoint, $x - 2 = 1$)\n"
            "$$\\sum_{n=0}^{\\infty} \\frac{(-1)^n}{\\sqrt{n+1}}. \\quad b_n = 1/\\sqrt{n+1} \\searrow 0.$$\n"
            "Leibniz conditions hold. The endpoint series **converges** (conditionally).\n\n"
            "### Move 3: Check $x = 1$ (left endpoint, $x - 2 = -1$)\n"
            "$$\\sum_{n=0}^{\\infty} \\frac{(-1)^n(-1)^n}{\\sqrt{n+1}} "
            "= \\sum_{n=0}^{\\infty} \\frac{1}{\\sqrt{n+1}} = \\sum n^{-1/2}.$$\n"
            "This is a p-series with $p = 1/2 < 1$. **Diverges.**\n\n"
            "### Move 4: Conclusion\n"
            "**Interval of convergence:** $(1, 3]$ — open at $x = 1$, closed at $x = 3$. "
            "Always report endpoints explicitly; the ratio test alone never determines them.\n\n"
            "**Why endpoints differ:** At $x = 3$ the alternating factor $(-1)^n$ combines with "
            "$1/\\sqrt{n+1}$ (Leibniz-friendly). At $x = 1$ the powers cancel to give a pure "
            "p-series with $p = 1/2$ — no alternation to help. This half-open interval $(1, 3]$ "
            "is a typical exam-level answer when the center is not at the origin."
        ),
        "body_he_md": (
            "**מצאו** תחום התכנסות של "
            "$\\sum_{n=0}^{\\infty} \\frac{(-1)^n(x-2)^n}{\\sqrt{n+1}}$.\n\n"
            "### צעד 1: מבחן מנה לרדיוס\n"
            "$$L=|x-2|\\lim\\frac{\\sqrt{n+1}}{\\sqrt{n+2}}=|x-2|\\cdot 1=|x-2|.$$\n"
            "מתכנס כאשר $|x-2|<1$, כלומר $1<x<3$. מתבדר כאשר $|x-2|>1$. "
            "**רדיוס $R=1$**, מרכז $c=2$.\n\n"
            "### צעד 2: בדיקת $x=3$ (קצה ימני, $x-2=1$)\n"
            "$$\\sum \\frac{(-1)^n}{\\sqrt{n+1}}. \\quad b_n=1/\\sqrt{n+1}\\searrow 0.$$\n"
            "תנאי לייבניץ מתקיימים. טור הקצה **מתכנס** (מותנית).\n\n"
            "### צעד 3: בדיקת $x=1$ (קצה שמאלי, $x-2=-1$)\n"
            "$$\\sum \\frac{(-1)^n(-1)^n}{\\sqrt{n+1}}=\\sum \\frac{1}{\\sqrt{n+1}}=\\sum n^{-1/2}.$$\n"
            "זהו טור p עם $p=1/2<1$. **מתבדר.**\n\n"
            "### צעד 4: מסקנה\n"
            "**תחום התכנסות:** $(1,3]$ — פתוח ב-$x=1$, סגור ב-$x=3$. "
            "דווחו תמיד על קצוות במפורש; מבחן המנה לבדו אינו קובע אותם.\n\n"
            "**מדוע הקצוות שונים:** ב-$x=3$ הגורם $(-1)^n$ משתלב עם $1/\\sqrt{n+1}$ (מתאים ללייבניץ). "
            "ב-$x=1$ החזקות מתבטלות ונותנות טור p טהור עם $p=1/2$ — "
            "ללא התחלפות שתעזור."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "**Step 1 — Absolute convergence:** "
            "$\\sum_{n=1}^{\\infty} \\left|\\frac{(-1)^n}{n^2}\\right| = \\sum_{n=1}^{\\infty} \\frac{1}{n^2}$. "
            "This is a p-series with $p = 2 > 1$, so it **converges**.\n\n"
            "**Step 2 — Conclusion:** Since $\\sum |a_n|$ converges, the original series converges "
            "**absolutely**. No need to apply Leibniz — absolute convergence is the stronger condition."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — התכנסות מוחלטת:** "
            "$\\sum \\left|\\frac{(-1)^n}{n^2}\\right|=\\sum \\frac{1}{n^2}$. "
            "זהו טור p עם $p=2>1$, לכן **מתכנס**.\n\n"
            "**שלב 2 — מסקנה:** מכיוון ש-$\\sum |a_n|$ מתכנס, הטור המקורי מתכנס **מוחלטית**. "
            "אין צורך בלייבניץ — התכנסות מוחלטית היא התנאי החזק יותר."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "**Step 1 — Ratio Test:** "
            "$$L = \\lim_{n\\to\\infty}\\left|\\frac{x^{n+1}/(n+1)!}{x^n/n!}\\right| "
            "= \\lim_{n\\to\\infty}\\frac{|x|}{n+1} = 0 \\quad \\text{for all } x.$$\n\n"
            "**Step 2 — Conclusion:** Since $L = 0 < 1$ for every real $x$, the series converges "
            "absolutely everywhere. **Radius $R = \\infty$.** This is the Taylor series for $e^x$."
        ),
        "checkpoint_solution_he": (
            "**שלב 1 — מבחן מנה:** "
            "$$L=\\lim\\left|\\frac{x^{n+1}/(n+1)!}{x^n/n!}\\right|"
            "=\\lim\\frac{|x|}{n+1}=0 \\quad \\text{לכל } x.$$\n\n"
            "**שלב 2 — מסקנה:** מכיוון ש-$L=0<1$ לכל $x$ ממשי, הטור מתכנס מוחלטית בכל מקום. "
            "**רדיוס $R=\\infty$.** זהו טור טיילור של $e^x$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "**Step 1: Identify the type.**\n"
            "- Alternating series $\\sum (-1)^n b_n$? → Leibniz test for convergence; "
            "then test $\\sum b_n$ for absolute convergence.\n"
            "- Power series $\\sum a_n(x-c)^n$? → Find $R$ first with the ratio test.\n\n"
            "**Step 2: Classify absolute vs. conditional.**\n"
            "Apply ratio/root test to $\\sum |a_n|$:\n"
            "- Converges → **absolutely convergent**.\n"
            "- Diverges → check conditional convergence with Leibniz (if alternating).\n\n"
            "**Step 3: For power series — find $R$, then check endpoints.**\n"
            "Plug $x = c + R$ and $x = c - R$ separately. Use p-series, Leibniz, or comparison.\n\n"
            "| Result | Conclusion |\n"
            "|---|---|\n"
            "| $\\sum|a_n|$ converges | Absolutely convergent |\n"
            "| $\\sum|a_n|$ diverges, $\\sum a_n$ converges by AST | Conditionally convergent |\n"
            "| Both diverge | Diverges |\n\n"
            "**Interval format:** $(c-R, c+R)$ open; $[c-R, c+R]$ closed; half-open depends on endpoints."
        ),
        "body_he_md": (
            "**שלב 1: זיהוי הסוג.**\n"
            "- טור מתחלף $\\sum (-1)^n b_n$? → מבחן לייבניץ להתכנסות; "
            "ואז בדקו $\\sum b_n$ להתכנסות מוחלטית.\n"
            "- טור חזקות $\\sum a_n(x-c)^n$? → מצאו $R$ תחילה במבחן המנה.\n\n"
            "**שלב 2: סיווג מוחלטת לעומת מותנית.**\n"
            "הפעילו מבחן מנה/שורש על $\\sum |a_n|$:\n"
            "- מתכנס → **מתכנס מוחלטית**.\n"
            "- מתבדר → בדקו התכנסות מותנית בלייבניץ (אם מתחלף).\n\n"
            "**שלב 3: לטורי חזקות — $R$, ואז קצוות.**\n"
            "הציבו $x=c+R$ ו-$x=c-R$ בנפרד. השתמשו בטורי p, לייבניץ, או השוואה.\n\n"
            "| תוצאה | מסקנה |\n"
            "|---|---|\n"
            "| $\\sum|a_n|$ מתכנס | מוחלטית |\n"
            "| $\\sum|a_n|$ מתבדר, $\\sum a_n$ מתכנס ע\"י לייבניץ | מותנית |\n"
            "| שניהם מתבדרים | מתבדר |\n\n"
            "**תבנית תחום:** $(c-R,c+R)$ פתוח; $[c-R,c+R]$ סגור; חצי-פתוח תלוי בקצוות."
        ),
    },
    "exercise_set": {
        "body_en_md": (
            "Work through every exercise below. **Try each one before opening the solution** — "
            "the classification steps (absolute vs. conditional) and endpoint checks matter as much "
            "as the final interval notation."
        ),
        "body_he_md": (
            "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — "
            "שלבי הסיווג (מוחלטת לעומת מותנית) ובדיקות הקצוות חשובים לא פחות מסימון התחום הסופי."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting endpoint checks.** The ratio test gives $R$ and the open interval "
            "$(c-R, c+R)$ — never the full interval of convergence. Always substitute "
            "$x = c \\pm R$ and test separately.\n\n"
            "2. **Confusing conditional with absolute.** Leibniz proves convergence, not absolute "
            "convergence. A series can pass Leibniz yet fail $\\sum |a_n|$ — that is conditional.\n\n"
            "3. **Ratio test inconclusive at $L = 1$.** This happens frequently at endpoints. "
            "Switch to p-series, Leibniz, integral test, or comparison.\n\n"
            "4. **Rearranging conditionally convergent series.** Never assume "
            "$1 - 1/2 + 1/3 - \\cdots$ behaves like a finite sum. Riemann's theorem says otherwise.\n\n"
            "**Exam habit:** After finding $R$, write \"Check $x = \\ldots$\" for both endpoints "
            "before moving on — exam graders deduct points for missing endpoint analysis."
        ),
        "body_he_md": (
            "1. **שכחת בדיקת קצוות.** מבחן המנה נותן $R$ ואת הקטע הפתוח "
            "$(c-R,c+R)$ — לעולם לא את תחום ההתכנסות המלא. הציבו תמיד "
            "$x=c\\pm R$ ובדקו בנפרד.\n\n"
            "2. **בלבול מותנית עם מוחלטת.** לייבניץ מוכיח התכנסות, לא התכנסות מוחלטית. "
            "טור יכול לעבור לייבניץ ולהיכשל ב-$\\sum |a_n|$ — זו התכנסות מותנית.\n\n"
            "3. **מבחן מנה לא מכריע ב-$L=1$.** זה קורה לעיתים קרובות בקצוות. "
            "עברו לטורי p, לייבניץ, מבחן אינטגרל, או השוואה.\n\n"
            "4. **סידור מחדש של טור מותנית.** אל תניחו ש-$1-1/2+1/3-\\cdots$ "
            "מתנהג כמו סכום סופי. משפט רימן אומר אחרת.\n\n"
            "**הרגל לבחינה:** אחרי מציאת $R$, כתבו \"בדוק $x=\\ldots$\" לשני הקצוות "
            "לפני שממשיכים — בוחנים מורידים נקודות על ניתוח קצוות חסר."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Advanced series convergence is the bridge between **infinite sums** and **functions**. "
            "Power series let you represent $e^x$, $\\sin x$, and $\\ln(1+x)$ as polynomials of "
            "infinite degree — the foundation of Taylor and Maclaurin expansions used throughout "
            "calculus, differential equations, and physics.\n\n"
            "Understanding absolute vs. conditional convergence explains why term rearrangement is "
            "safe in some contexts (Fourier analysis, probability) and dangerous in others.\n\n"
            "**Recommended next topics:**\n"
            "- `concept:improper_integrals` — integral test connects series and integrals.\n"
            "- `concept:integrals_techniques` — Taylor series justify substitution tricks.\n\n"
            "University exams and Bagrut 5-unit calculus both test interval-of-convergence problems "
            "as multi-step reasoning tasks, not formula recall."
        ),
        "body_he_md": (
            "התכנסות טורים מתקדמת היא הגשר בין **סכומים אינסופיים** ל**פונקציות**. "
            "טורי חזקות מאפשרים לייצג $e^x$, $\\sin x$ ו-$\\ln(1+x)$ כפולינומים "
            "בדרגה אינסופית — הבסיס להתרחבויות טיילור ומקלורן בחשבון, "
            "במשוואות דיפרנציאליות ובפיזיקה.\n\n"
            "הבנת מוחלטת לעומת מותנית מסבירה מדוע סידור מחדש בטוח בהקשרים מסוימים "
            "(פourier, הסתברות) ומסוכן באחרים.\n\n"
            "**נושאים מומלצים להמשך:**\n"
            "- `concept:improper_integrals` — מבחן האינטגרל מקשר טורים ואינטגרלים.\n"
            "- `concept:integrals_techniques` — טורי טיילור מצדיקים טריקים של החלפה.\n\n"
            "בחינות אוניברסיטה ובגרות 5 יחידות בודקות תחום התכנסות כמשימות "
            "היסק רב-שלבי, לא שינון נוסחאות."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Checklist for power series problems:**\n"
            "1. Apply Ratio Test to find $R$ (factor out $|x-c|$ cleanly).\n"
            "2. State the open interval $(c-R, c+R)$ where absolute convergence holds.\n"
            "3. Substitute $x = c + R$ and $x = c - R$ — simplify before choosing a test.\n"
            "4. Use AST, p-series, or comparison at endpoints; report closed/open/half-open interval.\n\n"
            "**Key facts to recall:**\n"
            "- $\\sum 1/n$: diverges. $\\sum 1/n^2$: converges.\n"
            "- $\\sum (-1)^n/n$: conditional. $\\sum (-1)^n/n^2$: absolute.\n"
            "- $e^x$ has $R = \\infty$; $\\ln(1+x)$ and $1/(1-x)$ have $R = 1$.\n\n"
            "**Last review:** Solve one interval-of-convergence problem from start to endpoints "
            "without notes, then verbalise why each endpoint passes or fails."
        ),
        "body_he_md": (
            "**רשימת בדיקה לבעיות טור חזקות:**\n"
            "1. הפעילו מבחן מנה למציאת $R$ (הוציאו $|x-c|$ בצורה נקייה).\n"
            "2. ציינו את הקטע הפתוח $(c-R,c+R)$ שבו מתקיימת התכנסות מוחלטית.\n"
            "3. הציבו $x=c+R$ ו-$x=c-R$ — פשטו לפני בחירת מבחן.\n"
            "4. השתמשו בלייבניץ, טורי p, או השוואה בקצוות; דווחו קטע סגור/פתוח/חצי-פתוח.\n\n"
            "**עובדות מרכזיות:**\n"
            "- $\\sum 1/n$: מתבדר. $\\sum 1/n^2$: מתכנס.\n"
            "- $\\sum (-1)^n/n$: מותנית. $\\sum (-1)^n/n^2$: מוחלטית.\n"
            "- ל-$e^x$: $R=\\infty$; ל-$\\ln(1+x)$ ו-$1/(1-x)$: $R=1$.\n\n"
            "**חזרה אחרונה:** פתרו בעיית תחום התכנסות אחת מהתחלה ועד קצוות "
            "בלי רשימות, ואז הסבירו בעל פה מדוע כל קצה עובר או נכשל."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Absolutely convergent** series can be rearranged freely; **conditionally convergent** "
            "series obey Riemann's theorem — rearrangement can change the sum to anything.\n"
            "- **Ratio/Root Test:** $L < 1$ absolute convergence, $L > 1$ divergence, $L = 1$ inconclusive.\n"
            "- **Power series** have radius $R$; converge absolutely on $(c-R, c+R)$; endpoints require separate tests.\n"
            "- **Workflow:** classify type → test $\\sum |a_n|$ → for power series, find $R$ then check $x = c \\pm R$.\n\n"
            "**Takeaway:** Endpoint analysis separates exam-ready students from those who stop at the ratio test."
        ),
        "body_he_md": (
            "- טור **מתכנס מוחלטית** — ניתן לסדר מחדש בחופשיות; טור **מותנית** — "
            "משפט רימן: סידור מחדש יכול לשנות את הסכום לכל ערך.\n"
            "- **מבחן מנה/שורש:** $L<1$ מוחלטית, $L>1$ התבדרות, $L=1$ לא מכריע.\n"
            "- **טור חזקות** עם רדיוס $R$; מתכנס מוחלטית ב-$(c-R,c+R)$; קצוות דורשים בדיקה נפרדת.\n"
            "- **תבנית עבודה:** סיווג סוג → בדיקת $\\sum |a_n|$ → לטור חזקות, $R$ ואז $x=c\\pm R$.\n\n"
            "**מסקנה:** ניתוח קצוות מפריד בין סטודנטים מוכנים לבחינה לבין מי שעוצרים אחרי מבחן המנה."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:** First test absolute convergence: "
            "$\\sum 1/\\sqrt{n} = \\sum n^{-1/2}$ is a p-series with $p = 1/2 < 1$, so it **diverges**. "
            "The series is not absolutely convergent. For conditional convergence, apply Leibniz with "
            "$b_n = 1/\\sqrt{n}$: positive, strictly decreasing, and $b_n \\to 0$. The alternating series "
            "**converges**. Since it converges but $\\sum |a_n|$ diverges, the answer is **conditionally convergent**.\n\n"
            "**How to think about it:** Always run the absolute test first — if $\\sum |a_n|$ converges, "
            "you are done (absolute). Only if it diverges do you need Leibniz for an alternating series.\n\n"
            "**Common slip:** Answering \"diverges\" because the p-series fails, without checking Leibniz. "
            "Or answering \"absolutely convergent\" because the alternating signs \"look small.\"\n\n"
            "**Exam tip:** The pattern $1/n^p$ with $p \\le 1$ diverges absolutely; with alternating signs "
            "and $b_n \\to 0$, Leibniz often saves it for $p > 0$."
        ),
        "explanation_he": (
            "**למה זה נכון:** קודם בדקו התכנסות מוחלטת: "
            "$\\sum 1/\\sqrt{n}=\\sum n^{-1/2}$ הוא טור p עם $p=1/2<1$, לכן **מתבדר**. "
            "הטור אינו מתכנס מוחלטית. להתכנסות מותנית, הפעילו לייבניץ עם "
            "$b_n=1/\\sqrt{n}$: חיובי, יורד קפדנית, ו-$b_n\\to 0$. הטור המתחלף **מתכנס**. "
            "מכיוון שהוא מתכנס אך $\\sum |a_n|$ מתבדר, התשובה היא **מתכנס מותנית**.\n\n"
            "**איך לחשוב:** תמיד הריצו בדיקה מוחלטת תחילה — אם $\\sum |a_n|$ מתכנס, סיימתם (מוחלטית). "
            "רק אם הוא מתבדר צריך לייבניץ לטור מתחלף.\n\n"
            "**טעות נפוצה:** תשובה \"מתבדר\" כי טור p נכשל, בלי לבדוק לייבניץ. "
            "או \"מוחלטית\" כי הסימנים המתחלפים \"נראים קטנים\".\n\n"
            "**טיפ לבחינה:** דפוס $1/n^p$ עם $p\\le 1$ מתבדר מוחלטית; עם סימנים מתחלפים "
            "ו-$b_n\\to 0$, לייבניץ לעיתים מציל ל-$p>0$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Ratio test: "
            "$L = 3|x-1| \\lim \\frac{n+1}{n+2} = 3|x-1|$. Convergence requires $3|x-1| < 1$, "
            "so $|x-1| < 1/3$ and **$R = 1/3$**. Center $c = 1$. At $x = 4/3$: "
            "$\\sum 1/(n+1)$ diverges (harmonic-type). At $x = 2/3$: "
            "$\\sum (-1)^n/(n+1)$ converges by Leibniz. **Interval: $[2/3, 4/3)$.**\n\n"
            "**How to think about it:** The factor $3^n$ in the numerator shrinks the radius — "
            "compare with $\\sum x^n/n$ which has $R = 1$. Here the effective ratio is $3|x-1|$.\n\n"
            "**Common slip:** Forgetting to divide by 3 when solving $|x-1| < 1/3$. "
            "Checking only one endpoint. Writing $(2/3, 4/3]$ instead of $[2/3, 4/3)$.\n\n"
            "**Exam tip:** After finding $R$, compute both endpoints as $c \\pm R$ explicitly "
            "before substituting — avoids arithmetic errors under time pressure."
        ),
        "explanation_he": (
            "**למה זה נכון:** מבחן מנה: "
            "$L=3|x-1|\\lim\\frac{n+1}{n+2}=3|x-1|$. התכנסות דורשת $3|x-1|<1$, "
            "לכן $|x-1|<1/3$ ו-**$R=1/3$**. מרכז $c=1$. ב-$x=4/3$: "
            "$\\sum 1/(n+1)$ מתבדר (סוג הרמוני). ב-$x=2/3$: "
            "$\\sum (-1)^n/(n+1)$ מתכנס בלייבניץ. **תחום: $[2/3,4/3)$.**\n\n"
            "**איך לחשוב:** הגורם $3^n$ במונה מקטין את הרדיוס — "
            "השוו ל-$\\sum x^n/n$ שיש לו $R=1$. כאן היחס האפקטיבי הוא $3|x-1|$.\n\n"
            "**טעות נפוצה:** שכחת לחלק ב-3 בפתרון $|x-1|<1/3$. "
            "בדיקת קצה אחד בלבד. כתיבת $(2/3,4/3]$ במקום $[2/3,4/3)$.\n\n"
            "**טיפ לבחינה:** אחרי מציאת $R$, חשבו שני קצוות כ-$c\\pm R$ במפורש "
            "לפני הצבה — מונע טעויות חשבון תחת לחץ."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** "
            "$\\sum |(-1)^n/n^3| = \\sum 1/n^3$. This is a p-series with $p = 3 > 1$, "
            "so $\\sum |a_n|$ **converges**. Therefore the original series converges **absolutely**. "
            "No Leibniz step is needed — absolute convergence is the stronger classification.\n\n"
            "**How to think about it:** For any series with terms $(-1)^n/n^p$, ask: is $p > 1$? "
            "If yes, absolute convergence follows immediately from the p-series test on $\\sum 1/n^p$.\n\n"
            "**Common slip:** Applying Leibniz unnecessarily and classifying as \"conditional.\" "
            "Confusing $n^3$ in the denominator (convergent p-series) with $n$ (harmonic, divergent).\n\n"
            "**Exam tip:** When you see $(-1)^n/n^p$, the absolute test is a one-line p-series check. "
            "Reserve Leibniz for cases where $p \\le 1$."
        ),
        "explanation_he": (
            "**למה זה נכון:** "
            "$\\sum |(-1)^n/n^3|=\\sum 1/n^3$. זהו טור p עם $p=3>1$, "
            "לכן $\\sum |a_n|$ **מתכנס**. מכאן הטור המקורי מתכנס **מוחלטית**. "
            "אין צורך בלייבניץ — התכנסות מוחלטית היא הסיווג החזק יותר.\n\n"
            "**איך לחשוב:** לכל טור עם איברים $(-1)^n/n^p$, שאלו: האם $p>1$? "
            "אם כן, התכנסות מוחלטית נובעת מיד ממבחן טורי p על $\\sum 1/n^p$.\n\n"
            "**טעות נפוצה:** הפעלת לייבניץ מיותרת וסיווג כ\"מותנית\". "
            "בלבול $n^3$ במכנה (טור p מתכנס) עם $n$ (הרמוני, מתבדר).\n\n"
            "**טיפ לבחינה:** כשראיתם $(-1)^n/n^p$, הבדיקה המוחלטית היא שורת p-series אחת. "
            "שמרו לייבניץ למקרים שבהם $p\\le 1$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Ratio test on $\\sum 2^n x^n$: "
            "$L = \\lim |2^{n+1}x^{n+1}/(2^n x^n)| = |2x|$. "
            "Convergence requires $|2x| < 1$, i.e. $|x| < 1/2$. **Radius $R = 1/2$.** "
            "At $x = 1/2$ the series becomes $\\sum 1$ (diverges); at $x = -1/2$ it becomes "
            "$\\sum (-1)^n$ (diverges). Interval: $(-1/2, 1/2)$.\n\n"
            "**How to think about it:** This is a geometric-type series with ratio $2x$. "
            "The coefficient $2^n$ pulls the center of convergence toward zero — smaller $R$ than $\\sum x^n$.\n\n"
            "**Common slip:** Reporting $R = 2$ instead of $R = 1/2$ (inverting the inequality). "
            "Forgetting that both endpoints diverge for this series.\n\n"
            "**Exam tip:** Rewrite as $\\sum (2x)^n$ mentally — immediate geometric recognition with $|r| < 1$."
        ),
        "explanation_he": (
            "**למה זה נכון:** מבחן מנה על $\\sum 2^nx^n$: "
            "$L=\\lim |2^{n+1}x^{n+1}/(2^nx^n)|=|2x|$. "
            "התכנסות דורשת $|2x|<1$, כלומר $|x|<1/2$. **רדיוס $R=1/2$.** "
            "ב-$x=1/2$ הטור הופך ל-$\\sum 1$ (מתבדר); ב-$x=-1/2$ ל-$\\sum (-1)^n$ (מתבדר). "
            "תחום: $(-1/2,1/2)$.\n\n"
            "**איך לחשוב:** זהו טור מסוג הנדסי עם יחס $2x$. "
            "המקדם $2^n$ מושך את מרכז ההתכנסות ל-0 — $R$ קטן יותר מ-$\\sum x^n$.\n\n"
            "**טעות נפוצה:** דיווח $R=2$ במקום $R=1/2$ (היפוך אי-שוויון). "
            "שכחה ששני הקצוות מתבדרים בטור זה.\n\n"
            "**טיפ לבחינה:** כתבו מנטלית $\\sum (2x)^n$ — זיהוי הנדסי מיידי עם $|r|<1$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Write $\\sum (-1)^n/\\sqrt{n+2}$ as an alternating series with "
            "$b_n = 1/\\sqrt{n+2}$. Check Leibniz: (1) $b_n > 0$ for all $n \\ge 0$. "
            "(2) $b_n$ is decreasing because $\\sqrt{n+2}$ increases. "
            "(3) $\\lim_{n\\to\\infty} b_n = 0$. All three conditions hold, so the series **converges** by AST.\n\n"
            "**How to think about it:** Shifting the index ($n+2$ vs $n$) does not affect convergence — "
            "only finitely many terms differ. Focus on the long-term behavior of $b_n$.\n\n"
            "**Common slip:** Claiming $b_n$ is not decreasing because \"the denominator has a square root.\" "
            "Forgetting to verify $b_n \\to 0$ (though it is obvious here).\n\n"
            "**Exam tip:** For AST proofs, state all three conditions explicitly — partial credit "
            "requires showing each one, not just the conclusion."
        ),
        "explanation_he": (
            "**למה זה נכון:** כתבו $\\sum (-1)^n/\\sqrt{n+2}$ כטור מתחלף עם "
            "$b_n=1/\\sqrt{n+2}$. בדקו לייבניץ: (1) $b_n>0$ לכל $n\\ge 0$. "
            "(2) $b_n$ יורד כי $\\sqrt{n+2}$ עולה. "
            "(3) $\\lim_{n\\to\\infty} b_n=0$. שלושת התנאים מתקיימים, לכן הטור **מתכנס** ב-AST.\n\n"
            "**איך לחשוב:** הזזת האינדקס ($n+2$ לעומת $n$) לא משפיעה על התכנסות — "
            "רק מספר סופי של איברים שונה. התמקדו בהתנהגות ארוכת הטווח של $b_n$.\n\n"
            "**טעות נפוצה:** טענה ש-$b_n$ אינו יורד כי \"במכנה יש שורש\". "
            "שכחת לאמת $b_n\\to 0$ (למרות שברור כאן).\n\n"
            "**טיפ לבחינה:** בהוכחות AST, ציינו את שלושת התנאים במפורש — "
            "נקודות חלקיות דורשות הצגת כל אחד, לא רק המסקנה."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Ratio test: "
            "$L = \\lim \\left|\\frac{(n+1)x^{n+1}}{nx^n}\\right| = |x| \\lim \\frac{n+1}{n} = |x| \\cdot 1 = |x|$. "
            "Convergence when $|x| < 1$, so **$R = 1$**. At $x = 1$: $\\sum n$ diverges (terms do not $\\to 0$). "
            "At $x = -1$: $\\sum n(-1)^n$ diverges (terms do not $\\to 0$). "
            "Interval: $(-1, 1)$ — open at both endpoints.\n\n"
            "**How to think about it:** The factor $n$ in the numerator makes terms grow in magnitude "
            "at endpoints even when $|x| = 1$. Compare with $\\sum x^n/n$ which converges at $x = -1$.\n\n"
            "**Common slip:** Stopping at $R = 1$ without checking endpoints. "
            "Assuming endpoints behave like $\\sum x^n/n$ because both have $R = 1$.\n\n"
            "**Exam tip:** When the general term has a polynomial factor in $n$, endpoint divergence "
            "is common — always substitute $x = \\pm R$."
        ),
        "explanation_he": (
            "**למה זה נכון:** מבחן מנה: "
            "$L=\\lim\\left|\\frac{(n+1)x^{n+1}}{nx^n}\\right|=|x|\\lim\\frac{n+1}{n}=|x|\\cdot 1=|x|$. "
            "התכנסות כאשר $|x|<1$, לכן **$R=1$**. ב-$x=1$: $\\sum n$ מתבדר (איברים לא $\\to 0$). "
            "ב-$x=-1$: $\\sum n(-1)^n$ מתבדר (איברים לא $\\to 0$). "
            "תחום: $(-1,1)$ — פתוח בשני הקצוות.\n\n"
            "**איך לחשוב:** הגורם $n$ במונה גורם לאיברים לגדול בקצוות גם כש-$|x|=1$. "
            "השוו ל-$\\sum x^n/n$ שמתכנס ב-$x=-1$.\n\n"
            "**טעות נפוצה:** עצירה ב-$R=1$ בלי בדיקת קצוות. "
            "הנחה שקצוות מתנהגים כמו $\\sum x^n/n$ כי לשניהם $R=1$.\n\n"
            "**טיפ לבחינה:** כשלאיבר הכללי יש גורם פולינומי ב-$n$, "
            "התבדרות בקצוות נפוצה — הציבו תמיד $x=\\pm R$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Ratio test gives $L = |x|$, so **$R = 1$**. "
            "At $x = 1$: $\\sum 1/n^2$ — p-series with $p = 2 > 1$, **converges**. "
            "At $x = -1$: $\\sum (-1)^n/n^2$; since $\\sum 1/n^2$ converges, this is "
            "**absolutely convergent** at the left endpoint too. "
            "**Interval: $[-1, 1]$** — closed at both ends.\n\n"
            "**How to think about it:** The $n^2$ denominator is strong enough to converge at both "
            "endpoints. This contrasts with $\\sum x^n/n$ which only converges at $x = -1$.\n\n"
            "**Common slip:** Using Leibniz at $x = -1$ instead of noting absolute convergence. "
            "Writing $(-1, 1)$ or $[-1, 1)$ — wrong bracket at one or both ends.\n\n"
            "**Exam tip:** When the denominator is $n^p$ with $p > 1$, both endpoints typically converge. "
            "Memorise this pattern alongside the $n^1$ case."
        ),
        "explanation_he": (
            "**למה זה נכון:** מבחן מנה נותן $L=|x|$, לכן **$R=1$**. "
            "ב-$x=1$: $\\sum 1/n^2$ — טור p עם $p=2>1$, **מתכנס**. "
            "ב-$x=-1$: $\\sum (-1)^n/n^2$; מכיוון ש-$\\sum 1/n^2$ מתכנס, זו "
            "**התכנסות מוחלטית** גם בקצה השמאלי. "
            "**תחום: $[-1,1]$** — סגור בשני הקצות.\n\n"
            "**איך לחשוב:** המכנה $n^2$ חזק מספיק להתכנסות בשני הקצוות. "
            "זה בניגוד ל-$\\sum x^n/n$ שמתכנס רק ב-$x=-1$.\n\n"
            "**טעות נפוצה:** שימוש בלייבניץ ב-$x=-1$ במקום לציין התכנסות מוחלטית. "
            "כתיבת $(-1,1)$ או $[-1,1)$ — סוגריים שגויים.\n\n"
            "**טיפ לבחינה:** כשהמכנה $n^p$ עם $p>1$, שני הקצוות בדרך כלל מתכנסים. "
            "שיננו דפוס זה לצד מקרה $n^1$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:** Rewrite as $\\sum \\left(\\frac{x+1}{3}\\right)^n$. "
            "Ratio test: $L = |x+1|/3$. Convergence when $|x+1| < 3$, so **$R = 3$**. "
            "Center $c = -1$. At $x = 2$: $\\sum 1$ diverges. At $x = -4$: $\\sum (-1)^n$ diverges "
            "(terms do not approach 0). **Interval: $(-4, 2)$** — open at both endpoints.\n\n"
            "**How to think about it:** The $3^n$ in the denominator expands the interval compared to "
            "$\\sum (x+1)^n$. Geometric intuition: ratio $|x+1|/3 < 1$.\n\n"
            "**Common slip:** Sign error on center ($c = +1$ instead of $-1$). "
            "Checking endpoints but forgetting that $\\sum (-1)^n$ diverges (not Leibniz — terms $\\not\\to 0$).\n\n"
            "**Exam tip:** For $\\sum (x-c)^n/r^n$, immediately identify $R = r$ and center $c$. "
            "Endpoint test reduces to $\\sum 1$ and $\\sum (-1)^n$."
        ),
        "explanation_he": (
            "**למה זה נכון:** כתבו מחדש $\\sum \\left(\\frac{x+1}{3}\\right)^n$. "
            "מבחן מנה: $L=|x+1|/3$. התכנסות כאשר $|x+1|<3$, לכן **$R=3$**. "
            "מרכז $c=-1$. ב-$x=2$: $\\sum 1$ מתבדר. ב-$x=-4$: $\\sum (-1)^n$ מתבדר "
            "(איברים לא שואפים ל-0). **תחום: $(-4,2)$** — פתוח בשני הקצוות.\n\n"
            "**איך לחשוב:** $3^n$ במכנה מרחיב את הקטע לעומת $\\sum (x+1)^n$. "
            "אינטואיציה הנדסית: יחס $|x+1|/3<1$.\n\n"
            "**טעות נפוצה:** שגיאת סימן במרכז ($c=+1$ במקום $-1$). "
            "בדיקת קצוות אך שכחה ש-$\\sum (-1)^n$ מתבדר (לא לייבניץ — איברים $\\not\\to 0$).\n\n"
            "**טיפ לבחינה:** עבור $\\sum (x-c)^n/r^n$, זהו מיד $R=r$ ומרכז $c$. "
            "בדיקת קצוות מתמצתת ל-$\\sum 1$ ו-$\\sum (-1)^n$."
        ),
    },
]

EXERCISE_SOLUTIONS = {
    "e1": {
        "solution_en": "**Step 1:** $\\sum |(-1)^n/n^3| = \\sum 1/n^3$. p-series with $p = 3 > 1$. **Absolutely convergent.**",
        "solution_he": "**שלב 1:** $\\sum |(-1)^n/n^3|=\\sum 1/n^3$. טור p עם $p=3>1$. **מתכנס מוחלטית.**",
    },
    "e2": {
        "solution_en": "Ratio: $L = |2x|$. Converges for $|2x| < 1$, i.e. $|x| < 1/2$. **$R = 1/2$.** Both endpoints diverge.",
        "solution_he": "מבחן מנה: $L=|2x|$. מתכנס ל-$|2x|<1$, כלומר $|x|<1/2$. **$R=1/2$.** שני הקצוות מתבדרים.",
    },
    "e3": {
        "solution_en": "$b_n = 1/\\sqrt{n+2} > 0$, decreasing, $b_n \\to 0$. All Leibniz conditions hold. **Converges.**",
        "solution_he": "$b_n=1/\\sqrt{n+2}>0$, יורד, $b_n\\to 0$. כל תנאי לייבניץ מתקיימים. **מתכנס.**",
    },
    "e4": {
        "solution_en": "Ratio: $|a_{n+1}/a_n| \\cdot |x| = (n+1)/n \\cdot |x| \\to |x|$. **$R = 1$.** Endpoints both diverge.",
        "solution_he": "מבחן מנה: $(n+1)/n \\cdot |x| \\to |x|$. **$R=1$.** שני הקצוות מתבדרים.",
    },
    "e5": {
        "solution_en": "$R = 1$. $x = 1$: $\\sum 1/n^2$ converges ($p = 2$). $x = -1$: absolutely convergent. **Interval: $[-1, 1]$.**",
        "solution_he": "$R=1$. $x=1$: $\\sum 1/n^2$ מתכנס ($p=2$). $x=-1$: מוחלטית. **תחום: $[-1,1]$.**",
    },
    "e6": {
        "solution_en": "$L = |x+1|/3$. **$R = 3$.** $x = 2$: $\\sum 1$ diverges. $x = -4$: $\\sum (-1)^n$ diverges. **Interval: $(-4, 2)$.**",
        "solution_he": "$L=|x+1|/3$. **$R=3$.** $x=2$: $\\sum 1$ מתבדר. $x=-4$: $\\sum (-1)^n$ מתבדר. **תחום: $(-4,2)$.**",
    },
    "e7": {
        "solution_en": "$\\ln(1+x) = \\sum_{n=1}^{\\infty} (-1)^{n+1} x^n/n$ for $x \\in (-1, 1]$. At $x = 1$ (endpoint, AST): $\\ln 2 = \\sum (-1)^{n+1}/n$. ✓",
        "solution_he": "$\\ln(1+x)=\\sum (-1)^{n+1}x^n/n$ ל-$x\\in(-1,1]$. ב-$x=1$ (קצה, AST): $\\ln 2=\\sum (-1)^{n+1}/n$. ✓",
    },
    "e8": {
        "solution_en": "Ratio: $|a_{n+1}/a_n| = \\frac{n+1}{(2n+2)(2n+1)}|x| \\to 0$ for all $x$. **$R = \\infty$.**",
        "solution_he": "מבחן מנה: $\\frac{n+1}{(2n+2)(2n+1)}|x|\\to 0$ לכל $x$. **$R=\\infty$.**",
    },
    "e9": {
        "solution_en": "$R = 4$ (ratio: $|x-3|/4$). $x = 7$: $\\sum 1/n$ diverges. $x = -1$: $\\sum (-1)^n/n$ converges (Leibniz). **Interval: $[-1, 7)$.**",
        "solution_he": "$R=4$ (מנה: $|x-3|/4$). $x=7$: $\\sum 1/n$ מתבדר. $x=-1$: $\\sum (-1)^n/n$ מתכנס (לייבניץ). **תחום: $[-1,7)$.**",
    },
    "e10": {
        "solution_en": "Since $-|a_n| \\le a_n \\le |a_n|$, we have $0 \\le a_n + |a_n| \\le 2|a_n|$. Comparison: $\\sum(a_n + |a_n|)$ converges. Then $\\sum a_n = \\sum(a_n + |a_n|) - \\sum |a_n|$ — difference of convergent series. ✓",
        "solution_he": "מכיוון ש-$-|a_n|\\le a_n\\le |a_n|$, יש $0\\le a_n+|a_n|\\le 2|a_n|$. השוואה: $\\sum(a_n+|a_n|)$ מתכנס. אז $\\sum a_n=\\sum(a_n+|a_n|)-\\sum|a_n|$ — הפרש טורים מתכנסים. ✓",
    },
    "e11": {
        "solution_en": "$R = 1$. $x = 1$: $\\sum 1/(n \\ln n)$ diverges (integral test). $x = -1$: $\\sum (-1)^n/(n \\ln n)$ converges (Leibniz). **Interval: $[-1, 1)$.**",
        "solution_he": "$R=1$. $x=1$: $\\sum 1/(n\\ln n)$ מתבדר (מבחן אינטגרל). $x=-1$: $\\sum (-1)^n/(n\\ln n)$ מתכנס (לייבניץ). **תחום: $[-1,1)$.**",
    },
    "e12": {
        "solution_en": "$e^{ix} = \\sum (ix)^n/n! = \\sum (-1)^k x^{2k}/(2k)! + i\\sum (-1)^k x^{2k+1}/(2k+1)!$. Real part: $\\cos x = \\sum (-1)^k x^{2k}/(2k)!$.",
        "solution_he": "$e^{ix}=\\sum (ix)^n/n!=\\sum (-1)^k x^{2k}/(2k)!+i\\sum (-1)^k x^{2k+1}/(2k+1)!$. החלק הממשי: $\\cos x=\\sum (-1)^k x^{2k}/(2k)!$.",
    },
    "e13": {
        "solution_en": "Alternating harmonic: $1 - 1/2 + 1/3 - \\cdots = \\ln 2$. Rearrange: add positive terms until sum exceeds 2, subtract negatives until below 2, repeat. Both $\\sum$ of positives and $\\sum$ of negatives diverge separately, so any target $L$ is reachable (Riemann).",
        "solution_he": "הרמוני אלטרנטיבי: $1-1/2+1/3-\\cdots=\\ln 2$. סדרו מחדש: חברו איברים חיוביים עד מעל 2, חסרו שליליים עד מתחת 2, חזרו. $\\sum$ החיוביים ו-$\\sum$ השליליים מתבדרים בנפרד, לכן ניתן להגיע לכל $L$ (רימן).",
    },
}


def apply_expansion(data):
    cp_idx = 0
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
            cp_idx += 1
            sec.update(SECTION_BODIES[f"checkpoint_{cp_idx}"])
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "exercise_set":
            sec.update(SECTION_BODIES["exercise_set"])
            for ex in sec.get("exercises", []):
                sol = EXERCISE_SOLUTIONS.get(ex.get("id"))
                if sol:
                    ex.update(sol)
        elif kind == "pitfall":
            sec.update(SECTION_BODIES["pitfall"])
        elif kind == "why_matters":
            sec.update(SECTION_BODIES["why_matters"])
        elif kind == "before_exam":
            sec.update(SECTION_BODIES["before_exam"])
        elif kind == "summary":
            sec.update(SECTION_BODIES["summary"])

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

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
            if sec.get("body_he_md") and hebrew_body_weak(
                sec.get("body_he_md"), sec.get("body_en_md")
            ):
                issues.append(f"{kind} HE weak parity")
        elif kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            n = sec.get("example_number", "?")
            if en_w < MIN_WORDS["worked_example"]["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"worked_example {n} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"q{q['ord']} {key}: {w} words")
            if lang == "he" and hebrew_body_weak(
                q.get("explanation_he"), q.get("explanation_en")
            ):
                issues.append(f"q{q['ord']} expl-he-weak")

    return issues


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("VALIDATION FAILED:")
        for i in issues:
            print(" ", i)
        sys.exit(1)

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

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
    print("All depth gates OK; seed-lessons dry-run passed.")


if __name__ == "__main__":
    main()
