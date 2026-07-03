#!/usr/bin/env python3
"""Expand analytic_geometry_4pt.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/analytic_geometry_4pt.json"

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
            "**Why this is correct:** A circle centered at the origin with radius $7$ satisfies "
            "$(x-0)^2+(y-0)^2=7^2$, which simplifies to $x^2+y^2=49$. Every point on the circle "
            "is exactly 7 units from $(0,0)$ — for example $(7,0)$ gives $49+0=49$.\n\n"
            "**How to think about it:** Read center $(a,b)$ and radius $r$ from the question, "
            "then plug into $(x-a)^2+(y-b)^2=r^2$. When the center is the origin, the $(x-a)$ and "
            "$(y-b)$ terms collapse to $x^2$ and $y^2$.\n\n"
            "**Common slip:** Writing $x^2+y^2=7$ forgets to square the radius. Another trap is "
            "$(x-7)^2+(y-7)^2=49$, which places the center at $(7,7)$ instead of $(0,0)$.\n\n"
            "**Exam tip:** After writing the equation, test one obvious point on the circle — "
            "usually $(r,0)$ or $(0,r)$ — to catch sign and squaring errors before moving on."
        ),
        "he": (
            "**למה זה נכון:** מעגל שמרכזו בראשית ורדיוס $7$ מקיים $(x-0)^2+(y-0)^2=7^2$, "
            "כלומר $x^2+y^2=49$. כל נקודה על המעגל במרחק 7 מ-$(0,0)$ — למשל $(7,0)$ נותן $49+0=49$.\n\n"
            "**איך לחשוב על זה:** קוראים מרכז $(a,b)$ ורדיוס $r$ מהשאלה, ומציבים ב-$(x-a)^2+(y-b)^2=r^2$. "
            "כשהמרכז בראשית, הביטויים מתכווצים ל-$x^2$ ו-$y^2$.\n\n"
            "**טעות נפוצה:** $x^2+y^2=7$ שוכח לרבע את הרדיוס. מלכודת נוספת: $(x-7)^2+(y-7)^2=49$ "
            "שמניחה מרכז $(7,7)$ במקום $(0,0)$.\n\n"
            "**טיפ לבחינה:** אחרי כתיבת המשוואה, בדקו נקודה ברורה על המעגל — בדרך כלל $(r,0)$ או $(0,r)$ — "
            "כדי לתפוס טעויות ריבוע וסימן לפני שממשיכים."
        ),
    },
    2: {
        "en": (
            "**Why this is correct:** In standard form $(x-a)^2+(y-b)^2=r^2$, the center is $(a,b)$ "
            "and the radius is $r$. Here $(x-4)^2+(y+3)^2=16$ means $a=4$, $b=-3$ (note the sign flip "
            "on $y$), and $r^2=16$ so $r=4$.\n\n"
            "**How to think about it:** Match each squared binomial to $(x-a)^2$ or $(y-b)^2$. "
            "The number inside the parentheses with the opposite sign is the coordinate; the right-hand "
            "side is $r^2$, not $r$.\n\n"
            "**Common slip:** Reading center $(4,+3)$ ignores that $(y+3)^2=(y-(-3))^2$. Another error "
            "is radius $16$ instead of $\\sqrt{16}=4$.\n\n"
            "**Exam tip:** Write $(y+3)^2=(y-(-3))^2$ explicitly on your paper once — examiners "
            "often hide negative centers this way. Always take the square root of the constant for $r$."
        ),
        "he": (
            "**למה זה נכון:** בצורה $(x-a)^2+(y-b)^2=r^2$ המרכז הוא $(a,b)$ והרדיוס $r$. "
            "כאן $(x-4)^2+(y+3)^2=16$ נותן $a=4$, $b=-3$ (שימו לב להיפוך הסימן ב-$y$), "
            "ו-$r^2=16$ כלומר $r=4$.\n\n"
            "**איך לחשוב על זה:** מתאימים כל סוגריים מרובע ל-$(x-a)^2$ או $(y-b)^2$. "
            "המספר בתוך הסוגריים עם סימן הפוך הוא הקואורדינטה; צד ימין הוא $r^2$, לא $r$.\n\n"
            "**טעות נפוצה:** מרכז $(4,+3)$ מתעלם מ-$(y+3)^2=(y-(-3))^2$. שגיאה נוספת: רדיוס $16$ "
            "במקום $\\sqrt{16}=4$.\n\n"
            "**טיפ לבחינה:** כתבו $(y+3)^2=(y-(-3))^2$ במפורש — בוחנים מסתירים מרכזים שליליים כך. "
            "תמיד שורשים את הקבוע לקבלת $r$."
        ),
    },
    3: {
        "en": (
            "**Why this is correct:** Substitute $(3,4)$ into $x^2+y^2$: $3^2+4^2=9+16=25$, which "
            "equals the right-hand side. The point lies exactly on the circle — not inside ($<25$) "
            "and not outside ($>25$).\n\n"
            "**How to think about it:** Compare the squared distance from the origin to $r^2$. "
            "If $x^2+y^2=r^2$, the point is on the circle; if less, inside; if greater, outside. "
            "The 3-4-5 triple makes this a classic Bagrut check.\n\n"
            "**Common slip:** Computing $\\sqrt{25}=5$ and comparing 5 to 25 — compare $x^2+y^2$ "
            "directly to $r^2=25$. Another error is adding coordinates $3+4=7$.\n\n"
            "**Exam tip:** When asked \"on, inside, or outside,\" always substitute first and "
            "state the inequality you are testing: $x^2+y^2$ versus $r^2$. One line of arithmetic earns full reasoning marks."
        ),
        "he": (
            "**למה זה נכון:** מציבים $(3,4)$ ב-$x^2+y^2$: $3^2+4^2=9+16=25$, ששווה לצד ימין. "
            "הנקודה בדיוק על המעגל — לא בפנים ($<25$) ולא בחוץ ($>25$).\n\n"
            "**איך לחשוב על זה:** משווים את ריבוע המרחק מהראשית ל-$r^2$. "
            "אם $x^2+y^2=r^2$ — על המעגל; אם פחות — בפנים; אם יותר — בחוץ. "
            "משולש 3-4-5 הופך את זה לבדיקה קלאסית בבגרות.\n\n"
            "**טעות נפוצה:** $\\sqrt{25}=5$ והשוואה ל-25 — משווים $x^2+y^2$ ישירות ל-$r^2=25$. "
            "שגיאה נוספת: $3+4=7$.\n\n"
            "**טיפ לבחינה:** כששואלים \"על, בפנים, או בחוץ,\" מציבים קודם ומציינים את אי-השוויון: "
            "$x^2+y^2$ מול $r^2$. שורת חישוב אחת מרוויחה נקודות נימוק."
        ),
    },
    4: {
        "en": (
            "**Why this is correct:** Group $x$ and $y$ terms and complete the square: "
            "$(x^2-6x+9)+(y^2+4y+4)=3+9+4=16$, giving $(x-3)^2+(y+2)^2=16$. "
            "Center $(3,-2)$, radius $4$.\n\n"
            "**How to think about it:** For $x^2+Dx$, add $(D/2)^2$ to both sides; repeat for $y$. "
            "Track constants carefully — whatever you add on the left must also be added on the right.\n\n"
            "**Common slip:** Center $(3,+2)$ misreads $(y+2)^2=(y-(-2))^2$. Another error is "
            "forgetting to add 9 and 4 to the right side, leaving $(x-3)^2+(y+2)^2=3$.\n\n"
            "**Exam tip:** Show the grouping step $(x^2-6x+\\underline{\\quad})+(y^2+4y+\\underline{\\quad})=\\ldots$ "
            "before squaring — Bagrut partial credit rewards structure even if the final radius is wrong."
        ),
        "he": (
            "**למה זה נכון:** מקבצים $x$ ו-$y$ ומשלימים לריבוע: "
            "$(x^2-6x+9)+(y^2+4y+4)=3+9+4=16$, כלומר $(x-3)^2+(y+2)^2=16$. "
            "מרכז $(3,-2)$, רדיוס $4$.\n\n"
            "**איך לחשוב על זה:** ל-$x^2+Dx$ מוסיפים $(D/2)^2$ לשני הצדדים; חוזרים על כך ל-$y$. "
            "עוקבים אחר קבועים — מה שמוסיפים משמאל חייב להיכנס גם מימין.\n\n"
            "**טעות נפוצה:** מרכז $(3,+2)$ שגוי ב-$(y+2)^2=(y-(-2))^2$. שגיאה נוספת: "
            "שכחת להוסיף 9 ו-4 לצד ימין.\n\n"
            "**טיפ לבחינה:** הציגו שלב קיבוץ לפני הריבוע — בוחנים נותנים נקודות חלקיות על מבנה "
            "גם אם הרדיוס הסופי שגוי."
        ),
    },
    5: {
        "en": (
            "**Why this is correct:** Substitute $y=x$ into $x^2+y^2=18$: $x^2+x^2=18$, so $2x^2=18$, "
            "$x^2=9$, $x=\\pm 3$. Then $y=x$ gives points $(3,3)$ and $(-3,-3)$. "
            "Both satisfy the circle: $3^2+3^2=18$ ✓.\n\n"
            "**How to think about it:** Line-circle intersection always reduces to one variable: "
            "express $y$ (or $x$) from the line, substitute into the circle, solve the quadratic, "
            "then back-substitute for the second coordinate.\n\n"
            "**Common slip:** Finding only $x=3$ and forgetting $x=-3$. Another error is substituting "
            "the circle into the line (harder algebra) instead of line into circle.\n\n"
            "**Exam tip:** When the line passes through the origin with slope 1, symmetry guarantees "
            "intersection points on $y=x$ and $y=-x$ lines — use that to verify signs quickly."
        ),
        "he": (
            "**למה זה נכון:** מציבים $y=x$ ב-$x^2+y^2=18$: $x^2+x^2=18$, כלומר $2x^2=18$, "
            "$x^2=9$, $x=\\pm 3$. אז $y=x$ נותן $(3,3)$ ו-$(-3,-3)$. "
            "שתיהן על המעגל: $3^2+3^2=18$ ✓.\n\n"
            "**איך לחשוב על זה:** חיתוך קו-מעגל תמיד מצמצם למשתנה אחד: "
            "מבטאים $y$ מהקו, מציבים במעגל, פותרים ריבועית, ומציבים חזרה.\n\n"
            "**טעות נפוצה:** מוצאים רק $x=3$ ושוכחים $x=-3$. שגיאה נוספת: "
            "הצבת המעגל בקו במקום הקו במעגל.\n\n"
            "**טיפ לבחינה:** כשהקו עובר בראשית עם שיפוע 1, הסימטריה מבטיחה זוגות נקודות — "
            "השתמשו בזה לאימות סימנים."
        ),
    },
    6: {
        "en": (
            "**Why this is correct:** Rewrite $y=3x+1$ as $3x-y+1=0$. Distance from center $(0,0)$ "
            "to the line is $d=\\frac{|1|}{\\sqrt{3^2+(-1)^2}}=\\frac{1}{\\sqrt{10}}\\approx 0.316$. "
            "Since $d<r=3$, the line is a **secant** — it cuts the circle at two points.\n\n"
            "**How to think about it:** Compare perpendicular distance $d$ from center to line with "
            "radius $r$: $d<r$ → secant (2 points); $d=r$ → tangent (1); $d>r$ → no intersection. "
            "This is faster than full substitution when only the count is asked.\n\n"
            "**Common slip:** Using $d=3$ (the radius) as the distance to the line. Another error "
            "is forgetting absolute value in the numerator.\n\n"
            "**Exam tip:** For \"secant, tangent, or misses\" questions, the distance formula saves "
            "2–3 minutes versus solving a quadratic. State $d$, $r$, and the inequality explicitly."
        ),
        "he": (
            "**למה זה נכון:** $y=3x+1$ כ-$3x-y+1=0$. מרחק מ-$(0,0)$ לקו: "
            "$d=\\frac{|1|}{\\sqrt{10}}\\approx 0.316$. מכיוון ש-$d<r=3$, הקו **חותך** — שתי נקודות חיתוך.\n\n"
            "**איך לחשוב על זה:** משווים מרחק ניצב $d$ ממרכז לקו לרדיוס $r$: "
            "$d<r$ → חותך; $d=r$ → משיק; $d>r$ → ללא חיתוך. מהיר יותר מהצבה מלאה כששואלים רק על מספר.\n\n"
            "**טעות נפוצה:** $d=3$ (הרדיוס) כמרחק לקו. שגיאה נוספת: שכחת ערך מוחלט במונה.\n\n"
            "**טיפ לבחינה:** בשאלות \"חותך, משיק, או לא נוגע,\" נוסחת המרחק חוסכת 2–3 דקות. "
            "ציינו $d$, $r$, ואי-השוויון במפורש."
        ),
    },
    7: {
        "en": (
            "**Why this is correct:** For a circle $x^2+y^2=r^2$, the tangent at $(x_0,y_0)$ on the "
            "circle is $xx_0+yy_0=r^2$. With $(3,4)$ and $r^2=25$: $3x+4y=25$. "
            "Verify: $(3,4)$ satisfies $9+16=25$ ✓.\n\n"
            "**How to think about it:** The tangent replaces each squared variable with a product "
            "of the variable and the touch-point coordinate. The radius to $(3,4)$ has slope $4/3$; "
            "the tangent slope is $-3/4$ — perpendicular, as expected.\n\n"
            "**Common slip:** Using $3x+4y=25$ but checking with center $(0,0)$ instead of touch point. "
            "Another error is $x+ y=25$ from adding coordinates.\n\n"
            "**Exam tip:** Memorize the tangent formula for origin-centered circles — it appears "
            "in nearly every 4-unit Bagrut geometry section. Show the template before substituting."
        ),
        "he": (
            "**למה זה נכון:** למעגל $x^2+y^2=r^2$, המשיק ב-$(x_0,y_0)$ הוא $xx_0+yy_0=r^2$. "
            "עם $(3,4)$ ו-$r^2=25$: $3x+4y=25$. אימות: $(3,4)$ מקיים $9+16=25$ ✓.\n\n"
            "**איך לחשוב על זה:** המשיק מחליף כל משתנה בריבוע במכפלה של המשתנה וקואורדינטת נקודת המגע. "
            "רדיוס ל-$(3,4)$ שיפוע $4/3$; שיפוע משיק $-3/4$ — ניצב, כצפוי.\n\n"
            "**טעות נפוצה:** בדיקה עם המרכז במקום נקודת המגע. שגיאה נוספת: $x+y=25$.\n\n"
            "**טיפ לבחינה:** שיננו נוסחת משיק למעגל בראשית — היא מופיעה בכמעט כל שאלת גאומטריה 4 יח'. "
            "הציגו תבנית לפני הצבה."
        ),
    },
    8: {
        "en": (
            "**Why this is correct:** Use general form $x^2+y^2+Dx+Ey+F=0$. "
            "$(0,0)$ gives $F=0$. $(4,0)$: $16+4D=0\\Rightarrow D=-4$. "
            "$(0,3)$: $9+3E=0\\Rightarrow E=-3$. So $x^2+y^2-4x-3y=0$. "
            "Completing the square: $(x-2)^2+(y-\\frac{3}{2})^2=\\frac{25}{4}$, center $(2,\\frac{3}{2})$, radius $\\frac{5}{2}$.\n\n"
            "**How to think about it:** Three non-collinear points determine a unique circle. "
            "Substitute each point into the general equation to get a linear system in $D,E,F$.\n\n"
            "**Common slip:** Arithmetic sign errors on $D$ or $E$. Another error is assuming "
            "center at origin because one point is $(0,0)$.\n\n"
            "**Exam tip:** After finding $D,E,F$, complete the square to verify radius is positive. "
            "If $r^2<0$, the three points are collinear — no circle exists."
        ),
        "he": (
            "**למה זה נכון:** צורה כללית $x^2+y^2+Dx+Ey+F=0$. "
            "$(0,0)$ נותן $F=0$. $(4,0)$: $D=-4$. $(0,3)$: $E=-3$. "
            "לכן $x^2+y^2-4x-3y=0$. השלמה לריבוע: $(x-2)^2+(y-\\frac{3}{2})^2=\\frac{25}{4}$.\n\n"
            "**איך לחשוב על זה:** שלוש נקודות לא על קו קובעות מעגל יחיד. "
            "מציבים כל נקודה ומקבלים מערכת לינארית ב-$D,E,F$.\n\n"
            "**טעות נפוצה:** שגיאות סימן ב-$D$ או $E$. הנחה שהמרכז בראשית כי $(0,0)$ על המעגל.\n\n"
            "**טיפ לבחינה:** אחרי $D,E,F$, השלימו לריבוע וודאו $r^2>0$. "
            "אם $r^2<0$ — הנקודות על קו, אין מעגל."
        ),
    },
}


def build_lesson():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    # --- intro ---
    data["sections"][0]["body_en_md"] = (
        "A circle drawn with a compass is a set of points equidistant from a center — "
        "in analytic geometry, that condition becomes an **equation**. Every point on a circle "
        "with center $(a,b)$ and radius $r$ satisfies:\n"
        "$$(x-a)^2 + (y-b)^2 = r^2$$\n\n"
        "At the **4-unit Bagrut** level, circle problems routinely combine with lines: "
        "finding intersection points (0, 1, or 2), deciding whether a line is a secant or tangent "
        "using perpendicular distance, and constructing tangent lines from an external point. "
        "These skills build directly on `concept:analytic_geometry_basic` (distance, slope, line equations) "
        "and prepare you for `concept:analytic_geometry_5pt` (conic sections).\n\n"
        "**What you will master:**\n"
        "- Write and read circle equations in standard and general form\n"
        "- Substitute a line into a circle to find intersection points\n"
        "- Use the discriminant or distance formula to classify line-circle contact\n"
        "- Find tangents at a point on the circle and from an external point\n\n"
        "Applications appear in optics (focal mirrors), GPS trilateration, and architectural "
        "arches — anywhere curved and straight geometry meet."
    )
    data["sections"][0]["body_he_md"] = (
        "מעגל שמציירים במחוגה הוא קבוצת נקודות במרחק קבוע ממרכז — "
        "בגאומטריה אנליטית התנאי הופך ל**משוואה**. כל נקודה על מעגל עם מרכז $(a,b)$ ורדיוס $r$ מקיימת:\n"
        "$$(x-a)^2 + (y-b)^2 = r^2$$\n\n"
        "ברמת **בגרות 4 יחידות**, בעיות מעגל משולבות עם קווים: "
        "מציאת נקודות חיתוך (0, 1 או 2), קביעה אם קו חותך או משיק באמצעות מרחק ניצב, "
        "ובניית משיקים מנקודה חיצונית. המיומנויות בנויות על `concept:analytic_geometry_basic` "
        "(מרחק, שיפוע, משוואות ישר) ומכינות ל-`concept:analytic_geometry_5pt` (חתכי חרוט).\n\n"
        "**מה תשלטו:**\n"
        "- כתיבה וקריאה של משוואות מעגל בצורה סטנדרטית וכללית\n"
        "- הצבת קו במעגל למציאת נקודות חיתוך\n"
        "- שימוש בדיסקרימיננטה או נוסחת מרחק לסיווג מגע קו-מעגל\n"
        "- משיקים בנקודה על המעגל ומנקודה חיצונית\n\n"
        "יישומים מופיעים באופטיקה, GPS וקשתות אדריכליות — בכל מקום שבו גיאומטריה מעוגלת וישרה נפגשות."
    )

    # --- definition ---
    data["sections"][1]["body_en_md"] = (
        "**Standard form of a circle:**\n"
        "$$(x-a)^2 + (y-b)^2 = r^2$$\n"
        "- **Center:** $(a, b)$ — read the opposite sign from each binomial\n"
        "- **Radius:** $r > 0$ — take the square root of the right-hand side\n\n"
        "**General form:** $x^2 + y^2 + Dx + Ey + F = 0$. Complete the square in $x$ and $y$ "
        "separately to convert to standard form. If the completed equation has $r^2 < 0$, "
        "no real circle exists.\n\n"
        "**Distance from center $(a,b)$ to line** $\\ell: Ax + By + C = 0$:\n"
        "$$d = \\frac{|Aa + Bb + C|}{\\sqrt{A^2 + B^2}}$$\n"
        "This perpendicular distance determines how the line relates to the circle.\n\n"
        "**Line-circle classification:**\n"
        "- $d < r$: line **intersects** at 2 points (secant / chord)\n"
        "- $d = r$: line is **tangent** (exactly 1 contact point)\n"
        "- $d > r$: line **misses** the circle entirely\n\n"
        "**Tangent at $(x_0, y_0)$ on** $x^2+y^2=r^2$ **(center at origin):**\n"
        "$$x \\cdot x_0 + y \\cdot y_0 = r^2$$\n"
        "The radius to the touch point is perpendicular to this tangent line."
    )
    data["sections"][1]["body_he_md"] = (
        "**צורה סטנדרטית של מעגל:**\n"
        "$$(x-a)^2 + (y-b)^2 = r^2$$\n"
        "- **מרכז:** $(a, b)$ — קוראים סימן הפוך מכל סוגריים; $(y+3)^2$ פירושו $b=-3$\n"
        "- **רדיוס:** $r > 0$ — שורש של צד ימין; $r^2=16$ נותן $r=4$, לא $16$\n\n"
        "**צורה כללית:** $x^2 + y^2 + Dx + Ey + F = 0$. משלימים לריבוע ב-$x$ וב-$y$ "
        "בנפרד: ל-$x^2+Dx$ מוסיפים $(D/2)^2$, ואותו קבוע גם לצד ימין. "
        "אם $r^2 < 0$ אחרי ההשלמה — אין מעגל ממשי (שלוש נקודות על קו).\n\n"
        "**מרחק ממרכז $(a,b)$ לקו** $\\ell: Ax + By + C = 0$:\n"
        "$$d = \\frac{|Aa + Bb + C|}{\\sqrt{A^2 + B^2}}$$\n"
        "מרחק ניצב זה — לא אורך הקטע — קובע את יחס הקו למעגל. "
        "כתבו את הקו בצורה $Ax+By+C=0$ לפני ההצבה.\n\n"
        "**סיווג קו-מעגל:**\n"
        "- $d < r$: **חיתוך** ב-2 נקודות (חותך / מיתר)\n"
        "- $d = r$: **משיק** (נקודת מגע אחת)\n"
        "- $d > r$: הקו **לא מגיע** למעגל\n\n"
        "**משיק ב-$(x_0, y_0)$ על** $x^2+y^2=r^2$ **(מרכז בראשית):**\n"
        "$$x \\cdot x_0 + y \\cdot y_0 = r^2$$\n"
        "הרדיוס לנקודת המגע ניצב לקו המשיק — שיפוע הרדיוס כפול שיפוע המשיק $=-1$."
    )

    # --- theory ---
    data["sections"][2]["body_en_md"] = (
        "**Method 1 — Substitution for intersection points:**\n"
        "1. Express $y$ (or $x$) from the line equation.\n"
        "2. Substitute into the circle equation.\n"
        "3. Solve the resulting quadratic for $x$ (or $y$).\n"
        "4. Back-substitute to find the other coordinate.\n"
        "The **discriminant** $\\Delta$ of the quadratic tells you how many intersections: "
        "$\\Delta > 0$ → two points; $\\Delta = 0$ → tangent; $\\Delta < 0$ → no real intersection.\n\n"
        "**Method 2 — Distance for classification only:**\n"
        "When asked \"how many intersections?\" without coordinates, compare $d$ (center to line) "
        "with $r$. This avoids solving a quadratic entirely.\n\n"
        "**Tangent from external point $(x_1, y_1)$ to** $x^2+y^2=r^2$:\n"
        "1. Write lines through $(x_1,y_1)$ with slope $m$: $y-y_1=m(x-x_1)$, i.e. $mx-y+(y_1-mx_1)=0$.\n"
        "2. Set distance from $(0,0)$ to the line equal to $r$.\n"
        "3. Solve for $m$ — typically two values (two tangent lines).\n"
        "4. **Check separately:** is the vertical line $x=x_1$ also tangent? (Only if $|x_1|=r$.)\n\n"
        "**Key geometric property:** The radius to the point of tangency is **perpendicular** "
        "to the tangent line. Use this to verify answers or find tangents via slope reciprocals."
    )
    data["sections"][2]["body_he_md"] = (
        "**שיטה 1 — הצבה לנקודות חיתוך:**\n"
        "1. מבטאים $y$ (או $x$) ממשוואת הקו.\n"
        "2. מציבים במשוואת המעגל.\n"
        "3. פותרים את הריבועית לפי $x$ (או $y$).\n"
        "4. מציבים חזרה לקואורדינטה השנייה.\n"
        "ה**דיסקרימיננטה** $\\Delta$ מגלה כמה חיתוכים: "
        "$\\Delta > 0$ → שתיים; $\\Delta = 0$ → משיק; $\\Delta < 0$ → אין חיתוך ממשי.\n\n"
        "**שיטה 2 — מרחק לסיווג בלבד:**\n"
        "כששואלים \"כמה חיתוכים?\" בלי קואורדינטות, משווים $d$ (מרכז לקו) ל-$r$. "
        "חוסך פתרון ריבועית.\n\n"
        "**משיק מנקודה חיצונית $(x_1, y_1)$ ל-** $x^2+y^2=r^2$:\n"
        "1. קווים דרך $(x_1,y_1)$ עם שיפוע $m$: $y-y_1=m(x-x_1)$.\n"
        "2. מרחק מ-$(0,0)$ לקו = $r$.\n"
        "3. פותרים לפי $m$ — בדרך כלל שני ערכים (שני משיקים).\n"
        "4. **בדקו בנפרד:** האם הקו האנכי $x=x_1$ גם משיק? (רק אם $|x_1|=r$.)\n\n"
        "**תכונה גיאומטרית:** הרדיוס לנקודת המגע **ניצב** למשיק. "
        "השתמשו בזה לאימות או למציאת משיקים דרך שיפועים הופכיים."
    )

    # --- worked example 1 ---
    data["sections"][3]["body_en_md"] = (
        "**Write the equation of the circle with center $(2, -1)$ and radius $3$.**\n\n"
        "We need the standard form directly from center-radius data — no completing the square required. "
        "This is the most common opening sub-question on Bagrut circle problems.\n\n"
        "### Move 1: Write the template\n"
        "$$(x - a)^2 + (y - b)^2 = r^2$$\n"
        "Substitute $a=2$, $b=-1$, $r=3$. Watch the sign on $b$: center $y=-1$ means $(y-(-1))^2=(y+1)^2$:\n"
        "$$(x - 2)^2 + (y + 1)^2 = 9$$\n\n"
        "### Move 2: Expand to general form (often requested next)\n"
        "$$x^2 - 4x + 4 + y^2 + 2y + 1 = 9 \\Rightarrow x^2 + y^2 - 4x + 2y - 4 = 0$$\n\n"
        "### Move 3: Verify with boundary points\n"
        "Horizontal: $(2+3,-1)=(5,-1)$ gives $(5-2)^2+0=9$ ✓. "
        "Vertical: $(2,-1+3)=(2,2)$ gives $0+(2+1)^2=9$ ✓.\n\n"
        "### Move 4: Read back center and radius\n"
        "From $(x-2)^2+(y+1)^2=9$: center $(2,-1)$, $r=3$ — matches the givens ✓.\n\n"
        "**Why this method:** Center-radius problems are one-step substitution. "
        "Always verify with two boundary points (one horizontal, one vertical offset) to catch sign errors.\n\n"
        "**Answer:** $(x-2)^2 + (y+1)^2 = 9$."
    )
    data["sections"][3]["body_he_md"] = (
        "**כתבו משוואת מעגל עם מרכז $(2, -1)$ ורדיוס $3$.**\n\n"
        "צריך צורה סטנדרטית ישירות מנתוני מרכז-רדיוס — בלי השלמה לריבוע. "
        "זה סעיף פתיחה נפוץ בשאלות מעגל בבגרות.\n\n"
        "### צעד 1: כתיבת התבנית\n"
        "$$(x - a)^2 + (y - b)^2 = r^2$$\n"
        "מציבים $a=2$, $b=-1$, $r=3$. שימו לב לסימן: מרכז $y=-1$ אומר $(y+1)^2$:\n"
        "$$(x - 2)^2 + (y + 1)^2 = 9$$\n\n"
        "### צעד 2: פיתוח לצורה כללית (לעיתים נדרש)\n"
        "$$x^2 + y^2 - 4x + 2y - 4 = 0$$\n\n"
        "### צעד 3: אימות עם נקודות גבול\n"
        "אופקית: $(5,-1)$ נותן $(5-2)^2+0=9$ ✓. "
        "אנכית: $(2,2)$ נותן $0+(2+1)^2=9$ ✓.\n\n"
        "### צעד 4: קריאה חזרה\n"
        "מ-$(x-2)^2+(y+1)^2=9$: מרכז $(2,-1)$, $r=3$ — תואם ✓.\n\n"
        "**למה השיטה:** בעיות מרכז-רדיוס הן הצבה בשלב אחד. "
        "אמתו עם שתי נקודות גבול (אופקית ואנכית) לתפיסת שגיאות סימן. "
        "בבגרות, צורה סטנדרטית מספיקה אלא אם מבקשים במפורש צורה כללית.\n\n"
        "**תשובה:** $(x-2)^2 + (y+1)^2 = 9$."
    )

    # --- checkpoint 1 ---
    data["sections"][4]["checkpoint_solution_en"] = (
        "We need the circle equation and a membership test for $(0,8)$.\n\n"
        "**Step 1 — Write standard form:**\n"
        "Center $(-3, 4)$, radius $5$. Negative $x$-center means $(x-(-3))^2=(x+3)^2$:\n"
        "$$(x + 3)^2 + (y - 4)^2 = 25$$\n\n"
        "**Step 2 — Check point $(0, 8)$:**\n"
        "Substitute into the left side:\n"
        "$(0+3)^2 + (8-4)^2 = 9 + 16 = 25$\n"
        "The left side equals $r^2=25$, so the point satisfies the equation.\n\n"
        "**Conclusion:** $(0,8)$ lies **on** the circle (not inside or outside).\n\n"
        "**Independent verification:** Distance from $(0,8)$ to center $(-3,4)$:\n"
        "$d=\\sqrt{(0-(-3))^2+(8-4)^2}=\\sqrt{9+16}=5=r$ ✓.\n"
        "Both methods agree — full confidence in the answer. "
        "On Bagrut, showing either substitution or distance earns partial credit."
    )
    data["sections"][4]["checkpoint_solution_he"] = (
        "צריך משוואת מעגל ובדיקת שייכות של $(0,8)$.\n\n"
        "**שלב 1 — צורה סטנדרטית:**\n"
        "מרכז $(-3, 4)$, רדיוס $5$. מרכז $x$ שלילי אומר $(x+3)^2$:\n"
        "$$(x + 3)^2 + (y - 4)^2 = 25$$\n\n"
        "**שלב 2 — בדיקת $(0, 8)$:**\n"
        "הצבה בצד שמאל:\n"
        "$(0+3)^2 + (8-4)^2 = 9 + 16 = 25$\n"
        "צד שמאל שווה ל-$r^2=25$, כלומר הנקודה מקיימת את המשוואה.\n\n"
        "**מסקנה:** $(0,8)$ **על** המעגל (לא בפנים ולא בחוץ).\n\n"
        "**אימות עצמאי:** מרחק מ-$(0,8)$ למרכז $(-3,4)$:\n"
        "$d=\\sqrt{9+16}=5=r$ ✓. שתי השיטות מסכימות. "
        "בבגרות, הצגת הצבה או מרחק מרוויחה נקודות חלקיות."
    )

    # --- worked example 2 ---
    data["sections"][5]["body_en_md"] = (
        "**Find all intersection points of $y = 2x - 3$ and $x^2 + y^2 = 25$.**\n\n"
        "Substitute the line into the circle — this always produces a quadratic in one variable. "
        "The circle has center $(0,0)$ and radius $5$.\n\n"
        "### Move 1: Substitute $y = 2x - 3$ into the circle\n"
        "$$x^2 + (2x-3)^2 = 25$$\n"
        "Expand the squared binomial carefully: $(2x-3)^2 = 4x^2 - 12x + 9$.\n"
        "$$x^2 + 4x^2 - 12x + 9 = 25 \\Rightarrow 5x^2 - 12x - 16 = 0$$\n\n"
        "### Move 2: Discriminant before full solution\n"
        "$$\\Delta = (-12)^2 - 4(5)(-16) = 144 + 320 = 464 > 0$$\n"
        "Two distinct intersection points exist — the line is a secant.\n\n"
        "### Move 3: Quadratic formula\n"
        "$$x = \\frac{12 \\pm \\sqrt{464}}{10} = \\frac{12 \\pm 4\\sqrt{29}}{10} = \\frac{6 \\pm 2\\sqrt{29}}{5}$$\n\n"
        "### Move 4: Back-substitute for $y$\n"
        "Using $y = 2x - 3$ for each $x$:\n"
        "$$y_1 = 2\\cdot\\frac{6+2\\sqrt{29}}{5}-3 = \\frac{12\\sqrt{29}-3}{5}, \\quad "
        "y_2 = \\frac{-12\\sqrt{29}-3}{5}$$\n\n"
        "### Move 5: Sanity check one point\n"
        "For $x=\\frac{6+2\\sqrt{29}}{5}$, verify $x^2+y^2=25$ using the line relation.\n\n"
        "**Answer:** $\\left(\\frac{6+2\\sqrt{29}}{5},\\ \\frac{12\\sqrt{29}-3}{5}\\right)$ and "
        "$\\left(\\frac{6-2\\sqrt{29}}{5},\\ \\frac{-12\\sqrt{29}-3}{5}\\right)$.\n\n"
        "**Why $\\Delta > 0$ first:** Confirming two roots before the quadratic formula saves "
        "time if the question only asks \"how many intersections.\" "
        "On Bagrut, write $\\Delta$ explicitly even when full coordinates are required."
    )
    data["sections"][5]["body_he_md"] = (
        "**מצאו את כל נקודות החיתוך של $y = 2x - 3$ ו-$x^2 + y^2 = 25$.**\n\n"
        "מציבים את הקו במעגל — תמיד מתקבלת ריבועית במשתנה אחד. "
        "המעגל מרכז $(0,0)$, רדיוס $5$.\n\n"
        "### צעד 1: הצבת $y = 2x - 3$ במעגל\n"
        "$$x^2 + (2x-3)^2 = 25$$\n"
        "פיתוח: $(2x-3)^2 = 4x^2 - 12x + 9$.\n"
        "$$5x^2 - 12x - 16 = 0$$\n\n"
        "### צעד 2: דיסקרימיננטה לפני פתרון מלא\n"
        "$$\\Delta = 144 + 320 = 464 > 0$$\n"
        "שתי נקודות חיתוך — הקו חותך.\n\n"
        "### צעד 3: נוסחת השורשים\n"
        "$$x = \\frac{6 \\pm 2\\sqrt{29}}{5}$$\n\n"
        "### צעד 4: הצבה חזרה ל-$y$\n"
        "מ-$y = 2x - 3$:\n"
        "$$y_1 = \\frac{12\\sqrt{29}-3}{5}, \\quad y_2 = \\frac{-12\\sqrt{29}-3}{5}$$\n\n"
        "### צעד 5: בדיקת הגיון\n"
        "אמתו נקודה אחת: $x^2+y^2=25$ עם יחס הקו. אם התוצאה לא 25, חזרו לפיתוח $(2x-3)^2$.\n\n"
        "**תשובה:** $\\left(\\frac{6+2\\sqrt{29}}{5},\\ \\frac{12\\sqrt{29}-3}{5}\\right)$ ו- "
        "$\\left(\\frac{6-2\\sqrt{29}}{5},\\ \\frac{-12\\sqrt{29}-3}{5}\\right)$.\n\n"
        "**למה $\\Delta > 0$ קודם:** מאשר שתי שורשים לפני נוסחת שורשים — חוסך זמן אם שואלים רק \"כמה חיתוכים\". "
        "בבגרות, כתבו $\\Delta$ במפורש גם כשנדרשות קואורדינטות מלאות."
    )

    # --- checkpoint 2 ---
    data["sections"][6]["checkpoint_solution_en"] = (
        "The question asks **how many** intersection points — not the coordinates themselves.\n\n"
        "**Step 1 — Substitute** $y = x + 1$ into $x^2 + y^2 = 8$:\n"
        "$$x^2 + (x+1)^2 = 8$$\n"
        "$$x^2 + x^2 + 2x + 1 = 8 \\Rightarrow 2x^2 + 2x - 7 = 0$$\n\n"
        "**Step 2 — Compute the discriminant:**\n"
        "For $ax^2+bx+c=0$ with $a=2$, $b=2$, $c=-7$:\n"
        "$$\\Delta = b^2 - 4ac = 4 - 4(2)(-7) = 4 + 56 = 60 > 0$$\n\n"
        "**Step 3 — Interpret:**\n"
        "$\\Delta > 0$ means two distinct real roots → the line cuts the circle at **two points**. "
        "The line is a **secant**.\n\n"
        "**Optional verification via distance:** Center $(0,0)$, radius $\\sqrt{8}=2\\sqrt{2}\\approx 2.83$. "
        "Line $x-y+1=0$: $d=1/\\sqrt{2}\\approx 0.71 < r$ ✓ — confirms secant without solving for $x$.\n\n"
        "**Answer:** Two intersection points. If coordinates were needed: $x=\\frac{-1\\pm\\sqrt{15}}{2}$."
    )
    data["sections"][6]["checkpoint_solution_he"] = (
        "השאלה שואלת **כמה** נקודות חיתוך — לא את הקואורדינטות.\n\n"
        "**שלב 1 — הצבה** $y = x + 1$ ב-$x^2 + y^2 = 8$:\n"
        "$$x^2 + (x+1)^2 = 8 \\Rightarrow 2x^2 + 2x - 7 = 0$$\n\n"
        "**שלב 2 — דיסקרימיננטה:**\n"
        "עבור $a=2$, $b=2$, $c=-7$:\n"
        "$$\\Delta = 4 + 56 = 60 > 0$$\n\n"
        "**שלב 3 — פרשנות:**\n"
        "$\\Delta > 0$ → שני שורשים ממשיים → הקו חותך ב**שתי** נקודות. הקו **חותך**.\n\n"
        "**אימות אופציונלי במרחק:** מרכז $(0,0)$, $r=\\sqrt{8}\\approx 2.83$. "
        "קו $x-y+1=0$: $d=1/\\sqrt{2}\\approx 0.71 < r$ ✓ — מאשר חותך בלי לפתור לפי $x$.\n\n"
        "**תשובה:** שתי נקודות חיתוך. אם נדרשות קואורדינטות: $x=\\frac{-1\\pm\\sqrt{15}}{2}$."
    )

    # --- worked example 3 ---
    data["sections"][7]["body_en_md"] = (
        "**Find the tangent lines from $(7, 0)$ to the circle $x^2 + y^2 = 25$.**\n\n"
        "This is a classic 5–6 mark Bagrut problem. First confirm the point is outside the circle.\n\n"
        "### Move 1: Outside-point check\n"
        "$7^2 + 0^2 = 49 > 25 = r^2$ ✓ — tangents exist (two of them, symmetric about the $x$-axis).\n\n"
        "### Move 2: Parametrize lines through $(7,0)$ with slope $m$\n"
        "$$y = m(x - 7) \\quad \\Rightarrow \\quad mx - y - 7m = 0$$\n"
        "Rewrite in $Ax+By+C=0$ form before applying the distance formula.\n\n"
        "### Move 3: Set distance from $(0,0)$ equal to $r=5$\n"
        "$$d = \\frac{|m(0) - 0 - 7m|}{\\sqrt{m^2 + 1}} = \\frac{7|m|}{\\sqrt{m^2+1}} = 5$$\n\n"
        "### Move 4: Square and solve for $m$\n"
        "$$49m^2 = 25(m^2 + 1) \\Rightarrow 24m^2 = 25 \\Rightarrow m = \\pm \\frac{5\\sqrt{6}}{12}$$\n\n"
        "### Move 5: Write both tangent equations\n"
        "$$y = \\frac{5\\sqrt{6}}{12}(x - 7) \\quad \\text{and} \\quad y = -\\frac{5\\sqrt{6}}{12}(x - 7)$$\n\n"
        "### Move 6: Check vertical line $x=7$ separately\n"
        "Distance from $(0,0)$ to $x=7$ is 7 > 5 — not tangent ✓.\n\n"
        "**Why distance works:** A tangent touches at exactly one point, so the perpendicular "
        "from center to line equals $r$. The length of tangent from $(7,0)$ is $\\sqrt{49-25}=2\\sqrt{6}$.\n\n"
        "**Answer:** $y = \\pm \\dfrac{5\\sqrt{6}}{12}(x - 7)$."
    )
    data["sections"][7]["body_he_md"] = (
        "**מצאו את המשיקים מ-$(7, 0)$ למעגל $x^2 + y^2 = 25$.**\n\n"
        "בעיה קלאסית 5–6 נקודות בבגרות. קודם מאשרים שהנקודה חיצונית.\n\n"
        "### צעד 1: בדיקת נקודה חיצונית\n"
        "$49 > 25$ ✓ — קיימים שני משיקים, סימטריים לציר $x$.\n\n"
        "### צעד 2: פרמטרизация קווים דרך $(7,0)$ עם שיפוע $m$\n"
        "$$y = m(x - 7) \\Rightarrow mx - y - 7m = 0$$\n"
        "כתבו בצורה $Ax+By+C=0$ לפני נוסחת המרחק.\n\n"
        "### צעד 3: מרחק מ-$(0,0)$ = $r=5$\n"
        "$$\\frac{7|m|}{\\sqrt{m^2+1}} = 5$$\n\n"
        "### צעד 4: ריבוע ופתרון\n"
        "$$49m^2 = 25(m^2 + 1) \\Rightarrow m = \\pm \\frac{5\\sqrt{6}}{12}$$\n\n"
        "### צעד 5: שתי משוואות משיק\n"
        "$$y = \\pm \\frac{5\\sqrt{6}}{12}(x - 7)$$\n\n"
        "### צעד 6: בדיקת קו אנכי $x=7$\n"
        "מרחק 7 > 5 — לא משיק ✓.\n\n"
        "**למה מרחק עובד:** משיק נוגע בנקודה אחת, הניצב ממרכז = $r$. "
        "אורך משיק מ-$(7,0)$ הוא $\\sqrt{49-25}=2\\sqrt{6}$. "
        "בבגרות, הציגו בדיקת נקודה חיצונית לפני חישוב $m$.\n\n"
        "**תשובה:** $y = \\pm \\dfrac{5\\sqrt{6}}{12}(x - 7)$."
    )

    # --- method_guide ---
    data["sections"][8]["body_en_md"] = (
        "Use this decision table before starting algebra:\n\n"
        "| Task | Method |\n|------|--------|\n"
        "| Write circle equation | $(x-a)^2+(y-b)^2=r^2$ from center + radius |\n"
        "| Read center and radius | Match to standard form; flip signs for center |\n"
        "| General → standard | Complete the square in $x$ and $y$ separately |\n"
        "| Point on circle? | Substitute; compare $x^2+y^2$ to $r^2$ |\n"
        "| Line-circle intersections | Substitute line into circle → quadratic |\n"
        "| Count intersections only | Compare $d$ (center to line) with $r$ |\n"
        "| Tangent from external point | Set $d(center, line)=r$; solve for $m$; check $x=x_0$ |\n"
        "| Tangent at $(x_0,y_0)$ on $x^2+y^2=r^2$ | $xx_0+yy_0=r^2$ |\n"
        "| Circle through 3 points | General form + 3 substitutions for $D,E,F$ |\n\n"
        "**When to use which:** If the question asks for coordinates, substitute. "
        "If it only asks secant/tangent/misses, use distance. "
        "If it asks for tangent from a point, distance-to-line with unknown slope is standard."
    )
    data["sections"][8]["body_he_md"] = (
        "טבלת החלטות לפני שמתחילים אלגברה:\n\n"
        "| משימה | שיטה |\n|-------|------|\n"
        "| כתיבת משוואת מעגל | $(x-a)^2+(y-b)^2=r^2$ ממרכז + רדיוס |\n"
        "| קריאת מרכז ורדיוס | התאמה לצורה סטנדרטית; היפוך סימנים |\n"
        "| כללית → סטנדרטית | השלמה לריבוע ב-$x$ וב-$y$ |\n"
        "| נקודה על מעגל? | הצבה; השוואת $x^2+y^2$ ל-$r^2$ |\n"
        "| חיתוכי קו-מעגל | הצבת קו במעגל → ריבועית |\n"
        "| ספירת חיתוכים בלבד | השוואת $d$ ל-$r$ |\n"
        "| משיק מנקודה חיצונית | $d(מרכז,קו)=r$; פתרון $m$; בדיקת $x=x_0$ |\n"
        "| משיק ב-$(x_0,y_0)$ על $x^2+y^2=r^2$ | $xx_0+yy_0=r^2$ |\n"
        "| מעגל דרך 3 נקודות | צורה כללית + 3 הצבות ל-$D,E,F$ |\n\n"
        "**מתי מה:** אם שואלים קואורדינטות — הצבה. "
        "אם רק חותך/משיק/לא נוגע — מרחק. "
        "משיק מנקודה — מרחק לקו עם שיפוע לא ידוע."
    )

    # --- pitfall ---
    pitfall_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "pitfall")
    data["sections"][pitfall_idx]["body_en_md"] = (
        "**Mistake 1 — Sign error when reading center from standard form.**\n"
        "$(x - 2)^2 + (y + 3)^2 = r^2$ has center $(2, -3)$ — not $(2, +3)$. "
        "Always rewrite $(y+3)^2$ as $(y-(-3))^2$ before reading $b$.\n\n"
        "**Mistake 2 — Substituting the circle into the line instead of line into circle.**\n"
        "Substituting $x^2+y^2=25$ into $y=2x-3$ creates a mess. "
        "Always isolate one variable from the **line** and plug into the **circle**.\n\n"
        "**Mistake 3 — Forgetting the vertical tangent case.**\n"
        "Using $y=m(x-x_0)$ misses the line $x=x_0$. Check: if $|x_0|=r$ for a circle at the origin, "
        "the vertical line through $(x_0,0)$ is also tangent.\n\n"
        "**Mistake 4 — Comparing $d$ to $r^2$ instead of $r$.**\n"
        "The distance formula gives $d$, the radius is $r$. Compare $d$ with $r$, not with $r^2$."
    )
    data["sections"][pitfall_idx]["body_he_md"] = (
        "**טעות 1 — שגיאת סימן בקריאת מרכז.**\n"
        "$(x - 2)^2 + (y + 3)^2 = r^2$ מרכז $(2, -3)$ — לא $(2, +3)$. "
        "כתבו $(y+3)^2=(y-(-3))^2$ לפני קריאת $b$.\n\n"
        "**טעות 2 — הצבת המעגל בקו במקום הקו במעגל.**\n"
        "הצבת $x^2+y^2=25$ ב-$y=2x-3$ יוצרת בלגן. "
        "תמיד בודדו משתנה מה**קו** והציבו ב**מעגל**.\n\n"
        "**טעות 3 — שכחת משיק אנכי.**\n"
        "$y=m(x-x_0)$ מפספס $x=x_0$. בדקו: אם $|x_0|=r$ למעגל בראשית, "
        "הקו האנכי דרך $(x_0,0)$ גם משיק.\n\n"
        "**טעות 4 — השוואת $d$ ל-$r^2$ במקום ל-$r$.**\n"
        "נוסחת המרחק נותנת $d$, הרדיוס הוא $r$. משווים $d$ עם $r$, לא עם $r^2$."
    )

    # --- why_matters ---
    wm_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "why_matters")
    data["sections"][wm_idx]["body_en_md"] = (
        "Circle-line geometry is a **capstone** of 4-unit analytic geometry and appears on nearly "
        "every Bagrut exam in some form — often as a multi-part question combining equation writing, "
        "intersection, and tangent construction in one scenario.\n\n"
        "**You will use this to unlock:**\n"
        "- `concept:analytic_geometry_5pt` — ellipses, parabolas, and hyperbolas extend the same "
        "distance and tangent ideas to general conic sections\n"
        "- `concept:optimization_problems` — tangent lines define boundary constraints in max/min setups\n"
        "- Engineering and physics: satellite dishes (parabolic), GPS trilateration (circles)\n\n"
        "**Why exams care:** 4-unit questions worth 5–8 marks combine circle equations with "
        "line intersection or tangent construction. Examiners reward showing the discriminant "
        "or distance formula explicitly before computing coordinates — method marks are substantial."
    )
    data["sections"][wm_idx]["body_he_md"] = (
        "גאומטריה של מעגל-קו היא **שיא** הגאומטריה האנליטית ב-4 יחידות ומופיעה בכמעט כל בחינת בגרות — "
        "לעיתים כשאלה רב-סעיפית שמשלבת כתיבת משוואה, חיתוך ובניית משיקים.\n\n"
        "**תשתמשו בזה להמשך:**\n"
        "- `concept:analytic_geometry_5pt` — אליפסות, פרבולות והיפרבולות מרחיבות רעיונות מרחק ומשיק\n"
        "- `concept:optimization_problems` — משיקים מגדירים אילוצי גבול באופטימיזציה\n"
        "- הנדסה ופיזיקה: צלחות לוויין, GPS (trilateration)\n\n"
        "**למה בחינות אכפת:** שאלות 4 יח' בשווי 5–8 נקודות משלבות משוואות מעגל עם חיתוך או משיקים. "
        "בוחנים מעריכים הצגת דיסקרימיננטה או נוסחת מרחק לפני קואורדינטות — נקודות שיטה משמעותיות."
    )

    # --- before_exam ---
    be_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "before_exam")
    data["sections"][be_idx]["body_en_md"] = (
        "**Key formulas:**\n"
        "- Circle: $(x-a)^2+(y-b)^2=r^2$, center $(a,b)$, radius $r$\n"
        "- Distance from $(a,b)$ to line $Ax+By+C=0$: $d=\\frac{|Aa+Bb+C|}{\\sqrt{A^2+B^2}}$\n"
        "- Tangent at $(x_0,y_0)$ on $x^2+y^2=r^2$: $xx_0+yy_0=r^2$\n"
        "- $d<r$: secant; $d=r$: tangent; $d>r$: no intersection\n\n"
        "**Typical Bagrut 4pt patterns:**\n"
        "1. Write circle equation; check if point is on circle. (3 marks)\n"
        "2. Find intersection points of line and circle. (4–5 marks)\n"
        "3. Find tangent lines from external point. (5–6 marks)\n\n"
        "**Marking tips:** Always verify the external point is outside ($x_1^2+y_1^2>r^2$). "
        "Show discriminant or distance formula before coordinates. "
        "Check the vertical line case when finding tangents from a point."
    )
    data["sections"][be_idx]["body_he_md"] = (
        "**נוסחאות מרכזיות:**\n"
        "- מעגל: $(x-a)^2+(y-b)^2=r^2$, מרכז $(a,b)$, רדיוס $r$\n"
        "- מרחק מ-$(a,b)$ לקו $Ax+By+C=0$: $d=\\frac{|Aa+Bb+C|}{\\sqrt{A^2+B^2}}$\n"
        "- משיק ב-$(x_0,y_0)$ על $x^2+y^2=r^2$: $xx_0+yy_0=r^2$\n"
        "- $d<r$: חותך; $d=r$: משיק; $d>r$: ללא חיתוך\n\n"
        "**דפוסי שאלות טיפוסיות בבגרות 4 יח':**\n"
        "1. כתיבת משוואת מעגל; בדיקה אם נקודה על מעגל. (3 נקודות)\n"
        "2. מציאת נקודות חיתוך קו ומעגל. (4–5 נקודות)\n"
        "3. מציאת משיקים מנקודה חיצונית. (5–6 נקודות)\n\n"
        "**טיפים לניקוד:** וודאו שהנקודה החיצונית באמת חיצונית ($x_1^2+y_1^2>r^2$). "
        "הציגו דיסקרימיננטה או נוסחת מרחק לפני קואורדינטות. "
        "בדקו משיק אנכי במציאת משיקים מנקודה."
    )

    # --- summary ---
    sum_idx = next(i for i, s in enumerate(data["sections"]) if s["kind"] == "summary")
    data["sections"][sum_idx]["body_en_md"] = (
        "- Circle equation: $(x-a)^2+(y-b)^2=r^2$; center $(a,b)$, radius $r$ — signs flip when reading center.\n"
        "- Convert general form $x^2+y^2+Dx+Ey+F=0$ by completing the square in $x$ and $y$.\n"
        "- Line-circle intersection: substitute line into circle, solve quadratic; use $\\Delta$ to count roots.\n"
        "- Faster classification: compare perpendicular distance $d$ from center to line with $r$.\n"
        "- Tangent at $(x_0,y_0)$ on $x^2+y^2=r^2$: $xx_0+yy_0=r^2$.\n"
        "- Tangent from external point: set $d=r$, solve for slope $m$; check vertical line $x=x_0$ separately.\n"
        "- Radius to point of tangency is perpendicular to the tangent — use for verification."
    )
    data["sections"][sum_idx]["body_he_md"] = (
        "- משוואת מעגל: $(x-a)^2+(y-b)^2=r^2$; מרכז $(a,b)$, רדיוס $r$ — סימנים מתהפכים בקריאה.\n"
        "- המרת צורה כללית $x^2+y^2+Dx+Ey+F=0$ בהשלמה לריבוע ב-$x$ וב-$y$.\n"
        "- חיתוך קו-מעגל: הצבת קו במעגל, פתרון ריבועית; $\\Delta$ לספירת שורשים.\n"
        "- סיווג מהיר: השוואת מרחק ניצב $d$ ממרכז לקו עם $r$.\n"
        "- משיק ב-$(x_0,y_0)$ על $x^2+y^2=r^2$: $xx_0+yy_0=r^2$.\n"
        "- משיק מנקודה חיצונית: $d=r$, פתרון $m$; בדיקת קו אנכי $x=x_0$ בנפרד.\n"
        "- רדיוס לנקודת מגע ניצב למשיק — לאימות."
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
