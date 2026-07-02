"""One-shot expansion for rigid_body_torque_equilibrium.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts/seed_data/lessons/rigid_body_torque_equilibrium.json"

with open(TARGET, encoding="utf-8") as f:
    lesson = json.load(f)

# --- sections ---
for sec in lesson["sections"]:
    sec.pop("summary_he", None)
    sid = sec["id"]
    if sid == "intro":
        sec["body_en_md"] = (
            "A ladder leaning against a wall, a bridge supported at both ends, a crane holding a load — "
            "these are all **static equilibrium** problems. The object is not accelerating: it neither "
            "translates nor rotates. That requires **two simultaneous conditions**: the net force on the "
            "body must be zero (translational equilibrium) and the net torque about any axis must be zero "
            "(rotational equilibrium).\n\n"
            "The power of statics is **strategic pivot choice**. When you take moments about a point where "
            "an unknown force acts, that force has zero moment arm and drops out of the torque equation — "
            "often leaving a single unknown you can solve immediately. This lesson builds on `concept:torque` "
            "and connects to `concept:rigid_body_dynamics` (when equilibrium breaks and objects start to rotate).\n\n"
            "**Exam topics (Bagrut 5-unit / university statics):**\n"
            "- Conditions for equilibrium: $\\sum\\vec{F} = 0$ and $\\sum\\vec{\\tau} = 0$\n"
            "- Torque calculation with correct moment arms\n"
            "- Beam on two supports, ladder against smooth wall, boom with cable\n"
            "- Friction limits and tipping vs sliding"
        )
        sec["body_he_md"] = (
            "סולם נשען על קיר, גשר נתמך בשני קצותיו, מנוף מחזיק עומס — כולם בעיות **שיווי משקל סטטי**. "
            "הגוף לא מואץ: לא זז ולא מסתובב. לכך נדרשים **שני תנאים בו-זמנית**: הכוח הנטו על הגוף חייב "
            "להיות אפס (שיווי משקל תרגומי) והמומנט הנטו סביב כל ציר חייב להיות אפס (שיווי משקל סיבובי).\n\n"
            "כוחה של הסטטיקה הוא **בחירת ציר סיבוב חכמה**. כשלוקחים מומנטים סביב נקודה שבה פועל כוח לא ידוע, "
            "לכוח זה זרוע מומנט אפסית והוא נעלם מהמשוואה — לעיתים נשאר רק נעלם אחד לפתרון. שיעור זה מבוסס על "
            "`concept:torque` ומוביל ל-`concept:rigid_body_dynamics` (כששיווי המשקל נשבר והגוף מתחיל להסתובב).\n\n"
            "**נושאי בחינה (בגרות 5 יחידות / סטטיקה באוניברסיטה):**\n"
            "- תנאי שיווי משקל: $\\sum\\vec{F} = 0$ ו-$\\sum\\vec{\\tau} = 0$\n"
            "- חישוב מומנטים עם זרועות נכונות\n"
            "- קורה על שני תמיכות, סולם על קיר חלק, זרוע עם כבל\n"
            "- גבולות חיכוך והחלטה: החלקה מול התהפכות"
        )
        sec["summary_he"] = lesson.get("summary_he")  # noqa — keep top-level
    elif sid == "definition":
        sec["body_en_md"] = (
            "**Torque** (moment of force) measures the tendency of a force to rotate a body about a pivot:\n"
            "$$\\tau = rF\\sin\\theta = F\\cdot d_{\\perp}$$\n"
            "where $r$ is the distance from pivot to the point of application, $\\theta$ is the angle between "
            "$\\vec{r}$ and $\\vec{F}$, and $d_{\\perp}$ is the **perpendicular distance** from the pivot to "
            "the line of action of the force.\n\n"
            "**Conditions for static equilibrium** of a rigid body:\n"
            "$$\\sum \\vec{F} = 0 \\quad \\Rightarrow \\quad \\sum F_x = 0, \\; \\sum F_y = 0$$\n"
            "$$\\sum \\vec{\\tau} = 0 \\quad \\text{(about any point)}$$\n\n"
            "The first condition prevents translation; the second prevents rotation. Both must hold simultaneously.\n\n"
            "**Sign conventions:**\n"
            "- Counterclockwise (CCW) torque: positive\n"
            "- Clockwise (CW) torque: negative\n"
            "Be consistent within each problem.\n\n"
            "**Pivot choice:** You may take moments about **any** point. Choose a pivot where unknown forces "
            "act — their moment arms are zero, so they vanish from $\\sum\\tau = 0$. This is the single most "
            "important strategy in statics problems."
        )
        sec["body_he_md"] = (
            "**מומנט סיבוב** (moment of force) מודד את נ tendency של כוח לסובב גוף סביב ציר:\n"
            "$$\\tau = rF\\sin\\theta = F\\cdot d_{\\perp}$$\n"
            "כאשר $r$ הוא המרחק מהציר לנקודת הפעלת הכוח, $\\theta$ הזווית בין $\\vec{r}$ ל-$\\vec{F}$, "
            "ו-$d_{\\perp}$ הוא **המרחק המאונך** מהציר לקו הפעולה של הכוח.\n\n"
            "**תנאי שיווי משקל סטטי** לגוף נוקשה:\n"
            "$$\\sum \\vec{F} = 0 \\quad \\Rightarrow \\quad \\sum F_x = 0, \\; \\sum F_y = 0$$\n"
            "$$\\sum \\vec{\\tau} = 0 \\quad \\text{(סביב כל נקודה)}$$\n\n"
            "התנאי הראשון מונע תנועה לינארית; השני מונע סיבוב. שניהם חייבים להתקיים בו-זמנית.\n\n"
            "**קונבנציות סימן:**\n"
            "- מומנט נגד כיוון השעון (CCW): חיובי\n"
            "- מומנט עם כיוון השעון (CW): שלילי\n"
            "היו עקביים בכל בעיה.\n\n"
            "**בחירת ציר:** ניתן לקחת מומנטים סביב **כל** נקודה. בחרו ציר שבו פועלים כוחות לא ידועים — "
            "זרוע המומנט שלהם אפסית ולכן הם נעלמים מ-$\\sum\\tau = 0$. זו האסטרטגיה החשובה ביותר בבעיות סטטיקה."
        )
    elif sid == "theory":
        sec["body_en_md"] = (
            "### Step-by-step approach\n"
            "1. **Draw a free-body diagram (FBD)** — isolate the object and show every external force: "
            "weight at CM, normal forces, friction, tension, reactions.\n"
            "2. **Choose a pivot point** — ideally where an unknown force acts (zero moment arm).\n"
            "3. **Write $\\sum\\tau = 0$** about the chosen pivot, assigning CCW positive.\n"
            "4. **Write $\\sum F_x = 0$ and $\\sum F_y = 0$** to find remaining unknowns.\n"
            "5. **Check constraints** — friction limits ($f \\leq \\mu_s N$), cable can only pull, smooth "
            "surfaces have no friction.\n\n"
            "### Center of gravity\n"
            "For uniform objects in uniform gravity, weight acts at the **center of mass (CM)**. "
            "The moment arm for gravity is the perpendicular distance from the pivot to the vertical "
            "line through the CM — often the horizontal distance for a horizontal beam.\n\n"
            "### Ladder against a smooth wall\n"
            "A smooth wall exerts only a **horizontal normal force** — no friction at the top. "
            "Friction at the floor acts **horizontally toward the wall** to prevent slipping. "
            "At the slipping limit: $f = N_{\\text{wall}}$ and $f = \\mu_s N_{\\text{floor}}$.\n\n"
            "### Boom with cable\n"
            "Pivot at the hinge eliminates both hinge force components from the torque equation. "
            "Only the vertical component of cable tension ($T\\sin\\theta$) creates torque about a "
            "horizontal boom. After finding $T$, use $\\sum F_x = 0$ and $\\sum F_y = 0$ for hinge forces."
        )
        sec["body_he_md"] = (
            "### גישה שלב-אחר-שלב\n"
            "1. **ציור ציר כוחות חופשי (FBD)** — בודדים את הגוף ומציגים כל כוח חיצוני: משקל ב-CM, "
            "כוחות נורמליים, חיכוך, מתיחות, תגובות.\n"
            "2. **בחירת ציר סיבוב** — רצוי שם שפועל כוח לא ידוע (זרוע מומנט אפסית).\n"
            "3. **כתיבת $\\sum\\tau = 0$** סביב הציר, עם CCW חיובי.\n"
            "4. **כתיבת $\\sum F_x = 0$ ו-$\\sum F_y = 0$** למציאת נעלמים נוספים.\n"
            "5. **בדיקת אילוצים** — גבולות חיכוך ($f \\leq \\mu_s N$), כבל רק מושך, משטח חלק ללא חיכוך.\n\n"
            "### מרכז כובד\n"
            "לגופים אחידים בכבידה אחידה, הכובד פועל ב**מרכז המסה (CM)**. זרוע המומנט לכובד היא המרחק "
            "המאונך מהציר לקו האנכי דרך ה-CM — לעיתים המרחק האופקי לקורה אופקית.\n\n"
            "### סולם על קיר חלק\n"
            "קיר חלק מפעיל רק **כוח נורמלי אופקי** — ללא חיכוך בראש. חיכוך ברצפה פועל **אופקית לכיוון הקיר** "
            "כדי למנוע החלקה. בגבול ההחלקה: $f = N_{\\text{wall}}$ ו-$f = \\mu_s N_{\\text{floor}}$.\n\n"
            "### זרוע עם כבל\n"
            "ציר בציר מבטל את שני רכיבי כוח הציר ממשוואת המומנט. רק הרכיב האנכי של מתיחות הכבל ($T\\sin\\theta$) "
            "יוצר מומנט על זרוע אופקית. אחרי מציאת $T$, השתמשו ב-$\\sum F_x = 0$ ו-$\\sum F_y = 0$ לכוחות הציר."
        )
    elif sid == "worked_example_1":
        sec["body_en_md"] = (
            "**Given:** A uniform beam ($M = 80\\;\\text{kg}$, $L = 6\\;\\text{m}$) is supported at both ends. "
            "A $20\\;\\text{kg}$ person stands $2\\;\\text{m}$ from the left end. Find both reaction forces. "
            "Take $g = 10\\;\\text{m/s}^2$.\n\n"
            "This is the classic **two-support beam** problem. Weight of the beam acts at its centre ($L/2 = 3$ m "
            "from either end).\n\n"
            "### Move 1 — Pivot at left end (eliminates $R_L$ from torque equation)\n"
            "CCW torques from $R_R$; CW from beam weight and person:\n"
            "$$\\sum\\tau_{\\text{left}} = 0: \\quad R_R(6) - Mg(3) - mg(2) = 0$$\n"
            "$$R_R = \\frac{80(10)(3) + 20(10)(2)}{6} = \\frac{2400 + 400}{6} = \\frac{2800}{6} \\approx 466.7\\;\\text{N}$$\n\n"
            "### Move 2 — Vertical force balance\n"
            "$$R_L + R_R = (M + m)g = (80+20)(10) = 1000\\;\\text{N}$$\n"
            "$$R_L = 1000 - 466.7 = 533.3\\;\\text{N}$$\n\n"
            "### Move 3 — Sanity check\n"
            "The person is closer to the left support, so $R_L > R_R$ ✓. Sum: $533.3 + 466.7 = 1000$ N ✓.\n\n"
            "**Alternative pivot:** Taking moments about the right end gives $R_L$ directly with the same result — "
            "the answer is independent of pivot choice, which is a useful consistency check.\n\n"
            "**Exam tip:** Label each torque CW or CCW before writing the equation. A sign error on one term "
            "flips the final answer.\n\n"
            "**Answer:** $R_L \\approx 533$ N, $R_R \\approx 467$ N."
        )
        sec["body_he_md"] = (
            "**נתון:** קורה אחידה ($M = 80\\;\\text{kg}$, $L = 6\\;\\text{m}$) נתמכת בשני קצותיה. "
            "אדם $20\\;\\text{kg}$ עומד $2\\;\\text{m}$ מהקצה השמאלי. מצאו את שתי כוחות התגובה. $g = 10\\;\\text{m/s}^2$.\n\n"
            "זו בעיית **קורה על שני תמיכות** קלאסית. משקל הקורה פועל במרכז ($L/2 = 3$ m מכל קצה).\n\n"
            "### צעד 1 — ציר בקצה שמאל (מבטל $R_L$ ממשוואת המומנט)\n"
            "מומנטים CCW מ-$R_R$; CW ממשקל הקורה והאדם:\n"
            "$$\\sum\\tau_{\\text{left}} = 0: \\quad R_R(6) - Mg(3) - mg(2) = 0$$\n"
            "$$R_R = \\frac{2400 + 400}{6} = \\frac{2800}{6} \\approx 466.7\\;\\text{N}$$\n\n"
            "### צעד 2 — איזון כוחות אנכיים\n"
            "$$R_L + R_R = (M + m)g = 1000\\;\\text{N}$$\n"
            "$$R_L = 1000 - 466.7 = 533.3\\;\\text{N}$$\n\n"
            "### צעד 3 — בדיקת סבירות\n"
            "האדם קרוב יותר לתמיכה השמאלית, ולכן $R_L > R_R$ ✓. סכום: $1000$ N ✓.\n\n"
            "**ציר חלופי:** מומנטים סביב הקצה הימני נותנים $R_L$ ישירות — אותה תוצאה. התשובה אינה תלויה בבחירת הציר.\n\n"
            "**טיפ לבחינה:** סמנו כל מומנט CW או CCW לפני כתיבת המשוואה. שגיאת סימן במונח אחד הופכת את התשובה.\n\n"
            "**תשובה:** $R_L \\approx 533$ N, $R_R \\approx 467$ N."
        )
    elif sid == "worked_example_2":
        sec["body_en_md"] = (
            "**Given:** A uniform ladder ($M = 20\\;\\text{kg}$, $L = 4\\;\\text{m}$) leans against a smooth wall "
            "at $\\theta = 60°$ from horizontal. Friction coefficient at floor $\\mu_s = 0.4$. How far can a "
            "$60\\;\\text{kg}$ person climb before the ladder slips?\n\n"
            "**Forces on FBD:** $N_{\\text{floor}}$ (up), $f_{\\text{floor}}$ (horizontal, toward wall), "
            "$N_{\\text{wall}}$ (horizontal, away from wall), ladder weight $Mg$ at centre, person weight $mg$ "
            "at distance $x$ from bottom along the ladder.\n\n"
            "### Move 1 — Pivot at base ($N_{\\text{floor}}$ and $f$ have zero moment arm)\n"
            "The wall normal acts at height $L\\sin\\theta$; weights have horizontal moment arms $r\\cos\\theta$:\n"
            "$$N_{\\text{wall}}\\cdot L\\sin\\theta - Mg\\cdot\\frac{L}{2}\\cos\\theta - mg\\cdot x\\cos\\theta = 0$$\n"
            "$$N_{\\text{wall}} = \\frac{(M/2 + mx/L)g}{\\tan\\theta} = \\frac{100 + 150x}{\\sqrt{3}}$$\n\n"
            "### Move 2 — Vertical force balance\n"
            "$$N_{\\text{floor}} = (M+m)g = 800\\;\\text{N}$$\n\n"
            "### Move 3 — Horizontal force balance\n"
            "Smooth wall → no friction at top; floor friction balances wall normal: $f = N_{\\text{wall}}$.\n\n"
            "### Move 4 — Impending slip: $f = \\mu_s N_{\\text{floor}}$\n"
            "$$\\frac{100 + 150x}{\\sqrt{3}} = 320 \\Rightarrow x \\approx 3.03\\;\\text{m}$$\n\n"
            "**Physical reading:** The person can climb to $3.03$ m on a $4$ m ladder — near the top. "
            "Higher on the ladder → larger $N_{\\text{wall}}$ → more friction needed.\n\n"
            "**Answer:** $x \\approx 3.03$ m before slipping."
        )
        sec["body_he_md"] = (
            "**נתון:** סולם אחיד ($M = 20\\;\\text{kg}$, $L = 4\\;\\text{m}$) נשען על קיר חלק ב-$\\theta = 60°$ "
            "מהאופקי. מקדם חיכוך ברצפה $\\mu_s = 0.4$. עד כמה גבוה ($x$ מהתחתית) יכול לטפס אדם $60\\;\\text{kg}$ "
            "לפני שהסולם מחליק?\n\n"
            "**כוחות:** $N_{\\text{floor}}$ (מעלה), $f_{\\text{floor}}$ (אופקי, לכיוון הקיר), "
            "$N_{\\text{wall}}$ (אופקי, הרחק מהקיר), $Mg$ במרכז, $mg$ במרחק $x$ מהתחתית.\n\n"
            "### צעד 1 — ציר בתחתית ($N_{\\text{floor}}$ ו-$f$ עם מומנט אפס)\n"
            "$$N_{\\text{wall}}\\cdot L\\sin\\theta - Mg\\cdot\\frac{L}{2}\\cos\\theta - mg\\cdot x\\cos\\theta = 0$$\n"
            "$$N_{\\text{wall}} = \\frac{(M/2 + mx/L)g}{\\tan\\theta} = \\frac{100 + 150x}{\\sqrt{3}}$$\n\n"
            "### צעד 2 — איזון אנכי\n"
            "$$N_{\\text{floor}} = (M+m)g = 800\\;\\text{N}$$\n\n"
            "### צעד 3 — איזון אופקי\n"
            "$$f = N_{\\text{wall}}$$\n\n"
            "### צעד 4 — גבול החלקה: $f = \\mu_s N_{\\text{floor}}$\n"
            "$$\\frac{100 + 150x}{\\sqrt{3}} = 320 \\Rightarrow x \\approx 3.03\\;\\text{m}$$\n\n"
            "**תשובה:** האדם יכול לטפס עד $x \\approx 3.03$ m — כמעט לראש הסולם ($L = 4$ m).\n\n"
            "**טיפ לבחינה:** בקיר חלק, $N_{\\text{wall}}$ תלוי ב-$x$; בגבול ההחלקה $f = N_{\\text{wall}}$. "
            "ככל שהאדם עולה גבוה יותר, נדרש חיכוך גדול יותר."
        )
    elif sid == "checkpoint_1":
        sec["checkpoint_solution_en"] = (
            "Uniform beam ($M = 40$ kg, $L = 4$ m), pivot at left end, vertical rope at $x = 3$ m.\n\n"
            "**Step 1 — Identify forces:** Beam weight $Mg$ at CM ($x = 2$ m), tension $T$ upward at $x = 3$ m. "
            "Pivot reaction at left has zero torque about the pivot.\n\n"
            "**Step 2 — Torque about left end (CCW positive):**\n"
            "$$\\sum\\tau = 0: \\quad T(3) - Mg(2) = 0$$\n"
            "The beam's CM is at $L/2 = 2$ m, not at the rope.\n\n"
            "**Step 3 — Solve:**\n"
            "$$T = \\frac{Mg(2)}{3} = \\frac{40(10)(2)}{3} = \\frac{800}{3} \\approx 266.7\\;\\text{N}$$\n\n"
            "**Common slip:** Using $L = 4$ m as the moment arm for gravity instead of $L/2 = 2$ m.\n\n"
            "**Answer:** $T \\approx 267$ N."
        )
        sec["checkpoint_solution_he"] = (
            "קורה אחידה ($M = 40$ kg, $L = 4$ m), ציר בקצה שמאל, חבל אנכי ב-$x = 3$ m.\n\n"
            "**שלב 1 — זיהוי כוחות:** משקל $Mg$ ב-CM ($x = 2$ m), מתיחות $T$ למעלה ב-$x = 3$ m. "
            "תגובת הציר בקצה שמאל — מומנט אפס סביב הציר.\n\n"
            "**שלב 2 — מומנט סביב קצה שמאל (CCW חיובי):**\n"
            "$$\\sum\\tau = 0: \\quad T(3) - Mg(2) = 0$$\n"
            "מרכז הקורה ב-$L/2 = 2$ m, לא בחבל.\n\n"
            "**שלב 3 — פתרון:**\n"
            "$$T = \\frac{40(10)(2)}{3} = \\frac{800}{3} \\approx 266.7\\;\\text{N}$$\n\n"
            "**טעות נפוצה:** שימוש ב-$L = 4$ m כזרוע לכובד במקום $L/2 = 2$ m.\n\n"
            "**תשובה:** $T \\approx 267$ N."
        )
    elif sid == "checkpoint_2":
        sec["checkpoint_solution_en"] = (
            "Plank ($L = 6$ m, $M = 30$ kg), supports at both ends. Find $x$ where a $50$ kg box makes "
            "$R_L = 2R_R$.\n\n"
            "**Step 1 — Force balance with ratio:**\n"
            "$R_L + R_R = (30+50)(10) = 800$ N. With $R_L = 2R_R$: $3R_R = 800$ → $R_R = 266.7$ N, "
            "$R_L = 533.3$ N.\n\n"
            "**Step 2 — Torque about left end:**\n"
            "$$R_R(6) = Mg(3) + mg(x)$$\n"
            "$$266.7(6) = 300(3) + 500x \\Rightarrow 1600 = 900 + 500x \\Rightarrow x = 1.4\\;\\text{m}$$\n\n"
            "**Verify:** At $x = 1.4$ m, the heavier right-side load requirement is satisfied.\n\n"
            "**Answer:** $x = 1.4$ m from the left end."
        )
        sec["checkpoint_solution_he"] = (
            "קרש ($L = 6$ m, $M = 30$ kg), תמיכות בשני הקצות. מצאו $x$ שבו קופסה $50$ kg גורמת ל-$R_L = 2R_R$.\n\n"
            "**שלב 1 — איזון כוחות עם יחס:**\n"
            "$R_L + R_R = 800$ N. עם $R_L = 2R_R$: $R_R = 266.7$ N, $R_L = 533.3$ N.\n\n"
            "**שלב 2 — מומנט סביב קצה שמאל:**\n"
            "$$266.7(6) = 300(3) + 500x \\Rightarrow x = 1.4\\;\\text{m}$$\n\n"
            "**אימות:** ב-$x = 1.4$ m התמיכה השמאלית נושאת פי 2 מהימנית.\n\n"
            "**תשובה:** $x = 1.4$ m מהקצה השמאל."
        )
    elif sid == "worked_example_3":
        sec["body_en_md"] = (
            "**Given:** A horizontal boom ($M = 30\\;\\text{kg}$, $L = 4\\;\\text{m}$) is hinged at the wall. "
            "A cable at angle $\\theta = 30°$ supports it at the far end. A $50\\;\\text{kg}$ load hangs from "
            "the tip. Find (a) cable tension, (b) hinge force components.\n\n"
            "**(a) Pivot at hinge** — hinge forces contribute zero torque:\n"
            "$$\\sum\\tau_{\\text{hinge}} = 0$$\n"
            "Only $T\\sin30°$ (vertical component) and weights create torque on a horizontal boom:\n"
            "$$T\\sin30°\\cdot L - Mg\\cdot\\frac{L}{2} - mg\\cdot L = 0$$\n"
            "$$T(0.5)(4) = 30(10)(2) + 50(10)(4) = 600 + 2000 = 2600$$\n"
            "$$T = \\frac{2600}{2} = 1300\\;\\text{N}$$\n\n"
            "**(b) Hinge force components from force balance:**\n"
            "$$\\sum F_x = 0: \\quad H_x = T\\cos30° = 1300(0.866) = 1126\\;\\text{N}$$\n"
            "$$\\sum F_y = 0: \\quad H_y + T\\sin30° - Mg - mg = 0$$\n"
            "$$H_y = 800 - 650 = 150\\;\\text{N} \\text{ (upward)}$$\n\n"
            "**Answer:** (a) $T = 1300$ N; (b) $H_x = 1126$ N (toward wall), $H_y = 150$ N (upward)."
        )
        sec["body_he_md"] = (
            "**נתון:** זרוע אופקית ($M = 30\\;\\text{kg}$, $L = 4\\;\\text{m}$) מחוברת בציר לקיר. "
            "כבל בזווית $\\theta = 30°$ תומך בקצה הרחוק. עומס $50\\;\\text{kg}$ תלוי בקצה. "
            "מצאו (א) מתח כבל, (ב) רכיבי כוח ציר.\n\n"
            "**(א) ציר בציר** — כוחות הציר עם מומנט אפס:\n"
            "$$T\\sin30°\\cdot L - Mg\\cdot\\frac{L}{2} - mg\\cdot L = 0$$\n"
            "$$T(0.5)(4) = 600 + 2000 = 2600 \\Rightarrow T = 1300\\;\\text{N}$$\n\n"
            "**(ב) רכיבי כוח ציר מאיזון כוחות:**\n"
            "$$H_x = T\\cos30° = 1126\\;\\text{N}$$\n"
            "$$H_y = (M+m)g - T\\sin30° = 800 - 650 = 150\\;\\text{N}$$\n\n"
            "**פירוק כוחות:** רק $T\\sin30°$ יוצר מומנט על זרוע אופקית; $T\\cos30°$ פועל דרך הציר (זרוע אפס).\n\n"
            "**בדיקה:** $H_x^2 + H_y^2 \\approx 1136$ N — כוח ציר סופי סביר לעומס $80$ kg.\n\n"
            "**טיפ לבחינה:** מצאו תחילה $T$ ממומנטים, אחר כך רכיבי ציר מאיזון — אל תנסו לפתור הכל בבת אחת. "
            "רכיב $T\\cos\\theta$ לא תורם מומנט על זרוע אופקית.\n\n"
            "**תשובה:** (א) $T = 1300$ N; (ב) $H_x = 1126$ N (לכיוון הקיר), $H_y = 150$ N (מעלה)."
        )
        sec["body_en_md"] = sec["body_en_md"].replace(
            "**Answer:** (a) $T = 1300$ N; (b) $H_x = 1126$ N (toward wall), $H_y = 150$ N (upward).",
            "**Force decomposition:** Only $T\\sin30°$ creates torque on a horizontal boom; $T\\cos30°$ acts "
            "through the pivot (zero arm).\n\n"
            "**Check:** $H = \\sqrt{H_x^2 + H_y^2} \\approx 1136$ N — reasonable hinge reaction for $80$ kg total load.\n\n"
            "**Exam tip:** Find $T$ from torques first, then hinge components from force balance — do not "
            "solve everything simultaneously.\n\n"
            "**Answer:** (a) $T = 1300$ N; (b) $H_x = 1126$ N (toward wall), $H_y = 150$ N (upward).",
        )
    elif sid == "method_guide":
        sec["body_en_md"] = (
            "| Step | Action | Why it matters |\n"
            "|---|---|---|\n"
            "| 1 | Draw FBD with ALL forces | Missing the beam's own weight is the #1 error |\n"
            "| 2 | Choose pivot where unknowns act | Zero moment arm → unknown drops out |\n"
            "| 3 | Write $\\sum\\tau = 0$ (CCW+, CW−) | Often one equation, one unknown |\n"
            "| 4 | Write $\\sum F_x = 0$, $\\sum F_y = 0$ | Finds remaining reactions |\n"
            "| 5 | Apply constraints ($f \\leq \\mu N$) | Ladder problems need friction limit |\n"
            "| 6 | Verify: sum of reactions = total weight | Quick arithmetic check |\n\n"
            "**Torque shortcut:** $\\tau = F \\times d_{\\perp}$ where $d_{\\perp}$ is the perpendicular "
            "distance from pivot to the line of action — not always the distance to the force's point of application.\n\n"
            "**Problem-type guide:**\n"
            "- *Beam on supports:* pivot at one end, then force balance.\n"
            "- *Ladder:* pivot at base; smooth wall → only $N_{\\text{wall}}$ at top.\n"
            "- *Boom + cable:* pivot at hinge; use $T\\sin\\theta$ for torque on horizontal boom.\n\n"
            "**Exam tip:** Write the pivot choice explicitly — examiners award method marks for clear strategy."
        )
        sec["body_he_md"] = (
            "| שלב | פעולה | למה חשוב |\n"
            "|---|---|---|\n"
            "| 1 | ציור FBD עם כל הכוחות | שכחת משקל הקורה — הטעות #1 |\n"
            "| 2 | בחירת ציר שם פועלים לא ידועים | זרוע אפס → הנעלם נעלם |\n"
            "| 3 | $\\sum\\tau = 0$ (CCW+, CW−) | לעיתים משוואה אחת, נעלם אחד |\n"
            "| 4 | $\\sum F_x = 0$, $\\sum F_y = 0$ | מוצא תגובות נוספות |\n"
            "| 5 | אילוצים ($f \\leq \\mu N$) | בעיות סולם דורשות גבול חיכוך |\n"
            "| 6 | אימות: סכום תגובות = משקל כולל | בדיקה מהירה |\n\n"
            "**קיצור דרך למומנט:** $\\tau = F \\times d_{\\perp}$ — המרחק המאונך מהציר לקו הפעולה, "
            "לא תמיד המרחק לנקודת הפעלת הכוח.\n\n"
            "**מדריך לפי סוג בעיה:**\n"
            "- *קורה על תמיכות:* ציר בקצה, אחר כך איזון כוחות.\n"
            "- *סולם:* ציר בבסיס; קיר חלק → רק $N_{\\text{wall}}$ בראש.\n"
            "- *זרוע + כבל:* ציר בציר; $T\\sin\\theta$ למומנט על זרוע אופקית.\n\n"
            "**טיפ לבחינה:** כתבו במפורש את בחירת הציר — בודקים נותנים נקודות על אסטרטגיה ברורה."
        )
    elif sid == "pitfall":
        sec["body_en_md"] = (
            "1. **Forgetting ALL forces on the FBD** — the beam, ladder, or boom has its own weight at the CM. "
            "Students often include the hanging load but omit $Mg$ of the structure itself.\n\n"
            "2. **Wrong moment arm.** Torque uses the perpendicular distance from the pivot to the **line of action**, "
            "not the distance along the beam to the point where the force is applied. For a force at angle $\\theta$ "
            "to the beam: $d_{\\perp} = r\\sin\\theta$ or project onto the perpendicular direction.\n\n"
            "3. **Smooth vs rough contact.** A smooth wall or floor exerts only a normal force — no friction. "
            "Confusing \"smooth wall\" with \"rough floor\" leads to extra unknowns or wrong force directions.\n\n"
            "4. **Inconsistent torque signs.** Define CCW positive once and stick to it. A CW torque from weight "
            "must be negative in the same equation where CCW support torque is positive.\n\n"
            "5. **Using $\\tau = Fd$ when force is not perpendicular.** The general formula is "
            "$\\tau = rF\\sin\\theta$. When force is parallel to the position vector, torque is zero.\n\n"
            "**Fix for misconception \"torque = force × distance (always)\":** "
            "Always identify $d_{\\perp}$ — draw the line of action and measure the shortest distance to the pivot."
        )
        sec["body_he_md"] = (
            "1. **שכחת כוחות ב-FBD** — לקורה, סולם או זרוע יש משקל עצמי ב-CM. תלמידים כוללים את העומס התלוי "
            "אך שוכחים את $Mg$ של המבנה.\n\n"
            "2. **זרוע מומנט שגויה.** המומנט משתמש במרחק המאונך מהציר ל**קו הפעולה**, לא במרחק לאורך הקורה "
            "לנקודת הפעלת הכוח. לכוח בזווית $\\theta$ לקורה: $d_{\\perp} = r\\sin\\theta$.\n\n"
            "3. **משטח חלק מול מחוספס.** קיר או רצפה חלקים מפעילים רק כוח נורמלי — ללא חיכוך. "
            "בלבול בין \"קיר חלק\" ל\"רצפה מחוספסת\" מוביל לכוחות שגויים.\n\n"
            "4. **סימני מומנט לא עקביים.** הגדירו CCW חיובי פעם אחת. מומנט CW מכובד חייב להיות שלילי "
            "באותה משוואה שבה מומנט CCW מחזק חיובי.\n\n"
            "5. **שימוש ב-$\\tau = Fd$ כשהכוח לא מאונך.** הנוסחה הכללית: $\\tau = rF\\sin\\theta$. "
            "כשהכוח מקביל לוקטור המיקום, המומנט אפס.\n\n"
            "**תיקון לטעות \"מומנט = כוח × מרחק (תמיד)\":** "
            "תמיד זהו $d_{\\perp}$ — ציירו את קו הפעולה ומדדו את המרחק הקצר ביותר לציר."
        )
    elif sid == "why_matters":
        sec["body_en_md"] = (
            "Static equilibrium is the foundation of **structural engineering** — every bridge, crane, and "
            "scaffold must satisfy $\\sum F = 0$ and $\\sum\\tau = 0$ or it collapses. Understanding torque "
            "equilibrium also explains everyday phenomena: why a heavy load on a shelf's front edge tips it, "
            "why you push a door at the handle (not the hinge), and why a seesaw balances when "
            "$m_1 r_1 = m_2 r_2$.\n\n"
            "This topic connects directly to `concept:torque` (computing moments), `concept:newton_laws` "
            "(force balance), and `concept:rigid_body_dynamics` (what happens when equilibrium fails). "
            "In Bagrut 5-unit physics, ladder and beam problems appear almost every year — mastering pivot "
            "choice saves time under exam pressure.\n\n"
            "**Why it matters for exams:** Examiners reward clear FBDs and explicit pivot statements. "
            "A correct setup with one algebra error often earns partial credit; a missing weight force earns none."
        )
        sec["body_he_md"] = (
            "שיווי משקל סטטי הוא הבסיס ל**הנדסה מבנית** — כל גשר, מנוף ופיגום חייבים לקיים "
            "$\\sum F = 0$ ו-$\\sum\\tau = 0$ אחרת הם קורסים. הבנת שיווי משקל מומנטים מסבירה גם תופעות יומיומיות: "
            "למה עומס כבד בקדמת מדף מפיל אותו, למה דוחפים דלת בידית (לא בציר), ולמה נדנדה מאוזנת כש-$m_1 r_1 = m_2 r_2$.\n\n"
            "נושא זה מחובר ל-`concept:torque` (חישוב מומנטים), `concept:newton_laws` (איזון כוחות), "
            "ו-`concept:rigid_body_dynamics` (מה קורה כשהשיווי משקל נשבר). בבגרות 5 יחידות, בעיות סולם וקורה "
            "מופיעות כמעט בכל שנה — שליטה בבחירת ציר חוסכת זמן בלחץ הבחינה.\n\n"
            "**למה זה חשוב לבחינות:** בודקים מעריכים FBD ברור והצהרת ציר מפורשת. "
            "הכנה נכונה עם שגיאת אלגebra אחת לעיתים מזכה בנקודות חלקיות; כוח משקל חסר — לא."
        )
    elif sid == "before_exam":
        sec["body_en_md"] = (
            "**Formula card — static equilibrium:**\n\n"
            "- **Torque:** $\\tau = rF\\sin\\theta = Fd_{\\perp}$ [N·m]\n"
            "- **Equilibrium:** $\\sum F_x = 0$, $\\sum F_y = 0$, $\\sum\\tau = 0$ (all three required)\n"
            "- Moment arm = perpendicular distance from pivot to line of action\n"
            "- Gravity acts at CM of uniform objects ($L/2$ for a uniform beam)\n"
            "- **Strategy:** Pivot where unknown forces act → zero moment arm\n"
            "- **Ladder:** Smooth wall → only $N_{\\text{wall}}$ at top; at slip limit $f = N_{\\text{wall}} = \\mu_s N_{\\text{floor}}$\n"
            "- **Boom:** $T\\sin\\theta$ creates torque on horizontal boom; hinge forces from $\\sum F_x, \\sum F_y$ after finding $T$\n"
            "- **Seesaw / lever:** $m_1 r_1 = m_2 r_2$ when balanced\n\n"
            "**Last review:** Say each formula out loud once, draw one FBD from memory, then solve one checkpoint without looking."
        )
        sec["body_he_md"] = (
            "**כרטיס נוסחאות — שיווי משקל סטטי:**\n\n"
            "- **מומנט:** $\\tau = rF\\sin\\theta = Fd_{\\perp}$ [N·m]\n"
            "- **שיווי משקל:** $\\sum F_x = 0$, $\\sum F_y = 0$, $\\sum\\tau = 0$ (שלושתם יחד)\n"
            "- זרוע מומנט = מרחק מאונך מציר לקו הפעולה\n"
            "- כובד פועל ב-CM של גופים אחידים ($L/2$ לקורה אחידה)\n"
            "- **אסטרטגיה:** ציר שם פועלים כוחות לא ידועים → זרוע אפס\n"
            "- **סולם:** קיר חלק → $N_{\\text{wall}}$ בלבד; בגבול החלקה $f = N_{\\text{wall}} = \\mu_s N_{\\text{floor}}$\n"
            "- **זרוע:** $T\\sin\\theta$ למומנט; כוחות ציר מ-$\\sum F_x, \\sum F_y$ אחרי $T$\n"
            "- **נדנדה:** $m_1 r_1 = m_2 r_2$ במצב מאוזן\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול, ציירו FBD אחד מהזיכרון, ופתרו checkpoint בלי להסתכל."
        )
    elif sid == "summary":
        sec["body_en_md"] = (
            "- **Two equilibrium conditions:** $\\sum\\vec{F} = 0$ (no translation) and $\\sum\\vec{\\tau} = 0$ "
            "(no rotation) — both required simultaneously.\n"
            "- **Torque:** $\\tau = Fd_{\\perp}$; CCW positive by convention.\n"
            "- **Key strategy:** Choose pivot where unknown forces act → zero moment arm eliminates them.\n"
            "- **Typical problems:** beam on two supports, ladder against smooth wall, boom with cable at angle.\n"
            "- **Always include:** weight of the structure itself at its CM.\n\n"
            "**Takeaway:** Draw the FBD first, state your pivot, write $\\sum\\tau = 0$ before force equations — "
            "this order solves most Bagrut statics problems in under five minutes."
        )
        sec["body_he_md"] = (
            "- **שני תנאי שיווי משקל:** $\\sum\\vec{F} = 0$ (ללא תרגום) ו-$\\sum\\vec{\\tau} = 0$ (ללא סיבוב) — שניהם יחד.\n"
            "- **מומנט:** $\\tau = Fd_{\\perp}$; CCW חיובי בקונבנציה.\n"
            "- **אסטרטגיה מרכזית:** בחרו ציר שם פועלים כוחות לא ידועים → זרוע אפס מבטלת אותם.\n"
            "- **בעיות טיפוסיות:** קורה על תמיכות, סולם על קיר חלק, זרוע עם כבל בזווית.\n"
            "- **תמיד כללו:** משקל המבנה עצמו ב-CM.\n\n"
            "**מסקנה:** ציירו FBD, הצהירו על הציר, כתבו $\\sum\\tau = 0$ לפני משוואות כוח — "
            "סדר זה פותר רוב בעיות הסטטיקה בבגרות תוך פחות מחמש דקות."
        )

# Fix typo in Hebrew definition
for sec in lesson["sections"]:
    if sec["id"] == "definition":
        sec["body_he_md"] = sec["body_he_md"].replace("נ tendency", "נטייה")

lesson["summary_he"] = (
    "סולם נשען על קיר, גשר נתמך בשני קצותיו, מנוף מחזיק עומס — כולם בעיות שיווי משקל סטטי. "
    "שני התנאים: כוח נטו אפס ומומנט נטו אפס. בחירת ציר חכמה מפשטת את החישובים."
)

# --- question explanations ---
EXPL = {
    "q1": {
        "en": (
            "When a force is applied at $90°$ to the lever arm, $\\sin90° = 1$ and the torque reduces to "
            "$\\tau = Fd$. Here $F = 40$ N and $d = 0.25$ m, so $\\tau = 40 \\times 0.25 = 10$ N·m.\n\n"
            "**Why option 1 (10 N·m) is correct:** Direct application of $\\tau = Fd\\sin\\theta$ with $\\theta = 90°$.\n\n"
            "**Distractor analysis:** 8 N·m might come from using $d = 0.2$ m by mistake. 160 N·m is "
            "$F \\times L$ without the correct moment arm. 0.16 N·m reverses the multiplication ($0.25/40$).\n\n"
            "**Common wrong path:** Using $\\tau = rF$ when the force is not perpendicular — always check $\\theta$.\n\n"
            "**Exam tip:** For perpendicular forces, write $\\tau = Fd$ immediately; for angled forces, "
            "identify $d_{\\perp}$ or use $\\tau = rF\\sin\\theta$."
        ),
        "he": (
            "כשכוח מופעל ב-$90°$ לזרוע, $\\sin90° = 1$ והמומנט מתפשט ל-$\\tau = Fd$. כאן $F = 40$ N "
            "ו-$d = 0.25$ m, ולכן $\\tau = 40 \\times 0.25 = 10$ N·m.\n\n"
            "**למה אפשרות 1 (10 N·m) נכונה:** יישום ישיר של $\\tau = Fd\\sin\\theta$ עם $\\theta = 90°$.\n\n"
            "**ניתוח מסיחים:** 8 N·m עלול לנבוע מ-$d = 0.2$ m בטעות. 160 N·m הוא $F \\times L$ עם זרוע שגויה. "
            "0.16 N·m — היפוך הכפל ($0.25/40$).\n\n"
            "**טעות נפוצה:** שימוש ב-$\\tau = rF$ כשהכוח לא מאונך — תמיד בדקו $\\theta$.\n\n"
            "**טיפ לבחינה:** לכוח מאונך, כתבו מיד $\\tau = Fd$; לכוח בזווית, זהו $d_{\\perp}$ או $\\tau = rF\\sin\\theta$."
        ),
    },
    "q2": {
        "en": (
            "For a beam on two supports, pivot at the left end eliminates $R_L$ from the torque equation. "
            "The beam's weight acts at $L/2 = 4$ m; the $20$ kg mass is at $x = 2$ m.\n\n"
            "**Torque equation:**\n"
            "$$R_R(8) = 60(10)(4) + 20(10)(2) = 2400 + 400 = 2800$$\n"
            "$$R_R = 2800/8 = 350\\;\\text{N}$$\n\n"
            "**Why 350 N is correct:** Each clockwise torque (beam + load) is balanced by the CCW torque from $R_R$.\n\n"
            "**Common wrong path:** Using $L = 8$ m as the moment arm for the beam's weight instead of $L/2 = 4$ m. "
            "Another slip: forgetting the beam's own $Mg$ and only including the $20$ kg load.\n\n"
            "**Exam tip:** After finding one reaction, verify with $R_L + R_R = (M+m)g = 800$ N."
        ),
        "he": (
            "לקורה על שני תמיכות, ציר בקצה שמאל מבטל $R_L$ ממשוואת המומנט. משקל הקורה פועל ב-$L/2 = 4$ m; "
            "המסה $20$ kg ב-$x = 2$ m. זו אותה אסטרטגיה כמו בדוגמה הפתורה 1 — תמיד כללו את משקל הקורה.\n\n"
            "**משוואת מומנט:**\n"
            "$$R_R(8) = 60(10)(4) + 20(10)(2) = 2800 \\Rightarrow R_R = 350\\;\\text{N}$$\n\n"
            "**למה 350 N נכון:** כל מומנט CW (קורה + עומס) מאוזן על ידי מומנט CCW מ-$R_R$.\n\n"
            "**טעות נפוצה:** שימוש ב-$L = 8$ m כזרוע לכובד הקורה במקום $L/2 = 4$ m. "
            "שגיאה נוספת: שכחת $Mg$ של הקורה.\n\n"
            "**טיפ לבחינה:** אחרי מציאת תגובה אחת, אמתו: $R_L + R_R = (M+m)g = 800$ N."
        ),
    },
}

# q3-q8 explanations (ord 3-8)
EXPL.update({
    "ord3": {
        "en": (
            "This is the simplest torque calculation: force perpendicular to the lever, so $\\sin\\theta = 1$ "
            "and $\\tau = Fd$.\n\n"
            "**Calculation:** $\\tau = 20 \\times 0.3 = 6$ N·m.\n\n"
            "**Why 6 N·m is correct:** The force is explicitly stated as perpendicular, so the full $0.3$ m "
            "is the moment arm $d_{\\perp}$.\n\n"
            "**Common wrong path:** Multiplying $20 \\times 0.3$ but reporting units as N instead of N·m. "
            "Another error: using $d = 0.3$ m along the wrench when the force is at an angle (not the case here).\n\n"
            "**Exam tip:** Always include units. Torque in SI is N·m (not joules — even though dimensions match, "
            "context distinguishes them)."
        ),
        "he": (
            "זהו חישוב המומנט הפשוט ביותר: כוח מאונך לזרוע, ולכן $\\sin\\theta = 1$ ו-$\\tau = Fd$. "
            "כשהכוח והזרוע מאונכים, אין צורך בנוסחה הכללית עם $\\sin\\theta$.\n\n"
            "**חישוב:** $\\tau = 20 \\times 0.3 = 6$ N·m.\n\n"
            "**למה 6 N·m נכון:** הכוח מוגדר במפורש כמאונך, ולכן $0.3$ m המלא הוא זרוע המומנט $d_{\\perp}$.\n\n"
            "**טעות נפוצה:** כפל נכון אך דיווח ביחידות N במקום N·m. שגיאה נוספת: שימוש ב-$d$ לא נכון כשהכוח בזווית.\n\n"
            "**טיפ לבחינה:** תמיד כללו יחידות. מומנט ב-SI הוא N·m — אל תבלבלו עם ג'ול או עם כוח ב-Newtons."
        ),
    },
    "ord4": {
        "en": (
            "A balanced seesaw satisfies $\\sum\\tau = 0$ about the pivot. The $30$ kg child creates a "
            "clockwise torque; the $20$ kg child must create an equal counterclockwise torque.\n\n"
            "**Equation:** $30(10)(1.5) = 20(10)(d)$ → $450 = 200d$ → $d = 2.25$ m.\n\n"
            "**Why 2.25 m is correct:** The lighter child must sit farther from the centre to balance the "
            "heavier child who sits closer ($m_1 r_1 = m_2 r_2$).\n\n"
            "**Common wrong path:** Inverting the mass ratio ($1.5 \\times 20/30 = 1.0$ m) — the lighter "
            "mass needs the **larger** distance. Another slip: using weights in kg without converting to N "
            "(masses cancel if both sides use $mg$ consistently).\n\n"
            "**Exam tip:** This is the lever law — check that $m_1/m_2 = d_2/d_1$."
        ),
        "he": (
            "נדנדה מאוזנת מקיימת $\\sum\\tau = 0$ סביב הציר. ילד $30$ kg יוצר מומנט CW; ילד $20$ kg חייב "
            "מומנט CCW שווה. זו בעיית מנוף קלאסית — חוק האיזון $m_1 r_1 = m_2 r_2$.\n\n"
            "**משוואה:** $30(10)(1.5) = 20(10)(d)$ → $d = 2.25$ m.\n\n"
            "**למה 2.25 m נכון:** הילד הקל יותר חייב לשבת רחוק יותר מהמרכז ($m_1 r_1 = m_2 r_2$).\n\n"
            "**טעות נפוצה:** היפוך יחס המסות — המסה הקלה צריכה **מרחק גדול יותר**. שגיאה: שימוש ב-kg בלי $g$ "
            "(המסות מתבטלות אם שני הצדדים עם $mg$).\n\n"
            "**טיפ לבחינה:** זה חוק המנוף — בדקו $m_1/m_2 = d_2/d_1$."
        ),
    },
    "ord5": {
        "en": (
            "Static equilibrium requires **both** translational and rotational balance — neither alone is sufficient.\n\n"
            "**Condition 1:** $\\sum\\vec{F} = 0$ — the net force is zero, so the object has no linear acceleration. "
            "In components: $\\sum F_x = 0$ and $\\sum F_y = 0$.\n\n"
            "**Condition 2:** $\\sum\\vec{\\tau} = 0$ — the net torque about any axis is zero, so the object has "
            "no angular acceleration.\n\n"
            "**Why both are needed:** A pair of equal, opposite forces through the CM gives $\\sum F = 0$ but "
            "creates a couple with nonzero torque. Conversely, a single force through the pivot gives "
            "$\\sum\\tau = 0$ but $\\sum F \\neq 0$.\n\n"
            "**Exam tip:** State both conditions explicitly — partial credit requires both, not just one."
        ),
        "he": (
            "שיווי משקל סטטי דורש **גם** איזון תרגומי **וגם** סיבובי — אף תנאי לבדו אינו מספיק.\n\n"
            "**תנאי 1:** $\\sum\\vec{F} = 0$ — כוח נטו אפס, אין תאוצה לינארית. ברכיבים: $\\sum F_x = 0$, $\\sum F_y = 0$.\n\n"
            "**תנאי 2:** $\\sum\\vec{\\tau} = 0$ — מומנט נטו אפס סביב כל ציר, אין תאוצה זוויתית.\n\n"
            "**למה שניהם נחוצים:** זוג כוחות שווים ונגדיים דרך CM נותן $\\sum F = 0$ אך יוצר זוג מומנטים. "
            "לעומת זאת, כוח בודד דרך הציר נותן $\\sum\\tau = 0$ אך $\\sum F \\neq 0$.\n\n"
            "**טיפ לבחינה:** נסחו שני תנאים במפורש — נקודות חלקיות דורשות את שניהם."
        ),
    },
    "ord6": {
        "en": (
            "This beam problem uses the same strategy as Worked Example 1: pivot at the left end to find $R_R$ "
            "directly from $\\sum\\tau = 0$.\n\n"
            "**Setup:** Uniform beam ($M = 50$ kg) has weight at $L/2 = 2.5$ m. Block ($30$ kg) at $x = 2$ m. "
            "Right support at $x = 5$ m.\n\n"
            "**Torque about left:** $R_R(5) = 50(10)(2.5) + 30(10)(2) = 1250 + 600 = 1850$ → $R_R = 370$ N.\n\n"
            "**Why 370 N is correct:** Both the beam's own weight and the block create clockwise torques balanced "
            "by the CCW torque from $R_R$.\n\n"
            "**Common wrong path:** Forgetting the beam weight (would give $R_R = 120$ N). Using $x = 5$ m "
            "as the arm for the block instead of $2$ m.\n\n"
            "**Exam tip:** Total weight = $(50+30)(10) = 800$ N. Check: $R_L = 800 - 370 = 430$ N > $R_R$ "
            "since the block is left of centre."
        ),
        "he": (
            "בעיית קורה זו משתמשת באותה אסטרטגיה כמו דוגמה 1: ציר בקצה שמאל למציאת $R_R$ מ-$\\sum\\tau = 0$.\n\n"
            "**הכנה:** קורה ($M = 50$ kg) עם משקל ב-$L/2 = 2.5$ m. גוש ($30$ kg) ב-$x = 2$ m. תמיכה ימנית ב-$x = 5$ m.\n\n"
            "**מומנט משמאל:** $R_R(5) = 1250 + 600 = 1850$ → $R_R = 370$ N.\n\n"
            "**למה 370 N נכון:** משקל הקורה והגוש יוצרים מומנטים CW, מאוזנים על ידי $R_R$.\n\n"
            "**טעות נפוצה:** שכחת משקל הקורה (יתן $R_R = 120$ N). שימוש ב-$x = 5$ m במקום $2$ m לגוש.\n\n"
            "**טיפ לבחינה:** משקל כולל = 800 N. $R_L = 430$ N > $R_R$ כי הגוש משמאל למרכז."
        ),
    },
    "ord7": {
        "en": (
            "A door with hinges at top and bottom, pushed horizontally at the handle, is a torque-distribution "
            "problem. The applied force $F = 60$ N at $0.85$ m from the hinge axis creates a torque that must "
            "be balanced by unequal horizontal forces at the two hinges.\n\n"
            "**Force balance:** $H_{\\text{top}} + H_{\\text{bottom}} = F = 60$ N (both horizontal, same direction).\n\n"
            "**Torque about bottom hinge** (assuming door height $h = 2$ m):\n"
            "$H_{\\text{top}} \\cdot h = F \\cdot 0.85$ → $H_{\\text{top}} = 60(0.85)/2 = 25.5$ N.\n"
            "$H_{\\text{bottom}} = 60 - 25.5 = 34.5$ N.\n\n"
            "**Why the bottom hinge carries more:** It is closer to the applied force, so needs a larger "
            "reaction to produce the same opposing torque.\n\n"
            "**Exam tip:** When door height is not given, state your assumption explicitly."
        ),
        "he": (
            "דלת עם צירים למעלה ולמטה, שנדחפת אופקית בידית, היא בעיית חלוקת מומנט. הכוח $F = 60$ N "
            "ב-$0.85$ m מהציר יוצר מומנט שחייב להיות מאוזן על ידי כוחות אופקיים לא שווים בשני הצירים. "
            "שני הצירים מספקים כוחות אופקיים באותו כיוון.\n\n"
            "**איזון כוחות:** $H_{\\text{top}} + H_{\\text{bottom}} = F = 60$ N.\n\n"
            "**מומנט סביב ציר תחתון** (גובה דלת $h = 2$ m):\n"
            "$H_{\\text{top}} = 60(0.85)/2 = 25.5$ N; $H_{\\text{bottom}} = 34.5$ N.\n\n"
            "**למה הציר התחתון נושא יותר:** הוא קרוב יותר לכוח המופעל, ולכן צריך תגובה גדולה יותר.\n\n"
            "**טיפ לבחינה:** כשגובה הדלת לא נתון, ציינו את ההנחה במפורש."
        ),
    },
    "ord8": {
        "en": (
            "A horizontal plank hinged at the wall with a cable at $45°$ is a classic boom problem. "
            "Pivot at the hinge eliminates both hinge force components from the torque equation.\n\n"
            "**Torque about hinge:** Only $T\\sin45°$ (vertical component of tension) and the plank's weight "
            "contribute. The horizontal component $T\\cos45°$ acts through the pivot (zero arm).\n\n"
            "$$T\\sin45° \\cdot 3 = Mg \\cdot 1.5 = 20(10)(1.5) = 300$$\n"
            "$$T = \\frac{300}{3 \\sin45°} = \\frac{100}{\\sqrt{2}/2} = \\frac{200}{\\sqrt{2}} \\approx 141.4\\;\\text{N}$$\n\n"
            "**Common wrong path:** Using full tension $T$ instead of $T\\sin45°$ in the torque equation. "
            "Another error: moment arm $3$ m for weight instead of $L/2 = 1.5$ m.\n\n"
            "**Exam tip:** For angled cables, always decompose into components before writing $\\sum\\tau = 0$."
        ),
        "he": (
            "קרש אופקי עם ציר בקיר וכבל ב-$45°$ הוא בעיית זרוע קלאסית. ציר בציר מבטל את רכיבי כוח הציר "
            "ממשוואת המומנט — זו אותה אסטרטגיה כמו בדוגמה 3.\n\n"
            "**מומנט סביב הציר:** רק $T\\sin45°$ (רכיב אנכי) ומשקל הקרש תורמים. $T\\cos45°$ פועל דרך הציר (זרוע אפס).\n\n"
            "$$T\\sin45° \\cdot 3 = 300 \\Rightarrow T = \\frac{200}{\\sqrt{2}} \\approx 141.4\\;\\text{N}$$\n\n"
            "**טעות נפוצה:** שימוש ב-$T$ המלא במקום $T\\sin45°$. שגיאה: זרוע $3$ m לכובד במקום $L/2 = 1.5$ m.\n\n"
            "**טיפ לבחינה:** לכבלים בזווית, פרקו לרכיבים לפני $\\sum\\tau = 0$. רק הרכיב האנכי $T\\sin\\theta$ תורם מומנט על זרוע אופקית."
        ),
    },
})

for q in lesson["questions"]:
    key = q.get("id") or f"ord{q['ord']}"
    if key in EXPL:
        q["explanation_en"] = EXPL[key]["en"]
        q["explanation_he"] = EXPL[key]["he"]
    elif f"ord{q['ord']}" in EXPL:
        q["explanation_en"] = EXPL[f"ord{q['ord']}"]["en"]
        q["explanation_he"] = EXPL[f"ord{q['ord']}"]["he"]

with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Wrote {TARGET}")
