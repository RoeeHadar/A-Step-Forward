"""Write Lesson 2: mean_value_theorem"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))

lesson = {
  "id": "mean_value_theorem",
  "type": "interactive",
  "subject": "calculus_1",
  "title_en": "The Mean Value Theorem",
  "title_he": "\u05de\u05e9\u05e4\u05d8 \u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2",
  "duration_min": 20,
  "level_min": "calculus_1",
  "agent_hints": "Students should know that MVT requires two hypotheses: continuity on the closed interval AND differentiability on the open interval. The most common exam tasks are: (1) find the guaranteed point c, (2) use MVT to prove an inequality like |f(x)-f(y)| <= M|x-y|, (3) use a corollary to conclude monotonicity or constancy. Always connect MVT to its geometric meaning \u2014 some tangent line is parallel to the secant \u2014 before writing the formula.",
  "sections": [
    {
      "id": "rolles_theorem",
      "title_en": "Rolle\u2019s Theorem",
      "title_he": "\u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc",
      "level_min": "calculus_1",
      "body_en_md": "**Rolle\u2019s Theorem.** Let $f$ be continuous on $[a, b]$, differentiable on $(a, b)$, and satisfy $f(a) = f(b)$. Then there exists $c \\in (a, b)$ such that $f'(c) = 0$.\n\n**Geometric meaning:** If a smooth curve starts and ends at the same height, it must have at least one horizontal tangent in between.\n\n**Why all three conditions are needed:**\n- Without *continuity* on $[a,b]$: a jump discontinuity can prevent a horizontal tangent.\n- Without *differentiability* on $(a,b)$: a corner (like $f(x)=|x|$ on $[-1,1]$) has $f(-1)=f(1)$ but no point where $f'=0$.\n- Without $f(a)=f(b)$: $f(x)=x$ on $[0,1]$ has no horizontal tangent.\n\n**Proof sketch.** $f$ attains its maximum and minimum on $[a,b]$ (Extreme Value Theorem). If both extrema occur at the endpoints, then $f$ is constant and $f'\\equiv 0$. Otherwise, an interior extremum $c$ exists, and $f'(c) = 0$ by Fermat\u2019s theorem.",
      "body_he_md": "**\u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc.** \u05ea\u05d4\u05d9 $f$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1-$[a, b]$, \u05d2\u05d6\u05d9\u05e8\u05d4 \u05d1-$(a, b)$, \u05d5\u05de\u05e7\u05d9\u05d9\u05de\u05ea $f(a) = f(b)$. \u05d0\u05d6 \u05e7\u05d9\u05d9\u05dd $c \\in (a, b)$ \u05db\u05da \u05e9-$f'(c) = 0$.\n\n**\u05de\u05e9\u05de\u05e2\u05d5\u05ea \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9:** \u05d0\u05dd \u05e2\u05e7\u05d5\u05de\u05d4 \u05d7\u05dc\u05e7\u05d4 \u05de\u05ea\u05d7\u05d9\u05dc\u05d4 \u05d5\u05de\u05e1\u05d9\u05d9\u05de\u05ea \u05d1\u05d0\u05d5\u05ea\u05d5 \u05d2\u05d5\u05d1\u05d4, \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d4\u05d9\u05d5\u05ea \u05dc\u05d4 \u05dc\u05e4\u05d7\u05d5\u05ea \u05e9\u05d9\u05e4\u05d5\u05e2 \u05d0\u05d5\u05e4\u05e7\u05d9 \u05d0\u05d7\u05d3 \u05d1\u05d9\u05e0\u05ea\u05d9\u05d9\u05dd.\n\n**\u05dc\u05de\u05d4 \u05e9\u05dc\u05d5\u05e9\u05ea \u05d4\u05ea\u05e0\u05d0\u05d9\u05dd \u05e0\u05d7\u05d5\u05e6\u05d9\u05dd:**\n- \u05dc\u05dc\u05d0 *\u05e8\u05e6\u05d9\u05e4\u05d5\u05ea* \u05d1-$[a,b]$: \u05e7\u05e4\u05d9\u05e6\u05ea \u05d0\u05d9 -\u05e8\u05e6\u05d9\u05e4\u05d5\u05ea \u05de\u05d5\u05e0\u05e2\u05ea \u05e9\u05d9\u05e4\u05d5\u05e2 \u05d0\u05d5\u05e4\u05e7\u05d9.\n- \u05dc\u05dc\u05d0 *\u05d2\u05d6\u05d9\u05e8\u05d5\u05ea* \u05d1-$(a,b)$: \u05e4\u05d9\u05e0\u05d4 (כגון $f(x)=|x|$ \u05d1-$[-1,1]$) \u05d0\u05d9\u05e0\u05d4 \u05e2\u05d5\u05e0\u05d4 \u05dc\u05e7\u05e8\u05d9\u05ea\u05e8\u05d9\u05d5\u05df.\n- \u05dc\u05dc\u05d0 $f(a)=f(b)$: $f(x)=x$ \u05d1-$[0,1]$ \u05d0\u05d9\u05df \u05e0\u05e7\u05d5\u05d3\u05d4 \u05d0\u05d5\u05e4\u05e7\u05d9\u05ea.\n\n**\u05d4\u05d5\u05db\u05d7\u05d4 \u05d1\u05e7\u05e6\u05e8\u05d4.** $f$ \u05de\u05e9\u05d9\u05d2\u05d4 \u05de\u05e7\u05e1\u05d9\u05de\u05d5\u05dd \u05d5\u05de\u05d9\u05e0\u05d9\u05de\u05d5\u05dd \u05d1-$[a,b]$ (\u05de\u05e9\u05e4\u05d8 \u05d5\u05d9\u05d9\u05e8\u05e9\u05d8\u05e8\u05e1). \u05d0\u05dd \u05e9\u05e0\u05d9 \u05d4\u05e7\u05e6\u05d5\u05d5\u05ea \u05d1\u05e7\u05e6\u05d4 \u05d4\u05e7\u05d8\u05e2\u05d9\u05dd, \u05d0\u05d6 $f$ \u05e7\u05d1\u05d5\u05e2\u05d4 \u05d5-$f'\\equiv 0$. \u05d0\u05d7\u05e8\u05ea, \u05e7\u05d9\u05d9\u05dd \u05e7\u05d9\u05e6\u05d5\u05df \u05e4\u05e0\u05d9\u05de\u05d9 $c$, \u05d5\u05dc\u05e4\u05d9 \u05de\u05e9\u05e4\u05d8 \u05e4\u05e8\u05de\u05d4 $f'(c)=0$."
    },
    {
      "id": "mvt_statement",
      "title_en": "The Mean Value Theorem \u2014 Statement and Geometry",
      "title_he": "\u05de\u05e9\u05e4\u05d8 \u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2 \u2014 \u05d0\u05de\u05d9\u05e8\u05d4 \u05d5\u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "**Mean Value Theorem (MVT).** Let $f$ be continuous on $[a, b]$ and differentiable on $(a, b)$. Then there exists $c \\in (a, b)$ such that:\n$$\\boxed{f'(c) = \\frac{f(b) - f(a)}{b - a}.}$$\n\n**Geometric meaning:** The slope of the tangent at $c$ equals the slope of the secant line through $(a, f(a))$ and $(b, f(b))$. Equivalently: *some tangent line is parallel to the secant*.\n\n**Example.** Let $f(x) = x^2$ on $[1, 3]$. The secant slope is $\\dfrac{9 - 1}{3 - 1} = 4$. MVT guarantees $c \\in (1,3)$ with $f'(c) = 2c = 4$, so $c = 2$. Indeed $c = 2 \\in (1,3)$. \\checkmark\n\n**Cauchy\u2019s MVT (generalized).** If also $g$ is continuous on $[a,b]$, differentiable on $(a,b)$, and $g'(x) \\neq 0$ on $(a,b)$, then:\n$$\\frac{f(b)-f(a)}{g(b)-g(a)} = \\frac{f'(c)}{g'(c)} \\quad\\text{for some } c \\in (a,b).$$",
      "body_he_md": "**\u05de\u05e9\u05e4\u05d8 \u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2 (MVT).** \u05ea\u05d4\u05d9 $f$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1-$[a, b]$ \u05d5\u05d2\u05d6\u05d9\u05e8\u05d4 \u05d1-$(a, b)$. \u05d0\u05d6 \u05e7\u05d9\u05d9\u05dd $c \\in (a, b)$ \u05db\u05da \u05e9:\n$$\\boxed{f'(c) = \\frac{f(b) - f(a)}{b - a}.}$$\n\n**\u05de\u05e9\u05de\u05e2\u05d5\u05ea \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9:** \u05e9\u05d9\u05e4\u05d5\u05e2 \u05d4\u05de\u05e9\u05d9\u05e7 \u05d1-$c$ \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e9\u05d9\u05e4\u05d5\u05e2 \u05d4\u05de\u05d9\u05ea\u05e8 \u05d3\u05e8\u05da $(a, f(a))$ \u05d5-$(b, f(b))$. \u05d1\u05de\u05d9\u05dc\u05d9\u05dd \u05d0\u05d7\u05e8\u05d5\u05ea: *\u05e7\u05d9\u05d9\u05dd \u05de\u05e9\u05d9\u05e7 \u05db\u05dc\u05e9\u05d4\u05d5 \u05de\u05e7\u05d1\u05d9\u05dc \u05dc\u05de\u05d9\u05ea\u05e8*.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4.** \u05ea\u05d4\u05d9 $f(x) = x^2$ \u05d1-$[1, 3]$. \u05e9\u05d9\u05e4\u05d5\u05e2 \u05d4\u05de\u05d9\u05ea\u05e8 $\\dfrac{9 - 1}{3 - 1} = 4$. MVT \u05de\u05d1\u05d8\u05d9\u05d7 $c \\in (1,3)$ \u05e2\u05dd $f'(c) = 2c = 4$, \u05dc\u05db\u05df $c = 2$. \u05d0\u05db\u05df $c = 2 \\in (1,3)$. \\checkmark"
    },
    {
      "id": "mvt_proof",
      "title_en": "Proof of MVT via Rolle\u2019s Theorem",
      "title_he": "\u05d4\u05d5\u05db\u05d7\u05ea MVT \u05d1\u05d0\u05de\u05e6\u05e2\u05d5\u05ea \u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc",
      "level_min": "calculus_1",
      "body_en_md": "**Proof.** Define the auxiliary function:\n$$g(x) = f(x) - f(a) - \\frac{f(b)-f(a)}{b-a}(x - a).$$\n\n$g$ subtracts the secant line from $f$. Check:\n- $g(a) = f(a) - f(a) - 0 = 0$.\n- $g(b) = f(b) - f(a) - (f(b)-f(a)) = 0$.\n\nSo $g(a) = g(b) = 0$, $g$ is continuous on $[a,b]$, and differentiable on $(a,b)$.\n\nBy **Rolle\u2019s Theorem**, $\\exists\\, c \\in (a,b)$ with $g'(c) = 0$.\n\nComputing: $g'(x) = f'(x) - \\dfrac{f(b)-f(a)}{b-a}$.\n\nSo $g'(c) = 0$ gives:\n$$f'(c) = \\frac{f(b)-f(a)}{b-a}. \\quad\\square$$",
      "body_he_md": "**\u05d4\u05d5\u05db\u05d7\u05d4.** \u05e0\u05d2\u05d3\u05d9\u05e8 \u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d9\u05ea \u05e2\u05d6\u05e8:\n$$g(x) = f(x) - f(a) - \\frac{f(b)-f(a)}{b-a}(x - a).$$\n\n$g$ \u05de\u05d7\u05e1\u05e8\u05ea \u05de-$f$ \u05d0\u05ea \u05d9\u05e9\u05e8 \u05d4\u05de\u05d9\u05ea\u05e8. \u05d1\u05d3\u05d9\u05e7\u05d4:\n- $g(a) = 0$.\n- $g(b) = 0$.\n\n\u05dc\u05db\u05df $g(a) = g(b) = 0$, $g$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1-$[a,b]$ \u05d5\u05d2\u05d6\u05d9\u05e8\u05d4 \u05d1-$(a,b)$.\n\n\u05dc\u05e4\u05d9 **\u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc**, \u05e7\u05d9\u05d9\u05dd $c \\in (a,b)$ \u05e2\u05dd $g'(c) = 0$.\n\n\u05d7\u05e9\u05d1: $g'(x) = f'(x) - \\dfrac{f(b)-f(a)}{b-a}$.\n\n\u05dc\u05db\u05df $g'(c) = 0$ \u05e0\u05d5\u05ea\u05df:\n$$f'(c) = \\frac{f(b)-f(a)}{b-a}. \\quad\\square$$"
    },
    {
      "id": "corollaries",
      "title_en": "Corollaries of MVT",
      "title_he": "\u05de\u05e1\u05e7\u05e0\u05d5\u05ea \u05d4\u05e0\u05d2\u05d6\u05e8\u05d5\u05ea \u05de\u05de\u05e9\u05e4\u05d8 \u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2",
      "level_min": "calculus_1",
      "body_en_md": "**Corollary 1 (Constant function).** If $f'(x) = 0$ for all $x \\in (a,b)$, then $f$ is constant on $[a,b]$.\n\n*Proof:* For any $x_1, x_2 \\in [a,b]$, MVT gives $f(x_2)-f(x_1) = f'(c)(x_2-x_1) = 0$. $\\square$\n\n**Corollary 2 (Monotonicity).** If $f'(x) > 0$ for all $x \\in (a,b)$, then $f$ is strictly increasing on $[a,b]$. (Similarly for $f' < 0$ and strictly decreasing.)\n\n**Corollary 3 (Equal derivatives).** If $f'(x) = g'(x)$ for all $x \\in (a,b)$, then $f - g$ is constant.\n\n**Application: Lipschitz bound.** If $|f'(x)| \\leq M$ on $(a,b)$, then for all $x, y \\in [a,b]$:\n$$|f(x) - f(y)| \\leq M|x - y|.$$\n\n*Proof:* MVT gives $f(x)-f(y) = f'(c)(x-y)$ for some $c$, so $|f(x)-f(y)| = |f'(c)||x-y| \\leq M|x-y|$. $\\square$\n\n**Example:** Prove $|\\sin x - \\sin y| \\leq |x - y|$ for all $x, y \\in \\mathbb{R}$.\n\nSince $|\\cos c| \\leq 1$, the Lipschitz bound gives $|\\sin x - \\sin y| = |\\cos c||x-y| \\leq |x-y|$. $\\square$",
      "body_he_md": "**\u05de\u05e1\u05e7\u05e0\u05d0 1 (\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05e7\u05d1\u05d5\u05e2\u05d4).** \u05d0\u05dd $f'(x) = 0$ \u05dc\u05db\u05dc $x \\in (a,b)$, \u05d0\u05d6 $f$ \u05e7\u05d1\u05d5\u05e2\u05d4 \u05d1-$[a,b]$.\n\n*\u05d4\u05d5\u05db\u05d7\u05d4:* \u05dc\u05db\u05dc $x_1, x_2$, MVT \u05e0\u05d5\u05ea\u05df $f(x_2)-f(x_1) = f'(c)(x_2-x_1) = 0$. $\\square$\n\n**\u05de\u05e1\u05e7\u05e0\u05d0 2 (\u05de\u05d5\u05e0\u05d5\u05d8\u05d5\u05e0\u05d9\u05d5\u05ea).** \u05d0\u05dd $f'(x) > 0$ \u05dc\u05db\u05dc $x \\in (a,b)$, \u05d0\u05d6 $f$ \u05e2\u05d5\u05dc\u05d4 \u05d1\u05d7\u05d9\u05d3\u05d5\u05ea \u05d1-$[a,b]$.\n\n**\u05de\u05e1\u05e7\u05e0\u05d0 3 (\u05e0\u05d2\u05d6\u05e8\u05d5\u05ea \u05e9\u05d5\u05d5\u05ea).** \u05d0\u05dd $f'(x) = g'(x)$ \u05dc\u05db\u05dc $x$, \u05d0\u05d6 $f - g$ \u05e7\u05d1\u05d5\u05e2\u05d4.\n\n**\u05d9\u05d9\u05e9\u05d5\u05dd: \u05d7\u05e1\u05dd \u05dc\u05d9\u05e4\u05e9\u05d9\u05e5.** \u05d0\u05dd $|f'(x)| \\leq M$ \u05d1-$(a,b)$, \u05d0\u05d6 \u05dc\u05db\u05dc $x, y \\in [a,b]$:\n$$|f(x) - f(y)| \\leq M|x - y|.$$\n\n**\u05d3\u05d5\u05d2\u05de\u05d4:** \u05d4\u05d5\u05db\u05d7 \u05e9-$|\\sin x - \\sin y| \\leq |x - y|$.\n\n\u05de\u05db\u05d9\u05d5\u05d5\u05df \u05e9-$|\\cos c| \\leq 1$: $|\\sin x - \\sin y| = |\\cos c||x-y| \\leq |x-y|$. $\\square$"
    },
    {
      "id": "connection_to_taylor",
      "title_en": "Connection to Taylor\u2019s Theorem",
      "title_he": "\u05e7\u05e9\u05e8 \u05dc\u05de\u05e9\u05e4\u05d8 \u05d8\u05d9\u05d9\u05dc\u05d5\u05e8",
      "level_min": "calculus_1",
      "body_en_md": "MVT is the $n=1$ case of Taylor\u2019s theorem with the Lagrange remainder:\n$$f(b) = f(a) + f'(c)(b-a) \\quad\\Leftrightarrow\\quad f'(c) = \\frac{f(b)-f(a)}{b-a}.$$\n\nMore generally, **Taylor\u2019s theorem** says:\n$$f(b) = \\sum_{k=0}^{n} \\frac{f^{(k)}(a)}{k!}(b-a)^k + \\frac{f^{(n+1)}(c)}{(n+1)!}(b-a)^{n+1}$$\nfor some $c$ between $a$ and $b$. Setting $n=0$ recovers MVT exactly.\n\n**Another connection \u2014 L\u2019H\u00f4pital\u2019s rule** follows from Cauchy\u2019s MVT: if $f(a)=g(a)=0$ and $g'\\neq 0$, then $\\dfrac{f(x)}{g(x)} = \\dfrac{f'(c)}{g'(c)} \\to \\dfrac{f'(a)}{g'(a)}$.",
      "body_he_md": "MVT \u05d4\u05d5\u05d0 \u05d4\u05de\u05e7\u05e8\u05d4 $n=1$ \u05e9\u05dc \u05de\u05e9\u05e4\u05d8 \u05d8\u05d9\u05d9\u05dc\u05d5\u05e8 \u05e2\u05dd \u05e9\u05d0\u05e8\u05d9\u05ea \u05dc\u05d2\u05e8\u05e0\u05d6':\n$$f(b) = f(a) + f'(c)(b-a).$$\n\n\u05d1\u05db\u05dc\u05dc\u05d9\u05d5\u05ea, **\u05de\u05e9\u05e4\u05d8 \u05d8\u05d9\u05d9\u05dc\u05d5\u05e8** \u05d0\u05d5\u05de\u05e8:\n$$f(b) = \\sum_{k=0}^{n} \\frac{f^{(k)}(a)}{k!}(b-a)^k + \\frac{f^{(n+1)}(c)}{(n+1)!}(b-a)^{n+1}.$$\n\u05e7\u05d1\u05d9\u05e2\u05ea $n=0$ \u05de\u05d7\u05d6\u05d9\u05e8\u05d4 \u05d1\u05d3\u05d9\u05d5\u05e7 \u05d0\u05ea MVT.\n\n**\u05e7\u05e9\u05e8 \u05e0\u05d5\u05e1\u05e3 \u2014 \u05db\u05dc\u05dc \u05dc\u05d5\u05e4\u05d9\u05d8\u05dc** \u05e0\u05d2\u05d6\u05e8 \u05de-MVT \u05e9\u05dc \u05e7\u05d5\u05e9\u05d9: \u05d0\u05dd $f(a)=g(a)=0$ \u05d5-$g'\\neq 0$, \u05d0\u05d6 $\\dfrac{f(x)}{g(x)} \\to \\dfrac{f'(a)}{g'(a)}$."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "Which condition is NOT required by Rolle\u2019s Theorem?",
      "body_he": "\u05d0\u05d9\u05d6\u05d4 \u05ea\u05e0\u05d0\u05d9 \u05d0\u05d9\u05e0\u05d5 \u05e0\u05d3\u05e8\u05e9 \u05d1\u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc?",
      "options": [
        {"id": "a", "text_en": "$f$ is continuous on $[a,b]$", "text_he": "$f$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1-$[a,b]$", "correct": False},
        {"id": "b", "text_en": "$f$ is differentiable on $(a,b)$", "text_he": "$f$ \u05d2\u05d6\u05d9\u05e8\u05d4 \u05d1-$(a,b)$", "correct": False},
        {"id": "c", "text_en": "$f(a) = f(b)$", "text_he": "$f(a) = f(b)$", "correct": False},
        {"id": "d", "text_en": "$f$ is differentiable at the endpoints $a$ and $b$", "text_he": "$f$ \u05d2\u05d6\u05d9\u05e8\u05d4 \u05d1\u05e7\u05e6\u05d5\u05d5\u05ea $a$ \u05d5-$b$", "correct": True}
      ],
      "explanation_en": "Rolle\u2019s theorem only requires differentiability on the open interval $(a,b)$, not at the endpoints. The function need only be continuous at $a$ and $b$.",
      "explanation_he": "\u05de\u05e9\u05e4\u05d8 \u05e8\u05d5\u05dc \u05d3\u05d5\u05e8\u05e9 \u05d2\u05d6\u05d9\u05e8\u05d5\u05ea \u05e8\u05e7 \u05d1\u05e7\u05d8\u05e2 \u05d4\u05e4\u05ea\u05d5\u05d7 $(a,b)$, \u05dc\u05d0 \u05d1\u05e7\u05e6\u05d5\u05d5\u05ea. \u05d1\u05e7\u05e6\u05d5\u05d5\u05ea \u05e0\u05d3\u05e8\u05e9\u05ea \u05e8\u05e7 \u05e8\u05e6\u05d9\u05e4\u05d5\u05ea."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "For $f(x) = x^3$ on $[0, 3]$, the MVT guarantees a point $c$ where $f'(c)$ equals the secant slope. What is $c$?",
      "body_he": "\u05e2\u05d1\u05d5\u05e8 $f(x) = x^3$ \u05d1-$[0, 3]$, MVT \u05de\u05d1\u05d8\u05d9\u05d7 \u05e0\u05e7\u05d5\u05d3\u05d4 $c$ \u05e9\u05d1\u05d4 $f'(c)$ \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e9\u05d9\u05e4\u05d5\u05e2 \u05d4\u05de\u05d9\u05ea\u05e8. \u05de\u05d4 \u05d4\u05d5\u05d0 $c$?",
      "options": [
        {"id": "a", "text_en": "$c = 1$", "text_he": "$c = 1$", "correct": False},
        {"id": "b", "text_en": "$c = \\sqrt{3}$", "text_he": "$c = \\sqrt{3}$", "correct": True},
        {"id": "c", "text_en": "$c = 3/2$", "text_he": "$c = 3/2$", "correct": False},
        {"id": "d", "text_en": "$c = 2$", "text_he": "$c = 2$", "correct": False}
      ],
      "explanation_en": "The secant slope is $\\dfrac{27-0}{3-0} = 9$. Setting $f'(c) = 3c^2 = 9$ gives $c^2 = 3$, so $c = \\sqrt{3} \\approx 1.73 \\in (0,3)$. \\checkmark",
      "explanation_he": "\u05e9\u05d9\u05e4\u05d5\u05e2 \u05d4\u05de\u05d9\u05ea\u05e8 $\\dfrac{27-0}{3-0} = 9$. \u05dc\u05e4\u05d9 $f'(c) = 3c^2 = 9$ \u05de\u05ea\u05e7\u05d1\u05dc $c^2 = 3$, \u05dc\u05db\u05df $c = \\sqrt{3} \\approx 1.73 \\in (0,3)$. \\checkmark"
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "To prove $|\\cos x - \\cos y| \\leq |x - y|$ for all $x, y \\in \\mathbb{R}$, the key step using MVT is:",
      "body_he": "\u05dc\u05d4\u05d5\u05db\u05d7\u05ea $|\\cos x - \\cos y| \\leq |x - y|$, \u05d4\u05e6\u05e2\u05d3 \u05d4\u05de\u05e8\u05db\u05d6\u05d9 \u05d1\u05d0\u05de\u05e6\u05e2\u05d5\u05ea MVT \u05d4\u05d5\u05d0:",
      "options": [
        {"id": "a", "text_en": "$\\cos x$ is bounded by $[-1,1]$", "text_he": "$\\cos x$ \u05d7\u05e1\u05d5\u05dd \u05d1-$[-1,1]$", "correct": False},
        {"id": "b", "text_en": "By MVT, $\\cos x - \\cos y = -\\sin(c)(x-y)$ for some $c$, and $|{-\\sin c}| \\leq 1$", "text_he": "\u05dc\u05e4\u05d9 MVT, $\\cos x - \\cos y = -\\sin(c)(x-y)$ \u05e2\u05d1\u05d5\u05e8 $c$ \u05db\u05dc\u05e9\u05d4\u05d5, \u05d5-$|{-\\sin c}| \\leq 1$", "correct": True},
        {"id": "c", "text_en": "$\\cos x$ is continuous everywhere", "text_he": "$\\cos x$ \u05e8\u05e6\u05d9\u05e4\u05d4 \u05d1\u05db\u05dc \u05de\u05e7\u05d5\u05dd", "correct": False},
        {"id": "d", "text_en": "The Taylor series of $\\cos x$ converges everywhere", "text_he": "\u05d8\u05d5\u05e8 \u05d8\u05d9\u05d9\u05dc\u05d5\u05e8 \u05e9\u05dc $\\cos x$ \u05de\u05ea\u05db\u05e0\u05e1 \u05d1\u05db\u05dc \u05de\u05e7\u05d5\u05dd", "correct": False}
      ],
      "explanation_en": "MVT applied to $\\cos$ on $[y,x]$ (or $[x,y]$) gives $\\cos x - \\cos y = (\\cos)'(c)(x-y) = -\\sin(c)(x-y)$. Since $|\\sin c| \\leq 1$, we get $|\\cos x - \\cos y| \\leq |x-y|$.",
      "explanation_he": "MVT \u05e2\u05dc $\\cos$ \u05d1-$[y,x]$ \u05e0\u05d5\u05ea\u05df $\\cos x - \\cos y = -\\sin(c)(x-y)$. \u05de\u05db\u05d9\u05d5\u05d5\u05df \u05e9-$|\\sin c| \\leq 1$: $|\\cos x - \\cos y| \\leq |x-y|$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "If $f'(x) = 0$ for all $x \\in (a, b)$, which corollary of MVT applies?",
      "body_he": "\u05d0\u05dd $f'(x) = 0$ \u05dc\u05db\u05dc $x \\in (a, b)$, \u05d0\u05d9\u05d6\u05d4 \u05de\u05e1\u05e7\u05e0\u05d0 \u05e9\u05dc MVT \u05d7\u05dc\u05d4?",
      "options": [
        {"id": "a", "text_en": "$f$ must equal zero on $(a,b)$", "text_he": "$f$ \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d4\u05d9\u05d5\u05ea \u05d0\u05e4\u05e1 \u05d1-$(a,b)$", "correct": False},
        {"id": "b", "text_en": "$f$ is constant on $[a,b]$", "text_he": "$f$ \u05e7\u05d1\u05d5\u05e2\u05d4 \u05d1-$[a,b]$", "correct": True},
        {"id": "c", "text_en": "$f$ is strictly increasing on $[a,b]$", "text_he": "$f$ \u05e2\u05d5\u05dc\u05d4 \u05d1\u05d7\u05d9\u05d3\u05d5\u05ea \u05d1-$[a,b]$", "correct": False},
        {"id": "d", "text_en": "$f$ has a local maximum at every point of $(a,b)$", "text_he": "$f$ \u05d9\u05e9 \u05dc\u05d4 \u05de\u05e7\u05e1\u05d9\u05de\u05d5\u05dd \u05de\u05e7\u05d5\u05de\u05d9 \u05d1\u05db\u05dc \u05e0\u05e7\u05d5\u05d3\u05d4 \u05d1-$(a,b)$", "correct": False}
      ],
      "explanation_en": "By the constant-function corollary: for any $x_1, x_2 \\in [a,b]$, MVT gives $f(x_2)-f(x_1)=f'(c)(x_2-x_1)=0$, so $f(x_2)=f(x_1)$. This means $f$ is constant.",
      "explanation_he": "\u05dc\u05e4\u05d9 \u05de\u05e1\u05e7\u05e0\u05d0 \u05d4\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05d4\u05e7\u05d1\u05d5\u05e2\u05d4: \u05dc\u05db\u05dc $x_1, x_2$, MVT \u05e0\u05d5\u05ea\u05df $f(x_2)-f(x_1)=f'(c)(x_2-x_1)=0$, \u05d0\u05d6 $f(x_2)=f(x_1)$. \u05db\u05dc\u05d5\u05de\u05e8 $f$ \u05e7\u05d1\u05d5\u05e2\u05d4."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "What does the Mean Value Theorem state geometrically?",
      "body_he": "\u05de\u05d4 \u05d0\u05d5\u05de\u05e8 \u05de\u05e9\u05e4\u05d8 \u05d4\u05e2\u05e8\u05da \u05d4\u05de\u05de\u05d5\u05e6\u05e2 \u05de\u05d1\u05d7\u05d9\u05e0\u05d4 \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05ea?",
      "options": [
        {"id": "a", "text_en": "The function reaches its average value at some interior point", "text_he": "\u05d4\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05de\u05d2\u05d9\u05e2\u05d4 \u05dc\u05e2\u05e8\u05db\u05d4 \u05d4\u05de\u05de\u05d5\u05e6\u05e2 \u05d1\u05e0\u05e7\u05d5\u05d3\u05d4 \u05e4\u05e0\u05d9\u05de\u05d9\u05ea \u05db\u05dc\u05e9\u05d4\u05d9", "correct": False},
        {"id": "b", "text_en": "There is at least one point where the tangent line is parallel to the secant line connecting the endpoints", "text_he": "\u05e7\u05d9\u05d9\u05dd \u05dc\u05e4\u05d7\u05d5\u05ea \u05e0\u05e7\u05d5\u05d3\u05d4 \u05d0\u05d7\u05ea \u05e9\u05d1\u05d4 \u05d4\u05de\u05e9\u05d9\u05e7 \u05de\u05e7\u05d1\u05d9\u05dc \u05dc\u05de\u05d9\u05ea\u05e8 \u05d4\u05de\u05d7\u05d1\u05e8 \u05d0\u05ea \u05d4\u05e7\u05e6\u05d5\u05d5\u05ea", "correct": True},
        {"id": "c", "text_en": "The function is symmetric about some point $c$", "text_he": "\u05d4\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05e1\u05d9\u05de\u05d8\u05e8\u05d9\u05ea \u05e1\u05d1\u05d9\u05d1 \u05e0\u05e7\u05d5\u05d3\u05d4 $c$ \u05db\u05dc\u05e9\u05d4\u05d9", "correct": False},
        {"id": "d", "text_en": "The area under the curve equals the area of a rectangle of width $b-a$", "text_he": "\u05d4\u05e9\u05d8\u05d7 \u05ea\u05d7\u05ea \u05d4\u05e2\u05e7\u05d5\u05de\u05d4 \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e9\u05d8\u05d7 \u05de\u05dc\u05d1\u05df \u05d1\u05e8\u05d5\u05d7\u05d1 $b-a$", "correct": False}
      ],
      "explanation_en": "MVT guarantees that somewhere on the curve, the tangent line has the same slope as the secant through the two endpoints $(a,f(a))$ and $(b,f(b))$, i.e., the tangent is parallel to the secant.",
      "explanation_he": "MVT \u05de\u05d1\u05d8\u05d9\u05d7 \u05e9\u05d1\u05e0\u05e7\u05d5\u05d3\u05d4 \u05db\u05dc\u05e9\u05d4\u05d9 \u05e2\u05dc \u05d4\u05e2\u05e7\u05d5\u05de\u05d4, \u05dc\u05de\u05e9\u05d9\u05e7 \u05d9\u05e9 \u05d0\u05d5\u05ea\u05d5 \u05e9\u05d9\u05e4\u05d5\u05e2 \u05db\u05de\u05d5 \u05dc\u05de\u05d9\u05ea\u05e8 \u05d4\u05de\u05d7\u05d1\u05e8 \u05d0\u05ea $(a,f(a))$ \u05d5-$(b,f(b))$, \u05db\u05dc\u05d5\u05de\u05e8 \u05d4\u05de\u05e9\u05d9\u05e7 \u05de\u05e7\u05d1\u05d9\u05dc \u05dc\u05de\u05d9\u05ea\u05e8."
    }
  ]
}

path = os.path.join(BASE, lesson["id"] + ".json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
print(f"Saved {lesson['id']}")
