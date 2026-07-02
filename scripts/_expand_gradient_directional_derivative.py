#!/usr/bin/env python3
"""Expand gradient_directional_derivative.json — MIN_WORDS, Hebrew parity, question explanations."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/gradient_directional_derivative.json"

MIN = {
    "intro": (110, 90),
    "definition": (130, 110),
    "theory": (160, 130),
    "worked_example": (130, 110),
    "pitfall": (100, 85),
    "why_matters": (90, 75),
    "method_guide": (100, 85),
    "before_exam": (90, 75),
    "summary": (70, 60),
}


def wc(text: str) -> int:
    if not text:
        return 0
    t = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    t = re.sub(r"\$[^$\n]+\$", " MATH ", t)
    t = re.sub(r"[#*_`>\[\]()]", " ", t)
    return len([w for w in t.split() if w])


def he_ratio(text: str) -> float:
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def he_weak(he: str, en: str) -> bool:
    he, en = (he or "").strip(), (en or "").strip()
    if not he:
        return True
    if wc(he) / max(wc(en), 1) < 0.55:
        return True
    if he_ratio(he) < 0.15 and wc(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


def fmt_expl(why_en, how_en, slip_en, tip_en, why_he, how_he, slip_he, tip_he) -> tuple[str, str]:
    en = (
        f"**Why this is correct:**\n{why_en}\n\n"
        f"**How to think about it:**\n{how_en}\n\n"
        f"**Common slip:**\n{slip_en}\n\n"
        f"**Exam tip:**\n{tip_en}"
    )
    he = (
        f"**למה זה נכון:**\n{why_he}\n\n"
        f"**איך לחשוב על זה:**\n{how_he}\n\n"
        f"**טעות נפוצה:**\n{slip_he}\n\n"
        f"**טיפ לבחינה:**\n{tip_he}"
    )
    return en, he


INTRO_EN = """Partial derivatives tell us how fast $f(x,y)$ changes when we move along the coordinate axes — holding one variable fixed. But real motion rarely follows the grid: a hiker climbs a ridge at $45°$, heat flows diagonally across a plate, and an optimizer in machine learning steps in a direction chosen by the algorithm, not by $x$ or $y$ alone.

The **directional derivative** $D_{\\mathbf{u}}f$ answers: "How fast does $f$ change if I move from $(a,b)$ in direction $\\mathbf{u}$?" The **gradient** $\\nabla f=(f_x,f_y)$ collects all partial information into one vector that points toward **steepest ascent**; its magnitude $|\\nabla f|$ is the maximum rate of increase.

This lesson bridges `concept:partial_derivatives` to optimization and geometry. You will compute $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$, find directions of fastest rise and fall, and use $\\nabla f\\perp$ level curves — the same perpendicularity that appears on contour maps and in gradient descent."""

INTRO_HE = """נגזרות חלקיות מודדות כמה מהר $f(x,y)$ משתנה כשזזים לאורך צירי הקואורדינטות — תוך קיבוע משתנה אחד. אך תנועה אמיתית לעיתים רחוקות עוקבת אחרי הרשת: מטפס עולה ב-$45°$, חום זורם באלכסון על לוח, ואלגוריתם אופטימיזציה בלמידת מכונה צועד בכיוון שנבחר, לא רק ב-$x$ או ב-$y$.

**הנגזרת הכיוונית** $D_{\\mathbf{u}}f$ עונה: "כמה מהר $f$ משתנה אם זזים מ-$(a,b)$ בכיוון $\\mathbf{u}$?" **הגרדיאנט** $\\nabla f=(f_x,f_y)$ אוסף את כל המידע החלקי לוקטור אחד שמצביע ל**עלייה התלולה ביותר**; גודלו $|\\nabla f|$ הוא שיעור העלייה המרבי.

שיעור זה מחבר את `concept:partial_derivatives` לאופטימיזציה ולגיאומטריה. תחשבו $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$, תמצאו כיווני עלייה וירידה מרביים, ותשתמשו ב-$\\nabla f\\perp$ עקומות גובה — אותה ניצבות שמופיעה במפות קווי מתאר ובירידת גרדיאנט."""

DEF_EN = """**Directional derivative (limit definition):** For a unit vector $\\mathbf{u}=(u_1,u_2)$,
$$D_{\\mathbf{u}}f(a,b)=\\lim_{h\\to 0}\\frac{f(a+hu_1,b+hu_2)-f(a,b)}{h}.$$
This is the ordinary derivative of $f$ along the straight-line path starting at $(a,b)$ in direction $\\mathbf{u}$.

**Computational formula (when $f$ is differentiable):**
$$D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}=f_x u_1+f_y u_2.$$

**Gradient:**
$$\\nabla f(x,y)=(f_x,f_y)=f_x\\,\\mathbf{i}+f_y\\,\\mathbf{j}.$$

**Dot-product form and angle:** $D_{\\mathbf{u}}f=|\\nabla f|\\cos\\theta$, where $\\theta$ is the angle between $\\nabla f$ and $\\mathbf{u}$.

**Extreme directional rates:**
- **Maximum** $D_{\\mathbf{u}}f=|\\nabla f|$ when $\\mathbf{u}=\\nabla f/|\\nabla f|$ (steepest ascent).
- **Minimum** $D_{\\mathbf{u}}f=-|\\nabla f|$ when $\\mathbf{u}=-\\nabla f/|\\nabla f|$ (steepest descent).
- **Zero** when $\\mathbf{u}\\perp\\nabla f$ — motion along a level curve.

**Geometry:** $\\nabla f$ is **perpendicular** to the level curve $f(x,y)=c$ at every point where $\\nabla f\\neq\\mathbf{0}$. In 3D, $\\nabla F$ is normal to the level surface $F(x,y,z)=c$.

**Critical points:** When $\\nabla f(a,b)=\\mathbf{0}$, every directional derivative at $(a,b)$ is zero — the function is flat in all directions to first order. This links gradients to local maxima, minima, and saddle points in the next optimization unit."""

DEF_HE = """**נגזרת כיוונית (הגדרת גבול):** לוקטור יחידה $\\mathbf{u}=(u_1,u_2)$,
$$D_{\\mathbf{u}}f(a,b)=\\lim_{h\\to 0}\\frac{f(a+hu_1,b+hu_2)-f(a,b)}{h}.$$
זו הנגזרת הרגילה של $f$ לאורך מסלול ישר שמתחיל ב-$(a,b)$ בכיוון $\\mathbf{u}$.

**נוסחת חישוב (כאשר $f$ גזירה):**
$$D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}=f_x u_1+f_y u_2.$$

**גרדיאנט:**
$$\\nabla f(x,y)=(f_x,f_y)=f_x\\,\\mathbf{i}+f_y\\,\\mathbf{j}.$$

**צורת מכפלה סקalarית וזווית:** $D_{\\mathbf{u}}f=|\\nabla f|\\cos\\theta$, כאשר $\\theta$ היא הזווית בין $\\nabla f$ ל-$\\mathbf{u}$.

**קצבי כיוון קיצוניים:**
- **מקסימום** $D_{\\mathbf{u}}f=|\\nabla f|$ כאשר $\\mathbf{u}=\\nabla f/|\\nabla f|$ (עלייה תלולה).
- **מינימום** $D_{\\mathbf{u}}f=-|\\nabla f|$ כאשר $\\mathbf{u}=-\\nabla f/|\\nabla f|$ (ירידה תלולה).
- **אפס** כאשר $\\mathbf{u}\\perp\\nabla f$ — תנועה לאורך עקומת גובה.

