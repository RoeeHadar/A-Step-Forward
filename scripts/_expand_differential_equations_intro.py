#!/usr/bin/env python3
"""Expand differential_equations_intro.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/differential_equations_intro.json"

INTRO = {
    "body_en_md": """A **differential equation (ODE)** is an equation that relates an unknown function $y(t)$ (or $y(x)$) to one or more of its derivatives. The **order** of an ODE is the highest derivative that appears. In this lesson we focus on **first-order** equations — those involving only $y$ and $y'=dy/dt$:

$$\\frac{dy}{dt} = f(t,y).$$

Unlike algebraic equations, where the unknown is a number, here the unknown is a **function**. Solving means finding all functions $y(t)$ that satisfy the equation.

Differential equations model real change over time:
- **Exponential growth/decay:** $dy/dt=ky$ (populations, radioactivity, compound interest).
- **Newton's law of cooling:** $dT/dt=-k(T-T_{\\text{env}})$ (coffee cooling, thermometers).
- **Newton's second law:** $m\\,d^2x/dt^2=F$ (motion — second order, preview).
- **Electric circuits:** $L\\,dI/dt+RI=V(t)$ (RL circuits).

The **general solution** contains an arbitrary constant $C$ from integration — it represents a family of curves. An **initial condition** such as $y(t_0)=y_0$ selects one member of that family and gives the **particular solution** relevant to a specific physical setup. On university calculus exams, you must always write $+C$ first, then apply the initial condition at the end.""",
    "body_he_md": """**משוואה דיפרנציאלית (ODE)** היא משוואה שמקשרת פונקציה לא ידועה $y(t)$ (או $y(x)$) לנגזרות שלה. **סדר** המשוואה הוא הנגזרת הגבוהה ביותר שמופיעה. בשיעור זה מתמקדים ב**משוואות מסדר ראשון** — אלו שמכילות רק $y$ ו-$y'=dy/dt$:

$$\\frac{dy}{dt}=f(t,y).$$

בניגוד למשוואות אלגבריות שבהן הנעלם הוא מספר, כאן הנעלם הוא **פונקציה**. "פתרון" פירושו מציאת כל הפונקציות $y(t)$ שמקיימות את המשוואה.

משוואות דיפרנציאליות מתארות שינוי אמיתי בזמן:
- **גידול/ריקבון מעריכי:** $dy/dt=ky$ (אוכלוסיות, רדיואקטיביות, ריבית דריבית).
- **חוק ניוטון לקירור:** $dT/dt=-k(T-T_{\\text{env}})$ (קפה מתקרר, מד-חום).
- **חוק שני של ניוטון:** $m\\,d^2x/dt^2=F$ (תנועה — מסדר שני, תצוגה מקדימה).
- **מעגלי חשמל:** $L\\,dI/dt+RI=V(t)$ (מעגלי RL).

**פתרון כללי** מכיל קבוע שרירותי $C$ מאינטגרציה — משפחת עקומות. **תנאי התחלה** כמו $y(t_0)=y_0$ בוחר עקומה אחת ונותן **פתרון פרטי** רלוונטי להקשר פיזיקלי. בבחינות חשבון אוניברסיטאיות: תמיד כתבו $+C$ קודם, ורק בסוף הציבו תנאי התחלה.""",
}

DEFINITION = {
    "body_en_md": """**Method 1 — Separable equations:**
An ODE is **separable** if it can be written as $\\dfrac{dy}{dx}=g(x)h(y)$ — the right side factors into a function of $x$ times a function of $y$.

**Technique:** Separate variables and integrate both sides:
$$\\frac{dy}{h(y)} = g(x)\\,dx \\implies \\int\\frac{dy}{h(y)} = \\int g(x)\\,dx + C.$$

Then solve for $y$ if possible and apply any initial condition.

**Method 2 — Linear first-order equations:**
Standard form: $\\dfrac{dy}{dx}+P(x)y=Q(x)$, where $P$ and $Q$ depend only on $x$.

**Integrating factor:** $\\mu(x)=e^{\\int P(x)\\,dx}$.

**Solution formula:**
$$y = \\frac{1}{\\mu(x)}\\left[\\int\\mu(x)Q(x)\\,dx + C\\right].$$

**Why it works:** Multiplying the ODE by $\\mu$ makes the left side an exact derivative:
$$\\frac{d}{dx}[\\mu y] = \\mu Q \\implies \\mu y = \\int\\mu Q\\,dx + C.$$

**Before applying Method 2:** divide the entire equation by any leading coefficient so $y'$ has coefficient 1. For example, $2y'+4xy=6$ becomes $y'+2xy=3$ **before** computing $\\mu=e^{\\int 2x\\,dx}$.

**Quick test:** If you can algebraically rearrange so all $y$-terms are on one side and all $x$-terms on the other, the equation is separable. If $y$ appears only to the first power with coefficients depending on $x$, try the integrating factor.""",
    "body_he_md": """**שיטה 1 — משוואות ספריות:**
ODE **ספרית** אם ניתן לכתוב $\\dfrac{dy}{dx}=g(x)h(y)$ — הצד הימני מתפרק לפונקציה של $x$ כפול פונקציה של $y$.

**טכניקה:** הפרידו משתנים ואינטגרו משני הצדדים:
$$\\frac{dy}{h(y)}=g(x)\\,dx\\implies\\int\\frac{dy}{h(y)}=\\int g(x)\\,dx+C.$$

לאחר מכן פתרו עבור $y$ אם אפשר והציבו תנאי התחלה. בדקו האם $y=\\text{קבוע}$ מקיים את המשוואה בנפרד.

**שיטה 2 — משוואות לינאריות מסדר ראשון:**
צורה סטנדרטית: $\\dfrac{dy}{dx}+P(x)y=Q(x)$, כאשר $P$ ו-$Q$ תלויים רק ב-$x$ (לא ב-$y$).

**גורם אינטגרציה:** $\\mu(x)=e^{\\int P(x)\\,dx}$.

**נוסחת פתרון:**
$$y=\\frac{1}{\\mu(x)}\\left[\\int\\mu(x)Q(x)\\,dx+C\\right].$$

**מדוע זה עובד:** כפל ב-$\\mu$ הופך את הצד השמאלי לנגזרת מדויקת:
$$\\frac{d}{dx}[\\mu y]=\\mu Q\\implies\\mu y=\\int\\mu Q\\,dx+C.$$

**לפני שיטה 2:** חלקו את כל המשוואה במקדם המוביל כך ש-$y'$ יקבל מקדם 1. למשל, $2y'+4xy=6$ הופך ל-$y'+2xy=3$ **לפני** חישוב $\\mu=e^{\\int 2x\\,dx}$.

**בדיקה מהירה:** אם כל איברי $y$ בצד אחד וכל איברי $x$ בצד שני — ספרית. אם $y$ בחזקה ראשונה עם מקדמים של $x$ — נסו גורם אינטגרציה.""",
}

THEORY = {
    "body_en_md": """**Exponential growth/decay:** $\\dfrac{dy}{dt}=ky$.

