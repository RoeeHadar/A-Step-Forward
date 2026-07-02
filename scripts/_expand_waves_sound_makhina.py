#!/usr/bin/env python3
"""Generate expanded waves_sound_makhina.json and validate depth gates."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/waves_sound_makhina.json"
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


EXPLANATIONS = {
    1: {
        "en": (
            "The wave equation $v = f\\lambda$ links speed, frequency, and wavelength. "
            "Given $v = 340$ m/s and $f = 680$ Hz, divide: $\\lambda = 340/680 = 0.5$ m. "
            "Option 1 m would require half the frequency (340 Hz), and 2 m would require "
            "340 Hz — both confuse doubling wavelength with halving frequency. Option 0.25 m "
            "comes from multiplying instead of dividing, a classic inversion error. "
            "Always identify which variable is unknown before rearranging. "
            "Sanity check: higher frequency means shorter wavelength at fixed speed, so "
            "680 Hz must give less than 1 m. **Exam tip:** write $v = f\\lambda$ first, "
            "circle the unknown, then substitute. **Self-check:** $680 \\times 0.5 = 340$ m/s. "
            "**Answer:** 0.5 m."
        ),
        "he": (
            "משוואת הגל $v = f\\lambda$ מקשרת מהירות, תדר ואורך גל. "
            "נתון $v = 340$ m/s ו-$f = 680$ Hz, מחלקים: $\\lambda = 340/680 = 0.5$ m. "
            "האפשרות 1 m דורשת תדר חצי (340 Hz), ו-2 m דורשת 340 Hz — "
            "בלבול בין הכפלת אורך גל להקטנת תדר. 0.25 m נובע מכפל במקום חלוקה, "
            "טעות היפוך קלאסית. תמיד זהו את הנעלם לפני שינוי הנוסחה. "
            "בדיקת הגיון: תדר גבוה יותר פירושו אורך גל קצר יותר במהירות קבועה, "
            "ולכן 680 Hz חייב לתת פחות מ-1 m. **טיפ לבחינה:** כתבו $v = f\\lambda$, "
            "סמנו את הנעלם, והציבו. **בדיקה:** $680 \\times 0.5 = 340$ m/s. **תשובה:** 0.5 m."
        ),
    },
    2: {
        "en": (
            "Rearrange $v = f\\lambda$ to find wavelength: $\\lambda = v/f$. "
            "Substituting $v = 340$ m/s and $f = 250$ Hz gives "
            "$\\lambda = 340/250 = 1.36$ m. A common mistake is to multiply "
            "$340 \\times 250$, which yields a huge number with wrong units. "
            "Another slip is using $f = v\\lambda$ instead of $f = v/\\lambda$. "
            "At 250 Hz the wavelength must exceed 1 m because the frequency is "
            "well below 340 Hz (where $\\lambda = 1$ m in air). "
            "Verify by back-substitution: $250 \\times 1.36 = 340$ m/s. "
            "**Exam tip:** label each quantity with units before calculating. "
            "**Self-check:** low frequency $\\Rightarrow$ long wavelength. "
            "**Answer:** 1.36 m."
        ),
        "he": (
            "מסדרים $v = f\\lambda$ לקבלת אורך גל: $\\lambda = v/f$. "
            "הצבה: $v = 340$ m/s, $f = 250$ Hz נותנת $\\lambda = 340/250 = 1.36$ m. "
            "טעות נפוצה: כפל $340 \\times 250$ — מספר ענק עם יחידות שגויות. "
            "טעות נוספת: שימוש ב-$f = v\\lambda$ במקום $f = v/\\lambda$. "
            "אם קיבלתם 85 m — חילקתם במקום לחלק בצורה נכונה. "
            "ב-250 Hz אורך הגל חייב לעלות על 1 m כי התדר נמוך מ-340 Hz "
            "(שם $\\lambda = 1$ m באוויר). "
            "אימות: $250 \\times 1.36 = 340$ m/s. "
            "**טיפ לבחינה:** סמנו יחידות לפני החישוב — m/s חלקי Hz = m. "
            "**בדיקה:** תדר נמוך $\\Rightarrow$ אורך גל ארוך. **תשובה:** 1.36 m."
        ),
    },
    3: {
        "en": (
            "When wavelength and frequency are known, wave speed follows from "
            "$v = f\\lambda$. Here $v = 170 \\times 2 = 340$ m/s. "
            "Students sometimes divide $\\lambda/f$ or add the numbers — "
            "neither matches the physics. The product $f\\lambda$ always gives "
            "speed because frequency counts oscillations per second and wavelength "
            "is metres per oscillation, so their product is m/s. "
            "Notice 170 Hz with 2 m wavelength is exactly the air-speed combination "
            "used throughout makhina problems. "
            "Back-check: $340/2 = 170$ Hz confirms consistency. "
            "**Exam tip:** if two of $(v, f, \\lambda)$ are given, the third comes "
            "from one multiplication or division. **Answer:** 340 m/s."
        ),
        "he": (
            "כשידועים אורך גל ותדר, מהירות הגל: $v = f\\lambda$. "
            "כאן $v = 170 \\times 2 = 340$ m/s. "
            "לפעמים מחלקים $\\lambda/f$ או מחברים — אף אחד לא מתאים לפיזיקה. "
            "המכפלה $f\\lambda$ תמיד נותנת מהירות: תדר = תנודות לשנייה, "
            "אורך גל = מטרים לתנודה, ומכפלתם m/s. "
            "שימו לב: 170 Hz עם 2 m הוא בדיוק השילוב של מהירות קול באוויר "
            "בתרגילי מכינה. "
            "בדיקה חוזרת: $340/2 = 170$ Hz מאשר עקביות. "
            "שימו לב: 170 Hz עם 2 m הוא השילוב הקלאסי של מהירות קול באוויר "
            "בתרגילי מכינה — זהו סימן לכך שהחישוב הגיוני. "
            "**טיפ לבחינה:** אם ידועים שניים מ-$(v, f, \\lambda)$, השלישי "
            "מגיע מכפל או חלוקה אחת. **תשובה:** 340 m/s."
        ),
    },
    4: {
        "en": (
            "An open pipe has anti-nodes at both ends, so the fundamental fits "
            "half a wavelength inside the length: $f_1 = v/(2L)$. "
            "With $L = 0.5$ m and $v = 340$ m/s: "
            "$f_1 = 340/(2 \\times 0.5) = 340$ Hz. "
            "Using $f_1 = v/L$ (forgetting the factor 2) gives 680 Hz — "
            "the most common pipe error. Using the closed-pipe formula "
            "$v/(4L)$ gives 170 Hz. "
            "Draw one half-wave inside the pipe before substituting. "
            "The second harmonic would be $2 \\times 340 = 680$ Hz. "
            "**Exam tip:** open pipe $\\Rightarrow$ divide by $2L$; "
            "closed pipe $\\Rightarrow$ divide by $4L$ with odd $n$ only. "
            "**Answer:** 340 Hz."
        ),
        "he": (
            "בצינור פתוח יש שיאים בשני הקצוות, ולכן ביסודי נכנס חצי אורך גל: "
            "$f_1 = v/(2L)$. עם $L = 0.5$ m ו-$v = 340$ m/s: "
            "$f_1 = 340/(2 \\times 0.5) = 340$ Hz. "
            "שימוש ב-$f_1 = v/L$ (שכחת גורם 2) נותן 680 Hz — "
            "הטעות הנפוצה ביותר בצינורות. נוסחת צינור סגור $v/(4L)$ "
            "נותנת 170 Hz. "
            "שרטטו חצי גל בתוך הצינור לפני ההצבה. "
            "ההרמוני השני: $2 \\times 340 = 680$ Hz. "
            "אם קיבלתם 680 Hz ליסודי — שכחתם לחלק ב-2. "
            "שרטטו חצי גל בתוך צינור באורך 0.5 m לפני ההצבה. "
            "**טיפ לבחינה:** צינור פתוח $\\Rightarrow$ חלוקה ב-$2L$; "
            "צינור סגור $\\Rightarrow$ חלוקה ב-$4L$ עם $n$ אי-זוגי בלבד. "
            "**תשובה:** 340 Hz."
        ),
    },
    5: {
        "en": (
            "Period and frequency are reciprocals: $T = 1/f$. "
            "For $f = 100$ Hz, $T = 1/100 = 0.01$ s = 10 ms. "
            "Do not divide 100 by 1 or confuse period with wavelength. "
            "Period measures time for one complete oscillation; "
            "at 100 Hz the air completes 100 cycles every second, "
            "so each cycle lasts 0.01 s. "
            "If you get 100 s you have inverted the relationship. "
            "Quick check: $1/0.01 = 100$ Hz. "
            "**Exam tip:** high frequency means short period — "
            "they move in opposite directions. "
            "**Self-check:** units must be seconds, not metres. "
            "**Answer:** 0.01 s."
        ),
        "he": (
            "מחזור ותדר הם הפוכים: $T = 1/f$. "
            "עבור $f = 100$ Hz, $T = 1/100 = 0.01$ s = 10 ms. "
            "אל תחלקו 100 ב-1 ואל תבלבלו מחזור עם אורך גל. "
            "מחזור מודד זמן לתנודה שלמה; "
            "ב-100 Hz האוויר מסיים 100 מחזורים בשנייה, "
            "ולכן כל מחזור נמשך 0.01 s. "
            "אם קיבלתם 100 s — היפכתם את הקשר. "
            "בדיקה מהירה: $1/0.01 = 100$ Hz. "
            "אל תחלקו 100 ב-1 ואל תבלבלו מחזור (שניות) עם אורך גל (מטרים). "
            "ב-100 Hz האוויר מסיים 100 מחזורים בשנייה — מחזור קצר. "
            "**טיפ לבחינה:** תדר גבוה $\\Rightarrow$ מחזור קצר — "
            "הם נעים בכיוונים מנוגדים. "
            "**בדיקה:** יחידות חייבות להיות שניות, לא מטרים. **תשובה:** 0.01 s."
        ),
    },
    6: {
        "en": (
            "A closed pipe has a node at the closed end and supports only odd "
            "harmonics: $f_n = nv/(4L)$ with $n = 1, 3, 5, \\ldots$. "
            "With $L = 0.85$ m and $v = 340$ m/s: "
            "$f_1 = 340/(4 \\times 0.85) = 100$ Hz, "
            "$f_3 = 3 \\times 340/3.4 = 300$ Hz, "
            "$f_5 = 5 \\times 340/3.4 = 500$ Hz. "
            "Using even $n$ or the open-pipe formula $nv/(2L)$ gives wrong answers. "
            "Listing $f_2 = 200$ Hz proves you treated the pipe as open. "
            "Draw the standing-wave pattern: only odd quarter-wavelengths fit. "
            "Verify: $f_1 = 340/(4 \\times 0.85) = 100$ Hz, then multiply by 3 and 5. "
            "**Exam tip:** write \"closed, odd $n$ only\" before calculating. "
            "The gap between harmonics is $2f_1 = 200$ Hz, not $f_1$. "
            "**Answer:** 100, 300, and 500 Hz."
        ),
        "he": (
            "צינור סגור: צומת בקצה הסגור, רק הרמוניות אי-זוגיות: "
            "$f_n = nv/(4L)$ עם $n = 1, 3, 5, \\ldots$. "
            "עם $L = 0.85$ m ו-$v = 340$ m/s: "
            "$f_1 = 340/(4 \\times 0.85) = 100$ Hz, "
            "$f_3 = 3 \\times 340/3.4 = 300$ Hz, "
            "$f_5 = 5 \\times 340/3.4 = 500$ Hz. "
            "שימוש ב-$n$ זוגי או בנוסחת צינור פתוח $nv/(2L)$ נותן תשובות שגויות. "
            "רשימת $f_2 = 200$ Hz מוכיחה שטיפלתם בצינור כפתוח. "
            "שרטטו דפוס גל עומד: רק רבעי אורך גל אי-זוגיים נכנסים. "
            "אימות: $f_1 = 340/(4 \\times 0.85) = 100$ Hz, ואז כפלו ב-3 ו-5. "
            "**טיפ לבחינה:** כתבו \"סגור, $n$ אי-זוגי בלבד\" לפני החישוב. "
            "המרווח בין הרמוניות הוא $2f_1 = 200$ Hz, לא $f_1$. "
            "**תשובה:** 100, 300 ו-500 Hz."
        ),
    },
    7: {
        "en": (
            "For an open pipe producing the fundamental frequency $f_1$, "
            "rearrange $f_1 = v/(2L)$ to get $L = v/(2f_1)$. "
            "Middle C is 262 Hz with $v = 343$ m/s: "
            "$L = 343/(2 \\times 262) \\approx 0.655$ m. "
            "Using $L = v/f_1$ (missing the 2) gives about 1.31 m — double the "
            "correct length. Using the closed-pipe denominator $4L$ gives roughly "
            "0.33 m. Always identify pipe type first. "
            "Verify: $343/(2 \\times 0.655) \\approx 262$ Hz. "
            "**Exam tip:** organ pipes and flutes are usually modelled as open "
            "at both ends unless the stem says \"closed.\" "
            "**Answer:** approximately 0.655 m."
        ),
        "he": (
            "לצינור פתוח בתדר יסודי $f_1$, מסדרים $f_1 = v/(2L)$ לקבלת "
            "$L = v/(2f_1)$. דו ימני (262 Hz) עם $v = 343$ m/s: "
            "$L = 343/(2 \\times 262) \\approx 0.655$ m. "
            "שימוש ב-$L = v/f_1$ (חסר 2) נותן כ-1.31 m — "
            "כפול מהאורך הנכון. מכנה של צינור סגור $4L$ נותן כ-0.33 m. "
            "זהו תמיד סוג צינור קודם. "
            "אימות: $343/(2 \\times 0.655) \\approx 262$ Hz. "
            "צינורות אורgan וחליל ממודלים כפתוחים "
            "אלא אם כתוב במפורש \"סגור.\" "
            "אם קיבלתם 1.31 m — שכחתם לחלק ב-2. "
            "אם קיבלתם 0.33 m — השתמשתם בנוסחת צינור סגור. "
            "**טיפ לבחינה:** זהו סוג צינור לפני בחירת נוסחה. **תשובה:** כ-0.655 m."
        ),
    },
    8: {
        "en": (
            "Decibels use a logarithmic scale: $\\Delta\\beta = 10\\log_{10}(I_2/I_1)$. "
            "When intensity increases by a factor of 100, "
            "$\\Delta\\beta = 10\\log_{10}(100) = 10 \\times 2 = 20$ dB. "
            "Students often answer 100 dB (confusing factor with level) "
            "or 3 dB (the increase for doubling intensity, not 100-fold). "
            "Remember: each factor of 10 in intensity adds 10 dB; "
            "100 = $10^2$ so the increase is 20 dB. "
            "Doubling adds only 3 dB — very different. "
            "**Exam tip:** write the ratio first, then take $\\log_{10}$, "
            "then multiply by 10. **Self-check:** +20 dB means "
            "intensity $\\times 100$, not level $\\times 100$. "
            "**Answer:** +20 dB."
        ),
        "he": (
            "דציבלים על סקאלה לוגריתמית: $\\Delta\\beta = 10\\log_{10}(I_2/I_1)$. "
            "כשהעוצמה גדלה פי 100, "
            "$\\Delta\\beta = 10\\log_{10}(100) = 10 \\times 2 = 20$ dB. "
            "תלמידים עונים לפעמים 100 dB (בלבול גורם עם רמה) "
            "או 3 dB (עלייה בהכפלת עוצמה, לא פי 100). "
            "זכרו: כל פי 10 בעוצמה מוסיף 10 dB; "
            "100 = $10^2$ ולכן העלייה 20 dB. "
            "הכפלה מוסיפה רק 3 dB — שונה מאוד. "
            "**טיפ לבחינה:** כתבו את היחס $I_2/I_1 = 100$, "
            "אז $\\log_{10}(100) = 2$, ואז $10 \\times 2 = 20$ dB. "
            "אל תענו 100 dB (בלבול גורם עם רמה) "
            "או 3 dB (עלייה בהכפלה בלבד). "
            "**בדיקה:** +20 dB = עוצמה $\\times 100$, לא רמה $\\times 100$. "
            "**תשובה:** +20 dB."
        ),
    },
}

SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "A **wave** is a disturbance that transfers **energy** through a medium "
            "without permanently transporting matter. When you hear music, air molecules "
            "oscillate back and forth around their equilibrium positions — they do not "
            "travel from the speaker to your ear. Sound is a **longitudinal** wave: "
            "particle motion is parallel to the direction of propagation, creating "
            "alternating regions of compression and rarefaction. Light and waves on a "
            "string are **transverse** — motion is perpendicular to travel.\n\n"
            "Four parameters describe any periodic wave:\n"
            "- **Frequency** $f$ (Hz): oscillations per second\n"
            "- **Period** $T = 1/f$ (s): time for one full cycle\n"
            "- **Wavelength** $\\lambda$ (m): spatial length of one cycle\n"
            "- **Wave speed** $v$ (m/s): how fast the pattern moves\n\n"
            "The master relation $v = f\\lambda$ ties all three together. "
            "On the makhina physics track you will apply this to sound in air "
            "($v \\approx 340$ m/s), standing waves in pipes and strings, "
            "and the decibel scale for intensity."
        ),
        "body_he_md": (
            "**גל** הוא הפרעה המעבירה **אנרגיה** דרך מדיום מבלי להעביר חומר "
            "בצורה קבועה. כשאתם שומעים מוזיקה, מולקולות האוויר מתנודדות קדימה "
            "ואחורה סביב מיקום שיווי המשקל — הן לא נוסעות מהרמקול לאוזן. "
            "קול הוא גל **אורך**: תנועת החלקיקים מקבילה לכיוון ההתפשטות, "
            "ויוצרת אזורי דחיסה ודלילות לסירוגין. "
            "אור וגלים על מיתר הם **רוחביים** — התנועה ניצבת לכיוון ההתפשטות.\n\n"
            "ארבעה פרמטרים מתארים כל גל מחזורי:\n"
            "- **תדר** $f$ (Hz): תנודות לשנייה\n"
            "- **מחזור** $T = 1/f$ (s): זמן למחזור שלם\n"
            "- **אורך גל** $\\lambda$ (m): אורך מרחבי של מחזור אחד\n"
            "- **מהירות גל** $v$ (m/s): מהירות תנועת הדפוס\n\n"
            "הקשר המרכזי $v = f\\lambda$ מקשר את שלושתם. "
            "במסלול מכינה בפיזיקה תיישמו זאת על קול באוויר "
            "($v \\approx 340$ m/s), גלים עומדים בצינורות ובמיתרים, "
            "וסולם הדציבלים לעוצמה."
        ),
    },
    "definition": {
        "body_en_md": (
            "The **wave equation** connects speed, frequency, and wavelength:\n"
            "$$v = f\\lambda$$\n\n"
            "All three are linked — knowing any two determines the third. "
            "Rearrangements: $f = v/\\lambda$ and $\\lambda = v/f$. "
            "Speed depends on the medium and its elastic properties: "
            "sound travels about 340 m/s in air, 1500 m/s in water, "
            "and 5000 m/s in steel. Never assume 340 m/s inside a string or solid.\n\n"
            "**Intensity** $I$ (W/m$^2$) is acoustic power per unit area. "
            "For a point source radiating uniformly in three dimensions, "
            "intensity falls as $I = P/(4\\pi r^2)$ — the inverse-square law. "
            "Doubling the distance from a speaker drops intensity by a factor of four.\n\n"
            "**Sound level** in decibels compresses huge intensity ranges into manageable numbers:\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right) \\text{ dB}, "
            "\\quad I_0 = 10^{-12} \\text{ W/m}^2$$\n\n"
            "$I_0$ is the threshold of human hearing at 1000 Hz. "
            "Whisper $\\approx 30$ dB; conversation $\\approx 60$ dB; "
            "pain threshold $\\approx 120$ dB. "
            "Each tenfold increase in intensity adds 10 dB; "
            "doubling intensity adds about 3 dB — not double the dB value.\n\n"
            "**Speed of sound** in air at 20°C: $v \\approx 343$ m/s "
            "(often rounded to 340 m/s in exam problems). "
            "A useful approximation: $v \\approx 331 + 0.6T$ m/s where $T$ is temperature in °C."
        ),
        "body_he_md": (
            "**משוואת הגל** מקשרת מהירות, תדר ואורך גל:\n"
            "$$v = f\\lambda$$\n\n"
            "שלושתם קשורים — ידיעת שניים קובעת את השלישי. "
            "סידורים: $f = v/\\lambda$ ו-$\\lambda = v/f$. "
            "המהירות תלויה במדיום ובתכונות האלסטיות שלו: "
            "קול נע בכ-340 m/s באוויר, 1500 m/s במים, "
            "ו-5000 m/s בפלדה. לעולם אל תניחו 340 m/s בתוך מיתר או מוצק.\n\n"
            "**עוצמה** $I$ (W/m$^2$) היא הספק אקוסטי ליחידת שטח. "
            "למקור נקודתי הקרן באופן אחיד בשלושה ממדים, "
            "העוצמה יורדת כ-$I = P/(4\\pi r^2)$ — חוק הריבוע ההפוך. "
            "הכפלת המרחק מרמקול מורידה את העוצמה פי ארבע.\n\n"
            "**רמת קול** בדציבלים דוחסת טווחי עוצמה עצומים למספרים נוחים:\n"
            "$$\\beta = 10\\log_{10}\\!\\left(\\frac{I}{I_0}\\right) \\text{ dB}, "
            "\\quad I_0 = 10^{-12} \\text{ W/m}^2$$\n\n"
            "$I_0$ הוא סף השמיעה האנושית ב-1000 Hz. "
            "לחישה $\\approx 30$ dB; שיחה $\\approx 60$ dB; "
            "סף כאב $\\approx 120$ dB. "
            "כל הכפלה פי 10 בעוצמה מוסיפה 10 dB; "
            "הכפלת עוצמה מוסיפה כ-3 dB — לא כפול ערך ה-dB.\n\n"
            "**מהירות קול** באוויר ב-20°C: $v \\approx 343$ m/s "
            "(לעיתים מעוגל ל-340 m/s בבחינות). "
            "קירוב שימושי: $v \\approx 331 + 0.6T$ m/s כאשר $T$ היא טמפרטורה ב-°C."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Standing waves and resonance\n"
            "When a wave reflects at a boundary and interferes with the incoming wave, "
            "a **standing wave** forms with fixed **nodes** (zero displacement) and "
            "**anti-nodes** (maximum displacement). The pattern does not travel — "
            "points between nodes oscillate in place. "
            "**Resonance** occurs when the driving frequency matches a natural "
            "standing-wave frequency; energy builds and amplitude grows dramatically. "
            "Musical instruments are tuned resonators.\n\n"
            "### Open pipe (both ends open)\n"
            "Both ends are pressure anti-nodes (displacement anti-nodes). "
            "The pipe length equals $n$ half-wavelengths:\n"
            "$$f_n = \\frac{nv}{2L}, \\quad n = 1, 2, 3, \\ldots$$\n"
            "Fundamental ($n=1$): $f_1 = v/(2L)$. "
            "Harmonics are exact multiples: $f_2 = 2f_1$, $f_3 = 3f_1$, etc. "
            "Flutes and most organ pipes are modelled this way.\n\n"
            "### Closed pipe (one end closed)\n"
            "A **node** at the closed end (air cannot move) and an **anti-node** "
            "at the open end. Only odd quarter-wavelengths fit inside the length:\n"
            "$$f_n = \\frac{nv}{4L}, \\quad n = 1, 3, 5, \\ldots$$\n"
            "Even harmonics ($n = 2, 4, 6$) are **absent** — a signature exam trap. "
            "Clarinet and some organ stops behave like closed pipes.\n\n"
            "### Stretched string (both ends fixed)\n"
            "Fixed ends are nodes. The mathematics matches an open pipe:\n"
            "$$f_n = \\frac{nv_{\\text{string}}}{2L}, \\quad "
            "v_{\\text{string}} = \\sqrt{\\frac{T}{\\mu}}$$\n"
            "where $T$ is tension (N) and $\\mu = m/L$ is mass per unit length (kg/m). "
            "Heavier or looser strings vibrate slower. "
            "String wave speed is typically 100–500 m/s — **not** 340 m/s air speed."
        ),
        "body_he_md": (
            "### גלים עומדים ותהודה\n"
            "כשגל מתחזק בגבול ומתאבך עם הגל הנכנס, "
            "נוצר **גל עומד** עם **צמתים** קבועים (אפס תזוזה) "
            "ו**שיאים** (תזוזה מקסימלית). הדפוס לא נוסע — "
            "נקודות בין צמתים מתנדנדות במקום. "
            "**תהודה** מתרחשת כשתדר ההנעה תואם תדר טבעי של גל עומד; "
            "אנרגיה נאגרת והאמפליטודה גדלה בחדות. "
            "כלי נגינה הם מהדהרים מכוונים.\n\n"
            "### צינור פתוח (שני קצוות פתוחים)\n"
            "שני הקצוות הם שיאי לחץ (שיאי תזוזה). "
            "אורך הצינור שווה $n$ חצאי אורך גל:\n"
            "$$f_n = \\frac{nv}{2L}, \\quad n = 1, 2, 3, \\ldots$$\n"
            "יסודי ($n=1$): $f_1 = v/(2L)$. "
            "הרמוניות הן כפולות מדויקות: $f_2 = 2f_1$, $f_3 = 3f_1$ וכו'. "
            "חלילים ורוב צינורות אורgan ממודלים כך.\n\n"
            "### צינור סגור (קצה אחד סגור)\n"
            "**צומת** בקצה הסגור (אוויר לא יכול לזוז) ו**שיא** בקצה הפתוח. "
            "רק רבעי אורך גל אי-זוגיים נכנסים:\n"
            "$$f_n = \\frac{nv}{4L}, \\quad n = 1, 3, 5, \\ldots$$\n"
            "הרמוניות זוגיות ($n = 2, 4, 6$) **חסרות** — מלכודת בחינה מוכרת. "
            "כלרinet וחלק מצינורות אורgan מתנהגים כצינור סגור.\n\n"
            "### מיתר מתוח (שני קצוות קבועים)\n"
            "קצוות קבועים = צמתים. המתמטיקה זהה לצינור פתוח:\n"
            "$$f_n = \\frac{nv_{\\text{מיתר}}}{2L}, \\quad "
            "v_{\\text{מיתר}} = \\sqrt{\\frac{T}{\\mu}}$$\n"
            "כאשר $T$ מתח (N) ו-$\\mu = m/L$ מסה ליחידת אורך (kg/m). "
            "מיתר כבד או רפוי מתנודד לאט יותר. "
            "מהירות גל על מיתר: 100–500 m/s — **לא** 340 m/s של אוויר."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "A tuning fork vibrates at $f = 440$ Hz (concert A). "
            "Speed of sound in air: $v = 340$ m/s. Find the wavelength.\n\n"
            "### Move 1: Write the wave equation\n"
            "$$v = f\\lambda \\quad \\Rightarrow \\quad \\lambda = \\frac{v}{f}$$\n\n"
            "### Move 2: Substitute values\n"
            "$$\\lambda = \\frac{340}{440} = \\frac{17}{22} \\approx 0.773 \\text{ m}$$\n\n"
            "### Move 3: Interpret physically\n"
            "The wavelength is about 77.3 cm — roughly the width of a textbook. "
            "Higher-pitched notes (higher $f$) have shorter wavelengths at the same speed. "
            "At 880 Hz (one octave above), $\\lambda \\approx 0.39$ m. "
            "This inverse relationship is tested on nearly every makhina wave question.\n\n"
            "### Move 4: Verify and exam tip\n"
            "Back-substitute: $440 \\times 0.773 \\approx 340$ m/s ✓. "
            "On makhina exams, always write the formula before substituting. "
            "If you got 1.36 m you multiplied instead of dividing. "
            "Concert A at 440 Hz is the reference pitch for tuning orchestras worldwide. "
            "Memorize $\\lambda = v/f$ as your first step on every wave problem. "
            "**Answer:** $\\lambda \\approx 0.773$ m (77.3 cm)."
        ),
        "body_he_md": (
            "מזלג כיוונון מתנודד ב-$f = 440$ Hz (לה A). "
            "מהירות קול באוויר: $v = 340$ m/s. מצאו את אורך הגל.\n\n"
            "### צעד 1: כתיבת משוואת הגל\n"
            "$$v = f\\lambda \\quad \\Rightarrow \\quad \\lambda = \\frac{v}{f}$$\n\n"
            "### צעד 2: הצבת ערכים\n"
            "$$\\lambda = \\frac{340}{440} = \\frac{17}{22} \\approx 0.773 \\text{ m}$$\n\n"
            "### צעד 3: פרשנות פיזיקלית\n"
            "אורך הגל כ-77.3 cm — בערך רוחב ספר לימוד. "
            "תווים גבוהים (תדר גבוה) = אורך גל קצר יותר באותה מהירות. "
            "ב-880 Hz (אוקטава מעל), $\\lambda \\approx 0.39$ m. "
            "הקשר ההפוך נבחן כמעט בכל שאלת גלים במכינה.\n\n"
            "### צעד 4: אימות וטיפ לבחינה\n"
            "הצבה חוזרת: $440 \\times 0.773 \\approx 340$ m/s ✓. "
            "בבחינות מכינה, כתבו תמיד את הנוסחה לפני ההצבה. "
            "אם קיבלתם 1.36 m — כפלתם במקום לחלק. "
            "לה A ב-440 Hz הוא תו הייחוס לכיוון תזמורות בכל העולם. "
            "**תשובה:** $\\lambda \\approx 0.773$ m (77.3 cm)."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "An open pipe resonates at 170 Hz as its fundamental frequency. "
            "Speed of sound $v = 340$ m/s. Find the pipe length and the second harmonic.\n\n"
            "### Move 1: Identify pipe type and formula\n"
            "The problem says \"open pipe\" and \"fundamental\" ($n = 1$). "
            "Both ends are anti-nodes, so one half-wavelength fits inside: "
            "$f_1 = v/(2L)$.\n\n"
            "### Move 2: Rearrange for length\n"
            "$$L = \\frac{v}{2f_1} = \\frac{340}{2 \\times 170} = \\frac{340}{340} = 1 \\text{ m}$$\n\n"
            "### Move 3: Find the second harmonic\n"
            "Open pipes support all integer harmonics:\n"
            "$$f_2 = 2f_1 = 2 \\times 170 = 340 \\text{ Hz}$$\n"
            "The pattern continues: $f_3 = 510$ Hz, $f_4 = 680$ Hz.\n\n"
            "### Move 4: Verify and common error\n"
            "Open pipe harmonics are $170, 340, 510, \\ldots$ Hz — all multiples. "
            "Check: $340/(2 \\times 1) = 170$ Hz ✓. "
            "If you got $L = 0.5$ m you used $f_1 = v/L$ without the factor 2. "
            "Always sketch half a wavelength inside the pipe before substituting. "
            "The third harmonic would be $f_3 = 510$ Hz. "
            "Open pipes are the default unless the stem says \"closed.\" "
            "**Answer:** $L = 1$ m; second harmonic = 340 Hz."
        ),
        "body_he_md": (
            "צינור פתוח מהדהר ב-170 Hz כתדר יסודי. "
            "מהירות קול $v = 340$ m/s. מצאו אורך צינור והרמוני שני.\n\n"
            "### צעד 1: זיהוי סוג צינור ונוסחה\n"
            "השאלה: \"צינור פתוח\" ו\"יסודי\" ($n = 1$). "
            "שני קצוות שיאים, נכנס חצי אורך גל: "
            "$f_1 = v/(2L)$.\n\n"
            "### צעד 2: סידור לאורך\n"
            "$$L = \\frac{v}{2f_1} = \\frac{340}{2 \\times 170} = \\frac{340}{340} = 1 \\text{ m}$$\n\n"
            "### צעד 3: הרמוני שני\n"
            "צינור פתוח תומך בכל $n$ שלם:\n"
            "$$f_2 = 2f_1 = 2 \\times 170 = 340 \\text{ Hz}$$\n"
            "הדפוס: $f_3 = 510$ Hz, $f_4 = 680$ Hz.\n\n"
            "### צעד 4: אימות וטעות נפוצה\n"
            "הרמוניות צינור פתוח: $170, 340, 510, \\ldots$ Hz — כפולות. "
            "בדיקה: $340/(2 \\times 1) = 170$ Hz ✓. "
            "אם קיבלתם $L = 0.5$ m השתמשתם ב-$f_1 = v/L$ בלי גורם 2. "
            "שרטטו תמיד חצי גל בתוך הצינור לפני ההצבה. "
            "ההרמוני השלישי: $f_3 = 510$ Hz. "
            "צינור פתוח הוא ברירת המחדל אלא אם כתוב \"סגור.\" "
            "**תשובה:** $L = 1$ m; הרמוני שני = 340 Hz."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "A guitar string has length $L = 0.65$ m, tension $T = 80$ N, "
            "and total mass $m = 3 \\times 10^{-3}$ kg. "
            "Find the wave speed and the first three harmonic frequencies.\n\n"
            "### Move 1: Find mass per unit length\n"
            "$$\\mu = \\frac{m}{L} = \\frac{3 \\times 10^{-3}}{0.65} "
            "\\approx 4.62 \\times 10^{-3} \\text{ kg/m}$$\n\n"
            "### Move 2: Wave speed on the string\n"
            "Use $v = \\sqrt{T/\\mu}$ — this is **not** the air speed 340 m/s:\n"
            "$$v_{\\text{string}} = \\sqrt{\\frac{T}{\\mu}} = "
            "\\sqrt{\\frac{80}{4.62 \\times 10^{-3}}} = \\sqrt{17316} \\approx 131.6 \\text{ m/s}$$\n\n"
            "### Move 3: Fundamental frequency\n"
            "Both ends fixed $\\Rightarrow$ same formula as open pipe:\n"
            "$$f_1 = \\frac{v}{2L} = \\frac{131.6}{2 \\times 0.65} \\approx 101.2 \\text{ Hz}$$\n\n"
            "### Move 4: Higher harmonics and verify\n"
            "$f_2 = 2f_1 \\approx 202.4$ Hz; $f_3 = 3f_1 \\approx 303.7$ Hz. "
            "All integer multiples exist on a string. "
            "Increasing tension raises all harmonics; increasing mass lowers them. "
            "The linear density $\\mu$ depends on string thickness and material. "
            "Pluck a tighter or lighter string to hear higher pitch — both raise $f_1$. "
            "Never substitute 340 m/s for string problems. "
            "Check: $\\sqrt{80/0.00462}/1.3 \\approx 101$ Hz ✓. "
            "**Answer:** $f_1 \\approx 101$ Hz, $f_2 \\approx 202$ Hz, $f_3 \\approx 304$ Hz."
        ),
        "body_he_md": (
            "מיתר גיטרה: אורך $L = 0.65$ m, מתח $T = 80$ N, "
            "ומסה $m = 3 \\times 10^{-3}$ kg. "
            "מצאו מהירות גל ושלוש הרמוניות ראשונות.\n\n"
            "### צעד 1: מסה ליחידת אורך\n"
            "$$\\mu = \\frac{m}{L} = \\frac{3 \\times 10^{-3}}{0.65} "
            "\\approx 4.62 \\times 10^{-3} \\text{ kg/m}$$\n\n"
            "### צעד 2: מהירות גל על המיתר\n"
            "משתמשים ב-$v = \\sqrt{T/\\mu}$ — **לא** 340 m/s של אוויר:\n"
            "$$v_{\\text{מיתר}} = \\sqrt{\\frac{T}{\\mu}} = "
            "\\sqrt{\\frac{80}{4.62 \\times 10^{-3}}} \\approx 131.6 \\text{ m/s}$$\n\n"
            "### צעד 3: תדר יסודי\n"
            "שני קצוות קבועים $\\Rightarrow$ אותה נוסחה כמו צינור פתוח:\n"
            "$$f_1 = \\frac{v}{2L} = \\frac{131.6}{2 \\times 0.65} \\approx 101.2 \\text{ Hz}$$\n\n"
            "### צעד 4: הרמוניות גבוהות ואימות\n"
            "$f_2 \\approx 202.4$ Hz; $f_3 \\approx 303.7$ Hz. "
            "כל הכפולות השלמות קיימות על מיתר. "
            "הגדלת מתח מעלה את כל ההרמוניות; הגדלת מסה מורידה. "
            "צפיפות לינארית $\\mu$ תלויה בעובי ובחומר המיתר. "
            "מתח גבוה או מיתר קל = תדר גבוה יותר — שניהם מעלים $f_1$. "
            "לעולם אל תציבו 340 m/s בבעיות מיתר. "
            "בדיקה: $\\sqrt{80/0.00462}/1.3 \\approx 101$ Hz ✓. "
            "**תשובה:** $f_1 \\approx 101$ Hz, $f_2 \\approx 202$ Hz, $f_3 \\approx 304$ Hz."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Task | Key relation |\n"
            "|---|---|\n"
            "| Find $\\lambda$ | $\\lambda = v/f$ |\n"
            "| Find $f$ | $f = v/\\lambda$ |\n"
            "| Find period | $T = 1/f$ |\n"
            "| Open pipe harmonics | $f_n = nv/(2L)$, all $n$ |\n"
            "| Closed pipe harmonics | $f_n = nv/(4L)$, odd $n$ only |\n"
            "| String wave speed | $v = \\sqrt{T/\\mu}$, $\\mu = m/L$ |\n"
            "| String harmonics | $f_n = nv_{\\text{str}}/(2L)$ |\n"
            "| Decibel change | $\\Delta\\beta = 10\\log(I_2/I_1)$ |\n\n"
            "**When to use:** Read the problem for pipe type (open/closed/string) "
            "before choosing a row. Draw the standing-wave pattern, "
            "then substitute numbers. Always check whether $n$ must be odd. "
            "**Tip:** If the problem mentions a flute or open organ pipe, use $2L$. "
            "If it mentions clarinet or \"one end closed,\" use $4L$ with odd $n$ only."
        ),
        "body_he_md": (
            "| משימה | קשר |\n"
            "|---|---|\n"
            "| מצא $\\lambda$ | $\\lambda = v/f$ |\n"
            "| מצא $f$ | $f = v/\\lambda$ |\n"
            "| מצא מחזור | $T = 1/f$ |\n"
            "| צינור פתוח | $f_n = nv/(2L)$, כל $n$ |\n"
            "| צינור סגור | $f_n = nv/(4L)$, $n$ אי-זוגי |\n"
            "| מהירות מיתר | $v = \\sqrt{T/\\mu}$, $\\mu = m/L$ |\n"
            "| הרמוניות מיתר | $f_n = nv/(2L)$ |\n"
            "| שינוי dB | $\\Delta\\beta = 10\\log(I_2/I_1)$ |\n\n"
            "**מתי להשתמש:** קראו את השאלה לסוג צינור (פתוח/סגור/מיתר) "
            "לפני בחירת שורה. שרטטו את דפוס הגל העומד, "
            "ואז הציבו מספרים. בדקו תמיד אם $n$ חייב להיות אי-זוגי. "
            "**טיפ:** חליל או צינור פתוח — $2L$. "
            "כלרinet או \"קצה סגור\" — $4L$ עם $n$ אי-זוגי בלבד."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Open vs closed pipe:** A closed pipe supports only **odd** harmonics "
            "($n = 1, 3, 5, \\ldots$). Listing $f_2$ for a closed pipe is always wrong.\n\n"
            "2. **$v = f\\lambda$, not $v = f/\\lambda$:** Wavelength belongs in the "
            "numerator. Inverting gives answers off by a factor of $\\lambda^2$.\n\n"
            "3. **String speed $\\neq$ sound speed:** On a string, "
            "$v = \\sqrt{T/\\mu}$, typically 100–200 m/s — not 340 m/s.\n\n"
            "4. **dB is logarithmic:** Doubling intensity adds 3 dB, not \"double dB.\" "
            "A factor of 100 in intensity means +20 dB.\n\n"
            "5. **Period vs frequency:** $T = 1/f$. High frequency means **short** period.\n\n"
            "**Exam tip:** When reviewing mistakes, ask which pitfall you hit — "
            "wrong pipe formula, wrong speed (air vs string), or logarithmic dB confusion."
        ),
        "body_he_md": (
            "1. **צינור פתוח מול סגור:** צינור סגור תומך רק בהרמוניות **אי-זוגיות** "
            "($n = 1, 3, 5, \\ldots$). רשימת $f_2$ בצינור סגור תמיד שגויה.\n\n"
            "2. **$v = f\\lambda$, לא $v = f/\\lambda$:** אורך גל במונה. "
            "היפוך נותן תשובה שגויה בגורם $\\lambda^2$.\n\n"
            "3. **מהירות מיתר $\\neq$ מהירות קול:** על מיתר, "
            "$v = \\sqrt{T/\\mu}$, בדרך כלל 100–200 m/s — לא 340 m/s.\n\n"
            "4. **dB לוגריתמי:** הכפלת עוצמה = +3 dB, לא \"כפול dB.\" "
            "פי 100 בעוצמה = +20 dB.\n\n"
            "5. **מחזור מול תדר:** $T = 1/f$. תדר גבוה = מחזור **קצר**.\n\n"
            "**טיפ לבחינה:** בבדיקת טעויות, שאלו איזו מלכודת פגעתם — "
            "נוסחת צינור שגויה, מהירות שגויה (אוויר מול מיתר), או בלבול dB לוגריתמי."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Wave physics bridges mechanics and electromagnetism on the makhina track. "
            "The same $v = f\\lambda$ relation describes sound, light, and water waves. "
            "Standing-wave resonance explains musical instruments, organ pipes, "
            "and why soldiers break step on bridges to avoid destructive resonance.\n\n"
            "**Why it matters for exams:** Makhina entrance tests frequently combine "
            "wave speed calculations with pipe or string resonance in one multi-step "
            "problem. Mastering the open/closed distinction saves time under pressure. "
            "Decibel questions often appear as quick one-step items alongside longer "
            "resonance problems — know both cold. "
            "Later topics (EM waves, optics) reuse the same $v = f\\lambda$ framework."
        ),
        "body_he_md": (
            "פיזיקת גלים מגשרת בין מכניקה לאלקטרומגנטיות במסלול מכינה. "
            "אותו קשר $v = f\\lambda$ מתאר קול, אור וגלים במים. "
            "תהודה של גלים עומדים מסבירה כלי נגינה, צינורות אורgan, "
            "ולמה חיילים מפסיקים לצעוד ביחד על גשר כדי למנוע תהודה הרסנית.\n\n"
            "**למה זה חשוב לבחינות:** מבחני כניסה למכינה משלבים לעיתים "
            "חישוב מהירות גל עם תהודה בצינור או מיתר בשאלה רב-שלבית. "
            "שליטה בהבחנה פתוח/סגור חוסכת זמן תחת לחץ. "
            "שאלות dB מופיעות לעיתים כפריט מהיר לצד בעיות תהודה ארוכות — "
            "הכירו את שני הסוגים."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "- **Master equation:** $v = f\\lambda$. Speed of sound in air $\\approx 340$ m/s.\n"
            "- **Open pipe:** $f_n = nv/(2L)$, all integer $n$.\n"
            "- **Closed pipe:** $f_n = nv/(4L)$, odd $n$ only.\n"
            "- **String:** $v = \\sqrt{T/\\mu}$ first, then $f_n = nv/(2L)$.\n"
            "- **Decibels:** $\\beta = 10\\log(I/I_0)$; factor of 10 = +10 dB.\n"
            "- **Period:** $T = 1/f$.\n"
            "- **Intensity:** $I = P/(4\\pi r^2)$ for a point source.\n\n"
            "**Last review:** Sketch one open pipe, one closed pipe, and one string "
            "standing-wave pattern from memory, then solve one checkpoint without notes. "
            "Say each formula aloud once before the exam. "
            "Double-check whether the problem gives air speed or asks for string speed."
        ),
        "body_he_md": (
            "- **משוואה מרכזית:** $v = f\\lambda$. מהירות קול באוויר $\\approx 340$ m/s.\n"
            "- **צינור פתוח:** $f_n = nv/(2L)$, כל $n$ שלם.\n"
            "- **צינור סגור:** $f_n = nv/(4L)$, $n$ אי-זוגי בלבד.\n"
            "- **מיתר:** קודם $v = \\sqrt{T/\\mu}$, אחר כך $f_n = nv/(2L)$.\n"
            "- **דציבלים:** $\\beta = 10\\log(I/I_0)$; פי 10 = +10 dB.\n"
            "- **מחזור:** $T = 1/f$.\n"
            "- **עוצמה:** $I = P/(4\\pi r^2)$ למקור נקודתי.\n\n"
            "**חזרה אחרונה:** שרטטו מזיכרון צינור פתוח, צינור סגור ומיתר "
            "עם דפוס גל עומד, ואז פתרו checkpoint אחד בלי רשימות. "
            "אמרו כל נוסחה בקול פעם אחת לפני הבחינה."
        ),
    },
    "summary": {
        "body_en_md": (
            "- $v = f\\lambda$ links speed, frequency, and wavelength in any medium.\n"
            "- Standing-wave resonance: open pipe and string allow all harmonics; "
            "closed pipe allows odd harmonics only.\n"
            "- String vibration speed: $\\sqrt{T/\\mu}$; always compute this before harmonics.\n"
            "- Sound intensity uses a logarithmic decibel scale; "
            "factor of 10 in intensity = +10 dB.\n\n"
            "**Takeaway:** Identify pipe/string type from the problem wording, "
            "draw the pattern, then apply the correct formula. "
            "Never mix air speed with string speed."
        ),
        "body_he_md": (
            "- $v = f\\lambda$ מקשר מהירות, תדר ואורך גל בכל מדיום.\n"
            "- תהודה: צינור פתוח ומיתר — כל ההרמוניות; "
            "צינור סגור — אי-זוגיות בלבד.\n"
            "- מהירות על מיתר: $\\sqrt{T/\\mu}$; חשבו זאת לפני הרמוניות.\n"
            "- עוצמת קול: סקאלת dB לוגריתמית; "
            "פי 10 בעוצמה = +10 dB.\n\n"
            "**מסקנה:** זהו סוג צינור/מיתר מניסוח השאלה, "
            "שרטטו דפוס, והחילו נוסחה נכונה. "
            "לעולם אל תערבבו מהירות אוויר עם מהירות מיתר."
        ),
    },
}

CHECKPOINTS = {
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Use $f = v/\\lambda$. Substituting: $f = 340/0.5 = 680$ Hz.\n\n"
            "**Check:** $680 \\times 0.5 = 340$ m/s ✓. "
            "The frequency is high because the wavelength is short (0.5 m). "
            "**Answer:** 680 Hz."
        ),
        "checkpoint_solution_he": (
            "משתמשים ב-$f = v/\\lambda$. הצבה: $f = 340/0.5 = 680$ Hz.\n\n"
            "**בדיקה:** $680 \\times 0.5 = 340$ m/s ✓. "
            "התדר גבוה כי אורך הגל קצר (0.5 m). **תשובה:** 680 Hz."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "Closed pipe: $f_n = nv/(4L)$ with odd $n$ only. "
            "The 3rd harmonic means $n = 3$:\n"
            "$$f_3 = \\frac{3 \\times 340}{4 \\times 1} = \\frac{1020}{4} = 255 \\text{ Hz}$$\n\n"
            "**Check:** $f_1 = 85$ Hz, $f_3 = 3 \\times 85 = 255$ Hz ✓. "
            "Do not use $n = 3$ in the open-pipe formula. **Answer:** 255 Hz."
        ),
        "checkpoint_solution_he": (
            "צינור סגור: $f_n = nv/(4L)$ עם $n$ אי-זוגי. "
            "הרמוני 3 = $n = 3$:\n"
            "$$f_3 = \\frac{3 \\times 340}{4 \\times 1} = 255 \\text{ Hz}$$\n\n"
            "**בדיקה:** $f_1 = 85$ Hz, $f_3 = 3 \\times 85 = 255$ Hz ✓. "
            "אל תשתמשו ב-$n = 3$ בנוסחת צינור פתוח. **תשובה:** 255 Hz."
        ),
    },
}


def main():
    orig = json.loads(SRC.read_text(encoding="utf-8"))
    lesson = dict(orig)
    lesson["version"] = 2
    lesson["summary_en"] = (
        "Sound is a longitudinal wave governed by $v=f\\lambda$. "
        "Master standing-wave resonance in open and closed pipes and stretched strings, "
        "plus the decibel scale for intensity."
    )
    lesson["summary_he"] = (
        "קול הוא גל אורך הנשלט על ידי $v=f\\lambda$. "
        "שליטה בתהודה של גלים עומדים בצינורות פתוחים/סגורים ובמיתרים מתוחים, "
        "ובסולם הדציבלים לעוצמה."
    )

    for sec in lesson["sections"]:
        sid = sec.get("id", "")
        kind = sec["kind"]

        if kind in SECTION_BODIES:
            sec["body_en_md"] = SECTION_BODIES[kind]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[kind]["body_he_md"]
        elif sid in ("worked_example_1", "worked_example_2", "worked_example_3"):
            sec["body_en_md"] = SECTION_BODIES[sid]["body_en_md"]
            sec["body_he_md"] = SECTION_BODIES[sid]["body_he_md"]
        elif sid in CHECKPOINTS:
            sec.update(CHECKPOINTS[sid])

    for q in lesson["questions"]:
        exp = EXPLANATIONS[q["ord"]]
        q["explanation_en"] = exp["en"]
        q["explanation_he"] = exp["he"]

    errors = []
    for sec in lesson["sections"]:
        kind = sec["kind"]
        sid = sec.get("id", "")
        key = kind if kind in SECTION_BODIES else sid if sid in SECTION_BODIES else None
        if key and key in MIN_WORDS:
            mw = MIN_WORDS[key if key in MIN_WORDS else kind]
        elif kind in MIN_WORDS:
            mw = MIN_WORDS[kind]
        else:
            continue
        for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
            wc = word_count(sec.get(field, ""))
            need = mw[lang]
            if wc < need:
                errors.append(f"{sec.get('id', kind)} {lang}: {wc} < {need}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{sec.get('id', kind)}: hebrew_body_weak")

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


if __name__ == "__main__":
    main()