**גיאומטריה:** $\\nabla f$ **ניצב** לעקומת הגובה $f(x,y)=c$ בכל נקודה שבה $\\nabla f\\neq\\mathbf{0}$. ב-3D, $\\nabla F$ הוא נורמל למשטח הגובה $F(x,y,z)=c$.

**נקודות קריטיות:** כאשר $\\nabla f(a,b)=\\mathbf{0}$, כל נגזרת כיוונית ב-$(a,b)$ מתאפסת — הפונקציה שטוחה בכל הכיוונים בסדר ראשון. זה מקשר גרדיאנטים למקסימום, מינימום ונקודות אוכף ביחידת האופטימיזציה."""

THEORY_EN = """**Why $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$:** Parametrize motion in direction $\\mathbf{u}$ by $\\mathbf{r}(t)=(a+tu_1,b+tu_2)$. Then $f$ along the path is $f(\\mathbf{r}(t))$, and by the chain rule at $t=0$:
$$\\frac{d}{dt}f(\\mathbf{r}(t))\\Big|_{t=0}=f_x u_1+f_y u_2=\\nabla f\\cdot\\mathbf{u}.$$

**Maximum rate (Cauchy–Schwarz):** For unit $\\mathbf{u}$, $|\\nabla f\\cdot\\mathbf{u}|\\le|\\nabla f||\\mathbf{u}|=|\\nabla f|$, with equality when $\\mathbf{u}$ is parallel to $\\nabla f$. Positive dot product → ascent; negative → descent.

**Perpendicularity to level curves:** If $(x(t),y(t))$ lies on $f(x,y)=c$, then $f(x(t),y(t))=c$. Differentiating:
$$f_x x'(t)+f_y y'(t)=0\\quad\\Longrightarrow\\quad\\nabla f\\cdot\\mathbf{r}'(t)=0.$$
So the gradient is normal to the tangent — it points "uphill" off the contour.

**Contour-map reading:** Where $|\\nabla f|$ is large, level curves are close together (steep terrain). Where $|\\nabla f|$ is small, contours spread out (flat region). At a critical point $\\nabla f=\\mathbf{0}$, all directional derivatives vanish.

**3D extension:** $\\nabla f=(f_x,f_y,f_z)$; $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$; tangent plane to $F=c$: $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$. This unifies directional derivatives with surface normals in multivariable calculus.

**Gradient descent preview:** Optimization algorithms move opposite to $\\nabla f$ because that direction minimizes $f$ fastest locally. The learning rate scales the step size; the gradient direction is always the local steepest-descent bearing."""

THEORY_HE = """**מדוע $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$:** פרמטריזציה של תנועה בכיוון $\\mathbf{u}$: $\\mathbf{r}(t)=(a+tu_1,b+tu_2)$. אז $f$ לאורך המסלול היא $f(\\mathbf{r}(t))$, ולפי כלל השרשרת ב-$t=0$:
$$\\left.\\frac{d}{dt}f(\\mathbf{r}(t))\\right|_{t=0}=f_x u_1+f_y u_2=\\nabla f\\cdot\\mathbf{u}.$$

**קצב מרבי (קושי–שוורץ):** לוקטור יחידה $\\mathbf{u}$: $|\\nabla f\\cdot\\mathbf{u}|\\le|\\nabla f|$, שוויון כאשר $\\mathbf{u}\\|\\nabla f$. מכפלה חיובית → עלייה; שלילית → ירידה.

**ניצבות לעקומות גובה:** אם $(x(t),y(t))$ על $f(x,y)=c$, אז $f(x(t),y(t))=c$. גזירה:
$$f_x x'(t)+f_y y'(t)=0\\quad\\Longrightarrow\\quad\\nabla f\\cdot\\mathbf{r}'(t)=0.$$
הגרדיאנט ניצב למשיק — הוא מצביע "במעלה" מחוץ לקו הגובה.

**קריאת מפת קווי מתאר:** כש-$|\\nabla f|$ גדול, קווי הגובה קרובים (שטח תלול). כש-$|\\nabla f|$ קטן, הקווים מתרחקים (שטוח). בנקודה קריטית $\\nabla f=\\mathbf{0}$, כל הנגזרות הכיווניות מתאפסות.

**הרחבה ל-3D:** $\\nabla f=(f_x,f_y,f_z)$; $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$; מישור משיק ל-$F=c$: $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$. זה מאחד נגזרות כיווניות עם נורמלים למשטחים בחשבון משתנים רבים.

**תצוגה מקדימה של ירידת גרדיאנט:** אלגוריתמי אופטימיזציה זזים נגד $\\nabla f$ כי בכיוון זה $f$ יורדת הכי מהר מקומית. קצב הלמידה קובע גודל הצעד; כיוון הגרדיאנט הוא תמיד כיוון הירידה התלולה המקומית."""

WE1_EN = """**Function:** $f(x,y)=x^2+3xy$. Find the directional derivative at $(1,2)$ in the direction of $\\mathbf{v}=(3,4)$.

The direction vector given is **not** a unit vector — normalization comes first.

### Move 1 — Normalize $\\mathbf{v}$
$$|\\mathbf{v}|=\\sqrt{9+16}=5,\\qquad \\mathbf{u}=\\left(\\frac{3}{5},\\frac{4}{5}\\right).$$

### Move 2 — Compute the gradient
$$\\nabla f=(f_x,f_y)=(2x+3y,\\,3x).$$

### Move 3 — Evaluate at $(1,2)$
$$\\nabla f(1,2)=(2+6,\\,3)=(8,\\,3).$$

### Move 4 — Dot product
$$D_{\\mathbf{u}}f(1,2)=\\nabla f\\cdot\\mathbf{u}=8\\cdot\\frac{3}{5}+3\\cdot\\frac{4}{5}=\\frac{24+12}{5}=\\frac{36}{5}=7.2.$$

**Interpretation:** At $(1,2)$, moving in direction $(3,4)$ increases $f$ at rate $7.2$ per unit distance. The positive value confirms we step roughly "with" the gradient component in that direction.

**Sanity check:** $|\\nabla f|=\\sqrt{64+9}=\\sqrt{73}\\approx8.54$, so $7.2<8.54$ — consistent with Cauchy–Schwarz (rate cannot exceed $|\\nabla f|$). The angle between $(8,3)$ and $(3/5,4/5)$ is acute, hence positive dot product.

**Bagrut/university link:** This is the standard four-step pipeline — normalize, gradient, evaluate, dot — that every directional-derivative computation follows."""

WE1_HE = """**פונקציה:** $f(x,y)=x^2+3xy$. מצאו נגזרת כיוונית ב-$(1,2)$ בכיוון $\\mathbf{v}=(3,4)$.

וקטור הכיוון **אינו** וקטור יחידה — קודם מנרמלים.

### צעד 1 — נרמול $\\mathbf{v}$
$$|\\mathbf{v}|=\\sqrt{9+16}=5,\\qquad \\mathbf{u}=\\left(\\frac{3}{5},\\frac{4}{5}\\right).$$

