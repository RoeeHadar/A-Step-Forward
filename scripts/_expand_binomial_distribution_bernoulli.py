#!/usr/bin/env python3
"""Apply Cursor expansion to binomial_distribution_bernoulli.json."""
import json
import re
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "seed_data" / "lessons" / "binomial_distribution_bernoulli.json"

EXPL_EN = {
    1: "**Why this is correct:**\nWe have $n=6$ independent trials with $p=0.5$, so $X\\sim B(6,0.5)$. Exactly three successes means $k=3$. The binomial PMF gives $P(X=3)=\\binom{6}{3}(0.5)^6=20/64=0.3125$.\n\n**How to think about it:**\nWith a fair coin ($p=0.5$), the distribution is symmetric and $\\binom{6}{3}=\\binom{6}{3}$ — a quick sanity check before calculating.\n\n**Common slip:**\nOmitting $\\binom{6}{3}$ and writing only $(0.5)^6$, which counts one arrangement instead of all $20$ ways to place three successes among six trials.\n\n**Exam tip:**\nWhen $p=0.5$, rewrite $(0.5)^n$ as $1/2^n$ and keep answers as exact fractions when possible.",
    2: "**Why this is correct:**\nEach true/false question is a Bernoulli trial with $p=0.5$ (guess). With $n=10$ independent questions, the count of correct answers $X\\sim B(10,0.5)$. The expected value is $E[X]=\\mu=np=10\\times0.5=5$.\n\n**How to think about it:**\nExpectation is linear: on average half the guesses succeed. You do not need the full PMF — the question asks for the mean, not a probability.\n\n**Common slip:**\nComputing $P(X=5)$ instead of $E[X]$, or using the variance formula when only the mean is requested.\n\n**Exam tip:**\nUnderline whether the stem says \"expected number,\" \"average,\" or \"most likely value\" — only the first two equal $np$.",
    3: "**Why this is correct:**\nFor $X\\sim B(3,0.4)$, zero successes means all three trials fail. Each failure has probability $1-p=0.6$, so $P(X=0)=(0.6)^3=0.216$.\n\n**How to think about it:**\nWhen $k=0$, the binomial coefficient is $1$ and the PMF collapses to $(1-p)^n$ — the complement shortcut for \"none succeed.\"\n\n**Common slip:**\nUsing $0.4^3$ instead of $0.6^3$ — the exponent on $p$ is the number of successes, not failures.\n\n**Exam tip:**\nMemorize $P(X=0)=(1-p)^n$ and $P(X=n)=p^n$; they appear constantly in complement problems.",
    4: "**Why this is correct:**\nFor $X\\sim B(5,0.6)$, variance is $\\sigma^2=np(1-p)=5\\times0.6\\times0.4=1.2$. No PMF calculation is needed.\n\n**How to think about it:**\nVariance is largest near $p=0.5$ and shrinks when $p$ is near $0$ or $1$. Here $p=0.6$ gives moderate spread around mean $\\mu=3$.\n\n**Common slip:**\nReporting standard deviation $\\sqrt{1.2}$ when variance is asked, or using $np$ instead of $np(1-p)$.\n\n**Exam tip:**\nWrite $\\sigma^2=npq$ with $q=1-p$ on your formula card — graders distinguish variance from SD explicitly.",
    5: "**Why this is correct:**\nDefective items: $n=7$, $p=0.1$, so $X\\sim B(7,0.1)$. \"At most one defective\" means $P(X\\leq1)=P(X=0)+P(X=1)$. $P(X=0)=0.9^7\\approx0.4783$ and $P(X=1)\\approx0.3720$, summing to $0.8503$.\n\n**How to think about it:**\nCumulative \"at most $k$\" requires adding PMF terms from $0$ through $k$. With small $p$, most mass sits at $0$ and $1$.\n\n**Common slip:**\nStopping at $P(X=0)$ only, or using complement without finishing the tail sum.\n\n**Exam tip:**\nFor \"at most 1,\" always write two terms explicitly — partial sums lose method marks even if the final number is close.",
    6: "**Why this is correct:**\n$P(X\\geq1)$ means \"at least one success.\" The complement is easier: $P(X\\geq1)=1-P(X=0)=1-(0.7)^{10}=0.9718$.\n\n**How to think about it:**\nSumming $P(X=1)+\\cdots+P(X=10)$ is correct but slow. One failure probability $(1-p)^n$ captures \"all fail.\"\n\n**Common slip:**\nUsing $1-p^{10}$ instead of $1-(1-p)^{10}$ — exponents apply to failure probability, not success.\n\n**Exam tip:**\nWhenever you see \"at least one,\" sketch the complement before reaching for the calculator.",
    7: "**Why this is correct:**\nFor $X\\sim B(8,0.5)$, an inclusive interval $3\\leq X\\leq5$ means $P(X=3)+P(X=4)+P(X=5)$. With $p=0.5$, $P(X=k)=\\binom{8}{k}/256$, giving $(56+70+56)/256=182/256\\approx0.711$.\n\n**How to think about it:**\nSymmetric binomial: $P(X=3)=P(X=5)$ because $\\binom{8}{3}=\\binom{8}{5}$. The middle term $P(X=4)$ is the mode near $n/2$.\n\n**Common slip:**\nUsing $P(X\\leq5)-P(X\\leq3)$ without the $-1$ adjustment — for inclusive bounds use $P(X\\leq b)-P(X\\leq a-1)$.\n\n**Exam tip:**\nList each $k$ in the interval before calculating — off-by-one errors are the top binomial exam mistake on timed tests.",
    8: "**Why this is correct:**\nBINS: **B**inary outcomes, **I**ndependent trials, fixed **N**umber $n$, **S**ame probability $p$ each trial. Most often violated: **Independence** (sampling without replacement — use hypergeometric) and **Same $p$** (conditions change mid-experiment).\n\n**How to think about it:**\nBefore any formula, translate the story into trials. If trials are not identical or not independent, the binomial model is wrong regardless of arithmetic.\n\n**Common slip:**\nApplying $B(n,p)$ to \"draw 5 cards without replacement\" — outcomes are dependent.\n\n**Exam tip:**\nWrite BINS as a checklist on word problems; one violated letter disqualifies the binomial model.",
}

