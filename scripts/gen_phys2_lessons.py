#!/usr/bin/env python3
"""
Generate 5 university Physics 2 (E&M) lessons for the A Step Forward platform.
Run from the monorepo root:
    python scripts/gen_phys2_lessons.py
"""
import json, os

LESSONS_DIR = "scripts/seed_data/lessons"

# ─────────────────────────────────────────────────────────────────
# LESSON 1 — Gauss's Law
# ─────────────────────────────────────────────────────────────────
gauss = {
  "id": "electric_field_gauss",
  "type": "interactive",
  "subject": "university_physics_2",
  "title_en": "Gauss's Law — Electric Flux and Symmetric Fields",
  "title_he": "חוק גאוס — שטף חשמלי ושדות בעלי סימטריה",
  "duration_min": 30,
  "level_min": "university",
  "agent_hints": "Stress the two-step strategy: (1) argue by symmetry that |E| is constant and angle is known on the chosen surface, (2) evaluate the surface integral as a simple product E·A. Common errors: applying Gauss's law to non-symmetric charge distributions; forgetting that Q_enc is the TOTAL enclosed charge; confusing the direction of dA for a closed surface (always outward normal). For the sphere inside/outside distinction, make students re-derive Q_enc(r) for r<R by using the volume fraction. Connect to conductors: show that E=0 inside follows directly from Gauss's law applied to a surface just inside the conductor.",
  "sections": [
    {
      "id": "electric_flux",
      "title_en": "Electric Flux",
      "title_he": "שטף חשמלי",
      "level_min": "university",
      "body_en_md": "## Electric Flux\n\nThe **electric flux** through a surface $S$ is defined as the surface integral of the electric field over that surface:\n\n$$\\Phi_E = \\iint_S \\vec{E} \\cdot d\\vec{A}$$\n\nwhere $d\\vec{A} = \\hat{n}\\,dA$ is an area element whose direction is the outward unit normal $\\hat{n}$.\n\n**Units:** $[\\Phi_E] = \\text{N}\\cdot\\text{m}^2/\\text{C} = \\text{V}\\cdot\\text{m}$.\n\n**Sign convention:** Flux is *positive* when $\\vec{E}$ has a component along the outward normal (field lines leaving the surface), and *negative* when it has a component against the outward normal (field lines entering).\n\nFor a *uniform* field $\\vec{E}$ through a *flat* surface of area $A$ with $\\vec{E}$ at angle $\\theta$ to the normal:\n\n$$\\Phi_E = EA\\cos\\theta$$\n\n**Physical meaning:** Flux counts the net number of field lines piercing the surface. It is not a vector—it is a scalar that can be positive, negative, or zero.",
      "body_he_md": "## שטף חשמלי\n\n**השטף החשמלי** דרך משטח $S$ מוגדר כאינטגרל המשטחי של השדה החשמלי על המשטח:\n\n$$\\Phi_E = \\iint_S \\vec{E} \\cdot d\\vec{A}$$\n\nכאשר $d\\vec{A} = \\hat{n}\\,dA$ הוא אלמנט שטח שכיוונו הוא הנורמל החיצוני היחידה $\\hat{n}$.\n\n**יחידות:** $[\\Phi_E] = \\text{N}\\cdot\\text{m}^2/\\text{C} = \\text{V}\\cdot\\text{m}$.\n\n**קונבנציית סימן:** שטף *חיובי* כאשר ל-$\\vec{E}$ יש רכיב בכיוון הנורמל החיצוני (קווי שדה יוצאים מהמשטח), ו*שלילי* כאשר הרכיב הוא נגד הנורמל (קווי שדה נכנסים).\n\nעבור שדה *אחיד* $\\vec{E}$ דרך משטח *שטוח* בשטח $A$ עם זווית $\\theta$ בין $\\vec{E}$ לנורמל:\n\n$$\\Phi_E = EA\\cos\\theta$$\n\n**משמעות פיזיקלית:** השטף סופר את המספר הנטו של קווי השדה החוצים את המשטח. הוא סקלר (לא וקטור) שיכול להיות חיובי, שלילי או אפס."
    },
    {
      "id": "gauss_law_statement",
      "title_en": "Gauss's Law — Statement and Intuition",
      "title_he": "חוק גאוס — ניסוח ואינטואיציה",
      "level_min": "university",
      "body_en_md": "## Gauss's Law\n\nFor any closed surface $S$ (a *Gaussian surface*), the total electric flux equals the net enclosed charge divided by $\\epsilon_0$:\n\n$$\\oint_S \\vec{E} \\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\nwhere $Q_{\\text{enc}}$ is the **total charge enclosed** by $S$, and $\\epsilon_0 = 8.854\\times10^{-12}\\;\\text{C}^2/(\\text{N}\\cdot\\text{m}^2)$ is the permittivity of free space.\n\n**Intuition:** Every line of electric field that originates on a positive charge $+q$ must cross any closed surface that encloses $q$ exactly once outward. So the net outward flux through any closed surface depends *only* on the total enclosed charge, not on the shape of the surface or on charges outside it.\n\n**Charges outside** the Gaussian surface contribute field lines that enter and exit the surface the same number of times—their net contribution to the flux is zero.\n\nGauss's law is one of Maxwell's four equations and is *equivalent* to Coulomb's law for static charges, but it is far more powerful when combined with symmetry.",
      "body_he_md": "## חוק גאוס\n\nעבור כל משטח סגור $S$ (משטח גאוסי), הזרם החשמלי הכולל שווה למטען הכלוא נטו חלקי $\\epsilon_0$:\n\n$$\\oint_S \\vec{E} \\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\n\nכאשר $Q_{\\text{enc}}$ הוא **המטען הכולל הכלוא** ב-$S$, ו-$\\epsilon_0 = 8.854\\times10^{-12}\\;\\text{C}^2/(\\text{N}\\cdot\\text{m}^2)$ הוא מקדם הדיאלקטריות של ריק.\n\n**אינטואיציה:** כל קו שדה חשמלי היוצא ממטען חיובי $+q$ חייב לחצות כל משטח סגור המכיל את $q$ פעם אחת כלפי חוץ. לפיכך, השטף החיצוני הנטו דרך כל משטח סגור תלוי *רק* במטען הכלוא הכולל — לא בצורת המשטח ולא במטענים מחוץ לו.\n\n**מטענים מחוץ** למשטח הגאוסי תורמים קווי שדה הנכנסים ויוצאים מספר שווה של פעמים — תרומתם הנטו לשטף היא אפס.\n\nחוק גאוס הוא אחת מארבע משוואות מקסוול ו*שקול* לחוק קולון עבור מטענים סטטיים, אך הוא עוצמתי בהרבה בשילוב עם סימטריה."
    },
    {
      "id": "gaussian_surface_choice",
      "title_en": "Choosing a Gaussian Surface — Symmetry Arguments",
      "title_he": "בחירת משטח גאוסי — ארגומנטים של סימטריה",
      "level_min": "university",
      "body_en_md": "## When Can We Use Gauss's Law to Find $\\vec{E}$?\n\nGauss's law is *always true*, but it lets you solve for $|\\vec{E}|$ algebraically only when you can show that:\n1. $|\\vec{E}|$ is **constant** over (part of) the Gaussian surface, **and**\n2. $\\vec{E}$ is either **parallel** or **perpendicular** to $d\\vec{A}$ everywhere on that part.\n\nWhen both conditions hold, $\\oint \\vec{E}\\cdot d\\vec{A}$ reduces to $E \\cdot A_{\\parallel}$ (the area where $\\vec{E}\\parallel\\hat{n}$).\n\n**The three standard geometries:**\n\n| Charge distribution | Symmetry | Gaussian surface |\n|---|---|---|\n| Infinite plane (charge density $\\sigma$) | Planar | Pillbox (cylinder with axis ⊥ plane) |\n| Infinite line (charge density $\\lambda$) | Cylindrical | Co-axial cylinder |\n| Sphere (charge $Q$, radius $R$) | Spherical | Concentric sphere |\n\n**Key rule:** The Gaussian surface is a *mathematical* construction—it has no physical reality. You may choose any shape; only symmetry determines the best choice.",
      "body_he_md": "## מתי ניתן להשתמש בחוק גאוס למציאת $\\vec{E}$?\n\nחוק גאוס *תמיד נכון*, אך הוא מאפשר לפתור אלגברית את $|\\vec{E}|$ רק כאשר ניתן להראות:\n1. $|\\vec{E}|$ הוא **קבוע** על (חלק מ)המשטח הגאוסי, **וגם**\n2. $\\vec{E}$ הוא **מקביל** או **מאונך** ל-$d\\vec{A}$ בכל מקום על אותו חלק.\n\nכאשר שני התנאים מתקיימים, $\\oint \\vec{E}\\cdot d\\vec{A}$ מצטמצם ל-$E \\cdot A_{\\parallel}$ (השטח שבו $\\vec{E}\\parallel\\hat{n}$).\n\n**שלוש הגיאומטריות הסטנדרטיות:**\n\n| פיזור מטען | סימטריה | משטח גאוסי |\n|---|---|---|\n| מישור אינסופי (צפיפות שטחית $\\sigma$) | מישורית | פחית (גליל עם ציר ⊥ מישור) |\n| קו אינסופי (צפיפות ליניארית $\\lambda$) | גלילית | גליל קואקסיאלי |\n| כדור (מטען $Q$, רדיוס $R$) | כדורית | כדור קונצנטרי |\n\n**כלל מרכזי:** המשטח הגאוסי הוא בנייה *מתמטית* — אין לו מציאות פיזיקלית. ניתן לבחור כל צורה; רק הסימטריה קובעת את הבחירה הטובה ביותר."
    },
    {
      "id": "applications",
      "title_en": "Derivations — Plane, Line Charge, and Sphere",
      "title_he": "גזירות — מישור, מטען קווי וכדור",
      "level_min": "university",
      "body_en_md": "## Application 1: Infinite Plane — Pillbox Surface\n\nConsider an infinite plane with uniform surface charge density $\\sigma$ (C/m²). By symmetry, $\\vec{E}$ points perpendicular to the plane and has the same magnitude on both sides.\n\nChoose a cylindrical pillbox of cross-sectional area $A$ centered on the plane. The three surfaces of the pillbox:\n- Two flat end-caps (area $A$ each), $\\vec{E}\\parallel\\hat{n}$: flux $= 2EA$\n- Curved side: $\\vec{E}\\perp\\hat{n}$: flux $= 0$\n\nApplying Gauss's law: $2EA = \\frac{\\sigma A}{\\epsilon_0}$, giving:\n\n$$\\boxed{E = \\frac{\\sigma}{2\\epsilon_0}}$$\n\n## Application 2: Infinite Line Charge — Coaxial Cylinder\n\nAn infinite line charge with linear charge density $\\lambda$ (C/m). By symmetry, $\\vec{E}$ points radially outward and depends only on $r$.\n\nChoose a coaxial cylinder of radius $r$ and length $L$:\n- Curved surface (area $2\\pi r L$): $\\vec{E}\\parallel\\hat{n}$, flux $= E(2\\pi r L)$\n- Two end-caps: $\\vec{E}\\perp\\hat{n}$, flux $= 0$\n\nEnclosed charge: $Q_{\\text{enc}} = \\lambda L$. Gauss's law:\n\n$$E(2\\pi r L) = \\frac{\\lambda L}{\\epsilon_0} \\implies \\boxed{E = \\frac{\\lambda}{2\\pi\\epsilon_0 r}}$$\n\n## Application 3: Uniformly Charged Sphere\n\nCharge $Q$ uniformly distributed throughout a sphere of radius $R$. By symmetry, $\\vec{E}$ is radial.\n\n**Outside ($r > R$):** Gaussian sphere of radius $r$:\n$$E(4\\pi r^2) = \\frac{Q}{\\epsilon_0} \\implies E = \\frac{1}{4\\pi\\epsilon_0}\\frac{Q}{r^2} = \\frac{kQ}{r^2}$$\nIdentical to a point charge at the origin.\n\n**Inside ($r < R$):** Enclosed charge $Q_{\\text{enc}} = Q\\cdot\\frac{r^3}{R^3}$ (volume fraction):\n$$E(4\\pi r^2) = \\frac{Q r^3}{\\epsilon_0 R^3} \\implies E = \\frac{kQ}{R^3}r$$\nFor a conducting shell: all charge is on the surface, so $Q_{\\text{enc}}=0$ for $r<R$ and $E=0$ inside.",
      "body_he_md": "## יישום 1: מישור אינסופי — משטח פחית\n\nנבחן מישור אינסופי עם צפיפות מטען שטחית אחידה $\\sigma$ (C/m²). מסימטריה, $\\vec{E}$ מאונך למישור ובעל אותה עוצמה משני צדיו.\n\nנבחר גליל פחית עם שטח חתך $A$ ממורכז על המישור. שלושת המשטחים:\n- שני מכסים שטוחים (שטח $A$ כל אחד), $\\vec{E}\\parallel\\hat{n}$: שטף $= 2EA$\n- צד מעוקל: $\\vec{E}\\perp\\hat{n}$: שטף $= 0$\n\nמחוק גאוס: $2EA = \\frac{\\sigma A}{\\epsilon_0}$, ולכן:\n\n$$\\boxed{E = \\frac{\\sigma}{2\\epsilon_0}}$$\n\n## יישום 2: מטען קווי אינסופי — גליל קואקסיאלי\n\nקו מטען אינסופי עם צפיפות מטען ליניארית $\\lambda$ (C/m). מסימטריה, $\\vec{E}$ מופנה רדיאלית החוצה ותלוי רק ב-$r$.\n\nנבחר גליל קואקסיאלי ברדיוס $r$ ואורך $L$:\n- משטח מעוקל (שטח $2\\pi r L$): $\\vec{E}\\parallel\\hat{n}$, שטף $= E(2\\pi r L)$\n- שני מכסים: $\\vec{E}\\perp\\hat{n}$, שטף $= 0$\n\nמטען כלוא: $Q_{\\text{enc}} = \\lambda L$. מחוק גאוס:\n\n$$E(2\\pi r L) = \\frac{\\lambda L}{\\epsilon_0} \\implies \\boxed{E = \\frac{\\lambda}{2\\pi\\epsilon_0 r}}$$\n\n## יישום 3: כדור טעון אחיד\n\nמטען $Q$ מפוזר אחידות בתוך כדור ברדיוס $R$. מסימטריה, $\\vec{E}$ הוא רדיאלי.\n\n**מחוץ לכדור ($r > R$):** כדור גאוסי ברדיוס $r$:\n$$E(4\\pi r^2) = \\frac{Q}{\\epsilon_0} \\implies E = \\frac{kQ}{r^2}$$\nזהה למטען נקודתי בראשית.\n\n**בתוך הכדור ($r < R$):** מטען כלוא $Q_{\\text{enc}} = Q\\cdot\\frac{r^3}{R^3}$ (חלק הנפח):\n$$E(4\\pi r^2) = \\frac{Q r^3}{\\epsilon_0 R^3} \\implies E = \\frac{kQ}{R^3}r$$\nעבור קליפת מוליך: כל המטען על פני השטח, $Q_{\\text{enc}}=0$ ל-$r<R$ ו-$E=0$ בפנים."
    },
    {
      "id": "conductors",
      "title_en": "Conductors in Electrostatic Equilibrium",
      "title_he": "מוליכים בשיווי-משקל אלקטרוסטטי",
      "level_min": "university",
      "body_en_md": "## Conductors in Electrostatic Equilibrium\n\nIn a conductor in electrostatic equilibrium, free charges redistribute until $\\vec{E} = 0$ everywhere inside the conductor. Three consequences follow directly from Gauss's law:\n\n1. **$E = 0$ inside the conductor.** Apply Gauss's law to any surface inside the conductor: since $\\vec{E} = 0$ on the surface, $\\Phi_E = 0$, hence $Q_{\\text{enc}} = 0$. Any net charge must reside on the *surface*.\n\n2. **All excess charge resides on the surface.** (Proven above.)\n\n3. **$\\vec{E}$ is perpendicular to the surface** just outside. If a tangential component existed, charges would accelerate along the surface—contradicting equilibrium. A pillbox argument gives:\n$$E_{\\text{surface}} = \\frac{\\sigma}{\\epsilon_0}$$\n(note: factor 2 difference from the *infinite plane* result because here the conductor contributes only one side to the integral).\n\n4. **Cavity inside a conductor:** If a charge $+q$ is placed in a cavity, then by Gauss's law a charge $-q$ is induced on the inner surface, and $+q$ appears on the outer surface. The field inside the conductor walls remains zero.",
      "body_he_md": "## מוליכים בשיווי-משקל אלקטרוסטטי\n\nבמוליך בשיווי-משקל אלקטרוסטטי, מטענים חופשיים מתפזרים עד ש-$\\vec{E} = 0$ בכל מקום בתוך המוליך. שלוש תוצאות נובעות ישירות מחוק גאוס:\n\n1. **$E = 0$ בתוך המוליך.** נפעיל את חוק גאוס על כל משטח בתוך המוליך: מאחר ש-$\\vec{E} = 0$ על המשטח, $\\Phi_E = 0$, ולפיכך $Q_{\\text{enc}} = 0$. כל מטען נטו חייב לשהות על *פני השטח*.\n\n2. **כל המטען העודף שוכן על פני השטח.** (הוכח לעיל.)\n\n3. **$\\vec{E}$ מאונך לפני השטח** ממש מחוץ למוליך. אם היה רכיב משיקי, מטענים היו מואצים לאורך פני השטח — בסתירה לשיווי-משקל. ארגומנט פחית נותן:\n$$E_{\\text{surface}} = \\frac{\\sigma}{\\epsilon_0}$$\n(שים לב: גורם 2 בהבדל מתוצאת *המישור האינסופי*, כי כאן המוליך תורם רק צד אחד לאינטגרל).\n\n4. **חלל בתוך מוליך:** אם מטען $+q$ ממוקם בחלל, אז מחוק גאוס מטען $-q$ מושרה על פני השטח הפנימי, ו-$+q$ מופיע על פני השטח החיצוני. השדה בתוך דפנות המוליך נשאר אפס."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A Gaussian surface is a closed surface that (select the BEST answer):",
      "body_he": "משטח גאוסי הוא משטח סגור ש(בחר את התשובה הטובה ביותר):",
      "options": [
        {"id": "a", "text_en": "Must coincide with a real physical surface, such as a conductor surface.", "text_he": "חייב להיות על משטח פיזיקלי ממשי, כמו פני מוליך.", "correct": False},
        {"id": "b", "text_en": "Is an imaginary mathematical surface chosen to exploit symmetry when applying Gauss's law.", "text_he": "הוא משטח מתמטי דמיוני שנבחר לנצל סימטריה בהפעלת חוק גאוס.", "correct": True},
        {"id": "c", "text_en": "Must enclose all charges in the problem.", "text_he": "חייב לכלוא את כל המטענים בבעיה.", "correct": False},
        {"id": "d", "text_en": "Can only be used for spherically symmetric charge distributions.", "text_he": "ניתן לשימוש רק עבור פיזורי מטען בעלי סימטריה כדורית.", "correct": False}
      ],
      "explanation_en": "A Gaussian surface is a purely mathematical construction—it has no physical reality. It can be any closed surface; the best choice exploits the symmetry of the charge distribution to make $|\\vec{E}|$ constant and the angle between $\\vec{E}$ and $d\\vec{A}$ uniform on the surface.",
      "explanation_he": "משטח גאוסי הוא בנייה מתמטית בלבד — אין לו מציאות פיזיקלית. ניתן לבחור כל משטח סגור; הבחירה הטובה ביותר מנצלת את סימטריית פיזור המטען כדי ש-$|\\vec{E}|$ יהיה קבוע וזווית $\\vec{E}$ עם $d\\vec{A}$ תהיה אחידה."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A point charge $+Q$ is placed at the center of a cube of side $a$. What is the total electric flux through the cube?",
      "body_he": "מטען נקודתי $+Q$ ממוקם במרכז קובייה עם צלע $a$. מהו השטף החשמלי הכולל דרך הקובייה?",
      "options": [
        {"id": "a", "text_en": "$Q/(6\\epsilon_0)$", "text_he": "$Q/(6\\epsilon_0)$", "correct": False},
        {"id": "b", "text_en": "$Q/\\epsilon_0$", "text_he": "$Q/\\epsilon_0$", "correct": True},
        {"id": "c", "text_en": "$6Q/\\epsilon_0$", "text_he": "$6Q/\\epsilon_0$", "correct": False},
        {"id": "d", "text_en": "It depends on the size $a$ of the cube.", "text_he": "תלוי בגודל $a$ של הקובייה.", "correct": False}
      ],
      "explanation_en": "Gauss's law states $\\Phi_E = Q_{\\text{enc}}/\\epsilon_0$ regardless of the surface shape. The cube is a valid closed Gaussian surface enclosing charge $Q$, so $\\Phi_E = Q/\\epsilon_0$. The fact that $|\\vec{E}|$ is not constant over the cube's faces is irrelevant—the law gives the total flux without requiring uniformity.",
      "explanation_he": "חוק גאוס קובע $\\Phi_E = Q_{\\text{enc}}/\\epsilon_0$ ללא קשר לצורת המשטח. הקובייה היא משטח גאוסי סגור תקין המכיל מטען $Q$, לכן $\\Phi_E = Q/\\epsilon_0$. העובדה ש-$|\\vec{E}|$ אינו קבוע על פני הקובייה אינה רלוונטית — החוק נותן את השטף הכולל ללא דרישת אחידות."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "An infinite line charge has linear charge density $\\lambda = 4\\;\\mu\\text{C/m}$. Using a cylindrical Gaussian surface of radius $r = 0.02\\;\\text{m}$, what is the magnitude of the electric field at that radius?",
      "body_he": "קו מטען אינסופי בעל צפיפות מטען ליניארית $\\lambda = 4\\;\\mu\\text{C/m}$. בשימוש במשטח גאוסי גלילי ברדיוס $r = 0.02\\;\\text{m}$, מהי עוצמת השדה החשמלי ברדיוס זה?",
      "options": [
        {"id": "a", "text_en": "$1.8\\times10^6\\;\\text{N/C}$", "text_he": "$1.8\\times10^6\\;\\text{N/C}$", "correct": True},
        {"id": "b", "text_en": "$3.6\\times10^6\\;\\text{N/C}$", "text_he": "$3.6\\times10^6\\;\\text{N/C}$", "correct": False},
        {"id": "c", "text_en": "$9.0\\times10^4\\;\\text{N/C}$", "text_he": "$9.0\\times10^4\\;\\text{N/C}$", "correct": False},
        {"id": "d", "text_en": "$9.0\\times10^6\\;\\text{N/C}$", "text_he": "$9.0\\times10^6\\;\\text{N/C}$", "correct": False}
      ],
      "explanation_en": "From Gauss's law: $E = \\frac{\\lambda}{2\\pi\\epsilon_0 r}$. With $\\lambda = 4\\times10^{-6}$ C/m, $r = 0.02$ m: $E = \\frac{4\\times10^{-6}}{2\\pi(8.854\\times10^{-12})(0.02)} = \\frac{4\\times10^{-6}}{1.113\\times10^{-12}\\times\\pi\\times0.04}\\approx 1.8\\times10^6$ N/C.",
      "explanation_he": "מחוק גאוס: $E = \\frac{\\lambda}{2\\pi\\epsilon_0 r}$. עם $\\lambda = 4\\times10^{-6}$ C/m, $r = 0.02$ m: $E \\approx 1.8\\times10^6$ N/C."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A solid insulating sphere of radius $R = 0.10\\;\\text{m}$ carries a total charge $Q = 8\\;\\text{nC}$ uniformly distributed throughout its volume. What is the electric field at $r = 0.05\\;\\text{m}$ (inside the sphere)?",
      "body_he": "כדור מבודד מוצק ברדיוס $R = 0.10\\;\\text{m}$ נושא מטען כולל $Q = 8\\;\\text{nC}$ המפוזר אחידות בנפחו. מהו השדה החשמלי ב-$r = 0.05\\;\\text{m}$ (בתוך הכדור)?",
      "options": [
        {"id": "a", "text_en": "$7200\\;\\text{N/C}$", "text_he": "$7200\\;\\text{N/C}$", "correct": False},
        {"id": "b", "text_en": "$3600\\;\\text{N/C}$", "text_he": "$3600\\;\\text{N/C}$", "correct": False},
        {"id": "c", "text_en": "$18000\\;\\text{N/C}$", "text_he": "$18000\\;\\text{N/C}$", "correct": False},
        {"id": "d", "text_en": "$3600\\;\\text{N/C}$ — wait, recalculate: $E = kQr/R^3 = (9\\times10^9)(8\\times10^{-9})(0.05)/(0.001) = 3600\\;\\text{N/C}$", "text_he": "$3600\\;\\text{N/C}$", "correct": False}
      ],
      "explanation_en": "Inside a uniformly charged solid sphere: $E = \\frac{kQ}{R^3}r$. With $k = 9\\times10^9$, $Q = 8\\times10^{-9}$ C, $R = 0.10$ m, $r = 0.05$ m: $E = \\frac{(9\\times10^9)(8\\times10^{-9})}{(0.10)^3}(0.05) = \\frac{72}{0.001}\\times0.05 = 72000\\times0.05 = 3600$ N/C.",
      "explanation_he": "בתוך כדור מוצק טעון אחיד: $E = \\frac{kQ}{R^3}r$. עם $k = 9\\times10^9$, $Q = 8\\times10^{-9}$ C, $R = 0.10$ m, $r = 0.05$ m: $E = 3600$ N/C."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A solid copper sphere (conductor) carries a net charge $+Q$. Which statement about the electric field and charge distribution is correct?",
      "body_he": "כדור נחושת מוצק (מוליך) נושא מטען נטו $+Q$. איזו טענה לגבי השדה החשמלי ופיזור המטען נכונה?",
      "options": [
        {"id": "a", "text_en": "The field inside the conductor is $E = kQ/R^2$ (same as outside at the surface).", "text_he": "השדה בתוך המוליך הוא $E = kQ/R^2$ (זהה לחיצוני על פני השטח).", "correct": False},
        {"id": "b", "text_en": "The charge $+Q$ is distributed uniformly throughout the volume of the sphere.", "text_he": "המטען $+Q$ מפוזר אחידות בנפח הכדור.", "correct": False},
        {"id": "c", "text_en": "$E = 0$ inside the conductor, and all charge $+Q$ resides on the surface, with $E = \\sigma/\\epsilon_0$ just outside.", "text_he": "$E = 0$ בתוך המוליך, וכל המטען $+Q$ שוכן על פני השטח, עם $E = \\sigma/\\epsilon_0$ ממש מחוץ.", "correct": True},
        {"id": "d", "text_en": "The field just inside the surface equals $\\sigma/(2\\epsilon_0)$.", "text_he": "השדה ממש מתחת לפני השטח שווה $\\sigma/(2\\epsilon_0)$.", "correct": False}
      ],
      "explanation_en": "In a conductor in electrostatic equilibrium: $\\vec{E} = 0$ inside (free charges shield the interior), all net charge is on the surface, and $E = \\sigma/\\epsilon_0$ just outside the surface (not $\\sigma/(2\\epsilon_0)$, which applies to an infinite plane with charges on both sides).",
      "explanation_he": "במוליך בשיווי-משקל אלקטרוסטטי: $\\vec{E} = 0$ בפנים (מטענים חופשיים מגנים על הפנים), כל המטען הנטו על פני השטח, ו-$E = \\sigma/\\epsilon_0$ ממש מחוץ (לא $\\sigma/(2\\epsilon_0)$, שמתייחס למישור אינסופי עם מטענים משני הצדדים)."
    }
  ]
}