### צעד 2 — חישוב הגרדיאנט
$$\\nabla f=(f_x,f_y)=(2x+3y,\\,3x).$$

### צעד 3 — הצבה ב-$(1,2)$
$$\\nabla f(1,2)=(2+6,\\,3)=(8,\\,3).$$

### צעד 4 — מכפלה סקalarית
$$D_{\\mathbf{u}}f(1,2)=8\\cdot\\frac{3}{5}+3\\cdot\\frac{4}{5}=\\frac{36}{5}=7.2.$$

**פרשנות:** ב-$(1,2)$, תנועה בכיוון $(3,4)$ מעלה את $f$ בקצב $7.2$ ליחידת מרחק. הערך החיובי מאשר שצעדים בערך "עם" רכיב הגרדיאנט בכיוון זה.

**בדיקת sanity:** $|\\nabla f|=\\sqrt{73}\\approx8.54$, לכן $7.2<8.54$ — עקבי עם קושי–שוורץ (קצב לא יכול לעלות על $|\\nabla f|$). הזווית בין $(8,3)$ ל-$(3/5,4/5)$ חדה, ולכן המכפלה חיובית.

**קשר לבגרות/אוניברסיטה:** זה pipeline ארבע-שלבי סטנדרטי — נרמול, גרדיאנט, הצבה, מכפלה — שכל חישוב נגזרת כיוונית עוקב אחריו."""

WE2_EN = """**Function:** $f(x,y)=x^2y-y^3$ at $(2,1)$. Find steepest ascent, steepest descent, and the level curve through the point.

### Move 1 — Partial derivatives and gradient
$$f_x=2xy,\\qquad f_y=x^2-3y^2.$$
$$\\nabla f(2,1)=(2\\cdot2\\cdot1,\\,4-3)=(4,\\,1).$$

### Move 2 — Steepest ascent
Maximum rate $=|\\nabla f|=\\sqrt{16+1}=\\sqrt{17}\\approx4.12$, in direction $\\mathbf{u}=(4,1)/\\sqrt{17}$.

### Move 3 — Steepest descent
Direction $-\\nabla f=(-4,-1)$; unit vector $(-4,-1)/\\sqrt{17}$; rate $=-\\sqrt{17}\\approx-4.12$.

### Move 4 — Level curve geometry
$f(2,1)=4(1)-1=3$, so the level curve is $x^2y-y^3=3$. The gradient $(4,1)$ is **perpendicular** to this curve at $(2,1)$ — verify with any tangent direction $(1,-4)$: $(4,1)\\cdot(1,-4)=0$ ✓.

### Move 5 — Compare with axis directions
Along $\\mathbf{e}_1=(1,0)$: $D_{\\mathbf{e}_1}f=4$. Along $\\mathbf{e}_2=(0,1)$: $D_{\\mathbf{e}_2}f=1$. Both are less than $\\sqrt{17}\\approx4.12$, confirming the gradient direction gives the maximum.

**Exam link:** "Direction of max increase" asks for the **unit vector** $\\nabla f/|\\nabla f|$, not the raw gradient.

**Rate check:** Steepest descent rate should be $-\\sqrt{17}$, the negative of the ascent rate — same magnitude, opposite sign. If both rates come out positive, re-check the minus on $-\\nabla f$."""

WE2_HE = """**פונקציה:** $f(x,y)=x^2y-y^3$ ב-$(2,1)$. מצאו עלייה תלולה, ירידה תלולה, ועקומת גובה דרך הנקודה.

### צעד 1 — נגזרות חלקיות וגרדיאנט
$$f_x=2xy,\\qquad f_y=x^2-3y^2.$$
$$\\nabla f(2,1)=(4,\\,1).$$

### צעד 2 — עלייה תלולה
קצב מרבי $=|\\nabla f|=\\sqrt{17}\\approx4.12$, בכיוון $\\mathbf{u}=(4,1)/\\sqrt{17}$.

### צעד 3 — ירידה תלולה
כיוון $-\\nabla f=(-4,-1)$; וקטור יחידה $(-4,-1)/\\sqrt{17}$; קצב $=-\\sqrt{17}\\approx-4.12$.

### צעד 4 — גיאומטריית עקומת גובה
$f(2,1)=3$, לכן $x^2y-y^3=3$. הגרדיאנט $(4,1)$ **ניצב** לעקומה ב-$(2,1)$ — אימות עם כיוון משיק $(1,-4)$: $(4,1)\\cdot(1,-4)=0$ ✓.

### צעד 5 — השוואה לכיווני ציר
לאורך $\\mathbf{e}_1=(1,0)$: $D_{\\mathbf{e}_1}f=4$. לאורך $\\mathbf{e}_2=(0,1)$: $D_{\\mathbf{e}_2}f=1$. שניהם קטנים מ-$\\sqrt{17}\\approx4.12$, מאשרים שהגרדיאנט נותן את המקסימום.

**קשר לבחינה:** "כיוון עלייה מרבית" = **וקטור יחידה** $\\nabla f/|\\nabla f|$, לא הגרדיאנט הגולמי.

**בדיקת קצב:** קצב ירידה תלולה צריך להיות $-\\sqrt{17}$, שלילי מקצב העלייה — אותו גודל, סימן הפוך. אם שני הקצבים יוצאים חיוביים, בדקו את המינוס ב-$-\\nabla f$."""

WE3_EN = """**Problem:** For $F(x,y,z)=x^2+y^2+z^2-4$, find $\\nabla F$ at $(1,1,\\sqrt{2})$ and the tangent plane to the sphere $F=0$.

### Move 1 — Confirm the point lies on the surface
$$F(1,1,\\sqrt{2})=1+1+2-4=0.\\quad\\checkmark$$

### Move 2 — Gradient (surface normal)
$$\\nabla F=(2x,\\,2y,\\,2z),\\qquad \\nabla F(1,1,\\sqrt{2})=(2,\\,2,\\,2\\sqrt{2}).$$

### Move 3 — Tangent plane
The gradient gives the normal. Plane equation:
$$\\nabla F(1,1,\\sqrt{2})\\cdot(x-1,\\,y-1,\\,z-\\sqrt{2})=0$$
$$2(x-1)+2(y-1)+2\\sqrt{2}(z-\\sqrt{2})=0.$$
Simplify: $x+y+\\sqrt{2}z=4$.

### Move 4 — Sample directional derivative
Along $\\mathbf{e}_1=(1,0,0)$: $D_{\\mathbf{e}_1}F=\\nabla F\\cdot(1,0,0)=2$.

### Move 5 — Geometric meaning
The sphere $x^2+y^2+z^2=4$ has radius $2$. The normal $(2,2,2\\sqrt{2})$ points outward from the origin through $(1,1,\\sqrt{2})$ — radial direction, as expected for a centered sphere.

**Takeaway:** For an implicit surface $F=c$, $\\nabla F$ replaces "slope" — it is always normal to the level set.

**Verify plane:** Substitute $(1,1,\\sqrt{2})$ into $x+y+\\sqrt{2}z=4$: $1+1+\\sqrt{2}\\cdot\\sqrt{2}=1+1+2=4$ ✓. The plane touches the sphere at exactly the given point."""

WE3_HE = """**בעיה:** עבור $F(x,y,z)=x^2+y^2+z^2-4$, מצאו $\\nabla F$ ב-$(1,1,\\sqrt{2})$ ואת מישור המשיק לכדור $F=0$.

