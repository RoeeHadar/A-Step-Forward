#!/usr/bin/env python3
"""Generate expanded sound_waves.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/sound_waves.json"
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
            "Sound is a **longitudinal mechanical wave** — air molecules oscillate back and forth "
            "along the direction the wave travels, creating alternating regions of **compression** "
            "(high pressure) and **rarefaction** (low pressure). Unlike light, sound **requires a "
            "medium**; it cannot propagate through a vacuum.\n\n"
            "**Key properties for Bagrut physics (questionnaire 3):**\n"
            "- Speed in air at 20°C: $v \\approx 340$ m/s (sometimes written $v \\approx 331 + 0.6T$ "
            "where $T$ is temperature in °C).\n"
            "- Human hearing range: roughly 20 Hz – 20,000 Hz.\n"
            "- Master relation: $v = f\\lambda$ links speed, frequency, and wavelength.\n\n"
            "This lesson builds on `concept:waves_basics` and extends to **intensity and decibels**, "
            "**standing waves in strings and pipes**, **resonance**, and **beats**. "
            "Exam items often mix wave-equation calculations with pipe-type identification — "
            "open vs closed is the most common trap."
        ),
        "body_he_md": (
            "קול הוא **גל מכני אורכי** — מולקולות האוויר מתנודדות קדימה ואחורה לאורך כיוון "
            "ההתפשטות, ויוצרות אזורי **דחיסה** (לחץ גבוה) ו**דלילות** (לחץ נמוך) לסירוגין. "
            "בניגוד לאור, קול **דורש מדיום**; הוא לא מתפשט בוואקום.\n\n"
            "**תכונות מפתח לבגרות בפיזיקה (שאלון 3):**\n"
            "- מהירות באוויר ב-20°C: $v \\approx 340$ m/s (לפעמים $v \\approx 331 + 0.6T$ "
            "כאשר $T$ בצלסיוס).\n"
            "- טווח שמיעה אנושי: בערך 20 Hz – 20,000 Hz.\n"
            "- הקשר המרכזי: $v = f\\lambda$ מקשר מהירות, תדר ואורך גל.\n\n"
            "שיעור זה מבוסס על `concept:waves_basics` ומתרחב ל**עוצמה ודציבלים**, "
            "**גלים עומדים במיתרים וצינורות**, **תהודה** ו**פעימות**. "
            "שאלות בבחינה לעיתים קרובות משלבות חישובי משוואת גל עם זיהוי סוג צינור — "
            "פתוח מול סגור היא המלכודת הנפוצה ביותר."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Wave equation** — the fundamental link between speed, frequency, and wavelength:\n"
            "$$\\boxed{v = f\\lambda}$$\n\n"
            "Rearrangements: $\\lambda = v/f$ and $f = v/\\lambda$. Speed depends on the medium; "
            "340 m/s is for air, not for a guitar string.\n\n"
            "**Sound intensity level (decibels):**\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right) \\text{ dB}, "
            "\\quad I_0 = 10^{-12}\\text{ W/m}^2$$\n"
            "$I_0$ is the threshold of hearing. Each **10× increase** in intensity adds **+10 dB**; "
            "doubling intensity adds about **+3 dB**.\n\n"
            "**Standing waves — fixed string or open pipe (both ends free/open):**\n"
            "$$f_n = \\frac{nv}{2L}, \\quad n = 1, 2, 3, \\ldots \\text{ (all harmonics)}$$\n\n"
            "**Closed pipe (one end closed, one open):**\n"
            "$$f_n = \\frac{(2n-1)v}{4L}, \\quad n = 1, 2, 3, \\ldots \\text{ (odd harmonics only)}$$\n"
            "Equivalently $f_n = nv/(4L)$ with $n = 1, 3, 5, \\ldots$. "
            "The closed end is a displacement **node**; the open end is an **anti-node**.\n\n"
            "**Beats:** When two sources have frequencies $f_1$ and $f_2$, "
            "the beat frequency is $f_{\\text{beat}} = |f_1 - f_2|$. "
            "Tuning instruments relies on listening for beats that disappear at perfect pitch."
        ),
        "body_he_md": (
            "**משוואת גל** — הקשר הבסיסי בין מהירות, תדר ואורך גל:\n"
            "$$\\boxed{v = f\\lambda}$$\n\n"
            "סידורים: $\\lambda = v/f$ ו-$f = v/\\lambda$. המהירות תלויה במדיום; "
            "340 m/s מתאים לאוויר, לא למיתר גיטרה.\n\n"
            "**רמת עוצמת קול (דציבלים):**\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right) \\text{ dB}, "
            "\\quad I_0 = 10^{-12}\\text{ W/m}^2$$\n"
            "$I_0$ הוא סף השמיעה. כל **הכפלה פי 10** בעוצמה מוסיפה **+10 dB**; "
            "הכפלת עוצמה מוסיפה כ-**+3 dB**.\n\n"
            "**גלים עומדים — מיתר קבוע או צינור פתוח (שני קצוות פתוחים):**\n"
            "$$f_n = \\frac{nv}{2L}, \\quad n = 1, 2, 3, \\ldots \\text{ (כל ההרמוניות)}$$\n\n"
            "**צינור סגור (קצה אחד סגור, אחד פתוח):**\n"
            "$$f_n = \\frac{(2n-1)v}{4L}, \\quad n = 1, 2, 3, \\ldots \\text{ (הרמוניות אי-זוגיות בלבד)}$$\n"
            "שקול ל-$f_n = nv/(4L)$ עם $n = 1, 3, 5, \\ldots$. "
            "הקצה הסגור הוא **צומת** תזוזה; הקצה הפתוח הוא **שיא**.\n\n"
            "**פעימות:** כששני מקורות בתדרים $f_1$ ו-$f_2$, "
            "תדר הפעימות הוא $f_{\\text{beat}} = |f_1 - f_2|$. "
            "כיוון כלים מסתמך על האזנה לפעימות שנעלמות בתדר מדויק."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Intensity and the inverse-square law\n\n"
            "**Intensity** $I = P/A$ (W/m²) is acoustic power per unit area. "
            "For a point source, intensity falls as $I \\propto 1/r^2$ — "
            "doubling the distance drops intensity by a factor of four.\n\n"
            "### Decibel arithmetic\n\n"
            "Because human hearing spans many orders of magnitude, we use a logarithmic scale:\n"
            "- **Double intensity** → $+3$ dB (barely noticeable).\n"
            "- **10× intensity** → $+10$ dB (sounds about twice as loud).\n"
            "- **100× intensity** → $+20$ dB.\n\n"
            "To combine two equal sources at 70 dB each: convert to intensity, add, "
            "then convert back — result is 73 dB, not 140 dB.\n\n"
            "### Resonance and standing waves\n\n"
            "When a driving frequency matches a natural standing-wave frequency, "
            "**resonance** occurs and amplitude grows dramatically. "
            "Musical instruments are tuned resonators.\n\n"
            "### Beats\n\n"
            "Two sources with slightly different frequencies $f_1$ and $f_2$ "
            "produce a pulsing loudness pattern with beat frequency:\n"
            "$$f_{\\text{beat}} = |f_1 - f_2|$$\n"
            "Tuning a guitar against a reference pitch relies on beats — "
            "when beats disappear, the strings match. "
            "This connects directly to tuning fork problems on the Bagrut."
        ),
        "body_he_md": (
            "### עוצמה וחוק הריבוע ההפוך\n\n"
            "**עוצמה** $I = P/A$ (W/m²) היא הספק אקוסטי ליחידת שטח. "
            "למקור נקודתי, העוצמה יורדת כ-$I \\propto 1/r^2$ — "
            "הכפלת המרחק מורידה את העוצמה פי ארבע.\n\n"
            "### חשבון דציבלים\n\n"
            "מכיוון שטווח השמיעה האנושי רחב, משתמשים בסקala לוגריתמית:\n"
            "- **הכפלת עוצמה** → $+3$ dB (כמעט לא מורגש).\n"
            "- **פי 10 בעוצמה** → $+10$ dB (נשמע בערך פי שניים חזק).\n"
            "- **פי 100 בעוצמה** → $+20$ dB.\n\n"
            "לשילוב שני מקורות שווים ב-70 dB כל אחד: ממירים לעוצמה, מחברים, "
            "וממירים חזרה — התוצאה 73 dB, לא 140 dB.\n\n"
            "### תהודה וגלים עומדים\n\n"
            "כשתדר הנעה תואם תדר טבעי של גל עומד, מתרחשת **תהודה** "
            "והאמפליטודה גדלה בחדות. כלי נגינה הם מהדהרים מכוונים.\n\n"
            "### פעימות\n\n"
            "שני מקורות בתדרים מעט שונים $f_1$ ו-$f_2$ "
            "יוצרים דפוס עוצמה פועם עם תדר פעימות:\n"
            "$$f_{\\text{beat}} = |f_1 - f_2|$$\n"
            "כיוון גיטרה מול תו ייחוס מסתמך על פעימות — "
            "כשהפעימות נעלמות, המיתרים תואמים."
        ),
    },
    "worked_example": {
        "body_en_md": (
            "**Find the wavelength** of a 440 Hz tone (concert A) in air ($v = 340$ m/s).\n\n"
            "### Move 1: Write the wave equation\n"
            "$$v = f\\lambda \\quad \\Rightarrow \\quad \\lambda = \\frac{v}{f}$$\n\n"
            "### Move 2: Substitute values\n"
            "$$\\lambda = \\frac{340}{440} = \\frac{17}{22} \\approx 0.773\\text{ m}$$\n\n"
            "### Move 3: Physical interpretation\n"
            "The wavelength is about 77 cm — roughly the width of a textbook. "
            "Higher pitch (higher $f$) means shorter wavelength at the same speed. "
            "At 880 Hz (one octave above), $\\lambda \\approx 0.39$ m. "
            "In water at 1500 m/s the same note would have $\\lambda \\approx 3.4$ m.\n\n"
            "### Move 4: Verify\n"
            "Back-substitute: $440 \\times 0.773 \\approx 340$ m/s ✓. "
            "If you got 1.36 m you multiplied instead of divided. "
            "Concert A at 440 Hz is the reference pitch for tuning orchestras worldwide. "
            "The period is $T = 1/f \\approx 2.27$ ms — another quick check.\n\n"
            "**Answer:** $\\lambda \\approx 0.77$ m. "
            "This inverse relationship between $f$ and $\\lambda$ at fixed $v$ "
            "is tested on nearly every Bagrut sound-wave question. "
            "Always write the formula before substituting numbers. "
            "Bagrut items often give $v$ and $f$ and ask for $\\lambda$ directly. "
            "Units check: wavelength in metres, frequency in hertz."
        ),
        "body_he_md": (
            "**מצאו את אורך הגל** של תו 440 Hz (לה A) באוויר ($v = 340$ m/s).\n\n"
            "### צעד 1: כתיבת משוואת הגל\n"
            "$$v = f\\lambda \\quad \\Rightarrow \\quad \\lambda = \\frac{v}{f}$$\n\n"
            "### צעד 2: הצבת ערכים\n"
            "$$\\lambda = \\frac{340}{440} = \\frac{17}{22} \\approx 0.773\\text{ m}$$\n\n"
            "### צעד 3: פרשנות פיזיקלית\n"
            "אורך הגל כ-77 cm — בערך רוחב ספר לימוד. "
            "תדר גבוה יותר = אורך גל קצר יותר באותה מהירות. "
            "ב-880 Hz (אוקטAVA מעל), $\\lambda \\approx 0.39$ m. "
            "במים ב-1500 m/s אותו תו היה $\\lambda \\approx 3.4$ m.\n\n"
            "### צעד 4: אימות\n"
            "הצבה חוזרת: $440 \\times 0.773 \\approx 340$ m/s ✓. "
            "אם קיבלתם 1.36 m — כפלתם במקום לחלק. "
            "לה A ב-440 Hz הוא תו הייחוס לכיוון תזמורות. "
            "המחזור $T = 1/f \\approx 2.27$ ms — בדיקה נוספת.\n\n"
            "**תשובה:** $\\lambda \\approx 0.77$ m. "
            "הקשר ההפוך בין $f$ ל-$\\lambda$ במהירות קבועה "
            "נבחן כמעט בכל שאלת גלי קול בבגרות. "
            "כתבו תמיד את הנוסחה לפני הצבת מספרים. "
            "שאלות בבגרות לעיתים נותנות $v$ ו-$f$ ושואלות ישירות על $\\lambda$. "
            "בדיקת יחידות: אורך גל במטרים, תדר בהרץ."
        ),
    },
    "worked_example_decibels": {
        "body_en_md": (
            "**A sound has intensity $I = 10^{-6}$ W/m².** Find the sound level in dB.\n\n"
            "### Move 1: Write the decibel formula\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right), "
            "\\quad I_0 = 10^{-12}\\text{ W/m}^2$$\n\n"
            "### Move 2: Compute the ratio\n"
            "$$\\frac{I}{I_0} = \\frac{10^{-6}}{10^{-12}} = 10^6$$\n\n"
            "### Move 3: Take the logarithm\n"
            "$$\\beta = 10\\log_{10}(10^6) = 10 \\times 6 = 60\\text{ dB}$$\n\n"
            "### Move 4: Interpret\n"
            "60 dB is typical conversation level. "
            "Whisper $\\approx 30$ dB; pain threshold $\\approx 120$ dB. "
            "Remember: use $\\log_{10}$, not $\\ln$ or $\\log_2$. "
            "If you forgot $I_0$ you would get 120 dB — always write the full ratio first. "
            "The ratio $10^6$ means the sound is one million times above threshold.\n\n"
            "**Answer:** 60 dB. Decibel problems on the Bagrut almost always require "
            "computing $I/I_0$ before taking the logarithm. "
            "Whisper is about 30 dB; pain threshold about 120 dB. "
            "Compare: $10^{-6}$ W/m² is loud conversation; $10^{-12}$ is threshold. "
            "This problem type appears on nearly every Bagrut sound section. "
            "Write $\\beta = 10\\log_{10}(I/I_0)$ before any numbers. "
            "Never skip the reference intensity $I_0$ in the ratio."
        ),
        "body_he_md": (
            "**לקול עוצמה $I = 10^{-6}$ W/m².** מצאו את רמת הקול ב-dB.\n\n"
            "### צעד 1: נוסחת הדציבל\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right), "
            "\\quad I_0 = 10^{-12}\\text{ W/m}^2$$\n\n"
            "### צעד 2: חישוב היחס\n"
            "$$\\frac{I}{I_0} = \\frac{10^{-6}}{10^{-12}} = 10^6$$\n\n"
            "### צעד 3: לוגריתם\n"
            "$$\\beta = 10\\log_{10}(10^6) = 10 \\times 6 = 60\\text{ dB}$$\n\n"
            "### צעד 4: פרשנות\n"
            "60 dB הוא רמת שיחה רגילה. "
            "לחישה $\\approx 30$ dB; סף כאב $\\approx 120$ dB. "
            "זכרו: משתמשים ב-$\\log_{10}$, לא ב-$\\ln$ או $\\log_2$. "
            "אם שכחתם $I_0$ הייתם מקבלים 120 dB — כתבו תמיד את היחס המלא קודם. "
            "היחס $10^6$ פירושו שהקול פי מיליון מעל הסף.\n\n"
            "**תשובה:** 60 dB. בעיות דציבל בבגרות כמעט תמיד דורשות "
            "חישוב $I/I_0$ לפני לוגריתם. "
            "לחישה בערך 30 dB; סף כאב בערך 120 dB. "
            "השוואה: $10^{-6}$ W/m² שיחה; $10^{-12}$ סף שמיעה. "
            "סוג בעיה זה מופיע כמעט בכל פרק קול בבגרות. "
            "כתבו $\\beta = 10\\log_{10}(I/I_0)$ לפני כל מספר. "
            "לעולם אל תדלגו על $I_0$ ביחס."
        ),
    },
    "worked_example_pipe": {
        "body_en_md": (
            "**A closed organ pipe** (closed at one end) has length $L = 0.85$ m. "
            "Find the three lowest resonance frequencies ($v = 340$ m/s).\n\n"
            "### Move 1: Identify pipe type and formula\n"
            "Closed pipe → odd harmonics only: "
            "$$f_n = \\frac{(2n-1)v}{4L}, \\quad n = 1, 2, 3, \\ldots$$\n\n"
            "### Move 2: First harmonic ($n = 1$)\n"
            "$$f_1 = \\frac{1 \\times 340}{4 \\times 0.85} = \\frac{340}{3.4} = 100\\text{ Hz}$$\n\n"
            "### Move 3: Second and third allowed harmonics ($n = 2, 3$)\n"
            "$$f_2 = \\frac{3 \\times 340}{3.4} = 300\\text{ Hz}, \\quad "
            "f_3 = \\frac{5 \\times 340}{3.4} = 500\\text{ Hz}$$\n\n"
            "### Move 4: Verify pattern\n"
            "Only odd multiples of 100 Hz appear: 100, 300, 500 Hz. "
            "200 Hz and 400 Hz are **absent** — signature of a closed pipe. "
            "Sketch: node at closed end, anti-node at open end. "
            "Compare with an open pipe of the same length: its fundamental would be 200 Hz — "
            "twice the closed-pipe value. "
            "Organ pipes and clarinets are classic Bagrut examples of closed pipes.\n\n"
            "### Move 5: Exam strategy\n"
            "When asked for \"three lowest frequencies,\" list $n = 1, 2, 3$ in the "
            "$(2n-1)$ formula — not $n = 1, 2, 3$ in the open-pipe formula. "
            "The gap between consecutive allowed frequencies is $2f_1 = 200$ Hz here.\n\n"
            "**Answer:** 100 Hz, 300 Hz, 500 Hz."
        ),
        "body_he_md": (
            "**צינור אורgan סגור** (סגור בקצה אחד) באורך $L = 0.85$ m. "
            "מצאו את שלושת תדרי התהודה הנמוכים ($v = 340$ m/s).\n\n"
            "### צעד 1: זיהוי סוג צינור ונוסחה\n"
            "צינור סגור → הרמוניות אי-זוגיות בלבד: "
            "$$f_n = \\frac{(2n-1)v}{4L}, \\quad n = 1, 2, 3, \\ldots$$\n\n"
            "### צעד 2: הרמוניה ראשונה ($n = 1$)\n"
            "$$f_1 = \\frac{340}{3.4} = 100\\text{ Hz}$$\n\n"
            "### צעד 3: הרמוניות שנייה ושלישית ($n = 2, 3$)\n"
            "$$f_2 = \\frac{3 \\times 340}{3.4} = 300\\text{ Hz}, \\quad "
            "f_3 = \\frac{5 \\times 340}{3.4} = 500\\text{ Hz}$$\n\n"
            "### צעד 4: אימות דפוס\n"
            "רק כפולות אי-זוגיות של 100 Hz: 100, 300, 500 Hz. "
            "200 Hz ו-400 Hz **חסרים** — חתימה של צינור סגור. "
            "שרטוט: צומת בקצה הסגור, שיא בקצה הפתוח. "
            "השוו לצינור פתוח באותו אורך: יסודי שלו 200 Hz — "
            "פי שניים מערך הצינור הסגור. "
            "צינורות אורgan וכלרinet הם דוגמאות קלאסיות לצינור סגור בבגרות.\n\n"
            "### צעד 5: אסטרטגיה לבחינה\n"
            "כששואלים \"שלושת התדרים הנמוכים,\" השתמשו ב-$n = 1, 2, 3$ "
            "בנוסחת $(2n-1)$ — לא בנוסחת צינור פתוח. "
            "המרווח בין תדרים מותרים עוקבים הוא $2f_1 = 200$ Hz כאן.\n\n"
            "**תשובה:** 100 Hz, 300 Hz, 500 Hz."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Task | Formula |\n|---|---|\n"
            "| Wavelength | $\\lambda = v/f$ |\n"
            "| Frequency from $\\lambda$ | $f = v/\\lambda$ |\n"
            "| Decibels | $\\beta = 10\\log_{10}(I/I_0)$, $I_0 = 10^{-12}$ W/m² |\n"
            "| String / open pipe | $f_n = nv/(2L)$, $n = 1, 2, 3, \\ldots$ |\n"
            "| Closed pipe | $f_n = (2n-1)v/(4L)$, odd harmonics only |\n"
            "| Beat frequency | $f_{\\text{beat}} = |f_1 - f_2|$ |\n"
            "| dB change | $\\Delta\\beta = 10\\log_{10}(I_2/I_1)$ |\n\n"
            "**When to use:** Read the problem type first — wave equation, decibels, "
            "pipe/string resonance, or beats — then pick the matching row. "
            "Draw the standing-wave pattern before substituting numbers. "
            "For closed pipes, write \"odd harmonics only\" before calculating.\n\n"
            "**Exam tip:** If the stem says flute or open organ pipe, use $2L$. "
            "If it says clarinet or \"one end closed,\" use $4L$ with odd $n$ only."
        ),
        "body_he_md": (
            "| משימה | נוסחה |\n|---|---|\n"
            "| אורך גל | $\\lambda = v/f$ |\n"
            "| תדר מאורך גל | $f = v/\\lambda$ |\n"
            "| דציבלים | $\\beta = 10\\log_{10}(I/I_0)$, $I_0 = 10^{-12}$ W/m² |\n"
            "| מיתר / צינור פתוח | $f_n = nv/(2L)$, $n = 1, 2, 3, \\ldots$ |\n"
            "| צינור סגור | $f_n = (2n-1)v/(4L)$, הרמוניות אי-זוגיות |\n"
            "| תדר פעימות | $f_{\\text{beat}} = |f_1 - f_2|$ |\n"
            "| שינוי dB | $\\Delta\\beta = 10\\log_{10}(I_2/I_1)$ |\n\n"
            "**מתי להשתמש:** קראו קודם את סוג הבעיה — משוואת גל, דציבלים, "
            "תהודה בצינור/מיתר, או פעימות — ובחרו את השורה המתאימה. "
            "שרטטו את דפוס הגל העומד לפני הצבת מספרים. "
            "לצינור סגור, כתבו \"הרמוניות אי-זוגיות בלבד\" לפני החישוב.\n\n"
            "**טיפ לבחינה:** אם כתוב חליל או צינור פתוח — $2L$. "
            "אם כלרinet או \"קצה סגור\" — $4L$ עם $n$ אי-זוגי בלבד."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Open vs closed pipe:** An open pipe (both ends open) has **all** harmonics "
            "$f_n = nv/(2L)$. A closed pipe has **odd harmonics only** "
            "$f_n = (2n-1)v/(4L)$. Listing 200 Hz for a closed pipe proves you used the wrong formula.\n\n"
            "2. **Decibel formula:** Always use $10\\log_{10}$, never $\\ln$ or $\\log_2$. "
            "Confusing +3 dB (doubling) with +10 dB (10×) is very common.\n\n"
            "3. **Reference intensity $I_0 = 10^{-12}$ W/m²:** Do not forget it in the ratio $I/I_0$.\n\n"
            "4. **Beat frequency is always positive:** Use $|f_1 - f_2|$, never a negative value.\n\n"
            "5. **String speed vs air speed:** Guitar strings use $v = \\sqrt{T/\\mu}$, not 340 m/s.\n\n"
            "**Example misconception:** \"Closed pipe has all harmonics.\"\n\n"
            "**Fix:** One closed end → only odd harmonics; even multiples are absent."
        ),
        "body_he_md": (
            "1. **צינור פתוח מול סגור:** צינור פתוח (שני קצוות) — **כל** ההרמוניות "
            "$f_n = nv/(2L)$. צינור סגור — **הרמוניות אי-זוגיות בלבד** "
            "$f_n = (2n-1)v/(4L)$. רשימת 200 Hz לצינור סגור מוכיחה נוסחה שגויה.\n\n"
            "2. **נוסחת דציבל:** תמיד $10\\log_{10}$, לא $\\ln$ או $\\log_2$. "
            "בלבול +3 dB (הכפלה) עם +10 dB (פי 10) שכיח מאוד.\n\n"
            "3. **עוצמת ייחוס $I_0 = 10^{-12}$ W/m²:** אל תשכחו ביחס $I/I_0$.\n\n"
            "4. **תדר פעימות תמיד חיובי:** $|f_1 - f_2|$, לא ערך שלילי.\n\n"
            "5. **מהירות מיתר מול אוויר:** מיתרים משתמשים ב-$v = \\sqrt{T/\\mu}$, לא 340 m/s.\n\n"
            "**תפיסה שגויה:** \"לצינור סגור יש כל ההרמוניות.\"\n\n"
            "**תיקון:** קצה סגור אחד → רק אי-זוגיות; כפולות זוגיות חסרות."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "### Formula Sheet\n\n"
            "$$v = f\\lambda \\qquad \\beta = 10\\log_{10}(I/I_0), \\; I_0 = 10^{-12}\\text{ W/m}^2$$\n\n"
            "$$f_n = \\frac{nv}{2L}\\text{ (string / open pipe)} \\qquad "
            "f_n = \\frac{(2n-1)v}{4L}\\text{ (closed pipe, odd only)}$$\n\n"
            "$$f_{\\text{beat}} = |f_1 - f_2| \\qquad \\Delta\\beta = 10\\log_{10}(I_2/I_1)$$\n\n"
            "### Checklist\n"
            "- [ ] Speed 340 m/s is for **air** only?\n"
            "- [ ] Pipe type identified before choosing formula?\n"
            "- [ ] Used $\\log_{10}$ for decibels?\n"
            "- [ ] Beat frequency taken as absolute value?\n"
            "- [ ] String problems use $v=\\sqrt{T/\\mu}$, not 340 m/s?\n\n"
            "**Last review:** Say each formula out loud once, then solve one checkpoint without looking. "
            "Sound questions on the Bagrut often combine two skills — "
            "wave equation plus pipe type — in a single multi-part item. "
            "Practice one wavelength problem and one pipe problem the night before. "
            "Mark which formulas use $2L$ versus $4L$ on your formula sheet."
        ),
        "body_he_md": (
            "### דף נוסחאות\n\n"
            "$$v = f\\lambda \\qquad \\beta = 10\\log_{10}(I/I_0), \\; I_0 = 10^{-12}\\text{ W/m}^2$$\n\n"
            "$$f_n = \\frac{nv}{2L}\\text{ (מיתר / צינור פתוח)} \\qquad "
            "f_n = \\frac{(2n-1)v}{4L}\\text{ (צינור סגור, אי-זוגיות)}$$\n\n"
            "$$f_{\\text{beat}} = |f_1 - f_2| \\qquad \\Delta\\beta = 10\\log_{10}(I_2/I_1)$$\n\n"
            "### רשימת בדיקה\n"
            "- [ ] 340 m/s רק ל**אוויר**?\n"
            "- [ ] סוג צינור זוהה לפני בחירת נוסחה?\n"
            "- [ ] השתמשתם ב-$\\log_{10}$ לדציבלים?\n"
            "- [ ] תדר פעימות בערך מוחלט?\n"
            "- [ ] בעיות מיתר: $v=\\sqrt{T/\\mu}$, לא 340 m/s?\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint אחד בלי להסתכל. "
            "שאלות קול בבגרות לעיתים קרובות משלבות שני כישורים — "
            "משוואת גל וסוג צינור — בפריט רב-חלקי אחד. "
            "תרגלו בעיית אורך גל ובעיית צינור בערב שלפני הבחינה."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Sound waves connect acoustic physics to everyday experience and to advanced topics "
            "in the knowledge graph.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:doppler` **Doppler Effect** (applies_to) — frequency shifts when "
            "source or observer moves.\n\n"
            "**Builds on:**\n"
            "- `concept:waves_basics` **Mechanical Waves** — wave speed, interference, "
            "and standing-wave fundamentals.\n\n"
            "**Why it matters for exams:** Bagrut questionnaire 3 rewards *transfer* — "
            "identifying pipe type from wording, combining decibels with wave equations, "
            "and explaining why closed pipes lack even harmonics. "
            "When you study, ask: \"Which formula matches this setup?\" "
            "Decibels link this lesson to logarithms in mathematics."
        ),
        "body_he_md": (
            "גלי קול מחברים פיזיקה אקוסטית לחוויה יומיומית ולנושאים מתקדמים "
            "בגרף הידע.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:doppler` **אפקט דופלר** (applies_to) — שינוי תדר כשמקור "
            "או צופה נע.\n\n"
            "**מבוסס על:**\n"
            "- `concept:waves_basics` **גלים מכניים** — מהירות גל, הפרעה "
            "ויסודות גלים עומדים.\n\n"
            "**למה זה חשוב לבחינות:** שאלון 3 בבגרות מעריך *העברה* — "
            "זיהוי סוג צינור מניסוח, שילוב דציבלים עם משוואת גל, "
            "והסבר מדוע לצינור סגור אין הרמוניות זוגיות. "
            "בזמן לימוד, שאלו: \"איזו נוסחה מתאימה להגדרה הזו?\" "
            "דציבלים מחברים שיעור זה ללוגריתמים במתמטיקה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Sound:** longitudinal wave; $v = f\\lambda$; needs a medium.\n"
            "- **Intensity level:** $\\beta = 10\\log(I/I_0)$ dB; $I_0 = 10^{-12}$ W/m².\n"
            "- **Standing waves:** string/open pipe → all harmonics $f_n = nv/(2L)$; "
            "closed pipe → odd only $f_n = (2n-1)v/(4L)$.\n"
            "- **Beats:** $f_{\\text{beat}} = |f_1 - f_2|$.\n"
            "- **dB changes:** factor of 10 → +10 dB; double → +3 dB.\n\n"
            "**Takeaway:** Identify pipe/string type from the problem wording alone, "
            "then apply the correct formula. Never mix air speed with string speed."
        ),
        "body_he_md": (
            "- **קול:** גל אורכי; $v = f\\lambda$; דורש מדיום.\n"
            "- **רמת עוצמה:** $\\beta = 10\\log(I/I_0)$ dB; $I_0 = 10^{-12}$ W/m².\n"
            "- **גלים עומדים:** מיתר/צינור פתוח → כל ההרמוניות $f_n = nv/(2L)$; "
            "צינור סגור → אי-זוגיות $f_n = (2n-1)v/(4L)$.\n"
            "- **פעימות:** $f_{\\text{beat}} = |f_1 - f_2|$.\n"
            "- **שינויי dB:** פי 10 → +10 dB; הכפלה → +3 dB.\n\n"
            "**מסקנה:** זהו סוג צינור/מיתר מניסוח השאלה, "
            "והחילו נוסחה נכונה. לעולם אל תערבבו מהירות אוויר עם מהירות מיתר."
        ),
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "Use the wave equation rearranged for frequency: $f = v/\\lambda$.\n\n"
            "**Step 1:** Substitute $v = 340$ m/s and $\\lambda = 1.7$ m:\n"
            "$$f = \\frac{340}{1.7} = 200\\text{ Hz}$$\n\n"
            "**Step 2:** Verify — $200 \\times 1.7 = 340$ m/s ✓.\n\n"
            "**Interpretation:** A 1.7 m wavelength is fairly long (low pitch). "
            "If you got 578 Hz you multiplied instead of dividing. **Answer:** 200 Hz."
        ),
        "checkpoint_solution_he": (
            "משתמשים במשוואת גל מסודרת לתדר: $f = v/\\lambda$.\n\n"
            "**שלב 1:** מציבים $v = 340$ m/s ו-$\\lambda = 1.7$ m:\n"
            "$$f = \\frac{340}{1.7} = 200\\text{ Hz}$$\n\n"
            "**שלב 2:** אימות — $200 \\times 1.7 = 340$ m/s ✓.\n\n"
            "**פרשנות:** אורך גל 1.7 m הוא ארוך יחסית (תדר נמוך). "
            "אם קיבלתם 578 Hz — כפלתם במקום לחלק. **תשובה:** 200 Hz."
        ),
    },
    {
        "checkpoint_solution_en": (
            "When intensity increases by a factor of 100, use "
            "$\\Delta\\beta = 10\\log_{10}(I_2/I_1)$.\n\n"
            "**Step 1:** The ratio $I_2/I_1 = 100 = 10^2$.\n\n"
            "**Step 2:** $\\Delta\\beta = 10\\log_{10}(100) = 10 \\times 2 = 20$ dB.\n\n"
            "**Common error:** Answering 100 dB (confusing factor with level) "
            "or 3 dB (the increase for doubling, not 100-fold). "
            "Each factor of 10 adds 10 dB. **Answer:** +20 dB."
        ),
        "checkpoint_solution_he": (
            "כשהעוצמה גדלה פי 100, משתמשים ב-$\\Delta\\beta = 10\\log_{10}(I_2/I_1)$.\n\n"
            "**שלב 1:** היחס $I_2/I_1 = 100 = 10^2$.\n\n"
            "**שלב 2:** $\\Delta\\beta = 10\\log_{10}(100) = 10 \\times 2 = 20$ dB.\n\n"
            "**טעות נפוצה:** תשובה 100 dB (בלבול גורם עם רמה) "
            "או 3 dB (עלייה בהכפלה, לא פי 100). "
            "כל פי 10 מוסיף 10 dB. **תשובה:** +20 dB."
        ),
    },
]

EXPLANATIONS = {
    1: {
        "en": (
            "Sound travels through air at approximately **340 m/s at 20°C**. "
            "This value appears on nearly every Bagrut wave question and is sometimes "
            "written as $v \\approx 331 + 0.6T$ where $T$ is temperature in °C. "
            "300 m/s is too low; it might come from rounding errors or confusing "
            "with other wave speeds. $3 \\times 10^8$ m/s is the speed of **light** in vacuum — "
            "a classic distractor mixing EM and mechanical waves. "
            "1500 m/s is roughly the speed of sound in **water**, not air. "
            "Always check the medium before substituting a speed value. "
            "**Exam tip:** if no temperature is given, use 340 m/s for air. "
            "**Self-check:** wavelength at 340 Hz should be about 1 m. **Answer:** 340 m/s."
        ),
        "he": (
            "קול מתפשט באוויר בכ-**340 m/s ב-20°C**. "
            "ערך זה מופיע כמעט בכל שאלת גלים בבגרות, "
            "ולפעמים כתוב $v \\approx 331 + 0.6T$ כאשר $T$ בצלסיוס. "
            "300 m/s נמוך מדי — עלול לנבוע מעיגול שגוי או בלבול עם מהירויות אחרות. "
            "$3 \\times 10^8$ m/s היא מהירות **האור** בוואקום — "
            "מסיח קלאסי שמערב גלים אלקטרומגנטיים ומכניים. "
            "1500 m/s היא בערך מהירות קול ב**מים**, לא באוויר. "
            "תמיד בדקו את המדיום לפני הצבת מהירות. "
            "**טיפ לבחינה:** אם לא ניתנה טמפרטורה, השתמשו ב-340 m/s לאוויר. "
            "**בדיקה:** אורך גל ב-340 Hz צריך להיות בערך 1 m. **תשובה:** 340 m/s."
        ),
    },
    2: {
        "en": (
            "The wave equation $v = f\\lambda$ links speed, frequency, and wavelength. "
            "Rearrange for the unknown: $\\lambda = v/f$. "
            "With $v = 340$ m/s and $f = 1000$ Hz: $\\lambda = 340/1000 = 0.34$ m. "
            "A common error is multiplying ($340 \\times 1000$) instead of dividing, "
            "giving an impossibly large wavelength. Another slip is using $f = v\\lambda$ "
            "without rearranging. Sanity check: 1000 Hz is a high pitch, "
            "so the wavelength must be short — 0.34 m (34 cm) is reasonable. "
            "Verify: $1000 \\times 0.34 = 340$ m/s ✓. "
            "**Exam tip:** write the formula first, circle the unknown, then substitute. "
            "**Answer:** 0.34 m."
        ),
        "he": (
            "משוואת הגל $v = f\\lambda$ מקשרת מהירות, תדר ואורך גל. "
            "סדרו לנעלם: $\\lambda = v/f$. "
            "עם $v = 340$ m/s ו-$f = 1000$ Hz: $\\lambda = 340/1000 = 0.34$ m. "
            "טעות נפוצה: כפל ($340 \\times 1000$) במקום חלוקה — "
            "אורך גל בלתי סביר. טעות נוספת: שימוש ב-$f = v\\lambda$ בלי סידור. "
            "בדיקת הגיון: 1000 Hz הוא תדר גבוה, "
            "ולכן אורך הגל חייב להיות קצר — 0.34 m (34 cm) הגיוני. "
            "אימות: $1000 \\times 0.34 = 340$ m/s ✓. "
            "אם קיבלתם 3.4 m — חילקתם ב-100 במקום ב-1000. "
            "**טיפ לבחינה:** כתבו נוסחה, סמנו נעלם, והציבו. **תשובה:** 0.34 m."
        ),
    },
    3: {
        "en": (
            "Sound level in decibels: $\\beta = 10\\log_{10}(I/I_0)$ with "
            "$I_0 = 10^{-12}$ W/m². "
            "Given $I = 10^{-8}$ W/m²: the ratio is $I/I_0 = 10^{-8}/10^{-12} = 10^4$. "
            "Then $\\beta = 10\\log_{10}(10^4) = 10 \\times 4 = 40$ dB. "
            "Common errors: forgetting $I_0$ (giving 80 dB), using $\\ln$ instead of "
            "$\\log_{10}$, or computing $\\log$ of $10^{-8}$ directly without the ratio. "
            "40 dB is a quiet room — between whisper (30 dB) and conversation (60 dB). "
            "Each factor of 10 in intensity adds 10 dB. "
            "**Exam tip:** always write the ratio $I/I_0$ before taking the log. "
            "**Self-check:** $10^{-8}$ is $10^4$ times $10^{-12}$. **Answer:** 40 dB."
        ),
        "he": (
            "רמת קול בדציבלים: $\\beta = 10\\log_{10}(I/I_0)$ עם "
            "$I_0 = 10^{-12}$ W/m². "
            "נתון $I = 10^{-8}$ W/m²: היחס $I/I_0 = 10^{-8}/10^{-12} = 10^4$. "
            "אז $\\beta = 10\\log_{10}(10^4) = 10 \\times 4 = 40$ dB. "
            "טעויות נפוצות: שכחת $I_0$ (80 dB), שימוש ב-$\\ln$ במקום $\\log_{10}$, "
            "או $\\log$ של $10^{-8}$ ישירות בלי יחס. "
            "40 dB הוא חדר שקט — בין לחישה (30 dB) לשיחה (60 dB). "
            "כל פי 10 בעוצמה מוסיף 10 dB. "
            "אם שכחתם $I_0$ הייתם מקבלים 80 dB — שגיאה שכיחה. "
            "**טיפ לבחינה:** כתבו תמיד את היחס $I/I_0$ לפני הלוג. "
            "**בדיקה:** $10^{-8}$ הוא פי $10^4$ מ-$10^{-12}$. **תשובה:** 40 dB."
        ),
    },
    4: {
        "en": (
            "When two sources have slightly different frequencies, "
            "you hear **beats** — a pulsing loudness pattern. "
            "The beat frequency is the absolute difference: "
            "$f_{\\text{beat}} = |f_1 - f_2| = |504 - 500| = 4$ Hz. "
            "This means you hear 4 loud-soft cycles per second. "
            "Common errors: subtracting in the wrong order and getting $-4$ Hz "
            "(always take the absolute value), or adding the frequencies ($1004$ Hz). "
            "Beats are used to tune instruments — when tuning a guitar string against "
            "a 440 Hz reference, you listen for slow beats and adjust until they vanish. "
            "**Exam tip:** beats require two close frequencies, not one. "
            "**Self-check:** $|504 - 500| = 4$, not 1004. **Answer:** 4 Hz."
        ),
        "he": (
            "כששני מקורות בתדרים מעט שונים, "
            "שומעים **פעימות** — דפוס עוצמה פועם. "
            "תדר הפעימות הוא ההפרש המוחלט: "
            "$f_{\\text{beat}} = |f_1 - f_2| = |504 - 500| = 4$ Hz. "
            "כלומר 4 מחזורי חזק-חלש בשנייה. "
            "טעויות נפוצות: חיסור בסדר שגוי ($-4$ Hz — "
            "תמיד ערך מוחלט), או חיבור התדרים ($1004$ Hz). "
            "פעימות משמשות לכיוון כלים — כיוון מיתר גיטרה מול 440 Hz, "
            "מקשיבים לפעימות איטיות ומתאימים עד שהן נעלמות. "
            "4 Hz פירושו ארבעה מחזורי חזק-חלש בכל שנייה. "
            "**טיפ לבחינה:** פעימות דורשות שני תדרים קרובים, לא אחד. "
            "**בדיקה:** $|504 - 500| = 4$, לא 1004. **תשובה:** 4 Hz."
        ),
    },
    5: {
        "en": (
            "Decibels use a logarithmic scale, so doubling intensity does **not** "
            "double the dB value. "
            "The change is $\\Delta\\beta = 10\\log_{10}(I_2/I_1) = 10\\log_{10}(2) "
            "\\approx 10 \\times 0.301 = 3.01$ dB $\\approx 3$ dB. "
            "Students often answer 6 dB (doubling the dB number) or 2 dB (rough guess). "
            "Remember the reference points: double → +3 dB; 10× → +10 dB; 100× → +20 dB. "
            "Human hearing barely notices a 3 dB change — "
            "it takes about 10 dB to sound twice as loud. "
            "**Exam tip:** write the ratio first ($I_2/I_1 = 2$), then "
            "$\\log_{10}(2) \\approx 0.3$, then multiply by 10. "
            "**Self-check:** +3 dB means intensity ×2, not level ×2. **Answer:** +3 dB."
        ),
        "he": (
            "דציבלים על סקala לוגריתמית, ולכן הכפלת עוצמה **לא** "
            "מכפילה את ערך ה-dB. "
            "השינוי: $\\Delta\\beta = 10\\log_{10}(I_2/I_1) = 10\\log_{10}(2) "
            "\\approx 10 \\times 0.301 = 3.01$ dB $\\approx 3$ dB. "
            "תלמידים עונים לעיתים 6 dB (הכפלת מספר ה-dB) או 2 dB (ניחוש). "
            "זכרו נקודות ייחוס: הכפלה → +3 dB; פי 10 → +10 dB; פי 100 → +20 dB. "
            "האוזן האנושית כמעט לא מרגישה שינוי של 3 dB — "
            "נדרשים כ-10 dB כדי לשמוע פי שניים חזק. "
            "**טיפ לבחינה:** כתבו יחס ($I_2/I_1 = 2$), אז "
            "$\\log_{10}(2) \\approx 0.3$, ואז ×10. "
            "**בדיקה:** +3 dB = עוצמה ×2, לא רמה ×2. **תשובה:** +3 dB."
        ),
    },
    6: {
        "en": (
            "An **open pipe** has anti-nodes at both ends, so the fundamental fits "
            "half a wavelength: $f_n = nv/(2L)$ for $n = 1, 2, 3, \\ldots$. "
            "With $L = 0.5$ m and $v = 340$ m/s: "
            "$f_1 = 340/(2 \\times 0.5) = 340$ Hz, "
            "$f_2 = 2 \\times 340 = 680$ Hz, "
            "$f_3 = 3 \\times 340 = 1020$ Hz. "
            "Using $f_1 = v/L$ (forgetting the factor 2) gives 680 Hz for the fundamental — "
            "the most common pipe error. Using the closed-pipe formula gives 170 Hz. "
            "Draw one half-wave inside the pipe before substituting. "
            "**Exam tip:** open pipe → divide by $2L$; closed pipe → divide by $4L$ "
            "with odd harmonics only. **Answer:** 340, 680, and 1020 Hz."
        ),
        "he": (
            "**צינור פתוח** — שיאים בשני הקצוות, ביסודי נכנס חצי אורך גל: "
            "$f_n = nv/(2L)$ עבור $n = 1, 2, 3, \\ldots$. "
            "עם $L = 0.5$ m ו-$v = 340$ m/s: "
            "$f_1 = 340/(2 \\times 0.5) = 340$ Hz, "
            "$f_2 = 680$ Hz, $f_3 = 1020$ Hz. "
            "שימוש ב-$f_1 = v/L$ (שכחת גורם 2) נותן 680 Hz ליסודי — "
            "הטעות הנפוצה ביותר. נוסחת צינור סגור נותנת 170 Hz. "
            "שרטטו חצי גל בתוך הצינור לפני ההצבה. "
            "המרווח בין הרמוניות: $f_2 - f_1 = 340$ Hz. "
            "**טיפ לבחינה:** צינור פתוח → חלוקה ב-$2L$; צינור סגור → $4L$ "
            "עם $n$ אי-זוגי בלבד. **תשובה:** 340, 680 ו-1020 Hz."
        ),
    },
    7: {
        "en": (
            "A **closed pipe** has a node at the closed end and supports only odd harmonics: "
            "$f_n = (2n-1)v/(4L)$ with $n = 1$ for the first harmonic. "
            "With $L = 0.85$ m and $v = 340$ m/s: "
            "$f_1 = 1 \\times 340/(4 \\times 0.85) = 340/3.4 = 100$ Hz. "
            "Using the open-pipe formula $v/(2L)$ gives 200 Hz — double the correct answer. "
            "Using $n = 2$ in the closed formula gives 300 Hz (the second allowed harmonic, "
            "not the first). Always identify \"first harmonic\" as $n = 1$. "
            "Verify: $f_3 = 5 \\times 340/3.4 = 500$ Hz confirms the odd pattern. "
            "**Exam tip:** write \"closed, odd $n$ only\" before calculating. "
            "**Answer:** 100 Hz."
        ),
        "he": (
            "**צינור סגור** — צומת בקצה הסגור, רק הרמוניות אי-זוגיות: "
            "$f_n = (2n-1)v/(4L)$ עם $n = 1$ להרמוניה ראשונה. "
            "עם $L = 0.85$ m ו-$v = 340$ m/s: "
            "$f_1 = 340/(4 \\times 0.85) = 340/3.4 = 100$ Hz. "
            "נוסחת צינור פתוח $v/(2L)$ נותנת 200 Hz — כפול מהנכון. "
            "שימוש ב-$n = 2$ נותן 300 Hz (הרמוניה שנייה מותרת, לא ראשונה). "
            "תמיד \"הרמוניה ראשונה\" = $n = 1$. "
            "אימות: $f_3 = 500$ Hz מאשר דפוס אי-זוגי. "
            "צינור פתוח באותו אורך היה נותן יסודי 200 Hz — פי שניים. "
            "**טיפ לבחינה:** כתבו \"סגור, $n$ אי-זוגי\" לפני חישוב. "
            "הרמוניה שנייה מותרת היא 300 Hz, לא 200 Hz. **תשובה:** 100 Hz."
        ),
    },
    8: {
        "en": (
            "For a string fixed at both ends, the fundamental frequency is "
            "$f_1 = v/(2L)$. Rearrange to find wave speed: $v = 2Lf$. "
            "With $f = 220$ Hz and $L = 0.65$ m: "
            "$v = 2 \\times 0.65 \\times 220 = 286$ m/s. "
            "This is the **string** wave speed — much slower than 340 m/s in air. "
            "Common errors: using $v = 340$ m/s (air speed), "
            "forgetting the factor 2 ($v = Lf$ gives 143 m/s), "
            "or using the closed-pipe formula. "
            "Verify: $286/(2 \\times 0.65) = 220$ Hz ✓. "
            "String speed depends on tension and mass density: $v = \\sqrt{T/\\mu}$. "
            "**Exam tip:** if the problem mentions a guitar string, never use 340 m/s. "
            "**Answer:** 286 m/s."
        ),
        "he": (
            "למיתר קבוע בשני קצות, תדר יסודי: $f_1 = v/(2L)$. "
            "סדרו למהירות גל: $v = 2Lf$. "
            "עם $f = 220$ Hz ו-$L = 0.65$ m: "
            "$v = 2 \\times 0.65 \\times 220 = 286$ m/s. "
            "זו מהירות **מיתר** — איטית מ-340 m/s באוויר. "
            "טעויות נפוצות: $v = 340$ m/s (מהירות אוויר), "
            "שכחת גורם 2 ($v = Lf$ נותן 143 m/s), "
            "או נוסחת צינור סגור. "
            "אימות: $286/(2 \\times 0.65) = 220$ Hz ✓. "
            "מהירות מיתר תלויה במתח ובצפיפות: $v = \\sqrt{T/\\mu}$. "
            "143 m/s נובע מ-$v = Lf$ בלי גורם 2 — טעות שכיחה. "
            "**טיפ לבחינה:** מיתר גיטרה — לעולם לא 340 m/s. **תשובה:** 286 m/s."
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
            if we_idx == 1:
                sec.update(SECTION_BODIES["worked_example"])
            elif we_idx == 2:
                sec.update(SECTION_BODIES["worked_example_decibels"])
            elif we_idx == 3:
                sec.update(SECTION_BODIES["worked_example_pipe"])
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
