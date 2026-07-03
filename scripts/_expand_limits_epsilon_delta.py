#!/usr/bin/env python3
"""Expand limits_epsilon_delta.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "scripts/seed_data/lessons/limits_epsilon_delta.json"


def wc(text: str) -> int:
    import re
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def main():
    data = json.loads(LESSON.read_text(encoding="utf-8"))

    for s in data["sections"]:
        kind = s.get("kind")
        if kind == "definition":
            s["body_en_md"] = (
                "**Definition (Weierstrass):**\n"
                "$$\\lim_{x\\to c}f(x) = L$$\n"
                "means: for every $\\varepsilon > 0$ there exists $\\delta > 0$ such that\n"
                "$$0 < |x - c| < \\delta \\implies |f(x) - L| < \\varepsilon$$\n\n"
                "**Quantifier order matters:** $\\varepsilon$ is chosen first (how tight the output tolerance must be); "
                "then you must produce a $\\delta$ that works for that $\\varepsilon$. You never pick $\\delta$ first and "
                "then hunt for a convenient $\\varepsilon$.\n\n"
                "**Interpretation:**\n"
                "- $\\varepsilon$ (epsilon) measures how close $f(x)$ must be to $L$ — the \"output tolerance\".\n"
                "- $\\delta$ (delta) is the \"input radius\" you find to achieve that output tolerance.\n"
                "- $0 < |x-c|$ means $x \\neq c$ — the limit is about approaching $c$, not being at $c$.\n"
                "- The definition says: however tight the output tolerance $\\varepsilon$, we can always find a small enough input window $\\delta$.\n\n"
                "**Continuity at a point:**\n"
                "$f$ is continuous at $c$ if:\n"
                "1. $f(c)$ is defined.\n"
                "2. $\\lim_{x\\to c}f(x)$ exists.\n"
                "3. $\\lim_{x\\to c}f(x) = f(c)$.\n\n"
                "Equivalently: for every $\\varepsilon > 0$ there exists $\\delta > 0$ such that\n"
                "$$|x - c| < \\delta \\implies |f(x) - f(c)| < \\varepsilon$$\n"
                "(Note: the strict inequality $0 < |x-c|$ is dropped — continuity cares about values *at* $c$ as well as nearby.)"
            )
            s["body_he_md"] = (
                "**הגדרה (ויירשטראס):**\n"
                "$$\\lim_{x\\to c}f(x) = L$$\n"
                "פירושה: לכל $\\varepsilon > 0$ קיים $\\delta > 0$ כך ש-\n"
                "$$0 < |x - c| < \\delta \\implies |f(x) - L| < \\varepsilon$$\n\n"
                "**סדר הכמתים חשוב:** $\\varepsilon$ נבחר ראשון (כמה צריך לדייק את הפלט); לאחר מכן מוצאים $\\delta$ שעובד עבור $\\varepsilon$ זה. "
                "אסור לבחור $\\delta$ קודם ואז לחפש $\\varepsilon$ נוח.\n\n"
                "**פרשנות:**\n"
                "- $\\varepsilon$ (אפסילון) מודד כמה קרוב $f(x)$ חייב להיות ל-$L$ — \"סבילות הפלט\".\n"
                "- $\\delta$ (דלתא) הוא \"רדיוס הקלט\" שמוצאים להשגת סבילות הפלט.\n"
                "- $0 < |x-c|$ פירושו $x \\neq c$ — הגבול עוסק בהתקרבות ל-$c$, לא בהיות ב-$c$.\n"
                "- ההגדרה אומרת: כמה שסבילות הפלט $\\varepsilon$ קטנה, תמיד ניתן למצוא חלון קלט קטן מספיק $\\delta$.\n\n"
                "**רציפות בנקודה:**\n"
                "$f$ רציפה ב-$c$ אם:\n"
                "1. $f(c)$ מוגדרת.\n"
                "2. $\\lim_{x\\to c}f(x)$ קיים.\n"
                "3. $\\lim_{x\\to c}f(x) = f(c)$.\n\n"
                "שקולה: לכל $\\varepsilon > 0$ קיים $\\delta > 0$ כך ש-\n"
                "$$|x - c| < \\delta \\implies |f(x) - f(c)| < \\varepsilon$$\n"
                "(הערה: אי-השוויון החד $0 < |x-c|$ מושמט — רציפות דואגת גם לערכים *ב*-$c$ ולא רק בסביבה.)"
            )

        elif kind == "theory":
            s["body_en_md"] = (
                "Every university $\\varepsilon$-$\\delta$ proof follows the same four-step skeleton. "
                "Mastering it turns a vague \"get close\" idea into a checkable argument graders can follow line by line.\n\n"
                "**Step 1 — Scratch work (find $\\delta$):**\n"
                "Work backwards. Assume $|x-c|<\\delta$ and try to bound $|f(x)-L|$ in terms of $\\delta$. "
                "The goal is to find $\\delta = \\delta(\\varepsilon)$ — a formula depending only on $\\varepsilon$ and fixed constants, never on $x$.\n\n"
                "**Step 2 — State $\\delta$:**\n"
                "Open the formal proof with \"Let $\\varepsilon > 0$ be given.\" Then choose $\\delta$ from scratch work and write: \"Let $\\delta = \\ldots$\".\n\n"
                "**Step 3 — Prove the implication:**\n"
                "Assume $0 < |x-c| < \\delta$. Start from $|f(x)-L|$ and bound it algebraically until you reach $< \\varepsilon$.\n\n"
                "**Step 4 — Conclude:**\n"
                "\"Therefore $\\lim_{x\\to c}f(x) = L$ by definition.\" $\\square$\n\n"
                "**Key inequalities used in $\\varepsilon$-$\\delta$ proofs:**\n"
                "- **Triangle inequality:** $|a+b| \\leq |a|+|b|$ — essential for sum and product rules.\n"
                "- **Product bound:** $|ab| = |a||b|$.\n"
                "- **Restriction trick:** if we additionally require $|x-c|<1$, then $|x|$ is bounded on a small interval and we can control variable coefficients like $|x+c|$.\n\n"
                "**Squeeze Theorem:** If $g(x) \\leq f(x) \\leq h(x)$ near $c$, and $\\lim_{x\\to c}g(x) = \\lim_{x\\to c}h(x) = L$, then $\\lim_{x\\to c}f(x) = L$. "
                "Use it when direct substitution fails but the function is trapped between two simpler ones with the same limit."
            )
            s["body_he_md"] = (
                "כל הוכחת $\\varepsilon$-$\\delta$ אוניברסיטאית עוקבת אחרי אותה תבנית של ארבעה שלבים. "
                "שליטה בה הופכת את הרעיון הלא-מדויק של \"להתקרב\" לטיעון שניתן לבדוק שורה אחר שורה.\n\n"
                "**שלב 1 — עבודת טיוטה (מציאת $\\delta$):**\n"
                "עבוד לאחור. הניח $|x-c|<\\delta$ ונסה לחסום $|f(x)-L|$ במונחי $\\delta$. "
                "המטרה: $\\delta = \\delta(\\varepsilon)$ — נוסחה שתלויה רק ב-$\\varepsilon$ ובקבועים, לא ב-$x$.\n\n"
                "**שלב 2 — ציון $\\delta$:**\n"
                "פתח את ההוכחה ב-\"יהי $\\varepsilon > 0$ נתון.\" לאחר מכן בחר $\\delta$ מעבודת הטיוטה: \"יהי $\\delta = \\ldots$\".\n\n"
                "**שלב 3 — הוכחת הגרירה:**\n"
                "הניח $0 < |x-c| < \\delta$. התחל מ-$|f(x)-L|$ וחסום אלגברית עד $< \\varepsilon$.\n\n"
                "**שלב 4 — סיום:**\n"
                "\"לכן $\\lim_{x\\to c}f(x) = L$ לפי ההגדרה.\" $\\square$\n\n"
                "**אי-שוויונות מרכזיים:**\n"
                "- **אי-שוויון משולש:** $|a+b| \\leq |a|+|b|$ — חיוני לכללי סכום ומכפלה.\n"
                "- **חסם מכפלה:** $|ab| = |a||b|$.\n"
                "- **טריק הגבלה:** אם נדרוש $|x-c|<1$, אז $|x|$ חסומה בקטע קטן וניתן לשלוט במקדמים כמו $|x+c|$.\n\n"
                "**משפט הסנדוויץ':** אם $g(x) \\leq f(x) \\leq h(x)$ בסביבת $c$, ו-$\\lim g = \\lim h = L$, אז $\\lim f = L$. "
                "השתמשו בו כשהצבה ישירה נכשלת אך הפונקציה כלואה בין שתי פונקציות פשוטות עם אותו גבול."
            )

        elif kind == "worked_example" and s.get("example_number") == 1:
            s["body_en_md"] = (
                "**Claim:** $\\lim_{x\\to 2}(3x-1) = 5$.\n\n"
                "Linear functions are the training ground for $\\varepsilon$-$\\delta$: the algebra is short, but the logical structure is exactly what harder proofs reuse.\n\n"
                "### Move 1 — Scratch work\n"
                "$$|f(x)-L| = |(3x-1)-5| = |3x-6| = 3|x-2|$$\n"
                "We need $3|x-2| < \\varepsilon$, i.e., $|x-2| < \\dfrac{\\varepsilon}{3}$.\n"
                "So choose $\\delta = \\dfrac{\\varepsilon}{3}$.\n\n"
                "### Move 2 — State $\\delta$\n"
                "Let $\\varepsilon > 0$ be given. Choose $\\delta = \\dfrac{\\varepsilon}{3}$.\n\n"
                "### Move 3 — Prove the implication\n"
                "Assume $0 < |x-2| < \\delta = \\dfrac{\\varepsilon}{3}$. Then:\n"
                "$$|(3x-1)-5| = |3x-6| = 3|x-2| < 3\\cdot\\frac{\\varepsilon}{3} = \\varepsilon$$\n\n"
                "### Move 4 — Conclude\n"
                "For every $\\varepsilon > 0$, choosing $\\delta = \\varepsilon/3$ ensures $|x-2| < \\delta \\implies |(3x-1)-5| < \\varepsilon$.\n"
                "$$\\therefore \\lim_{x\\to 2}(3x-1) = 5 \\quad \\checkmark$$\n\n"
                "**Pattern to remember:** for $f(x)=ax+b$, $|f(x)-L|=|a||x-c|$ always gives $\\delta=\\varepsilon/|a|$.\n\n"
                "**Why this example matters:** Every harder $\\varepsilon$-$\\delta$ proof reuses this skeleton — scratch work finds $\\delta$, the formal proof assumes $0<|x-c|<\\delta$ and closes the inequality chain. Practice until the four steps feel automatic on every linear function."
            )
            s["body_he_md"] = (
                "**טענה:** $\\lim_{x\\to 2}(3x-1) = 5$.\n\n"
                "פונקציות לינאריות הן מגרש האימונים ל-$\\varepsilon$-$\\delta$: האלגברה קצרה, אך מבנה ההוכחה זהה לזה שמשתמשים בו בהוכחות קשות יותר.\n\n"
                "### צעד 1 — עבודת טיוטה\n"
                "$$|f(x)-L| = |(3x-1)-5| = |3x-6| = 3|x-2|$$\n"
                "צריך $3|x-2| < \\varepsilon$, כלומר $|x-2| < \\dfrac{\\varepsilon}{3}$.\n"
                "לכן נבחר $\\delta = \\dfrac{\\varepsilon}{3}$.\n\n"
                "### צעד 2 — ציון $\\delta$\n"
                "יהי $\\varepsilon > 0$ נתון. בחר $\\delta = \\dfrac{\\varepsilon}{3}$.\n\n"
                "### צעד 3 — הוכחת הגרירה\n"
                "הניח $0 < |x-2| < \\delta = \\dfrac{\\varepsilon}{3}$. אז:\n"
                "$$|(3x-1)-5| = |3x-6| = 3|x-2| < 3\\cdot\\frac{\\varepsilon}{3} = \\varepsilon$$\n\n"
                "### צעד 4 — מסקנה\n"
                "לכל $\\varepsilon > 0$, בחירת $\\delta = \\varepsilon/3$ מבטיחה $|x-2| < \\delta \\implies |(3x-1)-5| < \\varepsilon$.\n"
                "$$\\therefore \\lim_{x\\to 2}(3x-1) = 5 \\quad \\checkmark$$\n\n"
                "**דפוס לזכור:** עבור $f(x)=ax+b$, תמיד $|f(x)-L|=|a||x-c|$ ולכן $\\delta=\\varepsilon/|a|$.\n\n"
                "**למה הדוגמה חשובה:** כל הוכחת $\\varepsilon$-$\\delta$ קשה יותר משתמשת באותה תבנית — טיוטה מוצאת $\\delta$, ההוכחה מניחה $0<|x-c|<\\delta$ וסוגרת את שרשרת האי-שוויונות. תרגלו עד שהארבעה שלבים מרגישים אוטומטיים."
            )

        elif kind == "worked_example" and s.get("example_number") == 2:
            s["body_en_md"] = (
                "**Claim:** $\\lim_{x\\to 0}x\\sin\\left(\\dfrac{1}{x}\\right) = 0$.\n\n"
                "**Note:** We cannot substitute $x=0$ ($1/x$ is undefined), and $\\lim_{x\\to 0}\\sin(1/x)$ does not exist — it oscillates wildly. "
                "Direct $\\varepsilon$-$\\delta$ on the sine factor alone is hopeless; the squeeze theorem is the right tool.\n\n"
                "### Move 1 — Bound the oscillating factor\n"
                "For all $x \\neq 0$:\n"
                "$$\\left|\\sin\\left(\\frac{1}{x}\\right)\\right| \\leq 1$$\n\n"
                "### Move 2 — Multiply by $|x|$\n"
                "$$\\left|x\\sin\\left(\\frac{1}{x}\\right)\\right| = |x|\\left|\\sin\\left(\\frac{1}{x}\\right)\\right| \\leq |x|$$\n\n"
                "### Move 3 — Apply Squeeze\n"
                "$$-|x| \\leq x\\sin\\left(\\frac{1}{x}\\right) \\leq |x|$$\n"
                "Since $\\lim_{x\\to 0}|x| = 0$ and $\\lim_{x\\to 0}(-|x|) = 0$, by the Squeeze Theorem:\n"
                "$$\\lim_{x\\to 0}x\\sin\\left(\\frac{1}{x}\\right) = 0 \\quad \\checkmark$$\n\n"
                "**$\\varepsilon$-$\\delta$ version (optional):** Given $\\varepsilon > 0$, let $\\delta = \\varepsilon$. "
                "Then $0 < |x-0| < \\delta$ implies $\\left|x\\sin(1/x)-0\\right| \\leq |x| < \\delta = \\varepsilon$. "
                "This shows the same limit without invoking squeeze — useful when the exam asks for an explicit $\\delta$.\n\n"
                "**Takeaway:** When a factor is bounded and another factor vanishes, squeeze (or direct $\\delta=\\varepsilon$) beats wrestling with oscillation. This pattern appears frequently on university analysis exams."
            )
            s["body_he_md"] = (
                "**טענה:** $\\lim_{x\\to 0}x\\sin\\left(\\dfrac{1}{x}\\right) = 0$.\n\n"
                "**הערה:** לא ניתן להציב $x=0$ ($1/x$ לא מוגדר), ו-$\\lim_{x\\to 0}\\sin(1/x)$ לא קיים — הוא מתנדנד. "
                "$\\varepsilon$-$\\delta$ ישיר על הסינוס בלבד אינו מעשי; משפט הסנדוויץ' הוא הכלי הנכון.\n\n"
                "### צעד 1 — חסום את הגורם המתנדד\n"
                "לכל $x \\neq 0$:\n"
                "$$\\left|\\sin\\left(\\frac{1}{x}\\right)\\right| \\leq 1$$\n\n"
                "### צעד 2 — הכפל ב-$|x|$\n"
                "$$\\left|x\\sin\\left(\\frac{1}{x}\\right)\\right| = |x|\\left|\\sin\\left(\\frac{1}{x}\\right)\\right| \\leq |x|$$\n\n"
                "### צעד 3 — יישום הסנדוויץ'\n"
                "$$-|x| \\leq x\\sin\\left(\\frac{1}{x}\\right) \\leq |x|$$\n"
                "מאחר ש-$\\lim_{x\\to 0}|x| = 0$ ו-$\\lim_{x\\to 0}(-|x|) = 0$, לפי משפט הסנדוויץ':\n"
                "$$\\lim_{x\\to 0}x\\sin\\left(\\frac{1}{x}\\right) = 0 \\quad \\checkmark$$\n\n"
                "**גרסת $\\varepsilon$-$\\delta$ (אופציונלי):** בהינתן $\\varepsilon > 0$, יהי $\\delta = \\varepsilon$. "
                "אז $0 < |x| < \\delta$ גורר $\\left|x\\sin(1/x)\\right| \\leq |x| < \\varepsilon$. "
                "מראה את אותו גבול בלי סנדוויץ' — שימושי כשבבחינה מבקשים $\\delta$ מפורש.\n\n"
                "**מסקנה:** כשגורם חסום וגורם שואף ל-$0$, סנדוויץ' (או $\\delta=\\varepsilon$ ישיר) עדיף על מאבק עם התנדנדות."
            )

        elif kind == "worked_example" and s.get("example_number") == 3:
            s["body_en_md"] = (
                "**Theorem:** If $\\lim_{x\\to c}f(x) = L$ and $\\lim_{x\\to c}g(x) = M$, then $\\lim_{x\\to c}(f(x)+g(x)) = L+M$.\n\n"
                "This is the prototype for combining two limits: split the total error budget $\\varepsilon$ equally between the two functions.\n\n"
                "### Move 1 — Setup\n"
                "Let $\\varepsilon > 0$ be given. We need $\\delta > 0$ such that:\n"
                "$$0 < |x-c| < \\delta \\implies |(f(x)+g(x)) - (L+M)| < \\varepsilon$$\n\n"
                "### Move 2 — Invoke individual limits with $\\varepsilon/2$\n"
                "Since $\\lim_{x\\to c}f(x) = L$: for $\\varepsilon/2 > 0$, there exists $\\delta_1 > 0$ such that\n"
                "$$0 < |x-c| < \\delta_1 \\implies |f(x)-L| < \\frac{\\varepsilon}{2}$$\n"
                "Since $\\lim_{x\\to c}g(x) = M$: for $\\varepsilon/2 > 0$, there exists $\\delta_2 > 0$ such that\n"
                "$$0 < |x-c| < \\delta_2 \\implies |g(x)-M| < \\frac{\\varepsilon}{2}$$\n\n"
                "### Move 3 — Choose $\\delta = \\min(\\delta_1, \\delta_2)$\n"
                "This ensures *both* individual bounds hold simultaneously.\n\n"
                "### Move 4 — Triangle inequality\n"
                "Assume $0 < |x-c| < \\delta$. By the triangle inequality:\n"
                "$$|(f(x)+g(x))-(L+M)| = |(f(x)-L)+(g(x)-M)|$$\n"
                "$$\\leq |f(x)-L| + |g(x)-M| < \\frac{\\varepsilon}{2} + \\frac{\\varepsilon}{2} = \\varepsilon$$\n\n"
                "**Conclusion:** $\\lim_{x\\to c}(f(x)+g(x)) = L+M$. $\\square$\n\n"
                "**Exam tip:** The same $\\varepsilon/2$ split appears in product and quotient limit proofs — learn the pattern once, reuse everywhere.\n\n"
                "**Why $\\min$?** If $|x-c|<\\delta_1$ controls $f$ and $|x-c|<\\delta_2$ controls $g$, we need the *stricter* window so both bounds apply at once. This standard template underlies all limit algebra rules."
            )
            s["body_he_md"] = (
                "**משפט:** אם $\\lim_{x\\to c}f(x) = L$ ו-$\\lim_{x\\to c}g(x) = M$, אז $\\lim_{x\\to c}(f(x)+g(x)) = L+M$.\n\n"
                "זוהי ההוכחה האב-טיפוס לשילוב שני גבולות: מחלקים את תקציב השגיאה $\\varepsilon$ שווה בשווה בין שתי הפונקציות.\n\n"
                "### צעד 1 — הכנה\n"
                "יהי $\\varepsilon > 0$ נתון. נדרש $\\delta > 0$ כך ש:\n"
                "$$0 < |x-c| < \\delta \\implies |(f(x)+g(x)) - (L+M)| < \\varepsilon$$\n\n"
                "### צעד 2 — שימוש בגבולות עם $\\varepsilon/2$\n"
                "מאחר ש-$\\lim f = L$: עבור $\\varepsilon/2 > 0$, קיים $\\delta_1 > 0$ כך ש-\n"
                "$$0 < |x-c| < \\delta_1 \\implies |f(x)-L| < \\frac{\\varepsilon}{2}$$\n"
                "מאחר ש-$\\lim g = M$: עבור $\\varepsilon/2 > 0$, קיים $\\delta_2 > 0$ כך ש-\n"
                "$$0 < |x-c| < \\delta_2 \\implies |g(x)-M| < \\frac{\\varepsilon}{2}$$\n\n"
                "### צעד 3 — בחירת $\\delta = \\min(\\delta_1, \\delta_2)$\n"
                "כך שני החסמים חלים בו-זמנית.\n\n"
                "### צעד 4 — אי-שוויון משולש\n"
                "הניח $0 < |x-c| < \\delta$. לפי אי-שוויון המשולש:\n"
                "$$|(f(x)+g(x))-(L+M)| \\leq |f(x)-L| + |g(x)-M| < \\frac{\\varepsilon}{2} + \\frac{\\varepsilon}{2} = \\varepsilon$$\n\n"
                "**מסקנה:** $\\lim_{x\\to c}(f(x)+g(x)) = L+M$. $\\square$\n\n"
                "**טיפ לבחינה:** אותו פיצול $\\varepsilon/2$ מופיע בהוכחות מכפלה ומנה — למדו את הדפוס פעם אחת.\n\n"
                "**למה $\\min$?** אם $|x-c|<\\delta_1$ שולט ב-$f$ ו-$|x-c|<\\delta_2$ ב-$g$, צריך את החלון *הצר יותר* כדי ששני החסמים יחולו יחד."
            )

        elif kind == "checkpoint" and "2x+1" in s.get("body_en_md", ""):
            s["checkpoint_solution_en"] = (
                "**Goal:** Prove $\\lim_{x\\to 3}(2x+1) = 7$ using $\\varepsilon$-$\\delta$.\n\n"
                "**Step 1 — Scratch work:** $|(2x+1)-7| = |2x-6| = 2|x-3|$. "
                "We need $2|x-3| < \\varepsilon$, so $|x-3| < \\varepsilon/2$. Choose $\\delta = \\varepsilon/2$.\n\n"
                "**Step 2 — State $\\delta$:** Let $\\varepsilon > 0$ be given. Set $\\delta = \\varepsilon/2$.\n\n"
                "**Step 3 — Proof:** Suppose $0 < |x-3| < \\delta$. Then:\n"
                "$$|(2x+1)-7| = 2|x-3| < 2\\delta = 2 \\cdot \\frac{\\varepsilon}{2} = \\varepsilon$$\n\n"
                "**Step 4 — Conclude:** Therefore $\\lim_{x\\to 3}(2x+1) = 7$ by definition. $\\blacksquare$"
            )
            s["checkpoint_solution_he"] = (
                "**מטרה:** הוכח $\\lim_{x\\to 3}(2x+1) = 7$ ב-$\\varepsilon$-$\\delta$.\n\n"
                "**שלב 1 — טיוטה:** $|(2x+1)-7| = 2|x-3| < \\varepsilon$ → $|x-3| < \\varepsilon/2$ → $\\delta = \\varepsilon/2$.\n\n"
                "**שלב 2 — ציון $\\delta$:** יהי $\\varepsilon > 0$ נתון. נבחר $\\delta = \\varepsilon/2$.\n\n"
                "**שלב 3 — הוכחה:** נניח $0 < |x-3| < \\delta$. אז:\n"
                "$$|(2x+1)-7| = 2|x-3| < 2\\delta = \\varepsilon$$\n\n"
                "**שלב 4 — מסקנה:** לכן $\\lim_{x\\to 3}(2x+1) = 7$ לפי ההגדרה. $\\blacksquare$"
            )

        elif kind == "checkpoint" and "sin x" in s.get("body_en_md", ""):
            s["checkpoint_solution_en"] = (
                "**Goal:** Find $\\lim_{x\\to\\infty}\\dfrac{\\sin x}{x}$ using the squeeze theorem.\n\n"
                "**Step 1 — Bound $\\sin x$:** For all $x \\neq 0$, $-1 \\leq \\sin x \\leq 1$.\n\n"
                "**Step 2 — Divide by $|x|$:** Since $|x| \\to \\infty$, for large $|x|$ we have:\n"
                "$$-\\frac{1}{|x|} \\leq \\frac{\\sin x}{x} \\leq \\frac{1}{|x|}$$\n\n"
                "**Step 3 — Evaluate bounds:** $\\lim_{x\\to\\infty} \\pm 1/|x| = 0$.\n\n"
                "**Step 4 — Squeeze:** Both bounds go to $0$, so $\\lim_{x\\to\\infty}(\\sin x)/x = 0$. $\\blacksquare$"
            )
            s["checkpoint_solution_he"] = (
                "**מטרה:** מצא $\\lim_{x\\to\\infty}\\dfrac{\\sin x}{x}$ במשפט הסנדוויץ'.\n\n"
                "**שלב 1 — חסם $\\sin x$:** לכל $x \\neq 0$, $-1 \\leq \\sin x \\leq 1$.\n\n"
                "**שלב 2 — חלק ב-$|x|$:** עבור $|x|$ גדול:\n"
                "$$-\\frac{1}{|x|} \\leq \\frac{\\sin x}{x} \\leq \\frac{1}{|x|}$$\n\n"
                "**שלב 3 — גבולות החסמים:** $\\lim \\pm 1/|x| = 0$.\n\n"
                "**שלב 4 — סנדוויץ':** שני החסמים $\\to 0$, לכן הגבול הוא $0$. $\\blacksquare$"
            )

        elif kind == "exercise_set":
            s["body_en_md"] = (
                "Work through every exercise below. **Try each one before opening the solution** — the steps matter as much as the final answer.\n\n"
                "For $\\varepsilon$-$\\delta$ proofs, always write scratch work separately, then copy your $\\delta$ into a formal four-step proof. "
                "For squeeze problems, identify the oscillating factor first, bound it by $\\pm 1$, then multiply by the vanishing factor. "
                "Exercises e1–e4 are linear warm-ups; e5–e8 add quadratics, continuity, and squeeze; e9–e13 are university-level extensions including product rule and $\\sin x/x$.\n\n"
                "Check each solution against the four-step template before peeking — building the habit now saves points on the real exam."
            )
            s["body_he_md"] = (
                "פתרו את כל התרגילים למטה. **נסו כל תרגיל לפני שפותחים את הפתרון** — הצעדים חשובים לא פחות מהתשובה הסופית.\n\n"
                "בהוכחות $\\varepsilon$-$\\delta$, כתבו תמיד עבודת טיוטה בנפרד, ואז העתיקו את $\\delta$ להוכחה פורמלית בארבעה שלבים. "
                "בבעיות סנדוויץ', זהו קודם את הגורם המתנדד, חסמו ב-$\\pm 1$, והכפילו בגורם שואף ל-$0$. "
                "תרגילים e1–e4 הם חימום לינארי; e5–e8 מוסיפים ריבועיות, רציפות וסנדוויץ'; e9–e13 הם הרחבות אוניברסיטאיות.\n\n"
                "בדקו כל פתרון מול תבנית ארבעת השלבים לפני הצצה — בניית ההרגל עכשיו חוסכת נקודות בבחינה האמיתית."
            )

        elif kind == "why_matters":
            s["body_en_md"] = (
                "The $\\varepsilon$-$\\delta$ definition is the logical foundation of all university calculus — not a side topic you can skip.\n\n"
                "**Connections in the knowledge graph:**\n"
                "- `concept:derivatives_intro` — the derivative is defined as a limit; every differentiation rule ultimately rests on limit laws proved via $\\varepsilon$-$\\delta$.\n"
                "- `concept:integrals_intro` — Riemann sums converge because limits of sums exist; continuity guarantees integrability on closed intervals.\n"
                "- `concept:limits_at_infinity` — the same \"output tolerance / input window\" idea extends to $x \\to \\infty$ with $M$ instead of $\\delta$.\n\n"
                "**Why it matters for exams:** Israeli university analysis courses (Technion, TAU, HUJI) routinely assign full $\\varepsilon$-$\\delta$ proofs worth 15–25 points. "
                "Bagrut 5-unit students who master the linear and squeeze templates here transition smoothly to first-year real analysis."
            )
            s["body_he_md"] = (
                "ההגדרה $\\varepsilon$-$\\delta$ היא הבסיס הלוגי של כל החשבון האוניברסיטאי — לא נושא צד שאפשר לדלג עליו.\n\n"
                "**קשרים בגרף הידע:**\n"
                "- `concept:derivatives_intro` — הנגזרת מוגדרת כגבול; כל כלל גזירה נשען על חוקי גבולות שהוכחו ב-$\\varepsilon$-$\\delta$.\n"
                "- `concept:integrals_intro` — סכומי רiemann מתכנסים כי גבולות סכומים קיימים; רציפות מבטיחה אינטגרביליות.\n"
                "- `concept:limits_at_infinity` — אותו רעיון של \"סבילות פלט / חלון קלט\" מורחב ל-$x \\to \\infty$ עם $M$ במקום $\\delta$.\n\n"
                "**למה זה חשוב לבחינות:** קורסי אנליזה באוניברסיטאות בישראל דורשים הוכחות $\\varepsilon$-$\\delta$ מלאות (15–25 נקודות). "
                "תלמידי 5 יח\"ל ששולטים בתבניות הלינאריות והסנדוויץ' כאן עוברים חלק לניתוח ממשי בשנה א'."
            )

    # Question explanations (80-150 words each)
    expl = {
        1: {
            "en": (
                "**Why this is correct:**\n"
                "Scratch work gives $|(2x-3)-7| = |2x-10| = 2|x-5|$. We need $2|x-5| < \\varepsilon$, so $|x-5| < \\varepsilon/2$. "
                "Choosing $\\delta = \\varepsilon/2$ closes the chain: if $0<|x-5|<\\delta$, then $|(2x-3)-7| = 2|x-5| < 2\\delta = \\varepsilon$.\n\n"
                "**How to think about it:**\n"
                "Linear functions follow one pattern: factor $|x-a|$, read the slope $|m|$, set $\\delta = \\varepsilon/|m|$. "
                "Always open with \"Given $\\varepsilon > 0$\" and end with \"by definition.\"\n\n"
                "**Common slip:**\n"
                "Using $\\delta = \\varepsilon$ instead of $\\varepsilon/2$ — forgetting the slope factor 2. "
                "Or writing scratch work inside the proof without restating $\\delta$ formally.\n\n"
                "**Exam tip:**\n"
                "University graders award partial credit for correct $\\delta$ even if the final inequality has a sign error. "
                "State $\\delta = \\varepsilon/2$ boldly after scratch work — it is the entire insight for linear proofs."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "עבודת טיוטה: $|(2x-3)-7| = 2|x-5| < \\varepsilon$ → $|x-5| < \\varepsilon/2$ → $\\delta = \\varepsilon/2$. "
                "אם $0<|x-5|<\\delta$, אז $|(2x-3)-7| = 2|x-5| < 2\\delta = \\varepsilon$.\n\n"
                "**איך לחשוב על זה:**\n"
                "פונקציה לינארית: פרקו $|x-a|$, קראו שיפוע $|m|$, $\\delta = \\varepsilon/|m|$. "
                "פתחו ב-\"יהי $\\varepsilon > 0$ נתון\" וסיימו ב-\"לפי ההגדרה\".\n\n"
                "**טעות נפוצה:**\n"
                "$\\delta = \\varepsilon$ במקום $\\varepsilon/2$ — שכחת גורם השיפוע 2. "
                "או כתיבת טיוטה בתוך ההוכחה בלי לציין $\\delta$ בפורמליות.\n\n"
                "**טיפ לבחינה:**\n"
                "בוחנים נותנים נקודות חלקיות ל-$\\delta$ נכון גם עם טעות סימן קטנה. "
                "כתבו $\\delta = \\varepsilon/2$ בבולד אחרי הטיוטה — זו כל התובנה בהוכחה לינארית."
            ),
        },
        2: {
            "en": (
                "**Why this is correct:**\n"
                "For a constant function $f(x) = 7$, we have $|f(x) - L| = |7 - 7| = 0$ for every $x$. "
                "Since $0 < \\varepsilon$ for any positive $\\varepsilon$, the inequality $|f(x)-L| < \\varepsilon$ is automatically satisfied. "
                "Any positive $\\delta$ works — commonly $\\delta = 1$.\n\n"
                "**How to think about it:**\n"
                "Constants are the trivial base case: the output never moves, so no matter how tight $\\varepsilon$ is, zero error is always inside the tolerance. "
                "You still must write the formal proof structure for full marks.\n\n"
                "**Common slip:**\n"
                "Claiming \"no $\\delta$ is needed\" — the definition requires you to *exhibit* a specific $\\delta > 0$. "
                "Writing $\\delta = 0$ is invalid because $\\delta$ must be positive.\n\n"
                "**Exam tip:**\n"
                "When the function is constant, one line of algebra ($|c-c|=0$) plus \"for any $\\delta > 0$\" is sufficient. "
                "Do not overcomplicate — but do not skip the \"Let $\\varepsilon > 0$\" opening either."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "לפונקציה קבועה $f(x)=7$: $|f(x)-L| = |7-7| = 0$ לכל $x$. "
                "מאחר ש-$0 < \\varepsilon$ לכל $\\varepsilon$ חיובי, האי-שוויון מתקיים אוטומטית. "
                "כל $\\delta$ חיובי עובד — בדרך כלל $\\delta = 1$.\n\n"
                "**איך לחשוב על זה:**\n"
                "קבועים הם המקרה הבסיסי: הפלט לא זז, ולכן אפס שגיאה תמיד בתוך הסבילות. "
                "עדיין חובה לכתוב מבנה הוכחה פורמלי לקבלת כל הנקודות.\n\n"
                "**טעות נפוצה:**\n"
                "טענה ש\"לא צריך $\\delta$\" — ההגדרה דורשת *להציג* $\\delta > 0$ ספציפי. "
                "$\\delta = 0$ אינו תקף.\n\n"
                "**טיפ לבחינה:**\n"
                "בפונקציה קבועה, שורת אלגברה ($|c-c|=0$) ו-\"לכל $\\delta > 0$\" מספיקות. "
                "אל תסבכו — אבל גם אל תדלגו על \"יהי $\\varepsilon > 0$\"."
            ),
        },
        3: {
            "en": (
                "**Why this is correct:**\n"
                "Here $f(x) = |x|$ and $L = 0$ at $c = 0$. Note $||x| - 0| = |x| = |x - 0|$. "
                "Choosing $\\delta = \\varepsilon$ gives: if $0 < |x| < \\delta$, then $||x| - 0| = |x| < \\delta = \\varepsilon$.\n\n"
                "**How to think about it:**\n"
                "When the absolute value is centered at zero, $|x|$ and $|x-0|$ coincide — the proof is essentially one line. "
                "This is also a good sanity check for understanding why $\\delta$ can equal $\\varepsilon$ directly.\n\n"
                "**Common slip:**\n"
                "Writing $||x|| = x$ without cases — at negative $x$, $|x| = -x$, not $x$. "
                "The proof via $|x-0|$ avoids case analysis entirely.\n\n"
                "**Exam tip:**\n"
                "Identity-style limits ($|x-c|$ at $c$) appear as warm-ups before quadratic proofs. "
                "Recognize the pattern: $\\delta = \\varepsilon$ with no extra factors."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "כאן $f(x)=|x|$, $L=0$, $c=0$. שימו לב: $||x|-0| = |x| = |x-0|$. "
                "בחירת $\\delta = \\varepsilon$ נותנת: אם $0<|x|<\\delta$, אז $||x|-0| = |x| < \\delta = \\varepsilon$.\n\n"
                "**איך לחשוב על זה:**\n"
                "כשערך מוחלט ממורכז ב-$0$, $|x|$ ו-$|x-0|$ זהים — ההוכחה היא שורה אחת. "
                "זו גם בדיקת sanity למה $\\delta$ יכול להיות $\\varepsilon$ ישירות.\n\n"
                "**טעות נפוצה:**\n"
                "כתיבת $||x|| = x$ בלי מקרים — ב-$x$ שלילי, $|x|=-x$. "
                "הוכחה דרך $|x-0|$ נמנעת מפירוק למקרים.\n\n"
                "**טיפ לבחינה:**\n"
                "גבולות \"זהות\" ($|x-c|$ ב-$c$) מופיעים כחימום לפני הוכחות ריבועיות. "
                "זהו את הדפוס: $\\delta = \\varepsilon$ ללא גורמים נוספים."
            ),
        },
        4: {
            "en": (
                "**Why this is correct:**\n"
                "$|(5-2x)-3| = |-2x+2| = 2|x-1|$. We need $2|x-1| < \\varepsilon$, so $|x-1| < \\varepsilon/2$. "
                "With $\\delta = \\varepsilon/2$, if $0<|x-1|<\\delta$ then $|(5-2x)-3| = 2|x-1| < 2\\delta = \\varepsilon$.\n\n"
                "**How to think about it:**\n"
                "Watch the sign of the slope: $f(x) = 5 - 2x$ has slope $-2$, but $|a| = 2$ regardless. "
                "The $\\delta$ formula uses $|m|$, never the signed slope.\n\n"
                "**Common slip:**\n"
                "Using $\\delta = \\varepsilon/(-2)$ or forgetting absolute value on the coefficient — $\\delta$ must be positive. "
                "Another trap: expanding $(5-2x)-3$ incorrectly as $2-2x$ instead of $-2x+2$.\n\n"
                "**Exam tip:**\n"
                "After scratch work, write $\\delta = \\varepsilon/2$ and box it. Graders scan for the $\\delta$ choice before reading the algebra chain."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "$|(5-2x)-3| = |-2x+2| = 2|x-1|$. צריך $2|x-1| < \\varepsilon$ → $|x-1| < \\varepsilon/2$ → $\\delta = \\varepsilon/2$.\n\n"
                "**איך לחשוב על זה:**\n"
                "שימו לב לסימן השיפוע: $f(x)=5-2x$ עם שיפוע $-2$, אך $|a|=2$ בכל מקרה. "
                "נוסחת $\\delta$ משתמשת ב-$|m|$, לא בשיפוע עם סימן.\n\n"
                "**טעות נפוצה:**\n"
                "$\\delta = \\varepsilon/(-2)$ או שכחת ערך מוחלט — $\\delta$ חייבת להיות חיובית. "
                "מלכודת נוספת: פירוק $(5-2x)-3$ ל-$2-2x$ במקום $-2x+2$.\n\n"
                "**טיפ לבחינה:**\n"
                "אחרי טיוטה, כתבו $\\delta = \\varepsilon/2$ וסמנו. בוחנים מחפשים את בחירת $\\delta$ לפני שרשרת האלגברה. "
                "זכרו: $\\delta$ חייבת להיות חיובית — השתמשו ב-$|m|$, לא בשיפוע עם סימן."
            ),
        },
        5: {
            "en": (
                "**Why this is correct:**\n"
                "$|x^2-9| = |x-3||x+3|$. Restrict $|x-3|<1$ so $x \\in (2,4)$, giving $|x+3|<7$. "
                "Thus $|x^2-9| < 7|x-3|$. Choose $\\delta = \\min(1, \\varepsilon/7)$: if $|x-3|<\\delta$, then $|x^2-9| < 7|x-3| < 7 \\cdot (\\varepsilon/7) = \\varepsilon$.\n\n"
                "**How to think about it:**\n"
                "Quadratic proofs always need the restriction trick: bound the extra factor $|x+c|$ on a small interval, then take $\\delta = \\min(1, \\varepsilon/M)$.\n\n"
                "**Common slip:**\n"
                "Choosing $\\delta = \\varepsilon/7$ without the $\\min(1,\\ldots)$ — if $\\varepsilon > 7$, this $\\delta$ could exceed 1 and the bound $|x+3|<7$ fails.\n\n"
                "**Exam tip:**\n"
                "Write the restriction $|x-c|<1$ explicitly in scratch work, compute $M$, then state $\\delta = \\min(1, \\varepsilon/M)$. This template appears on nearly every analysis midterm."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "$|x^2-9| = |x-3||x+3|$. הגבילו $|x-3|<1$ → $x\\in(2,4)$ → $|x+3|<7$. "
                "לכן $|x^2-9| < 7|x-3|$. בחרו $\\delta = \\min(1, \\varepsilon/7)$.\n\n"
                "**איך לחשוב על זה:**\n"
                "הוכחות ריבועיות דורשות טריק הגבלה: חסמו $|x+c|$ בקטע קטן, ואז $\\delta = \\min(1, \\varepsilon/M)$.\n\n"
                "**טעות נפוצה:**\n"
                "$\\delta = \\varepsilon/7$ בלי $\\min(1,\\ldots)$ — אם $\\varepsilon > 7$, $\\delta$ עלולה לחרוג מ-1 והחסם $|x+3|<7$ נכשל.\n\n"
                "**טיפ לבחינה:**\n"
                "כתבו $|x-c|<1$ בטיוטה, חשבו $M$, וציינו $\\delta = \\min(1, \\varepsilon/M)$. תבנית זו מופיעה בכמעט כל מבחן אנליזה. "
                "אם $\\varepsilon$ גדול, $\\min$ מגן מפני $\\delta>1$ ששובר את החסם על $|x+c|$."
            ),
        },
        6: {
            "en": (
                "**Why this is correct:**\n"
                "Continuity at $x=2$ requires: for every $\\varepsilon>0$, there exists $\\delta>0$ with $|x-2|<\\delta \\implies |x^2-4|<\\varepsilon$. "
                "Using $|x^2-4|=|x-2||x+2|$ and restricting $|x-2|<1$ gives $|x+2|<5$, so $|x^2-4|<5|x-2|$. "
                "Choose $\\delta=\\min(1,\\varepsilon/5)$.\n\n"
                "**How to think about it:**\n"
                "Continuity drops the strict $0<|x-c|$ — values *at* $c$ must also satisfy the inequality. "
                "The algebra is identical to the limit proof; only the hypothesis changes.\n\n"
                "**Common slip:**\n"
                "Proving the limit exists but forgetting to note $f(2)=4$ — continuity needs three conditions, not just the $\\varepsilon$-$\\delta$ bound.\n\n"
                "**Exam tip:**\n"
                "State explicitly: \"$f(2)=4$ and for $|x-2|<\\delta$, $|x^2-4|<\\varepsilon$.\" Combining both sentences earns full continuity marks."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "רציפות ב-$x=2$ דורשת: לכל $\\varepsilon>0$, קיים $\\delta>0$ עם $|x-2|<\\delta \\implies |x^2-4|<\\varepsilon$. "
                "מ-$|x^2-4|=|x-2||x+2|$ והגבלה $|x-2|<1$ → $|x+2|<5$ → $|x^2-4|<5|x-2|$ → $\\delta=\\min(1,\\varepsilon/5)$.\n\n"
                "**איך לחשוב על זה:**\n"
                "ברציפות מושמט $0<|x-c|$ — גם ערכים *ב*-$c$ חייבים לעמוד באי-השוויון. "
                "האלגברה זהה להוכחת גבול; רק ההנחה משתנה.\n\n"
                "**טעות נפוצה:**\n"
                "הוכחת קיום גבול בלי לציין $f(2)=4$ — רציפות דורשת שלושה תנאים.\n\n"
                "**טיפ לבחינה:**\n"
                "ציינו במפורש: \"$f(2)=4$ ולכל $|x-2|<\\delta$, $|x^2-4|<\\varepsilon$.\" שילוב שני המשפטים מבטיח את כל הנקודות."
            ),
        },
        7: {
            "en": (
                "**Why this is correct:**\n"
                "$|x^2\\sin(1/x^2)| \\leq x^2$ because $|\\sin(1/x^2)| \\leq 1$. So $-x^2 \\leq x^2\\sin(1/x^2) \\leq x^2$. "
                "Both bounds $\\to 0$ as $x \\to 0$, so by the squeeze theorem the limit is $0$.\n\n"
                "**How to think about it:**\n"
                "The pattern: bound the wild trig factor by $\\pm 1$, multiply by the vanishing polynomial ($x^2$ here), verify both bounds share limit $0$.\n\n"
                "**Common slip:**\n"
                "Claiming the limit does not exist because $\\sin(1/x^2)$ oscillates — squeeze does not require monotonicity of the middle term.\n\n"
                "**Exam tip:**\n"
                "Write the three-line template: (1) $|\\sin|\\leq 1$, (2) multiply and simplify, (3) evaluate bounds. Examiners give method marks for the sandwich setup even if the final limit is misstated."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "$|x^2\\sin(1/x^2)| \\leq x^2$ כי $|\\sin(1/x^2)| \\leq 1$. לכן $-x^2 \\leq x^2\\sin(1/x^2) \\leq x^2$. "
                "שני החסמים $\\to 0$ ב-$x\\to 0$, ולפי סנדוויץ' הגבול הוא $0$.\n\n"
                "**איך לחשוב על זה:**\n"
                "דפוס: חסמו את הטריג ב-$\\pm 1$, הכפילו בפולינום שואף ל-$0$ ($x^2$ כאן), וודאו ששני החסמים לאותו גבול.\n\n"
                "**טעות נפוצה:**\n"
                "טענה שהגבול לא קיים כי $\\sin(1/x^2)$ מתנדנד — סנדוויץ' לא דורש מונוטוניות.\n\n"
                "**טיפ לבחינה:**\n"
                "כתבו תבנית שלוש שורות: (1) $|\\sin|\\leq 1$, (2) הכפלה ופישוט, (3) חישוב גבולות החסמים. בוחנים נותנים נקודות שיטה על בניית הסנדוויץ'."
            ),
        },
        8: {
            "en": (
                "**Why this is correct:**\n"
                "By the mean value theorem, $|\\sin x - \\sin c| = |\\cos\\xi||x-c| \\leq |x-c|$ for some $\\xi$ between $x$ and $c$ (since $|\\cos\\xi|\\leq 1$). "
                "Given $\\varepsilon>0$, choose $\\delta=\\varepsilon$: if $|x-c|<\\delta$, then $|\\sin x-\\sin c|\\leq|x-c|<\\varepsilon$.\n\n"
                "**How to think about it:**\n"
                "This is a Lipschitz-style bound: sine changes at most as fast as its argument. "
                "The $\\varepsilon$-$\\delta$ proof is then one line — $\\delta = \\varepsilon$ with no extra factors.\n\n"
                "**Common slip:**\n"
                "Using $\\delta = \\varepsilon/2$ out of habit from linear proofs — here the coefficient is 1, not 2. "
                "Or citing MVT without noting $|\\cos\\xi|\\leq 1$.\n\n"
                "**Exam tip:**\n"
                "When asked to prove continuity of $\\sin x$ \"everywhere,\" fix an arbitrary $c$ and write the proof with generic $c$. "
                "One template covers all points — do not prove separately for each value."
            ),
            "he": (
                "**למה זה נכון:**\n"
                "לפי משפט ערך הממוצע: $|\\sin x - \\sin c| = |\\cos\\xi||x-c| \\leq |x-c|$ לאיזשהו $\\xi$ בין $x$ ל-$c$ (כי $|\\cos\\xi|\\leq 1$). "
                "בהינתן $\\varepsilon>0$, בחר $\\delta=\\varepsilon$: אם $|x-c|<\\delta$, אז $|\\sin x-\\sin c| \\leq |x-c| < \\varepsilon$.\n\n"
                "**איך לחשוב על זה:**\n"
                "זהו חסם מסוג Lipschitz: סינוס משתנה לכל היותר בקצב של הארגומנט. "
                "הוכחת $\\varepsilon$-$\\delta$ היא שורה אחת — $\\delta = \\varepsilon$ ללא גורמים נוספים.\n\n"
                "**טעות נפוצה:**\n"
                "$\\delta = \\varepsilon/2$ מכוח הרגל מהוכחות לינאריות — כאן המקדם 1, לא 2. "
                "או ציטוט MVT בלי $|\\cos\\xi|\\leq 1$.\n\n"
                "**טיפ לבחינה:**\n"
                "כשמבקשים רציפות של $\\sin x$ \"בכל מקום\", קבעו $c$ כללי והוכיחו עם $c$ כפרמטר. "
                "תבנית אחת מכסה את כל הנקודות."
            ),
        },
    }

    for q in data["questions"]:
        o = q["ord"]
        if o in expl:
            q["explanation_en"] = expl[o]["en"]
            q["explanation_he"] = expl[o]["he"]

    LESSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Written:", LESSON)

    # Validate
    issues = []
    for s in data["sections"]:
        kind = s.get("kind")
        mins = {
            "intro": (110, 90), "definition": (130, 110), "theory": (160, 130),
            "worked_example": (130, 110), "pitfall": (100, 85), "why_matters": (90, 75),
            "method_guide": (100, 85), "before_exam": (90, 75), "summary": (70, 60),
            "exercise_set": (90, 75),
        }.get(kind)
        if mins:
            en, he = wc(s["body_en_md"]), wc(s["body_he_md"])
            if en < mins[0]:
                issues.append(f"{kind} EN: {en} < {mins[0]}")
            if he < mins[1]:
                issues.append(f"{kind} HE: {he} < {mins[1]}")
    for q in data["questions"]:
        en, he = wc(q["explanation_en"]), wc(q["explanation_he"])
        if en < 80:
            issues.append(f"q{q['ord']} expl-en: {en}")
        if he < 80:
            issues.append(f"q{q['ord']} expl-he: {he}")
    if issues:
        print("ISSUES:")
        for i in issues:
            print(" ", i)
    else:
        print("All depth gates passed.")


if __name__ == "__main__":
    main()
