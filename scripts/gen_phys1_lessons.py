#!/usr/bin/env python3
"""
Generate 5 university Physics 1 (Mechanics) lessons for A Step Forward.
Run from the monorepo root:
    python scripts/gen_phys1_lessons.py
"""
import json, os

LESSONS_DIR = "scripts/seed_data/lessons"
os.makedirs(LESSONS_DIR, exist_ok=True)

def save(lesson):
    path = os.path.join(LESSONS_DIR, lesson["id"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
    print(f"Saved {lesson['id']}")


# ─────────────────────────────────────────────────────────────────
# LESSON 1 — Rigid Body Statics: Torque & Equilibrium
# ─────────────────────────────────────────────────────────────────
save({
  "id": "rigid_body_torque_equilibrium",
  "subject": "university_physics_1",
  "title_en": "Rigid Body Statics — Torque & Equilibrium (University)",
  "title_he": "סטטיקה של גוף קשיח — מומנט ושיווי משקל (אוניברסיטה)",
  "duration_min": 28,
  "type": "interactive",
  "level_min": "university",
  "agent_hints": "Students often forget that $\\sum\\vec{\\tau}=0$ must hold about **every** pivot simultaneously — choosing the pivot at an unknown-force point eliminates that unknown from the torque equation. Emphasize the sign convention for torques (CCW positive) and that $\\tau = rF\\sin\\theta$ uses the perpendicular distance. For the moment-of-inertia table, link to the integral $I=\\int r^2\\,dm$ so students understand why the rod-about-end value is four times the rod-about-center value.",
  "sections": [
    {
      "id": "torque_definition",
      "title_en": "Torque — Cross Product and Right-Hand Rule",
      "title_he": "מומנט כוח — מכפלה וקטורית וכלל היד הימנית",
      "level_min": "university",
      "body_en_md": "## Torque as a Cross Product\n\nThe **torque** (moment of force) produced by force $\\vec{F}$ acting at position $\\vec{r}$ relative to a chosen pivot is:\n$$\\boxed{\\vec{\\tau} = \\vec{r} \\times \\vec{F}}$$\n\n**Magnitude:** $|\\vec{\\tau}| = rF\\sin\\theta$, where $\\theta$ is the angle between $\\vec{r}$ and $\\vec{F}$.\n\nEquivalent expressions:\n- $\\tau = r_\\perp F$ where $r_\\perp = r\\sin\\theta$ is the **moment arm** (perpendicular distance from pivot to the line of action)\n- $\\tau = r F_\\perp$ where $F_\\perp$ is the component of $\\vec{F}$ perpendicular to $\\vec{r}$\n\n**Units:** N·m (not joules — torque is not energy, though the units are identical dimensionally).\n\n**Direction — right-hand rule:** Point fingers along $\\vec{r}$, curl toward $\\vec{F}$; thumb points in the direction of $\\vec{\\tau}$. For planar problems, torques are either $+\\hat{z}$ (counter-clockwise, CCW) or $-\\hat{z}$ (clockwise, CW).\n\n**Sign convention in 2-D:** CCW torques are positive, CW torques are negative.\n\n### Example\nA force $F = 20$ N acts at $r = 0.5$ m from the pivot at $\\theta = 30°$ from $\\vec{r}$:\n$$\\tau = (0.5)(20)\\sin 30° = (0.5)(20)(0.5) = 5 \\text{ N·m (CCW)}$$",
      "body_he_md": "## מומנט כוח כמכפלה וקטורית\n\n**מומנט הכוח** הנוצר על ידי כוח $\\vec{F}$ הפועל בנקודה $\\vec{r}$ ביחס לציר סיבוב נבחר:\n$$\\boxed{\\vec{\\tau} = \\vec{r} \\times \\vec{F}}$$\n\n**עוצמה:** $|\\vec{\\tau}| = rF\\sin\\theta$, כאשר $\\theta$ הזווית בין $\\vec{r}$ ל-$\\vec{F}$.\n\nביטויים שקולים:\n- $\\tau = r_\\perp F$ כאשר $r_\\perp = r\\sin\\theta$ הוא **זרוע המומנט** (המרחק הניצב מציר הסיבוב לישר הכוח)\n- $\\tau = r F_\\perp$ כאשר $F_\\perp$ הוא הרכיב הניצב של $\\vec{F}$ ל-$\\vec{r}$\n\n**יחידות:** N·m (לא ג'אול — מומנט אינו אנרגיה, אך הממדים זהים).\n\n**כיוון — כלל היד הימנית:** הצב אצבעות לאורך $\\vec{r}$ ועקם לכיוון $\\vec{F}$; האגודל מצביע לכיוון $\\vec{\\tau}$. לבעיות מישוריות, מומנטים הם $+\\hat{z}$ (נגד כיוון השעון, CCW) או $-\\hat{z}$ (עם כיוון השעון, CW).\n\n**קונבנציית סימן בדו-ממד:** מומנטים CCW חיוביים, CW שליליים.\n\n### דוגמה\nכוח $F = 20$ N פועל ב-$r = 0.5$ m מציר הסיבוב בזווית $\\theta = 30°$:\n$$\\tau = (0.5)(20)\\sin 30° = 5 \\text{ N·m (CCW)}$$"
    },
    {
      "id": "static_equilibrium",
      "title_en": "Conditions for Static Equilibrium",
      "title_he": "תנאי שיווי המשקל הסטטי",
      "level_min": "university",
      "body_en_md": "## Two Conditions for Static Equilibrium\n\nA rigid body is in **static equilibrium** when it is neither translating nor rotating. This requires both:\n\n$$\\boxed{\\sum \\vec{F} = 0 \\quad \\text{and} \\quad \\sum \\vec{\\tau} = 0}$$\n\nIn 2-D (x-y plane), these expand to three scalar equations:\n$$\\sum F_x = 0, \\qquad \\sum F_y = 0, \\qquad \\sum \\tau_z = 0.$$\n\n**Key insight:** $\\sum\\vec{\\tau} = 0$ holds about **any** pivot point — you are free to choose whichever pivot is most convenient. Choosing the pivot at the point where an unknown force acts **eliminates** that force from the torque equation entirely (since its moment arm is zero), greatly simplifying the algebra.\n\n**Strategy:**\n1. Draw a free-body diagram with all forces labeled.\n2. Choose a pivot to eliminate as many unknowns as possible.\n3. Write $\\sum\\tau = 0$ first (usually the most useful equation).\n4. Use $\\sum F_x = 0$ and $\\sum F_y = 0$ for remaining unknowns.\n\n**When to apply:** leaning ladders, beams supported at two points, trusses, crane arms, and any static structure.",
      "body_he_md": "## שני תנאים לשיווי משקל סטטי\n\nגוף קשיח נמצא ב**שיווי משקל סטטי** כאשר הוא אינו מתרגם ואינו מסתובב. הדבר מחייב:\n\n$$\\boxed{\\sum \\vec{F} = 0 \\quad \\text{ו-} \\quad \\sum \\vec{\\tau} = 0}$$\n\nבדו-ממד (מישור x-y), מתקבלות שלוש משוואות סקלריות:\n$$\\sum F_x = 0, \\qquad \\sum F_y = 0, \\qquad \\sum \\tau_z = 0.$$\n\n**תובנה מרכזית:** $\\sum\\vec{\\tau} = 0$ מתקיים ביחס לכל ציר סיבוב — אנו חופשיים לבחור את הציר הנוח ביותר. בחירת ציר הסיבוב בנקודה שבה פועל כוח לא-ידוע **מבטלת** את הכוח הזה ממשוואת המומנטים (זרוע מומנטו אפס), מה שמפשט מאוד את האלגברה.\n\n**אסטרטגיה:**\n1. צייר דיאגרמת גוף חופשי עם כל הכוחות.\n2. בחר ציר סיבוב שיבטל כמה שיותר נגלות.\n3. כתוב $\\sum\\tau = 0$ ראשון.\n4. השתמש ב-$\\sum F_x = 0$ ו-$\\sum F_y = 0$ לנגלות הנותרות."
    },
    {
      "id": "beam_worked_example",
      "title_en": "Worked Example — Beam with Hinge and Cable",
      "title_he": "דוגמה מלאה — קורה עם ציר ותיל",
      "level_min": "university",
      "body_en_md": "## Worked Example: Uniform Beam Supported by Hinge and Cable\n\n**Setup:** A uniform beam of mass $M$ and length $L$ is attached to a wall by a frictionless hinge at its left end (A). A cable makes angle $\\theta$ with the beam at the right end (B). An additional mass $m$ hangs from the midpoint. Find the cable tension $T$ and the hinge reaction force.\n\n**Free-body diagram forces:**\n- Weight of beam: $Mg$ downward at $x = L/2$\n- Weight of hanging mass: $mg$ downward at $x = L/2$\n- Cable tension: $T$ at angle $\\theta$ above beam at $x = L$\n- Hinge: unknown $H_x$ (horizontal) and $H_y$ (vertical) at $x = 0$\n\n**Step 1 — Torques about hinge (A):** The hinge forces have zero moment arm → eliminated.\n$$\\sum \\tau_A = T\\sin\\theta \\cdot L - Mg\\cdot\\frac{L}{2} - mg\\cdot\\frac{L}{2} = 0$$\n$$\\boxed{T = \\frac{(M+m)g}{2\\sin\\theta}}$$\n\n**Step 2 — Force balance:**\n$$\\sum F_x = 0: \\quad H_x - T\\cos\\theta = 0 \\implies H_x = T\\cos\\theta$$\n$$\\sum F_y = 0: \\quad H_y + T\\sin\\theta - Mg - mg = 0 \\implies H_y = (M+m)g - T\\sin\\theta = \\frac{(M+m)g}{2}$$\n\n**Hinge magnitude:** $|\\vec{H}| = \\sqrt{H_x^2 + H_y^2}$.\n\n**Physical check:** As $\\theta \\to 90°$ (vertical cable), $T \\to (M+m)g/2$ — the cable bears half the total weight, which makes sense by symmetry.",
      "body_he_md": "## דוגמה מלאה: קורה אחידה על ציר ותיל\n\n**ניסוח:** קורה אחידה בעלת מסה $M$ ואורך $L$ מחוברת לקיר ע\"י ציר חלק בקצה השמאלי (A). תיל בזווית $\\theta$ מהקורה מחובר לקצה הימני (B). מסה $m$ נתלית מנקודת האמצע. מצא את מתח התיל $T$ וכוח הציר.\n\n**כוחות בדיאגרמת גוף חופשי:**\n- משקל הקורה: $Mg$ כלפי מטה ב-$x = L/2$\n- משקל המסה: $mg$ כלפי מטה ב-$x = L/2$\n- מתח התיל: $T$ בזווית $\\theta$ מעל הקורה ב-$x = L$\n- ציר: $H_x$ (אופקי) ו-$H_y$ (אנכי) ב-$x = 0$\n\n**שלב 1 — מומנטים סביב הציר (A):** כוחות הציר בעלי זרוע מומנט אפס → מבוטלים.\n$$\\sum \\tau_A = T\\sin\\theta \\cdot L - Mg\\cdot\\frac{L}{2} - mg\\cdot\\frac{L}{2} = 0$$\n$$\\boxed{T = \\frac{(M+m)g}{2\\sin\\theta}}$$\n\n**שלב 2 — שיווי כוחות:**\n$$H_x = T\\cos\\theta, \\qquad H_y = \\frac{(M+m)g}{2}$$\n\n**בדיקה:** כאשר $\\theta \\to 90°$ (תיל אנכי), $T \\to (M+m)g/2$ — התיל נושא חצי מהמשקל הכולל, כפי שניתן לצפות מסימטריה."
    },
    {
      "id": "moment_of_inertia",
      "title_en": "Moment of Inertia and Rotational Dynamics",
      "title_he": "מומנט אינרציה ודינמיקה סיבובית",
      "level_min": "university",
      "body_en_md": "## Moment of Inertia — Definition\n\nThe **moment of inertia** is the rotational analog of mass:\n$$I = \\int r^2\\,dm$$\nwhere $r$ is the perpendicular distance from each mass element $dm$ to the rotation axis.\n\n**Key values (memorize these):**\n\n| Object | Axis | $I$ |\n|---|---|---|\n| Point mass $m$ | Distance $R$ from axis | $mR^2$ |\n| Uniform rod, mass $M$, length $L$ | Through center, ⊥ to rod | $\\frac{1}{12}ML^2$ |\n| Uniform rod, mass $M$, length $L$ | Through one end, ⊥ to rod | $\\frac{1}{3}ML^2$ |\n| Solid disk/cylinder, mass $M$, radius $R$ | Through center, along axis | $\\frac{1}{2}MR^2$ |\n| Solid sphere, mass $M$, radius $R$ | Through center | $\\frac{2}{5}MR^2$ |\n| Spherical shell, mass $M$, radius $R$ | Through center | $\\frac{2}{3}MR^2$ |\n\n**Parallel-axis theorem:** If $I_{cm}$ is the moment about the center of mass, then for any parallel axis at distance $d$:\n$$I = I_{cm} + Md^2$$\n\n## Newton's Second Law for Rotation\n\nThe rotational analog of $\\vec{F} = m\\vec{a}$ is:\n$$\\boxed{\\tau_{\\text{net}} = I\\alpha}$$\nwhere $\\alpha = d\\omega/dt$ is the angular acceleration.\n\n**Worked Example:** A uniform rod ($M$, $L$) pivots about one end. A horizontal force $F$ is applied at the midpoint. Find $\\alpha$.\n\nTorque: $\\tau = F \\cdot (L/2)$ (moment arm = $L/2$, force is perpendicular to rod which is horizontal so $\\sin 90° = 1$).\nMoment of inertia about end: $I = \\frac{1}{3}ML^2$.\n$$\\alpha = \\frac{\\tau}{I} = \\frac{F(L/2)}{ML^2/3} = \\frac{3F}{2ML}$$",
      "body_he_md": "## מומנט אינרציה — הגדרה\n\n**מומנט האינרציה** הוא האנלוג הסיבובי של המסה:\n$$I = \\int r^2\\,dm$$\nכאשר $r$ הוא המרחק הניצב מכל אלמנט מסה $dm$ לציר הסיבוב.\n\n**ערכים מרכזיים:**\n\n| גוף | ציר | $I$ |\n|---|---|---|\n| מסה נקודתית $m$ | מרחק $R$ מהציר | $mR^2$ |\n| מוט אחיד, $M$, $L$ | דרך מרכז, ⊥ למוט | $\\frac{1}{12}ML^2$ |\n| מוט אחיד, $M$, $L$ | דרך קצה, ⊥ למוט | $\\frac{1}{3}ML^2$ |\n| דיסק/גליל מלא, $M$, $R$ | דרך מרכז, לאורך ציר | $\\frac{1}{2}MR^2$ |\n| כדור מלא, $M$, $R$ | דרך מרכז | $\\frac{2}{5}MR^2$ |\n\n**משפט הציר המקביל:** אם $I_{cm}$ הוא מומנט סביב מרכז המסה, אזי לכל ציר מקביל במרחק $d$:\n$$I = I_{cm} + Md^2$$\n\n## חוק ניוטון השני לסיבוב\n\n$$\\boxed{\\tau_{\\text{net}} = I\\alpha}$$\n\n**דוגמה:** מוט אחיד ($M$, $L$) מסתובב סביב קצהו. כוח $F$ פועל בנקודת האמצע. מצא $\\alpha$.\n\nמומנט: $\\tau = F \\cdot (L/2)$. מומנט אינרציה: $I = \\frac{1}{3}ML^2$.\n$$\\alpha = \\frac{\\tau}{I} = \\frac{F(L/2)}{ML^2/3} = \\frac{3F}{2ML}$$"
    },
    {
      "id": "equilibrium_strategy",
      "title_en": "Problem-Solving Strategy and Pitfalls",
      "title_he": "אסטרטגיית פתרון ומלכודות נפוצות",
      "level_min": "university",
      "body_en_md": "## General Strategy for Statics Problems\n\n1. **Identify all forces** — weight (applied at CM), normal forces, friction, tension, hinge reactions.\n2. **Choose a pivot wisely** — place it where the most unknown forces act; their torques vanish.\n3. **Set up torque equation** — each force contributes $\\pm r F\\sin\\theta$; CCW positive.\n4. **Force equations** — two scalar equations give the remaining unknowns.\n5. **Check units and limits** — what happens as $\\theta \\to 0$? $\\theta \\to 90°$?\n\n## Common Errors\n\n- **Using wrong moment arm:** Always compute the perpendicular distance from the pivot to the line of action, not just $r$.\n- **Missing the weight of the beam:** A beam's own weight acts at its center of mass.\n- **Wrong sign for torque:** Decide on a consistent CCW = + convention before writing equations.\n- **Forgetting that equilibrium must hold about ALL pivots:** If you choose a second pivot and the equation is not satisfied, there is an error.\n- **Confusing $I\\alpha$ with statics:** The condition $\\tau_{\\text{net}} = I\\alpha$ applies to dynamics; for statics $\\alpha = 0$ so $\\tau_{\\text{net}} = 0$.",
      "body_he_md": "## אסטרטגיה כללית לבעיות סטטיקה\n\n1. **זהה את כל הכוחות** — משקל (פועל ב-CM), נורמליים, חיכוך, מתח, כוחות ציר.\n2. **בחר ציר סיבוב בחוכמה** — הצב אותו שם שפועלים הכי הרבה כוחות לא-ידועים; מומנטיהם מתבטלים.\n3. **כתוב משוואת מומנטים** — כל כוח תורם $\\pm r F\\sin\\theta$; CCW חיובי.\n4. **משוואות כוחות** — שתי משוואות סקלריות נותנות את הנגלות הנותרות.\n5. **בדוק יחידות וגבולות** — מה קורה כאשר $\\theta \\to 0$? $\\theta \\to 90°$?\n\n## שגיאות נפוצות\n\n- **זרוע מומנט שגויה:** חשב תמיד את המרחק הניצב מהציר לישר הכוח.\n- **שכחת משקל הקורה:** משקל הקורה פועל במרכז המסה שלה.\n- **סימן שגוי למומנט:** קבע CCW = + לפני כתיבת המשוואות.\n- **בלבול בין דינמיקה לסטטיקה:** בסטטיקה $\\alpha = 0$ ולכן $\\tau_{\\text{net}} = 0$."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A force of 10 N is applied at a point 0.4 m from a pivot. The angle between the position vector $\\vec{r}$ and the force $\\vec{F}$ is 150°. What is the magnitude of the torque about the pivot?",
      "body_he": "כוח של 10 N פועל בנקודה הנמצאת 0.4 m מציר סיבוב. הזווית בין וקטור המיקום $\\vec{r}$ לכוח $\\vec{F}$ היא 150°. מהו גודל המומנט סביב הציר?",
      "options": [
        {"id": "a", "text_en": "4.0 N·m", "text_he": "4.0 N·m", "correct": False},
        {"id": "b", "text_en": "2.0 N·m", "text_he": "2.0 N·m", "correct": True},
        {"id": "c", "text_en": "3.46 N·m", "text_he": "3.46 N·m", "correct": False},
        {"id": "d", "text_en": "0 N·m", "text_he": "0 N·m", "correct": False}
      ],
      "explanation_en": "$\\tau = rF\\sin\\theta = (0.4)(10)\\sin 150° = 4 \\times 0.5 = 2.0$ N·m. Note $\\sin 150° = \\sin 30° = 0.5$.",
      "explanation_he": "$\\tau = rF\\sin\\theta = (0.4)(10)\\sin 150° = 4 \\times 0.5 = 2.0$ N·m. שימו לב: $\\sin 150° = \\sin 30° = 0.5$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A uniform beam of mass $M = 8$ kg and length $L = 4$ m is hinged at the wall (left end). A cable at 30° above horizontal supports the right end. No additional masses. What is the cable tension $T$?",
      "body_he": "קורה אחידה בעלת מסה $M = 8$ kg ואורך $L = 4$ m מחוברת לקיר בציר (קצה שמאלי). תיל בזווית 30° מעל האופקי תומך בקצה הימני. אין מסות נוספות. מהו מתח התיל $T$?",
      "options": [
        {"id": "a", "text_en": "$T = 40$ N", "text_he": "$T = 40$ N", "correct": False},
        {"id": "b", "text_en": "$T = 78.4$ N", "text_he": "$T = 78.4$ N", "correct": True},
        {"id": "c", "text_en": "$T = 68$ N", "text_he": "$T = 68$ N", "correct": False},
        {"id": "d", "text_en": "$T = 39.2$ N", "text_he": "$T = 39.2$ N", "correct": False}
      ],
      "explanation_en": "Taking torques about the hinge: $T\\sin30°\\cdot L - Mg\\cdot(L/2)=0 \\Rightarrow T = Mg/(2\\sin30°) = (8)(9.8)/(2\\times0.5) = 78.4$ N.",
      "explanation_he": "מומנטים סביב הציר: $T\\sin30°\\cdot L - Mg\\cdot(L/2)=0 \\Rightarrow T = Mg/(2\\sin30°) = (8)(9.8)/(2\\times0.5) = 78.4$ N."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "When solving a beam equilibrium problem, why is it advantageous to choose the pivot at the hinge point (where the hinge force acts)?",
      "body_he": "בפתרון בעיית שיווי משקל של קורה, מדוע כדאי לבחור את ציר הסיבוב בנקודת הציר (שבה פועל כוח הציר)?",
      "options": [
        {"id": "a", "text_en": "Because the hinge force is the largest force in the problem.", "text_he": "כי כוח הציר הוא הכוח הגדול ביותר בבעיה.", "correct": False},
        {"id": "b", "text_en": "Because the hinge force passes through that point, so its torque is zero and it is eliminated from the torque equation.", "text_he": "כי כוח הציר עובר דרך אותה נקודה, ולכן מומנטו אפס והוא מבוטל ממשוואת המומנטים.", "correct": True},
        {"id": "c", "text_en": "Because the net torque is only zero when computed about the hinge.", "text_he": "כי מומנט הכוח הנטו הוא אפס רק כאשר מחשבים אותו סביב הציר.", "correct": False},
        {"id": "d", "text_en": "Because the weight of the beam acts at the hinge.", "text_he": "כי משקל הקורה פועל בנקודת הציר.", "correct": False}
      ],
      "explanation_en": "For a force acting at a point, its torque about that same point is zero (moment arm = 0). Placing the pivot there removes that unknown from the torque equation. Note: $\\sum\\tau = 0$ holds about ANY pivot — it is a theorem, not specific to one point.",
      "explanation_he": "כוח הפועל בנקודה מסוימת יוצר מומנט אפס סביב אותה נקודה (זרוע מומנט = 0). בחירת הציר שם מבטלת את הנגלה הזו ממשוואת המומנטים. הערה: $\\sum\\tau = 0$ מתקיים סביב כל ציר — זהו משפט, לא תכונה של נקודה מסוימת."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A uniform solid disk (mass $M$, radius $R$) and a uniform thin ring (mass $M$, radius $R$) are both rotating about their central axes. Which has the larger moment of inertia, and by what factor?",
      "body_he": "דיסק מלא אחיד (מסה $M$, רדיוס $R$) וטבעת דקה אחידה (מסה $M$, רדיוס $R$) מסתובבים שניהם סביב ציריהם המרכזיים. למי מומנט אינרציה גדול יותר, ובאיזה גורם?",
      "options": [
        {"id": "a", "text_en": "The disk, by factor 2", "text_he": "לדיסק, בגורם 2", "correct": False},
        {"id": "b", "text_en": "The ring, by factor 2", "text_he": "לטבעת, בגורם 2", "correct": True},
        {"id": "c", "text_en": "They are equal", "text_he": "הם שווים", "correct": False},
        {"id": "d", "text_en": "The ring, by factor 4", "text_he": "לטבעת, בגורם 4", "correct": False}
      ],
      "explanation_en": "Disk: $I = \\frac{1}{2}MR^2$. Ring (all mass at radius $R$): $I = MR^2$. The ring is larger by factor 2 because all its mass is at the maximum radius, whereas the disk's mass is distributed from 0 to $R$.",
      "explanation_he": "דיסק: $I = \\frac{1}{2}MR^2$. טבעת (כל המסה ברדיוס $R$): $I = MR^2$. לטבעת מומנט גדול פי 2 מהדיסק, כי כל מסתה נמצאת ברדיוס המקסימלי, בעוד שמסת הדיסק מפוזרת מ-0 עד $R$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A uniform rod of mass $M = 3$ kg and length $L = 1.2$ m is free to rotate about one end. A torque $\\tau = 7.2$ N·m is applied about that end. What is the angular acceleration $\\alpha$?",
      "body_he": "מוט אחיד בעל מסה $M = 3$ kg ואורך $L = 1.2$ m חופשי להסתובב סביב קצהו. מומנט כוח $\\tau = 7.2$ N·m מופעל סביב אותו קצה. מהו התאוצה הזוויתית $\\alpha$?",
      "options": [
        {"id": "a", "text_en": "$\\alpha = 2.0$ rad/s²", "text_he": "$\\alpha = 2.0$ rad/s²", "correct": False},
        {"id": "b", "text_en": "$\\alpha = 5.0$ rad/s²", "text_he": "$\\alpha = 5.0$ rad/s²", "correct": True},
        {"id": "c", "text_en": "$\\alpha = 3.0$ rad/s²", "text_he": "$\\alpha = 3.0$ rad/s²", "correct": False},
        {"id": "d", "text_en": "$\\alpha = 6.0$ rad/s²", "text_he": "$\\alpha = 6.0$ rad/s²", "correct": False}
      ],
      "explanation_en": "$I_{\\text{end}} = \\frac{1}{3}ML^2 = \\frac{1}{3}(3)(1.2)^2 = \\frac{1}{3}(3)(1.44) = 1.44$ kg·m². Then $\\alpha = \\tau/I = 7.2/1.44 = 5.0$ rad/s².",
      "explanation_he": "$I_{\\text{end}} = \\frac{1}{3}ML^2 = \\frac{1}{3}(3)(1.2)^2 = 1.44$ kg·m². אז $\\alpha = \\tau/I = 7.2/1.44 = 5.0$ rad/s²."
    }
  ]
})


# ─────────────────────────────────────────────────────────────────
# LESSON 2 — Simple Harmonic Motion
# ─────────────────────────────────────────────────────────────────
save({
  "id": "harmonic_oscillation",
  "subject": "university_physics_1",
  "title_en": "Harmonic Oscillations — SHM, Pendula, and Damping (University)",
  "title_he": "תנודות הרמוניות — SHM, מטוטלות ובלימה (אוניברסיטה)",
  "duration_min": 26,
  "type": "interactive",
  "level_min": "university",
  "agent_hints": "The central equation is $a = -\\omega^2 x$ — stress that this IS the definition of SHM, not a result derived from it. Students confuse $\\omega$ (angular frequency, rad/s) with $f$ (frequency, Hz); relate them via $\\omega = 2\\pi f$. For energy, insist students derive the velocity-position relation $v^2 = \\omega^2(A^2 - x^2)$ from energy conservation rather than memorizing it. The physical pendulum formula $\\omega = \\sqrt{MgL_{cm}/I_{pivot}}$ reduces to the simple pendulum when $I_{pivot} = mL^2$ (point mass) — show this explicitly.",
  "sections": [
    {
      "id": "shm_kinematics",
      "title_en": "Simple Harmonic Motion — Definition and Kinematics",
      "title_he": "תנועה הרמונית פשוטה — הגדרה וקינמטיקה",
      "level_min": "university",
      "body_en_md": "## Definition of SHM\n\nA particle undergoes **simple harmonic motion** (SHM) when its acceleration is proportional to its displacement from equilibrium and directed toward it:\n$$\\boxed{a = -\\omega^2 x}$$\nwhere $\\omega > 0$ is the **angular frequency** (rad/s). This is both the definition and the equation of motion.\n\n## Solution\n\nThe general solution to $\\ddot{x} = -\\omega^2 x$ is:\n$$\\boxed{x(t) = A\\cos(\\omega t + \\phi)}$$\nwhere:\n- $A > 0$ is the **amplitude** (maximum displacement)\n- $\\phi$ is the **phase constant** (determined by initial conditions)\n- $\\omega = 2\\pi f = 2\\pi/T$\n\n**Velocity and acceleration by differentiation:**\n$$v(t) = \\dot{x} = -A\\omega\\sin(\\omega t + \\phi)$$\n$$a(t) = \\ddot{x} = -A\\omega^2\\cos(\\omega t + \\phi) = -\\omega^2 x$$\n\n**Key relationships:**\n- $v_{\\max} = A\\omega$ (at $x = 0$)\n- $|a_{\\max}| = A\\omega^2$ (at $x = \\pm A$)\n- $v^2 + \\omega^2 x^2 = \\omega^2 A^2$ (from eliminating $t$)\n\n**Period and frequency:**\n$$T = \\frac{2\\pi}{\\omega}, \\qquad f = \\frac{\\omega}{2\\pi}$$",
      "body_he_md": "## הגדרת SHM\n\nחלקיק מבצע **תנועה הרמונית פשוטה** (SHM) כאשר תאוצתו פרופורציונלית לתזוזתו מנקודת שיווי המשקל ומופנית לעברה:\n$$\\boxed{a = -\\omega^2 x}$$\nכאשר $\\omega > 0$ הוא **התדירות הזוויתית** (rad/s). זוהי גם ההגדרה וגם משוואת התנועה.\n\n## פתרון\n\nהפתרון הכללי של $\\ddot{x} = -\\omega^2 x$ הוא:\n$$\\boxed{x(t) = A\\cos(\\omega t + \\phi)}$$\nכאשר:\n- $A > 0$ הוא ה**אמפליטודה** (תזוזה מרבית)\n- $\\phi$ הוא **קבוע הפאזה** (נקבע מתנאים התחלתיים)\n- $\\omega = 2\\pi f = 2\\pi/T$\n\n**מהירות ותאוצה על ידי גזירה:**\n$$v(t) = -A\\omega\\sin(\\omega t + \\phi), \\qquad a(t) = -A\\omega^2\\cos(\\omega t + \\phi) = -\\omega^2 x$$\n\n**יחסים מרכזיים:**\n- $v_{\\max} = A\\omega$ (ב-$x = 0$)\n- $|a_{\\max}| = A\\omega^2$ (ב-$x = \\pm A$)\n- $v^2 + \\omega^2 x^2 = \\omega^2 A^2$"
    },
    {
      "id": "spring_pendulum_systems",
      "title_en": "Spring-Mass System and Simple Pendulum",
      "title_he": "מערכת קפיץ-מסה ומטוטלת פשוטה",
      "level_min": "university",
      "body_en_md": "## Spring-Mass System\n\nFor a mass $m$ on a spring of constant $k$ (no friction), Newton's second law gives:\n$$m\\ddot{x} = -kx \\implies \\ddot{x} = -\\frac{k}{m}x$$\n\nComparing with $a = -\\omega^2 x$:\n$$\\boxed{\\omega = \\sqrt{\\frac{k}{m}}, \\qquad T = 2\\pi\\sqrt{\\frac{m}{k}}}$$\n\n**Note:** $T$ depends on $m$ and $k$, **not** on amplitude $A$ (isochronism).\n\n## Simple Pendulum (Small-Angle Approximation)\n\nFor a point mass $m$ on a string of length $L$, the tangential restoring force is $F_\\theta = -mg\\sin\\theta$. For small angles ($\\theta \\lesssim 15°$), $\\sin\\theta \\approx \\theta$ (radians):\n$$mL\\ddot{\\theta} = -mg\\theta \\implies \\ddot{\\theta} = -\\frac{g}{L}\\theta$$\n\nThis is SHM in $\\theta$ with:\n$$\\boxed{\\omega = \\sqrt{\\frac{g}{L}}, \\qquad T = 2\\pi\\sqrt{\\frac{L}{g}}}$$\n\nFor $\\theta > 15°$ the period increases (nonlinear correction): $T \\approx T_0\\left(1 + \\frac{\\theta_0^2}{16}\\right)$ for moderate amplitudes.\n\n**On the Moon** ($g_{\\text{Moon}} = g/6$): $T_{\\text{Moon}} = \\sqrt{6}\\,T_{\\text{Earth}}$ — period increases by $\\sqrt{6} \\approx 2.45$.",
      "body_he_md": "## מערכת קפיץ-מסה\n\nעבור מסה $m$ על קפיץ בקבוע $k$ (ללא חיכוך), חוק שני של ניוטון נותן:\n$$m\\ddot{x} = -kx \\implies \\ddot{x} = -\\frac{k}{m}x$$\n\nהשוואה עם $a = -\\omega^2 x$ נותנת:\n$$\\boxed{\\omega = \\sqrt{\\frac{k}{m}}, \\qquad T = 2\\pi\\sqrt{\\frac{m}{k}}}$$\n\n**הערה:** $T$ תלוי ב-$m$ וב-$k$, **לא** באמפליטודה $A$ (איזוכרוניות).\n\n## מטוטלת פשוטה (קירוב זוויות קטנות)\n\nעבור מסה נקודתית $m$ על חוט באורך $L$, לזוויות קטנות ($\\theta \\lesssim 15°$):\n$$\\ddot{\\theta} = -\\frac{g}{L}\\theta$$\n\nזוהי SHM ב-$\\theta$ עם:\n$$\\boxed{\\omega = \\sqrt{\\frac{g}{L}}, \\qquad T = 2\\pi\\sqrt{\\frac{L}{g}}}$$\n\n**על הירח** ($g_{\\text{ירח}} = g/6$): $T_{\\text{ירח}} = \\sqrt{6}\\,T_{\\text{כדה\"א}}$ — התקופה גדלה פי $\\sqrt{6}$."
    },
    {
      "id": "energy_shm",
      "title_en": "Energy in SHM",
      "title_he": "אנרגיה ב-SHM",
      "level_min": "university",
      "body_en_md": "## Energy Conservation in SHM\n\nFor a spring-mass system, the total mechanical energy is:\n$$E = \\frac{1}{2}mv^2 + \\frac{1}{2}kx^2 = \\text{const}$$\n\nAt maximum displacement ($x = A$, $v = 0$): $E = \\frac{1}{2}kA^2$.\nAt equilibrium ($x = 0$, $v = v_{\\max}$): $E = \\frac{1}{2}mv_{\\max}^2$.\n\nTherefore:\n$$\\boxed{E = \\frac{1}{2}kA^2 = \\frac{1}{2}mv_{\\max}^2}$$\n\nAt arbitrary position $x$:\n$$KE(x) = \\frac{1}{2}k(A^2 - x^2), \\qquad PE(x) = \\frac{1}{2}kx^2$$\n\n**Velocity-position relation** (useful shortcut):\n$$v = \\pm\\omega\\sqrt{A^2 - x^2}$$\n\nDerivation: $\\frac{1}{2}mv^2 = \\frac{1}{2}k(A^2-x^2)$, then divide by $m$ and use $k/m = \\omega^2$.\n\n**Average energies:** $\\langle KE\\rangle = \\langle PE\\rangle = E/2$ (equipartition in SHM).",
      "body_he_md": "## שימור אנרגיה ב-SHM\n\nעבור מערכת קפיץ-מסה, האנרגיה המכנית הכוללת:\n$$E = \\frac{1}{2}mv^2 + \\frac{1}{2}kx^2 = \\text{const}$$\n\nבתזוזה מרבית ($x = A$, $v = 0$): $E = \\frac{1}{2}kA^2$.\nבנקודת שיווי משקל ($x = 0$, $v = v_{\\max}$): $E = \\frac{1}{2}mv_{\\max}^2$.\n\n$$\\boxed{E = \\frac{1}{2}kA^2 = \\frac{1}{2}mv_{\\max}^2}$$\n\nבמיקום $x$ שרירותי:\n$$KE(x) = \\frac{1}{2}k(A^2 - x^2), \\qquad PE(x) = \\frac{1}{2}kx^2$$\n\n**יחס מהירות-מיקום:**\n$$v = \\pm\\omega\\sqrt{A^2 - x^2}$$\n\nגזירה: $\\frac{1}{2}mv^2 = \\frac{1}{2}k(A^2-x^2)$, חלוק ב-$m$ ושימוש ב-$k/m = \\omega^2$."
    },
    {
      "id": "damped_oscillations",
      "title_en": "Damped Oscillations",
      "title_he": "תנודות בלומות",
      "level_min": "university",
      "body_en_md": "## Damped SHM\n\nWith a linear drag force $F_{\\text{drag}} = -b\\dot{x}$, the equation of motion becomes:\n$$m\\ddot{x} + b\\dot{x} + kx = 0$$\n\nDefine $\\gamma = b/(2m)$ (damping coefficient) and $\\omega_0 = \\sqrt{k/m}$. The solution depends on the discriminant $\\gamma^2 - \\omega_0^2$:\n\n| Case | Condition | Solution |\n|---|---|---|\n| Underdamped | $\\gamma < \\omega_0$ | $x(t) = Ae^{-\\gamma t}\\cos(\\omega' t + \\phi)$, $\\omega' = \\sqrt{\\omega_0^2 - \\gamma^2}$ |\n| Critically damped | $\\gamma = \\omega_0$ | $x(t) = (C_1 + C_2 t)e^{-\\gamma t}$ |\n| Overdamped | $\\gamma > \\omega_0$ | $x(t) = e^{-\\gamma t}(C_1 e^{\\sqrt{\\gamma^2-\\omega_0^2}t} + C_2 e^{-\\sqrt{\\gamma^2-\\omega_0^2}t})$ |\n\n**Quality factor:** $Q = \\omega_0/(2\\gamma) = \\omega_0 m/b$. A high $Q$ means slow energy loss. For underdamped: energy decays as $E \\propto e^{-2\\gamma t}$.\n\n**Physical pendulum:** For a rigid body pivoting about a point at distance $L_{cm}$ from its CM:\n$$\\omega = \\sqrt{\\frac{MgL_{cm}}{I_{\\text{pivot}}}}, \\qquad T = 2\\pi\\sqrt{\\frac{I_{\\text{pivot}}}{MgL_{cm}}}$$",
      "body_he_md": "## SHM בלום\n\nעם כוח סחב ליניארי $F_{\\text{drag}} = -b\\dot{x}$, משוואת התנועה:\n$$m\\ddot{x} + b\\dot{x} + kx = 0$$\n\nנגדיר $\\gamma = b/(2m)$ (מקדם בלימה) ו-$\\omega_0 = \\sqrt{k/m}$. הפתרון תלוי בסימן $\\gamma^2 - \\omega_0^2$:\n\n| מקרה | תנאי | פתרון |\n|---|---|---|\n| תת-בלום | $\\gamma < \\omega_0$ | $x(t) = Ae^{-\\gamma t}\\cos(\\omega' t + \\phi)$, $\\omega' = \\sqrt{\\omega_0^2 - \\gamma^2}$ |\n| בלום קריטי | $\\gamma = \\omega_0$ | $x(t) = (C_1 + C_2 t)e^{-\\gamma t}$ |\n| יתר-בלום | $\\gamma > \\omega_0$ | אקספוננציאלי כפול |\n\n**גורם איכות:** $Q = \\omega_0/(2\\gamma)$. $Q$ גבוה — אנרגיה אובדת לאט.\n\n**מטוטלת פיזית (גוף קשיח):** לגוף קשיח המסתובב סביב נקודה במרחק $L_{cm}$ ממרכז המסה:\n$$\\omega = \\sqrt{\\frac{MgL_{cm}}{I_{\\text{pivot}}}}, \\qquad T = 2\\pi\\sqrt{\\frac{I_{\\text{pivot}}}{MgL_{cm}}}$$"
    },
    {
      "id": "shm_pitfalls",
      "title_en": "Key Distinctions and Common Errors",
      "title_he": "הבחנות מרכזיות ושגיאות נפוצות",
      "level_min": "university",
      "body_en_md": "## Important Distinctions\n\n- **$\\omega$ vs $f$ vs $T$:** $\\omega$ is in rad/s; $f = \\omega/(2\\pi)$ is in Hz; $T = 1/f$ is in seconds. Always check units.\n- **Amplitude independence:** For ideal SHM, period $T$ does not depend on $A$. This breaks down for large pendulum angles and for nonlinear springs.\n- **Phase constant $\\phi$:** Determined by initial position and velocity: $x_0 = A\\cos\\phi$, $v_0 = -A\\omega\\sin\\phi$.\n\n## Summary of Key Formulas\n\n| System | $\\omega$ | $T$ |\n|---|---|---|\n| Spring-mass | $\\sqrt{k/m}$ | $2\\pi\\sqrt{m/k}$ |\n| Simple pendulum | $\\sqrt{g/L}$ | $2\\pi\\sqrt{L/g}$ |\n| Physical pendulum | $\\sqrt{MgL_{cm}/I_{\\text{pivot}}}$ | $2\\pi\\sqrt{I_{\\text{pivot}}/(MgL_{cm})}$ |\n\n## Technion-Style Exam Note\n\nTypical exam problems combine energy and kinematics: e.g., \"A mass oscillates on a spring. At $x = 3$ cm the speed is 4 m/s; at $x = 5$ cm the speed is 2 m/s. Find $A$ and $\\omega$.\" Use $v^2 = \\omega^2(A^2 - x^2)$ twice and solve the system.",
      "body_he_md": "## הבחנות חשובות\n\n- **$\\omega$ לעומת $f$ לעומת $T$:** $\\omega$ ב-rad/s; $f = \\omega/(2\\pi)$ ב-Hz; $T = 1/f$ בשניות.\n- **אי-תלות באמפליטודה:** ל-SHM אידיאלי, התקופה $T$ אינה תלויה ב-$A$.\n- **קבוע הפאזה $\\phi$:** נקבע מתנאים התחלתיים: $x_0 = A\\cos\\phi$, $v_0 = -A\\omega\\sin\\phi$.\n\n## סיכום נוסחאות\n\n| מערכת | $\\omega$ | $T$ |\n|---|---|---|\n| קפיץ-מסה | $\\sqrt{k/m}$ | $2\\pi\\sqrt{m/k}$ |\n| מטוטלת פשוטה | $\\sqrt{g/L}$ | $2\\pi\\sqrt{L/g}$ |\n| מטוטלת פיזית | $\\sqrt{MgL_{cm}/I_{\\text{pivot}}}$ | $2\\pi\\sqrt{I_{\\text{pivot}}/(MgL_{cm})}$ |"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A block of mass $m = 0.5$ kg oscillates on a spring with $k = 200$ N/m. What is the angular frequency $\\omega$ and period $T$?",
      "body_he": "בלוק בעל מסה $m = 0.5$ kg מתנדנד על קפיץ עם $k = 200$ N/m. מהי התדירות הזוויתית $\\omega$ והתקופה $T$?",
      "options": [
        {"id": "a", "text_en": "$\\omega = 20$ rad/s, $T \\approx 0.314$ s", "text_he": "$\\omega = 20$ rad/s, $T \\approx 0.314$ s", "correct": True},
        {"id": "b", "text_en": "$\\omega = 10$ rad/s, $T \\approx 0.628$ s", "text_he": "$\\omega = 10$ rad/s, $T \\approx 0.628$ s", "correct": False},
        {"id": "c", "text_en": "$\\omega = 400$ rad/s, $T \\approx 0.016$ s", "text_he": "$\\omega = 400$ rad/s, $T \\approx 0.016$ s", "correct": False},
        {"id": "d", "text_en": "$\\omega = 20$ rad/s, $T \\approx 0.628$ s", "text_he": "$\\omega = 20$ rad/s, $T \\approx 0.628$ s", "correct": False}
      ],
      "explanation_en": "$\\omega = \\sqrt{k/m} = \\sqrt{200/0.5} = \\sqrt{400} = 20$ rad/s. $T = 2\\pi/\\omega = 2\\pi/20 \\approx 0.314$ s.",
      "explanation_he": "$\\omega = \\sqrt{k/m} = \\sqrt{200/0.5} = \\sqrt{400} = 20$ rad/s. $T = 2\\pi/\\omega = 2\\pi/20 \\approx 0.314$ s."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A spring-mass system has $k = 50$ N/m, $m = 2$ kg, and amplitude $A = 0.1$ m. What is the kinetic energy when $x = 0.06$ m?",
      "body_he": "מערכת קפיץ-מסה: $k = 50$ N/m, $m = 2$ kg, אמפליטודה $A = 0.1$ m. מהי האנרגיה הקינטית כאשר $x = 0.06$ m?",
      "options": [
        {"id": "a", "text_en": "$KE = 0.25$ J", "text_he": "$KE = 0.25$ J", "correct": False},
        {"id": "b", "text_en": "$KE = 0.16$ J", "text_he": "$KE = 0.16$ J", "correct": True},
        {"id": "c", "text_en": "$KE = 0.09$ J", "text_he": "$KE = 0.09$ J", "correct": False},
        {"id": "d", "text_en": "$KE = 0.50$ J", "text_he": "$KE = 0.50$ J", "correct": False}
      ],
      "explanation_en": "$E = \\frac{1}{2}kA^2 = \\frac{1}{2}(50)(0.01) = 0.25$ J. $PE = \\frac{1}{2}kx^2 = \\frac{1}{2}(50)(0.0036) = 0.09$ J. $KE = E - PE = 0.25 - 0.09 = 0.16$ J.",
      "explanation_he": "$E = \\frac{1}{2}kA^2 = \\frac{1}{2}(50)(0.01) = 0.25$ J. $PE = \\frac{1}{2}kx^2 = \\frac{1}{2}(50)(0.0036) = 0.09$ J. $KE = E - PE = 0.25 - 0.09 = 0.16$ J."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "A simple pendulum has period $T = 2$ s on Earth ($g = 9.8$ m/s²). What is its period on the Moon where $g_{\\text{Moon}} = 1.63$ m/s²?",
      "body_he": "למטוטלת פשוטה תקופה $T = 2$ s על כדור הארץ ($g = 9.8$ m/s²). מהי תקופתה על הירח שם $g_{\\text{ירח}} = 1.63$ m/s²?",
      "options": [
        {"id": "a", "text_en": "$T_{\\text{Moon}} \\approx 4.9$ s", "text_he": "$T_{\\text{ירח}} \\approx 4.9$ s", "correct": True},
        {"id": "b", "text_en": "$T_{\\text{Moon}} \\approx 0.33$ s", "text_he": "$T_{\\text{ירח}} \\approx 0.33$ s", "correct": False},
        {"id": "c", "text_en": "$T_{\\text{Moon}} \\approx 12$ s", "text_he": "$T_{\\text{ירח}} \\approx 12$ s", "correct": False},
        {"id": "d", "text_en": "$T_{\\text{Moon}} = 2$ s (unchanged)", "text_he": "$T_{\\text{ירח}} = 2$ s (ללא שינוי)", "correct": False}
      ],
      "explanation_en": "$T \\propto 1/\\sqrt{g}$, so $T_{\\text{Moon}}/T_{\\text{Earth}} = \\sqrt{g_{\\text{Earth}}/g_{\\text{Moon}}} = \\sqrt{9.8/1.63} \\approx \\sqrt{6.01} \\approx 2.45$. Thus $T_{\\text{Moon}} \\approx 2 \\times 2.45 \\approx 4.9$ s.",
      "explanation_he": "$T \\propto 1/\\sqrt{g}$, לכן $T_{\\text{ירח}}/T_{\\text{כדה\"א}} = \\sqrt{g_{\\text{כדה\"א}}/g_{\\text{ירח}}} = \\sqrt{9.8/1.63} \\approx 2.45$. כלומר $T_{\\text{ירח}} \\approx 4.9$ s."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "An oscillator has damping coefficient $\\gamma = 5$ s⁻¹ and natural frequency $\\omega_0 = 3$ rad/s. Which type of damping is this?",
      "body_he": "למתנד מקדם בלימה $\\gamma = 5$ s⁻¹ ותדירות טבעית $\\omega_0 = 3$ rad/s. איזה סוג בלימה זה?",
      "options": [
        {"id": "a", "text_en": "Underdamped, because $\\gamma < \\omega_0$", "text_he": "תת-בלום, כי $\\gamma < \\omega_0$", "correct": False},
        {"id": "b", "text_en": "Critically damped, because $\\gamma = \\omega_0$", "text_he": "בלום קריטי, כי $\\gamma = \\omega_0$", "correct": False},
        {"id": "c", "text_en": "Overdamped, because $\\gamma > \\omega_0$", "text_he": "יתר-בלום, כי $\\gamma > \\omega_0$", "correct": True},
        {"id": "d", "text_en": "Underdamped, because $\\gamma > \\omega_0$", "text_he": "תת-בלום, כי $\\gamma > \\omega_0$", "correct": False}
      ],
      "explanation_en": "Compare $\\gamma = 5$ s⁻¹ with $\\omega_0 = 3$ rad/s: since $\\gamma > \\omega_0$, the system is overdamped. It returns to equilibrium without oscillating, exponentially.",
      "explanation_he": "מַשְׁוִים $\\gamma = 5$ s⁻¹ עם $\\omega_0 = 3$ rad/s: מאחר ש-$\\gamma > \\omega_0$, המערכת היא יתר-בלומה. היא חוזרת לשיווי המשקל ללא תנודות, בצורה אקספוננציאלית."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A uniform rod of mass $M$ and length $L$ oscillates as a physical pendulum, pivoting about one end. What is its period?",
      "body_he": "מוט אחיד בעל מסה $M$ ואורך $L$ מתנדנד כמטוטלת פיזית, ומסתובב סביב קצהו. מהי תקופתו?",
      "options": [
        {"id": "a", "text_en": "$T = 2\\pi\\sqrt{\\frac{L}{g}}$", "text_he": "$T = 2\\pi\\sqrt{\\frac{L}{g}}$", "correct": False},
        {"id": "b", "text_en": "$T = 2\\pi\\sqrt{\\frac{2L}{3g}}$", "text_he": "$T = 2\\pi\\sqrt{\\frac{2L}{3g}}$", "correct": True},
        {"id": "c", "text_en": "$T = 2\\pi\\sqrt{\\frac{L}{2g}}$", "text_he": "$T = 2\\pi\\sqrt{\\frac{L}{2g}}$", "correct": False},
        {"id": "d", "text_en": "$T = 2\\pi\\sqrt{\\frac{L}{3g}}$", "text_he": "$T = 2\\pi\\sqrt{\\frac{L}{3g}}$", "correct": False}
      ],
      "explanation_en": "$I_{\\text{pivot}} = \\frac{1}{3}ML^2$ (rod about one end); $L_{cm} = L/2$ (CM at midpoint). $T = 2\\pi\\sqrt{I_{\\text{pivot}}/(MgL_{cm})} = 2\\pi\\sqrt{(ML^2/3)/(Mg\\cdot L/2)} = 2\\pi\\sqrt{2L/(3g)}$.",
      "explanation_he": "$I_{\\text{pivot}} = \\frac{1}{3}ML^2$ (מוט סביב קצה); $L_{cm} = L/2$ (מרכז מסה באמצע). $T = 2\\pi\\sqrt{I_{\\text{pivot}}/(MgL_{cm})} = 2\\pi\\sqrt{(ML^2/3)/(Mg\\cdot L/2)} = 2\\pi\\sqrt{2L/(3g)}$."
    }
  ]
})


# ─────────────────────────────────────────────────────────────────
# LESSON 3 — Fluids: Hydrostatics & Hydrodynamics
# ─────────────────────────────────────────────────────────────────
save({
  "id": "fluids_hydrostatics",
  "subject": "university_physics_1",
  "title_en": "Fluids — Hydrostatics and Bernoulli's Equation (University)",
  "title_he": "נוזלים — הידרוסטטיקה ומשוואת ברנולי (אוניברסיטה)",
  "duration_min": 26,
  "type": "interactive",
  "level_min": "university",
  "agent_hints": "Archimedes' principle confuses students because it only depends on the displaced fluid volume, not the object's shape or composition. Drill: submerged volume = object volume × (ρ_obj/ρ_fluid) for floating objects. Bernoulli's equation is energy-per-unit-volume conservation along a streamline — emphasize the three terms: static pressure, dynamic pressure (½ρv²), and gravitational pressure (ρgh). The Venturi meter and Torricelli's theorem are direct applications worth deriving in full.",
  "sections": [
    {
      "id": "pressure_hydrostatics",
      "title_en": "Pressure and Hydrostatic Pressure",
      "title_he": "לחץ ולחץ הידרוסטטי",
      "level_min": "university",
      "body_en_md": "## Pressure\n\n**Pressure** is force per unit area:\n$$P = \\frac{F}{A}$$\n**Units:** Pascal (Pa) = N/m²; also bar, atm ($1\\,\\text{atm} = 101{,}325$ Pa).\n\nPressure in a fluid at rest acts equally in all directions at any point (Pascal's law).\n\n## Hydrostatic Pressure\n\nConsider a column of fluid of density $\\rho$ (assumed constant, i.e., incompressible). The pressure at depth $h$ below the surface:\n$$\\boxed{P = P_0 + \\rho g h}$$\nwhere $P_0$ is the pressure at the surface.\n\n**Derivation:** For a horizontal fluid slice of area $A$ and thickness $dh$, weight = $\\rho g A\\,dh$, so $dP = \\rho g\\,dh$. Integrating from 0 to $h$: $P = P_0 + \\rho g h$.\n\n**Pascal's Principle:** Any change in pressure applied to a fluid is transmitted undiminished to every part of the fluid. This is the basis of hydraulic systems: $F_2 = F_1(A_2/A_1)$ — a small force on a small piston generates a large force on a large piston.\n\n**Gauge pressure:** $P_{\\text{gauge}} = P - P_{\\text{atm}} = \\rho g h$ (pressure above atmospheric).",
      "body_he_md": "## לחץ\n\n**לחץ** הוא כוח ליחידת שטח:\n$$P = \\frac{F}{A}$$\n**יחידות:** פסקל (Pa) = N/m².\n\nלחץ בנוזל במנוחה פועל שווה בכל הכיוונים (עקרון פסקל).\n\n## לחץ הידרוסטטי\n\nלנוזל בעל צפיפות $\\rho$ (בלתי דחיס), הלחץ בעומק $h$ מתחת לפני השטח:\n$$\\boxed{P = P_0 + \\rho g h}$$\nכאשר $P_0$ הוא הלחץ בפני השטח.\n\n**גזירה:** לפרוסה אופקית בעלת שטח $A$ ועובי $dh$: $dP = \\rho g\\,dh$. אינטגרציה מ-0 עד $h$: $P = P_0 + \\rho g h$.\n\n**עיקרון פסקל:** שינוי לחץ המוחל על נוזל מועבר ללא הפחתה לכל חלק של הנוזל. בסיס מערכות הידראוליות: $F_2 = F_1(A_2/A_1)$.\n\n**לחץ מד:** $P_{\\text{מד}} = P - P_{\\text{אטמ}} = \\rho g h$."
    },
    {
      "id": "archimedes",
      "title_en": "Archimedes' Principle and Buoyancy",
      "title_he": "עיקרון ארכימדס וכוח הציפה",
      "level_min": "university",
      "body_en_md": "## Archimedes' Principle\n\nAn object submerged (fully or partially) in a fluid experiences an **upward buoyant force** equal to the weight of the displaced fluid:\n$$\\boxed{F_b = \\rho_{\\text{fluid}}\\,g\\,V_{\\text{submerged}}}$$\n\n**Derivation:** The net upward pressure force on the bottom minus top of the object equals $\\rho_{\\text{fluid}} g V_{\\text{sub}}$.\n\n## Floating Condition\n\nFor an object floating in equilibrium, $F_b = W_{\\text{object}}$:\n$$\\rho_{\\text{fluid}}\\,g\\,V_{\\text{sub}} = \\rho_{\\text{obj}}\\,g\\,V_{\\text{obj}}$$\n$$\\boxed{\\frac{V_{\\text{sub}}}{V_{\\text{obj}}} = \\frac{\\rho_{\\text{obj}}}{\\rho_{\\text{fluid}}}}$$\n\n**Examples:**\n- Ice ($\\rho = 917$ kg/m³) in water ($\\rho = 1000$ kg/m³): fraction submerged = 91.7% — matches the well-known iceberg result.\n- An object with $\\rho_{\\text{obj}} > \\rho_{\\text{fluid}}$ sinks; $\\rho_{\\text{obj}} < \\rho_{\\text{fluid}}$ floats partially; $\\rho_{\\text{obj}} = \\rho_{\\text{fluid}}$ is neutrally buoyant.\n\n**Worked Example:** A wooden block ($\\rho_1 = 600$ kg/m³) floats in oil ($\\rho_2 = 800$ kg/m³). What fraction is submerged?\n$$f = \\frac{\\rho_1}{\\rho_2} = \\frac{600}{800} = 0.75 \\implies 75\\%\\text{ submerged}$$",
      "body_he_md": "## עיקרון ארכימדס\n\nעצם מוטבל (חלקית או מלאה) בנוזל חווה **כוח ציפה כלפי מעלה** השווה למשקל הנוזל שנעקר:\n$$\\boxed{F_b = \\rho_{\\text{נוזל}}\\,g\\,V_{\\text{מוטבל}}}$$\n\n## תנאי ציפה\n\nלעצם הצף בשיווי משקל, $F_b = W_{\\text{עצם}}$:\n$$\\boxed{\\frac{V_{\\text{מוטבל}}}{V_{\\text{עצם}}} = \\frac{\\rho_{\\text{עצם}}}{\\rho_{\\text{נוזל}}}}$$\n\n**דוגמאות:**\n- קרח ($\\rho = 917$ kg/m³) במים ($\\rho = 1000$ kg/m³): שבר מוטבל = 91.7%.\n- עצם עם $\\rho_{\\text{עצם}} > \\rho_{\\text{נוזל}}$ שוקע; $\\rho_{\\text{עצם}} < \\rho_{\\text{נוזל}}$ צף חלקית.\n\n**דוגמה מלאה:** בלוק עץ ($\\rho_1 = 600$ kg/m³) צף בשמן ($\\rho_2 = 800$ kg/m³). כמה אחוז מוטבל?\n$$f = \\frac{\\rho_1}{\\rho_2} = \\frac{600}{800} = 0.75 \\implies 75\\%$$"
    },
    {
      "id": "continuity",
      "title_en": "Ideal Fluid Flow and the Continuity Equation",
      "title_he": "זרימת נוזל אידיאלי ומשוואת הרציפות",
      "level_min": "university",
      "body_en_md": "## Ideal (Inviscid, Incompressible) Fluid\n\nAssumptions for ideal flow:\n1. **Incompressible:** $\\rho = $ constant throughout the fluid.\n2. **Inviscid:** no viscosity (no internal friction).\n3. **Steady:** flow pattern does not change with time.\n4. **Irrotational:** no vortices (needed for Bernoulli's full derivation).\n\n## Continuity Equation\n\nConservation of mass for incompressible flow in a pipe of varying cross-section:\n$$\\boxed{A_1 v_1 = A_2 v_2}$$\nThe quantity $Q = Av$ is the **volumetric flow rate** (m³/s), constant throughout.\n\n**Physical interpretation:** if the pipe narrows, the fluid must speed up to maintain the same volume per second.\n\n**Worked Example:** Water flows through a pipe of radius $r_1 = 0.1$ m at speed $v_1 = 2$ m/s. The pipe narrows to $r_2 = 0.05$ m. Find $v_2$:\n$$A_1 v_1 = A_2 v_2 \\implies \\pi r_1^2 v_1 = \\pi r_2^2 v_2$$\n$$v_2 = v_1\\left(\\frac{r_1}{r_2}\\right)^2 = 2\\left(\\frac{0.1}{0.05}\\right)^2 = 2 \\times 4 = 8 \\text{ m/s}$$",
      "body_he_md": "## נוזל אידיאלי (בלתי צמיג, בלתי דחיס)\n\nהנחות:\n1. **בלתי דחיס:** $\\rho = $ const.\n2. **בלתי צמיג:** ללא חיכוך פנימי.\n3. **יציב:** דפוס הזרימה אינו משתנה בזמן.\n4. **בלתי סיבובי.**\n\n## משוואת הרציפות\n\nשימור מסה לזרימה בלתי דחיסה בצינור בחתך משתנה:\n$$\\boxed{A_1 v_1 = A_2 v_2}$$\nהגודל $Q = Av$ הוא **ספיקת הנפח** (m³/s), קבועה לאורך הצינור.\n\n**דוגמה מלאה:** מים זורמים בצינור ברדיוס $r_1 = 0.1$ m במהירות $v_1 = 2$ m/s. הצינור מצטמצם ל-$r_2 = 0.05$ m. מצא $v_2$:\n$$v_2 = v_1\\left(\\frac{r_1}{r_2}\\right)^2 = 2 \\times 4 = 8 \\text{ m/s}$$"
    },
    {
      "id": "bernoulli",
      "title_en": "Bernoulli's Equation",
      "title_he": "משוואת ברנולי",
      "level_min": "university",
      "body_en_md": "## Bernoulli's Equation\n\nFor steady, incompressible, inviscid flow along a streamline:\n$$\\boxed{P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}}$$\n\n**Interpretation:** This is energy conservation per unit volume:\n- $P$: static pressure (potential energy per unit volume from pressure)\n- $\\frac{1}{2}\\rho v^2$: dynamic pressure (kinetic energy per unit volume)\n- $\\rho g h$: gravitational potential energy per unit volume\n\n**Derivation sketch:** Apply the work-energy theorem to a fluid parcel along a streamline. The work done by pressure forces equals the change in kinetic plus potential energy.\n\n## Venturi Meter Application\n\nFor a horizontal pipe ($h = $ const), Bernoulli gives:\n$$P_1 + \\frac{1}{2}\\rho v_1^2 = P_2 + \\frac{1}{2}\\rho v_2^2$$\n\nCombined with $A_1 v_1 = A_2 v_2$ (continuity):\n$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2) = \\frac{1}{2}\\rho v_1^2\\left[\\left(\\frac{A_1}{A_2}\\right)^2 - 1\\right]$$\n\nMeasuring the pressure difference $\\Delta P$ gives the flow speed $v_1$ — this is the Venturi principle.\n\n**Continued example:** $r_1 = 0.1$ m, $v_1 = 2$ m/s, $r_2 = 0.05$ m, $v_2 = 8$ m/s, $\\rho = 1000$ kg/m³:\n$$\\Delta P = P_1 - P_2 = \\frac{1}{2}(1000)(8^2 - 2^2) = 500 \\times 60 = 30{,}000 \\text{ Pa}$$",
      "body_he_md": "## משוואת ברנולי\n\nלזרימה יציבה, בלתי דחיסה ובלתי צמיגה לאורך קו זרם:\n$$\\boxed{P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}}$$\n\n**פרשנות:** שימור אנרגיה ליחידת נפח:\n- $P$: לחץ סטטי\n- $\\frac{1}{2}\\rho v^2$: לחץ דינמי (אנרגיה קינטית/נפח)\n- $\\rho g h$: אנרגיה פוטנציאלית גרביטציונית/נפח\n\n## יישום: מד ונטורי\n\nלצינור אופקי ($h = $ const):\n$$P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2)$$\n\nבשילוב עם $A_1 v_1 = A_2 v_2$:\n$$\\Delta P = \\frac{1}{2}\\rho v_1^2\\left[\\left(\\frac{A_1}{A_2}\\right)^2 - 1\\right]$$\n\nמדידת הפרש הלחצים נותנת את מהירות הזרימה.\n\n**המשך דוגמה:** $r_1 = 0.1$ m, $v_1 = 2$ m/s, $r_2 = 0.05$ m, $v_2 = 8$ m/s:\n$$\\Delta P = \\frac{1}{2}(1000)(64 - 4) = 30{,}000 \\text{ Pa}$$"
    },
    {
      "id": "torricelli_applications",
      "title_en": "Torricelli's Theorem and Applications",
      "title_he": "משפט טוריצ'לי ויישומים",
      "level_min": "university",
      "body_en_md": "## Torricelli's Theorem\n\nA large open tank with water at height $h$ above a small hole at the bottom. Applying Bernoulli between the top surface (point 1) and the hole (point 2), with the same reference height for both:\n\n- Point 1: $P_1 = P_{\\text{atm}}$, $v_1 \\approx 0$ (large tank), $h_1 = h$\n- Point 2: $P_2 = P_{\\text{atm}}$, $v_2 = ?$, $h_2 = 0$\n\n$$P_{\\text{atm}} + 0 + \\rho g h = P_{\\text{atm}} + \\frac{1}{2}\\rho v_2^2 + 0$$\n$$\\boxed{v_2 = \\sqrt{2gh}}$$\n\nThis is the same speed as a free-falling object dropped from height $h$ — a beautiful connection to kinematics.\n\n## Airplane Lift (Qualitative)\n\nThe curved top of a wing forces air to travel faster over the top surface than the bottom. By Bernoulli, the faster-moving air has lower pressure. The pressure difference creates net upward lift. (Full treatment requires the Kutta-Joukowski theorem.)\n\n## Summary of Fluid Mechanics Results\n\n| Principle | Equation |\n|---|---|\n| Hydrostatic pressure | $P = P_0 + \\rho g h$ |\n| Archimedes | $F_b = \\rho_{\\text{fl}} g V_{\\text{sub}}$ |\n| Continuity | $A_1 v_1 = A_2 v_2$ |\n| Bernoulli | $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ |\n| Torricelli | $v = \\sqrt{2gh}$ |",
      "body_he_md": "## משפט טוריצ'לי\n\nמיכל גדול ופתוח עם מים בגובה $h$ מעל חור קטן בתחתיתו. נפעיל את ברנולי בין פני השטח העליונים לחור:\n\n$$P_{\\text{אטמ}} + 0 + \\rho g h = P_{\\text{אטמ}} + \\frac{1}{2}\\rho v^2 + 0$$\n$$\\boxed{v = \\sqrt{2gh}}$$\n\nזהו אותו מהירות שמשיג עצם הנופל חופשי מגובה $h$ — קשר יפה לקינמטיקה.\n\n## עילוי מטוסים (איכותי)\n\nהאוויר זורם מהר יותר מעל החלק העליון המעוגל של הכנף. לפי ברנולי, לחץ נמוך יותר → הפרש לחצים → עילוי כלפי מעלה.\n\n## סיכום תוצאות מכניקת נוזלים\n\n| עיקרון | משוואה |\n|---|---|\n| לחץ הידרוסטטי | $P = P_0 + \\rho g h$ |\n| ארכימדס | $F_b = \\rho_{\\text{נוזל}} g V_{\\text{מוטבל}}$ |\n| רציפות | $A_1 v_1 = A_2 v_2$ |\n| ברנולי | $P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{const}$ |\n| טוריצ'לי | $v = \\sqrt{2gh}$ |"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A diver is 15 m below the ocean surface. The atmospheric pressure is $1.013 \\times 10^5$ Pa and $\\rho_{\\text{seawater}} = 1025$ kg/m³. What is the absolute pressure at that depth?",
      "body_he": "צוללן נמצא 15 m מתחת לפני האוקיינוס. הלחץ האטמוספרי $1.013 \\times 10^5$ Pa ו-$\\rho_{\\text{מי ים}} = 1025$ kg/m³. מהו הלחץ המוחלט באותו עומק?",
      "options": [
        {"id": "a", "text_en": "$2.52 \\times 10^5$ Pa", "text_he": "$2.52 \\times 10^5$ Pa", "correct": True},
        {"id": "b", "text_en": "$1.51 \\times 10^5$ Pa", "text_he": "$1.51 \\times 10^5$ Pa", "correct": False},
        {"id": "c", "text_en": "$1.013 \\times 10^5$ Pa", "text_he": "$1.013 \\times 10^5$ Pa", "correct": False},
        {"id": "d", "text_en": "$3.04 \\times 10^5$ Pa", "text_he": "$3.04 \\times 10^5$ Pa", "correct": False}
      ],
      "explanation_en": "$P = P_0 + \\rho g h = 1.013\\times10^5 + (1025)(9.8)(15) = 1.013\\times10^5 + 1.507\\times10^5 = 2.52\\times10^5$ Pa.",
      "explanation_he": "$P = P_0 + \\rho g h = 1.013\\times10^5 + (1025)(9.8)(15) \\approx 2.52\\times10^5$ Pa."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A solid sphere of density $\\rho_s = 750$ kg/m³ is placed in water ($\\rho_w = 1000$ kg/m³). What fraction of its volume is submerged when it floats at equilibrium?",
      "body_he": "כדור מוצק בצפיפות $\\rho_s = 750$ kg/m³ מונח במים ($\\rho_w = 1000$ kg/m³). כמה מנפחו שקוע כאשר הוא צף בשיווי משקל?",
      "options": [
        {"id": "a", "text_en": "100% (sinks)", "text_he": "100% (שוקע)", "correct": False},
        {"id": "b", "text_en": "75%", "text_he": "75%", "correct": True},
        {"id": "c", "text_en": "25%", "text_he": "25%", "correct": False},
        {"id": "d", "text_en": "50%", "text_he": "50%", "correct": False}
      ],
      "explanation_en": "$V_{\\text{sub}}/V_{\\text{obj}} = \\rho_s/\\rho_w = 750/1000 = 0.75$. Since $\\rho_s < \\rho_w$, the object floats with 75% submerged.",
      "explanation_he": "$V_{\\text{מוטבל}}/V_{\\text{עצם}} = \\rho_s/\\rho_w = 750/1000 = 0.75$. מאחר ש-$\\rho_s < \\rho_w$, הכדור צף עם 75% שקוע."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "Water flows through a pipe with cross-sectional area $A_1 = 0.04$ m² at speed $v_1 = 3$ m/s. The pipe expands to area $A_2 = 0.12$ m². What is $v_2$?",
      "body_he": "מים זורמים בצינור עם שטח חתך $A_1 = 0.04$ m² במהירות $v_1 = 3$ m/s. הצינור מתרחב לשטח $A_2 = 0.12$ m². מהי $v_2$?",
      "options": [
        {"id": "a", "text_en": "$v_2 = 9$ m/s", "text_he": "$v_2 = 9$ m/s", "correct": False},
        {"id": "b", "text_en": "$v_2 = 1$ m/s", "text_he": "$v_2 = 1$ m/s", "correct": True},
        {"id": "c", "text_en": "$v_2 = 3$ m/s", "text_he": "$v_2 = 3$ m/s", "correct": False},
        {"id": "d", "text_en": "$v_2 = 0.33$ m/s", "text_he": "$v_2 = 0.33$ m/s", "correct": False}
      ],
      "explanation_en": "Continuity: $A_1 v_1 = A_2 v_2 \\Rightarrow v_2 = (0.04)(3)/(0.12) = 1$ m/s. When the pipe expands (larger $A$), the fluid slows down.",
      "explanation_he": "רציפות: $A_1 v_1 = A_2 v_2 \\Rightarrow v_2 = (0.04)(3)/(0.12) = 1$ m/s. כאשר הצינור מתרחב, הנוזל מואט."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "In a horizontal Venturi tube, water ($\\rho = 1000$ kg/m³) flows with $v_1 = 2$ m/s in the wide section and $v_2 = 6$ m/s in the narrow section. What is $P_1 - P_2$?",
      "body_he": "בצינור ונטורי אופקי, מים ($\\rho = 1000$ kg/m³) זורמים במהירות $v_1 = 2$ m/s בחלק הרחב ו-$v_2 = 6$ m/s בחלק הצר. מהו $P_1 - P_2$?",
      "options": [
        {"id": "a", "text_en": "$16{,}000$ Pa", "text_he": "$16{,}000$ Pa", "correct": True},
        {"id": "b", "text_en": "$32{,}000$ Pa", "text_he": "$32{,}000$ Pa", "correct": False},
        {"id": "c", "text_en": "$2{,}000$ Pa", "text_he": "$2{,}000$ Pa", "correct": False},
        {"id": "d", "text_en": "$8{,}000$ Pa", "text_he": "$8{,}000$ Pa", "correct": False}
      ],
      "explanation_en": "Bernoulli (horizontal): $P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2) = \\frac{1}{2}(1000)(36-4) = 500 \\times 32 = 16{,}000$ Pa.",
      "explanation_he": "ברנולי (אופקי): $P_1 - P_2 = \\frac{1}{2}\\rho(v_2^2 - v_1^2) = \\frac{1}{2}(1000)(36-4) = 16{,}000$ Pa."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "Using Torricelli's theorem, what is the speed of water exiting a small hole at the bottom of a tank in which the water level is $h = 5$ m above the hole? ($g = 9.8$ m/s²)",
      "body_he": "לפי משפט טוריצ'לי, מהי מהירות המים היוצאים מחור קטן בתחתית מיכל שבו פני המים גבוהים $h = 5$ m מעל החור? ($g = 9.8$ m/s²)",
      "options": [
        {"id": "a", "text_en": "$v \\approx 9.9$ m/s", "text_he": "$v \\approx 9.9$ m/s", "correct": True},
        {"id": "b", "text_en": "$v \\approx 7.0$ m/s", "text_he": "$v \\approx 7.0$ m/s", "correct": False},
        {"id": "c", "text_en": "$v \\approx 4.9$ m/s", "text_he": "$v \\approx 4.9$ m/s", "correct": False},
        {"id": "d", "text_en": "$v \\approx 14$ m/s", "text_he": "$v \\approx 14$ m/s", "correct": False}
      ],
      "explanation_en": "$v = \\sqrt{2gh} = \\sqrt{2(9.8)(5)} = \\sqrt{98} \\approx 9.9$ m/s.",
      "explanation_he": "$v = \\sqrt{2gh} = \\sqrt{2(9.8)(5)} = \\sqrt{98} \\approx 9.9$ m/s."
    }
  ]
})


# ─────────────────────────────────────────────────────────────────
# LESSON 4 — Center of Mass & Systems of Particles
# ─────────────────────────────────────────────────────────────────
save({
  "id": "center_of_mass_uni",
  "subject": "university_physics_1",
  "title_en": "Center of Mass and Systems of Particles — Calculus Treatment (University)",
  "title_he": "מרכז מסה ומערכות חלקיקים — גישה בחשבון אינטגרלי (אוניברסיטה)",
  "duration_min": 25,
  "type": "interactive",
  "level_min": "university",
  "agent_hints": "The key conceptual leap is Newton's 2nd law for a system: only external forces accelerate the CM — all internal forces cancel in pairs (Newton's 3rd law). Use this to explain why a person cannot move the CM of their own body by purely internal muscle forces. The rocket equation is subtle: stress that $M$ changes with time and the standard $F = ma$ form must be replaced by the momentum form $d(Mv)/dt = F_{ext}$, leading to the Tsiolkovsky equation. For CM integrals, always set up $dm = \\rho\\,dV$ (or $\\lambda\\,dx$ for 1-D) before integrating.",
  "sections": [
    {
      "id": "cm_discrete",
      "title_en": "Center of Mass — Discrete Systems",
      "title_he": "מרכז מסה — מערכות דיסקרטיות",
      "level_min": "university",
      "body_en_md": "## Definition for a Discrete System\n\nFor a system of $N$ particles with masses $m_i$ and position vectors $\\vec{r}_i$, the **center of mass** (CM) is:\n$$\\boxed{\\vec{r}_{cm} = \\frac{\\sum_{i=1}^N m_i \\vec{r}_i}{M_{\\text{total}}}}$$\nwhere $M_{\\text{total}} = \\sum_i m_i$.\n\nIn components:\n$$x_{cm} = \\frac{\\sum m_i x_i}{M}, \\qquad y_{cm} = \\frac{\\sum m_i y_i}{M}, \\qquad z_{cm} = \\frac{\\sum m_i z_i}{M}$$\n\n## Velocity and Momentum of the CM\n\n$$\\vec{v}_{cm} = \\frac{d\\vec{r}_{cm}}{dt} = \\frac{\\sum m_i \\vec{v}_i}{M} = \\frac{\\vec{p}_{\\text{total}}}{M}$$\n\nThe CM velocity is the total linear momentum divided by total mass.\n\n**Example:** Two particles: $m_1 = 2$ kg at $x_1 = 1$ m, $m_2 = 4$ kg at $x_2 = 4$ m:\n$$x_{cm} = \\frac{(2)(1) + (4)(4)}{2+4} = \\frac{18}{6} = 3 \\text{ m}$$\nNote the CM is closer to the heavier particle (as expected).",
      "body_he_md": "## הגדרה למערכת דיסקרטית\n\nעבור מערכת של $N$ חלקיקים עם מסות $m_i$ ווקטורי מיקום $\\vec{r}_i$, **מרכז המסה** (CM) הוא:\n$$\\boxed{\\vec{r}_{cm} = \\frac{\\sum_{i=1}^N m_i \\vec{r}_i}{M_{\\text{כולל}}}}$$\nכאשר $M_{\\text{כולל}} = \\sum_i m_i$.\n\n## מהירות ותנע של ה-CM\n\n$$\\vec{v}_{cm} = \\frac{\\sum m_i \\vec{v}_i}{M} = \\frac{\\vec{p}_{\\text{כולל}}}{M}$$\n\nמהירות ה-CM היא התנע הכולל חלקי המסה הכוללת.\n\n**דוגמה:** שני חלקיקים: $m_1 = 2$ kg ב-$x_1 = 1$ m, $m_2 = 4$ kg ב-$x_2 = 4$ m:\n$$x_{cm} = \\frac{(2)(1) + (4)(4)}{6} = \\frac{18}{6} = 3 \\text{ m}$$"
    },
    {
      "id": "cm_continuous",
      "title_en": "Center of Mass — Continuous Bodies",
      "title_he": "מרכז מסה — גופים רציפים",
      "level_min": "university",
      "body_en_md": "## Integral Formula\n\nFor a continuous body with mass element $dm$:\n$$\\boxed{\\vec{r}_{cm} = \\frac{1}{M}\\int \\vec{r}\\,dm}$$\n\nIn 1-D with linear density $\\lambda(x)$ [kg/m]: $dm = \\lambda(x)\\,dx$.\nIn 2-D with surface density $\\sigma$ [kg/m²]: $dm = \\sigma\\,dA$.\nIn 3-D with volume density $\\rho$ [kg/m³]: $dm = \\rho\\,dV$.\n\n## Derivation 1 — Uniform Rod of Length $L$\n\nPlace the rod along the x-axis from 0 to $L$. Uniform linear density $\\lambda = M/L$.\n$$x_{cm} = \\frac{1}{M}\\int_0^L x\\,\\lambda\\,dx = \\frac{\\lambda}{M}\\int_0^L x\\,dx = \\frac{\\lambda}{M}\\cdot\\frac{L^2}{2} = \\frac{(M/L)}{M}\\cdot\\frac{L^2}{2} = \\boxed{\\frac{L}{2}}$$\nThe CM is at the midpoint — as expected by symmetry.\n\n## Derivation 2 — Right Triangle\n\nFor a uniform right triangle with base $b$ along x-axis and height $h$ along y-axis. The width at height $y$ is $w(y) = b(1 - y/h)$ (linear taper).\n$$y_{cm} = \\frac{1}{M}\\int_0^h y\\,\\sigma\\,w(y)\\,dy = \\frac{\\sigma b}{M}\\int_0^h y\\left(1-\\frac{y}{h}\\right)dy$$\nEvaluating: $\\int_0^h y(1-y/h)dy = h^2/2 - h^2/3 = h^2/6$.\nWith $M = \\frac{1}{2}\\sigma b h$: $y_{cm} = \\frac{\\sigma b}{M}\\cdot\\frac{h^2}{6} = \\frac{h}{3}$.\n$$\\boxed{y_{cm} = \\frac{h}{3}}\\text{ (one-third from the base)}$$",
      "body_he_md": "## נוסחת האינטגרל\n\nלגוף רציף עם אלמנט מסה $dm$:\n$$\\boxed{\\vec{r}_{cm} = \\frac{1}{M}\\int \\vec{r}\\,dm}$$\n\nב-1D עם צפיפות ליניארית $\\lambda(x)$: $dm = \\lambda(x)\\,dx$.\nב-2D עם צפיפות שטחית $\\sigma$: $dm = \\sigma\\,dA$.\nב-3D עם צפיפות נפחית $\\rho$: $dm = \\rho\\,dV$.\n\n## גזירה 1 — מוט אחיד באורך $L$\n\nהמוט לאורך ציר x מ-0 עד $L$. $\\lambda = M/L$.\n$$x_{cm} = \\frac{1}{M}\\int_0^L x\\lambda\\,dx = \\frac{\\lambda}{M}\\cdot\\frac{L^2}{2} = \\boxed{\\frac{L}{2}}$$\n\n## גזירה 2 — משולש ישר-זווית\n\nמשולש אחיד בעל בסיס $b$ (לאורך x) וגובה $h$ (לאורך y):\n$$y_{cm} = \\frac{h}{3} \\qquad \\text{(שליש מהבסיס)}$$"
    },
    {
      "id": "newtons_law_system",
      "title_en": "Newton's Second Law for a System",
      "title_he": "חוק ניוטון השני למערכת חלקיקים",
      "level_min": "university",
      "body_en_md": "## $\\vec{F}_{ext} = M\\vec{a}_{cm}$\n\nDifferentiate $M\\vec{v}_{cm} = \\vec{p}_{\\text{total}}$ with respect to time:\n$$\\frac{d\\vec{p}_{\\text{total}}}{dt} = \\sum_i \\frac{d\\vec{p}_i}{dt} = \\sum_i \\vec{F}_i^{\\text{total}}$$\n\nThe forces on particle $i$ consist of external forces $\\vec{F}_i^{\\text{ext}}$ and internal forces $\\vec{F}_{ij}$ from other particles. By Newton's 3rd law, internal forces cancel in pairs:\n$$\\sum_{i \\ne j}\\vec{F}_{ij} = 0$$\n\nTherefore:\n$$\\boxed{\\vec{F}_{\\text{ext}} = M\\vec{a}_{cm}}$$\n\n**Consequence:** Only external forces can change the motion of the CM. A system of particles with no external forces has its CM moving at constant velocity (or at rest).\n\n## Conservation of Momentum\n\nIf $\\vec{F}_{\\text{ext}} = 0$, then $\\vec{p}_{\\text{total}} = M\\vec{v}_{cm} = \\text{const}$.\n\n## CM Reference Frame\n\nIn the **center-of-mass (CM) frame**, the total momentum is zero by definition:\n$$\\sum_i m_i \\vec{v}_i' = 0$$\nwhere $\\vec{v}_i' = \\vec{v}_i - \\vec{v}_{cm}$ are velocities relative to the CM.\n\nThe total kinetic energy in the CM frame ($K_{\\text{CM frame}}$) is the minimum possible kinetic energy of the system — the remaining energy $\\frac{1}{2}Mv_{cm}^2$ is associated with CM motion.",
      "body_he_md": "## $\\vec{F}_{ext} = M\\vec{a}_{cm}$\n\nנגזור $M\\vec{v}_{cm} = \\vec{p}_{\\text{כולל}}$ לפי זמן. כוחות פנימיים מבוטלים בזוגות (חוק שלישי של ניוטון):\n$$\\boxed{\\vec{F}_{\\text{חיצוני}} = M\\vec{a}_{cm}}$$\n\n**מסקנה:** רק כוחות חיצוניים יכולים לשנות את תנועת מרכז המסה.\n\n## שימור תנע\n\nאם $\\vec{F}_{\\text{חיצוני}} = 0$, אז $\\vec{p}_{\\text{כולל}} = M\\vec{v}_{cm} = \\text{const}$.\n\n## מערכת ייחוס CM\n\nב**מערכת ייחוס מרכז המסה**, התנע הכולל הוא אפס בהגדרה:\n$$\\sum_i m_i \\vec{v}_i' = 0$$\nהאנרגיה הקינטית במערכת CM היא המינימלית האפשרית למערכת."
    },
    {
      "id": "rocket_equation",
      "title_en": "The Rocket Equation (Tsiolkovsky)",
      "title_he": "משוואת הרקטה (צ'יולקובסקי)",
      "level_min": "university",
      "body_en_md": "## Variable-Mass Systems\n\nA rocket ejects exhaust gas at velocity $\\vec{u}$ **relative to the rocket**. Let $M(t)$ be the rocket mass at time $t$, and $v(t)$ its velocity (in an inertial frame).\n\nIn time $dt$: mass $|dM|$ is ejected. The exhaust velocity in the inertial frame is $v + u$ (if $u$ is defined as backward, i.e., $u < 0$ so exhaust moves backward). Conservation of momentum (no external force):\n\n$$M\\,dv = -u\\,dM \\implies M\\frac{dv}{dt} = -u\\frac{dM}{dt}$$\n\nHere $dM/dt < 0$ (mass is decreasing), and $-u\\,dM/dt > 0$ (thrust). Integrating from $M_0$ to $M_f$:\n$$\\int_{v_0}^{v_f}dv = -u\\int_{M_0}^{M_f}\\frac{dM}{M} = u\\ln\\frac{M_0}{M_f}$$\n$$\\boxed{\\Delta v = u\\ln\\frac{M_0}{M_f}}$$\n\nThis is the **Tsiolkovsky rocket equation** (Δv budget equation in orbital mechanics).\n\n**Physical insight:** $\\ln(M_0/M_f)$ grows slowly — to double $\\Delta v$, you need to square the mass ratio. Efficient rockets maximize exhaust velocity $u$ (specific impulse).\n\n**Example:** Exhaust speed $u = 3000$ m/s, $M_0/M_f = e^2 \\approx 7.4$. Then $\\Delta v = 3000 \\times 2 = 6000$ m/s.",
      "body_he_md": "## מערכות בעלות מסה משתנה\n\nרקטה מפליטה גז פליטה במהירות $u$ **ביחס לרקטה**. $M(t)$ = מסת הרקטה, $v(t)$ = מהירותה.\n\nשימור תנע (ללא כוח חיצוני): $M\\,dv = -u\\,dM$.\nאינטגרציה מ-$M_0$ ל-$M_f$:\n$$\\boxed{\\Delta v = u\\ln\\frac{M_0}{M_f}}$$\n\nזוהי **משוואת הרקטה של צ'יולקובסקי**.\n\n**תובנה פיזיקלית:** $\\ln(M_0/M_f)$ גדל לאט — להכפלת $\\Delta v$ יש לריבוע יחס המסות. רקטות יעילות ממקסמות את מהירות הפליטה $u$.\n\n**דוגמה:** $u = 3000$ m/s, $M_0/M_f = e^2 \\approx 7.4$ $\\Rightarrow$ $\\Delta v = 6000$ m/s."
    },
    {
      "id": "cm_applications_summary",
      "title_en": "Applications and Problem-Solving Summary",
      "title_he": "יישומים וסיכום פתרון בעיות",
      "level_min": "university",
      "body_en_md": "## Key Problem Types\n\n1. **Find CM position:** Use $\\vec{r}_{cm} = (\\sum m_i\\vec{r}_i)/M$ for discrete; integral for continuous.\n2. **CM doesn't move:** If $\\vec{F}_{ext} = 0$, then $\\Delta\\vec{r}_{cm} = 0$. Example: person walks on a floating raft — the raft moves backward as the person moves forward, keeping CM fixed.\n3. **Explosion/collision:** CM velocity unchanged during collision/explosion (internal forces only).\n4. **Rocket problem:** Use Tsiolkovsky or work incrementally: $M(t) = M_0 - \\dot{m}t$, thrust $= u\\dot{m}$.\n\n## Technion-Style Example\n\n*A bullet of mass $m = 0.01$ kg is fired horizontally at $v_0 = 300$ m/s into a stationary wooden block of mass $M = 2$ kg resting on a frictionless surface. The bullet embeds in the block. Find the CM velocity before and after.*\n\n- **Before:** $v_{cm} = (m v_0)/(m+M) = (0.01 \\times 300)/(2.01) \\approx 1.49$ m/s.\n- **After:** Same — CM velocity is conserved! The block+bullet system moves at 1.49 m/s.\n- This follows from $\\vec{F}_{ext} = 0$ (no friction), so $\\vec{p}_{\\text{total}} = \\text{const}$.",
      "body_he_md": "## סוגי בעיות מרכזיים\n\n1. **מציאת מיקום CM:** $\\vec{r}_{cm} = (\\sum m_i\\vec{r}_i)/M$ לדיסקרטי; אינטגרל לרציף.\n2. **CM אינו זז:** אם $\\vec{F}_{ext} = 0$, אז $\\Delta\\vec{r}_{cm} = 0$.\n3. **פיצוץ/התנגשות:** מהירות ה-CM אינה משתנה (רק כוחות פנימיים).\n4. **בעיית רקטה:** שימוש במשוואת צ'יולקובסקי.\n\n## דוגמה בסגנון הטכניון\n\n*כדור ($m = 0.01$ kg, $v_0 = 300$ m/s) נורה לתוך בלוק עץ ($M = 2$ kg) על משטח חלק. מצא מהירות CM לפני ואחרי.*\n\n$v_{cm} = (mv_0)/(m+M) = 3/(2.01) \\approx 1.49$ m/s — שמורה לפני ואחרי!"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "Three masses are placed along the x-axis: $m_1 = 1$ kg at $x = 0$, $m_2 = 3$ kg at $x = 2$ m, $m_3 = 2$ kg at $x = 5$ m. Where is the center of mass?",
      "body_he": "שלוש מסות מונחות לאורך ציר x: $m_1 = 1$ kg ב-$x = 0$, $m_2 = 3$ kg ב-$x = 2$ m, $m_3 = 2$ kg ב-$x = 5$ m. היכן מרכז המסה?",
      "options": [
        {"id": "a", "text_en": "$x_{cm} \\approx 2.67$ m", "text_he": "$x_{cm} \\approx 2.67$ m", "correct": True},
        {"id": "b", "text_en": "$x_{cm} = 2.33$ m", "text_he": "$x_{cm} = 2.33$ m", "correct": False},
        {"id": "c", "text_en": "$x_{cm} = 2.00$ m", "text_he": "$x_{cm} = 2.00$ m", "correct": False},
        {"id": "d", "text_en": "$x_{cm} = 3.50$ m", "text_he": "$x_{cm} = 3.50$ m", "correct": False}
      ],
      "explanation_en": "$M = 1+3+2 = 6$ kg. $x_{cm} = [(1)(0)+(3)(2)+(2)(5)]/6 = (0+6+10)/6 = 16/6 \\approx 2.67$ m. The CM lies between $m_2$ and $m_3$ but closer to $m_2$, the heaviest particle.",
      "explanation_he": "$M = 6$ kg. $x_{cm} = (0 + 6 + 10)/6 = 16/6 \\approx 2.67$ m. מרכז המסה קרוב יותר ל-$m_2$, המסה הכבדה ביותר."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A uniform thin rod of length $L = 0.8$ m and mass $M$ lies along the x-axis from $x = 0$ to $x = 0.8$ m. Using $x_{cm} = \\frac{1}{M}\\int_0^L x\\lambda\\,dx$, the center of mass is at:",
      "body_he": "מוט דק אחיד באורך $L = 0.8$ m ומסה $M$ מונח לאורך ציר x מ-$x = 0$ עד $x = 0.8$ m. לפי $x_{cm} = \\frac{1}{M}\\int_0^L x\\lambda\\,dx$, מרכז המסה נמצא ב:",
      "options": [
        {"id": "a", "text_en": "$x_{cm} = 0.4$ m", "text_he": "$x_{cm} = 0.4$ m", "correct": True},
        {"id": "b", "text_en": "$x_{cm} = 0.267$ m", "text_he": "$x_{cm} = 0.267$ m", "correct": False},
        {"id": "c", "text_en": "$x_{cm} = 0.6$ m", "text_he": "$x_{cm} = 0.6$ m", "correct": False},
        {"id": "d", "text_en": "$x_{cm} = 0$ m", "text_he": "$x_{cm} = 0$ m", "correct": False}
      ],
      "explanation_en": "$\\lambda = M/L$. $x_{cm} = \\frac{\\lambda}{M}\\int_0^L x\\,dx = \\frac{\\lambda}{M}\\cdot\\frac{L^2}{2} = \\frac{L}{2} = 0.4$ m. The CM of a uniform rod is always at its midpoint.",
      "explanation_he": "$\\lambda = M/L$. $x_{cm} = \\frac{\\lambda}{M}\\cdot\\frac{L^2}{2} = \\frac{L}{2} = 0.4$ m. מרכז המסה של מוט אחיד נמצא תמיד באמצעו."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "Two ice skaters (masses $M_1 = 60$ kg and $M_2 = 80$ kg) stand at rest on frictionless ice and push off each other. After the push, $v_1 = 2$ m/s to the right. What is $v_2$?",
      "body_he": "שני מחליקי קרח (מסות $M_1 = 60$ kg ו-$M_2 = 80$ kg) עומדים במנוחה על קרח חלק ודוחפים אחד את השני. לאחר הדחיפה, $v_1 = 2$ m/s ימינה. מהי $v_2$?",
      "options": [
        {"id": "a", "text_en": "$v_2 = 1.5$ m/s to the left", "text_he": "$v_2 = 1.5$ m/s שמאלה", "correct": True},
        {"id": "b", "text_en": "$v_2 = 2.0$ m/s to the left", "text_he": "$v_2 = 2.0$ m/s שמאלה", "correct": False},
        {"id": "c", "text_en": "$v_2 = 1.5$ m/s to the right", "text_he": "$v_2 = 1.5$ m/s ימינה", "correct": False},
        {"id": "d", "text_en": "$v_2 = 2.67$ m/s to the left", "text_he": "$v_2 = 2.67$ m/s שמאלה", "correct": False}
      ],
      "explanation_en": "Initially at rest, $\\vec{p}_{\\text{total}} = 0$. After: $M_1 v_1 + M_2 v_2 = 0 \\Rightarrow v_2 = -M_1 v_1/M_2 = -(60)(2)/80 = -1.5$ m/s. Negative = to the left.",
      "explanation_he": "בהתחלה במנוחה, $\\vec{p}_{\\text{כולל}} = 0$. לאחר: $M_1 v_1 + M_2 v_2 = 0 \\Rightarrow v_2 = -(60)(2)/80 = -1.5$ m/s (שמאלה)."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A 70 kg astronaut and a 10 kg toolbox are initially at rest in space. The astronaut pushes the toolbox away at 5 m/s relative to the initial frame. What is the astronaut's recoil speed?",
      "body_he": "אסטרונאוט (70 kg) וארגז כלים (10 kg) נמצאים בתחילה במנוחה בחלל. האסטרונאוט דוחף את הארגז בתנועה של 5 m/s ביחס למסגרת ההתייחסות ההתחלתית. מהי מהירות הרתע של האסטרונאוט?",
      "options": [
        {"id": "a", "text_en": "$\\approx 0.71$ m/s (opposite direction)", "text_he": "$\\approx 0.71$ m/s (כיוון הפוך)", "correct": True},
        {"id": "b", "text_en": "$5$ m/s", "text_he": "$5$ m/s", "correct": False},
        {"id": "c", "text_en": "$0.5$ m/s", "text_he": "$0.5$ m/s", "correct": False},
        {"id": "d", "text_en": "$3.5$ m/s", "text_he": "$3.5$ m/s", "correct": False}
      ],
      "explanation_en": "$p_{\\text{total}} = 0$. $10(5) + 70 v_{\\text{astro}} = 0 \\Rightarrow v_{\\text{astro}} = -50/70 \\approx -0.714$ m/s. The astronaut recoils at $\\approx 0.71$ m/s in the opposite direction.",
      "explanation_he": "$p_{\\text{כולל}} = 0$. $10(5) + 70 v_{\\text{אסטרונאוט}} = 0 \\Rightarrow v_{\\text{אסטרונאוט}} = -50/70 \\approx -0.71$ m/s (כיוון הפוך)."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A rocket has initial mass $M_0 = 10{,}000$ kg and final mass $M_f = 2{,}000$ kg after burning all fuel. The exhaust speed is $u = 2500$ m/s. What is $\\Delta v$?",
      "body_he": "לרקטה מסה התחלתית $M_0 = 10{,}000$ kg ומסה סופית $M_f = 2{,}000$ kg לאחר שריפת כל הדלק. מהירות הפליטה $u = 2500$ m/s. מהו $\\Delta v$?",
      "options": [
        {"id": "a", "text_en": "$\\Delta v \\approx 4024$ m/s", "text_he": "$\\Delta v \\approx 4024$ m/s", "correct": True},
        {"id": "b", "text_en": "$\\Delta v = 2500$ m/s", "text_he": "$\\Delta v = 2500$ m/s", "correct": False},
        {"id": "c", "text_en": "$\\Delta v \\approx 8000$ m/s", "text_he": "$\\Delta v \\approx 8000$ m/s", "correct": False},
        {"id": "d", "text_en": "$\\Delta v = 20{,}000$ m/s", "text_he": "$\\Delta v = 20{,}000$ m/s", "correct": False}
      ],
      "explanation_en": "$\\Delta v = u\\ln(M_0/M_f) = 2500\\ln(10000/2000) = 2500\\ln 5 = 2500 \\times 1.609 \\approx 4023$ m/s.",
      "explanation_he": "$\\Delta v = u\\ln(M_0/M_f) = 2500\\ln(5) = 2500 \\times 1.609 \\approx 4023$ m/s."
    }
  ]
})


# ─────────────────────────────────────────────────────────────────
# LESSON 5 — Angular Momentum & Rotation
# ─────────────────────────────────────────────────────────────────
save({
  "id": "angular_momentum_particles",
  "subject": "university_physics_1",
  "title_en": "Angular Momentum — Particles, Rigid Bodies, and Rolling (University)",
  "title_he": "תנע זוויתי — חלקיקים, גופים קשיחים וגלגול (אוניברסיטה)",
  "duration_min": 27,
  "type": "interactive",
  "level_min": "university",
  "agent_hints": "Angular momentum conservation is the rotational analog of linear momentum conservation — stress the exact parallel. For rolling without slipping, students must understand that $v_{cm} = R\\omega$ connects translational and rotational motion and must be applied before doing energy conservation. Common error: computing only $\\frac{1}{2}Mv_{cm}^2$ and forgetting the rotational KE $\\frac{1}{2}I\\omega^2$. The ice-skater example beautifully illustrates $I_1\\omega_1 = I_2\\omega_2$: as $I$ decreases (arms in), $\\omega$ increases to conserve $L$.",
  "sections": [
    {
      "id": "angular_momentum_particle",
      "title_en": "Angular Momentum of a Particle",
      "title_he": "תנע זוויתי של חלקיק",
      "level_min": "university",
      "body_en_md": "## Definition\n\nFor a particle of mass $m$ at position $\\vec{r}$ with momentum $\\vec{p} = m\\vec{v}$, the **angular momentum** about the origin is:\n$$\\boxed{\\vec{L} = \\vec{r} \\times \\vec{p} = m(\\vec{r} \\times \\vec{v})}$$\n\n**Magnitude:** $L = mrv\\sin\\theta$, where $\\theta$ is the angle between $\\vec{r}$ and $\\vec{v}$.\n\n**Units:** kg·m²/s.\n\n**Direction:** right-hand rule on $\\vec{r} \\times \\vec{p}$ — perpendicular to the plane of $\\vec{r}$ and $\\vec{v}$.\n\n**Important:** $\\vec{L}$ depends on the choice of origin. Always specify the origin.\n\n## Special Cases\n\n- **Circular motion** (radius $r$, speed $v$, $\\theta = 90°$): $L = mrv = mr^2\\omega$\n- **Projectile at peak** (horizontal velocity $v_x$, height $h$ above launch): $L = mhv_x$ (about launch point)\n- **Radial motion** ($\\vec{v}\\parallel\\vec{r}$, $\\theta = 0$ or 180°): $L = 0$ — no angular momentum!\n\n**Example:** A 0.2 kg ball moves at 5 m/s in a circle of radius 0.3 m. $L = (0.2)(0.3)(5) = 0.30$ kg·m²/s.",
      "body_he_md": "## הגדרה\n\nלחלקיק בעל מסה $m$ במיקום $\\vec{r}$ עם תנע $\\vec{p} = m\\vec{v}$, **התנע הזוויתי** סביב הראשית:\n$$\\boxed{\\vec{L} = \\vec{r} \\times \\vec{p} = m(\\vec{r} \\times \\vec{v})}$$\n\n**עוצמה:** $L = mrv\\sin\\theta$, כאשר $\\theta$ הזווית בין $\\vec{r}$ ל-$\\vec{v}$.\n\n**יחידות:** kg·m²/s.\n\n**כיוון:** כלל היד הימנית על $\\vec{r} \\times \\vec{p}$.\n\n**חשוב:** $\\vec{L}$ תלוי בבחירת הראשית.\n\n## מקרים מיוחדים\n\n- **תנועה מעגלית** (רדיוס $r$, מהירות $v$): $L = mrv = mr^2\\omega$\n- **תנועה רדיאלית** ($\\vec{v}\\parallel\\vec{r}$): $L = 0$\n\n**דוגמה:** כדור (0.2 kg) בתנועה מעגלית (r = 0.3 m, v = 5 m/s): $L = 0.30$ kg·m²/s."
    },
    {
      "id": "torque_angular_momentum",
      "title_en": "Torque and the Angular Momentum Theorem",
      "title_he": "מומנט כוח ומשפט התנע הזוויתי",
      "level_min": "university",
      "body_en_md": "## The Angular Momentum Theorem\n\nDifferentiate $\\vec{L} = \\vec{r} \\times \\vec{p}$:\n$$\\frac{d\\vec{L}}{dt} = \\frac{d\\vec{r}}{dt}\\times\\vec{p} + \\vec{r}\\times\\frac{d\\vec{p}}{dt} = \\vec{v}\\times m\\vec{v} + \\vec{r}\\times\\vec{F} = 0 + \\vec{\\tau}$$\n\n(since $\\vec{v}\\times\\vec{v} = 0$)\n\n$$\\boxed{\\vec{\\tau} = \\frac{d\\vec{L}}{dt}}$$\n\nThis is the **rotational analog of Newton's 2nd law**. For a system of particles, only **external** torques change the total $\\vec{L}$.\n\n## Conservation of Angular Momentum\n\nIf $\\vec{\\tau}_{\\text{ext}} = 0$, then:\n$$\\frac{d\\vec{L}}{dt} = 0 \\implies \\vec{L} = \\text{const}$$\n\n**Application — ice skater:** A skater spinning with arms extended (large $I_1$, angular velocity $\\omega_1$) pulls arms in (smaller $I_2$):\n$$I_1\\omega_1 = I_2\\omega_2 \\implies \\omega_2 = \\frac{I_1}{I_2}\\omega_1 > \\omega_1$$\nNo external torque about the vertical axis → $L = I\\omega$ conserved → faster spin.\n\n**Application — satellite orbit:** As a satellite moves closer to Earth (smaller $r$), its orbital speed increases to conserve $L = mrv$ (Kepler's second law follows).",
      "body_he_md": "## משפט התנע הזוויתי\n\nגזירת $\\vec{L} = \\vec{r} \\times \\vec{p}$:\n$$\\boxed{\\vec{\\tau} = \\frac{d\\vec{L}}{dt}}$$\n\nזהו **האנלוג הסיבובי לחוק ניוטון השני**. רק מומנטים **חיצוניים** משנים את $\\vec{L}$ הכולל.\n\n## שימור תנע זוויתי\n\nאם $\\vec{\\tau}_{\\text{חיצוני}} = 0$:\n$$\\vec{L} = \\text{const}$$\n\n**יישום — מחלקת קרח:** מחלק ידיים פרוסות ($I_1$ גדול, $\\omega_1$) מושך ידיים פנימה ($I_2$ קטן):\n$$I_1\\omega_1 = I_2\\omega_2 \\implies \\omega_2 = \\frac{I_1}{I_2}\\omega_1 > \\omega_1$$\n\n**יישום — לוויין במסלול:** כאשר לוויין מתקרב לכדה\"א, מהירותו גדלה לשימור $L = mrv$ (חוק שני של קפלר)."
    },
    {
      "id": "rigid_body_angular_momentum",
      "title_en": "Angular Momentum of a Rigid Body",
      "title_he": "תנע זוויתי של גוף קשיח",
      "level_min": "university",
      "body_en_md": "## Rigid Body Rotating About a Fixed Symmetry Axis\n\nFor a rigid body rotating with angular velocity $\\omega$ about a principal axis:\n$$\\boxed{L = I\\omega}$$\nwhere $I = \\int r^2\\,dm$ is the moment of inertia about that axis.\n\nThe angular momentum theorem then gives:\n$$\\tau_{\\text{net}} = \\frac{dL}{dt} = I\\frac{d\\omega}{dt} = I\\alpha$$\n(recovering $\\tau = I\\alpha$).\n\n## Rolling Without Slipping\n\nFor a symmetric object (sphere, disk, cylinder) of mass $M$, radius $R$, rolling without slipping on a surface:\n\n**Rolling constraint:** $v_{cm} = R\\omega$ (the contact point is momentarily at rest).\n\n**Total kinetic energy:**\n$$KE_{\\text{total}} = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I_{cm}\\omega^2$$\nThe first term is translational KE of CM; the second is rotational KE about CM.\n\nSubstituting $\\omega = v_{cm}/R$:\n$$KE_{\\text{total}} = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I_{cm}\\frac{v_{cm}^2}{R^2} = \\frac{1}{2}v_{cm}^2\\left(M + \\frac{I_{cm}}{R^2}\\right)$$\n\n**Total angular momentum** about contact point:\n$$L = I_{\\text{contact}}\\omega = (I_{cm} + MR^2)\\omega$$\n(parallel-axis theorem for $I_{\\text{contact}}$).",
      "body_he_md": "## גוף קשיח המסתובב סביב ציר סימטריה קבוע\n\nלגוף קשיח המסתובב עם $\\omega$ סביב ציר ראשי:\n$$\\boxed{L = I\\omega}$$\nכאשר $I = \\int r^2\\,dm$. משפט התנע הזוויתי נותן:\n$$\\tau_{\\text{net}} = I\\alpha$$\n\n## גלגול ללא החלקה\n\nלעצם סימטרי (כדור, דיסק, גליל) בעל מסה $M$ ורדיוס $R$ הגולל ללא החלקה:\n\n**תנאי גלגול:** $v_{cm} = R\\omega$.\n\n**אנרגיה קינטית כוללת:**\n$$KE_{\\text{כולל}} = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I_{cm}\\omega^2 = \\frac{1}{2}v_{cm}^2\\left(M + \\frac{I_{cm}}{R^2}\\right)$$"
    },
    {
      "id": "rolling_down_incline",
      "title_en": "Worked Example — Ball Rolling Down an Incline",
      "title_he": "דוגמה מלאה — כדור הגולל במורד מדרון",
      "level_min": "university",
      "body_en_md": "## Uniform Solid Ball Rolling Down an Incline\n\n**Setup:** A uniform solid sphere of mass $M$ and radius $R$ starts from rest at the top of an incline of height $h$. It rolls without slipping. Find the speed $v_{cm}$ at the bottom.\n\n**Method: Energy Conservation**\n\nInitial energy: $E_i = Mgh$ (all potential, at rest).\nFinal energy: $E_f = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}I_{cm}\\omega^2$.\n\nFor solid sphere: $I_{cm} = \\frac{2}{5}MR^2$.\nRolling: $\\omega = v_{cm}/R$.\n\n$$E_f = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}\\cdot\\frac{2}{5}MR^2\\cdot\\frac{v_{cm}^2}{R^2} = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{5}Mv_{cm}^2 = \\frac{7}{10}Mv_{cm}^2$$\n\nSetting $E_i = E_f$:\n$$Mgh = \\frac{7}{10}Mv_{cm}^2 \\implies \\boxed{v_{cm} = \\sqrt{\\frac{10gh}{7}}}$$\n\n**Compare with sliding (no friction, no rotation):** $v_{\\text{slide}} = \\sqrt{2gh}$.\n\nRatio: $v_{\\text{roll}}/v_{\\text{slide}} = \\sqrt{10/14} = \\sqrt{5/7} \\approx 0.845$.\n\nThe rolling ball is **slower** because some energy goes into rotation. Objects with larger $I/MR^2$ ratios are even slower (hollow sphere $> $ solid sphere $> $ disk $> $ ring).",
      "body_he_md": "## כדור מלא אחיד הגולל במורד מדרון\n\n**ניסוח:** כדור מלא אחיד ($M$, $R$) מתחיל ממנוחה בגובה $h$ וגולל ללא החלקה. מצא $v_{cm}$ בתחתית.\n\n**שיטה: שימור אנרגיה**\n\n$I_{cm} = \\frac{2}{5}MR^2$, $\\omega = v_{cm}/R$.\n\n$$Mgh = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}\\cdot\\frac{2}{5}MR^2\\cdot\\frac{v_{cm}^2}{R^2} = \\frac{7}{10}Mv_{cm}^2$$\n\n$$\\boxed{v_{cm} = \\sqrt{\\frac{10gh}{7}}}$$\n\n**השוואה להחלקה (ללא חיכוך):** $v_{\\text{החלקה}} = \\sqrt{2gh}$.\n\nיחס: $v_{\\text{גלגול}}/v_{\\text{החלקה}} = \\sqrt{5/7} \\approx 0.845$.\n\nהכדור הגולל **איטי יותר** כי חלק מהאנרגיה הולך לסיבוב."
    },
    {
      "id": "angular_momentum_summary",
      "title_en": "Summary — Parallels with Linear Mechanics",
      "title_he": "סיכום — מקבילות עם מכניקה לינארית",
      "level_min": "university",
      "body_en_md": "## Translational ↔ Rotational Analogies\n\n| Linear | Rotational |\n|---|---|\n| $m$ (mass) | $I = \\int r^2\\,dm$ (moment of inertia) |\n| $\\vec{p} = m\\vec{v}$ (momentum) | $\\vec{L} = I\\vec{\\omega}$ (angular momentum) |\n| $\\vec{F} = m\\vec{a}$ | $\\vec{\\tau} = I\\vec{\\alpha}$ |\n| $\\vec{F} = d\\vec{p}/dt$ | $\\vec{\\tau} = d\\vec{L}/dt$ |\n| $\\vec{F}_{ext} = 0 \\Rightarrow \\vec{p} = \\text{const}$ | $\\vec{\\tau}_{ext} = 0 \\Rightarrow \\vec{L} = \\text{const}$ |\n| $KE = \\frac{1}{2}mv^2$ | $KE = \\frac{1}{2}I\\omega^2$ |\n\n## Gyroscope Precession (Preview)\n\nA spinning gyroscope tilted at angle $\\theta$ from vertical: the torque $\\vec{\\tau} = \\vec{r}\\times M\\vec{g}$ is horizontal (perpendicular to $\\vec{L}$), causing $\\vec{L}$ to precess (rotate) about the vertical with precession rate:\n$$\\Omega_{\\text{prec}} = \\frac{\\tau}{L} = \\frac{MgL_{cm}}{I\\omega}$$\n\nThis is a direct consequence of $\\vec{\\tau} = d\\vec{L}/dt$.",
      "body_he_md": "## מקבילות תרגום ↔ סיבוב\n\n| לינארי | סיבובי |\n|---|---|\n| $m$ | $I = \\int r^2\\,dm$ |\n| $\\vec{p} = m\\vec{v}$ | $\\vec{L} = I\\vec{\\omega}$ |\n| $\\vec{F} = m\\vec{a}$ | $\\vec{\\tau} = I\\vec{\\alpha}$ |\n| $\\vec{F} = d\\vec{p}/dt$ | $\\vec{\\tau} = d\\vec{L}/dt$ |\n| $\\vec{F}_{ext} = 0 \\Rightarrow \\vec{p} = \\text{const}$ | $\\vec{\\tau}_{ext} = 0 \\Rightarrow \\vec{L} = \\text{const}$ |\n| $KE = \\frac{1}{2}mv^2$ | $KE = \\frac{1}{2}I\\omega^2$ |\n\n## פרצסיה של ג'ירוסקופ (תצוגה מקדימה)\n\nג'ירוסקופ מסתובב בזווית $\\theta$ מהאנכי: המומנט $\\vec{\\tau} = \\vec{r}\\times M\\vec{g}$ גורם ל-$\\vec{L}$ לפרצס (להסתובב) סביב האנכי במהירות:\n$$\\Omega_{\\text{פרצסיה}} = \\frac{\\tau}{L} = \\frac{MgL_{cm}}{I\\omega}$$"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "A particle of mass 2 kg moves at 4 m/s. Its position vector relative to the origin has magnitude $r = 3$ m, and the angle between $\\vec{r}$ and $\\vec{v}$ is 60°. What is the magnitude of its angular momentum about the origin?",
      "body_he": "חלקיק בעל מסה 2 kg נע במהירות 4 m/s. וקטור המיקום שלו ביחס לראשית הוא $r = 3$ m, והזווית בין $\\vec{r}$ ל-$\\vec{v}$ היא 60°. מהו גודל התנע הזוויתי שלו סביב הראשית?",
      "options": [
        {"id": "a", "text_en": "$L = 12\\sqrt{3} \\approx 20.8$ kg·m²/s", "text_he": "$L = 12\\sqrt{3} \\approx 20.8$ kg·m²/s", "correct": True},
        {"id": "b", "text_en": "$L = 24$ kg·m²/s", "text_he": "$L = 24$ kg·m²/s", "correct": False},
        {"id": "c", "text_en": "$L = 12$ kg·m²/s", "text_he": "$L = 12$ kg·m²/s", "correct": False},
        {"id": "d", "text_en": "$L = 6$ kg·m²/s", "text_he": "$L = 6$ kg·m²/s", "correct": False}
      ],
      "explanation_en": "$L = mrv\\sin\\theta = (2)(3)(4)\\sin 60° = 24 \\times (\\sqrt{3}/2) = 12\\sqrt{3} \\approx 20.8$ kg·m²/s.",
      "explanation_he": "$L = mrv\\sin\\theta = (2)(3)(4)\\sin 60° = 24 \\times (\\sqrt{3}/2) = 12\\sqrt{3} \\approx 20.8$ kg·m²/s."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "An ice skater with moment of inertia $I_1 = 4.0$ kg·m² spins at $\\omega_1 = 3.0$ rad/s. She pulls her arms in, reducing $I_2 = 1.5$ kg·m². What is $\\omega_2$?",
      "body_he": "מחלקת קרח עם מומנט אינרציה $I_1 = 4.0$ kg·m² מסתובבת ב-$\\omega_1 = 3.0$ rad/s. היא מושכת ידיה פנימה ל-$I_2 = 1.5$ kg·m². מהי $\\omega_2$?",
      "options": [
        {"id": "a", "text_en": "$\\omega_2 = 8.0$ rad/s", "text_he": "$\\omega_2 = 8.0$ rad/s", "correct": True},
        {"id": "b", "text_en": "$\\omega_2 = 3.0$ rad/s (unchanged)", "text_he": "$\\omega_2 = 3.0$ rad/s (ללא שינוי)", "correct": False},
        {"id": "c", "text_en": "$\\omega_2 = 1.125$ rad/s", "text_he": "$\\omega_2 = 1.125$ rad/s", "correct": False},
        {"id": "d", "text_en": "$\\omega_2 = 4.5$ rad/s", "text_he": "$\\omega_2 = 4.5$ rad/s", "correct": False}
      ],
      "explanation_en": "No external torque about vertical axis, so $L = I\\omega = $ const. $I_1\\omega_1 = I_2\\omega_2 \\Rightarrow \\omega_2 = (4.0)(3.0)/1.5 = 8.0$ rad/s.",
      "explanation_he": "אין מומנט חיצוני סביב הציר האנכי, לכן $L = I\\omega = $ const. $\\omega_2 = (4.0)(3.0)/1.5 = 8.0$ rad/s."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "A solid cylinder ($I_{cm} = \\frac{1}{2}MR^2$) rolls without slipping down an incline from height $h$. What is $v_{cm}$ at the bottom?",
      "body_he": "גליל מלא ($I_{cm} = \\frac{1}{2}MR^2$) גולל ללא החלקה ממדרון מגובה $h$. מהי $v_{cm}$ בתחתית?",
      "options": [
        {"id": "a", "text_en": "$v_{cm} = \\sqrt{\\frac{4gh}{3}}$", "text_he": "$v_{cm} = \\sqrt{\\frac{4gh}{3}}$", "correct": True},
        {"id": "b", "text_en": "$v_{cm} = \\sqrt{2gh}$", "text_he": "$v_{cm} = \\sqrt{2gh}$", "correct": False},
        {"id": "c", "text_en": "$v_{cm} = \\sqrt{gh}$", "text_he": "$v_{cm} = \\sqrt{gh}$", "correct": False},
        {"id": "d", "text_en": "$v_{cm} = \\sqrt{\\frac{10gh}{7}}$", "text_he": "$v_{cm} = \\sqrt{\\frac{10gh}{7}}$", "correct": False}
      ],
      "explanation_en": "$Mgh = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{2}\\cdot\\frac{1}{2}MR^2\\cdot(v_{cm}/R)^2 = \\frac{1}{2}Mv_{cm}^2 + \\frac{1}{4}Mv_{cm}^2 = \\frac{3}{4}Mv_{cm}^2$. So $v_{cm} = \\sqrt{4gh/3}$.",
      "explanation_he": "$Mgh = \\frac{3}{4}Mv_{cm}^2 \\Rightarrow v_{cm} = \\sqrt{4gh/3}$. (לגליל: $\\frac{1}{2}Mv_{cm}^2 + \\frac{1}{4}Mv_{cm}^2 = \\frac{3}{4}Mv_{cm}^2$)"
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A disk ($I = \\frac{1}{2}MR^2$, $M = 5$ kg, $R = 0.2$ m) rotates at $\\omega = 10$ rad/s. What is its angular momentum $L$?",
      "body_he": "דיסק ($I = \\frac{1}{2}MR^2$, $M = 5$ kg, $R = 0.2$ m) מסתובב ב-$\\omega = 10$ rad/s. מהו תנעו הזוויתי $L$?",
      "options": [
        {"id": "a", "text_en": "$L = 1.0$ kg·m²/s", "text_he": "$L = 1.0$ kg·m²/s", "correct": True},
        {"id": "b", "text_en": "$L = 2.0$ kg·m²/s", "text_he": "$L = 2.0$ kg·m²/s", "correct": False},
        {"id": "c", "text_en": "$L = 0.5$ kg·m²/s", "text_he": "$L = 0.5$ kg·m²/s", "correct": False},
        {"id": "d", "text_en": "$L = 10$ kg·m²/s", "text_he": "$L = 10$ kg·m²/s", "correct": False}
      ],
      "explanation_en": "$I = \\frac{1}{2}MR^2 = \\frac{1}{2}(5)(0.04) = 0.10$ kg·m². $L = I\\omega = (0.10)(10) = 1.0$ kg·m²/s.",
      "explanation_he": "$I = \\frac{1}{2}MR^2 = \\frac{1}{2}(5)(0.04) = 0.10$ kg·m². $L = I\\omega = (0.10)(10) = 1.0$ kg·m²/s."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "A torque $\\vec{\\tau}$ acts on a spinning top that has angular momentum $\\vec{L}$. Which statement correctly applies the torque-angular momentum theorem $\\vec{\\tau} = d\\vec{L}/dt$?",
      "body_he": "מומנט $\\vec{\\tau}$ פועל על כרכרה מסתובבת בעלת תנע זוויתי $\\vec{L}$. איזו טענה מיישמת נכון את משפט המומנט-תנע הזוויתי $\\vec{\\tau} = d\\vec{L}/dt$?",
      "options": [
        {"id": "a", "text_en": "If $\\vec{\\tau}$ is perpendicular to $\\vec{L}$, the magnitude of $\\vec{L}$ changes but its direction stays the same.", "text_he": "אם $\\vec{\\tau}$ מאונך ל-$\\vec{L}$, גודל $\\vec{L}$ משתנה אך כיוונו נשאר.", "correct": False},
        {"id": "b", "text_en": "If $\\vec{\\tau}$ is perpendicular to $\\vec{L}$, the direction of $\\vec{L}$ changes (precession) but its magnitude stays constant.", "text_he": "אם $\\vec{\\tau}$ מאונך ל-$\\vec{L}$, כיוון $\\vec{L}$ משתנה (פרצסיה) אך גודלו נשאר קבוע.", "correct": True},
        {"id": "c", "text_en": "A constant torque always increases $|\\vec{L}|$ at a constant rate.", "text_he": "מומנט קבוע תמיד מגדיל את $|\\vec{L}|$ בשיעור קבוע.", "correct": False},
        {"id": "d", "text_en": "Torque and angular momentum always point in the same direction.", "text_he": "מומנט ותנע זוויתי תמיד מצביעים באותו כיוון.", "correct": False}
      ],
      "explanation_en": "When $\\vec{\\tau} \\perp \\vec{L}$, the change $d\\vec{L} = \\vec{\\tau}\\,dt$ is perpendicular to $\\vec{L}$, so $|\\vec{L}|$ is unchanged but the direction rotates — this is gyroscopic precession. A torque parallel to $\\vec{L}$ would change the magnitude.",
      "explanation_he": "כאשר $\\vec{\\tau} \\perp \\vec{L}$, השינוי $d\\vec{L} = \\vec{\\tau}\\,dt$ מאונך ל-$\\vec{L}$, לכן $|\\vec{L}|$ אינו משתנה אך הכיוון מסתובב — זוהי פרצסיה ג'ירוסקופית. מומנט המקביל ל-$\\vec{L}$ ישנה את הגודל."
    }
  ]
})


print("\nAll 5 lessons saved successfully.")