### צעד 1 — אימות שהנקודה על המשטח
$$F(1,1,\\sqrt{2})=1+1+2-4=0.\\quad\\checkmark$$

### צעד 2 — גרדיאנט (נורמל למשטח)
$$\\nabla F=(2x,\\,2y,\\,2z),\\qquad \\nabla F(1,1,\\sqrt{2})=(2,\\,2,\\,2\\sqrt{2}).$$

### צעד 3 — מישור משיק
הגרדיאנט נותן את הנורמל. משוואת המישור:
$$2(x-1)+2(y-1)+2\\sqrt{2}(z-\\sqrt{2})=0.$$
פישוט: $x+y+\\sqrt{2}z=4$.

### צעד 4 — נגזרת כיוונית לדוגמה
לאורך $\\mathbf{e}_1=(1,0,0)$: $D_{\\mathbf{e}_1}F=2$.

### צעד 5 — משמעות גיאומטרית
הכדור $x^2+y^2+z^2=4$ ברדיוס $2$. הנורמל $(2,2,2\\sqrt{2})$ מצביע החוצה מהמקור דרך $(1,1,\\sqrt{2})$ — כיוון רדיאלי, כצפוי לכדור ממורכז.

**מסקנה:** למשטח מרומז $F=c$, $\\nabla F$ מחליף "שיפוע" — תמיד ניצב לקבוצת הגובה.

**אימות מישור:** הציבו $(1,1,\\sqrt{2})$ ב-$x+y+\\sqrt{2}z=4$: $1+1+2=4$ ✓. המישור נוגע בכדור בדיוק בנקודה הנתונה.

**קשר לבחינה:** כתבו $F(x,y,z)=0$ מפורש, גרדיאנט, משוואת מישור — שלושה שלבים שחוזרים בכל שאלת משיק ב-3D."""

CHK1_EN = """For $f(x,y)=e^x\\cos y$, find $D_{\\mathbf{u}}f$ at $(0,0)$ in direction $\\mathbf{u}=(1/\\sqrt{2},1/\\sqrt{2})$.

**Step 1 — Partials:** $f_x=e^x\\cos y$, $f_y=-e^x\\sin y$.

**Step 2 — Gradient at origin:** $\\nabla f(0,0)=(1,0)$.

**Step 3 — Dot product (already a unit vector):**
$$D_{\\mathbf{u}}f=(1,0)\\cdot\\left(\\frac{1}{\\sqrt{2}},\\frac{1}{\\sqrt{2}}\\right)=\\frac{1}{\\sqrt{2}}\\approx0.707.$$

**Check:** At $(0,0)$, $f=e^0\\cos0=1$. Moving NE, $x$ increases (raising $f$) while $y$ increases (lowering via $\\cos y$); net positive rate $1/\\sqrt{2}$ is plausible ✓."""

CHK1_HE = """עבור $f(x,y)=e^x\\cos y$, מצאו $D_{\\mathbf{u}}f$ ב-$(0,0)$ בכיוון $\\mathbf{u}=(1/\\sqrt{2},1/\\sqrt{2})$.

**שלב 1 — נגזרות חלקיות:** $f_x=e^x\\cos y$, $f_y=-e^x\\sin y$.

**שלב 2 — גרדיאנט במקור:** $\\nabla f(0,0)=(1,0)$.

**שלב 3 — מכפלה סקalarית (כבר וקטור יחידה):**
$$D_{\\mathbf{u}}f=\\frac{1}{\\sqrt{2}}\\approx0.707.$$

**בדיקה:** ב-$(0,0)$, $f=1$. תנועה NE מעלה $x$ (מעלה $f$) ומעלה $y$ (מורידה דרך $\\cos y$); קצב חיובי $1/\\sqrt{2}$ סביר ✓."""

CHK2_EN = """For $f(x,y)=x^2+4y^2$, find direction of maximum increase at $(1,1)$ and the maximum rate.

**Step 1:** $\\nabla f=(2x,\\,8y)$.

**Step 2 — At $(1,1)$:** $\\nabla f=(2,\\,8)$.

**Step 3 — Unit direction:** $(2,8)/\\sqrt{4+64}=(1,4)/\\sqrt{17}$.

**Step 4 — Maximum rate:** $|\\nabla f|=\\sqrt{68}=2\\sqrt{17}\\approx8.25$.

**Verify:** $D_{\\mathbf{u}}f$ with $\\mathbf{u}=\\nabla f/|\\nabla f|$ equals $|\\nabla f|$ by Cauchy–Schwarz ✓."""

CHK2_HE = """עבור $f(x,y)=x^2+4y^2$, מצאו כיוון עלייה מרבית ב-$(1,1)$ ואת הקצב המרבי.

**שלב 1:** $\\nabla f=(2x,\\,8y)$.

**שלב 2 — ב-$(1,1)$:** $\\nabla f=(2,\\,8)$.

**שלב 3 — כיוון יחידה:** $(1,4)/\\sqrt{17}$.

**שלב 4 — קצב מרבי:** $|\\nabla f|=2\\sqrt{17}\\approx8.25$.

**אימות:** $D_{\\mathbf{u}}f$ עם $\\mathbf{u}=\\nabla f/|\\nabla f|$ שווה ל-$|\\nabla f|$ לפי קושי–שוורץ ✓."""

METHOD_EN = """**Algorithm for $D_{\\mathbf{u}}f$ at $(a,b)$ in direction $\\mathbf{v}$:**
1. **Normalize:** $\\mathbf{u}=\\mathbf{v}/|\\mathbf{v}|$ (skip if already unit).
2. **Gradient:** $\\nabla f=(f_x,f_y)$ (or add $f_z$ in 3D).
3. **Evaluate** $\\nabla f(a,b)$.
4. **Dot:** $D_{\\mathbf{u}}f=\\nabla f(a,b)\\cdot\\mathbf{u}$.

| Question type | Answer |
|---|---|
| Max rate of increase | $|\\nabla f|$, direction $\\nabla f/|\\nabla f|$ |
| Steepest descent | $-|\\nabla f|$, direction $-\\nabla f/|\\nabla f|$ |
| Rate in direction $\\mathbf{u}$ | $\\nabla f\\cdot\\mathbf{u}$ (unit $\\mathbf{u}$!) |
| Zero rate direction | Any $\\mathbf{u}\\perp\\nabla f$ (tangent to level curve) |
| Normal to $F(x,y,z)=c$ | $\\nabla F$ at the point |
| Tangent plane | $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$ |

**Workflow:** Write $\\nabla f$ before plugging numbers. Circle whether the problem gives a raw vector or a unit vector."""

METHOD_HE = """**אלגוריתם ל-$D_{\\mathbf{u}}f$ ב-$(a,b)$ בכיוון $\\mathbf{v}$:**
1. **נרמול:** $\\mathbf{u}=\\mathbf{v}/|\\mathbf{v}|$ (דלגו אם כבר יחידה).
2. **גרדיאנט:** $\\nabla f=(f_x,f_y)$ (הוסיפו $f_z$ ב-3D).
3. **הצבה** $\\nabla f(a,b)$.
4. **מכפלה:** $D_{\\mathbf{u}}f=\\nabla f(a,b)\\cdot\\mathbf{u}$.

