#!/usr/bin/env python3
"""Expand electric_circuits.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/electric_circuits.json"


def word_count(text):
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


EXPLANATIONS = {
    1: {
        "en": (
            "Ohm's law relates voltage, current, and resistance in a single resistor: "
            "$V = IR$. When a battery drives current through a resistor, the resistance "
            "determines how much current flows for a given voltage.\n\n"
            "**Solution:** $R = V/I = 12/3 = \\boxed{4\\,\\Omega}$.\n\n"
            "Rearrange to $R = V/I$ because resistance is the ratio of voltage drop to "
            "current through that element. With $V = 12$ V and $I = 3$ A, "
            "$R = 4\\,\\Omega$.\n\n"
            "**Common wrong path:** Dividing $I/V$ instead of $V/I$, giving "
            "$0.25\\,\\Omega$ — resistance must have units of volts per ampere (ohms).\n\n"
            "**Exam tip:** Always write $R = V/I$ first, substitute, then check: "
            "$V = IR = 4 \\times 3 = 12$ V ✓. Bagrut electricity questions often give "
            "two of three quantities; identify which form of Ohm's law to use."
        ),
        "he": (
            "חוק אוהם מקשר מתח, זרם והתנגדות בנגד בודד: $V = IR$. כשסוללה מניעה זרם "
            "דרך נגד, ההתנגדות קובעת כמה זרם יזרום ל מתח נתון.\n\n"
            "**פתרון:** $R = V/I = 12/3 = \\boxed{4\\,\\Omega}$.\n\n"
            "מסדרים ל-$R = V/I$ כי התנגדות היא יחס נפילת מתח לזרם. עם $V = 12$ V "
            "ו-$I = 3$ A, $R = 4\\,\\Omega$.\n\n"
            "**טעות נפוצה:** חלוקת $I/V$ במקום $V/I$ — התנגדות חייבת להיות ביחידות "
            "וולט/אמפר (אוהם).\n\n"
            "**טיפ לבחינה:** כתבו $R = V/I$, הציבו, ובדקו: $V = IR = 4 \\times 3 = 12$ V ✓. "
            "בשאלון 2 נותנים לעיתים שני מתוך שלושה — זהו איזו צורה של חוק אוהם ליישם."
        ),
    },
    2: {
        "en": (
            "Power dissipated in a resistor converts electrical energy to heat. When current "
            "$I$ and resistance $R$ are both known for the same resistor, "
            "$P = I^2 R$ is the safest formula — it uses quantities that belong to that "
            "single element.\n\n"
            "**Solution:** $P = I^2 R = 2^2 \\times 10 = 4 \\times 10 = \\boxed{40\\text{ W}}$.\n\n"
            "Alternative check: $V = IR = 20$ V, then $P = IV = 20 \\times 2 = 40$ W ✓.\n\n"
            "**Common wrong path:** Using $P = V^2/R$ with the battery voltage instead of "
            "the voltage across this specific resistor, or mixing branch current with "
            "total circuit voltage in $P = IV$.\n\n"
            "**Exam tip:** On Bagrut, write which power formula you choose and why. "
            "$P = I^2R$ avoids the \"wrong V\" trap when multiple resistors share a circuit."
        ),
        "he": (
            "הספק המתפזר בנגד ממיר אנרגיה חשמלית לחום. כשזרם $I$ והתנגדות $R$ ידועים "
            "לאותו נגד, $P = I^2 R$ היא הנוסחה הבטוחה — משתמשת בגדלים של אותו רכיב.\n\n"
            "**פתרון:** $P = I^2 R = 4 \\times 10 = \\boxed{40\\text{ W}}$.\n\n"
            "בדיקה חלופית: $V = IR = 20$ V, אז $P = IV = 40$ W ✓.\n\n"
            "**טעות נפוצה:** שימוש ב-$P = V^2/R$ עם מתח הסוללה במקום מתח על הנגד, "
            "או ערבוב זרם ענף עם מתח כולל ב-$P = IV$.\n\n"
            "**טיפ לבחינה:** בבגרות, כתבו איזו נוסחת הספק בחרתם ולמה. "
            "$P = I^2R$ נמנעת ממלכודת \"מתח שגוי\" כשיש כמה נגדים."
        ),
    },
    3: {
        "en": (
            "A light bulb rated 60 W at 120 V means it dissipates 60 W when the voltage "
            "across it is 120 V. From $P = IV$, find current first; then Ohm's law gives "
            "resistance.\n\n"
            "**Step 1 — Current:** $I = P/V = 60/120 = \\boxed{0.5\\text{ A}}$.\n\n"
            "**Step 2 — Resistance:** $R = V/I = 120/0.5 = \\boxed{240\\,\\Omega}$.\n\n"
            "**Check:** $P = I^2 R = 0.25 \\times 240 = 60$ W ✓.\n\n"
            "**Common wrong path:** Computing $R = P/V = 0.5\\,\\Omega$ — that confuses "
            "power with voltage. Resistance is $V/I$, not $P/V$.\n\n"
            "**Exam tip:** Appliance ratings (\"60 W, 120 V\") appear frequently on "
            "Bagrut questionnaire 2. Always find $I$ from $P = IV$ before applying "
            "$R = V/I$."
        ),
        "he": (
            "נורה המדורגת 60 W ב-120 V מתפזר בה 60 W כשהמתח עליה 120 V. "
            "מ-$P = IV$ מוצאים זרם קודם; אחר כך חוק אוהם נותן התנגדות.\n\n"
            "**שלב 1 — זרם:** $I = P/V = 60/120 = \\boxed{0.5\\text{ A}}$.\n\n"
            "**שלב 2 — התנגדות:** $R = V/I = 120/0.5 = \\boxed{240\\,\\Omega}$.\n\n"
            "**בדיקה:** $P = I^2 R = 0.25 \\times 240 = 60$ W ✓.\n\n"
            "**טעות נפוצה:** חישוב $R = P/V = 0.5\\,\\Omega$ — מבלבל הספק עם מתח. "
            "התנגדות היא $V/I$, לא $P/V$.\n\n"
            "**טיפ לבחינה:** דירוגי מכשירים (\"60 W, 120 V\") מופיעים הרבה בשאלון 2. "
            "תמיד מצאו $I$ מ-$P = IV$ לפני $R = V/I$."
        ),
    },
    4: {
        "en": (
            "Resistors in parallel each provide an independent path for current. The "
            "equivalent resistance is always **smaller** than any individual resistor "
            "because more paths mean less overall opposition.\n\n"
            "**Formula:** $1/R_{\\text{eq}} = 1/R_1 + 1/R_2 + 1/R_3$.\n\n"
            "**Calculation:**\n"
            "$$\\frac{1}{R_{\\text{eq}}} = \\frac{1}{2} + \\frac{1}{3} + \\frac{1}{6} "
            "= \\frac{3}{6} + \\frac{2}{6} + \\frac{1}{6} = \\frac{6}{6} = 1 "
            "\\Rightarrow R_{\\text{eq}} = \\boxed{1\\,\\Omega}$$\n\n"
            "**Common wrong path:** Adding resistances directly ($2+3+6=11\\,\\Omega$) "
            "as if they were in series. Parallel uses reciprocals.\n\n"
            "**Exam tip:** For three resistors, find a common denominator for "
            "$1/R_1 + 1/R_2 + 1/R_3$. When all three values share a common multiple "
            "(2, 3, 6 → LCM 6), the arithmetic simplifies cleanly."
        ),
        "he": (
            "נגדים במקביל נותנים לכל אחד מסלול זרם עצמאי. ההתנגדות השקולה תמיד **קטנה** "
            "מכל נגד בודד — יותר מסלולים = פחות התנגדות כוללת.\n\n"
            "**נוסחה:** $1/R_{\\text{שקול}} = 1/R_1 + 1/R_2 + 1/R_3$.\n\n"
            "**חישוב:**\n"
            "$$\\frac{1}{R_{\\text{שקול}}} = \\frac{1}{2} + \\frac{1}{3} + \\frac{1}{6} "
            "= \\frac{6}{6} = 1 \\Rightarrow R_{\\text{שקול}} = \\boxed{1\\,\\Omega}$$\n\n"
            "**טעות נפוצה:** חיבור ישיר ($2+3+6=11\\,\\Omega$) כאילו בטור. במקביל "
            "משתמשים במנגדים.\n\n"
            "**טיפ לבחינה:** לשלושה נגדים, מצאו מכנה משותף ל-$1/R_1 + 1/R_2 + 1/R_3$. "
            "כש-2, 3, 6 חולקים כפולה משותפת (6), החשבון מתפשט."
        ),
    },
    5: {
        "en": (
            "Mixed series-parallel circuits require simplifying from the inside out. "
            "First combine series groups, then parallel groups, until one $R_{\\text{eq}}$ "
            "remains.\n\n"
            "**Step 1 — Series pair:** $R_{12} = R_1 + R_2 = 6 + 12 = 18\\,\\Omega$.\n\n"
            "**Step 2 — Parallel with $R_3$:**\n"
            "$$R_{\\text{eq}} = \\frac{R_{12} \\cdot R_3}{R_{12} + R_3} "
            "= \\frac{18 \\times 9}{27} = \\boxed{6\\,\\Omega}$$\n\n"
            "**Step 3 — Total current:** $I = V/R_{\\text{eq}} = 18/6 = \\boxed{3\\text{ A}}$.\n\n"
            "**Common wrong path:** Adding all three resistances ($27\\,\\Omega$) or "
            "treating the series pair as parallel with $R_3$ using the wrong formula.\n\n"
            "**Exam tip:** Redraw the circuit after each simplification step. "
            "Bagrut graders award points for showing $R_{12}$ before $R_{\\text{eq}}$."
        ),
        "he": (
            "מעגלים מעורבי טור-מקביל דורשים פישוט מבפנים החוצה. קודם מצרפים קבוצות "
            "טור, אחר כך מקביל, עד שנשאר $R_{\\text{שקול}}$ אחד.\n\n"
            "**שלב 1 — זוג בטור:** $R_{12} = 6 + 12 = 18\\,\\Omega$.\n\n"
            "**שלב 2 — מקביל עם $R_3$:**\n"
            "$$R_{\\text{שקול}} = \\frac{18 \\times 9}{27} = \\boxed{6\\,\\Omega}$$\n\n"
            "**שלב 3 — זרם כולל:** $I = 18/6 = \\boxed{3\\text{ A}}$.\n\n"
            "**טעות נפוצה:** חיבור שלושת הנגדים ($27\\,\\Omega$) או טיפול בזוג הטור "
            "כמקביל עם נוסחה שגויה.\n\n"
            "**טיפ לבחינה:** שרטטו מחדש אחרי כל שלב פישוט. בבגרות נותנים נקודות "
            "על הצגת $R_{12}$ לפני $R_{\\text{שקול}}$."
        ),
    },
    6: {
        "en": (
            "Real batteries have internal resistance $r$. The EMF $\\varepsilon$ is the "
            "ideal voltage; under load, terminal voltage drops by $Ir$.\n\n"
            "**Step 1 — Current:** Total resistance is external plus internal:\n"
            "$$I = \\frac{\\varepsilon}{R + r} = \\frac{12}{5 + 1} = \\boxed{2\\text{ A}}$$\n\n"
            "**Step 2 — Terminal voltage:**\n"
            "$$V_{\\text{term}} = \\varepsilon - Ir = 12 - 2(1) = \\boxed{10\\text{ V}}$$\n\n"
            "Alternative: $V_{\\text{term}} = IR = 2 \\times 5 = 10$ V ✓.\n\n"
            "**Common wrong path:** Using $\\varepsilon$ alone in $I = V/R$ (ignoring $r$), "
            "or computing terminal voltage as $\\varepsilon + Ir$ instead of minus.\n\n"
            "**Exam tip:** When a stem mentions \"internal resistance,\" immediately add "
            "$r$ to the total resistance in the denominator. Terminal voltage is always "
            "less than EMF when the battery supplies current."
        ),
        "he": (
            "לסוללות אמיתיות יש התנגדות פנימית $r$. כ\"א $\\varepsilon$ הוא המתח האידיאלי; "
            "תחת עומס, מתח המסוף יורד ב-$Ir$.\n\n"
            "**שלב 1 — זרם:** התנגדות כוללת = חיצונית + פנימית:\n"
            "$$I = \\frac{\\varepsilon}{R + r} = \\frac{12}{6} = \\boxed{2\\text{ A}}$$\n\n"
            "**שלב 2 — מתח מסוף:**\n"
            "$$V_{\\text{מסוף}} = \\varepsilon - Ir = 12 - 2 = \\boxed{10\\text{ V}}$$\n\n"
            "חלופה: $V_{\\text{מסוף}} = IR = 10$ V ✓.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\varepsilon$ בלבד ב-$I = V/R$ (התעלמות מ-$r$), "
            "או חישוב $\\varepsilon + Ir$ במקום מינוס.\n\n"
            "**טיפ לבחינה:** כשמוזכרת \"התנגדות פנימית\", הוסיפו $r$ למכנה. "
            "מתח מסוף תמיד קטן מ-EMF כשהסוללה מספקת זרם."
        ),
    },
    7: {
        "en": (
            "This problem combines parallel and series simplification. Two identical "
            "$6\\,\\Omega$ resistors in parallel give half the individual value; "
            "the third resistor is in series with that combination.\n\n"
            "**Step 1 — Parallel pair:** $R_{\\parallel} = \\frac{6 \\times 6}{6 + 6} "
            "= 3\\,\\Omega$.\n\n"
            "**Step 2 — Total resistance:** $R_{\\text{eq}} = 3 + 6 = 9\\,\\Omega$ "
            "(series with third resistor).\n\n"
            "**Step 3 — Current through third resistor:** In series, the same current "
            "flows everywhere: $I = V/R_{\\text{eq}} = 24/9 = \\boxed{8/3\\text{ A}}$.\n\n"
            "**Step 4 — Power in third resistor:** $P = I^2 R = (8/3)^2 \\times 6 "
            "\\approx \\boxed{42.7\\text{ W}}$.\n\n"
            "**Common wrong path:** Using $I = V/R = 24/6 = 4$ A (ignoring the parallel "
            "pair's contribution to total resistance).\n\n"
            "**Exam tip:** After finding $I$, work backward to get branch currents and "
            "voltages across the parallel section if the question asks for them."
        ),
        "he": (
            "בעיה זו משלבת פישוט מקביל וטור. שני נגדים זהים $6\\,\\Omega$ במקביל נותנים "
            "חצי מהערך; הנגד השלישי בטור עם השילוב.\n\n"
            "**שלב 1 — זוג מקביל:** $R_{\\parallel} = 3\\,\\Omega$.\n\n"
            "**שלב 2 — התנגדות כוללת:** $R_{\\text{שקול}} = 3 + 6 = 9\\,\\Omega$.\n\n"
            "**שלב 3 — זרם דרך השלישי:** בטור, אותו זרם בכל מקום: "
            "$I = 24/9 = \\boxed{8/3\\text{ A}}$.\n\n"
            "**שלב 4 — הספק בנגד השלישי:** $P = I^2 R \\approx \\boxed{42.7\\text{ W}}$.\n\n"
            "**טעות נפוצה:** $I = 24/6 = 4$ A — התעלמות מתרומת זוג המקביל.\n\n"
            "**טיפ לבחינה:** אחרי מציאת $I$, חזרו אחורה לזרמי ענפים ומתחים "
            "בקטע המקביל אם נדרש."
        ),
    },
    8: {
        "en": (
            "When two batteries oppose each other in a single loop, the net EMF is the "
            "difference, not the sum. KVL accounts for each voltage rise and drop "
            "consistently around the closed path.\n\n"
            "**Setup:** Assume current $I$ flows in the direction of $\\varepsilon_1$. "
            "Both resistors are in series with $I$.\n\n"
            "**KVL (clockwise):**\n"
            "$$\\varepsilon_1 - \\varepsilon_2 = I(R_1 + R_2)$$\n"
            "$$12 - 6 = I(4 + 8) \\Rightarrow 6 = 12I \\Rightarrow I = \\boxed{0.5\\text{ A}}$$\n\n"
            "The positive result confirms current flows in the assumed direction "
            "(dominated by the larger battery).\n\n"
            "**Common wrong path:** Adding both EMFs ($18$ V) instead of subtracting, "
            "or forgetting that opposing batteries reduce net driving voltage.\n\n"
            "**Exam tip:** Label battery terminals and mark each EMF as $+\\varepsilon$ "
            "or $-\\varepsilon$ based on traversal direction. Sign errors in KVL are "
            "the top reason for lost points on Bagrut loop problems."
        ),
        "he": (
            "כששתי סוללות מתנגדות בלולאה אחת, כ\"א נטו הוא ההפרש, לא הסכום. "
            "KVL מחשב כל עלייה וירידת מתח סביב המסלול הסגור.\n\n"
            "**הכנה:** נניח זרם $I$ בכיוון $\\varepsilon_1$. שני הנגדים בטור עם $I$.\n\n"
            "**KVL (עם כיוון השעון):**\n"
            "$$\\varepsilon_1 - \\varepsilon_2 = I(R_1 + R_2)$$\n"
            "$$12 - 6 = 12I \\Rightarrow I = \\boxed{0.5\\text{ A}}$$\n\n"
            "תוצאה חיובית — הזרם בכיוון ההנחה (מונע על ידי הסוללה הגדולה).\n\n"
            "**טעות נפוצה:** חיבור שני כ\"א ($18$ V) במקום חיסור, או שכחה "
            "שסוללות נגדיות מקטינות מתח מניע.\n\n"
            "**טיפ לבחינה:** סמנו קטבי סוללה ו-$+\\varepsilon$/$-\\varepsilon$ לפי "
            "כיוון המעבר. שגיאות סימן ב-KVL — הסיבה העיקרית לאובדן נקודות בבגרות."
        ),
    },
}


def build_sections():
    return [
        {
            "kind": "intro",
            "title_en": "Why Circuit Analysis Matters",
            "title_he": "מדוע ניתוח מעגלים חשוב",
            "body_en_md": (
                "Electric circuits power every device in our lives — phones, lights, cars, "
                "and hospital equipment all rely on controlled current flow. Understanding "
                "how voltage distributes and how current splits at junctions is essential "
                "for both Bagrut Physics (questionnaire 2 — electricity) and engineering.\n\n"
                "**Bagrut relevance (questionnaire 2 — electricity):**\n"
                "- *'Find total current through a circuit'*\n"
                "- *'Find voltage across each resistor'*\n"
                "- *'Calculate power dissipated'*\n"
                "- *'Find unknown resistance in a balanced Wheatstone bridge'*\n\n"
                "**Key quantities:**\n\n"
                "| Quantity | Symbol | SI Unit |\n"
                "|---|---|---|\n"
                "| Voltage (EMF) | $V$ | Volt (V) |\n"
                "| Current | $I$ | Ampere (A) |\n"
                "| Resistance | $R$ | Ohm ($\\Omega$) |\n"
                "| Power | $P$ | Watt (W) |\n"
                "| Charge | $Q$ | Coulomb (C) |\n"
                "| Time | $t$ | second (s) |\n\n"
                "**Water analogy:** Voltage is like water pressure, current is flow rate, "
                "and resistance is pipe narrowness. A narrow pipe (high $R$) reduces flow "
                "($I$) for the same pressure ($V$). This analogy helps intuition but "
                "always verify with $V = IR$.\n\n"
                "This lesson builds on `concept:electric_potential` and unlocks "
                "`concept:kirchhoff_laws` and `concept:ac_circuits`."
            ),
            "body_he_md": (
                "מעגלים חשמליים מפעילים כל מכשיר בחיינו — טלפונים, תאורה, רכבים "
                "וציוד רפואי — כולם מסתמכים על זרימת זרם מבוקרת. הבנת חלוקת מתח "
                "ופיצול זרם בצמתים חיונית לבגרות בפיזיקה (שאלון 2 — חשמל) ולהנדסה.\n\n"
                "**רלוונטיות לבגרות (שאלון 2 — חשמל):**\n"
                "- *'מצא זרם כולל במעגל'*\n"
                "- *'מצא מתח על כל נגד'*\n"
                "- *'חשב הספק שמתפזר'*\n"
                "- *'מצא התנגדות לא ידועה בגשר ווטסטון מאוזן'*\n\n"
                "**גדלים מפתח:**\n\n"
                "| גודל | סמל | יחידת SI |\n"
                "|---|---|---|\n"
                "| מתח (כ\"א) | $V$ | וולט (V) |\n"
                "| זרם | $I$ | אמפר (A) |\n"
                "| התנגדות | $R$ | אוהם ($\\Omega$) |\n"
                "| הספק | $P$ | וואט (W) |\n"
                "| מטען | $Q$ | קולomb (C) |\n"
                "| זמן | $t$ | שנייה (s) |\n\n"
                "**דימוי מים:** מתח כמו לחץ מים, זרם כמו קצב זרימה, התנגדות כמו "
                "צמצום צינור. צינור צר ($R$ גבוה) מקטין זרימה ($I$) לאותו לחץ ($V$). "
                "הדימוי עוזר להבנה הראשונית אך תמיד אמתו עם $V = IR$.\n\n"
                "שיעור זה מבוסס על `concept:electric_potential` ופותח את "
                "`concept:kirchhoff_laws` ו-`concept:ac_circuits`."
            ),
        },
        {
            "kind": "definition",
            "title_en": "Ohm's Law, Series, Parallel, and Power",
            "title_he": "חוק אוהם, טור, מקביל, והספק",
            "body_en_md": (
                "**Ohm's Law** relates voltage, current, and resistance for a conductor "
                "at constant temperature:\n"
                "$$\\boxed{V = IR}$$\n\n"
                "Rearrangements: $I = V/R$, $R = V/I$. Units: $1\\,\\Omega = 1\\,\\text{V/A}$.\n\n"
                "**Resistance in Series** (same current through each branch element):\n"
                "$$\\boxed{R_{\\text{eq}} = R_1 + R_2 + R_3 + \\cdots}$$\n"
                "Voltages add: $V_{\\text{total}} = V_1 + V_2 + \\cdots$. "
                "The largest resistor drops the most voltage.\n\n"
                "**Resistance in Parallel** (same voltage across each branch):\n"
                "$$\\boxed{\\frac{1}{R_{\\text{eq}}} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\cdots}$$\n"
                "For two resistors: $R_{\\text{eq}} = \\frac{R_1 R_2}{R_1 + R_2}$. "
                "Currents add: $I_{\\text{total}} = I_1 + I_2 + \\cdots$.\n\n"
                "**Power** (rate of energy conversion, SI unit: watt):\n"
                "$$\\boxed{P = IV = I^2 R = \\frac{V^2}{R}}$$\n"
                "**Energy:** $E = Pt = IVt$ (joules).\n\n"
                "**Kirchhoff's Laws (preview):**\n"
                "- **KCL:** $\\sum I_{\\text{in}} = \\sum I_{\\text{out}}$ at every junction.\n"
                "- **KVL:** $\\sum V = 0$ around any closed loop.\n\n"
                "These laws solve circuits that are neither pure series nor pure parallel."
            ),
            "body_he_md": (
                "**חוק אוהם** מקשר מתח, זרם והתנגדות במוליך בתנאי טמפרatura קבועה:\n"
                "$$\\boxed{V = IR}$$\n\n"
                "צורות: $I = V/R$, $R = V/I$. יחידות: $1\\,\\Omega = 1\\,\\text{V/A}$.\n\n"
                "**התנגדות בטור** (אותו זרם בכל רכיב):\n"
                "$$\\boxed{R_{\\text{שקול}} = R_1 + R_2 + \\cdots}$$\n"
                "מתחים מסתכמים: $V_{\\text{כולל}} = V_1 + V_2 + \\cdots$. "
                "הנגד הגדול ביותר יורד בו הכי הרבה מתח.\n\n"
                "**התנגדות במקביל** (אותו מתח על כל ענף):\n"
                "$$\\boxed{\\frac{1}{R_{\\text{שקול}}} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\cdots}$$\n"
                "לשניים: $R_{\\text{שקול}} = \\frac{R_1 R_2}{R_1+R_2}$. "
                "זרמים מסתכמים: $I_{\\text{כולל}} = I_1 + I_2 + \\cdots$.\n\n"
                "**הספק** (קצב המרת אנרגיה, יחידה: וואט):\n"
                "$$\\boxed{P = IV = I^2 R = V^2/R}$$\n"
                "**אנרגיה:** $E = Pt = IVt$ (J).\n\n"
                "**חוקי קירכהוף (תצוגה מקדימה):**\n"
                "- **KCL:** $\\sum I_{\\text{נכנסים}} = \\sum I_{\\text{יוצאים}}$ בכל צומת.\n"
                "- **KVL:** $\\sum V = 0$ בכל לולאה סגורה.\n\n"
                "חוקים אלה פותרים מעגלים שאינם טור או מקביל טהורים."
            ),
        },
        {
            "kind": "theory",
            "title_en": "Applying Kirchhoff's Laws and Internal Resistance",
            "title_he": "יישום חוקי קירכהוף והתנגדות פנימית",
            "body_en_md": (
                "When series/parallel simplification fails, Kirchhoff's laws provide a "
                "systematic path. Bagrut multi-loop problems use the same sign conventions "
                "every time — learn them once, apply everywhere.\n\n"
                "### Procedure for KVL\n\n"
                "1. Assign current directions to each branch (a wrong guess gives a "
                "negative answer — magnitude is still correct).\n"
                "2. Traverse each loop consistently (clockwise is standard).\n"
                "3. Resistor: $+IR$ if traversing **against** current; $-IR$ if **with** "
                "current (voltage drop).\n"
                "4. Battery: $+\\varepsilon$ crossing from $-$ to $+$; $-\\varepsilon$ "
                "from $+$ to $-$.\n"
                "5. Write one KVL equation per independent loop.\n"
                "6. Use KCL at junctions to reduce unknowns.\n\n"
                "### Internal Resistance\n\n"
                "Real batteries have internal resistance $r$. Under load:\n"
                "$$\\boxed{V_{\\text{terminal}} = \\varepsilon - Ir}$$\n"
                "Terminal voltage is always less than EMF when supplying current. "
                "Short-circuit current: $I_{\\max} = \\varepsilon/r$.\n\n"
                "### Wheatstone Bridge\n\n"
                "Four resistors in a diamond. Balanced (no galvanometer current):\n"
                "$$\\boxed{\\frac{R_1}{R_2} = \\frac{R_3}{R_X}} \\Rightarrow "
                "R_X = \\frac{R_2 R_3}{R_1}$$\n\n"
                "### Combining Series and Parallel\n\n"
                "Strategy: simplify from innermost combination outward.\n"
                "1. Find equivalent of parallel groups.\n"
                "2. Add series resistors.\n"
                "3. Repeat until one $R_{\\text{eq}}$ remains.\n"
                "4. Use $I = V/R_{\\text{eq}}$ for total current.\n"
                "5. Work backward for individual branch currents and voltages."
            ),
            "body_he_md": (
                "כשפישוט טור/מקביל נכשל, חוקי קירכהוף מספקים נתיב שיטתי. "
                "בעיות בגרות מרובות לולאות משתמשות באותן מוסכמות סימן — "
                "למדו פעם אחת, יישמו בכל מקום.\n\n"
                "### שיטה ל-KVL\n\n"
                "1. הקצו כיווני זרם לכל ענף (ניחוש שגוי נותן תשובה שלילית — "
                "העוצמה עדיין נכונה).\n"
                "2. עברו בכל לולאה בעקביות (עם כיוון השעון סטנדרטי).\n"
                "3. נגד: $+IR$ במעבר **נגד** הזרם; $-IR$ **עם** הזרם (ירידת מתח).\n"
                "4. סוללה: $+\\varepsilon$ ממינוס לפלוס; $-\\varepsilon$ מפלוס למינוס.\n"
                "5. כתבו משוואת KVL לכל לולאה עצמאית.\n"
                "6. השתמשו ב-KCL בצמתים לצמצום נעלמים.\n\n"
                "### התנגדות פנימית\n\n"
                "לסוללות אמיתיות יש $r$ פנימית. תחת עומס:\n"
                "$$\\boxed{V_{\\text{מסוף}} = \\varepsilon - Ir}$$\n"
                "מתח מסוף תמיד קטן מ-EMF כשמספקים זרם. "
                "זרם קצר: $I_{\\max} = \\varepsilon/r$.\n\n"
                "### גשר ווטסטון\n\n"
                "ארבעה נגדים בתצורת יהלום. מאוזן (אין זרם בגלוונומטר):\n"
                "$$\\boxed{\\frac{R_1}{R_2} = \\frac{R_3}{R_X}} \\Rightarrow "
                "R_X = \\frac{R_2 R_3}{R_1}$$\n\n"
                "### שילוב טור ומקביל\n\n"
                "אסטרategיה: פישוט מהשילוב הפנימי ביותר החוצה.\n"
                "1. מצאו שקול של קבוצות מקביל.\n"
                "2. חברו נגדי טור.\n"
                "3. חזרו עד $R_{\\text{שקול}}$ אחד.\n"
                "4. $I = V/R_{\\text{שקול}}$ לזרם כולל.\n"
                "5. חזרו אחורה לזרמים ומתחים בודדים."
            ),
        },
    ]


def patch_file():
    data = json.loads(OUT.read_text(encoding="utf-8"))

    # Replace first three sections
    new_sections = build_sections()
    for i, sec in enumerate(new_sections):
        data["sections"][i] = sec

    # Patch worked example 1
    data["sections"][3]["body_en_md"] = (
        "**Given:** $R_1 = 4\\,\\Omega$ and $R_2 = 6\\,\\Omega$ in series with a "
        "20 V battery (negligible internal resistance).\n\n"
        "**Find:** (a) Total current. (b) Voltage across each resistor.\n\n"
        "In a series circuit, the same current flows through every element. "
        "Total resistance is the sum; total voltage divides in proportion to "
        "each resistor's value.\n\n"
        "### Move 1 — Equivalent resistance\n"
        "$$R_{\\text{eq}} = R_1 + R_2 = 4 + 6 = 10\\,\\Omega$$\n\n"
        "### Move 2 — Total current (Ohm's law)\n"
        "$$I = \\frac{V}{R_{\\text{eq}}} = \\frac{20}{10} = \\boxed{2\\text{ A}}$$\n\n"
        "### Move 3 — Voltage across each resistor\n"
        "$$V_1 = IR_1 = 2 \\times 4 = \\boxed{8\\text{ V}}, \\quad "
        "V_2 = IR_2 = 2 \\times 6 = \\boxed{12\\text{ V}}$$\n\n"
        "**Check:** $V_1 + V_2 = 8 + 12 = 20\\text{ V}$ ✓ (KVL on the loop).\n\n"
        "**Bagrut note:** The larger resistor ($6\\,\\Omega$) drops more voltage "
        "($12$ V vs $8$ V). This proportional division appears in nearly every "
        "series circuit question on questionnaire 2."
    )
    data["sections"][3]["body_he_md"] = (
        "**נתון:** $R_1=4\\,\\Omega$ ו-$R_2=6\\,\\Omega$ בטור עם סוללה 20 V "
        "(התנגדות פנימית זניחה).\n\n"
        "**מצא:** (א) זרם כולל. (ב) מתח על כל נגד.\n\n"
        "במעגל טור, אותו זרם זורם בכל רכיב. ההתנגדות הכוללת היא הסכום; "
        "המתח מתחלק ביחס לערך כל נגד.\n\n"
        "### צעד 1 — התנגדות שקולה\n"
        "$$R_{\\text{שקול}} = 4+6 = 10\\,\\Omega$$\n\n"
        "### צעד 2 — זרם כולל\n"
        "$$I = 20/10 = \\boxed{2\\text{ A}}$$\n\n"
        "### צעד 3 — מתחים\n"
        "$$V_1 = 2\\times4 = \\boxed{8\\text{ V}}, \\quad V_2 = 2\\times6 = \\boxed{12\\text{ V}}$$\n\n"
        "**בדיקה:** $8+12=20\\text{ V}$ ✓ (KVL על הלולאה).\n\n"
        "**הערת בגרות:** הנגד הגדול ($6\\,\\Omega$) יורד בו יותר מתח "
        "($12$ V לעומת $8$ V). חלוקה יחסית זו מופיעה בכמעט כל שאלת טור בשאלון 2."
    )

    # Checkpoint 1
    data["sections"][4]["checkpoint_solution_en"] = (
        "Three resistors in series: $R_1=2\\,\\Omega$, $R_2=3\\,\\Omega$, "
        "$R_3=5\\,\\Omega$, connected to 30 V.\n\n"
        "**Step 1 — Total resistance:**\n"
        "$$R_{\\text{eq}} = 2 + 3 + 5 = 10\\,\\Omega$$\n\n"
        "**Step 2 — Total current:**\n"
        "$$I = \\frac{V}{R_{\\text{eq}}} = \\frac{30}{10} = \\boxed{3\\text{ A}}$$\n\n"
        "**Step 3 — Voltage across $R_3$:**\n"
        "$$V_3 = IR_3 = 3 \\times 5 = \\boxed{15\\text{ V}}$$\n\n"
        "**Check:** $V_1=6$ V, $V_2=9$ V, $V_3=15$ V; sum $= 30$ V ✓."
    )
    data["sections"][4]["checkpoint_solution_he"] = (
        "שלושה נגדים בטור: $R_1=2\\,\\Omega$, $R_2=3\\,\\Omega$, $R_3=5\\,\\Omega$, "
        "מחוברים ל-30 V.\n\n"
        "**שלב 1 — התנגדות כוללת:**\n"
        "$$R_{\\text{שקול}} = 2+3+5 = 10\\,\\Omega$$\n\n"
        "**שלב 2 — זרם כולל:**\n"
        "$$I = 30/10 = \\boxed{3\\text{ A}}$$\n\n"
        "**שלב 3 — מתח על $R_3$:**\n"
        "$$V_3 = 3 \\times 5 = \\boxed{15\\text{ V}}$$\n\n"
        "**בדיקה:** $V_1=6$ V, $V_2=9$ V, $V_3=15$ V; סכום $= 30$ V ✓."
    )

    # Worked example 2
    data["sections"][5]["body_en_md"] = (
        "**Given:** $R_1 = 6\\,\\Omega$ and $R_2 = 3\\,\\Omega$ in **parallel** "
        "across a 12 V source.\n\n"
        "**Find:** (a) Equivalent resistance. (b) Total current. "
        "(c) Power in each resistor.\n\n"
        "Parallel branches share the same voltage. Each branch current is "
        "independent; total current is the sum.\n\n"
        "### Move 1 — Equivalent resistance\n"
        "$$R_{\\text{eq}} = \\frac{R_1 R_2}{R_1 + R_2} = \\frac{6 \\times 3}{9} "
        "= \\boxed{2\\,\\Omega}$$\n\n"
        "### Move 2 — Total current\n"
        "$$I_{\\text{total}} = \\frac{V}{R_{\\text{eq}}} = \\frac{12}{2} "
        "= \\boxed{6\\text{ A}}$$\n\n"
        "### Move 3 — Branch currents\n"
        "$$I_1 = \\frac{V}{R_1} = 2\\text{ A}, \\quad I_2 = \\frac{V}{R_2} = 4\\text{ A}$$"
        " ($I_1+I_2=6\\text{ A}$ ✓)\n\n"
        "### Move 4 — Power dissipation\n"
        "$$P_1 = I_1^2 R_1 = 24\\text{ W}, \\quad P_2 = I_2^2 R_2 = 48\\text{ W}, "
        "\\quad P_{\\text{total}} = VI = 72\\text{ W}$$ ✓\n\n"
        "**Key insight:** The smaller resistor ($3\\,\\Omega$) carries more current "
        "and dissipates more power — parallel circuits favor the path of least resistance."
    )
    data["sections"][5]["body_he_md"] = (
        "**נתון:** $R_1=6\\,\\Omega$ ו-$R_2=3\\,\\Omega$ **במקביל** מול 12 V.\n\n"
        "**מצא:** (א) התנגדות שקולה. (ב) זרם כולל. (ג) הספק בכל נגד.\n\n"
        "ענפים מקבילים חולקים אותו מתח. זרם כל ענף עצמאי; הזרם הכולל הוא הסכום.\n\n"
        "### צעד 1 — התנגדות שקולה\n"
        "$$R_{\\text{שקול}} = \\frac{6\\times3}{9} = \\boxed{2\\,\\Omega}$$\n\n"
        "### צעד 2 — זרם כולל\n"
        "$$I_{\\text{כולל}} = 12/2 = \\boxed{6\\text{ A}}$$\n\n"
        "### צעד 3 — זרמי ענפים\n"
        "$$I_1 = 2\\text{ A}, \\quad I_2 = 4\\text{ A}$$ ($I_1+I_2=6\\text{ A}$ ✓)\n\n"
        "### צעד 4 — הספק\n"
        "$$P_1=24\\text{ W}, \\quad P_2=48\\text{ W}, \\quad P_{\\text{כולל}}=72\\text{ W}$$ ✓\n\n"
        "**תובנה:** הנגד הקטן ($3\\,\\Omega$) נושא יותר זרם ומתפזר בו יותר הספק — "
        "מעגלים מקבילים מעדיפים מסלול של פחות התנגדות."
    )

    # Checkpoint 2
    data["sections"][6]["checkpoint_solution_en"] = (
        "Two resistors $R_1=4\\,\\Omega$ and $R_2=12\\,\\Omega$ in parallel across 24 V.\n\n"
        "**Step 1 — Equivalent resistance:**\n"
        "$$R_{\\text{eq}} = \\frac{4 \\times 12}{4 + 12} = \\frac{48}{16} "
        "= \\boxed{3\\,\\Omega}$$\n\n"
        "**Step 2 — Total current:**\n"
        "$$I = \\frac{V}{R_{\\text{eq}}} = \\frac{24}{3} = \\boxed{8\\text{ A}}$$\n\n"
        "**Step 3 — Total power:**\n"
        "$$P = VI = 24 \\times 8 = \\boxed{192\\text{ W}}$$\n\n"
        "**Check:** $I_1=6$ A, $I_2=2$ A; $P_1=144$ W + $P_2=48$ W $= 192$ W ✓."
    )
    data["sections"][6]["checkpoint_solution_he"] = (
        "שני נגדים $R_1=4\\,\\Omega$ ו-$R_2=12\\,\\Omega$ במקביל מול 24 V.\n\n"
        "**שלב 1 — התנגדות שקולה:**\n"
        "$$R_{\\text{שקול}} = \\frac{48}{16} = \\boxed{3\\,\\Omega}$$\n\n"
        "**שלב 2 — זרם כולל:**\n"
        "$$I = 24/3 = \\boxed{8\\text{ A}}$$\n\n"
        "**שלב 3 — הספק כולל:**\n"
        "$$P = 24 \\times 8 = \\boxed{192\\text{ W}}$$\n\n"
        "**בדיקה:** $I_1=6$ A, $I_2=2$ A; $P_1=144$ W + $P_2=48$ W $= 192$ W ✓."
    )

    # Worked example 3
    data["sections"][7]["body_en_md"] = (
        "**Given:** Wheatstone bridge: $R_1=10\\,\\Omega$, $R_2=15\\,\\Omega$, "
        "$R_3=20\\,\\Omega$, unknown $R_X$. Bridge is balanced (zero galvanometer current).\n\n"
        "**Find:** $R_X$.\n\n"
        "At balance, the potential at both galvanometer terminals is equal. "
        "The ratio of resistances on one side equals the ratio on the other.\n\n"
        "### Move 1 — Balance condition\n"
        "$$\\frac{R_1}{R_2} = \\frac{R_3}{R_X}$$\n\n"
        "### Move 2 — Solve for $R_X$\n"
        "$$R_X = \\frac{R_2 \\times R_3}{R_1} = \\frac{15 \\times 20}{10} "
        "= \\boxed{30\\,\\Omega}$$\n\n"
        "**Derivation sketch:** At balance, voltage dividers on both arms give equal "
        "midpoint potentials: $\\frac{R_3}{R_1+R_3} = \\frac{R_X}{R_2+R_X}$. "
        "Cross-multiplying yields $R_3 R_2 = R_X R_1$.\n\n"
        "**Bagrut note:** Wheatstone bridge questions typically ask only for $R_X$ "
        "using the ratio formula — memorize $\\frac{R_1}{R_2} = \\frac{R_3}{R_X}$, "
        "not a sum formula."
    )
    data["sections"][7]["body_he_md"] = (
        "**נתון:** גשר ווטסטון: $R_1=10\\,\\Omega$, $R_2=15\\,\\Omega$, "
        "$R_3=20\\,\\Omega$, $R_X=?$. הגשר מאוזן (אפס זרם בגלוונומטר).\n\n"
        "**מצא:** $R_X$.\n\n"
        "באיזון, הפוטנציאל בשני קצות הגלוונומטר שווה. "
        "יחס ההתנגדויות בצד אחד שווה ליחס בצד השני.\n\n"
        "### צעד 1 — תנאי איזון\n"
        "$$\\frac{R_1}{R_2} = \\frac{R_3}{R_X}$$\n\n"
        "### צעד 2 — פתרון\n"
        "$$R_X = \\frac{15\\times20}{10} = \\boxed{30\\,\\Omega}$$\n\n"
        "**סקיצת גזירה:** באיזון, מחלקי מתח בשני הענפים נותנים פוטנציאל אמצעי שווה: "
        "$\\frac{R_3}{R_1+R_3} = \\frac{R_X}{R_2+R_X}$. "
        "כפל צולב נותן $R_3 R_2 = R_X R_1$.\n\n"
        "**הערת בגרות:** שאלות גשר ווטסטון בדרך כלל מבקשות רק $R_X$ "
        "בנוסחת היחס — שמרו $\\frac{R_1}{R_2} = \\frac{R_3}{R_X}$, לא נוסחת סכום."
    )

    # Method guide
    data["sections"][8]["body_en_md"] = (
        "Use this step-by-step approach for every circuit problem on Bagrut:\n\n"
        "1. **Draw the circuit diagram** clearly. Label all components, nodes, and "
        "given values. Mark battery polarity ($+$ and $-$).\n"
        "2. **Classify connections:** pure series? pure parallel? mixed? "
        "If mixed, identify innermost groups first.\n"
        "3. **Simplify series/parallel combinations** from innermost outward until "
        "one $R_{\\text{eq}}$ remains (or until Kirchhoff is needed).\n"
        "4. **Apply Ohm's law** for total current: $I = V/R_{\\text{eq}}$.\n"
        "5. **Work backward** to find individual currents and voltages:\n"
        "   - Series branch: same $I$ everywhere; $V_i = IR_i$.\n"
        "   - Parallel branch: same $V$ across each; $I_i = V/R_i$.\n"
        "6. **Calculate power** if needed: $P = I^2R$ (safest — uses local $I$ and $R$).\n"
        "7. **For Kirchhoff problems:** assign branch currents → write KCL → "
        "write KVL → solve the linear system.\n"
        "8. **Verify:** KVL around every loop; KCL at every junction; "
        "power supplied = power dissipated."
    )
    data["sections"][8]["body_he_md"] = (
        "השתמשו בגישה שלב-אחר-שלב לכל בעיית מעגל בבגרות:\n\n"
        "1. **שרטוט מעגל** ברור. תייגו רכיבים, צמתים וערכים. סמנו קטבי סוללה.\n"
        "2. **סיווג חיבורים:** טור טהור? מקביל טהור? מעורב? "
        "אם מעורב, זהו קבוצות פנימיות קודם.\n"
        "3. **פישוט טור/מקביל** מבפנים החוצה עד $R_{\\text{שקול}}$ אחד "
        "(או עד שצריך קירכהוף).\n"
        "4. **חוק אוהם** לזרם כולל: $I = V/R_{\\text{שקול}}$.\n"
        "5. **עבודה אחורה** לזרמים ומתחים:\n"
        "   - ענף טור: אותו $I$; $V_i = IR_i$.\n"
        "   - ענף מקביל: אותו $V$; $I_i = V/R_i$.\n"
        "6. **חישוב הספק:** $P = I^2R$ (הבטוחה — $I$ ו-$R$ מקומיים).\n"
        "7. **לקירכהוף:** הקצו זרמי ענף → KCL → KVL → פתרו מערכת.\n"
        "8. **אימות:** KVL בכל לולאה; KCL בכל צומת; הספק מסופק = מתפזר."
    )

    # Pitfall - expand
    idx_pitfall = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "pitfall")
    data["sections"][idx_pitfall]["body_en_md"] = (
        "1. **Adding parallel resistors like series.** For parallel: "
        "$1/R_{\\text{eq}} = \\sum 1/R_i$, NOT $R_1 + R_2$. "
        "Parallel equivalent is always **smaller** than the smallest resistor.\n\n"
        "2. **Equal current in parallel branches.** Parallel branches share the same "
        "**voltage**, not the same current. The smaller resistor carries more current.\n\n"
        "3. **Using $P = IV$ with wrong quantities.** Match $I$ and $V$ to the **same** "
        "resistor. Safer: $P = I^2R$ when you know the branch current.\n\n"
        "4. **Ignoring internal resistance.** Real batteries: "
        "$V_{\\text{terminal}} = \\varepsilon - Ir$. Under load, terminal voltage drops.\n\n"
        "5. **KVL sign errors.** Battery $-$ to $+$: add $+\\varepsilon$. "
        "Resistor with current: add $-IR$ (drop). Inconsistent signs give wrong currents.\n\n"
        "6. **Wrong Wheatstone bridge formula.** It's $R_1/R_2 = R_3/R_X$ (ratio), "
        "not a sum. Derive from equal midpoint potentials if unsure.\n\n"
        "7. **Stopping at $R_{\\text{eq}}$ without working backward.** Many Bagrut "
        "questions ask for voltage across one specific resistor — require a second step."
    )
    data["sections"][idx_pitfall]["body_he_md"] = (
        "1. **חיבור נגדים מקבילים כמו טור.** במקביל: $1/R_{\\text{שקול}} = \\sum 1/R_i$, "
        "לא $R_1+R_2$. שקול מקביל תמיד **קטן** מהנגד הקטן ביותר.\n\n"
        "2. **זרם שווה בענפים מקבילים.** ענפים מקבילים חולקים **מתח** שווה, לא זרם. "
        "הנגד הקטן נושא יותר זרם.\n\n"
        "3. **$P=IV$ עם גדלים שגויים.** התאימו $I$ ו-$V$ ל**אותו** נגד. "
        "בטוח יותר: $P = I^2R$ כשיודעים זרם ענף.\n\n"
        "4. **התעלמות מהתנגדות פנימית.** $V_{\\text{מסוף}} = \\varepsilon - Ir$. "
        "תחת עומס, מתח מסוף יורד.\n\n"
        "5. **שגיאות סימן ב-KVL.** סוללה ממינוס לפלוס: $+\\varepsilon$. "
        "נגד עם זרם: $-IR$. סימנים לא עקביים → זרמים שגויים.\n\n"
        "6. **נוסחת גשר ווטסטון שגויה.** $R_1/R_2 = R_3/R_X$ (יחס), לא סכום.\n\n"
        "7. **עצירה ב-$R_{\\text{שקול}}$ בלי חזרה אחורה.** הרבה שאלות בגרות "
        "מבקשות מתח על נגד ספציפי — דורש שלב שני."
    )

    # before_exam - expand HE
    idx_exam = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "before_exam")
    data["sections"][idx_exam]["body_he_md"] = (
        "### דף נוסחאות\n\n"
        "$$V=IR \\quad R_{\\text{טור}}=\\sum R_i \\quad "
        "\\frac{1}{R_{\\text{מקביל}}}=\\sum\\frac{1}{R_i} \\quad P=IV=I^2R=V^2/R$$\n\n"
        "$$V_{\\text{מסוף}}=\\varepsilon-Ir \\quad "
        "\\frac{R_1}{R_2}=\\frac{R_3}{R_X}\\text{ (גשר מאוזן)}$$\n\n"
        "### רשימת בדיקה\n"
        "- [ ] טור/מקביל זוהה נכון?\n"
        "- [ ] KCL על כל הצמתים?\n"
        "- [ ] סימני KVL עקביים?\n"
        "- [ ] התנגדות פנימית נכללה?\n"
        "- [ ] נוסחת הספק מתאימה לגדלים הזמינים?\n\n"
        "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint אחד בלי להסתכל."
    )

    # Question explanations
    for q in data["questions"]:
        exp = EXPLANATIONS.get(q["ord"])
        if exp:
            q["explanation_en"] = exp["en"]
            q["explanation_he"] = exp["he"]

    data["author"] = "cursor-claude-2026"
    data["version"] = 2

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

    # Quick audit
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in ("intro", "definition", "theory", "worked_example", "pitfall",
                    "method_guide", "before_exam", "summary", "why_matters"):
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            print(f"  {kind}: EN={en_w} HE={he_w}")

    for q in data["questions"]:
        en_w = word_count(q.get("explanation_en", ""))
        he_w = word_count(q.get("explanation_he", ""))
        print(f"  Q{q['ord']} expl: EN={en_w} HE={he_w}")


if __name__ == "__main__":
    patch_file()