This is separable: $\\int dy/y=\\int k\\,dt\\Rightarrow\\ln|y|=kt+C_1\\Rightarrow y=Ae^{kt}$ where $A=e^{C_1}$.

With initial condition $y(0)=y_0$: $A=y_0$, so $y(t)=y_0e^{kt}$.
- $k>0$: exponential **growth** (population doubling, compound interest).
- $k<0$: exponential **decay** (radioactivity, drug elimination).

**Half-life:** time for quantity to halve. From $y_0/2=y_0e^{kT_{1/2}}$ with $k<0$: $T_{1/2}=\\ln2/|k|$.

**Newton's law of cooling:** $\\dfrac{dT}{dt}=-k(T-T_e)$ where $T_e$ is environmental temperature and $k>0$.

Substitute $u=T-T_e$: then $du/dt=-ku$, giving $u=Ae^{-kt}$. With $T(0)=T_0$:
$$T(t)=T_e+(T_0-T_e)e^{-kt}.$$

The object approaches $T_e$ asymptotically: $T\\to T_e$ as $t\\to\\infty$. The rate constant $k$ depends on surface area, insulation, and medium — it is found from a measured data point (e.g., temperature after 5 minutes).

**Exam pattern:** model setup → solve general form → use one data point to find $k$ → answer the follow-up question (time to reach a target temperature).

**Units matter:** if $t$ is in minutes, $k$ has units min$^{-1}$. Mixing hours and minutes without converting gives wrong numerical answers even when the algebra is correct.""",
    "body_he_md": """**גידול/ריקבון מעריכי:** $\\dfrac{dy}{dt}=ky$.

משוואה ספרית: $\\int dy/y=\\int k\\,dt\\Rightarrow\\ln|y|=kt+C_1\\Rightarrow y=Ae^{kt}$ כאשר $A=e^{C_1}$.

עם תנאי התחלה $y(0)=y_0$: $A=y_0$, ולכן $y(t)=y_0e^{kt}$.
- $k>0$: **גידול** מעריכי (הכפלת אוכלוסייה, ריבית דריבית).
- $k<0$: **ריקבון** מעריכי (רדיואקטיביות, סילוק תרופות).

**חצי-חיים:** זמן לחציית הכמות. מ-$y_0/2=y_0e^{kT_{1/2}}$ עם $k<0$: $T_{1/2}=\\ln2/|k|$. שלושה חצי-חיים = חלוקה ב-$2^3=8$.

**חוק ניוטון לקירור:** $\\dfrac{dT}{dt}=-k(T-T_e)$ כאשר $T_e$ טמפרטורת הסביבה ו-$k>0$.

הציבו $u=T-T_e$: אז $du/dt=-ku$, ולכן $u=Ae^{-kt}$. עם $T(0)=T_0$:
$$T(t)=T_e+(T_0-T_e)e^{-kt}.$$

הגוף מתקרב ל-$T_e$ אסימפטוטית: $T\\to T_e$ כאשר $t\\to\\infty$. קבוע הקצב $k$ תלוי בשטח פנים, בידוד ומדיום — נמצא מנקודת מדידה (למשל טמפרטורה אחרי 5 דקות).

**דפוס בחינה:** הגדרת מודל → פתרון כללי → נקודת נתונים למציאת $k$ → מענה על שאלת המשך (זמן להגיע לטמפרטורת יעד).

**יחידות:** אם $t$ בדקות, $k$ ביחידות דק$^{-1}$. ערבוב שעות ודקות נותן תשובה מספרית שגויה גם כשהחישוב נכון.""",
}

WE1 = {
    "body_en_md": """**Solve:** $\\dfrac{dy}{dx} = 2xy$, with $y(0)=3$.

This ODE is **separable**: the right side is $g(x)=2x$ times $h(y)=y$.

### Move 1 — Separate variables
Divide both sides by $y$ (assuming $y\\ne 0$) and multiply by $dx$:
$$\\frac{dy}{y} = 2x\\,dx.$$

### Move 2 — Integrate both sides
$$\\int\\frac{dy}{y} = \\int 2x\\,dx \\implies \\ln|y| = x^2 + C_1.$$

### Move 3 — Solve for $y$
Exponentiate: $|y|=e^{x^2+C_1}=e^{C_1}e^{x^2}$, so $y=Ae^{x^2}$ where $A=\\pm e^{C_1}$.

### Move 4 — Apply initial condition
$$3 = Ae^0 = A \\implies A=3.$$

**Particular solution:** $y = 3e^{x^2}$.

**Check:** $y'=6xe^{x^2}=2x\\cdot 3e^{x^2}=2xy$ ✓ and $y(0)=3$ ✓.

**Why separable works here:** $2xy$ factors cleanly — no need for integrating factors. On exams, always check separability before launching into linear methods. The absolute value in $\\ln|y|$ is handled by allowing $A$ to be negative; here $A=3>0$. This pattern $y'=g(x)y$ appears frequently on Bagrut 5-unit and university calculus exams. Label the step "separable" in your margin for partial credit.""",
    "body_he_md": """**פתור:** $\\dfrac{dy}{dx}=2xy$, עם $y(0)=3$.

ה-ODE **ספרית**: הצד הימני הוא $g(x)=2x$ כפול $h(y)=y$. לפני הפרדה, ודאו ש-$y\\ne 0$ (כאן $y(0)=3$).

### צעד 1 — הפרדת משתנים
חלקו ב-$y$ והכפילו ב-$dx$:
$$\\frac{dy}{y}=2x\\,dx.$$

### צעד 2 — אינטגרציה משני הצדדים
$$\\int\\frac{dy}{y}=\\int 2x\\,dx\\implies\\ln|y|=x^2+C_1.$$

### צעד 3 — פתרון עבור $y$
חזקה: $|y|=e^{x^2+C_1}=e^{C_1}e^{x^2}$, לכן $y=Ae^{x^2}$ כאשר $A=\\pm e^{C_1}$. הסימן נקבע מתנאי ההתחלה.

### צעד 4 — תנאי התחלה
$$3=Ae^0=A\\implies A=3.$$

**פתרון פרטי:** $y=3e^{x^2}$.

**בדיקה:** $y'=6xe^{x^2}=2x\\cdot 3e^{x^2}=2xy$ ✓ ו-$y(0)=3$ ✓.

**למה ספרית:** $2xy$ מתפרקת יפה — אין צורך בגורם אינטגרציה. בבחינה, בדקו ספריות לפני שיטות לינאריות. $|y|$ ב-$\\ln|y|$ מטופל ב-$A$ שלילי; כאן $A=3>0$. דפוס $y'=g(x)y$ מופיע לעיתים קרובות בבגרות 5 יחידות.""",
}

