"""Write all 6 new lesson JSON files."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def save(lesson):
    path = os.path.join(BASE, lesson["id"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
    print(f"Saved {lesson['id']}")


# ===========================================================================
# LESSON 1 — limits_epsilon_delta
# ===========================================================================
save({
  "id": "limits_epsilon_delta",
  "type": "interactive",
  "subject": "calculus_1",
  "title_en": "Limits \u2014 The \u03b5-\u03b4 Definition",
  "title_he": "\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u2014 \u05d4\u05d2\u05d3\u05e8\u05ea \u05d0\u05e4\u05e1\u05d9\u05dc\u05d5\u05df-\u05d3\u05dc\u05ea\u05d0",
  "duration_min": 30,
  "level_min": "calculus_1",
  "agent_hints": "Students at Technion 104031 must write complete \u03b5-\u03b4 proofs \u2014 not just understand intuitively. The core skill: given \u03b5 > 0, construct \u03b4(\u03b5) explicitly, then verify |x-a|<\u03b4 \u21d2 |f(x)-L|<\u03b5 forwards. Common errors: assuming \u03b4=\u03b5 always works; omitting the bounding step (restrict \u03b4 \u2264 1 to bound a product factor); writing steps in the wrong order. Always have students state the goal |f(x)-L|<\u03b5 before working backwards to find \u03b4.",
  "sections": [
    {
      "id": "intuitive_review",
      "title_en": "Intuitive Limits Review",
      "title_he": "\u05d7\u05d6\u05e8\u05d4 \u05d0\u05d9\u05e0\u05d8\u05d5\u05d0\u05d9\u05d8\u05d9\u05d1\u05d9\u05ea \u05e2\u05dc \u05d2\u05d1\u05d5\u05dc\u05d5\u05ea",
      "level_min": "calculus_1",
      "body_en_md": "We write $\\lim_{x \\to a} f(x) = L$ to mean: as $x$ approaches $a$ (with $x \\neq a$), the output $f(x)$ gets arbitrarily close to $L$.\n\nThis is intuitive \u2014 it says nothing about *how close* $x$ must be to $a$ to guarantee a given closeness of $f(x)$ to $L$. The \u03b5-\u03b4 definition quantifies exactly this.\n\n**Examples:**\n- $\\lim_{x \\to 2}(3x-1) = 5$: as $x \\to 2$, $3x-1 \\to 5$. \u2713 (can be proved rigorously)\n- $\\lim_{x \\to 0}\\dfrac{\\sin x}{x} = 1$: not obvious algebraically \u2014 requires careful work.\n- $\\lim_{x \\to 0}\\sin(1/x)$: **does not exist** \u2014 the function oscillates between \u22121 and 1 infinitely often near 0.\n\nThe formal definition will let us prove the first, establish the second, and disprove the third with mathematical certainty.",
      "body_he_md": "\u05db\u05d5\u05ea\u05d1\u05d9\u05dd $\\lim_{x \\to a} f(x) = L$ \u05db\u05d3\u05d9 \u05dc\u05d5\u05de\u05e8: \u05db\u05d0\u05e9\u05e8 $x$ \u05de\u05ea\u05e7\u05e8\u05d1 \u05dc-$a$ (\u05e2\u05dd $x \\neq a$), \u05d4\u05e4\u05dc\u05d8 $f(x)$ \u05de\u05ea\u05e7\u05e8\u05d1 \u05dc-$L$ \u05d1\u05e6\u05d5\u05e8\u05d4 \u05e9\u05e8\u05d9\u05e8\u05d5\u05ea\u05d9\u05ea.\n\n\u05d6\u05d5 \u05d0\u05de\u05d9\u05e8\u05d4 \u05d0\u05d9\u05e0\u05d8\u05d5\u05d0\u05d9\u05d8\u05d9\u05d1\u05d9\u05ea \u2014 \u05d4\u05d9\u05d0 \u05d0\u05d9\u05e0\u05d4 \u05de\u05e4\u05e8\u05d8\u05ea *\u05db\u05de\u05d4* \u05e7\u05e8\u05d5\u05d1 $x$ \u05d7\u05d9\u05d9\u05d1 \u05dc\u05d4\u05d9\u05d5\u05ea \u05dc-$a$ \u05db\u05d3\u05d9 \u05dc\u05d4\u05d1\u05d8\u05d9\u05d7 \u05e7\u05e8\u05d1\u05d5\u05ea \u05e0\u05ea\u05d5\u05e0\u05d4 \u05e9\u05dc $f(x)$ \u05dc-$L$. \u05d4\u05d2\u05d3\u05e8\u05ea \u03b5-\u03b4 \u05de\u05db\u05de\u05ea\u05ea \u05d1\u05d3\u05d9\u05d5\u05e7 \u05d0\u05ea \u05d6\u05d4.\n\n**\u05d3\u05d5\u05d2\u05de\u05d0\u05d5\u05ea:**\n- $\\lim_{x \\to 2}(3x-1) = 5$: \u05db\u05d0\u05e9\u05e8 $x \\to 2$, $3x-1 \\to 5$. \u2713\n- $\\lim_{x \\to 0}\\dfrac{\\sin x}{x} = 1$: \u05dc\u05d0 \u05de\u05d5\u05d1\u05df \u05de\u05d0\u05dc\u05d9\u05d5 \u05d0\u05dc\u05d2\u05d1\u05e8\u05d0\u05d9\u05ea \u2014 \u05d3\u05d5\u05e8\u05e9 \u05e2\u05d1\u05d5\u05d3\u05d4 \u05e7\u05e4\u05d3\u05e0\u05d9\u05ea.\n- $\\lim_{x \\to 0}\\sin(1/x)$: **\u05d0\u05d9\u05e0\u05d5 \u05e7\u05d9\u05d9\u05dd** \u2014 \u05d4\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05de\u05ea\u05e0\u05d3\u05e0\u05d3\u05ea \u05d1\u05d9\u05df \u22121 \u05dc-1 \u05d0\u05d9\u05e0\u05e1\u05d5\u05e3 \u05e4\u05e2\u05de\u05d9\u05dd \u05dc\u05d9\u05d3 0.\n\n\u05d4\u05d4\u05d2\u05d3\u05e8\u05d4 \u05d4\u05e4\u05d5\u05e8\u05de\u05dc\u05d9\u05ea \u05ea\u05d0\u05e4\u05e9\u05e8 \u05dc\u05e0\u05d5 \u05dc\u05d4\u05d5\u05db\u05d9\u05d7 \u05d0\u05ea \u05d4\u05e8\u05d0\u05e9\u05d5\u05df, \u05dc\u05d1\u05e1\u05e1 \u05d0\u05ea \u05d4\u05e9\u05e0\u05d9, \u05d5\u05dc\u05e1\u05ea\u05d5\u05e8 \u05d0\u05ea \u05d4\u05e9\u05dc\u05d9\u05e9\u05d9 \u05d1\u05d5\u05d3\u05d0\u05d5\u05ea \u05de\u05ea\u05de\u05d8\u05d9\u05ea."
    },
    {
      "id": "epsilon_delta_definition",
      "title_en": "The Formal \u03b5-\u03b4 Definition",
      "title_he": "\u05d4\u05d4\u05d2\u05d3\u05e8\u05d4 \u05d4\u05e4\u05d5\u05e8\u05de\u05dc\u05d9\u05ea \u03b5-\u03b4",
      "level_min": "calculus_1",
      "body_en_md": "**Definition.** $\\lim_{x \\to a} f(x) = L$ means:\n$$\\forall\\,\\epsilon > 0,\\quad\\exists\\,\\delta > 0 \\quad\\text{such that}\\quad 0 < |x - a| < \\delta \\;\\Rightarrow\\; |f(x) - L| < \\epsilon.$$\n\n**Reading it aloud:** \u201cFor every challenge $\\epsilon > 0$ (no matter how small), we can produce a response $\\delta > 0$ such that whenever $x$ is within $\\delta$ of $a$ (but $x \\neq a$), $f(x)$ is within $\\epsilon$ of $L$.\u201d\n\n**Key points:**\n1. $\\delta$ may depend on $\\epsilon$, on $a$, on $f$, and on $L$ \u2014 and usually must.\n2. The condition $0 < |x-a|$ (strict inequality on the left) excludes $x = a$ itself.\n3. The definition must hold for **all** $\\epsilon > 0$, however small.\n\n**Negation** (to disprove a limit): $\\lim_{x \\to a}f(x) \\neq L$ iff $\\exists\\,\\epsilon_0 > 0$ such that for every $\\delta > 0$, there exists $x$ with $0 < |x-a| < \\delta$ yet $|f(x) - L| \\geq \\epsilon_0$.",
      "body_he_md": "**\u05d4\u05d2\u05d3\u05e8\u05d4.** $\\lim_{x \\to a} f(x) = L$ \u05e4\u05d9\u05e8\u05d5\u05e9\u05d5:\n$$\\forall\\,\\epsilon > 0,\\quad\\exists\\,\\delta > 0 \\quad\\text{\u05db\u05da \u05e9-}\\quad 0 < |x - a| < \\delta \\;\\Rightarrow\\; |f(x) - L| < \\epsilon.$$\n\n**\u05e7\u05e8\u05d9\u05d0\u05d4 \u05d1\u05e7\u05d5\u05dc:** \u201c\u05dc\u05db\u05dc \u05d0\u05ea\u05d2\u05e8 $\\epsilon > 0$ (\u05dc\u05d0 \u05de\u05e9\u05e0\u05d4 \u05db\u05de\u05d4 \u05e7\u05d8\u05df), \u05e0\u05d9\u05ea\u05df \u05dc\u05de\u05e6\u05d5\u05d0 \u05ea\u05d2\u05d5\u05d1\u05d4 $\\delta > 0$ \u05db\u05da \u05e9\u05d1\u05db\u05dc \u05e4\u05e2\u05dd \u05e9-$x$ \u05e0\u05de\u05e6\u05d0 \u05d1\u05ea\u05d5\u05da $\\delta$ \u05de-$a$ (\u05d0\u05da $x \\neq a$), $f(x)$ \u05e0\u05de\u05e6\u05d0 \u05d1\u05ea\u05d5\u05da $\\epsilon$ \u05de-$L$.\u201d\n\n**\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea \u05de\u05e8\u05db\u05d6\u05d9\u05d5\u05ea:**\n1. $\\delta$ \u05e2\u05e9\u05d5\u05d9 \u05dc\u05ea\u05dc\u05d5\u05ea \u05d1-$\\epsilon$, \u05d1-$a$, \u05d1-$f$ \u05d5\u05d1-$L$ \u2014 \u05d5\u05d1\u05d3\u05e8\u05da \u05db\u05dc\u05dc \u05d7\u05d9\u05d9\u05d1.\n2. \u05d4\u05ea\u05e0\u05d0\u05d9 $0 < |x-a|$ (\u05d0\u05d9-\u05e9\u05d5\u05d5\u05d9\u05d5\u05df \u05d7\u05d6\u05e7) \u05e9\u05d5\u05dc\u05dc $x = a$ \u05e2\u05e6\u05de\u05d4.\n3. \u05d4\u05d4\u05d2\u05d3\u05e8\u05d4 \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d4\u05ea\u05e7\u05d9\u05d9\u05dd \u05dc\u05db\u05dc $\\epsilon > 0$, \u05d9\u05d4\u05d9\u05d4 \u05e7\u05d8\u05df \u05db\u05d0\u05e9\u05e8 \u05d9\u05d4\u05d9\u05d4.\n\n**\u05e9\u05dc\u05d9\u05dc\u05d4** (\u05dc\u05e1\u05ea\u05d5\u05e8 \u05d2\u05d1\u05d5\u05dc): $\\lim_{x \\to a}f(x) \\neq L$ \u05d0\u05de\"\u05dd $\\exists\\,\\epsilon_0 > 0$ \u05db\u05da \u05e9\u05dc\u05db\u05dc $\\delta > 0$, \u05e7\u05d9\u05d9\u05dd $x$ \u05e2\u05dd $0 < |x-a| < \\delta$ \u05d0\u05da $|f(x) - L| \\geq \\epsilon_0$."
    },
    {
      "id": "proof_template_linear",
      "title_en": "Proof Template \u2014 Linear Functions",
      "title_he": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05d4\u05d5\u05db\u05d7\u05d4 \u2014 \u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05d5\u05ea",
      "level_min": "calculus_1",
      "body_en_md": "## The Four-Step Template\n\n1. **State the goal:** write $|f(x) - L| < \\epsilon$.\n2. **Simplify:** express $|f(x) - L|$ algebraically in terms of $|x - a|$.\n3. **Choose $\\delta$:** set $\\delta$ as an explicit function of $\\epsilon$.\n4. **Verify:** assume $0 < |x - a| < \\delta$ and derive $|f(x) - L| < \\epsilon$.\n\n---\n\n**Worked Example 1.** Prove $\\lim_{x \\to 2}(3x - 1) = 5$.\n\n*Scratch work (step 2):*\n$$|(3x-1) - 5| = |3x - 6| = 3|x - 2|.$$\nWe need $3|x-2| < \\epsilon$, i.e., $|x-2| < \\epsilon/3$. Choose $\\delta = \\epsilon/3$.\n\n*Formal proof:*\n> **Given** $\\epsilon > 0$. **Let** $\\delta = \\dfrac{\\epsilon}{3}$. **Suppose** $0 < |x-2| < \\delta$. **Then:**\n> $$|(3x-1) - 5| = 3|x - 2| < 3\\delta = 3 \\cdot \\frac{\\epsilon}{3} = \\epsilon. \\quad\\square$$\n\n**General rule for $f(x) = mx + b$:** $|f(x) - L| = |m|\\,|x-a|$, so $\\delta = \\epsilon/|m|$ (provided $m \\neq 0$).",
      "body_he_md": "## \u05ea\u05d1\u05e0\u05d9\u05ea \u05d0\u05e8\u05d1\u05e2\u05ea \u05d4\u05e9\u05dc\u05d1\u05d9\u05dd\n\n1. **\u05d4\u05e6\u05d4\u05e8 \u05e2\u05dc \u05d4\u05de\u05d8\u05e8\u05d4:** \u05db\u05ea\u05d5\u05d1 $|f(x) - L| < \\epsilon$.\n2. **\u05e4\u05e9\u05d8:** \u05d4\u05d1\u05e2 \u05d0\u05ea $|f(x) - L|$ \u05d0\u05dc\u05d2\u05d1\u05e8\u05d0\u05d9\u05ea \u05d1\u05de\u05d5\u05e0\u05d7\u05d9 $|x - a|$.\n3. **\u05d1\u05d7\u05e8 $\\delta$:** \u05d4\u05d2\u05d3\u05e8 $\\delta$ \u05db\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05de\u05e4\u05d5\u05e8\u05e9\u05ea \u05e9\u05dc $\\epsilon$.\n4. **\u05d0\u05de\u05ea:** \u05d4\u05e0\u05d7 $0 < |x - a| < \\delta$ \u05d5\u05d4\u05e1\u05e7 $|f(x) - L| < \\epsilon$.\n\n---\n\n**\u05d3\u05d5\u05d2\u05de\u05d4 \u05de\u05dc\u05d0\u05d4 1.** \u05d4\u05d5\u05db\u05d7 \u05e9-$\\lim_{x \\to 2}(3x - 1) = 5$.\n\n*\u05e2\u05d1\u05d5\u05d3\u05ea \u05e9\u05e8\u05d1\u05d5\u05d8 (\u05e9\u05dc\u05d1 2):*\n$$|(3x-1) - 5| = |3x - 6| = 3|x - 2|.$$\n\u05e6\u05e8\u05d9\u05db\u05d9\u05dd $3|x-2| < \\epsilon$, \u05db\u05dc\u05d5\u05de\u05e8 $|x-2| < \\epsilon/3$. \u05d1\u05d5\u05d7\u05e8\u05d9\u05dd $\\delta = \\epsilon/3$.\n\n*\u05d4\u05d5\u05db\u05d7\u05d4 \u05e4\u05d5\u05e8\u05de\u05dc\u05d9\u05ea:*\n> **\u05e0\u05ea\u05d5\u05df** $\\epsilon > 0$. **\u05e0\u05d2\u05d3\u05d9\u05e8** $\\delta = \\dfrac{\\epsilon}{3}$. **\u05e0\u05e0\u05d9\u05d7** $0 < |x-2| < \\delta$. **\u05d0\u05d6:**\n> $$|(3x-1) - 5| = 3|x - 2| < 3\\delta = 3 \\cdot \\frac{\\epsilon}{3} = \\epsilon. \\quad\\square$$\n\n**\u05db\u05dc\u05dc \u05db\u05dc\u05dc\u05d9 \u05dc-$f(x) = mx + b$:** $|f(x) - L| = |m|\\,|x-a|$, \u05dc\u05db\u05df $\\delta = \\epsilon/|m|$ (\u05d1\u05ea\u05e0\u05d0\u05d9 $m \\neq 0$)."
    },
    {
      "id": "quadratic_proof_bounding",
      "title_en": "Proofs with Quadratics \u2014 The Bounding Trick",
      "title_he": "\u05d4\u05d5\u05db\u05d7\u05d5\u05ea \u05e2\u05dd \u05e8\u05d9\u05d1\u05d5\u05e2\u05d9\u05d5\u05ea \u2014 \u05d8\u05e8\u05d9\u05e7 \u05d4\u05d7\u05e1\u05d9\u05de\u05d4",
      "level_min": "calculus_1",
      "body_en_md": "**Worked Example 2.** Prove $\\lim_{x \\to 1} x^2 = 1$.\n\n*Scratch work:*\n$$|x^2 - 1| = |x-1|\\,|x+1|.$$\nThe factor $|x-1|$ is controlled by $\\delta$, but $|x+1|$ also depends on $x$ and must be bounded separately.\n\n**Bounding trick:** Impose $\\delta \\leq 1$ upfront. If $|x-1| < 1$, then $0 < x < 2$, so $1 < x+1 < 3$, giving $|x+1| < 3$.\n\nTherefore: $|x^2 - 1| < 3|x-1| < 3\\delta$.\n\nWe need $3\\delta \\leq \\epsilon$, i.e., $\\delta \\leq \\epsilon/3$. Combined with $\\delta \\leq 1$:\n$$\\boxed{\\delta = \\min\\!\\left(1,\\ \\frac{\\epsilon}{3}\\right).}$$\n\n*Formal proof:*\n> **Given** $\\epsilon > 0$. **Let** $\\delta = \\min(1, \\epsilon/3)$. **Suppose** $0 < |x-1| < \\delta$.\n> Since $\\delta \\leq 1$: $|x-1| < 1 \\Rightarrow |x+1| < 3$.\n> Therefore: $|x^2 - 1| = |x-1|\\,|x+1| < 3|x-1| < 3\\delta \\leq \\epsilon$. $\\square$\n\n**General principle:** For a product $|g(x)| \\cdot |x-a|$, restrict $\\delta \\leq 1$ to bound $|g(x)| \\leq M$, then choose $\\delta = \\min(1, \\epsilon/M)$.",
      "body_he_md": "**\u05d3\u05d5\u05d2\u05de\u05d4 \u05de\u05dc\u05d0\u05d4 2.** \u05d4\u05d5\u05db\u05d7 \u05e9-$\\lim_{x \\to 1} x^2 = 1$.\n\n*\u05e2\u05d1\u05d5\u05d3\u05ea \u05e9\u05e8\u05d1\u05d5\u05d8:*\n$$|x^2 - 1| = |x-1|\\,|x+1|.$$\n\u05d4\u05d2\u05d5\u05e8\u05dd $|x-1|$ \u05e0\u05e9\u05dc\u05d8 \u05e2\u05dc \u05d9\u05d3\u05d9 $\\delta$, \u05d0\u05da $|x+1|$ \u05ea\u05dc\u05d5\u05d9 \u05d2\u05dd \u05d1-$x$ \u05d5\u05d1\u05d9\u05e9 \u05dc\u05d7\u05e1\u05d5\u05dd \u05d1\u05e0\u05e4\u05e8\u05d3.\n\n**\u05d8\u05e8\u05d9\u05e7 \u05d4\u05d7\u05e1\u05d9\u05de\u05d4:** \u05de\u05d5\u05e1\u05d9\u05e4\u05d9\u05dd \u05d0\u05ea \u05d4\u05d2\u05d1\u05dc\u05d4 $\\delta \\leq 1$ \u05de\u05dc\u05db\u05ea\u05d7\u05d9\u05dc\u05d4. \u05d0\u05dd $|x-1| < 1$, \u05d0\u05d6 $0 < x < 2$, \u05dc\u05db\u05df $1 < x+1 < 3$, \u05d5\u05de\u05db\u05d0\u05df $|x+1| < 3$.\n\n\u05dc\u05db\u05df: $|x^2 - 1| < 3|x-1| < 3\\delta$.\n\n\u05e6\u05e8\u05d9\u05db\u05d9\u05dd $3\\delta \\leq \\epsilon$, \u05db\u05dc\u05d5\u05de\u05e8 $\\delta \\leq \\epsilon/3$. \u05d1\u05e9\u05d9\u05dc\u05d5\u05d1 \u05e2\u05dd $\\delta \\leq 1$:\n$$\\boxed{\\delta = \\min\\!\\left(1,\\ \\frac{\\epsilon}{3}\\right).}$$\n\n*\u05d4\u05d5\u05db\u05d7\u05d4 \u05e4\u05d5\u05e8\u05de\u05dc\u05d9\u05ea:*\n> **\u05e0\u05ea\u05d5\u05df** $\\epsilon > 0$. **\u05e0\u05d2\u05d3\u05d9\u05e8** $\\delta = \\min(1, \\epsilon/3)$. **\u05e0\u05e0\u05d9\u05d7** $0 < |x-1| < \\delta$.\n> \u05de\u05db\u05d9\u05d5\u05d5\u05df \u05e9-$\\delta \\leq 1$: $|x-1| < 1 \\Rightarrow |x+1| < 3$.\n> \u05dc\u05db\u05df: $|x^2 - 1| = |x-1|\\,|x+1| < 3|x-1| < 3\\delta \\leq \\epsilon$. $\\square$\n\n**\u05e2\u05e7\u05e8\u05d5\u05df \u05db\u05dc\u05dc\u05d9:** \u05e2\u05d1\u05d5\u05e8 \u05de\u05db\u05e4\u05dc\u05d4 $|g(x)| \\cdot |x-a|$, \u05de\u05d2\u05d1\u05d9\u05dc\u05d9\u05dd $\\delta \\leq 1$ \u05dc\u05d7\u05e1\u05d9\u05de\u05ea $|g(x)| \\leq M$, \u05d5\u05d0\u05d6 \u05d1\u05d5\u05d7\u05e8\u05d9\u05dd $\\delta = \\min(1, \\epsilon/M)$."
    },
    {
      "id": "onesided_infinite",
      "title_en": "One-Sided and Infinite Limits",
      "title_he": "\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d7\u05d3-\u05e6\u05d3\u05d3\u05d9\u05d9\u05dd \u05d5\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d0\u05d9\u05e0\u05e1\u05d5\u05e4\u05d9\u05d9\u05dd",
      "level_min": "calculus_1",
      "body_en_md": "### One-Sided Limits\n\n**Right-hand limit** $\\lim_{x \\to a^+} f(x) = L$:\n$$\\forall\\,\\epsilon>0,\\;\\exists\\,\\delta>0:\\quad 0 < x - a < \\delta \\;\\Rightarrow\\; |f(x)-L|<\\epsilon.$$\n**Left-hand limit:** replace $0 < x-a$ with $0 < a-x$.\n\nThe two-sided limit exists iff both one-sided limits exist and are equal.\n\n### Limits at Infinity and Infinite Limits\n\n**$f(x) \\to L$ as $x \\to \\infty$:** $\\;\\forall\\,\\epsilon>0,\\;\\exists\\,N>0: x>N\\Rightarrow|f(x)-L|<\\epsilon$.\n\n**$f(x) \\to \\infty$ as $x \\to a$:** $\\;\\forall\\,M>0,\\;\\exists\\,\\delta>0: 0<|x-a|<\\delta\\Rightarrow f(x)>M$.\n\n**Example.** $\\lim_{x\\to\\infty}\\dfrac{1}{x}=0$. Given $\\epsilon>0$, let $N=\\dfrac{1}{\\epsilon}$. Then $x>N \\Rightarrow \\dfrac{1}{x}<\\dfrac{1}{N}=\\epsilon$. $\\checkmark$",
      "body_he_md": "### \u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d7\u05d3-\u05e6\u05d3\u05d3\u05d9\u05d9\u05dd\n\n**\u05d2\u05d1\u05d5\u05dc \u05de\u05d4\u05e6\u05d3 \u05d4\u05d9\u05de\u05e0\u05d9** $\\lim_{x \\to a^+} f(x) = L$:\n$$\\forall\\,\\epsilon>0,\\;\\exists\\,\\delta>0:\\quad 0 < x - a < \\delta \\;\\Rightarrow\\; |f(x)-L|<\\epsilon.$$\n**\u05d2\u05d1\u05d5\u05dc \u05de\u05d4\u05e6\u05d3 \u05d4\u05e9\u05de\u05d0\u05dc\u05d9:** \u05de\u05d7\u05dc\u05d9\u05e4\u05d9\u05dd $0 < x-a$ \u05d1-$0 < a-x$.\n\n\u05d4\u05d2\u05d1\u05d5\u05dc \u05d4\u05d3\u05d5-\u05e6\u05d3\u05d3\u05d9 \u05e7\u05d9\u05d9\u05dd \u05d0\u05de\"\u05dd \u05e9\u05e0\u05d9 \u05d4\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d4\u05d7\u05d3-\u05e6\u05d3\u05d3\u05d9\u05d9\u05dd \u05e7\u05d9\u05d9\u05de\u05d9\u05dd \u05d5\u05e9\u05d5\u05d5\u05d9\u05dd.\n\n### \u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d1\u05d0\u05d9\u05e0\u05e1\u05d5\u05e3 \u05d5\u05d2\u05d1\u05d5\u05dc\u05d5\u05ea \u05d0\u05d9\u05e0\u05e1\u05d5\u05e4\u05d9\u05d9\u05dd\n\n**$f(x) \\to L$ \u05db\u05d0\u05e9\u05e8 $x \\to \\infty$:** $\\;\\forall\\,\\epsilon>0,\\;\\exists\\,N>0: x>N\\Rightarrow|f(x)-L|<\\epsilon$.\n\n**$f(x) \\to \\infty$ \u05db\u05d0\u05e9\u05e8 $x \\to a$:** $\\;\\forall\\,M>0,\\;\\exists\\,\\delta>0: 0<|x-a|<\\delta\\Rightarrow f(x)>M$.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4.** $\\lim_{x\\to\\infty}\\dfrac{1}{x}=0$. \u05e0\u05ea\u05d5\u05df $\\epsilon>0$, \u05e0\u05d2\u05d3\u05d9\u05e8 $N=\\dfrac{1}{\\epsilon}$. \u05d0\u05d6 $x>N \\Rightarrow \\dfrac{1}{x}<\\dfrac{1}{N}=\\epsilon$. $\\checkmark$"
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "To prove $\\lim_{x \\to 3}(2x - 1) = 5$ using the \u03b5-\u03b4 definition, which $\\delta$ should be chosen?",
      "body_he": "\u05dc\u05d4\u05d5\u05db\u05d7\u05ea $\\lim_{x \\to 3}(2x - 1) = 5$ \u05d1\u05e9\u05d9\u05d8\u05ea \u03b5-\u03b4, \u05d0\u05d9\u05d6\u05d4 $\\delta$ \u05e6\u05e8\u05d9\u05da \u05dc\u05d1\u05d7\u05d5\u05e8?",
      "options": [
        {"id": "a", "text_en": "$\\delta = \\epsilon$", "text_he": "$\\delta = \\epsilon$", "correct": False},
        {"id": "b", "text_en": "$\\delta = \\epsilon / 2$", "text_he": "$\\delta = \\epsilon / 2$", "correct": True},
        {"id": "c", "text_en": "$\\delta = 2\\epsilon$", "text_he": "$\\delta = 2\\epsilon$", "correct": False},
        {"id": "d", "text_en": "$\\delta = \\epsilon / 3$", "text_he": "$\\delta = \\epsilon / 3$", "correct": False}
      ],
      "explanation_en": "$|(2x-1)-5| = |2x-6| = 2|x-3|$. We need $2|x-3| < \\epsilon$, i.e., $|x-3| < \\epsilon/2$. So $\\delta = \\epsilon/2$.",
      "explanation_he": "$|(2x-1)-5| = |2x-6| = 2|x-3|$. \u05e6\u05e8\u05d9\u05db\u05d9\u05dd $2|x-3| < \\epsilon$, \u05db\u05dc\u05d5\u05de\u05e8 $|x-3| < \\epsilon/2$. \u05dc\u05db\u05df $\\delta = \\epsilon/2$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A student proves $\\lim_{x \\to 2}(3x-1)=5$ and writes $|3x-1-5| = |x-2| < \\delta = \\epsilon/3 < \\epsilon$. What is the error?",
      "body_he": "\u05ea\u05dc\u05de\u05d9\u05d3 \u05de\u05d5\u05db\u05d9\u05d7 $\\lim_{x \\to 2}(3x-1)=5$ \u05d5\u05db\u05d5\u05ea\u05d1 $|3x-1-5| = |x-2| < \\delta = \\epsilon/3 < \\epsilon$. \u05de\u05d4 \u05d4\u05e9\u05d2\u05d9\u05d0\u05d4?",
      "options": [
        {"id": "a", "text_en": "The choice $\\delta = \\epsilon/3$ is wrong; it should be $\\delta = \\epsilon$", "text_he": "\u05d4\u05d1\u05d7\u05d9\u05e8\u05d4 $\\delta = \\epsilon/3$ \u05e9\u05d2\u05d5\u05d9\u05d4; \u05e6\u05e8\u05d9\u05da $\\delta = \\epsilon$", "correct": False},
        {"id": "b", "text_en": "$|3x-1-5| = 3|x-2|$, not $|x-2|$ \u2014 the factor of 3 was dropped", "text_he": "$|3x-1-5| = 3|x-2|$, \u05dc\u05d0 $|x-2|$ \u2014 \u05e4\u05e7\u05d8\u05d5\u05e8 3 \u05d4\u05d5\u05d8\u05dc", "correct": True},
        {"id": "c", "text_en": "The proof must begin by assuming $\\epsilon < 1$", "text_he": "\u05d4\u05d4\u05d5\u05db\u05d7\u05d4 \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d4\u05ea\u05d7\u05d9\u05dc \u05d1\u05d4\u05e0\u05d7\u05d4 \u05e9-$\\epsilon < 1$", "correct": False},
        {"id": "d", "text_en": "There is no error; the proof is valid", "text_he": "\u05d0\u05d9\u05df \u05e9\u05d2\u05d9\u05d0\u05d4; \u05d4\u05d4\u05d5\u05db\u05d7\u05d4 \u05ea\u05e7\u05e4\u05d4", "correct": False}
      ],
      "explanation_en": "The correct simplification is $|3x-6| = 3|x-2|$, not $|x-2|$. With the correct factor: $3|x-2| < 3\\delta = \\epsilon$. The choice $\\delta = \\epsilon/3$ is correct \u2014 only the simplification step has the error.",
      "explanation_he": "\u05d4\u05e4\u05d9\u05e9\u05d5\u05d8 \u05d4\u05e0\u05db\u05d5\u05df \u05d4\u05d5\u05d0 $|3x-6| = 3|x-2|$, \u05dc\u05d0 $|x-2|$. \u05e2\u05dd \u05d4\u05e4\u05e7\u05d8\u05d5\u05e8 \u05d4\u05e0\u05db\u05d5\u05df: $3|x-2| < 3\\delta = \\epsilon$. \u05d1\u05d7\u05d9\u05e8\u05ea $\\delta = \\epsilon/3$ \u05e0\u05db\u05d5\u05e0\u05d4 \u2014 \u05e8\u05e7 \u05e9\u05dc\u05d1 \u05d4\u05e4\u05d9\u05e9\u05d5\u05d8 \u05de\u05db\u05d9\u05dc \u05e9\u05d2\u05d9\u05d0\u05d4."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "In the proof of $\\lim_{x \\to 1} x^2 = 1$, we restrict $\\delta \\leq 1$. With $|x-1| < 1$, what bound do we get on $|x+1|$?",
      "body_he": "\u05d1\u05d4\u05d5\u05db\u05d7\u05ea $\\lim_{x \\to 1} x^2 = 1$, \u05de\u05d2\u05d1\u05d9\u05dc\u05d9\u05dd $\\delta \\leq 1$. \u05db\u05d0\u05e9\u05e8 $|x-1| < 1$, \u05d0\u05d9\u05d6\u05d4 \u05d7\u05e1\u05dd \u05de\u05ea\u05e7\u05d1\u05dc \u05e2\u05dc $|x+1|$?",
      "options": [
        {"id": "a", "text_en": "$|x+1| < 1$", "text_he": "$|x+1| < 1$", "correct": False},
        {"id": "b", "text_en": "$|x+1| < 2$", "text_he": "$|x+1| < 2$", "correct": False},
        {"id": "c", "text_en": "$|x+1| < 3$", "text_he": "$|x+1| < 3$", "correct": True},
        {"id": "d", "text_en": "$|x+1| < 4$", "text_he": "$|x+1| < 4$", "correct": False}
      ],
      "explanation_en": "If $|x-1|<1$ then $0<x<2$, so $1<x+1<3$, giving $|x+1|<3$. This yields $|x^2-1|=|x-1||x+1|<3|x-1|$; choosing $\\delta=\\min(1,\\epsilon/3)$ completes the proof.",
      "explanation_he": "\u05d0\u05dd $|x-1|<1$ \u05d0\u05d6 $0<x<2$, \u05dc\u05db\u05df $1<x+1<3$, \u05d5\u05de\u05db\u05d0\u05df $|x+1|<3$. \u05d6\u05d4 \u05e0\u05d5\u05ea\u05df $|x^2-1|=|x-1||x+1|<3|x-1|$; \u05d1\u05d7\u05d9\u05e8\u05ea $\\delta=\\min(1,\\epsilon/3)$ \u05de\u05e9\u05dc\u05d9\u05de\u05d4 \u05d0\u05ea \u05d4\u05d4\u05d5\u05db\u05d7\u05d4."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "Why does $\\delta$ generally depend on $\\epsilon$ and cannot be a fixed universal constant?",
      "body_he": "\u05de\u05d3\u05d5\u05e2 $\\delta$ \u05ea\u05dc\u05d5\u05d9 \u05d1\u05d3\u05e8\u05da \u05db\u05dc\u05dc \u05d1-$\\epsilon$ \u05d5\u05dc\u05d0 \u05d9\u05db\u05d5\u05dc \u05dc\u05d4\u05d9\u05d5\u05ea \u05e7\u05d1\u05d5\u05e2 \u05d0\u05d5\u05e0\u05d9\u05d1\u05e8\u05e1\u05dc\u05d9?",
      "options": [
        {"id": "a", "text_en": "Because $\\delta$ must always equal $\\epsilon$ by definition", "text_he": "\u05db\u05d9 $\\delta$ \u05d7\u05d9\u05d9\u05d1 \u05ea\u05de\u05d9\u05d3 \u05dc\u05d4\u05d9\u05d5\u05ea \u05e9\u05d5\u05d5\u05d4 \u05dc-$\\epsilon$ \u05dc\u05e4\u05d9 \u05d4\u05d4\u05d2\u05d3\u05e8\u05d4", "correct": False},
        {"id": "b", "text_en": "Different functions change at different rates near $a$, requiring different $\\delta$ values to guarantee $|f(x)-L|<\\epsilon$", "text_he": "\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d5\u05ea \u05e9\u05d5\u05e0\u05d5\u05ea \u05de\u05e9\u05ea\u05e0\u05d5\u05ea \u05d1\u05e7\u05e6\u05d1\u05d9\u05dd \u05e9\u05d5\u05e0\u05d9\u05dd \u05dc\u05d9\u05d3 $a$, \u05d5\u05dc\u05db\u05df \u05d3\u05e8\u05d5\u05e9\u05d9\u05dd \u05e2\u05e8\u05db\u05d9 $\\delta$ \u05e9\u05d5\u05e0\u05d9\u05dd \u05dc\u05d4\u05d1\u05d8\u05d7\u05ea $|f(x)-L|<\\epsilon$", "correct": True},
        {"id": "c", "text_en": "Because the domain of $f$ is always bounded", "text_he": "\u05db\u05d9 \u05ea\u05d7\u05d5\u05dd $f$ \u05ea\u05de\u05d9\u05d3 \u05d7\u05e1\u05d5\u05dd", "correct": False},
        {"id": "d", "text_en": "Because $\\epsilon$ is always irrational", "text_he": "\u05db\u05d9 $\\epsilon$ \u05ea\u05de\u05d9\u05d3 \u05d0\u05d9-\u05e8\u05e6\u05d9\u05d5\u05e0\u05dc\u05d9", "correct": False}
      ],
      "explanation_en": "The definition requires: for *every* $\\epsilon > 0$, produce $\\delta > 0$ that works. A steeply-changing function (large $|f'(a)|$) requires a much smaller $\\delta$ than a nearly flat function for the same $\\epsilon$.",
      "explanation_he": "\u05d4\u05d4\u05d2\u05d3\u05e8\u05d4 \u05d3\u05d5\u05e8\u05e9\u05ea: \u05dc*\u05db\u05dc* $\\epsilon > 0$, \u05e6\u05e8\u05d9\u05da \u05dc\u05d4\u05de\u05e6\u05d9\u05d0 $\\delta > 0$ \u05e9\u05e2\u05d5\u05d1\u05d3. \u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05e9\u05de\u05e9\u05ea\u05e0\u05d4 \u05d1\u05d7\u05d3\u05d5\u05ea (ערך $|f'(a)|$ \u05d2\u05d3\u05d5\u05dc) \u05d3\u05d5\u05e8\u05e9\u05ea $\\delta$ \u05e7\u05d8\u05df \u05d1\u05d4\u05e8\u05d1\u05d4 \u05de\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4 \u05db\u05de\u05e2\u05d8 \u05e9\u05d8\u05d5\u05d7\u05d4 \u05e2\u05d1\u05d5\u05e8 \u05d0\u05d5\u05ea\u05d5 $\\epsilon$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "To prove $\\lim_{x \\to 0}(x^2 + x) = 0$, restricting $\\delta \\leq 1$ gives $|x^2 + x| < 2|x|$. A valid choice of $\\delta$ is:",
      "body_he": "\u05dc\u05d4\u05d5\u05db\u05d7\u05ea $\\lim_{x \\to 0}(x^2 + x) = 0$, \u05d4\u05d2\u05d1\u05dc\u05d4 $\\delta \\leq 1$ \u05e0\u05d5\u05ea\u05e0\u05ea $|x^2 + x| < 2|x|$. \u05d1\u05d7\u05d9\u05e8\u05d4 \u05ea\u05e7\u05e4\u05d4 \u05e9\u05dc $\\delta$ \u05d4\u05d9\u05d0:",
      "options": [
        {"id": "a", "text_en": "$\\delta = \\min(1, \\epsilon)$", "text_he": "$\\delta = \\min(1, \\epsilon)$", "correct": False},
        {"id": "b", "text_en": "$\\delta = \\min(1, \\epsilon/2)$", "text_he": "$\\delta = \\min(1, \\epsilon/2)$", "correct": True},
        {"id": "c", "text_en": "$\\delta = \\epsilon^2$", "text_he": "$\\delta = \\epsilon^2$", "correct": False},
        {"id": "d", "text_en": "$\\delta = \\min(1, 2\\epsilon)$", "text_he": "$\\delta = \\min(1, 2\\epsilon)$", "correct": False}
      ],
      "explanation_en": "With $|x|<\\delta\\leq 1$: $|x^2+x|<2|x|<2\\delta$. We need $2\\delta\\leq\\epsilon$, so $\\delta\\leq\\epsilon/2$. Thus $\\delta=\\min(1,\\epsilon/2)$. Note that $\\min(1,\\epsilon)$ only gives $2\\delta \\leq 2\\epsilon$, not $\\leq \\epsilon$.",
      "explanation_he": "\u05e2\u05dd $|x|<\\delta\\leq 1$: $|x^2+x|<2|x|<2\\delta$. \u05e6\u05e8\u05d9\u05db\u05d9\u05dd $2\\delta\\leq\\epsilon$, \u05dc\u05db\u05df $\\delta\\leq\\epsilon/2$. \u05db\u05da $\\delta=\\min(1,\\epsilon/2)$. \u05dc\u05ea\u05e9\u05d5\u05de\u05ea \u05dc\u05d1: $\\min(1,\\epsilon)$ \u05e0\u05d5\u05ea\u05df \u05e8\u05e7 $2\\delta \\leq 2\\epsilon$, \u05dc\u05d0 $\\leq \\epsilon$."
    }
  ]
})

print("Lesson 1 done")