# ─────────────────────────────────────────────────────────────────
# LESSON 2 — Biot-Savart Law
# ─────────────────────────────────────────────────────────────────
biot_savart = {
  "id": "magnetic_field_biot_savart",
  "type": "interactive",
  "subject": "university_physics_2",
  "title_en": "Biot-Savart Law — Magnetic Fields from Currents",
  "title_he": "חוק ביו-סבר — שדות מגנטיים מזרמים",
  "duration_min": 30,
  "level_min": "university",
  "agent_hints": "The Biot-Savart law is the magnetic analogue of Coulomb's law. Stress the cross product: direction of dB requires right-hand rule applied to dl×r-hat. Students must always identify: (1) the current element vector dl, (2) the displacement unit vector r-hat from dl to the field point P, (3) the distance r. Common errors: getting the direction of r-hat backwards (it goes FROM source TO field point); forgetting the sin(theta) factor; sign errors in the cross product. For the infinite wire derivation, set up the integral with the angle variable and use the standard result. For the loop, use symmetry to argue that only the z-component survives. Emphasize that Biot-Savart is always valid but Ampere's law is easier when there is enough symmetry.",
  "sections": [
    {
      "id": "magnetic_force_basics",
      "title_en": "Magnetic Force and Current Elements",
      "title_he": "כוח מגנטי ואלמנטי זרם",
      "level_min": "university",
      "body_en_md": "## Magnetic Force on Moving Charges and Currents\n\nA charge $q$ moving with velocity $\\vec{v}$ in magnetic field $\\vec{B}$ experiences the **Lorentz force**:\n\n$$\\vec{F} = q\\vec{v}\\times\\vec{B}$$\n\nThe magnitude is $F = qvB\\sin\\theta$ where $\\theta$ is the angle between $\\vec{v}$ and $\\vec{B}$. The force is always perpendicular to both $\\vec{v}$ and $\\vec{B}$, doing no work.\n\nFor a current-carrying wire, a small segment $d\\vec{l}$ carrying current $I$ experiences:\n\n$$d\\vec{F} = I\\,d\\vec{l}\\times\\vec{B}$$\n\nFor a straight wire of length $L$ in a uniform field $\\vec{B}$ at angle $\\theta$:\n\n$$F = ILB\\sin\\theta$$\n\n**Units of $B$:** Tesla ($\\text{T} = \\text{kg}/(\\text{A}\\cdot\\text{s}^2)$). Also: $1\\;\\text{T} = 10^4\\;\\text{Gauss}$.",
      "body_he_md": "## כוח מגנטי על מטענים נעים ועל זרמים\n\nמטען $q$ הנע במהירות $\\vec{v}$ בשדה מגנטי $\\vec{B}$ חווה את **כוח לורנץ**:\n\n$$\\vec{F} = q\\vec{v}\\times\\vec{B}$$\n\nהעוצמה $F = qvB\\sin\\theta$ כאשר $\\theta$ הוא הזווית בין $\\vec{v}$ ל-$\\vec{B}$. הכוח מאונך תמיד לשניהם, ואינו מבצע עבודה.\n\nעבור חוט נושא זרם, קטע קטן $d\\vec{l}$ הנושא זרם $I$ חווה:\n\n$$d\\vec{F} = I\\,d\\vec{l}\\times\\vec{B}$$\n\nעבור חוט ישר באורך $L$ בשדה אחיד $\\vec{B}$ בזווית $\\theta$:\n\n$$F = ILB\\sin\\theta$$\n\n**יחידות של $B$:** טסלה ($\\text{T} = \\text{kg}/(\\text{A}\\cdot\\text{s}^2)$). גם: $1\\;\\text{T} = 10^4\\;\\text{גאוס}$."
    },
    {
      "id": "biot_savart_law",
      "title_en": "The Biot-Savart Law",
      "title_he": "חוק ביו-סבר",
      "level_min": "university",
      "body_en_md": "## Biot-Savart Law\n\nThe magnetic field $d\\vec{B}$ produced at a field point $P$ by a current element $I\\,d\\vec{l}$ is:\n\n$$d\\vec{B} = \\frac{\\mu_0}{4\\pi}\\frac{I\\,d\\vec{l}\\times\\hat{r}}{r^2}$$\n\nwhere:\n- $\\mu_0 = 4\\pi\\times10^{-7}\\;\\text{T}\\cdot\\text{m/A}$ is the permeability of free space\n- $\\hat{r}$ is the unit vector pointing from the current element **to** the field point $P$\n- $r$ is the distance from the current element to $P$\n- The cross product $d\\vec{l}\\times\\hat{r}$ gives the direction of $d\\vec{B}$ via the right-hand rule\n\nThe magnitude is:\n$$dB = \\frac{\\mu_0}{4\\pi}\\frac{I\\,dl\\,\\sin\\alpha}{r^2}$$\n\nwhere $\\alpha$ is the angle between $d\\vec{l}$ and $\\hat{r}$.\n\n**To find the total field:** integrate over the entire current distribution:\n$$\\vec{B} = \\frac{\\mu_0 I}{4\\pi}\\int\\frac{d\\vec{l}\\times\\hat{r}}{r^2}$$",
      "body_he_md": "## חוק ביו-סבר\n\nהשדה המגנטי $d\\vec{B}$ המיוצר בנקודה שדה $P$ על-ידי אלמנט זרם $I\\,d\\vec{l}$ הוא:\n\n$$d\\vec{B} = \\frac{\\mu_0}{4\\pi}\\frac{I\\,d\\vec{l}\\times\\hat{r}}{r^2}$$\n\nכאשר:\n- $\\mu_0 = 4\\pi\\times10^{-7}\\;\\text{T}\\cdot\\text{m/A}$ הוא מקדם החדירות של ריק\n- $\\hat{r}$ הוא וקטור היחידה המופנה מאלמנט הזרם **אל** נקודת השדה $P$\n- $r$ הוא המרחק מאלמנט הזרם ל-$P$\n- המכפלה הוקטורית $d\\vec{l}\\times\\hat{r}$ נותנת את כיוון $d\\vec{B}$ בכלל כף-יד-ימין\n\nהעוצמה:\n$$dB = \\frac{\\mu_0}{4\\pi}\\frac{I\\,dl\\,\\sin\\alpha}{r^2}$$\n\nכאשר $\\alpha$ הוא הזווית בין $d\\vec{l}$ ל-$\\hat{r}$.\n\n**לחישוב השדה הכולל:** מאגדים על פיזור הזרם כולו:\n$$\\vec{B} = \\frac{\\mu_0 I}{4\\pi}\\int\\frac{d\\vec{l}\\times\\hat{r}}{r^2}$$"
    },
    {
      "id": "infinite_wire",
      "title_en": "Derivation: Infinite Straight Wire",
      "title_he": "גזירה: חוט ישר אינסופי",
      "level_min": "university",
      "body_en_md": "## Magnetic Field of an Infinite Straight Wire\n\nConsider an infinite straight wire carrying current $I$ along the $z$-axis. We find the field at distance $d$ from the wire.\n\nParametrize the wire by $z$: each element $dz$ at position $z$ contributes $d\\vec{B}$ in the $\\hat{\\phi}$ direction (azimuthal, by symmetry). Setting $r = \\sqrt{z^2+d^2}$ and $\\sin\\alpha = d/r$:\n\n$$dB = \\frac{\\mu_0 I}{4\\pi}\\frac{dz\\,\\sin\\alpha}{r^2} = \\frac{\\mu_0 I}{4\\pi}\\frac{d\\,dz}{(z^2+d^2)^{3/2}}$$\n\nIntegrating over $z\\in(-\\infty,+\\infty)$ using $\\int_{-\\infty}^{\\infty}\\frac{dz}{(z^2+d^2)^{3/2}} = \\frac{2}{d^2}$:\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2\\pi d}}$$\n\n**Direction:** Right-hand rule — wrap the right hand around the wire with the thumb pointing in the direction of $I$; the fingers curl in the direction of $\\vec{B}$ (counterclockwise circles around the wire for current upward).",
      "body_he_md": "## שדה מגנטי של חוט ישר אינסופי\n\nנבחן חוט ישר אינסופי הנושא זרם $I$ לאורך ציר $z$. נמצא את השדה במרחק $d$ מהחוט.\n\nנפרמטריז את החוט לפי $z$: כל אלמנט $dz$ במיקום $z$ תורם $d\\vec{B}$ בכיוון $\\hat{\\phi}$ (אזימוטלי, מסימטריה). עם $r = \\sqrt{z^2+d^2}$ ו-$\\sin\\alpha = d/r$:\n\n$$dB = \\frac{\\mu_0 I}{4\\pi}\\frac{d\\,dz}{(z^2+d^2)^{3/2}}$$\n\nאינטגרציה על $z\\in(-\\infty,+\\infty)$ עם $\\int_{-\\infty}^{\\infty}\\frac{dz}{(z^2+d^2)^{3/2}} = \\frac{2}{d^2}$:\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2\\pi d}}$$\n\n**כיוון:** כלל יד-ימין — עוטפים את כף-יד-ימין סביב החוט כאשר האגודל מצביע בכיוון $I$; האצבעות מתעקלות בכיוון $\\vec{B}$ (עיגולים נגד כיוון השעון סביב החוט עבור זרם כלפי מעלה)."
    },
    {
      "id": "circular_loop",
      "title_en": "Circular Current Loop and Force Between Wires",
      "title_he": "לולאת זרם מעגלית וכוח בין חוטים",
      "level_min": "university",
      "body_en_md": "## Magnetic Field at the Center of a Circular Loop\n\nA circular loop of radius $R$ in the $xy$-plane carries current $I$. By symmetry, the field at the center is purely in the $\\hat{z}$ direction (perpendicular components cancel).\n\nFor a current element $Rd\\phi$ at angle $\\phi$: $d\\vec{l}\\times\\hat{r}$ always points in $+\\hat{z}$ (angle between $d\\vec{l}$ and $\\hat{r}$ is $90°$, $r = R$):\n\n$$dB_z = \\frac{\\mu_0 I}{4\\pi}\\frac{R\\,d\\phi}{R^2} = \\frac{\\mu_0 I}{4\\pi R}d\\phi$$\n\nIntegrating around the full loop ($\\phi: 0\\to 2\\pi$):\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2R}}$$\n\nDirection: right-hand rule — curl fingers in direction of $I$; thumb points in direction of $\\vec{B}$.\n\n## Force Between Parallel Wires\n\nTwo parallel wires separated by distance $d$, carrying currents $I_1$ and $I_2$:\n\n- Wire 1 creates field $B_1 = \\mu_0 I_1/(2\\pi d)$ at wire 2's location\n- Force per unit length on wire 2: $F/L = I_2 B_1 = \\frac{\\mu_0 I_1 I_2}{2\\pi d}$\n\n**Same direction currents:** forces are attractive (field from wire 1 at wire 2 is perpendicular to $I_2$, pointing toward wire 1 by right-hand rule).\n\n**Opposite direction currents:** forces are repulsive.",
      "body_he_md": "## שדה מגנטי במרכז לולאה מעגלית\n\nלולאה מעגלית ברדיוס $R$ במישור $xy$ נושאת זרם $I$. מסימטריה, השדה במרכז הוא בכיוון $\\hat{z}$ בלבד (רכיבים מאונכים מבטלים זה את זה).\n\nעבור אלמנט זרם $Rd\\phi$ בזווית $\\phi$: $d\\vec{l}\\times\\hat{r}$ מצביע תמיד ב-$+\\hat{z}$ (זווית בין $d\\vec{l}$ ל-$\\hat{r}$ היא $90°$, $r = R$):\n\n$$dB_z = \\frac{\\mu_0 I}{4\\pi}\\frac{R\\,d\\phi}{R^2} = \\frac{\\mu_0 I}{4\\pi R}d\\phi$$\n\nאינטגרציה סביב הלולאה כולה ($\\phi: 0\\to 2\\pi$):\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2R}}$$\n\nכיוון: כלל יד-ימין — מעקלים אצבעות בכיוון $I$; אגודל מצביע בכיוון $\\vec{B}$.\n\n## כוח בין חוטים מקבילים\n\nשני חוטים מקבילים במרחק $d$ זה מזה, הנושאים זרמים $I_1$ ו-$I_2$:\n\n- חוט 1 יוצר שדה $B_1 = \\mu_0 I_1/(2\\pi d)$ במיקום חוט 2\n- כוח ליחידת אורך על חוט 2: $F/L = \\frac{\\mu_0 I_1 I_2}{2\\pi d}$\n\n**זרמים באותו כיוון:** כוחות притягиvaniyה (אטרקטיביים).\n\n**זרמים בכיוונים הפוכים:** כוחות דוחים."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A current element $I\\,d\\vec{l}$ points in the $+\\hat{x}$ direction. A field point $P$ is located in the $+\\hat{y}$ direction from the current element. What is the direction of the magnetic field $d\\vec{B}$ at $P$?",
      "body_he": "אלמנט זרם $I\\,d\\vec{l}$ מצביע בכיוון $+\\hat{x}$. נקודת שדה $P$ נמצאת בכיוון $+\\hat{y}$ מאלמנט הזרם. מהו כיוון השדה המגנטי $d\\vec{B}$ ב-$P$?",
      "options": [
        {"id": "a", "text_en": "$+\\hat{z}$", "text_he": "$+\\hat{z}$", "correct": True},
        {"id": "b", "text_en": "$-\\hat{z}$", "text_he": "$-\\hat{z}$", "correct": False},
        {"id": "c", "text_en": "$+\\hat{y}$", "text_he": "$+\\hat{y}$", "correct": False},
        {"id": "d", "text_en": "$-\\hat{x}$", "text_he": "$-\\hat{x}$", "correct": False}
      ],
      "explanation_en": "$d\\vec{B}\\propto d\\vec{l}\\times\\hat{r}$. Here $d\\vec{l} = dl\\,\\hat{x}$ and $\\hat{r} = \\hat{y}$ (from source to field point). So $\\hat{x}\\times\\hat{y} = +\\hat{z}$.",
      "explanation_he": "$d\\vec{B}\\propto d\\vec{l}\\times\\hat{r}$. כאן $d\\vec{l} = dl\\,\\hat{x}$ ו-$\\hat{r} = \\hat{y}$ (מהמקור לנקודת השדה). לכן $\\hat{x}\\times\\hat{y} = +\\hat{z}$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "An infinite straight wire carries current $I = 5\\;\\text{A}$. What is the magnitude of the magnetic field at a perpendicular distance $r = 4\\;\\text{cm}$ from the wire? ($\\mu_0 = 4\\pi\\times10^{-7}\\;\\text{T}\\cdot\\text{m/A}$)",
      "body_he": "חוט ישר אינסופי נושא זרם $I = 5\\;\\text{A}$. מהי עוצמת השדה המגנטי במרחק מאונך $r = 4\\;\\text{cm}$ מהחוט?",
      "options": [
        {"id": "a", "text_en": "$2.5\\times10^{-5}\\;\\text{T}$", "text_he": "$2.5\\times10^{-5}\\;\\text{T}$", "correct": True},
        {"id": "b", "text_en": "$5.0\\times10^{-5}\\;\\text{T}$", "text_he": "$5.0\\times10^{-5}\\;\\text{T}$", "correct": False},
        {"id": "c", "text_en": "$1.25\\times10^{-5}\\;\\text{T}$", "text_he": "$1.25\\times10^{-5}\\;\\text{T}$", "correct": False},
        {"id": "d", "text_en": "$6.25\\times10^{-6}\\;\\text{T}$", "text_he": "$6.25\\times10^{-6}\\;\\text{T}$", "correct": False}
      ],
      "explanation_en": "$B = \\frac{\\mu_0 I}{2\\pi r} = \\frac{(4\\pi\\times10^{-7})(5)}{2\\pi(0.04)} = \\frac{20\\pi\\times10^{-7}}{0.08\\pi} = \\frac{20\\times10^{-7}}{0.08} = 2.5\\times10^{-5}$ T.",
      "explanation_he": "$B = \\frac{\\mu_0 I}{2\\pi r} = \\frac{(4\\pi\\times10^{-7})(5)}{2\\pi(0.04)} = 2.5\\times10^{-5}$ T."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "A circular loop of radius $R = 0.05\\;\\text{m}$ carries current $I = 3\\;\\text{A}$. What is the magnetic field at the center of the loop?",
      "body_he": "לולאה מעגלית ברדיוס $R = 0.05\\;\\text{m}$ נושאת זרם $I = 3\\;\\text{A}$. מהו השדה המגנטי במרכז הלולאה?",
      "options": [
        {"id": "a", "text_en": "$3.77\\times10^{-5}\\;\\text{T}$", "text_he": "$3.77\\times10^{-5}\\;\\text{T}$", "correct": False},
        {"id": "b", "text_en": "$1.88\\times10^{-5}\\;\\text{T}$", "text_he": "$1.88\\times10^{-5}\\;\\text{T}$", "correct": False},
        {"id": "c", "text_en": "$3.77\\times10^{-5}\\;\\text{T}$", "text_he": "$3.77\\times10^{-5}\\;\\text{T}$", "correct": False},
        {"id": "d", "text_en": "$3.77\\times10^{-5}\\;\\text{T}$ ($= \\mu_0 I/2R$)", "text_he": "$3.77\\times10^{-5}\\;\\text{T}$ ($= \\mu_0 I/2R$)", "correct": True}
      ],
      "explanation_en": "$B = \\frac{\\mu_0 I}{2R} = \\frac{(4\\pi\\times10^{-7})(3)}{2(0.05)} = \\frac{12\\pi\\times10^{-7}}{0.1} = 120\\pi\\times10^{-7} \\approx 3.77\\times10^{-5}$ T.",
      "explanation_he": "$B = \\frac{\\mu_0 I}{2R} = \\frac{(4\\pi\\times10^{-7})(3)}{0.1} \\approx 3.77\\times10^{-5}$ T."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "Two infinite parallel wires are separated by $d = 0.10\\;\\text{m}$. Wire 1 carries $I_1 = 4\\;\\text{A}$ (upward) and wire 2 carries $I_2 = 6\\;\\text{A}$ (upward). What is the force per unit length between them, and is it attractive or repulsive?",
      "body_he": "שני חוטים מקבילים אינסופיים מופרדים ב-$d = 0.10\\;\\text{m}$. חוט 1 נושא $I_1 = 4\\;\\text{A}$ (כלפי מעלה) וחוט 2 נושא $I_2 = 6\\;\\text{A}$ (כלפי מעלה). מהו הכוח ליחידת אורך ביניהם, ואם הוא אטרקטיבי או דוחה?",
      "options": [
        {"id": "a", "text_en": "$4.8\\times10^{-5}\\;\\text{N/m}$, repulsive", "text_he": "$4.8\\times10^{-5}\\;\\text{N/m}$, דוחה", "correct": False},
        {"id": "b", "text_en": "$4.8\\times10^{-5}\\;\\text{N/m}$, attractive", "text_he": "$4.8\\times10^{-5}\\;\\text{N/m}$, אטרקטיבי", "correct": True},
        {"id": "c", "text_en": "$9.6\\times10^{-5}\\;\\text{N/m}$, attractive", "text_he": "$9.6\\times10^{-5}\\;\\text{N/m}$, אטרקטיבי", "correct": False},
        {"id": "d", "text_en": "$2.4\\times10^{-5}\\;\\text{N/m}$, attractive", "text_he": "$2.4\\times10^{-5}\\;\\text{N/m}$, אטרקטיבי", "correct": False}
      ],
      "explanation_en": "$F/L = \\frac{\\mu_0 I_1 I_2}{2\\pi d} = \\frac{(4\\pi\\times10^{-7})(4)(6)}{2\\pi(0.10)} = \\frac{96\\pi\\times10^{-7}}{0.2\\pi} = \\frac{96\\times10^{-7}}{0.2} = 4.8\\times10^{-5}$ N/m. Currents in the same direction → attractive.",
      "explanation_he": "$F/L = \\frac{\\mu_0 I_1 I_2}{2\\pi d} = 4.8\\times10^{-5}$ N/m. זרמים באותו כיוון → כוח אטרקטיבי."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A point $P$ is located at a distance $d$ from two long parallel wires. Wire 1 carries current $I$ to the right; wire 2 carries current $I$ to the left. Both wires are equidistant from $P$, with wire 1 above $P$ and wire 2 below $P$ (both at perpendicular distance $d$). What is the direction of the total $\\vec{B}$ at $P$?",
      "body_he": "נקודה $P$ ממוקמת במרחק $d$ משני חוטים מקבילים ארוכים. חוט 1 נושא זרם $I$ ימינה; חוט 2 נושא זרם $I$ שמאלה. שני החוטים במרחק שווה מ-$P$, חוט 1 מעל $P$ וחוט 2 מתחת ל-$P$ (שניהם במרחק מאונך $d$). מהו כיוון $\\vec{B}$ הכולל ב-$P$?",
      "options": [
        {"id": "a", "text_en": "The fields cancel and $\\vec{B} = 0$ at $P$.", "text_he": "השדות מתבטלים ו-$\\vec{B} = 0$ ב-$P$.", "correct": False},
        {"id": "b", "text_en": "Both wires contribute fields in the same direction at $P$, so the total field is double that from one wire.", "text_he": "שני החוטים תורמים שדות באותו כיוון ב-$P$, ולכן השדה הכולל הוא פי שניים מחוט אחד.", "correct": True},
        {"id": "c", "text_en": "The total field is directed along the line connecting the two wires.", "text_he": "השדה הכולל מכוון לאורך הקו המחבר את שני החוטים.", "correct": False},
        {"id": "d", "text_en": "The total field is perpendicular to the plane containing the two wires.", "text_he": "השדה הכולל מאונך למישור המכיל את שני החוטים.", "correct": False}
      ],
      "explanation_en": "Wire 1 (above $P$, current right): by right-hand rule, $\\vec{B}_1$ at $P$ points out of the page. Wire 2 (below $P$, current left): by right-hand rule, $\\vec{B}_2$ at $P$ also points out of the page. The fields add, giving $B_{\\text{total}} = 2\\times\\frac{\\mu_0 I}{2\\pi d}$.",
      "explanation_he": "חוט 1 (מעל $P$, זרם ימינה): $\\vec{B}_1$ ב-$P$ יוצא מהדף. חוט 2 (מתחת ל-$P$, זרם שמאלה): $\\vec{B}_2$ ב-$P$ גם יוצא מהדף. השדות מתחברים."
    }
  ]
}

