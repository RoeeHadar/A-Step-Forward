"""One-shot expansion for series_convergence_tests.json — Cursor batch."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/series_convergence_tests.json"

EXPLANATIONS = {
    1: {
        "en": (
            "**Why this is correct:**\n"
            "The series $\\sum_{n=1}^{\\infty} \\frac{1}{n^3}$ matches the p-series template "
            "$\\sum \\frac{1}{n^p}$ with $p = 3$. The p-series test states convergence if and only if $p > 1$. "
            "Since $3 > 1$, the series **converges**. No ratio or comparison test is needed once you recognize the form.\n\n"
            "**How to think about it:**\n"
            "Start every series problem by classifying the term $a_n$. Powers of $n$ in the denominator with a fixed exponent "
            "almost always signal a p-series. Verify $a_n \\to 0$ with the divergence test (here $1/n^3 \\to 0$), "
            "then apply the decisive p-test.\n\n"
            "**Common slip:**\n"
            "Confusing $p = 3$ with \"converges because terms go to zero.\" The harmonic series $\\sum 1/n$ also has "
            "$a_n \\to 0$ yet diverges — going to zero is necessary but not sufficient.\n\n"
            "**Exam tip:**\n"
            "Israeli university exams expect you to **name the test** explicitly: write \"p-series with $p = 3 > 1$, converges.\" "
            "That one sentence earns a method mark even if you never compute a limit."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "הטור $\\sum_{n=1}^{\\infty} \\frac{1}{n^3}$ מתאים לתבנית טור p: $\\sum \\frac{1}{n^p}$ עם $p = 3$. "
            "מבחן טורי p קובע: מתכנס אם ורק אם $p > 1$. מכיוון ש-$3 > 1$, הטור **מתכנס**. "
            "אין צורך במבחן מנה או השוואה ברגע שמזהים את הצורה.\n\n"
            "**איך לחשוב על זה:**\n"
            "בכל בעיית טור, סווגו תחילה את האיבר $a_n$. חזקות של $n$ במכנה עם מעריך קבוע "
            "כמעט תמיד מרמזות על טור p. אמתו $a_n \\to 0$ במבחן הגבול (כאן $1/n^3 \\to 0$), "
            "ואז הפעילו את מבחן p.\n\n"
            "**טעות נפוצה:**\n"
            "לבלבל $p = 3$ עם \"מתכנס כי האיברים שואפים לאפס.\" הטור ההרמוני $\\sum 1/n$ גם שואף לאפס אך מתבדר — "
            "שאיפה לאפס הכרחית אך לא מספיקה.\n\n"
            "**טיפ לבחינה:**\n"
            "בבחינות אוניברסיטאיות מצפים **לציין את המבחן**: \"טור p עם $p = 3 > 1$, מתכנס.\" "
            "משפט אחד זה מזכה בנקודת שיטה גם בלי חישוב גבול."
        ),
    },
    2: {
        "en": (
            "**Why this is correct:**\n"
            "$\\sum_{n=1}^{\\infty} \\frac{1}{n}$ is the **harmonic series**, the borderline p-series with $p = 1$. "
            "The p-series test requires $p > 1$ for convergence; at $p = 1$ the condition fails, so the series **diverges**. "
            "This is one of the most important counterexamples in calculus.\n\n"
            "**How to think about it:**\n"
            "Memorize: $\\sum 1/n^p$ converges iff $p > 1$. The harmonic series ($p = 1$) diverges slowly — "
            "partial sums grow like $\\ln n$ — which is why $a_n \\to 0$ alone does not guarantee convergence.\n\n"
            "**Common slip:**\n"
            "Assuming \"each term is smaller than the previous, so it must converge.\" Decreasing terms are necessary "
            "for many tests but not sufficient; the harmonic series decreases yet diverges.\n\n"
            "**Exam tip:**\n"
            "When a series looks like $1/n$, state immediately: \"harmonic / p-series with $p = 1$, diverges.\" "
            "Examiners use this as a quick classification question and as a comparison benchmark in limit-comparison problems."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "$\\sum_{n=1}^{\\infty} \\frac{1}{n}$ הוא **הטור ההרמוני**, טור p הגבולי עם $p = 1$. "
            "מבחן טורי p דורש $p > 1$ להתכנסות; ב-$p = 1$ התנאי נכשל, ולכן הטור **מתבדר**. "
            "זו אחת מדוגמאות הנגד החשובות ביותר בחשבון.\n\n"
            "**איך לחשוב על זה:**\n"
            "זכרו: $\\sum 1/n^p$ מתכנס אם ורק אם $p > 1$. הטור ההרמוני ($p = 1$) מתבדר לאט — "
            "סכומים חלקיים גדלים כמו $\\ln n$ — ולכן $a_n \\to 0$ לבדו לא מבטיח התכנסות.\n\n"
            "**טעות נפוצה:**\n"
            "להניח \"כל איבר קטן מהקודם, אז חייב להתכנס.\" ירידה הכרחית במבחנים רבים אך לא מספיקה; "
            "הטור ההרמוני יורד ועדיין מתבדר.\n\n"
            "**טיפ לבחינה:**\n"
            "כשטור נראה כמו $1/n$, כתבו מיד: \"הרמוני / טור p עם $p = 1$, מתבדר.\" "
            "בודקים משתמשים בזה לסיווג מהיר וכאמת מידה בהשוואת גבולות."
        ),
    },
    3: {
        "en": (
            "**Why this is correct:**\n"
            "The divergence test examines $\\lim_{n\\to\\infty} a_n$. Here $a_n = \\frac{n}{n+1} \\to 1 \\neq 0$. "
            "When the general term does not approach zero, the partial sums cannot settle to a finite limit, "
            "so $\\sum \\frac{n}{n+1}$ **diverges** by the divergence test.\n\n"
            "**How to think about it:**\n"
            "Always run the divergence test first — it takes one limit and can instantly prove divergence. "
            "If $\\lim a_n = L \\neq 0$, adding infinitely many terms near $L$ blows up. "
            "Only when $\\lim a_n = 0$ must you proceed to other tests.\n\n"
            "**Common slip:**\n"
            "Trying the ratio test or p-series because the fraction \"looks complicated.\" "
            "The limit $\\frac{n}{n+1} \\to 1$ is visible without any test beyond basic limits.\n\n"
            "**Exam tip:**\n"
            "The question explicitly asks for the divergence test — show the limit calculation: "
            "$\\lim_{n\\to\\infty} \\frac{n}{n+1} = 1 \\neq 0$, conclude diverges. "
            "Skipping the limit loses the method mark even if your final answer is correct."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "מבחן הגבול בודק $\\lim_{n\\to\\infty} a_n$. כאן $a_n = \\frac{n}{n+1} \\to 1 \\neq 0$. "
            "כשהאיבר הכללי לא שואף לאפס, הסכומים החלקיים לא יכולים להתייצב לגבול סופי, "
            "ולכן $\\sum \\frac{n}{n+1}$ **מתבדר** לפי מבחן הגבול.\n\n"
            "**איך לחשוב על זה:**\n"
            "הפעילו תמיד מבחן הגבול ראשון — גבול אחד שיכול להוכיח התבדרות מיידית. "
            "אם $\\lim a_n = L \\neq 0$, חיבור אינסוף איברים קרובים ל-$L$ מתפוצץ. "
            "רק כש-$\\lim a_n = 0$ ממשיכים למבחנים אחרים.\n\n"
            "**טעות נפוצה:**\n"
            "לנסות מבחן מנה או p כי השבר \"נראה מסובך.\" הגבול $\\frac{n}{n+1} \\to 1$ ברור בלי מבחנים נוספים.\n\n"
            "**טיפ לבחינה:**\n"
            "השאלה מבקשת במפורש מבחן הגבול — הציגו את חישוב הגבול: "
            "$\\lim_{n\\to\\infty} \\frac{n}{n+1} = 1 \\neq 0$, מסקנה: מתבדר. "
            "דילוג על הגבול מוריד נקודת שיטה גם כשהתשובה הסופית נכונה."
        ),
    },
    4: {
        "en": (
            "**Why this is correct:**\n"
            "$\\sum_{n=1}^{\\infty} \\left(\\frac{1}{3}\\right)^n$ is a geometric series with first term "
            "$a = \\frac{1}{3}$ and ratio $r = \\frac{1}{3}$. Since $|r| = \\frac{1}{3} < 1$, it **converges**. "
            "The sum from $n = 1$ is $\\frac{a}{1-r} = \\frac{1/3}{2/3} = \\frac{1}{2}$.\n\n"
            "**How to think about it:**\n"
            "Exponential decay $(1/3)^n$ shrinks fast enough for an infinite sum to stay finite. "
            "You can also apply the ratio test: $\\left|\\frac{a_{n+1}}{a_n}\\right| = \\frac{1}{3} < 1$. "
            "Geometric recognition is faster when the form is obvious.\n\n"
            "**Common slip:**\n"
            "Using the formula starting at $n = 0$: $\\sum_{n=0}^{\\infty} r^n = \\frac{1}{1-r}$, which gives "
            "$\\frac{3}{2}$ instead of $\\frac{1}{2}$. Check the index of the first term.\n\n"
            "**Exam tip:**\n"
            "When $|r| < 1$, state convergence first, then optionally compute the sum. "
            "If the question only asks \"does it converge?\", naming the geometric test with $r = 1/3 < 1$ is sufficient."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "$\\sum_{n=1}^{\\infty} \\left(\\frac{1}{3}\\right)^n$ הוא טור הנדסי עם איבר ראשון "
            "$a = \\frac{1}{3}$ ומנה $r = \\frac{1}{3}$. מכיוון $|r| = \\frac{1}{3} < 1$, הוא **מתכנס**. "
            "הסכום מ-$n = 1$ הוא $\\frac{a}{1-r} = \\frac{1/3}{2/3} = \\frac{1}{2}$.\n\n"
            "**איך לחשוב על זה:**\n"
            "דעיכה אקסponנציאלית $(1/3)^n$ מתכווצת מספיק כדי שהסכום האינסופי יישאר סופי. "
            "אפשר גם מבחן מנה: $\\left|\\frac{a_{n+1}}{a_n}\\right| = \\frac{1}{3} < 1$. "
            "זיהוי הנדסי מהיר יותר כשהצורה ברורה.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש בנוסחה מ-$n = 0$: $\\sum_{n=0}^{\\infty} r^n = \\frac{1}{1-r}$, שנותן "
            "$\\frac{3}{2}$ במקום $\\frac{1}{2}$. בדקו את אינדקס האיבר הראשון.\n\n"
            "**טיפ לבחינה:**\n"
            "כש-$|r| < 1$, ציינו התכנסות קודם, ואז (אופציונלי) חשבו סכום. "
            "אם שואלים רק \"האם מתכנס?\", מספיק לציין טור הנדסי עם $r = 1/3 < 1$."
        ),
    },
    5: {
        "en": (
            "**Why this is correct:**\n"
            "For $a_n = \\frac{n^2}{2^n}$, the ratio test gives\n"
            "$$\\frac{a_{n+1}}{a_n} = \\frac{(n+1)^2}{2^{n+1}} \\cdot \\frac{2^n}{n^2} = \\frac{(n+1)^2}{2n^2} \\to \\frac{1}{2}.$$"
            "So $L = \\frac{1}{2} < 1$, and the series **converges absolutely** by the ratio test. "
            "Exponential $2^n$ in the denominator dominates polynomial $n^2$ in the numerator.\n\n"
            "**How to think about it:**\n"
            "Ratio test is the default when $a_n$ mixes polynomials with $r^n$ or factorials. "
            "After simplifying, compare growth rates: exponentials beat any fixed power of $n$.\n\n"
            "**Common slip:**\n"
            "Forgetting the $2^{n+1}$ in the denominator when forming $a_{n+1}/a_n$, leaving an extra factor of 2. "
            "Write $a_{n+1}$ and $a_n$ on separate lines before dividing.\n\n"
            "**Exam tip:**\n"
            "Report $L$ explicitly and compare to 1: \"$L = 1/2 < 1$, converges.\" "
            "Partial credit is awarded for correct setup of the ratio even if the limit arithmetic has a minor error."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "עבור $a_n = \\frac{n^2}{2^n}$, מבחן המנה נותן\n"
            "$$\\frac{a_{n+1}}{a_n} = \\frac{(n+1)^2}{2^{n+1}} \\cdot \\frac{2^n}{n^2} = \\frac{(n+1)^2}{2n^2} \\to \\frac{1}{2}.$$"
            "לכן $L = \\frac{1}{2} < 1$, והטור **מתכנס בהחלט** לפי מבחן המנה. "
            "האקסponנציאל $2^n$ במכנה שולט על הפולינום $n^2$ במונה.\n\n"
            "**איך לחשוב על זה:**\n"
            "מבחן המנה הוא ברירת המחדל כש-$a_n$ מערב פולינומים עם $r^n$ או עצרות. "
            "אחרי פישוט, השוו קצבי גדילה: אקסponנציאל מנצח כל חזקה קבועה של $n$.\n\n"
            "**טעות נפוצה:**\n"
            "שכחת $2^{n+1}$ במכנה בבניית $a_{n+1}/a_n$, מה שמשאיר גורם 2 מיותר. "
            "כתבו $a_{n+1}$ ו-$a_n$ בשורות נפרדות לפני החילוק.\n\n"
            "**טיפ לבחינה:**\n"
            "דווחו על $L$ במפורש והשוו ל-1: \"$L = 1/2 < 1$, מתכנס.\" "
            "נקודות חלקיות על הגדרה נכונה של המנה גם אם יש טעת חישוב קטנה בגבול."
        ),
    },
    6: {
        "en": (
            "**Why this is correct:**\n"
            "For large $n$, the dominant behavior of $a_n = \\frac{3n^2+1}{n^4-2}$ is $\\frac{3n^2}{n^4} = \\frac{3}{n^2}$. "
            "Compare with $b_n = \\frac{1}{n^2}$. Then\n"
            "$$\\lim_{n\\to\\infty} \\frac{a_n}{b_n} = \\lim_{n\\to\\infty} \\frac{3n^2+1}{n^4-2} \\cdot n^2 = 3 \\in (0, \\infty).$$"
            "Since $\\sum \\frac{1}{n^2}$ converges ($p = 2 > 1$), limit comparison implies $\\sum a_n$ **converges**.\n\n"
            "**How to think about it:**\n"
            "Pick a benchmark p-series by reading the highest powers in numerator and denominator. "
            "Lower-order terms and constants do not affect the limit ratio when $L$ is finite and positive.\n\n"
            "**Common slip:**\n"
            "Choosing $b_n = 1/n$ instead of $1/n^2$ because the numerator has $n^2$. "
            "The denominator's $n^4$ dominates, giving effective degree $-2$, not $-1$.\n\n"
            "**Exam tip:**\n"
            "Write your chosen $b_n$, compute $L$, cite the known convergence of $\\sum b_n$, then conclude. "
            "Three explicit lines — benchmark, limit, conclusion — match the rubric on most Israeli calculus exams."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "ל-$n$ גדול, ההתנהגות הדומיננטית של $a_n = \\frac{3n^2+1}{n^4-2}$ היא $\\frac{3n^2}{n^4} = \\frac{3}{n^2}$. "
            "השוו ל-$b_n = \\frac{1}{n^2}$. אז\n"
            "$$\\lim_{n\\to\\infty} \\frac{a_n}{b_n} = \\lim_{n\\to\\infty} \\frac{3n^2+1}{n^4-2} \\cdot n^2 = 3 \\in (0, \\infty).$$"
            "מכיוון ש-$\\sum \\frac{1}{n^2}$ מתכנס ($p = 2 > 1$), השוואת גבולות מסיקה ש-$\\sum a_n$ **מתכנס**.\n\n"
            "**איך לחשוב על זה:**\n"
            "בחרו אמת מידה מטור p על ידי קריאת החזקות הגבוהות במונה ובמכנה. "
            "איברים ממדרג נמוך וקבועים לא משנים את יחס הגבול כש-$L$ סופי וחיובי.\n\n"
            "**טעות נפוצה:**\n"
            "בחירת $b_n = 1/n$ במקום $1/n^2$ כי במונה יש $n^2$. "
            "המכנה $n^4$ שולט, ונותן מדרגה אפקטיבית $-2$, לא $-1$.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו את $b_n$ שבחרתם, חשבו $L$, צטטו התכנסות ידועה של $\\sum b_n$, וסיימו במסקנה. "
            "שלוש שורות מפורשות — אמת מידה, גבול, מסקנה — תואמות את הרובריקה ברוב בחינות החשבון."
        ),
    },
    7: {
        "en": (
            "**Why this is correct:**\n"
            "Let $f(x) = \\frac{1}{x \\ln x}$ for $x \\geq 2$. Then $f$ is positive, continuous, and decreasing, "
            "and $f(n) = a_n$. The integral test links series and integral:\n"
            "$$\\int_2^{\\infty} \\frac{dx}{x \\ln x} = \\lim_{b\\to\\infty} \\big[\\ln(\\ln x)\\big]_2^b = \\infty.$$"
            "The improper integral diverges, so $\\sum_{n=2}^{\\infty} \\frac{1}{n \\ln n}$ **diverges**.\n\n"
            "**How to think about it:**\n"
            "Integral test works when $a_n = f(n)$ with an easy antiderivative. "
            "Substitution $u = \\ln x$ gives $du = dx/x$ — the classic $\\int du/u$ pattern.\n\n"
            "**Common slip:**\n"
            "Evaluating $\\ln(\\ln 2)$ as zero or forgetting that $\\ln(\\ln x) \\to \\infty$ as $x \\to \\infty$. "
            "The outer logarithm grows without bound, so the integral diverges.\n\n"
            "**Exam tip:**\n"
            "Verify all three hypotheses (positive, continuous, decreasing) in one line before integrating. "
            "Examiners deduct if you jump to the antiderivative without stating the integral test applies."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "נסמן $f(x) = \\frac{1}{x \\ln x}$ עבור $x \\geq 2$. אז $f$ חיובית, רציפה ויורדת, "
            "ו-$f(n) = a_n$. מבחן האינטגרל מקשר טור ואינטגרל:\n"
            "$$\\int_2^{\\infty} \\frac{dx}{x \\ln x} = \\lim_{b\\to\\infty} \\big[\\ln(\\ln x)\\big]_2^b = \\infty.$$"
            "האינטגרל המוכלל מתבדר, ולכן $\\sum_{n=2}^{\\infty} \\frac{1}{n \\ln n}$ **מתבדר**.\n\n"
            "**איך לחשוב על זה:**\n"
            "מבחן האינטגרל מתאים כש-$a_n = f(n)$ עם פונקציה ראשונית פשוטה. "
            "הצבה $u = \\ln x$ נותנת $du = dx/x$ — תבנית $\\int du/u$ קלאסית.\n\n"
            "**טעות נפוצה:**\n"
            "הערכת $\\ln(\\ln 2)$ כאפס, או שכחה ש-$\\ln(\\ln x) \\to \\infty$ כש-$x \\to \\infty$. "
            "הלוגריתם החיצוני גדל ללא גבול, ולכן האינטגרל מתבדר.\n\n"
            "**טיפ לבחינה:**\n"
            "אמתו את שלוש ההנחות (חיובית, רציפה, יורדת) בשורה אחת לפני האינטגרציה. "
            "בודקים מורידים נקודות אם קופצים לפונקציה ראשונית בלי לציין שמבחן האינטגרל חל."
        ),
    },
    8: {
        "en": (
            "**Why this is correct:**\n"
            "The term $a_n = \\left(\\frac{n}{2n+1}\\right)^n$ has the form $(f(n))^n$, so the root test is natural:\n"
            "$$\\sqrt[n]{|a_n|} = \\frac{n}{2n+1} \\to \\frac{1}{2} \\quad \\text{as } n \\to \\infty.$$"
            "Thus $L = \\frac{1}{2} < 1$, and the series **converges absolutely** by the root test.\n\n"
            "**How to think about it:**\n"
            "When the entire term is raised to the $n$th power, the $n$th root collapses the exponent immediately. "
            "The ratio test would also work but requires more algebra; root test is the efficient choice.\n\n"
            "**Common slip:**\n"
            "Taking $\\lim \\frac{n}{2n+1} = \\frac{1}{2}$ but forgetting to compare $L$ to 1, "
            "or confusing root test with ratio test and computing $a_{n+1}/a_n$ instead.\n\n"
            "**Exam tip:**\n"
            "State: \"$L = \\lim \\sqrt[n]{|a_n|} = 1/2 < 1$, converges by root test.\" "
            "If $L$ were exactly 1, you would need a different test — root and ratio are inconclusive at the boundary."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "האיבר $a_n = \\left(\\frac{n}{2n+1}\\right)^n$ בצורה $(f(n))^n$, ולכן מבחן השורש מתאים:\n"
            "$$\\sqrt[n]{|a_n|} = \\frac{n}{2n+1} \\to \\frac{1}{2} \\quad \\text{כאשר } n \\to \\infty.$$"
            "לכן $L = \\frac{1}{2} < 1$, והטור **מתכנס בהחלט** לפי מבחן השורש.\n\n"
            "**איך לחשוב על זה:**\n"
            "כשכל האיבר מועלה בחזקת $n$, שורש ה-$n$ מקרי את המעריך מיד. "
            "מבחן המנה גם יעבוד אך דורש יותר אלגebra; מבחן השורש הוא הבחירה היעילה.\n\n"
            "**טעות נפוצה:**\n"
            "לקחת $\\lim \\frac{n}{2n+1} = \\frac{1}{2}$ אך לשכוח להשוות $L$ ל-1, "
            "או לבלבל עם מבחן המנה ולחשב $a_{n+1}/a_n$ במקום.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו: \"$L = \\lim \\sqrt[n]{|a_n|} = 1/2 < 1$, מתכנס לפי מבחן השורש.\" "
            "אם $L$ היה בדיוק 1, הייתם צריכים מבחן אחר — מבחן שורש ומנה לא מכריעים על הגבול."
        ),
    },
}


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    # --- intro ---
    data["sections"][0]["body_en_md"] = (
        "An **infinite series** $\\sum_{n=1}^{\\infty} a_n$ asks a deceptively simple question: "
        "can we add infinitely many numbers and obtain a finite total? The answer is sometimes yes "
        "(Basel problem: $\\sum 1/n^2 = \\pi^2/6$) and sometimes no (harmonic series $\\sum 1/n$ diverges). "
        "Knowing **which** is which is central to calculus, physics, and engineering.\n\n"
        "Series appear everywhere in university math: **Taylor series** represent functions as infinite polynomials, "
        "**Fourier series** decompose signals, and **power series** define solutions to differential equations. "
        "Every convergence claim in those tools rests on the tests you learn here — you cannot safely use "
        "$\\sum_{n=0}^{\\infty} \\frac{x^n}{n!} = e^x$ without knowing that the series converges for all $x$.\n\n"
        "No single test works for every series. This lesson builds your **toolkit** of eight convergence tests "
        "plus a decision strategy for choosing the right one. Mastering test selection — not just memorizing formulas — "
        "is what separates exam-ready students from those who stall on \"$L = 1$, now what?\""
    )
    data["sections"][0]["body_he_md"] = (
        "**טור אינסופי** $\\sum_{n=1}^{\\infty} a_n$ שואל שאלה פשוטה לכאורה: "
        "האם ניתן לחבר אינסוף מספרים ולקבל סכום סופי? התשובה לפעמים כן "
        "(בעיית באזל: $\\sum 1/n^2 = \\pi^2/6$) ולפעמים לא (הטור ההרמוני $\\sum 1/n$ מתבדר). "
        "לדעת **מתי** כל מקרה — מרכזי בחשבון, בפיזיקה ובהנדסה.\n\n"
        "טורים מופיעים בכל מקום במתמטיקה אוניברסיטאית: **טורי טיילור** מייצגים פונקציות כפולינומים אינסופיים, "
        "**טורי פורייה** מפרקים אותות, ו**טורי חזקות** מגדירים פתרונות למשוואות דיפרנציאליות. "
        "כל טענה על התכנסות בכלים אלה נשענת על המבחנים שלמדים כאן — אי אפשר להשתמש בבטחון ב-"
        "$\\sum_{n=0}^{\\infty} \\frac{x^n}{n!} = e^x$ בלי לדעת שהטור מתכנס לכל $x$.\n\n"
        "אין מבחן אחד שעובד לכל הטורים. שיעור זה בונה **ארגז כלים** של שמונה מבחני התכנסות "
        "ועם אסטרטגיית בחירה. שליטה בבחירת המבחן — לא רק שינון נוסחאות — "
        "מבדילה בין סטודנטים מוכנים לבחינה לבין אלה שנתקעים על \"$L = 1$, ועכשיו מה?\""
    )

    # --- definition (expand slightly for HE parity) ---
    data["sections"][1]["body_en_md"] = (
        "**Partial sums.** For $\\sum_{n=1}^{\\infty} a_n$, define $S_N = \\sum_{n=1}^N a_n$. "
        "The series **converges** if $\\lim_{N\\to\\infty} S_N = L$ (finite); otherwise it **diverges**.\n\n"
        "**Test 1 — Divergence Test (nth-term test).** If $\\lim_{n\\to\\infty} a_n \\neq 0$ (or the limit does not exist), "
        "the series diverges. If $\\lim_{n\\to\\infty} a_n = 0$, the test is **inconclusive** — you must try another test.\n\n"
        "**Test 2 — Integral Test.** If $f$ is positive, continuous, and decreasing on $[1,\\infty)$ with $f(n)=a_n$, "
        "then $\\sum a_n$ and $\\int_1^{\\infty} f(x)\\,dx$ both converge or both diverge.\n\n"
        "**Test 3 — p-Series.** $\\sum_{n=1}^{\\infty} \\frac{1}{n^p}$ converges if and only if $p > 1$.\n\n"
        "**Test 4 — Direct Comparison.** If $0 \\leq a_n \\leq b_n$ for all sufficiently large $n$: "
        "if $\\sum b_n$ converges then $\\sum a_n$ converges; if $\\sum a_n$ diverges then $\\sum b_n$ diverges.\n\n"
        "**Test 5 — Limit Comparison.** If $a_n, b_n > 0$ and $\\lim_{n\\to\\infty} \\frac{a_n}{b_n} = L$ with $0 < L < \\infty$, "
        "then $\\sum a_n$ and $\\sum b_n$ share the same convergence behavior.\n\n"
        "**Test 6 — Ratio Test.** Let $L = \\lim_{n\\to\\infty} \\left|\\frac{a_{n+1}}{a_n}\\right|$. "
        "If $L < 1$: converges absolutely. If $L > 1$: diverges. If $L = 1$: inconclusive.\n\n"
        "**Test 7 — Root Test.** Let $L = \\lim_{n\\to\\infty} \\sqrt[n]{|a_n|}$. Same three-way conclusion as the ratio test.\n\n"
        "**Test 8 — Alternating Series (Leibniz).** For $\\sum (-1)^{n+1} b_n$ with $b_n > 0$: "
        "converges if $b_n$ is decreasing and $\\lim_{n\\to\\infty} b_n = 0$.\n\n"
        "**Absolute vs conditional convergence.** $\\sum a_n$ is **absolutely convergent** if $\\sum |a_n|$ converges "
        "(which implies $\\sum a_n$ converges). It is **conditionally convergent** if $\\sum a_n$ converges but $\\sum |a_n|$ diverges."
    )
    data["sections"][1]["body_he_md"] = (
        "**סכומים חלקיים.** עבור $\\sum_{n=1}^{\\infty} a_n$, נגדיר $S_N = \\sum_{n=1}^N a_n$. "
        "הטור **מתכנס** אם $\\lim_{N\\to\\infty} S_N = L$ (סופי); אחרת הוא **מתבדר**.\n\n"
        "**מבחן 1 — מבחן הגבול (nth-term).** אם $\\lim_{n\\to\\infty} a_n \\neq 0$ (או שהגבול לא קיים), "
        "הטור מתבדר. אם $\\lim_{n\\to\\infty} a_n = 0$, המבחן **לא מסייע** — יש לנסות מבחן אחר.\n\n"
        "**מבחן 2 — מבחן האינטגרל.** אם $f$ חיובית, רציפה ויורדת ב-$[1,\\infty)$ עם $f(n)=a_n$, "
        "אז $\\sum a_n$ ו-$\\int_1^{\\infty} f(x)\\,dx$ שניהם מתכנסים או שניהם מתבדרים.\n\n"
        "**מבחן 3 — טורי p.** $\\sum_{n=1}^{\\infty} \\frac{1}{n^p}$ מתכנס אם ורק אם $p > 1$.\n\n"
        "**מבחן 4 — השוואה ישירה.** אם $0 \\leq a_n \\leq b_n$ לכל $n$ גדול מספיק: "
        "$\\sum b_n$ מתכנס $\\Rightarrow$ $\\sum a_n$ מתכנס; $\\sum a_n$ מתבדר $\\Rightarrow$ $\\sum b_n$ מתבדר.\n\n"
        "**מבחן 5 — השוואת גבולות.** אם $a_n, b_n > 0$ ו-$\\lim_{n\\to\\infty} \\frac{a_n}{b_n} = L \\in (0,\\infty)$, "
        "לשני הטורים אותו גורל התכנסות.\n\n"
        "**מבחן 6 — מבחן המנה.** $L = \\lim\\left|\\frac{a_{n+1}}{a_n}\\right|$. $L<1$: מתכנס בהחלט. $L>1$: מתבדר. $L=1$: לא מכריע.\n\n"
        "**מבחן 7 — מבחן השורש.** $L = \\lim \\sqrt[n]{|a_n|}$. אותה מסקנה תלת-כיוונית כמו במבחן המנה.\n\n"
        "**מבחן 8 — לייבניץ (מתחלפים).** עבור $\\sum (-1)^{n+1} b_n$ עם $b_n > 0$: "
        "מתכנס אם $b_n$ יורד ו-$\\lim_{n\\to\\infty} b_n = 0$.\n\n"
        "**התכנסות מוחלטת לעומת מותנית.** $\\sum a_n$ **מתכנס בהחלט** אם $\\sum |a_n|$ מתכנס "
        "(ומשתמע מכך $\\sum a_n$ מתכנס). **מותנית** אם $\\sum a_n$ מתכנס אך $\\sum |a_n|$ מתבדר."
    )

    # --- theory ---
    data["sections"][2]["body_en_md"] = (
        "**Ratio test and factorials/exponentials.** The ratio test shines when $a_n$ involves $n!$ or $r^n$: "
        "these factors cancel cleanly in $a_{n+1}/a_n$. Stirling's approximation $n! \\approx (n/e)^n\\sqrt{2\\pi n}$ "
        "explains why factorials lose to exponentials with base $> e$.\n\n"
        "**Root test and $n$th powers.** When $a_n = (f(n))^n$, the root test collapses the power in one step: "
        "$\\sqrt[n]{|a_n|} = |f(n)|$. Use this instead of the ratio test when the entire term is raised to the $n$th power.\n\n"
        "**p-series as the benchmark.** The most common strategy for rational terms in $n$ is: "
        "identify the effective power $p$ (highest degree in denominator minus numerator) and compare with $\\sum 1/n^p$ "
        "via limit comparison.\n\n"
        "**Alternating series caution.** Leibniz proves convergence but NOT absolute convergence. "
        "Always test $\\sum |a_n|$ separately — e.g. $\\sum (-1)^n/\\sqrt{n}$ converges by Leibniz but "
        "$\\sum 1/\\sqrt{n}$ diverges ($p = 1/2$), so convergence is conditional.\n\n"
        "**Divergence test is never enough for convergence.** $a_n \\to 0$ is necessary but not sufficient: "
        "the harmonic series has $a_n \\to 0$ yet diverges. When the divergence test is inconclusive, "
        "the real work begins — and $L = 1$ in the ratio/root tests creates the same \"inconclusive\" pause."
    )
    data["sections"][2]["body_he_md"] = (
        "**מבחן המנה ועצרות/חזקות.** המבחן מצטיין כש-$a_n$ כולל $n!$ או $r^n$: "
        "גורמים אלה מתבטלים יפה ב-$a_{n+1}/a_n$. קירוב סטירלינג $n! \\approx (n/e)^n\\sqrt{2\\pi n}$ "
        "מסביר מדוע עצרות מפסידות לאקסponנציאל עם בסיס $> e$.\n\n"
        "**מבחן השורש וחזקות ה-$n$.** כש-$a_n = (f(n))^n$, מבחן השורש מקרי את החזקה בצעד אחד: "
        "$\\sqrt[n]{|a_n|} = |f(n)|$. השתמשו בו במקום מבחן המנה כשכל האיבר מועלה בחזקת $n$.\n\n"
        "**טורי p כאמת מידה.** האסטרטגיה הנפוצה לביטויים רציונליים ב-$n$: "
        "זיהוי המדרגה האפקטивית $p$ (מכנה פחות מונה) והשוואה ל-$\\sum 1/n^p$ בהשוואת גבולות.\n\n"
        "**אזהרת טורים מתחלפים.** לייבניץ מוכיח התכנסות אך לא התכנסות מוחלטת. "
        "תמיד בדקו $\\sum |a_n|$ בנפרד — למשל $\\sum (-1)^n/\\sqrt{n}$ מתכנס בלייבניץ אך "
        "$\\sum 1/\\sqrt{n}$ מתבדר ($p = 1/2$), כלומר ההתכנסות מותנית.\n\n"
        "**מבחן הגבול לעולם לא מספיק להוכחת התכנסות.** $a_n \\to 0$ הכרחי אך לא מספיק: "
        "הטור ההרמוני שואף לאפס ומתבדר. כשמבחן הגבול לא מסייע, העבודה האמיתית מתחילה — "
        "ו-$L = 1$ במבחני מנה/שורש יוצר את אותה \"הפסקה\" לא מכריעה."
    )

    # --- worked example 1 ---
    data["sections"][3]["body_en_md"] = (
        "**Does $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2}$ converge?**\n\n"
        "This is the Basel problem — one of the most famous convergent series. "
        "We will classify it using the standard exam workflow: divergence test first, then p-series.\n\n"
        "### Move 1 — Divergence test\n"
        "$a_n = 1/n^2 \\to 0$. The test is **inconclusive** — terms going to zero does not prove convergence.\n\n"
        "### Move 2 — Recognize the form\n"
        "The series is $\\sum \\frac{1}{n^p}$ with $p = 2$.\n\n"
        "### Move 3 — p-Series test\n"
        "Since $p = 2 > 1$, the series **converges**.\n\n"
        "### Move 4 — Known sum (bonus)\n"
        "Euler showed $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$. "
        "We proved convergence without needing the exact value — classification and summation are separate skills.\n\n"
        "**Conclusion:** $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2}$ **converges** (p-series, $p = 2 > 1$).\n\n"
        "**Sanity check:** Compare with $\\sum 1/n$ (diverges, $p=1$) and $\\sum 1/n^3$ (converges, $p=3$). "
        "Our series sits between them with $p=2$, consistent with convergence. "
        "On exams, write the p-value explicitly before stating the conclusion."
    )
    data["sections"][3]["body_he_md"] = (
        "**האם $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2}$ מתכנס?**\n\n"
        "זו בעיית באזל — אחד הטורים המתכנסים המפורסמים ביותר. "
        "נסווג אותו לפי תבנית הבחינה: מבחן הגבול תחילה, ואז טור p.\n\n"
        "### צעד 1 — מבחן הגבול\n"
        "$a_n = 1/n^2 \\to 0$. המבחן **לא מסייע** — שאיפה לאפס לא מוכיחה התכנסות.\n\n"
        "### צעד 2 — זיהוי הצורה\n"
        "הטור הוא $\\sum \\frac{1}{n^p}$ עם $p = 2$.\n\n"
        "### צעד 3 — מבחן טורי p\n"
        "מכיוון ש-$p = 2 > 1$, הטור **מתכנס**.\n\n"
        "### צעד 4 — סכום ידוע (בונוס)\n"
        "אוילר הראה $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$. "
        "הוכחנו התכנסות בלי הערך המדויק — סיווג וחישוב סכום הם מיומנויות נפרדות.\n\n"
        "**סיכום:** $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^2}$ **מתכנס** (טור p, $p = 2 > 1$).\n\n"
        "**בדיקת הגיון:** השוו ל-$\\sum 1/n$ (מתבדר, $p=1$) ול-$\\sum 1/n^3$ (מתכנס, $p=3$). "
        "הטור שלנו ביניהם עם $p=2$, עקבי עם התכנסות."
    )

    # --- checkpoint 1 ---
    data["sections"][4]["body_he_md"] = (
        "קבעו אם כל טור מתכנס או מתבדר על ידי מבחן טורי p:\n\n"
        "(א) $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{n^{3/2}}$   (ב) $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{1}{\\sqrt{n}}$"
    )
    data["sections"][4]["checkpoint_solution_en"] = (
        "**(a)** $\\sum \\frac{1}{n^{3/2}} = \\sum \\frac{1}{n^p}$ with $p = 3/2$. "
        "Since $p = 3/2 > 1$, the p-series test gives **converges**.\n\n"
        "**(b)** $\\sum \\frac{1}{\\sqrt{n}} = \\sum \\frac{1}{n^{1/2}}$ with $p = 1/2$. "
        "Since $p = 1/2 < 1$, the p-series test gives **diverges**.\n\n"
        "**Self-check:** (a) terms shrink faster than $1/n$ (which diverges); (b) slower than $1/n^2$ (which converges)."
    )
    data["sections"][4]["checkpoint_solution_he"] = (
        "**(א)** $\\sum \\frac{1}{n^{3/2}} = \\sum \\frac{1}{n^p}$ עם $p = 3/2$. "
        "מכיוון $p = 3/2 > 1$, מבחן טורי p: **מתכנס**.\n\n"
        "**(ב)** $\\sum \\frac{1}{\\sqrt{n}} = \\sum \\frac{1}{n^{1/2}}$ עם $p = 1/2$. "
        "מכיוון $p = 1/2 < 1$, מבחן טורי p: **מתבדר**.\n\n"
        "**בדיקה:** (א) האיברים קטנים מהר מ-$1/n$ (שמתבדר); (ב) לאט מ-$1/n^2$ (שמתכנס)."
    )

    # --- worked example 2 ---
    data["sections"][5]["body_en_md"] = (
        "**Does $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{n!}{n^n}$ converge?**\n\n"
        "Factorials in the numerator suggest the ratio test. We first check the divergence test, "
        "then compute $L = \\lim |a_{n+1}/a_n|$.\n\n"
        "### Move 1 — Divergence test\n"
        "$a_n = n!/n^n$. By Stirling, $a_n \\approx (1/e)^n \\sqrt{2\\pi n} \\to 0$. Inconclusive.\n\n"
        "### Move 2 — Choose the ratio test\n"
        "Factorial structure in $a_n$ is the standard signal for the ratio test.\n\n"
        "### Move 3 — Compute the ratio\n"
        "$$\\frac{a_{n+1}}{a_n} = \\frac{(n+1)!}{(n+1)^{n+1}} \\cdot \\frac{n^n}{n!} = \\frac{n^n}{(n+1)^n}.$$\n\n"
        "### Move 4 — Evaluate the limit\n"
        "$$L = \\lim_{n\\to\\infty} \\left(\\frac{n}{n+1}\\right)^n = \\lim_{n\\to\\infty} \\left(1 - \\frac{1}{n+1}\\right)^n = e^{-1} = \\frac{1}{e}.$$\n\n"
        "### Move 5 — Conclusion\n"
        "$L = 1/e < 1$. By the ratio test, the series **converges absolutely**.\n\n"
        "**Exam note:** Exponentials with base $e$ beat factorial growth — a recurring theme in Calc II series problems.\n\n"
        "**Alternative check:** Limit comparison with $\\sum (1/e)^n$ (geometric, $|r|=1/e<1$) also shows convergence, "
        "confirming the ratio-test answer from a different angle. "
        "Both tests agree because factorial decay is slower than exponential decay with base $1/e$."
    )
    data["sections"][5]["body_he_md"] = (
        "**האם $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{n!}{n^n}$ מתכנס?**\n\n"
        "עצרות במונה מרמזות על מבחן המנה. נבדוק תחילה מבחן הגבול, "
        "ואז נחשב $L = \\lim |a_{n+1}/a_n|$.\n\n"
        "### צעד 1 — מבחן הגבול\n"
        "$a_n = n!/n^n$. לפי סטירלינג, $a_n \\approx (1/e)^n \\sqrt{2\\pi n} \\to 0$. לא מסייע.\n\n"
        "### צעד 2 — בחירת מבחן המנה\n"
        "מבנה עצרת ב-$a_n$ הוא הסימן הסטנדרטי למבחן המנה.\n\n"
        "### צעד 3 — חישוב המנה\n"
        "$$\\frac{a_{n+1}}{a_n} = \\frac{(n+1)!}{(n+1)^{n+1}} \\cdot \\frac{n^n}{n!} = \\frac{n^n}{(n+1)^n}.$$\n\n"
        "### צעד 4 — חישוב הגבול\n"
        "$$L = \\lim_{n\\to\\infty} \\left(\\frac{n}{n+1}\\right)^n = e^{-1} = \\frac{1}{e}.$$\n\n"
        "### צעד 5 — מסקנה\n"
        "$L = 1/e < 1$. לפי מבחן המנה, הטור **מתכנס בהחלט**.\n\n"
        "**הערה לבחינה:** אקסponנציאל עם בסיס $e$ מנצח גידול עצרת — נושא חוזר בבעיות טורים בחשבון 2.\n\n"
        "**בדיקה חלופית:** השוואת גבולות עם $\\sum (1/e)^n$ (הנדסי, $|r|=1/e<1$) גם מראה התכנסות, "
        "ומאשרת את תשובת מבחן המנה מזווית אחרת. "
        "שני המבחנים מסכימים כי דעיכת עצרת איטית מדעיכה אקסponנציאלית עם בסיס $1/e$."
    )

    # --- checkpoint 2 ---
    data["sections"][6]["checkpoint_solution_en"] = (
        "**Step 1 — Set up the ratio:** $a_n = 2^n / n!$, so\n"
        "$$\\frac{a_{n+1}}{a_n} = \\frac{2^{n+1}}{(n+1)!} \\cdot \\frac{n!}{2^n} = \\frac{2}{n+1}.$$\n\n"
        "**Step 2 — Limit:** $L = \\lim_{n\\to\\infty} \\frac{2}{n+1} = 0$.\n\n"
        "**Step 3 — Conclusion:** Since $L = 0 < 1$, the series **converges absolutely** by the ratio test. "
        "Factorial in the denominator dominates the exponential numerator."
    )
    data["sections"][6]["checkpoint_solution_he"] = (
        "**שלב 1 — הגדרת המנה:** $a_n = 2^n / n!$, לכן\n"
        "$$\\frac{a_{n+1}}{a_n} = \\frac{2^{n+1}}{(n+1)!} \\cdot \\frac{n!}{2^n} = \\frac{2}{n+1}.$$\n\n"
        "**שלב 2 — גבול:** $L = \\lim_{n\\to\\infty} \\frac{2}{n+1} = 0$.\n\n"
        "**שלב 3 — מסקנה:** מכיוון $L = 0 < 1$, הטור **מתכנס בהחלט** לפי מבחן המנה. "
        "העצרת במכנה שולטת על האקסponנציאל במונה."
    )

    # --- worked example 3 ---
    data["sections"][7]["body_en_md"] = (
        "**Show that $\\displaystyle\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{\\sqrt{n}}$ is conditionally convergent.**\n\n"
        "Alternating series require a two-part analysis: prove convergence with Leibniz, "
        "then test absolute convergence separately.\n\n"
        "**Part A — Convergence (Leibniz test).**\n\n"
        "Write $\\sum (-1)^n b_n$ with $b_n = 1/\\sqrt{n} > 0$.\n"
        "- **Condition 1:** $b_n = 1/\\sqrt{n}$ is strictly decreasing ($\\sqrt{n}$ increases).\n"
        "- **Condition 2:** $\\lim_{n\\to\\infty} b_n = 0$.\n\n"
        "Both hold, so by the **Alternating Series Test**, the series **converges**.\n\n"
        "**Part B — Absolute convergence fails.**\n\n"
        "$\\displaystyle\\sum_{n=1}^{\\infty} \\left|\\frac{(-1)^n}{\\sqrt{n}}\\right| = \\sum_{n=1}^{\\infty} \\frac{1}{n^{1/2}}$ — "
        "a p-series with $p = 1/2 < 1$, so it **diverges**.\n\n"
        "**Conclusion:** The series **converges conditionally** — Leibniz gives convergence, "
        "but absolute convergence fails. Rearranging terms could change the sum (Riemann's theorem).\n\n"
        "**Exam tip:** Always report the three-way classification: absolute, conditional, or divergent.\n\n"
        "**Numerical preview:** Partial sums of the alternating series oscillate and shrink: "
        "$S_1=-1$, $S_2\\approx -0.293$, $S_3\\approx -0.871$, … approaching roughly $-0.82$. "
        "The limit exists (conditional convergence) even though absolute values sum to infinity."
    )
    data["sections"][7]["body_he_md"] = (
        "**הראה ש-$\\displaystyle\\sum_{n=1}^{\\infty} \\frac{(-1)^n}{\\sqrt{n}}$ מתכנס מותנית.**\n\n"
        "טורים מתחלפים דורשים ניתוח דו-שלבי: הוכחת התכנסות בלייבניץ, "
        "ואז בדיקת התכנסות מוחלטת בנפרד.\n\n"
        "**חלק א — התכנסות (לייבניץ).**\n\n"
        "כתבו $\\sum (-1)^n b_n$ עם $b_n = 1/\\sqrt{n} > 0$.\n"
        "- **תנאי 1:** $b_n = 1/\\sqrt{n}$ יורד קפדנית ($\\sqrt{n}$ עולה).\n"
        "- **תנאי 2:** $\\lim_{n\\to\\infty} b_n = 0$.\n\n"
        "שניהם מתקיימים, לכן לפי **מבחן לייבניץ** הטור **מתכנס**.\n\n"
        "**חלק ב — כישלון התכנסות מוחלטת.**\n\n"
        "$\\displaystyle\\sum \\frac{1}{n^{1/2}}$ — טור p עם $p = 1/2 < 1$, לכן **מתבדר**.\n\n"
        "**מסקנה:** הטור **מתכנס מותנית** — לייבניץ נותן התכנסות, "
        "אך התכנסות מוחלטת נכשלת. סידור מחדש עלול לשנות את הסכום (משפט רימן).\n\n"
        "**טיפ לבחינה:** דווחו תמיד על סיווג תלת-כיווני: מוחלטת, מותנית, או מתבדר.\n\n"
        "**תצוגה מקדימה מספרית:** סכומים חלקיים של הטור המתחלף מתנדנדים ומתכווצים: "
        "$S_1=-1$, $S_2\\approx -0.293$, $S_3\\approx -0.871$, … מתקרבים לכ-$-0.82$. "
        "הגבול קיים (התכנסות מותנית) גם כשערכים מוחלטים מסתכמים לאינסוף."
    )

    # --- method_guide (expand) ---
    data["sections"][8]["body_en_md"] = (
        "**Decision strategy (apply in order):**\n\n"
        "1. **First: Divergence test.** Is $\\lim a_n \\neq 0$? If yes → diverges. If no → continue.\n\n"
        "2. **Alternating series?** Does $a_n = (-1)^n b_n$ with $b_n > 0$? Apply Leibniz. "
        "Also test $\\sum b_n$ for absolute convergence.\n\n"
        "3. **Contains $n!$ or $a^n$?** Ratio test. (Especially when both appear.)\n\n"
        "4. **Contains $(f(n))^n$?** Root test.\n\n"
        "5. **Looks like $1/n^p$ (possibly with polynomial tweaks)?** p-Series directly, or limit comparison with $1/n^p$.\n\n"
        "6. **Can you bound it above/below by a known series?** Direct comparison.\n\n"
        "7. **Has an easy antiderivative?** Integral test.\n\n"
        "| Series form | Best test |\n|---|---|\n"
        "| $\\sum 1/n^p$ | p-Series |\n"
        "| $\\sum r^n$, $\\sum n!/n^n$ | Ratio |\n"
        "| $\\sum (f(n))^n$ | Root |\n"
        "| $\\sum (-1)^n b_n$ | Leibniz + $\\sum b_n$ |\n"
        "| Rational in $n$ | Limit comparison with $1/n^p$ |\n"
        "| $\\sum a_n \\leq \\sum b_n$ known | Direct comparison |\n"
        "| Easy antiderivative | Integral test |\n\n"
        "**When $L = 1$:** Switch tests — try limit comparison with a p-series benchmark. "
        "The ratio and root tests cannot distinguish $\\sum 1/n$ from $\\sum 1/n^2$."
    )
    data["sections"][8]["body_he_md"] = (
        "**אסטרטגיית החלטה (הפעל בסדר):**\n\n"
        "1. **ראשון: מבחן הגבול.** $\\lim a_n \\neq 0$? אם כן → מתבדר. אם לא → המשך.\n\n"
        "2. **טור מתחלף?** $a_n = (-1)^n b_n$ עם $b_n > 0$? הפעל לייבניץ. "
        "גם בדוק $\\sum b_n$ להתכנסות מוחלטית.\n\n"
        "3. **מכיל $n!$ או $a^n$?** מבחן המנה.\n\n"
        "4. **מכיל $(f(n))^n$?** מבחן השורש.\n\n"
        "5. **נראה כ-$1/n^p$?** טורי p, או השוואת גבולות עם $1/n^p$.\n\n"
        "6. **ניתן לחסום מעל/מתחת לטור ידוע?** השוואה ישירה.\n\n"
        "7. **יש פונקציה ראשונית פשוטה?** מבחן האינטגרל.\n\n"
        "| צורת הטור | המבחן הטוב ביותר |\n|---|---|\n"
        "| $\\sum 1/n^p$ | טורי p |\n"
        "| $\\sum r^n$, $\\sum n!/n^n$ | מנה |\n"
        "| $\\sum (f(n))^n$ | שורש |\n"
        "| $\\sum (-1)^n b_n$ | לייבניץ + $\\sum b_n$ |\n"
        "| רציונלי ב-$n$ | השוואת גבולות עם $1/n^p$ |\n"
        "| $\\sum a_n \\leq \\sum b_n$ | השוואה ישירה |\n"
        "| פונקציה ראשונית פשוטה | אינטגרל |\n\n"
        "**כש-$L = 1$:** החליפו מבחן — נסו השוואת גבולות עם אמת מידה מטור p. "
        "מבחני מנה ושורש לא מבחינים בין $\\sum 1/n$ ל-$\\sum 1/n^2$."
    )

    # --- pitfall (expand) ---
    idx_pitfall = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "pitfall")
    data["sections"][idx_pitfall]["body_en_md"] = (
        "1. **Misusing the divergence test.** If $\\lim a_n = 0$, the series MIGHT converge or diverge. "
        "The test only proves divergence, never convergence. Students who stop after $a_n \\to 0$ "
        "and declare \"converges\" lose marks on harmonic-type problems.\n\n"
        "2. **Ratio/root test when $L=1$.** When either test gives $L=1$, it is completely inconclusive. "
        "Many students incorrectly conclude convergence. You must switch to comparison or integral tests.\n\n"
        "3. **Confusing conditional and absolute convergence.** Proving $\\sum a_n$ converges (e.g., by Leibniz) "
        "does NOT prove absolute convergence. Always test $\\sum |a_n|$ separately and report the three-way classification.\n\n"
        "4. **Forgetting Leibniz conditions.** Both must hold: $b_n$ **decreasing** (not just $b_n \\to 0$) and $b_n > 0$. "
        "A sequence that oscillates toward zero may fail the decreasing requirement.\n\n"
        "5. **Wrong comparison direction.** In direct comparison, $a_n \\leq b_n$ with divergent $\\sum a_n$ "
        "does NOT imply $\\sum b_n$ diverges. You need a lower bound: $a_n \\geq c_n$ with divergent $\\sum c_n$."
    )
    data["sections"][idx_pitfall]["body_he_md"] = (
        "1. **שימוש שגוי במבחן הגבול.** $\\lim a_n = 0$ לא מוכיח התכנסות — הטור עלול להתכנס או להתבדר. "
        "המבחן מוכיח רק התבדרות. סטודנטים שעוצרים אחרי $a_n \\to 0$ ומכריזים \"מתכנס\" "
        "מאבדים נקודות בבעיות הרמוניות.\n\n"
        "2. **מבחן מנה/שורש כש-$L=1$.** $L=1$ לא מסייע כלל — חייבים מבחן אחר. "
        "תלמידים רבים טועים וסוגרים שהטור מתכנס. עברו להשוואה או לאינטגרל.\n\n"
        "3. **בלבול מוחלטת ומותנית.** הוכחת $\\sum a_n$ מתכנס (לייבניץ) לא מוכיחה התכנסות מוחלטת. "
        "תמיד בדקו $\\sum |a_n|$ בנפרד ודווחו על סיווג תלת-כיווני.\n\n"
        "4. **שכחת תנאי לייבניץ.** שני התנאים חייבים: $b_n$ **יורד** (לא רק $b_n\\to 0$) ו-$b_n > 0$. "
        "סדרה שמתנדנדת לכיוון אפס עלולה לא לעמוד בדרישת הירידה.\n\n"
        "5. **כיוון שגוי בהשוואה.** $a_n \\leq b_n$ עם $\\sum a_n$ מתבדר לא מסיק ש-$\\sum b_n$ מתבדר. "
        "צריך חסם מלרע: $a_n \\geq c_n$ עם $\\sum c_n$ מתבדר."
    )

    # --- why_matters ---
    idx_why = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "why_matters")
    data["sections"][idx_why]["body_en_md"] = (
        "Convergence tests are the gatekeeper for everything that follows in Calc II: "
        "power series, Taylor expansions, and Fourier analysis all assume you can prove a series converges "
        "before you differentiate or integrate it term-by-term.\n\n"
        "**Connection to `concept:series_convergence_advanced`:** Once you classify convergence here, "
        "the advanced lesson asks *how* series converge (absolute vs conditional) and finds intervals of convergence "
        "for $\\sum a_n (x-c)^n$.\n\n"
        "**Why it matters for exams:** Israeli Technion/HU/TAU calculus finals typically include 2–3 series "
        "classification problems worth 15–20 points combined. Partial credit goes to correct test identification "
        "even when the limit computation has an arithmetic slip.\n\n"
        "**Physics link:** Perturbation series in quantum mechanics and asymptotic expansions in engineering "
        "require knowing when an infinite sum represents a finite physical quantity — divergent series are not "
        "just mathematical curiosities; they signal a broken model."
    )
    data["sections"][idx_why]["body_he_md"] = (
        "מבחני התכנסות הם שער לכל מה שבא אחר כך בחשבון 2: "
        "טורי חזקות, טורי טיילור וניתוח פורייה — כולם מניחים שאתם יכולים להוכיח התכנסות "
        "לפני גזירה או אינטגרציה איבר-איבר.\n\n"
        "**קשר ל-`concept:series_convergence_advanced`:** אחרי שסיווגתם התכנסות כאן, "
        "השיעור המתקדם שואל *כיצד* הטור מתכנס (מוחלטת לעומת מותנית) ומוצא תחומי התכנסות "
        "ל-$\\sum a_n (x-c)^n$.\n\n"
        "**למה זה חשוב לבחינות:** בבחינות סופיות בטכניון/HU/TAU יש בדרך כלל 2–3 בעיות סיווג טורים "
        "ששוות 15–20 נקודות. נקודות חלקיות על זיהוי מבחן נכון גם כשיש טעת חישוב.\n\n"
        "**קשר לפיזיקה:** טורי perturbation במכניקת קוונטים והתפתחויות אסymptוטיות בהנדסה "
        "דורשים לדעת מתי סכום אינסופי מייצג כמות פיזיקלית סופית — טורים מתבדרים "
        "אינם סקרנות מתמטית בלבד; הם מאותתים על מודל שבור."
    )

    # --- before_exam (slight expand) ---
    idx_exam = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "before_exam")
    data["sections"][idx_exam]["body_en_md"] = (
        "**Formula card:**\n"
        "- p-Series: $\\sum 1/n^p$ converges iff $p>1$\n"
        "- Ratio: $L = \\lim|a_{n+1}/a_n|$; $L<1$ conv., $L>1$ div., $L=1$ inconclusive\n"
        "- Root: $L = \\lim \\sqrt[n]{|a_n|}$; same rule\n"
        "- Leibniz: $b_n>0$, decreasing, $b_n\\to 0$ $\\Rightarrow$ $\\sum(-1)^n b_n$ converges\n"
        "- Absolute convergence $\\Rightarrow$ convergence (not vice versa)\n\n"
        "**Israeli university exam patterns:**\n"
        "- 2–3 series to classify (must state the test and verify all conditions).\n"
        "- One proof question (usually: absolute implies convergence, or Leibniz theorem).\n"
        "- Common traps: ratio test giving $L=1$, alternating series that is only conditionally convergent.\n\n"
        "**Exam tip:** Always state which test you are using, verify its conditions explicitly, and state the conclusion. "
        "Write \"inconclusive\" when $L=1$ or $a_n\\to 0$ — then name your backup test. "
        "Partial credit is given for correct test identification even if the limit is computed incorrectly."
    )
    data["sections"][idx_exam]["body_he_md"] = (
        "**גיליון נוסחאות:**\n"
        "- p-Series: $\\sum 1/n^p$ מתכנס אם ורק אם $p>1$\n"
        "- מנה: $L=\\lim|a_{n+1}/a_n|$; $L<1$ מתכנס, $L>1$ מתבדר, $L=1$ לא מכריע\n"
        "- שורש: $L=\\lim\\sqrt[n]{|a_n|}$; אותו כלל\n"
        "- לייבניץ: $b_n>0$ יורד ל-0 $\\Rightarrow$ $\\sum(-1)^n b_n$ מתכנס\n"
        "- מוחלטת $\\Rightarrow$ מתכנס (ולא להיפך)\n\n"
        "**דגשים בבחינות ישראליות:**\n"
        "- 2–3 טורים לסיווג (חובה לציין המבחן ולאמת כל התנאים).\n"
        "- שאלת הוכחה (בד\"כ: מוחלטת $\\Rightarrow$ מתכנס, או משפט לייבניץ).\n"
        "- מלכודות: $L=1$ במנה, טור מתחלף שמתכנס מותנית בלבד.\n\n"
        "**טיפ:** תמיד ציינו איזה מבחן אתם מפעילים, אמתו תנאים במפורש, וסיימו במסקנה. "
        "כתבו \"לא מכריע\" כש-$L=1$ או $a_n\\to 0$ — ואז ציינו מבחן גיבוי. "
        "נקודות חלקיות על זיהוי מבחן נכון גם כשחישוב הגבול שגוי."
    )

    # --- summary (expand) ---
    idx_sum = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "summary")
    data["sections"][idx_sum]["body_en_md"] = (
        "- **Divergence test:** if $a_n \\not\\to 0$, series diverges; if $a_n\\to 0$, inconclusive — proceed to another test.\n"
        "- **p-Series:** $\\sum 1/n^p$ converges iff $p>1$; harmonic series ($p=1$) diverges.\n"
        "- **Ratio test:** use when $a_n$ involves $n!$ or $r^n$; inconclusive at $L=1$ — switch tests.\n"
        "- **Root test:** use when $a_n = (f(n))^n$; same $L=1$ caveat as ratio.\n"
        "- **Comparison tests:** direct (bound terms) or limit (match dominant power to $1/n^p$).\n"
        "- **Integral test:** when $a_n = f(n)$ with easy antiderivative.\n"
        "- **Leibniz:** alternating series with decreasing $b_n\\to 0$ converges; test $\\sum|a_n|$ for absolute vs conditional.\n"
        "- **Decision flow:** divergence test → identify form → apply best test → if $L=1$, use comparison."
    )
    data["sections"][idx_sum]["body_he_md"] = (
        "- **מבחן גבול:** $a_n\\not\\to 0$ — מתבדר; $a_n\\to 0$ — לא מסייע, המשיכו למבחן אחר.\n"
        "- **p-Series:** $\\sum 1/n^p$ מתכנס אם ורק אם $p>1$; הרמוני ($p=1$) מתבדר.\n"
        "- **מנה:** כש-$a_n$ כולל $n!$ או $r^n$; לא מכריע ב-$L=1$ — החליפו מבחן.\n"
        "- **שורש:** כש-$a_n=(f(n))^n$; אותה אזהרה על $L=1$.\n"
        "- **השוואות:** ישירה (חסימה) או גבולות (התאמת מדרגה ל-$1/n^p$).\n"
        "- **אינטגרל:** כש-$a_n = f(n)$ עם פונקציה ראשונית פשוטה.\n"
        "- **לייבניץ:** מתחלפים עם $b_n$ יורד ל-0; בדקו $\\sum|a_n|$ למוחלטת/מותנית.\n"
        "- **זרימה:** מבחן גבול → זיהוי צורה → מבחן מתאים → אם $L=1$, השוואה."
    )

    # --- question explanations ---
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    # validate parse
    json.loads(TARGET.read_text(encoding="utf-8"))
    print("JSON valid")


if __name__ == "__main__":
    main()