| סוג שאלה | תשובה |
|---|---|
| קצב עלייה מרבי | $|\\nabla f|$, כיוון $\\nabla f/|\\nabla f|$ |
| ירידה תלולה | $-|\\nabla f|$, כיוון $-\\nabla f/|\\nabla f|$ |
| קצב בכיוון $\\mathbf{u}$ | $\\nabla f\\cdot\\mathbf{u}$ ($\\mathbf{u}$ יחידה!) |
| קצב אפס | כל $\\mathbf{u}\\perp\\nabla f$ (משיק לעקומת גובה) |
| נורמל ל-$F=c$ | $\\nabla F$ בנקודה |
| מישור משיק | $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$ |

**תהליך:** כתבו $\\nabla f$ לפני מספרים. סמנו האם נתון וקטור גולמי או יחידה."""

PITFALL_EN = """1. **Forgetting to normalize.** $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ requires $\\mathbf{u}$ to be a **unit** vector. If given $\\mathbf{v}=(3,4)$, first compute $\\mathbf{u}=(3/5,4/5)$.

2. **Confusing max rate with max value.** The gradient direction maximizes the **rate of change**, not the value of $f$. A function can decrease fastest while still having $f>0$.

3. **Gradient parallel to level curve.** $\\nabla f$ is **perpendicular** to level curves, never tangent (unless $\\nabla f=\\mathbf{0}$).

4. **Wrong sign for descent.** Steepest descent uses $-\\nabla f/|\\nabla f|$ with rate $-|\\nabla f|$. Using $+\\nabla f$ gives ascent.

5. **Reporting gradient instead of unit direction.** Exam stems asking "in which direction" expect $\\nabla f/|\\nabla f|$, not $(f_x,f_y)$ alone.

**Fix pattern:** After computing $\\nabla f$, ask: "Does the question want a **number** (rate), a **vector** (direction), or a **plane** (3D tangent)?\""""

PITFALL_HE = """1. **שכחת נרמול.** $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ דורש $\\mathbf{u}$ **יחידה**. אם נתון $\\mathbf{v}=(3,4)$, קודם $\\mathbf{u}=(3/5,4/5)$.

2. **בלבול קצב מרבי מול ערך מרבי.** הגרדיאנט ממקסם **קצב שינוי**, לא ערך $f$. פונקציה יכולה לרדת הכי מהר ועדיין $f>0$.

3. **גרדיאנט מקביל לעקומת גובה.** $\\nabla f$ **ניצב** לעקומות גובה, לא משיק (אלא אם $\\nabla f=\\mathbf{0}$).

4. **סימן שגוי לירידה.** ירידה תלולה: $-\\nabla f/|\\nabla f|$ עם קצב $-|\\nabla f|$. $+\\nabla f$ נותן עלייה.

5. **דיווח גרדיאנט במקום כיוון יחידה.** "באיזה כיוון" = $\\nabla f/|\\nabla f|$, לא $(f_x,f_y)$ בלבד.

**תבנית תיקון:** אחרי $\\nabla f$, שאלו: האם רוצים **מספר** (קצב), **וקטור** (כיוון), או **מישור** (משיק ב-3D)?"""

WHY_EN = """The gradient is the central object linking **partial derivatives**, **optimization**, and **geometry** in multivariable calculus. Every step of gradient descent in machine learning is $-\\nabla f$; every contour line on a topographic map is perpendicular to $\\nabla f$.

**Builds on:** `concept:partial_derivatives` — you must compute $f_x,f_y$ fluently before dotting with $\\mathbf{u}$.

**Unlocks:**
- `concept:optimization_problems` — Lagrange multipliers use $\\nabla f=\\lambda\\nabla g$.
- `concept:double_integrals` — change of variables uses Jacobian determinants related to gradient geometry.

**Real applications:** Heat flows opposite to $\\nabla T$ (Fourier law intuition); fluid pressure gradients drive flow; neural-network training adjusts weights along $-\\nabla L$.

**Exam transfer:** University calculus finals routinely mix "compute $D_{\\mathbf{u}}f$", "find tangent plane", and "prove $\\nabla f\\perp$ level curve" on the same function — one gradient computation serves all three."""

WHY_HE = """הגרדיאנט הוא האובייקט המרכזי שמקשר **נגזרות חלקיות**, **אופטימיזציה** ו**גיאומטריה** בחשבון משתנים רבים. כל צעד בירידת גרדיאנט בלמידת מכונה הוא $-\\nabla f$; כל קו גובה במפה טופוגרפית ניצב ל-$\\nabla f$.

**מבוסס על:** `concept:partial_derivatives` — חובה לחשב $f_x,f_y$ בקלות לפני מכפלה עם $\\mathbf{u}$.

**פותח:**
- `concept:optimization_problems` — כופלי לגראנז' משתמשים ב-$\\nabla f=\\lambda\\nabla g$.
- `concept:double_integrals` — החלפת משתנים קשורה לגיאומטריית גרדיאנט.

**יישומים:** חום זורם נגד $\\nabla T$; לחץ נוזלים מניע זרימה; אימון רשתות עצביות מעדכן משקלים לאורך $-\\nabla L$.

**העברה לבחינה:** בחינות סופיות משלבות "חשב $D_{\\mathbf{u}}f$", "מצא מישור משיק", "הוכח $\\nabla f\\perp$" — חישוב גרדיאנט אחד משרת את שלושתם."""

BEFORE_EN = """**Formula card (recite once):**
- $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ — $\\mathbf{u}$ **must be unit**
- $\\nabla f=(f_x,f_y)$ or $(f_x,f_y,f_z)$
- Max increase: rate $|\\nabla f|$, direction $\\nabla f/|\\nabla f|$
- Steepest descent: rate $-|\\nabla f|$, direction $-\\nabla f/|\\nabla f|$
- $D_{\\mathbf{u}}f=0$ when $\\mathbf{u}\\perp\\nabla f$
- Tangent plane: $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$

**Exam patterns:** (1) Normalize, dot, done. (2) Report direction **and** rate — two separate answers. (3) Implicit surface → rewrite as $F=c$, gradient gives normal.

**Last review:** Solve checkpoint 1 (unit direction given) and checkpoint 2 (max rate) in under 5 minutes without notes.

**Time budget:** Normalization + gradient + dot product should take under 90 seconds per numeric item; reserve extra time for 3D tangent-plane simplification."""

BEFORE_HE = """**גיליון נוסחאות (אמרו פעם אחת):**
- $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ — $\\mathbf{u}$ **חייב להיות יחידה**
- $\\nabla f=(f_x,f_y)$ או $(f_x,f_y,f_z)$
- עלייה מרבית: קצב $|\\nabla f|$, כיוון $\\nabla f/|\\nabla f|$
- ירידה תלולה: קצב $-|\\nabla f|$, כיוון $-\\nabla f/|\\nabla f|$
- $D_{\\mathbf{u}}f=0$ כאשר $\\mathbf{u}\\perp\\nabla f$
- מישור משיק: $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$

**דפוסי בחינה:** (1) נרמול, מכפלה, סיום. (2) דווחו כיוון **וגם** קצב — שתי תשובות. (3) משטח מרומז → $F=c$, גרדיאנט = נורמל.

**חזרה אחרונה:** פתרו checkpoint 1 ו-2 תוך 5 דקות בלי notes."""