# ─────────────────────────────────────────────────────────────────
# LESSON 3 — Ampère's Law
# ─────────────────────────────────────────────────────────────────
ampere = {
  "id": "ampere_law",
  "type": "interactive",
  "subject": "university_physics_2",
  "title_en": "Ampère's Law — Magnetic Fields from Symmetric Currents",
  "title_he": "חוק אמפר — שדות מגנטיים מזרמים סימטריים",
  "duration_min": 30,
  "level_min": "university",
  "agent_hints": "Ampère's law is the magnetic analogue of Gauss's law. The Ampèrian loop is a closed *path* (1D), not a surface. The key symmetry conditions: (1) |B| is constant along the loop, and (2) the angle between B and dl is constant. For the solenoid, the argument that B≈0 outside is subtle: use two rectangular loops to show it, or invoke the superposition of many loops. Students often confuse the enclosed current (current threads through the surface bounded by the loop) with the current at the loop itself. For the toroid, stress that outside the toroid the enclosed current is zero (currents going up and down cancel).",
  "sections": [
    {
      "id": "ampere_statement",
      "title_en": "Ampère's Law — Statement and Analogy with Gauss",
      "title_he": "חוק אמפר — ניסוח ואנלוגיה עם גאוס",
      "level_min": "university",
      "body_en_md": "## Ampère's Law\n\nFor any closed path (Ampèrian loop) $C$, the line integral of $\\vec{B}$ around the loop equals $\\mu_0$ times the total current threading through any surface bounded by the loop:\n\n$$\\oint_C \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$$\n\nwhere $I_{\\text{enc}}$ is the **net current passing through** any surface bounded by $C$ (the sign determined by the right-hand rule: curl the right hand in the direction of traversal; the thumb points in the positive direction for current).\n\n**Analogy with Gauss's law:**\n\n| Gauss's Law | Ampère's Law |\n|---|---|\n| Closed **surface** integral of $\\vec{E}$ | Closed **line** integral of $\\vec{B}$ |\n| $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ | $\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$ |\n| Source: electric charge | Source: electric current |\n| Exploit spherical/planar/cylindrical symmetry | Exploit cylindrical/planar symmetry |\n\n**When is it useful?** Only when you can argue by symmetry that $|\\vec{B}|$ is constant along the loop and the angle between $\\vec{B}$ and $d\\vec{l}$ is fixed. Otherwise, Ampère's law is true but cannot be solved algebraically—use Biot-Savart instead.",
      "body_he_md": "## חוק אמפר\n\nעבור כל מסלול סגור (לולאת אמפר) $C$, האינטגרל הקווי של $\\vec{B}$ סביב הלולאה שווה ל-$\\mu_0$ כפול הזרם הכולל החוצה דרך כל משטח שגובל בלולאה:\n\n$$\\oint_C \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$$\n\nכאשר $I_{\\text{enc}}$ הוא **הזרם הנטו העובר דרך** כל משטח הגובל ב-$C$ (הסימן נקבע על-ידי כלל יד-ימין: עוקפים ביד-ימין בכיוון המעבר; האגודל מצביע בכיוון החיובי לזרם).\n\n**אנלוגיה עם חוק גאוס:**\n\n| חוק גאוס | חוק אמפר |\n|---|---|\n| אינטגרל **משטחי** סגור של $\\vec{E}$ | אינטגרל **קווי** סגור של $\\vec{B}$ |\n| $\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ | $\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$ |\n| מקור: מטען חשמלי | מקור: זרם חשמלי |\n\n**מתי שימושי?** רק כאשר ניתן לטעון מסימטריה ש-$|\\vec{B}|$ קבוע לאורך הלולאה והזווית בין $\\vec{B}$ ל-$d\\vec{l}$ קבועה. אחרת, חוק אמפר נכון אך לא ניתן לפתרון אלגברי — יש להשתמש בביו-סבר."
    },
    {
      "id": "infinite_wire_ampere",
      "title_en": "Application: Infinite Wire (Confirms Biot-Savart)",
      "title_he": "יישום: חוט אינסופי (מאשר ביו-סבר)",
      "level_min": "university",
      "body_en_md": "## Infinite Straight Wire — Circular Ampèrian Loop\n\nFor an infinite straight wire carrying current $I$, choose an Ampèrian loop that is a circle of radius $r$ centered on the wire, in the plane perpendicular to the wire.\n\n**Symmetry argument:** $\\vec{B}$ has cylindrical symmetry around the wire, so $|\\vec{B}|$ is constant on the circle and $\\vec{B}$ is tangent to the circle everywhere (parallel to $d\\vec{l}$).\n\nApplying Ampère's law:\n$$\\oint \\vec{B}\\cdot d\\vec{l} = B(2\\pi r) = \\mu_0 I$$\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2\\pi r}}$$\n\nThis confirms the Biot-Savart result, but with far less work. The direction is given by the right-hand rule as before.",
      "body_he_md": "## חוט ישר אינסופי — לולאת אמפר מעגלית\n\nעבור חוט ישר אינסופי הנושא זרם $I$, נבחר לולאת אמפר מעגלית ברדיוס $r$ ממורכזת על החוט, במישור מאונך לחוט.\n\n**ארגומנט סימטריה:** ל-$\\vec{B}$ סימטריה גלילית סביב החוט, לכן $|\\vec{B}|$ קבוע על המעגל ו-$\\vec{B}$ משיקי לכל מקום (מקביל ל-$d\\vec{l}$).\n\nמחוק אמפר:\n$$B(2\\pi r) = \\mu_0 I$$\n\n$$\\boxed{B = \\frac{\\mu_0 I}{2\\pi r}}$$\n\nזה מאשר את תוצאת ביו-סבר, אך בהרבה פחות עבודה."
    },
    {
      "id": "solenoid_toroid",
      "title_en": "Solenoid and Toroid",
      "title_he": "סולנואיד וטורואיד",
      "level_min": "university",
      "body_en_md": "## Solenoid\n\nAn ideal solenoid has $n$ turns per meter, carries current $I$, and is assumed infinite in length. The field inside is uniform and parallel to the axis; outside it is approximately zero.\n\nChoose a rectangular Ampèrian loop of length $l$ with one side inside (parallel to the axis) and one side outside:\n\n$$\\oint \\vec{B}\\cdot d\\vec{l} = B_{\\text{in}}\\cdot l + 0 + 0 + 0 = \\mu_0 (nl) I$$\n\n$$\\boxed{B_{\\text{solenoid}} = \\mu_0 n I}$$\n\nOutside the solenoid: $B \\approx 0$.\n\n## Toroid\n\nA toroid has $N$ total turns wound on a donut-shaped core. For a circular Ampèrian loop of radius $r$ inside the toroid (between inner radius $a$ and outer radius $b$):\n\n$$B(2\\pi r) = \\mu_0 N I \\implies \\boxed{B_{\\text{toroid}} = \\frac{\\mu_0 N I}{2\\pi r}} \\quad (a < r < b)$$\n\nFor $r < a$ or $r > b$: $I_{\\text{enc}} = 0$ (equal and opposite currents thread through the loop), so $B = 0$.",
      "body_he_md": "## סולנואיד\n\nסולנואיד אידיאלי בעל $n$ כריכות למטר, נושא זרם $I$, ומניחים שאינסופי באורכו. השדה בפנים אחיד ומקביל לציר; מחוץ הוא אפסי בקירוב.\n\nנבחר לולאת אמפר מלבנית באורך $l$ עם צד אחד בפנים (מקביל לציר) וצד אחד מחוץ:\n\n$$B_{\\text{in}}\\cdot l = \\mu_0 (nl) I$$\n\n$$\\boxed{B_{\\text{solenoid}} = \\mu_0 n I}$$\n\nמחוץ לסולנואיד: $B \\approx 0$.\n\n## טורואיד\n\nטורואיד בעל $N$ כריכות כולל כרוך על ליבה בצורת סופגנייה. עבור לולאת אמפר מעגלית ברדיוס $r$ בתוך הטורואיד (בין רדיוס פנימי $a$ לרדיוס חיצוני $b$):\n\n$$B(2\\pi r) = \\mu_0 N I \\implies \\boxed{B_{\\text{toroid}} = \\frac{\\mu_0 N I}{2\\pi r}} \\quad (a < r < b)$$\n\nל-$r < a$ או $r > b$: $I_{\\text{enc}} = 0$ (זרמים שווים ומנוגדים חוצים דרך הלולאה), ולכן $B = 0$."
    },
    {
      "id": "limitations",
      "title_en": "Limitations — Why Displacement Current is Needed",
      "title_he": "מגבלות — מדוע דרוש זרם תזוזה",
      "level_min": "university",
      "body_en_md": "## Limitations of the Original Ampère's Law\n\nConsider a capacitor being charged by a current $I$. Draw an Ampèrian loop around the wire feeding one plate:\n\n- **If the bounding surface is a flat disk** crossing the wire: $I_{\\text{enc}} = I$ ✓\n- **If the bounding surface bulges out** between the capacitor plates (no wire passes through): $I_{\\text{enc}} = 0$ ✗\n\nThe two surfaces give *different* values for $I_{\\text{enc}}$, which is a contradiction—Ampère's law is **inconsistent** for time-varying electric fields.\n\n**The fix:** Maxwell added the **displacement current**\n$$I_d = \\epsilon_0 \\frac{d\\Phi_E}{dt}$$\n\nmaking the modified Ampère-Maxwell law:\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0(I_{\\text{enc}} + I_d)$$\n\nBetween the capacitor plates, $I_d = \\epsilon_0 dE/dt \\cdot A = I$ (exactly equal to the conduction current!), restoring consistency.\n\nThis is explored in detail in the Maxwell's Equations lesson.",
      "body_he_md": "## מגבלות חוק אמפר המקורי\n\nנבחן קבל מתטען על-ידי זרם $I$. נצייר לולאת אמפר סביב החוט המזין לוח אחד:\n\n- **אם משטח הגבול הוא דיסק שטוח** החוצה את החוט: $I_{\\text{enc}} = I$ ✓\n- **אם משטח הגבול בולט** בין לוחות הקבל (אין חוט שחוצה): $I_{\\text{enc}} = 0$ ✗\n\nשני המשטחים נותנים ערכים *שונים* ל-$I_{\\text{enc}}$ — סתירה. חוק אמפר **לא עקבי** עבור שדות חשמליים משתנים בזמן.\n\n**הפתרון:** מקסוול הוסיף את **זרם התזוזה**\n$$I_d = \\epsilon_0 \\frac{d\\Phi_E}{dt}$$\n\nמה שיוצר את חוק אמפר-מקסוול המתוקן:\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0(I_{\\text{enc}} + I_d)$$\n\nבין לוחות הקבל, $I_d = I$ (שווה בדיוק לזרם ההולכה!), ומשחזר עקביות."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "An infinite solenoid has $n = 2000$ turns/m and carries current $I = 0.5\\;\\text{A}$. What is the magnetic field inside?",
      "body_he": "סולנואיד אינסופי בעל $n = 2000$ כריכות/מ' נושא זרם $I = 0.5\\;\\text{A}$. מהו השדה המגנטי בתוכו?",
      "options": [
        {"id": "a", "text_en": "$4\\pi\\times10^{-4}\\;\\text{T} \\approx 1.26\\;\\text{mT}$", "text_he": "$4\\pi\\times10^{-4}\\;\\text{T} \\approx 1.26\\;\\text{mT}$", "correct": True},
        {"id": "b", "text_en": "$2\\pi\\times10^{-4}\\;\\text{T}$", "text_he": "$2\\pi\\times10^{-4}\\;\\text{T}$", "correct": False},
        {"id": "c", "text_en": "$8\\pi\\times10^{-4}\\;\\text{T}$", "text_he": "$8\\pi\\times10^{-4}\\;\\text{T}$", "correct": False},
        {"id": "d", "text_en": "$1.0\\times10^{-3}\\;\\text{T}$", "text_he": "$1.0\\times10^{-3}\\;\\text{T}$", "correct": False}
      ],
      "explanation_en": "$B = \\mu_0 n I = (4\\pi\\times10^{-7})(2000)(0.5) = 4\\pi\\times10^{-4}\\approx1.26\\times10^{-3}$ T.",
      "explanation_he": "$B = \\mu_0 n I = (4\\pi\\times10^{-7})(2000)(0.5) = 4\\pi\\times10^{-4} \\approx 1.26\\;\\text{mT}$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "If the current through a solenoid is doubled while the number of turns per meter is halved, the magnetic field inside:",
      "body_he": "אם הזרם דרך סולנואיד מוכפל בעוד שמספר הכריכות למטר מוחצה, השדה המגנטי בפנים:",
      "options": [
        {"id": "a", "text_en": "Doubles", "text_he": "מוכפל", "correct": False},
        {"id": "b", "text_en": "Is halved", "text_he": "מוחצה", "correct": False},
        {"id": "c", "text_en": "Remains unchanged", "text_he": "נשאר ללא שינוי", "correct": True},
        {"id": "d", "text_en": "Increases by a factor of 4", "text_he": "גדל פי 4", "correct": False}
      ],
      "explanation_en": "$B = \\mu_0 n I$. Doubling $I$ and halving $n$: $B' = \\mu_0(n/2)(2I) = \\mu_0 nI = B$. The product $nI$ is unchanged.",
      "explanation_he": "$B = \\mu_0 n I$. הכפלת $I$ וחציית $n$: $B' = \\mu_0(n/2)(2I) = \\mu_0 nI = B$. המכפלה $nI$ אינה משתנה."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "A toroid has $N = 500$ turns, inner radius $a = 0.05\\;\\text{m}$, outer radius $b = 0.10\\;\\text{m}$, and carries current $I = 2\\;\\text{A}$. What is $B$ at radius $r = 0.07\\;\\text{m}$ (inside the toroid)?",
      "body_he": "טורואיד בעל $N = 500$ כריכות, רדיוס פנימי $a = 0.05\\;\\text{m}$, רדיוס חיצוני $b = 0.10\\;\\text{m}$, נושא זרם $I = 2\\;\\text{A}$. מהו $B$ ברדיוס $r = 0.07\\;\\text{m}$ (בתוך הטורואיד)?",
      "options": [
        {"id": "a", "text_en": "$2.86\\times10^{-3}\\;\\text{T}$", "text_he": "$2.86\\times10^{-3}\\;\\text{T}$", "correct": True},
        {"id": "b", "text_en": "$1.43\\times10^{-3}\\;\\text{T}$", "text_he": "$1.43\\times10^{-3}\\;\\text{T}$", "correct": False},
        {"id": "c", "text_en": "$4.00\\times10^{-3}\\;\\text{T}$", "text_he": "$4.00\\times10^{-3}\\;\\text{T}$", "correct": False},
        {"id": "d", "text_en": "$0$ (field is zero inside a toroid)", "text_he": "$0$ (השדה אפס בתוך טורואיד)", "correct": False}
      ],
      "explanation_en": "$B = \\frac{\\mu_0 N I}{2\\pi r} = \\frac{(4\\pi\\times10^{-7})(500)(2)}{2\\pi(0.07)} = \\frac{4\\pi\\times10^{-4}}{0.14\\pi} = \\frac{4\\times10^{-4}}{0.14} \\approx 2.86\\times10^{-3}$ T.",
      "explanation_he": "$B = \\frac{\\mu_0 N I}{2\\pi r} = \\frac{(4\\pi\\times10^{-7})(500)(2)}{2\\pi(0.07)} \\approx 2.86\\times10^{-3}$ T."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "Which of the following is the BEST choice of Ampèrian loop for finding the field inside a solenoid?",
      "body_he": "מהי הבחירה הטובה ביותר של לולאת אמפר למציאת השדה בתוך סולנואיד?",
      "options": [
        {"id": "a", "text_en": "A circular loop coaxial with the solenoid", "text_he": "לולאה מעגלית קואקסיאלית עם הסולנואיד", "correct": False},
        {"id": "b", "text_en": "A rectangular loop with one side along the axis inside and one side outside the solenoid", "text_he": "לולאה מלבנית עם צד אחד לאורך הציר בפנים וצד אחד מחוץ לסולנואיד", "correct": True},
        {"id": "c", "text_en": "A spherical surface enclosing the solenoid", "text_he": "משטח כדורי המקיף את הסולנואיד", "correct": False},
        {"id": "d", "text_en": "Any closed loop works equally well because $\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$ always", "text_he": "כל לולאה סגורה עובדת באותה מידה כי $\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}}$ תמיד", "correct": False}
      ],
      "explanation_en": "A rectangular loop with one long side inside (where $\\vec{B}\\parallel d\\vec{l}$, constant magnitude) and one long side outside (where $B\\approx 0$) allows both conditions for Ampère's law to hold: $|\\vec{B}|$ constant on the contributing segment, and known angle. A circular coaxial loop has $\\vec{B}$ perpendicular to $d\\vec{l}$ so the integral is zero—useless.",
      "explanation_he": "לולאה מלבנית עם צד ארוך אחד בפנים (שם $\\vec{B}\\parallel d\\vec{l}$, עוצמה קבועה) וצד ארוך אחד מחוץ (שם $B\\approx 0$) מאפשרת לשני תנאי חוק אמפר להתקיים. לולאה מעגלית קואקסיאלית — $\\vec{B}$ מאונך ל-$d\\vec{l}$, האינטגרל אפס — לא שימושית."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A cylindrical conductor of radius $R$ carries a uniformly distributed current $I$. A circular Ampèrian loop of radius $r < R$ (inside the conductor) gives:",
      "body_he": "מוליך גלילי ברדיוס $R$ נושא זרם $I$ מפוזר אחידות. לולאת אמפר מעגלית ברדיוס $r < R$ (בתוך המוליך) נותנת:",
      "options": [
        {"id": "a", "text_en": "$B = \\frac{\\mu_0 I}{2\\pi r}$ (same as outside)", "text_he": "$B = \\frac{\\mu_0 I}{2\\pi r}$ (זהה לחיצוני)", "correct": False},
        {"id": "b", "text_en": "$B = \\frac{\\mu_0 I r}{2\\pi R^2}$", "text_he": "$B = \\frac{\\mu_0 I r}{2\\pi R^2}$", "correct": True},
        {"id": "c", "text_en": "$B = 0$ because the conductor shields the interior", "text_he": "$B = 0$ כי המוליך מגן על הפנים", "correct": False},
        {"id": "d", "text_en": "$B = \\frac{\\mu_0 I}{2\\pi R}$ (constant inside)", "text_he": "$B = \\frac{\\mu_0 I}{2\\pi R}$ (קבוע בפנים)", "correct": False}
      ],
      "explanation_en": "The enclosed current is $I_{\\text{enc}} = I(r^2/R^2)$ (proportional to cross-sectional area). Ampère's law: $B(2\\pi r) = \\mu_0 I r^2/R^2$, giving $B = \\mu_0 I r/(2\\pi R^2)$. Inside the conductor, $B$ grows linearly with $r$; outside it falls as $1/r$.",
      "explanation_he": "הזרם הכלוא הוא $I_{\\text{enc}} = I(r^2/R^2)$ (יחסי לשטח החתך). מחוק אמפר: $B(2\\pi r) = \\mu_0 I r^2/R^2$, ולכן $B = \\mu_0 I r/(2\\pi R^2)$. בתוך המוליך, $B$ גדל ליניארית עם $r$; מחוץ הוא יורד כ-$1/r$."
    }
  ]
}