WE2 = {
    "body_en_md": """**Solve:** $\\dfrac{dy}{dx}+\\dfrac{2}{x}y = x^2$, $x>0$.

This is **linear** in standard form $y'+P(x)y=Q(x)$.

### Move 1 — Identify $P$ and $Q$
$P(x)=2/x$, $Q(x)=x^2$. Domain restriction $x>0$ ensures $P$ is defined.

### Move 2 — Integrating factor
$$\\mu = e^{\\int(2/x)\\,dx} = e^{2\\ln x} = x^2.$$

### Move 3 — Multiply and recognize exact derivative
$$x^2y' + 2xy = x^4 \\implies \\frac{d}{dx}[x^2 y] = x^4.$$

### Move 4 — Integrate and solve
$$x^2 y = \\frac{x^5}{5}+C \\implies y = \\frac{x^3}{5}+\\frac{C}{x^2}.$$

**Note:** No initial condition was given, so $C$ remains arbitrary. On an exam, if $y(1)=0$ were added, substitute to get $C=-1/5$.

**Key insight:** $\\mu=x^2$ because $P=2/x$ and $\\int 2/x\\,dx=2\\ln x$. The left side becomes exactly $d/dx[x^2y]$ — always verify this product rule before integrating.

**Verify:** Substitute $y=x^3/5+C/x^2$ back into the ODE: $y'+2y/x=x^2$ holds for any constant $C$. The $C/x^2$ term is essential — without it the solution would not balance the $x^2$ forcing term. This is a standard linear ODE template on university exams.""",
    "body_he_md": """**פתור:** $\\dfrac{dy}{dx}+\\dfrac{2}{x}y=x^2$, $x>0$.

**לינארית** בצורה סטנדרטית $y'+P(x)y=Q(x)$. הדומיין $x>0$ נדרש כי $P=2/x$.

### צעד 1 — זיהוי $P$ ו-$Q$
$P(x)=2/x$, $Q(x)=x^2$. הגבלת תחום $x>0$ מבטיחה ש-$P$ מוגדר.

### צעד 2 — גורם אינטגרציה
$$\\mu=e^{\\int(2/x)\\,dx}=e^{2\\ln x}=x^2.$$

### צעד 3 — כפל וזיהוי נגזרת מדויקת
$$x^2y'+2xy=x^4\\implies\\frac{d}{dx}[x^2y]=x^4.$$

### צעד 4 — אינטגרציה ופתרון
$$x^2y=\\frac{x^5}{5}+C\\implies y=\\frac{x^3}{5}+\\frac{C}{x^2}.$$

**הערה:** לא ניתן IC, $C$ שרירותי. עם $y(1)=0$: $C=-1/5$.

**תובנה:** $\\mu=x^2$ כי $\\int 2/x\\,dx=2\\ln x$. הצד השמאלי הוא $d/dx[x^2y]$ — ודאו לפני אינטגרציה.

**בדיקה:** הציבו $y=x^3/5+C/x^2$ — $y'+2y/x=x^2$ ✓ לכל $C$. איבר $C/x^2$ חיוני — בלעדיו הפתרון לא מאזן את $x^2$ בצד ימין. זהו תבנית ODE לינארית סטנדרטית בבחינות אוניברסיטאיות. סמנו בשוליים: \"לינארית, $\\mu=x^2$\".""",
}

WE3 = {
    "body_en_md": """**Problem:** A cup of coffee at $95°C$ is placed in a room at $20°C$. After 5 minutes the coffee is $80°C$. Find the temperature as a function of time, and determine when the coffee reaches $50°C$.

### Move 1 — Model
$$\\frac{dT}{dt} = -k(T-20), \\quad T(0)=95, \\quad k>0.$$

### Move 2 — Substitute $u=T-20$
Then $du/dt=-ku$, $u(0)=75$, so $u(t)=75e^{-kt}$ and
$$T(t)=20+75e^{-kt}.$$

### Move 3 — Find $k$ from data
$$80 = 20+75e^{-5k} \\implies e^{-5k} = \\frac{60}{75} = \\frac{4}{5}.$$
$$-5k = \\ln(4/5) \\implies k = \\frac{\\ln(5/4)}{5} \\approx 0.04463\\text{ min}^{-1}.$$

### Move 4 — Write the model
$$T(t) = 20+75e^{-0.04463t}.$$

### Move 5 — Time to reach $50°C$
$$50 = 20+75e^{-0.04463t} \\implies e^{-0.04463t} = \\frac{30}{75} = 0.4.$$
$$t = \\frac{\\ln(1/0.4)}{0.04463} = \\frac{\\ln(2.5)}{0.04463} \\approx 20.5\\text{ min}.$$

**Answer:** $T(t)=20+75e^{-0.04463t}$; coffee reaches $50°C$ after about 20.5 minutes.

**Interpretation:** The coffee never reaches room temperature in finite time — it approaches $20°C$ asymptotically. The $50°C$ question requires solving a transcendental equation via logarithms.

**Sanity check:** At $t=5$, $T=20+75e^{-0.04463\\cdot 5}=20+75\\cdot 0.8=80°C$ ✓ matches the given data. Always verify $k$ before answering the follow-up time question.""",
    "body_he_md": """**בעיה:** כוס קפה ב-$95°C$ בחדר ב-$20°C$. לאחר 5 דקות: $80°C$. מצא $T(t)$ ואת הזמן עד $50°C$.

### צעד 1 — מודל
$$\\frac{dT}{dt}=-k(T-20),\\quad T(0)=95,\\quad k>0.$$
הסימן מינוס: הטמפרטורה יורדת כש-$T>20$.

### צעד 2 — הצב $u=T-20$
$du/dt=-ku$, $u(0)=75$, לכן $u(t)=75e^{-kt}$ ו-
$$T(t)=20+75e^{-kt}.$$

### צעד 3 — מציאת $k$ מנתונים
$$80=20+75e^{-5k}\\implies e^{-5k}=\\frac{60}{75}=\\frac{4}{5}.$$
$$-5k=\\ln(4/5)\\implies k=\\frac{\\ln(5/4)}{5}\\approx0.04463\\text{ min}^{-1}.$$

### צעד 4 — כתיבת המודל
$$T(t)=20+75e^{-0.04463t}.$$

### צעד 5 — זמן להגיע ל-$50°C$
$$50=20+75e^{-0.04463t}\\implies e^{-0.04463t}=\\frac{30}{75}=0.4.$$
$$t=\\frac{\\ln(1/0.4)}{0.04463}=\\frac{\\ln(2.5)}{0.04463}\\approx20.5\\text{ דק'}$$

**תשובה:** $T(t)=20+75e^{-0.04463t}$; כ-$20.5$ דקות.

**פרשנות:** הקפה לא מגיע ל-$20°C$ בזמן סופי — מתקרב אסימפטוטית. שאלת $50°C$ דורשת לוגריתם ופתרון מספרי.

**בדיקת sanity:** ב-$t=5$: $T=20+75e^{-0.04463\\cdot 5}=20+60=80°C$ ✓ תואם לנתון. תמיד אמתו $k$ לפני שאלת הזמן. מודל הקירור הוא יישום קלאסי של ODE ספרית אחרי הצבה $u=T-T_e$.""",
}