SUMMARY_EN = """- **Directional derivative:** $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ — rate of change in unit direction $\\mathbf{u}$.
- **Gradient:** points steepest uphill; $|\\nabla f|=$ max rate of increase.
- **Descent:** direction $-\\nabla f/|\\nabla f|$, rate $-|\\nabla f|$.
- **Zero rate:** $\\mathbf{u}\\perp\\nabla f$ — tangent to level curve.
- **Geometry:** $\\nabla f\\perp$ level curves; $\\nabla F\\perp$ level surfaces.
- **3D:** tangent plane $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$.

**Takeaway:** Normalize first, gradient second, dot product last — the same three-step pipeline handles nearly every exam item in this topic."""

SUMMARY_HE = """- **נגזרת כיוונית:** $D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}$ — קצב שינוי בכיוון יחידה $\\mathbf{u}$.
- **גרדיאנט:** מצביע למעלה תלול; $|\\nabla f|=$ קצב עלייה מרבי.
- **ירידה:** כיוון $-\\nabla f/|\\nabla f|$, קצב $-|\\nabla f|$.
- **קצב אפס:** $\\mathbf{u}\\perp\\nabla f$ — משיק לעקומת גובה.
- **גיאומטריה:** $\\nabla f\\perp$ עקומות גובה; $\\nabla F\\perp$ משטחי גובה.
- **3D:** מישור משיק $\\nabla F(\\mathbf{x}_0)\\cdot(\\mathbf{x}-\\mathbf{x}_0)=0$.

**מסקנה:** נרמול, גרדיאנט, מכפלה — אותה שלישייה מטפלת כמעט בכל פריט בחינה בנושא."""

