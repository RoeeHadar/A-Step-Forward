"""Write Lesson 3: partial_derivatives"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))

lesson = {
  "id": "partial_derivatives",
  "type": "interactive",
  "subject": "calculus_2",
  "title_en": "Partial Derivatives & the Gradient",
  "title_he": "\u05e0\u05d2\u05d6\u05e8\u05d5\u05ea \u05d7\u05dc\u05e7\u05d9\u05d5\u05ea \u05d5\u05d4\u05d2\u05e8\u05d3\u05d9\u05d0\u05e0\u05d8",
  "duration_min": 25,
  "level_min": "calculus_1",
  "agent_hints": "Students first meeting multivariable calculus often treat partial derivatives as just single-variable derivatives with the other variable temporarily frozen, which is correct for computation but misses the subtlety that continuity of partials implies differentiability (not just existence). Stress: (1) the geometric meaning of each partial as slope in a coordinate direction, (2) the gradient as the direction of steepest ascent and its role in the tangent-plane formula, (3) the chain rule careful bookkeeping with a dependency diagram. Technion 104281 exams expect students to compute tangent planes and directional derivatives fluently.",
  "sections": [
    {
      "id": "multivariable_functions",
      "title_en": "Multivariable Functions and Visualization",
      "title_he": "\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d5\u05ea \u05e8\u05d1\u05d5\u05ea-\u05de\u05e9\u05ea\u05e0\u05d9\u05dd \u05d5\u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05d6\u05e6\u05d9\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "A **function of two variables** $f: \\mathbb{R}^2 \\to \\mathbb{R}$ assigns a real number $f(x,y)$ to each point $(x,y)$ in its domain.\n\n**Examples:**\n- $f(x,y) = x^2 + y^2$ (paraboloid; level curves are circles)\n- $f(x,y) = x^2 - y^2$ (saddle; level curves are hyperbolas)\n- $f(x,y) = e^{-(x^2+y^2)}$ (Gaussian bump)\n\n**Level curves** (contour lines): the set $\\{(x,y) : f(x,y) = c\\}$ for fixed $c$. Closely spaced level curves indicate steep terrain; widely spaced ones indicate gentle slopes.\n\n**Graph:** the surface $z = f(x,y)$ in $\\mathbb{R}^3$. The partial derivatives measure how this surface slopes in the $x$- and $y$-directions.",
      "body_he_md": "**פונקציה משני משתנים** $f: \\mathbb{R}^2 \\to \\mathbb{R}$ מציבה מספר ממשי $f(x,y)$ לכל נקודה $(x,y)$ בתחומה.\n\n**דוגמאות:**\n- $f(x,y) = x^2 + y^2$ (פרבולואיד; עקומות שיווי-גובה הן מעגלים)\n- $f(x,y) = x^2 - y^2$ (אוכף; עקומות שיווי-גובה הן היפרבולות)\n- $f(x,y) = e^{-(x^2+y^2)}$ (פקעת גאוסית)\n\n**עקומות שיווי-גובה:** הקבוצה $\\{(x,y) : f(x,y) = c\\}$ עבור $c$ קבוע. עקומות צפופות מצביעות על שיפוע תלול; עקומות מרווחות על שיפוע עדין.\n\n**גרף:** המשטח $z = f(x,y)$ ב-$\\mathbb{R}^3$. הנגזרות החלקיות מודדות כיצד משטח זה משופע בכיווני $x$ ו-$y$."
    },
    {
      "id": "partial_derivative_definition",
      "title_en": "Partial Derivatives \u2014 Definition and Computation",
      "title_he": "\u05e0\u05d2\u05d6\u05e8\u05d5\u05ea \u05d7\u05dc\u05e7\u05d9\u05d5\u05ea \u2014 \u05d4\u05d2\u05d3\u05e8\u05d4 \u05d5\u05d7\u05d9\u05e9\u05d5\u05d1",
      "level_min": "calculus_1",
      "body_en_md": "**Definition.** The partial derivative of $f$ with respect to $x$ at $(x_0, y_0)$ is:\n$$\\frac{\\partial f}{\\partial x}(x_0, y_0) = \\lim_{h \\to 0} \\frac{f(x_0+h,\\, y_0) - f(x_0,\\, y_0)}{h}.$$\nIt measures the rate of change of $f$ in the $x$-direction with $y$ held fixed.\n\n**Computation rule:** Differentiate with respect to $x$, treating $y$ as a constant (and vice versa for $\\partial f/\\partial y$).\n\n**Worked Example.** Let $f(x,y) = x^2 y + e^{xy}$.\n\n$$\\frac{\\partial f}{\\partial x} = 2xy + y e^{xy}, \\qquad \\frac{\\partial f}{\\partial y} = x^2 + x e^{xy}.$$\n\n**Second-order partials:** $f_{xx} = \\partial^2 f/\\partial x^2$, $f_{xy} = \\partial^2 f / \\partial x\\, \\partial y$, etc.\n\n**Clairaut\u2019s theorem:** If $f_{xy}$ and $f_{yx}$ are both continuous, then $f_{xy} = f_{yx}$ (mixed partials commute).",
      "body_he_md": "**הגדרה.** הנגזרת החלקית של $f$ לפי $x$ בנקודה $(x_0, y_0)$:\n$$\\frac{\\partial f}{\\partial x}(x_0, y_0) = \\lim_{h \\to 0} \\frac{f(x_0+h,\\, y_0) - f(x_0,\\, y_0)}{h}.$$\nהיא מודדת את קצב השינוי של $f$ בכיוון $x$ כאשר $y$ קבוע.\n\n**כלל חישוב:** גוזרים לפי $x$ תוך התייחסות ל-$y$ כקבוע (ולהפך עבור $\\partial f/\\partial y$).\n\n**דוגמה.** יהי $f(x,y) = x^2 y + e^{xy}$.\n\n$$\\frac{\\partial f}{\\partial x} = 2xy + y e^{xy}, \\qquad \\frac{\\partial f}{\\partial y} = x^2 + x e^{xy}.$$\n\n**נגזרות מסדר שני:** $f_{xx}$, $f_{xy}$, וכו'.\n\n**משפט קלארו:** אם $f_{xy}$ ו-$f_{yx}$ שתיהן רציפות, אז $f_{xy} = f_{yx}$ (נגזרות חלקיות מעורבות מתחלפות)."
    },
    {
      "id": "gradient_directional",
      "title_en": "Gradient and Directional Derivative",
      "title_he": "\u05d2\u05e8\u05d3\u05d9\u05d0\u05e0\u05d8 \u05d5\u05e0\u05d2\u05d6\u05e8\u05ea \u05db\u05d9\u05d5\u05d5\u05df",
      "level_min": "calculus_1",
      "body_en_md": "**Gradient.** The gradient of $f$ at $(x,y)$ is the vector:\n$$\\nabla f = \\left(\\frac{\\partial f}{\\partial x},\\; \\frac{\\partial f}{\\partial y}\\right).$$\n\n**Key property:** $\\nabla f$ points in the direction of steepest ascent of $f$; $-\\nabla f$ points toward steepest descent. The magnitude $|\\nabla f|$ is the rate of steepest ascent.\n\n**Directional derivative.** The rate of change of $f$ in the direction of a unit vector $\\hat{u} = (u_1, u_2)$ is:\n$$D_{\\hat{u}} f = \\nabla f \\cdot \\hat{u} = \\frac{\\partial f}{\\partial x} u_1 + \\frac{\\partial f}{\\partial y} u_2.$$\n\n**Maximum directional derivative:** $D_{\\hat{u}}f$ is maximized when $\\hat{u} = \\nabla f / |\\nabla f|$ (the gradient direction), with maximum value $|\\nabla f|$.\n\n**Example.** $f(x,y) = x^2 + 3y^2$ at $(1,1)$: $\\nabla f = (2x, 6y)|_{(1,1)} = (2, 6)$. The direction of steepest ascent is $(1/\\sqrt{10}, 3/\\sqrt{10})$, with rate $\\sqrt{40} = 2\\sqrt{10}$.",
      "body_he_md": "**גרדיאנט.** גרדיאנט של $f$ בנקודה $(x,y)$ הוא הוקטור:\n$$\\nabla f = \\left(\\frac{\\partial f}{\\partial x},\\; \\frac{\\partial f}{\\partial y}\\right).$$\n\n**תכונה מרכזית:** $\\nabla f$ מצביע בכיוון העלייה התלולה ביותר של $f$; $-\\nabla f$ בכיוון הירידה התלולה ביותר. הגודל $|\\nabla f|$ הוא קצב העלייה התלולה ביותר.\n\n**נגזרת כיוון.** קצב השינוי של $f$ בכיוון וקטור יחידה $\\hat{u} = (u_1, u_2)$:\n$$D_{\\hat{u}} f = \\nabla f \\cdot \\hat{u} = \\frac{\\partial f}{\\partial x} u_1 + \\frac{\\partial f}{\\partial y} u_2.$$\n\n**נגזרת כיוון מקסימלית:** $D_{\\hat{u}}f$ ממוקסמת כאשר $\\hat{u} = \\nabla f / |\\nabla f|$, עם ערך מקסימלי $|\\nabla f|$.\n\n**דוגמה.** $f(x,y) = x^2 + 3y^2$ ב-$(1,1)$: $\\nabla f = (2, 6)$. כיוון העלייה התלולה ביותר הוא $(1/\\sqrt{10}, 3/\\sqrt{10})$, בקצב $2\\sqrt{10}$."
    },
    {
      "id": "tangent_plane",
      "title_en": "Tangent Plane",
      "title_he": "\u05de\u05d9\u05e9\u05d5\u05e8 \u05de\u05e9\u05d9\u05e7",
      "level_min": "calculus_1",
      "body_en_md": "If $f$ is differentiable at $(a, b)$, the **tangent plane** to $z = f(x,y)$ at $(a, b, f(a,b))$ is:\n$$\\boxed{z = f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b).}$$\n\nThis is the best linear approximation to $f$ near $(a,b)$.\n\n**Linear approximation formula:**\n$$f(x,y) \\approx f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b) \\quad \\text{for } (x,y) \\approx (a,b).$$\n\n**Example.** $f(x,y) = \\ln(x + 2y)$ at $(1, 0)$.\n\n$f(1,0) = \\ln 1 = 0$.\n$f_x = \\dfrac{1}{x+2y}\\big|_{(1,0)} = 1$, $\\;f_y = \\dfrac{2}{x+2y}\\big|_{(1,0)} = 2$.\n\nTangent plane: $z = (x-1) + 2y$, i.e., $z = x + 2y - 1$.",
      "body_he_md": "אם $f$ גזירה ב-$(a, b)$, **המישור המשיק** ל-$z = f(x,y)$ ב-$(a, b, f(a,b))$ הוא:\n$$\\boxed{z = f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b).}$$\n\nזה הקירוב הלינארי הטוב ביותר ל-$f$ ליד $(a,b)$.\n\n**נוסחת קירוב לינארי:**\n$$f(x,y) \\approx f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b).$$\n\n**דוגמה.** $f(x,y) = \\ln(x + 2y)$ ב-$(1, 0)$.\n\n$f(1,0) = 0$. $f_x|_{(1,0)} = 1$, $f_y|_{(1,0)} = 2$.\n\nמישור משיק: $z = (x-1) + 2y$, כלומר $z = x + 2y - 1$."
    },
    {
      "id": "chain_rule_multivariable",
      "title_en": "Chain Rule for Multivariable Functions",
      "title_he": "\u05db\u05dc\u05dc \u05d4\u05e9\u05e8\u05e9\u05e8\u05ea \u05dc\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d5\u05ea \u05e8\u05d1\u05d5\u05ea-\u05de\u05e9\u05ea\u05e0\u05d9\u05dd",
      "level_min": "calculus_1",
      "body_en_md": "**Chain Rule (one parameter).** If $z = f(x(t), y(t))$, then:\n$$\\frac{dz}{dt} = \\frac{\\partial f}{\\partial x}\\frac{dx}{dt} + \\frac{\\partial f}{\\partial y}\\frac{dy}{dt}.$$\n\n**Chain Rule (two parameters).** If $z = f(x(s,t), y(s,t))$, then:\n$$\\frac{\\partial z}{\\partial s} = \\frac{\\partial f}{\\partial x}\\frac{\\partial x}{\\partial s} + \\frac{\\partial f}{\\partial y}\\frac{\\partial y}{\\partial s}, \\qquad \\frac{\\partial z}{\\partial t} = \\frac{\\partial f}{\\partial x}\\frac{\\partial x}{\\partial t} + \\frac{\\partial f}{\\partial y}\\frac{\\partial y}{\\partial t}.$$\n\n**Tip:** Draw a dependency diagram (tree) with $z$ at the top, $x,y$ in the middle, and $s,t$ at the bottom. Each path from $z$ to a parameter gives one product term.\n\n**Example.** $f(x,y) = x^2 + y^2$, $x = t\\cos t$, $y = t\\sin t$.\n$$\\frac{dz}{dt} = 2x(\\cos t - t\\sin t) + 2y(\\sin t + t\\cos t) = 2t(\\cos^2 t + \\sin^2 t) + 2t^2(0) = 2t.$$\n(Can verify directly: $z = t^2$, so $dz/dt = 2t$.)",
      "body_he_md": "**כלל השרשרת (פרמטר אחד).** אם $z = f(x(t), y(t))$, אז:\n$$\\frac{dz}{dt} = \\frac{\\partial f}{\\partial x}\\frac{dx}{dt} + \\frac{\\partial f}{\\partial y}\\frac{dy}{dt}.$$\n\n**כלל השרשרת (שני פרמטרים).** אם $z = f(x(s,t), y(s,t))$, אז:\n$$\\frac{\\partial z}{\\partial s} = \\frac{\\partial f}{\\partial x}\\frac{\\partial x}{\\partial s} + \\frac{\\partial f}{\\partial y}\\frac{\\partial y}{\\partial s}, \\qquad \\frac{\\partial z}{\\partial t} = \\frac{\\partial f}{\\partial x}\\frac{\\partial x}{\\partial t} + \\frac{\\partial f}{\\partial y}\\frac{\\partial y}{\\partial t}.$$\n\n**טיפ:** שרטטו דיאגרמת תלות (עץ) עם $z$ בראש, $x,y$ באמצע, ו-$s,t$ בתחתית. כל נתיב מ-$z$ לפרמטר נותן אבר מכפלה אחד.\n\n**דוגמה.** $f(x,y) = x^2 + y^2$, $x = t\\cos t$, $y = t\\sin t$. $z = t^2$, $dz/dt = 2t$."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "For $f(x,y) = x^3 y^2 + \\sin(xy)$, what is $\\dfrac{\\partial f}{\\partial x}$?",
      "body_he": "\u05e2\u05d1\u05d5\u05e8 $f(x,y) = x^3 y^2 + \\sin(xy)$, \u05de\u05d4 \u05d4\u05d9\u05d0 $\\dfrac{\\partial f}{\\partial x}$?",
      "options": [
        {"id": "a", "text_en": "$3x^2 y^2 + y\\cos(xy)$", "text_he": "$3x^2 y^2 + y\\cos(xy)$", "correct": True},
        {"id": "b", "text_en": "$3x^2 y^2 + \\cos(xy)$", "text_he": "$3x^2 y^2 + \\cos(xy)$", "correct": False},
        {"id": "c", "text_en": "$x^3 \\cdot 2y + \\cos(xy)$", "text_he": "$x^3 \\cdot 2y + \\cos(xy)$", "correct": False},
        {"id": "d", "text_en": "$3x^2 + y\\cos(xy)$", "text_he": "$3x^2 + y\\cos(xy)$", "correct": False}
      ],
      "explanation_en": "Differentiate with $y$ fixed: $\\partial(x^3 y^2)/\\partial x = 3x^2 y^2$ and $\\partial(\\sin(xy))/\\partial x = \\cos(xy)\\cdot y$. So $\\partial f/\\partial x = 3x^2 y^2 + y\\cos(xy)$.",
      "explanation_he": "\u05d2\u05d5\u05d6\u05e8\u05d9\u05dd \u05db\u05e9-$y$ \u05e7\u05d1\u05d5\u05e2: $\\partial(x^3 y^2)/\\partial x = 3x^2 y^2$ \u05d5-$\\partial(\\sin(xy))/\\partial x = \\cos(xy)\\cdot y$. \u05dc\u05db\u05df $\\partial f/\\partial x = 3x^2 y^2 + y\\cos(xy)$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "The gradient $\\nabla f$ at a point $(a,b)$ points in the direction of:",
      "body_he": "\u05d4\u05d2\u05e8\u05d3\u05d9\u05d0\u05e0\u05d8 $\\nabla f$ \u05d1\u05e0\u05e7\u05d5\u05d3\u05d4 $(a,b)$ \u05de\u05e6\u05d1\u05d9\u05e2 \u05d1\u05db\u05d9\u05d5\u05d5\u05df:",
      "options": [
        {"id": "a", "text_en": "Steepest descent of $f$", "text_he": "\u05d9\u05e8\u05d9\u05d3\u05d4 \u05ea\u05dc\u05d5\u05dc\u05d4 \u05d1\u05d9\u05d5\u05ea\u05e8 \u05e9\u05dc $f$", "correct": False},
        {"id": "b", "text_en": "Steepest ascent of $f$", "text_he": "\u05e2\u05dc\u05d9\u05d9\u05d4 \u05ea\u05dc\u05d5\u05dc\u05d4 \u05d1\u05d9\u05d5\u05ea\u05e8 \u05e9\u05dc $f$", "correct": True},
        {"id": "c", "text_en": "The level curve of $f$ through $(a,b)$", "text_he": "\u05e2\u05e7\u05d5\u05de\u05ea \u05e9\u05d9\u05d5\u05d5\u05d9-\u05d2\u05d5\u05d1\u05d4 \u05e9\u05dc $f$ \u05d3\u05e8\u05da $(a,b)$", "correct": False},
        {"id": "d", "text_en": "The direction of the $x$-axis", "text_he": "\u05db\u05d9\u05d5\u05d5\u05df \u05e6\u05d9\u05e8 $x$", "correct": False}
      ],
      "explanation_en": "The gradient $\\nabla f$ always points in the direction of steepest ascent of $f$. Its magnitude $|\\nabla f|$ equals the maximum rate of increase. The negative gradient $-\\nabla f$ points toward steepest descent.",
      "explanation_he": "\u05d4\u05d2\u05e8\u05d3\u05d9\u05d0\u05e0\u05d8 $\\nabla f$ \u05ea\u05de\u05d9\u05d3 \u05de\u05e6\u05d1\u05d9\u05e2 \u05d1\u05db\u05d9\u05d5\u05d5\u05df \u05d4\u05e2\u05dc\u05d9\u05d9\u05d4 \u05d4\u05ea\u05dc\u05d5\u05dc\u05d4 \u05d1\u05d9\u05d5\u05ea\u05e8 \u05e9\u05dc $f$. \u05d2\u05d5\u05d3\u05dc\u05d5 $|\\nabla f|$ \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e7\u05e6\u05d1 \u05d4\u05d2\u05d9\u05d3\u05d5\u05dc \u05d4\u05de\u05e7\u05e1\u05d9\u05de\u05dc\u05d9."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "For $f(x,y) = x^2 + y^2$ at $(1, 2)$, compute the directional derivative in the direction $\\hat{u} = (3/5, 4/5)$.",
      "body_he": "\u05e2\u05d1\u05d5\u05e8 $f(x,y) = x^2 + y^2$ \u05d1-$(1, 2)$, \u05d7\u05e9\u05d1 \u05d0\u05ea \u05e0\u05d2\u05d6\u05e8\u05ea \u05d4\u05db\u05d9\u05d5\u05d5\u05df \u05d1\u05db\u05d9\u05d5\u05d5\u05df $\\hat{u} = (3/5, 4/5)$.",
      "options": [
        {"id": "a", "text_en": "$22/5$", "text_he": "$22/5$", "correct": True},
        {"id": "b", "text_en": "$26/5$", "text_he": "$26/5$", "correct": False},
        {"id": "c", "text_en": "$2$", "text_he": "$2$", "correct": False},
        {"id": "d", "text_en": "$\\sqrt{20}$", "text_he": "$\\sqrt{20}$", "correct": False}
      ],
      "explanation_en": "$\\nabla f = (2x, 2y)|_{(1,2)} = (2, 4)$. Then $D_{\\hat{u}}f = (2,4)\\cdot(3/5, 4/5) = 6/5 + 16/5 = 22/5$.",
      "explanation_he": "$\\nabla f|_{(1,2)} = (2, 4)$. \u05d0\u05d6 $D_{\\hat{u}}f = (2,4)\\cdot(3/5, 4/5) = 6/5 + 16/5 = 22/5$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "The equation of the tangent plane to $z = f(x,y)$ at the point $(a, b)$ is:",
      "body_he": "\u05de\u05e9\u05d5\u05d5\u05d0\u05ea \u05d4\u05de\u05d9\u05e9\u05d5\u05e8 \u05d4\u05de\u05e9\u05d9\u05e7 \u05dc-$z = f(x,y)$ \u05d1\u05e0\u05e7\u05d5\u05d3\u05d4 $(a,b)$ \u05d4\u05d9\u05d0:",
      "options": [
        {"id": "a", "text_en": "$z = f_x(a,b)(x-a) + f_y(a,b)(y-b)$", "text_he": "$z = f_x(a,b)(x-a) + f_y(a,b)(y-b)$", "correct": False},
        {"id": "b", "text_en": "$z = f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b)$", "text_he": "$z = f(a,b) + f_x(a,b)(x-a) + f_y(a,b)(y-b)$", "correct": True},
        {"id": "c", "text_en": "$z = f(a,b) + \\nabla f(a,b) \\cdot (x+y)$", "text_he": "$z = f(a,b) + \\nabla f(a,b) \\cdot (x+y)$", "correct": False},
        {"id": "d", "text_en": "$z - f(a,b) = f_{xx}(a,b)(x-a)^2 + f_{yy}(a,b)(y-b)^2$", "text_he": "$z - f(a,b) = f_{xx}(a,b)(x-a)^2 + f_{yy}(a,b)(y-b)^2$", "correct": False}
      ],
      "explanation_en": "The tangent plane passes through $(a, b, f(a,b))$ and has slopes $f_x(a,b)$ and $f_y(a,b)$ in the $x$- and $y$-directions. Option (a) is missing the $f(a,b)$ constant; options (c) and (d) are not the tangent plane formula.",
      "explanation_he": "\u05d4\u05de\u05d9\u05e9\u05d5\u05e8 \u05d4\u05de\u05e9\u05d9\u05e7 \u05e2\u05d5\u05d1\u05e8 \u05d3\u05e8\u05da $(a, b, f(a,b))$ \u05d5\u05d9\u05e9 \u05dc\u05d5 \u05e9\u05d9\u05e4\u05d5\u05e2\u05d9\u05dd $f_x(a,b)$ \u05d5-$f_y(a,b)$. \u05d0\u05e4\u05e9\u05e8\u05d5\u05ea (א) \u05d7\u05e1\u05e8 \u05d0\u05ea \u05d4\u05e7\u05d1\u05d5\u05e2 $f(a,b)$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "If $z = f(x,y)$ where $x = e^t$ and $y = \\ln t$, then $\\dfrac{dz}{dt}$ equals:",
      "body_he": "\u05d0\u05dd $z = f(x,y)$ \u05db\u05d0\u05e9\u05e8 $x = e^t$ \u05d5-$y = \\ln t$, \u05d0\u05d6 $\\dfrac{dz}{dt}$ \u05e9\u05d5\u05d5\u05d4 \u05dc:",
      "options": [
        {"id": "a", "text_en": "$f_x e^t + f_y \\ln t$", "text_he": "$f_x e^t + f_y \\ln t$", "correct": False},
        {"id": "b", "text_en": "$f_x e^t + f_y / t$", "text_he": "$f_x e^t + f_y / t$", "correct": True},
        {"id": "c", "text_en": "$f_x + f_y / t$", "text_he": "$f_x + f_y / t$", "correct": False},
        {"id": "d", "text_en": "$f_x e^t + f_y t$", "text_he": "$f_x e^t + f_y t$", "correct": False}
      ],
      "explanation_en": "By the chain rule: $\\dfrac{dz}{dt} = f_x \\dfrac{dx}{dt} + f_y \\dfrac{dy}{dt} = f_x \\cdot e^t + f_y \\cdot \\dfrac{1}{t}$.",
      "explanation_he": "\u05dc\u05e4\u05d9 \u05db\u05dc\u05dc \u05d4\u05e9\u05e8\u05e9\u05e8\u05ea: $\\dfrac{dz}{dt} = f_x \\dfrac{dx}{dt} + f_y \\dfrac{dy}{dt} = f_x \\cdot e^t + f_y \\cdot \\dfrac{1}{t}$."
    }
  ]
}

path = os.path.join(BASE, lesson["id"] + ".json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
print(f"Saved {lesson['id']}")
