#!/usr/bin/env python3
"""Expand momentum.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/momentum.json"
SRC = OUT

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
    "checkpoint": {"en": 90, "he": 75},
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
            "Momentum is defined as $\\vec{p} = m\\vec{v}$ — the product of mass and velocity. "
            "Unlike speed alone, momentum carries both magnitude and direction, making it a vector quantity.\n\n"
            "For a 3 kg ball moving at 8 m/s:\n"
            "$$p = mv = 3 \\times 8 = \\boxed{24\\text{ kg·m/s}}$$\n\n"
            "The direction of the momentum matches the direction of velocity. If the ball moves east, "
            "the momentum vector points east with magnitude 24 kg·m/s.\n\n"
            "**Common wrong path:** Using $p = m/v$ or forgetting that momentum has units kg·m/s "
            "(not kg·m/s², which is force).\n\n"
            "**Exam tip:** On Bagrut questionnaire 1, a direct momentum calculation is often the "
            "first sub-question before a collision problem. Always state units and direction when asked."
        ),
        "he": (
            "תנע מוגדר כ-$\\vec{p} = m\\vec{v}$ — מכפלת מסה ומהירות. "
            "בניגוד למהירות בלבד, תנע נושא גם גודל וגם כיוון, ולכן הוא גודל וקטורי.\n\n"
            "לכדור 3 ק\"ג הנע ב-8 m/s:\n"
            "$$p = mv = 3 \\times 8 = \\boxed{24\\text{ kg·m/s}}$$\n\n"
            "כיוון התנע תואם לכיוון המהירות. אם הכדור נע מזרחה, וקטור התנע פונה מזרחה בגודל 24 kg·m/s.\n\n"
            "**טעות נפוצה:** שימוש ב-$p = m/v$ או שכחת שיחידות התנע הן kg·m/s "
            "(לא kg·m/s², שזה כוח).\n\n"
            "**טיפ לבחינה:** בבגרות שאלון 1, חישוב תנע ישיר הוא לעיתים הסעיף הראשון לפני בעיית התנגשות. "
            "תמיד ציינו יחידות וכיוון כשנדרש."
        ),
    },
    2: {
        "en": (
            "Impulse equals the change in momentum: $\\vec{J} = \\Delta\\vec{p} = m\\Delta\\vec{v}$. "
            "When velocity changes from 10 m/s to 20 m/s, the change is $\\Delta v = 20 - 10 = 10$ m/s.\n\n"
            "For a 1500 kg car:\n"
            "$$J = m\\Delta v = 1500 \\times 10 = \\boxed{15000\\text{ N·s}}$$\n\n"
            "Impulse can also be written as $J = F\\Delta t$, linking force and contact time. "
            "Both forms give the same answer — choose whichever fits the given data.\n\n"
            "**Common wrong path:** Using $J = mv$ (initial momentum) instead of $J = m\\Delta v$, "
            "or computing $\\Delta v = 20 + 10 = 30$ by adding instead of subtracting.\n\n"
            "**Exam tip:** N·s and kg·m/s are equivalent units. If the problem gives force and time, "
            "use $J = F\\Delta t$; if it gives mass and velocity change, use $J = m\\Delta v$."
        ),
        "he": (
            "מתקף שווה לשינוי בתנע: $\\vec{J} = \\Delta\\vec{p} = m\\Delta\\vec{v}$. "
            "כשמהירות משתנה מ-10 m/s ל-20 m/s, השינוי הוא $\\Delta v = 20 - 10 = 10$ m/s.\n\n"
            "למכונית 1500 kg:\n"
            "$$J = m\\Delta v = 1500 \\times 10 = \\boxed{15000\\text{ N·s}}$$\n\n"
            "מתקף ניתן גם לכתיבה כ-$J = F\\Delta t$, המקשר כוח וזמן מגע. "
            "שתי הצורות נותנות אותה תשובה — בחרו את מה שמתאים לנתונים.\n\n"
            "**טעות נפוצה:** שימוש ב-$J = mv$ (תנע ראשוני) במקום $J = m\\Delta v$, "
            "או חישוב $\\Delta v = 20 + 10 = 30$ בחיבור במקום חיסור.\n\n"
            "**טיפ לבחינה:** N·s ו-kg·m/s הם יחידות שקולות. אם השאלה נותנת כוח וזמן, "
            "השתמשו ב-$J = F\\Delta t$; אם נותנת מסה ושינוי מהירות, ב-$J = m\\Delta v$."
        ),
    },
    3: {
        "en": (
            "When a ball bounces off a wall, both the magnitude and direction of velocity change. "
            "Impulse is $\\vec{J} = m(\\vec{v}_f - \\vec{v}_i)$ — you must subtract initial from final "
            "with correct signs.\n\n"
            "Define 'away from wall' as positive. The ball approaches at $-10$ m/s and leaves at $+8$ m/s:\n"
            "$$J = m(v_f - v_i) = 0.2(8 - (-10)) = 0.2 \\times 18 = \\boxed{3.6\\text{ N·s}}$$\n\n"
            "The wall applies a positive impulse (pushing the ball away). The magnitude 18 m/s in the "
            "parentheses is the total change in velocity, not simply $10 + 8$ without sign logic.\n\n"
            "**Common wrong path:** Using $J = m(v_i - v_f)$ (reversed sign) or ignoring that "
            "approaching velocity is negative when 'away' is positive.\n\n"
            "**Exam tip:** Always define your positive direction before writing $v_i$ and $v_f$. "
            "Draw a quick arrow diagram — sign errors are the #1 mistake on impulse problems."
        ),
        "he": (
            "כשכדור קופץ מקיר, גם גודל וגם כיוון המהירות משתנים. "
            "מתקף הוא $\\vec{J} = m(\\vec{v}_f - \\vec{v}_i)$ — חייבים לחסר ראשוני מסופי עם סימנים נכונים.\n\n"
            "הגדירו 'מרחק מהקיר' כחיובי. הכדור מתקרב ב-$-10$ m/s ויוצא ב-$+8$ m/s:\n"
            "$$J = m(v_f - v_i) = 0.2(8 - (-10)) = 0.2 \\times 18 = \\boxed{3.6\\text{ N·s}}$$\n\n"
            "הקיר מפעיל מתקף חיובי (דוחף את הכדור הרחק). הגודל 18 m/s בסוגריים הוא שינוי המהירות הכולל, "
            "לא פשוט $10 + 8$ בלי לוגיקת סימנים.\n\n"
            "**טעות נפוצה:** שימוש ב-$J = m(v_i - v_f)$ (סימן הפוך) או התעלמות מכך שמהירות ההתקרבות "
            "שלילית כש'מרחק' חיובי.\n\n"
            "**טיפ לבחינה:** תמיד הגדירו כיוון חיובי לפני כתיבת $v_i$ ו-$v_f$. "
            "שרטטו דיאגרמת חיצים — טעויות סימן הן הטעות #1 בבעיות מתקף."
        ),
    },
    4: {
        "en": (
            "This problem connects impulse to velocity change through $J = F\\Delta t = m\\Delta v$. "
            "First compute the impulse from the given force and contact time.\n\n"
            "**Step 1 — Impulse:**\n"
            "$$J = F\\Delta t = 1000 \\times 0.05 = 50\\text{ N·s}$$\n\n"
            "**Step 2 — Velocity change:**\n"
            "$$\\Delta v = \\frac{J}{m} = \\frac{50}{200} = \\boxed{0.25\\text{ m/s}}$$\n\n"
            "The impulse-momentum theorem tells us that a 50 N·s push on a 200 kg object "
            "changes its speed by only 0.25 m/s — large mass resists velocity change.\n\n"
            "**Common wrong path:** Dividing force by mass ($F/m = 5$) without multiplying by time first, "
            "or confusing $\\Delta v$ with final velocity.\n\n"
            "**Exam tip:** Write the chain $F\\Delta t = \\Delta p = m\\Delta v$ explicitly. "
            "Examiners award partial credit for correct setup even if arithmetic slips later."
        ),
        "he": (
            "בעיה זו מקשרת מתקף לשינוי מהירות דרך $J = F\\Delta t = m\\Delta v$. "
            "קודם חשבו מתקף מהכוח וזמן המגע הנתונים.\n\n"
            "**שלב 1 — מתקף:**\n"
            "$$J = F\\Delta t = 1000 \\times 0.05 = 50\\text{ N·s}$$\n\n"
            "**שלב 2 — שינוי מהירות:**\n"
            "$$\\Delta v = \\frac{J}{m} = \\frac{50}{200} = \\boxed{0.25\\text{ m/s}}$$\n\n"
            "משפט המתקף-תנע אומר שדחיפה של 50 N·s על גוף 200 kg משנה את המהירות ב-0.25 m/s בלבד — "
            "מסה גדולה מתנגדת לשינוי מהירות.\n\n"
            "**טעות נפוצה:** חלוקת כוח במסה ($F/m = 5$) בלי כפל בזמן קודם, "
            "או בלבול בין $\\Delta v$ למהירות סופית.\n\n"
            "**טיפ לבחינה:** כתבו במפורש את השרשרת $F\\Delta t = \\Delta p = m\\Delta v$. "
            "בוחנים נותנים נקודות חלקיות על הגדרה נכונה גם אם החשבון מתקלקל."
        ),
    },
    5: {
        "en": (
            "This is a perfectly inelastic collision — the balls stick together. "
            "Only momentum is conserved (not kinetic energy). Define east as positive.\n\n"
            "**Initial momentum:**\n"
            "$$p_i = m_1 v_1 + m_2 v_2 = 4(6) + 2(-3) = 24 - 6 = 18\\text{ kg·m/s}$$\n\n"
            "**Final momentum (combined mass):**\n"
            "$$p_f = (m_1 + m_2)v_f = 6v_f$$\n\n"
            "**Conservation:** $6v_f = 18 \\Rightarrow \\boxed{v_f = 3\\text{ m/s (east)}}$\n\n"
            "The lighter ball moving west partially cancels the heavier ball's eastward momentum, "
            "but the net momentum still points east.\n\n"
            "**Common wrong path:** Adding both velocities as positive ($6 + 3 = 9$) "
            "instead of giving west a negative sign, or using $v_f = (v_1 + v_2)/2$.\n\n"
            "**Exam tip:** State 'perfectly inelastic' and write $p_{\\text{before}} = p_{\\text{after}}$ "
            "before substituting numbers. The combined mass $(m_1 + m_2)$ is essential."
        ),
        "he": (
            "זו התנגשות לא-אלסטית לחלוטין — הכדורים נצמדים. "
            "רק תנע נשמר (לא אנרגיה קינטית). הגדירו מזרח כחיובי.\n\n"
            "**תנע ראשוני:**\n"
            "$$p_i = m_1 v_1 + m_2 v_2 = 4(6) + 2(-3) = 24 - 6 = 18\\text{ kg·m/s}$$\n\n"
            "**תנע סופי (מסה משולבת):**\n"
            "$$p_f = (m_1 + m_2)v_f = 6v_f$$\n\n"
            "**שימור:** $6v_f = 18 \\Rightarrow \\boxed{v_f = 3\\text{ m/s (מזרח)}}$\n\n"
            "הכדור הקל הנע מערבה מבטל חלקית את תנע הכדור הכבול מזרחה, "
            "אך התנע הנטו עדיין פונה מזרחה.\n\n"
            "**טעות נפוצה:** חיבור שתי המהירויות כחיוביות ($6 + 3 = 9$) "
            "במקום לתת למערב סימן שלילי, או שימוש ב-$v_f = (v_1 + v_2)/2$.\n\n"
            "**טיפ לבחינה:** ציינו 'לא-אלסטית לחלוטין' וכתבו $p_{\\text{לפני}} = p_{\\text{אחרי}}$ "
            "לפני הצבת מספרים. המסה המשולבת $(m_1 + m_2)$ חיונית. "
            "בבגרות, סעיף נוסף לעיתים שואל כמה אחוז מה-KE אבד — חשבו $KE_i$ ו-$KE_f$ בנפרד."
        ),
    },
    6: {
        "en": (
            "This is a recoil problem — an isolated person-skateboard system with zero initial momentum. "
            "When the person jumps forward, the skateboard must move backward to conserve momentum.\n\n"
            "Total initial momentum is zero (both at rest):\n"
            "$$0 = m_{\\text{person}} v_{\\text{person}} + m_{\\text{board}} v_{\\text{board}}$$\n"
            "$$0 = 60(3) + 20\\, v_{\\text{board}}$$\n"
            "$$v_{\\text{board}} = -\\frac{180}{20} = \\boxed{-9\\text{ m/s}}$$\n\n"
            "The negative sign means the skateboard moves opposite to the person's jump direction. "
            "The lighter skateboard recoils faster — this is the same physics as a gun firing a bullet.\n\n"
            "**Common wrong path:** Setting $v_{\\text{board}} = +9$ (ignoring the negative sign) "
            "or forgetting that the system's total momentum must remain zero.\n\n"
            "**Exam tip:** Recoil problems always start with $p_{\\text{total}} = 0$. "
            "If one object moves right, the other must move left with equal and opposite momentum."
        ),
        "he": (
            "זו בעיית רתיעה — מערכת מבודדת של אדם וסקייטבורד עם תנע ראשוני אפס. "
            "כשהאדם קופץ קדימה, הסקייטבורד חייב לנוע אחורה כדי לשמר תנע.\n\n"
            "התנע הכולל הראשוני הוא אפס (שניהם במנוחה):\n"
            "$$0 = m_{\\text{אדם}} v_{\\text{אדם}} + m_{\\text{לוח}} v_{\\text{לוח}}$$\n"
            "$$0 = 60(3) + 20\\, v_{\\text{לוח}}$$\n"
            "$$v_{\\text{לוח}} = -\\frac{180}{20} = \\boxed{-9\\text{ m/s}}$$\n\n"
            "הסימן השלילי פירושו שהסקייטבורד נע בכיוון ההפוך לקפיצת האדם. "
            "הסקייטבורד הקל נסוג מהר יותר — אותה פיזיקה כמו ירי כדור מתותח.\n\n"
            "**טעות נפוצה:** קביעת $v_{\\text{לוח}} = +9$ (התעלמות מהסימן השלילי) "
            "או שכחה שהתנע הכולל של המערכת חייב להישאר אפס.\n\n"
            "**טיפ לבחינה:** בעיות רתיעה תמיד מתחילות ב-$p_{\\text{כולל}} = 0$. "
            "אם גוף אחד נע ימינה, השני חייב לנוע שמאלה עם תנע שווה ונגדי."
        ),
    },
    7: {
        "en": (
            "An elastic collision conserves both momentum and kinetic energy. "
            "Use the standard 1D formulas with initial velocities $u_1 = 4$ m/s and $u_2 = -2$ m/s.\n\n"
            "$$v_1 = \\frac{(m_1-m_2)u_1 + 2m_2 u_2}{m_1+m_2} = \\frac{(3-1)(4) + 2(1)(-2)}{4} = \\frac{8-4}{4} = \\boxed{1\\text{ m/s}}$$\n\n"
            "$$v_2 = \\frac{(m_2-m_1)u_2 + 2m_1 u_1}{m_1+m_2} = \\frac{(1-3)(-2) + 2(3)(4)}{4} = \\frac{4+24}{4} = \\boxed{7\\text{ m/s}}$$\n\n"
            "The lighter ball ($m_2 = 1$ kg) was moving toward the heavier one and reverses to 7 m/s — "
            "a classic elastic collision result when the lighter mass gets a 'boost'.\n\n"
            "**Common wrong path:** Applying the inelastic formula $(m_1+m_2)v_f$ or "
            "forgetting the negative sign on $u_2 = -2$ m/s.\n\n"
            "**Exam tip:** Verify with energy: $KE_i = \\frac{1}{2}(3)(16) + \\frac{1}{2}(1)(4) = 26$ J "
            "and $KE_f = \\frac{1}{2}(3)(1) + \\frac{1}{2}(1)(49) = 26$ J. Equal KE confirms elastic."
        ),
        "he": (
            "התנגשות אלסטית שומרת גם תנע וגם אנרגיה קינטית. "
            "השתמשו בנוסחאות 1D הסטנדרטיות עם $u_1 = 4$ m/s ו-$u_2 = -2$ m/s.\n\n"
            "$$v_1 = \\frac{(3-1)(4) + 2(1)(-2)}{4} = \\frac{8-4}{4} = \\boxed{1\\text{ m/s}}$$\n\n"
            "$$v_2 = \\frac{(1-3)(-2) + 2(3)(4)}{4} = \\frac{4+24}{4} = \\boxed{7\\text{ m/s}}$$\n\n"
            "הכדור הקל ($m_2 = 1$ kg) נע לכיוון הכבד ומתהפך ל-7 m/s — "
            "תוצאה קלאסית בהתנגשות אלסטית כשהמסה הקלה מקבלת 'דחיפה'.\n\n"
            "**טעות נפוצה:** יישום נוסחת לא-אלסטית $(m_1+m_2)v_f$ או "
            "שכחת הסימן השלילי על $u_2 = -2$ m/s.\n\n"
            "**טיפ לבחינה:** אמתו באנרגיה: $KE_i = 26$ J ו-$KE_f = 26$ J. "
            "שוויון KE מאשר התנגשות אלסטית. "
            "בבגרות, כתבו את הנוסחאות לפני הצבת מספרים — זה שווה נקודות חלקיות גם אם החשבון מתקלקל."
        ),
    },
    8: {
        "en": (
            "This combines impulse with initial velocity to find final velocity. "
            "The bat applies impulse $J = F\\Delta t$ over 0.01 s.\n\n"
            "**Step 1 — Impulse:**\n"
            "$$J = 600 \\times 0.01 = 6\\text{ N·s}$$\n\n"
            "**Step 2 — Final velocity:**\n"
            "$$v_f = v_i + \\frac{J}{m} = -15 + \\frac{6}{0.3} = -15 + 20 = \\boxed{5\\text{ m/s}}$$\n\n"
            "The ball was moving at $-15$ m/s (toward the batter) and the bat's impulse adds "
            "20 m/s in the positive direction, reversing the ball's motion entirely.\n\n"
            "**Common wrong path:** Using $v_f = J/m = 20$ m/s without adding initial velocity, "
            "or computing $J = F/m$ instead of $J = F\\Delta t$.\n\n"
            "**Exam tip:** Draw a before/after velocity diagram. The impulse changes velocity by "
            "$\\Delta v = J/m = 20$ m/s — a large change because the ball is light (0.3 kg)."
        ),
        "he": (
            "בעיה זו משלבת מתקף עם מהירות ראשונית למציאת מהירות סופית. "
            "החבט מפעיל מתקף $J = F\\Delta t$ על פני 0.01 ש.\n\n"
            "**שלב 1 — מתקף:**\n"
            "$$J = 600 \\times 0.01 = 6\\text{ N·s}$$\n\n"
            "**שלב 2 — מהירות סופית:**\n"
            "$$v_f = v_i + \\frac{J}{m} = -15 + \\frac{6}{0.3} = -15 + 20 = \\boxed{5\\text{ m/s}}$$\n\n"
            "הכדור נע ב-$-15$ m/s (לכיוון החובט) והמתקף של החבט מוסיף "
            "20 m/s בכיוון החיובי, מהפך את תנועת הכדור לחלוטין.\n\n"
            "**טעות נפוצה:** שימוש ב-$v_f = J/m = 20$ m/s בלי הוספת מהירות ראשונית, "
            "או חישוב $J = F/m$ במקום $J = F\\Delta t$.\n\n"
            "**טיפ לבחינה:** שרטטו דיאגרמת מהירות לפני/אחרי. המתקף משנה מהירות ב-"
            "$\\Delta v = J/m = 20$ m/s — שינוי גדול כי הכדור קל (0.3 kg)."
        ),
    },
}


def build_lesson():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    # --- intro ---
    intro_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "intro")
    data["sections"][intro_idx]["body_en_md"] = (
        "**Momentum** is the 'quantity of motion' of an object — it captures both how much mass is moving "
        "and how fast. Unlike speed alone, momentum is a vector: it has magnitude $p = mv$ and direction "
        "matching the velocity.\n\n"
        "Everyday examples that build intuition:\n"
        "- A slow-moving freight train is hard to stop (large mass, moderate velocity).\n"
        "- A bullet is hard to stop (small mass, enormous velocity).\n"
        "- A parked car has zero momentum — no motion means $p = 0$.\n\n"
        "**Bagrut relevance (questionnaire 1):**\n"
        "- Collision problems (balls, cars, bullets embedding in blocks)\n"
        "- Explosion and recoil problems (person jumping off skateboard, gun firing)\n"
        "- Impulse from a bat, kick, or wall during contact\n\n"
        "**Key insight:** Newton's original 2nd law was written in terms of momentum, not acceleration:\n"
        "$$\\vec{F}_{\\text{net}} = \\frac{d\\vec{p}}{dt}$$\n"
        "For constant mass, this reduces to the familiar $F = ma$. Momentum is the more general formulation "
        "and explains why conservation laws work so cleanly in collision problems on Bagrut."
    )
    data["sections"][intro_idx]["body_he_md"] = (
        "**תנע** הוא 'כמות התנועה' של גוף — הוא לוכד גם את כמות המסה וגם את המהירות. "
        "בניגוד למהירות בלבד, תנע הוא וקטור: יש לו גודל $p = mv$ וכיוון התואם למהירות.\n\n"
        "דוגמאות מהחיים שבונות אינטואיציה:\n"
        "- רכבת משא איטית קשה לעצירה (מסה גדולה, מהירות בינונית).\n"
        "- כדור נשק קשה לעצירה (מסה קטנה, מהירות עצומה).\n"
        "- מכונית חונה: תנע אפס — אין תנועה אז $p = 0$.\n\n"
        "**רלוונטיות לבגרות (שאלון 1):**\n"
        "- בעיות התנגשות (כדורים, מכוניות, כדורי נשק שנתקעים בגוש)\n"
        "- בעיות פיצוץ ורתיעה (אדם קופץ מסקייטבורד, ירי מתותח)\n"
        "- מתקף מחבט, בעיטה, או קיר במהלך מגע\n\n"
        "**תובנה מרכזית:** החוק השני של ניוטון נכתב במקור בצורת תנע:\n"
        "$$\\vec{F}_{\\text{נטו}} = \\frac{d\\vec{p}}{dt}$$\n"
        "למסה קבועה, זה מתכווץ ל-$F = ma$ המוכר. תנע הוא הניסוח הכללי יותר "
        "ומסביר מדוע חוקי שימור עובדים כל כך נקי בבעיות התנגשות בבגרות."
    )

    # --- definition ---
    def_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "definition")
    data["sections"][def_idx]["body_en_md"] = (
        "**Momentum** measures how hard it is to stop a moving object:\n"
        "$$\\boxed{\\vec{p} = m\\vec{v}}$$\n"
        "- Direction: same as $\\vec{v}$ (vector quantity).\n"
        "- SI Unit: kg·m/s (equivalent to N·s).\n\n"
        "**Impulse** is the change in momentum delivered by a force over time:\n"
        "$$\\boxed{\\vec{J} = \\vec{F}\\,\\Delta t = \\Delta\\vec{p} = m\\vec{v}_f - m\\vec{v}_i}$$\n"
        "- SI Unit: N·s = kg·m/s.\n"
        "- For varying force: $J = \\int F\\,dt$ = area under the $F$-$t$ graph.\n"
        "- A large force over a short time (bat hitting ball) can equal a small force over long time.\n\n"
        "**Conservation of Momentum:** For an **isolated system** (no net external force):\n"
        "$$\\boxed{\\vec{p}_{\\text{total}} = \\sum_i m_i\\vec{v}_i = \\text{constant}}$$\n"
        "$$m_1\\vec{v}_{1i} + m_2\\vec{v}_{2i} = m_1\\vec{v}_{1f} + m_2\\vec{v}_{2f}$$\n\n"
        "**Elastic collision:** Momentum AND kinetic energy conserved.\n\n"
        "**Perfectly inelastic collision:** Objects stick together; only momentum conserved:\n"
        "$$m_1 v_{1i} + m_2 v_{2i} = (m_1 + m_2)v_f$$\n\n"
        "**Partially inelastic:** Momentum conserved, some KE lost to heat/deformation.\n\n"
        "**When to use which law:** If the problem mentions 'stick together' or 'embed', use inelastic momentum. "
        "If it says 'elastic' or 'billiard balls', use both momentum and KE. If it gives force and time, use impulse."
    )
    data["sections"][def_idx]["body_he_md"] = (
        "**תנע** מודד כמה קשה לעצור גוף בתנועה:\n"
        "$$\\boxed{\\vec{p} = m\\vec{v}}$$\n"
        "- כיוון: כמו $\\vec{v}$ (גודל וקטורי).\n"
        "- יחידת SI: kg·m/s (שקול ל-N·s).\n\n"
        "**מתקף** הוא שינוי בתנע שנגרם על ידי כוח לאורך זמן:\n"
        "$$\\boxed{\\vec{J} = \\vec{F}\\,\\Delta t = \\Delta\\vec{p} = m\\vec{v}_f - m\\vec{v}_i}$$\n"
        "- יחידת SI: N·s = kg·m/s.\n"
        "- לכוח משתנה: $J = \\int F\\,dt$ = שטח תחת גרף $F$-$t$.\n"
        "- כוח גדול לזמן קצר (חבט פוגע בכדור) יכול להיות שווה לכוח קטן לזמן ארוך.\n\n"
        "**שימור תנע:** ל**מערכת מבודדת** (אין כוח חיצוני נטו):\n"
        "$$\\boxed{\\vec{p}_{\\text{כולל}} = \\sum_i m_i\\vec{v}_i = \\text{const}}$$\n"
        "$$m_1\\vec{v}_{1i} + m_2\\vec{v}_{2i} = m_1\\vec{v}_{1f} + m_2\\vec{v}_{2f}$$\n\n"
        "**התנגשות אלסטית:** תנע ואנרגיה קינטית שניהם נשמרים.\n\n"
        "**התנגשות לא-אלסטית לחלוטין:** גופים נצמדים; רק תנע נשמר:\n"
        "$$m_1 v_{1i} + m_2 v_{2i} = (m_1 + m_2)v_f$$\n\n"
        "**לא-אלסטית חלקית:** תנע נשמר, חלק מה-KE הולך לחום/עיוות.\n\n"
        "**מתי להשתמש באיזה חוק:** אם השאלה מזכירה 'נצמדים' או 'מתקע', השתמשו בשימור תנע לא-אלסטי. "
        "אם נאמר 'אלסטי' או 'כדורי ביליארד', השתמשו גם בתנע וגם ב-KE. אם נותנים כוח וזמן, השתמשו במתקף."
    )

    # --- theory ---
    th_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "theory")
    data["sections"][th_idx]["body_en_md"] = (
        "Bagrut momentum problems fall into three categories: impulse, inelastic collision, and elastic collision. "
        "Recognizing which type you face determines which equations to use.\n\n"
        "### Derivation from Newton's 3rd Law\n\n"
        "When two objects interact internally (e.g. collide), Newton's 3rd law gives:\n"
        "$$\\vec{F}_{1\\to2} = -\\vec{F}_{2\\to1}$$\n\n"
        "By Newton's 2nd law: $\\vec{F}_{1\\to2} = \\frac{d\\vec{p}_2}{dt}$ and "
        "$\\vec{F}_{2\\to1} = \\frac{d\\vec{p}_1}{dt}$.\n\n"
        "Adding: $\\frac{d\\vec{p}_1}{dt} + \\frac{d\\vec{p}_2}{dt} = 0 "
        "\\Rightarrow \\frac{d(\\vec{p}_1+\\vec{p}_2)}{dt} = 0 "
        "\\Rightarrow \\vec{p}_{\\text{total}} = \\text{const}.$\n\n"
        "Internal forces always cancel in pairs — only external forces can change total momentum.\n\n"
        "### Elastic collision formulas (1D)\n\n"
        "For two masses $m_1$, $m_2$ with initial velocities $u_1$, $u_2$:\n"
        "$$v_1 = \\frac{(m_1-m_2)u_1 + 2m_2 u_2}{m_1+m_2}, \\quad "
        "v_2 = \\frac{(m_2-m_1)u_2 + 2m_1 u_1}{m_1+m_2}$$\n\n"
        "**Special case — equal masses ($m_1 = m_2$):** $v_1 = u_2$, $v_2 = u_1$ (velocities exchange!).\n\n"
        "### Elastic vs Inelastic\n\n"
        "| Type | Momentum | KE | Example |\n"
        "|---|---|---|---|\n"
        "| Elastic | Conserved | Conserved | Billiard balls, Newton's cradle |\n"
        "| Inelastic | Conserved | Not conserved | Clay hitting clay |\n"
        "| Perfectly inelastic | Conserved | Minimized | Car crash, bullet in block |\n\n"
        "The energy 'lost' in inelastic collisions goes to heat, sound, and permanent deformation — "
        "it is not destroyed, just converted to non-mechanical forms."
    )
    data["sections"][th_idx]["body_he_md"] = (
        "בעיות תנע בבגרות נחלקות לשלוש קטגוריות: מתקף, התנגשות לא-אלסטית, והתנגשות אלסטית. "
        "זיהוי הסוג קובע אילו משוואות להשתמש.\n\n"
        "### גזירה מהחוק השלישי של ניוטון\n\n"
        "כששני גופים מתקשרים פנימית (למשל מתנגשים), החוק השלישי נותן:\n"
        "$$\\vec{F}_{1\\to2} = -\\vec{F}_{2\\to1}$$\n\n"
        "לפי החוק השני: $\\vec{F}_{1\\to2} = \\frac{d\\vec{p}_2}{dt}$ ו-"
        "$\\vec{F}_{2\\to1} = \\frac{d\\vec{p}_1}{dt}$.\n\n"
        "חיבור: $\\frac{d\\vec{p}_1}{dt} + \\frac{d\\vec{p}_2}{dt} = 0 "
        "\\Rightarrow \\vec{p}_{\\text{כולל}} = \\text{const}.$\n\n"
        "כוחות פנימיים תמיד מתבטלים בזוגות — רק כוחות חיצוניים יכולים לשנות תנע כולל.\n\n"
        "### נוסחאות התנגשות אלסטית (1D)\n\n"
        "לשתי מסות $m_1$, $m_2$ עם מהירויות $u_1$, $u_2$:\n"
        "$$v_1 = \\frac{(m_1-m_2)u_1 + 2m_2 u_2}{m_1+m_2}, \\quad "
        "v_2 = \\frac{(m_2-m_1)u_2 + 2m_1 u_1}{m_1+m_2}$$\n\n"
        "**מקרה מיוחד — מסות שוות:** $v_1 = u_2$, $v_2 = u_1$ (מהירויות מתחלפות!).\n\n"
        "### אלסטית מול לא-אלסטית\n\n"
        "| סוג | תנע | אנרגיה קינטית | דוגמה |\n"
        "|---|---|---|---|\n"
        "| אלסטית | נשמר | נשמר | כדורי ביליארד, עריסת ניוטון |\n"
        "| לא-אלסטית | נשמר | לא נשמר | חימר פוגע בחימר |\n"
        "| לא-אלסטית לחלוטין | נשמר | מינימלי | תאונת דרכים, כדור בגוש |\n\n"
        "ה'אנרגיה שאבדה' בהתנגשויות לא-אלסטיות הולכת לחום, קול ועיוות קבוע — "
        "היא לא נהרסת, רק מומרת לצורות לא-מכניות."
    )

    # --- worked examples ---
    we_indices = [i for i, s in enumerate(data["sections"]) if s["kind"] == "worked_example"]

    data["sections"][we_indices[0]]["body_en_md"] = (
        "**Given:** A 2 kg ball moving at $v_1 = 5\\text{ m/s}$ (east) hits a stationary 3 kg ball "
        "and they stick together.\n\n**Find:** Final velocity of the combined object.\n\n"
        "This is a perfectly inelastic collision — use conservation of momentum with combined mass.\n\n"
        "### Move 1 — Define positive direction\n\n"
        "East = positive. The stationary ball has $v_{2i} = 0$.\n\n"
        "### Move 2 — Initial momentum\n"
        "$$p_{\\text{before}} = m_1 v_{1i} + m_2 v_{2i} = 2(5) + 3(0) = 10\\text{ kg·m/s}$$\n\n"
        "### Move 3 — Final momentum and solve\n"
        "$$p_{\\text{after}} = (m_1 + m_2)v_f = 5v_f$$\n"
        "$$5v_f = 10 \\Rightarrow \\boxed{v_f = 2\\text{ m/s (east)}}$$\n\n"
        "### Move 4 — Energy check (not conserved)\n"
        "$$KE_i = \\frac{1}{2}(2)(25) = 25\\text{ J}, \\quad "
        "KE_f = \\frac{1}{2}(5)(4) = 10\\text{ J}$$\n"
        "$$\\Delta KE = -15\\text{ J}\\text{ (lost to deformation and heat)}$$\n\n"
        "**Bagrut note:** Always compute KE change in inelastic problems — examiners often ask "
        "what fraction of energy was lost. Here 60% of initial KE vanished.\n\n"
        "**Physical reading:** The lighter ball carried all initial momentum (10 kg·m/s). "
        "After sticking, the combined 5 kg mass moves slower — momentum conserved, energy not.\n\n"
        "**Strategy:** Write $p_{\\text{before}}$ and $p_{\\text{after}}$ on separate lines before equating."
    )
    data["sections"][we_indices[0]]["body_he_md"] = (
        "**נתון:** כדור 2 kg ב-$v_1=5\\text{ m/s}$ (מזרחה) פוגע בכדור 3 kg במנוחה ונצמד אליו.\n\n"
        "**מצא:** מהירות סופית של הגוף המשולב.\n\n"
        "זו התנגשות לא-אלסטית לחלוטין — השתמשו בשימור תנע עם מסה משולבת.\n\n"
        "### צעד 1 — הגדרת כיוון חיובי\n\n"
        "מזרח = חיובי. הכדור במנוחה: $v_{2i} = 0$.\n\n"
        "### צעד 2 — תנע ראשוני\n"
        "$$p_{\\text{לפני}} = 2(5) + 3(0) = 10\\text{ kg·m/s}$$\n\n"
        "### צעד 3 — תנע סופי ופתרון\n"
        "$$p_{\\text{אחרי}} = 5v_f, \\quad 5v_f = 10 \\Rightarrow \\boxed{v_f = 2\\text{ m/s (מזרח)}}$$\n\n"
        "### צעד 4 — בדיקת אנרגיה (לא נשמרת)\n"
        "$$KE_i = 25\\text{ J}, \\quad KE_f = 10\\text{ J}, \\quad \\Delta KE = -15\\text{ J}$$\n\n"
        "**הערת בגרות:** תמיד חשבו שינוי KE בבעיות לא-אלסטיות — בוחנים לעיתים שואלים "
        "איזה שבר מהאנרגיה אבד. כאן 60% מה-KE הראשונית נעלמו.\n\n"
        "**קריאה פיזיקלית:** הכדור הקל נשא את כל התנע הראשוני (10 kg·m/s). "
        "אחרי הצמדה, המסה המשולבת 5 kg נעה לאט יותר — תנע נשמר, אנרגיה לא.\n\n"
        "**אסטרטגיה:** כתבו $p_{\\text{לפני}}$ ו-$p_{\\text{אחרי}}$ בשורות נפרדות לפני השוואה."
    )

    data["sections"][we_indices[1]]["body_en_md"] = (
        "**Given:** A 0.1 kg bullet moving at 400 m/s embeds itself in a 10 kg stationary wooden block.\n\n"
        "**Find:** (a) Final velocity of bullet+block. (b) Kinetic energy lost.\n\n"
        "Bullet embedding is the classic Bagrut perfectly inelastic collision — "
        "the combined mass moves together after impact.\n\n"
        "### Move 1 — Conservation of momentum\n"
        "$$m_{\\text{bullet}} v_{\\text{bullet}} = (m_{\\text{bullet}} + m_{\\text{block}})v_f$$\n"
        "$$0.1 \\times 400 = 10.1\\, v_f \\Rightarrow \\boxed{v_f = \\frac{40}{10.1} \\approx 3.96\\text{ m/s}}$$\n\n"
        "### Move 2 — Initial kinetic energy\n"
        "$$KE_i = \\frac{1}{2}(0.1)(400)^2 = 8000\\text{ J}$$\n\n"
        "### Move 3 — Final kinetic energy\n"
        "$$KE_f = \\frac{1}{2}(10.1)(3.96)^2 \\approx 79.2\\text{ J}$$\n\n"
        "### Move 4 — Energy lost\n"
        "$$\\Delta KE = 8000 - 79.2 \\approx \\boxed{7921\\text{ J}} \\text{ (~99\\% lost)}$$\n\n"
        "**Physical reading:** Nearly all the bullet's kinetic energy converts to heat and "
        "permanent deformation of the wood. Only ~1% remains as motion of the combined system.\n\n"
        "**Bagrut strategy:** The bullet's mass (0.1 kg) is negligible compared to the block (10 kg), "
        "so $v_f \\approx 40/10 = 4$ m/s is a quick estimate — always verify with exact calculation.\n\n"
        "**Units check:** Bullet momentum $= 0.1 \\times 400 = 40$ kg·m/s; this equals combined momentum after."
    )
    data["sections"][we_indices[1]]["body_he_md"] = (
        "**נתון:** כדור נשק 0.1 kg ב-400 m/s מתקע בגוש עץ 10 kg במנוחה.\n\n"
        "**מצא:** (א) מהירות סופית. (ב) אנרגיה קינטית שאבדה.\n\n"
        "התקעת כדור נשק היא ההתנגשות הלא-אלסטית הקלאסית בבגרות — "
        "המסה המשולבת נעה יחד אחרי הפגיעה.\n\n"
        "### צעד 1 — שימור תנע\n"
        "$$0.1 \\times 400 = 10.1 \\times v_f \\Rightarrow \\boxed{v_f \\approx 3.96\\text{ m/s}}$$\n\n"
        "### צעד 2 — KE ראשונית\n"
        "$$KE_i = \\frac{1}{2}(0.1)(400)^2 = 8000\\text{ J}$$\n\n"
        "### צעד 3 — KE סופית\n"
        "$$KE_f \\approx 79.2\\text{ J}$$\n\n"
        "### צעד 4 — אנרגיה שאבדה\n"
        "$$\\Delta KE \\approx \\boxed{7921\\text{ J}} \\text{ (~99\\% אבד)}$$\n\n"
        "**קריאה פיזיקלית:** כמעט כל האנרגיה הקינטית של הכדור מומרת לחום ועיוות קבוע של העץ. "
        "רק ~1% נשאר כתנועה של המערכת המשולבת.\n\n"
        "**אסטרטגיית בגרות:** מסת הכדור (0.1 kg) זניחה לעומת הגוש (10 kg), "
        "אז $v_f \\approx 40/10 = 4$ m/s היא הערכה מהירה — תמיד אמתו בחישוב מדויק.\n\n"
        "**בדיקת יחידות:** תנע הכדור $= 0.1 \\times 400 = 40$ kg·m/s; שווה לתנע המשולב אחרי."
    )

    data["sections"][we_indices[2]]["body_en_md"] = (
        "**Given:** Mass $m$ moving at $u$ collides elastically with identical mass $m$ at rest.\n\n"
        "**Claim:** The first mass stops and the second moves at velocity $u$.\n\n"
        "**Proof using both conservation laws:**\n\n"
        "Let final velocities be $v_1$ and $v_2$.\n\n"
        "**Conservation of momentum:**\n"
        "$$mu = mv_1 + mv_2 \\Rightarrow \\boxed{u = v_1 + v_2} \\tag{1}$$\n\n"
        "**Conservation of kinetic energy:**\n"
        "$$\\frac{1}{2}mu^2 = \\frac{1}{2}mv_1^2 + \\frac{1}{2}mv_2^2 "
        "\\Rightarrow \\boxed{u^2 = v_1^2 + v_2^2} \\tag{2}$$\n\n"
        "**From (1):** $v_2 = u - v_1$. Substitute into (2):\n"
        "$$u^2 = v_1^2 + (u-v_1)^2 = 2v_1^2 - 2uv_1 + u^2$$\n"
        "$$0 = 2v_1(v_1 - u)$$\n\n"
        "Solutions: $v_1 = 0$ (physical — collision occurred) or $v_1 = u$ (trivial — no collision).\n\n"
        "$$\\boxed{v_1 = 0, \\quad v_2 = u}$$\n\n"
        "**The velocities exchange.** This explains Newton's cradle: when the end ball hits the row, "
        "momentum travels through and the far ball launches at the same speed.\n\n"
        "**Bagrut shortcut:** For equal masses in 1D elastic collision, just swap the velocities.\n\n"
        "**Verification:** Substitute back: $KE_i = \\frac{1}{2}mu^2$ and "
        "$KE_f = 0 + \\frac{1}{2}mu^2 = KE_i$ — energy is conserved, confirming elastic collision.\n\n"
        "**Exam context:** This result appears in Newton's cradle and equal-mass billiard ball problems on Bagrut."
    )
    data["sections"][we_indices[2]]["body_he_md"] = (
        "**נתון:** מסה $m$ ב-$u$ מתנגשת אלסטית עם מסה שווה $m$ במנוחה.\n\n"
        "**טענה:** המסה הראשונה עוצרת והשנייה נעה ב-$u$.\n\n"
        "**הוכחה משני חוקי שימור:**\n\n"
        "יהיו $v_1$, $v_2$ המהירויות הסופיות.\n\n"
        "**שימור תנע:**\n"
        "$$u = v_1 + v_2 \\tag{1}$$\n\n"
        "**שימור אנרגיה:**\n"
        "$$u^2 = v_1^2 + v_2^2 \\tag{2}$$\n\n"
        "**מ-(1):** $v_2 = u-v_1$. מציבים ב-(2):\n"
        "$$0 = 2v_1(v_1 - u)$$\n\n"
        "פתרונות: $v_1 = 0$ (פיזיקלי — התנגשות התרחשה) או $v_1 = u$ (טריוויאלי — ללא התנגשות).\n\n"
        "$$\\boxed{v_1 = 0, \\quad v_2 = u}$$\n\n"
        "**המהירויות מתחלפות.** זה מסביר את עריסת ניוטון: כשהכדור הקצה פוגע בשורה, "
        "התנע עובר והכדור הרחוק מושק ב אותה מהירות.\n\n"
        "**קיצור בגרות:** למסות שוות בהתנגשות אלסטית 1D, פשוט החליפו מהירויות.\n\n"
        "**אימות:** הצבה חזרה: $KE_i = \\frac{1}{2}mu^2$ ו-$KE_f = 0 + \\frac{1}{2}mu^2 = KE_i$ — "
        "אנרגיה נשמרת, מאשר התנגשות אלסטית.\n\n"
        "**הקשר לבחינה:** תוצאה זו מופיעה בעריסת ניוטון ובבעיות כדורי ביליארד במסות שוות בבגרות."
    )

    # --- checkpoints ---
    cp_indices = [i for i, s in enumerate(data["sections"]) if s["kind"] == "checkpoint"]
    data["sections"][cp_indices[0]]["checkpoint_solution_en"] = (
        "Perfectly inelastic collision: a 5 kg cart at 4 m/s hits a stationary 3 kg cart; they stick together.\n\n"
        "**Step 1 — Define positive direction** along the initial motion.\n\n"
        "**Step 2 — Initial momentum:**\n"
        "$$p_{\\text{before}} = m_1 v_1 + m_2 v_2 = 5(4) + 3(0) = 20\\text{ kg·m/s}$$\n\n"
        "**Step 3 — Conservation:**\n"
        "$$p_{\\text{after}} = (5+3)v_f = 8v_f$$\n"
        "$$8v_f = 20 \\Rightarrow \\boxed{v_f = 2.5\\text{ m/s}}$$\n\n"
        "**Check:** The final speed (2.5 m/s) is less than the initial (4 m/s) because "
        "momentum is shared with the added mass — this is always true in inelastic collisions.\n\n"
        "**Energy note:** $KE_i = 40$ J, $KE_f = \\frac{1}{2}(8)(6.25) = 25$ J. "
        "About 37.5% of kinetic energy was lost to deformation during the collision.\n\n"
        "**Quick method:** $v_f = p_{\\text{total}} / m_{\\text{total}} = 20/8 = 2.5$ m/s directly.\n\n"
        "**Direction:** The combined carts move in the same direction as the heavier initial motion (east/forward)."
    )
    data["sections"][cp_indices[0]]["checkpoint_solution_he"] = (
        "התנגשות לא-אלסטית לחלוטין: עגלה 5 kg ב-4 m/s פוגעת בעגלה 3 kg עומדת; מתחברות.\n\n"
        "**שלב 1 — הגדרת כיוון חיובי** לאורך התנועה הראשונית.\n\n"
        "**שלב 2 — תנע ראשוני:**\n"
        "$$p_{\\text{לפני}} = 5(4) + 3(0) = 20\\text{ kg·m/s}$$\n\n"
        "**שלב 3 — שימור:**\n"
        "$$8v_f = 20 \\Rightarrow \\boxed{v_f = 2.5\\text{ m/s}}$$\n\n"
        "**בדיקה:** המהירות הסופית (2.5 m/s) קטנה מהראשונית (4 m/s) כי "
        "התנע מתחלק עם המסה שנוספה — תמיד נכון בהתנגשויות לא-אלסטיות.\n\n"
        "**הערת אנרגיה:** $KE_i = 40$ J, $KE_f = 25$ J. "
        "כ-37.5% מהאנרגיה הקינטית אבדו לעיוות במהלך ההתנגשות.\n\n"
        "**שיטה מהירה:** $v_f = p_{\\text{כולל}} / m_{\\text{כולל}} = 20/8 = 2.5$ m/s ישירות.\n\n"
        "**כיוון:** העגלות המשולבות נעות באותו כיוון כמו התנועה הראשונית הדומיננטית."
    )
    data["sections"][cp_indices[1]]["checkpoint_solution_en"] = (
        "A 0.5 kg ball at 10 m/s (right) hits a 1.5 kg stationary ball; they stick together.\n\n"
        "**Step 1 — Momentum conservation:**\n"
        "$$v_f = \\frac{(0.5)(10)}{0.5+1.5} = \\frac{5}{2} = \\boxed{2.5\\text{ m/s}}$$\n\n"
        "**Step 2 — Initial KE:**\n"
        "$$KE_i = \\frac{1}{2}(0.5)(100) = 25\\text{ J}$$\n\n"
        "**Step 3 — Final KE:**\n"
        "$$KE_f = \\frac{1}{2}(2)(6.25) = 6.25\\text{ J}$$\n\n"
        "**Step 4 — Fraction lost:**\n"
        "$$\\frac{KE_i - KE_f}{KE_i} = \\frac{25 - 6.25}{25} = \\boxed{75\\%}$$\n\n"
        "**Check:** 75% energy loss is typical when a light object hits a heavier stationary one "
        "and they stick — most KE goes to deformation.\n\n"
        "**Momentum check:** Initial $p = 0.5 \\times 10 = 5$ kg·m/s. "
        "Final $p = 2 \\times 2.5 = 5$ kg·m/s — momentum is conserved exactly.\n\n"
        "**Fraction lost formula:** $\\frac{KE_i - KE_f}{KE_i} = 1 - \\frac{KE_f}{KE_i}$ — memorize this for Bagrut.\n\n"
        "**Direction:** Final velocity 2.5 m/s to the right — same as the lighter ball's initial direction."
    )
    data["sections"][cp_indices[1]]["checkpoint_solution_he"] = (
        "כדור 0.5 kg ב-10 m/s (ימינה) פוגע בכדור 1.5 kg עומד; נצמדים.\n\n"
        "**שלב 1 — שימור תנע:**\n"
        "$$v_f = \\frac{5}{2} = \\boxed{2.5\\text{ m/s}}$$\n\n"
        "**שלב 2 — KE ראשונית:**\n"
        "$$KE_i = 25\\text{ J}$$\n\n"
        "**שלב 3 — KE סופית:**\n"
        "$$KE_f = 6.25\\text{ J}$$\n\n"
        "**שלב 4 — שבר שאבד:**\n"
        "$$\\frac{25 - 6.25}{25} = \\boxed{75\\%}$$\n\n"
        "**בדיקה:** אובדן 75% אנרגיה טיפוסי כשגוף קל פוגע בכבד עומד ונצמד — "
        "רוב ה-KE הולך לעיוות.\n\n"
        "**בדיקת תנע:** ראשוני $p = 0.5 \\times 10 = 5$ kg·m/s. "
        "סופי $p = 2 \\times 2.5 = 5$ kg·m/s — תנע נשמר בדיוק.\n\n"
        "**נוסחת שבר אובדן:** $\\frac{KE_i - KE_f}{KE_i} = 1 - \\frac{KE_f}{KE_i}$ — שיננו לבגרות.\n\n"
        "**כיוון:** מהירות סופית 2.5 m/s ימינה — כמו כיוון הכדור הקל הראשוני."
    )

    # --- method_guide ---
    mg_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "method_guide")
    data["sections"][mg_idx]["body_en_md"] = (
        "Follow this systematic approach for every momentum problem on Bagrut:\n\n"
        "1. **Identify the system.** Are external forces negligible during the interaction? "
        "Collisions are brief — gravity and friction are usually negligible. Recoil on frictionless "
        "surface: yes. Pushing a box slowly: no.\n\n"
        "2. **Choose a positive direction** and state it clearly on your paper.\n\n"
        "3. **Write initial momenta** for each object. Include signs! A ball moving left has "
        "negative momentum if right is positive.\n\n"
        "4. **Identify collision type:** elastic (KE conserved), perfectly inelastic (stick together), "
        "or partially inelastic.\n\n"
        "5. **Apply conservation of momentum:** $\\sum p_i = \\sum p_f$.\n\n"
        "6. **For elastic collisions:** also apply $\\sum KE_i = \\sum KE_f$ — gives a second equation.\n\n"
        "7. **Solve** the system of equations for unknowns.\n\n"
        "8. **Calculate KE change** if asked: $\\Delta KE = KE_f - KE_i \\leq 0$ in inelastic cases.\n\n"
        "9. **Sanity check:** Is the direction of final velocity sensible? Is the speed reasonable?"
    )
    data["sections"][mg_idx]["body_he_md"] = (
        "עקבו אחר גישה שיטתית זו לכל בעיית תנע בבגרות:\n\n"
        "1. **זהו את המערכת.** האם כוחות חיצוניים זניחים במהלך האינטראקציה? "
        "התנגשויות קצרות — כבידה וחיכוך בדרך כלל זניחים. רתיעה על משטח חלק: כן. "
        "דחיפת קופסה לאט: לא.\n\n"
        "2. **בחרו כיוון חיובי** והצהירו עליו בבירור על הדף.\n\n"
        "3. **כתבו תנעים ראשוניים** לכל גוף. כולל סימנים! כדור שנע שמאלה בעל תנע שלילי "
        "אם ימין חיובי.\n\n"
        "4. **זהו סוג התנגשות:** אלסטית (KE נשמר), לא-אלסטית לחלוטין (נצמדים), "
        "או לא-אלסטית חלקית.\n\n"
        "5. **יישמו שימור תנע:** $\\sum p_i = \\sum p_f$.\n\n"
        "6. **להתנגשות אלסטית:** גם $\\sum KE_i = \\sum KE_f$ — משוואה שנייה.\n\n"
        "7. **פתרו** את מערכת המשוואות.\n\n"
        "8. **חשבו שינוי KE** אם נדרש: $\\Delta KE \\leq 0$ במקרים לא-אלסטיים.\n\n"
        "9. **בדיקת הגיון:** האם כיוון המהירות הסופית הגיוני? האם המהירות סבירה?"
    )

    # --- pitfall ---
    pit_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "pitfall")
    data["sections"][pit_idx]["body_en_md"] = (
        "1. **Applying conservation of momentum when external forces are not negligible.** "
        "Gravity and friction are external. During brief collisions they are small compared to "
        "impact forces — but for slow processes (pushing, sliding on rough surface), include them.\n\n"
        "2. **Forgetting signs.** Momentum is a vector. Always define positive direction first. "
        "A ball at $-5$ m/s has negative momentum if $+$ is right.\n\n"
        "3. **Confusing 'elastic' with 'bouncing'.** Elastic means both momentum AND KE conserved. "
        "A ball bouncing off a wall loses some KE as sound — it is not perfectly elastic.\n\n"
        "4. **Using wrong mass in KE after inelastic collision.** After sticking, use combined mass "
        "$m_1 + m_2$ in $KE_f = \\frac{1}{2}(m_1+m_2)v_f^2$, not individual masses.\n\n"
        "5. **Impulse = force only (forgetting time).** $J = F\\Delta t$, not $F$ alone. "
        "Units are N·s, not N.\n\n"
        "6. **Assuming KE is conserved in inelastic collisions.** Never assume energy conservation "
        "unless the problem says 'elastic'. In inelastic cases, compute $\\Delta KE$ explicitly.\n\n"
        "7. **Mixing up $v_f = v_1 + v_2$ with momentum conservation.** Average velocity is wrong; "
        "always use $m_1 v_1 + m_2 v_2 = (m_1+m_2)v_f$ for sticking collisions."
    )
    data["sections"][pit_idx]["body_he_md"] = (
        "1. **שימוש בשימור תנע כשכוחות חיצוניים לא זניחים.** "
        "כבידה וחיכוך הם חיצוניים. בהתנגשויות קצרות הם קטנים — אך בתהליכים איטיים (דחיפה, החלקה), "
        "יש לכלול אותם.\n\n"
        "2. **שכחת סימנים.** תנע הוא וקטור. תמיד הגדירו כיוון חיובי קודם. "
        "כדור ב-$-5$ m/s בעל תנע שלילי אם $+$ הוא ימינה.\n\n"
        "3. **ערבוב 'אלסטי' ו'קופץ'.** אלסטי = תנע ו-KE שניהם נשמרים. "
        "כדור שקופץ מקיר מאבד KE כקול — לא אלסטי לחלוטין.\n\n"
        "4. **שימוש במסה שגויה ב-KE לאחר התנגשות לא-אלסטית.** אחרי הצמדה, "
        "השתמשו ב-$m_1+m_2$ ב-$KE_f$, לא במסות בודדות.\n\n"
        "5. **מתקף = כוח בלבד (שכחת זמן).** $J = F\\Delta t$, לא $F$ לבד. "
        "יחידות: N·s, לא N.\n\n"
        "6. **הנחת שימור KE בהתנגשות לא-אלסטית.** לעולם אל תניחו שימור אנרגיה "
        "אלא אם נאמר 'אלסטי'. במקרים לא-אלסטיים, חשבו $\\Delta KE$ במפורש.\n\n"
        "7. **ערבוב $v_f = v_1 + v_2$ עם שימור תנע.** ממוצע מהירויות שגוי; "
        "תמיד $m_1 v_1 + m_2 v_2 = (m_1+m_2)v_f$ להתנגשויות עם הצמדה."
    )

    # --- why_matters ---
    wm_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "why_matters")
    data["sections"][wm_idx]["body_en_md"] = (
        "Momentum is one of the most powerful tools in Bagrut Physics — it connects directly to "
        "collisions, explosions, rocket propulsion, and even modern particle physics.\n\n"
        "**You will use this to unlock:**\n"
        "- `concept:collisions` — advanced 2D collisions and center-of-mass frame\n"
        "- `concept:angular_momentum` — rotational analog of linear momentum\n\n"
        "**Builds on:**\n"
        "- `concept:work_energy` — KE conservation in elastic collisions\n"
        "- `concept:newton_laws` — derivation of conservation from Newton's 3rd law\n\n"
        "**Why it matters for exams:** Bagrut questionnaire 1 almost always includes at least one "
        "momentum problem worth 8–15 points. The skill of choosing the right conservation law "
        "and handling signs correctly separates strong from weak students."
    )
    data["sections"][wm_idx]["body_he_md"] = (
        "תנע הוא אחד הכלים החזקים ביותר בפיזיקת בגרות — הוא מתחבר ישירות להתנגשויות, "
        "פיצוצים, propulsion של רקטות, ואפילו פיזיקת חלקיקים מודרנית.\n\n"
        "**תשתמשו בזה להמשך:**\n"
        "- `concept:collisions` — התנגשויות 2D מתקדמות ומערכת מרכז מסה\n"
        "- `concept:angular_momentum` — האנלוגיה הסיבובית לתנע ליניארי\n\n"
        "**מבוסס על:**\n"
        "- `concept:work_energy` — שימור KE בהתנגשויות אלסטיות\n"
        "- `concept:newton_laws` — גזירת השימור מהחוק השלישי\n\n"
        "**למה חשוב לבחינות:** בגרות שאלון 1 כמעט תמיד כולל לפחות בעיית תנע אחת בשווי 8–15 נקודות. "
        "המיומנות לבחור את חוק השימור הנכון ולטפל בסימנים נכון מפרידה בין תלמידים חזקים לחלשים."
    )

    # --- before_exam ---
    be_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "before_exam")
    data["sections"][be_idx]["body_en_md"] = (
        "### Formula Sheet\n\n"
        "$$p = mv \\qquad J = F\\Delta t = \\Delta p \\qquad p_{\\text{total}} = \\text{const (isolated)}$$\n\n"
        "**Perfectly inelastic:** $m_1 v_{1i} + m_2 v_{2i} = (m_1+m_2)v_f$\n\n"
        "**Elastic (equal masses):** velocities exchange ($v_1 = u_2$, $v_2 = u_1$)\n\n"
        "**Elastic (general 1D):**\n"
        "$$v_1 = \\frac{(m_1-m_2)u_1+2m_2 u_2}{m_1+m_2}, \\quad "
        "v_2 = \\frac{(m_2-m_1)u_2+2m_1 u_1}{m_1+m_2}$$\n\n"
        "### Typical Bagrut patterns\n"
        "- *'Two carts collide and stick. Find final velocity and energy lost.'*\n"
        "- *'Bullet embeds in block. Find velocity and spring compression.'*\n"
        "- *'Person jumps off skateboard. Find recoil velocity.'*\n\n"
        "### Checklist\n"
        "- [ ] Positive direction defined?\n"
        "- [ ] All initial momenta have correct signs?\n"
        "- [ ] Collision type identified?\n"
        "- [ ] For elastic: KE equation used?\n"
        "- [ ] Units correct (kg·m/s)?\n\n"
        "**Last review:** Say each formula out loud once, then solve one checkpoint without looking. "
        "Practice defining positive direction before every collision problem."
    )
    data["sections"][be_idx]["body_he_md"] = (
        "### דף נוסחאות\n\n"
        "$$p = mv \\qquad J = F\\Delta t = \\Delta p \\qquad p_{\\text{כולל}} = \\text{const (מבודד)}$$\n\n"
        "**לא-אלסטית לחלוטין:** $m_1 v_{1i} + m_2 v_{2i} = (m_1+m_2)v_f$\n\n"
        "**אלסטית (מסות שוות):** מהירויות מתחלפות\n\n"
        "**אלסטית (כללי 1D):** נוסחאות לעיל\n\n"
        "### דפוסי בגרות אופייניים\n"
        "- *'שתי עגלות מתנגשות ונצמדות. מצא מהירות סופית ואנרגיה שאבדה.'*\n"
        "- *'כדור נשק מתקע בגוש. מצא מהירות ודחיסת קפיץ.'*\n"
        "- *'אדם קופץ מסקייטבורד. מצא מהירות רתיעה.'*\n\n"
        "### רשימת בדיקה\n"
        "- [ ] כיוון חיובי הוגדר?\n"
        "- [ ] כל התנעים הראשוניים עם סימנים נכונים?\n"
        "- [ ] סוג ההתנגשות זוהה?\n"
        "- [ ] להתנגשות אלסטית: משוואת KE נוספה?\n"
        "- [ ] יחידות נכונות (kg·m/s)?"
    )

    # --- summary ---
    sum_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "summary")
    data["sections"][sum_idx]["body_en_md"] = (
        "- **Momentum:** $\\vec{p} = m\\vec{v}$ (kg·m/s) — vector, direction matches velocity.\n"
        "- **Impulse:** $\\vec{J} = \\vec{F}\\Delta t = \\Delta\\vec{p}$ — links force, time, and velocity change.\n"
        "- **Conservation:** $\\sum p_i = \\sum p_f$ for isolated systems (no net external force).\n"
        "- **Perfectly inelastic:** objects stick; $(m_1+m_2)v_f = m_1 v_{1i} + m_2 v_{2i}$.\n"
        "- **Elastic — equal masses:** velocities exchange ($v_1 = u_2$, $v_2 = u_1$).\n"
        "- **Elastic — general 1D:** use the $v_1$, $v_2$ formulas with both $u_1$ and $u_2$.\n"
        "- **Energy loss:** $\\Delta KE = KE_f - KE_i \\leq 0$ in inelastic collisions.\n"
        "- **Why conserved:** Newton's 3rd law cancels internal forces in pairs.\n\n"
        "**Takeaway:** Classify the problem type first (impulse / inelastic / elastic), "
        "define positive direction, then apply the correct conservation law."
    )
    data["sections"][sum_idx]["body_he_md"] = (
        "- **תנע:** $\\vec{p} = m\\vec{v}$ (kg·m/s) — וקטור, כיוון תואם למהירות.\n"
        "- **מתקף:** $\\vec{J} = \\vec{F}\\Delta t = \\Delta\\vec{p}$ — מקשר כוח, זמן, ושינוי מהירות.\n"
        "- **שימור:** $\\sum p_i = \\sum p_f$ למערכות מבודדות (אין כוח חיצוני נטו).\n"
        "- **לא-אלסטית לחלוטין:** גופים נצמדים; $(m_1+m_2)v_f = m_1 v_{1i} + m_2 v_{2i}$.\n"
        "- **אלסטית — מסות שוות:** מהירויות מתחלפות.\n"
        "- **אלסטית — כללי 1D:** נוסחאות $v_1$, $v_2$ עם $u_1$ ו-$u_2$.\n"
        "- **אנרגיה שאבדה:** $\\Delta KE \\leq 0$ בהתנגשויות לא-אלסטיות.\n"
        "- **מדוע נשמר:** החוק השלישי מבטל כוחות פנימיים בזוגות.\n\n"
        "**מסקנה:** סווגו את סוג הבעיה קודם (מתקף / לא-אלסטית / אלסטית), "
        "הגדירו כיוון חיובי, ואז יישמו את חוק השימור הנכון."
    )

    # --- question explanations ---
    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]

    return data


def validate(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "checkpoint":
            for lang in ("en", "he"):
                key = f"checkpoint_solution_{lang}"
                w = word_count(sec.get(key, ""))
                if w < MIN_WORDS["checkpoint"][lang]:
                    issues.append(f"checkpoint_solution {lang}: {w} < {MIN_WORDS['checkpoint'][lang]}")
            continue
        if kind in MIN_WORDS and kind != "checkpoint":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"{kind} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} expl {lang}: {w} words")

    return issues


def main():
    data = build_lesson()
    issues = validate(data)
    if issues:
        print("VALIDATION ISSUES:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")
    print("Running seed-lessons --dry-run...")
    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)
    print("All checks passed.")


if __name__ == "__main__":
    main()