EXPLS = {
    1: fmt_expl(
        "For $f(x,y)=3x^2-2y^2$, partial derivatives treat the other variable as constant: $f_x=6x$ and $f_y=-4y$. The gradient packages both: $\\nabla f=(6x,-4y)$. Each component is a function, not a number — evaluation happens at a specific point later.",
        "Write $\\nabla f=(f_x,f_y)$ immediately after computing partials. Differentiate $3x^2$ → $6x$ ( $y$ fixed); differentiate $-2y^2$ → $-4y$ ( $x$ fixed). No dot product yet — this stem asks only for the gradient field.",
        "Swapping signs: $f_y=+4y$ instead of $-4y$. Or returning a scalar like $6x-4y$ instead of the vector $(6x,-4y)$. Another slip: differentiating $3x^2$ as $3x$.",
        "Gradient questions are quick points if you treat them as 'two partials in parentheses.' On finals, $\\nabla f$ is often step 1 of a longer directional-derivative or tangent-plane problem — keep the vector form.",
        "עבור $f(x,y)=3x^2-2y^2$, נגזרות חלקיות עם משתנה שני קבוע: $f_x=6x$, $f_y=-4y$. הגרדיאנט אורז את שניהם: $\\nabla f=(6x,-4y)$. כל רכיב הוא פונקציה, לא מספר.",
        "כתבו $\\nabla f=(f_x,f_y)$ מיד אחרי הנגזרות. גזרו $3x^2$ → $6x$ ($y$ קבוע); $-2y^2$ → $-4y$ ($x$ קבוע). אין מכפלה סקalarית — השאלה מבקשת רק את שדה הגרדיאנט.",
        "החלפת סימנים: $f_y=+4y$. או החזרת סקalar $6x-4y$ במקום וקטור $(6x,-4y)$. גזירה $3x^2$ כ-$3x$.",
        "שאלות גרדיאנט = נקודות מהירות אם רואים 'שתי נגזרות חלקיות בסוגריים'. בבחינה, $\\nabla f$ לעיתים שלב 1 לנגזרת כיוונית או מישור משיק.",
    ),
    2: fmt_expl(
        "Partials: $f_x=\\pi\\cos(\\pi x)$, $f_y=2y$. At $(1,0)$: $\\cos(\\pi)=-1$ gives $\\nabla f=(-\\pi,0)$. Direction $\\mathbf{u}=(0,1)$ is already unit. Dot product $(-\\pi,0)\\cdot(0,1)=0$ — motion purely in $y$ while the gradient has no $y$-component.",
        "When $\\mathbf{u}$ aligns with an axis, the dot product picks one partial. Here $\\mathbf{u}=(0,1)$ selects $f_y$, but $f_y(1,0)=0$. Geometrically, $(1,0)$ lies where $\\cos(\\pi x)$ is flat in $y$ because $f$ does not depend on $y$ at that $x$-slice... actually $f_y=2y=0$ at $y=0$.",
        "Using $\\nabla f=(\\pi,0)$ by forgetting $\\cos(\\pi)=-1$. Or computing $D_{\\mathbf{u}}f=-\\pi$ by dotting with $(1,0)$ instead of the given $(0,1)$. Skipping evaluation at $(1,0)$.",
        "If $D_{\\mathbf{u}}f=0$, verify whether $\\mathbf{u}\\perp\\nabla f$ — a fast zero check before redoing all arithmetic. Axis-aligned directions often simplify the dot product to a single partial.",
        "נגזרות: $f_x=\\pi\\cos(\\pi x)$, $f_y=2y$. ב-$(1,0)$: $\\cos(\\pi)=-1$ → $\\nabla f=(-\\pi,0)$. $\\mathbf{u}=(0,1)$ כבר יחידה. $(-\\pi,0)\\cdot(0,1)=0$ — תנועה ב-$y$ בלבד בעוד לגרדיאנט אין רכיב $y$.",
        "כש-$\\mathbf{u}$ על ציר, המכפלה בוחרת נגזרת אחת. כאן $\\mathbf{u}=(0,1)$ → $f_y$, ו-$f_y(1,0)=0$. ב-$(1,0)$, $f_y=2y=0$.",
        "$\\nabla f=(\\pi,0)$ בלי $\\cos(\\pi)=-1$. או $D_{\\mathbf{u}}f=-\\pi$ עם $(1,0)$ במקום $(0,1)$. דילוג על הצבה ב-$(1,0)$.",
        "אם $D_{\\mathbf{u}}f=0$, בדקו $\\mathbf{u}\\perp\\nabla f$. כיוונים על צירים מפשטים לרוב נגזרת חלקית אחת.",
    ),
    3: fmt_expl(
        "For $f=\\sqrt{x^2+y^2}$, partials give $f_x=x/r$, $f_y=y/r$ where $r=\\sqrt{x^2+y^2}$. At $(3,4)$: $r=5$, so $\\nabla f=(3/5,4/5)$. Maximum directional rate equals $|\\nabla f|=\\sqrt{(3/5)^2+(4/5)^2}=1$. The gradient already has unit length at every nonzero point on this cone.",
        "Recognize $f$ as distance from the origin. The gradient points radially outward with magnitude 1 everywhere (except the origin). So max rate is always 1 — no need for a separate Cauchy–Schwarz step once $|\\nabla f|$ is computed.",
        "Answering $5$ (confusing $r=5$ with the rate). Or reporting direction $(3,4)$ without normalizing. Some students set $\\nabla f=(x,y)$ and forget the denominator $r$.",
        "For radial functions $\\sqrt{x^2+y^2}$, memorize: $\\nabla f=(x/r,y/r)$ and $|\\nabla f|=1$. This pattern appears in polar-coordinate warm-up problems on university exams.",
        "עבור $f=\\sqrt{x^2+y^2}$, $f_x=x/r$, $f_y=y/r$ עם $r=\\sqrt{x^2+y^2}$. ב-$(3,4)$: $r=5$, $\\nabla f=(3/5,4/5)$. קצב מרבי $=|\\nabla f|=1$. הגרדיאנט כבר באורך יחידה בכל נקודה לא-אפס על הקונוס.",
        "זיהו $f$ כמרחק מהמקור. הגרדיאנט רדיאלי החוצה עם גודל 1 בכל מקום (חוץ מהמקור). קצב מרבי תמיד 1.",
        "תשובה $5$ (בלבול $r=5$ עם הקצב). או כיוון $(3,4)$ בלי נרמול. $\\nabla f=(x,y)$ בלי מכנה $r$.",
        "לפונקציות רדיאליות: $\\nabla f=(x/r,y/r)$ ו-$|\\nabla f|=1$. דפוס שכיח בחימום בקואורדינטות קוטביות.",
    ),
    4: fmt_expl(
        "$D_{\\mathbf{u}}f=\\nabla f\\cdot\\mathbf{u}=|\\nabla f||\\mathbf{u}|\\cos\\theta$. Zero occurs when $\\cos\\theta=0$, i.e. $\\mathbf{u}\\perp\\nabla f$. On a level curve, the tangent direction is perpendicular to the gradient — walking along the contour keeps $f$ constant to first order.",
        "Conceptual question — no numbers. Ask: 'Which direction keeps me on the same height?' Answer: tangent to the level curve, which is any direction orthogonal to $\\nabla f$. There are infinitely many such $\\mathbf{u}$ (both along the curve).",
        "Saying 'parallel to the gradient' (that gives max change, not zero). Or 'along the $x$-axis' without justification. Confusing zero **rate** with zero **value** of $f$.",
        "When a stem asks 'in which direction is $D_{\\mathbf{u}}f=0$?', write '$\\mathbf{u}\\perp\\nabla f$, i.e. tangent to the level curve' — one line earns full conceptual credit on theory questions.",
        "$D_{\\mathbf{u}}f=|\\nabla f|\\cos\\theta$. אפס כש-$\\cos\\theta=0$, כלומר $\\mathbf{u}\\perp\\nabla f$. על עקומת גובה, כיוון המשיק ניצב לגרדיאנט — הליכה לאורך הקontour שומרת $f$ קבועה בסדר ראשון.",
        "שאלה מושגית — בלי מספרים. 'איזה כיוון שומר על אותו גובה?' → משיק לעקומת גובה, ניצב ל-$\\nabla f$. יש אינסוף כיוונים כאלה.",
        "'מקביל לגרדיאנט' (נותן שינוי מרבי, לא אפס). או 'לאורך ציר $x$' בלי הנמקה. בלבול קצב אפס עם ערך $f$ אפס.",
        "כששואלים 'באיזה כיוון $D_{\\mathbf{u}}f=0$?', כתבו '$\\mathbf{u}\\perp\\nabla f$, משיק לעקומת גובה' — שורה אחת לניקוד מלא.",
    ),
    5: fmt_expl(
        "Partials: $f_x=e^y-y\\sin(xy)$, $f_y=xe^y-x\\sin(xy)$. At $(1,0)$: $f_x=e^0-0=1$, $f_y=1-0=1$, so $\\nabla f=(1,1)$. Normalize $\\mathbf{v}=(1,-1)$: $\\mathbf{u}=(1,-1)/\\sqrt{2}$. Dot: $(1,1)\\cdot(1,-1)/\\sqrt{2}=0$ — the direction is $45°$ to the gradient, exactly perpendicular.",
        "After $\\nabla f=(1,1)$, notice the direction $(1,-1)$ is orthogonal (dot $1\\cdot1+1\\cdot(-1)=0$ before normalizing). Zero is immediate without dividing by $\\sqrt{2}$ — normalization cancels for the dot-product sign check.",
        "Forgetting the $-y\\sin(xy)$ term in $f_x$. Using $\\mathbf{v}$ without normalizing and getting $0$ anyway (lucky here, wrong in general). Evaluating trig at wrong angle.",
        "When $\\mathbf{v}$ and $\\nabla f$ look symmetric, test perpendicularity with a quick dot before full normalization — saves time on timed exams if the answer is zero.",
        "נגזרות: $f_x=e^y-y\\sin(xy)$, $f_y=xe^y-x\\sin(xy)$. ב-$(1,0)$: $\\nabla f=(1,1)$. $\\mathbf{v}=(1,-1)$ → $\\mathbf{u}=(1,-1)/\\sqrt{2}$. $(1,1)\\cdot(1,-1)/\\sqrt{2}=0$ — הכיוון $45°$ לגרדיאנט, ניצב בדיוק.",
        "אחרי $\\nabla f=(1,1)$, $(1,-1)$ ניצב (מכפלה $0$ לפני נרמול). אפס מיידי — נרמול מבטל לבדיקת סימן.",
        "שכחת $-y\\sin(xy)$ ב-$f_x$. שימוש ב-$\\mathbf{v}$ בלי נרמול (כאן יוצא 0 בכל זאת, לא תמיד). הצבה שגויה.",
        "כש-$\\mathbf{v}$ ו-$\\nabla f$ סימטריים, בדקו ניצבות במכפלה לפני נרמול מלא — חוסך זמן אם התשובה 0.",
    ),
    6: fmt_expl(
        "$f_x=2xy+2y^2$, $f_y=x^2+4xy$. At $(1,2)$: $f_x=4+8=12$, $f_y=1+8=9$, so $\\nabla f=(12,9)$. Steepest descent direction is $-\\nabla f=(-12,-9)$; unit vector $(-4,-3)/5$ after dividing by $\\gcd$ or $|\\nabla f|=15$. Rate $=-15$.",
        "Steepest descent = negative gradient direction. Compute $|\\nabla f|=\\sqrt{144+81}=15$ first — that is the magnitude of the rate (with minus sign for descent). Normalize $(-12,-9)$ to $(-4,-3)/5$ for the direction answer.",
        "Using $(12,9)/15$ for descent (sign error — that is ascent). Reporting rate $+15$. Or giving $(-12,-9)$ without normalizing when the stem asks for a unit direction.",
        "Always label two outputs on descent problems: **direction** (unit vector) and **rate** (scalar, negative). Examiners deduct if you swap them or omit the minus on the rate.",
        "$f_x=2xy+2y^2$, $f_y=x^2+4xy$. ב-$(1,2)$: $\\nabla f=(12,9)$. ירידה תלולה: $-\\nabla f=(-12,-9)$; יחידה $(-4,-3)/5$; קצב $=-15$.",
        "ירידה תלולה = כיוון גרדיאנט שלילי. $|\\nabla f|=15$ — גודל הקצב (עם מינוס). נרמול $(-12,-9)$ ל-$(-4,-3)/5$ לכיוון.",
        "$(12,9)/15$ לירידה (סימן שגוי — עלייה). קצב $+15$. $(-12,-9)$ בלי נרמול כשמבקשים יחידה.",
        "בירידה תלולה: **כיוון** (יחידה) ו**קצב** (סקalar שלילי) — שתי תשובות. מורידים נקודות על החלפה או מינוס חסר.",
    ),
    7: fmt_expl(
        "Parametrize the level curve: $\\mathbf{r}(t)=(x(t),y(t))$ with $f(x(t),y(t))=c$. Differentiate: $f_x x'+f_y y'=0$, so $\\nabla f\\cdot\\mathbf{r}'=0$. The tangent $\\mathbf{r}'$ is perpendicular to $\\nabla f$ — QED.",
        "This is the proof template for 'gradient perpendicular to level curve.' Start from 'stays on level set' → differentiate → chain rule → dot product zero. No coordinates needed — works at any point.",
        "Differentiating $f=c$ to get $f_x+f_y=0$ (forgetting $x',y'$). Claiming parallel instead of perpendicular. Using a single point instead of a general parametrization.",
        "Proof questions on this topic are short — write the chain-rule line $\\nabla f\\cdot\\mathbf{r}'=0$ clearly; that is the graded step. Draw a small contour + gradient arrow on scratch paper to sanity-check.",
        "פרמטריזציה: $\\mathbf{r}(t)=(x(t),y(t))$, $f(x(t),y(t))=c$. גזירה: $f_x x'+f_y y'=0$ → $\\nabla f\\cdot\\mathbf{r}'=0$. המשיק ניצב ל-$\\nabla f$ — סוף ההוכחה.",
        "תבנית הוכחה: 'נשאר על קבוצת גובה' → גזירה → שרשרת → מכפלה אפס. בלי קואורדינטות — בכל נקודה שבה $\\nabla f\\neq\\mathbf{0}$.",
        "גזירה $f_x+f_y=0$ (שכחת $x',y'$). טענה על מקביל במקום ניצב. נקודה בודדת במקום פרמטריזציה כללית.",
        "הוכחות קצרות — שורת השרשרת $\\nabla f\\cdot\\mathbf{r}'=0$ היא הצעד המדורג. ציירו contour + גרדיאנט על טיוטה לבדיקה מהירה.",
    ),
    8: fmt_expl(
        "$\\nabla T=(-4x,-6y)$. At $(1,1)$: $\\nabla T=(-4,-6)$. Fastest **increase** is along $\\nabla T$, unit direction $(-4,-6)/\\sqrt{52}=(-2,-3)/\\sqrt{13}$. Rate $=|\\nabla T|=\\sqrt{16+36}=2\\sqrt{13}\\approx7.21$.",
        "Temperature $T=100-2x^2-3y^2$ decreases from the center — but 'increases fastest' still means $+\\nabla T$ direction (toward warmer nearby points). The negative components indicate warmth increases toward lower $x,y$ near $(1,1)$.",
        "Using $(4,6)$ instead of $(-4,-6)$ (sign flip on gradient). Confusing 'coolest direction' with 'fastest increase.' Reporting rate $7.21$ without $\\sqrt{}$ form when exact answer expected.",
        "Applied word problems: define $T(x,y)$, take partials, evaluate at the point — same pipeline as pure math. Underline 'fastest increase' vs 'fastest decrease' before choosing $\\pm\\nabla T$.",
        "$\\nabla T=(-4x,-6y)$. ב-$(1,1)$: $\\nabla T=(-4,-6)$. **עלייה** מהירה לאורך $\\nabla T$, יחידה $(-2,-3)/\\sqrt{13}$. קצב $=2\\sqrt{13}\\approx7.21$.",
        "$T=100-2x^2-3y^2$ יורד מהמרכז — אך 'עולה הכי מהר' = כיוון $+\\nabla T$. הרכיבים השליליים: חום עולה לכיוון $x,y$ נמוכים יותר ליד $(1,1)$.",
        "$(4,6)$ במקום $(-4,-6)$. בלבול 'כיוון קריר' עם 'עלייה מהירה'. קצב $7.21$ בלי $\\sqrt{}$ כשמצפים למדויק.",
        "בעיות מילוליות: הגדירו $T(x,y)$, נגזרות, הצבה — אותו pipeline. סמנו 'עלייה' מול 'ירידה' לפני $\\pm\\nabla T$.",
    ),
}


