# -*- coding: utf-8 -*-
"""Patch question explanations to 80-150 words for trigonometric_identities.json."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parent / "seed_data/lessons/trigonometric_identities.json"

with PATH.open(encoding="utf-8") as f:
    lesson = json.load(f)

EXPLANATIONS = [
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "The Pythagorean identity $\\sin^2 x + \\cos^2 x = 1$ rearranges to $1 - \\sin^2 x = \\cos^2 x$ — option B.\n\n"
            "**How to think about it:**\n"
            "Whenever you see $1\\pm\\sin^2 x$ or $1\\pm\\cos^2 x$, reach for Pythagoras before any other identity. "
            "This pattern appears in proofs, simplifications, and MCQ items throughout Bagrut 5 units.\n\n"
            "**Common slip:**\n"
            "Option A ($\\cos x$) drops the square; option C would require $1=2\\sin^2 x$ for all $x$; "
            "option D confuses $\\tan^2 x+1=\\sec^2 x$ with this rearrangement.\n\n"
            "**Exam tip:**\n"
            "Verify with $x=0$: $1-\\sin^2 0=1=\\cos^2 0$. A 5-second check prevents MCQ errors under time pressure."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "מזהות פיתגורס $\\sin^2 x + \\cos^2 x = 1$ מתקבל $1 - \\sin^2 x = \\cos^2 x$ — אפשרות ב'.\n\n"
            "**איך לחשוב על זה:**\n"
            "בכל $1\\pm\\sin^2 x$ או $1\\pm\\cos^2 x$, פנו קודם לפיתגורס לפני כל זהות אחרת. "
            "הדפוס הזה חוזר בהוכחות, בפישוט ובשאלות רב-ברירה בבגרות 5 יחידות.\n\n"
            "**טעות נפוצה:**\n"
            "אפשרות א' ($\\cos x$) מוותרת על הריבוע; ג' דורשת $1=2\\sin^2 x$ לכל $x$; "
            "ד' מבלבלת עם $\\tan^2 x+1=\\sec^2 x$.\n\n"
            "**טיפ לבחינה:**\n"
            "אימות: $x=0$ נותן $1=\\cos^2 0$. בדיקה של 5 שניות מונעת טעויות ברב-ברירה תחת לחץ. "
            "שמרו את נגזרות פיתגורס ($1-\\sin^2=\\cos^2$, $1-\\cos^2=\\sin^2$) בראש — הן מופיעות "
            "בכל פרק זהויות בבגרות 5 יחידות."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "The double-angle formula for sine is $\\sin(2x)=2\\sin x\\cos x$ — option B matches exactly.\n\n"
            "**How to think about it:**\n"
            "You double the **angle**, not the function value. Sine double-angle always includes **both** "
            "$\\sin x$ and $\\cos x$ multiplied together.\n\n"
            "**Common slip:**\n"
            "Option A ($2\\sin x$) is the classic $\\sin(2x)=2\\sin x$ error; at $x=30°$, $\\sin60°=\\sqrt3/2$ "
            "but $2\\sin30°=1$. Options C and D are $\\cos(2x)$ forms, not $\\sin(2x)$.\n\n"
            "**Exam tip:**\n"
            "Write the formula before substituting values. Under time pressure, students swap sine and cosine "
            "double-angle formulas — naming the identity first prevents this."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "נוסחת זווית כפולה לסינוס: $\\sin(2x)=2\\sin x\\cos x$ — אפשרות ב'.\n\n"
            "**איך לחשוב על זה:**\n"
            "מכפילים את **הזווית**, לא את ערך הפונקציה. זווית כפולה לסינוס תמיד כוללת **גם** $\\sin x$ **גם** $\\cos x$.\n\n"
            "**טעות נפוצה:**\n"
            "אפשרות א' ($2\\sin x$) — הטעות $\\sin(2x)=2\\sin x$; ב-$x=30°$, $\\sin60°=\\sqrt3/2$ אך $2\\sin30°=1$. "
            "ג' ו-ד' הן צורות $\\cos(2x)$.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו את הנוסחה לפני הצבה. תחת לחץ מבלבלים בין נוסחאות סינוס וקוסינוס — שם הזהות קודם מונע זאת. "
            "זכרו: $\\cos(2x)$ ו-$\\sin(2x)$ הן נוסחאות נפרדות — אל תחליפו ביניהן."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Start LHS: convert $\\tan x$ and $\\cot x$ to $\\sin/\\cos$, common denominator "
            "$(\\sin^2 x+\\cos^2 x)/(\\sin x\\cos x)=1/(\\sin x\\cos x)$, then use $\\sin(2x)=2\\sin x\\cos x$ "
            "to get $2/\\sin(2x)$.\n\n"
            "**How to think about it:**\n"
            "This is a standard multi-step proof combining conversion, Pythagorean identity, and double-angle — "
            "a common 8-point Bagrut pattern.\n\n"
            "**Common slip:**\n"
            "Cross-multiplying or treating this as an equation to solve for $x$ — invalid in identity proofs.\n\n"
            "**Exam tip:**\n"
            "Label each step LHS = … = RHS. Partial credit rewards each correct substitution. "
            "State domain: $\\sin x\\ne0$, $\\cos x\\ne0$."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "מצ״ש: המרת $\\tan x$ ו-$\\cot x$ ל-$\\sin/\\cos$, מכנה משותף "
            "$(\\sin^2 x+\\cos^2 x)/(\\sin x\\cos x)=1/(\\sin x\\cos x)$, ואז $\\sin(2x)=2\\sin x\\cos x$ "
            "נותן $2/\\sin(2x)$.\n\n"
            "**איך לחשוב על זה:**\n"
            "הוכחה רב-שלבית שמשלבת המרה, פיתגורס וזווית כפולה — דפוס נפוץ ב-8 נקודות בבגרות.\n\n"
            "**טעות נפוצה:**\n"
            "הכפלה צולבת או \"פתרון\" ל-$x$ — לא תקף בהוכחות זהויות.\n\n"
            "**טיפ לבחינה:**\n"
            "סמנו צ״ש = … = צ״י. כל הצבה נכונה שווה נקודות. ציינו תחום: $\\sin x\\ne0$, $\\cos x\\ne0$. "
            "הוכחה זו מופיעה כמעט בכל מועד בגרות 5 יחידות — תרגלו אותה עד שזורמת בלי רשימות."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "The statement is **False**. $\\cos(A+B)=\\cos A\\cos B-\\sin A\\sin B$, not $\\cos A+\\cos B$.\n\n"
            "**How to think about it:**\n"
            "Trigonometric functions do not distribute over addition. Only structured sum formulas apply — "
            "never assume linearity like ordinary algebra.\n\n"
            "**Common slip:**\n"
            "Students write $\\cos(A+B)=\\cos A+\\cos B$ by analogy with $2(x+y)=2x+2y$. "
            "Counterexample: $A=B=\\pi/3$ gives LHS$=-1/2$ but RHS$=1$.\n\n"
            "**Exam tip:**\n"
            "When unsure on true/false identity items, test with $A=B=45°$ or $\\pi/4$. "
            "One counterexample disproves the claim. Never assume trig functions distribute like polynomials."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "הטענה **שגויה**. $\\cos(A+B)=\\cos A\\cos B-\\sin A\\sin B$, לא $\\cos A+\\cos B$.\n\n"
            "**איך לחשוב על זה:**\n"
            "פונקציות טריגונומטריות לא \"מתפזרות\" על חיבור. רק נוסחאות סכום מובנות — אל תניחו לינאריות.\n\n"
            "**טעות נפוצה:**\n"
            "כותבים $\\cos(A+B)=\\cos A+\\cos B$ בדמיון ל-$2(x+y)=2x+2y$. "
            "דוגמה נגדית: $A=B=\\pi/3$ נותן $-1/2$ מול $1$.\n\n"
            "**טיפ לבחינה:**\n"
            "בשאלות נכון/לא נכון, בדקו עם $A=B=45°$. דוגמה נגדית אחת מספיקה להפרכה. "
            "אל תניחו שפונקציות טריגונומטריות מתפזרות כמו פולינומים — זו טעות שחוזרת בכל מועד. "
            "שימו לב: $\\sin(A+B)$ **כן** מתפזר, אך $\\cos(A+B)$ **לא** — הסימן והמבנה שונים לחלוטין."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Let $a=\\sin^2 x$, $b=\\cos^2 x$. Then $\\sin^6 x+\\cos^6 x=a^3+b^3=(a+b)(a^2-ab+b^2)$. "
            "Since $a+b=1$, rewrite as $(a+b)^2-3ab=1-3\\sin^2 x\\cos^2 x$.\n\n"
            "**How to think about it:**\n"
            "Sixth powers signal the sum-of-cubes factorization $a^3+b^3$ — much faster than expanding term by term.\n\n"
            "**Common slip:**\n"
            "Expanding $\\sin^6$ and $\\cos^6$ directly without factoring — correct but wastes exam time.\n\n"
            "**Exam tip:**\n"
            "Partial credit on 8-point proofs rewards correct setup with $a=\\sin^2 x$, $b=\\cos^2 x$ even if "
            "the final simplification has a minor algebra slip. Spot $a^3+b^3$ before expanding sixth powers."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "נסמן $a=\\sin^2 x$, $b=\\cos^2 x$. אז $\\sin^6 x+\\cos^6 x=a^3+b^3=(a+b)(a^2-ab+b^2)$. "
            "מכיוון $a+b=1$, מתקבל $(a+b)^2-3ab=1-3\\sin^2 x\\cos^2 x$.\n\n"
            "**איך לחשוב על זה:**\n"
            "חזקות שישית מרמזות על $a^3+b^3$ — מהיר הרבה יותר מפיתוח איבר-איבר.\n\n"
            "**טעות נפוצה:**\n"
            "פיתוח $\\sin^6$ ו-$\\cos^6$ ישירות בלי פירוק — נכון אך מבזבז זמן בבחינה.\n\n"
            "**טיפ לבחינה:**\n"
            "נקודות חלקיות ניתנות על הגדרה נכונה $a=\\sin^2 x$, $b=\\cos^2 x$ גם אם הפישוט הסופי טועה מעט. "
            "זיהו $a^3+b^3$ לפני פיתוח חזקות שישית — חוסך 3–4 דקות בשאלת הוכחה ארוכה. "
            "אחרי הפירוק, השתמשו ב-$a+b=\\sin^2 x+\\cos^2 x=1$ כדי לצמצם ל-$1-3ab$."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "Divide $\\sin^2 x+\\cos^2 x=1$ by $\\cos^2 x$ (for $\\cos x\\ne0$): "
            "$\\tan^2 x+1=\\sec^2 x$ — the standard Pythagorean derivative.\n\n"
            "**How to think about it:**\n"
            "Every proof of $\\tan^2+1=\\sec^2$ either divides Pythagoras by $\\cos^2$ or converts "
            "$\\tan x=\\sin x/\\cos x$ on the LHS and combines fractions.\n\n"
            "**Common slip:**\n"
            "Assuming $\\tan^2 x+1=\\sec^2 x$ without showing the division or conversion step loses proof marks.\n\n"
            "**Exam tip:**\n"
            "State the domain $\\cos x\\ne0$ explicitly when you divide. Bagrut graders deduct for missing "
            "domain restrictions even when the algebra is correct. This one-line proof is worth memorizing cold."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "מחלקים $\\sin^2 x+\\cos^2 x=1$ ב-$\\cos^2 x$ (ל-$\\cos x\\ne0$): "
            "$\\tan^2 x+1=\\sec^2 x$ — נגזרת פיתגורס סטנדרטית.\n\n"
            "**איך לחשוב על זה:**\n"
            "כל הוכחה של $\\tan^2+1=\\sec^2$ או מחלקת פיתגורס ב-$\\cos^2$ או ממירה $\\tan x=\\sin x/\\cos x$ "
            "ומאחדת שברים.\n\n"
            "**טעות נפוצה:**\n"
            "להניח $\\tan^2 x+1=\\sec^2 x$ בלי להראות את החלוקה או ההמרה — מאבד נקודות הוכחה.\n\n"
            "**טיפ לבחינה:**\n"
            "ציינו $\\cos x\\ne0$ במפורש בחלוקה. בודקים מורידים על הגבלות תחום חסרות גם כשהאלגברה נכונה. "
            "הוכחה קצרה זו שווה לשינון בעל פה — היא בסיס לכל נגזרות $\\sec^2$ ו-$\\csc^2$. "
            "אפשר גם להוכיח מצ״ש: $\\tan^2 x+1=\\frac{\\sin^2 x+\\cos^2 x}{\\cos^2 x}=\\sec^2 x$. "
            "שתי הדרכים שקולות — בחרו את הנוחה לכם."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "$\\cos(2x)=\\cos^2 x-\\sin^2 x$. Replace $\\cos^2 x=1-\\sin^2 x$ by Pythagoras: "
            "$\\cos(2x)=(1-\\sin^2 x)-\\sin^2 x=1-2\\sin^2 x$.\n\n"
            "**How to think about it:**\n"
            "$\\cos(2x)$ has three equivalent forms — choose the one that matches what you need to eliminate. "
            "Here the target has $\\sin^2 x$, so replace $\\cos^2 x$.\n\n"
            "**Common slip:**\n"
            "Using $\\cos(2x)=2\\cos^2 x-1$ when the goal expression contains only $\\sin^2 x$ — wrong form choice.\n\n"
            "**Exam tip:**\n"
            "Before substituting, ask: \"Do I want to eliminate sines or cosines?\" That picks the right "
            "$\\cos(2x)$ form in one decision. All three forms are equivalent — choose for convenience."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "$\\cos(2x)=\\cos^2 x-\\sin^2 x$. מחליפים $\\cos^2 x=1-\\sin^2 x$ מפיתגורס: "
            "$\\cos(2x)=(1-\\sin^2 x)-\\sin^2 x=1-2\\sin^2 x$.\n\n"
            "**איך לחשוב על זה:**\n"
            "ל-$\\cos(2x)$ שלוש צורות שקולות — בחרו את זו שמתאימה למה שצריך לצמצם. "
            "כאן היעד מכיל $\\sin^2 x$, ולכן מחליפים $\\cos^2 x$.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$\\cos(2x)=2\\cos^2 x-1$ כשהביטוי הסופי מכיל רק $\\sin^2 x$ — בחירת צורה שגויה.\n\n"
            "**טיפ לבחינה:**\n"
            "לפני הצבה, שאלו: \"רוצים לצמצם סינוסים או קוסינוסים?\" — זה קובע את צורת $\\cos(2x)$ הנכונה. "
            "שלוש הצורות שקולות — בחרו לפי הנוחות. נוסחה זו מופיעה לעיתים קרובות בהמרת $\\cos^2 x$ ל-$\\sin^2 x$. "
            "אימות: ב-$x=0$, $\\cos(0)=1$ ו-$1-2\\sin^2 0=1$ — שני הצדדים תואמים."
        ),
    },
    {
        "explanation_en": (
            "**Why this is correct:**\n"
            "RHS: $\\csc x+\\cot x=(1+\\cos x)/\\sin x$. Multiply by conjugate $(1-\\cos x)$: "
            "numerator $=1-\\cos^2 x=\\sin^2 x$, so RHS$=\\sin x/(1-\\cos x)=$ LHS.\n\n"
            "**How to think about it:**\n"
            "Denominators with $1\\pm\\cos x$ or $1\\pm\\sin x$ often yield Pythagorean identity after "
            "conjugate multiplication — a signature Bagrut move.\n\n"
            "**Common slip:**\n"
            "Cross-multiplying the original identity treats it as an equation and assumes what you prove.\n\n"
            "**Exam tip:**\n"
            "When the RHS has $\\csc+\\cot$, combine to a single fraction first, then conjugate. "
            "Domain: $\\sin x\\ne0$ and $1-\\cos x\\ne0$. Conjugate tricks appear on most Bagrut proof sections."
        ),
        "explanation_he": (
            "**למה זה נכון:**\n"
            "צ״י: $\\csc x+\\cot x=(1+\\cos x)/\\sin x$. כפל בצמוד $(1-\\cos x)$: "
            "מונה $=1-\\cos^2 x=\\sin^2 x$, ולכן צ״י$=\\sin x/(1-\\cos x)=$ צ״ש.\n\n"
            "**איך לחשוב על זה:**\n"
            "מכנים עם $1\\pm\\cos x$ או $1\\pm\\sin x$ לעיתים נותנים פיתגורס אחרי כפל בצמוד — "
            "מהלך מרכזי בבגרות.\n\n"
            "**טעות נפוצה:**\n"
            "הכפלה צולבת של הזהות המקורית — מתייחסים לזהות כמשוואה ומניחים את מה שמוכיחים.\n\n"
            "**טיפ לבחינה:**\n"
            "כשיש $\\csc+\\cot$ בצ״י, אחדו לשבר אחד ואז כפלו בצמוד. תחום: $\\sin x\\ne0$, $1-\\cos x\\ne0$. "
            "טריק הצמוד מופיע ברוב פרקי ההוכחות בבגרות — תרגלו על $\\frac{\\sin x}{1-\\cos x}$ ו-$\\frac{1+\\sin x}{\\cos x}$."
        ),
    },
]

for i, expl in enumerate(EXPLANATIONS):
    lesson["questions"][i].update(expl)

with PATH.open("w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("Patched explanations for", PATH.name)
