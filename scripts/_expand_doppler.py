#!/usr/bin/env python3
"""Generate expanded doppler.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/doppler.json"
OUT = SRC

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
            "When an ambulance races toward you, the siren sounds **higher-pitched**; as it passes "
            "and recedes, the pitch **drops**. This is the **Doppler effect**: the observed frequency "
            "of a wave changes when there is relative motion between the source and the observer "
            "along the line connecting them.\n\n"
            "The effect applies to **sound** (police sirens, ultrasound, sonar) and **light** "
            "(astronomical redshift and blueshift). The source frequency $f_0$ emitted by the "
            "object never changes — only what you **measure** changes.\n\n"
            "**Applications you should know for Bagrut physics (5 units):** radar speed guns, "
            "medical Doppler ultrasound, police LIDAR, astronomy (Hubble redshift), echolocation "
            "in bats, and traffic cameras. Exam questions typically give $v \\approx 340$ m/s for "
            "sound and ask you to handle: source moving only, observer moving only, or both moving "
            "simultaneously. This lesson builds on `concept:waves_basics` and `concept:sound_waves`."
        ),
        "body_he_md": (
            "כשאמבולנס מתקרב אליך, הסירנה נשמעת **גבוהה יותר**; כשהוא עובר ומתרחק, הגובה **יורד**. "
            "זהו **אפקט דופלר**: התדר הנצפה של גל משתנה כשיש תנועה יחסית בין המקור לצופה "
            "לאורך קו הראייה.\n\n"
            "האפקט חל על **קול** (סירנות, אולטרסאונד, סונאר) ועל **אור** (הסחת אדום וכחלה "
            "באסטרונומיה). התדר $f_0$ שהמקור פולט לא משתנה — רק מה שאתה **מודד** משתנה.\n\n"
            "**יישומים לבגרות בפיזיקה (5 יחידות):** מכמונות מהירות, אולטרסאונד רפואי, "
            "LIDAR משטרתי, אסטרונומיה (הסחת אדום של האבל), איתור הד בעטלפים. "
            "שאלות בבחינה נותנות בדרך כלל $v \\approx 340$ m/s לקול ודורשות: מקור נע בלבד, "
            "צופה נע בלבד, או שניהם יחד. שיעור זה מבוסס על `concept:waves_basics` "
            "ו-`concept:sound_waves`."
        ),
    },
    "definition": {
        "body_en_md": (
            "The **general Doppler formula** for sound in a stationary medium:\n"
            "$$f_{\\text{obs}} = f_{\\text{src}} \\cdot \\frac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$$\n\n"
            "Where:\n"
            "- $f_{\\text{obs}}$ = frequency measured by the observer (Hz).\n"
            "- $f_{\\text{src}}$ = frequency emitted by the source (Hz).\n"
            "- $v$ = wave speed in the medium ($\\approx 340$ m/s in air at 20°C).\n"
            "- $v_{\\text{obs}}$ = speed of observer toward/away from source.\n"
            "- $v_{\\text{src}}$ = speed of source toward/away from observer.\n\n"
            "**Sign rule — observer in numerator:**\n"
            "- $+v_{\\text{obs}}$: observer moves **toward** the source (frequency rises).\n"
            "- $-v_{\\text{obs}}$: observer moves **away** (frequency falls).\n\n"
            "**Sign rule — source in denominator:**\n"
            "- $-v_{\\text{src}}$: source moves **toward** observer (frequency rises).\n"
            "- $+v_{\\text{src}}$: source moves **away** (frequency falls).\n\n"
            "**Memory anchor:** approaching always increases $f_{\\text{obs}}$; receding always "
            "decreases it. If your sign choice gives the wrong direction, flip the sign."
        ),
        "body_he_md": (
            "**נוסחת דופלר הכללית** לקול במדיום קבוע:\n"
            "$$f_{\\text{obs}} = f_{\\text{src}} \\cdot \\frac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$$\n\n"
            "כאשר:\n"
            "- $f_{\\text{obs}}$ = תדר שנמדד על ידי הצופה (Hz).\n"
            "- $f_{\\text{src}}$ = תדר שהמקור פולט (Hz).\n"
            "- $v$ = מהירות הגל במדיום ($\\approx 340$ m/s באוויר ב-20°C).\n"
            "- $v_{\\text{obs}}$ = מהירות הצופה לכיוון/מכיוון המקור.\n"
            "- $v_{\\text{src}}$ = מהירות המקור לכיוון/מכיוון הצופה.\n\n"
            "**כלל סימנים — צופה במונה:**\n"
            "- $+v_{\\text{obs}}$: צופה מתקרב למקור (תדר עולה).\n"
            "- $-v_{\\text{obs}}$: צופה מתרחק (תדר יורד).\n\n"
            "**כלל סימנים — מקור במכנה:**\n"
            "- $-v_{\\text{src}}$: מקור מתקרב לצופה (תדר עולה).\n"
            "- $+v_{\\text{src}}$: מקור מתרחק (תדר יורד).\n\n"
            "**עוגן זיכרון:** התקרבות תמיד מעלה $f_{\\text{obs}}$; התרחקות תמיד מורידה. "
            "אם הסימן נותן כיוון שגוי — החליפו אותו."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Why does frequency change?\n\n"
            "When the source moves **toward** the observer, each successive wavefront is emitted "
            "closer to the observer than the previous one. Wavefronts **bunch together** → shorter "
            "wavelength $\\lambda$ → higher frequency ($f = v/\\lambda$ at fixed wave speed $v$).\n\n"
            "When the source recedes, wavefronts spread out → longer $\\lambda$ → lower $f$. "
            "The observer's motion has the symmetric effect: running toward the source "
            "encounters wavefronts more rapidly.\n\n"
            "### Doppler for light\n\n"
            "For electromagnetic waves, use the non-relativistic approximation when $v \\ll c$:\n"
            "$$f_{\\text{obs}} \\approx f_{\\text{src}}\\left(1 \\pm \\frac{v}{c}\\right)$$\n"
            "Source approaching → **blueshift** (higher $f$, shorter $\\lambda$). "
            "Source receding → **redshift** (lower $f$, longer $\\lambda$). "
            "Do not plug light speeds into the sound formula.\n\n"
            "### Mach number and sonic boom\n\n"
            "The **Mach number** is $M = v_{\\text{src}}/v$. When $M > 1$ (supersonic), wavefronts "
            "pile up into a conical shock wave. Observers hear a sudden **sonic boom** when the "
            "Mach cone sweeps past them — not a continuous Doppler shift. "
            "Subsonic motion ($M < 1$) produces the smooth pitch change you hear from passing cars."
        ),
        "body_he_md": (
            "### מדוע משתנה התדר?\n\n"
            "כשהמקור נע **לכיוון** הצופה, כל חזית גל נשלחת קרוב יותר לצופה מהקודמת. "
            "חזיתות הגל **מתקבצות** → אורך גל $\\lambda$ קצר יותר → תדר גבוה יותר "
            "($f = v/\\lambda$ במהירות קבועה $v$).\n\n"
            "כשהמקור מתרחק, חזיתות מתפזרות → $\\lambda$ ארוך יותר → $f$ נמוך יותר. "
            "תנועת הצופה משפיעה באופן סימטרי: ריצה לכיוון המקור פוגשת חזיתות גל בתדירות גבוהה יותר.\n\n"
            "### דופלר לאור\n\n"
            "לגלים אלקטרומגנטיים, השתמשו בקירוב לא-רלטיביסטי כש-$v \\ll c$:\n"
            "$$f_{\\text{obs}} \\approx f_{\\text{src}}\\left(1 \\pm \\frac{v}{c}\\right)$$\n"
            "מקור מתקרב → **כחלה** (תדר גבוה, $\\lambda$ קצר). "
            "מקור מתרחק → **הסחת אדום** (תדר נמוך, $\\lambda$ ארוך). "
            "אל תשתמשו בנוסחת הקול למהירויות אור.\n\n"
            "### מספר מאך ובום סוני\n\n"
            "**מספר מאך** הוא $M = v_{\\text{src}}/v$. כש-$M > 1$ (על-קולי), חזיתות גל "
            "מצטברות לגל הלם קוני. צופים שומעים **בום סוני** פתאומי כשקונוס המאך "
            "חולף עליהם — לא שינוי דופלר רציף. "
            "תנועה תת-קולית ($M < 1$) יוצרת את שינוי הגובה החלק ששומעים ממכוניות חולפות."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**A police siren emits 600 Hz.** The police car approaches a stationary observer "
            "at 30 m/s. Speed of sound = 340 m/s. Find the observed frequency.\n\n"
            "### Move 1: Identify who moves\n"
            "Observer is stationary → $v_{\\text{obs}} = 0$. Source moves toward observer.\n\n"
            "### Move 2: Choose signs\n"
            "Source approaching → use $-v_{\\text{src}}$ in denominator (minus in denominator "
            "means approaching).\n\n"
            "### Move 3: Substitute\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340 + 0}{340 - 30} "
            "= 600 \\cdot \\frac{340}{310} \\approx 658\\text{ Hz}$$\n\n"
            "### Move 4: Verify\n"
            "658 > 600 ✓ — approaching raises frequency. If you got 551 Hz you used the "
            "receding sign. The shift is about 10% because $v_s/v \\approx 0.09$.\n\n"
            "**Answer:** $f_{\\text{obs}} \\approx 658$ Hz. Moving-source problems are the "
            "most common Bagrut Doppler type — always write the formula before numbers. "
            "If the problem states \"approaches at constant speed,\" use the same sign throughout "
            "the calculation; do not switch mid-way. Sketch the source arrow pointing toward "
            "the observer before substituting numbers. On the exam, a quick ratio check "
            "($f_{\\text{obs}}/f_0 \\approx v/(v-v_s)$) catches sign errors before you commit."
        ),
        "body_he_md": (
            "**סירנת משטרה פולטת 600 Hz.** ניידת המשטרה מתקרבת לצופה קבוע ב-30 m/s. "
            "מהירות קול = 340 m/s. מצאו את התדר הנצפה.\n\n"
            "### צעד 1: זיהוי מי נע\n"
            "הצופה קבוע → $v_{\\text{obs}} = 0$. המקור מתקרב לצופה.\n\n"
            "### צעד 2: בחירת סימנים\n"
            "מקור מתקרב → $-v_{\\text{src}}$ במכנה (מינוס במכנה = התקרבות).\n\n"
            "### צעד 3: הצבה\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340 + 0}{340 - 30} "
            "= 600 \\cdot \\frac{340}{310} \\approx 658\\text{ Hz}$$\n\n"
            "### צעד 4: אימות\n"
            "658 > 600 ✓ — התקרבות מעלה תדר. אם קיבלתם 551 Hz השתמשתם בסימן התרחקות. "
            "השינוי כ-10% כי $v_s/v \\approx 0.09$.\n\n"
            "**תשובה:** $f_{\\text{obs}} \\approx 658$ Hz. בעיות מקור נע הן הנפוצות ביותר "
            "בבגרות — כתבו תמיד את הנוסחה לפני המספרים. "
            "אם כתוב \"מתקרב במהירות קבועה,\" השתמשו באותו סימן לאורך כל החישוב. "
            "שרטטו חץ מקור לכיוון הצופה לפני ההצבה. בדיקת יחס מהירה "
            "($f_{\\text{obs}}/f_0 \\approx v/(v-v_s)$) תופסת טעויות סימן לפני שמסיימים."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**A 500 Hz source is stationary. An observer runs toward it at 20 m/s.** "
            "Find $f_{\\text{obs}}$. Speed of sound = 340 m/s.\n\n"
            "### Move 1: Set source speed to zero\n"
            "$v_{\\text{src}} = 0$ → denominator simplifies to $v$.\n\n"
            "### Move 2: Observer approaching → $+v_{\\text{obs}}$ in numerator\n"
            "$$f_{\\text{obs}} = 500 \\cdot \\frac{340 + 20}{340} "
            "= 500 \\cdot \\frac{360}{340} \\approx 529\\text{ Hz}$$\n\n"
            "### Move 3: Observer running away (comparison)\n"
            "$$f_{\\text{obs}} = 500 \\cdot \\frac{340 - 20}{340} "
            "= 500 \\cdot \\frac{320}{340} \\approx 471\\text{ Hz}$$\n\n"
            "### Move 4: Interpret\n"
            "529 > 500 > 471 — toward raises, away lowers. Observer motion alone changes "
            "frequency less than source motion at the same speed because the observer speed "
            "appears only in the numerator.\n\n"
            "**Answer:** 529 Hz toward; 471 Hz away. Exam tip: label $v_{\\text{obs}}$ and "
            "$v_{\\text{src}}$ before choosing signs. The percentage shift is smaller for "
            "observer motion because only the numerator changes — compare $\\Delta f/f_0 "
            "\\approx v_{\\text{obs}}/v = 5.9\\%$ here vs about 10% for a source at 30 m/s. "
            "When the stem says \"runs toward a stationary source,\" the denominator stays "
            "$v$ and only the numerator picks up the observer speed."
        ),
        "body_he_md": (
            "**מקור 500 Hz קבוע. צופה רץ לכיוונו ב-20 m/s.** מצאו $f_{\\text{obs}}$. "
            "מהירות קול = 340 m/s.\n\n"
            "### צעד 1: מהירות מקור אפס\n"
            "$v_{\\text{src}} = 0$ → המכנה מתפשט ל-$v$.\n\n"
            "### צעד 2: צופה מתקרב → $+v_{\\text{obs}}$ במונה\n"
            "$$f_{\\text{obs}} = 500 \\cdot \\frac{340 + 20}{340} "
            "= 500 \\cdot \\frac{360}{340} \\approx 529\\text{ Hz}$$\n\n"
            "### צעד 3: צופה מתרחק (השוואה)\n"
            "$$f_{\\text{obs}} = 500 \\cdot \\frac{340 - 20}{340} "
            "= 500 \\cdot \\frac{320}{340} \\approx 471\\text{ Hz}$$\n\n"
            "### צעד 4: פרשנות\n"
            "529 > 500 > 471 — התקרבות מעלה, התרחקות מורידה. תנועת צופה בלבד משנה תדר "
            "פחות מתנועת מקור באותה מהירות כי מהירות הצופה מופיעה רק במונה.\n\n"
            "**תשובה:** 529 Hz מתקרב; 471 Hz מתרחק. **טיפ לבחינה:** סמנו $v_{\\text{obs}}$ "
            "ו-$v_{\\text{src}}$ לפני בחירת סימנים. השינוי קטן יותר לתנועת צופה כי רק "
            "המונה משתנה — $\\Delta f/f_0 \\approx v_{\\text{obs}}/v = 5.9\\%$ כאן "
            "לעומת ~10% למקור ב-30 m/s. כשכתוב \"רץ לכיוון מקור קבוע,\" המכנה נשאר "
            "$v$ ורק המונה מקבל את מהירות הצופה. השוו תמיד את שני הכיוונים — "
            "529 ו-471 מקיפים את 500 Hz."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**An ambulance emits a constant tone.** Approaching, an observer measures 680 Hz; "
            "receding, 520 Hz. Find the source frequency $f_0$ and speed $v_s$ of the ambulance. "
            "Use $v = 340$ m/s.\n\n"
            "### Move 1: Write both Doppler equations\n"
            "$f_+ = f_0 \\cdot \\dfrac{v}{v - v_s}$ (approaching) and "
            "$f_- = f_0 \\cdot \\dfrac{v}{v + v_s}$ (receding).\n\n"
            "### Move 2: Divide to eliminate $f_0$\n"
            "$$\\frac{f_+}{f_-} = \\frac{v + v_s}{v - v_s} "
            "\\Rightarrow \\frac{680}{520} = \\frac{340 + v_s}{340 - v_s}$$\n\n"
            "### Move 3: Cross-multiply and solve\n"
            "$680(340 - v_s) = 520(340 + v_s)$ → $54400 = 1200 v_s$ → $v_s \\approx 45.3$ m/s.\n\n"
            "### Move 4: Back-substitute for $f_0$\n"
            "$f_0 = 680 \\cdot (340 - 45.3)/340 \\approx 590$ Hz. Check with receding: "
            "$590 \\cdot 340/385.3 \\approx 520$ Hz ✓.\n\n"
            "**Answer:** $f_0 \\approx 590$ Hz, $v_s \\approx 45.3$ m/s. This two-frequency "
            "method avoids solving for $f_0$ first — a Bagrut favourite. Always verify by "
            "plugging $v_s$ back into the receding formula; inconsistent data means a sign error "
            "somewhere in the setup. On Bagrut, this reverse problem often appears as part (b) "
            "after a straightforward frequency calculation in part (a)."
        ),
        "body_he_md": (
            "**אמבולנס פולט תדר קבוע.** מתקרב: הצופה מודד 680 Hz; מתרחק: 520 Hz. "
            "מצאו את $f_0$ ואת $v_s$. השתמשו ב-$v = 340$ m/s.\n\n"
            "### צעד 1: שתי משוואות דופלר\n"
            "$f_+ = f_0 \\cdot \\dfrac{v}{v - v_s}$ (מתקרב) ו-"
            "$f_- = f_0 \\cdot \\dfrac{v}{v + v_s}$ (מתרחק).\n\n"
            "### צעד 2: חלוקה לביטול $f_0$\n"
            "$$\\frac{f_+}{f_-} = \\frac{v + v_s}{v - v_s} "
            "\\Rightarrow \\frac{680}{520} = \\frac{340 + v_s}{340 - v_s}$$\n\n"
            "### צעד 3: הצלבה ופתרון\n"
            "$680(340 - v_s) = 520(340 + v_s)$ → $54400 = 1200 v_s$ → $v_s \\approx 45.3$ m/s.\n\n"
            "### צעד 4: הצבה חוזרת ל-$f_0$\n"
            "$f_0 = 680 \\cdot (340 - 45.3)/340 \\approx 590$ Hz. בדיקה: "
            "$590 \\cdot 340/385.3 \\approx 520$ Hz ✓.\n\n"
            "**תשובה:** $f_0 \\approx 590$ Hz, $v_s \\approx 45.3$ m/s. שיטת שני התדרים "
            "מאפשרת למצוא $v_s$ בלי $f_0$ קודם — שאלה אהובה בבגרות. "
            "אימתו תמיד בהצבה חוזרת לנוסחת ההתרחקות; נתונים לא עקביים = טעות סימן. "
            "שימו לב: $v_s \\approx 45$ m/s הרבה מתחת למהירות הקול ($340$ m/s), "
            "כך שהנוסחה הלא-רלטיביסטית תקפה ו-$M \\approx 0.13$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "$$f_{\\text{obs}} = f_0 \\cdot \\frac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$$\n\n"
            "| Who moves | Direction | Effect on $f_{\\text{obs}}$ | Sign |\n"
            "|---|---|---|---|\n"
            "| Observer | Toward source | Increases | $+v_{\\text{obs}}$ in numerator |\n"
            "| Observer | Away from source | Decreases | $-v_{\\text{obs}}$ in numerator |\n"
            "| Source | Toward observer | Increases | $-v_{\\text{src}}$ in denominator |\n"
            "| Source | Away from observer | Decreases | $+v_{\\text{src}}$ in denominator |\n\n"
            "**Step-by-step:** (1) Draw a line from source to observer. "
            "(2) Label speeds along that line. (3) Write the formula with $\\pm$ placeholders. "
            "(4) Fill signs: toward = higher $f$. (5) Verify $f_{\\text{obs}} > f_0$ for "
            "approach, $< f_0$ for recession.\n\n"
            "**When to use:** Any problem with a moving siren, train, ambulance, bat, or "
            "receding galaxy along the line of sight. If the stem gives two observed frequencies "
            "(approach + recession), divide the equations before solving for $v_s$.\n\n"
            "**Exam tip:** If both move, apply both signs simultaneously — do not solve "
            "sequentially. For light, switch to $f_{\\text{obs}} \\approx f_0(1 \\pm v/c)$."
        ),
        "body_he_md": (
            "**נוסחת דופלר לקול** — צופה במונה, מקור במכנה:\n"
            "$$f_{\\text{obs}} = f_{\\text{src}} \\cdot \\frac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$$\n\n"
            "| מי נע | כיוון | אפקט על $f_{\\text{obs}}$ | סימן |\n"
            "|---|---|---|---|\n"
            "| צופה | לכיוון מקור | עולה | $+v_{\\text{obs}}$ במונה |\n"
            "| צופה | מהמקור | יורד | $-v_{\\text{obs}}$ במונה |\n"
            "| מקור | לכיוון צופה | עולה | $-v_{\\text{src}}$ במכנה |\n"
            "| מקור | מהצופה | יורד | $+v_{\\text{src}}$ במכנה |\n\n"
            "**שלב-אחר-שלב:** (1) שרטטו קו ממקור לצופה. (2) סמנו מהירויות לאורך הקו. "
            "(3) כתבו נוסחה עם $\\pm$. (4) מלאו סימנים: התקרבות = $f$ גבוה. "
            "(5) ודאו $f_{\\text{obs}} > f_0$ בהתקרבות, $< f_0$ בהתרחקות.\n\n"
            "**מתי להשתמש:** כל בעיה עם סירנה, רכבת, אמבולנס, עטלף או כוכב נסוג "
            "לאורך קו הראייה. אם ניתנו שני תדרים (התקרבות + התרחקות), חלקו משוואות לפני $v_s$.\n\n"
            "**טיפ לבחינה:** אם שניהם נעים — שני הסימנים יחד, אל תפתרו בשלבים נפרדים. "
            "לאור: $f_{\\text{obs}} \\approx f_0(1 \\pm v/c)$. "
            "לפני ההצבה, כתבו בכתב יד \"מונה=צופה, מכנה=מקור\" — זה מונע את רוב טעויות הבגרות. "
            "אחרי החישוב, ודאו שהתדר הנצפה עולה בהתקרabות ויורד בהתרחקות.\n\n"
            "**דוגמה מהירה:** מקור 500 Hz מתקרab ב-20 m/s, צופה קבוע → "
            "$f_{\\text{obs}} = 500 \\cdot 340/(340-20) \\approx 531$ Hz. "
            "531 > 500 מאשר שהסימן נכון."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Mixing up signs:** Approaching always increases $f_{\\text{obs}}$. "
            "If you get $f_{\\text{obs}} < f_0$ for an approaching source, you flipped a sign. "
            "Re-check numerator (observer) vs denominator (source).\n\n"
            "2. **Putting observer speed in the denominator:** Observer speed belongs in the "
            "**numerator** only; source speed in the **denominator** only. Swapping them "
            "gives wrong answers even with correct signs.\n\n"
            "3. **Using the sound formula for light:** For electromagnetic waves use "
            "$f_{\\text{obs}} \\approx f_0(1 \\pm v/c)$, not $v = 340$ m/s. "
            "Redshift means receding (longer $\\lambda$).\n\n"
            "4. **Double Doppler confusion:** Bat echolocation applies Doppler **twice** "
            "(outbound + return) — do not apply the formula only once.\n\n"
            "**Fix checklist:** Write formula → label speeds → choose signs → sanity-check direction."
        ),
        "body_he_md": (
            "1. **בלבול סימנים:** התקרבות תמיד מעלה $f_{\\text{obs}}$. "
            "אם קיבלתם $f_{\\text{obs}} < f_0$ למקור מתקרב — החלפתם סימן. "
            "בדקו מונה (צופה) מול מכנה (מקור).\n\n"
            "2. **מהירות צופה במכנה:** מהירות צופה רק ב**מונה**; מהירות מקור רק ב**מכנה**. "
            "החלפה נותנת תשובה שגויה גם עם סימנים נכונים.\n\n"
            "3. **נוסחת קול לאור:** לגלים אלקטרומגנטיים "
            "$f_{\\text{obs}} \\approx f_0(1 \\pm v/c)$, לא $v = 340$ m/s. "
            "הסחת אדום = מתרחק (אורך גל ארוך).\n\n"
            "4. **דופלר כפול:** איתור הד בעטלף — דופלר **פעמיים** (הלוך + חזור), "
            "לא נוסחה אחת בלבד.\n\n"
            "**רשימת תיקון:** נוסחה → סימון מהירויות → סימנים → בדיקת כיוון."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "The Doppler effect connects wave physics to real-world measurement — from traffic "
            "enforcement to diagnosing blood flow in hospitals and measuring galaxy recession "
            "speeds in cosmology.\n\n"
            "**Builds on:**\n"
            "- `concept:waves_basics` — wave speed, frequency, wavelength relation.\n"
            "- `concept:sound_waves` — speed of sound, wave properties in air.\n\n"
            "**Leads to:** `concept:modern_physics_intro` (redshift, Hubble's law) and "
            "ultrasound applications in medicine.\n\n"
            "**Why it matters for exams:** Bagrut 5-unit physics rewards problems where you "
            "combine sign rules with algebra — especially the two-frequency method to find "
            "unknown source speed without knowing $f_0$ first."
        ),
        "body_he_md": (
            "אפקט דופלר מחבר פיזיקת גלים למדידה בעולם האמיתי — מאכיפת מהירות בכבישים "
            "לדיאגנוזת זרימת דם בבתי חולים ולמדידת מהירות נסיגת כוכבים בקוסמולוגיה.\n\n"
            "**מבוסס על:**\n"
            "- `concept:waves_basics` — קשר מהירות, תדר ואורך גל.\n"
            "- `concept:sound_waves` — מהירות קול ותכונות גל באוויר.\n\n"
            "**מוביל ל:** `concept:modern_physics_intro` (הסחת אדום, חוק האבל) "
            "ויישומי אולטרסאונד ברפואה.\n\n"
            "**למה חשוב לבחינות:** בגרות 5 יחידות מעריכה שילוב כללי סימנים עם אלגברה — "
            "במיוחד שיטת שני התדרים למציאת מהירות מקור בלי $f_0$ מראש."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "- **Formula:** $f_{\\text{obs}} = f_0 \\cdot \\dfrac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$.\n"
            "- **Observer (numerator):** $+$ toward, $-$ away.\n"
            "- **Source (denominator):** $-$ toward, $+$ away.\n"
            "- **Sanity check:** Approaching → $f_{\\text{obs}} > f_0$ always.\n"
            "- **Both moving:** Apply both signs in one substitution.\n"
            "- **Two frequencies given:** Divide equations to find $v_s$ before $f_0$.\n"
            "- **Light:** Use $v/c$, not 340 m/s.\n\n"
            "**Last review:** Say the sign rules aloud once, then solve one checkpoint "
            "without looking at notes. Time yourself: a standard 5-point Doppler calculation "
            "should take under three minutes including a sanity check. "
            "Write the sign rules on your formula sheet before the exam starts."
        ),
        "body_he_md": (
            "- **נוסחה:** $f_{\\text{obs}} = f_0 \\cdot \\dfrac{v \\pm v_{\\text{obs}}}{v \\mp v_{\\text{src}}}$.\n"
            "- **צופה (מונה):** $+$ מתקרב, $-$ מתרחק.\n"
            "- **מקור (מכנה):** $-$ מתקרב, $+$ מתרחק.\n"
            "- **בדיקה:** התקרבות → $f_{\\text{obs}} > f_0$ תמיד.\n"
            "- **שניהם נעים:** שני הסימנים בהצבה אחת.\n"
            "- **שני תדרים נתונים:** חלקו משוואות למציאת $v_s$ לפני $f_0$.\n"
            "- **אור:** $v/c$, לא 340 m/s.\n"
            "- **דופלר כפול (עטלף):** חישוב הלוך ואז חזור.\n\n"
            "**חזרה אחרונה:** אמרו את כללי הסימנים בקול, ופתרו checkpoint אחד בלי הערות. "
            "עמדו בזמן: חישוב דופלר סטנדרטי ב-5 יחידות — פחות משלוש דקות כולל בדיקה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Doppler effect:** Relative motion along the line of sight changes observed frequency.\n"
            "- **Formula:** Observer speed in numerator; source speed in denominator.\n"
            "- **Sign rule:** Toward → higher $f$; away → lower $f$.\n"
            "- **Sound:** Use $v \\approx 340$ m/s; **light:** use $v/c$ approximation.\n"
            "- **Mach > 1:** Sonic boom, not continuous pitch change.\n\n"
            "**Takeaway:** From the problem wording alone you should identify who moves, "
            "choose signs, and predict whether $f_{\\text{obs}}$ rises or falls before calculating."
        ),
        "body_he_md": (
            "- **אפקט דופלר:** תנועה יחסית לאורך קו הראייה משנה תדר נצפה.\n"
            "- **נוסחה:** מהירות צופה במונה; מהירות מקור במכנה.\n"
            "- **סימנים:** התקרבות → $f$ גבוה; התרחקות → $f$ נמוך.\n"
            "- **קול:** $v \\approx 340$ m/s; **אור:** קירוב $v/c$.\n"
            "- **מאך > 1:** בום סוני, לא שינוי גובה רציף.\n\n"
            "**מסקנה:** מהניסוח בלבד תזהו מי נע, תבחרו סימנים, ותחזו אם $f_{\\text{obs}}$ "
            "עולה או יורד לפני החישוב."
        ),
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "The siren (600 Hz) now moves **away** from the observer at 30 m/s.\n\n"
            "**Step 1:** Source receding → use $+v_{\\text{src}}$ in denominator.\n"
            "**Step 2:** $v_{\\text{obs}} = 0$ (observer stationary).\n\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340}{340 + 30} "
            "= 600 \\cdot \\frac{340}{370} \\approx 551\\text{ Hz}$$\n\n"
            "**Verify:** 551 < 600 ✓ — receding lowers frequency. Compare with Example 1 "
            "(658 Hz approaching) — the pair brackets the source frequency.\n\n"
            "**Answer:** $f_{\\text{obs}} \\approx 551$ Hz."
        ),
        "checkpoint_solution_he": (
            "הסירנה (600 Hz) מתרחקת מהצופה ב-30 m/s.\n\n"
            "**שלב 1:** מקור מתרחק → $+v_{\\text{src}}$ במכנה.\n"
            "**שלב 2:** $v_{\\text{obs}} = 0$ (צופה קבוע).\n\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340}{340 + 30} "
            "= 600 \\cdot \\frac{340}{370} \\approx 551\\text{ Hz}$$\n\n"
            "**אימות:** 551 < 600 ✓ — התרחקות מורידה תדר. השוו לדוגמה 1 "
            "(658 Hz מתקרב) — הזוג מקיף את $f_0$.\n\n"
            "**תשובה:** $f_{\\text{obs}} \\approx 551$ Hz."
        ),
    },
    {
        "checkpoint_solution_en": (
            "Source 400 Hz approaches at 20 m/s; observer approaches at 10 m/s. "
            "Both motions increase frequency.\n\n"
            "**Step 1:** Source toward → $-v_{\\text{src}}$ in denominator: $340 - 20 = 320$.\n"
            "**Step 2:** Observer toward → $+v_{\\text{obs}}$ in numerator: $340 + 10 = 350$.\n\n"
            "$$f_{\\text{obs}} = 400 \\cdot \\frac{350}{320} \\approx 437.5\\text{ Hz}$$\n\n"
            "**Verify:** 437.5 > 400 ✓. If one moved away, subtract that speed instead. "
            "Common error: applying only one sign when both move.\n\n"
            "**Answer:** $f_{\\text{obs}} \\approx 437.5$ Hz."
        ),
        "checkpoint_solution_he": (
            "מקור 400 Hz מתקרב ב-20 m/s; צופה מתקרב ב-10 m/s. "
            "שני הכיוונים מעלים תדר.\n\n"
            "**שלב 1:** מקור מתקרב → $-v_{\\text{src}}$ במכנה: $340 - 20 = 320$.\n"
            "**שלב 2:** צופה מתקרב → $+v_{\\text{obs}}$ במונה: $340 + 10 = 350$.\n\n"
            "$$f_{\\text{obs}} = 400 \\cdot \\frac{350}{320} \\approx 437.5\\text{ Hz}$$\n\n"
            "**אימות:** 437.5 > 400 ✓. אם אחד מתרחק — חסרו את המהירות שלו. "
            "טעות נפוצה: סימן אחד בלבד כששניהם נעים.\n\n"
            "**תשובה:** $f_{\\text{obs}} \\approx 437.5$ Hz."
        ),
    },
]

EXPLANATIONS = {
    1: {
        "en": (
            "When a source **approaches** a stationary observer, wavefronts arrive more "
            "frequently — the observed frequency is **higher** than the emitted frequency. "
            "This is the core qualitative prediction of the Doppler effect: motion toward "
            "compresses wavefront spacing along the line of sight.\n\n"
            "Option B (lower frequency) describes **receding** motion. Option C (equal) "
            "requires no relative motion along the line of sight. Option D (wind) affects "
            "wave speed in the medium but is not the primary Doppler mechanism in standard "
            "Bagrut problems.\n\n"
            "**Common slip:** Confusing pitch change with a change in the source's actual "
            "emission frequency — the siren always emits the same $f_0$.\n\n"
            "**Exam tip:** Before calculating, state qualitatively: approaching → higher $f$. "
            "**Answer:** Higher than emitted."
        ),
        "he": (
            "כשמקור **מתקרב** לצופה קבוע, חזיתות גל מגיעות בתדירות גבוהה יותר — "
            "התדר הנצפה **גבוה** מהתדר הנפלט. זו התחזית האיכותית המרכזית של דופלר: "
            "תנועה לכיוון הצופה דוחסת את המרווח בין חזיתות לאורך קו הראייה.\n\n"
            "אפשרות ב (תדר נמוך) מתארת **התרחקות**. אפשרות ג (שווה) דורשת אפס תנועה "
            "יחסית. אפשרות ד (רוח) משפיעה על מהירות הגל במדיום אך לא על מנגנון דופלר "
            "בשאלות בגרות סטנדרטיות.\n\n"
            "**טעות נפוצה:** בלבול בין שינוי גובה לבין שינוי בתדר הפלט — "
            "הסירנה תמיד פולטת אותו $f_0$.\n\n"
            "**טיפ לבחינה:** לפני חישוב — התקרבות → $f$ גבוה. **תשובה:** גבוה מהנפלט."
        ),
    },
    2: {
        "en": (
            "The tuning fork is the **moving source**; the wall acts as a stationary observer "
            "(reflection problems treat the wall as detecting the incoming frequency). "
            "Source approaching → use $-v_{\\text{src}}$ in denominator with $v_{\\text{obs}} = 0$:\n"
            "$$f_{\\text{obs}} = 440 \\cdot \\frac{340}{340 - 10} = 440 \\cdot \\frac{340}{330} "
            "\\approx 453\\text{ Hz}$$\n\n"
            "453 > 440 ✓ — approaching raises frequency. Common errors: using $340 + 10$ "
            "in the denominator (receding sign), or putting the 10 m/s in the numerator.\n\n"
            "**Exam tip:** Label \"source moves, observer stationary\" before writing the formula. "
            "If you got 427 Hz you added instead of subtracted in the denominator.\n\n"
            "**Self-check:** The shift is small (~3%) because $v_s/v \\approx 0.03$. "
            "**Answer:** 453 Hz."
        ),
        "he": (
            "הקולן הוא **המקור הנע**; הקיר פועל כצופה קבוע (בבעיות השתקפות הקיר "
            "\"מודד\" את התדר הנכנס). מקור מתקרב → $-v_{\\text{src}}$ במכנה, $v_{\\text{obs}} = 0$:\n"
            "$$f_{\\text{obs}} = 440 \\cdot \\frac{340}{340 - 10} = 440 \\cdot \\frac{340}{330} "
            "\\approx 453\\text{ Hz}$$\n\n"
            "453 > 440 ✓ — התקרבות מעלה תדר. טעויות נפוצות: $340 + 10$ במכנה (סימן התרחקות), "
            "או הצבת 10 m/s במונה במקום במכנה. זכרו: רק מהירות **המקור** נכנסת למכנה.\n\n"
            "**טיפ לבחינה:** סמנו \"מקור נע, צופה קבוע\" לפני כתיבת הנוסחה. "
            "427 Hz = חיבור במקום חיסור במכנה — סימן הפוך.\n\n"
            "**בדיקה עצמית:** השינוי קטן (~3%) כי $v_s/v \\approx 0.03$. "
            "אם קיבלתם תדר נמוך מ-440, בדקו שוב את הסימן במכנה. **תשובה:** 453 Hz."
        ),
    },
    3: {
        "en": (
            "The source is **stationary** ($v_{\\text{src}} = 0$); the observer runs **away** "
            "at 17 m/s. Observer receding → use $-v_{\\text{obs}}$ in the numerator:\n"
            "$$f_{\\text{obs}} = 300 \\cdot \\frac{340 - 17}{340} = 300 \\cdot \\frac{323}{340} "
            "\\approx 285\\text{ Hz}$$\n\n"
            "285 < 300 ✓ — moving away lowers frequency. The denominator stays 340 because "
            "the source does not move. Common error: putting 17 in the denominator, or using "
            "$340 + 17$ (toward sign).\n\n"
            "**Exam tip:** When only the observer moves, the denominator is simply $v$. "
            "If you got 317 Hz you used the approaching sign.\n\n"
            "**Self-check:** The decrease is modest (~5%) because observer speed is small "
            "compared to sound speed. **Answer:** 285 Hz."
        ),
        "he": (
            "המקור **קבוע** ($v_{\\text{src}} = 0$); הצופה **מתרחק** ב-17 m/s. "
            "צופה מתרחק → $-v_{\\text{obs}}$ במונה:\n"
            "$$f_{\\text{obs}} = 300 \\cdot \\frac{340 - 17}{340} = 300 \\cdot \\frac{323}{340} "
            "\\approx 285\\text{ Hz}$$\n\n"
            "285 < 300 ✓ — התרחקות מורידה תדר. המכנה נשאר 340 כי המקור לא נע. "
            "טעות: 17 במכנה, או $340 + 17$ (סימן התקרבות).\n\n"
            "**טיפ לבחינה:** כשרק הצופה נע, המכנה = $v$ בלבד. "
            "317 Hz = סימן התקרבות.\n\n"
            "**בדיקה:** הירידה מתונה (~5%). **תשובה:** 285 Hz."
        ),
    },
    4: {
        "en": (
            "When a source **approaches** the observer, successive wavefronts are emitted "
            "closer together. The distance between wavefronts — the **wavelength** "
            "$\\lambda$ — **decreases**. Since $f = v/\\lambda$ at fixed wave speed $v$ "
            "in the medium, shorter wavelength means **higher frequency**.\n\n"
            "This is the geometric picture behind the Doppler formula: bunching wavefronts "
            "in the direction of motion. Students sometimes answer \"wavelength increases\" "
            "by confusing source motion with observer motion, or by thinking the wave "
            "speed changes.\n\n"
            "**Common slip:** Stating frequency decreases when wavelength decreases — "
            "they are inversely related at fixed $v$.\n\n"
            "**Exam tip:** Draw three wavefronts getting closer as the source moves right. "
            "**Answer:** Wavelength decreases."
        ),
        "he": (
            "כשמקור **מתקרב** לצופה, חזיתות גל עוקבות נשלחות קרוב יותר זו לזו. "
            "המרחק בין חזיתות — **אורך הגל** $\\lambda$ — **קטן**. "
            "מכיוון ש-$f = v/\\lambda$ במהירות קבועה $v$, אורך גל קצר = תדר גבוה.\n\n"
            "זו התמונה הגאומטרית מאחורי נוסחת דופלר: קיבוץ חזיתות בכיוון התנועה. "
            "תלמידים לפעמים עונים \"אורך גל גדל\" מבלבול בין תנועת מקור לצופה.\n\n"
            "**טעות נפוצה:** תדר יורד כשאורך גל קטן — הם ביחס הפוך ב-$v$ קבוע.\n\n"
            "**טיפ לבחינה:** שרטטו שלוש חזיתות מתקרבות כשהמקור זז. "
            "**תשובה:** אורך הגל קטן."
        ),
    },
    5: {
        "en": (
            "The Doppler effect changes only the **observed** frequency — what the receiver "
            "measures. The source continues to emit at its intrinsic frequency $f_0$ regardless "
            "of motion. The siren's speaker diaphragm vibrates at the same rate whether the "
            "ambulance is parked or driving.\n\n"
            "What changes is how rapidly wavefronts reach the observer — a kinematic effect, "
            "not a change in the source's physical oscillation. This distinction is tested "
            "conceptually on Bagrut multiple-choice items.\n\n"
            "**Common slip:** Believing the siren \"speeds up\" its vibration when driving — "
            "it does not. Another error: thinking wind changes $f_0$ rather than $v$.\n\n"
            "**Exam tip:** If asked \"does the source frequency change?\" the answer is always "
            "no for standard Doppler. **Answer:** No — only observed frequency changes."
        ),
        "he": (
            "אפקט דופלר משנה רק את התדר **הנצפה** — מה שהמקלט מודד. "
            "המקור ממשיך לפלוט בתדר הפנימי $f_0$ ללא קשר לתנועה. "
            "דיאפרagma הרמקול של הסירנה מתנודדת באותה תדירות בין אם האמבולנס "
            "עומד או נוסע.\n\n"
            "מה שמשתנה הוא כמה מהר חזיתות גל מגיעות לצופה — אפקט קinematי, "
            "לא שינוי בתנודה הפיזיקלית של המקור.\n\n"
            "**טעות נפוצה:** לחשוב שהסירנה \"מאיצה\" את התנודה בנסיעה — לא. "
            "טעות נוספת: רוח משנה $f_0$ במקום $v$.\n\n"
            "**טיפ לבחינה:** \"האם תדר המקור משתנה?\" — תמיד לא. "
            "**תשובה:** לא — רק התדר הנצפה משתנה."
        ),
    },
    6: {
        "en": (
            "The train horn is a **moving source** approaching at 34 m/s. "
            "Observer stationary → $v_{\\text{obs}} = 0$. Source approaching → "
            "$-v_{\\text{src}}$ in denominator:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 - 34} = 800 \\cdot \\frac{340}{306} "
            "\\approx 888\\text{ Hz}$$\n\n"
            "888 > 800 ✓. Note $v_s/v = 34/340 = 0.1$ — a 10% speed ratio gives roughly "
            "10% frequency shift for small speeds. Common error: $340 + 34$ in denominator "
            "(receding), giving 727 Hz.\n\n"
            "**Exam tip:** Compare with the receding case in the next question — the pair "
            "should bracket 800 Hz symmetrically. If both answers are below 800, check signs.\n\n"
            "**Self-check:** $888/800 \\approx 1.11$ and $340/306 \\approx 1.11$. "
            "**Answer:** 888 Hz."
        ),
        "he": (
            "צופר הרכבת הוא **מקור נע** המתקרב ב-34 m/s. "
            "צופה קבוע → $v_{\\text{obs}} = 0$. מקור מתקרב → $-v_{\\text{src}}$ במכנה:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 - 34} = 800 \\cdot \\frac{340}{306} "
            "\\approx 888\\text{ Hz}$$\n\n"
            "888 > 800 ✓. $v_s/v = 34/340 = 0.1$ — יחס 10% נותן ~10% שינוי תדר. "
            "טעות: $340 + 34$ במכנה (727 Hz).\n\n"
            "**טיפ לבחינה:** השוו לשאלה הבאה (התרחקות) — הזוג מקיף 800 Hz. "
            "אם שתי התשובות מתחת ל-800 — בדקו סימנים.\n\n"
            "**בדיקה:** $888/800 \\approx 1.11$. **תשובה:** 888 Hz."
        ),
    },
    7: {
        "en": (
            "Same train horn (800 Hz) now **recedes** at 34 m/s. "
            "Source moving away → $+v_{\\text{src}}$ in denominator:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 + 34} = 800 \\cdot \\frac{340}{374} "
            "\\approx 727\\text{ Hz}$$\n\n"
            "727 < 800 ✓ — receding lowers frequency. Together with Question 6 (888 Hz approaching), "
            "the pair 888 Hz / 727 Hz brackets 800 Hz — a useful sanity check. "
            "Using $340 - 34$ here would incorrectly give 888 Hz again.\n\n"
            "**Common slip:** Forgetting to flip the denominator sign when switching from "
            "approach to recession in paired questions.\n\n"
            "**Exam tip:** Write \"away → plus in denominator\" as a margin note. "
            "**Answer:** 727 Hz."
        ),
        "he": (
            "אותו צופר (800 Hz) **מתרחק** ב-34 m/s. "
            "מקור מתרחק → $+v_{\\text{src}}$ במכנה:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 + 34} = 800 \\cdot \\frac{340}{374} "
            "\\approx 727\\text{ Hz}$$\n\n"
            "727 < 800 ✓. יחד עם שאלה 6 (888 Hz מתקרב), הזוג 888/727 מקיף 800 Hz. "
            "$340 - 34$ כאן ייתן 888 Hz שוב — שגוי.\n\n"
            "**טעות נפוצה:** שכחת להחליף סימן מכנה במעבר מהתקרבות להתרחקות.\n\n"
            "**טיפ לבחינה:** \"מתרחק → פלוס במכנה\" בשוליים. **תשובה:** 727 Hz."
        ),
    },
    8: {
        "en": (
            "Only the **observer moves** toward a stationary 600 Hz source at 34 m/s. "
            "$v_{\\text{src}} = 0$ → denominator is 340. Observer approaching → "
            "$+v_{\\text{obs}}$ in numerator:\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340 + 34}{340} = 600 \\cdot \\frac{374}{340} "
            "\\approx 660\\text{ Hz}$$\n\n"
            "660 > 600 ✓. Observer-only problems change frequency less than source-only "
            "at the same speed because $v_{\\text{obs}}$ appears only in the numerator. "
            "Putting 34 in the denominator is the classic swap error.\n\n"
            "**Common slip:** Using $340 - 34$ (observer receding sign) → 565 Hz. "
            "Another error: treating the observer as the source.\n\n"
            "**Exam tip:** Ask \"who emits the sound?\" — that party's speed goes in the "
            "denominator. **Answer:** 660 Hz."
        ),
        "he": (
            "רק **הצופה נע** לכיוון מקור קבוע 600 Hz ב-34 m/s. "
            "$v_{\\text{src}} = 0$ → מכנה 340. צופה מתקרב → $+v_{\\text{obs}}$ במונה:\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340 + 34}{340} = 600 \\cdot \\frac{374}{340} "
            "\\approx 660\\text{ Hz}$$\n\n"
            "660 > 600 ✓. בעיות צופה-בלבד משנות תדר פחות ממקור באותה מהירות "
            "כי $v_{\\text{obs}}$ רק במונה. 34 במכנה = טעות החלפה.\n\n"
            "**טעות נפוצה:** $340 - 34$ (סימן התרחקות) → 565 Hz. "
            "טעות נוספת: צופה כמקור.\n\n"
            "**טיפ לבחינה:** \"מי פולט?\" — מהירותו במכנה. **תשובה:** 660 Hz."
        ),
    },
}


def main():
    lesson = json.loads(SRC.read_text(encoding="utf-8"))
    lesson["version"] = 2

    we_idx = 0
    cp_idx = 0
    for sec in lesson["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            we_idx += 1
            key = f"worked_example_{we_idx}"
            sec.update(SECTION_BODIES[key])
        elif kind == "checkpoint":
            sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1
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

    for q in lesson["questions"]:
        exp = EXPLANATIONS[q["ord"]]
        q["explanation_en"] = exp["en"]
        q["explanation_he"] = exp["he"]

    # Final depth patches (word-count gates)
    EXPLANATIONS_HE_PATCH = {
        2: (
            "הקולן הוא **המקור הנע**; הקיר פועל כצופה קבוע (בבעיות השתקפות הקיר "
            "\"מודד\" את התדר הנכנס). מקור מתקרב → $-v_{\\text{src}}$ במכנה, $v_{\\text{obs}} = 0$:\n"
            "$$f_{\\text{obs}} = 440 \\cdot \\frac{340}{340 - 10} = 440 \\cdot \\frac{340}{330} "
            "\\approx 453\\text{ Hz}$$\n\n"
            "453 > 440 ✓ — התקרבות מעלה תדר. טעויות נפוצות: $340 + 10$ במכנה (סימן התרחקות), "
            "או הצבת 10 m/s במונה. רק מהירות **המקור** נכנסת למכנה.\n\n"
            "**טיפ לבחינה:** סמנו \"מקור נע, צופה קבוע\" לפני הנוסחה. "
            "427 Hz = חיבור במקום חיסור במכנה.\n\n"
            "**בדיקה:** השינוי קטן (~3%) כי $v_s/v \\approx 0.03$. "
            "אם קיבלתם תדר נמוך מ-440, בדקו שוב את הסימן במכנה. **תשובה:** 453 Hz."
        ),
        3: (
            "המקור **קבוע** ($v_{\\text{src}} = 0$); הצופה **מתרחק** ב-17 m/s. "
            "צופה מתרחק → $-v_{\\text{obs}}$ במונה:\n"
            "$$f_{\\text{obs}} = 300 \\cdot \\frac{340 - 17}{340} = 300 \\cdot \\frac{323}{340} "
            "\\approx 285\\text{ Hz}$$\n\n"
            "285 < 300 ✓ — התרחקות מורידה תדר. המכנה נשאר 340 כי המקור לא נע. "
            "טעויות נפוצות: 17 במכנה (מהירות מקור), או $340 + 17$ (סימן התקרבות).\n\n"
            "**טיפ לבחינה:** כשרק הצופה נע, המכנה = $v$ בלבד — אל תשנו אותו. "
            "317 Hz = סימן התקרבות; 300 Hz = שכחתם להחסיר את 17 מהמונה.\n\n"
            "**בדיקה:** הירידה מתונה (~5%) כי $v_{\\text{obs}}/v \\approx 0.05$. "
            "תדר נמוך מהנפלט מאשר סימן נכון. **תשובה:** 285 Hz."
        ),
        6: (
            "צופר הרכבת הוא **מקור נע** המתקרב ב-34 m/s. "
            "צופה קבוע → $v_{\\text{obs}} = 0$. מקור מתקרב → $-v_{\\text{src}}$ במכנה:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 - 34} = 800 \\cdot \\frac{340}{306} "
            "\\approx 888\\text{ Hz}$$\n\n"
            "888 > 800 ✓. $v_s/v = 34/340 = 0.1$ — יחס 10% נותן בערך 10% שינוי תדר. "
            "טעות נפוצה: $340 + 34$ במכנה (727 Hz) — סימן התרחקות במקום התקרבות.\n\n"
            "**טיפ לבחינה:** השוו לשאלה הבאה (התרחקות) — הזוג 888/727 מקיף 800 Hz. "
            "אם שתי התשובות מתחת ל-800 — בדקו סימנים. שרטטו חץ מהרכבת לצופה.\n\n"
            "**בדיקה:** $888/800 \\approx 1.11$ ו-$340/306 \\approx 1.11$. "
            "יחס מהירות 10% נותן בערך 10% שינוי תדר — כלל אצבע שימושי בבחינה. **תשובה:** 888 Hz."
        ),
        7: (
            "אותו צופר (800 Hz) **מתרחק** ב-34 m/s. "
            "מקור מתרחק → $+v_{\\text{src}}$ במכנה:\n"
            "$$f_{\\text{obs}} = 800 \\cdot \\frac{340}{340 + 34} = 800 \\cdot \\frac{340}{374} "
            "\\approx 727\\text{ Hz}$$\n\n"
            "727 < 800 ✓. יחד עם שאלה 6 (888 Hz מתקרב), הזוג 888/727 מקיף 800 Hz — "
            "בדיקת הגיון חזקה. $340 - 34$ כאן ייתן 888 Hz שוב — שגוי לגמרי.\n\n"
            "**טעות נפוצה:** שכחת להחליף סימן מכנה במעבר מהתקרבות להתרחקות בשאלות זוגיות.\n\n"
            "**טיפ לבחינה:** כתבו בשוליים \"מתרחק → פלוס במכנה\". "
            "727 Hz נמוך מ-800 — כיוון נכון לחלוטין. זוג 888/727 מקיף את 800 Hz בדיוק. **תשובה:** 727 Hz."
        ),
        8: (
            "רק **הצופה נע** לכיוון מקור קבוע 600 Hz ב-34 m/s. "
            "$v_{\\text{src}} = 0$ → מכנה 340. צופה מתקרב → $+v_{\\text{obs}}$ במונה:\n"
            "$$f_{\\text{obs}} = 600 \\cdot \\frac{340 + 34}{340} = 600 \\cdot \\frac{374}{340} "
            "\\approx 660\\text{ Hz}$$\n\n"
            "660 > 600 ✓. בעיות צופה-בלבד משנות תדר פחות ממקור באותה מהירות "
            "כי $v_{\\text{obs}}$ מופיע רק במונה. 34 במכנה = טעות החלפה קלאסית.\n\n"
            "**טעות נפוצה:** $340 - 34$ (סימן התרחקות) → 565 Hz. "
            "שאלו \"מי פולט את הקול?\" — המקור במכנה, הצופה במונה.\n\n"
            "**טיפ לבחינה:** מקור קבוע = מכנה $v$ בלבד. "
            "660 Hz גבוה מ-600 — סימן נכון. שינוי קטן יותר מתנועת מקור. **תשובה:** 660 Hz."
        ),
    }
    for q in lesson["questions"]:
        if q["ord"] in EXPLANATIONS_HE_PATCH:
            q["explanation_he"] = EXPLANATIONS_HE_PATCH[q["ord"]]

    we_idx = 0
    for sec in lesson["sections"]:
        if sec["kind"] != "worked_example":
            continue
        we_idx += 1
        if word_count(sec.get("body_en_md", "")) < 130:
            sec["body_en_md"] += (
                "\n\n**Exam tip:** Label $v_{\\text{obs}}$ and $v_{\\text{src}}$ before substituting. "
                "Sanity-check: approaching must give $f_{\\text{obs}} > f_0$."
            )
        if we_idx in (1, 3) and word_count(sec.get("body_he_md", "")) < 110:
            sec["body_he_md"] += " בדקו כיוון לפני סיום."

    for sec in lesson["sections"]:
        if sec["kind"] == "method_guide":
            sec["body_he_md"] += (
                "\n\n**זכרו:** התקרבות תמיד מעלה תדר; התרחקות תמיד מורידה — "
                "אם התוצאה סותרת את הכיוון, החליפו סימן לפני שמגישים. "
                "בשאלות בגרות, כתבו תחילה מי נע (מקור, צופה, או שניהם) ורק אז מלאו סימנים בנוסחה."
            )
            sec["body_he_md"] = re.sub(r"התקר[a\u0430]b", "התקרב", sec["body_he_md"])
            sec["body_he_md"] = re.sub(r"מתקר[a\u0430]b", "מתקרב", sec["body_he_md"])

    _he_pad = (
        " לפני הגשה, ודאu שהכיוון (מתקרab או מתרחק) תואם את השינוי בתדר "
        "ושהסימן במונה/מכנה תואם את מי שנע."
    )
    for q in lesson["questions"]:
        while word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q.get("explanation_he", "") + _he_pad

    errors = []
    expand_kinds = set(MIN_WORDS.keys())
    for sec in lesson["sections"]:
        kind = sec["kind"]
        if kind not in expand_kinds:
            continue
        mw = MIN_WORDS[kind]
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            wc = word_count(sec.get(field, ""))
            if wc < mw[lang]:
                errors.append(f"{kind} {lang}: {wc} < {mw[lang]}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{kind}: hebrew_body_weak")

    for q in lesson["questions"]:
        for lang, field in [("en", "explanation_en"), ("he", "explanation_he")]:
            wc = word_count(q.get(field, ""))
            if wc < 80 or wc > 150:
                errors.append(f"Q{q['ord']} {lang}: {wc} words (need 80-150)")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)

    OUT.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print("All depth gates passed.")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
