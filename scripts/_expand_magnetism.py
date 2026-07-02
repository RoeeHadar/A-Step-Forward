#!/usr/bin/env python3
"""Generate expanded magnetism.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/magnetism.json"

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
            "Unlike electric forces, which act on **any** charge, a magnetic field exerts a force "
            "only on **moving** charges — or equivalently, on current-carrying wires. A stationary "
            "charge sitting in a uniform $\\vec{B}$ field feels **nothing**. Set it in motion, and "
            "the field pushes it sideways: this is the **Lorentz force**, the foundation of "
            "magnetism in Bagrut physics.\n\n"
            "The force is always **perpendicular** to both the velocity $\\vec{v}$ (or current "
            "direction) and the field $\\vec{B}$. That geometry explains why charged particles "
            "curve into circles, why motors spin, and why magnetic forces never change kinetic "
            "energy directly.\n\n"
            "**Applications you should know for Bagrut 5 units:** electric motors and generators, "
            "MRI scanners, mass spectrometers, particle accelerators (cyclotrons), Earth's auroras, "
            "and the force between parallel current-carrying wires. Exam questions focus on "
            "$F=qvB\\sin\\theta$ for moving charges and $F=BIL\\sin\\theta$ for wires, plus "
            "circular-orbit radius $r=mv/(qB)$. This lesson builds on `concept:vectors_basics` "
            "and connects forward to `concept:electromagnetic_induction`."
        ),
        "body_he_md": (
            "בניגוד לכוחות חשמליים שפועלים על **כל** מטען, שדה מגנטי מפעיל כוח רק על מטענים "
            "**נעים** — או, באופן שקול, על מוליכים עם זרם. מטען נייח בשדה $\\vec{B}$ אחיד "
            "לא מרגיש **כלום**. כשמניעים אותו, השדה דוחף אותו לצד: זהו **כוח לורנץ**, "
            "יסוד המגנטיות בבגרות בפיזיקה.\n\n"
            "הכוח תמיד **ניצב** גם למהירות $\\vec{v}$ (או לכיוון הזרם) וגם לשדה $\\vec{B}$. "
            "הגאומטריה הזו מסבירה מדוע חלקיקים טעונים נכנסים למסלול מעגלי, מדוע מנועים "
            "מסתובבים, ומדוע כוח מגנטי לא משנה ישירות אנרגיה קינטית.\n\n"
            "**יישומים לבגרות 5 יחידות:** מנועים חשמליים וגנרטורים, MRI, ספקטרומטרי מסה, "
            "מאיצי חלקיקים (ציקלוטרונים), זוהר הקוטב, והכוח בין חוטים מקבילים עם זרם. "
            "שאלות בבחינה מתמקדות ב-$F=qvB\\sin\\theta$ למטענים נעים וב-$F=BIL\\sin\\theta$ "
            "לחוטים, וברדיוס מסלול מעגלי $r=mv/(qB)$. שיעור זה מבוסס על "
            "`concept:vectors_basics` ומוביל ל-`concept:electromagnetic_induction`."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Force on a moving point charge (Lorentz force):**\n"
            "$$\\vec{F}=q\\vec{v}\\times\\vec{B} \\quad \\Rightarrow \\quad |F|=qvB\\sin\\theta$$\n\n"
            "Where $\\theta$ is the angle between $\\vec{v}$ and $\\vec{B}$. "
            "Units: $F$ in newtons (N), $q$ in coulombs (C), $v$ in m/s, $B$ in tesla (T). "
            "One tesla is a strong field — MRI uses 1–3 T; Earth's field is about $5\\times10^{-5}$ T.\n\n"
            "**Force on a straight current-carrying conductor:**\n"
            "$$|F|=BIL\\sin\\theta$$\n\n"
            "Where $I$ is current in amperes (A), $L$ is the length of wire inside the field (m), "
            "and $\\theta$ is the angle between the wire and $\\vec{B}$. Only the segment "
            "immersed in the field counts toward $L$.\n\n"
            "**Direction — right-hand rule:**\n"
            "- Point fingers along $\\vec{v}$ (positive charge) or current direction $I$.\n"
            "- Curl fingers toward $\\vec{B}$ (through the smaller angle).\n"
            "- Thumb points in the direction of $\\vec{F}$.\n"
            "- For **negative** charge: reverse the force direction (or use left hand).\n\n"
            "**Key distinction:** Electric force $\\vec{F}_E=q\\vec{E}$ acts on stationary charges; "
            "magnetic force acts only when there is motion perpendicular (or a component "
            "perpendicular) to $\\vec{B}$."
        ),
        "body_he_md": (
            "**כוח על מטען נקודתי נע (כוח לורנץ):**\n"
            "$$\\vec{F}=q\\vec{v}\\times\\vec{B} \\quad \\Rightarrow \\quad |F|=qvB\\sin\\theta$$\n\n"
            "כאשר $\\theta$ הוא הזווית בין $\\vec{v}$ ל-$\\vec{B}$. "
            "יחידות: $F$ בניוטון (N), $q$ בקולomb (C), $v$ ב-m/s, $B$ בטesla (T). "
            "טesla אחד הוא שדה חזק — MRI משתמש ב-1–3 T; שדה כדור הארץ כ-$5\\times10^{-5}$ T.\n\n"
            "**כוח על מוליך ישר עם זרם:**\n"
            "$$|F|=BIL\\sin\\theta$$\n\n"
            "כאשר $I$ הוא זרם באמפר (A), $L$ אורך החוט **בתוך** השדה (m), "
            "ו-$\\theta$ הזווית בין החוט ל-$\\vec{B}$. רק הקטע שנמצא בשדה נספר ל-$L$.\n\n"
            "**כיוון — כלל יד ימין:**\n"
            "- כיוונו את האצבעות לאורך $\\vec{v}$ (מטען חיובי) או כיוון הזרם $I$.\n"
            "- כופפו את האצבעות לכיוון $\\vec{B}$ (דרך הזווית הקטנה).\n"
            "- האגודל מצביע על כיוון $\\vec{F}$.\n"
            "- **מטען שלילי:** הפכו את כיוון הכוח (או השתמשו ביד שמאל).\n\n"
            "**הבחנה חשובה:** כוח חשמלי $\\vec{F}_E=q\\vec{E}$ פועל גם על מטענים נחים; "
            "כוח מגנטי פועל רק כשיש תנועה עם רכיב ניצב ל-$\\vec{B}$."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Circular motion when $\\vec{v}\\perp\\vec{B}$\n\n"
            "When velocity is perpendicular to the field, the Lorentz force magnitude is "
            "$F=qvB$ and always points toward the centre of the circular path — it acts as a "
            "**centripetal force**:\n"
            "$$qvB = \\frac{mv^2}{r} \\quad \\Rightarrow \\quad r=\\frac{mv}{qB}$$\n\n"
            "Heavier particles or faster speeds → larger radius. Stronger field → tighter curve.\n\n"
            "### Period and frequency are speed-independent\n\n"
            "The time for one full orbit is:\n"
            "$$T=\\frac{2\\pi r}{v}=\\frac{2\\pi m}{qB}$$\n\n"
            "Remarkably, $T$ does **not** depend on speed $v$ or radius $r$ — only on $m$, $q$, "
            "and $B$. Cyclotrons exploit this: particles stay in sync with the alternating "
            "electric field as they spiral outward.\n\n"
            "### Magnetic force does no work\n\n"
            "Because $\\vec{F}\\perp\\vec{v}$ at every instant, the dot product "
            "$W=\\vec{F}\\cdot\\vec{d}=0$. Kinetic energy and speed stay constant; only "
            "direction changes. An electric field **can** accelerate charges; a pure magnetic "
            "field **deflects** them.\n\n"
            "### Special angle cases\n"
            "- $\\theta=0°$ or $180°$ (parallel/antiparallel): $\\sin\\theta=0$ → $F=0$.\n"
            "- $\\theta=90°$ (perpendicular): $\\sin\\theta=1$ → maximum force $F=qvB$ or $F=BIL$.\n"
            "- General $\\theta$: only the perpendicular component $v_\\perp=v\\sin\\theta$ "
            "contributes to the force magnitude."
        ),
        "body_he_md": (
            "### תנועה מעגלית כש-$\\vec{v}\\perp\\vec{B}$\n\n"
            "כשהמהירות ניצבת לשדה, גודל כוח לורנץ הוא $F=qvB$ ותמיד מצביע לכיוון "
            "מרכז המסלול — הוא פועל כ**כוח מרכזי**:\n"
            "$$qvB = \\frac{mv^2}{r} \\quad \\Rightarrow \\quad r=\\frac{mv}{qB}$$\n\n"
            "חלקיק כבד יותר או מהירות גבוהה יותר → רדיוס גדול יותר. שדה חזק יותר → עקומה צפופה.\n\n"
            "### מחזור ותדר — לא תלויים במהירות\n\n"
            "זמן הקפה מלאה:\n"
            "$$T=\\frac{2\\pi r}{v}=\\frac{2\\pi m}{qB}$$\n\n"
            "באופן מפתיע, $T$ **לא** תלוי במהירות $v$ או ברדיוס $r$ — רק ב-$m$, $q$ ו-$B$. "
            "ציקלוטרונים מנצלים זאת: חלקיקים נשארים מסונכרנים עם השדה החשמלי המשתנה.\n\n"
            "### כוח מגנטי לא עושה עבודה\n\n"
            "מכיוון ש-$\\vec{F}\\perp\\vec{v}$ בכל רגע, המכפלה הסקalarית "
            "$W=\\vec{F}\\cdot\\vec{d}=0$. אנרגיה קינטית ומהירות נשארות קבועות; "
            "רק הכיוון משתנה. שדה חשמלי **יכול** להאיץ מטענים; שדה מגנטי טהור "
            "**מסיט** אותם.\n\n"
            "### מקרים מיוחדים של זווית\n"
            "- $\\theta=0°$ או $180°$ (מקביל/נגדי): $\\sin\\theta=0$ → $F=0$.\n"
            "- $\\theta=90°$ (ניצב): $\\sin\\theta=1$ → כוח מקסימלי $F=qvB$ או $F=BIL$.\n"
            "- $\\theta$ כללי: רק הרכיב הניצב $v_\\perp=v\\sin\\theta$ תורם לגודל הכוח."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**An electron** ($q=-1.6\\times10^{-19}$ C, magnitude $|q|=1.6\\times10^{-19}$ C) "
            "moves at $v=2\\times10^6$ m/s **perpendicular** to a uniform field $B=0.5$ T. "
            "Find the magnitude of the magnetic force.\n\n"
            "### Move 1: Choose the formula\n"
            "Moving charge in a field → $F=|q|vB\\sin\\theta$. Perpendicular motion → "
            "$\\theta=90°$, $\\sin90°=1$.\n\n"
            "### Move 2: Substitute\n"
            "$$F=qvB=1.6\\times10^{-19}\\cdot2\\times10^6\\cdot0.5=1.6\\times10^{-13}\\text{ N}$$\n\n"
            "### Move 3: Direction (qualitative)\n"
            "Electron = negative charge → reverse the right-hand-rule result. The force "
            "magnitude is tiny because electron charge is small, but sufficient to curve "
            "the path in strong fields.\n\n"
            "### Move 4: Verify\n"
            "Units: C·(m/s)·T = N ✓. Order of magnitude $10^{-13}$ N is typical for "
            "subatomic particles in lab fields.\n\n"
            "**Answer:** $F=1.6\\times10^{-13}$ N. On Bagrut exams, always state whether "
            "you need magnitude only or full vector direction. For electrons, remember "
            "to flip the RHR direction even when the formula uses $|q|$.\n\n"
            "**Exam tip:** If the same electron were moving parallel to $\\vec{B}$, the "
            "force would drop to zero — the angle $\\theta$ is as important as $q$, $v$, "
            "and $B$. Sketch $\\vec{v}$ and $\\vec{B}$ before choosing $\\sin\\theta$."
        ),
        "body_he_md": (
            "**אלקטרון** ($q=-1.6\\times10^{-19}$ C, גודל $|q|=1.6\\times10^{-19}$ C) "
            "נע במהירות $v=2\\times10^6$ m/s **ניצב** לשדה אחיד $B=0.5$ T. "
            "מצאו את גודל הכוח המגנטי.\n\n"
            "### צעד 1: בחירת נוסחה\n"
            "מטען נע בשדה → $F=|q|vB\\sin\\theta$. תנועה ניצבת → $\\theta=90°$, $\\sin90°=1$.\n\n"
            "### צעד 2: הצבה\n"
            "$$F=qvB=1.6\\times10^{-19}\\cdot2\\times10^6\\cdot0.5=1.6\\times10^{-13}\\text{ N}$$\n\n"
            "### צעד 3: כיוון (איכותי)\n"
            "אלקטרון = מטען שלילי → הפכו את תוצאת כלל יד ימין. גודל הכוח זעיר "
            "כי מטען האלקטרון קטן, אך מספיק לעקומת מסלול בשדות חזקים.\n\n"
            "### צעד 4: אימות\n"
            "יחידות: C·(m/s)·T = N ✓. סדר גודל $10^{-13}$ N אופייני לחלקיקים "
            "תת-אטומיים בשדות מעבדה.\n\n"
            "**תשובה:** $F=1.6\\times10^{-13}$ N. בבגרות, ציינו תמיד אם נדרש רק גודל "
            "או גם כיוון וקטורי. לאלקטרון — הפכו כיוון RHR גם כשהנוסחה משתמשת ב-$|q|$.\n\n"
            "**טיפ לבחינה:** אם אותו אלקטרון היה נע מקביל ל-$\\vec{B}$, הכוח היה יורד "
            "לאפס — הזווית $\\theta$ חשובה כמו $q$, $v$ ו-$B$. שרטטו $\\vec{v}$ ו-$\\vec{B}$ "
            "לפני בחירת $\\sin\\theta$."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**A straight wire** of length $L=0.5$ m carries current $I=3$ A through a "
            "region of uniform $B=0.4$ T. The wire is **perpendicular** to the field. "
            "Find the force on the wire.\n\n"
            "### Move 1: Identify formula\n"
            "Current-carrying conductor → $F=BIL\\sin\\theta$. Perpendicular → "
            "$\\sin90°=1$.\n\n"
            "### Move 2: Calculate magnitude\n"
            "$$F=BIL\\sin90°=0.4\\cdot3\\cdot0.5=0.6\\text{ N}$$\n\n"
            "### Move 3: Find direction\n"
            "Right-hand rule: fingers along current $I$, curl toward $\\vec{B}$ → thumb "
            "gives $\\vec{F}$. If current flows east and $\\vec{B}$ points north, force "
            "points upward (out of the plane).\n\n"
            "### Move 4: Physical context\n"
            "0.6 N is a modest push — comparable to the weight of a small apple on ~60 g. "
            "Motor designs use many turns of wire to multiply this force.\n\n"
            "### Move 5: Compare with charge formula\n"
            "Do not use $F=qvB$ here — that is for a single moving charge. A wire carries "
            "many charges; the collective effect is packaged as current $I$. The effective "
            "speed of charge drift is tiny, but $I$ and $L$ capture the total force.\n\n"
            "**Answer:** $F=0.6$ N, direction from RHR. Exam tip: only the portion of wire "
            "inside the field contributes to $L$. If half the wire sticks out, use half the length.\n\n"
            "**Bagrut context:** Wire-force problems often combine with torque on a coil — "
            "the same $F=BIL$ applies to each side of a rectangular loop. If the stem gives "
            "field strength in mT, convert to T before substituting."
        ),
        "body_he_md": (
            "**חוט ישר** באורך $L=0.5$ m נושא זרם $I=3$ A באזור עם שדה אחיד $B=0.4$ T. "
            "החוט **ניצב** לשדה. מצאו את הכוח על החוט.\n\n"
            "### צעד 1: זיהוי נוסחה\n"
            "מוליך עם זרם → $F=BIL\\sin\\theta$. ניצב → $\\sin90°=1$.\n\n"
            "### צעד 2: חישוב גודל\n"
            "$$F=BIL\\sin90°=0.4\\cdot3\\cdot0.5=0.6\\text{ N}$$\n\n"
            "### צעד 3: מציאת כיוון\n"
            "כלל יד ימין: אצבעות לאורך הזרם $I$, כופפו לכיוון $\\vec{B}$ → האגודל "
            "נותן $\\vec{F}$. אם הזרם מזרח ו-$\\vec{B}$ צפון, הכוח כלפי מעלה.\n\n"
            "### צעד 4: הקשר פיזיקלי\n"
            "0.6 N הוא דחיפה מתונה — דומה למשקל תפוח קטן (~60 g). מנועים "
            "משתמשים בלולאות רבות להכפלת הכוח.\n\n"
            "### צעד 5: השוואה לנוסחת מטען\n"
            "אל תשתמשו ב-$F=qvB$ — זו נוסחה למטען בודד נע. בחוט יש מטענים רבים; "
            "האפקט המצטבר מיוצג על ידי הזרם $I$. מהירות drift קטנה, אך $I$ ו-$L$ "
            "תופסים את הכוח הכולל.\n\n"
            "**תשובה:** $F=0.6$ N, כיוון מ-RHR. **טיפ לבחינה:** רק החלק **בתוך** "
            "השדה נספר ל-$L$. אם חצי החוט בחוץ — השתמשו בחצי האורך.\n\n"
            "**הקשר בגרות:** בעיות כוח על חוט משולבות לעיתים עם מומנט על סליל — "
            "אותו $F=BIL$ חל על כל צלע של לולאה מלבנית. אם ניתן שדה ב-mT, "
            "המרו ל-T לפני ההצבה."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**A proton** ($m=1.67\\times10^{-27}$ kg, $q=1.6\\times10^{-19}$ C) enters a "
            "uniform $B=0.5$ T field at $v=2\\times10^6$ m/s **perpendicular** to $\\vec{B}$. "
            "Find the orbit radius $r$, period $T$, and state whether magnetic force does work.\n\n"
            "### Move 1: Radius\n"
            "$$r=\\frac{mv}{qB}=\\frac{1.67\\times10^{-27}\\cdot2\\times10^6}{1.6\\times10^{-19}\\cdot0.5}"
            "=\\frac{3.34\\times10^{-21}}{8\\times10^{-20}}\\approx0.042\\text{ m}=4.2\\text{ cm}$$\n\n"
            "### Move 2: Period\n"
            "$$T=\\frac{2\\pi m}{qB}=\\frac{2\\pi\\cdot1.67\\times10^{-27}}{1.6\\times10^{-19}\\cdot0.5}"
            "\\approx1.31\\times10^{-7}\\text{ s}$$\n\n"
            "### Move 3: Work done\n"
            "Magnetic force is always $\\perp\\vec{v}$ → $W=0$ → kinetic energy unchanged. "
            "The proton speed stays $2\\times10^6$ m/s throughout the orbit. Only the "
            "**direction** of velocity changes, not its magnitude — unlike an electric "
            "field which can accelerate or decelerate charges along $\\vec{E}$.\n\n"
            "### Move 4: Cross-check period\n"
            "Also $T=2\\pi r/v=2\\pi(0.042)/(2\\times10^6)\\approx1.3\\times10^{-7}$ s ✓. "
            "Note $T=2\\pi m/(qB)$ does not depend on $v$ — a faster proton would orbit "
            "at larger $r$ but complete each lap in the same time.\n\n"
            "### Move 5: Frequency (optional)\n"
            "Cyclotron frequency $f=1/T=qB/(2\\pi m)\\approx7.6\\times10^6$ Hz. "
            "Mass spectrometers use $r=mv/(qB)$ to separate ions of different mass.\n\n"
            "**Answer:** $r\\approx4.2$ cm, $T\\approx1.3\\times10^{-7}$ s, $W=0$. "
            "Bagrut often asks \"what happens to speed?\" — answer: unchanged in a pure "
            "magnetic field. If both $E$ and $B$ are present, the full Lorentz force "
            "includes an electric term that can change energy."
        ),
        "body_he_md": (
            "**פרוטון** ($m=1.67\\times10^{-27}$ kg, $q=1.6\\times10^{-19}$ C) נכנס לשדה "
            "אחיד $B=0.5$ T במהירות $v=2\\times10^6$ m/s **ניצב** ל-$\\vec{B}$. "
            "מצאו רדיוס $r$, מחזור $T$, וציינו האם הכוח המגנטי עושה עבודה.\n\n"
            "### צעד 1: רדיוס\n"
            "$$r=\\frac{mv}{qB}=\\frac{1.67\\times10^{-27}\\cdot2\\times10^6}{1.6\\times10^{-19}\\cdot0.5}"
            "\\approx0.042\\text{ m}=4.2\\text{ cm}$$\n\n"
            "### צעד 2: מחזור\n"
            "$$T=\\frac{2\\pi m}{qB}\\approx1.31\\times10^{-7}\\text{ s}$$\n\n"
            "### צעד 3: עבודה\n"
            "כוח מגנטי תמיד $\\perp\\vec{v}$ → $W=0$ → אנרגיה קינטית לא משתנה. "
            "מהירות הפרוטון נשארת $2\\times10^6$ m/s לאורך כל המסלול. רק **כיוון** "
            "המהירות משתנה, לא גודלה — בניגוד לשדה חשמלי שיכול להאיץ לאורך $\\vec{E}$.\n\n"
            "### צעד 4: אימות מחזור\n"
            "גם $T=2\\pi r/v\\approx1.3\\times10^{-7}$ s ✓. שימו לב: $T=2\\pi m/(qB)$ "
            "לא תלוי ב-$v$ — פרוטון מהיר יותר יקיף ברדיוס גדול יותר אך באותו זמן.\n\n"
            "### צעד 5: תדר (אופציונלי)\n"
            "תדר ציקלוטרון $f=1/T=qB/(2\\pi m)\\approx7.6\\times10^6$ Hz. "
            "ספקטרומטרי מסה משתמשים ב-$r=mv/(qB)$ להפרדת יונים.\n\n"
            "**תשובה:** $r\\approx4.2$ cm, $T\\approx1.3\\times10^{-7}$ s, $W=0$. "
            "בבגרות שואלים לעיתים \"מה קורה למהירות?\" — תשובה: לא משתנה בשדה מגנטי "
            "טהור. אם קיימים גם $E$ ו-$B$, כוח לורנץ המלא כולל רכיב חשמלי שיכול לשנות אנרגיה."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "A proton ($q=1.6\\times10^{-19}$ C) moves at $v=3\\times10^5$ m/s at "
            "$\\theta=30°$ to $B=0.2$ T.\n\n"
            "**Step 1:** Formula for moving charge: $F=qvB\\sin\\theta$.\n"
            "**Step 2:** $\\sin30°=0.5$.\n\n"
            "$$F=1.6\\times10^{-19}\\cdot3\\times10^5\\cdot0.2\\cdot0.5"
            "=1.6\\times10^{-19}\\cdot3\\times10^4=4.8\\times10^{-15}\\text{ N}$$\n\n"
            "**Verify:** If you forgot $\\sin\\theta$ and got $9.6\\times10^{-15}$ N, "
            "you used perpendicular formula incorrectly. At 30°, force is half the maximum.\n\n"
            "**Answer:** $F=4.8\\times10^{-15}$ N."
        ),
        "checkpoint_solution_he": (
            "פרוטון ($q=1.6\\times10^{-19}$ C) נע ב-$v=3\\times10^5$ m/s בזווית "
            "$\\theta=30°$ ל-$B=0.2$ T.\n\n"
            "**שלב 1:** נוסחה למטען נע: $F=qvB\\sin\\theta$.\n"
            "**שלב 2:** $\\sin30°=0.5$.\n\n"
            "$$F=1.6\\times10^{-19}\\cdot3\\times10^5\\cdot0.2\\cdot0.5=4.8\\times10^{-15}\\text{ N}$$\n\n"
            "**אימות:** אם שכחתם $\\sin\\theta$ וקיבלתם $9.6\\times10^{-15}$ N — "
            "השתמשתם בנוסחה הניצבת בטעות. ב-30°, הכוח חצי מהמקסימום.\n\n"
            "**תשובה:** $F=4.8\\times10^{-15}$ N."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "A 2 m wire carries 5 A at $\\theta=60°$ to a 0.3 T field.\n\n"
            "**Step 1:** Wire in field → $F=BIL\\sin\\theta$.\n"
            "**Step 2:** $\\sin60°=\\frac{\\sqrt{3}}{2}\\approx0.866$.\n\n"
            "$$F=0.3\\cdot5\\cdot2\\cdot\\sin60°=3\\cdot\\frac{\\sqrt{3}}{2}\\approx2.60\\text{ N}$$\n\n"
            "**Verify:** Maximum force (perpendicular) would be $0.3\\cdot5\\cdot2=3$ N. "
            "At 60°, we expect less than 3 N — 2.6 N is reasonable.\n\n"
            "**Answer:** $F\\approx2.6$ N."
        ),
        "checkpoint_solution_he": (
            "חוט באורך 2 m נושא 5 A בזווית $\\theta=60°$ לשדה 0.3 T.\n\n"
            "**שלב 1:** חוט בשדה → $F=BIL\\sin\\theta$.\n"
            "**שלב 2:** $\\sin60°=\\frac{\\sqrt{3}}{2}\\approx0.866$.\n\n"
            "$$F=0.3\\cdot5\\cdot2\\cdot\\sin60°=3\\cdot\\frac{\\sqrt{3}}{2}\\approx2.60\\text{ N}$$\n\n"
            "**אימות:** כוח מקסימלי (ניצב) היה $3$ N. ב-60° מצפים לפחות — 2.6 N סביר.\n\n"
            "**תשובה:** $F\\approx2.6$ N."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Situation | Formula | Direction |\n"
            "|---|---|---|\n"
            "| Moving charge in $B$ | $F=qvB\\sin\\theta$ | Right-hand rule (reverse for $-q$) |\n"
            "| Current wire in $B$ | $F=BIL\\sin\\theta$ | Right-hand rule (current direction) |\n"
            "| Circular orbit ($v\\perp B$) | $r=mv/(qB)$ | Centripetal, force toward centre |\n"
            "| Period of orbit | $T=2\\pi m/(qB)$ | Independent of speed $v$ |\n"
            "| No magnetic force | $\\theta=0°$ or $180°$ | Parallel/antiparallel to $B$ |\n\n"
            "**Step-by-step:** (1) Is it a charge or a wire? (2) Find $\\theta$ between "
            "$\\vec{v}$ (or wire) and $\\vec{B}$. (3) Apply the correct formula with "
            "$\\sin\\theta$. (4) Use RHR for direction; flip for negative charge. "
            "(5) If motion is circular, equate $qvB=mv^2/r$.\n\n"
            "**When to use:** Any Bagrut problem mentioning magnetic field, current in "
            "a field, or curved particle paths in $B$. For combined $E$ and $B$ fields, "
            "add electric and magnetic forces separately.\n\n"
            "**Exam tip:** Write $\\sin\\theta$ explicitly even when $\\theta=90°$ — "
            "it prevents the common error of forgetting the factor at other angles."
        ),
        "body_he_md": (
            "| מצב | נוסחה | כיוון |\n"
            "|---|---|---|\n"
            "| מטען נע ב-$B$ | $F=qvB\\sin\\theta$ | כלל יד ימין (הפוך ל-$-q$) |\n"
            "| חוט עם זרם ב-$B$ | $F=BIL\\sin\\theta$ | כלל יד ימין (כיוון זרם) |\n"
            "| מסלול מעגלי ($v\\perp B$) | $r=mv/(qB)$ | מרכזי, כוח למרכז |\n"
            "| מחזור הקפה | $T=2\\pi m/(qB)$ | לא תלוי במהירות $v$ |\n"
            "| ללא כוח מגנטי | $\\theta=0°$ או $180°$ | מקביל/נגדי ל-$B$ |\n\n"
            "**שלב-אחר-שלב:** (1) מטען או חוט? (2) מצאו $\\theta$ בין $\\vec{v}$ (או חוט) "
            "ל-$\\vec{B}$. (3) יישמו נוסחה עם $\\sin\\theta$. (4) RHR לכיוון; הפוך "
            "למטען שלילי. (5) אם תנועה מעגלית — השוו $qvB=mv^2/r$.\n\n"
            "**מתי להשתמש:** כל בעיית בגרות עם שדה מגנטי, זרם בשדה, או מסלול מעוקל "
            "ב-$B$. בשדות $E$ ו-$B$ משולבים — חברו כוחות בנפרד.\n\n"
            "**טיפ לבחינה:** כתבו $\\sin\\theta$ במפורש גם כש-$\\theta=90°$ — "
            "זה מונע שכחה של הגורם בזוויות אחרות."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Forgetting $\\sin\\theta$:** If velocity or current is not perpendicular "
            "to $\\vec{B}$, you must multiply by $\\sin\\theta$. At $\\theta=30°$, force "
            "is **half** the maximum — a very common Bagrut arithmetic trap.\n\n"
            "2. **Wrong direction for negative charge:** The right-hand rule gives force "
            "on a **positive** charge. Electrons and negative ions need the direction "
            "**reversed**. Students often get magnitude right but direction wrong.\n\n"
            "3. **Claiming magnetic force does work:** Magnetic force is always "
            "$\\perp\\vec{v}$, so $W=0$ and kinetic energy is unchanged. Do not write "
            "$W=BILd$ for a charge moving in a pure magnetic field.\n\n"
            "4. **Confusing electric and magnetic fields:** $\\vec{E}$ acts on stationary "
            "and moving charges along $\\vec{E}$. $\\vec{B}$ acts only on moving charges, "
            "perpendicular to both $\\vec{v}$ and $\\vec{B}$.\n\n"
            "**Example misconception:** \"The magnetic field speeds up the particle.\"\n\n"
            "**Fix:** It changes direction, not speed (in a uniform $\\vec{B}$ alone)."
        ),
        "body_he_md": (
            "1. **שכחת $\\sin\\theta$:** אם המהירות או הזרם לא ניצבים ל-$\\vec{B}$, "
            "חובה להכפיל ב-$\\sin\\theta$. ב-$\\theta=30°$ הכוח **חצי** מהמקסימום — "
            "מלכודת חשבון נפוצה בבגרות.\n\n"
            "2. **כיוון שגוי למטען שלילי:** כלל יד ימין נותן כוח על מטען **חיובי**. "
            "אלקטרונים ויונים שליליים — **הפכו** את הכיוון. לעיתים הגודל נכון "
            "אך הכיוון שגוי.\n\n"
            "3. **טענה שכוח מגנטי עושה עבודה:** הכוח תמיד $\\perp\\vec{v}$, לכן "
            "$W=0$ ואנרגיה קינטית לא משתנה. אל תכתבו $W=BILd$ למטען בשדה מגנטי טהור.\n\n"
            "4. **בלבול שדה חשמלי ומגנטי:** $\\vec{E}$ פועל על מטענים נחים ונעים "
            "לאורך $\\vec{E}$. $\\vec{B}$ פועל רק על מטענים נעים, ניצב ל-$\\vec{v}$ "
            "ול-$\\vec{B}$.\n\n"
            "**דוגמת טעות:** \"השדה המגנטי מאיץ את החלקיק.\"\n\n"
            "**תיקון:** הוא משנה כיוון, לא מהירות (ב-$\\vec{B}$ אחיד בלבד)."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Magnetism is the bridge between mechanics and electromagnetism — you need "
            "vectors, circular motion, and energy ideas all at once. Every motor, speaker, "
            "hard drive, and MRI scanner relies on the Lorentz force you learn here.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:electromagnetic_induction` **Electromagnetic Induction** (direct prereq)\n"
            "- `concept:magnetic_force` applications in circuits and AC devices\n\n"
            "**Builds on:**\n"
            "- `concept:vectors_basics` **Vectors — Basics** (cross product intuition)\n"
            "- `concept:circular_motion` **Circular Motion** (centripetal force)\n\n"
            "**Why it matters for exams:** Bagrut 5-unit physics regularly combines "
            "Lorentz force with kinematics and energy. Mass spectrometer and cyclotron "
            "questions test whether you can transfer $r=mv/(qB)$ to new contexts."
        ),
        "body_he_md": (
            "מגנטיות היא הגשר בין מכניקה לאלקטרומגנטיות — צריך וקטורים, תנועה מעגלית "
            "ורעיונות אנרגיה יחד. כל מנוע, רמקול, דיסק קשיח ו-MRI מסתמכים על "
            "כוח לורנץ שנלמד כאן.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:electromagnetic_induction` **השראה אלקטרומגנטית** (דרישה ישירה)\n"
            "- יישומי `concept:magnetic_force` במעגלים ומכשירי AC\n\n"
            "**מבוסס על:**\n"
            "- `concept:vectors_basics` **וקטורים — יסודות** (אינטואיציה למכפלה וекטורית)\n"
            "- `concept:circular_motion` **תנועה מעגלית** (כוח מרכזי)\n\n"
            "**למה זה חשוב לבחינות:** בגרות 5 יחידות משלבת לעיתים קרובות כוח לורנץ "
            "עם קinematika ואנרגיה. שאלות ספקטרומטר מסה וציקלוטרון בודקות "
            "העברה של $r=mv/(qB)$ להקשרים חדשים."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Core formulas — say each aloud once:**\n"
            "- Moving charge: $F=qvB\\sin\\theta$ (Lorentz force magnitude).\n"
            "- Wire in field: $F=BIL\\sin\\theta$.\n"
            "- Direction: right-hand rule; **flip for negative charge**.\n"
            "- Circular orbit ($v\\perp B$): $r=mv/(qB)$, $T=2\\pi m/(qB)$.\n"
            "- Magnetic force does **NO work**: $W=0$, speed unchanged.\n\n"
            "**Quick checks before submitting:** Did you include $\\sin\\theta$? "
            "Is $L$ only the wire segment inside the field? Did you reverse "
            "direction for electrons?\n\n"
            "**Last review:** Solve one checkpoint from this lesson without looking, "
            "then verify units (N = C·m/s·T = A·m·T)."
        ),
        "body_he_md": (
            "**נוסחאות מרכזיות — אמרו כל אחת בקול פעם אחת:**\n"
            "- מטען נע: $F=qvB\\sin\\theta$ (גודל כוח לורנץ).\n"
            "- חוט בשדה: $F=BIL\\sin\\theta$.\n"
            "- כיוון: כלל יד ימין; **הפוך למטען שלילי**.\n"
            "- מסלול מעגלי ($v\\perp B$): $r=mv/(qB)$, $T=2\\pi m/(qB)$.\n"
            "- כוח מגנטי **לא עושה עבודה**: $W=0$, מהירות לא משתנה.\n\n"
            "**בדיקות מהירות לפני הגשה:** הכללתם $\\sin\\theta$? "
            "האם $L$ הוא רק הקטע **בתוך** השדה? הפכתם כיוון לאלקטרונים?\n\n"
            "**חזרה אחרונה:** פתרו checkpoint אחד מהשיעור בלי להסתכל, "
            "ואמתו יחידות (N = C·m/s·T = A·m·T)."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Lorentz force** on a moving charge: $F=qvB\\sin\\theta$; direction from "
            "right-hand rule (reverse for $-q$).\n"
            "- **Force on a wire:** $F=BIL\\sin\\theta$; same RHR using current direction.\n"
            "- **Circular motion** when $v\\perp B$: radius $r=mv/(qB)$; period "
            "$T=2\\pi m/(qB)$ independent of speed.\n"
            "- Magnetic force is always perpendicular to motion → **no work done**, "
            "kinetic energy constant.\n\n"
            "**Takeaway:** From the problem wording alone — charge or wire, angle to "
            "$\\vec{B}$, and whether orbit or force magnitude is asked — you should "
            "know which row of the method guide to use before substituting numbers."
        ),
        "body_he_md": (
            "- **כוח לורנץ** על מטען נע: $F=qvB\\sin\\theta$; כיוון מכלל יד ימין "
            "(הפוך ל-$-q$).\n"
            "- **כוח על חוט:** $F=BIL\\sin\\theta$; אותו RHR לפי כיוון זרם.\n"
            "- **תנועה מעגלית** כש-$v\\perp B$: רדיוס $r=mv/(qB)$; מחזור "
            "$T=2\\pi m/(qB)$ לא תלוי במהירות.\n"
            "- כוח מגנטי תמיד ניצב לתנועה → **אין עבודה**, אנרגיה קינטית קבועה.\n\n"
            "**מסקנה:** מניסוח השאלה בלבד — מטען או חוט, זווית ל-$\\vec{B}$, "
            "ומסלול מעגלי או גודל כוח — תדעו איזו שורה במדריך השיטה לפני ההצבה."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "When velocity is **parallel** to $\\vec{B}$, the angle $\\theta=0°$ and "
            "$\\sin0°=0$. The Lorentz force formula $F=qvB\\sin\\theta$ gives "
            "$F=0$ — no magnetic force at all.\n\n"
            "This is a fundamental property: magnetic fields only push charges that "
            "have a velocity component **perpendicular** to the field. Option A (maximum) "
            "would require $\\theta=90°$. Options C and D give nonzero magnitudes that "
            "ignore the angle.\n\n"
            "**Common slip:** Using $F=qvB$ without checking whether motion is parallel.\n\n"
            "**Exam tip:** \"Parallel to field\" always means zero magnetic force. "
            "Before answering, check whether the stem describes parallel, perpendicular, "
            "or general-angle motion. **Answer:** Zero."
        ),
        "explanation_he": (
            "כשהמהירות **מקבילה** ל-$\\vec{B}$, הזווית $\\theta=0°$ ו-$\\sin0°=0$. "
            "נוסחת לורנץ $F=qvB\\sin\\theta$ נותנת $F=0$ — אין כוח מגנטי כלל.\n\n"
            "זו תכונה יסודית: שדות מגנטיים דוחפים רק מטענים עם רכיב מהירות "
            "**ניצב** לשדה. אפשרות א (מקסימום) דורשת $\\theta=90°$. אפשרויות ג ו-ד "
            "נותנות גודל לא-אפס ומתעלמות מהזווית.\n\n"
            "**טעות נפוצה:** שימוש ב-$F=qvB$ בלי לבדוק אם התנועה מקבילה.\n\n"
            "**טיפ לבחינה:** \"מקביל לשדה\" = תמיד כוח אפס. **זכרו:** גם פרוטון וגם "
            "אלקטרון — אם נעים מקביל לשדה, הכוח אפס; $q$ משפיע על כיוון, לא על "
            "גודל כש-$\\sin\\theta=0$. **תשובה:** אפס."
        ),
    },
    {
        "explanation_en": (
            "This is a straight Lorentz force magnitude problem. Charge $q=2\\times10^{-6}$ C, "
            "$v=100$ m/s, $B=0.1$ T, and $\\theta=90°$ (perpendicular) so $\\sin90°=1$:\n"
            "$$F=qvB=2\\times10^{-6}\\cdot100\\cdot0.1=2\\times10^{-5}\\text{ N}$$\n\n"
            "Units check: C × (m/s) × T = N ✓. The force is small because the charge "
            "is microcoulomb-scale. A positive charge would feel force direction from "
            "the right-hand rule; this question asks magnitude only.\n\n"
            "**Common slip:** Forgetting to convert units or dropping a power of ten "
            "in scientific notation. If you got $2\\times10^{-4}$ N, check multiplication order.\n\n"
            "**Exam tip:** Write the formula before numbers; circle $\\sin\\theta$ even "
            "when it equals 1. **Answer:** $2\\times10^{-5}$ N."
        ),
        "explanation_he": (
            "זו בעיית גודל כוח לורנץ ישירה. מטען $q=2\\times10^{-6}$ C, $v=100$ m/s, "
            "$B=0.1$ T, ו-$\\theta=90°$ (ניצב) אז $\\sin90°=1$:\n"
            "$$F=qvB=2\\times10^{-6}\\cdot100\\cdot0.1=2\\times10^{-5}\\text{ N}$$\n\n"
            "בדיקת יחידות: C × (m/s) × T = N ✓. הכוח קטן כי המטען בסדר גודל מיקרו-קולomb. "
            "מטען חיובי היה מקבל כיוון מכלל יד ימין; כאן נשאל רק על הגודל.\n\n"
            "**טעות נפוצה:** שכחת המרת יחידות או איבוד סדר גודל בסימון מדעי. "
            "אם קיבלתם $2\\times10^{-4}$ N — בדקו סדר פעולות.\n\n"
            "**טיפ לבחינה:** כתבו נוסחה לפני מספרים; סמנו $\\sin\\theta$ גם כשהוא 1. "
            "**תשובה:** $2\\times10^{-5}$ N."
        ),
    },
    {
        "explanation_en": (
            "A current-carrying wire in a magnetic field experiences $F=BIL\\sin\\theta$. "
            "Here $B=0.5$ T, $I=4$ A, $L=1$ m, wire perpendicular to field → "
            "$\\sin90°=1$:\n"
            "$$F=BIL=0.5\\cdot4\\cdot1=2\\text{ N}$$\n\n"
            "This is the motor principle: current plus field produces a mechanical force. "
            "Direction would come from the right-hand rule (not asked here).\n\n"
            "**Common slip:** Using $F=qvB$ (charge formula) instead of $F=BIL$ (wire formula), "
            "or using total circuit length when only 1 m is in the field.\n\n"
            "**Exam tip:** Identify \"wire with current\" → $BIL\\sin\\theta$ immediately. "
            "**Answer:** 2 N."
        ),
        "explanation_he": (
            "חוט עם זרם בשדה מגנטי חווה $F=BIL\\sin\\theta$. כאן $B=0.5$ T, $I=4$ A, "
            "$L=1$ m, חוט ניצב לשדה → $\\sin90°=1$:\n"
            "$$F=BIL=0.5\\cdot4\\cdot1=2\\text{ N}$$\n\n"
            "זה עקרון המנוע: זרם ושדה יוצרים כוח מכני. כיוון — מכלל יד ימין (לא נשאל). "
            "הנוסחה משתמשת בזרם $I$, לא במטען $q$ — אל תערבבו בין סוגי בעיות.\n\n"
            "**טעות נפוצה:** שימוש ב-$F=qvB$ (נוסחת מטען) במקום $F=BIL$ (נוסחת חוט), "
            "או שימוש באורך מעגל מלא כש-1 m בלבד בשדה. אם קיבלתם 0.5 N — בדקו $I$ או $L$.\n\n"
            "**טיפ לבחינה:** \"חוט עם זרם\" → $BIL\\sin\\theta$ מיד. **תשובה:** 2 N."
        ),
    },
    {
        "explanation_en": (
            "When a charge moves **parallel** to $\\vec{B}$, $\\theta=0°$ and "
            "$\\sin0°=0$, so $F=qvB\\sin0°=0$. There is no magnetic force.\n\n"
            "Magnetic fields only affect the component of velocity perpendicular to "
            "$\\vec{B}$. Parallel motion has no perpendicular component — the charge "
            "travels straight through the field unchanged (ignoring other forces). "
            "This geometry is tested frequently as a conceptual MCQ on Bagrut exams.\n\n"
            "**Common slip:** Answering $F=qvB$ by reflex without reading \"parallel.\"\n\n"
            "**Exam tip:** Parallel → zero; perpendicular → maximum. The angle is "
            "always the first thing to check. **Answer:** Zero."
        ),
        "explanation_he": (
            "כשמטען נע **מקביל** ל-$\\vec{B}$, $\\theta=0°$ ו-$\\sin0°=0$, "
            "לכן $F=qvB\\sin0°=0$. אין כוח מגנטי.\n\n"
            "שדות מגנטיים משפיעים רק על הרכיב הניצב של המהירות ל-$\\vec{B}$. "
            "תנועה מקבילה — אין רכיב ניצב — המטען עובר ישר בשדה ללא שינוי. "
            "שאלה קונцepטואלית נפוצה בבגרות.\n\n"
            "**טעות נפוצה:** תשובה $F=qvB$ בהרף בלי לקרוא \"מקביל\". "
            "טעות נוספת: בלבול עם כוח חשמלי שכן פועל על מטען נע מקביל ל-$\\vec{E}$.\n\n"
            "**טיפ לבחינה:** מקביל → אפס; ניצב → מקסימום. הזווית — הדבר הראשון "
            "לבדיקה. **תשובה:** אפס."
        ),
    },
    {
        "explanation_en": (
            "Magnetic force is always **perpendicular** to velocity ($\\vec{F}\\perp\\vec{v}$). "
            "Work is $W=\\vec{F}\\cdot\\vec{d}=Fd\\cos\\theta$. Since the angle between "
            "force and displacement along the path is 90°, $\\cos90°=0$ and $W=0$.\n\n"
            "Therefore magnetic force cannot change kinetic energy or speed — it only "
            "deflects the particle's direction. This contrasts with electric force, "
            "which can accelerate charges along the field direction.\n\n"
            "**Common slip:** Writing $W=BILd$ or assuming the field \"speeds up\" "
            "the particle.\n\n"
            "**Exam tip:** \"Does magnetic force do work?\" → always **No** for uniform "
            "$\\vec{B}$ alone. **Answer:** No — force ⊥ velocity → $W=0$."
        ),
        "explanation_he": (
            "כוח מגנטי תמיד **ניצב** למהירות ($\\vec{F}\\perp\\vec{v}$). "
            "עבודה היא $W=\\vec{F}\\cdot\\vec{d}=Fd\\cos\\theta$. מכיוון שהזווית "
            "בין כוח לתזוזה לאורך המסלול היא 90°, $\\cos90°=0$ ו-$W=0$.\n\n"
            "לכן כוח מגנטי לא יכול לשנות אנרגיה קינטית או מהירות — רק לסטות "
            "את כיוון החלקיק. זה בניגוד לכוח חשמלי שיכול להאיץ לאורך השדה.\n\n"
            "**טעות נפוצה:** כתיבת $W=BILd$ או הנחה שהשדה \"מאיץ\" את החלקיק.\n\n"
            "**טיפ לבחינה:** \"האם כוח מגנטי עושה עבודה?\" → תמיד **לא** "
            "ב-$\\vec{B}$ אחיד בלבד. **תשובה:** לא — כוח ⊥ מהירות → $W=0$."
        ),
    },
    {
        "explanation_en": (
            "Perpendicular motion in a uniform field gives circular orbit radius "
            "$r=mv/(qB)$. For the electron: $m=9.1\\times10^{-31}$ kg, "
            "$q=1.6\\times10^{-19}$ C, $v=3\\times10^6$ m/s, $B=0.01$ T:\n"
            "$$r=\\frac{9.1\\times10^{-31}\\cdot3\\times10^6}{1.6\\times10^{-19}\\cdot0.01}"
            "=\\frac{2.73\\times10^{-24}}{1.6\\times10^{-21}}\\approx1.7\\times10^{-3}\\text{ m}$$\n\n"
            "Electrons curve tightly because their mass is tiny. Compare: a proton at "
            "the same speed would have ~1836× larger radius. The orbit radius scales "
            "linearly with mass and speed, and inversely with $q$ and $B$.\n\n"
            "**Common slip:** Using $r=mv/qB$ but forgetting $q$ in denominator, "
            "or mixing up charge and mass exponents.\n\n"
            "**Exam tip:** $r\\propto m$ — heavier particles, wider arcs. "
            "**Answer:** $\\approx1.7\\times10^{-3}$ m."
        ),
        "explanation_he": (
            "תנועה ניצבת בשדה אחיד נותנת רדיוס מסלול $r=mv/(qB)$. לאלקטרון: "
            "$m=9.1\\times10^{-31}$ kg, $q=1.6\\times10^{-19}$ C, $v=3\\times10^6$ m/s, "
            "$B=0.01$ T:\n"
            "$$r=\\frac{9.1\\times10^{-31}\\cdot3\\times10^6}{1.6\\times10^{-19}\\cdot0.01}"
            "\\approx1.7\\times10^{-3}\\text{ m}$$\n\n"
            "אלקטרונים מתעקלים בצפיפות כי מסתם זעירה. פרוטון באותה מהירות — "
            "רדיוס גדול פי ~1836. הרדיוס פרופורציוני ל-$m$ ו-$v$, ויחסי "
            "הפוך ל-$q$ ו-$B$.\n\n"
            "**טעות נפוצה:** שימוש ב-$r=mv/qB$ אך שכחת $q$ במכנה, "
            "או בלבול מעריכים של מטען ומסה. אם $B$ מוכפל, $r$ מחולק ב-2.\n\n"
            "**טיפ לבחינה:** $r\\propto m$ — חלקיק כבד, קשת רחבה. "
            "אם $B$ מוכפל, $r$ מחולק ב-2. השוו תמיד לפרוטון באותה מהירות. "
            "**תשובה:** $\\approx1.7\\times10^{-3}$ m."
        ),
    },
    {
        "explanation_en": (
            "Two parallel wires carrying currents in the **same direction** attract each "
            "other. Each wire creates a magnetic field that exerts a force on the other wire.\n\n"
            "Use the right-hand rule: the field from wire 1 at wire 2's location combines "
            "with wire 2's current to produce a force **toward** wire 1 (and vice versa). "
            "Same-direction currents → **attraction**. Opposite-direction currents → repulsion. "
            "This is the basis of the SI ampere definition.\n\n"
            "**Common slip:** Guessing \"like currents repel\" by analogy with electric "
            "charges — magnetism has the opposite rule for parallel wires.\n\n"
            "**Exam tip:** Remember \"same direction → attract\" for parallel wires. "
            "**Answer:** They attract."
        ),
        "explanation_he": (
            "שני חוטים מקבילים עם זרמים **באותו כיוון** נמשכים זה לזה. כל חוט "
            "יוצר שדה מגנטי שמפעיל כוח על החוט השני.\n\n"
            "כלל יד ימין: השדה מחוט 1 במיקום חוט 2, עם הזרם בחוט 2, נותן כוח "
            "**לכיוון** חוט 1 (ולהפך). זרמים באותו כיוון → **משיכה**. "
            "זרמים בכיוונים מנוגדים → דחייה. זהו בסיס הגדרת האמפר ב-SI.\n\n"
            "**טעות נפוצה:** ניחוש \"זרמים דומים דוחים\" בדימוי למטענים חשמליים — "
            "במגנטיות הכלל ההפוך לחוטים מקבילים. אל תערבבו עם כוחות קולomb.\n\n"
            "**טיפ לבחינה:** \"אותו כיוון → משיכה\" לחוטים מקבילים. "
            "שרטטו שני חוטים וחצים של זרם לפני שעונים. **תשובה:** משיכה."
        ),
    },
    {
        "explanation_en": (
            "Wire force formula: $F=BIL\\sin\\theta$. Given $B=0.6$ T, $I=10$ A, "
            "$L=0.3$ m, $\\theta=45°$:\n"
            "$$F=0.6\\cdot10\\cdot0.3\\cdot\\sin45°=1.8\\cdot0.707\\approx1.27\\text{ N}$$\n\n"
            "At 45°, force is about 71% of the maximum (perpendicular) value "
            "$F_{\\max}=BIL=1.8$ N. Always include $\\sin\\theta$ when the angle "
            "is not 90°. The wire segment length $L=0.3$ m must be the portion "
            "inside the field, not the total circuit length.\n\n"
            "**Common slip:** Using $\\cos45°$ instead of $\\sin45°$, or forgetting "
            "$L=0.3$ m (using a different wire length). Getting 1.8 N means you omitted $\\sin45°$.\n\n"
            "**Exam tip:** $F_{\\max}=BIL$ when perpendicular; multiply by $\\sin\\theta$ "
            "otherwise. **Answer:** $\\approx1.27$ N."
        ),
        "explanation_he": (
            "נוסחת כוח על חוט: $F=BIL\\sin\\theta$. נתון $B=0.6$ T, $I=10$ A, "
            "$L=0.3$ m, $\\theta=45°$:\n"
            "$$F=0.6\\cdot10\\cdot0.3\\cdot\\sin45°=1.8\\cdot0.707\\approx1.27\\text{ N}$$\n\n"
            "ב-45°, הכוח כ-71% מהמקסימום (ניצב) $F_{\\max}=BIL=1.8$ N. "
            "הכלילו $\\sin\\theta$ כשהזווית לא 90°. אורך הקטע $L=0.3$ m "
            "חייב להיות החלק **בתוך** השדה, לא אורך המעגל כולו.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\cos45°$ במקום $\\sin45°$, או שכחת "
            "$L=0.3$ m. אם קיבלתם 1.8 N — שכחתם $\\sin45°$.\n\n"
            "**טיפ לבחינה:** $F_{\\max}=BIL$ בניצב; הכפילו ב-$\\sin\\theta$ אחרת. "
            "השוו תמיד ל-$F_{\\max}=1.8$ N כדי לוודא שהזווית נכללה. **תשובה:** $\\approx1.27$ N."
        ),
    },
]


def apply_expansion(data):
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            n = sec.get("example_number")
            if n == 1:
                sec.update(SECTION_BODIES["worked_example_1"])
            elif n == 2:
                sec.update(SECTION_BODIES["worked_example_2"])
            elif n == 3:
                sec.update(SECTION_BODIES["worked_example_3"])
        elif kind == "checkpoint":
            body_en = sec.get("body_en_md", "")
            if "proton" in body_en.lower() or "30°" in body_en:
                sec.update(SECTION_BODIES["checkpoint_1"])
            else:
                sec.update(SECTION_BODIES["checkpoint_2"])
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

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    return data


def validate_depth(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"{kind} HE weak parity")
        elif kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            n = sec.get("example_number", "?")
            if en_w < MIN_WORDS["worked_example"]["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append("worked_example HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} {key}: {w} words")

    return issues


def main():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("DEPTH ISSUES:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("All depth gates passed.")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")

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
