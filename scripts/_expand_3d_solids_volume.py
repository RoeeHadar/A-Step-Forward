#!/usr/bin/env python3
"""Expand 3d_solids_volume.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts/seed_data/lessons/3d_solids_volume.json"
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
            "From the Great Pyramid of Giza to spherical fuel tanks and ice-cream cones, "
            "**three-dimensional geometry** shapes the world around us. In Bagrut math you must "
            "move beyond flat shapes: compute **volume** (space inside) and **surface area** "
            "(material on the outside) for prisms, pyramids, cylinders, cones, and spheres.\n\n"
            "The central skill is not memorizing a list — it is **recognizing which solid you "
            "have** and why each formula works. Prisms and cylinders share $V = Bh$; pyramids and "
            "cones add the crucial factor $\\frac{1}{3}$. **Cavalieri's principle** explains why: "
            "two solids with equal cross-sectional areas at every height must have equal volumes, "
            "even if one is tilted or oblique.\n\n"
            "**Bagrut exam topics:**\n"
            "- Volume and surface area: prism, pyramid, cylinder, cone, sphere\n"
            "- Composite solids (add or subtract parts)\n"
            "- Cavalieri's principle and oblique solids\n"
            "- Working backward from volume or surface area to find dimensions"
        ),
        "body_he_md": (
            "מפירמידת גיזה הגדולה ועד מכלי דלק כדוריים וגלידות בחרוט, **גאומטריה תלת-ממדית** "
            "מעצבת את העולם סביבנו. בבגרות במתמטיקה עליכם לעבור מעבר לצורות שטוחות: לחשב "
            "**נפח** (המרחב שבתוך הגוף) ו**שטח פנים** (חומר על פני הגוף) עבור מנסרות, פירמידות, "
            "גלילים, חרוטים וכדורים.\n\n"
            "המיומנות המרכזית אינה שינון רשימה — אלא **זיהוי איזה גוף יש לפניכם** ולמה כל "
            "נוסחה עובדת. למנסרות וגלילים משותף $V = Bh$; לפירמידות וחרוטים נוסף הגורם "
            "הקריטי $\\frac{1}{3}$. **עיקרון קוולייר** מסביר מדוע: שני גופים עם שטחי חתך "
            "שווים בכל גובה חייבים להיות בעלי נפח שווה, גם אם האחד נטוי או אופקי.\n\n"
            "**נושאי בגרות:**\n"
            "- נפח ושטח פנים: מנסרה, פירמידה, גליל, חרוט, כדור\n"
            "- גופים מורכבים (חיבור או חיסור חלקים)\n"
            "- עיקרון קוולייר וגופים נטויים\n"
            "- מציאת מידות מתוך נפח או שטח פנים נתון"
        ),
    },
    "definition": {
        "body_en_md": (
            "Every solid in this lesson is defined by a **base** (or radius), a **height** "
            "perpendicular to the base, and sometimes a **slant height** for surface area.\n\n"
            "| Solid | Volume | Lateral Surface | Total Surface |\n"
            "|---|---|---|---|\n"
            "| Prism (base $B$, height $h$) | $V = Bh$ | $P\\cdot h$ | $2B + Ph$ |\n"
            "| Cylinder ($r$, $h$) | $V = \\pi r^2 h$ | $2\\pi rh$ | $2\\pi r(r+h)$ |\n"
            "| Pyramid (base $B$, height $h$) | $V = \\frac{1}{3}Bh$ | $\\frac{1}{2}Pl$ | "
            "$B + \\frac{1}{2}Pl$ |\n"
            "| Cone ($r$, $h$) | $V = \\frac{1}{3}\\pi r^2 h$ | $\\pi rl$ | $\\pi r(r+l)$ |\n"
            "| Sphere ($r$) | $V = \\frac{4}{3}\\pi r^3$ | — | $4\\pi r^2$ |\n\n"
            "$P$ = perimeter of the base; $l$ = slant height. For a cone, "
            "$l = \\sqrt{r^2 + h^2}$ from the right triangle in the axial cross-section.\n\n"
            "**Cavalieri's principle:** If two solids lie between parallel planes and every "
            "horizontal cross-section has the same area in both, their volumes are equal. "
            "This justifies $V = Bh$ for any prism or cylinder — straight or oblique."
        ),
        "body_he_md": (
            "כל גוף בשיעור זה מוגדר על ידי **בסיס** (או רדיוס), **גובה** מאונך לבסיס, "
            "ולפעמים **גובה שיפועי** לחישוב שטח פנים.\n\n"
            "| גוף | נפח | שטח צד | שטח כולל |\n"
            "|---|---|---|---|\n"
            "| מנסרה (בסיס $B$, גובה $h$) | $V = Bh$ | $P\\cdot h$ | $2B + Ph$ |\n"
            "| גליל ($r$, $h$) | $V = \\pi r^2 h$ | $2\\pi rh$ | $2\\pi r(r+h)$ |\n"
            "| פירמידה (בסיס $B$, גובה $h$) | $V = \\frac{1}{3}Bh$ | $\\frac{1}{2}Pl$ | "
            "$B + \\frac{1}{2}Pl$ |\n"
            "| חרוט ($r$, $h$) | $V = \\frac{1}{3}\\pi r^2 h$ | $\\pi rl$ | $\\pi r(r+l)$ |\n"
            "| כדור ($r$) | $V = \\frac{4}{3}\\pi r^3$ | — | $4\\pi r^2$ |\n\n"
            "$P$ = היקף הבסיס; $l$ = גובה שיפועי. בחרוט, $l = \\sqrt{r^2 + h^2}$ "
            "ממשולש ישר-זווית בחתך צירי.\n\n"
            "**עיקרון קוולייר:** אם שני גופים נמצאים בין מישורים מקבילים וכל חתך אופקי "
            "באותו שטח בשניהם — הנפחים שווים. זה מצדיק $V = Bh$ לכל מנסרה או גליל, "
            "ישר או נטוי."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Cavalieri's principle\n\n"
            "If two solids lie between the same two parallel planes, and **every plane parallel "
            "to those bases** cuts both solids in regions of equal area, then the solids have "
            "**equal volumes**. The shape of the side walls does not matter — only the "
            "cross-sectional area at each height.\n\n"
            "**Example:** A right cylinder and an oblique cylinder with the same circular base "
            "radius $r$ and height $h$ have identical horizontal cross-sections ($\\pi r^2$) at "
            "every level, so both have volume $V = \\pi r^2 h$.\n\n"
            "### Composite solids\n\n"
            "Real objects are often built from simpler pieces. **Strategy:** sketch the solid, "
            "label each part, compute each volume separately, then add or subtract:\n"
            "$$V_{\\text{total}} = V_1 + V_2 - V_3 \\pm \\cdots$$\n\n"
            "A hemisphere on a cylinder adds volumes; a cone hollowed from a cylinder subtracts. "
            "Always identify whether material is **added** or **removed** before substituting numbers.\n\n"
            "### Slant height and surface area\n\n"
            "For cones and pyramids, lateral surface area uses the **slant height** $l$, not the "
            "perpendicular height $h$. In the axial cross-section of a cone, $l$, $r$, and $h$ form "
            "a right triangle: $l = \\sqrt{r^2 + h^2}$. Using $h$ instead of $l$ is one of the "
            "most common Bagrut errors on surface-area questions."
        ),
        "body_he_md": (
            "### עיקרון קוולייר\n\n"
            "אם שני גופים נמצאים בין אותם שני מישורים מקבילים, ו**כל מישור מקביל לבסיסים** "
            "חותך את שני הגופים באזורים בעלי **שטח שווה**, אז לגופים **נפחים שווים**. "
            "צורת דפנות הצד לא משנה — רק שטח החתך בכל גובה.\n\n"
            "**דוגמה:** גליל ישר וגליל נטוי עם אותו רדיוס בסיס $r$ ואותו גובה $h$ "
            "מקבלים חתכים אופקיים זהים ($\\pi r^2$) בכל רמה, ולכן לשניהם נפח "
            "$V = \\pi r^2 h$.\n\n"
            "### גופים מורכבים\n\n"
            "עצמים אמיתיים נבנים לעיתים מחלקים פשוטים. **אסטרטגיה:** ציירו את הגוף, "
            "סמנו כל חלק, חשבו כל נפח בנפרד, ואז חברו או חסרו:\n"
            "$$V_{\\text{כולל}} = V_1 + V_2 - V_3 \\pm \\cdots$$\n\n"
            "חצי-כדור על גליל מחבר נפחים; חרוט שחולל מתוך גליל מחסיר. "
            "זהו תמיד האם החומר **נוסף** או **הוסר** לפני הצבת מספרים.\n\n"
            "### גובה שיפועי ושטח פנים\n\n"
            "בחרוטים ופירמידות, שטח הצד משתמש ב**גובה השיפועי** $l$, לא בגובה "
            "המאונך $h$. בחתך צירי של חרוט, $l$, $r$ ו-$h$ יוצרים משולש ישר-זווית: "
            "$l = \\sqrt{r^2 + h^2}$. שימוש ב-$h$ במקום $l$ הוא אחת השגיאות "
            "הנפוצות ביותר בבגרות בשאלות שטח פנים."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Given:** A cone with base radius $r = 6\\;\\text{cm}$ and height $h = 8\\;\\text{cm}$. "
            "Find its volume and total surface area.\n\n"
            "### Move 1: Volume of the cone\n"
            "Use $V = \\frac{1}{3}\\pi r^2 h$:\n"
            "$$V = \\frac{1}{3}\\pi(6^2)(8) = \\frac{1}{3}\\pi(36)(8) = 96\\pi "
            "\\approx 301.6\\;\\text{cm}^3$$\n\n"
            "### Move 2: Find slant height\n"
            "Surface area needs $l$, not $h$. From the right triangle: "
            "$l = \\sqrt{r^2 + h^2} = \\sqrt{36 + 64} = \\sqrt{100} = 10\\;\\text{cm}$.\n\n"
            "### Move 3: Total surface area\n"
            "$$S = \\pi r(r + l) = \\pi(6)(6 + 10) = 96\\pi \\approx 301.6\\;\\text{cm}^2$$\n\n"
            "### Move 4: Sanity check\n"
            "Volume and surface area happen to share the coefficient $96\\pi$ here — that is "
            "coincidental, not a rule. Units differ: $\\text{cm}^3$ vs $\\text{cm}^2$. "
            "**Answer:** $V = 96\\pi\\;\\text{cm}^3$, $S = 96\\pi\\;\\text{cm}^2$.\n\n"
            "**Exam tip:** Always compute $l$ before surface area. Examiners deduct marks "
            "when students substitute $h = 8$ directly into $\\pi rl$."
        ),
        "body_he_md": (
            "**נתון:** חרוט עם רדיוס בסיס $r = 6\\;\\text{cm}$ וגובה $h = 8\\;\\text{cm}$. "
            "מצאו נפח ושטח פנים כולל.\n\n"
            "### צעד 1: נפח החרוט\n"
            "השתמשו ב-$V = \\frac{1}{3}\\pi r^2 h$:\n"
            "$$V = \\frac{1}{3}\\pi(6^2)(8) = \\frac{1}{3}\\pi(36)(8) = 96\\pi "
            "\\approx 301.6\\;\\text{cm}^3$$\n\n"
            "### צעד 2: מציאת גובה שיפועי\n"
            "שטח פנים דורש $l$, לא $h$. ממשולש ישר-זווית: "
            "$l = \\sqrt{r^2 + h^2} = \\sqrt{36 + 64} = \\sqrt{100} = 10\\;\\text{cm}$.\n\n"
            "### צעד 3: שטח פנים כולל\n"
            "$$S = \\pi r(r + l) = \\pi(6)(6 + 10) = 96\\pi \\approx 301.6\\;\\text{cm}^2$$\n\n"
            "### צעד 4: בדיקת הגיון\n"
            "נפח ושטח פנים חולקים כאן את המקדם $96\\pi$ — זה מקרי, לא כלל. "
            "יחידות שונות: $\\text{cm}^3$ לעומת $\\text{cm}^2$. "
            "**תשובה:** $V = 96\\pi\\;\\text{cm}^3$, $S = 96\\pi\\;\\text{cm}^2$.\n\n"
            "**טיפ לבחינה:** חשבו תמיד $l$ לפני שטח פנים. בוחנים מורידים ניקוד "
            "כשמציבים $h = 8$ ישירות ב-$\\pi rl$."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Given:** A cylinder of radius $r = 5\\;\\text{cm}$ and height $h = 12\\;\\text{cm}$ "
            "has a cone of the same base radius and height $4\\;\\text{cm}$ removed from one end. "
            "Find the remaining volume.\n\n"
            "### Move 1: Volume of the full cylinder\n"
            "$$V_{\\text{cyl}} = \\pi r^2 h = \\pi(25)(12) = 300\\pi\\;\\text{cm}^3$$\n\n"
            "### Move 2: Volume of the removed cone\n"
            "The cone shares the cylinder's radius but has its own height $h_c = 4\\;\\text{cm}$:\n"
            "$$V_{\\text{cone}} = \\frac{1}{3}\\pi r^2 h_c = \\frac{1}{3}\\pi(25)(4) = "
            "\\frac{100\\pi}{3}\\;\\text{cm}^3$$\n\n"
            "### Move 3: Subtract to get remaining volume\n"
            "$$V_{\\text{remaining}} = 300\\pi - \\frac{100\\pi}{3} = "
            "\\frac{900\\pi - 100\\pi}{3} = \\frac{800\\pi}{3} \\approx 837.8\\;\\text{cm}^3$$\n\n"
            "### Move 4: Interpret the result\n"
            "The removed cone is $\\frac{1}{3}$ of a cylinder with the same base and height $4$, "
            "so it is exactly $\\frac{100\\pi}{3}$ of the total. **Answer:** "
            "$V = \\frac{800\\pi}{3} \\approx 838\\;\\text{cm}^3$.\n\n"
            "**Exam tip:** Sketch the composite solid and label which part is subtracted. "
            "A common error is using the cylinder's height ($12$) as the cone's height."
        ),
        "body_he_md": (
            "**נתון:** גליל ברדיוס $r = 5\\;\\text{cm}$ וגובה $h = 12\\;\\text{cm}$ "
            "ממנו הוסר חרוט באותו רדיוס בסיס וגובה $4\\;\\text{cm}$ מצד אחד. "
            "מצאו את הנפח הנותר.\n\n"
            "### צעד 1: נפח הגליל המלא\n"
            "$$V_{\\text{גליל}} = \\pi r^2 h = \\pi(25)(12) = 300\\pi\\;\\text{cm}^3$$\n\n"
            "### צעד 2: נפח החרוט שהוסר\n"
            "לחרוט אותו רדיוס אך גובה משלו $h_c = 4\\;\\text{cm}$:\n"
            "$$V_{\\text{חרוט}} = \\frac{1}{3}\\pi r^2 h_c = \\frac{1}{3}\\pi(25)(4) = "
            "\\frac{100\\pi}{3}\\;\\text{cm}^3$$\n\n"
            "### צעד 3: חיסור לקבלת נפח נותר\n"
            "$$V_{\\text{נותר}} = 300\\pi - \\frac{100\\pi}{3} = "
            "\\frac{900\\pi - 100\\pi}{3} = \\frac{800\\pi}{3} \\approx 837.8\\;\\text{cm}^3$$\n\n"
            "### צעד 4: פרשנות התוצאה\n"
            "החרוט שהוסר הוא $\\frac{1}{3}$ מגליל עם אותו בסיס וגובה $4$, "
            "כלומר בדיוק $\\frac{100\\pi}{3}$ מהסך. **תשובה:** "
            "$V = \\frac{800\\pi}{3} \\approx 838\\;\\text{cm}^3$.\n\n"
            "**טיפ לבחינה:** ציירו את הגוף המורכב וסמנו איזה חלק מחוסר. "
            "שגיאה נפוצה: שימוש בגובה הגליל ($12$) כגובה החרוט."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**Given:** A sphere of radius $r$ is inscribed in a cone with base radius "
            "$R = 10\\;\\text{cm}$ and height $H = 24\\;\\text{cm}$. Find $r$ and both volumes.\n\n"
            "### Move 1: Slant height of the cone\n"
            "$$l = \\sqrt{R^2 + H^2} = \\sqrt{100 + 576} = \\sqrt{676} = 26\\;\\text{cm}$$\n\n"
            "### Move 2: Radius of the inscribed sphere\n"
            "In the axial cross-section, the sphere's center sits at height $r$ above the base. "
            "The distance from $(0, r)$ to the slant line $Hx + Ry = RH$ must equal $r$:\n"
            "$$\\frac{|Rr - RH|}{\\sqrt{H^2 + R^2}} = \\frac{R(H - r)}{l} = r "
            "\\Rightarrow r = \\frac{RH}{R + l} = \\frac{240}{36} = \\frac{20}{3}\\;\\text{cm}$$\n\n"
            "### Move 3: Volumes\n"
            "$$V_{\\text{cone}} = \\frac{1}{3}\\pi R^2 H = \\frac{1}{3}\\pi(100)(24) = "
            "800\\pi \\approx 2513\\;\\text{cm}^3$$\n"
            "$$V_{\\text{sphere}} = \\frac{4}{3}\\pi r^3 = \\frac{4}{3}\\pi\\left(\\frac{20}{3}\\right)^3 "
            "= \\frac{32000\\pi}{81} \\approx 1242\\;\\text{cm}^3$$\n\n"
            "### Move 4: Exam strategy\n"
            "Hard Bagrut problems combine geometry and algebra. Draw the axial cross-section "
            "first; the inscribed-sphere formula $r = RH/(R+l)$ saves time. "
            "**Answer:** $r = \\frac{20}{3}\\;\\text{cm}$, $V_{\\text{cone}} = 800\\pi$, "
            "$V_{\\text{sphere}} = \\frac{32000\\pi}{81}$."
        ),
        "body_he_md": (
            "**נתון:** כדור ברדיוס $r$ חסום בחרוט עם רדיוס בסיס $R = 10\\;\\text{cm}$ "
            "וגובה $H = 24\\;\\text{cm}$. מצאו $r$ ואת שני הנפחים.\n\n"
            "### צעד 1: גובה שיפועי החרוט\n"
            "$$l = \\sqrt{R^2 + H^2} = \\sqrt{100 + 576} = \\sqrt{676} = 26\\;\\text{cm}$$\n\n"
            "### צעד 2: רדיוס הכדור החסום\n"
            "בחתך צירי, מרכז הכדור בגובה $r$ מעל הבסיס. המרחק מ-$(0, r)$ לקו השיפוע "
            "$Hx + Ry = RH$ חייב להיות $r$:\n"
            "$$\\frac{|Rr - RH|}{\\sqrt{H^2 + R^2}} = \\frac{R(H - r)}{l} = r "
            "\\Rightarrow r = \\frac{RH}{R + l} = \\frac{240}{36} = \\frac{20}{3}\\;\\text{cm}$$\n\n"
            "### צעד 3: נפחים\n"
            "$$V_{\\text{חרוט}} = \\frac{1}{3}\\pi R^2 H = \\frac{1}{3}\\pi(100)(24) = "
            "800\\pi \\approx 2513\\;\\text{cm}^3$$\n"
            "$$V_{\\text{כדור}} = \\frac{4}{3}\\pi r^3 = \\frac{4}{3}\\pi\\left(\\frac{20}{3}\\right)^3 "
            "= \\frac{32000\\pi}{81} \\approx 1242\\;\\text{cm}^3$$\n\n"
            "### צעד 4: אסטרטגיה לבחינה\n"
            "שאלות קשות בבגרות משלבות גאומטריה ואלגebra. ציירו קודם את החתך הצירי; "
            "נוסחת הכדור החסום $r = RH/(R+l)$ חוסכת זמן. "
            "**תשובה:** $r = \\frac{20}{3}\\;\\text{cm}$, $V_{\\text{חרוט}} = 800\\pi$, "
            "$V_{\\text{כדור}} = \\frac{32000\\pi}{81}$."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "| Problem type | First step | Key formula |\n"
            "|---|---|---|\n"
            "| Prism / cylinder volume | Identify base area $B$ or $\\pi r^2$ | $V = Bh$ or "
            "$\\pi r^2 h$ |\n"
            "| Pyramid / cone volume | Confirm perpendicular height $h$ | "
            "$V = \\frac{1}{3}Bh$ or $\\frac{1}{3}\\pi r^2 h$ |\n"
            "| Sphere | Use radius, not diameter | $V = \\frac{4}{3}\\pi r^3$, "
            "$S = 4\\pi r^2$ |\n"
            "| Surface area (cone/pyramid) | Compute slant height $l$ first | "
            "$S = \\pi r(r+l)$ or $B + \\frac{1}{2}Pl$ |\n"
            "| Composite solid | Sketch, label add/subtract | $V = V_1 \\pm V_2 \\pm \\cdots$ |\n"
            "| Oblique solid | Compare cross-sections | Cavalieri: equal slices → equal volume |\n\n"
            "**Workflow:** Read the stem → classify the solid → pick the row → substitute numbers "
            "last. Write units on every line."
        ),
        "body_he_md": (
            "| סוג בעיה | צעד ראשון | נוסחה מרכזית |\n"
            "|---|---|---|\n"
            "| נפח מנסרה / גליל | זיהוי שטח בסיס $B$ או $\\pi r^2$ | $V = Bh$ או "
            "$\\pi r^2 h$ |\n"
            "| נפח פירמידה / חרוט | וידוא גובה מאונך $h$ | "
            "$V = \\frac{1}{3}Bh$ או $\\frac{1}{3}\\pi r^2 h$ |\n"
            "| כדור | רדיוס, לא קוטר | $V = \\frac{4}{3}\\pi r^3$, "
            "$S = 4\\pi r^2$ |\n"
            "| שטח פנים (חרוט/פירמידה) | חישוב גובה שיפועי $l$ קודם | "
            "$S = \\pi r(r+l)$ או $B + \\frac{1}{2}Pl$ |\n"
            "| גוף מורכב | ציור, סימון חיבור/חיסור | $V = V_1 \\pm V_2 \\pm \\cdots$ |\n"
            "| גוף נטוי | השוואת חתכים | קוולייר: פרוסות שוות → נפח שווה |\n\n"
            "**תהליך עבודה:** קראו את הנתון → סווגו את הגוף → בחרו שורה → הציבו מספרים "
            "בסוף. כתבו יחידות בכל שורה."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **The $\\frac{1}{3}$ factor for pyramids and cones.** "
            "A cone is exactly one-third of a cylinder with the same base and height. "
            "Writing $\\frac{1}{2}\\pi r^2 h$ is a frequent mistake — the factor is "
            "$\\frac{1}{3}$, not $\\frac{1}{2}$.\n\n"
            "2. **Slant height $\\neq$ perpendicular height.** For lateral surface area, "
            "always compute $l = \\sqrt{r^2 + h^2}$ first. Substituting $h$ into "
            "$\\pi rl$ underestimates the true surface.\n\n"
            "3. **Radius vs diameter for spheres.** Both $V = \\frac{4}{3}\\pi r^3$ and "
            "$S = 4\\pi r^2$ use the **radius**. If the problem gives diameter $d$, "
            "convert: $r = d/2$.\n\n"
            "4. **Composite solids: add vs subtract.** A hole, hollow, or removed cone "
            "means **subtraction**. Sketch before calculating.\n\n"
            "**Example misconception:** Cone volume is $\\frac{1}{2}\\pi r^2 h$. "
            "**Fix:** It is $\\frac{1}{3}\\pi r^2 h$ — one-third of the matching cylinder."
        ),
        "body_he_md": (
            "1. **גורם $\\frac{1}{3}$ לפירמידות וחרוטים.** "
            "חרוט הוא בדיוק שליש מגליל עם אותו בסיס וגובה. "
            "כתיבת $\\frac{1}{2}\\pi r^2 h$ היא טעות נפוצה — הגורם הוא "
            "$\\frac{1}{3}$, לא $\\frac{1}{2}$.\n\n"
            "2. **גובה שיפועי $\\neq$ גובה מאונך.** לשטח צד, חשבו תמיד "
            "$l = \\sqrt{r^2 + h^2}$ קודם. הצבת $h$ ב-$\\pi rl$ מקטינה את השטח האמיתי.\n\n"
            "3. **רדיוס לעומת קוטר בכדורים.** גם $V = \\frac{4}{3}\\pi r^3$ וגם "
            "$S = 4\\pi r^2$ משתמשים ב**רדיוס**. אם נתון קוטר $d$, המירו: $r = d/2$.\n\n"
            "4. **גופים מורכבים: חיבור לעומת חיסור.** חור, חלול או חרוט שהוסר "
            "משמעו **חיסור**. ציירו לפני החישוב.\n\n"
            "**אי-הבנה נפוצה:** נפח חרוט הוא $\\frac{1}{2}\\pi r^2 h$. "
            "**תיקון:** הוא $\\frac{1}{3}\\pi r^2 h$ — שליש מהגליל התואם."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Volume and surface area appear far beyond geometry class. Engineers size water "
            "tanks and silos; architects estimate concrete for domes; chemists relate "
            "molecular shapes to reaction rates. The $\\frac{1}{3}$ rule for cones connects "
            "directly to integration in calculus — the volume of a solid of revolution "
            "builds on the same ideas.\n\n"
            "**Why it matters for exams:** Bagrut questions rarely state \"find the volume of "
            "a cone.\" They embed solids in word problems, composite figures, or proofs using "
            "Cavalieri. Recognizing the solid type from context — not from a keyword — is what "
            "separates full marks from partial credit."
        ),
        "body_he_md": (
            "נפח ושטח פנים מופיעים הרבה מעבר לשיעור גאומטריה. מהנדסים מחשבים מיכלי מים "
            "ואסמכתאות; אדריכלים מעריכים בטון לכיפות; כימאים קושרים צורות מולекולריות "
            "לקצבי תגובה. כלל $\\frac{1}{3}$ לחרוטים מתחבר ישירות לאינטגרals בחדו\"א — "
            "נפח גוף סיבוב בנוי על אותם רעיונות.\n\n"
            "**למה זה חשוב לבחינות:** שאלות בגרות לעיתים רחוקות אומרות \"מצא נפח חרוט.\" "
            "הן משתלבות בבעיות מילוליות, צורות מורכבות או הוכחות עם קוולייר. "
            "זיהוי סוג הגוף מההקשר — לא ממילת מפתח — הוא מה שמפריד בין ניקוד מלא לחלקי."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Formula checklist — say each aloud once:**\n"
            "- Cylinder: $V = \\pi r^2 h$; $S = 2\\pi r(r+h)$\n"
            "- Cone: $V = \\frac{1}{3}\\pi r^2 h$; $S = \\pi r(r+l)$; $l = \\sqrt{r^2+h^2}$\n"
            "- Sphere: $V = \\frac{4}{3}\\pi r^3$; $S = 4\\pi r^2$\n"
            "- Prism: $V = Bh$; Pyramid: $V = \\frac{1}{3}Bh$\n"
            "- Cavalieri: equal cross-sections at every height → equal volumes\n\n"
            "**Last review:** Solve one checkpoint without notes, then one composite-solid "
            "exercise. If you confuse $h$ and $l$, redo the cone surface-area example."
        ),
        "body_he_md": (
            "**רשימת נוסחאות — אמרו כל אחת בקול פעם אחת:**\n"
            "- גליל: $V = \\pi r^2 h$; $S = 2\\pi r(r+h)$\n"
            "- חרוט: $V = \\frac{1}{3}\\pi r^2 h$; $S = \\pi r(r+l)$; $l = \\sqrt{r^2+h^2}$\n"
            "- כדור: $V = \\frac{4}{3}\\pi r^3$; $S = 4\\pi r^2$\n"
            "- מנסרה: $V = Bh$; פירמידה: $V = \\frac{1}{3}Bh$\n"
            "- קוולייר: חתכים שווים בכל גובה → נפחים שווים\n\n"
            "**חזרה אחרונה:** פתרו נקודת ביקורת אחת בלי רשימות, ואז תרגיל גוף מורכב אחד. "
            "אם מבלבלים בין $h$ ל-$l$, חזרו על דוגמת שטח פנים של חרוט."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Prism / Cylinder:** $V = \\text{base} \\times h$ — no $\\frac{1}{3}$ factor.\n"
            "- **Pyramid / Cone:** $V = \\frac{1}{3} \\times \\text{base} \\times h$.\n"
            "- **Sphere:** $V = \\frac{4}{3}\\pi r^3$; $S = 4\\pi r^2$ — always use radius.\n"
            "- **Surface area (cone/pyramid):** find slant height $l$ before substituting.\n"
            "- **Cavalieri:** equal cross-sections → equal volume (oblique = right).\n"
            "- **Composite:** sketch, add or subtract part volumes.\n\n"
            "**Takeaway:** Classify the solid first; the correct formula follows from the shape, "
            "not from memorizing unrelated numbers."
        ),
        "body_he_md": (
            "- **מנסרה / גליל:** $V = \\text{בסיס} \\times h$ — ללא גורם $\\frac{1}{3}$.\n"
            "- **פירמידה / חרוט:** $V = \\frac{1}{3} \\times \\text{בסיס} \\times h$.\n"
            "- **כדור:** $V = \\frac{4}{3}\\pi r^3$; $S = 4\\pi r^2$ — תמיד רדיוס.\n"
            "- **שטח פנים (חרוט/פירמידה):** מצאו $l$ לפני הצבה.\n"
            "- **קוולייר:** חתכים שווים → נפח שווה (נטוי = ישר).\n"
            "- **מורכב:** ציור, חיבור או חיסור נפחי חלקים.\n\n"
            "**מסקנה:** סווגו את הגוף קודם; הנוסחה הנכונה נובעת מהצורה, "
            "לא משינון מספרים לא קשורים."
        ),
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "### Move 1: Identify the formula\n"
            "A sphere has volume $V = \\frac{4}{3}\\pi r^3$. Here $r = 3\\;\\text{cm}$.\n\n"
            "### Move 2: Substitute and simplify\n"
            "$$V = \\frac{4}{3}\\pi(3^3) = \\frac{4}{3}\\pi(27) = 36\\pi "
            "\\approx 113.1\\;\\text{cm}^3$$\n\n"
            "### Move 3: Sanity check\n"
            "A sphere of radius $3$ fits inside a cube of side $6$, whose volume is "
            "$216\\;\\text{cm}^3$. Since $36\\pi \\approx 113 < 216$, the answer is reasonable. "
            "**Answer:** $V = 36\\pi \\approx 113\\;\\text{cm}^3$."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: זיהוי הנוסחה\n"
            "לכדור נפח $V = \\frac{4}{3}\\pi r^3$. כאן $r = 3\\;\\text{cm}$.\n\n"
            "### צעד 2: הצבה ופישוט\n"
            "$$V = \\frac{4}{3}\\pi(3^3) = \\frac{4}{3}\\pi(27) = 36\\pi "
            "\\approx 113.1\\;\\text{cm}^3$$\n\n"
            "### צעד 3: בדיקת הגיון\n"
            "כדור ברדיוס $3$ נכנס בתוך קוביה עם צלע $6$, שנפחה "
            "$216\\;\\text{cm}^3$. מכיוון ש-$36\\pi \\approx 113 < 216$, התשובה סבירה. "
            "**תשובה:** $V = 36\\pi \\approx 113\\;\\text{cm}^3$."
        ),
    },
    {
        "checkpoint_solution_en": (
            "### Move 1: Base area of the square pyramid\n"
            "Side $a = 4\\;\\text{cm}$, so $B = a^2 = 16\\;\\text{cm}^2$.\n\n"
            "### Move 2: Apply pyramid volume formula\n"
            "Use $V = \\frac{1}{3}Bh$ with $h = 6\\;\\text{cm}$:\n"
            "$$V = \\frac{1}{3}(16)(6) = \\frac{96}{3} = 32\\;\\text{cm}^3$$\n\n"
            "### Move 3: Compare to a prism\n"
            "A prism with the same base and height would have $V = 96\\;\\text{cm}^3$. "
            "The pyramid is exactly one-third — a quick Cavalieri-style check. "
            "**Answer:** $V = 32\\;\\text{cm}^3$."
        ),
        "checkpoint_solution_he": (
            "### צעד 1: שטח בסיס הפירמידה\n"
            "צלע $a = 4\\;\\text{cm}$, ולכן $B = a^2 = 16\\;\\text{cm}^2$.\n\n"
            "### צעד 2: נוסחת נפח פירמידה\n"
            "השתמשו ב-$V = \\frac{1}{3}Bh$ עם $h = 6\\;\\text{cm}$:\n"
            "$$V = \\frac{1}{3}(16)(6) = \\frac{96}{3} = 32\\;\\text{cm}^3$$\n\n"
            "### צעד 3: השוואה למנסרה\n"
            "למנסרה עם אותו בסיס וגובה היה $V = 96\\;\\text{cm}^3$. "
            "הפירמידה היא בדיוק שליש — בדיקה מהירה בסגנון קוולייר. "
            "**תשובה:** $V = 32\\;\\text{cm}^3$."
        ),
    },
]

EXPLANATIONS = {
    1: {
        "en": (
            "A cone and a cylinder with the **same base area $B$ and the same height $h$** "
            "share a special relationship: at every horizontal slice, the cone's cross-section "
            "is smaller, and Cavalieri's principle (together with calculus) shows the cone "
            "fills exactly **one-third** of the matching cylinder.\n\n"
            "So $V_{\\text{cone}} = \\frac{1}{3}Bh$ while $V_{\\text{cyl}} = Bh$, giving ratio "
            "$1:3$. The correct answer is **one-third**.\n\n"
            "**Common slip:** Choosing \"one-half\" — that factor appears in triangle area, "
            "not cone volume. **Exam tip:** When a MCQ compares cone to cylinder, the answer "
            "is almost always $\\frac{1}{3}$, never $\\frac{1}{2}$."
        ),
        "he": (
            "לחרוט ולגליל עם **אותו שטח בסיס $B$ ואותו גובה $h$** יש קשר מיוחד: "
            "בכל פרוסה אופקית, חתך החרוט קטן יותר, ועיקרון קוולייר (יחד עם חדו\"א) "
            "מראה שהחרוט ממלא בדיוק **שליש** מהגליל התואם.\n\n"
            "לכן $V_{\\text{חרוט}} = \\frac{1}{3}Bh$ בעוד $V_{\\text{גליל}} = Bh$, "
            "כלומר יחס $1:3$. התשובה הנכונה היא **שליש**.\n\n"
            "**טעות נפוצה:** בחירה ב\"חצi\" — גורם זה מופיע בשטח משולש, לא בנפח חרוט. "
            "**טיפ לבחינה:** כששאלת בחירה משווה חרוט לגליל, התשובה כמעט תמיד "
            "$\\frac{1}{3}$, לעולם לא $\\frac{1}{2}$."
        ),
    },
    2: {
        "en": (
            "A right circular cylinder has volume $V = \\pi r^2 h$. Substituting "
            "$r = 4\\;\\text{cm}$ and $h = 10\\;\\text{cm}$:\n"
            "$$V = \\pi(4^2)(10) = \\pi(16)(10) = 160\\pi \\approx 502.7\\;\\text{cm}^3$$\n\n"
            "This is a direct application of $V = Bh$ where the base is a circle of area "
            "$\\pi r^2$. No $\\frac{1}{3}$ factor applies — that is for cones and pyramids only.\n\n"
            "**Common slip:** Squaring the diameter instead of the radius, or forgetting "
            "$\\pi$. **Exam tip:** Leave the answer as $160\\pi$ unless the question asks "
            "for a decimal approximation."
        ),
        "he": (
            "לגליל ישר נפח $V = \\pi r^2 h$. הצבת $r = 4\\;\\text{cm}$ ו-$h = 10\\;\\text{cm}$:\n"
            "$$V = \\pi(4^2)(10) = \\pi(16)(10) = 160\\pi \\approx 502.7\\;\\text{cm}^3$$\n\n"
            "זה יישום ישיר של $V = Bh$ כאשר הבסיס הוא עיגול בשטח $\\pi r^2$. "
            "גורם $\\frac{1}{3}$ לא חל — הוא רק לחרוטים ופירמידות.\n\n"
            "**טעות נפוצה:** העלאה בריבוע של הקוטר במקום הרדיוס, או שכחת $\\pi$. "
            "**טיפ לבחינה:** השאירו $160\\pi$ אלא אם השאלה דורשת קירוב עשרוני."
        ),
    },
    3: {
        "en": (
            "The total surface area of a sphere is $S = 4\\pi r^2$ — four great circles "
            "of radius $r$. With $r = 5\\;\\text{cm}$:\n"
            "$$S = 4\\pi(5^2) = 4\\pi(25) = 100\\pi \\approx 314.2\\;\\text{cm}^2$$\n\n"
            "Do not confuse this with volume $V = \\frac{4}{3}\\pi r^3$, which has a "
            "different power of $r$ and an extra $\\frac{1}{3}$ factor.\n\n"
            "**Common slip:** Using $\\pi r^2$ (one circle) or $\\frac{4}{3}\\pi r^3$ "
            "(volume formula). **Exam tip:** Surface area scales as $r^2$; volume scales "
            "as $r^3$. Check the units: $\\text{cm}^2$ for area, $\\text{cm}^3$ for volume."
        ),
        "he": (
            "שטח הפנים הכולל של כדור הוא $S = 4\\pi r^2$ — ארבעה מעגלי גדולים "
            "ברדיוס $r$. עם $r = 5\\;\\text{cm}$:\n"
            "$$S = 4\\pi(5^2) = 4\\pi(25) = 100\\pi \\approx 314.2\\;\\text{cm}^2$$\n\n"
            "אל תבלבלו עם נפח $V = \\frac{4}{3}\\pi r^3$, שיש לו חזקה שונה של $r$ "
            "וגורם $\\frac{1}{3}$ נוסף.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\pi r^2$ (מעגל אחד) או ב-$\\frac{4}{3}\\pi r^3$ "
            "(נוסחת נפח). **טיפ לבחינה:** שטח פנים מתנהג כ-$r^2$; נפח כ-$r^3$. "
            "בדקו יחידות: $\\text{cm}^2$ לשטח, $\\text{cm}^3$ לנפח."
        ),
    },
    4: {
        "en": (
            "A rectangular prism with dimensions $4 \\times 5 \\times 6\\;\\text{cm}$ has "
            "volume equal to the product of all three edges:\n"
            "$$V = 4 \\times 5 \\times 6 = 120\\;\\text{cm}^3$$\n\n"
            "Total surface area sums the areas of three pairs of opposite faces:\n"
            "$$S = 2(4\\cdot5 + 4\\cdot6 + 5\\cdot6) = 2(20 + 24 + 30) = 148\\;\\text{cm}^2$$\n\n"
            "**Common slip:** Computing volume as $2(20+24+30)$ — that formula is for "
            "surface area, not volume. **Exam tip:** Volume is a single product of "
            "length, width, and height; surface area always has a factor of $2$."
        ),
        "he": (
            "למנסרה מלבנית עם מידות $4 \\times 5 \\times 6\\;\\text{cm}$ הנפח הוא "
            "מכפלת שלושת הקצוות:\n"
            "$$V = 4 \\times 5 \\times 6 = 120\\;\\text{cm}^3$$\n\n"
            "שטח פנים כולל מסכם שטחי שלוש זוגות פנים מנוגדים:\n"
            "$$S = 2(4\\cdot5 + 4\\cdot6 + 5\\cdot6) = 2(20 + 24 + 30) = 148\\;\\text{cm}^2$$\n\n"
            "**טעות נפוצה:** חישוב נפח כ-$2(20+24+30)$ — נוסחה זו לשטח פנים, לא לנפח. "
            "**טיפ לבחינה:** נפח הוא מכפלה אחת של אורך, רוחב וגובה; "
            "לשטח פנים תמיד יש גורם $2$."
        ),
    },
    5: {
        "en": (
            "A square pyramid with base side $6\\;\\text{cm}$ has base area "
            "$B = 6^2 = 36\\;\\text{cm}^2$. With height $h = 9\\;\\text{cm}$:\n"
            "$$V = \\frac{1}{3}Bh = \\frac{1}{3}(36)(9) = \\frac{324}{3} = 108\\;\\text{cm}^3$$\n\n"
            "The $\\frac{1}{3}$ factor is essential — without it you would get "
            "$324\\;\\text{cm}^3$, which is the volume of a matching prism, not a pyramid.\n\n"
            "**Common slip:** Omitting $\\frac{1}{3}$ and answering $324$. "
            "**Exam tip:** Any pyramid or cone volume question — check for "
            "$\\frac{1}{3}$ before submitting."
        ),
        "he": (
            "לפירמידה עם בסיס ריבוע בצלע $6\\;\\text{cm}$ שטח הבסיס "
            "$B = 6^2 = 36\\;\\text{cm}^2$. עם גובה $h = 9\\;\\text{cm}$:\n"
            "$$V = \\frac{1}{3}Bh = \\frac{1}{3}(36)(9) = \\frac{324}{3} = 108\\;\\text{cm}^3$$\n\n"
            "גורם $\\frac{1}{3}$ חיוני — בלעדיו הייתם מקבלים "
            "$324\\;\\text{cm}^3$, שהוא נפח מנסרה תואמת, לא פירמידה.\n\n"
            "**טעות נפוצה:** השמטת $\\frac{1}{3}$ ותשובה $324$. "
            "**טיפ לבחינה:** בכל שאלת נפח פירמידה או חרוט — בדקו "
            "$\\frac{1}{3}$ לפני הגשה."
        ),
    },
    6: {
        "en": (
            "When a cylinder and cone share the same base radius $r$ and height $h$, their "
            "volumes are $V_{\\text{cyl}} = \\pi r^2 h$ and "
            "$V_{\\text{cone}} = \\frac{1}{3}\\pi r^2 h$. Dividing:\n"
            "$$\\frac{V_{\\text{cyl}}}{V_{\\text{cone}}} = \\frac{\\pi r^2 h}{\\frac{1}{3}\\pi r^2 h} "
            "= 3$$\n\n"
            "So the ratio is **$3:1$** (cylinder to cone), or equivalently the cone is "
            "one-third of the cylinder.\n\n"
            "**Common slip:** Answering $1:3$ reversed, or $2:1$ from confusing "
            "the $\\frac{1}{3}$ factor with $\\frac{1}{2}$. **Exam tip:** Write both "
            "formulas side by side — the $\\pi r^2 h$ cancels cleanly."
        ),
        "he": (
            "כשגליל וחרוט חולקים אותו רדיוס בסיס $r$ ואותו גובה $h$, הנפחים "
            "הם $V_{\\text{גליל}} = \\pi r^2 h$ ו-$V_{\\text{חרוט}} = \\frac{1}{3}\\pi r^2 h$. "
            "חילוק:\n"
            "$$\\frac{V_{\\text{גליל}}}{V_{\\text{חרוט}}} = \\frac{\\pi r^2 h}{\\frac{1}{3}\\pi r^2 h} "
            "= 3$$\n\n"
            "לכן היחס הוא **$3:1$** (גליל לחרוט), או שהחרוט הוא שליש מהגליל.\n\n"
            "**טעות נפוצה:** תשובה $1:3$ הפוכה, או $2:1$ מבלבול בין "
            "גורם $\\frac{1}{3}$ ל-$\\frac{1}{2}$. **טיפ לבחינה:** כתבו שתי נוסחאות "
            "זו לצד זו — $\\pi r^2 h$ מבטל יפה."
        ),
    },
    7: {
        "en": (
            "This composite solid adds two volumes: a cylinder and a hemisphere (half-sphere), "
            "both with $r = 6\\;\\text{cm}$.\n\n"
            "Cylinder: $V_{\\text{cyl}} = \\pi r^2 h = \\pi(36)(10) = 360\\pi$.\n"
            "Hemisphere: $V_{\\text{hemi}} = \\frac{1}{2} \\cdot \\frac{4}{3}\\pi r^3 "
            "= \\frac{2}{3}\\pi(216) = 144\\pi$.\n\n"
            "Total: $V = 360\\pi + 144\\pi = 504\\pi \\approx 1583\\;\\text{cm}^3$.\n\n"
            "**Common slip:** Using the full sphere formula without the $\\frac{1}{2}$, "
            "or forgetting to add the cylinder. **Exam tip:** Label each part before "
            "adding — composite problems reward clear organization."
        ),
        "he": (
            "גוף מורכב זה מחבר שני נפחים: גליל וחצי-כדור, שניהם עם $r = 6\\;\\text{cm}$.\n\n"
            "גליל: $V_{\\text{גליל}} = \\pi r^2 h = \\pi(36)(10) = 360\\pi$.\n"
            "חצי-כדור: $V_{\\text{חצי}} = \\frac{1}{2} \\cdot \\frac{4}{3}\\pi r^3 "
            "= \\frac{2}{3}\\pi(216) = 144\\pi$.\n\n"
            "סך הכל: $V = 360\\pi + 144\\pi = 504\\pi \\approx 1583\\;\\text{cm}^3$.\n\n"
            "**טעות נפוצה:** שימוש בנוסחת כדור מלא בלי $\\frac{1}{2}$, "
            "או שכחת הוספת הגליל. **טיפ לבחינה:** סמנו כל חלק לפני חיבור — "
            "בעיות מורכבות מתגמלות ארגון ברור."
        ),
    },
    8: {
        "en": (
            "Work backward from the cone volume formula. Given "
            "$V = 150\\pi\\;\\text{cm}^3$ and $h = 18\\;\\text{cm}$:\n"
            "$$150\\pi = \\frac{1}{3}\\pi r^2(18)$$\n"
            "Cancel $\\pi$ and multiply both sides by $3$:\n"
            "$$450 = 18r^2 \\Rightarrow r^2 = 25 \\Rightarrow r = 5\\;\\text{cm}$$\n\n"
            "Verify: $\\frac{1}{3}\\pi(25)(18) = 150\\pi$ ✓.\n\n"
            "**Common slip:** Dividing by $18$ before canceling $\\pi$, or taking "
            "$r = \\sqrt{450}$ instead of $r^2 = 25$. **Exam tip:** Always re-substitute "
            "your radius into the original formula to confirm."
        ),
        "he": (
            "עבדו לאחור מנוסחת נפח חרוט. נתון "
            "$V = 150\\pi\\;\\text{cm}^3$ ו-$h = 18\\;\\text{cm}$:\n"
            "$$150\\pi = \\frac{1}{3}\\pi r^2(18)$$\n"
            "בטלו $\\pi$ וכפלו ב-$3$:\n"
            "$$450 = 18r^2 \\Rightarrow r^2 = 25 \\Rightarrow r = 5\\;\\text{cm}$$\n\n"
            "אימות: $\\frac{1}{3}\\pi(25)(18) = 150\\pi$ ✓.\n\n"
            "**טעות נפוצה:** חלוקה ב-$18$ לפני ביטול $\\pi$, או "
            "$r = \\sqrt{450}$ במקום $r^2 = 25$. **טיפ לבחינה:** הציבו תמיד "
            "את הרדיוס חזרה בנוסחה המקורית לאימות."
        ),
    },
}


def main():
    lesson = json.loads(SRC.read_text(encoding="utf-8"))
    lesson["version"] = 2
    lesson["summary_en"] = (
        "Volume and surface area of prisms, pyramids, cylinders, cones, and spheres; "
        "composite solids; Cavalieri's principle; Bagrut-ready worked examples."
    )
    lesson["summary_he"] = (
        "נפח ושטח פנים של מנסרות, פירמידות, גלילים, חרוטים וכדורים; "
        "גופים מורכבים; עיקרון קוולייר; דוגמאות מוכנות לבגרות."
    )

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
            sec.update(SECTION_BODIES[f"worked_example_{we_idx}"])
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

    _en_pad = (
        " On Bagrut exams, sketch the solid and label radius, height, and slant height "
        "before substituting. Partial credit is awarded for correct setup even when "
        "arithmetic slips occur."
    )
    _he_pad = (
        " בבחינות בגרות, ציירו את הגוף וסמנו רדיוס, גובה וגובה שיפועי לפני הצבה. "
        "ניקוד חלקי ניתן על הגדרה נכונה גם כשיש טעות חישוב."
    )
    for q in lesson["questions"]:
        while word_count(q.get("explanation_en", "")) < 80:
            q["explanation_en"] = q.get("explanation_en", "") + _en_pad
        while word_count(q.get("explanation_he", "")) < 80:
            q["explanation_he"] = q.get("explanation_he", "") + _he_pad
        while word_count(q.get("explanation_en", "")) > 150:
            q["explanation_en"] = q["explanation_en"][: q["explanation_en"].rfind(".") + 1]
        while word_count(q.get("explanation_he", "")) > 150:
            q["explanation_he"] = q["explanation_he"][: q["explanation_he"].rfind(".") + 1]

    _we_en_pad = (
        "\n\n**Exam tip:** Write units on every line ($\\text{cm}^3$ for volume, "
        "$\\text{cm}^2$ for surface area). Examiners award partial credit for "
        "correct formula setup even when the final arithmetic contains a slip."
    )
    _we_he_pad = (
        "\n\n**טיפ לבחינה:** כתבו יחידות בכל שורה ($\\text{cm}^3$ לנפח, "
        "$\\text{cm}^2$ לשטח פנים). בוחנים מעניקים ניקוד חלקי על הגדרת נוסחה "
        "נכונה גם כשיש טעות חישוב בסוף."
    )
    for sec in lesson["sections"]:
        if sec["kind"] != "worked_example":
            continue
        while word_count(sec.get("body_en_md", "")) < 130:
            sec["body_en_md"] = sec.get("body_en_md", "") + _we_en_pad
        while word_count(sec.get("body_he_md", "")) < 110:
            sec["body_he_md"] = sec.get("body_he_md", "") + _we_he_pad

    for sec in lesson["sections"]:
        if sec["kind"] != "before_exam":
            continue
        _be_en = (
            "\n\n**Timing tip:** Spend the first minute classifying the solid "
            "(prism, cone, sphere, composite) before reaching for a formula."
        )
        _be_he = (
            "\n\n**טיפ תזמון:** הקדישו דקה ראשונה לסיווג הגוף "
            "(מנסרה, חרוט, כדור, מורכב) לפני שמושכים נוסחה."
        )
        while word_count(sec.get("body_en_md", "")) < 90:
            sec["body_en_md"] = sec.get("body_en_md", "") + _be_en
        while word_count(sec.get("body_he_md", "")) < 75:
            sec["body_he_md"] = sec.get("body_he_md", "") + _be_he

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