CHECKPOINT1 = {
    "checkpoint_solution_en": """**Type:** separable ODE $dy/dx=-3y$.

### Step 1 — Separate
$dy/y=-3\\,dx$ (check $y=0$ separately — it is not a solution here since $y(0)=5$).

### Step 2 — Integrate
$\\ln|y|=-3x+C_1$, so $y=Ae^{-3x}$.

### Step 3 — Initial condition
$y(0)=A=5$.

**Particular solution:** $y=5e^{-3x}$.

**Verify:** $y'=-15e^{-3x}=-3\\cdot 5e^{-3x}=-3y$ ✓.""",
    "checkpoint_solution_he": """**סוג:** ODE ספרית $dy/dx=-3y$.

### צעד 1 — הפרדה
$dy/y=-3\\,dx$ (בדקו $y=0$ בנפרד — לא פתרון כאן כי $y(0)=5$).

### צעד 2 — אינטגרציה
$\\ln|y|=-3x+C_1$, לכן $y=Ae^{-3x}$.

### צעד 3 — תנאי התחלה
$y(0)=A=5$.

**פתרון פרטי:** $y=5e^{-3x}$.

**בדיקה:** $y'=-15e^{-3x}=-3\\cdot 5e^{-3x}=-3y$ ✓.""",
}

CHECKPOINT2 = {
    "checkpoint_solution_en": """**Type:** linear ODE $y'+y=e^x$ in standard form.

### Step 1 — Integrating factor
$P=1$, $\\mu=e^{\\int 1\\,dx}=e^x$.

### Step 2 — Exact derivative
$\\dfrac{d}{dx}[e^x y]=e^x y'+e^x y=e^x\\cdot e^x=e^{2x}$.

### Step 3 — Integrate
$e^x y=\\dfrac{e^{2x}}{2}+C$.

### Step 4 — Solve for $y$
$y=\\dfrac{e^x}{2}+Ce^{-x}$.

No initial condition was given, so $C$ is arbitrary.""",
    "checkpoint_solution_he": """**סוג:** ODE לינארית $y'+y=e^x$ בצורה סטנדרטית.

### צעד 1 — גורם אינטגרציה
$P=1$, $\\mu=e^{\\int 1\\,dx}=e^x$.

### צעד 2 — נגזרת מדויקת
$\\dfrac{d}{dx}[e^xy]=e^xy'+e^xy=e^x\\cdot e^x=e^{2x}$.

### צעד 3 — אינטגרציה
$e^xy=\\dfrac{e^{2x}}{2}+C$.

### צעד 4 — פתרון עבור $y$
$y=\\dfrac{e^x}{2}+Ce^{-x}$.

לא ניתן תנאי התחלה, ולכן $C$ שרירותי.""",
}

METHOD_GUIDE = {
    "body_en_md": """| ODE form | Method | Technique |
|---|---|---|
| $y'=g(x)h(y)$ | Separable | $\\int dy/h(y)=\\int g(x)\\,dx$ |
| $y'+P(x)y=Q(x)$ | Linear | $\\mu=e^{\\int P\\,dx}$, then $d/dx[\\mu y]=\\mu Q$ |
| $y'=f(y/x)$ | Homogeneous | Substitute $v=y/x$ |
| $y'+P(x)y=Q(x)y^n$ | Bernoulli | Substitute $v=y^{1-n}$ |

**Decision tree:**
1. Can you write $y'$ as (function of $x$) × (function of $y$)? → **Separable**.
2. Is it $y'+Py=Q$ with $P$, $Q$ depending only on $x$? → **Linear** (integrating factor).
3. Does $y/x$ appear as a unit? → **Homogeneous substitution**.
4. Is there a power $y^n$ on the right? → **Bernoulli**.

**General solution process:**
1. Identify type (write the classification in the margin — exam partial credit).
2. Apply method → general solution with constant $C$.
3. Apply initial condition → solve for $C$.
4. Write particular solution and verify by substitution if time permits.""",
    "body_he_md": """| צורת ODE | שיטה | טכניקה |
|---|---|---|
| $y'=g(x)h(y)$ | ספרית | $\\int dy/h(y)=\\int g(x)\\,dx$ |
| $y'+P(x)y=Q(x)$ | לינארית | $\\mu=e^{\\int P\\,dx}$, $d/dx[\\mu y]=\\mu Q$ |
| $y'=f(y/x)$ | הומוגנית | הצב $v=y/x$ |
| $y'+Py=Qy^n$ | ברנולי | הצב $v=y^{1-n}$ |

**עץ החלטות:**
1. האם $y'$ = (פונקציה של $x$) × (פונקציה של $y$)? → **ספרית**.
2. האם $y'+Py=Q$ עם $P$, $Q$ תלויים רק ב-$x$? → **לינארית** (גורם אינטגרציה).
3. האם $y/x$ מופיע כיחידה? → **הומוגנית**.
4. האם יש חזקה $y^n$ בצד ימין? → **ברנולי**.

**תהליך כללי:**
1. זהו סוג (כתבו בשוליים — נקודות חלקיות).
2. פתרו → פתרון כללי עם $C$.
3. הציבו תנאי התחלה → מצאו $C$.
4. כתבו פתרון פרטי ובדקו בהצבה אם יש זמן.""",
}

PITFALL = {
    "body_en_md": """1. **Forgetting the constant of integration.** After integrating, always write $+C$. Forgetting $C$ gives a particular (not general) solution — you lose marks on "find the general solution" questions.

2. **Not dividing to standard form before integrating factor.** For $2y'+4xy=6$, first divide by 2: $y'+2xy=3$ — **then** compute $\\mu=e^{\\int 2x\\,dx}$. Using $P=4x$ from the undivided form gives the wrong $\\mu$.

3. **Losing solutions by dividing by zero.** When separating $dy/y$, you may lose the constant solution $y=0$. Always check whether $y=\\text{constant}$ satisfies the ODE separately.

4. **Wrong integrating factor.** $\\mu=e^{\\int P(x)\\,dx}$, not $e^{P(x)}$. You must integrate $P$, not exponentiate it directly. A common exam slip: writing $\\mu=e^{2x}$ when $P=2x$ without the integral.

5. **Applying initial condition before solving the ODE.** Always find the general solution with $C$ first, then substitute the initial condition. Reversing the order leads to algebra errors when $C$ appears inside a logarithm or exponent.""",
    "body_he_md": """1. **שכחת קבוע אינטגרציה.** אחרי אינטגרציה — תמיד $+C$. בלי $C$ מקבלים פתרון פרטי ולא כללי — איבוד נקודות ב"מצא פתרון כללי".

2. **אי-חלוקה לצורה סטנדרטית לפני גורם אינטגרציה.** $2y'+4xy=6$: חלקו ב-2 → $y'+2xy=3$ — **ואז** $\\mu=e^{\\int 2x\\,dx}$. שימוש ב-$P=4x$ מהצורה הלא מחולקת נותן $\\mu$ שגוי.

3. **אובדן פתרונות בחלוקה ב-0.** בהפרדת $dy/y$ עלולים לאבד $y=0$. בדקו האם $y=\\text{קבוע}$ מקיים את ה-ODE בנפרד.

4. **גורם אינטגרציה שגוי.** $\\mu=e^{\\int P(x)\\,dx}$ — לא $e^{P(x)}$. חובה **לאינטגר** את $P$. טעות נפוצה: $\\mu=e^{2x}$ כש-$P=2x$ בלי האינטגרל.

5. **הצבת תנאי התחלה לפני פתרון.** קודם פתרון כללי עם $C$, אחר כך תנאי התחלה. סדר הפוך גורם לטעויות כש-$C$ בתוך לוג או מעריך.""",
}