EXPL_HE = {
    1: "**למה זה נכון:**\nיש $n=6$ ניסויים בלתי-תלויים עם $p=0.5$, ולכן $X\\sim B(6,0.5)$. בדיוק שלוש הצלחות פירושו $k=3$. מ-PMF הבינומי מתקבל $P(X=3)=\\binom{6}{3}(0.5)^6=20/64=0.3125$.\n\n**איך לחשוב על זה:**\nבמטבע הוגן ($p=0.5$) הפילוג סימטרי — בדיקת הגיון מהירה לפני החישוב.\n\n**טעות נפוצה:**\nהשמטת $\\binom{6}{3}$ וכתיבת $(0.5)^6$ בלבד, שסופרת סידור אחד במקום $20$ דרכים לשלוש הצלחות.\n\n**טיפ לבחינה:**\nכש-$p=0.5$, כתבו $(0.5)^n=1/2^n$ והשאירו תשובות כשברים מדויקים כשאפשר.",
    2: "**למה זה נכון:**\nכל שאלת נכון/לא-נכון היא ניסוי ברנולי עם $p=0.5$. עם $n=10$ שאלות בלתי-תלויות, $X\\sim B(10,0.5)$ ו-$E[X]=\\mu=np=5$.\n\n**איך לחשוב על זה:**\nהתוחלת לינארית: בממוצע חצי מהניחושים מצליחים. אין צורך ב-PMF — השאלה מבקשת ממוצע, לא הסתברות.\n\n**טעות נפוצה:**\nחישוב $P(X=5)$ במקום $E[X]$, או שימוש בנוסחת השונות כשמבקשים רק ממוצע.\n\n**טיפ לבחינה:**\nסמנו אם הניסוח אומר \"מספר צפוי\", \"ממוצע\" או \"הערך הסביר ביותר\" — רק השניים הראשונים שווים ל-$np$.",
    3: "**למה זה נכון:**\nעבור $X\\sim B(3,0.4)$, אפס הצלחות פירושו שלושה כישלונות. $P(X=0)=(0.6)^3=0.216$.\n\n**איך לחשוב על זה:**\nכש-$k=0$, המקדם $\\binom{3}{0}=1$ ו-PMF מתכווץ ל-$(1-p)^n$.\n\n**טעות נפוצה:**\nשימוש ב-$0.4^3$ במקום $0.6^3$ — החזקה על $p$ היא מספר ההצלחות.\n\n**טיפ לבחינה:**\nשיננו $P(X=0)=(1-p)^n$ ו-$P(X=n)=p^n$ — הם מופיעים בכל בעיות המשלים.",
    4: "**למה זה נכון:**\nעבור $X\\sim B(5,0.6)$, השונות היא $\\sigma^2=np(1-p)=5\\times0.6\\times0.4=1.2$.\n\n**איך לחשוב על זה:**\nהשונות מקסימלית ליד $p=0.5$ וקטנה כש-$p$ קרוב ל-$0$ או $1$. כאן $\\mu=3$.\n\n**טעות נפוצה:**\nדיווח על סטיית תקן $\\sqrt{1.2}$ כשמבקשים שונות, או שימוש ב-$np$ במקום $np(1-p)$.\n\n**טיפ לבחינה:**\nכתבו $\\sigma^2=npq$ עם $q=1-p$ על גיליון הנוסחאות.",
    5: "**למה זה נכון:**\n$n=7$, $p=0.1$, $X\\sim B(7,0.1)$. \"לכל היותר אחד פגום\" = $P(X\\leq1)=P(X=0)+P(X=1)\\approx0.8503$.\n\n**איך לחשוב על זה:**\n\"לכל היותר $k$\" דורש סכימת איברי PMF מ-$0$ עד $k$. עם $p$ קטן, רוב המסה ב-$0$ ו-$1$.\n\n**טעות נפוצה:**\nעצירה ב-$P(X=0)$ בלבד, או שימוש במשלים בלי לסיים את סכימת הזנב.\n\n**טיפ לבחינה:**\nב\"לכל היותר 1\" — כתבו שני איברים במפורש.",
    6: "**למה זה נכון:**\n$P(X\\geq1)=1-P(X=0)=1-(0.7)^{10}=0.9718$.\n\n**איך לחשוב על זה:**\nסכימת $P(X=1)+\\cdots+P(X=10)$ נכונה אך איטית. $(1-p)^n$ תופס \"כולם נכשלים\".\n\n**טעות נפוצה:**\nשימוש ב-$1-p^{10}$ במקום $1-(1-p)^{10}$.\n\n**טיפ לבחינה:**\nב\"לפחות אחד\" — שרטטו משלים לפני המחשבון.",
    7: "**למה זה נכון:**\n$X\\sim B(8,0.5)$, $3\\leq X\\leq5$ = $P(X=3)+P(X=4)+P(X=5)=(56+70+56)/256\\approx0.711$.\n\n**איך לחשוב על זה:**\nבינומי סימטרי: $P(X=3)=P(X=5)$. האיבר האמצעי $P(X=4)$ שכיח ליד $n/2$.\n\n**טעות נפוצה:**\nשימוש ב-$P(X\\leq5)-P(X\\leq3)$ בלי התאמת $-1$ — לגבולות כוללים: $P(X\\leq b)-P(X\\leq a-1)$.\n\n**טיפ לבחינה:**\nרשמו כל $k$ בטווח לפני החישוב.",
    8: "**למה זה נכון:**\nBINS: **B**inary, **I**ndependent, **N**umber קבוע, **S**ame $p$. מופרים: בלתי-תלות (דגימה ללא החזרה) וקביעות $p$.\n\n**איך לחשוב על זה:**\nלפני נוסחה — תרגמו את הסיפור לניסויים. אם הניסויים לא זהים או לא בלתי-תלויים, המודל הבינומי שגוי.\n\n**טעות נפוצה:**\nיישום $B(n,p)$ על \"שליפת 5 קלפים ללא החזרה\".\n\n**טיפ לבחינה:**\nכתבו BINS כרשימת בדיקה; אות אחת מופרת — פסלו את המודל הבינומי.",
}


