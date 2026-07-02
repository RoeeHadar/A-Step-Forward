"""Expand discrete_distributions_binomial_poisson.json to MIN_WORDS depth."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/discrete_distributions_binomial_poisson.json"

MIN_WORDS = {
    "intro": (110, 90),
    "definition": (130, 110),
    "theory": (160, 130),
    "worked_example": (130, 110),
    "pitfall": (100, 85),
    "why_matters": (90, 75),
    "method_guide": (100, 85),
}


def word_count(text: str) -> int:
    return len(re.sub(r"\$[^$]*\$", " ", text).split())


def patch_sections(sections: list) -> None:
    for s in sections:
        kind = s.get("kind")
        if kind == "intro":
            s["body_en_md"] = (
                "Two of the most important **discrete probability distributions** model **counts** — "
                "how many times something happens, not how large a measurement is.\n\n"
                "- **Binomial $B(n,p)$:** How many successes occur in exactly $n$ fixed, independent trials, "
                "each with the same success probability $p$? Example: flip a fair coin 10 times — how many heads?\n"
                "- **Poisson $\\text{Poi}(\\lambda)$:** How many events occur in a fixed interval of time or space "
                "when events arrive at a constant average rate $\\lambda$? Example: how many customer calls arrive "
                "at a help desk in one hour?\n\n"
                "At university level you must do three things fluently: **recognise** which distribution fits a word "
                "problem, **compute** probabilities using the PMF (and approximations when appropriate), and "
                "**interpret** mean and variance in context. These distributions also connect forward to the normal "
                "approximation, hypothesis testing, and queueing models — but every advanced topic still starts with "
                "writing $X \\sim B(n,p)$ or $X \\sim \\text{Poi}(\\lambda)$ and stating what counts as a success."
            )
            s["body_he_md"] = (
                "שני **פילוגי הסתברות בדידים** חשובים במיוחד מדגמים **ספירות** — כמה פעמים משהו קורה, "
                "לא כמה גדול מדידה.\n\n"
                "- **בינומי $B(n,p)$:** כמה הצלחות מתרחשות בדיוק ב-$n$ ניסויים קבועים, בלתי-תלויים, "
                "כל אחד עם אותה הסתברות הצלחה $p$? דוגמה: 10 הטלות מטבע — כמה עצות?\n"
                "- **פואסון $\\text{Poi}(\\lambda)$:** כמה אירועים מתרחשים במרווח זמן או מרחב קבוע "
                "כאשר האירועים מגיעים בקצב ממוצע קבוע $\\lambda$? דוגמה: כמה שיחות מגיעות למוקד בשעה?\n\n"
                "ברמת אוניברסיטה עליכם לשלוט בשלושה דברים: **לזהות** איזה פילוג מתאים לבעיה מילולית, "
                "**לחשב** הסתברויות בעזרת PMF (וקירובים כשמתאים), ו**לפרש** ממוצע ושונות בהקשר. "
                "הפילוגים מקשרים קדימה לקירוב נורמלי, בדיקות השערות ומודלים של תורים — "
                "אך כל נושא מתקדם מתחיל בכתיבת $X \\sim B(n,p)$ או $X \\sim \\text{Poi}(\\lambda)$ "
                "ובהגדרת מה נחשב הצלחה."
            )
        elif kind == "definition":
            s["body_en_md"] = (
                "Let $X$ be a discrete random variable counting events.\n\n"
                "**Binomial distribution $X \\sim B(n,p)$:**\n"
                "- Setup: $n$ independent Bernoulli trials; each trial succeeds with probability $p$ "
                "and fails with $q = 1-p$.\n"
                "- Support: $k = 0, 1, \\ldots, n$.\n"
                "- PMF: $P(X=k) = \\binom{n}{k} p^k (1-p)^{n-k}$.\n"
                "- Mean: $\\mu = E[X] = np$. Variance: $\\sigma^2 = \\text{Var}(X) = np(1-p)$.\n\n"
                "**Poisson distribution $X \\sim \\text{Poi}(\\lambda)$:**\n"
                "- Setup: counts rare/independent events in a fixed interval; $\\lambda > 0$ is the expected count.\n"
                "- Support: $k = 0, 1, 2, \\ldots$ (unbounded above).\n"
                "- PMF: $P(X=k) = \\dfrac{e^{-\\lambda}\\lambda^k}{k!}$.\n"
                "- Mean: $\\mu = \\lambda$. Variance: $\\sigma^2 = \\lambda$ (mean equals variance — a signature property).\n\n"
                "**When to use each:**\n"
                "- Binomial: fixed $n$, two outcomes per trial, constant $p$, independent trials.\n"
                "- Poisson: events in time/space with constant rate; no fixed upper bound on count.\n"
                "- **Poisson approximation to binomial:** when $n \\geq 20$ and $p \\leq 0.05$, replace $B(n,p)$ "
                "with $\\text{Poi}(\\lambda)$ where $\\lambda = np$.\n\n"
                "**Key vocabulary:** PMF gives $P(X=k)$ for each possible count $k$. "
                "Support is the set of allowed $k$ values. Parameters $(n,p)$ or $\\lambda$ must be "
                "identified from the story before any numeric work begins."
            )
            s["body_he_md"] = (
                "יהי $X$ משתנה מקרי בדיד שסופר אירועים.\n\n"
                "**פילוג בינומי $X \\sim B(n,p)$:**\n"
                "- תנאים: $n$ ניסויי ברנולי בלתי-תלויים; כל ניסוי מצליח בהסתברות $p$ ונכשל ב-$q=1-p$.\n"
                "- תחום: $k=0,1,\\ldots,n$.\n"
                "- PMF: $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$.\n"
                "- ממוצע: $\\mu=E[X]=np$. שונות: $\\sigma^2=\\text{Var}(X)=np(1-p)$.\n\n"
                "**פילוג פואסון $X \\sim \\text{Poi}(\\lambda)$:**\n"
                "- תנאים: ספירת אירועים נדירים/בלתי-תלויים במרווח קבוע; $\\lambda>0$ הוא מספר האירועים הצפוי.\n"
                "- תחום: $k=0,1,2,\\ldots$ (ללא גבול עליון).\n"
                "- PMF: $P(X=k)=\\dfrac{e^{-\\lambda}\\lambda^k}{k!}$.\n"
                "- ממוצע: $\\mu=\\lambda$. שונות: $\\sigma^2=\\lambda$ (ממוצע שווה לשונות — תכונה מזהה).\n\n"
                "**מתי להשתמש בכל אחד:**\n"
                "- בינומי: $n$ קבוע, שני תוצאות בניסוי, $p$ קבוע, ניסויים בלתי-תלויים.\n"
                "- פואסון: אירועים בזמן/מרחב בקצב קבוע; אין גבול עליון קשיח על הספירה.\n"
                "- **קירוב פואסון לבינומי:** כאשר $n\\geq20$ ו-$p\\leq0.05$, החליפו $B(n,p)$ ב-$\\text{Poi}(\\lambda)$ כאשר $\\lambda=np$.\n\n"
                "**מילון מפתח:** PMF נותן $P(X=k)$ לכל $k$ אפשרי. "
                "תחום התמיכה הוא קבוצת ערכי $k$ המותרים. פרמטרים $(n,p)$ או $\\lambda$ "
                "חייבים להיזהה מהסיפור לפני כל עבודה מספרית."
            )
        elif kind == "theory":
            s["body_en_md"] = (
                "**Binomial symmetry:** If $X \\sim B(n,p)$, then $n-X \\sim B(n,1-p)$. Swapping the labels "
                "\"success\" and \"failure\" flips $p$ to $1-p$ — useful when computing tail probabilities "
                "from the smaller tail.\n\n"
                "**Poisson additivity:** If $X \\sim \\text{Poi}(\\lambda_1)$ and $Y \\sim \\text{Poi}(\\lambda_2)$ "
                "are independent, then $X+Y \\sim \\text{Poi}(\\lambda_1+\\lambda_2)$. Example: calls in the first "
                "minute plus calls in the second minute (same rate) give a Poisson count with doubled $\\lambda$.\n\n"
                "**Normal approximation to binomial:** When $np \\geq 5$ and $n(1-p) \\geq 5$:\n"
                "$$X \\approx N\\bigl(np,\\; np(1-p)\\bigr).$$\n"
                "With continuity correction for discrete-to-continuous conversion:\n"
                "$$P(X \\leq k) \\approx P\\!\\left(Z \\leq \\frac{k+0.5-np}{\\sqrt{np(1-p)}}\\right), "
                "\\quad P(X \\geq k) \\approx P\\!\\left(Z \\geq \\frac{k-0.5-np}{\\sqrt{np(1-p)}}\\right).$$\n\n"
                "**Limit connection:** Poisson is the limit of Binomial as $n \\to \\infty$, $p \\to 0$, "
                "with $np = \\lambda$ fixed. This explains why rare events over many trials behave Poisson.\n\n"
                "**Exam strategy:** First classify the story (fixed trials vs. rate in an interval). "
                "Then check whether an approximation is allowed before doing heavy arithmetic.\n\n"
                "**Cumulative probabilities:** For binomial, $P(X \\leq k) = \\sum_{j=0}^{k} P(X=j)$. "
                "For Poisson tails with small $\\lambda$, direct summation beats normal approx. "
                "For large $n$ with moderate $p$, normal approx with continuity correction is standard."
            )
            s["body_he_md"] = (
                "**סימטריה בינומית:** אם $X \\sim B(n,p)$, אז $n-X \\sim B(n,1-p)$. החלפת תוויות "
                "\"הצלחה\" ו\"כישלון\" הופכת $p$ ל-$1-p$ — שימושי בחישוב זנבות הסתברות מהזנב הקטן יותר.\n\n"
                "**אדיטיביות פואסון:** אם $X \\sim \\text{Poi}(\\lambda_1)$ ו-$Y \\sim \\text{Poi}(\\lambda_2)$ "
                "בלתי-תלויים, אז $X+Y \\sim \\text{Poi}(\\lambda_1+\\lambda_2)$. דוגמה: שיחות בדקה הראשונה "
                "ועוד בדקה השנייה (אותו קצב) נותנות ספירה פואסונית עם $\\lambda$ כפול.\n\n"
                "**קירוב נורמלי לבינומי:** כאשר $np\\geq5$ ו-$n(1-p)\\geq5$:\n"
                "$$X \\approx N\\bigl(np,\\; np(1-p)\\bigr).$$\n"
                "עם תיקון רציפות להמרה מדיסקרטי לרציף:\n"
                "$$P(X\\leq k)\\approx P\\!\\left(Z\\leq\\frac{k+0.5-np}{\\sqrt{np(1-p)}}\\right), "
                "\\quad P(X\\geq k)\\approx P\\!\\left(Z\\geq\\frac{k-0.5-np}{\\sqrt{np(1-p)}}\\right).$$\n\n"
                "**קשר גבול:** פואסון הוא גבול של בינומי כאשר $n\\to\\infty$, $p\\to0$, ו-$np=\\lambda$ קבוע. "
                "זה מסביר מדוע אירועים נדירים על פני ניסויים רבים מתנהגים פואסונית.\n\n"
                "**אסטרטגיית בחינה:** קודם סווגו את הסיפור (ניסויים קבועים מול קצב במרווח). "
                "אז בדקו אם מותר קירוב לפני חישוב כבד.\n\n"
                "**הסתברויות מצטברות:** בבינומי, $P(X\\leq k)=\\sum_{j=0}^{k}P(X=j)$. "
                "בזנבות פואסון עם $\\lambda$ קטן, סכימה ישירה עדיפה על קירוב נורמלי. "
                "ב-$n$ גדול עם $p$ בינוני, קירוב נורמלי עם תיקון רציפות הוא הסטנדרט."
            )
        elif kind == "worked_example":
            n = s.get("example_number", 1)
            if n == 1:
                s["body_en_md"] = (
                    "A fair die is rolled 10 times. Let $X$ = number of sixes. Find $P(X=3)$.\n\n"
                    "### Move 1: Identify the distribution.\n"
                    "Fixed $n=10$ independent trials; success = rolling a six with $p=1/6$. "
                    "Therefore $X \\sim B(10, 1/6)$.\n\n"
                    "### Move 2: Write the PMF.\n"
                    "$$P(X=3) = \\binom{10}{3}\\left(\\frac{1}{6}\\right)^3\\left(\\frac{5}{6}\\right)^7.$$\n\n"
                    "### Move 3: Evaluate.\n"
                    "$$\\binom{10}{3} = 120, \\quad \\left(\\frac{1}{6}\\right)^3 = \\frac{1}{216}, "
                    "\\quad \\left(\\frac{5}{6}\\right)^7 \\approx 0.279.$$\n"
                    "$$P(X=3) = 120 \\times \\frac{1}{216} \\times 0.279 \\approx 0.155.$$\n\n"
                    "**Mean and variance:** $\\mu = np = 10/6 \\approx 1.67$. "
                    "$\\sigma^2 = np(1-p) = 10 \\cdot \\frac{1}{6} \\cdot \\frac{5}{6} \\approx 1.39$.\n\n"
                    "**Exam habit:** State $n$, $p$, and what counts as success before substituting into the PMF.\n\n"
                    "**Sanity check:** With $p=1/6$, expected sixes is about $10/6 \\approx 1.67$, so $k=3$ is above the mean "
                    "but still plausible — probability near 0.15 is reasonable, not near 0 or 1.\n\n"
                    "**Alternative view:** Could also compute $P(X \\geq 3)$ by summing PMF terms, but a single $k$ value "
                    "needs only one PMF evaluation — identify the task before choosing a method."
                )
                s["body_he_md"] = (
                    "קוביה הוגנת מוטלת 10 פעמים. $X$ = מספר השישיות. מצא $P(X=3)$.\n\n"
                    "### צעד 1: זיהוי הפילוג.\n"
                    "$n=10$ ניסויים קבועים ובלתי-תלויים; הצלחה = יציאת שיש עם $p=1/6$. "
                    "לכן $X \\sim B(10, 1/6)$.\n\n"
                    "### צעד 2: כתיבת ה-PMF.\n"
                    "$$P(X=3) = \\binom{10}{3}\\left(\\frac{1}{6}\\right)^3\\left(\\frac{5}{6}\\right)^7.$$\n\n"
                    "### צעד 3: חישוב.\n"
                    "$$\\binom{10}{3}=120, \\quad \\left(\\frac{1}{6}\\right)^3=\\frac{1}{216}, "
                    "\\quad \\left(\\frac{5}{6}\\right)^7\\approx0.279.$$\n"
                    "$$P(X=3)=120\\times\\frac{1}{216}\\times0.279\\approx0.155.$$\n\n"
                    "**ממוצע ושונות:** $\\mu=np=10/6\\approx1.67$. "
                    "$\\sigma^2=np(1-p)=10\\cdot\\frac{1}{6}\\cdot\\frac{5}{6}\\approx1.39$.\n\n"
                    "**הרגל לבחינה:** ציינו $n$, $p$ ומה נחשב הצלחה לפני הצבה ב-PMF.\n\n"
                    "**בדיקת הגיון:** עם $p=1/6$, מספר שישיות צפוי הוא כ-$10/6\\approx1.67$, "
                    "ולכן $k=3$ מעל הממוצע אך עדיין סביר — הסתברות סביב 0.15 הגיונית, לא קרובה ל-0 או 1.\n\n"
                    "**מבט חלופי:** אפשר גם לחשב $P(X\\geq3)$ בסכימת איברי PMF, אך ערך $k$ בודד "
                    "דורש רק הערכת PMF אחת — זהו את המשימה לפני בחירת שיטה. כתבו את שלושת הגורמים בנפרד."
                )
            elif n == 2:
                s["body_en_md"] = (
                    "A factory produces light bulbs where 2% are defective. A box of 50 is inspected. "
                    "Find the probability that exactly 2 are defective.\n\n"
                    "### Move 1: Exact binomial setup.\n"
                    "$X \\sim B(50, 0.02)$ with success = defective bulb.\n"
                    "$$P(X=2) = \\binom{50}{2}(0.02)^2(0.98)^{48} = 1225 \\times 0.0004 \\times 0.3817 \\approx 0.187.$$\n\n"
                    "### Move 2: Check Poisson approximation conditions.\n"
                    "$n=50 \\geq 20$ and $p=0.02 \\leq 0.05$ — approximation is appropriate. "
                    "Set $\\lambda = np = 50 \\times 0.02 = 1$.\n\n"
                    "### Move 3: Poisson PMF.\n"
                    "$$P(X=2) = \\frac{e^{-1} \\cdot 1^2}{2!} = \\frac{e^{-1}}{2} \\approx 0.184.$$\n\n"
                    "**Comparison:** Binomial $0.187$ vs Poisson $0.184$ — very close. "
                    "When defects are rare over many items, Poisson saves computation with negligible error.\n\n"
                    "**Exam tip:** Always verify $n \\geq 20$ and $p \\leq 0.05$ before replacing binomial with Poisson.\n\n"
                    "**Why both methods:** The exact binomial confirms the approximation; in exams you may be asked "
                    "only for Poisson — still write $\\lambda=np$ explicitly to earn method marks.\n\n"
                    "**Expected defects:** $\\mu = np = 1$ means about one defective bulb per box on average — "
                    "so $k=2$ is above average but not rare."
                )
                s["body_he_md"] = (
                    "מפעל מייצר נורות כאשר 2% פגומות. קופסה של 50 נבדקת. "
                    "מצא הסתברות שבדיוק 2 פגומות.\n\n"
                    "### צעד 1: הגדרה בינומית מדויקת.\n"
                    "$X \\sim B(50, 0.02)$ כאשר הצלחה = נורה פגומה.\n"
                    "$$P(X=2)=\\binom{50}{2}(0.02)^2(0.98)^{48}=1225\\times0.0004\\times0.3817\\approx0.187.$$\n\n"
                    "### צעד 2: בדיקת תנאי קירוב פואסון.\n"
                    "$n=50\\geq20$ ו-$p=0.02\\leq0.05$ — הקירוב מתאים. "
                    "קבעו $\\lambda=np=50\\times0.02=1$.\n\n"
                    "### צעד 3: PMF פואסון.\n"
                    "$$P(X=2)=\\frac{e^{-1}\\cdot1^2}{2!}=\\frac{e^{-1}}{2}\\approx0.184.$$\n\n"
                    "**השוואה:** בינומי 0.187 מול פואסון 0.184 — קרוב מאוד. "
                    "כשפגמים נדירים על פני פריטים רבים, פואסון חוסך חישוב עם שגיאה זניחה.\n\n"
                    "**טיפ לבחינה:** וודאו $n\\geq20$ ו-$p\\leq0.05$ לפני החלפת בינומי בפואסון.\n\n"
                    "**למה שתי שיטות:** הבינומי המדויק מאמת את הקירוב; בבחינה ייתכן שיבקשו רק פואסון — "
                    "עדיין כתבו $\\lambda=np$ במפורש לניקוד שיטה.\n\n"
                    "**פגומים צפויים:** $\\mu=np=1$ פירושו נורה פגומה אחת בממוצע לקופסה — "
                    "ולכן $k=2$ מעל הממוצע אך לא נדיר. השוו את התוצאה לבינומי המדויק."
                )
            elif n == 3:
                s["body_en_md"] = (
                    "A manufacturer claims 60% of products pass quality control. In a sample of 100 items, "
                    "what is the probability that **at least 65** pass?\n\n"
                    "### Move 1: Model the count.\n"
                    "$X \\sim B(100, 0.6)$ where success = passing QC. We need $P(X \\geq 65)$.\n\n"
                    "### Move 2: Verify normal approximation.\n"
                    "$np = 60 \\geq 5$ and $n(1-p) = 40 \\geq 5$. Use $X \\approx N(60, 24)$ with "
                    "$\\sigma = \\sqrt{24} \\approx 4.899$.\n\n"
                    "### Move 3: Continuity correction.\n"
                    '"At least 65" means $X \\geq 65$; subtract 0.5 when converting to continuous:\n'
                    "$$P(X \\geq 65) \\approx P\\!\\left(Z \\geq \\frac{64.5-60}{4.899}\\right) "
                    "= P(Z \\geq 0.918).$$\n\n"
                    "### Move 4: Standard normal table.\n"
                    "$$P(Z \\geq 0.918) = 1 - \\Phi(0.918) \\approx 1 - 0.8206 = 0.1794.$$\n\n"
                    "**Conclusion:** About an 18% chance of at least 65 passes — higher than the nominal 60% "
                    "rate but not extreme. **Check:** $z \\approx 1$ is plausible for a modest exceedance over the mean.\n\n"
                    "**Without correction:** Using 65 instead of 64.5 would give $z \\approx 1.02$ and a slightly "
                    "smaller tail probability — continuity correction matters on graded exams.\n\n"
                    "**Interpretation:** 18% is not negligible — quality auditors would investigate if observed "
                    "pass rates consistently exceed the claimed 60% by this margin."
                )
                s["body_he_md"] = (
                    "יצרן טוען ש-60% מהמוצרים עוברים בקרת איכות. בדגימה של 100 פריטים, "
                    "מה ההסתברות ש**לפחות 65** עוברים?\n\n"
                    "### צעד 1: מודל הספירה.\n"
                    "$X \\sim B(100, 0.6)$ כאשר הצלחה = מעבר QC. נדרש $P(X\\geq65)$.\n\n"
                    "### צעד 2: אימות קירוב נורמלי.\n"
                    "$np=60\\geq5$ ו-$n(1-p)=40\\geq5$. השתמשו ב-$X\\approx N(60,24)$ עם "
                    "$\\sigma=\\sqrt{24}\\approx4.899$.\n\n"
                    "### צעד 3: תיקון רציפות.\n"
                    '"לפחות 65" פירושו $X\\geq65$; חסרו 0.5 בהמרה לרציף:\n'
                    "$$P(X\\geq65)\\approx P\\!\\left(Z\\geq\\frac{64.5-60}{4.899}\\right)=P(Z\\geq0.918).$$\n\n"
                    "### צעד 4: טבלת נורמל סטנדרטי.\n"
                    "$$P(Z\\geq0.918)=1-\\Phi(0.918)\\approx1-0.8206=0.1794.$$\n\n"
                    "**מסקנה:** הסתברות של כ-18% לפחות 65 מעברים — גבוהה מהשיעור 60% "
                    "אך לא קיצונית. **בדיקה:** $z\\approx1$ סביר לחריגה מתונה מעל הממוצע.\n\n"
                    "**בלי תיקון:** שימוש ב-65 במקום 64.5 ייתן $z\\approx1.02$ והסתברות זנב "
                    "קטנה מעט — תיקון רציפות חשוב בבחינות מדורגות.\n\n"
                    "**פרשנות:** 18% אינה זניחה — מבקרי איכות יחקירו אם שיעורי מעבר "
                    "בפועל חוזרים ועולים על 60% המוצהר בפער זה."
                )
        elif kind == "checkpoint":
            if "B(5, 0.4)" in s.get("body_en_md", ""):
                s["checkpoint_solution_en"] = (
                    "**Step 1 — Identify distribution.** $X \\sim B(5, 0.4)$; success probability $p=0.4$, "
                    "failure $q=0.6$.\n\n"
                    "**Step 2 — PMF for $k=2$.**\n"
                    "$$P(X=2) = \\binom{5}{2}(0.4)^2(0.6)^3 = 10 \\times 0.16 \\times 0.216 = 0.3456.$$\n\n"
                    "**Step 3 — Mean.** $\\mu = np = 5 \\times 0.4 = 2$.\n\n"
                    "**Check:** Mean 2 matches the centre of the distribution; $P(X=2) \\approx 0.35$ is the "
                    "largest probability mass near the mean for this symmetric-ish setup."
                )
                s["checkpoint_solution_he"] = (
                    "**שלב 1 — זיהוי פילוג.** $X \\sim B(5, 0.4)$; הסתברות הצלחה $p=0.4$, כישלון $q=0.6$.\n\n"
                    "**שלב 2 — PMF עבור $k=2$.**\n"
                    "$$P(X=2)=\\binom{5}{2}(0.4)^2(0.6)^3=10\\times0.16\\times0.216=0.3456.$$\n\n"
                    "**שלב 3 — ממוצע.** $\\mu=np=5\\times0.4=2$.\n\n"
                    "**בדיקה:** ממוצע 2 תואם את מרכז הפילוג; $P(X=2)\\approx0.35$ הוא מסה הסתברות "
                    "גדולה ליד הממוצע במבנה זה."
                )
            elif "lambda = 3" in s.get("body_en_md", "") or "\\lambda = 3" in s.get("body_en_md", ""):
                s["checkpoint_solution_en"] = (
                    "**Step 1 — Model.** Calls per minute: $X \\sim \\text{Poi}(3)$ with $\\lambda=3$.\n\n"
                    "**Step 2 — $P(X=0)$.**\n"
                    "$$P(X=0) = e^{-3} \\approx 0.0498.$$\n\n"
                    "**Step 3 — $P(X=3)$.**\n"
                    "$$P(X=3) = \\frac{e^{-3} \\cdot 3^3}{3!} = \\frac{e^{-3} \\cdot 27}{6} = e^{-3} \\cdot 4.5 \\approx 0.2240.$$\n\n"
                    "**Check:** $P(X=0)$ is small (few minutes with zero calls); $P(X=3)$ is larger because "
                    "$\\lambda=3$ centres the distribution near 3 events per minute."
                )
                s["checkpoint_solution_he"] = (
                    "**שלב 1 — מודל.** שיחות לדקה: $X \\sim \\text{Poi}(3)$ עם $\\lambda=3$.\n\n"
                    "**שלב 2 — $P(X=0)$.**\n"
                    "$$P(X=0)=e^{-3}\\approx0.0498.$$\n\n"
                    "**שלב 3 — $P(X=3)$.**\n"
                    "$$P(X=3)=\\frac{e^{-3}\\cdot3^3}{3!}=\\frac{e^{-3}\\cdot27}{6}=e^{-3}\\cdot4.5\\approx0.2240.$$\n\n"
                    "**בדיקה:** $P(X=0)$ קטנה (מעט דקות ללא שיחות); $P(X=3)$ גדולה יותר כי "
                    "$\\lambda=3$ ממרכז את הפילוג סביב 3 אירועים לדקה."
                )
        elif kind == "method_guide":
            s["body_en_md"] = (
                "Use this decision flow before any calculation:\n\n"
                "| Question in the word problem | Distribution |\n"
                "|---|---|\n"
                "| Fixed $n$ trials, two outcomes, constant $p$ | $B(n,p)$ |\n"
                "| Events in time/space at rate $\\lambda$ | $\\text{Poi}(\\lambda)$ |\n"
                "| $n$ large, $p$ small ($n\\geq20$, $p\\leq0.05$) | $\\text{Poi}(np)$ approx. |\n"
                "| $np\\geq5$ and $n(1-p)\\geq5$, need tail probability | $N(np,np(1-p))$ approx. |\n\n"
                "**Binomial PMF checklist:** (1) Identify $n$ and $p$. (2) Compute $\\binom{n}{k}$. "
                "(3) Multiply $p^k(1-p)^{n-k}$. Mean $np$; variance $np(1-p)$.\n\n"
                "**Poisson PMF checklist:** (1) Set $\\lambda$ from rate $\\times$ interval length. "
                "(2) Use $e^{-\\lambda}\\lambda^k/k!$. For $P(X \\leq m)$, sum individual terms or use tables.\n\n"
                "**Normal approximation:** Standardise with continuity correction ($\\pm 0.5$) "
                "before reading $\\Phi(z)$ from the table."
            )
            s["body_he_md"] = (
                "השתמשו בזרימת ההחלטה הזו לפני כל חישוב:\n\n"
                "| שאלה בבעיה מילולית | פילוג |\n"
                "|---|---|\n"
                "| $n$ ניסויים קבוע, שני תוצאות, $p$ קבוע | $B(n,p)$ |\n"
                "| אירועים בזמן/מרחב בקצב $\\lambda$ | $\\text{Poi}(\\lambda)$ |\n"
                "| $n$ גדול, $p$ קטן ($n\\geq20$, $p\\leq0.05$) | $\\text{Poi}(np)$ |\n"
                "| $np\\geq5$ ו-$n(1-p)\\geq5$, צריך זנב | $N(np,np(1-p))$ |\n\n"
                "**רשימת בדיקה PMF בינומי:** (1) זהו $n$ ו-$p$. (2) חשב $\\binom{n}{k}$. "
                "(3) הכפל $p^k(1-p)^{n-k}$. ממוצע $np$; שונות $np(1-p)$.\n\n"
                "**רשימת בדיקה PMF פואסון:** (1) קבע $\\lambda$ מקצב $\\times$ אורך מרווח. "
                "(2) השתמש ב-$e^{-\\lambda}\\lambda^k/k!$. ל-$P(X\\leq m)$, סכמו איברים או טבלאות.\n\n"
                "**קירוב נורמלי:** סטנדרטיזציה עם תיקון רציפות ($\\pm0.5$) לפני קריאת $\\Phi(z)$ מהטבלה."
            )
        elif kind == "pitfall":
            s["body_en_md"] = (
                "1. **Using Binomial when Poisson fits (or vice versa).** Ask: Is there a fixed trial count $n$? "
                "Is the story about a constant rate over time/space? Use the decision table before writing a PMF.\n\n"
                "2. **Forgetting $\\binom{n}{k}$ in the Binomial PMF.** $P(X=k)$ requires the combination factor — "
                "computing only $p^k(1-p)^{n-k}$ gives the probability of one specific sequence, not $k$ successes "
                "in any order.\n\n"
                "3. **Wrong $\\lambda$ in Poisson approximation.** Set $\\lambda = np$, not $p$ alone. "
                "For 100 items with defect rate 0.01, $\\lambda = 1$, not 0.01.\n\n"
                "4. **Missing continuity correction in normal approximation.** "
                "For $P(X \\geq k)$ use $k-0.5$; for $P(X \\leq k)$ use $k+0.5$. "
                "Skipping correction loses marks and accuracy.\n\n"
                "5. **Applying normal approximation when $np < 5$ or $n(1-p) < 5$.** "
                "The bell curve fits poorly — use exact Binomial or Poisson instead.\n\n"
                "6. **Confusing Poisson mean with Binomial mean.** Poisson: $\\mu = \\lambda$. "
                "Binomial: $\\mu = np$. Do not interchange formulas across distributions."
            )
            s["body_he_md"] = (
                "1. **שימוש בבינומי כשפואסון מתאים (או להיפך).** שאלו: האם יש מספר ניסויים קבוע $n$? "
                "האם הסיפור על קצב קבוע בזמן/מרחב? השתמשו בטבלת ההחלטה לפני כתיבת PMF.\n\n"
                "2. **שכחת $\\binom{n}{k}$ ב-PMF הבינומי.** $P(X=k)$ דורש את מקדם הצירוף — "
                "חישוב רק $p^k(1-p)^{n-k}$ נותן הסתברות לרצף ספציפי, לא $k$ הצלחות בכל סדר.\n\n"
                "3. **$\\lambda$ שגוי בקירוב פואסון.** קבעו $\\lambda=np$, לא $p$ לבד. "
                "ל-100 פריטים עם שיעור פגם 0.01, $\\lambda=1$, לא 0.01.\n\n"
                "4. **אי-שימוש בתיקון רציפות בקירוב נורמלי.** "
                "ל-$P(X\\geq k)$ השתמשו ב-$k-0.5$; ל-$P(X\\leq k)$ ב-$k+0.5$. "
                "דילוג על התיקון מאבד ניקוד ודיוק.\n\n"
                "5. **קירוב נורמלי כאשר $np<5$ או $n(1-p)<5$.** "
                "עקומת הפעמון מתאימה בצורה גרועה — השתמשו בבינומי או פואסון מדויק.\n\n"
                "6. **בלבול ממוצע פואסון ובינומי.** פואסון: $\\mu=\\lambda$. "
                "בינומי: $\\mu=np$. אל תחליפו נוסחאות בין פילוגים."
            )
        elif kind == "why_matters":
            s["body_en_md"] = (
                "Binomial and Poisson distributions are the workhorses of **applied probability** — "
                "quality control (defect counts), telecommunications (call arrivals), epidemiology "
                "(rare disease cases), and finance (defaults in a portfolio of loans).\n\n"
                "**Why it matters for exams:** University statistics courses reward the full pipeline: "
                "model selection, exact or approximate computation, and interpretation. "
                "A correct number without naming $X \\sim B(n,p)$ or justifying an approximation loses method marks.\n\n"
                "Within A Step Forward, this lesson connects to `concept:basic_probability`, "
                "`concept:normal_distribution_basics`, and `concept:hypothesis_testing_intro`. "
                "Mastering discrete counts here makes continuous normal models and inference natural next steps.\n\n"
                "In Israeli university entrance and first-year courses, binomial/Poisson questions often appear "
                "as multi-part problems: identify, compute, then compare an approximation — practice all three stages."
            )
            s["body_he_md"] = (
                "פילוגים בינומי ופואסון הם עבודות הסוס של **הסתברות יישומית** — "
                "בקרת איכות (ספירת פגמים), תקשורת (הגעת שיחות), אפידמיולוגיה "
                "(מקרים נדירים של מחלה), ופיננסים (חדלות פירעון בתיק אשראי).\n\n"
                "**למה זה חשוב לבחינות:** קורסי סטטיסטיקה באוניברסיטה מעריכים את כל השלב: "
                "בחירת מודל, חישוב מדויק או מקורב, ופרשנות. "
                "מספר נכון בלי לציין $X \\sim B(n,p)$ או לנמק קירוב מאבד נקודות שיטה.\n\n"
                "ב-A Step Forward, שיעור זה מקשר ל-`concept:basic_probability`, "
                "`concept:normal_distribution_basics`, ו-`concept:hypothesis_testing_intro`. "
                "שליטה בספירות בדידות כאן הופכת מודלים נורמליים רציפים והסקה לצעדים טבעיים הבאים.\n\n"
                "בקורסי כניסה ושנה א' באוניברסיטה בישראל, שאלות בינומי/פואסון מופיעות לעיתים "
                "כבעיות רב-סעיפיות: זיהוי, חישוב, והשוואת קירוב — תרגלו את שלושת השלבים."
            )
        elif kind == "before_exam":
            s["body_en_md"] = (
                "**Formula card:**\n"
                "- Binomial PMF: $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$; $\\mu=np$; $\\sigma^2=np(1-p)$\n"
                "- Poisson PMF: $P(X=k)=e^{-\\lambda}\\lambda^k/k!$; $\\mu=\\sigma^2=\\lambda$\n"
                "- Poisson approx: $n\\geq20$, $p\\leq0.05$, $\\lambda=np$\n"
                "- Normal approx: $np\\geq5$ and $n(1-p)\\geq5$; $X\\approx N(np,np(1-p))$\n"
                "- Continuity correction: $P(X\\geq k)\\approx P(Z\\geq(k-0.5-\\mu)/\\sigma)$\n\n"
                "**University exam patterns:**\n"
                "- Compute exact Binomial or Poisson probabilities; show PMF setup.\n"
                "- Decide which distribution applies and justify in one sentence.\n"
                "- Apply Poisson or normal approximation with stated conditions.\n"
                "- Interpret $\\mu$ and $\\sigma^2$ in the problem context.\n\n"
                "**Last-minute checklist:** Did I state $n$, $p$ or $\\lambda$? Did I check approximation rules? "
                "Did I apply continuity correction for normal approx?"
            )
            s["body_he_md"] = (
                "**גיליון נוסחאות:**\n"
                "- בינומי: $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$; $\\mu=np$; $\\sigma^2=np(1-p)$\n"
                "- פואסון: $P(X=k)=e^{-\\lambda}\\lambda^k/k!$; $\\mu=\\sigma^2=\\lambda$\n"
                "- קירוב פואסון: $n\\geq20$, $p\\leq0.05$, $\\lambda=np$\n"
                "- קירוב נורמלי: $np\\geq5$ ו-$n(1-p)\\geq5$; $X\\approx N(np,np(1-p))$\n"
                "- תיקון רציפות: $P(X\\geq k)\\approx P(Z\\geq(k-0.5-\\mu)/\\sigma)$\n\n"
                "**דגמי בחינה אוניברסיטאית:**\n"
                "- חישוב הסתברויות בינומיות או פואסוניות מדויקות; הצגת PMF.\n"
                "- החלטה איזה פילוג מתאים ונימוק במשפט.\n"
                "- קירוב פואסון או נורמלי עם תנאים מפורשים.\n"
                "- פרשנות $\\mu$ ו-$\\sigma^2$ בהקשר הבעיה.\n\n"
                "**רשימת בדיקה:** האם ציינתי $n$, $p$ או $\\lambda$? האם בדקתי תנאי קירוב? "
                "האם הוספתי תיקון רציפות לקירוב נורמלי?"
            )


EXPLANATIONS = {
    1: {
        "en": (
            "**Why this is correct:**\n"
            "For $X \\sim B(8, 0.5)$, the mean is $\\mu = np = 8 \\times 0.5 = 4$ and the variance is "
            "$\\sigma^2 = np(1-p) = 8 \\times 0.5 \\times 0.5 = 2$. These are standard binomial moments — "
            "no PMF summation is needed when only $\\mu$ and $\\sigma^2$ are asked.\n\n"
            "**How to think about it:**\n"
            "Identify $n=8$ trials and $p=0.5$ success rate. Mean counts expected successes; "
            "variance is largest at $p=0.5$ for fixed $n$, here giving $\\sigma^2=2$.\n\n"
            "**Common slip:**\n"
            "Using $\\sigma^2 = np$ (Poisson formula) instead of $np(1-p)$, or reporting standard deviation "
            "$\\sqrt{2}$ when the question asks for variance.\n\n"
            "**Exam tip:**\n"
            "Write $\\mu=np$ and $\\sigma^2=npq$ with $q=1-p$ on your formula sheet — one line of substitution "
            "earns full marks on parameter questions.\n\n"
            "**Self-check:** For fair coin ($p=0.5$), mean should be half the trials: $8/2=4$ confirms the answer."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "עבור $X \\sim B(8, 0.5)$, הממוצע הוא $\\mu=np=8\\times0.5=4$ והשונות "
            "$\\sigma^2=np(1-p)=8\\times0.5\\times0.5=2$. אלה רגעים בינומיים סטנדרטיים — "
            "אין צורך בסכום PMF כששואלים רק $\\mu$ ו-$\\sigma^2$.\n\n"
            "**איך לחשוב על זה:**\n"
            "זהו $n=8$ ניסויים ו-$p=0.5$ הסתברות הצלחה. הממוצע סופר הצלחות צפויות; "
            "השונות מקסימלית ב-$p=0.5$ עבור $n$ קבוע, כאן $\\sigma^2=2$.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$\\sigma^2=np$ (נוסחת פואסון) במקום $np(1-p)$, או דיווח סטיית תקן "
            "$\\sqrt{2}$ כשהשאלה מבקשת שונות.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו $\\mu=np$ ו-$\\sigma^2=npq$ עם $q=1-p$ בגיליון הנוסחאות — שורת הצבה אחת "
            "מזכה בניקוד מלא בשאלות פרמטרים.\n\n"
            "**בדיקה עצמית:** במטבע הוגן ($p=0.5$), הממוצע צריך להיות חצי הניסויים: $8/2=4$ מאמת את התשובה."
        ),
    },
    2: {
        "en": (
            "**Why this is correct:**\n"
            "$P(X=0)$ for $X \\sim B(4, 0.3)$ means zero successes in four trials: every trial fails "
            "with probability $1-p = 0.7$. So $P(X=0) = (0.7)^4 = 0.2401$.\n\n"
            "**How to think about it:**\n"
            "The PMF at $k=0$ simplifies because $\\binom{4}{0}=1$ and $p^0=1$, leaving only "
            "$(1-p)^n$. Alternatively use the full PMF with $k=0$ to verify.\n\n"
            "**Common slip:**\n"
            "Using $p^4 = (0.3)^4$ instead of $(1-p)^4$ — confusing \"zero successes\" with "
            "\"four successes.\" Another error: stopping at $(0.7)^4$ without evaluating to 0.2401.\n\n"
            "**Exam tip:**\n"
            "For \"exactly zero\" binomial problems, ask: must every trial fail? If yes, multiply "
            "$(1-p)$ exactly $n$ times — faster than the full combination formula.\n\n"
            "**Self-check:** $(0.7)^4 \\approx 0.24$ is between 0 and 1 and less than 0.5 — sensible for four failures."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "$P(X=0)$ עבור $X \\sim B(4, 0.3)$ פירושו אפס הצלחות בארבעה ניסויים: כל ניסוי נכשל "
            "בהסתברות $1-p=0.7$. לכן $P(X=0)=(0.7)^4=0.2401$.\n\n"
            "**איך לחשוב על זה:**\n"
            "ה-PMF ב-$k=0$ מתפשט כי $\\binom{4}{0}=1$ ו-$p^0=1$, ונשאר רק $(1-p)^n$. "
            "לחלופין השתמשו ב-PMF המלא עם $k=0$ לאימות.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$p^4=(0.3)^4$ במקום $(1-p)^4$ — בלבול \"אפס הצלחות\" עם "
            "\"ארבע הצלחות.\" שגיאה נוספת: עצירה ב-$(0.7)^4$ בלי חישוב ל-0.2401.\n\n"
            "**טיפ לבחינה:**\n"
            "ב\"בדיוק אפס\" בינומי, שאלו: האם כל ניסוי חייב להיכשל? אם כן, הכפילו $(1-p)$ "
            "בדיוק $n$ פעמים — מהיר יותר מהנוסחה המלאה.\n\n"
            "**בדיקה עצמית:** $(0.7)^4\\approx0.24$ בין 0 ל-1 ופחות מ-0.5 — סביר לארבעה כישלונות."
        ),
    },
    3: {
        "en": (
            "**Why this is correct:**\n"
            "For $X \\sim \\text{Poi}(2)$, the PMF at $k=0$ is $P(X=0) = e^{-\\lambda}\\lambda^0/0! = e^{-2} \\approx 0.1353$. "
            "This is the probability of no events when the average rate is 2 per interval.\n\n"
            "**How to think about it:**\n"
            "Poisson counts rare events; $P(X=0)$ asks \"nothing happens.\" Plug $\\lambda=2$ into "
            "$e^{-\\lambda}$ — the factorial term is 1 when $k=0$.\n\n"
            "**Common slip:**\n"
            "Forgetting the exponential factor and writing only $\\lambda^k/k!$, or using binomial "
            "$(1-p)^n$ instead of Poisson when the story gives a rate, not fixed trials.\n\n"
            "**Exam tip:**\n"
            "Memorise $e^{-1}\\approx0.368$, $e^{-2}\\approx0.135$, $e^{-3}\\approx0.050$ for quick sanity checks "
            "on Poisson zero-probability questions.\n\n"
            "**Self-check:** With $\\lambda=2$, we expect about 2 events per interval — probability of zero should be moderate, not near 1."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "עבור $X \\sim \\text{Poi}(2)$, ה-PMF ב-$k=0$ הוא $P(X=0)=e^{-\\lambda}\\lambda^0/0!=e^{-2}\\approx0.1353$. "
            "זו ההסתברות שאין אירועים כשהקצב הממוצע הוא 2 למרווח.\n\n"
            "**איך לחשוב על זה:**\n"
            "פואסון סופר אירועים נדירים; $P(X=0)$ שואל \"שום דבר לא קורה.\" הציבו $\\lambda=2$ "
            "ב-$e^{-\\lambda}$ — איבר העצרת הוא 1 כש-$k=0$.\n\n"
            "**טעות נפוצה:**\n"
            "שכחת גורם המעריך וכתיבה רק של $\\lambda^k/k!$, או שימוש בבינומי "
            "$(1-p)^n$ במקום פואסון כשהסיפור נותן קצב, לא ניסויים קבועים.\n\n"
            "**טיפ לבחינה:**\n"
            "שננו $e^{-1}\\approx0.368$, $e^{-2}\\approx0.135$, $e^{-3}\\approx0.050$ לבדיקות מהירות "
            "בשאלות הסתברות-אפס פואסוניות.\n\n"
            "**בדיקה עצמית:** עם $\\lambda=2$, מצפים לכ-2 אירועים למרווח — הסתברות לאפס צריכה להיות בינונית, לא קרובה ל-1."
        ),
    },
    4: {
        "en": (
            "**Why this is correct:**\n"
            "A defining property of the Poisson distribution: mean and variance both equal $\\lambda$. "
            "For $X \\sim \\text{Poi}(5)$, therefore $\\mu = 5$ and $\\sigma^2 = 5$.\n\n"
            "**How to think about it:**\n"
            "Unlike binomial where $\\sigma^2 = np(1-p) \\leq np$, Poisson has mean = variance. "
            "If exam data show equal mean and variance, Poisson is a strong candidate model.\n\n"
            "**Common slip:**\n"
            "Applying binomial variance $np(1-p)$ to a Poisson question, or reporting standard deviation "
            "5 instead of variance 5.\n\n"
            "**Exam tip:**\n"
            "When asked only for mean and variance of Poisson($\\lambda$), the answer is two copies of "
            "$\\lambda$ — no calculation beyond reading the parameter.\n\n"
            "**Self-check:** Variance 5 means standard deviation $\\sqrt{5}\\approx2.24$ — do not confuse the two."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "תכונה מגדירה של פילוג פואסון: ממוצע ושונות שווים ל-$\\lambda$. "
            "עבור $X \\sim \\text{Poi}(5)$, לכן $\\mu=5$ ו-$\\sigma^2=5$.\n\n"
            "**איך לחשוב על זה:**\n"
            "בניגוד לבינומי שבו $\\sigma^2=np(1-p)\\leq np$, בפואסון ממוצע = שונות. "
            "אם בנתוני בחינה ממוצע ושונות שווים, פואסון הוא מועמד חזק.\n\n"
            "**טעות נפוצה:**\n"
            "יישום שונות בינומית $np(1-p)$ על שאלת פואסון, או דיווח סטיית תקן 5 "
            "במקום שונות 5.\n\n"
            "**טיפ לבחינה:**\n"
            "כששואלים רק ממוצע ושונות של פואסון($\\lambda$), התשובה היא שני עותקים של "
            "$\\lambda$ — ללא חישוב מעבר לקריאת הפרמטר.\n\n"
            "**בדיקה עצמית:** שונות 5 פירושה סטיית תקן $\\sqrt{5}\\approx2.24$ — אל תבלבלו ביניהם."
        ),
    },
    5: {
        "en": (
            "**Why this is correct:**\n"
            "$P(X=3) = \\binom{10}{3}(0.3)^3(0.7)^7 = 120 \\times 0.027 \\times 0.0824 \\approx 0.267$. "
            "Three successes in 10 trials with $p=0.3$ uses the full binomial PMF.\n\n"
            "**How to think about it:**\n"
            "Compute $\\binom{10}{3}=120$ first, then powers of $p$ and $1-p$. "
            "The answer should be less than 0.5 for a single $k$ near the mean $np=3$.\n\n"
            "**Common slip:**\n"
            "Omitting $\\binom{10}{3}$, swapping $p$ and $1-p$ exponents, or using Poisson because "
            "$p=0.3$ is \"small\" without checking the fixed-$n$ binomial setup.\n\n"
            "**Exam tip:**\n"
            "Show the three-factor PMF structure on paper — graders award partial credit even if "
            "final multiplication has a minor arithmetic error.\n\n"
            "**Self-check:** Mean $np=3$ — probability at $k=3$ should be among the largest PMF values."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "$P(X=3)=\\binom{10}{3}(0.3)^3(0.7)^7=120\\times0.027\\times0.0824\\approx0.267$. "
            "שלוש הצלחות ב-10 ניסויים עם $p=0.3$ משתמשות ב-PMF בינומי המלא.\n\n"
            "**איך לחשוב על זה:**\n"
            "חשבו $\\binom{10}{3}=120$ קודם, אחר כך חזקות של $p$ ו-$1-p$. "
            "התשובה צריכה להיות פחות מ-0.5 עבור $k$ בודד ליד הממוצע $np=3$.\n\n"
            "**טעות נפוצה:**\n"
            "השמטת $\\binom{10}{3}$, החלפת מעריכי $p$ ו-$1-p$, או שימוש בפואסון כי "
            "$p=0.3$ \"קטן\" בלי לבדוק מבנה בינומי עם $n$ קבוע.\n\n"
            "**טיפ לבחינה:**\n"
            "הציגו מבנה PMF של שלושה גורמים — בודקים נותנים ניקוד חלקי גם אם "
            "הכפל הסופי שגוי במעט.\n\n"
            "**בדיקה עצמית:** ממוצע $np=3$ — ההסתברות ב-$k=3$ צריכה להיות בין הגבוהות ב-PMF."
        ),
    },
    6: {
        "en": (
            "**Why this is correct:**\n"
            "Accidents at rate 2/day: $X \\sim \\text{Poi}(2)$. "
            "$P(X \\leq 1) = P(X=0) + P(X=1) = e^{-2} + 2e^{-2} = 3e^{-2} \\approx 0.406$. "
            "Tail sums require adding individual Poisson terms.\n\n"
            "**How to think about it:**\n"
            "\"At most 1\" means $k=0$ or $k=1$. Compute each PMF term separately, then add. "
            "Do not subtract from 1 unless you first computed $P(X \\geq 2)$.\n\n"
            "**Common slip:**\n"
            "Using only $P(X=1)$ and forgetting $P(X=0)$, or treating \"rate 2\" as $p=2$ in a binomial.\n\n"
            "**Exam tip:**\n"
            "For small $\\lambda$ and small upper bound $m$, direct summation is faster and more reliable "
            "than normal approximation.\n\n"
            "**Self-check:** $P(X\\leq1)\\approx0.41$ means roughly 41% of days have zero or one accident — plausible for $\\lambda=2$."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "תאונות בקצב 2 ליום: $X \\sim \\text{Poi}(2)$. "
            "$P(X \\leq 1)=P(X=0)+P(X=1)=e^{-2}+2e^{-2}=3e^{-2}\\approx0.406$. "
            "סכימת זנבות דורשת הוספת איברי פואסון בודדים.\n\n"
            "**איך לחשוב על זה:**\n"
            "\"לכל היותר 1\" פירושו $k=0$ או $k=1$. חשבו כל איבר PMF בנפרד, ואז חברו. "
            "אל תחסרו מ-1 אלא אם חישבתם קודם $P(X \\geq 2)$.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש רק ב-$P(X=1)$ ושכחת $P(X=0)$, או התייחסות ל\"קצב 2\" כ-$p=2$ בבינומי.\n\n"
            "**טיפ לבחינה:**\n"
            "ל-$\\lambda$ קטן וגבול עליון $m$ קטן, סכימה ישירה מהירה ואמינה יותר "
            "מקירוב נורמלי.\n\n"
            "**בדיקה עצמית:** $P(X\\leq1)\\approx0.41$ פירושו שכ-41% מהימים עם אפס או תאונה אחת — סביר ל-$\\lambda=2$."
        ),
    },
    7: {
        "en": (
            "**Why this is correct:**\n"
            "100 items with defect probability 0.01: check Poisson approx ($n=100 \\geq 20$, $p=0.01 \\leq 0.05$). "
            "Set $\\lambda = np = 1$. Then $P(X=2) = e^{-1} \\cdot 1^2 / 2! = e^{-1}/2 \\approx 0.184$.\n\n"
            "**How to think about it:**\n"
            "The exact model is $B(100, 0.01)$, but Poisson with $\\lambda=1$ approximates well. "
            "Always state $\\lambda=np$ before applying the Poisson PMF.\n\n"
            "**Common slip:**\n"
            "Using $\\lambda=0.01$ (confusing rate per item with expected total count), or applying "
            "binomial with heavy computation when approximation is explicitly requested.\n\n"
            "**Exam tip:**\n"
            "When the question says \"use Poisson approximation,\" write the rule check "
            "($n \\geq 20$, $p \\leq 0.05$) — examiners award method marks before the numeric answer.\n\n"
            "**Self-check:** With $\\lambda=1$, $P(X=2)\\approx0.18$ is the second-largest mass after $k=0,1$."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "100 פריטים עם הסתברות פגם 0.01: בדקו קירוב פואסון ($n=100\\geq20$, $p=0.01\\leq0.05$). "
            "קבעו $\\lambda=np=1$. אז $P(X=2)=e^{-1}\\cdot1^2/2!=e^{-1}/2\\approx0.184$.\n\n"
            "**איך לחשוב על זה:**\n"
            "המודל המדויק הוא $B(100,0.01)$, אך פואסון עם $\\lambda=1$ מקורב היטב. "
            "תמיד ציינו $\\lambda=np$ לפני PMF פואסון.\n\n"
            "**טעות נפוצה:**\n"
            "שימוש ב-$\\lambda=0.01$ (בלבול קצב לפריט עם ספירה צפויה כוללת), או בינומי "
            "כבד כשהשאלה מבקשת במפורש קירוב.\n\n"
            "**טיפ לבחינה:**\n"
            "כשהשאלה אומרת \"השתמש בקירוב פואסון\", כתבו בדיקת תנאים "
            "($n\\geq20$, $p\\leq0.05$) — נקודות שיטה לפני התשובה המספרית.\n\n"
            "**בדיקה עצמית:** עם $\\lambda=1$, $P(X=2)\\approx0.18$ הוא מסה גדולה שנייה אחרי $k=0,1$."
        ),
    },
    8: {
        "en": (
            "**Why this is correct:**\n"
            "For $B(50, 0.4)$: $np = 50 \\times 0.4 = 20 \\geq 5$ and $n(1-p) = 50 \\times 0.6 = 30 \\geq 5$. "
            "Both success and failure counts are large enough — **normal approximation is valid**.\n\n"
            "**How to think about it:**\n"
            "The rule requires BOTH $np \\geq 5$ AND $n(1-p) \\geq 5$. Here $p=0.4$ is not extreme, "
            "so both conditions are comfortably satisfied.\n\n"
            "**Common slip:**\n"
            "Checking only $np$ and ignoring $n(1-p)$, or declaring invalid because $p \\neq 0.5$. "
            "Another error: computing a probability when the question only asks validity.\n\n"
            "**Exam tip:**\n"
            "Write \"np = ... ≥ 5 ✓\" and \"n(1-p) = ... ≥ 5 ✓\" as two separate lines — "
            "this template answers every \"is normal approx valid?\" question."
        ),
        "he": (
            "**למה זה נכון:**\n"
            "עבור $B(50,0.4)$: $np=50\\times0.4=20\\geq5$ ו-$n(1-p)=50\\times0.6=30\\geq5$. "
            "גם ספירת הצלחות וגם כישלונות גדולות מספיק — **קירוב נורמלי תקף**.\n\n"
            "**איך לחשוב על זה:**\n"
            "הכלל דורש גם $np\\geq5$ וגם $n(1-p)\\geq5$. כאן $p=0.4$ לא קיצוני, "
            "ולכן שני התנאים מתקיימים בנוחות.\n\n"
            "**טעות נפוצה:**\n"
            "בדיקה רק של $np$ והתעלמות מ-$n(1-p)$, או הצהרה על אי-תקפות כי $p\\neq0.5$. "
            "שגיאה נוספת: חישוב הסתברות כשהשאלה שואלת רק תקפות.\n\n"
            "**טיפ לבחינה:**\n"
            "כתבו \"np = ... ≥ 5 ✓\" ו-\"n(1-p) = ... ≥ 5 ✓\" בשתי שורות — "
            "תבנית זו עונה על כל שאלת \"האם קירוב נורמלי תקף?\""
        ),
    },
}


def patch_questions(questions: list) -> None:
    for q in questions:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]


def validate(data: dict) -> None:
    errors = []
    for s in data["sections"]:
        kind = s.get("kind")
        if kind in MIN_WORDS:
            en_min, he_min = MIN_WORDS[kind]
            en_w = word_count(s.get("body_en_md", ""))
            he_w = word_count(s.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"section {kind}: EN {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"section {kind}: HE {he_w} < {he_min}")
        if kind == "worked_example":
            en_w = word_count(s.get("body_en_md", ""))
            he_w = word_count(s.get("body_he_md", ""))
            if en_w < MIN_WORDS["worked_example"][0]:
                errors.append(f"worked_example {s.get('example_number')}: EN {en_w}")
            if he_w < MIN_WORDS["worked_example"][1]:
                errors.append(f"worked_example {s.get('example_number')}: HE {he_w}")
    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 160:
                errors.append(f"Q{q['ord']} explanation_{lang}: {w} words")
    if errors:
        raise SystemExit("Validation failed:\n" + "\n".join(errors))
    print("Local validation passed.")


def main() -> None:
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    patch_sections(data["sections"])
    patch_questions(data["questions"])
    data["author"] = "cursor-claude-2026"
    validate(data)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