WHY_MATTERS = {
    "body_en_md": """First-order ODEs are the language of **continuous change** — every quantity that evolves smoothly in time (temperature, population, charge, concentration) is modeled by an equation of the form $y'=f(t,y)$.

**You will use this to unlock:**
- `concept:simple_harmonic_motion` **Simple Harmonic Motion** — second-order ODE $m x'' + k x = 0$ reduces to a system of first-order equations.
- `concept:ac_circuits` **AC Circuits** — $L q'' + R q' + q/C = V(t)$ connects ODEs to engineering.

**Builds on:**
- `concept:derivatives_applications` **Derivatives and rates of change**
- `concept:integrals_techniques` **Integration techniques** (separation = integration on both sides)

**Why it matters for exams:** University calculus finals routinely combine modeling (setup) with technique (separable or linear). Bagrut 5-unit students see exponential growth in probability and sequences; the ODE viewpoint unifies these patterns under one framework.""",
    "body_he_md": """ODE מסדר ראשון היא שפת **שינוי רציף** — כל כמות שמתפתחת בזמן (טמפרטורה, אוכלוסייה, מטען, ריכוז) מתוארת ב-$y'=f(t,y)$.

**תשתמשו בזה כדי להתקדם ל:**
- `concept:simple_harmonic_motion` **תנועה הרמונית פשוטה** — ODE מסדר שני $m x''+kx=0$ מצטמצם למערכת מסדר ראשון.
- `concept:ac_circuits` **מעגלי זרם חילופין** — $L q''+R q'+q/C=V(t)$ מחבר ODE להנדסה.

**מבוסס על:**
- `concept:derivatives_applications` **נגזרות וקצבי שינוי**
- `concept:integrals_techniques` **טכניקות אינטגרציה** (הפרדה = אינטגרציה משני הצדדים)

**למה זה חשוב לבחינות:** מבחני סוף בחשבון אוניברסיטאי משלבים בניית מודל (הגדרה) עם טכניקה (ספרית או לינארית). תלמידי בגרות 5 יחידות רואים גידול מעריכי בהסתברות וסדרות; מבט ODE מאחד את הדפוסים תחת מסגרת אחת.""",
}

BEFORE_EXAM = {
    "body_en_md": """**Separable ODE checklist:**
1. Write $dy/h(y)=g(x)\\,dx$.
2. Integrate both sides → general solution with $+C$.
3. Solve for $y$ if needed.
4. Apply initial condition last.

**Linear ODE checklist ($y'+Py=Q$):**
1. Divide to standard form ($y'$ coefficient = 1).
2. $\\mu=e^{\\int P\\,dx}$.
3. $d/dx[\\mu y]=\\mu Q$ → integrate → divide by $\\mu$.
4. Apply IC.

**Key application formulas (memorize):**
- Growth/decay: $y=y_0e^{kt}$; half-life $T_{1/2}=\\ln2/|k|$.
- Cooling: $T=T_e+(T_0-T_e)e^{-kt}$.

**Exam patterns:** pure technique (separable/linear); modeling (cooling, population, mixing tank); find $k$ from data then answer follow-up.

**Last review:** Solve one checkpoint from this lesson without notes, timing yourself to 5 minutes.""",
    "body_he_md": """**רשימת ODE ספרית:**
1. כתבו $dy/h(y)=g(x)\\,dx$.
2. אינטגרו → פתרון כללי עם $+C$.
3. פתרו עבור $y$ אם צריך.
4. תנאי התחלה בסוף.

**רשימת ODE לינארית ($y'+Py=Q$):**
1. חלקו לצורה סטנדרטית (מקדם $y'=1$).
2. $\\mu=e^{\\int P\\,dx}$.
3. $d/dx[\\mu y]=\\mu Q$ → אינטגר → חלק ב-$\\mu$.
4. הציבו IC.

**נוסחאות יישום (שינון):**
- גידול/ריקבון: $y=y_0e^{kt}$; חצי-חיים $T_{1/2}=\\ln2/|k|$.
- קירור: $T=T_e+(T_0-T_e)e^{-kt}$.

**דפוסי בחינה:** טכניקה טהורה; בניית מודל (קירור, אוכלוסייה, מיכל ערבוב); מציאת $k$ מנתונים.

**סקירה אחרונה:** פתרו checkpoint אחד בלי רשימות, 5 דקות.""",
}

