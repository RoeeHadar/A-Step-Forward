#!/usr/bin/env python3
"""Expand projectile_motion.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/projectile_motion.json"

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
            "At the highest point of a projectile trajectory, the vertical component of velocity "
            "momentarily becomes zero — the object stops rising and begins to fall. However, "
            "horizontal motion is unaffected by gravity (assuming no air resistance), so "
            "$v_x$ remains constant throughout the flight. Therefore only $v_y = 0$ at the apex.\n\n"
            "**Why option 3 is correct:** The vertical velocity crosses zero at the turning point; "
            "horizontal velocity never changes.\n\n"
            "**Common wrong path:** Choosing \"speed = 0\" because the object \"stops going up.\" "
            "Speed is the magnitude $|v| = \\sqrt{v_x^2 + v_y^2}$, which equals $|v_x|$ at the top — "
            "not zero unless the launch was purely vertical.\n\n"
            "**Exam tip:** Draw separate $x$ and $y$ motion diagrams. At the apex, mark $v_y = 0$ "
            "but keep $v_x$ unchanged. Acceleration is always $-g$ downward, never zero."
        ),
        "he": (
            "בנקודת השיא של מסלול קליע, הרכיב האנכי של המהירות מתאפס לרגע — הגוף מפסיק לעלות "
            "ומתחיל לרדת. עם זאת, התנועה האופקית אינה מושפעת מכוח הכבידה (בהנחה שאין התנגדות "
            "אוויר), ולכן $v_x$ נשאר קבוע לאורך כל הטיסה. לכן רק $v_y = 0$ בראש המסלול.\n\n"
            "**למה אפשרות 3 נכונה:** המהירות האנכית חוצה אפס בנקודת הפנייה; המהירות האופקית "
            "לא משתנה.\n\n"
            "**טעות נפוצה:** בחירה ב\"מהירות = 0\" כי הגוף \"מפסיק לעלות.\" מהירות היא "
            "הגודל $|v| = \\sqrt{v_x^2 + v_y^2}$, ששווה ל-$|v_x|$ בראש — לא אפס אלא אם "
            "השיגור היה אנכי לחלוטין.\n\n"
            "**טיפ לבחינה:** ציירו דיאגרמות נפרדות ל-$x$ ו-$y$. בראש, סמנו $v_y = 0$ "
            "אך השאירו $v_x$ ללא שינוי. התאוצה תמיד $-g$ כלפי מטה, לעולם לא אפס."
        ),
    },
    2: {
        "en": (
            "For a horizontal launch from height $h$, the initial vertical velocity is zero: "
            "$v_{0y} = 0$. The vertical motion is pure free fall from rest, so the time to reach "
            "the ground comes from $h = \\frac{1}{2}gt^2$.\n\n"
            "Substituting $h = 5$ m and $g = 9.8$ m/s²:\n"
            "$$t = \\sqrt{\\frac{2h}{g}} = \\sqrt{\\frac{2 \\times 5}{9.8}} \\approx 1.01\\text{ s}$$\n\n"
            "The horizontal speed (8 m/s) does not affect the fall time — this independence "
            "principle is the heart of projectile motion.\n\n"
            "**Common wrong path:** Using $t = h/v_0$ or $t = v_0/g$, mixing horizontal and "
            "vertical formulas.\n\n"
            "**Exam tip:** For horizontal launch, always find $t$ from the vertical equation first, "
            "then use that same $t$ for horizontal distance $x = v_0 t$."
        ),
        "he": (
            "בשיגור אופקי מגובה $h$, המהירות האנכית ההתחלתית היא אפס: $v_{0y} = 0$. "
            "התנועה האנכית היא נפילה חופשית ממנוחה, ולכן זמן ההגעה לקרקע מגיע מ-$h = \\frac{1}{2}gt^2$.\n\n"
            "הצבה $h = 5$ m ו-$g = 9.8$ m/s²:\n"
            "$$t = \\sqrt{\\frac{2h}{g}} = \\sqrt{\\frac{2 \\times 5}{9.8}} \\approx 1.01\\text{ s}$$\n\n"
            "המהירות האופקית (8 m/s) לא משפיעה על זמן הנפילה — עקרון העצמאות הוא לב "
            "תנועת הקליע.\n\n"
            "**טעות נפוצה:** שימוש ב-$t = h/v_0$ או $t = v_0/g$, ערבוב נוסחאות אופקיות ואנכיות.\n\n"
            "**טיפ לבחינה:** בשיגור אופקי, תמיד מצאו $t$ מהמשוואה האנכית קודם, "
            "ואז השתמשו באותו $t$ לטווח $x = v_0 t$. "
            "המהירות האופקית 8 m/s לא מופיעה בשום שלב של חישוב הזמן — "
            "זו בדיקה מהירה שאתם באמת מבינים את עקרון העצמאות."
        ),
    },
    3: {
        "en": (
            "At a launch angle of $45°$, the range formula simplifies beautifully because "
            "$\\sin 2\\theta = \\sin 90° = 1$. The general range is "
            "$R = \\dfrac{v_0^2 \\sin 2\\theta}{g}$, so at $45°$:\n"
            "$$R = \\frac{v_0^2}{g} = \\frac{14^2}{9.8} = \\frac{196}{9.8} = 20\\text{ m}$$\n\n"
            "This is the maximum range for a given initial speed on level ground — a fact "
            "worth memorizing for Bagrut.\n\n"
            "**Common wrong path:** Using $R = v_0 T$ without first finding components, or "
            "forgetting the factor of $\\sin 2\\theta$ and computing $R = v_0^2 \\sin\\theta / g$.\n\n"
            "**Self-check:** At $45°$, $v_{0x} = v_{0y}$, so the symmetric trajectory confirms "
            "maximum range.\n\n"
            "**Exam tip:** When you see $45°$ on level ground, jump directly to $R = v_0^2/g$."
        ),
        "he": (
            "בזווית שיגור של $45°$, נוסחת הטווח מתפשטת יפה כי $\\sin 2\\theta = \\sin 90° = 1$. "
            "הטווח הכללי הוא $R = \\dfrac{v_0^2 \\sin 2\\theta}{g}$, ולכן ב-$45°$:\n"
            "$$R = \\frac{v_0^2}{g} = \\frac{14^2}{9.8} = \\frac{196}{9.8} = 20\\text{ m}$$\n\n"
            "זה הטווח המקסימלי למהירות התחלתית נתונה על קרקע שטוחה — עובדה שכדאי לזכור לבגרות.\n\n"
            "**טעות נפוצה:** שימוש ב-$R = v_0 T$ בלי למצוא רכיבים קודם, או שכחת גורם "
            "$\\sin 2\\theta$ וחישוב $R = v_0^2 \\sin\\theta / g$.\n\n"
            "**בדיקה עצמית:** ב-$45°$, $v_{0x} = v_{0y}$, והמסלול הסימטרי מאשר טווח מקסימלי.\n\n"
            "**טיפ לבחינה:** כשמופיע $45°$ על קרקע שטוחה, קפצו ישירות ל-$R = v_0^2/g$. "
            "אם תפרקו לרכיבים, וודאו ש-$v_{0x} = v_{0y}$ ב-$45°$ — "
            "זה מאשר שהמסלול סימטרי ושהטווח אכן מקסימלי."
        ),
    },
    4: {
        "en": (
            "Throughout projectile flight, the vertical velocity changes due to gravity: "
            "$v_y(t) = v_{0y} - gt$. At the highest point, the object momentarily stops "
            "moving upward before reversing direction — this is exactly when $v_y$ crosses zero.\n\n"
            "Setting $v_y = 0$:\n"
            "$$0 = v_{0y} - gt_{\\text{top}} \\Rightarrow t_{\\text{top}} = \\frac{v_{0y}}{g}$$\n\n"
            "At this instant, $v_y = 0$ but $v_x$ is unchanged. The answer is simply $v_y = 0$.\n\n"
            "**Common wrong path:** Answering that the entire velocity is zero, or confusing "
            "$v_y = 0$ with acceleration $a_y = 0$. Gravity still acts at the apex.\n\n"
            "**Exam tip:** \"At the top\" always means $v_y = 0$, never $v = 0$ (unless purely "
            "vertical launch) and never $a = 0$."
        ),
        "he": (
            "לאורך טיסת הקליע, המהירות האנכית משתנה בגלל כוח הכבידה: $v_y(t) = v_{0y} - gt$. "
            "בנקודת השיא, הגוף מפסיק לרגע לנוע כלפי מעלה לפני שמשנה כיוון — "
            "זה בדיוק כש-$v_y$ חוצה אפס.\n\n"
            "הצבת $v_y = 0$:\n"
            "$$0 = v_{0y} - gt_{\\text{top}} \\Rightarrow t_{\\text{top}} = \\frac{v_{0y}}{g}$$\n\n"
            "ברגע זה, $v_y = 0$ אך $v_x$ ללא שינוי. התשובה היא פשוט $v_y = 0$.\n\n"
            "**טעות נפוצה:** תשובה שהמהירות כולה אפס, או בלבול בין $v_y = 0$ לתאוצה $a_y = 0$. "
            "כוח הכבידה פועל גם בראש.\n\n"
            "**טיפ לבחינה:** \"בנקודת השיא\" תמיד פירושו $v_y = 0$, לעולם לא $v = 0$ "
            "(אלא אם שיגור אנכי) ולעולם לא $a = 0$."
        ),
    },
    5: {
        "en": (
            "For a projectile launched at $45°$ on level ground, $\\sin 2\\theta = \\sin 90° = 1$, "
            "so the range formula $R = v_0^2 \\sin 2\\theta / g$ becomes $R = v_0^2 / g$.\n\n"
            "With $v_0 = 10$ m/s:\n"
            "$$R = \\frac{10^2}{9.8} = \\frac{100}{9.8} \\approx 10.2\\text{ m}$$\n\n"
            "Alternatively, decompose: $v_{0x} = v_{0y} = 10/\\sqrt{2} \\approx 7.07$ m/s, "
            "$T = 2 v_{0y}/g \\approx 1.44$ s, $R = v_{0x} T \\approx 10.2$ m — same result.\n\n"
            "**Common wrong path:** Using $R = v_0 T$ with $T = v_0/g$ (wrong time formula), "
            "or computing $R = v_0^2 \\sin\\theta / g$ instead of $\\sin 2\\theta$.\n\n"
            "**Self-check:** At $45°$, $v_{0x} = v_{0y}$, confirming symmetric flight.\n\n"
            "**Exam tip:** $45°$ on flat ground is the fastest range calculation — use $R = v_0^2/g$. "
            "Memorize this shortcut; it appears on nearly every Bagrut projectile question set."
        ),
        "he": (
            "בקליע שמושק ב-$45°$ על קרקע שטוחה, $\\sin 2\\theta = \\sin 90° = 1$, "
            "ולכן נוסחת הטווח $R = v_0^2 \\sin 2\\theta / g$ הופכת ל-$R = v_0^2 / g$.\n\n"
            "עם $v_0 = 10$ m/s:\n"
            "$$R = \\frac{10^2}{9.8} = \\frac{100}{9.8} \\approx 10.2\\text{ m}$$\n\n"
            "לחלופין, פירוק: $v_{0x} = v_{0y} = 10/\\sqrt{2} \\approx 7.07$ m/s, "
            "$T = 2 v_{0y}/g \\approx 1.44$ s, $R = v_{0x} T \\approx 10.2$ m — אותה תוצאה.\n\n"
            "**טעות נפוצה:** שימוש ב-$R = v_0 T$ עם $T = v_0/g$ (נוסחת זמן שגויה), "
            "או חישוב $R = v_0^2 \\sin\\theta / g$ במקום $\\sin 2\\theta$.\n\n"
            "**בדיקה עצמית:** ב-$45°$, $v_{0x} = v_{0y}$, מאשרת טיסה סימטרית.\n\n"
            "**טיפ לבחינה:** $45°$ על קרקע שטוחה הוא חישוב הטווח המהיר ביותר — "
            "השתמשו ב-$R = v_0^2/g$. שמרו את הקיצור הזה; הוא מופיע כמעט בכל "
            "מקבץ שאלות קליע בבגרות."
        ),
    },
    6: {
        "en": (
            "This is a standard angled launch from level ground. First decompose the initial velocity "
            "using the given trigonometric values: $v_{0x} = 30 \\cos 37° = 30 \\times 0.8 = 24$ m/s "
            "and $v_{0y} = 30 \\sin 37° = 30 \\times 0.6 = 18$ m/s.\n\n"
            "Maximum height: $H = v_{0y}^2/(2g) = 18^2/19.6 = 324/19.6 \\approx 16.5$ m.\n"
            "Time of flight: $T = 2v_{0y}/g = 36/9.8 \\approx 3.67$ s.\n"
            "Range: $R = v_{0x} \\cdot T = 24 \\times 3.67 \\approx 88$ m.\n\n"
            "**Common wrong path:** Using $T = v_{0y}/g$ (time to top only, not full flight), "
            "or computing range before finding components.\n\n"
            "**Exam tip:** Write $v_{0x}$, $v_{0y}$ first in a box, then apply $H$, $T$, $R$ "
            "in that order. The $37°$ angle gives the clean $3$-$4$-$5$ triangle ratios. "
            "On Bagrut, when sine and cosine values are given explicitly, use them — "
            "do not reach for a calculator."
        ),
        "he": (
            "זהו שיגור זוויתי סטנדרטי מקרקע שטוחה. קודם מפרקים את המהירות ההתחלתית "
            "בערכי הטריגונומטריה הנתונים: $v_{0x} = 30 \\cos 37° = 30 \\times 0.8 = 24$ m/s "
            "ו-$v_{0y} = 30 \\sin 37° = 30 \\times 0.6 = 18$ m/s.\n\n"
            "גובה מקסימלי: $H = v_{0y}^2/(2g) = 18^2/19.6 = 324/19.6 \\approx 16.5$ m.\n"
            "זמן טיסה: $T = 2v_{0y}/g = 36/9.8 \\approx 3.67$ s.\n"
            "טווח: $R = v_{0x} \\cdot T = 24 \\times 3.67 \\approx 88$ m.\n\n"
            "**טעות נפוצה:** שימוש ב-$T = v_{0y}/g$ (זמן עד הראש בלבד, לא טיסה מלאה), "
            "או חישוב טווח לפני מציאת רכיבים.\n\n"
            "**טיפ לבחינה:** כתבו $v_{0x}$, $v_{0y}$ קודם בתיבה, ואז יישמו $H$, $T$, $R$ "
            "בסדר הזה. זווית $37°$ נותנת יחסי משולש $3$-$4$-$5$ נקיים. "
            "בבגרות, כשערכי sin ו-cos ניתנים במפורש, השתמשו בהם — "
            "אל תגיעו למחשבון."
        ),
    },
    7: {
        "en": (
            "For a horizontal launch, the horizontal velocity stays constant at $v_0 = 12$ m/s "
            "throughout the flight. The vertical velocity grows from zero due to free fall.\n\n"
            "Step 1 — time to ground: $t = \\sqrt{2h/g} = \\sqrt{160/9.8} \\approx 4.04$ s.\n"
            "Step 2 — vertical velocity at landing: $v_y = gt = 9.8 \\times 4.04 \\approx 39.6$ m/s.\n"
            "Step 3 — landing speed: $|v| = \\sqrt{v_x^2 + v_y^2} = \\sqrt{144 + 1568} = \\sqrt{1712} \\approx 41.4$ m/s.\n\n"
            "**Common wrong path:** Reporting only $v_y = 39.6$ m/s as the landing speed, "
            "ignoring the constant horizontal component. Also confusing speed with velocity direction.\n\n"
            "**Exam tip:** Landing speed for horizontal launch always exceeds $v_0$ because "
            "gravity adds a vertical component. Draw a velocity vector triangle at impact."
        ),
        "he": (
            "בשיגור אופקי, המהירות האופקית נשארת קבועה ב-$v_0 = 12$ m/s לאורך כל הטיסה. "
            "המהירות האנכית גדלה מאפס בגלל נפילה חופשית.\n\n"
            "שלב 1 — זמן עד קרקע: $t = \\sqrt{2h/g} = \\sqrt{160/9.8} \\approx 4.04$ s.\n"
            "שלב 2 — מהירות אנכית בנחיתה: $v_y = gt = 9.8 \\times 4.04 \\approx 39.6$ m/s.\n"
            "שלב 3 — מהירות נחיתה: $|v| = \\sqrt{v_x^2 + v_y^2} = \\sqrt{144 + 1568} = \\sqrt{1712} \\approx 41.4$ m/s.\n\n"
            "**טעות נפוצה:** דיווח רק על $v_y = 39.6$ m/s כמהירות נחיתה, "
            "תוך התעלמות מהרכיב האופקי הקבוע. גם בלבול בין מהירות לכיוון.\n\n"
            "**טיפ לבחינה:** מהירות נחיתה בשיגור אופקי תמיד גדולה מ-$v_0$ כי "
            "כוח הכבידה מוסיף רכיב אנכי. ציירו משולש מהירות בנקודת הפגיעה."
        ),
    },
    8: {
        "en": (
            "The question asks for speed when the vertical component is zero — this is exactly "
            "the highest point of the trajectory. At the apex, $v_y = 0$ but $v_x$ is unchanged "
            "from launch.\n\n"
            "The horizontal component: $v_{0x} = v_0 \\cos\\theta = 20 \\cos 60° = 20 \\times 0.5 = 10$ m/s.\n\n"
            "Since $v_y = 0$ at this point, the speed equals $|v_x|$:\n"
            "$$|v| = \\sqrt{v_x^2 + 0^2} = 10\\text{ m/s}$$\n\n"
            "**Common wrong path:** Answering $20$ m/s (the initial speed) or $0$ m/s "
            "(confusing $v_y = 0$ with total speed zero).\n\n"
            "**Exam tip:** \"Speed at maximum height\" is a standard Bagrut shortcut: "
            "it always equals $v_0 \\cos\\theta$, never $v_0$ itself (unless $\\theta = 0°$)."
        ),
        "he": (
            "השאלה שואלת על מהירות כשהרכיב האנכי אפס — זה בדיוק נקודת השיא של המסלול. "
            "בראש, $v_y = 0$ אך $v_x$ ללא שינוי מהשיגור.\n\n"
            "הרכיב האופקי: $v_{0x} = v_0 \\cos\\theta = 20 \\cos 60° = 20 \\times 0.5 = 10$ m/s.\n\n"
            "מאחר ש-$v_y = 0$ בנקודה זו, המהירות שווה ל-$|v_x|$:\n"
            "$$|v| = \\sqrt{v_x^2 + 0^2} = 10\\text{ m/s}$$\n\n"
            "**טעות נפוצה:** תשובה $20$ m/s (המהירות ההתחלתית) או $0$ m/s "
            "(בלבול בין $v_y = 0$ למהירות כוללת אפס).\n\n"
            "**טיפ לבחינה:** \"מהירות בגובה מקסימלי\" הוא קיצור דרך סטנדרטי בבגרות: "
            "תמיד שווה ל-$v_0 \\cos\\theta$, לעולם לא ל-$v_0$ עצמו (אלא אם $\\theta = 0°$). "
            "שאלו את עצמכם: \"מה נשאר מהמהירות ההתחלתית כשהרכיב האנכי התאפס?\" — "
            "רק הרכיב האופקי."
        ),
    },
}


def build_lesson():
    with open(OUT, encoding="utf-8") as f:
        lesson = json.load(f)

    section_bodies = {
        "intro": {
            "en": (
                "When you throw a ball horizontally off a cliff or kick a football at an angle, "
                "the object follows a curved **parabolic path** through the air. This motion is called "
                "**projectile motion** — it combines constant horizontal velocity with vertical free fall "
                "under gravity.\n\n"
                "**The central insight:** horizontal and vertical motions are **completely independent**. "
                "Gravity acts only on the vertical component; the horizontal component never changes "
                "(ignoring air resistance):\n"
                "- Horizontal: constant velocity ($a_x = 0$, $v_x = v_{0x}$).\n"
                "- Vertical: free fall ($a_y = -g = -9.8$ m/s² downward).\n\n"
                "This independence lets you solve two-dimensional problems by treating $x$ and $y$ "
                "separately — a technique that appears throughout Bagrut Physics (questionnaire 1).\n\n"
                "**Where this appears on Bagrut:**\n"
                "- Horizontal launch from a cliff or building.\n"
                "- Angled kick or throw on level ground.\n"
                "- Finding range, maximum height, time of flight, or landing speed.\n\n"
                "By the end of this lesson you will decompose initial velocity, apply the correct "
                "formulas for each problem type, and avoid the classic trap of mixing $x$ and $y$ components."
            ),
            "he": (
                "כשזורקים כדור אופקית מצוק או בועטים בכדור בזווית, הגוף עוקב אחר "
                "**מסלול פרבולי** באוויר. תנועה זו נקראת **תנועת קליע** — היא משלבת "
                "מהירות אופקית קבועה עם נפילה חופשית אנכית תחת כוח הכבידה.\n\n"
                "**התובנה המרכזית:** התנועה האופקית והאנכית **עצמאיות לחלוטין**. "
                "כוח הכבידה פועל רק על הרכיב האנכי; הרכיב האופקי לא משתנה "
                "(בהנחה שאין התנגדות אוויר):\n"
                "- אופקי: מהירות קבועה ($a_x = 0$, $v_x = v_{0x}$).\n"
                "- אנכי: נפילה חופשית ($a_y = -g = -9.8$ m/s² כלפי מטה).\n\n"
                "עצמאות זו מאפשרת לפתור בעיות דו-ממדיות על ידי טיפול נפרד ב-$x$ ו-$y$ — "
                "טכניקה שמופיעה לאורך בגרות פיזיקה (שאלון 1).\n\n"
                "**היכן זה מופיע בבגרות:**\n"
                "- שיגור אופקי מצוק או בניין.\n"
                "- בעיטה או זריקה בזווית על קרקע שטוחה.\n"
                "- מציאת טווח, גובה מקסימלי, זמן טיסה, או מהירות נחיתה.\n\n"
                "בסוף השיעור תפרקו מהירות התחלתית, תיישמו את הנוסחה הנכונה לכל סוג בעיה, "
                "ותימנעו מהמלכודת הקלאסית של ערבוב רכיבי $x$ ו-$y$."
            ),
        },
        "definition": {
            "en": (
                "A projectile is any object moving under gravity alone (no propulsion, negligible air "
                "resistance). Its motion is fully described by separating initial velocity into "
                "horizontal and vertical components.\n\n"
                "**Initial velocity components** (launch angle $\\theta$, initial speed $v_0$):\n"
                "$$v_{0x} = v_0\\cos\\theta, \\quad v_{0y} = v_0\\sin\\theta$$\n\n"
                "**Position as a function of time:**\n"
                "$$x(t) = v_{0x}\\,t, \\quad y(t) = v_{0y}\\,t - \\tfrac{1}{2}gt^2$$\n\n"
                "**Velocity as a function of time:**\n"
                "$$v_x(t) = v_{0x} \\quad \\text{(constant)}, \\quad v_y(t) = v_{0y} - gt$$\n\n"
                "**Horizontal launch** ($\\theta = 0°$): $v_{0x} = v_0$, $v_{0y} = 0$.\n\n"
                "**Key results on level ground** (launch and landing at same height):\n"
                "- Time of flight: $T = \\dfrac{2v_{0y}}{g}$\n"
                "- Range: $R = \\dfrac{v_0^2\\sin 2\\theta}{g}$ (maximum at $\\theta = 45°$)\n"
                "- Maximum height: $H = \\dfrac{v_{0y}^2}{2g}$\n\n"
                "**Speed at any point:** $|v| = \\sqrt{v_x^2 + v_y^2}$. "
                "**Direction:** $\\alpha = \\arctan(v_y / v_x)$ measured from the horizontal.\n\n"
                "**Acceleration:** Throughout the flight, $a_x = 0$ and $a_y = -g$ — gravity never "
                "acts horizontally. This is why we can treat the two axes independently on Bagrut problems. "
                "Air resistance is neglected unless the problem states otherwise."
            ),
            "he": (
                "קליע הוא כל גוף הנע תחת כוח הכבידה בלבד (ללא propulsion, התנגדות אוויר זניחה). "
                "תנועתו מתוארת במלואה על ידי הפרדת המהירות ההתחלתית לרכיבים אופקיים ואנכיים.\n\n"
                "**רכיבי מהירות התחלתית** (זווית שיגור $\\theta$, מהירות התחלתית $v_0$):\n"
                "$$v_{0x} = v_0\\cos\\theta, \\quad v_{0y} = v_0\\sin\\theta$$\n\n"
                "**מיקום כפונקציה של זמן:**\n"
                "$$x(t) = v_{0x}\\,t, \\quad y(t) = v_{0y}\\,t - \\tfrac{1}{2}gt^2$$\n\n"
                "**מהירות כפונקציה של זמן:**\n"
                "$$v_x(t) = v_{0x} \\quad \\text{(קבוע)}, \\quad v_y(t) = v_{0y} - gt$$\n\n"
                "**שיגור אופקי** ($\\theta = 0°$): $v_{0x} = v_0$, $v_{0y} = 0$.\n\n"
                "**תוצאות מפתח על קרקע שטוחה** (שיגור ונחיתה באותו גובה):\n"
                "- זמן טיסה: $T = \\dfrac{2v_{0y}}{g}$\n"
                "- טווח: $R = \\dfrac{v_0^2\\sin 2\\theta}{g}$ (מקסימום ב-$\\theta = 45°$)\n"
                "- גובה מקסימלי: $H = \\dfrac{v_{0y}^2}{2g}$\n\n"
                "**מהירות בכל נקודה:** $|v| = \\sqrt{v_x^2 + v_y^2}$. "
                "**כיוון:** $\\alpha = \\arctan(v_y / v_x)$ נמדד מהאופקי.\n\n"
                "**תאוצה:** לאורך כל הטיסה, $a_x = 0$ ו-$a_y = -g$ — כוח הכבידה לעולם "
                "לא פועל אופקית. לכן ניתן לטפל בשני הצירים בנפרד בבעיות בגרות."
            ),
        },
        "theory": {
            "en": (
                "Bagrut projectile problems fall into two main types. Recognizing which type you "
                "face is the first step — using the wrong time formula is the most common error.\n\n"
                "**Type 1 — Horizontal launch from height $h$:**\n"
                "The object is thrown purely horizontally: $v_{0y} = 0$, $v_{0x} = v_0$.\n"
                "- Vertical motion: free fall from rest → $h = \\frac{1}{2}gt^2$ → $t = \\sqrt{2h/g}$.\n"
                "- Horizontal range: $x = v_0 \\cdot t$ (same time $t$ for both axes!).\n"
                "- Landing speed: first find $v_y = gt$, then $|v| = \\sqrt{v_0^2 + v_y^2}$.\n\n"
                "**Type 2 — Angled launch from level ground:**\n"
                "Initial components: $v_{0y} = v_0\\sin\\theta$, $v_{0x} = v_0\\cos\\theta$.\n"
                "- Time to max height: $t_{\\text{up}} = v_{0y}/g$.\n"
                "- Total flight time: $T = 2t_{\\text{up}} = 2v_{0y}/g$ (symmetric trajectory).\n"
                "- Max height: $H = v_{0y}^2/(2g)$.\n"
                "- Range: $R = v_{0x} \\cdot T$ or $R = v_0^2\\sin 2\\theta / g$.\n\n"
                "**At any point in flight:**\n"
                "$|v| = \\sqrt{v_x^2 + v_y^2}$, direction $\\alpha = \\arctan(v_y/v_x)$.\n\n"
                "**Complementary angles:** $\\theta$ and $90° - \\theta$ give the same range "
                "because $\\sin(2\\theta) = \\sin(180° - 2\\theta)$.\n\n"
                "**Choosing a strategy:** List your givens (height? angle? range? speed?) and "
                "match them to Type 1 or Type 2 before substituting numbers. Mixing formulas "
                "from different types is the fastest path to a wrong answer on exam day."
            ),
            "he": (
                "בעיות קליע בבגרות נחלקות לשני סוגים עיקריים. זיהוי הסוג הוא הצעד הראשון — "
                "שימוש בנוסחת זמן שגויה הוא הטעות הנפוצה ביותר.\n\n"
                "**סוג 1 — שיגור אופקי מגובה $h$:**\n"
                "הגוף נזרק אופקית בלבד: $v_{0y} = 0$, $v_{0x} = v_0$.\n"
                "- תנועה אנכית: נפילה חופשית ממנוחה → $h = \\frac{1}{2}gt^2$ → $t = \\sqrt{2h/g}$.\n"
                "- טווח אופקי: $x = v_0 \\cdot t$ (אותו $t$ לשני הצירים!).\n"
                "- מהירות נחיתה: קודם $v_y = gt$, ואז $|v| = \\sqrt{v_0^2 + v_y^2}$.\n\n"
                "**סוג 2 — שיגור זוויתי מקרקע שטוחה:**\n"
                "רכיבים התחלתיים: $v_{0y} = v_0\\sin\\theta$, $v_{0x} = v_0\\cos\\theta$.\n"
                "- זמן עד גובה מקסימלי: $t_{\\text{up}} = v_{0y}/g$.\n"
                "- זמן טיסה כולל: $T = 2t_{\\text{up}} = 2v_{0y}/g$ (מסלול סימטרי).\n"
                "- גובה מקסימלי: $H = v_{0y}^2/(2g)$.\n"
                "- טווח: $R = v_{0x} \\cdot T$ או $R = v_0^2\\sin 2\\theta / g$.\n\n"
                "**בכל נקודה בטיסה:**\n"
                "$|v| = \\sqrt{v_x^2 + v_y^2}$, כיוון $\\alpha = \\arctan(v_y/v_x)$.\n\n"
                "**זוויות משלימות:** $\\theta$ ו-$90° - \\theta$ נותנות אותו טווח "
                "כי $\\sin(2\\theta) = \\sin(180° - 2\\theta)$.\n\n"
                "**בחירת אסטרטגיה:** רשמו את הנתונים (גובה? זווית? טווח? מהירות?) "
                "והתאימו לסוג 1 או 2 לפני הצבת מספרים. ערבוב נוסחאות מסוגים שונים "
                "הוא הדרך המהירה לתשובה שגויה ביום הבחינה."
            ),
        },
    }

    worked_examples = {
        1: {
            "en": (
                "**A ball is thrown horizontally** at $v_0 = 15$ m/s from a cliff $h = 20$ m high. "
                "Find the time to ground, horizontal range, and landing speed.\n\n"
                "This is Type 1: horizontal launch. The vertical motion determines time; "
                "horizontal motion determines range. The initial vertical velocity is zero, "
                "so the ball falls exactly as if dropped from rest at height $h$.\n\n"
                "### Move 1 — Time to ground\n"
                "With $v_{0y} = 0$, free fall gives (note: horizontal speed does not enter this step):\n"
                "$$h = \\tfrac{1}{2}gt^2 \\Rightarrow t = \\sqrt{\\tfrac{2h}{g}} = \\sqrt{\\tfrac{2 \\times 20}{9.8}} \\approx 2.02\\text{ s}$$\n\n"
                "### Move 2 — Horizontal range\n"
                "$$x = v_0 \\cdot t = 15 \\times 2.02 = 30.3\\text{ m}$$\n\n"
                "### Move 3 — Landing speed\n"
                "Vertical component at impact: $v_y = gt = 9.8 \\times 2.02 = 19.8$ m/s.\n"
                "$$|v| = \\sqrt{15^2 + 19.8^2} = \\sqrt{225 + 392} = \\sqrt{617} \\approx 24.8\\text{ m/s}$$\n\n"
                "### Move 4 — Direction at impact\n"
                "The landing angle below horizontal: $\\alpha = \\arctan(19.8/15) \\approx 52.8°$.\n\n"
                "**Answer:** $t \\approx 2.02$ s, $x \\approx 30.3$ m, $|v| \\approx 24.8$ m/s.\n\n"
                "**Bagrut note:** The landing speed exceeds $v_0 = 15$ m/s because gravity adds "
                "a downward vertical component. Always combine both components with Pythagoras.\n\n"
                "**Physical picture:** While the ball travels horizontally at 15 m/s, gravity "
                "continuously accelerates it downward. At impact, the velocity vector points "
                "below the horizontal — typical of cliff-drop problems on Bagrut questionnaire 1. "
                "Compare the landing speed $24.8$ m/s to the launch speed $15$ m/s to see gravity's effect."
            ),
            "he": (
                "**כדור נזרק אופקית** במהירות $v_0 = 15$ m/s מצוק בגובה $h = 20$ m. "
                "מצאו זמן עד קרקע, טווח אופקי, ומהירות נחיתה.\n\n"
                "זה סוג 1: שיגור אופקי. התנועה האנכית קובעת את הזמן; "
                "התנועה האופקית קובעת את הטווח. המהירות האנכית ההתחלתית אפס, "
                "ולכן הכדור נופל בדיוק כאילו נשחרר ממנוחה מגובה $h$.\n\n"
                "### צעד 1 — זמן עד קרקע\n"
                "עם $v_{0y} = 0$, נפילה חופשית נותנת (שימו לב: המהירות האופקית לא נכנסת לשלב זה):\n"
                "$$h = \\tfrac{1}{2}gt^2 \\Rightarrow t = \\sqrt{\\tfrac{2h}{g}} = \\sqrt{\\tfrac{2 \\times 20}{9.8}} \\approx 2.02\\text{ s}$$\n\n"
                "### צעד 2 — טווח אופקי\n"
                "$$x = v_0 \\cdot t = 15 \\times 2.02 = 30.3\\text{ m}$$\n\n"
                "### צעד 3 — מהירות נחיתה\n"
                "רכיב אנכי בפגיעה: $v_y = gt = 9.8 \\times 2.02 = 19.8$ m/s.\n"
                "$$|v| = \\sqrt{15^2 + 19.8^2} = \\sqrt{225 + 392} = \\sqrt{617} \\approx 24.8\\text{ m/s}$$\n\n"
                "### צעד 4 — כיוון בפגיעה\n"
                "זווית הנחיתה מתחת לאופקי: $\\alpha = \\arctan(19.8/15) \\approx 52.8°$.\n\n"
                "**תשובה:** $t \\approx 2.02$ s, $x \\approx 30.3$ m, $|v| \\approx 24.8$ m/s.\n\n"
                "**הערת בגרות:** מהירות הנחיתה גדולה מ-$v_0 = 15$ m/s כי כוח הכבידה מוסיף "
                "רכיב אנכי כלפי מטה. תמיד שלבו שני רכיבים בפיתגורס.\n\n"
                "**תמונה פיזיקלית:** בזמן שהכדור נע אופקית ב-15 m/s, כוח הכבידה "
                "מאיץ אותו כלפי מטה. בפגיעה, וקטור המהירות פונה מתחת לאופקי — "
                "טיפוסי לבעיות נפילה מצוק בשאלון 1 בבגרות. "
                "השוו את מהירות הנחיתה $24.8$ m/s למהירות השיגור $15$ m/s כדי לראות את השפעת הכבידה."
            ),
        },
        2: {
            "en": (
                "**A ball is kicked** at $v_0 = 20$ m/s at $\\theta = 30°$ from level ground. "
                "Find maximum height, time of flight, and range.\n\n"
                "This is Type 2: angled launch from level ground. The trajectory is symmetric — "
                "time going up equals time coming down. Decompose first, then apply the standard formulas.\n\n"
                "### Move 1 — Decompose initial velocity\n"
                "$$v_{0x} = 20\\cos 30° = 17.3\\text{ m/s}, \\quad v_{0y} = 20\\sin 30° = 10\\text{ m/s}$$\n\n"
                "### Move 2 — Maximum height\n"
                "At the top, $v_y = 0$. Using energy or kinematics:\n"
                "$$H = \\frac{v_{0y}^2}{2g} = \\frac{100}{19.6} \\approx 5.1\\text{ m}$$\n\n"
                "### Move 3 — Time of flight\n"
                "Total flight time is twice the time to reach max height:\n"
                "$$T = \\frac{2v_{0y}}{g} = \\frac{20}{9.8} \\approx 2.04\\text{ s}$$\n\n"
                "### Move 4 — Range\n"
                "$$R = v_{0x} \\cdot T = 17.3 \\times 2.04 \\approx 35.3\\text{ m}$$\n\n"
                "**Alternative range check:** $R = v_0^2\\sin 60°/g = 400 \\times 0.866/9.8 \\approx 35.3$ m ✓.\n\n"
                "### Move 5 — Speed at max height\n"
                "At the apex, $v_y = 0$ and speed equals $|v_x| = 17.3$ m/s — not zero!\n\n"
                "**Answer:** $H \\approx 5.1$ m, $T \\approx 2.04$ s, $R \\approx 35.3$ m.\n\n"
                "**Physical reading:** At $30°$, the horizontal component dominates ($v_{0x} > v_{0y}$), "
                "so the range is larger than the max height — a flatter trajectory than at $60°$. "
                "Notice that $R \\approx 7H$, confirming the ball travels much farther horizontally than it rises.\n\n"
                "**Bagrut strategy:** For angled launch, always compute $v_{0x}$ and $v_{0y}$ first. "
                "Write them in a box on your scratch paper before touching $H$, $T$, or $R$."
            ),
            "he": (
                "**כדור נבעט** במהירות $v_0 = 20$ m/s בזווית $\\theta = 30°$ מקרקע שטוחה. "
                "מצאו גובה מקסימלי, זמן טיסה, וטווח.\n\n"
                "זה סוג 2: שיגור זוויתי מקרקע שטוחה. המסלול סימטרי — "
                "זמן העלייה שווה לזמן הירידה. פרקו קודם, ואז יישמו את הנוסחאות הסטנדרטיות.\n\n"
                "### צעד 1 — פירוק מהירות התחלתית\n"
                "$$v_{0x} = 20\\cos 30° = 17.3\\text{ m/s}, \\quad v_{0y} = 20\\sin 30° = 10\\text{ m/s}$$\n\n"
                "### צעד 2 — גובה מקסימלי\n"
                "בראש, $v_y = 0$. באמצעות אנרגיה או קינמטיקה:\n"
                "$$H = \\frac{v_{0y}^2}{2g} = \\frac{100}{19.6} \\approx 5.1\\text{ m}$$\n\n"
                "### צעד 3 — זמן טיסה\n"
                "זמן הטיסה הכולל הוא פי שניים מזמן ההגעה לגובה מקסימלי:\n"
                "$$T = \\frac{2v_{0y}}{g} = \\frac{20}{9.8} \\approx 2.04\\text{ s}$$\n\n"
                "### צעד 4 — טווח\n"
                "$$R = v_{0x} \\cdot T = 17.3 \\times 2.04 \\approx 35.3\\text{ m}$$\n\n"
                "**בדיקת טווח חלופית:** $R = v_0^2\\sin 60°/g = 400 \\times 0.866/9.8 \\approx 35.3$ m ✓.\n\n"
                "### צעד 5 — מהירות בגובה מקסימלי\n"
                "בראש, $v_y = 0$ והמהירות שווה ל-$|v_x| = 17.3$ m/s — לא אפס!\n\n"
                "**תשובה:** $H \\approx 5.1$ m, $T \\approx 2.04$ s, $R \\approx 35.3$ m.\n\n"
                "**קריאה פיזיקלית:** ב-$30°$, הרכיב האופקי דומיננטי ($v_{0x} > v_{0y}$), "
                "ולכן הטווח גדול מהגובה המקסימלי — מסלול שטוח יותר מאשר ב-$60°$. "
                "שימו לב ש-$R \\approx 7H$, מאשר שהכדור נוסע הרבה יותר רחוק אופקית מאשר שהוא עולה.\n\n"
                "**אסטרטגיית בגרות:** בשיגור זוויתי, תמיד חשבו $v_{0x}$ ו-$v_{0y}$ קודם. "
                "כתבו אותם בתיבה על דף הטיוטה לפני שמתחילים ב-$H$, $T$ או $R$."
            ),
        },
        3: {
            "en": (
                "**A ball must reach a target 80 m away.** Initial speed $v_0 = 30$ m/s. "
                "Find the launch angle(s).\n\n"
                "When range and speed are given, the range formula inverts directly to find $\\theta$.\n\n"
                "### Move 1 — Apply range formula\n"
                "$$R = \\frac{v_0^2\\sin 2\\theta}{g} \\Rightarrow \\sin 2\\theta = \\frac{Rg}{v_0^2} = \\frac{80 \\times 9.8}{900} = \\frac{784}{900} = 0.871$$\n\n"
                "### Move 2 — Find $2\\theta$\n"
                "$$2\\theta = \\arcsin(0.871) \\approx 60.5° \\text{ or } 119.5°$$\n\n"
                "### Move 3 — Two launch angles\n"
                "$$\\theta_1 \\approx 30.3° \\quad \\text{and} \\quad \\theta_2 \\approx 59.7°$$\n\n"
                "### Move 4 — Interpret the two solutions\n"
                "Both angles hit the same target 80 m away. The $30.3°$ launch is flatter and faster "
                "horizontally; the $59.7°$ launch is steeper with more time in the air.\n\n"
                "**Why two solutions?** Complementary angles ($\\theta$ and $90° - \\theta$) "
                "produce the same $\\sin 2\\theta$ value, hence the same range.\n\n"
                "**Answer:** $\\theta \\approx 30.3°$ or $\\theta \\approx 59.7°$.\n\n"
                "**Exam tip:** Always check both roots of $\\sin 2\\theta$. The lower angle "
                "gives a flatter trajectory; the higher angle gives a steeper arc — same landing point.\n\n"
                "**Verification:** Substitute $\\theta = 30.3°$ back: "
                "$\\sin(60.6°) \\approx 0.871$ ✓. Both angles are physically valid launch directions."
            ),
            "he": (
                "**כדור חייב להגיע ליעד במרחק 80 m.** מהירות התחלתית $v_0 = 30$ m/s. "
                "מצאו את זוויות השיגור.\n\n"
                "כשניתנים טווח ומהירות, נוסחת הטווח מתהפכת ישירות למציאת $\\theta$.\n\n"
                "### צעד 1 — יישום נוסחת הטווח\n"
                "$$R = \\frac{v_0^2\\sin 2\\theta}{g} \\Rightarrow \\sin 2\\theta = \\frac{Rg}{v_0^2} = \\frac{80 \\times 9.8}{900} = \\frac{784}{900} = 0.871$$\n\n"
                "### צעד 2 — מציאת $2\\theta$\n"
                "$$2\\theta = \\arcsin(0.871) \\approx 60.5° \\text{ או } 119.5°$$\n\n"
                "### צעד 3 — שתי זוויות שיגור\n"
                "$$\\theta_1 \\approx 30.3° \\quad \\text{ו-} \\quad \\theta_2 \\approx 59.7°$$\n\n"
                "### צעד 4 — פרשנות שתי התשובות\n"
                "שתי הזוויות פוגעות באותו יעד במרחק 80 m. שיגור $30.3°$ שטוח ומהיר יותר אופקית; "
                "שיגור $59.7°$ תלול יותר עם יותר זמן באוויר.\n\n"
                "**למה שתי תשובות?** זוויות משלימות ($\\theta$ ו-$90° - \\theta$) "
                "מייצרות אותו ערך $\\sin 2\\theta$, ולכן אותו טווח.\n\n"
                "**תשובה:** $\\theta \\approx 30.3°$ או $\\theta \\approx 59.7°$.\n\n"
                "**טיפ לבחינה:** תמיד בדקו את שני השורשים של $\\sin 2\\theta$. "
                "הזווית הנמוכה נותנת מסלול שטוח יותר; הגבוהה — קשת תלולה יותר — אותה נקודת נחיתה.\n\n"
                "**אימות:** הציבו $\\theta = 30.3°$ בחזרה: "
                "$\\sin(60.6°) \\approx 0.871$ ✓. שתי הזוויות הן כיווני שיגור פיזיקליים תקינים."
            ),
        },
    }

    checkpoint_solutions = {
        1: {
            "en": (
                "This is a horizontal launch from height $h = 45$ m at $v_0 = 10$ m/s.\n\n"
                "**Step 1 — Time to ground:** Vertical free fall from rest:\n"
                "$$t = \\sqrt{\\frac{2h}{g}} = \\sqrt{\\frac{2 \\times 45}{9.8}} = \\sqrt{\\frac{90}{9.8}} \\approx 3.03\\text{ s}$$\n\n"
                "**Step 2 — Range:** Use the same time for horizontal motion:\n"
                "$$x = v_0 \\cdot t = 10 \\times 3.03 \\approx 30.3\\text{ m}$$\n\n"
                "**Check:** The horizontal speed does not affect fall time. Doubling $v_0$ would "
                "double the range but leave $t$ unchanged."
            ),
            "he": (
                "זהו שיגור אופקי מגובה $h = 45$ m במהירות $v_0 = 10$ m/s.\n\n"
                "**שלב 1 — זמן עד קרקע:** נפילה חופשית אנכית ממנוחה:\n"
                "$$t = \\sqrt{\\frac{2h}{g}} = \\sqrt{\\frac{2 \\times 45}{9.8}} = \\sqrt{\\frac{90}{9.8}} \\approx 3.03\\text{ s}$$\n\n"
                "**שלב 2 — טווח:** אותו זמן לתנועה אופקית:\n"
                "$$x = v_0 \\cdot t = 10 \\times 3.03 \\approx 30.3\\text{ m}$$\n\n"
                "**בדיקה:** המהירות האופקית לא משפיעה על זמן הנפילה. "
                "הכפלת $v_0$ תכפיל את הטווח אך לא תשנה את $t$."
            ),
        },
        2: {
            "en": (
                "Angled launch at $v_0 = 25$ m/s, $\\theta = 60°$. Find maximum height.\n\n"
                "**Step 1 — Vertical component:**\n"
                "$$v_{0y} = 25\\sin 60° = 25 \\times \\frac{\\sqrt{3}}{2} \\approx 21.65\\text{ m/s}$$\n\n"
                "**Step 2 — Maximum height:**\n"
                "$$H = \\frac{v_{0y}^2}{2g} = \\frac{21.65^2}{2 \\times 9.8} = \\frac{468.7}{19.6} \\approx 23.9\\text{ m}$$\n\n"
                "**Check:** At $60°$, most of the initial speed goes vertical ($v_{0y} > v_{0x}$), "
                "so $H$ is large relative to range."
            ),
            "he": (
                "שיגור זוויתי ב-$v_0 = 25$ m/s, $\\theta = 60°$. מצאו גובה מקסימלי.\n\n"
                "**שלב 1 — רכיב אנכי:**\n"
                "$$v_{0y} = 25\\sin 60° = 25 \\times \\frac{\\sqrt{3}}{2} \\approx 21.65\\text{ m/s}$$\n\n"
                "**שלב 2 — גובה מקסימלי:**\n"
                "$$H = \\frac{v_{0y}^2}{2g} = \\frac{21.65^2}{2 \\times 9.8} = \\frac{468.7}{19.6} \\approx 23.9\\text{ m}$$\n\n"
                "**בדיקה:** ב-$60°$, רוב המהירות ההתחלתית הולכת לאנכי ($v_{0y} > v_{0x}$), "
                "ולכן $H$ גדול יחסית לטווח."
            ),
        },
    }

    other_sections = {
        "method_guide": {
            "en": (
                "| Problem type | Step 1 | Step 2 | Step 3 | Step 4 |\n"
                "|---|---|---|---|---|\n"
                "| Horizontal from height $h$ | $t = \\sqrt{2h/g}$ | $x = v_0 t$ | $v_y = gt$ | $|v| = \\sqrt{v_0^2 + v_y^2}$ |\n"
                "| Angled from ground | $v_{0x}, v_{0y}$ | $H = v_{0y}^2/(2g)$ | $T = 2v_{0y}/g$ | $R = v_{0x} T$ |\n"
                "| Find angle for range | $\\sin 2\\theta = Rg/v_0^2$ | $2\\theta = \\arcsin(...)$ | Two angles | Check both roots |\n\n"
                "**Decision tree:**\n"
                "1. Is the launch horizontal ($\\theta = 0°$ from a height)? → Use row 1.\n"
                "2. Is it angled from level ground? → Use row 2.\n"
                "3. Given range and speed, need angle? → Use row 3.\n\n"
                "**Maximum range:** $\\theta = 45°$ gives $R_{\\max} = v_0^2/g$.\n\n"
                "**At any time $t$:** $v_y = v_{0y} - gt$, $v_x = v_{0x}$ (constant).\n\n"
                "**Tip:** Write $v_{0x}$ and $v_{0y}$ in a box before any calculation."
            ),
            "he": (
                "| סוג בעיה | שלב 1 | שלב 2 | שלב 3 | שלב 4 |\n"
                "|---|---|---|---|---|\n"
                "| אופקי מגובה $h$ | $t = \\sqrt{2h/g}$ | $x = v_0 t$ | $v_y = gt$ | $|v| = \\sqrt{v_0^2 + v_y^2}$ |\n"
                "| זוויתי מקרקע | $v_{0x}, v_{0y}$ | $H = v_{0y}^2/(2g)$ | $T = 2v_{0y}/g$ | $R = v_{0x} T$ |\n"
                "| מציאת זווית לטווח | $\\sin 2\\theta = Rg/v_0^2$ | $2\\theta = \\arcsin(...)$ | שתי זוויות | בדקו שני שורשים |\n\n"
                "**עץ החלטות:**\n"
                "1. השיגור אופקי ($\\theta = 0°$ מגובה)? → שורה 1.\n"
                "2. זוויתי מקרקע שטוחה? → שורה 2.\n"
                "3. ניתנים טווח ומהירות, צריך זווית? → שורה 3.\n\n"
                "**טווח מקסימלי:** $\\theta = 45°$ נותן $R_{\\max} = v_0^2/g$.\n\n"
                "**בכל זמן $t$:** $v_y = v_{0y} - gt$, $v_x = v_{0x}$ (קבוע).\n\n"
                "**טיפ:** כתבו $v_{0x}$ ו-$v_{0y}$ בתיבה לפני כל חישוב."
            ),
        },
        "pitfall": {
            "en": (
                "Projectile motion has several traps that catch even strong students on Bagrut exams.\n\n"
                "1. **Mixing $x$ and $y$ components:** $v_x$ is always constant; only $v_y$ changes "
                "due to gravity. Never use $v_y$ in a horizontal distance formula or $v_x$ in a "
                "vertical height formula.\n\n"
                "2. **Using $g = 9.8$ vs $10$ m/s²:** Check which value the exam specifies. "
                "Mixing them mid-problem causes wrong answers.\n\n"
                "3. **At max height, speed $\\neq 0$:** Only $v_y = 0$ at the apex. "
                "$v_x$ remains unchanged, so $|v| = |v_x| > 0$ for any angled launch.\n\n"
                "4. **Wrong time formula:** For horizontal launch use $t = \\sqrt{2h/g}$. "
                "For angled launch returning to same height, use $T = 2v_{0y}/g$ — not $v_{0y}/g$ "
                "(that is only time to the top).\n\n"
                "**Example misconception:** \"At the highest point, speed is zero.\"\n\n"
                "**Fix:** Only $v_y = 0$. The horizontal component $v_x$ never changes."
            ),
            "he": (
                "לתנועת קליע יש מלכודות שתופסות גם תלמידים חזקים בבחינות בגרות.\n\n"
                "1. **ערבוב רכיבי $x$ ו-$y$:** $v_x$ תמיד קבוע; רק $v_y$ משתנה בגלל כוח הכבידה. "
                "לעולם לא משתמשים ב-$v_y$ בנוסחת מרחק אופקי או ב-$v_x$ בנוסחת גובה אנכי.\n\n"
                "2. **שימוש ב-$g = 9.8$ מול $10$ m/s²:** בדקו איזה ערך הבחינה מציינת. "
                "ערבוב באמצע בעיה גורם לתשובות שגויות.\n\n"
                "3. **בגובה מקסימלי, מהירות $\\neq 0$:** רק $v_y = 0$ בראש. "
                "$v_x$ ללא שינוי, ולכן $|v| = |v_x| > 0$ לכל שיגור בזווית.\n\n"
                "4. **נוסחת זמן שגויה:** לשיגור אופקי $t = \\sqrt{2h/g}$. "
                "לשיגור זוויתי שחוזר לאותו גובה, $T = 2v_{0y}/g$ — לא $v_{0y}/g$ "
                "(זה רק זמן עד הראש).\n\n"
                "**דוגמת טעות:** \"בנקודת השיא, המהירות אפס.\"\n\n"
                "**תיקון:** רק $v_y = 0$. הרכיב האופקי $v_x$ לא משתנה."
            ),
        },
        "why_matters": {
            "en": (
                "Projectile motion is not an isolated topic — it is the first major application of "
                "two-dimensional kinematics and connects directly to vectors, trigonometry, and "
                "later topics like circular motion and work-energy.\n\n"
                "**Builds on:**\n"
                "- `concept:vectors_2d` **Vectors in the Plane** — decomposing velocity into components.\n"
                "- `concept:trigonometry_ratios` **Trigonometry in Right Triangle** — sine and cosine of launch angle.\n\n"
                "**Why it matters for exams:** Bagrut and university courses reward *transfer* — applying "
                "this idea in a new context. When you study, always ask: \"Where else did I see this pattern?\" "
                "Projectile problems also train you to separate independent motions — a skill used in "
                "electromagnetism, waves, and relative motion."
            ),
            "he": (
                "תנועת קליע אינה נושא מבודד — היא היישום המרכזי הראשון של קינמטיקה דו-ממדית "
                "ומתחברת ישירות לוקטורים, טריגונומטריה, ונושאים מאוחרים כמו תנועה מעגלית ועבודה-אנרגיה.\n\n"
                "**מבוסס על:**\n"
                "- `concept:vectors_2d` **וקטורים במישור** — פירוק מהירות לרכיבים.\n"
                "- `concept:trigonometry_ratios` **טריגונומטריה במשולש ישר זווית** — sin ו-cos של זווית שיגור.\n\n"
                "**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — יישום הרעיון בהקשר חדש. "
                "בזמן לימוד, שאלו תמיד: \"איפה עוד ראיתי את הדפוס הזה?\" "
                "בעיות קליע גם מאמנות אתכם להפריד תנועות עצמאיות — מיומנות בשימוש "
                "באלקטרומגנטיות, גלים, ותנועה יחסית."
            ),
        },
        "before_exam": {
            "en": (
                "Before your Bagrut exam, review these projectile motion essentials:\n\n"
                "- **Always separate $x$ and $y$** — write two columns on your scratch paper.\n"
                "- Horizontal: $x = v_{0x} t$ with constant $v_x = v_{0x}$.\n"
                "- Vertical: $v_y = v_{0y} - gt$, $y = v_{0y} t - \\frac{1}{2}gt^2$.\n"
                "- At the top of the trajectory: $v_y = 0$ (not $v = 0$!).\n"
                "- Horizontal from height: $t = \\sqrt{2h/g}$, then $x = v_0 t$.\n"
                "- Angled from ground: $H = v_{0y}^2/(2g)$, $T = 2v_{0y}/g$, $R = v_{0x} T$.\n"
                "- Maximum range at $\\theta = 45°$: $R_{\\max} = v_0^2/g$.\n\n"
                "**Last review:** Say each formula out loud once, then solve one checkpoint "
                "without looking at your notes."
            ),
            "he": (
                "לפני בחינת הבגרות, חזרו על יסודות תנועת הקליע:\n\n"
                "- **תמיד הפרידו $x$ ו-$y$** — כתבו שתי עמודות על דף הטיוטה.\n"
                "- אופקי: $x = v_{0x} t$ עם $v_x = v_{0x}$ קבוע.\n"
                "- אנכי: $v_y = v_{0y} - gt$, $y = v_{0y} t - \\frac{1}{2}gt^2$.\n"
                "- בראש המסלול: $v_y = 0$ (לא $v = 0$!).\n"
                "- אופקי מגובה: $t = \\sqrt{2h/g}$, ואז $x = v_0 t$.\n"
                "- זוויתי מקרקע: $H = v_{0y}^2/(2g)$, $T = 2v_{0y}/g$, $R = v_{0x} T$.\n"
                "- טווח מקסימלי ב-$\\theta = 45°$: $R_{\\max} = v_0^2/g$.\n\n"
                "**חזרה אחרונה:** אמרו כל נוסחה בקול פעם אחת, ואז פתרו checkpoint "
                "אחד בלי להסתכל בהערות."
            ),
        },
        "summary": {
            "en": (
                "Projectile motion combines independent horizontal and vertical motions:\n\n"
                "- $v_x$ stays constant; $v_y$ changes at $a_y = -g = -9.8$ m/s².\n"
                "- **Horizontal launch:** $t = \\sqrt{2h/g}$, range $= v_0 t$, landing speed "
                "via Pythagoras.\n"
                "- **Angled launch:** $H = v_{0y}^2/(2g)$, $T = 2v_{0y}/g$, $R = v_{0x} T$.\n"
                "- At maximum height: $v_y = 0$, but $v_x$ (and speed) remain nonzero.\n"
                "- Complementary angles give equal range; maximum at $45°$.\n\n"
                "**Takeaway:** Identify the problem type first, decompose $v_0$ into components, "
                "then apply the matching formula row — never mix axes."
            ),
            "he": (
                "תנועת קליע משלבת תנועות אופקיות ואנכיות עצמאיות:\n\n"
                "- $v_x$ נשאר קבוע; $v_y$ משתנה ב-$a_y = -g = -9.8$ m/s².\n"
                "- **שיגור אופקי:** $t = \\sqrt{2h/g}$, טווח $= v_0 t$, מהירות נחיתה "
                "בפיתגורס.\n"
                "- **שיגור זוויתי:** $H = v_{0y}^2/(2g)$, $T = 2v_{0y}/g$, $R = v_{0x} T$.\n"
                "- בגובה מקסימלי: $v_y = 0$, אך $v_x$ (והמהירות) נשארים שונים מאפס.\n"
                "- זוויות משלימות נותנות טווח שווה; מקסימום ב-$45°$.\n\n"
                "**מסקנה:** זהו קודם את סוג הבעיה, פרקו $v_0$ לרכיבים, "
                "ואז יישמו את שורת הנוסחאות המתאימה — לעולם לא ערבבו צירים."
            ),
        },
    }

    ex_num = 0
    cp_num = 0
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        if kind in section_bodies:
            sec["body_en_md"] = section_bodies[kind]["en"]
            sec["body_he_md"] = section_bodies[kind]["he"]
        elif kind == "worked_example":
            ex_num += 1
            sec["body_en_md"] = worked_examples[ex_num]["en"]
            sec["body_he_md"] = worked_examples[ex_num]["he"]
        elif kind == "checkpoint":
            cp_num += 1
            sec["checkpoint_solution_en"] = checkpoint_solutions[cp_num]["en"]
            sec["checkpoint_solution_he"] = checkpoint_solutions[cp_num]["he"]
        elif kind in other_sections:
            sec["body_en_md"] = other_sections[kind]["en"]
            sec["body_he_md"] = other_sections[kind]["he"]

    for q in lesson["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]

    return lesson


def validate(lesson):
    errors = []
    ex_num = 0
    for sec in lesson["sections"]:
        kind = sec.get("kind")
        key = "worked_example" if kind == "worked_example" else kind
        if key in MIN_WORDS:
            for lang, field in [("en", "body_en_md"), ("he", "body_he_md")]:
                wc = word_count(sec.get(field, ""))
                mn = MIN_WORDS[key][lang]
                if wc < mn:
                    errors.append(f"{kind} {field}: {wc} < {mn}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                errors.append(f"{kind}: weak Hebrew body")

    for q in lesson["questions"]:
        for lang, field in [("en", "explanation_en"), ("he", "explanation_he")]:
            wc = word_count(q.get(field, ""))
            if wc < 80 or wc > 150:
                errors.append(f"Q{q['ord']} {field}: {wc} words (need 80-150)")

    return errors


def main():
    lesson = build_lesson()
    errors = validate(lesson)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")
    print("All depth gates passed.")


if __name__ == "__main__":
    main()