# ─────────────────────────────────────────────────────────────────
# LESSON 4 — Maxwell's Equations & EM Waves
# ─────────────────────────────────────────────────────────────────
maxwell = {
  "id": "maxwell_equations",
  "type": "interactive",
  "subject": "university_physics_2",
  "title_en": "Maxwell's Equations and Electromagnetic Waves",
  "title_he": "משוואות מקסוול וגלים אלקטרומגנטיים",
  "duration_min": 35,
  "level_min": "university",
  "agent_hints": "Maxwell's equations are the culmination of E&M. Students need to see them first in integral form, understand what each term means physically, and then see the wave equation derived heuristically. Key points: (1) displacement current is NOT a real current of charges, it is epsilon_0 * dPhi_E/dt; (2) Gauss for B says no magnetic monopoles exist; (3) Faraday's law with the minus sign is Lenz's law; (4) the wave speed c = 1/sqrt(mu_0 epsilon_0) is a profound prediction from pure electromagnetic theory. Poynting vector direction: use the right-hand rule for E x B. Emphasize E = cB for plane waves.",
  "sections": [
    {
      "id": "displacement_current",
      "title_en": "Displacement Current",
      "title_he": "זרם תזוזה",
      "level_min": "university",
      "body_en_md": "## The Problem with Ampère's Law\n\nWhen a capacitor charges, there is current $I$ in the wires but *no* current between the plates—yet the electric field there changes. The original Ampère's law gives different answers for different bounding surfaces on the same loop, which is inconsistent.\n\n## Maxwell's Displacement Current\n\nMaxwell introduced an additional term:\n\n$$I_d = \\epsilon_0 \\frac{d\\Phi_E}{dt}$$\n\ncalled the **displacement current**. It has the dimensions of current (amperes) and is created by a *changing electric flux*, even in a vacuum. The modified **Ampère-Maxwell law** is:\n\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0\\left(I_{\\text{enc}} + \\epsilon_0\\frac{d\\Phi_E}{dt}\\right)$$\n\n**Between the capacitor plates:** No conduction current, but $E$ changes at rate $I/(\\epsilon_0 A)$, giving $I_d = \\epsilon_0(dE/dt)\\cdot A = I$. The two terms are now equal for both bounding surfaces—consistency restored.\n\n**Physical meaning:** A changing electric field acts as a source of magnetic field, just like a real current.",
      "body_he_md": "## הבעיה עם חוק אמפר\n\nכאשר קבל מתטען, יש זרם $I$ בחוטים אך *אין* זרם בין הלוחות — אך השדה החשמלי שם משתנה. חוק אמפר המקורי נותן תשובות שונות למשטחים גובלים שונים על אותה לולאה, שהוא לא-עקבי.\n\n## זרם התזוזה של מקסוול\n\nמקסוול הכניס איבר נוסף:\n\n$$I_d = \\epsilon_0 \\frac{d\\Phi_E}{dt}$$\n\nהנקרא **זרם תזוזה**. יש לו ממדים של זרם (אמפר) ונוצר על-ידי *שטף חשמלי משתנה*, גם בריק. חוק **אמפר-מקסוול** המתוקן:\n\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0\\left(I_{\\text{enc}} + \\epsilon_0\\frac{d\\Phi_E}{dt}\\right)$$\n\n**בין לוחות הקבל:** אין זרם הולכה, אבל $E$ משתנה בקצב $I/(\\epsilon_0 A)$, נותן $I_d = I$. שני האיברים עכשיו שווים לשני המשטחים הגובלים — עקביות שוחזרה.\n\n**משמעות פיזיקלית:** שדה חשמלי משתנה פועל כמקור לשדה מגנטי, בדיוק כמו זרם ממשי."
    },
    {
      "id": "four_maxwell_equations",
      "title_en": "The Four Maxwell Equations",
      "title_he": "ארבע משוואות מקסוול",
      "level_min": "university",
      "body_en_md": "## Maxwell's Equations (Integral Form)\n\nThe complete laws of classical electromagnetism are encoded in four equations:\n\n**1. Gauss's Law for $\\vec{E}$:**\n$$\\oint \\vec{E}\\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\nElectric field lines originate on positive charges and end on negative charges.\n\n**2. Gauss's Law for $\\vec{B}$:**\n$$\\oint \\vec{B}\\cdot d\\vec{A} = 0$$\nMagnetic field lines have no sources or sinks—there are no magnetic monopoles.\n\n**3. Faraday's Law:**\n$$\\oint \\vec{E}\\cdot d\\vec{l} = -\\frac{d\\Phi_B}{dt}$$\nA changing magnetic flux induces an electric field (with the sign from Lenz's law).\n\n**4. Ampère-Maxwell Law:**\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0\\frac{d\\Phi_E}{dt}$$\nA current *or* a changing electric flux creates a magnetic field.\n\nThese four equations, together with the Lorentz force law $\\vec{F} = q(\\vec{E} + \\vec{v}\\times\\vec{B})$, completely describe all classical electromagnetic phenomena.",
      "body_he_md": "## משוואות מקסוול (צורה אינטגרלית)\n\nחוקי האלקטרומגנטיות הקלאסית המלאים מוצפנים בארבע משוואות:\n\n**1. חוק גאוס ל-$\\vec{E}$:**\n$$\\oint \\vec{E}\\cdot d\\vec{A} = \\frac{Q_{\\text{enc}}}{\\epsilon_0}$$\nקווי שדה חשמלי יוצאים ממטענים חיוביים ומסתיימים במטענים שליליים.\n\n**2. חוק גאוס ל-$\\vec{B}$:**\n$$\\oint \\vec{B}\\cdot d\\vec{A} = 0$$\nלקווי השדה המגנטי אין מקורות — אין מונופולים מגנטיים.\n\n**3. חוק פאראדיי:**\n$$\\oint \\vec{E}\\cdot d\\vec{l} = -\\frac{d\\Phi_B}{dt}$$\nשטף מגנטי משתנה מושרה שדה חשמלי (הסימן מחוק לנץ).\n\n**4. חוק אמפר-מקסוול:**\n$$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0\\frac{d\\Phi_E}{dt}$$\nזרם *או* שטף חשמלי משתנה יוצר שדה מגנטי.\n\nארבע משוואות אלה, יחד עם חוק כוח לורנץ $\\vec{F} = q(\\vec{E} + \\vec{v}\\times\\vec{B})$, מתארות כל תופעה אלקטרומגנטית קלאסית."
    },
    {
      "id": "em_waves",
      "title_en": "Electromagnetic Waves",
      "title_he": "גלים אלקטרומגנטיים",
      "level_min": "university",
      "body_en_md": "## From Maxwell's Equations to EM Waves\n\nMaxwell's equations in free space (no charges, no currents) predict waves. Taking the curl of Faraday's law and substituting the Ampère-Maxwell law leads to the **wave equations**:\n\n$$\\frac{\\partial^2 E}{\\partial x^2} = \\mu_0\\epsilon_0\\frac{\\partial^2 E}{\\partial t^2}, \\qquad \\frac{\\partial^2 B}{\\partial x^2} = \\mu_0\\epsilon_0\\frac{\\partial^2 B}{\\partial t^2}$$\n\nThis is a wave traveling at speed:\n\n$$\\boxed{c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} = \\frac{1}{\\sqrt{(4\\pi\\times10^{-7})(8.854\\times10^{-12})}} \\approx 3\\times10^8\\;\\text{m/s}}$$\n\n**Properties of plane EM waves:**\n- $\\vec{E}\\perp\\vec{B}\\perp\\hat{k}$ (the propagation direction): the fields are mutually perpendicular and both perpendicular to the direction of propagation\n- $E = cB$ (the amplitude ratio)\n- The wave is transverse\n\nFor a plane wave propagating in $+\\hat{x}$:\n$$E_y = E_0\\cos(kx - \\omega t), \\quad B_z = \\frac{E_0}{c}\\cos(kx - \\omega t)$$",
      "body_he_md": "## ממשוואות מקסוול לגלים EM\n\nמשוואות מקסוול בחלל חופשי (ללא מטענים, ללא זרמים) מנבאות גלים. נטילת רוטור של חוק פאראדיי והצבת חוק אמפר-מקסוול מובילה ל**משוואות גל**:\n\n$$\\frac{\\partial^2 E}{\\partial x^2} = \\mu_0\\epsilon_0\\frac{\\partial^2 E}{\\partial t^2}, \\qquad \\frac{\\partial^2 B}{\\partial x^2} = \\mu_0\\epsilon_0\\frac{\\partial^2 B}{\\partial t^2}$$\n\nזהו גל הנע במהירות:\n\n$$\\boxed{c = \\frac{1}{\\sqrt{\\mu_0\\epsilon_0}} \\approx 3\\times10^8\\;\\text{m/s}}$$\n\n**תכונות גלי EM מישוריים:**\n- $\\vec{E}\\perp\\vec{B}\\perp\\hat{k}$: השדות מאוניים זה לזה ושניהם מאוניים לכיוון התפשטות הגל\n- $E = cB$ (יחס העוצמות)\n- הגל הוא רוחבי (transverse)\n\nעבור גל מישורי המתפשט ב-$+\\hat{x}$:\n$$E_y = E_0\\cos(kx - \\omega t), \\quad B_z = \\frac{E_0}{c}\\cos(kx - \\omega t)$$"
    },
    {
      "id": "poynting_vector",
      "title_en": "Energy Transport — Poynting Vector",
      "title_he": "הובלת אנרגיה — וקטור פוינטינג",
      "level_min": "university",
      "body_en_md": "## The Poynting Vector\n\nThe energy flux (power per unit area) of an electromagnetic wave is given by the **Poynting vector**:\n\n$$\\vec{S} = \\frac{1}{\\mu_0}\\vec{E}\\times\\vec{B}$$\n\n- $\\vec{S}$ points in the direction of energy propagation (same as $\\hat{k}$, the wave propagation direction)\n- $|\\vec{S}|$ gives the instantaneous power per unit area (W/m²)\n\nThe **intensity** (time-averaged power per unit area) of a plane wave with peak amplitude $E_0$:\n\n$$I = \\langle |\\vec{S}| \\rangle = \\frac{E_0^2}{2\\mu_0 c} = \\frac{1}{2}\\epsilon_0 c E_0^2$$\n\n**Energy density:** The energy is shared equally between $\\vec{E}$ and $\\vec{B}$:\n$$u = \\epsilon_0 E^2 = \\frac{B^2}{\\mu_0}$$\n\nThe intensity and Poynting vector are used to analyze solar radiation, antenna radiation patterns, and optical fiber communication.",
      "body_he_md": "## וקטור פוינטינג\n\nצפיפות שטף האנרגיה (הספק ליחידת שטח) של גל אלקטרומגנטי נתון על-ידי **וקטור פוינטינג**:\n\n$$\\vec{S} = \\frac{1}{\\mu_0}\\vec{E}\\times\\vec{B}$$\n\n- $\\vec{S}$ מצביע בכיוון התפשטות האנרגיה (זהה ל-$\\hat{k}$)\n- $|\\vec{S}|$ נותן את ההספק הרגעי ליחידת שטח (W/m²)\n\n**העוצמה** (הספק ממוצע בזמן ליחידת שטח) של גל מישורי עם עוצמת שיא $E_0$:\n\n$$I = \\langle |\\vec{S}| \\rangle = \\frac{E_0^2}{2\\mu_0 c} = \\frac{1}{2}\\epsilon_0 c E_0^2$$\n\n**צפיפות אנרגיה:** האנרגיה מחולקת שווה בין $\\vec{E}$ ל-$\\vec{B}$:\n$$u = \\epsilon_0 E^2 = \\frac{B^2}{\\mu_0}$$\n\nוקטור פוינטינג משמש לניתוח קרינת השמש, דפוסי קרינת אנטנות ותקשורת בסיבים אופטיים."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A capacitor with plate area $A = 0.01\\;\\text{m}^2$ is being charged so that the electric field between the plates increases at a rate $dE/dt = 5\\times10^{11}\\;\\text{V/(m}\\cdot\\text{s)}$. What is the displacement current between the plates?",
      "body_he": "קבל עם שטח לוח $A = 0.01\\;\\text{m}^2$ מתטען כך שהשדה החשמלי בין הלוחות גדל בקצב $dE/dt = 5\\times10^{11}\\;\\text{V/(m}\\cdot\\text{s)}$. מהו זרם התזוזה בין הלוחות?",
      "options": [
        {"id": "a", "text_en": "$4.43\\times10^{-2}\\;\\text{A}$", "text_he": "$4.43\\times10^{-2}\\;\\text{A}$", "correct": True},
        {"id": "b", "text_en": "$5.0\\times10^{9}\\;\\text{A}$", "text_he": "$5.0\\times10^{9}\\;\\text{A}$", "correct": False},
        {"id": "c", "text_en": "$8.85\\times10^{-3}\\;\\text{A}$", "text_he": "$8.85\\times10^{-3}\\;\\text{A}$", "correct": False},
        {"id": "d", "text_en": "$0.177\\;\\text{A}$", "text_he": "$0.177\\;\\text{A}$", "correct": False}
      ],
      "explanation_en": "$I_d = \\epsilon_0\\frac{d\\Phi_E}{dt} = \\epsilon_0 A\\frac{dE}{dt} = (8.854\\times10^{-12})(0.01)(5\\times10^{11}) = (8.854\\times10^{-12})(5\\times10^9) = 4.43\\times10^{-2}$ A.",
      "explanation_he": "$I_d = \\epsilon_0 A\\frac{dE}{dt} = (8.854\\times10^{-12})(0.01)(5\\times10^{11}) \\approx 4.43\\times10^{-2}$ A."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "Which of Maxwell's four equations states that there are no magnetic monopoles?",
      "body_he": "איזו ממשוואות מקסוול קובעת שאין מונופולים מגנטיים?",
      "options": [
        {"id": "a", "text_en": "$\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ (Gauss for $E$)", "text_he": "$\\oint \\vec{E}\\cdot d\\vec{A} = Q_{\\text{enc}}/\\epsilon_0$ (גאוס ל-$E$)", "correct": False},
        {"id": "b", "text_en": "$\\oint \\vec{B}\\cdot d\\vec{A} = 0$ (Gauss for $B$)", "text_he": "$\\oint \\vec{B}\\cdot d\\vec{A} = 0$ (גאוס ל-$B$)", "correct": True},
        {"id": "c", "text_en": "$\\oint \\vec{E}\\cdot d\\vec{l} = -d\\Phi_B/dt$ (Faraday)", "text_he": "$\\oint \\vec{E}\\cdot d\\vec{l} = -d\\Phi_B/dt$ (פאראדיי)", "correct": False},
        {"id": "d", "text_en": "$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0 d\\Phi_E/dt$ (Ampère-Maxwell)", "text_he": "$\\oint \\vec{B}\\cdot d\\vec{l} = \\mu_0 I_{\\text{enc}} + \\mu_0\\epsilon_0 d\\Phi_E/dt$ (אמפר-מקסוול)", "correct": False}
      ],
      "explanation_en": "$\\oint \\vec{B}\\cdot d\\vec{A} = 0$ states that the net magnetic flux through any closed surface is zero—there are no magnetic sources (monopoles). Every field line that enters a closed surface must exit it. Compare with Gauss's law for $E$, where the flux equals $Q_{\\text{enc}}/\\epsilon_0$ because electric monopoles (charges) exist.",
      "explanation_he": "$\\oint \\vec{B}\\cdot d\\vec{A} = 0$ קובעת שהשטף המגנטי הנטו דרך כל משטח סגור הוא אפס — אין מקורות מגנטיים (מונופולים). כל קו שדה הנכנס למשטח סגור חייב לצאת ממנו. השווה עם חוק גאוס ל-$E$, שם השטף שווה $Q_{\\text{enc}}/\\epsilon_0$ כי מטענים חשמליים (מונופולים חשמליים) קיימים."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "For a plane electromagnetic wave propagating in the $+z$ direction with $\\vec{E} = E_0\\hat{x}\\cos(kz - \\omega t)$, what is $\\vec{B}$?",
      "body_he": "עבור גל אלקטרומגנטי מישורי המתפשט בכיוון $+z$ עם $\\vec{E} = E_0\\hat{x}\\cos(kz - \\omega t)$, מהו $\\vec{B}$?",
      "options": [
        {"id": "a", "text_en": "$\\vec{B} = \\frac{E_0}{c}\\hat{x}\\cos(kz - \\omega t)$", "text_he": "$\\vec{B} = \\frac{E_0}{c}\\hat{x}\\cos(kz - \\omega t)$", "correct": False},
        {"id": "b", "text_en": "$\\vec{B} = \\frac{E_0}{c}\\hat{y}\\cos(kz - \\omega t)$", "text_he": "$\\vec{B} = \\frac{E_0}{c}\\hat{y}\\cos(kz - \\omega t)$", "correct": True},
        {"id": "c", "text_en": "$\\vec{B} = \\frac{E_0}{c}\\hat{z}\\cos(kz - \\omega t)$", "text_he": "$\\vec{B} = \\frac{E_0}{c}\\hat{z}\\cos(kz - \\omega t)$", "correct": False},
        {"id": "d", "text_en": "$\\vec{B} = -\\frac{E_0}{c}\\hat{y}\\cos(kz - \\omega t)$", "text_he": "$\\vec{B} = -\\frac{E_0}{c}\\hat{y}\\cos(kz - \\omega t)$", "correct": False}
      ],
      "explanation_en": "For a plane EM wave: $\\vec{E}\\times\\vec{B}$ must point in the propagation direction $+\\hat{z}$. With $\\vec{E}\\parallel\\hat{x}$, we need $\\hat{x}\\times\\hat{B} = \\hat{z}$, so $\\hat{B} = \\hat{y}$ (since $\\hat{x}\\times\\hat{y} = \\hat{z}$). Also $B = E/c$, so $\\vec{B} = (E_0/c)\\hat{y}\\cos(kz-\\omega t)$.",
      "explanation_he": "עבור גל EM מישורי: $\\vec{E}\\times\\vec{B}$ חייב להצביע בכיוון ההתפשטות $+\\hat{z}$. עם $\\vec{E}\\parallel\\hat{x}$, נצטרך $\\hat{x}\\times\\hat{B} = \\hat{z}$, ולכן $\\hat{B} = \\hat{y}$ (כי $\\hat{x}\\times\\hat{y} = \\hat{z}$). גם $B = E/c$, ולכן $\\vec{B} = (E_0/c)\\hat{y}\\cos(kz-\\omega t)$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "An EM wave has $\\vec{E}$ pointing in $+\\hat{y}$ and $\\vec{B}$ pointing in $+\\hat{z}$. What is the direction of the Poynting vector $\\vec{S} = \\frac{1}{\\mu_0}\\vec{E}\\times\\vec{B}$?",
      "body_he": "לגל EM יש $\\vec{E}$ המצביע ב-$+\\hat{y}$ ו-$\\vec{B}$ המצביע ב-$+\\hat{z}$. מהו כיוון וקטור פוינטינג $\\vec{S} = \\frac{1}{\\mu_0}\\vec{E}\\times\\vec{B}$?",
      "options": [
        {"id": "a", "text_en": "$+\\hat{x}$", "text_he": "$+\\hat{x}$", "correct": True},
        {"id": "b", "text_en": "$-\\hat{x}$", "text_he": "$-\\hat{x}$", "correct": False},
        {"id": "c", "text_en": "$+\\hat{y}$", "text_he": "$+\\hat{y}$", "correct": False},
        {"id": "d", "text_en": "$+\\hat{z}$", "text_he": "$+\\hat{z}$", "correct": False}
      ],
      "explanation_en": "$\\hat{y}\\times\\hat{z} = \\hat{x}$. So $\\vec{S}\\propto\\vec{E}\\times\\vec{B}\\propto\\hat{y}\\times\\hat{z} = +\\hat{x}$.",
      "explanation_he": "$\\hat{y}\\times\\hat{z} = \\hat{x}$. לכן $\\vec{S}\\propto\\vec{E}\\times\\vec{B}\\propto+\\hat{x}$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "What is the speed of light in vacuum predicted by Maxwell's equations, given $\\mu_0 = 4\\pi\\times10^{-7}\\;\\text{T}\\cdot\\text{m/A}$ and $\\epsilon_0 = 8.854\\times10^{-12}\\;\\text{C}^2/(\\text{N}\\cdot\\text{m}^2)$?",
      "body_he": "מהי מהירות האור בריק כפי שמנבאות משוואות מקסוול, בהינתן $\\mu_0 = 4\\pi\\times10^{-7}\\;\\text{T}\\cdot\\text{m/A}$ ו-$\\epsilon_0 = 8.854\\times10^{-12}\\;\\text{C}^2/(\\text{N}\\cdot\\text{m}^2)$?",
      "options": [
        {"id": "a", "text_en": "$3.0\\times10^8\\;\\text{m/s}$", "text_he": "$3.0\\times10^8\\;\\text{m/s}$", "correct": True},
        {"id": "b", "text_en": "$1.5\\times10^8\\;\\text{m/s}$", "text_he": "$1.5\\times10^8\\;\\text{m/s}$", "correct": False},
        {"id": "c", "text_en": "$9.0\\times10^{16}\\;\\text{m/s}$", "text_he": "$9.0\\times10^{16}\\;\\text{m/s}$", "correct": False},
        {"id": "d", "text_en": "$6.0\\times10^8\\;\\text{m/s}$", "text_he": "$6.0\\times10^8\\;\\text{m/s}$", "correct": False}
      ],
      "explanation_en": "$c = 1/\\sqrt{\\mu_0\\epsilon_0} = 1/\\sqrt{(4\\pi\\times10^{-7})(8.854\\times10^{-12})} = 1/\\sqrt{1.113\\times10^{-17}} \\approx 3.0\\times10^8$ m/s. This was a profound theoretical prediction that the speed of light equals $1/\\sqrt{\\mu_0\\epsilon_0}$, confirming that light is an electromagnetic wave.",
      "explanation_he": "$c = 1/\\sqrt{\\mu_0\\epsilon_0} \\approx 3.0\\times10^8$ m/s. זה היה ניבוי תיאורטי עמוק שמהירות האור שווה ל-$1/\\sqrt{\\mu_0\\epsilon_0}$, המאשר שאור הוא גל אלקטרומגנטי."
    }
  ]
}