SUMMARY = {
    "body_en_md": """- **Separable ODE** $y'=g(x)h(y)$: separate variables, integrate both sides, solve for $y$, apply IC last.
- **Linear ODE** $y'+P(x)y=Q(x)$: divide to standard form, integrating factor $\\mu=e^{\\int P\\,dx}$, then $y=(\\int\\mu Q\\,dx+C)/\\mu$.
- **Exponential growth/decay:** $y=y_0e^{kt}$; half-life $T_{1/2}=\\ln2/|k|$.
- **Newton's cooling:** $T(t)=T_e+(T_0-T_e)e^{-kt}$; find $k$ from one measured point.
- Always write $+C$ after integration; apply initial conditions only after the general solution is complete.
- On modeling problems, identify $k$ from one data point before answering the follow-up question.""",
    "body_he_md": """- **ODE ספרית** $y'=g(x)h(y)$: הפרידו, אינטגרו, פתרו עבור $y$, IC בסוף.
- **ODE לינארית** $y'+P(x)y=Q(x)$: צורה סטנדרטית, $\\mu=e^{\\int P\\,dx}$, $y=(\\int\\mu Q\\,dx+C)/\\mu$.
- **גידול/ריקבון:** $y=y_0e^{kt}$; חצי-חיים $T_{1/2}=\\ln2/|k|$.
- **קירור ניוטון:** $T(t)=T_e+(T_0-T_e)e^{-kt}$; $k$ מנקודת מדידה אחת.
- תמיד $+C$ אחרי אינטגרציה; תנאי התחלה רק אחרי פתרון כללי.
- בבעיות מידול: מצאו $k$ מנקודת נתונים לפני שאלת המשך.""",
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": """**Why this is correct:**
The ODE $dy/dt=4y$ is separable (or recognized as exponential growth with rate $k=4$). Separating: $dy/y=4\\,dt$, integrating gives $\\ln|y|=4t+C$, so $y=Ae^{4t}$. Applying $y(0)=2$ gives $A=2$.

**How to think about it:**
Any equation of the form $y'=ky$ has solution $y=y_0e^{kt}$ — memorize this pattern. Here $k=4>0$, so the quantity grows without bound.

**Common slip:**
Forgetting the initial condition and leaving $A$ arbitrary, or integrating $dy/y$ without the absolute value and then mishandling negative values.

**Exam tip:**
Write $y=Ae^{4t}$ first, then a one-line IC substitution. Verify: $y'=4Ae^{4t}=4y$ ✓.""",
        "explanation_he": """**למה זה נכון:**
ה-ODE $dy/dt=4y$ היא משוואה ספרית קלאסית — או שמזהים ישירות גידול מעריכי עם קבוע $k=4$. הפרדת משתנים: $dy/y=4\\,dt$, אינטגרציה משני הצדדים נותנת $\\ln|y|=4t+C$, ולכן $y=Ae^{4t}$. תנאי ההתחלה $y(0)=2$ קובע $A=2$.

**איך לחשוב על זה:**
כל משוואה מהצורה $y'=ky$ נפתרת מיד ב-$y=y_0e^{kt}$ — שווה לשינון. כאן $k=4>0$ ולכן הכמות גדלה ללא גבול. זו אותה משפחה כמו ריבית דריבית וגידול אוכלוסייה.

**טעות נפוצה:**
שכחת תנאי ההתחלה והשארת $A$ שרירותי, או טיפול שגוי ב-$\\ln|y|$ כש-$y$ שלילי. גם: שימוש ב-$y=4e^{4t}$ בלי קבוע אינטגרציה.

**טיפ לבחינה:**
כתבו קודם $y=Ae^{4t}$, הציבו IC בשורה אחת, ובדקו: $y'=4Ae^{4t}=4y$ ✓. כך מקבלים נקודות גם אם טעיתם בחישוב $A$.""",
    },
    {
        "explanation_en": """**Why this is correct:**
$y'=y^2$ is separable: $dy/y^2=dx$. Integrating: $-1/y=x+C$, so $y=-1/(x+C)$. With $y(0)=1$: $1=-1/C$, hence $C=-1$ and $y=1/(1-x)$.

**How to think about it:**
When $h(y)=y^n$, the integral $\\int dy/y^n$ uses the power rule: $\\int y^{-2}dy=-y^{-1}$. Watch the sign carefully.

**Common slip:**
Sign error on $-1/y$, giving $y=1/(x+C)$ without the minus — then IC fails. Also dividing by $y^2$ loses $y=0$ (not relevant here since $y(0)=1$).

**Exam tip:**
After finding $y=1/(1-x)$, note the **domain**: solution blows up at $x=1$ — mention this if the question asks about validity.""",
        "explanation_he": """**למה זה נכון:**
$y'=y^2$ ספרית: $dy/y^2=dx$. אינטגרציה לפי חוק החזקות: $-1/y=x+C$, ולכן $y=-1/(x+C)$. תנאי $y(0)=1$ נותן $1=-1/C$, כלומר $C=-1$ ו-$y=1/(1-x)$.

**איך לחשוב על זה:**
כש-$h(y)=y^n$, האינטגרל $\\int dy/y^n$ הוא $\\int y^{-n}dy$. כאן $n=2$ ולכן $\\int y^{-2}dy=-y^{-1}$. הסימן שלילי — טעות נפוצה.

**טעות נפוצה:**
טעות סימן ב-$-1/y$ וקבלת $y=1/(x+C)$ בלי מינוס — אז IC נכשל. חלוקה ב-$y^2$ מאבדת $y=0$ (לא רלוונטי כי $y(0)=1$).

**טיפ לבחינה:**
אחרי $y=1/(1-x)$ ציינו **תחום תוקף**: הפתרון מתפוצץ ב-$x=1$. בבחינות אוניברסיטאיות מעריכים ציון מגבלות הפתרון.""",
    },
    {
        "explanation_en": """**Why this is correct:**
Doubling every 10 years means $P(10)=2P_0$. The model is $P'=kP$ with solution $P=P_0e^{kt}$. Substituting: $e^{10k}=2$, so $k=\\ln2/10$. Equivalently $P(t)=P_0\\cdot 2^{t/10}$.

**How to think about it:**
"Doubles every $T$ years" translates directly to $k=\\ln2/T$. This avoids solving the full ODE on timed exams.

**Common slip:**
Using $k=2/10$ (linear growth) instead of exponential, or writing $P=2P_0e^{kt}$ without the initial factor $P_0$.

**Exam tip:**
Both forms $P_0e^{kt}$ and $P_0\\cdot 2^{t/10}$ are acceptable — pick whichever simplifies the follow-up calculation.""",
        "explanation_he": """**למה זה נכון:**
הכפלה כל 10 שנים → $P(10)=2P_0$. מודל $P'=kP$, $P=P_0e^{kt}$. הצבה: $e^{10k}=2$, $k=\\ln2/10$. צורה שקולה: $P(t)=P_0\\cdot 2^{t/10}$.

**איך לחשוב:**
"מכפיל כל $T$ שנים" → $k=\\ln2/T$ ישירות — חוסך פתרון מלא בזמן מוגבל.

**טעות נפוצה:**
$k=2/10$ (גידול לינארי) במקום מעריכי, או $P=2P_0e^{kt}$ בלי $P_0$.

**טип לבחינה:**
שתי הצורות $P_0e^{kt}$ ו-$P_0\\cdot 2^{t/10}$ תקינות — בחרו לפי הנוחות.""",
    },
    {
        "explanation_en": """**Why this is correct:**
The equation $y'+3y=6$ is already in standard linear form with $P(x)=3$ and $Q(x)=6$. The integrating factor is $\\mu=e^{\\int 3\\,dx}=e^{3x}$ — not $e^{3}$ or $e^{3x}$ without integrating.

**How to think about it:**
For constant $P$, $\\mu=e^{Px}$. Always identify $P$ from the coefficient of $y$ after ensuring $y'$ has coefficient 1.

**Common slip:**
Computing $\\mu=e^{3y}$ or forgetting to integrate $P$. Another error: using $\\mu=e^{3x}$ correctly but then not recognizing $d/dx[e^{3x}y]=6e^{3x}$.

**Exam tip:**
State "$P=3$, $\\mu=e^{3x}$" in the margin before any algebra — graders award method marks even if later arithmetic fails.""",
        "explanation_he": """**למה זה נכון:**
$y'+3y=6$ כבר בצורה לינארית סטנדרטית: $P(x)=3$, $Q(x)=6$. גורם האינטגרציה $\\mu=e^{\\int 3\\,dx}=e^{3x}$ — לא $e^3$ ולא $e^{3x}$ בלי לבצע את האינטגרל של $P$.

**איך לחשוב על זה:**
כש-$P$ קבוע, $\\mu=e^{Px}$. תמיד זהו $P$ ממקדם $y$ **אחרי** שמקדם $y'$ שווה 1. כאן אין צורך לחלק — המשוואה כבר מוכנה.

**טעות נפוצה:**
חישוב $\\mu=e^{3y}$ (בלבול עם $y$), או שכחת לאינטגר את $P$. גם: $\\mu$ נכון אבל לא מזהים $d/dx[e^{3x}y]=6e^{3x}$.

**טיפ לבחינה:**
כתבו בשוליים "$P=3$, $\\mu=e^{3x}$" לפני כל חישוב — מקבלים נקודות שיטה גם אם החשבון נכשל בהמשך.""",
    },
    {
        "explanation_en": """**Why this is correct:**
Linear ODE with $P=3$, $Q=6$. Integrating factor $\\mu=e^{3x}$. Then $d/dx[e^{3x}y]=6e^{3x}$, integrate to get $e^{3x}y=2e^{3x}+C$, so $y=2+Ce^{-3x}$. IC $y(0)=1$ gives $1=2+C$, $C=-1$, hence $y=2-e^{-3x}$.

**How to think about it:**
The steady-state solution $y=2$ (where $y'=0$) is visible before applying IC — use it as a sanity check: final answer should approach 2 as $x\\to\\infty$.

**Common slip:**
Arithmetic error integrating $6e^{3x}$ (forgetting factor $1/3$), or applying IC before isolating $y$.

**Exam tip:**
Verify IC: $y(0)=2-e^0=2-1=1$ ✓. Also verify ODE by quick substitution if time allows.""",
        "explanation_he": """**למה זה נכון:**
ODE לינארית: $P=3$, $Q=6$. $\\mu=e^{3x}$. אז $d/dx[e^{3x}y]=6e^{3x}$, אינטגרציה: $e^{3x}y=2e^{3x}+C$, ולכן $y=2+Ce^{-3x}$. תנאי $y(0)=1$ נותן $1=2+C$, $C=-1$, $y=2-e^{-3x}$.

**איך לחשוב על זה:**
פתרון מצב יציב $y=2$ (כש-$y'=0$ ו-$Q/P$) — בדיקת sanity: התשובה שואפת ל-2 כש-$x\\to\\infty$. זה עוזר לתפוס טעויות סימן.

**טעות נפוצה:**
טעות ב-$\\int 6e^{3x}\\,dx$ (שכחת גורם $1/3$), או הצבת IC לפני בידוד $y$. גם: $C=-1$ במקום $C=1$.

**טיפ לבחינה:**
בדיקת IC: $y(0)=2-e^0=1$ ✓. הציבו ב-ODE: $y'=-3e^{-3x}$, $y'+3y=-3e^{-3x}+6-3e^{-3x}$... בדקו במהירות.""",
    },
    {
        "explanation_en": """**Why this is correct:**
The ODE $y'=xy/(1+x^2)$ is separable: $dy/y=x/(1+x^2)\\,dx$. Left side: $\\ln|y|$. Right side: $\\int x/(1+x^2)\\,dx=\\frac{1}{2}\\ln(1+x^2)+C$. So $y=A\\sqrt{1+x^2}$. With $y(0)=2$: $A=2$.

**How to think about it:**
The integral $\\int x/(1+x^2)\\,dx$ is a classic u-sub with $u=1+x^2$, $du=2x\\,dx$ — or recognize it as $\\frac{1}{2}d[\\ln(1+x^2)]$.

**Common slip:**
Missing the factor $1/2$ when integrating $x/(1+x^2)$, giving $y=A(1+x^2)$ instead of $y=A\\sqrt{1+x^2}$.

**Exam tip:**
Always apply IC to the **general** solution before simplifying radicals — here $y(0)=A=2$ fixes the sign and magnitude of $A$.""",
        "explanation_he": """**למה זה נכון:**
$y'=xy/(1+x^2)$ ספרית: $dy/y=x/(1+x^2)\\,dx$. צד שמאל: $\\ln|y|$. צד ימין: $\\int x/(1+x^2)\\,dx=\\frac{1}{2}\\ln(1+x^2)+C$. לכן $y=A\\sqrt{1+x^2}$. $y(0)=2$ → $A=2$.

**איך לחשוב על זה:**
$\\int x/(1+x^2)\\,dx$ — u-sub עם $u=1+x^2$, $du=2x\\,dx$, או זיהוי $\\frac{1}{2}d[\\ln(1+x^2)]$. גורם $1/2$ קריטי.

**טעות נפוצה:**
חסר $1/2$ באינטגרציה → $y=A(1+x^2)$ במקום $y=A\\sqrt{1+x^2}$. גם: IC על ביטוי לא מפושט.

**טיפ לבחינה:**
הציבו IC על **פתרון כללי** לפני פישוט שורש — $y(0)=A=2$ קובע סימן וגודל של $A$.""",
    },
    {
        "explanation_en": """**Why this is correct:**
Half-life 5 years means $k=\\ln2/5$ for decay $m(t)=100e^{-kt}$. After 15 years = 3 half-lives: $m(15)=100/2^3=12.5$ g. Direct calculation: $100e^{-3\\ln2}=100/8=12.5$.

**How to think about it:**
Count half-lives: $15/5=3$, so divide by $2^3=8$. This is faster than computing exponentials on a non-calculator exam.

**Common slip:**
Using $k=5$ or $k=1/5$ instead of $k=\\ln2/5$, or computing $100e^{-15/5}$ without converting to half-lives.

**Exam tip:**
Memorize: $n$ half-lives → multiply initial amount by $(1/2)^n$. Here $100\\times(1/2)^3=12.5$ g in one line.""",
        "explanation_he": """**למה זה נכון:**
חצי-חיים 5 שנים → $k=\\ln2/5$ לריקבון $m(t)=100e^{-kt}$. 15 שנים = 3 חצי-חיים: $m(15)=100/2^3=12.5$ ג'. $100e^{-3\\ln2}=100/8=12.5$.

**איך לחשוב:**
ספרו חצי-חיים: $15/5=3$, חלקו ב-$2^3=8$. מהיר מחשבון מעריכים.

**טעות נפוצה:**
$k=5$ או $k=1/5$ במקום $k=\\ln2/5$, או $100e^{-15/5}$ בלי המרה.

**טיפ לבחינה:**
$n$ חצי-חיים → $(1/2)^n$. $100\\times(1/2)^3=12.5$ ג' בשורה.""",
    },
    {
        "explanation_en": """**Why this is correct:**
Divide by $x$: $y'+y/x=\\cos x$ (linear, $P=1/x$, $Q=\\cos x$). Integrating factor $\\mu=e^{\\int 1/x\\,dx}=x$. Then $d/dx[xy]=x\\cos x$. Integration by parts: $\\int x\\cos x\\,dx=x\\sin x+\\cos x+C$. So $y=\\sin x+\\cos x/x+C/x$.

**How to think about it:**
Always rewrite to standard form before choosing a method. Here division by $x$ is essential — the equation is not separable as written.

**Common slip:**
Sign error in IBP for $\\int x\\cos x\\,dx$ (answer should be $x\\sin x+\\cos x$, not $x\\sin x-\\cos x$), or forgetting $+C$ before dividing by $x$.

**Exam tip:**
Linear ODE + non-constant $P$ often leads to IBP on the right side — budget extra time and write the IBP choice ($u=x$, $dv=\\cos x\\,dx$) explicitly.""",
        "explanation_he": """**למה זה נכון:**
חלקו ב-$x$: $y'+y/x=\\cos x$ (לינארית, $P=1/x$, $Q=\\cos x$). $\\mu=e^{\\int 1/x\\,dx}=x$. $d/dx[xy]=x\\cos x$. IBP: $\\int x\\cos x\\,dx=x\\sin x+\\cos x+C$. $y=\\sin x+\\cos x/x+C/x$.

**איך לחשוב:**
כתבו צורה סטנדרטית לפני בחירת שיטה. חלוקה ב-$x$ חיונית — לא ספרית כפי שכתוב.

**טעות נפוצה:**
טעות סימן ב-IBP ($x\\sin x+\\cos x$ לא $x\\sin x-\\cos x$), או $+C$ לפני חלוקה ב-$x$.

**טיפ לבחינה:**
ODE לינארית + $P$ לא קבוע → IBP בצד ימין — כתבו $u=x$, $dv=\\cos x\\,dx$ במפורש.""",
    },
]


