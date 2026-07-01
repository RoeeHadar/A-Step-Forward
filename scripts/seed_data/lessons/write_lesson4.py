"""Write Lesson 4: double_integrals"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))

lesson = {
  "id": "double_integrals",
  "type": "interactive",
  "subject": "calculus_2",
  "title_en": "Double Integrals",
  "title_he": "\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc\u05d9\u05dd \u05db\u05e4\u05d5\u05dc\u05d9\u05d9\u05dd",
  "duration_min": 30,
  "level_min": "calculus_1",
  "agent_hints": "The most common student error is reversing the order of integration without re-drawing the region, leading to incorrect limits. Always insist on sketching the region D before setting up limits. Fubini's theorem is the key tool; stress that switching order requires rewriting ALL limits, not just swapping. For non-rectangular regions, classify as Type I or Type II, write the outer limits as constants and the inner limits as functions. Technion 104281 exams often require changing to polar coordinates \u2014 this lesson covers Cartesian only.",
  "sections": [
    {
      "id": "definition_riemann",
      "title_en": "Definition \u2014 Riemann Sum and Volume",
      "title_he": "\u05d4\u05d2\u05d3\u05e8\u05d4 \u2014 \u05e1\u05db\u05d5\u05dd \u05e8\u05d9\u05de\u05df \u05d5\u05e0\u05e4\u05d7",
      "level_min": "calculus_1",
      "body_en_md": "Let $f(x,y) \\geq 0$ be defined on a rectangle $R = [a,b] \\times [c,d]$. Partition $R$ into small sub-rectangles $R_{ij}$ of area $\\Delta A_{ij}$. The **Riemann sum** is:\n$$\\sum_{i,j} f(x_{ij}^*, y_{ij}^*) \\Delta A_{ij}.$$\n\nThe **double integral** is the limit of these sums as the partition gets finer:\n$$\\iint_R f(x,y)\\,dA = \\lim_{\\|P\\| \\to 0} \\sum_{i,j} f(x_{ij}^*, y_{ij}^*) \\Delta A_{ij}.$$\n\n**Geometric meaning:** $\\iint_R f(x,y)\\,dA$ equals the **volume** of the solid region bounded above by $z = f(x,y)$ and below by the region $R$ in the $xy$-plane.\n\nFor non-positive $f$, the integral gives a signed volume (negative where $f < 0$).\n\n**Useful special cases:**\n- $\\iint_D 1\\,dA = \\text{Area}(D)$\n- $\\iint_D f(x,y)\\,dA / \\text{Area}(D) = $ average value of $f$ over $D$",
      "body_he_md": "\u05ea\u05d4\u05d9 $f(x,y) \\geq 0$ \u05de\u05d5\u05d2\u05d3\u05e8\u05ea \u05e2\u05dc \u05de\u05dc\u05d1\u05df $R = [a,b] \\times [c,d]$. \u05e0\u05d7\u05dc\u05e7 \u05d0\u05ea $R$ \u05dc\u05ea\u05ea-\u05de\u05dc\u05d1\u05e0\u05d9\u05dd $R_{ij}$ \u05d1\u05e9\u05d8\u05d7 $\\Delta A_{ij}$. **\u05e1\u05db\u05d5\u05dd \u05e8\u05d9\u05de\u05df**:\n$$\\sum_{i,j} f(x_{ij}^*, y_{ij}^*) \\Delta A_{ij}.$$\n\n**\u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05db\u05e4\u05d5\u05dc** \u05d4\u05d5\u05d0 \u05d4\u05d2\u05d1\u05d5\u05dc \u05e9\u05dc \u05e1\u05db\u05d5\u05de\u05d5\u05ea \u05d0\u05dc\u05d5 \u05db\u05d0\u05e9\u05e8 \u05d4\u05d7\u05dc\u05d5\u05e7\u05d4 \u05de\u05d3\u05d5\u05d9\u05e7\u05ea \u05d9\u05d5\u05ea\u05e8:\n$$\\iint_R f(x,y)\\,dA = \\lim_{\\|P\\| \\to 0} \\sum_{i,j} f(x_{ij}^*, y_{ij}^*) \\Delta A_{ij}.$$\n\n**\u05de\u05e9\u05de\u05e2\u05d5\u05ea \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9:** $\\iint_R f(x,y)\\,dA$ \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e0\u05e4\u05d7 \u05d4\u05d2\u05d5\u05e3 \u05d4\u05ea\u05dc\u05ea-\u05de\u05de\u05d3\u05d9 \u05d4\u05d7\u05e1\u05d5\u05dd \u05de\u05e2\u05dc \u05e2\u05dc \u05d9\u05d3\u05d9 $z = f(x,y)$ \u05d5\u05de\u05ea\u05d7\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 $R$.\n\n**\u05de\u05e7\u05e8\u05d9\u05dd \u05de\u05d9\u05d5\u05d7\u05d3\u05d9\u05dd:**\n- $\\iint_D 1\\,dA = \\text{Area}(D)$\n- $\\iint_D f\\,dA / \\text{Area}(D) = $ \u05e2\u05e8\u05da \u05de\u05de\u05d5\u05e6\u05e2 \u05e9\u05dc $f$ \u05e2\u05dc $D$"
    },
    {
      "id": "fubini",
      "title_en": "Fubini\u2019s Theorem \u2014 Iterated Integrals",
      "title_he": "\u05de\u05e9\u05e4\u05d8 \u05e4\u05d5\u05d1\u05d9\u05e0\u05d9 \u2014 \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc\u05d9\u05dd \u05d7\u05d5\u05d6\u05e8\u05d9\u05dd",
      "level_min": "calculus_1",
      "body_en_md": "**Fubini\u2019s Theorem.** If $f$ is continuous on $R = [a,b] \\times [c,d]$, then:\n$$\\iint_R f(x,y)\\,dA = \\int_a^b\\!\\int_c^d f(x,y)\\,dy\\,dx = \\int_c^d\\!\\int_a^b f(x,y)\\,dx\\,dy.$$\n\nThe inner integral is evaluated first (treating the outer variable as a constant), then the outer integral.\n\n**Worked Example 1.** Compute $\\displaystyle\\iint_{[0,1]\\times[0,2]} xy\\,dA$.\n\n$$\\int_0^1\\!\\int_0^2 xy\\,dy\\,dx = \\int_0^1 x \\left[\\frac{y^2}{2}\\right]_0^2 dx = \\int_0^1 x \\cdot 2\\,dx = \\left[x^2\\right]_0^1 = 1.$$\n\n**Worked Example 2.** Compute $\\displaystyle\\iint_{[0,\\pi]\\times[0,1]} y\\sin x\\,dA$.\n\n$$\\int_0^\\pi\\sin x\\left(\\int_0^1 y\\,dy\\right)dx = \\int_0^\\pi \\sin x \\cdot \\frac{1}{2}\\,dx = \\frac{1}{2}[-\\cos x]_0^\\pi = \\frac{1}{2}\\cdot 2 = 1.$$",
      "body_he_md": "**\u05de\u05e9\u05e4\u05d8 \u05e4\u05d5\u05d1\u05d9\u05e0\u05d9.** \u05d0\u05dd $f$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1-$R = [a,b] \\times [c,d]$, \u05d0\u05d6:\n$$\\iint_R f(x,y)\\,dA = \\int_a^b\\!\\int_c^d f(x,y)\\,dy\\,dx = \\int_c^d\\!\\int_a^b f(x,y)\\,dx\\,dy.$$\n\n\u05de\u05d7\u05e9\u05d1\u05d9\u05dd \u05ea\u05d7\u05d9\u05dc\u05d4 \u05d0\u05ea \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05e4\u05e0\u05d9\u05de\u05d9 (\u05ea\u05d5\u05da \u05d4\u05ea\u05d9\u05d9\u05d7\u05e1\u05d5\u05ea \u05dc\u05de\u05e9\u05ea\u05e0\u05d4 \u05d4\u05d7\u05d9\u05e6\u05d5\u05e0\u05d9 \u05db\u05e7\u05d1\u05d5\u05e2), \u05d0\u05d7\u05e8 \u05db\u05da \u05d0\u05ea \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05d7\u05d9\u05e6\u05d5\u05e0\u05d9.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4 1.** \u05d7\u05e9\u05d1 $\\displaystyle\\iint_{[0,1]\\times[0,2]} xy\\,dA$.\n\n$$\\int_0^1\\!\\int_0^2 xy\\,dy\\,dx = \\int_0^1 x \\cdot 2\\,dx = 1.$$\n\n**\u05d3\u05d5\u05d2\u05de\u05d4 2.** \u05d7\u05e9\u05d1 $\\displaystyle\\iint_{[0,\\pi]\\times[0,1]} y\\sin x\\,dA$.\n\n$$\\int_0^\\pi \\sin x \\cdot \\frac{1}{2}\\,dx = \\frac{1}{2}\\cdot 2 = 1.$$"
    },
    {
      "id": "non_rectangular",
      "title_en": "Non-Rectangular Regions \u2014 Type I and Type II",
      "title_he": "\u05d0\u05d6\u05d5\u05e8\u05d9\u05dd \u05dc\u05d0-\u05de\u05dc\u05d1\u05e0\u05d9\u05d9\u05dd \u2014 \u05e1\u05d5\u05d2 I \u05d5\u05e1\u05d5\u05d2 II",
      "level_min": "calculus_1",
      "body_en_md": "**Type I region:** $D = \\{(x,y) : a \\leq x \\leq b,\\; g_1(x) \\leq y \\leq g_2(x)\\}$.\n$$\\iint_D f\\,dA = \\int_a^b \\int_{g_1(x)}^{g_2(x)} f(x,y)\\,dy\\,dx.$$\nOuter variable $x$ has constant limits; inner variable $y$ has function limits.\n\n**Type II region:** $D = \\{(x,y) : c \\leq y \\leq d,\\; h_1(y) \\leq x \\leq h_2(y)\\}$.\n$$\\iint_D f\\,dA = \\int_c^d \\int_{h_1(y)}^{h_2(y)} f(x,y)\\,dx\\,dy.$$\n\n**Worked Example.** $\\iint_D x^2 y\\,dA$ where $D$ is the triangle with vertices $(0,0)$, $(1,0)$, $(0,1)$.\n\nThe triangle is $D = \\{(x,y) : 0 \\leq x \\leq 1,\\; 0 \\leq y \\leq 1-x\\}$ (Type I).\n$$\\int_0^1\\int_0^{1-x} x^2 y\\,dy\\,dx = \\int_0^1 x^2 \\cdot \\frac{(1-x)^2}{2}\\,dx = \\frac{1}{2}\\int_0^1(x^2 - 2x^3 + x^4)\\,dx$$\n$$= \\frac{1}{2}\\left[\\frac{x^3}{3} - \\frac{x^4}{2} + \\frac{x^5}{5}\\right]_0^1 = \\frac{1}{2}\\left(\\frac{1}{3} - \\frac{1}{2} + \\frac{1}{5}\\right) = \\frac{1}{2}\\cdot\\frac{1}{30} = \\frac{1}{60}.$$",
      "body_he_md": "**\u05d0\u05d6\u05d5\u05e8 \u05e1\u05d5\u05d2 I:** $D = \\{(x,y) : a \\leq x \\leq b,\\; g_1(x) \\leq y \\leq g_2(x)\\}$.\n$$\\iint_D f\\,dA = \\int_a^b \\int_{g_1(x)}^{g_2(x)} f(x,y)\\,dy\\,dx.$$\n\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea $x$ \u05d4\u05d7\u05d9\u05e6\u05d5\u05e0\u05d9 \u05d7\u05e1\u05d5\u05d9\u05dd; \u05d2\u05d1\u05d5\u05dc\u05d5\u05ea $y$ \u05d4\u05e4\u05e0\u05d9\u05de\u05d9 \u05d4\u05df \u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d5\u05ea.\n\n**\u05d0\u05d6\u05d5\u05e8 \u05e1\u05d5\u05d2 II:** $D = \\{(x,y) : c \\leq y \\leq d,\\; h_1(y) \\leq x \\leq h_2(y)\\}$.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4.** $\\iint_D x^2 y\\,dA$ \u05db\u05d0\u05e9\u05e8 $D$ \u05d4\u05d5\u05d0 \u05d4\u05de\u05e9\u05d5\u05dc\u05e9 \u05e2\u05dd \u05e7\u05d5\u05d3\u05e7\u05d5\u05d3\u05d9\u05dd $(0,0)$, $(1,0)$, $(0,1)$.\n\n$D$: $0 \\leq x \\leq 1$, $0 \\leq y \\leq 1-x$.\n$$\\int_0^1\\int_0^{1-x} x^2 y\\,dy\\,dx = \\frac{1}{2}\\int_0^1 x^2(1-x)^2\\,dx = \\frac{1}{60}.$$"
    },
    {
      "id": "switching_order",
      "title_en": "Switching the Order of Integration",
      "title_he": "\u05d4\u05d7\u05dc\u05e4\u05ea \u05e1\u05d3\u05e8 \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e6\u05d9\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "Sometimes the inner integral is hard (or impossible) in the given order, but easy after switching. **Always sketch the region first.**\n\n**Procedure:**\n1. Sketch the region $D$ described by the given iterated integral.\n2. Re-describe $D$ with the roles of $x$ and $y$ swapped.\n3. Write the new iterated integral with the new limits.\n\n**Example.** Switch the order: $\\displaystyle\\int_0^1\\int_x^1 e^{y^2}\\,dy\\,dx$.\n\nThe region is $D = \\{0 \\leq x \\leq 1,\\; x \\leq y \\leq 1\\}$.\nSketching: $D = \\{0 \\leq y \\leq 1,\\; 0 \\leq x \\leq y\\}$.\n\n$$\\int_0^1\\int_0^y e^{y^2}\\,dx\\,dy = \\int_0^1 y\\, e^{y^2}\\,dy = \\left[\\frac{e^{y^2}}{2}\\right]_0^1 = \\frac{e-1}{2}.$$\n\n(In the original order, $\\int e^{y^2}\\,dy$ has no elementary antiderivative.)",
      "body_he_md": "\u05dc\u05e2\u05d9\u05ea\u05d9\u05dd \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05e4\u05e0\u05d9\u05de\u05d9 \u05e7\u05e9\u05d4 (\u05d0\u05d5 \u05d1\u05dc\u05ea\u05d9 \u05d0\u05e4\u05e9\u05e8\u05d9) \u05d1\u05e1\u05d3\u05e8 \u05d4\u05e0\u05ea\u05d5\u05df, \u05d0\u05d1\u05dc \u05e7\u05dc \u05dc\u05d0\u05d7\u05e8 \u05d4\u05d7\u05dc\u05e4\u05d4. **\u05ea\u05de\u05d9\u05d3 \u05e9\u05e8\u05d8\u05d8\u05d5 \u05d0\u05ea \u05d4\u05d0\u05d6\u05d5\u05e8 \u05ea\u05d7\u05d9\u05dc\u05d4.**\n\n**\u05e1\u05d3\u05e8 \u05e4\u05e2\u05d5\u05dc\u05d4:**\n1. \u05e9\u05e8\u05d8\u05d8\u05d5 \u05d0\u05ea $D$.\n2. \u05ea\u05d0\u05e8\u05d5 \u05de\u05d7\u05d3\u05e9 \u05d0\u05ea $D$ \u05e2\u05dd \u05ea\u05e4\u05e7\u05d9\u05d3\u05d9 $x$ \u05d5-$y$ \u05de\u05d5\u05d7\u05dc\u05e4\u05d9\u05dd.\n3. \u05db\u05ea\u05d1\u05d5 \u05d0\u05ea \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05d7\u05d5\u05d6\u05e8 \u05d4\u05d7\u05d3\u05e9 \u05e2\u05dd \u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d7\u05d3\u05e9\u05d9\u05dd.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4.** \u05d4\u05d7\u05dc\u05e4: $\\displaystyle\\int_0^1\\int_x^1 e^{y^2}\\,dy\\,dx$.\n\n$D$: $0 \\leq x \\leq 1$, $x \\leq y \\leq 1$. \u05d1\u05e1\u05d3\u05e8 \u05d4\u05d7\u05d3\u05e9: $0 \\leq y \\leq 1$, $0 \\leq x \\leq y$.\n\n$$\\int_0^1 y\\,e^{y^2}\\,dy = \\frac{e-1}{2}.$$"
    },
    {
      "id": "applications",
      "title_en": "Applications \u2014 Area, Average Value, Center of Mass",
      "title_he": "\u05d9\u05d9\u05e9\u05d5\u05de\u05d9\u05dd \u2014 \u05e9\u05d8\u05d7, \u05e2\u05e8\u05da \u05de\u05de\u05d5\u05e6\u05e2, \u05de\u05e8\u05db\u05d6 \u05de\u05e1\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "**Area:** $\\text{Area}(D) = \\iint_D 1\\,dA$.\n\n**Average value:** $\\bar{f} = \\dfrac{1}{\\text{Area}(D)} \\iint_D f(x,y)\\,dA$.\n\n**Center of mass** (uniform density): $\\bar{x} = \\dfrac{\\iint_D x\\,dA}{\\text{Area}(D)}$, $\\;\\bar{y} = \\dfrac{\\iint_D y\\,dA}{\\text{Area}(D)}$.\n\n**Non-uniform density $\\rho(x,y)$:**\n$$\\text{Mass} = \\iint_D \\rho(x,y)\\,dA, \\quad \\bar{x} = \\frac{\\iint_D x\\,\\rho(x,y)\\,dA}{\\text{Mass}}.$$\n\n**Example.** Area of the unit disk $x^2 + y^2 \\leq 1$:\n$$\\int_{-1}^{1}\\int_{-\\sqrt{1-x^2}}^{\\sqrt{1-x^2}} 1\\,dy\\,dx = \\pi.$$\n(This integral is much easier in polar coordinates, but Cartesian confirms $\\pi$.)",
      "body_he_md": "**\u05e9\u05d8\u05d7:** $\\text{Area}(D) = \\iint_D 1\\,dA$.\n\n**\u05e2\u05e8\u05da \u05de\u05de\u05d5\u05e6\u05e2:** $\\bar{f} = \\dfrac{1}{\\text{Area}(D)} \\iint_D f(x,y)\\,dA$.\n\n**\u05de\u05e8\u05db\u05d6 \u05de\u05e1\u05d4** (\u05e6\u05e4\u05d9\u05e4\u05d5\u05ea \u05d0\u05d7\u05d9\u05d3\u05d4): $\\bar{x} = \\dfrac{\\iint_D x\\,dA}{\\text{Area}(D)}$, $\\;\\bar{y} = \\dfrac{\\iint_D y\\,dA}{\\text{Area}(D)}$.\n\n**\u05e6\u05e4\u05d9\u05e4\u05d5\u05ea \u05dc\u05d0 \u05d0\u05d7\u05d9\u05d3\u05d4 $\\rho(x,y)$:**\n$$\\text{Mass} = \\iint_D \\rho\\,dA, \\quad \\bar{x} = \\frac{\\iint_D x\\rho\\,dA}{\\text{Mass}}.$$\n\n**\u05d3\u05d5\u05d2\u05de\u05d4.** \u05e9\u05d8\u05d7 \u05d3\u05d9\u05e1\u05e7\u05d0\u05d5\u05ea \u05d4\u05d9\u05d7\u05d9\u05d3\u05d4: $\\iint 1\\,dA = \\pi$."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "Compute $\\displaystyle\\iint_{[0,2]\\times[0,3]} (x + y)\\,dA$.",
      "body_he": "\u05d7\u05e9\u05d1 $\\displaystyle\\iint_{[0,2]\\times[0,3]} (x + y)\\,dA$.",
      "options": [
        {"id": "a", "text_en": "$15$", "text_he": "$15$", "correct": True},
        {"id": "b", "text_en": "$12$", "text_he": "$12$", "correct": False},
        {"id": "c", "text_en": "$18$", "text_he": "$18$", "correct": False},
        {"id": "d", "text_en": "$10$", "text_he": "$10$", "correct": False}
      ],
      "explanation_en": "$\\int_0^2\\int_0^3(x+y)\\,dy\\,dx = \\int_0^2\\left[xy + y^2/2\\right]_0^3 dx = \\int_0^2(3x + 9/2)\\,dx = [3x^2/2 + 9x/2]_0^2 = 6 + 9 = 15$.",
      "explanation_he": "$\\int_0^2\\int_0^3(x+y)\\,dy\\,dx = \\int_0^2(3x + 9/2)\\,dx = [3x^2/2 + 9x/2]_0^2 = 6 + 9 = 15$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "Compute $\\iint_D y\\,dA$ where $D$ is the region bounded by $y=x$ and $y=x^2$ (for $0 \\leq x \\leq 1$).",
      "body_he": "\u05d7\u05e9\u05d1 $\\iint_D y\\,dA$ \u05db\u05d0\u05e9\u05e8 $D$ \u05d4\u05d5\u05d0 \u05d4\u05d0\u05d6\u05d5\u05e8 \u05d4\u05d7\u05e1\u05d5\u05dd \u05d1\u05d9\u05df $y=x$ \u05dc-$y=x^2$ (\u05e2\u05d1\u05d5\u05e8 $0 \\leq x \\leq 1$).",
      "options": [
        {"id": "a", "text_en": "$1/8$", "text_he": "$1/8$", "correct": True},
        {"id": "b", "text_en": "$1/6$", "text_he": "$1/6$", "correct": False},
        {"id": "c", "text_en": "$1/4$", "text_he": "$1/4$", "correct": False},
        {"id": "d", "text_en": "$1/12$", "text_he": "$1/12$", "correct": False}
      ],
      "explanation_en": "$D$: $0 \\leq x \\leq 1$, $x^2 \\leq y \\leq x$. So $\\int_0^1\\int_{x^2}^x y\\,dy\\,dx = \\int_0^1\\frac{x^2-x^4}{2}\\,dx = \\frac{1}{2}\\left[\\frac{x^3}{3}-\\frac{x^5}{5}\\right]_0^1 = \\frac{1}{2}\\cdot\\frac{2}{15} = \\frac{1}{15}$. Wait, let me recheck: $\\int_0^1\\frac{x^2-x^4}{2}dx = \\frac{1}{2}(1/3 - 1/5) = \\frac{1}{2}\\cdot\\frac{2}{15} = \\frac{1}{15}$. Hmm, the answer should be 1/8. Let me recheck with the correct answer 1/8. Actually $\\int_{x^2}^x y\\,dy = [y^2/2]_{x^2}^x = (x^2-x^4)/2$. Then $\\int_0^1(x^2-x^4)/2\\,dx = (1/3-1/5)/2 = (2/15)/2 = 1/15$. So the correct answer is 1/15, not 1/8. I need to fix this.",
      "explanation_he": "$D$: $0 \\leq x \\leq 1$, $x^2 \\leq y \\leq x$. $\\int_0^1\\frac{x^2-x^4}{2}\\,dx = \\frac{1}{2}\\left(\\frac{1}{3}-\\frac{1}{5}\\right) = \\frac{1}{15}$."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "By Fubini\u2019s theorem, $\\displaystyle\\iint_{[1,2]\\times[0,1]} \\frac{x}{y+1}\\,dA$ equals:",
      "body_he": "\u05dc\u05e4\u05d9 \u05de\u05e9\u05e4\u05d8 \u05e4\u05d5\u05d1\u05d9\u05e0\u05d9, $\\displaystyle\\iint_{[1,2]\\times[0,1]} \\frac{x}{y+1}\\,dA$ \u05e9\u05d5\u05d5\u05d4 \u05dc:",
      "options": [
        {"id": "a", "text_en": "$\\frac{3}{2}\\ln 2$", "text_he": "$\\frac{3}{2}\\ln 2$", "correct": True},
        {"id": "b", "text_en": "$\\ln 2$", "text_he": "$\\ln 2$", "correct": False},
        {"id": "c", "text_en": "$3\\ln 2$", "text_he": "$3\\ln 2$", "correct": False},
        {"id": "d", "text_en": "$\\frac{1}{2}\\ln 2$", "text_he": "$\\frac{1}{2}\\ln 2$", "correct": False}
      ],
      "explanation_en": "The integrand separates: $\\int_1^2 x\\,dx \\cdot \\int_0^1 \\frac{1}{y+1}\\,dy = \\left[\\frac{x^2}{2}\\right]_1^2 \\cdot [\\ln(y+1)]_0^1 = \\frac{3}{2} \\cdot \\ln 2 = \\frac{3\\ln 2}{2}$.",
      "explanation_he": "\u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05e0\u05d3 \u05de\u05ea\u05e4\u05e6\u05dc: $\\int_1^2 x\\,dx \\cdot \\int_0^1 \\frac{dy}{y+1} = \\frac{3}{2}\\ln 2$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "To evaluate $\\displaystyle\\int_0^1\\int_y^1 e^{x^2}\\,dx\\,dy$, we switch the order. The new integral is:",
      "body_he": "\u05db\u05d3\u05d9 \u05dc\u05d7\u05e9\u05d1 $\\displaystyle\\int_0^1\\int_y^1 e^{x^2}\\,dx\\,dy$, \u05de\u05d7\u05dc\u05d9\u05e4\u05d9\u05dd \u05e1\u05d3\u05e8. \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05d7\u05d3\u05e9 \u05d4\u05d5\u05d0:",
      "options": [
        {"id": "a", "text_en": "$\\displaystyle\\int_0^1\\int_0^x e^{x^2}\\,dy\\,dx$", "text_he": "$\\displaystyle\\int_0^1\\int_0^x e^{x^2}\\,dy\\,dx$", "correct": True},
        {"id": "b", "text_en": "$\\displaystyle\\int_0^1\\int_0^y e^{x^2}\\,dx\\,dy$", "text_he": "$\\displaystyle\\int_0^1\\int_0^y e^{x^2}\\,dx\\,dy$", "correct": False},
        {"id": "c", "text_en": "$\\displaystyle\\int_0^1\\int_x^1 e^{x^2}\\,dy\\,dx$", "text_he": "$\\displaystyle\\int_0^1\\int_x^1 e^{x^2}\\,dy\\,dx$", "correct": False},
        {"id": "d", "text_en": "$\\displaystyle\\int_0^1\\int_0^1 e^{x^2}\\,dy\\,dx$", "text_he": "$\\displaystyle\\int_0^1\\int_0^1 e^{x^2}\\,dy\\,dx$", "correct": False}
      ],
      "explanation_en": "The region is $\\{0\\leq y\\leq 1,\\; y\\leq x\\leq 1\\}$, equivalently $\\{0\\leq x\\leq 1,\\; 0\\leq y\\leq x\\}$. So the switched integral is $\\int_0^1\\int_0^x e^{x^2}\\,dy\\,dx = \\int_0^1 xe^{x^2}\\,dx = [e^{x^2}/2]_0^1 = (e-1)/2$.",
      "explanation_he": "\u05d4\u05d0\u05d6\u05d5\u05e8 $\\{0\\leq y\\leq 1, y\\leq x\\leq 1\\}$, \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9: $\\{0\\leq x\\leq 1, 0\\leq y\\leq x\\}$. \u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d7\u05d3\u05e9: $\\int_0^1\\int_0^x e^{x^2}\\,dy\\,dx = \\int_0^1 xe^{x^2}\\,dx = (e-1)/2$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "Geometrically, $\\iint_D f(x,y)\\,dA$ (with $f \\geq 0$) represents:",
      "body_he": "\u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05ea, $\\iint_D f(x,y)\\,dA$ (\u05e2\u05dd $f \\geq 0$) \u05de\u05d9\u05d9\u05e6\u05d2:",
      "options": [
        {"id": "a", "text_en": "The area of the region $D$", "text_he": "\u05e9\u05d8\u05d7 \u05d4\u05d0\u05d6\u05d5\u05e8 $D$", "correct": False},
        {"id": "b", "text_en": "The volume of the solid bounded above by $z=f(x,y)$ and below by the region $D$", "text_he": "\u05e0\u05e4\u05d7 \u05d4\u05d2\u05d5\u05e3 \u05d4\u05d7\u05e1\u05d5\u05dd \u05de\u05e2\u05dc \u05e2\u05dc \u05d9\u05d3\u05d9 $z=f(x,y)$ \u05d5\u05de\u05ea\u05d7\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05d0\u05d6\u05d5\u05e8 $D$", "correct": True},
        {"id": "c", "text_en": "The surface area of $z = f(x,y)$ over $D$", "text_he": "\u05e9\u05d8\u05d7 \u05d4\u05de\u05e9\u05d8\u05d7 $z = f(x,y)$ \u05de\u05e2\u05dc $D$", "correct": False},
        {"id": "d", "text_en": "The average value of $f$ over $D$", "text_he": "\u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2 \u05e9\u05dc $f$ \u05e2\u05dc $D$", "correct": False}
      ],
      "explanation_en": "When $f(x,y) \\geq 0$, the double integral gives the volume of the 3D solid between the surface $z=f(x,y)$ and the region $D$ in the $xy$-plane. The area is $\\iint_D 1\\,dA$ (option a with $f\\equiv 1$); the average is $\\iint_D f\\,dA / \\text{Area}(D)$.",
      "explanation_he": "\u05db\u05d0\u05e9\u05e8 $f \\geq 0$, \u05d4\u05d0\u05d9\u05e0\u05d8\u05d2\u05e8\u05dc \u05d4\u05db\u05e4\u05d5\u05dc \u05e0\u05d5\u05ea\u05df \u05d0\u05ea \u05d4\u05e0\u05e4\u05d7 \u05e9\u05dc \u05d4\u05d2\u05d5\u05e3 \u05d4\u05ea\u05dc\u05ea-\u05de\u05de\u05d3\u05d9 \u05d1\u05d9\u05df \u05d4\u05de\u05e9\u05d7 $z=f(x,y)$ \u05dc-$D$."
    }
  ]
}

# Fix q2 - the answer should be 1/15 not 1/8
lesson["questions"][1]["options"] = [
  {"id": "a", "text_en": "$1/15$", "text_he": "$1/15$", "correct": True},
  {"id": "b", "text_en": "$1/8$", "text_he": "$1/8$", "correct": False},
  {"id": "c", "text_en": "$1/6$", "text_he": "$1/6$", "correct": False},
  {"id": "d", "text_en": "$1/12$", "text_he": "$1/12$", "correct": False}
]
lesson["questions"][1]["explanation_en"] = "$D$: $0 \\leq x \\leq 1$, $x^2 \\leq y \\leq x$ (Type I). $\\int_0^1\\int_{x^2}^x y\\,dy\\,dx = \\int_0^1\\frac{x^2-x^4}{2}\\,dx = \\frac{1}{2}\\!\\left(\\frac{1}{3}-\\frac{1}{5}\\right) = \\frac{1}{2}\\cdot\\frac{2}{15} = \\frac{1}{15}$."
lesson["questions"][1]["explanation_he"] = "$D$: $0 \\leq x \\leq 1$, $x^2 \\leq y \\leq x$. $\\int_0^1\\frac{x^2-x^4}{2}\\,dx = \\frac{1}{2}\\left(\\frac{1}{3}-\\frac{1}{5}\\right) = \\frac{1}{15}$."

path = os.path.join(BASE, lesson["id"] + ".json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
print(f"Saved {lesson['id']}")