# ─────────────────────────────────────────────────────────────────
# LESSON 5 — Faraday's Law & Electromagnetic Induction (Uni level)
# ─────────────────────────────────────────────────────────────────
faraday_uni = {
  "id": "faraday_induction_uni",
  "type": "interactive",
  "subject": "university_physics_2",
  "title_en": "Faraday's Law and Electromagnetic Induction — University Level",
  "title_he": "חוק פאראדיי והשראה אלקטרומגנטית — רמה אוניברסיטאית",
  "duration_min": 35,
  "level_min": "university",
  "agent_hints": "This is the university-level (calculus-based) treatment of Faraday's law. Distinguish from the high-school lesson: here we use the integral form, derive motional EMF as a line integral of (v x B), and study self-inductance via the solenoid formula L = mu_0 n^2 V. The RL circuit requires solving a first-order ODE. Key subtleties: (1) the minus sign in Faraday's law IS Lenz's law; (2) motional EMF can be derived two ways: the flux method and the force-on-charges method; (3) self-inductance means the coil opposes changes in its own current. For the RL circuit, walk through the separation-of-variables solution. Common error: students forget that tau = L/R has units of seconds only when L is in henries and R in ohms.",
  "sections": [
    {
      "id": "faraday_law_integral",
      "title_en": "Faraday's Law — Integral Form",
      "title_he": "חוק פאראדיי — צורה אינטגרלית",
      "level_min": "university",
      "body_en_md": "## Faraday's Law\n\nThe magnetic flux through a surface $S$ bounded by a closed curve $C$ is:\n\n$$\\Phi_B = \\iint_S \\vec{B}\\cdot d\\vec{A}$$\n\nFaraday's law states that the EMF around the closed path $C$ equals the *negative* rate of change of magnetic flux:\n\n$$\\mathcal{E} = \\oint_C \\vec{E}\\cdot d\\vec{l} = -\\frac{d\\Phi_B}{dt}$$\n\n**The minus sign (Lenz's law):** The induced EMF drives a current in the direction that *opposes* the change in flux. If the flux through a loop is increasing (downward, say), the induced current creates a field opposing that increase (upward).\n\n**Three ways the flux can change:**\n1. The magnitude of $\\vec{B}$ changes\n2. The area of the loop changes\n3. The angle between $\\vec{B}$ and $\\vec{A}$ changes\n\nAll three mechanisms are captured by $d\\Phi_B/dt$, and all produce an EMF according to Faraday's law.\n\n**Note:** This is the *general* form—the induced electric field $\\vec{E}$ exists even in the absence of a conductor, and it drives the circulation of $\\vec{E}$ around any closed path.",
      "body_he_md": "## חוק פאראדיי\n\nהשטף המגנטי דרך משטח $S$ הגובל בעקומה סגורה $C$:\n\n$$\\Phi_B = \\iint_S \\vec{B}\\cdot d\\vec{A}$$\n\nחוק פאראדיי קובע שה-EMF סביב המסלול הסגור $C$ שווה לקצב השינוי ה*שלילי* של השטף המגנטי:\n\n$$\\mathcal{E} = \\oint_C \\vec{E}\\cdot d\\vec{l} = -\\frac{d\\Phi_B}{dt}$$\n\n**הסימן השלילי (חוק לנץ):** ה-EMF המושרה מניע זרם בכיוון ה*מתנגד* לשינוי בשטף. אם השטף דרך לולאה גדל (כלפי מטה, נניח), הזרם המושרה יוצר שדה המתנגד לגידול זה (כלפי מעלה).\n\n**שלוש דרכים שבהן השטף יכול להשתנות:**\n1. גודל $\\vec{B}$ משתנה\n2. שטח הלולאה משתנה\n3. הזווית בין $\\vec{B}$ ל-$\\vec{A}$ משתנה\n\nכל שלושת המנגנונים כלולים ב-$d\\Phi_B/dt$, וכולם מייצרים EMF לפי חוק פאראדיי.\n\n**הערה:** זוהי הצורה ה*כללית* — השדה החשמלי המושרה $\\vec{E}$ קיים גם בהיעדר מוליך."
    },
    {
      "id": "motional_emf",
      "title_en": "Motional EMF and Lenz's Law Applications",
      "title_he": "EMF של תנועה ויישומי חוק לנץ",
      "level_min": "university",
      "body_en_md": "## Motional EMF\n\nA straight conducting rod of length $L$ moves with velocity $\\vec{v}$ perpendicular to a uniform magnetic field $\\vec{B}$. The free charges in the rod experience force $\\vec{F} = q\\vec{v}\\times\\vec{B}$, which separates charges and creates a potential difference.\n\nThe motional EMF is:\n$$\\mathcal{E} = \\oint (\\vec{v}\\times\\vec{B})\\cdot d\\vec{l} = BLv$$\n(when $\\vec{v}$, $L$, and $\\vec{B}$ are mutually perpendicular).\n\nEquivalently, by the flux method: the rod sweeps area $A = Lvt$, so $\\Phi_B = BLvt$ and $\\mathcal{E} = -d\\Phi_B/dt = -BLv$ (the sign from Lenz's law tells us the current direction).\n\n## Applying Lenz's Law\n\n**Step-by-step procedure:**\n1. Determine the initial direction of $\\vec{B}$ through the loop\n2. Determine whether $\\Phi_B$ is increasing or decreasing\n3. The induced current creates a $\\vec{B}$ that *opposes* the change\n4. Apply the right-hand rule to find the current direction consistent with step 3\n\n**Example:** A bar magnet (north pole facing a loop) is pushed toward the loop. Flux through loop increases (upward). Induced current must create downward flux inside loop → current flows clockwise (viewed from the magnet side).",
      "body_he_md": "## EMF של תנועה\n\nמוט מוליך ישר באורך $L$ נע במהירות $\\vec{v}$ מאונכת לשדה מגנטי אחיד $\\vec{B}$. המטענים החופשיים במוט חווים כוח $\\vec{F} = q\\vec{v}\\times\\vec{B}$, המפריד מטענים ויוצר הפרש פוטנציאל.\n\nה-EMF של התנועה הוא:\n$$\\mathcal{E} = \\oint (\\vec{v}\\times\\vec{B})\\cdot d\\vec{l} = BLv$$\n(כאשר $\\vec{v}$, $L$ ו-$\\vec{B}$ מאוניים זה לזה).\n\nבשיטת השטף: המוט מגרוף שטח $A = Lvt$, ולכן $\\Phi_B = BLvt$ ו-$\\mathcal{E} = -d\\Phi_B/dt = -BLv$ (הסימן מחוק לנץ נותן את כיוון הזרם).\n\n## יישום חוק לנץ\n\n**נוהל שלב-אחר-שלב:**\n1. קבע את כיוון $\\vec{B}$ הראשוני דרך הלולאה\n2. קבע אם $\\Phi_B$ גדל או יורד\n3. הזרם המושרה יוצר $\\vec{B}$ ה*מתנגד* לשינוי\n4. הפעל כלל יד-ימין למציאת כיוון הזרם עקבי עם שלב 3\n\n**דוגמה:** מגנט קבוע (קוטב צפון לכיוון לולאה) נדחף לכיוון הלולאה. השטף גדל (כלפי מעלה). הזרם המושרה חייב ליצור שטף כלפי מטה → זרם זורם עם כיוון השעון (מצד המגנט)."
    },
    {
      "id": "generator_transformer",
      "title_en": "Generator and Transformer",
      "title_he": "גנרטור וטרנספורמטור",
      "level_min": "university",
      "body_en_md": "## AC Generator\n\nA coil of $N$ turns, area $A$, rotates at angular frequency $\\omega$ in a uniform field $\\vec{B}$. The flux through the coil is:\n\n$$\\Phi_B = NBA\\cos(\\omega t)$$\n\nFaraday's law gives the EMF:\n\n$$\\mathcal{E} = -N\\frac{d\\Phi_B}{dt} = NBA\\omega\\sin(\\omega t) = \\mathcal{E}_0\\sin(\\omega t)$$\n\nwhere $\\mathcal{E}_0 = NBA\\omega$ is the peak EMF. This is the operating principle of AC generators.\n\n## Ideal Transformer\n\nAn ideal transformer has a primary coil ($N_1$ turns, voltage $V_1$) and a secondary coil ($N_2$ turns, voltage $V_2$) on a common iron core. By Faraday's law, the same rate of flux change threads both coils:\n\n$$\\frac{V_1}{V_2} = \\frac{N_1}{N_2}$$\n\nPower is conserved: $V_1 I_1 = V_2 I_2$, so:\n\n$$\\frac{I_1}{I_2} = \\frac{N_2}{N_1}$$\n\nA step-up transformer ($N_2 > N_1$) increases voltage and decreases current. The transformer enables long-distance AC power transmission at high voltage (low current, low $I^2R$ losses).",
      "body_he_md": "## גנרטור AC\n\nסליל בעל $N$ כריכות, שטח $A$, מסתובב בתדירות זוויתית $\\omega$ בשדה אחיד $\\vec{B}$. השטף דרך הסליל:\n\n$$\\Phi_B = NBA\\cos(\\omega t)$$\n\nחוק פאראדיי נותן את ה-EMF:\n\n$$\\mathcal{E} = -N\\frac{d\\Phi_B}{dt} = NBA\\omega\\sin(\\omega t) = \\mathcal{E}_0\\sin(\\omega t)$$\n\nכאשר $\\mathcal{E}_0 = NBA\\omega$ הוא ה-EMF השיא. זהו עקרון הפעולה של גנרטורי AC.\n\n## טרנספורמטור אידיאלי\n\nטרנספורמטור אידיאלי בעל סליל ראשוני ($N_1$ כריכות, מתח $V_1$) וסליל משני ($N_2$ כריכות, מתח $V_2$) על ליבת ברזל משותפת. מחוק פאראדיי, אותו קצב שינוי שטף עובר דרך שני הסלילים:\n\n$$\\frac{V_1}{V_2} = \\frac{N_1}{N_2}$$\n\nשימור הספק: $V_1 I_1 = V_2 I_2$, ולכן:\n\n$$\\frac{I_1}{I_2} = \\frac{N_2}{N_1}$$\n\nטרנספורמטור מעלה ($N_2 > N_1$) מגביר מתח ומקטין זרם."
    },
    {
      "id": "inductance_rl_circuit",
      "title_en": "Self-Inductance and RL Circuits",
      "title_he": "אינדוקטנס עצמי ומעגלי RL",
      "level_min": "university",
      "body_en_md": "## Self-Inductance\n\nWhen the current through a coil changes, the resulting change in flux induces an EMF in the coil itself (back-EMF):\n\n$$\\mathcal{E}_L = -L\\frac{dI}{dt}$$\n\nThe proportionality constant $L$ is the **self-inductance** (units: Henry = V·s/A = Ω·s).\n\nFor an ideal solenoid (length $\\ell$, $n$ turns/m, cross-sectional area $A_c$, volume $V = A_c\\ell$):\n\n$$L = \\frac{N\\Phi_B}{I} = \\mu_0 n^2 A_c \\ell = \\mu_0 n^2 V$$\n\n## RL Circuit\n\nA series circuit with EMF $\\mathcal{E}_0$, resistance $R$, and inductance $L$. Applying Kirchhoff's voltage law:\n\n$$\\mathcal{E}_0 - IR - L\\frac{dI}{dt} = 0 \\implies \\frac{dI}{dt} = \\frac{\\mathcal{E}_0 - IR}{L}$$\n\nSolving by separation of variables with $I(0) = 0$:\n\n$$\\boxed{I(t) = \\frac{\\mathcal{E}_0}{R}\\left(1 - e^{-t/\\tau}\\right)}, \\quad \\tau = \\frac{L}{R}$$\n\n$\\tau$ is the **time constant**: after $t = \\tau$, the current reaches $1 - 1/e \\approx 63\\%$ of its final value $\\mathcal{E}_0/R$.\n\n**Energy stored in the inductor:**\n$$U_L = \\frac{1}{2}LI^2$$\n\nThis energy is stored in the magnetic field of the coil.",
      "body_he_md": "## אינדוקטנס עצמי\n\nכאשר הזרם דרך סליל משתנה, השינוי בשטף מושרה EMF בסליל עצמו (EMF אחורי):\n\n$$\\mathcal{E}_L = -L\\frac{dI}{dt}$$\n\nקבוע הפרופורציה $L$ הוא **האינדוקטנס העצמי** (יחידות: הנרי = V·s/A = Ω·s).\n\nעבור סולנואיד אידיאלי (אורך $\\ell$, $n$ כריכות/מ', שטח חתך $A_c$, נפח $V = A_c\\ell$):\n\n$$L = \\mu_0 n^2 A_c \\ell = \\mu_0 n^2 V$$\n\n## מעגל RL\n\nמעגל טורי עם EMF $\\mathcal{E}_0$, התנגדות $R$ ואינדוקטנס $L$. מחוק קירכהוף למתחים:\n\n$$\\mathcal{E}_0 - IR - L\\frac{dI}{dt} = 0 \\implies \\frac{dI}{dt} = \\frac{\\mathcal{E}_0 - IR}{L}$$\n\nפתרון בהפרדת משתנים עם $I(0) = 0$:\n\n$$\\boxed{I(t) = \\frac{\\mathcal{E}_0}{R}\\left(1 - e^{-t/\\tau}\\right)}, \\quad \\tau = \\frac{L}{R}$$\n\n$\\tau$ הוא **קבוע הזמן**: לאחר $t = \\tau$, הזרם מגיע ל-$1 - 1/e \\approx 63\\%$ מערכו הסופי $\\mathcal{E}_0/R$.\n\n**אנרגיה המאוחסנת במשרן:**\n$$U_L = \\frac{1}{2}LI^2$$"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A rectangular loop lies in the plane of the page. A uniform magnetic field $\\vec{B}$ pointing into the page is increasing in magnitude. By Lenz's law, the induced current in the loop flows:",
      "body_he": "לולאה מלבנית שוכבת במישור הדף. שדה מגנטי אחיד $\\vec{B}$ המצביע לתוך הדף גדל בעוצמתו. לפי חוק לנץ, הזרם המושרה בלולאה זורם:",
      "options": [
        {"id": "a", "text_en": "Clockwise (to oppose the increasing flux into the page)", "text_he": "עם כיוון השעון (כדי להתנגד לגידול השטף לתוך הדף)", "correct": False},
        {"id": "b", "text_en": "Counterclockwise (to create flux out of the page, opposing the increase)", "text_he": "נגד כיוון השעון (כדי ליצור שטף מחוץ לדף, מתנגד לגידול)", "correct": True},
        {"id": "c", "text_en": "Along the direction of $\\vec{B}$", "text_he": "בכיוון $\\vec{B}$", "correct": False},
        {"id": "d", "text_en": "There is no induced current because $\\vec{B}$ is uniform", "text_he": "אין זרם מושרה כי $\\vec{B}$ אחיד", "correct": False}
      ],
      "explanation_en": "The flux into the page is increasing. By Lenz's law, the induced current must create a magnetic field opposing this increase, i.e., out of the page inside the loop. By the right-hand rule, this requires a counterclockwise current (viewed from the front of the page).",
      "explanation_he": "השטף לתוך הדף גדל. לפי חוק לנץ, הזרם המושרה חייב ליצור שדה המתנגד לגידול זה, כלומר מחוץ לדף בתוך הלולאה. לפי כלל יד-ימין, זה מצריך זרם נגד כיוון השעון (מצד הקדמי של הדף)."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A conducting rod of length $L = 0.5\\;\\text{m}$ moves with velocity $v = 4\\;\\text{m/s}$ perpendicular to a uniform magnetic field $B = 0.3\\;\\text{T}$. The rod is also perpendicular to the field. What is the magnitude of the induced EMF?",
      "body_he": "מוט מוליך באורך $L = 0.5\\;\\text{m}$ נע במהירות $v = 4\\;\\text{m/s}$ מאונכת לשדה מגנטי אחיד $B = 0.3\\;\\text{T}$. המוט גם מאונך לשדה. מהי עוצמת ה-EMF המושרה?",
      "options": [
        {"id": "a", "text_en": "$0.60\\;\\text{V}$", "text_he": "$0.60\\;\\text{V}$", "correct": True},
        {"id": "b", "text_en": "$0.30\\;\\text{V}$", "text_he": "$0.30\\;\\text{V}$", "correct": False},
        {"id": "c", "text_en": "$1.20\\;\\text{V}$", "text_he": "$1.20\\;\\text{V}$", "correct": False},
        {"id": "d", "text_en": "$0.075\\;\\text{V}$", "text_he": "$0.075\\;\\text{V}$", "correct": False}
      ],
      "explanation_en": "$\\mathcal{E} = BLv = (0.3)(0.5)(4) = 0.60$ V. This follows both from the flux method and from the force-on-charges approach: $F = qvB$ on each charge, work per unit charge over length $L$ is $vBL$.",
      "explanation_he": "$\\mathcal{E} = BLv = (0.3)(0.5)(4) = 0.60$ V. זה נובע הן משיטת השטף והן מגישת הכוח על המטענים: $F = qvB$ על כל מטען, עבודה ליחידת מטען על אורך $L$ היא $vBL$."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "An ideal transformer has $N_1 = 200$ turns on the primary and $N_2 = 50$ turns on the secondary. If the primary voltage is $V_1 = 240\\;\\text{V}$ and the primary current is $I_1 = 2\\;\\text{A}$, what are the secondary voltage $V_2$ and secondary current $I_2$?",
      "body_he": "לטרנספורמטור אידיאלי יש $N_1 = 200$ כריכות בראשוני ו-$N_2 = 50$ כריכות במשני. אם המתח הראשוני הוא $V_1 = 240\\;\\text{V}$ והזרם הראשוני $I_1 = 2\\;\\text{A}$, מהם המתח המשני $V_2$ והזרם המשני $I_2$?",
      "options": [
        {"id": "a", "text_en": "$V_2 = 60\\;\\text{V},\\; I_2 = 8\\;\\text{A}$", "text_he": "$V_2 = 60\\;\\text{V},\\; I_2 = 8\\;\\text{A}$", "correct": True},
        {"id": "b", "text_en": "$V_2 = 60\\;\\text{V},\\; I_2 = 0.5\\;\\text{A}$", "text_he": "$V_2 = 60\\;\\text{V},\\; I_2 = 0.5\\;\\text{A}$", "correct": False},
        {"id": "c", "text_en": "$V_2 = 960\\;\\text{V},\\; I_2 = 0.5\\;\\text{A}$", "text_he": "$V_2 = 960\\;\\text{V},\\; I_2 = 0.5\\;\\text{A}$", "correct": False},
        {"id": "d", "text_en": "$V_2 = 240\\;\\text{V},\\; I_2 = 2\\;\\text{A}$", "text_he": "$V_2 = 240\\;\\text{V},\\; I_2 = 2\\;\\text{A}$", "correct": False}
      ],
      "explanation_en": "$V_2 = V_1(N_2/N_1) = 240(50/200) = 60$ V. By power conservation: $I_2 = I_1(N_1/N_2) = 2(200/50) = 8$ A. Check: $P = V_1 I_1 = 480$ W $= V_2 I_2 = (60)(8) = 480$ W ✓.",
      "explanation_he": "$V_2 = V_1(N_2/N_1) = 240(50/200) = 60$ V. משימור הספק: $I_2 = I_1(N_1/N_2) = 2(200/50) = 8$ A. בדיקה: $P = 480$ W $= (60)(8) = 480$ W ✓."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A series RL circuit has $\\mathcal{E}_0 = 12\\;\\text{V}$, $R = 6\\;\\Omega$, and $L = 0.3\\;\\text{H}$. What is the time constant $\\tau$ and the current at $t = \\tau$?",
      "body_he": "מעגל RL טורי בעל $\\mathcal{E}_0 = 12\\;\\text{V}$, $R = 6\\;\\Omega$ ו-$L = 0.3\\;\\text{H}$. מהו קבוע הזמן $\\tau$ והזרם ב-$t = \\tau$?",
      "options": [
        {"id": "a", "text_en": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) \\approx 1.26\\;\\text{A}$", "text_he": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) \\approx 1.26\\;\\text{A}$", "correct": True},
        {"id": "b", "text_en": "$\\tau = 1.8\\;\\text{s},\\; I(\\tau) \\approx 1.26\\;\\text{A}$", "text_he": "$\\tau = 1.8\\;\\text{s},\\; I(\\tau) \\approx 1.26\\;\\text{A}$", "correct": False},
        {"id": "c", "text_en": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) = 2\\;\\text{A}$", "text_he": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) = 2\\;\\text{A}$", "correct": False},
        {"id": "d", "text_en": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) = 0\\;\\text{A}$", "text_he": "$\\tau = 0.05\\;\\text{s},\\; I(\\tau) = 0\\;\\text{A}$", "correct": False}
      ],
      "explanation_en": "$\\tau = L/R = 0.3/6 = 0.05$ s. Final current: $I_\\infty = \\mathcal{E}_0/R = 12/6 = 2$ A. At $t = \\tau$: $I(\\tau) = 2(1 - e^{-1}) = 2(1 - 0.368) = 2(0.632) \\approx 1.26$ A.",
      "explanation_he": "$\\tau = L/R = 0.3/6 = 0.05$ s. זרם סופי: $I_\\infty = 2$ A. ב-$t = \\tau$: $I(\\tau) = 2(1 - e^{-1}) \\approx 1.26$ A."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "Which statement correctly distinguishes when to use Faraday's law versus Biot-Savart?",
      "body_he": "איזו טענה מבחינה נכון מתי להשתמש בחוק פאראדיי לעומת ביו-סבר?",
      "options": [
        {"id": "a", "text_en": "Use Faraday's law to find the magnetic field produced by a steady current; use Biot-Savart to find induced EMF.", "text_he": "השתמש בחוק פאראדיי למציאת השדה המגנטי מזרם קבוע; השתמש בביו-סבר למציאת EMF מושרה.", "correct": False},
        {"id": "b", "text_en": "Use Biot-Savart to calculate $\\vec{B}$ from a given current distribution; use Faraday's law to find the EMF (and induced current) caused by a changing magnetic flux.", "text_he": "השתמש בביו-סבר לחישוב $\\vec{B}$ מפיזור זרם נתון; השתמש בחוק פאראדיי למציאת ה-EMF (והזרם המושרה) הנגרם משטף מגנטי משתנה.", "correct": True},
        {"id": "c", "text_en": "Biot-Savart and Faraday's law are interchangeable; use whichever is more convenient.", "text_he": "ביו-סבר וחוק פאראדיי ניתנים להחלפה; השתמש באיזה שנוח יותר.", "correct": False},
        {"id": "d", "text_en": "Use Faraday's law only for AC circuits; use Biot-Savart for DC circuits.", "text_he": "השתמש בחוק פאראדיי רק למעגלי AC; השתמש בביו-סבר למעגלי DC.", "correct": False}
      ],
      "explanation_en": "Biot-Savart (and Ampère's law) are used to find the magnetic field $\\vec{B}$ produced by a given current distribution. Faraday's law is used in the opposite direction: given a (possibly time-varying) magnetic field, it tells you the EMF induced in a loop and hence the induced current. They are not interchangeable: Biot-Savart is a source law (currents → fields), while Faraday is an induction law (changing fields → EMF).",
      "explanation_he": "ביו-סבר (וחוק אמפר) משמשים למציאת השדה המגנטי $\\vec{B}$ המיוצר על-ידי פיזור זרם נתון. חוק פאראדיי משמש בכיוון ההפוך: בהינתן שדה מגנטי (אפשרי משתנה בזמן), הוא נותן את ה-EMF המושרה בלולאה ומכאן את הזרם המושרה. הם אינם ניתנים להחלפה."
    }
  ]
}

# ─── write files ─────────────────────────────────────────────────

lessons = [gauss, biot_savart, ampere, maxwell, faraday_uni]

for lesson in lessons:
    path = os.path.join(LESSONS_DIR, f"{lesson['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
    print(f"Wrote {path}")

print("Done.")