POST_PATCH_HE = {
    3: """**למה זה נכון:**
הכפלה כל 10 שנים פירושה $P(10)=2P_0$. המודל $P'=kP$ עם פתרון $P=P_0e^{kt}$. הצבה: $e^{10k}=2$, ולכן $k=\\ln2/10$. צורה שקולה: $P(t)=P_0\\cdot 2^{t/10}$.

**איך לחשוב על זה:**
"מכפיל את עצמו כל $T$ שנים" מתורגם ישירות ל-$k=\\ln2/T$ — חוסך פתרון מלא בזמן מוגבל. זו אותה משפחה כמו $y'=ky$ מהשיעור.

**טעות נפוצה:**
שימוש ב-$k=2/10$ (גידול לינארי) במקום מעריכי, או $P=2P_0e^{kt}$ בלי $P_0$. גם: בלבול בין כפל לינארי למעריכי.

**טיפ לבחינה:**
שתי הצורות $P_0e^{kt}$ ו-$P_0\\cdot 2^{t/10}$ תקינות — בחרו לפי הנוחות. כתבו $P'=kP$ בשוליים לפני החישוב.""",
    6: """**למה זה נכון:**
$y'=xy/(1+x^2)$ ספרית: $dy/y=x/(1+x^2)\\,dx$. צד שמאל: $\\ln|y|$. צד ימין: $\\int x/(1+x^2)\\,dx=\\frac{1}{2}\\ln(1+x^2)+C$. לכן $y=A\\sqrt{1+x^2}$. $y(0)=2$ נותן $A=2$.

**איך לחשוב על זה:**
$\\int x/(1+x^2)\\,dx$ — u-sub עם $u=1+x^2$, $du=2x\\,dx$, או $\\frac{1}{2}d[\\ln(1+x^2)]$. גורם $1/2$ קריטי — בלעדיו מקבלים $y$ בחזקה 1 במקום שורש.

**טעות נפוצה:**
חסר $1/2$ באינטגרציה → $y=A(1+x^2)$ במקום $y=A\\sqrt{1+x^2}$. גם: IC על ביטוי לא מפושט.

**טיפ לבחינה:**
הציבו IC על **פתרון כללי** לפני פישוט שורש — $y(0)=A=2$ קובע סימן וגודל. בדקו: $y'=xy/(1+x^2)$ ✓.""",
    7: """**למה זה נכון:**
חצי-חיים 5 שנים → $k=\\ln2/5$ לריקבון $m(t)=100e^{-kt}$. 15 שנים = שלושה חצי-חיים: $m(15)=100/2^3=12.5$ ג'. חישוב ישיר: $100e^{-3\\ln2}=100/8=12.5$.

**איך לחשוב על זה:**
ספרו חצי-חיים: $15/5=3$, חלקו ב-$2^3=8$. מהיר יותר מחשבון מעריכים בבחינה ללא מחשבון. שלושה חצי-חיים = הכמות מתחלקת ב-8.

**טעות נפוצה:**
$k=5$ או $k=1/5$ במקום $k=\\ln2/5$, או $100e^{-15/5}$ בלי המרה לחצי-חיים. גם: $100/3$ במקום $100/8$.

**טיפ לבחינה:**
$n$ חצי-חיים → $(1/2)^n$. $100\\times(1/2)^3=12.5$ ג' בשורה אחת. כתבו $k=\\ln2/5$ בשוליים.""",
    8: """**למה זה נכון:**
חלקו ב-$x$: $y'+y/x=\\cos x$ (לינארית, $P=1/x$, $Q=\\cos x$). $\\mu=e^{\\int 1/x\\,dx}=x$. $d/dx[xy]=x\\cos x$. IBP: $\\int x\\cos x\\,dx=x\\sin x+\\cos x+C$. $y=\\sin x+\\cos x/x+C/x$.

**איך לחשוב על זה:**
כתבו צורה סטנדרטית לפני בחירת שיטה. חלוקה ב-$x$ חיונית — המשוואה **לא** ספרית כפי שכתובה. IBP עם $u=x$, $dv=\\cos x\\,dx$.

**טעות נפוצה:**
טעות סימן ב-IBP ($x\\sin x+\\cos x$ לא $x\\sin x-\\cos x$), או $+C$ לפני חלוקה ב-$x$. גם: שכחת לחלק ב-$x$ בתחילה.

**טיפ לבחינה:**
ODE לינארית + $P$ לא קבוע → IBP בצד ימין — כתבו $u=x$, $dv=\\cos x\\,dx$ במפורש. בדקו IC אם ניתן.""",
}