def validate(data: dict) -> list[str]:
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in MIN:
            en_min, he_min = MIN[kind]
            en_w, he_w = wc(sec.get("body_en_md", "")), wc(sec.get("body_he_md", ""))
            if en_w < en_min:
                errors.append(f"{kind} en {en_w} < {en_min}")
            if he_w < he_min:
                errors.append(f"{kind} he {he_w} < {he_min}")
            if he_weak(sec.get("body_he_md", ""), sec.get("body_en_md", "")):
                errors.append(f"{kind}: weak Hebrew body")
    for q in data["questions"]:
        for lang in ("en", "he"):
            expl = q.get(f"explanation_{lang}", "")
            w = wc(expl)
            if w < 80:
                errors.append(f"q{q['ord']} expl-{lang} {w} < 80")
            if w > 150:
                errors.append(f"q{q['ord']} expl-{lang} {w} > 150")
        if he_weak(q.get("explanation_he", ""), q.get("explanation_en", "")):
            errors.append(f"q{q['ord']}: weak Hebrew expl")
    return errors


def main():
    data = json.loads(TARGET.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind == "intro":
            sec["body_en_md"] = INTRO_EN
            sec["body_he_md"] = INTRO_HE
        elif kind == "definition":
            sec["body_en_md"] = DEF_EN
            sec["body_he_md"] = DEF_HE
        elif kind == "theory":
            sec["body_en_md"] = THEORY_EN
            sec["body_he_md"] = THEORY_HE
        elif kind == "worked_example":
            n = sec.get("example_number", 1)
            if n == 1:
                sec["body_en_md"], sec["body_he_md"] = WE1_EN, WE1_HE
            elif n == 2:
                sec["body_en_md"], sec["body_he_md"] = WE2_EN, WE2_HE
            elif n == 3:
                sec["body_en_md"], sec["body_he_md"] = WE3_EN, WE3_HE
        elif kind == "checkpoint":
            if "e^x" in sec.get("body_en_md", ""):
                sec["checkpoint_solution_en"] = CHK1_EN
                sec["checkpoint_solution_he"] = CHK1_HE
            else:
                sec["checkpoint_solution_en"] = CHK2_EN
                sec["checkpoint_solution_he"] = CHK2_HE
        elif kind == "method_guide":
            sec["body_en_md"] = METHOD_EN
            sec["body_he_md"] = METHOD_HE
        elif kind == "pitfall":
            sec["body_en_md"] = PITFALL_EN
            sec["body_he_md"] = PITFALL_HE
        elif kind == "why_matters":
            sec["body_en_md"] = WHY_EN
            sec["body_he_md"] = WHY_HE
        elif kind == "before_exam":
            sec["body_en_md"] = BEFORE_EN
            sec["body_he_md"] = BEFORE_HE
        elif kind == "summary":
            sec["body_en_md"] = SUMMARY_EN
            sec["body_he_md"] = SUMMARY_HE

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in EXPLS:
            q["explanation_en"], q["explanation_he"] = EXPLS[ord_]

    errs = validate(data)
    if errs:
        print("Validation errors:")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