def patch_sections(sections):
    for s in sections:
        k = s.get("kind")
        if k == "intro":
            s["body_he_md"] = s["body_he_md"].replace("ניסuיים קlinיים", "ניסuיים קlinיים")
            s["body_he_md"] = s["body_he_md"].replace("קlinיים", "קlinיים")
        if k == "definition":
            s["body_en_md"] = (
                "**Bernoulli trial:** A single random experiment with exactly two outcomes. "
                "Label one outcome \"success\" with probability $p$ and the other \"failure\" with $q=1-p$. "
                "Examples: flip heads ($p=0.5$), pass an exam ($p=0.7$), item defective ($p=0.05$).\n\n"
                "**Binomial random variable $X \\sim B(n,p)$:** Let $X$ count the number of successes in $n$ "
                "independent Bernoulli trials, each with the same success probability $p$. "
                "The support is $k=0,1,\\ldots,n$.\n\n"
                "**BINS conditions** — all four must hold:\n"
                "- **B**inary: exactly two outcomes per trial.\n"
                "- **I**ndependent: one trial does not change probabilities for others.\n"
                "- **N**umber: trial count $n$ is fixed before observing results.\n"
                "- **S**ame: every trial uses the same $p$.\n\n"
                "**PMF:**\n"
                "$$P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}, \\quad k=0,1,\\ldots,n$$\n"
                "where $\\binom{n}{k}=\\dfrac{n!}{k!(n-k)!}$ counts orderings with exactly $k$ successes.\n\n"
                "**Mean and spread:**\n"
                "$$\\mu=E[X]=np, \\qquad \\sigma^2=\\text{Var}(X)=np(1-p), \\qquad \\sigma=\\sqrt{np(1-p)}.$$"
            )
            s["body_he_md"] = (
                "**ניסוי ברנולי:** ניסוי מקרי בודד עם בדיוק שני תוצאות. "
                "מסמנים \"הצלחה\" בהסתברות $p$ ו\"כישלון\" ב-$q=1-p$. "
                "דוגמאות: עץ במטבע ($p=0.5$), מעבר מבחן ($p=0.7$), פריט פגום ($p=0.05$).\n\n"
                "**משתנה בינומי $X\\sim B(n,p)$:** $X$ סופר הצלחות ב-$n$ "
                "ניסויי ברנולי בלתי-תלויים עם אותו $p$. תחום: $k=0,1,\\ldots,n$.\n\n"
                "**תנאי BINS** — כל ארבעתם חייבים להתקיים:\n"
                "- **B**inary — שני תוצאות בניסוי.\n"
                "- **I**ndependent — ניסוי אחד לא משנה הסתברויות באחרים.\n"
                "- **N**umber — $n$ קבוע לפני צפייה בתוצאות.\n"
                "- **S**ame — אותו $p$ בכל ניסוי.\n\n"
                "**PMF:**\n"
                "$$P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}, \\quad k=0,1,\\ldots,n$$\n"
                "כאשר $\\binom{n}{k}$ סופר סידורים עם בדיוק $k$ הצלחות.\n\n"
                "**ממוצע ופיזור:**\n"
                "$$\\mu=E[X]=np, \\qquad \\sigma^2=np(1-p), \\qquad \\sigma=\\sqrt{np(1-p)}.$$"
            )
        elif k == "theory":
            s["body_en_md"] = (
                "**Shape of the binomial distribution:**\n"
                "- $p=0.5$: symmetric about $n/2$; $\\binom{n}{k}=\\binom{n}{n-k}$.\n"
                "- $p<0.5$: right-skewed — most probability mass at small $k$.\n"
                "- $p>0.5$: left-skewed — mass concentrates near $n$.\n"
                "- As $n$ increases, the PMF approaches a bell curve (normal limit / CLT).\n\n"
                "**Mode:** For integer $np$, the mode is $\\lfloor np\\rfloor$ or $\\lceil np\\rceil$; "
                "for $p=0.5$ and even $n$, the peak is at $k=n/2$.\n\n"
                "**Cumulative probabilities:**\n"
                "$$P(X\\leq k)=\\sum_{j=0}^{k}\\binom{n}{j}p^j(1-p)^{n-j}$$\n"
                "$$P(X\\geq k)=1-P(X\\leq k-1)$$\n"
                "$$P(a\\leq X\\leq b)=P(X\\leq b)-P(X\\leq a-1)$$\n\n"
                "**Complement shortcuts (exam speed):**\n"
                "- $P(X\\geq1)=1-(1-p)^n$ (at least one success)\n"
                "- $P(X=0)=(1-p)^n$ (all fail)\n"
                "- $P(X=n)=p^n$ (all succeed)\n\n"
                "**Symmetry trick:** If $X\\sim B(n,p)$, then $n-X\\sim B(n,1-p)$. "
                "Compute the smaller tail when $p$ is far from $0.5$."
            )
            s["body_he_md"] = (
                "**צורת הפילוג הבינומי:**\n"
                "- $p=0.5$: סימטרי סביב $n/2$; $\\binom{n}{k}=\\binom{n}{n-k}$.\n"
                "- $p<0.5$: מוטה ימינה — רוב המסה ב-$k$ קטנים.\n"
                "- $p>0.5$: מוטה שמאלה — מסה מתרכזת ליד $n$.\n"
                "- ככל ש-$n$ גדל, ה-PMF מתקרב לעקומת פעמון (גבול נורמלי / CLT).\n\n"
                "**שכיח:** כש-$np$ שלם, השכיח הוא $\\lfloor np\\rfloor$ או $\\lceil np\\rceil$; "
                "ל-$p=0.5$ ו-$n$ זוגי, השיא ב-$k=n/2$.\n\n"
                "**הסתברויות מצטברות:**\n"
                "$$P(X\\leq k)=\\sum_{j=0}^{k}\\binom{n}{j}p^j(1-p)^{n-j}$$\n"
                "$$P(X\\geq k)=1-P(X\\leq k-1)$$\n"
                "$$P(a\\leq X\\leq b)=P(X\\leq b)-P(X\\leq a-1)$$\n\n"
                "**קיצורי משלים (מהירות בבחינה):**\n"
                "- $P(X\\geq1)=1-(1-p)^n$\n"
                "- $P(X=0)=(1-p)^n$\n"
                "- $P(X=n)=p^n$\n\n"
                "**טריק סימטריה:** אם $X\\sim B(n,p)$, אז $n-X\\sim B(n,1-p)$. "
                "חשבו את הזנב הקטן יותר כש-$p$ רחוק מ-$0.5$."
            )
        elif k == "worked_example" and s.get("example_number") == 1:
            s["body_en_md"] = (
                "A multiple-choice quiz has 5 questions, each with 4 options (one correct). "
                "A student guesses randomly. What is the probability of getting exactly 2 correct?\n\n"
                "### Move 1: Verify BINS and identify parameters.\n"
                "Each question: success = correct guess, $p=1/4$. Fixed $n=5$, independent guesses. "
                "So $X\\sim B(5,0.25)$ and we want $P(X=2)$.\n\n"
                "### Move 2: Write the PMF.\n"
                "$$P(X=2)=\\binom{5}{2}(0.25)^2(0.75)^3.$$\n\n"
                "### Move 3: Evaluate.\n"
                "$$\\binom{5}{2}=10, \\quad (0.25)^2=0.0625, \\quad (0.75)^3=0.421875.$$\n"
                "$$P(X=2)=10\\times0.0625\\times0.421875=0.2637.$$\n\n"
                "**Mean check:** $\\mu=np=5\\times0.25=1.25$ correct answers expected by guessing — "
                "$k=2$ is above average but plausible.\n\n"
                "**Exam habit:** State what counts as success before substituting into the PMF."
            )
            s["body_he_md"] = (
                "חידון בחירה מרובה: 5 שאלות, 4 אפשרויות בכל אחת. תלמיד מנחש. "
                "מה ההסתברות לקבל בדיוק 2 נכונות?\n\n"
                "### צעד 1: אימות BINS וזיהוי פרמטרים.\n"
                "בכל שאלה: הצלחה = ניחוש נכון, $p=1/4$. $n=5$ קבוע, ניחושים בלתי-תלויים. "
                "לכן $X\\sim B(5,0.25)$ ורוצים $P(X=2)$.\n\n"
                "### צעד 2: כתיבת PMF.\n"
                "$$P(X=2)=\\binom{5}{2}(0.25)^2(0.75)^3.$$\n\n"
                "### צעד 3: חישוב.\n"
                "$$\\binom{5}{2}=10, \\quad P(X=2)=10\\times0.0625\\times0.421875=0.2637.$$\n\n"
                "**בדיקת ממוצע:** $\\mu=1.25$ — $k=2$ מעל הממוצע אך סביר.\n\n"
                "**הרגל לבחינה:** הגדירו מה נחשב הצלחה לפני הצבה ב-PMF."
            )
        elif k == "worked_example" and s.get("example_number") == 2:
            s["body_en_md"] = (
                "A quality inspector checks 8 items. Each item has a 20% chance of being defective. "
                "Find the probability that **at most 2** are defective.\n\n"
                "### Move 1: Model.\n"
                "$X\\sim B(8,0.2)$ with success = defective. Want $P(X\\leq2)=P(X=0)+P(X=1)+P(X=2)$.\n\n"
                "### Move 2: Compute each PMF term.\n"
                "$$P(X=0)=(0.8)^8=0.1678.$$\n"
                "$$P(X=1)=\\binom{8}{1}(0.2)^1(0.8)^7=8\\times0.2\\times0.2097=0.3355.$$\n"
                "$$P(X=2)=\\binom{8}{2}(0.2)^2(0.8)^6=28\\times0.04\\times0.2621=0.2936.$$\n\n"
                "### Move 3: Sum.\n"
                "$$P(X\\leq2)=0.1678+0.3355+0.2936=0.7969.$$\n\n"
                "**Conclusion:** About 79.7% chance at most 2 defective. "
                "**Sanity check:** With $p=0.2$, mean $\\mu=1.6$ — most mass at 0, 1, 2."
            )
            s["body_he_md"] = (
                "מפקח בודק 8 פריטים. כל פריט בהסתברות 20% פגום. "
                "מצא הסתברות ש**לכל היותר 2** פגומים.\n\n"
                "### צעד 1: מודל.\n"
                "$X\\sim B(8,0.2)$, הצלחה = פגום. $P(X\\leq2)=P(X=0)+P(X=1)+P(X=2)$.\n\n"
                "### צעד 2: חישוב כל איבר.\n"
                "$$P(X=0)=0.8^8=0.1678.$$\n"
                "$$P(X=1)=8\\times0.2\\times0.8^7=0.3355.$$\n"
                "$$P(X=2)=28\\times0.04\\times0.8^6=0.2936.$$\n\n"
                "### צעד 3: סכום.\n"
                "$$P(X\\leq2)=0.7969.$$\n\n"
                "**מסקנה:** כ-79.7% לכל היותר 2 פגומים. **בדיקה:** $\\mu=1.6$ — רוב המסה ב-0,1,2."
            )
        elif k == "worked_example" and s.get("example_number") == 3:
            s["body_en_md"] = (
                "A coin is flipped 4 times. The probability of **exactly 3 heads** equals "
                "the probability of **exactly 2 heads**. Find $p$.\n\n"
                "### Move 1: Write PMF expressions.\n"
                "$$P(X=3)=\\binom{4}{3}p^3(1-p)=4p^3(1-p).$$\n"
                "$$P(X=2)=\\binom{4}{2}p^2(1-p)^2=6p^2(1-p)^2.$$\n\n"
                "### Move 2: Set equal and simplify.\n"
                "$$4p^3(1-p)=6p^2(1-p)^2.$$\n"
                "For $0<p<1$, divide by $2p^2(1-p)$: $2p=3(1-p)$.\n\n"
                "### Move 3: Solve.\n"
                "$$5p=3 \\Rightarrow p=0.6.$$\n\n"
                "**Check:** $P(X=3)=P(X=2)=0.3456$. ✓\n\n"
                "**Exam note:** When equating PMFs, cancel common factors carefully — "
                "exclude $p=0$ and $p=1$ as non-physical solutions."
            )
            s["body_he_md"] = (
                "מטבע מוטל 4 פעמים. $P(X=3)=P(X=2)$. מצא $p$.\n\n"
                "### צעד 1: כתיבת PMF.\n"
                "$$P(X=3)=4p^3(1-p), \\quad P(X=2)=6p^2(1-p)^2.$$\n\n"
                "### צעד 2: השוואה ופישוט.\n"
                "$$4p^3(1-p)=6p^2(1-p)^2.$$\n"
                "ל-$0<p<1$, חלוקה ב-$2p^2(1-p)$: $2p=3(1-p)$.\n\n"
                "### צעד 3: פתרון.\n"
                "$$p=0.6.$$\n\n"
                "**בדיקה:** $P(X=3)=P(X=2)=0.3456$. ✓\n\n"
                "**הערת בחינה:** בטלו גורמים משותפים בזהירות — דחו $p=0,1$."
            )
        elif k == "checkpoint" and "basketball" in s.get("body_en_md", "").lower() or "70%" in s.get("body_en_md", ""):
            s["checkpoint_solution_en"] = (
                "**Step 1 — Model:** Each free throw is a Bernoulli trial with $p=0.7$. "
                "Four independent throws: $X\\sim B(4,0.7)$.\n\n"
                "**Step 2 — All four in means $k=4$:**\n"
                "$$P(X=4)=\\binom{4}{4}(0.7)^4(0.3)^0=(0.7)^4=0.2401.$$\n\n"
                "**Check:** $\\binom{4}{4}=1$ and $(0.3)^0=1$, so only $p^4$ remains. "
                "Mean $\\mu=2.8$ — getting all four is above average but not extreme."
            )
            s["checkpoint_solution_he"] = (
                "**שלב 1 — מודל:** כל זריקה = ניסוי ברנולי עם $p=0.7$. "
                "4 זריקות בלתי-תלויות: $X\\sim B(4,0.7)$.\n\n"
                "**שלב 2 — כולן נכנסות = $k=4$:**\n"
                "$$P(X=4)=(0.7)^4=0.2401.$$\n\n"
                "**בדיקה:** $\\binom{4}{4}=1$ ו-$(0.3)^0=1$, נשאר רק $p^4$. "
                "ממוצע $\\mu=2.8$ — כולן נכנסות מעל הממוצע אך לא קיצוני."
            )
        elif k == "checkpoint" and "B(6, 0.3)" in s.get("body_en_md", ""):
            s["checkpoint_solution_en"] = (
                "**Step 1 — Model:** $X\\sim B(6,0.3)$ counts successes in 6 trials.\n\n"
                "**Step 2 — Complement for \"at least one\":**\n"
                "$$P(X\\geq1)=1-P(X=0)=1-(0.7)^6=1-0.1176=0.8824.$$\n\n"
                "**Check:** $P(X=0)$ is the probability all six fail — much faster than summing five terms."
            )
            s["checkpoint_solution_he"] = (
                "**שלב 1 — מודל:** $X\\sim B(6,0.3)$ סופר הצלחות ב-6 ניסויים.\n\n"
                "**שלב 2 — משלים ל\"לפחות אחת\":**\n"
                "$$P(X\\geq1)=1-(0.7)^6=0.8824.$$\n\n"
                "**בדיקה:** $P(X=0)$ = כולם נכשלים — מהיר הרבה יותר מסכימת חמישה איברים."
            )
        elif k == "method_guide":
            s["body_en_md"] = (
                "**Binomial problem protocol:**\n"
                "1. **Verify BINS** — write one line per letter; stop if any fails.\n"
                "2. **Identify** $n$, $p$, and what counts as success.\n"
                "3. **Classify** the question: exact $P(X=k)$, cumulative $P(X\\leq k)$, "
                "tail $P(X\\geq k)$, or interval $P(a\\leq X\\leq b)$.\n"
                "4. **Choose method:** direct PMF, sum terms, complement, or symmetry $n-X$.\n"
                "5. **Compute** and sanity-check against $\\mu=np$.\n\n"
                "| Problem type | Method |\n|---|---|\n"
                "| Exactly $k$ | PMF formula |\n"
                "| At most $k$ | Sum $P(X=0)+\\cdots+P(X=k)$ |\n"
                "| At least 1 | $1-(1-p)^n$ |\n"
                "| Between $a$ and $b$ | Sum or $P(X\\leq b)-P(X\\leq a-1)$ |\n\n"
                "**Useful identities:** $\\binom{n}{0}=\\binom{n}{n}=1$; $\\binom{n}{1}=n$; "
                "$\\binom{n}{2}=n(n-1)/2$; $\\binom{n}{k}=\\binom{n}{n-k}$."
            )
            s["body_he_md"] = (
                "**פרוטוקול בעיות בינומיות:**\n"
                "1. **אמת BINS** — שורה לכל אות; עצרו אם אחד נכשל.\n"
                "2. **זהו** $n$, $p$ ומה נחשב הצלחה.\n"
                "3. **סווגו:** מדויק $P(X=k)$, מצטבר $P(X\\leq k)$, "
                "זנב $P(X\\geq k)$, או טווח $P(a\\leq X\\leq b)$.\n"
                "4. **בחרו שיטה:** PMF ישיר, סכימה, משלים, או סימטריה $n-X$.\n"
                "5. **חשבו** ובדקו מול $\\mu=np$.\n\n"
                "| סוג בעיה | שיטה |\n|---|---|\n"
                "| בדיוק $k$ | נוסחת PMF |\n"
                "| לכל היותר $k$ | סכום $P(X=0)+\\cdots+P(X=k)$ |\n"
                "| לפחות 1 | $1-(1-p)^n$ |\n"
                "| בין $a$ ל-$b$ | סכום או $P(X\\leq b)-P(X\\leq a-1)$ |\n\n"
                "**זהויות שימושיות:** $\\binom{n}{0}=1$; $\\binom{n}{1}=n$; "
                "$\\binom{n}{2}=n(n-1)/2$; $\\binom{n}{k}=\\binom{n}{n-k}$."
            )
        elif k == "pitfall":
            s["body_en_md"] = (
                "1. **Forgetting $\\binom{n}{k}$.** The PMF is not just $p^k(1-p)^{n-k}$ — "
                "you must count how many arrangements produce exactly $k$ successes.\n\n"
                "2. **Sampling without replacement.** Drawing from a small finite population without replacement "
                "violates independence → use the **hypergeometric** distribution, not binomial.\n\n"
                "3. **Confusing $P(X=k)$ with $P(X\\leq k)$.** "
                "Underline \"exactly,\" \"at most,\" \"at least,\" or \"between\" before calculating.\n\n"
                "4. **Skipping the complement.** $P(X\\geq1)=1-(1-p)^n$ saves time; "
                "summing $P(X=1)+\\cdots+P(X=n)$ invites arithmetic errors.\n\n"
                "5. **Reversed exponents.** $P(X=k)=p^k(1-p)^{n-k}$: $k$ successes, $n-k$ failures — not the other way.\n\n"
                "6. **Using binomial when $n$ is not fixed.** "
                "If trials continue until a success (geometric) or events arrive in time (Poisson), BINS fails."
            )
            s["body_he_md"] = (
                "1. **שכחת $\\binom{n}{k}$.** ה-PMF הוא לא רק $p^k(1-p)^{n-k}$ — "
                "חובה לספור כמה סידורים נותנים בדיוק $k$ הצלחות.\n\n"
                "2. **דגימה ללא החזרה.** שליפה מאוכלוסייה סופית קטנה ללא החזרה מפרה בלתי-תלות → "
                "**פילוג היפרגיאומטרי**, לא בינומי.\n\n"
                "3. **בלבול $P(X=k)$ עם $P(X\\leq k)$.** "
                "סמנו \"בדיוק\", \"לכל היותר\", \"לפחות\" או \"בין\" לפני החישוב.\n\n"
                "4. **דילוג על המשלים.** $P(X\\geq1)=1-(1-p)^n$ חוסך זמן; "
                "סכימת $P(X=1)+\\cdots$ מזמינה טעויות חשבון.\n\n"
                "5. **חזקות הפוכות.** $P(X=k)=p^k(1-p)^{n-k}$: $k$ הצלחות, $n-k$ כישלונות.\n\n"
                "6. **בינומי כש-$n$ לא קבוע.** "
                "אם הניסויים ממשיכים עד הצלחה (גיאומטרי) או אירועים בזמן (פואסון), BINS נכשל."
            )
        elif k == "why_matters":
            s["body_en_md"] = (
                "The binomial model is the workhorse of **count data** across science and industry. "
                "Quality engineers use $B(n,p)$ to set acceptance sampling rules; "
                "clinical researchers model treatment success rates across fixed cohorts; "
                "pollsters estimate vote shares from yes/no survey responses.\n\n"
                "**Connections in the KG:**\n"
                "- `lesson:probability_basics_3pt` — sample spaces and independence underpin BINS.\n"
                "- `lesson:discrete_distributions_binomial_poisson` — Poisson limit and normal approximation.\n"
                "- `lesson:statistics_inference` — confidence intervals and tests for proportions use $\\hat p$ and $B(n,p)$ logic.\n\n"
                "**Exam transfer:** Every word problem starts by asking \"Is this a fixed-$n$ count of successes?\" "
                "If yes, write $X\\sim B(n,p)$ before any arithmetic."
            )
            s["body_he_md"] = (
                "המודל הבינומי הוא כלי העבודה של **נתוני ספירה** במדע ובתעשייה. "
                "מהנדסי איכות משתמשים ב-$B(n,p)$ לכללי דגימת קבלה; "
                "חוקרים קlinיים מדגמים שיעורי הצלחת טיפול בקבוצות קבועות; "
                "סוקרים מעריכים נתחי הצבעה מתשובות כן/לא.\n\n"
                "**קשרים ב-KG:**\n"
                "- `lesson:probability_basics_3pt` — מרחבי מדגם ובלתי-תלות תומכים ב-BINS.\n"
                "- `lesson:discrete_distributions_binomial_poisson` — גבול פואסון וקירוב נורמלי.\n"
                "- `lesson:statistics_inference` — רווחי סמך ובדיקות לפרופורציות.\n\n"
                "**העברה בבחינה:** כל בעיה מילולית מתחילה ב\"האם זו ספירת הצלחות ב-$n$ קבוע?\" "
                "אם כן — כתבו $X\\sim B(n,p)$ לפני כל חישוב."
            )
        elif k == "before_exam":
            s["body_en_md"] = (
                "**Formula card:**\n"
                "- $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$\n"
                "- $\\mu=np$, $\\sigma^2=np(1-p)$, $\\sigma=\\sqrt{np(1-p)}$\n"
                "- $P(X\\geq1)=1-(1-p)^n$; $P(X=0)=(1-p)^n$; $P(X=n)=p^n$\n"
                "- $P(a\\leq X\\leq b)=P(X\\leq b)-P(X\\leq a-1)$\n\n"
                "**Exam patterns:**\n"
                "- Direct PMF for given $k$.\n"
                "- Cumulative $P(X\\leq k)$ or tail $P(X\\geq k)$ — sum or complement.\n"
                "- Find unknown $p$ or $n$ from equal probabilities.\n"
                "- Verify BINS; identify when hypergeometric or Poisson applies instead.\n\n"
                "**Last review:** Recite formulas once, then solve both checkpoints without notes."
            )
            s["body_he_md"] = (
                "**גיליון נוסחאות:**\n"
                "- $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$\n"
                "- $\\mu=np$, $\\sigma^2=np(1-p)$\n"
                "- $P(X\\geq1)=1-(1-p)^n$; $P(X=0)=(1-p)^n$; $P(X=n)=p^n$\n"
                "- $P(a\\leq X\\leq b)=P(X\\leq b)-P(X\\leq a-1)$\n\n"
                "**דגשי מבחן:**\n"
                "- PMF ישיר ל-$k$ נתון.\n"
                "- מצטבר $P(X\\leq k)$ או זנב $P(X\\geq k)$ — סכום או משלים.\n"
                "- מציאת $p$ או $n$ מהשוואת הסתברויות.\n"
                "- אימות BINS; מתי היפרגיאומטרי או פואסון.\n\n"
                "**חזרה אחרונה:** אמרו נוסחאות פעם אחת, ואז פתרו את שני ה-checkpoints בלי רשימות."
            )
        elif k == "summary":
            s["body_en_md"] = (
                "- **Bernoulli trial:** one experiment, success probability $p$, failure $1-p$.\n"
                "- **Binomial $B(n,p)$:** counts successes in $n$ independent identical trials.\n"
                "- **PMF:** $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$; mean $np$; variance $np(1-p)$.\n"
                "- **Cumulative:** sum PMF terms, use complement, or interval formula $P(X\\leq b)-P(X\\leq a-1)$.\n"
                "- **BINS** must hold; otherwise consider hypergeometric, geometric, or Poisson models.\n"
                "- **Shape:** symmetric at $p=0.5$; skewed otherwise; approaches normal as $n$ grows."
            )
            s["body_he_md"] = (
                "- **ניסוי ברנולי:** ניסוי בודד, הצלחה $p$, כישלון $1-p$.\n"
                "- **בינומי $B(n,p)$:** ספירת הצלחות ב-$n$ ניסויים בלתי-תלויים זהים.\n"
                "- **PMF:** $P(X=k)=\\binom{n}{k}p^k(1-p)^{n-k}$; ממוצע $np$; שונות $np(1-p)$.\n"
                "- **מצטבר:** סכום איברי PMF, משלים, או $P(X\\leq b)-P(X\\leq a-1)$.\n"
                "- **BINS** חייבים להתקיים; אחרת — היפרגיאומטרי, גיאומטרי או פואסון.\n"
                "- **צורה:** סימטרי ב-$p=0.5$; מוטה אחרת; מתקרב לנורמלי כש-$n$ גדל."
            )


def fix_hebrew_typos(text: str) -> str:
    return text.replace("קlinיים", "קליניים")


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    patch_sections(data["sections"])
    for s in data["sections"]:
        for key in ("body_he_md", "checkpoint_solution_he"):
            if key in s:
                s[key] = fix_hebrew_typos(s[key])

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPL_EN:
            q["explanation_en"] = EXPL_EN[ord_]
        if ord_ in EXPL_HE:
            q["explanation_he"] = EXPL_HE[ord_]

    # Fix e9 corrupted char in exercise set
    for s in data["sections"]:
        if s.get("kind") == "exercise_set":
            for ex in s.get("exercises", []):
                if ex["id"] == "e9":
                    ex["solution_en"] = (
                        "$\\binom{n}{2}=\\binom{n}{3}$ (since $p=0.5$ cancels). "
                        "$n(n-1)/2 = n(n-1)(n-2)/6$. Divide: $1=(n-2)/3$. So $n=5$."
                    )

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