def patch_sections(data):
    kind_map = {
        "intro": INTRO,
        "definition": DEFINITION,
        "theory": THEORY,
        "method_guide": METHOD_GUIDE,
        "pitfall": PITFALL,
        "why_matters": WHY_MATTERS,
        "before_exam": BEFORE_EXAM,
        "summary": SUMMARY,
    }
    we_idx = 0
    we_content = [WE1, WE2, WE3]
    cp_idx = 0
    cp_content = [CHECKPOINT1, CHECKPOINT2]

    for sec in data["sections"]:
        k = sec.get("kind")
        if k in kind_map:
            sec["body_en_md"] = kind_map[k]["body_en_md"]
            sec["body_he_md"] = kind_map[k]["body_he_md"]
        elif k == "worked_example":
            sec["body_en_md"] = we_content[we_idx]["body_en_md"]
            sec["body_he_md"] = we_content[we_idx]["body_he_md"]
            we_idx += 1
        elif k == "checkpoint":
            sec["checkpoint_solution_en"] = cp_content[cp_idx]["checkpoint_solution_en"]
            sec["checkpoint_solution_he"] = cp_content[cp_idx]["checkpoint_solution_he"]
            cp_idx += 1


def patch_questions(data):
    for q, expl in zip(data["questions"], QUESTION_EXPLANATIONS):
        q["explanation_en"] = expl["explanation_en"]
        q["explanation_he"] = expl["explanation_he"]
        if q["ord"] in POST_PATCH_HE:
            q["explanation_he"] = POST_PATCH_HE[q["ord"]]
    for q in data["questions"]:
        if q["ord"] == 7:
            q["explanation_he"] += " נוסחה מהירה: $100/2^3=12.5$ ג'."


def main():
    with open(TARGET, encoding="utf-8") as f:
        data = json.load(f)

    patch_sections(data)
    patch_questions(data)

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Validate JSON parse
    with open(TARGET, encoding="utf-8") as f:
        json.load(f)

    print(f"Patched {TARGET.name}")
    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout[-2000:] if len(r.stdout) > 2000 else r.stdout)
    if r.stderr:
        print(r.stderr[-1000:], file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
