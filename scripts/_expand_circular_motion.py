#!/usr/bin/env python3
"""Expand circular_motion.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/circular_motion.json"
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
            "**Why friction is correct:** On a flat (unbanked) road, the centripetal direction is "
            "horizontal — toward the center of the circular path. Gravity acts vertically and the "
            "normal force is vertical; neither has a horizontal component toward the center. Static "
            "friction between tires and pavement is the only real force that can point horizontally "
            "inward, so $f = mv^2/r$ at the limit of safe turning.\n\n"
            "**How to think about it:** Draw a free-body diagram from above. Ask: \"Which existing "
            "force can point toward the center?\" Centripetal force is a label for the net inward "
            "component, not a new force type.\n\n"
            "**Common wrong path:** Choosing \"centrifugal force\" — fictitious in an inertial frame. "
            "Picking gravity or normal force ignores that both are vertical on level ground.\n\n"
            "**Exam tip:** For flat turns, write $f \\leq \\mu_s mg$ and set $f = mv^2/r$ at maximum "
            "speed. For banked roads, friction may be unnecessary at the design speed."
        ),
        "he": (
            "**למה חיכוך נכון:** בכביש שטוח (לא מוטה), הכיוון הריכוזי אופקי — לכיוון מרכז המסלול. "
            "כבידה פועלת אנכית והכוח הנורמלי אנכי; לאף אחד אין רכיב אופקי לכיוון המרכז. חיכוך סטטי "
            "בין צמיגים לכביש הוא הכוח האמיתי היחיד שיכול להצביע אופקית פנימה, ולכן $f = mv^2/r$ "
            "בגבול הפנייה הבטוחה.\n\n"
            "**איך לחשוב על זה:** שרטטו דיאגרמת כוחות מלמעלה. שאלו: \"איזה כוח קיים יכול לכיוון "
            "המרכז?\" כוח ריכוזי הוא תווית לרכיב הנטו פנימה, לא סוג כוח חדש.\n\n"
            "**טעות נפוצה:** בחירה ב\"כוח צנטריפוגלי\" — פיקטיבי במסגרת אינרציאלית. בחירה בכבידה "
            "או בנורמלי מתעלמת מכך ששניהם אנכיים על כביש ישר.\n\n"
            "**טיפ לבחינה:** בפניות שטוחות, כתבו $f \\leq \\mu_s mg$ והציבו $f = mv^2/r$ במהירות "
            "מקסימלית. בכביש מוטה, לעיתים אין צורך בחיכוך במהירות התכנון."
        ),
    },
    2: {
        "en": (
            "**Why 9 m/s² is correct:** Centripetal acceleration magnitude is $a_c = v^2/r$. "
            "Substituting $v = 6\\;\\text{m/s}$ and $r = 4\\;\\text{m}$:\n"
            "$$a_c = \\frac{36}{4} = 9\\;\\text{m/s}^2$$\n"
            "Direction is always toward the center of the circle, even when speed is constant.\n\n"
            "**How to think about it:** $a_c$ grows with the square of speed — doubling $v$ "
            "quadruples $a_c$. It shrinks with radius — wider turns need less inward acceleration "
            "at the same speed.\n\n"
            "**Common wrong path:** Using $a = v/t$ or $a = 2\\pi r/T^2$ without linking to $v^2/r$. "
            "Forgetting that constant speed still means nonzero acceleration because direction changes.\n\n"
            "**Exam tip:** Always state units (m/s²). Quick check: $6^2/4 = 9$ — no calculator needed "
            "when numbers are chosen cleanly on Bagrut papers."
        ),
        "he": (
            "**למה 9 m/s² נכון:** גודל התאוצה הריכוזית: $a_c = v^2/r$. עם $v = 6\\;\\text{m/s}$ "
            "ו-$r = 4\\;\\text{m}$:\n"
            "$$a_c = \\frac{36}{4} = 9\\;\\text{m/s}^2$$\n"
            "הכיוון תמיד לכיוון מרכז המעגל, גם כשהמהירות קבועה.\n\n"
            "**איך לחשוב על זה:** $a_c$ גדל בריבוע המהירות — הכפלת $v$ מרביעה את $a_c$. הוא קטן "
            "עם רדיוס גדול — פניות רחבות דורשות פחות תאוצה פנימית באותה מהירות.\n\n"
            "**טעות נפוצה:** שימוש ב-$a = v/t$ בלי קשר ל-$v^2/r$. שכחה שמהירות קבועה עדיין "
            "משמעותה תאוצה שונה מאפס כי הכיוון משתנה.\n\n"
            "**טיפ לבחינה:** ציינו יחידות (m/s²). בדיקה מהירה: $6^2/4 = 9$ — לעיתים בלי מחשבון "
            "בשאלות בגרות עם מספרים \"נקיים\"."
        ),
    },
    3: {
        "en": (
            "**Why 36 N is correct:** Centripetal force is the net force toward the center: "
            "$F_c = mv^2/r$. With $m = 2\\;\\text{kg}$, $v = 3\\;\\text{m/s}$, $r = 0.5\\;\\text{m}$:\n"
            "$$F_c = \\frac{2 \\times 9}{0.5} = \\frac{18}{0.5} = 36\\;\\text{N}$$\n\n"
            "**How to think about it:** Identify what real force provides $F_c$ (tension, friction, "
            "gravity component, normal component). Here the question asks only for magnitude — "
            "apply Newton's second law in the radial direction.\n\n"
            "**Common wrong path:** Using $F = ma$ with tangential acceleration, or computing "
            "$mv^2$ without dividing by $r$. Another slip: using diameter instead of radius.\n\n"
            "**Exam tip:** Write $F_c = mv^2/r$ first, substitute, then identify the provider "
            "in word problems (\"tension equals…\", \"friction equals…\"). Units must be newtons."
        ),
        "he": (
            "**למה 36 N נכון:** הכוח הריכוזי הוא הכוח הנטו לכיוון המרכז: $F_c = mv^2/r$. "
            "עם $m = 2\\;\\text{kg}$, $v = 3\\;\\text{m/s}$, $r = 0.5\\;\\text{m}$:\n"
            "$$F_c = \\frac{2 \\times 9}{0.5} = 36\\;\\text{N}$$\n\n"
            "**איך לחשוב על זה:** זהו איזה כוח אמיתי מספק את $F_c$ (מתח, חיכוך, רכיב כבידה, "
            "רכיב נורמלי). כאן נשאל רק הגודל — יישמו את חוק ניוטון השני בכיוון הרדיוס.\n\n"
            "**טעות נפוצה:** $F = ma$ עם תאוצה משיקית, או $mv^2$ בלי חלוקה ב-$r$. גם שימוש "
            "בקוטר במקום רדיוס.\n\n"
            "**טיפ לבחינה:** כתבו $F_c = mv^2/r$, הציבו, ואז זהו את \"ספק\" הכוח בשאלות מילוליות. "
            "יחידות — ניוטון."
        ),
    },
    4: {
        "en": (
            "**Why these values are correct:** For uniform circular motion, $v = 2\\pi r/T$ and "
            "$\\omega = 2\\pi/T$. With $r = 2\\;\\text{m}$, $T = 4\\;\\text{s}$:\n"
            "$$v = \\frac{2\\pi(2)}{4} = \\pi \\approx 3.14\\;\\text{m/s}, \\quad "
            "\\omega = \\frac{2\\pi}{4} = \\frac{\\pi}{2} \\approx 1.57\\;\\text{rad/s}$$\n"
            "Then $a_c = v^2/r = \\pi^2/2 \\approx 4.93\\;\\text{m/s}^2$, or equivalently "
            "$a_c = \\omega^2 r$.\n\n"
            "**How to think about it:** Period links all three quantities. Compute $v$ or $\\omega$ "
            "first, then $a_c$ — both paths must agree.\n\n"
            "**Common wrong path:** Using $v = r/T$ without $2\\pi$, or confusing frequency $f = 1/T$ "
            "with angular frequency $\\omega = 2\\pi f$.\n\n"
            "**Exam tip:** Show $T$ conversion to seconds if given in minutes. Verify "
            "$a_c = \\omega^2 r = (\\pi/2)^2 \\times 2 = \\pi^2/2$ as a cross-check."
        ),
        "he": (
            "**למה הערכים נכונים:** בתנועה מעגלית אחידה, $v = 2\\pi r/T$ ו-$\\omega = 2\\pi/T$. "
            "עם $r = 2\\;\\text{m}$, $T = 4\\;\\text{s}$:\n"
            "$$v = \\pi \\approx 3.14\\;\\text{m/s}, \\quad \\omega = \\frac{\\pi}{2} \\approx 1.57\\;\\text{rad/s}$$\n"
            "אז $a_c = v^2/r = \\pi^2/2 \\approx 4.93\\;\\text{m/s}^2$, או $a_c = \\omega^2 r$.\n\n"
            "**איך לחשוב על זה:** המחזור מקשר את כל הכמויות. חשבו $v$ או $\\omega$ קודם, "
            "ואז $a_c$ — שני המסלולים חייבים להתאים.\n\n"
            "**טעות נפוצה:** $v = r/T$ בלי $2\\pi$, או בלבול בין תדר $f = 1/T$ לבין "
            "$\\omega = 2\\pi f$.\n\n"
            "**טיפ לבחינה:** המירו $T$ לשניות אם ניתן בדקות. אמתו $a_c = \\omega^2 r$ "
            "כבדיקה צולבת.\n\n"
            "**בדיקת יחידות:** $v$ ב-m/s, $\\omega$ ב-rad/s, $a_c$ ב-m/s². "
            "אם $a_c$ יצא ב-rad/s² — בדקו שלא השתמשתם ב-$T$ במקום $\\omega$."
        ),
    },
    5: {
        "en": (
            "**Why 4 m/s² is correct:** Centripetal acceleration depends only on speed and radius "
            "for a given point on the path: $a_c = v^2/r$. With $v = 20\\;\\text{m/s}$, "
            "$r = 100\\;\\text{m}$:\n"
            "$$a_c = \\frac{400}{100} = 4\\;\\text{m/s}^2$$\n"
            "This is about 0.4 g — a moderate turn for a highway curve.\n\n"
            "**How to think about it:** Mass does not appear in $a_c$ — only in $F_c = ma_c$. "
            "If the question asked for force, you would multiply by mass; here acceleration alone "
            "is requested.\n\n"
            "**Common wrong path:** Dividing $v$ by $r$ instead of squaring $v$, or using "
            "$a = v/t$ with an invented time. Confusing centripetal with tangential acceleration "
            "when speed is constant.\n\n"
            "**Exam tip:** Compare $a_c$ to $g$: values near $10\\;\\text{m/s}^2$ mean "
            "roughly \"1 g\" inward — useful for roller-coaster and pilot problems."
        ),
        "he": (
            "**למה 4 m/s² נכון:** תאוצה ריכוזית תלויה רק במהירות וברדיוס: $a_c = v^2/r$. "
            "עם $v = 20\\;\\text{m/s}$, $r = 100\\;\\text{m}$:\n"
            "$$a_c = \\frac{400}{100} = 4\\;\\text{m/s}^2$$\n"
            "זה כ-0.4 g — פנייה בינונית בעקומה בכביש מהיר.\n\n"
            "**איך לחשוב על זה:** מסה לא מופיעה ב-$a_c$ — רק ב-$F_c = ma_c$. אם היו שואלים "
            "כוח, היו מכפילים במסה; כאן נדרשת רק תאוצה.\n\n"
            "**טעות נפוצה:** חלוקת $v$ ב-$r$ במקום ריבוע, או $a = v/t$ עם זמן מומצא. "
            "בלבול בין ריכוזית למשיקית כשהמהירות קבועה.\n\n"
            "**טיפ לבחינה:** השוו $a_c$ ל-$g$: ערכים קרובים ל-$10\\;\\text{m/s}^2$ "
            "משמעותם כ-\"1 g\" פנימה — שימושי במתקני שעשועים ותעופה."
        ),
    },
    6: {
        "en": (
            "**Why ~1012 m/s is correct:** Orbital speed in one revolution: $v = 2\\pi r/T$. "
            "Convert the lunar period to seconds first:\n"
            "$$T = 27.3 \\times 24 \\times 3600 \\approx 2.36\\times10^6\\;\\text{s}$$\n"
            "$$v = \\frac{2\\pi(3.8\\times10^8)}{2.36\\times10^6} \\approx 1012\\;\\text{m/s}$$\n"
            "About 1 km/s — far slower than low-Earth orbit (~8 km/s) because the Moon's orbit "
            "is much larger.\n\n"
            "**How to think about it:** This is kinematics on a circle, not yet $v = \\sqrt{gR}$. "
            "Either $v = 2\\pi r/T$ or $v = r\\omega$ works when period is given.\n\n"
            "**Common wrong path:** Forgetting to convert days to seconds (off by ~10⁵), or using "
            "Earth radius instead of orbital radius $3.8\\times10^8$ m.\n\n"
            "**Exam tip:** After computing, sanity-check: Moon completes one orbit in ~27 days at "
            "~380,000 km → speed must be ~1 km/s, not 8 km/s."
        ),
        "he": (
            "**למה ~1012 m/s נכון:** מהירות מסלולית בהקפה אחת: $v = 2\\pi r/T$. "
            "המירו תחילה את מחזור הירח לשניות:\n"
            "$$T = 27.3 \\times 24 \\times 3600 \\approx 2.36\\times10^6\\;\\text{s}$$\n"
            "$$v = \\frac{2\\pi(3.8\\times10^8)}{2.36\\times10^6} \\approx 1012\\;\\text{m/s}$$\n"
            "כ-1 ק\"מ/ש — איטי בהרבה ממסלול LEO (~8 ק\"מ/ש) כי מסלול הירח גדול הרבה יותר.\n\n"
            "**איך לחשוב על זה:** זו קינמטיקה על מעגל, עדיין לא $v = \\sqrt{gR}$. "
            "$v = 2\\pi r/T$ או $v = r\\omega$ כשיש מחזור.\n\n"
            "**טעות נפוצה:** שכחת המרת ימים לשניות (טעות ב-$10^5$), או שימוש ברדיוס כדה\"א "
            "במקום $3.8\\times10^8$ m.\n\n"
            "**טיפ לבחינה:** בדיקת הגיון: הירח מקיף ב-~27 יום ב-~380,000 ק\"מ → "
            "מהירות ~1 ק\"מ/ש, לא 8."
        ),
    },
    7: {
        "en": (
            "**Why ~17.3 m/s is correct:** On a flat turn, maximum static friction provides "
            "centripetal force: $f_{\\max} = \\mu_s mg = mv^2/r$. Solving for $v$:\n"
            "$$v = \\sqrt{\\mu_s rg} = \\sqrt{0.5 \\times 60 \\times 10} = \\sqrt{300} \\approx 17.3\\;\\text{m/s}$$\n"
            "Above this speed, tires slip outward (in the absence of banking).\n\n"
            "**How to think about it:** Set the maximum available inward force equal to required "
            "$mv^2/r$. Mass cancels — heavier cars have the same safe speed if $\\mu_s$ is the same.\n\n"
            "**Common wrong path:** Using $\\mu_k$ while the car is not yet sliding, or forgetting "
            "$g$ under the square root. Using $v = \\mu_s rg$ without the square root.\n\n"
            "**Exam tip:** Convert to km/h for context: $17.3\\;\\text{m/s} \\approx 62\\;\\text{km/h}$. "
            "Wet roads lower $\\mu_s$ — safe speed drops as $\\sqrt{\\mu_s}$."
        ),
        "he": (
            "**למה ~17.3 m/s נכון:** בפנייה שטוחה, חיכוך סטטי מרבי מספק כוח ריכוזי: "
            "$f_{\\max} = \\mu_s mg = mv^2/r$. פתרון עבור $v$:\n"
            "$$v = \\sqrt{\\mu_s rg} = \\sqrt{0.5 \\times 60 \\times 10} = \\sqrt{300} \\approx 17.3\\;\\text{m/s}$$\n"
            "מעל מהירות זו הצמיגים מחליקים החוצה (ללא נטייה).\n\n"
            "**איך לחשוב על זה:** השוו כוח פנימי זמין מרבי ל-$mv^2/r$ הנדרש. "
            "מסה מתבטלת — מכונית כבדה באותה מהירות בטוחה אם $\\mu_s$ זהה.\n\n"
            "**טעות נפוצה:** $\\mu_k$ כשעדיין לא מחליקים, או שכחת $g$ תחת השורש. "
            "$v = \\mu_s rg$ בלי שורש.\n\n"
            "**טיפ לבחינה:** המרה לקמ\"ש: $17.3\\;\\text{m/s} \\approx 62\\;\\text{km/h}$. "
            "כביש רטוב מקטין $\\mu_s$ — מהירות בטוחה יורדת כ-$\\sqrt{\\mu_s}$."
        ),
    },
    8: {
        "en": (
            "**Why these answers are correct:** (a) At the top of a vertical loop, minimum speed "
            "occurs when tension vanishes: $mg = mv^2/r$, so $v_{\\min} = \\sqrt{gr} = \\sqrt{100} = "
            "10\\;\\text{m/s}$. (b) At the bottom with $v = 20\\;\\text{m/s}$, centripetal direction "
            "is upward: $N - mg = mv^2/r$:\n"
            "$$N = m\\left(g + \\frac{v^2}{r}\\right) = 500\\left(10 + \\frac{400}{10}\\right) = "
            "500 \\times 50 = 25000\\;\\text{N}$$\n\n"
            "**How to think about it:** Top and bottom use opposite sign conventions for "
            "$N$ and $mg$ relative to the center. Always draw the center direction first.\n\n"
            "**Common wrong path:** Using $N + mg = mv^2/r$ at the bottom (both cannot point "
            "toward center), or $mg - N$ at the top with wrong sign. Confusing minimum speed "
            "with speed at the bottom.\n\n"
            "**Exam tip:** At bottom, normal force exceeds weight — riders feel \"heavy.\" "
            "Factor $N/mg = 1 + v^2/(rg)$ gives g-force directly."
        ),
        "he": (
            "**למה התשובות נכונות:** (א) בראש לולאה אנכית, מהירות מינימלית כשמתח מתאפס: "
            "$mg = mv^2/r$, ולכן $v_{\\min} = \\sqrt{gr} = 10\\;\\text{m/s}$. (ב) בתחתית "
            "עם $v = 20\\;\\text{m/s}$, כיוון ריכוזי למעלה: $N - mg = mv^2/r$:\n"
            "$$N = 500\\left(10 + \\frac{400}{10}\\right) = 25000\\;\\text{N}$$\n\n"
            "**איך לחשוב על זה:** ראש ותחתית — מוסכמות סימן שונות ל-$N$ ו-$mg$ ביחס למרכז. "
            "שרטטו קודם כיוון מרכז.\n\n"
            "**טעות נפוצה:** $N + mg = mv^2/r$ בתחתית (שניהם לא יכולים למרכז), או $mg - N$ "
            "בראש עם סימן שגוי. בלבול מהירות מינימלית עם מהירות בתחתית.\n\n"
            "**טיפ לבחינה:** בתחתית, נורמלי גדול ממשקל — \"כבדים\" יותר. "
            "$N/mg = 1 + v^2/(rg)$ נותן g-force ישירות."
        ),
    },
}


def build_lesson():
    with open(SRC, encoding="utf-8") as f:
        lesson = json.load(f)

    section_bodies = {
        "intro": {
            "en": (
                "A car rounding a corner, a satellite orbiting Earth, a ball swung on a string — "
                "all follow curved paths. When the path is a circle at constant speed, we call it "
                "**uniform circular motion (UCM)**. The speed $|v|$ stays fixed, but velocity "
                "$\\vec{v}$ changes direction every instant. That changing direction means "
                "**nonzero acceleration** directed toward the center — centripetal acceleration.\n\n"
                "Newton's second law then requires a **net force toward the center**, supplied by "
                "real forces: tension, friction, gravity, normal force components, or combinations.\n\n"
                "**Why this matters:**\n"
                "- **Road design:** Banking angles and speed limits are set using $mv^2/r$.\n"
                "- **Space:** Orbital speed $v = \\sqrt{gR}$ links circular motion to gravitation.\n"
                "- **Amusement parks:** Loop-the-loop problems combine energy and centripetal force.\n\n"
                "In Israeli Bagrut physics, circular motion questions appear in mechanics sections "
                "and often combine with energy (vertical circles) or friction (flat turns).\n\n"
                "**Bagrut exam topics:**\n"
                "- Centripetal acceleration $a_c = v^2/r$ and force $F_c = mv^2/r$\n"
                "- Period, frequency, angular velocity $\\omega = 2\\pi/T$\n"
                "- Banked roads, hills and valleys, satellites, vertical loops"
            ),
            "he": (
                "מכונית בפנייה, לוויין מקיף את כדור הארץ, כדור על חוט — כולם נעים במסלולים "
                "עקומים. כשהמסלול הוא מעגל במהירות קבועה, מדובר ב**תנועה מעגלית אחידה (UCM)**. "
                "הגודל $|v|$ נשאר קבוע, אך הוקטור $\\vec{v}$ משנה כיוון בכל רגע. שינוי הכיוון "
                "משמעותו **תאוצה שונה מאפס** לכיוון המרכז — תאוצה ריכוזית.\n\n"
                "חוק ניוטון השני דורש אז **כוח נטו לכיוון המרכז**, שמסופק על-ידי כוחות אמיתיים: "
                "מתח, חיכוך, כבידה, רכיבי כוח נורמלי, או שילובים.\n\n"
                "**למה זה חשוב:**\n"
                "- **תכנון כבישים:** זוויות נטייה ומגבלות מהירות מבוססות על $mv^2/r$.\n"
                "- **חלל:** מהירות מסלול $v = \\sqrt{gR}$ מקשרת תנועה מעגלית לכבידה.\n"
                "- **מתקני שעשועים:** לולאות אנכיות משלבות אנרגיה וכוח ריכוזי.\n\n"
                "בבגרות פיזיקה, שאלות תנועה מעגלית מופיעות במכניקה ולעיתים משלבות אנרגיה "
                "(מעגלים אנכיים) או חיכוך (פניות שטוחות).\n\n"
                "**נושאי בגרות:**\n"
                "- תאוצה ריכוזית $a_c = v^2/r$ וכוח $F_c = mv^2/r$\n"
                "- מחזור, תדר, מהירות זוויתית $\\omega = 2\\pi/T$\n"
                "- כבישים מוטים, גבעות ועמקים, לוויינים, לולאות אנכיות"
            ),
        },
        "definition": {
            "en": (
                "Circular motion uses both **angular** and **linear** quantities. They convert via "
                "radius $r$.\n\n"
                "**Angular velocity** (rad/s):\n"
                "$$\\omega = 2\\pi f = \\frac{2\\pi}{T}$$\n\n"
                "**Linear speed** from angular:\n"
                "$$v = r\\omega$$\n\n"
                "**Centripetal acceleration** — magnitude, always **toward the center**:\n"
                "$$a_c = \\frac{v^2}{r} = \\omega^2 r$$\n\n"
                "**Centripetal force** — net inward force (not a new force type):\n"
                "$$F_c = \\frac{mv^2}{r} = m\\omega^2 r$$\n\n"
                "**Period and frequency:**\n"
                "$$T = \\frac{1}{f} = \\frac{2\\pi r}{v} = \\frac{2\\pi}{\\omega}$$\n\n"
                "| Quantity | Symbol | SI unit | Notes |\n"
                "|---|---|---|---|\n"
                "| Period | $T$ | s | Time for one revolution |\n"
                "| Frequency | $f$ | Hz | Revolutions per second |\n"
                "| Angular velocity | $\\omega$ | rad/s | $2\\pi$ rad = one full turn |\n"
                "| Linear speed | $v$ | m/s | Tangential speed |\n\n"
                "**Critical idea:** \"Centripetal force\" labels whichever real forces (or components) "
                "sum to $mv^2/r$ inward. On a string, it is tension; on a flat turn, friction; "
                "for a satellite, gravity."
            ),
            "he": (
                "תנועה מעגלית משתמשת בכמויות **זוויתיות** ו**לינאריות**, המתורגמות דרך רדיוס $r$.\n\n"
                "**מהירות זוויתית** (rad/s):\n"
                "$$\\omega = 2\\pi f = \\frac{2\\pi}{T}$$\n\n"
                "**מהירות לינארית** מהזוויתית:\n"
                "$$v = r\\omega$$\n\n"
                "**תאוצה ריכוזית** — גודל, תמיד **לכיוון המרכז**:\n"
                "$$a_c = \\frac{v^2}{r} = \\omega^2 r$$\n\n"
                "**כוח ריכוזי** — כוח נטו פנימה (לא סוג כוח חדש):\n"
                "$$F_c = \\frac{mv^2}{r} = m\\omega^2 r$$\n\n"
                "**מחזור ותדר:**\n"
                "$$T = \\frac{1}{f} = \\frac{2\\pi r}{v} = \\frac{2\\pi}{\\omega}$$\n\n"
                "| כמות | סימון | יחידה SI | הערות |\n"
                "|---|---|---|---|\n"
                "| מחזור | $T$ | s | זמן להקפה אחת |\n"
                "| תדר | $f$ | Hz | הקפות לשנייה |\n"
                "| מהירות זוויתית | $\\omega$ | rad/s | $2\\pi$ rad = סיבוב מלא |\n"
                "| מהירות לינארית | $v$ | m/s | מהירות משיקית |\n\n"
                "**רעיון מרכזי:** \"כוח ריכוזי\" מתייג אילו כוחות אמיתיים (או רכיבים) "
                "מסתכמים ל-$mv^2/r$ פנימה. על חוט — מתח; בפנייה שטוחה — חיכוך; "
                "ללוויין — כבידה."
            ),
        },
        "theory": {
            "en": (
                "### Why is there acceleration at constant speed?\n"
                "Velocity is a vector. In UCM, $|v|$ is constant but direction rotates. "
                "Since $\\vec{a} = d\\vec{v}/dt$, any direction change implies $\\vec{a} \\neq 0$. "
                "The acceleration vector points **radially inward** — centripetal means "
                "\"center-seeking.\"\n\n"
                "### Geometric derivation of $a_c = v^2/r$\n"
                "In time $\\Delta t$, the object moves arc length $v\\Delta t$ and turns through "
                "angle $\\Delta\\theta = v\\Delta t/r$. The change in velocity magnitude "
                "$|\\Delta\\vec{v}| \\approx v\\Delta\\theta = v^2\\Delta t/r$. Hence:\n"
                "$$a = \\frac{|\\Delta\\vec{v}|}{\\Delta t} = \\frac{v^2}{r}$$\n"
                "Equivalently, $a_c = \\omega^2 r$ using $v = r\\omega$.\n\n"
                "### Free-body patterns (identify the provider)\n"
                "- **Horizontal string:** $T = mv^2/r$ (tension inward)\n"
                "- **Flat curve:** $f = mv^2/r$ (friction inward)\n"
                "- **Top of hill:** $mg - N = mv^2/r$ (center below car)\n"
                "- **Bottom of valley:** $N - mg = mv^2/r$ (center above car)\n"
                "- **Banked road (design speed):** $N\\sin\\theta = mv^2/r$, $N\\cos\\theta = mg$\n\n"
                "### Special results\n"
                "- **Banking (no friction):** $\\tan\\theta = v^2/(rg)$\n"
                "- **Satellite (low orbit):** $mg = mv^2/r \\Rightarrow v = \\sqrt{gR}$\n"
                "- **Vertical loop, top (minimum speed):** $T = 0 \\Rightarrow v_{\\min} = \\sqrt{gr}$\n\n"
                "**Energy link:** In vertical circles, speed varies. Use conservation of energy "
                "between top and bottom, then apply $F_c = mv^2/r$ at each point separately.\n\n"
                "**Units reminder:** $\\omega$ in rad/s, $v$ in m/s, $a_c$ in m/s², $F_c$ in N."
            ),
            "he": (
                "### מדוע יש תאוצה במהירות קבועה?\n"
                "מהירות היא וקטור. ב-UCM, $|v|$ קבוע אך הכיוון מסתובב. "
                "מכיוון ש-$\\vec{a} = d\\vec{v}/dt$, כל שינוי כיוון משמעותו $\\vec{a} \\neq 0$. "
                "וקטור התאוצה מצביע **רадиально פנימה** — centripetal = \"מחפש מרכז\".\n\n"
                "### גזירה גיאומטרית של $a_c = v^2/r$\n"
                "בזמן $\\Delta t$, הגוף עובר מרחק $v\\Delta t$ ופונה בזווית "
                "$\\Delta\\theta = v\\Delta t/r$. שינוי המהירות $|\\Delta\\vec{v}| \\approx v\\Delta\\theta = "
                "v^2\\Delta t/r$. לכן:\n"
                "$$a = \\frac{|\\Delta\\vec{v}|}{\\Delta t} = \\frac{v^2}{r}$$\n"
                "שקול: $a_c = \\omega^2 r$ עם $v = r\\omega$.\n\n"
                "### דפוסי FBD (זיהוי \"ספק\" הכוח)\n"
                "- **חוט אופקי:** $T = mv^2/r$ (מתח פנימה)\n"
                "- **עקומה שטוחה:** $f = mv^2/r$ (חיכוך פנימה)\n"
                "- **ראש גבעה:** $mg - N = mv^2/r$ (מרכז מתחת למכונית)\n"
                "- **תחתית עמק:** $N - mg = mv^2/r$ (מרכז מעל)\n"
                "- **כביש מוטה (מהירות תכנון):** $N\\sin\\theta = mv^2/r$, $N\\cos\\theta = mg$\n\n"
                "### תוצאות מיוחדות\n"
                "- **נטייה (ללא חיכוך):** $\\tan\\theta = v^2/(rg)$\n"
                "- **לוויין (מסלול נמוך):** $mg = mv^2/r \\Rightarrow v = \\sqrt{gR}$\n"
                "- **לולאה אנכית, ראש (מהירות מינ'):** $T = 0 \\Rightarrow v_{\\min} = \\sqrt{gr}$\n\n"
                "**קשר לאנרגיה:** במעגלים אנכיים המהירות משתנה. שימור אנרגיה בין ראש לתחתית, "
                "ואז $F_c = mv^2/r$ בכל נקודה בנפרד."
            ),
        },
    }

    for sec in lesson["sections"]:
        kind = sec.get("kind")
        sid = sec.get("id", "")

        if kind == "intro":
            sec["body_en_md"] = section_bodies["intro"]["en"]
            sec["body_he_md"] = section_bodies["intro"]["he"]
        elif kind == "definition":
            sec["body_en_md"] = section_bodies["definition"]["en"]
            sec["body_he_md"] = section_bodies["definition"]["he"]
        elif kind == "theory":
            sec["body_en_md"] = section_bodies["theory"]["en"]
            sec["body_he_md"] = section_bodies["theory"]["he"]
        elif kind == "worked_example" and sid == "worked_example_1":
            sec["body_en_md"] = (
                "**Given:** A $0.5\\;\\text{kg}$ ball is swung in a horizontal circle of radius "
                "$r = 1.2\\;\\text{m}$ at constant speed $v = 4\\;\\text{m/s}$ on a light string. "
                "Find the tension in the string. ($g = 10\\;\\text{m/s}^2$)\n\n"
                "In a horizontal circle (idealized), gravity acts vertically and tension has "
                "vertical and horizontal components. At moderate speeds the horizontal component "
                "provides nearly all centripetal force.\n\n"
                "### Move 1 — Identify centripetal requirement\n"
                "Centripetal direction = horizontal, toward center of circle:\n"
                "$$F_c = \\frac{mv^2}{r} = \\frac{0.5 \\times 16}{1.2} = \\frac{8}{1.2}$$\n\n"
                "### Move 2 — Relate tension to centripetal force\n"
                "If the string is nearly horizontal, $T \\approx mv^2/r$:\n"
                "$$T \\approx 6.67\\;\\text{N}$$\n\n"
                "### Move 3 — Check with exact geometry (optional)\n"
                "With slight string angle $\\theta$ from horizontal: $T\\cos\\theta = mg$ and "
                "$T\\sin\\theta = mv^2/r$. For small angles, $T$ is only slightly above 6.67 N.\n\n"
                "**Answer:** $T \\approx 6.67\\;\\text{N}$.\n\n"
                "**Exam tip:** When the problem says \"horizontal circle\" at Bagrut level, "
                "using $T = mv^2/r$ directly is usually the intended path."
            )
            sec["body_he_md"] = (
                "**נתון:** כדור $0.5\\;\\text{kg}$ מסתובב במעגל אופקי ברדיוס $r = 1.2\\;\\text{m}$ "
                "במהירות קבועה $v = 4\\;\\text{m/s}$ על חוט קל. מצאו מתח בחוט. ($g = 10\\;\\text{m/s}^2$)\n\n"
                "במעגל אופקי (אידיאלי), כבידה אנכית ולמתח יש רכיבים אנכיים ואופקיים. "
                "במהירויות בינוניות הרכיב האופקי מספק כמעט את כל הכוח הריכוזי.\n\n"
                "### צעד 1 — דרישת כוח ריכוזי\n"
                "כיוון ריכוזי = אופקי, לכיוון מרכז המעגל:\n"
                "$$F_c = \\frac{mv^2}{r} = \\frac{0.5 \\times 16}{1.2} = \\frac{8}{1.2}$$\n\n"
                "### צעד 2 — קשר מתח לכוח ריכוזי\n"
                "אם החוט כמעט אופקי, $T \\approx mv^2/r$:\n"
                "$$T \\approx 6.67\\;\\text{N}$$\n\n"
                "### צעד 3 — בדיקה גיאומטרית (אופציונלי)\n"
                "עם זווית $\\theta$ קטנה מהאופקי: $T\\cos\\theta = mg$ ו-$T\\sin\\theta = mv^2/r$. "
                "לזוויות קטנות, $T$ מעט מעל 6.67 N.\n\n"
                "**תשובה:** $T \\approx 6.67\\;\\text{N}$.\n\n"
                "**טיפ לבחינה:** כשכתוב \"מעגל אופקי\" ברמת בגרות, "
                "$T = mv^2/r$ ישירות הוא בדרך כלל הנתיב המיועד.\n\n"
                "**בדיקה:** $6.67\\;\\text{N}$ סביר לכדור קל — אם קיבלתם מאות ניוטון, "
                "בדקו שחילקתם ב-$r$ ולא שכחתם לרבוע את $v$."
            )
        elif kind == "worked_example" and sid == "worked_example_2":
            sec["body_en_md"] = (
                "**Given:** A road is banked at $\\theta = 20°$ for a curve of radius "
                "$r = 80\\;\\text{m}$. Find the **ideal speed** at which no friction is needed. "
                "($g = 10\\;\\text{m/s}^2$)\n\n"
                "On a banked turn, the normal force tilts. Its horizontal component supplies "
                "centripetal force; vertical component balances weight.\n\n"
                "### Move 1 — Draw FBD in rotated axes\n"
                "Forces: $N$ (perpendicular to road), $mg$ (down). No friction at ideal speed.\n"
                "$$N\\sin\\theta = \\frac{mv^2}{r} \\quad \\text{(horizontal, inward)}$$\n"
                "$$N\\cos\\theta = mg \\quad \\text{(vertical)}$$\n\n"
                "### Move 2 — Eliminate $N$ and $m$\n"
                "Divide the equations:\n"
                "$$\\tan\\theta = \\frac{v^2}{rg}$$\n\n"
                "### Move 3 — Solve for $v$\n"
                "$$v = \\sqrt{rg\\tan\\theta} = \\sqrt{80 \\times 10 \\times \\tan 20°}$$\n"
                "$$v = \\sqrt{800 \\times 0.364} = \\sqrt{291.2} \\approx \\boxed{17.1\\;\\text{m/s}}$$\n\n"
                "**Interpretation:** At 17.1 m/s (~62 km/h), drivers need no sideways friction. "
                "Slower or faster speeds require friction to prevent sliding.\n\n"
                "**Exam tip:** Memorize $\\tan\\theta = v^2/(rg)$ — it appears frequently on Bagrut.\n\n"
                "### Move 4 — Convert to km/h\n"
                "$$17.1\\;\\text{m/s} \\times 3.6 \\approx 62\\;\\text{km/h}$$\n"
                "Compare to posted speed limits on highway ramps — banking is designed near this range.\n\n"
                "**Self-check:** If $\\tan 20° \\approx 0.364$, then $v^2 = 0.364 \\times 800 = 291$ ✓."
            )
            sec["body_he_md"] = (
                "**נתון:** כביש מוטה ב-$\\theta = 20°$ לעקומה ברדיוס $r = 80\\;\\text{m}$. "
                "מצאו **מהירות אידיאלית** שבה אין צורך בחיכוך. ($g = 10\\;\\text{m/s}^2$)\n\n"
                "בפנייה מוטה, הכוח הנורמלי נוטה. הרכיב האופקי שלו מספק כוח ריכוזי; "
                "האנכי מאזן משקל.\n\n"
                "### צעד 1 — FBD בצירים מסובבים\n"
                "כוחות: $N$ (מאונך לכביש), $mg$ (מטה). ללא חיכוך במהירות אידיאלית.\n"
                "$$N\\sin\\theta = \\frac{mv^2}{r} \\quad \\text{(אופקי, פנימה)}$$\n"
                "$$N\\cos\\theta = mg \\quad \\text{(אנכי)}$$\n\n"
                "### צעד 2 — ביטול $N$ ו-$m$\n"
                "חלוקת המשוואות:\n"
                "$$\\tan\\theta = \\frac{v^2}{rg}$$\n\n"
                "### צעד 3 — פתרון עבור $v$\n"
                "$$v = \\sqrt{rg\\tan\\theta} = \\sqrt{80 \\times 10 \\times \\tan 20°} "
                "\\approx \\boxed{17.1\\;\\text{m/s}}$$\n\n"
                "**פרשנות:** ב-17.1 m/s (~62 קמ\"ש) אין צורך בחיכוך צדדי. "
                "מהירויות אחרות דורשות חיכוך למניעת החלקה.\n\n"
                "**טיפ לבחינה:** שיננו $\\tan\\theta = v^2/(rg)$ — מופיע לעיתים קרובות בבגרות.\n\n"
                "### צעד 4 — המרה לקמ\"ש\n"
                "$$17.1\\;\\text{m/s} \\times 3.6 \\approx 62\\;\\text{km/h}$$\n"
                "השוו למגבלות מהירות בכבישים — נטייה מתוכננת בטווח זה.\n\n"
                "**בדיקה עצמית:** $\\tan 20° \\approx 0.364$, אז $v^2 = 0.364 \\times 800 = 291$ ✓."
            )
        elif kind == "worked_example" and sid == "worked_example_3":
            sec["body_en_md"] = (
                "**Given:** A $0.3\\;\\text{kg}$ ball on a $0.8\\;\\text{m}$ string moves in a "
                "**vertical** circle. Find (a) minimum speed at the top, (b) tension at the bottom "
                "when the ball barely completes the loop (minimum speed at top). ($g = 10\\;\\text{m/s}^2$)\n\n"
                "Vertical circles combine **energy** (speed changes with height) and "
                "**centripetal force** (direction of \"center\" is always toward the pivot).\n\n"
                "### Move 1 — Minimum speed at top\n"
                "At the top, both gravity and tension pull toward center (downward). "
                "Minimum speed when $T = 0$:\n"
                "$$mg = \\frac{mv_{\\text{top}}^2}{r} \\Rightarrow "
                "v_{\\text{top,min}} = \\sqrt{gr} = \\sqrt{8} \\approx 2.83\\;\\text{m/s}$$\n\n"
                "### Move 2 — Speed at bottom via energy\n"
                "Drop height from top to bottom = $2r$:\n"
                "$$\\frac{1}{2}mv_{\\text{bot}}^2 = \\frac{1}{2}mv_{\\text{top}}^2 + mg(2r)$$\n"
                "$$v_{\\text{bot}}^2 = v_{\\text{top}}^2 + 4gr = 8 + 32 = 40$$"
                " $\\Rightarrow v_{\\text{bot}} = \\sqrt{40}\\;\\text{m/s}$\n\n"
                "### Move 3 — Tension at bottom\n"
                "At bottom, center is above — upward is inward:\n"
                "$$T - mg = \\frac{mv_{\\text{bot}}^2}{r}$$\n"
                "$$T = m\\left(g + \\frac{v_{\\text{bot}}^2}{r}\\right) = "
                "0.3\\left(10 + \\frac{40}{0.8}\\right) = 0.3 \\times 60 = \\boxed{18\\;\\text{N}}$$\n\n"
                "**Check:** $T > mg$ at bottom — the string must pull harder than weight alone.\n\n"
                "**Exam tip:** Always label where the center is (above or below) before writing "
                "$mg \\pm T = mv^2/r$."
            )
            sec["body_he_md"] = (
                "**נתון:** כדור $0.3\\;\\text{kg}$ על חוט $0.8\\;\\text{m}$ נע ב**מעגל אנכי**. "
                "מצאו (א) מהירות מינימלית בראש, (ב) מתח בתחתית כשהכדור בדיוק מסיים את הלולאה "
                "(מהירות מינ' בראש). ($g = 10\\;\\text{m/s}^2$)\n\n"
                "מעגלים אנכיים משלבים **אנרגיה** (מהירות משתנה עם גובה) ו**כוח ריכוזי** "
                "(כיוון \"מרכז\" תמיד לכיוון הציר).\n\n"
                "### צעד 1 — מהירות מינימלית בראש\n"
                "בראש, כבידה ומתח מושכים למרכז (מטה). מהירות מינ' כש-$T = 0$:\n"
                "$$mg = \\frac{mv_{\\text{top}}^2}{r} \\Rightarrow "
                "v_{\\text{top,min}} = \\sqrt{gr} = \\sqrt{8} \\approx 2.83\\;\\text{m/s}$$\n\n"
                "### צעד 2 — מהירות בתחתית דרך אנרגיה\n"
                "ירידה מראש לתחתית = $2r$:\n"
                "$$\\frac{1}{2}mv_{\\text{bot}}^2 = \\frac{1}{2}mv_{\\text{top}}^2 + mg(2r)$$\n"
                "$$v_{\\text{bot}}^2 = 8 + 32 = 40 \\Rightarrow v_{\\text{bot}} = \\sqrt{40}\\;\\text{m/s}$$\n\n"
                "### צעד 3 — מתח בתחתית\n"
                "בתחתית, המרכז למעלה — כלפי מעלה = פנימה:\n"
                "$$T - mg = \\frac{mv_{\\text{bot}}^2}{r}$$\n"
                "$$T = 0.3\\left(10 + \\frac{40}{0.8}\\right) = \\boxed{18\\;\\text{N}}$$\n\n"
                "**בדיקה:** $T > mg$ בתחתית — החוט חייב למשוך חזק יותר מהמשקל בלבד.\n\n"
                "**טיפ לבחינה:** סמנו תמיד איפה המרכז (מעל או מתחת) לפני $mg \\pm T = mv^2/r$."
            )
        elif kind == "checkpoint" and sid == "checkpoint_1":
            sec["checkpoint_solution_en"] = (
                "A car on a hill crest — center of curvature is **below** the car at the top.\n\n"
                "**Step 1 — Centripetal direction:** Downward (toward center of the circular arc).\n\n"
                "**Step 2 — Newton's 2nd law (radial):**\n"
                "$$mg - N = \\frac{mv^2}{R}$$\n"
                "Gravity exceeds normal force; the deficit provides inward acceleration.\n\n"
                "**Step 3 — Solve for $N$:**\n"
                "$$N = m\\left(g - \\frac{v^2}{R}\\right) = 1000\\left(10 - \\frac{400}{50}\\right) "
                "= 1000(10 - 8) = \\boxed{2000\\;\\text{N}}$$\n\n"
                "**Check:** $N < mg$ — passengers feel lighter at the crest. If $v^2/R > g$, "
                "the car would lose contact ($N = 0$)."
            )
            sec["checkpoint_solution_he"] = (
                "מכונית על פסגת גבעה — מרכז העקמומיות **מתחת** למכונית בראש.\n\n"
                "**שלב 1 — כיוון ריכוזי:** מטה (לכיוון מרכז הקשת).\n\n"
                "**שלב 2 — חוק ניוטון השני (רадиальי):**\n"
                "$$mg - N = \\frac{mv^2}{R}$$\n"
                "כבידה גדולה מהנורמלי; ההפרש מספק תאוצה פנימה.\n\n"
                "**שלב 3 — פתרון עבור $N$:**\n"
                "$$N = 1000\\left(10 - \\frac{400}{50}\\right) = 1000(10 - 8) = \\boxed{2000\\;\\text{N}}$$\n\n"
                "**בדיקה:** $N < mg$ — נוסעים מרגישים קלים יותר בפסגה. אם $v^2/R > g$, "
                "המכונית תנתק ($N = 0$)."
            )
        elif kind == "checkpoint" and sid == "checkpoint_2":
            sec["checkpoint_solution_en"] = (
                "ISS orbit — gravity provides centripetal force (approximate $g$ constant).\n\n"
                "**Step 1 — Orbital radius from Earth's center:**\n"
                "$$r = R_E + h = 6400 + 400 = 6800\\;\\text{km} = 6.8\\times10^6\\;\\text{m}$$\n\n"
                "**Step 2 — Set $mg = mv^2/r$ (or $g = v^2/r$):**\n"
                "$$v = \\sqrt{gr} = \\sqrt{10 \\times 6.8\\times10^6} = \\sqrt{6.8\\times10^7}$$\n\n"
                "**Step 3 — Evaluate:**\n"
                "$$v \\approx 8246\\;\\text{m/s} \\approx \\boxed{8.2\\;\\text{km/s}}$$\n\n"
                "**Context:** Real ISS speed is ~7.7 km/s because $g$ decreases with altitude. "
                "Our estimate is within ~7% — acceptable for Bagrut \"assume $g$ constant\" problems.\n\n"
                "**Exam tip:** Always add altitude to Earth radius before using $v = \\sqrt{gr}$."
            )
            sec["checkpoint_solution_he"] = (
                "מסלול ISS — כבידה מספקת כוח ריכוזי (קירוב $g$ קבוע).\n\n"
                "**שלב 1 — רדיוס מסלול ממרכז כדה\"א:**\n"
                "$$r = R_E + h = 6800\\;\\text{km} = 6.8\\times10^6\\;\\text{m}$$\n\n"
                "**שלב 2 — $mg = mv^2/r$ (או $g = v^2/r$):**\n"
                "$$v = \\sqrt{gr} = \\sqrt{10 \\times 6.8\\times10^6}$$\n\n"
                "**שלב 3 — חישוב:**\n"
                "$$v \\approx 8246\\;\\text{m/s} \\approx \\boxed{8.2\\;\\text{km/s}}$$\n\n"
                "**הקשר:** מהירות ISS אמיתית ~7.7 ק\"מ/ש כי $g$ קטן עם הגובה. "
                "הערכה שלנו בתוך ~7% — מקובל בבגרות עם \"הנח $g$ קבוע\".\n\n"
                "**טיפ לבחינה:** תמיד הוסיפו גובה לרדיוס כדה\"א לפני $v = \\sqrt{gr}$."
            )
        elif kind == "method_guide":
            sec["body_en_md"] = (
                "| Situation | Net force toward center | Key equation |\n"
                "|---|---|---|\n"
                "| Ball on string (horizontal) | Tension component | $T \\approx mv^2/r$ |\n"
                "| Car on flat road (turn) | Static friction | $f = mv^2/r$; $v_{\\max} = \\sqrt{\\mu_s rg}$ |\n"
                "| Top of hill / bridge crest | $mg - N$ | $N = m(g - v^2/r)$ |\n"
                "| Bottom of valley | $N - mg$ | $N = m(g + v^2/r)$ |\n"
                "| Banked road (no friction) | $N\\sin\\theta$ | $\\tan\\theta = v^2/(rg)$ |\n"
                "| Satellite (circular orbit) | Gravity | $g = v^2/r$ → $v = \\sqrt{gr}$ |\n"
                "| Vertical loop — top | $mg + T$ | $v_{\\min} = \\sqrt{gr}$ at $T = 0$ |\n"
                "| Vertical loop — bottom | $T - mg$ | $T = m(g + v^2/r)$ |\n\n"
                "**Decision flow:**\n"
                "1. Draw the object and mark the **center of the circle**.\n"
                "2. List all forces; resolve into radial and tangential if needed.\n"
                "3. Write $\\sum F_{\\text{radial}} = mv^2/r$ toward center (positive inward).\n"
                "4. If speed varies (vertical circle), use energy conservation between points first.\n\n"
                "**Tip:** Mass often cancels in ratio problems. Compare $v^2/r$ to $g$ for "
                "contact-loss questions ($N = 0$ when $v^2/r = g$ at a crest)."
            )
            sec["body_he_md"] = (
                "| מצב | כוח נטו לכיוון מרכז | נוסחה מרכזית |\n"
                "|---|---|---|\n"
                "| כדור על חוט (אופקי) | רכיב מתח | $T \\approx mv^2/r$ |\n"
                "| פנייה בכביש שטוח | חיכוך סטטי | $f = mv^2/r$; $v_{\\max} = \\sqrt{\\mu_s rg}$ |\n"
                "| ראש גבעה / גשר | $mg - N$ | $N = m(g - v^2/r)$ |\n"
                "| תחתית עמק | $N - mg$ | $N = m(g + v^2/r)$ |\n"
                "| כביש מוטה (ללא חיכוך) | $N\\sin\\theta$ | $\\tan\\theta = v^2/(rg)$ |\n"
                "| לוויין (מסלול מעגלי) | כבידה | $g = v^2/r$ → $v = \\sqrt{gr}$ |\n"
                "| לולאה אנכית — ראש | $mg + T$ | $v_{\\min} = \\sqrt{gr}$ ב-$T = 0$ |\n"
                "| לולאה אנכית — תחתית | $T - mg$ | $T = m(g + v^2/r)$ |\n\n"
                "**זרימת החלטה:**\n"
                "1. שרטטו את הגוף וסמנו את **מרכז המעגל**.\n"
                "2. רשמו כל הכוחות; פרקו לרадиальי ומשיקי אם צריך.\n"
                "3. כתבו $\\sum F_{\\text{רדיальי}} = mv^2/r$ לכיוון מרכז (חיובי פנימה).\n"
                "4. אם המהירות משתנה (מעגל אנכי), שימור אנרגיה בין נקודות קודם.\n\n"
                "**טיפ:** מסה לעיתים מתבטלת בבעיות יחס. השוו $v^2/r$ ל-$g$ "
                "בשאלות ניתוק ($N = 0$ כש-$v^2/r = g$ בפסגה)."
            )
        elif kind == "pitfall":
            sec["body_en_md"] = (
                "1. **\"Centrifugal force\" is not real in an inertial frame.** Passengers feel "
                "thrown outward because their inertia carries them tangent to the curve while the "
                "car turns. In a ground frame, only **centripetal** (inward) forces exist.\n\n"
                "2. **Centripetal force is not a new force type.** It names the net inward "
                "component — tension, friction, gravity, or normal. Never add \"$F_c$\" as an "
                "extra force on an FBD.\n\n"
                "3. **Constant speed $\\neq$ zero acceleration.** In UCM, $|v|$ is fixed but "
                "$\\vec{v}$ rotates; $a_c = v^2/r \\neq 0$ always.\n\n"
                "4. **Top vs bottom of vertical loop:** At the **top**, center is below — both "
                "$mg$ and $T$ point toward center: $mg + T = mv^2/r$. At the **bottom**, "
                "center is above: $T - mg = mv^2/r$. Reversing signs is the #1 loop error.\n\n"
                "5. **Radius from center, not diameter.** Orbital problems need $r = R_{\\text{planet}} + h$ "
                "from the planet's center, not altitude alone."
            )
            sec["body_he_md"] = (
                "1. **\"כוח צנטריפוגלי\" אינו אמיתי במסגרת אינרציאלית.** נוסעים מרגישים "
                "נזרקים החוצה כי האינרציה שלהם נושאת אותם במשיק למסלול בעוד הרכב פונה. "
                "במסגרת קרקע, קיימים רק כוחות **ריכוזיים** (פנימה).\n\n"
                "2. **כוח ריכוזי אינו סוג כוח חדש.** הוא שם הרכיב הנטו הפנימה — מתח, חיכוך, "
                "כבידה, נורמלי. לעולם אל תוסיפו \"$F_c$\" ככוח נוסף ב-FBD.\n\n"
                "3. **מהירות קבועה $\\neq$ תאוצה אפס.** ב-UCM, $|v|$ קבוע אך $\\vec{v}$ מסתובב; "
                "$a_c = v^2/r \\neq 0$ תמיד.\n\n"
                "4. **ראש מול תחתית בלולאה אנכית:** ב**ראש**, המרכז למטה — $mg$ ו-$T$ "
                "למרכז: $mg + T = mv^2/r$. ב**תחתית**, המרכז למעלה: $T - mg = mv^2/r$. "
                "היפוך סימנים — טעות #1 בלולאות.\n\n"
                "5. **רדיוס ממרכז, לא קוטר.** בעיות מסלול: $r = R_{\\text{כוכב}} + h$ "
                "ממרכז הכוכב, לא גובה בלבד."
            )
        elif kind == "why_matters":
            sec["body_en_md"] = (
                "Circular motion is the bridge between **Newton's laws in straight lines** and "
                "**rotation, orbits, and engineering design**. Every curved path at speed involves "
                "$a_c = v^2/r$ — whether a bicycle turn, a wind turbine blade tip, or a GPS satellite.\n\n"
                "**You will use this to unlock:**\n"
                "- `concept:rotational_dynamics` **Rotational Dynamics & Angular Momentum** (prerequisite)\n"
                "- `concept:gravitation` **Gravitation** — satellite orbits reuse $v = \\sqrt{gR}$\n\n"
                "**Builds on:**\n"
                "- `concept:newton_laws` **Newton's Laws of Motion**\n"
                "- `concept:work_energy` **Work & Energy** — vertical circle problems\n\n"
                "**Why it matters for exams:** Bagrut rewards identifying which real force provides "
                "$mv^2/r$ in a new context — banked roads, roller coasters, conical pendulums. "
                "Always ask: \"Where is the center, and what pulls toward it?\""
            )
            sec["body_he_md"] = (
                "תנועה מעגלית היא הגשר בין **חוקי ניוטון בקו ישר** ל**סיבוב, מסלולים ותכנון "
                "הנדסי**. כל מסלול עקום במהירות כולל $a_c = v^2/r$ — פניית אופניים, קצה "
                "טורבינת רוח, או לוויין GPS.\n\n"
                "**תשתמשו בזה כדי להתקדם ל:**\n"
                "- `concept:rotational_dynamics` **דינמיקה סיבובית ותנע זוויתי** (דרישת קדם)\n"
                "- `concept:gravitation` **גרביטציה** — מסלולי לוויינים משתמשים ב-$v = \\sqrt{gR}$\n\n"
                "**מבוסס על:**\n"
                "- `concept:newton_laws` **חוקי ניוטון**\n"
                "- `concept:work_energy` **עבודה ואנרגיה** — בעיות מעגל אנכי\n\n"
                "**למה זה חשוב לבחינות:** בבגרות מעריכים זיהוי איזה כוח אמיתי מספק "
                "$mv^2/r$ בהקשר חדש — כבישים מוטים, רכבות הרים, מטוטלת חרוטית. "
                "שאלו תמיד: \"איפה המרכז, ומה נמשך אליו?\""
            )
        elif kind == "before_exam":
            sec["body_en_md"] = (
                "**Core formulas (say each once):**\n"
                "- $a_c = v^2/r = \\omega^2 r$; $F_c = mv^2/r = m\\omega^2 r$\n"
                "- $v = r\\omega$; $\\omega = 2\\pi f = 2\\pi/T$; $v = 2\\pi r/T$\n"
                "- Banked road: $\\tan\\theta = v^2/(rg)$\n"
                "- Flat turn: $v_{\\max} = \\sqrt{\\mu_s rg}$\n"
                "- Loop top (min): $v_{\\min} = \\sqrt{gr}$ when $T = 0$\n"
                "- Satellite: $v = \\sqrt{gr}$ with $r$ from planet center\n\n"
                "**Problem-solving checklist:**\n"
                "1. Mark center of circle on diagram.\n"
                "2. FBD — list real forces only.\n"
                "3. $\\sum F_{\\text{inward}} = mv^2/r$.\n"
                "4. Check units and compare $v^2/r$ to $g$ if contact forces appear.\n\n"
                "**Last review:** Solve one checkpoint (hill crest + banked road) without notes.\n\n"
                "**Quick sanity checks:** $a_c = 4\\;\\text{m/s}^2$ for $v=20$, $r=100$; "
                "$v_{\\min}=10\\;\\text{m/s}$ for loop with $r=10$ m at top."
            )
            sec["body_he_md"] = (
                "**נוסחאות ליבה (אמרו כל אחת פעם):**\n"
                "- $a_c = v^2/r = \\omega^2 r$; $F_c = mv^2/r = m\\omega^2 r$\n"
                "- $v = r\\omega$; $\\omega = 2\\pi f = 2\\pi/T$; $v = 2\\pi r/T$\n"
                "- כביש מוטה: $\\tan\\theta = v^2/(rg)$\n"
                "- פנייה שטוחה: $v_{\\max} = \\sqrt{\\mu_s rg}$\n"
                "- לולאה ראש (מינ'): $v_{\\min} = \\sqrt{gr}$ ב-$T = 0$\n"
                "- לוויין: $v = \\sqrt{gr}$ עם $r$ ממרכז כוכב\n\n"
                "**צ'ק-ליסט פתרון:**\n"
                "1. סמנו מרכז מעגל בשרטוט.\n"
                "2. FBD — רק כוחות אמיתיים.\n"
                "3. $\\sum F_{\\text{פנימה}} = mv^2/r$.\n"
                "4. בדקו יחידות והשוו $v^2/r$ ל-$g$ אם יש כוחות מגע.\n\n"
                "**חזרה אחרונה:** פתרו checkpoint אחד (פסגת גבעה + כביש מוטה) בלי פתקים."
            )
        elif kind == "summary":
            sec["body_en_md"] = (
                "- **Centripetal acceleration:** $a_c = v^2/r = \\omega^2 r$, always toward center\n"
                "- **Centripetal force:** net inward force $= mv^2/r$ — provided by tension, "
                "friction, gravity, or normal components\n"
                "- **Uniform circular motion:** $|v|$ constant, direction changing → $a_c \\neq 0$\n"
                "- **Kinematic links:** $v = r\\omega$, $T = 2\\pi/\\omega$, $v = 2\\pi r/T$\n"
                "- **Banked road:** $\\tan\\theta = v^2/(rg)$ at design speed without friction\n"
                "- **Vertical loop:** $v_{\\min} = \\sqrt{gr}$ at top; energy links top and bottom speeds\n"
                "- **Satellite:** $v = \\sqrt{gr}$ with $r$ measured from planet center\n\n"
                "**Takeaway:** Draw the center, identify the real inward force, apply "
                "$\\sum F = mv^2/r$ — the same three-step pattern covers every Bagrut variant."
            )
            sec["body_he_md"] = (
                "- **תאוצה ריכוזית:** $a_c = v^2/r = \\omega^2 r$, תמיד לכיוון מרכז\n"
                "- **כוח ריכוזי:** כוח נטו פנימה $= mv^2/r$ — מתח, חיכוך, כבידה, או רכיבי נורמלי\n"
                "- **תנועה מעגלית אחידה:** $|v|$ קבוע, כיוון משתנה → $a_c \\neq 0$\n"
                "- **קשרים קינמטיים:** $v = r\\omega$, $T = 2\\pi/\\omega$, $v = 2\\pi r/T$\n"
                "- **כביש מוטה:** $\\tan\\theta = v^2/(rg)$ במהירות תכנון ללא חיכוך\n"
                "- **לולאה אנכית:** $v_{\\min} = \\sqrt{gr}$ בראש; אנרגיה מקשרת מהירויות\n"
                "- **לוויין:** $v = \\sqrt{gr}$ עם $r$ ממרכז כוכב\n\n"
                "**מסקנה:** שרטטו מרכז, זהו כוח פנימה אמיתי, יישמו $\\sum F = mv^2/r$ — "
                "אותה שיטת שלושה שלבים לכל וariant בבגרות."
            )

    for q in lesson["questions"]:
        ord_n = q.get("ord")
        if ord_n in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_n]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_n]["he"]

    lesson["version"] = 2
    return lesson


def validate(lesson):
    errors = []
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                errors.append(f"{sec.get('id', kind)} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                errors.append(f"{sec.get('id', kind)} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                errors.append(f"{sec.get('id', kind)} HE weak/English paste")
        if kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS["worked_example"]["en"]:
                errors.append(f"{sec.get('id')} EN: {en_w} < 130")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                errors.append(f"{sec.get('id')} HE: {he_w} < 110")

    for q in lesson["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"q{q.get('ord')} expl_{lang}: {w} words (need 80-150)")

    return errors


def main():
    lesson = build_lesson()
    errors = validate(lesson)
    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}")
    print(f"Validation: {len(errors)} issues")

    result = subprocess.run(
        ["node", str(ROOT / "scripts/seed-lessons.mjs"), "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)
    if "207/207" not in result.stdout:
        print("WARNING: expected 207/207 in dry-run output")


if __name__ == "__main__":
    main()
