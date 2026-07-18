#!/usr/bin/env python3
"""Deterministic, sympy-verified generator of original question-store items.

Produces legally-clean (`license = generated-original`) composite items whose
answers are computed by sympy — correct by construction and independently
re-confirmed by the Node verifier via CAS (scripts/gen/cas_check.py).

Design goals (from pilot review feedback):
  * DIVERSITY — every bank spans easy / medium / hard and >=4 question kinds.
  * DEPTH     — conceptual items (slope, tangent, normal, f'' vs f',
                monotonicity, concavity, interpretation), not just "compute f'".
  * WORKED SOLUTIONS — every item ships a multi-step bilingual derivation, and
                `open` items carry an explicit `steps` list the learner reveals.
  * DISTINCT — functions differ from the lessons' theory worked-examples.
  * READABLE MATH — Hebrew never appears inside $...$ (KaTeX has no HE glyphs);
                connective words stay in plain markdown, math stays LTR in $...$.

Usage:
  python scripts/gen/generate_math_items.py --concept derivatives_rules \
      --lesson scripts/seed_data/lessons/derivatives_rules.json \
      --out content/question-store/generated/derivatives_rules.json
"""
from __future__ import annotations

import argparse
import json
import os

import sympy as sp

x = sp.symbols("x")


# --------------------------------------------------------------------------- #
# Low-level helpers                                                            #
# --------------------------------------------------------------------------- #
def _latex(expr) -> str:
    return sp.latex(sp.sympify(expr)) if not isinstance(expr, str) else sp.latex(sp.sympify(expr.replace("^", "**")))


def _L(expr) -> str:
    """LaTeX of an already-sympy expression (no re-parse)."""
    return sp.latex(expr)


def _plain(expr) -> str:
    return str(expr)


def _to_num(expr):
    """Convert a sympy value to a JSON-friendly int/float."""
    val = float(sp.N(expr))
    return round(val) if abs(val - round(val)) < 1e-9 else round(val, 6)


def _expl(steps: list[str]) -> str:
    """Join step strings into multi-paragraph markdown."""
    return "\n\n".join(s for s in steps if s)


def _sen(n: int, label: str, body: str) -> str:
    return f"**Step {n} — {label}.** {body}"


def _she(n: int, label: str, body: str) -> str:
    return f"**שלב {n} — {label}.** {body}"


DEFAULT_RUBRIC_EN = (
    "Full marks: correct method shown step by step AND correct final answer. "
    "Partial: correct method with an arithmetic slip. Method shown always earns "
    "method marks even if the final value is wrong."
)
DEFAULT_RUBRIC_HE = (
    "ניקוד מלא: שיטה נכונה המוצגת שלב-אחר-שלב וגם תשובה סופית נכונה. "
    "חלקי: שיטה נכונה עם טעות חשבון. הצגת השיטה תמיד מזכה בנקודות שיטה גם אם "
    "הערך הסופי שגוי."
)


def _item(concept, meta, *, kind, difficulty, stem_en, stem_he, answer_payload,
          explanation_en, explanation_he, skill_atoms, verify,
          rubric_en=None, rubric_he=None):
    part = {
        "ord": 1,
        "kind": kind,
        "difficulty": difficulty,
        "stem_en": stem_en,
        "stem_he": stem_he,
        "answer_payload": answer_payload,
        "explanation_en": explanation_en,
        "explanation_he": explanation_he,
        "skill_atoms": skill_atoms,
        "verify": verify,
    }
    if rubric_en:
        part["rubric_en"] = rubric_en
    if rubric_he:
        part["rubric_he"] = rubric_he
    return {
        "concept_id": concept,
        "subject": meta["subject"],
        "level": meta["level"],
        "math_track": meta.get("math_track", []),
        "points_level": meta.get("points_level"),
        "kind": kind,
        "difficulty": difficulty,
        "stem_en": "",
        "stem_he": "",
        "parts": [part],
        "skill_atoms": skill_atoms,
        "answer_payload": answer_payload,
        "source": "generated",
        "license": "generated-original",
        "provenance": {"generator": "generate_math_items.py", "method": "sympy"},
        "verification_status": "unverified",
    }


# --------------------------------------------------------------------------- #
# Generic constructors (multi-step explanations built in)                      #
# --------------------------------------------------------------------------- #
def num(concept, meta, difficulty, stem_en, stem_he, cas_value, atoms,
        steps_en, steps_he):
    """Numeric item; answer recomputed by CAS from the sympy value expression."""
    value = _to_num(sp.sympify(str(cas_value).replace("^", "**")))
    return _item(
        concept, meta, kind="numeric", difficulty=difficulty,
        stem_en=stem_en, stem_he=stem_he,
        answer_payload={"value": value},
        explanation_en=_expl(steps_en), explanation_he=_expl(steps_he),
        skill_atoms=atoms,
        verify={"check": "value", "value": str(cas_value), "claimed": str(value)},
    )


def short(concept, meta, difficulty, stem_en, stem_he, acceptable, atoms,
          steps_en, steps_he, verify):
    return _item(
        concept, meta, kind="short_answer", difficulty=difficulty,
        stem_en=stem_en, stem_he=stem_he,
        answer_payload={"acceptable_answers": acceptable, "case_sensitive": False},
        explanation_en=_expl(steps_en), explanation_he=_expl(steps_he),
        skill_atoms=atoms, verify=verify,
    )


def mcq(concept, meta, difficulty, stem_en, stem_he, options, correct_index,
        verify, atoms, steps_en, steps_he):
    opts = [f"${o}$" for o in options]
    return _item(
        concept, meta, kind="mcq", difficulty=difficulty,
        stem_en=stem_en, stem_he=stem_he,
        answer_payload={"options_en": opts, "options_he": opts, "correct_index": correct_index},
        explanation_en=_expl(steps_en), explanation_he=_expl(steps_he),
        skill_atoms=atoms, verify=verify,
    )


def tf(concept, meta, difficulty, stem_en, stem_he, verify, truth, atoms,
       steps_en, steps_he):
    return _item(
        concept, meta, kind="true_false", difficulty=difficulty,
        stem_en=stem_en, stem_he=stem_he,
        answer_payload={"value": bool(truth)},
        explanation_en=_expl(steps_en), explanation_he=_expl(steps_he),
        skill_atoms=atoms, verify=verify,
    )


def open_worked(concept, meta, difficulty, stem_en, stem_he, steps_en, steps_he,
                atoms, verify, tail_en="", tail_he=""):
    """An open (self-assessed) item that reveals a full multi-step solution.

    steps_* are shown as an ordered 'Expected Steps' list; the explanation
    repeats them as a sample solution so the reveal is self-contained.
    """
    return _item(
        concept, meta, kind="open", difficulty=difficulty,
        stem_en=stem_en, stem_he=stem_he,
        answer_payload={"steps_en": steps_en, "steps_he": steps_he},
        explanation_en=_expl([*steps_en, tail_en]),
        explanation_he=_expl([*steps_he, tail_he]),
        skill_atoms=atoms, verify=verify,
        rubric_en=DEFAULT_RUBRIC_EN, rubric_he=DEFAULT_RUBRIC_HE,
    )


# --------------------------------------------------------------------------- #
# Calculus-specific smart constructors                                         #
# --------------------------------------------------------------------------- #
def diff_short(concept, meta, f, difficulty, atoms, rule_en, rule_he):
    fp = sp.diff(f, x)
    fps = sp.simplify(fp)
    steps_en = [
        _sen(1, "Identify the rule", rule_en),
        _sen(2, "Differentiate", f"$f'(x) = {_L(fp)}$."),
    ]
    steps_he = [
        _she(1, "זיהוי הכלל", rule_he),
        _she(2, "גזירה", f"$f'(x) = {_L(fp)}$."),
    ]
    if sp.simplify(fp - fps) == 0 and _L(fp) != _L(fps):
        steps_en.append(_sen(3, "Simplify", f"$f'(x) = {_L(fps)}$."))
        steps_he.append(_she(3, "פישוט", f"$f'(x) = {_L(fps)}$."))
    steps_en.append(f"**Answer:** $f'(x) = {_L(fps)}$.")
    steps_he.append(f"**תשובה:** $f'(x) = {_L(fps)}$.")
    return short(
        concept, meta, difficulty,
        f"Differentiate $f(x) = {_L(f)}$.",
        f"גזרו את $f(x) = {_L(f)}$.",
        [_plain(fp), _plain(fps), _L(fp), _L(fps)], atoms,
        steps_en, steps_he,
        verify={"check": "derivative", "of": _plain(f), "var": "x", "claimed": _plain(fp)},
    )


def diff_at_num(concept, meta, f, x0, difficulty, atoms):
    fp = sp.diff(f, x)
    val = fp.subs(x, x0)
    steps_en = [
        _sen(1, "Differentiate", f"$f'(x) = {_L(fp)}$."),
        _sen(2, f"Substitute $x = {x0}$", f"$f'({x0}) = {_L(val)}$."),
        f"**Answer:** $f'({x0}) = {_L(val)}$.",
    ]
    steps_he = [
        _she(1, "גזירה", f"$f'(x) = {_L(fp)}$."),
        _she(2, f"הצבת $x = {x0}$", f"$f'({x0}) = {_L(val)}$."),
        f"**תשובה:** $f'({x0}) = {_L(val)}$.",
    ]
    return num(
        concept, meta, difficulty,
        f"Given $f(x) = {_L(f)}$, compute $f'({x0})$.",
        f"בהינתן $f(x) = {_L(f)}$, חשבו את $f'({x0})$.",
        _plain(val), atoms, steps_en, steps_he,
    )


def tangent_line(concept, meta, f, a, difficulty, atoms):
    fp = sp.diff(f, x)
    m = fp.subs(x, a)
    y0 = f.subs(x, a)
    line = sp.expand(m * (x - a) + y0)
    steps_en = [
        _sen(1, "Slope from the derivative", f"$f'(x) = {_L(fp)}$, so the slope is $m = f'({a}) = {_L(m)}$."),
        _sen(2, "Point of tangency", f"$f({a}) = {_L(y0)}$, giving the point $({a}, {_L(y0)})$."),
        _sen(3, "Point-slope form", f"$y - {_L(y0)} = {_L(m)}\\,(x - {a})$."),
        f"**Answer:** $y = {_L(line)}$.",
    ]
    steps_he = [
        _she(1, "שיפוע מהנגזרת", f"$f'(x) = {_L(fp)}$, ולכן השיפוע הוא $m = f'({a}) = {_L(m)}$."),
        _she(2, "נקודת ההשקה", f"$f({a}) = {_L(y0)}$, כלומר הנקודה $({a}, {_L(y0)})$."),
        _she(3, "צורת נקודה-שיפוע", f"$y - {_L(y0)} = {_L(m)}\\,(x - {a})$."),
        f"**תשובה:** $y = {_L(line)}$.",
    ]
    return open_worked(
        concept, meta, difficulty,
        f"Find the equation of the tangent line to $f(x) = {_L(f)}$ at $x = {a}$.",
        f"מצאו את משוואת המשיק ל-$f(x) = {_L(f)}$ בנקודה $x = {a}$.",
        steps_en, steps_he, atoms,
        verify={"check": "derivative_at", "of": _plain(f), "var": "x", "at": str(a), "claimed": _plain(m)},
    )


def normal_slope_num(concept, meta, f, a, difficulty, atoms):
    fp = sp.diff(f, x)
    m = fp.subs(x, a)
    n = sp.simplify(-1 / m)
    steps_en = [
        _sen(1, "Tangent slope", f"$f'(x) = {_L(fp)}$, so $m_{{tan}} = f'({a}) = {_L(m)}$."),
        _sen(2, "Normal is perpendicular", f"The normal slope is $-\\dfrac{{1}}{{m_{{tan}}}} = {_L(n)}$."),
        f"**Answer:** normal slope $= {_L(n)}$.",
    ]
    steps_he = [
        _she(1, "שיפוע המשיק", f"$f'(x) = {_L(fp)}$, ולכן $m_{{tan}} = f'({a}) = {_L(m)}$."),
        _she(2, "הנורמל מאונך", f"שיפוע הנורמל הוא $-\\dfrac{{1}}{{m_{{tan}}}} = {_L(n)}$."),
        f"**תשובה:** שיפוע הנורמל $= {_L(n)}$.",
    ]
    return num(
        concept, meta, difficulty,
        f"Find the slope of the normal line to $f(x) = {_L(f)}$ at $x = {a}$.",
        f"מצאו את שיפוע הנורמל ל-$f(x) = {_L(f)}$ בנקודה $x = {a}$.",
        _plain(n), atoms, steps_en, steps_he,
    )


def concavity_tf(concept, meta, f, x0, claim_up, difficulty, atoms):
    f2 = sp.diff(f, x, 2)
    v = f2.subs(x, x0)
    truth = bool(v > 0) if claim_up else bool(v < 0)
    word_en = "concave up" if claim_up else "concave down"
    word_he = "קעורה כלפי מעלה" if claim_up else "קעורה כלפי מטה"
    actual_en = "concave up" if v > 0 else ("concave down" if v < 0 else "an inflection candidate")
    actual_he = "קעורה כלפי מעלה" if v > 0 else ("קעורה כלפי מטה" if v < 0 else "מועמדת לפיתול")
    rel = ">" if v > 0 else ("<" if v < 0 else "=")
    predicate = f"({_plain(v)}) > 0" if claim_up else f"({_plain(v)}) < 0"
    steps_en = [
        _sen(1, "Second derivative", f"$f''(x) = {_L(f2)}$."),
        _sen(2, f"Evaluate at $x = {x0}$", f"$f''({x0}) = {_L(v)}$."),
        f"**Conclusion:** $f''({x0}) {rel} 0$, so $f$ is {actual_en} there — the statement is {'true' if truth else 'false'}.",
    ]
    steps_he = [
        _she(1, "נגזרת שנייה", f"$f''(x) = {_L(f2)}$."),
        _she(2, f"הצבה ב-$x = {x0}$", f"$f''({x0}) = {_L(v)}$."),
        f"**מסקנה:** $f''({x0}) {rel} 0$, ולכן $f$ {actual_he} שם — ההיגד {'נכון' if truth else 'לא נכון'}.",
    ]
    return tf(
        concept, meta, difficulty,
        f"True or False: $f(x) = {_L(f)}$ is {word_en} at $x = {x0}$.",
        f"נכון או לא נכון: $f(x) = {_L(f)}$ {word_he} בנקודה $x = {x0}$.",
        {"check": "truth", "predicate": predicate, "claimed": ("true" if truth else "false")},
        truth, atoms, steps_en, steps_he,
    )


def monotonic_tf(concept, meta, f, test_pt, claim_increasing, difficulty, atoms):
    fp = sp.diff(f, x)
    v = fp.subs(x, test_pt)
    truth = bool(v > 0) if claim_increasing else bool(v < 0)
    word_en = "increasing" if claim_increasing else "decreasing"
    word_he = "עולה" if claim_increasing else "יורדת"
    actual_en = "increasing" if v > 0 else "decreasing"
    actual_he = "עולה" if v > 0 else "יורדת"
    rel = ">" if v > 0 else "<"
    predicate = f"({_plain(v)}) > 0" if claim_increasing else f"({_plain(v)}) < 0"
    steps_en = [
        _sen(1, "Sign of the first derivative", f"$f'(x) = {_L(fp)}$."),
        _sen(2, f"Test at $x = {test_pt}$", f"$f'({test_pt}) = {_L(v)}$."),
        f"**Conclusion:** $f'(x) {rel} 0$ there, so $f$ is {actual_en} — the statement is {'true' if truth else 'false'}.",
    ]
    steps_he = [
        _she(1, "סימן הנגזרת הראשונה", f"$f'(x) = {_L(fp)}$."),
        _she(2, f"בדיקה ב-$x = {test_pt}$", f"$f'({test_pt}) = {_L(v)}$."),
        f"**מסקנה:** $f'(x) {rel} 0$ שם, ולכן $f$ {actual_he} — ההיגד {'נכון' if truth else 'לא נכון'}.",
    ]
    return tf(
        concept, meta, difficulty,
        f"True or False: $f(x) = {_L(f)}$ is {word_en} near $x = {test_pt}$.",
        f"נכון או לא נכון: $f(x) = {_L(f)}$ {word_he} בסביבת $x = {test_pt}$.",
        {"check": "truth", "predicate": predicate, "claimed": ("true" if truth else "false")},
        truth, atoms, steps_en, steps_he,
    )


# --------------------------------------------------------------------------- #
# Concept generators                                                           #
# --------------------------------------------------------------------------- #
def gen_derivatives_rules(meta):
    c = "derivatives_rules"
    R_pow = ("Sum and power rules — differentiate each term with $\\frac{d}{dx}x^n = n x^{n-1}$.",
             "כללי הסכום והחזקה — גוזרים כל איבר לפי $\\frac{d}{dx}x^n = n x^{n-1}$.")
    R_prod = ("Product rule: $(uv)' = u'v + uv'$.", "כלל המכפלה: $(uv)' = u'v + uv'$.")
    R_quot = ("Quotient rule: $\\left(\\frac{u}{v}\\right)' = \\frac{u'v - uv'}{v^2}$.",
              "כלל המנה: $\\left(\\frac{u}{v}\\right)' = \\frac{u'v - uv'}{v^2}$.")
    R_chain = ("Chain rule: differentiate the outer function, then multiply by the inner derivative.",
               "כלל השרשרת: גוזרים את הפונקציה החיצונית ומכפילים בנגזרת הפנימית.")
    items = [
        diff_short(c, meta, 5 * x**4 - 2 * x**3 + 7 * x - 4, "easy", ["power_rule", "sum_rule"], *R_pow),
        diff_at_num(c, meta, 2 * x**3 + x**2 - 5 * x, 2, "easy", ["power_rule", "sum_rule"]),
        diff_short(c, meta, (2 * x**2 - 1) * sp.cos(x), "medium", ["product_rule"], *R_prod),
        diff_short(c, meta, x**3 * sp.exp(x), "medium", ["product_rule"], *R_prod),
        diff_short(c, meta, (3 * x - 2) / (x**2 + 1), "medium", ["quotient_rule"], *R_quot),
        diff_short(c, meta, sp.sin(4 * x**2 + 1), "medium", ["chain_rule"], *R_chain),
        diff_short(c, meta, (2 * x**3 - 5) ** 6, "hard", ["chain_rule", "power_rule"], *R_chain),
        diff_short(c, meta, x**2 * sp.exp(sp.cos(x)), "hard", ["product_rule", "chain_rule"], *R_prod),
        mcq(c, meta, "medium",
            "Which expression correctly applies the product rule to $f(x) = x^2 \\sin x$?",
            "איזה ביטוי מיישם נכון את כלל המכפלה עבור $f(x) = x^2 \\sin x$?",
            ["2x\\sin x + x^2\\cos x", "2x\\cos x", "2x\\sin x - x^2\\cos x", "x^2\\cos x"], 0,
            {"check": "derivative", "of": "x**2*sin(x)", "var": "x", "claimed": "2*x*sin(x)+x**2*cos(x)"},
            ["product_rule"],
            ["**Step 1 — Set $u = x^2$, $v = \\sin x$.** Then $u' = 2x$, $v' = \\cos x$.",
             "**Step 2 — Apply $(uv)' = u'v + uv'$.** $f'(x) = 2x\\sin x + x^2\\cos x$.",
             "**Answer:** $2x\\sin x + x^2\\cos x$. Option B forgets a term; C flips a sign."],
            ["**שלב 1 — נסמן $u = x^2$, $v = \\sin x$.** אז $u' = 2x$, $v' = \\cos x$.",
             "**שלב 2 — מיישמים $(uv)' = u'v + uv'$.** $f'(x) = 2x\\sin x + x^2\\cos x$.",
             "**תשובה:** $2x\\sin x + x^2\\cos x$. אפשרות B משמיטה איבר; C הופכת סימן."]),
        tf(c, meta, "medium",
           "True or False: $\\dfrac{d}{dx}\\big(e^{3x}\\big) = 3e^{3x}$.",
           "נכון או לא נכון: $\\dfrac{d}{dx}\\big(e^{3x}\\big) = 3e^{3x}$.",
           {"check": "derivative", "of": "exp(3*x)", "var": "x", "claimed": "3*exp(3*x)"},
           True, ["chain_rule", "derivative_exp"],
           ["**Step 1 — Chain rule on $e^{u}$.** $\\frac{d}{dx}e^{u} = e^{u}\\cdot u'$ with $u = 3x$, $u' = 3$.",
            "**Step 2 — Multiply.** $\\frac{d}{dx}e^{3x} = 3e^{3x}$.",
            "**Conclusion:** the statement is **true**."],
           ["**שלב 1 — כלל השרשרת על $e^{u}$.** $\\frac{d}{dx}e^{u} = e^{u}\\cdot u'$ עם $u = 3x$, $u' = 3$.",
            "**שלב 2 — הכפלה.** $\\frac{d}{dx}e^{3x} = 3e^{3x}$.",
            "**מסקנה:** ההיגד **נכון**."]),
        tf(c, meta, "hard",
           "True or False: $\\dfrac{d}{dx}\\big(x^2 e^x\\big) = 2x e^x$.",
           "נכון או לא נכון: $\\dfrac{d}{dx}\\big(x^2 e^x\\big) = 2x e^x$.",
           {"check": "truth", "predicate": "Eq(1**2*exp(1), 0)", "claimed": "false"},
           False, ["product_rule"],
           ["**Step 1 — Product rule.** $u = x^2,\\ v = e^x \\Rightarrow (uv)' = 2x e^x + x^2 e^x$.",
            "**Step 2 — Compare.** The statement drops the $x^2 e^x$ term.",
            "**Conclusion:** the statement is **false**; the correct derivative is $e^x(2x + x^2)$."],
           ["**שלב 1 — כלל המכפלה.** $u = x^2,\\ v = e^x \\Rightarrow (uv)' = 2x e^x + x^2 e^x$.",
            "**שלב 2 — השוואה.** ההיגד משמיט את האיבר $x^2 e^x$.",
            "**מסקנה:** ההיגד **לא נכון**; הנגזרת הנכונה היא $e^x(2x + x^2)$."]),
    ]
    return items


def gen_derivatives_trig_exp(meta):
    c = "derivatives_trig_exp"
    R_chain = ("Chain rule with a trig/exp outer function.", "כלל השרשרת עם פונקציה חיצונית טריגונומטרית/מעריכית.")
    items = [
        diff_short(c, meta, sp.sin(x) + sp.cos(x), "easy", ["derivative_sin_cos"],
                   "Derivatives of sine and cosine: $(\\sin x)' = \\cos x$, $(\\cos x)' = -\\sin x$.",
                   "נגזרות סינוס וקוסינוס: $(\\sin x)' = \\cos x$, $(\\cos x)' = -\\sin x$."),
        diff_short(c, meta, sp.exp(x) + sp.log(x), "easy", ["derivative_exp", "derivative_ln"],
                   "$(e^x)' = e^x$ and $(\\ln x)' = \\frac{1}{x}$.",
                   "$(e^x)' = e^x$ וגם $(\\ln x)' = \\frac{1}{x}$."),
        diff_short(c, meta, sp.sin(3 * x**2), "medium", ["chain_rule", "derivative_sin_cos"], *R_chain),
        diff_short(c, meta, sp.exp(x**2 - 1), "medium", ["chain_rule", "derivative_exp"], *R_chain),
        diff_short(c, meta, sp.log(x**2 + 4), "medium", ["chain_rule", "derivative_ln"], *R_chain),
        diff_short(c, meta, x * sp.sin(x), "medium", ["product_rule", "derivative_sin_cos"],
                   "Product rule: $(uv)' = u'v + uv'$.", "כלל המכפלה: $(uv)' = u'v + uv'$."),
        diff_at_num(c, meta, sp.exp(2 * x), 0, "easy", ["chain_rule", "derivative_exp"]),
        mcq(c, meta, "easy",
            "What is $\\dfrac{d}{dx}(\\cos x)$?",
            "מהי $\\dfrac{d}{dx}(\\cos x)$?",
            ["-\\sin x", "\\sin x", "-\\cos x", "\\tan x"], 0,
            {"check": "derivative", "of": "cos(x)", "var": "x", "claimed": "-sin(x)"},
            ["derivative_sin_cos"],
            ["**Rule:** $(\\cos x)' = -\\sin x$. The minus sign is the most common exam slip.",
             "**Answer:** $-\\sin x$."],
            ["**כלל:** $(\\cos x)' = -\\sin x$. סימן המינוס הוא הטעות הנפוצה ביותר.",
             "**תשובה:** $-\\sin x$."]),
        mcq(c, meta, "hard",
            "Using the chain rule, $\\dfrac{d}{dx}\\big(\\ln(\\sin x)\\big) = ?$",
            "לפי כלל השרשרת, $\\dfrac{d}{dx}\\big(\\ln(\\sin x)\\big) = ?$",
            ["\\cot x", "\\tan x", "\\frac{1}{\\sin x}", "\\cos x"], 0,
            {"check": "derivative", "of": "log(sin(x))", "var": "x", "claimed": "cos(x)/sin(x)"},
            ["chain_rule", "derivative_ln"],
            ["**Step 1 — Outer $\\ln u$ gives $\\frac{1}{u}$;** here $u = \\sin x$.",
             "**Step 2 — Multiply by $u' = \\cos x$:** $\\frac{\\cos x}{\\sin x} = \\cot x$.",
             "**Answer:** $\\cot x$."],
            ["**שלב 1 — חיצוני $\\ln u$ נותן $\\frac{1}{u}$;** כאן $u = \\sin x$.",
             "**שלב 2 — מכפילים ב-$u' = \\cos x$:** $\\frac{\\cos x}{\\sin x} = \\cot x$.",
             "**תשובה:** $\\cot x$."]),
        tf(c, meta, "medium",
           "True or False: $\\dfrac{d}{dx}\\big(\\sin(x^2)\\big) = \\cos(x^2)$.",
           "נכון או לא נכון: $\\dfrac{d}{dx}\\big(\\sin(x^2)\\big) = \\cos(x^2)$.",
           {"check": "truth", "predicate": "Eq(2*cos(1), cos(1))", "claimed": "false"},
           False, ["chain_rule", "derivative_sin_cos"],
           ["**Step 1 — Chain rule.** The inner function is $x^2$ with derivative $2x$.",
            "**Step 2 — Correct derivative.** $\\frac{d}{dx}\\sin(x^2) = 2x\\cos(x^2)$.",
            "**Conclusion:** the statement drops the factor $2x$, so it is **false**."],
           ["**שלב 1 — כלל השרשרת.** הפונקציה הפנימית היא $x^2$ ונגזרתה $2x$.",
            "**שלב 2 — הנגזרת הנכונה.** $\\frac{d}{dx}\\sin(x^2) = 2x\\cos(x^2)$.",
            "**מסקנה:** ההיגד משמיט את הגורם $2x$, ולכן **לא נכון**."]),
    ]
    return items


def gen_derivatives_applications(meta):
    c = "derivatives_applications"
    # Distinct from theory (theory used x^3-6x^2+9x+1, x^3-3x+2, fencing 100).
    f1 = 2 * x**3 - 9 * x**2 + 12 * x
    f2 = x**3 - 12 * x + 5
    items = [
        diff_at_num(c, meta, f1, 1, "easy", ["tangent_line"]),
        num(c, meta, "easy",
            "The slope of the curve $y = x^3 - 12x + 5$ at $x = 2$ equals the value of $y'$ there. Find it.",
            "שיפוע העקומה $y = x^3 - 12x + 5$ בנקודה $x = 2$ שווה לערך $y'$ שם. מצאו אותו.",
            "3*2**2-12", ["slope_of_curve", "tangent_line"],
            ["**Step 1 — Differentiate.** $y' = 3x^2 - 12$.",
             "**Step 2 — Slope is the derivative value.** $y'(2) = 3(4) - 12 = 0$.",
             "**Answer:** slope $= 0$ (a horizontal tangent — $x=2$ is a critical point)."],
            ["**שלב 1 — גזירה.** $y' = 3x^2 - 12$.",
             "**שלב 2 — השיפוע הוא ערך הנגזרת.** $y'(2) = 3\\cdot4 - 12 = 0$.",
             "**תשובה:** שיפוע $= 0$ (משיק אופקי — $x=2$ נקודה קריטית)."]),
        tangent_line(c, meta, f2, 3, "medium", ["tangent_line"]),
        normal_slope_num(c, meta, f2, 1, "hard", ["normal_line", "tangent_line"]),
        monotonic_tf(c, meta, f1, 0, True, "medium", ["monotonicity"]),
        concavity_tf(c, meta, f1, 1, False, "medium", ["concavity"]),
        num(c, meta, "medium",
            "Find the $x$-coordinate of the inflection point of $f(x) = 2x^3 - 9x^2 + 12x$.",
            "מצאו את שיעור ה-$x$ של נקודת הפיתול של $f(x) = 2x^3 - 9x^2 + 12x$.",
            "3/2", ["inflection_point", "concavity"],
            ["**Step 1 — Second derivative.** $f''(x) = 12x - 18$.",
             "**Step 2 — Set $f'' = 0$.** $12x - 18 = 0 \\Rightarrow x = \\tfrac{3}{2}$.",
             "**Step 3 — Confirm sign change.** $f''$ goes from $-$ to $+$ across $x = \\tfrac32$, so it is a genuine inflection.",
             "**Answer:** $x = \\tfrac{3}{2}$."],
            ["**שלב 1 — נגזרת שנייה.** $f''(x) = 12x - 18$.",
             "**שלב 2 — $f'' = 0$.** $12x - 18 = 0 \\Rightarrow x = \\tfrac{3}{2}$.",
             "**שלב 3 — אימות שינוי סימן.** $f''$ עוברת מ-$-$ ל-$+$ סביב $x = \\tfrac32$, ולכן זו נקודת פיתול אמיתית.",
             "**תשובה:** $x = \\tfrac{3}{2}$."]),
        mcq(c, meta, "hard",
            "At $x = 1$, $f(x) = 2x^3 - 9x^2 + 12x$ has $f'(1) = 0$ and $f''(1) = -6$. What is $x = 1$?",
            "בנקודה $x = 1$ מתקיים $f'(1) = 0$ ו-$f''(1) = -6$ עבור $f(x) = 2x^3 - 9x^2 + 12x$. מהי $x = 1$?",
            ["\\text{local maximum}", "\\text{local minimum}", "\\text{inflection point}", "\\text{not critical}"], 0,
            {"check": "truth", "predicate": "(12*1-18) < 0", "claimed": "true"},
            ["extremum_classification", "concavity"],
            ["**Second-derivative test:** $f'(1) = 0$ makes $x=1$ critical; $f''(1) = -6 < 0$ means concave down.",
             "**Conclusion:** concave down at a critical point $\\Rightarrow$ **local maximum**."],
            ["**מבחן הנגזרת השנייה:** $f'(1) = 0$ הופך את $x=1$ לקריטית; $f''(1) = -6 < 0$ פירושו קעורה כלפי מטה.",
             "**מסקנה:** קעורה כלפי מטה בנקודה קריטית $\\Rightarrow$ **מקסימום מקומי**."]),
        open_worked(c, meta, "hard",
            "A rectangle has its base on the $x$-axis and its two upper corners on the parabola $y = 12 - x^2$. Find the dimensions that maximize its area.",
            "למלבן בסיס על ציר ה-$x$ ושתי פינותיו העליונות על הפרבולה $y = 12 - x^2$. מצאו את הממדים הממקסמים את השטח.",
            ["**Step 1 — Set up.** By symmetry the corners are at $\\pm x$, so width $= 2x$ and height $= 12 - x^2$.",
             "**Step 2 — Area function.** $A(x) = 2x(12 - x^2) = 24x - 2x^3$, for $0 < x < 2\\sqrt3$.",
             "**Step 3 — Optimize.** $A'(x) = 24 - 6x^2 = 0 \\Rightarrow x^2 = 4 \\Rightarrow x = 2$.",
             "**Step 4 — Confirm max.** $A''(x) = -12x < 0$, so $x = 2$ is a maximum.",
             "**Answer:** width $= 4$, height $= 12 - 4 = 8$, area $= 32$."],
            ["**שלב 1 — הצבה.** מסימטריה הפינות ב-$\\pm x$, ולכן רוחב $= 2x$ וגובה $= 12 - x^2$.",
             "**שלב 2 — פונקציית שטח.** $A(x) = 2x(12 - x^2) = 24x - 2x^3$, עבור $0 < x < 2\\sqrt3$.",
             "**שלב 3 — אופטימיזציה.** $A'(x) = 24 - 6x^2 = 0 \\Rightarrow x^2 = 4 \\Rightarrow x = 2$.",
             "**שלב 4 — אימות מקסימום.** $A''(x) = -12x < 0$, ולכן $x = 2$ מקסימום.",
             "**תשובה:** רוחב $= 4$, גובה $= 8$, שטח $= 32$."],
            ["optimization", "extremum_classification"],
            {"check": "truth", "predicate": "Eq(24 - 6*2**2, 0)", "claimed": "true"}),
        num(c, meta, "medium",
            r"For $f(x) = 2x^3 - 9x^2 + 12x$, compute $f''(2)$ and note its sign.",
            r"עבור $f(x) = 2x^3 - 9x^2 + 12x$, חשבו את $f''(2)$ וציינו את הסימן.",
            "12*2-18", ["concavity", "second_derivative"],
            [r"**Step 1 — First derivative.** $f'(x) = 6x^2 - 18x + 12$.",
             r"**Step 2 — Second derivative.** $f''(x) = 12x - 18$.",
             r"**Step 3 — Evaluate.** $f''(2) = 24 - 18 = 6 > 0$, so $f$ is concave up at $x = 2$.",
             r"**Answer:** $6$."],
            [r"**שלב 1 — נגזרת ראשונה.** $f'(x) = 6x^2 - 18x + 12$.",
             r"**שלב 2 — נגזרת שנייה.** $f''(x) = 12x - 18$.",
             r"**שלב 3 — הצבה.** $f''(2) = 24 - 18 = 6 > 0$, ולכן $f$ קעורה כלפי מעלה ב-$x = 2$.",
             r"**תשובה:** $6$."]),
        open_worked(c, meta, "hard",
            r"A particle moves along a line with position $s(t) = t^3 - 6t^2 + 9t$ (metres, $t \ge 0$). Find the times it is momentarily at rest and its acceleration at each.",
            r"חלקיק נע על ישר עם מיקום $s(t) = t^3 - 6t^2 + 9t$ (מטרים, $t \ge 0$). מצאו את הזמנים בהם הוא במנוחה רגעית ואת התאוצה בכל אחד מהם.",
            [r"**Step 1 — Velocity.** $v(t) = s'(t) = 3t^2 - 12t + 9 = 3(t-1)(t-3)$.",
             r"**Step 2 — At rest means $v = 0$.** $t = 1$ and $t = 3$ seconds.",
             r"**Step 3 — Acceleration.** $a(t) = v'(t) = 6t - 12$.",
             r"**Step 4 — Evaluate.** $a(1) = -6\ \text{m/s}^2$ (decelerating), $a(3) = 6\ \text{m/s}^2$ (accelerating).",
             r"**Answer:** at rest at $t = 1, 3$; accelerations $-6$ and $6\ \text{m/s}^2$."],
            [r"**שלב 1 — מהירות.** $v(t) = s'(t) = 3t^2 - 12t + 9 = 3(t-1)(t-3)$.",
             r"**שלב 2 — מנוחה פירושה $v = 0$.** $t = 1$ ו-$t = 3$ שניות.",
             r"**שלב 3 — תאוצה.** $a(t) = v'(t) = 6t - 12$.",
             r"**שלב 4 — הצבה.** $a(1) = -6\ \text{m/s}^2$ (מאט), $a(3) = 6\ \text{m/s}^2$ (מאיץ).",
             r"**תשובה:** במנוחה ב-$t = 1, 3$; תאוצות $-6$ ו-$6\ \text{m/s}^2$."],
            ["rate_of_change", "tangent_line"],
            {"check": "derivative_at", "of": "t**3-6*t**2+9*t", "var": "t", "at": "1", "claimed": "0"}),
    ]
    return items


def gen_function_analysis_5pt(meta):
    c = "function_analysis_5pt"
    f = x**4 - 8 * x**2 + 3
    items = [
        diff_short(c, meta, f, "easy", ["monotonicity"],
                   "Power and sum rules term by term.", "כללי חזקה וסכום איבר-איבר."),
        num(c, meta, "medium",
            "Compute $f''(2)$ for $f(x) = x^4 - 8x^2 + 3$.",
            "חשבו את $f''(2)$ עבור $f(x) = x^4 - 8x^2 + 3$.",
            "12*2**2-16", ["concavity"],
            ["**Step 1 — First derivative.** $f'(x) = 4x^3 - 16x$.",
             "**Step 2 — Second derivative.** $f''(x) = 12x^2 - 16$.",
             "**Step 3 — Evaluate.** $f''(2) = 48 - 16 = 32 > 0$ (concave up).",
             "**Answer:** $32$."],
            ["**שלב 1 — נגזרת ראשונה.** $f'(x) = 4x^3 - 16x$.",
             "**שלב 2 — נגזרת שנייה.** $f''(x) = 12x^2 - 16$.",
             "**שלב 3 — הצבה.** $f''(2) = 48 - 16 = 32 > 0$ (קעורה כלפי מעלה).",
             "**תשובה:** $32$."]),
        monotonic_tf(c, meta, f, 1, False, "medium", ["monotonicity"]),
        concavity_tf(c, meta, f, 0, False, "medium", ["concavity"]),
        tangent_line(c, meta, f, 1, "hard", ["tangent_line"]),
        mcq(c, meta, "medium",
            "How many critical points does $f(x) = x^4 - 8x^2 + 3$ have?",
            "כמה נקודות קיצון יש ל-$f(x) = x^4 - 8x^2 + 3$?",
            ["3", "1", "2", "4"], 0,
            {"check": "derivative_at", "of": "x**4-8*x**2+3", "var": "x", "at": "2", "claimed": "0"},
            ["critical_points"],
            ["**Step 1 — Solve $f'(x) = 0$.** $4x^3 - 16x = 4x(x^2 - 4) = 0$.",
             "**Step 2 — Roots.** $x = 0,\\ x = 2,\\ x = -2$ — three critical points.",
             "**Answer:** 3."],
            ["**שלב 1 — פתרון $f'(x) = 0$.** $4x^3 - 16x = 4x(x^2 - 4) = 0$.",
             "**שלב 2 — שורשים.** $x = 0,\\ x = 2,\\ x = -2$ — שלוש נקודות קיצון.",
             "**תשובה:** 3."]),
        open_worked(c, meta, "hard",
            "Investigate $f(x) = x^4 - 8x^2 + 3$: find its critical points and classify each as a local maximum or minimum.",
            "חקרו את $f(x) = x^4 - 8x^2 + 3$: מצאו את נקודות הקיצון וסווגו כל אחת כמקסימום או מינימום מקומי.",
            ["**Step 1 — $f'(x) = 4x^3 - 16x = 4x(x-2)(x+2)$; roots $x = -2, 0, 2$.**",
             "**Step 2 — $f''(x) = 12x^2 - 16$.**",
             "**Step 3 — Classify.** $f''(-2) = 32 > 0$ (min), $f''(0) = -16 < 0$ (max), $f''(2) = 32 > 0$ (min).",
             "**Step 4 — Values.** $f(-2) = -13$, $f(0) = 3$, $f(2) = -13$.",
             "**Answer:** local minima at $(\\pm2, -13)$, local maximum at $(0, 3)$ — a 'W' shape."],
            ["**שלב 1 — $f'(x) = 4x^3 - 16x = 4x(x-2)(x+2)$; שורשים $x = -2, 0, 2$.**",
             "**שלב 2 — $f''(x) = 12x^2 - 16$.**",
             "**שלב 3 — סיווג.** $f''(-2) = 32 > 0$ (מין), $f''(0) = -16 < 0$ (מקס), $f''(2) = 32 > 0$ (מין).",
             "**שלב 4 — ערכים.** $f(-2) = -13$, $f(0) = 3$, $f(2) = -13$.",
             "**תשובה:** מינימום מקומי ב-$(\\pm2, -13)$, מקסימום מקומי ב-$(0, 3)$ — צורת 'W'."],
            ["critical_points", "extremum_classification"],
            {"check": "derivative_at", "of": "x**4-8*x**2+3", "var": "x", "at": "0", "claimed": "0"}),
        num(c, meta, "medium",
            r"The function $g(x) = x^3 - 3x^2 + 5$ has a local minimum. Find its $y$-value.",
            r"לפונקציה $g(x) = x^3 - 3x^2 + 5$ יש מינימום מקומי. מצאו את ערך ה-$y$ שלו.",
            "2**3-3*2**2+5", ["extremum_classification"],
            [r"**Step 1 — Critical points.** $g'(x) = 3x^2 - 6x = 3x(x - 2) = 0 \Rightarrow x = 0, 2$.",
             r"**Step 2 — Classify with $g''(x) = 6x - 6$.** $g''(2) = 6 > 0$, so $x = 2$ is the local minimum.",
             r"**Step 3 — Value.** $g(2) = 8 - 12 + 5 = 1$.",
             r"**Answer:** $1$."],
            [r"**שלב 1 — נקודות קריטיות.** $g'(x) = 3x^2 - 6x = 3x(x - 2) = 0 \Rightarrow x = 0, 2$.",
             r"**שלב 2 — סיווג עם $g''(x) = 6x - 6$.** $g''(2) = 6 > 0$, ולכן $x = 2$ מינימום מקומי.",
             r"**שלב 3 — ערך.** $g(2) = 8 - 12 + 5 = 1$.",
             r"**תשובה:** $1$."]),
        monotonic_tf(c, meta, x**3 - 3 * x**2 + 5, 1, False, "medium", ["monotonicity"]),
        concavity_tf(c, meta, x**3 - 3 * x**2 + 5, 0, False, "medium", ["concavity"]),
        open_worked(c, meta, "hard",
            r"For $g(x) = x^3 - 3x^2 + 5$, state the intervals of increase/decrease and the concavity, and give the inflection point.",
            r"עבור $g(x) = x^3 - 3x^2 + 5$, ציינו את קטעי העלייה/הירידה, את הקעירות ואת נקודת הפיתול.",
            [r"**Step 1 — $g'(x) = 3x(x - 2)$.** Sign chart: $g' > 0$ on $(-\infty, 0)$ and $(2, \infty)$ (increasing); $g' < 0$ on $(0, 2)$ (decreasing).",
             r"**Step 2 — $g''(x) = 6x - 6 = 6(x - 1)$.** $g'' < 0$ for $x < 1$ (concave down), $g'' > 0$ for $x > 1$ (concave up).",
             r"**Step 3 — Inflection.** Concavity switches at $x = 1$; $g(1) = 1 - 3 + 5 = 3$, so the inflection point is $(1, 3)$.",
             r"**Answer:** increasing on $(-\infty,0)\cup(2,\infty)$, decreasing on $(0,2)$; concave down then up; inflection $(1, 3)$."],
            [r"**שלב 1 — $g'(x) = 3x(x - 2)$.** טבלת סימנים: $g' > 0$ ב-$(-\infty, 0)$ וב-$(2, \infty)$ (עולה); $g' < 0$ ב-$(0, 2)$ (יורדת).",
             r"**שלב 2 — $g''(x) = 6(x - 1)$.** $g'' < 0$ עבור $x < 1$ (קעורה כלפי מטה), $g'' > 0$ עבור $x > 1$ (קעורה כלפי מעלה).",
             r"**שלב 3 — פיתול.** הקעירות מתחלפת ב-$x = 1$; $g(1) = 3$, ולכן נקודת הפיתול היא $(1, 3)$.",
             r"**תשובה:** עולה ב-$(-\infty,0)\cup(2,\infty)$, יורדת ב-$(0,2)$; קעורה מטה ואז מעלה; פיתול $(1, 3)$."],
            ["monotonicity", "concavity", "inflection_point"],
            {"check": "second_derivative_at", "of": "x**3-3*x**2+5", "var": "x", "at": "1", "claimed": "0"}),
    ]
    return items


def gen_integrals_applications(meta):
    c = "integrals_applications"
    items = [
        num(c, meta, "easy",
            "Compute $\\int_0^2 (3x^2 + 1)\\,dx$.",
            "חשבו את $\\int_0^2 (3x^2 + 1)\\,dx$.",
            "integrate(3*x**2+1,(x,0,2))", ["definite_integral"],
            ["**Step 1 — Antiderivative.** $\\int (3x^2 + 1)\\,dx = x^3 + x$.",
             "**Step 2 — Evaluate $[x^3 + x]_0^2$.** $(8 + 2) - 0 = 10$.",
             "**Answer:** $10$."],
            ["**שלב 1 — פונקציה קדומה.** $\\int (3x^2 + 1)\\,dx = x^3 + x$.",
             "**שלב 2 — הצבה $[x^3 + x]_0^2$.** $(8 + 2) - 0 = 10$.",
             "**תשובה:** $10$."]),
        short(c, meta, "easy",
              "Find an antiderivative of $f(x) = 4x^3$.",
              "מצאו פונקציה קדומה של $f(x) = 4x^3$.",
              ["x**4", "x^4", "x**4+C"], ["antiderivative"],
              ["**Rule — reverse the power rule:** $\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}$.",
               "**Apply.** $\\int 4x^3\\,dx = x^4 + C$.",
               "**Check.** $\\frac{d}{dx}(x^4) = 4x^3$. ✓"],
              ["**כלל — היפוך כלל החזקה:** $\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}$.",
               "**יישום.** $\\int 4x^3\\,dx = x^4 + C$.",
               "**בדיקה.** $\\frac{d}{dx}(x^4) = 4x^3$. ✓"],
              verify={"check": "derivative", "of": "x**4", "var": "x", "claimed": "4*x**3"}),
        num(c, meta, "medium",
            "Find the area between $f(x) = x^2$ and $g(x) = x$ from $x = 0$ to $x = 1$.",
            "מצאו את השטח בין $f(x) = x^2$ ל-$g(x) = x$ בתחום $x = 0$ עד $x = 1$.",
            "integrate(x-x**2,(x,0,1))", ["area_between_curves"],
            ["**Step 1 — Which is on top?** On $(0,1)$, $x \\ge x^2$, so integrate $g - f = x - x^2$.",
             "**Step 2 — Integrate.** $\\int_0^1 (x - x^2)\\,dx = \\left[\\tfrac{x^2}{2} - \\tfrac{x^3}{3}\\right]_0^1 = \\tfrac12 - \\tfrac13 = \\tfrac16$.",
             "**Answer:** $\\tfrac{1}{6}$."],
            ["**שלב 1 — מי למעלה?** בקטע $(0,1)$ מתקיים $x \\ge x^2$, ולכן אינטגרל על $g - f = x - x^2$.",
             "**שלב 2 — אינטגרציה.** $\\int_0^1 (x - x^2)\\,dx = \\left[\\tfrac{x^2}{2} - \\tfrac{x^3}{3}\\right]_0^1 = \\tfrac16$.",
             "**תשובה:** $\\tfrac{1}{6}$."]),
        num(c, meta, "medium",
            "Compute $\\int_1^4 \\dfrac{1}{\\sqrt{x}}\\,dx$.",
            "חשבו את $\\int_1^4 \\dfrac{1}{\\sqrt{x}}\\,dx$.",
            "integrate(1/sqrt(x),(x,1,4))", ["definite_integral"],
            ["**Step 1 — Rewrite.** $\\frac{1}{\\sqrt{x}} = x^{-1/2}$.",
             "**Step 2 — Antiderivative.** $\\int x^{-1/2}\\,dx = 2\\sqrt{x}$.",
             "**Step 3 — Evaluate.** $[2\\sqrt{x}]_1^4 = 2(2) - 2(1) = 2$.",
             "**Answer:** $2$."],
            ["**שלב 1 — כתיבה מחדש.** $\\frac{1}{\\sqrt{x}} = x^{-1/2}$.",
             "**שלב 2 — פונקציה קדומה.** $\\int x^{-1/2}\\,dx = 2\\sqrt{x}$.",
             "**שלב 3 — הצבה.** $[2\\sqrt{x}]_1^4 = 4 - 2 = 2$.",
             "**תשובה:** $2$."]),
        tf(c, meta, "medium",
           "True or False: $\\int_{-1}^{1} x^3\\,dx = 0$.",
           "נכון או לא נכון: $\\int_{-1}^{1} x^3\\,dx = 0$.",
           {"check": "integral_definite", "of": "x**3", "var": "x", "lower": "-1", "upper": "1", "claimed": "0"},
           True, ["definite_integral"],
           ["**Step 1 — Odd function symmetry.** $x^3$ is odd, and the interval $[-1,1]$ is symmetric.",
            "**Step 2 — Cancellation.** The area below the axis cancels the area above.",
            "**Conclusion:** the integral is $0$ — **true**."],
           ["**שלב 1 — סימטריית פונקציה אי-זוגית.** $x^3$ אי-זוגית והקטע $[-1,1]$ סימטרי.",
            "**שלב 2 — ביטול.** השטח מתחת לציר מבטל את השטח מעליו.",
            "**מסקנה:** האינטגרל הוא $0$ — **נכון**."]),
        mcq(c, meta, "hard",
            "The area under $f(x) = \\sin x$ from $0$ to $\\pi$ is:",
            "השטח מתחת ל-$f(x) = \\sin x$ מ-$0$ עד $\\pi$ הוא:",
            ["2", "0", "1", "\\pi"], 0,
            {"check": "integral_definite", "of": "sin(x)", "var": "x", "lower": "0", "upper": "pi", "claimed": "2"},
            ["definite_integral", "area_under_curve"],
            ["**Step 1 — Antiderivative.** $\\int \\sin x\\,dx = -\\cos x$.",
             "**Step 2 — Evaluate.** $[-\\cos x]_0^{\\pi} = -\\cos\\pi + \\cos 0 = 1 + 1 = 2$.",
             "**Answer:** $2$."],
            ["**שלב 1 — פונקציה קדומה.** $\\int \\sin x\\,dx = -\\cos x$.",
             "**שלב 2 — הצבה.** $[-\\cos x]_0^{\\pi} = 1 + 1 = 2$.",
             "**תשובה:** $2$."]),
        num(c, meta, "easy",
            r"Compute $\int_0^3 (2x + 1)\,dx$.",
            r"חשבו את $\int_0^3 (2x + 1)\,dx$.",
            "integrate(2*x+1,(x,0,3))", ["definite_integral"],
            [r"**Step 1 — Antiderivative.** $\int (2x + 1)\,dx = x^2 + x$.",
             r"**Step 2 — Evaluate $[x^2 + x]_0^3$.** $(9 + 3) - 0 = 12$.",
             r"**Answer:** $12$."],
            [r"**שלב 1 — פונקציה קדומה.** $\int (2x + 1)\,dx = x^2 + x$.",
             r"**שלב 2 — הצבה $[x^2 + x]_0^3$.** $12 - 0 = 12$.",
             r"**תשובה:** $12$."]),
        num(c, meta, "medium",
            r"Find the area enclosed between $y = 4 - x^2$ and the $x$-axis.",
            r"מצאו את השטח הכלוא בין $y = 4 - x^2$ לציר ה-$x$.",
            "integrate(4-x**2,(x,-2,2))", ["area_under_curve"],
            [r"**Step 1 — Find the roots.** $4 - x^2 = 0 \Rightarrow x = \pm 2$ are the limits.",
             r"**Step 2 — Integrate.** $\int_{-2}^{2} (4 - x^2)\,dx = \left[4x - \tfrac{x^3}{3}\right]_{-2}^{2}$.",
             r"**Step 3 — Evaluate.** $\left(8 - \tfrac83\right) - \left(-8 + \tfrac83\right) = 16 - \tfrac{16}{3} = \tfrac{32}{3}$.",
             r"**Answer:** $\tfrac{32}{3}$."],
            [r"**שלב 1 — מציאת השורשים.** $4 - x^2 = 0 \Rightarrow x = \pm 2$ הם הגבולות.",
             r"**שלב 2 — אינטגרציה.** $\int_{-2}^{2} (4 - x^2)\,dx = \left[4x - \tfrac{x^3}{3}\right]_{-2}^{2}$.",
             r"**שלב 3 — הצבה.** $16 - \tfrac{16}{3} = \tfrac{32}{3}$.",
             r"**תשובה:** $\tfrac{32}{3}$."]),
        open_worked(c, meta, "hard",
            r"Find the area of the region enclosed between $y = x^2$ and $y = 2x$.",
            r"מצאו את שטח התחום הכלוא בין $y = x^2$ ל-$y = 2x$.",
            [r"**Step 1 — Intersections.** $x^2 = 2x \Rightarrow x^2 - 2x = 0 \Rightarrow x = 0, 2$.",
             r"**Step 2 — Which is on top?** On $(0, 2)$, $2x \ge x^2$, so integrate $2x - x^2$.",
             r"**Step 3 — Integrate.** $\int_0^2 (2x - x^2)\,dx = \left[x^2 - \tfrac{x^3}{3}\right]_0^2 = 4 - \tfrac83 = \tfrac{4}{3}$.",
             r"**Answer:** $\tfrac{4}{3}$."],
            [r"**שלב 1 — נקודות חיתוך.** $x^2 = 2x \Rightarrow x = 0, 2$.",
             r"**שלב 2 — מי למעלה?** בקטע $(0, 2)$ מתקיים $2x \ge x^2$, ולכן אינטגרל על $2x - x^2$.",
             r"**שלב 3 — אינטגרציה.** $\int_0^2 (2x - x^2)\,dx = \left[x^2 - \tfrac{x^3}{3}\right]_0^2 = \tfrac{4}{3}$.",
             r"**תשובה:** $\tfrac{4}{3}$."],
            ["area_between_curves"],
            {"check": "value", "value": "integrate(2*x-x**2,(x,0,2))", "claimed": "4/3"}),
        mcq(c, meta, "hard",
            r"The region under $y = \sqrt{x}$ for $0 \le x \le 4$ is rotated about the $x$-axis. Its volume $\pi\int_0^4 x\,dx$ equals:",
            r"התחום שמתחת ל-$y = \sqrt{x}$ עבור $0 \le x \le 4$ מסובב סביב ציר ה-$x$. הנפח $\pi\int_0^4 x\,dx$ שווה ל:",
            [r"8\pi", r"16\pi", r"4\pi", r"2\pi"], 0,
            {"check": "truth", "predicate": "Eq(pi*integrate(x,(x,0,4)), 8*pi)", "claimed": "true"},
            ["volume_of_revolution", "definite_integral"],
            [r"**Disk method.** $V = \pi\int_0^4 \left(\sqrt{x}\right)^2\,dx = \pi\int_0^4 x\,dx$.",
             r"**Evaluate.** $\pi\left[\tfrac{x^2}{2}\right]_0^4 = \pi\cdot 8 = 8\pi$.",
             r"**Answer:** $8\pi$."],
            [r"**שיטת הדיסקים.** $V = \pi\int_0^4 \left(\sqrt{x}\right)^2\,dx = \pi\int_0^4 x\,dx$.",
             r"**הצבה.** $\pi\left[\tfrac{x^2}{2}\right]_0^4 = 8\pi$.",
             r"**תשובה:** $8\pi$."]),
        tf(c, meta, "medium",
           r"True or False: $\int_0^{2\pi} \sin x\,dx = 0$.",
           r"נכון או לא נכון: $\int_0^{2\pi} \sin x\,dx = 0$.",
           {"check": "integral_definite", "of": "sin(x)", "var": "x", "lower": "0", "upper": "2*pi", "claimed": "0"},
           True, ["definite_integral"],
           [r"**Antiderivative.** $[-\cos x]_0^{2\pi} = -\cos 2\pi + \cos 0 = -1 + 1 = 0$.",
            r"**Interpretation.** The positive area on $(0,\pi)$ cancels the negative area on $(\pi,2\pi)$.",
            r"**Conclusion:** **true** — but note the *total* area is $4$, not $0$."],
           [r"**פונקציה קדומה.** $[-\cos x]_0^{2\pi} = -1 + 1 = 0$.",
            r"**פרשנות.** השטח החיובי ב-$(0,\pi)$ מבטל את השטח השלילי ב-$(\pi,2\pi)$.",
            r"**מסקנה:** **נכון** — אך שימו לב שהשטח ה*כולל* הוא $4$, לא $0$."]),
    ]
    return items


def gen_sequences_5pt(meta):
    c = "sequences_5pt"
    items = [
        num(c, meta, "easy",
            "An arithmetic sequence has $a_1 = 7$ and common difference $d = 4$. Find $a_{12}$.",
            "בסדרה חשבונית $a_1 = 7$ וההפרש $d = 4$. מצאו את $a_{12}$.",
            "7+11*4", ["arithmetic_sequence"],
            ["**Formula.** $a_n = a_1 + (n-1)d$.",
             "**Substitute.** $a_{12} = 7 + 11\\cdot 4 = 7 + 44 = 51$.",
             "**Answer:** $51$."],
            ["**נוסחה.** $a_n = a_1 + (n-1)d$.",
             "**הצבה.** $a_{12} = 7 + 11\\cdot 4 = 51$.",
             "**תשובה:** $51$."]),
        num(c, meta, "medium",
            "A geometric sequence has $a_1 = 5$ and ratio $r = 3$. Find $a_5$.",
            "בסדרה הנדסית $a_1 = 5$ והמנה $r = 3$. מצאו את $a_5$.",
            "5*3**4", ["geometric_sequence"],
            ["**Formula.** $a_n = a_1 r^{\\,n-1}$.",
             "**Substitute.** $a_5 = 5\\cdot 3^4 = 5\\cdot 81 = 405$.",
             "**Answer:** $405$."],
            ["**נוסחה.** $a_n = a_1 r^{\\,n-1}$.",
             "**הצבה.** $a_5 = 5\\cdot 3^4 = 405$.",
             "**תשובה:** $405$."]),
        num(c, meta, "medium",
            "Find the sum of the first $10$ terms of an arithmetic sequence with $a_1 = 3$, $d = 4$.",
            "מצאו את סכום 10 האיברים הראשונים בסדרה חשבונית עם $a_1 = 3$, $d = 4$.",
            "10*(2*3+9*4)/2", ["sequence_sum", "arithmetic_sequence"],
            ["**Formula.** $S_n = \\tfrac{n}{2}\\big(2a_1 + (n-1)d\\big)$.",
             "**Substitute.** $S_{10} = 5\\,(6 + 36) = 5\\cdot 42 = 210$.",
             "**Answer:** $210$."],
            ["**נוסחה.** $S_n = \\tfrac{n}{2}\\big(2a_1 + (n-1)d\\big)$.",
             "**הצבה.** $S_{10} = 5\\,(6 + 36) = 210$.",
             "**תשובה:** $210$."]),
        num(c, meta, "hard",
            "The sum of an infinite geometric series is $\\dfrac{a_1}{1-r}$. Find it for $a_1 = 8$, $r = \\tfrac12$.",
            "סכום טור הנדסי אינסופי הוא $\\dfrac{a_1}{1-r}$. מצאו אותו עבור $a_1 = 8$, $r = \\tfrac12$.",
            "8/(1-1/2)", ["infinite_series", "geometric_sequence"],
            ["**Convergence.** $|r| = \\tfrac12 < 1$, so the series converges.",
             "**Substitute.** $S = \\dfrac{8}{1 - \\tfrac12} = \\dfrac{8}{\\tfrac12} = 16$.",
             "**Answer:** $16$."],
            ["**התכנסות.** $|r| = \\tfrac12 < 1$, ולכן הטור מתכנס.",
             "**הצבה.** $S = \\dfrac{8}{1 - \\tfrac12} = 16$.",
             "**תשובה:** $16$."]),
        mcq(c, meta, "medium",
            "Which sequence is geometric?",
            "איזו סדרה היא הנדסית?",
            ["2, 6, 18, 54", "2, 5, 8, 11", "1, 4, 9, 16", "3, 3, 3, 4"], 0,
            {"check": "truth", "predicate": "Eq(6/2, 18/6)", "claimed": "true"},
            ["geometric_sequence"],
            ["**Test the ratio.** $2, 6, 18, 54$: each term is $\\times 3$ of the previous ($6/2 = 18/6 = 3$).",
             "**Others.** $2,5,8,11$ is arithmetic; $1,4,9,16$ are squares; the last is neither.",
             "**Answer:** $2, 6, 18, 54$."],
            ["**בדיקת המנה.** $2, 6, 18, 54$: כל איבר גדול פי $3$ מקודמו ($6/2 = 18/6 = 3$).",
             "**האחרות.** $2,5,8,11$ חשבונית; $1,4,9,16$ ריבועים; האחרונה אף אחת.",
             "**תשובה:** $2, 6, 18, 54$."]),
        tf(c, meta, "easy",
           "True or False: the $6$th term of an arithmetic sequence with $a_1 = 3$, $d = 4$ is $23$.",
           "נכון או לא נכון: האיבר השישי בסדרה חשבונית עם $a_1 = 3$, $d = 4$ הוא $23$.",
           {"check": "truth", "predicate": "Eq(3+5*4, 23)", "claimed": "true"}, True, ["arithmetic_sequence"],
           ["**Compute.** $a_6 = a_1 + 5d = 3 + 20 = 23$.",
            "**Conclusion:** **true**."],
           ["**חישוב.** $a_6 = a_1 + 5d = 3 + 20 = 23$.",
            "**מסקנה:** **נכון**."]),
        num(c, meta, "easy",
            r"In an arithmetic sequence $a_1 = 5$, $d = 3$, which term $n$ equals $35$?",
            r"בסדרה חשבונית $a_1 = 5$, $d = 3$, איזה איבר $n$ שווה ל-$35$?",
            "(35-5)/3+1", ["arithmetic_sequence"],
            [r"**Formula.** $a_n = a_1 + (n-1)d = 35$.",
             r"**Solve.** $5 + 3(n-1) = 35 \Rightarrow 3(n-1) = 30 \Rightarrow n - 1 = 10 \Rightarrow n = 11$.",
             r"**Answer:** $n = 11$."],
            [r"**נוסחה.** $a_n = a_1 + (n-1)d = 35$.",
             r"**פתרון.** $5 + 3(n-1) = 35 \Rightarrow n - 1 = 10 \Rightarrow n = 11$.",
             r"**תשובה:** $n = 11$."]),
        num(c, meta, "medium",
            r"Find the sum of the first $6$ terms of a geometric sequence with $a_1 = 2$, $r = 3$.",
            r"מצאו את סכום 6 האיברים הראשונים בסדרה הנדסית עם $a_1 = 2$, $r = 3$.",
            "2*(3**6-1)/(3-1)", ["geometric_sum", "geometric_sequence"],
            [r"**Formula.** $S_n = a_1\dfrac{r^n - 1}{r - 1}$.",
             r"**Substitute.** $S_6 = 2\cdot\dfrac{3^6 - 1}{3 - 1} = 2\cdot\dfrac{728}{2} = 728$.",
             r"**Answer:** $728$."],
            [r"**נוסחה.** $S_n = a_1\dfrac{r^n - 1}{r - 1}$.",
             r"**הצבה.** $S_6 = 2\cdot\dfrac{729 - 1}{2} = 728$.",
             r"**תשובה:** $728$."]),
        num(c, meta, "hard",
            r"Find the sum of the infinite geometric series with $a_1 = 9$, $r = -\tfrac{1}{3}$.",
            r"מצאו את סכום הטור ההנדסי האינסופי עם $a_1 = 9$, $r = -\tfrac{1}{3}$.",
            "9/(1-(-1/3))", ["infinite_series", "geometric_sequence"],
            [r"**Convergence.** $|r| = \tfrac13 < 1$, so the series converges.",
             r"**Substitute.** $S = \dfrac{a_1}{1 - r} = \dfrac{9}{1 - (-\tfrac13)} = \dfrac{9}{\tfrac43} = \tfrac{27}{4}$.",
             r"**Answer:** $\tfrac{27}{4} = 6.75$."],
            [r"**התכנסות.** $|r| = \tfrac13 < 1$, ולכן הטור מתכנס.",
             r"**הצבה.** $S = \dfrac{9}{1 - (-\tfrac13)} = \dfrac{9}{\tfrac43} = \tfrac{27}{4}$.",
             r"**תשובה:** $\tfrac{27}{4} = 6.75$."]),
        open_worked(c, meta, "hard",
            r"The 3rd term of a geometric sequence is $12$ and the 6th term is $96$. Find $a_1$ and $r$.",
            r"האיבר השלישי בסדרה הנדסית הוא $12$ והאיבר השישי הוא $96$. מצאו את $a_1$ ואת $r$.",
            [r"**Step 1 — Divide the terms.** $\dfrac{a_6}{a_3} = \dfrac{a_1 r^5}{a_1 r^2} = r^3 = \dfrac{96}{12} = 8$.",
             r"**Step 2 — Solve for $r$.** $r^3 = 8 \Rightarrow r = 2$.",
             r"**Step 3 — Back-substitute.** $a_3 = a_1 r^2 = 4a_1 = 12 \Rightarrow a_1 = 3$.",
             r"**Answer:** $a_1 = 3$, $r = 2$."],
            [r"**שלב 1 — חלוקת האיברים.** $\dfrac{a_6}{a_3} = r^3 = \dfrac{96}{12} = 8$.",
             r"**שלב 2 — פתרון עבור $r$.** $r^3 = 8 \Rightarrow r = 2$.",
             r"**שלב 3 — הצבה חוזרת.** $a_3 = 4a_1 = 12 \Rightarrow a_1 = 3$.",
             r"**תשובה:** $a_1 = 3$, $r = 2$."],
            ["geometric_sequence"],
            {"check": "truth", "predicate": "Eq(3*2**5, 96)", "claimed": "true"}),
        tf(c, meta, "medium",
           r"True or False: the sequence $a_n = 2n + 1$ is arithmetic with common difference $2$.",
           r"נכון או לא נכון: הסדרה $a_n = 2n + 1$ היא חשבונית עם הפרש $2$.",
           {"check": "truth", "predicate": "Eq((2*3+1)-(2*2+1), 2)", "claimed": "true"}, True,
           ["arithmetic_sequence"],
           [r"**Test the difference.** $a_{n+1} - a_n = [2(n+1)+1] - [2n+1] = 2$ for all $n$.",
            r"**Conclusion:** constant difference $2$ $\Rightarrow$ arithmetic — **true**."],
           [r"**בדיקת ההפרש.** $a_{n+1} - a_n = 2$ לכל $n$.",
            r"**מסקנה:** הפרש קבוע $2$ $\Rightarrow$ חשבונית — **נכון**."]),
    ]
    return items


def gen_exponential_logarithmic(meta):
    c = "exponential_logarithmic"
    items = [
        num(c, meta, "easy", "Evaluate $\\log_2 32$.", "חשבו את $\\log_2 32$.",
            "log(32,2)", ["log_evaluation"],
            ["**Ask:** $2$ to what power is $32$?",
             "**Answer:** $2^5 = 32$, so $\\log_2 32 = 5$."],
            ["**שאלה:** $2$ בחזקת כמה שווה $32$?",
             "**תשובה:** $2^5 = 32$, ולכן $\\log_2 32 = 5$."]),
        num(c, meta, "medium", "Evaluate $\\ln(e^7)$.", "חשבו את $\\ln(e^7)$.",
            "log(exp(7))", ["log_rules"],
            ["**Rule.** $\\ln(e^k) = k$ because $\\ln$ and $e^x$ are inverses.",
             "**Answer:** $7$."],
            ["**כלל.** $\\ln(e^k) = k$ כי $\\ln$ ו-$e^x$ הפוכות זו לזו.",
             "**תשובה:** $7$."]),
        num(c, meta, "medium",
            "Solve $3^{x} = 81$.",
            "פתרו את $3^{x} = 81$.",
            "log(81,3)", ["exp_equation"],
            ["**Step 1 — Same base.** $81 = 3^4$.",
             "**Step 2 — Equate exponents.** $3^x = 3^4 \\Rightarrow x = 4$.",
             "**Answer:** $x = 4$."],
            ["**שלב 1 — בסיס משותף.** $81 = 3^4$.",
             "**שלב 2 — השוואת מעריכים.** $3^x = 3^4 \\Rightarrow x = 4$.",
             "**תשובה:** $x = 4$."]),
        num(c, meta, "hard",
            "Solve $\\log_2(x) + \\log_2(x-2) = 3$ (take the valid root).",
            "פתרו את $\\log_2(x) + \\log_2(x-2) = 3$ (קחו את השורש התקף).",
            "4", ["log_rules", "exp_equation"],
            ["**Step 1 — Combine logs.** $\\log_2\\big(x(x-2)\\big) = 3$.",
             "**Step 2 — Exponentiate.** $x(x-2) = 2^3 = 8 \\Rightarrow x^2 - 2x - 8 = 0$.",
             "**Step 3 — Factor.** $(x-4)(x+2) = 0 \\Rightarrow x = 4$ or $x = -2$.",
             "**Step 4 — Domain check.** $\\log$ needs $x > 2$, so reject $x = -2$.",
             "**Answer:** $x = 4$."],
            ["**שלב 1 — איחוד לוגריתמים.** $\\log_2\\big(x(x-2)\\big) = 3$.",
             "**שלב 2 — העלאה בחזקה.** $x(x-2) = 2^3 = 8 \\Rightarrow x^2 - 2x - 8 = 0$.",
             "**שלב 3 — פירוק.** $(x-4)(x+2) = 0 \\Rightarrow x = 4$ או $x = -2$.",
             "**שלב 4 — בדיקת תחום.** הלוגריתם דורש $x > 2$, ולכן פוסלים $x = -2$.",
             "**תשובה:** $x = 4$."]),
        mcq(c, meta, "medium",
            "Which equals $\\log(a) + \\log(b)$?",
            "למה שווה $\\log(a) + \\log(b)$?",
            ["\\log(ab)", "\\log(a+b)", "\\log(a)\\log(b)", "\\log(a/b)"], 0,
            {"check": "truth", "predicate": "Eq(log(6)+log(5), log(30))", "claimed": "true"},
            ["log_rules"],
            ["**Product rule for logs.** $\\log a + \\log b = \\log(ab)$.",
             "**Check.** $\\log 6 + \\log 5 = \\log 30$. ✓"],
            ["**כלל המכפלה ללוגריתמים.** $\\log a + \\log b = \\log(ab)$.",
             "**בדיקה.** $\\log 6 + \\log 5 = \\log 30$. ✓"]),
        tf(c, meta, "easy",
           "True or False: $\\log_5 25 = 2$.",
           "נכון או לא נכון: $\\log_5 25 = 2$.",
           {"check": "truth", "predicate": "Eq(log(25,5), 2)", "claimed": "true"}, True, ["log_evaluation"],
           ["**Reason.** $5^2 = 25$, so $\\log_5 25 = 2$.",
            "**Conclusion:** **true**."],
           ["**נימוק.** $5^2 = 25$, ולכן $\\log_5 25 = 2$.",
            "**מסקנה:** **נכון**."]),
        num(c, meta, "easy",
            r"Solve $2^{x} = \tfrac{1}{8}$.",
            r"פתרו את $2^{x} = \tfrac{1}{8}$.",
            "log(1/8,2)", ["exp_equation"],
            [r"**Step 1 — Same base.** $\tfrac{1}{8} = 2^{-3}$.",
             r"**Step 2 — Equate exponents.** $2^x = 2^{-3} \Rightarrow x = -3$.",
             r"**Answer:** $x = -3$."],
            [r"**שלב 1 — בסיס משותף.** $\tfrac{1}{8} = 2^{-3}$.",
             r"**שלב 2 — השוואת מעריכים.** $2^x = 2^{-3} \Rightarrow x = -3$.",
             r"**תשובה:** $x = -3$."]),
        num(c, meta, "medium",
            r"Evaluate $\log_3 81 - \log_3 3$.",
            r"חשבו את $\log_3 81 - \log_3 3$.",
            "log(81,3)-log(3,3)", ["log_rules", "log_evaluation"],
            [r"**Step 1 — Evaluate each log.** $\log_3 81 = 4$ (since $3^4 = 81$) and $\log_3 3 = 1$.",
             r"**Step 2 — Subtract.** $4 - 1 = 3$.",
             r"**Alternative — quotient rule.** $\log_3\tfrac{81}{3} = \log_3 27 = 3$.",
             r"**Answer:** $3$."],
            [r"**שלב 1 — חישוב כל לוגריתם.** $\log_3 81 = 4$ (כי $3^4 = 81$) ו-$\log_3 3 = 1$.",
             r"**שלב 2 — חיסור.** $4 - 1 = 3$.",
             r"**דרך חלופית — כלל המנה.** $\log_3\tfrac{81}{3} = \log_3 27 = 3$.",
             r"**תשובה:** $3$."]),
        num(c, meta, "hard",
            r"Solve $2^{2x} - 5\cdot 2^{x} + 4 = 0$ and give the larger root.",
            r"פתרו את $2^{2x} - 5\cdot 2^{x} + 4 = 0$ ותנו את השורש הגדול.",
            "log(4,2)", ["exp_equation", "factoring"],
            [r"**Step 1 — Substitute $y = 2^x$.** The equation becomes $y^2 - 5y + 4 = 0$.",
             r"**Step 2 — Factor.** $(y - 1)(y - 4) = 0 \Rightarrow y = 1$ or $y = 4$.",
             r"**Step 3 — Back-substitute.** $2^x = 1 \Rightarrow x = 0$; $2^x = 4 \Rightarrow x = 2$.",
             r"**Answer:** the larger root is $x = 2$."],
            [r"**שלב 1 — הצבה $y = 2^x$.** המשוואה הופכת ל-$y^2 - 5y + 4 = 0$.",
             r"**שלב 2 — פירוק.** $(y - 1)(y - 4) = 0 \Rightarrow y = 1$ או $y = 4$.",
             r"**שלב 3 — הצבה חוזרת.** $2^x = 1 \Rightarrow x = 0$; $2^x = 4 \Rightarrow x = 2$.",
             r"**תשובה:** השורש הגדול הוא $x = 2$."]),
        open_worked(c, meta, "hard",
            r"Solve $4^{x} = 8^{x - 1}$.",
            r"פתרו את $4^{x} = 8^{x - 1}$.",
            [r"**Step 1 — Common base $2$.** $4 = 2^2$, $8 = 2^3$, so $2^{2x} = 2^{3(x-1)}$.",
             r"**Step 2 — Equate exponents.** $2x = 3(x - 1) = 3x - 3$.",
             r"**Step 3 — Solve.** $-x = -3 \Rightarrow x = 3$.",
             r"**Check.** $4^3 = 64$ and $8^{2} = 64$. ✓",
             r"**Answer:** $x = 3$."],
            [r"**שלב 1 — בסיס משותף $2$.** $4 = 2^2$, $8 = 2^3$, ולכן $2^{2x} = 2^{3(x-1)}$.",
             r"**שלב 2 — השוואת מעריכים.** $2x = 3x - 3$.",
             r"**שלב 3 — פתרון.** $x = 3$.",
             r"**בדיקה.** $4^3 = 64$ וגם $8^{2} = 64$. ✓",
             r"**תשובה:** $x = 3$."],
            ["exp_equation"],
            {"check": "truth", "predicate": "Eq(4**3, 8**(3-1))", "claimed": "true"}),
        tf(c, meta, "medium",
           r"True or False: $\ln(ab) = \ln a + \ln b$ for all $a, b > 0$.",
           r"נכון או לא נכון: $\ln(ab) = \ln a + \ln b$ לכל $a, b > 0$.",
           {"check": "truth", "predicate": "Eq(log(2*3), log(2)+log(3))", "claimed": "true"}, True,
           ["log_rules"],
           [r"**Product rule for logarithms.** The log of a product is the sum of the logs.",
            r"**Check.** $\ln 6 = \ln 2 + \ln 3$. ✓ — **true**."],
           [r"**כלל המכפלה ללוגריתמים.** לוגריתם של מכפלה הוא סכום הלוגריתמים.",
            r"**בדיקה.** $\ln 6 = \ln 2 + \ln 3$. ✓ — **נכון**."]),
    ]
    return items


def gen_complex_numbers_5pt(meta):
    c = "complex_numbers_5pt"
    items = [
        num(c, meta, "easy", "Compute the modulus $|5 - 12i|$.", "חשבו את הערך המוחלט $|5 - 12i|$.",
            "Abs(5-12*I)", ["complex_modulus"],
            ["**Formula.** $|a + bi| = \\sqrt{a^2 + b^2}$.",
             "**Compute.** $\\sqrt{25 + 144} = \\sqrt{169} = 13$.",
             "**Answer:** $13$."],
            ["**נוסחה.** $|a + bi| = \\sqrt{a^2 + b^2}$.",
             "**חישוב.** $\\sqrt{25 + 144} = \\sqrt{169} = 13$.",
             "**תשובה:** $13$."]),
        num(c, meta, "medium",
            "Compute the real part of $(2 + 3i)(4 - i)$.",
            "חשבו את החלק הממשי של $(2 + 3i)(4 - i)$.",
            "re((2+3*I)*(4-I))", ["complex_arithmetic"],
            ["**Step 1 — Expand.** $(2+3i)(4-i) = 8 - 2i + 12i - 3i^2$.",
             "**Step 2 — Use $i^2 = -1$.** $= 8 + 10i + 3 = 11 + 10i$.",
             "**Answer:** real part $= 11$."],
            ["**שלב 1 — פתיחת סוגריים.** $(2+3i)(4-i) = 8 - 2i + 12i - 3i^2$.",
             "**שלב 2 — שימוש ב-$i^2 = -1$.** $= 11 + 10i$.",
             "**תשובה:** החלק הממשי $= 11$."]),
        num(c, meta, "medium",
            "Compute the imaginary part of $\\dfrac{1}{2 + i}$ times $5$ (i.e. $5\\,\\mathrm{Im}\\tfrac{1}{2+i}$).",
            "חשבו את $5$ כפול החלק המדומה של $\\dfrac{1}{2 + i}$ (כלומר $5\\,\\mathrm{Im}\\tfrac{1}{2+i}$).",
            "5*im(1/(2+I))", ["complex_arithmetic"],
            ["**Step 1 — Multiply by the conjugate.** $\\frac{1}{2+i}\\cdot\\frac{2-i}{2-i} = \\frac{2-i}{5}$.",
             "**Step 2 — Imaginary part.** $\\mathrm{Im} = -\\tfrac{1}{5}$, so $5\\cdot(-\\tfrac15) = -1$.",
             "**Answer:** $-1$."],
            ["**שלב 1 — הכפלה בצמוד.** $\\frac{1}{2+i}\\cdot\\frac{2-i}{2-i} = \\frac{2-i}{5}$.",
             "**שלב 2 — חלק מדומה.** $\\mathrm{Im} = -\\tfrac{1}{5}$, ולכן $5\\cdot(-\\tfrac15) = -1$.",
             "**תשובה:** $-1$."]),
        mcq(c, meta, "medium",
            "What is the conjugate of $3 - 7i$?",
            "מהו הצמוד של $3 - 7i$?",
            ["3+7i", "-3+7i", "3-7i", "-3-7i"], 0,
            {"check": "truth", "predicate": "Eq(conjugate(3-7*I), 3+7*I)", "claimed": "true"},
            ["complex_conjugate"],
            ["**Rule.** The conjugate flips the sign of the imaginary part: $\\overline{a+bi} = a - bi$.",
             "**Answer:** $3 + 7i$."],
            ["**כלל.** הצמוד הופך את סימן החלק המדומה: $\\overline{a+bi} = a - bi$.",
             "**תשובה:** $3 + 7i$."]),
        tf(c, meta, "hard",
           "True or False: $(1 + i)^2 = 2i$.",
           "נכון או לא נכון: $(1 + i)^2 = 2i$.",
           {"check": "truth", "predicate": "Eq((1+I)**2, 2*I)", "claimed": "true"}, True, ["complex_arithmetic"],
           ["**Step 1 — Expand.** $(1+i)^2 = 1 + 2i + i^2$.",
            "**Step 2 — $i^2 = -1$.** $= 1 + 2i - 1 = 2i$.",
            "**Conclusion:** **true**."],
           ["**שלב 1 — פתיחה.** $(1+i)^2 = 1 + 2i + i^2$.",
            "**שלב 2 — $i^2 = -1$.** $= 2i$.",
            "**מסקנה:** **נכון**."]),
        num(c, meta, "easy",
            r"Compute the real part of $(3 + 4i) + (1 - 2i)$.",
            r"חשבו את החלק הממשי של $(3 + 4i) + (1 - 2i)$.",
            "re((3+4*I)+(1-2*I))", ["complex_arithmetic"],
            [r"**Step 1 — Add real and imaginary parts separately.** $(3 + 1) + (4 - 2)i = 4 + 2i$.",
             r"**Step 2 — Real part.** $\mathrm{Re} = 4$.",
             r"**Answer:** $4$."],
            [r"**שלב 1 — חיבור חלקים ממשי ומדומה בנפרד.** $(3 + 1) + (4 - 2)i = 4 + 2i$.",
             r"**שלב 2 — חלק ממשי.** $\mathrm{Re} = 4$.",
             r"**תשובה:** $4$."]),
        num(c, meta, "medium",
            r"Compute the modulus $|3 + 4i|$.",
            r"חשבו את הערך המוחלט $|3 + 4i|$.",
            "Abs(3+4*I)", ["complex_modulus"],
            [r"**Formula.** $|a + bi| = \sqrt{a^2 + b^2}$.",
             r"**Compute.** $\sqrt{9 + 16} = \sqrt{25} = 5$.",
             r"**Answer:** $5$."],
            [r"**נוסחה.** $|a + bi| = \sqrt{a^2 + b^2}$.",
             r"**חישוב.** $\sqrt{9 + 16} = \sqrt{25} = 5$.",
             r"**תשובה:** $5$."]),
        num(c, meta, "medium",
            r"Compute the imaginary part of $(2 + 3i)(4 - i)$.",
            r"חשבו את החלק המדומה של $(2 + 3i)(4 - i)$.",
            "im((2+3*I)*(4-I))", ["complex_arithmetic"],
            [r"**Step 1 — Expand.** $(2+3i)(4-i) = 8 - 2i + 12i - 3i^2$.",
             r"**Step 2 — Use $i^2 = -1$.** $= 8 + 10i + 3 = 11 + 10i$.",
             r"**Answer:** imaginary part $= 10$."],
            [r"**שלב 1 — פתיחת סוגריים.** $(2+3i)(4-i) = 8 - 2i + 12i - 3i^2$.",
             r"**שלב 2 — שימוש ב-$i^2 = -1$.** $= 11 + 10i$.",
             r"**תשובה:** החלק המדומה $= 10$."]),
        mcq(c, meta, "medium",
            r"What is $i^{2026}$?",
            r"מהו $i^{2026}$?",
            ["-1", "1", "i", "-i"], 0,
            {"check": "truth", "predicate": "Eq(I**2026, -1)", "claimed": "true"},
            ["complex_powers"],
            [r"**Powers of $i$ cycle every 4:** $i, -1, -i, 1$.",
             r"**Reduce the exponent mod 4.** $2026 = 4\cdot 506 + 2$, so $i^{2026} = i^2 = -1$.",
             r"**Answer:** $-1$."],
            [r"**חזקות $i$ מחזוריות כל 4:** $i, -1, -i, 1$.",
             r"**מצמצמים את המעריך מודולו 4.** $2026 = 4\cdot 506 + 2$, ולכן $i^{2026} = i^2 = -1$.",
             r"**תשובה:** $-1$."]),
        open_worked(c, meta, "hard",
            r"Solve $z^2 = -9$ for complex $z$.",
            r"פתרו את $z^2 = -9$ עבור $z$ מרוכב.",
            [r"**Step 1 — Write $z = a + bi$ or use roots of a negative.** $z^2 = -9 = 9i^2$.",
             r"**Step 2 — Take square roots.** $z = \pm\sqrt{9}\,i = \pm 3i$.",
             r"**Step 3 — Check.** $(3i)^2 = 9i^2 = -9$. ✓",
             r"**Answer:** $z = 3i$ or $z = -3i$."],
            [r"**שלב 1 — כותבים $z^2 = -9 = 9i^2$.**",
             r"**שלב 2 — מוציאים שורש.** $z = \pm 3i$.",
             r"**שלב 3 — בדיקה.** $(3i)^2 = 9i^2 = -9$. ✓",
             r"**תשובה:** $z = 3i$ או $z = -3i$."],
            ["complex_arithmetic"],
            {"check": "truth", "predicate": "Eq((3*I)**2, -9)", "claimed": "true"}),
        tf(c, meta, "medium",
           r"True or False: $|z_1 z_2| = |z_1|\,|z_2|$ (illustrated with $z_1 = 1 + i$, $z_2 = 2 - i$).",
           r"נכון או לא נכון: $|z_1 z_2| = |z_1|\,|z_2|$ (בדוגמה $z_1 = 1 + i$, $z_2 = 2 - i$).",
           {"check": "truth", "predicate": "Eq(Abs((1+I)*(2-I)), Abs(1+I)*Abs(2-I))", "claimed": "true"},
           True, ["complex_modulus"],
           [r"**Property.** The modulus is multiplicative: the modulus of a product is the product of the moduli.",
            r"**Check.** $|1+i| = \sqrt2$, $|2-i| = \sqrt5$; $(1+i)(2-i) = 3 + i$ with $|3+i| = \sqrt{10} = \sqrt2\cdot\sqrt5$. ✓ — **true**."],
           [r"**תכונה.** הערך המוחלט כפלי: הערך המוחלט של מכפלה הוא מכפלת הערכים המוחלטים.",
            r"**בדיקה.** $|1+i| = \sqrt2$, $|2-i| = \sqrt5$; $(1+i)(2-i) = 3 + i$ עם $|3+i| = \sqrt{10}$. ✓ — **נכון**."]),
    ]
    return items


def gen_analytic_geometry_5pt(meta):
    c = "analytic_geometry_5pt"
    items = [
        num(c, meta, "easy",
            "Find the distance between $(1, 2)$ and $(7, 10)$.",
            "מצאו את המרחק בין $(1, 2)$ ל-$(7, 10)$.",
            "sqrt((7-1)**2+(10-2)**2)", ["distance_formula"],
            ["**Formula.** $d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$.",
             "**Compute.** $\\sqrt{6^2 + 8^2} = \\sqrt{100} = 10$.",
             "**Answer:** $10$."],
            ["**נוסחה.** $d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$.",
             "**חישוב.** $\\sqrt{36 + 64} = \\sqrt{100} = 10$.",
             "**תשובה:** $10$."]),
        num(c, meta, "easy",
            "Find the slope of the line through $(2, 1)$ and $(6, 13)$.",
            "מצאו את שיפוע הישר העובר דרך $(2, 1)$ ו-$(6, 13)$.",
            "(13-1)/(6-2)", ["line_slope"],
            ["**Formula.** $m = \\dfrac{y_2 - y_1}{x_2 - x_1}$.",
             "**Compute.** $\\dfrac{12}{4} = 3$.",
             "**Answer:** $m = 3$."],
            ["**נוסחה.** $m = \\dfrac{y_2 - y_1}{x_2 - x_1}$.",
             "**חישוב.** $\\dfrac{12}{4} = 3$.",
             "**תשובה:** $m = 3$."]),
        mcq(c, meta, "medium",
            "The line perpendicular to $y = 2x + 1$ has slope:",
            "לישר המאונך ל-$y = 2x + 1$ יש שיפוע:",
            ["-\\frac{1}{2}", "2", "\\frac{1}{2}", "-2"], 0,
            {"check": "truth", "predicate": "Eq(-1/2*2, -1)", "claimed": "true"},
            ["perpendicular_slope", "line_slope"],
            ["**Rule.** Perpendicular slopes multiply to $-1$.",
             "**Compute.** If $m_1 = 2$ then $m_2 = -\\tfrac{1}{2}$ (since $2\\cdot(-\\tfrac12) = -1$).",
             "**Answer:** $-\\tfrac{1}{2}$."],
            ["**כלל.** מכפלת שיפועים מאונכים היא $-1$.",
             "**חישוב.** אם $m_1 = 2$ אז $m_2 = -\\tfrac{1}{2}$ (כי $2\\cdot(-\\tfrac12) = -1$).",
             "**תשובה:** $-\\tfrac{1}{2}$."]),
        num(c, meta, "medium",
            "The circle $(x-2)^2 + (y+1)^2 = 49$ has what radius?",
            "מהו הרדיוס של המעגל $(x-2)^2 + (y+1)^2 = 49$?",
            "sqrt(49)", ["circle_equation"],
            ["**Standard form.** $(x-h)^2 + (y-k)^2 = r^2$.",
             "**Read off.** $r^2 = 49 \\Rightarrow r = 7$.",
             "**Answer:** $7$ (centre $(2, -1)$)."],
            ["**צורה תקנית.** $(x-h)^2 + (y-k)^2 = r^2$.",
             "**קריאה.** $r^2 = 49 \\Rightarrow r = 7$.",
             "**תשובה:** $7$ (מרכז $(2, -1)$)."]),
        open_worked(c, meta, "hard",
            "Find the equation of the circle whose diameter has endpoints $(-1, 2)$ and $(5, 10)$.",
            "מצאו את משוואת המעגל שקוטרו בין הנקודות $(-1, 2)$ ל-$(5, 10)$.",
            ["**Step 1 — Centre = midpoint.** $\\left(\\tfrac{-1+5}{2}, \\tfrac{2+10}{2}\\right) = (2, 6)$.",
             "**Step 2 — Radius = half the diameter.** Diameter $= \\sqrt{6^2 + 8^2} = 10$, so $r = 5$.",
             "**Step 3 — Write the equation.** $(x-2)^2 + (y-6)^2 = 25$.",
             "**Answer:** $(x-2)^2 + (y-6)^2 = 25$."],
            ["**שלב 1 — מרכז = אמצע הקוטר.** $\\left(\\tfrac{-1+5}{2}, \\tfrac{2+10}{2}\\right) = (2, 6)$.",
             "**שלב 2 — רדיוס = חצי הקוטר.** קוטר $= \\sqrt{36 + 64} = 10$, ולכן $r = 5$.",
             "**שלב 3 — כתיבת המשוואה.** $(x-2)^2 + (y-6)^2 = 25$.",
             "**תשובה:** $(x-2)^2 + (y-6)^2 = 25$."],
            ["circle_equation", "distance_formula"],
            {"check": "truth", "predicate": "Eq(sqrt((5-(-1))**2+(10-2)**2)/2, 5)", "claimed": "true"}),
        tf(c, meta, "medium",
           "True or False: the points $(0,0)$, $(3,4)$ and $(6,8)$ are collinear.",
           "נכון או לא נכון: הנקודות $(0,0)$, $(3,4)$ ו-$(6,8)$ נמצאות על ישר אחד.",
           {"check": "truth", "predicate": "Eq((4-0)/(3-0), (8-0)/(6-0))", "claimed": "true"}, True,
           ["line_slope"],
           ["**Test.** Slope from $(0,0)$ to $(3,4)$ is $\\tfrac43$; from $(0,0)$ to $(6,8)$ is $\\tfrac{8}{6} = \\tfrac43$.",
            "**Conclusion:** equal slopes $\\Rightarrow$ collinear — **true**."],
           ["**בדיקה.** שיפוע מ-$(0,0)$ ל-$(3,4)$ הוא $\\tfrac43$; מ-$(0,0)$ ל-$(6,8)$ הוא $\\tfrac{8}{6} = \\tfrac43$.",
            "**מסקנה:** שיפועים שווים $\\Rightarrow$ על ישר אחד — **נכון**."]),
        num(c, meta, "easy",
            r"Find the $x$-coordinate of the midpoint of $(2, 3)$ and $(8, 11)$.",
            r"מצאו את שיעור ה-$x$ של אמצע הקטע בין $(2, 3)$ ל-$(8, 11)$.",
            "(2+8)/2", ["midpoint"],
            [r"**Formula.** midpoint $= \left(\tfrac{x_1+x_2}{2}, \tfrac{y_1+y_2}{2}\right)$.",
             r"**Compute the $x$-coordinate.** $\tfrac{2+8}{2} = 5$.",
             r"**Answer:** $5$."],
            [r"**נוסחה.** אמצע $= \left(\tfrac{x_1+x_2}{2}, \tfrac{y_1+y_2}{2}\right)$.",
             r"**חישוב שיעור ה-$x$.** $\tfrac{2+8}{2} = 5$.",
             r"**תשובה:** $5$."]),
        mcq(c, meta, "medium",
            r"Which point lies on the circle $x^2 + y^2 = 25$?",
            r"איזו נקודה נמצאת על המעגל $x^2 + y^2 = 25$?",
            ["(3,4)", "(2,5)", "(1,1)", "(5,5)"], 0,
            {"check": "truth", "predicate": "Eq(3**2+4**2, 25)", "claimed": "true"},
            ["circle_equation"],
            [r"**Test each point in $x^2 + y^2$.** $(3,4)$: $9 + 16 = 25$. ✓",
             r"**Others.** $(2,5)\to 29$, $(1,1)\to 2$, $(5,5)\to 50$ — none equal $25$.",
             r"**Answer:** $(3, 4)$."],
            [r"**מציבים כל נקודה ב-$x^2 + y^2$.** $(3,4)$: $9 + 16 = 25$. ✓",
             r"**האחרות.** $(2,5)\to 29$, $(1,1)\to 2$, $(5,5)\to 50$ — אף אחת אינה $25$.",
             r"**תשובה:** $(3, 4)$."]),
        num(c, meta, "medium",
            r"The circle $x^2 + y^2 - 6x + 4y - 12 = 0$ has what radius?",
            r"מהו הרדיוס של המעגל $x^2 + y^2 - 6x + 4y - 12 = 0$?",
            "sqrt(25)", ["circle_equation"],
            [r"**Step 1 — Complete the square.** $(x^2 - 6x) + (y^2 + 4y) = 12$.",
             r"**Step 2 — Add the squares.** $(x-3)^2 - 9 + (y+2)^2 - 4 = 12 \Rightarrow (x-3)^2 + (y+2)^2 = 25$.",
             r"**Step 3 — Read off.** $r^2 = 25 \Rightarrow r = 5$ (centre $(3, -2)$).",
             r"**Answer:** $5$."],
            [r"**שלב 1 — השלמה לריבוע.** $(x^2 - 6x) + (y^2 + 4y) = 12$.",
             r"**שלב 2 — מוסיפים את הריבועים.** $(x-3)^2 + (y+2)^2 = 25$.",
             r"**שלב 3 — קריאה.** $r^2 = 25 \Rightarrow r = 5$ (מרכז $(3, -2)$).",
             r"**תשובה:** $5$."]),
        open_worked(c, meta, "hard",
            r"Find the equation of the line through $(1, 2)$ that is perpendicular to $y = 3x - 1$.",
            r"מצאו את משוואת הישר העובר דרך $(1, 2)$ המאונך ל-$y = 3x - 1$.",
            [r"**Step 1 — Perpendicular slope.** The given slope is $3$, so the perpendicular slope is $-\tfrac13$.",
             r"**Step 2 — Point-slope form.** $y - 2 = -\tfrac13 (x - 1)$.",
             r"**Step 3 — Simplify.** $y = -\tfrac13 x + \tfrac13 + 2 = -\tfrac13 x + \tfrac73$.",
             r"**Answer:** $y = -\tfrac13 x + \tfrac73$."],
            [r"**שלב 1 — שיפוע מאונך.** השיפוע הנתון הוא $3$, ולכן השיפוע המאונך הוא $-\tfrac13$.",
             r"**שלב 2 — צורת נקודה-שיפוע.** $y - 2 = -\tfrac13 (x - 1)$.",
             r"**שלב 3 — פישוט.** $y = -\tfrac13 x + \tfrac73$.",
             r"**תשובה:** $y = -\tfrac13 x + \tfrac73$."],
            ["perpendicular_slope", "line_slope"],
            {"check": "truth", "predicate": "Eq(-1/3*3, -1)", "claimed": "true"}),
        tf(c, meta, "medium",
           r"True or False: the distance between $(0, 0)$ and $(5, 12)$ is $13$.",
           r"נכון או לא נכון: המרחק בין $(0, 0)$ ל-$(5, 12)$ הוא $13$.",
           {"check": "truth", "predicate": "Eq(sqrt(5**2+12**2), 13)", "claimed": "true"}, True,
           ["distance_formula"],
           [r"**Compute.** $d = \sqrt{5^2 + 12^2} = \sqrt{25 + 144} = \sqrt{169} = 13$.",
            r"**Conclusion:** **true** ($5$-$12$-$13$ is a Pythagorean triple)."],
           [r"**חישוב.** $d = \sqrt{5^2 + 12^2} = \sqrt{169} = 13$.",
            r"**מסקנה:** **נכון** ($5$-$12$-$13$ שלשה פיתגורית)."]),
    ]
    return items


def gen_trigonometric_equations(meta):
    c = "trigonometric_equations"
    items = [
        num(c, meta, "easy", "Evaluate $\\tan\\!\\big(\\tfrac{\\pi}{3}\\big)$.", "חשבו את $\\tan\\!\\big(\\tfrac{\\pi}{3}\\big)$.",
            "tan(pi/3)", ["trig_values"],
            ["**Recall.** $\\tan\\theta = \\dfrac{\\sin\\theta}{\\cos\\theta}$; at $\\tfrac{\\pi}{3}$, $\\sin = \\tfrac{\\sqrt3}{2}$, $\\cos = \\tfrac12$.",
             "**Compute.** $\\tan\\tfrac{\\pi}{3} = \\sqrt3 \\approx 1.732$.",
             "**Answer:** $\\sqrt3$."],
            ["**תזכורת.** $\\tan\\theta = \\dfrac{\\sin\\theta}{\\cos\\theta}$; ב-$\\tfrac{\\pi}{3}$, $\\sin = \\tfrac{\\sqrt3}{2}$, $\\cos = \\tfrac12$.",
             "**חישוב.** $\\tan\\tfrac{\\pi}{3} = \\sqrt3 \\approx 1.732$.",
             "**תשובה:** $\\sqrt3$."]),
        short(c, meta, "medium",
              "Find the smallest positive solution of $\\sin x = \\tfrac{1}{2}$ (in radians).",
              "מצאו את הפתרון החיובי הקטן ביותר של $\\sin x = \\tfrac{1}{2}$ (ברדיאנים).",
              ["pi/6", "0.5236", "pi/6 rad"], ["trig_equation_solution"],
              ["**Step 1 — Reference angle.** $\\sin x = \\tfrac12$ at $x = \\tfrac{\\pi}{6}$ in the first quadrant.",
               "**Step 2 — Smallest positive.** $\\tfrac{\\pi}{6} \\approx 0.524$ is the smallest positive solution.",
               "**Answer:** $x = \\tfrac{\\pi}{6}$."],
              ["**שלב 1 — זווית ייחוס.** $\\sin x = \\tfrac12$ ב-$x = \\tfrac{\\pi}{6}$ ברביע הראשון.",
               "**שלב 2 — הקטן החיובי.** $\\tfrac{\\pi}{6} \\approx 0.524$ הוא הפתרון החיובי הקטן ביותר.",
               "**תשובה:** $x = \\tfrac{\\pi}{6}$."],
              verify={"check": "expr_value", "of": "sin(x)", "var": "x", "at": "pi/6", "claimed": "1/2"}),
        mcq(c, meta, "medium",
            "Which is a solution of $\\cos x = 0$?",
            "איזה הוא פתרון של $\\cos x = 0$?",
            ["\\frac{\\pi}{2}", "0", "\\pi", "\\frac{\\pi}{3}"], 0,
            {"check": "expr_value", "of": "cos(x)", "var": "x", "at": "pi/2", "claimed": "0"},
            ["trig_equation_solution"],
            ["**Where is cosine zero?** On the unit circle, $\\cos x = 0$ at $x = \\tfrac{\\pi}{2}$ (and odd multiples).",
             "**Answer:** $\\tfrac{\\pi}{2}$."],
            ["**היכן קוסינוס מתאפס?** על מעגל היחידה, $\\cos x = 0$ ב-$x = \\tfrac{\\pi}{2}$ (וכפולות אי-זוגיות).",
             "**תשובה:** $\\tfrac{\\pi}{2}$."]),
        num(c, meta, "hard",
            "How many solutions does $\\sin x = \\tfrac{1}{2}$ have in $[0, 2\\pi)$?",
            "כמה פתרונות יש למשוואה $\\sin x = \\tfrac{1}{2}$ בתחום $[0, 2\\pi)$?",
            "2", ["trig_equation_solution"],
            ["**Step 1 — Two quadrants.** $\\sin$ is positive in quadrants I and II.",
             "**Step 2 — Solutions.** $x = \\tfrac{\\pi}{6}$ and $x = \\pi - \\tfrac{\\pi}{6} = \\tfrac{5\\pi}{6}$.",
             "**Answer:** $2$ solutions."],
            ["**שלב 1 — שני רביעים.** $\\sin$ חיובי ברביעים I ו-II.",
             "**שלב 2 — פתרונות.** $x = \\tfrac{\\pi}{6}$ וגם $x = \\pi - \\tfrac{\\pi}{6} = \\tfrac{5\\pi}{6}$.",
             "**תשובה:** $2$ פתרונות."]),
        tf(c, meta, "easy",
           "True or False: $x = \\tfrac{\\pi}{4}$ satisfies $\\tan x = 1$.",
           "נכון או לא נכון: $x = \\tfrac{\\pi}{4}$ מקיים $\\tan x = 1$.",
           {"check": "expr_value", "of": "tan(x)", "var": "x", "at": "pi/4", "claimed": "1"}, True, ["trig_values"],
           ["**Reason.** At $\\tfrac{\\pi}{4}$, $\\sin = \\cos = \\tfrac{\\sqrt2}{2}$, so $\\tan = 1$.",
            "**Conclusion:** **true**."],
           ["**נימוק.** ב-$\\tfrac{\\pi}{4}$, $\\sin = \\cos = \\tfrac{\\sqrt2}{2}$, ולכן $\\tan = 1$.",
            "**מסקנה:** **נכון**."]),
        tf(c, meta, "medium",
           "True or False: $\\cos^2 x + \\sin^2 x = 1$ for every $x$.",
           "נכון או לא נכון: $\\cos^2 x + \\sin^2 x = 1$ לכל $x$.",
           {"check": "truth", "predicate": "Eq(cos(1)**2+sin(1)**2, 1)", "claimed": "true"}, True,
           ["trig_identity"],
           ["**Pythagorean identity.** For any angle, $\\sin^2 x + \\cos^2 x = 1$ — it comes from the unit circle.",
            "**Conclusion:** **true**."],
           ["**זהות פיתגורס.** לכל זווית, $\\sin^2 x + \\cos^2 x = 1$ — נובע ממעגל היחידה.",
            "**מסקנה:** **נכון**."]),
        num(c, meta, "easy",
            r"Evaluate $\sin\!\big(\tfrac{\pi}{6}\big)$.",
            r"חשבו את $\sin\!\big(\tfrac{\pi}{6}\big)$.",
            "sin(pi/6)", ["trig_values"],
            [r"**Recall the special angle.** $\sin\tfrac{\pi}{6} = \tfrac12$ (the $30^\circ$ value).",
             r"**Answer:** $\tfrac12$."],
            [r"**נזכרים בזווית מיוחדת.** $\sin\tfrac{\pi}{6} = \tfrac12$ (הערך של $30^\circ$).",
             r"**תשובה:** $\tfrac12$."]),
        mcq(c, meta, "medium",
            r"Which value in $\left[0, \tfrac{\pi}{2}\right]$ solves $2\sin x - 1 = 0$?",
            r"איזה ערך בקטע $\left[0, \tfrac{\pi}{2}\right]$ פותר את $2\sin x - 1 = 0$?",
            [r"\frac{\pi}{6}", r"\frac{\pi}{3}", r"\frac{\pi}{2}", r"\frac{\pi}{4}"], 0,
            {"check": "expr_value", "of": "2*sin(x)-1", "var": "x", "at": "pi/6", "claimed": "0"},
            ["trig_equation_solution"],
            [r"**Step 1 — Isolate.** $2\sin x - 1 = 0 \Rightarrow \sin x = \tfrac12$.",
             r"**Step 2 — First-quadrant solution.** $\sin x = \tfrac12$ at $x = \tfrac{\pi}{6}$.",
             r"**Answer:** $\tfrac{\pi}{6}$."],
            [r"**שלב 1 — בידוד.** $2\sin x - 1 = 0 \Rightarrow \sin x = \tfrac12$.",
             r"**שלב 2 — פתרון ברביע הראשון.** $\sin x = \tfrac12$ ב-$x = \tfrac{\pi}{6}$.",
             r"**תשובה:** $\tfrac{\pi}{6}$."]),
        num(c, meta, "hard",
            r"Find the smallest positive solution (radians) of $\tan x = \sqrt{3}$.",
            r"מצאו את הפתרון החיובי הקטן ביותר (ברדיאנים) של $\tan x = \sqrt{3}$.",
            "atan(sqrt(3))", ["trig_equation_solution"],
            [r"**Step 1 — Reference angle.** $\tan x = \sqrt3$ at $x = \tfrac{\pi}{3}$ (the $60^\circ$ value).",
             r"**Step 2 — Smallest positive.** $\tfrac{\pi}{3} \approx 1.047$ is the smallest positive solution.",
             r"**Answer:** $x = \tfrac{\pi}{3}$."],
            [r"**שלב 1 — זווית ייחוס.** $\tan x = \sqrt3$ ב-$x = \tfrac{\pi}{3}$ (הערך של $60^\circ$).",
             r"**שלב 2 — הקטן החיובי.** $\tfrac{\pi}{3} \approx 1.047$ הוא הפתרון החיובי הקטן ביותר.",
             r"**תשובה:** $x = \tfrac{\pi}{3}$."]),
        open_worked(c, meta, "hard",
            r"Solve $2\cos^2 x - \cos x - 1 = 0$ for $x \in [0, 2\pi)$.",
            r"פתרו את $2\cos^2 x - \cos x - 1 = 0$ עבור $x \in [0, 2\pi)$.",
            [r"**Step 1 — Substitute $c = \cos x$.** $2c^2 - c - 1 = 0$.",
             r"**Step 2 — Factor.** $(2c + 1)(c - 1) = 0 \Rightarrow c = -\tfrac12$ or $c = 1$.",
             r"**Step 3 — Solve $\cos x = 1$.** $x = 0$.",
             r"**Step 4 — Solve $\cos x = -\tfrac12$.** $x = \tfrac{2\pi}{3}$ and $x = \tfrac{4\pi}{3}$.",
             r"**Answer:** $x = 0,\ \tfrac{2\pi}{3},\ \tfrac{4\pi}{3}$."],
            [r"**שלב 1 — הצבה $c = \cos x$.** $2c^2 - c - 1 = 0$.",
             r"**שלב 2 — פירוק.** $(2c + 1)(c - 1) = 0 \Rightarrow c = -\tfrac12$ או $c = 1$.",
             r"**שלב 3 — פתרון $\cos x = 1$.** $x = 0$.",
             r"**שלב 4 — פתרון $\cos x = -\tfrac12$.** $x = \tfrac{2\pi}{3}$ ו-$x = \tfrac{4\pi}{3}$.",
             r"**תשובה:** $x = 0,\ \tfrac{2\pi}{3},\ \tfrac{4\pi}{3}$."],
            ["trig_equation_solution", "factoring"],
            {"check": "expr_value", "of": "2*cos(x)**2-cos(x)-1", "var": "x", "at": "2*pi/3", "claimed": "0"}),
        tf(c, meta, "medium",
           r"True or False: $\sin(\pi - x) = \sin x$ for every $x$.",
           r"נכון או לא נכון: $\sin(\pi - x) = \sin x$ לכל $x$.",
           {"check": "truth", "predicate": "Eq(sin(pi-1), sin(1))", "claimed": "true"}, True,
           ["trig_identity"],
           [r"**Supplementary-angle identity.** Reflecting across $\tfrac{\pi}{2}$ leaves the sine unchanged.",
            r"**Check.** $\sin(\pi - 1) = \sin 1$. ✓ — **true**."],
           [r"**זהות זוויות משלימות ל-$\pi$.** שיקוף סביב $\tfrac{\pi}{2}$ אינו משנה את הסינוס.",
            r"**בדיקה.** $\sin(\pi - 1) = \sin 1$. ✓ — **נכון**."]),
    ]
    return items


def gen_limits_5pt(meta):
    c = "limits_5pt"
    items = [
        num(c, meta, "easy",
            "Compute $\\lim_{x \\to 3} (x^2 - 2x + 1)$.",
            "חשבו את $\\lim_{x \\to 3} (x^2 - 2x + 1)$.",
            "3**2-2*3+1", ["limit_substitution"],
            ["**Continuity.** Polynomials are continuous, so substitute directly.",
             "**Compute.** $9 - 6 + 1 = 4$.",
             "**Answer:** $4$."],
            ["**רציפות.** פולינומים רציפים, ולכן מציבים ישירות.",
             "**חישוב.** $9 - 6 + 1 = 4$.",
             "**תשובה:** $4$."]),
        num(c, meta, "medium",
            "Compute $\\lim_{x \\to 2} \\dfrac{x^2 - 4}{x - 2}$.",
            "חשבו את $\\lim_{x \\to 2} \\dfrac{x^2 - 4}{x - 2}$.",
            "limit((x**2-4)/(x-2), x, 2)", ["limit_indeterminate", "factoring"],
            ["**Step 1 — $\\tfrac{0}{0}$ form.** Direct substitution gives $\\tfrac{0}{0}$, so factor first.",
             "**Step 2 — Factor and cancel.** $\\dfrac{(x-2)(x+2)}{x-2} = x + 2$.",
             "**Step 3 — Substitute.** $\\lim_{x\\to2}(x+2) = 4$.",
             "**Answer:** $4$."],
            ["**שלב 1 — צורת $\\tfrac{0}{0}$.** הצבה ישירה נותנת $\\tfrac{0}{0}$, ולכן מפרקים לגורמים.",
             "**שלב 2 — פירוק וצמצום.** $\\dfrac{(x-2)(x+2)}{x-2} = x + 2$.",
             "**שלב 3 — הצבה.** $\\lim_{x\\to2}(x+2) = 4$.",
             "**תשובה:** $4$."]),
        num(c, meta, "hard",
            "Compute $\\lim_{x \\to 0} \\dfrac{\\sin(3x)}{x}$.",
            "חשבו את $\\lim_{x \\to 0} \\dfrac{\\sin(3x)}{x}$.",
            "limit(sin(3*x)/x, x, 0)", ["special_limit"],
            ["**Step 1 — Use $\\lim_{u\\to0}\\tfrac{\\sin u}{u} = 1$.** Rewrite $\\dfrac{\\sin 3x}{x} = 3\\cdot\\dfrac{\\sin 3x}{3x}$.",
             "**Step 2 — As $x\\to0$, $3x\\to0$,** so $\\dfrac{\\sin 3x}{3x}\\to 1$.",
             "**Step 3 — Multiply.** $3\\cdot 1 = 3$.",
             "**Answer:** $3$."],
            ["**שלב 1 — שימוש ב-$\\lim_{u\\to0}\\tfrac{\\sin u}{u} = 1$.** כותבים $\\dfrac{\\sin 3x}{x} = 3\\cdot\\dfrac{\\sin 3x}{3x}$.",
             "**שלב 2 — כאשר $x\\to0$, גם $3x\\to0$,** ולכן $\\dfrac{\\sin 3x}{3x}\\to 1$.",
             "**שלב 3 — הכפלה.** $3\\cdot 1 = 3$.",
             "**תשובה:** $3$."]),
        mcq(c, meta, "medium",
            "What is $\\lim_{x \\to \\infty} \\dfrac{2x^2 + 1}{x^2 + 3}$?",
            "מהו $\\lim_{x \\to \\infty} \\dfrac{2x^2 + 1}{x^2 + 3}$?",
            ["2", "0", "\\infty", "1"], 0,
            {"check": "truth", "predicate": "Eq(limit((2*x**2+1)/(x**2+3), x, oo), 2)", "claimed": "true"},
            ["limit_at_infinity"],
            ["**Rule — compare leading terms.** For equal degrees, the limit is the ratio of leading coefficients.",
             "**Compute.** $\\dfrac{2}{1} = 2$.",
             "**Answer:** $2$."],
            ["**כלל — השוואת איברים מובילים.** במעלות שוות, הגבול הוא יחס המקדמים המובילים.",
             "**חישוב.** $\\dfrac{2}{1} = 2$.",
             "**תשובה:** $2$."]),
        tf(c, meta, "medium",
           "True or False: $\\lim_{x \\to 0} \\dfrac{1}{x}$ does not exist.",
           "נכון או לא נכון: $\\lim_{x \\to 0} \\dfrac{1}{x}$ אינו קיים.",
           {"check": "truth", "predicate": "Ne(limit(1/x, x, 0, '+'), limit(1/x, x, 0, '-'))", "claimed": "true"},
           True, ["one_sided_limit"],
           ["**Left vs right.** As $x\\to0^+$, $\\tfrac1x \\to +\\infty$; as $x\\to0^-$, $\\tfrac1x \\to -\\infty$.",
            "**Conclusion:** the one-sided limits disagree, so the limit **does not exist** — the statement is true."],
           ["**שמאל מול ימין.** כש-$x\\to0^+$, $\\tfrac1x \\to +\\infty$; כש-$x\\to0^-$, $\\tfrac1x \\to -\\infty$.",
            "**מסקנה:** הגבולות החד-צדדיים שונים, ולכן הגבול **אינו קיים** — ההיגד נכון."]),
        num(c, meta, "easy",
            r"Compute $\lim_{x \to 1} (x^3 + 2x - 1)$.",
            r"חשבו את $\lim_{x \to 1} (x^3 + 2x - 1)$.",
            "1**3+2*1-1", ["limit_substitution"],
            [r"**Continuity.** The expression is a polynomial, so the limit equals the substituted value.",
             r"**Compute.** $1 + 2 - 1 = 2$.",
             r"**Answer:** $2$."],
            [r"**רציפות.** הביטוי הוא פולינום, ולכן הגבול שווה לערך ההצבה.",
             r"**חישוב.** $1 + 2 - 1 = 2$.",
             r"**תשובה:** $2$."]),
        num(c, meta, "medium",
            r"Compute $\lim_{x \to \infty} \dfrac{3x^2 - x}{2x^2 + 5}$.",
            r"חשבו את $\lim_{x \to \infty} \dfrac{3x^2 - x}{2x^2 + 5}$.",
            "limit((3*x**2-x)/(2*x**2+5), x, oo)", ["limit_at_infinity"],
            [r"**Step 1 — Equal degrees.** Top and bottom are both degree $2$.",
             r"**Step 2 — Ratio of leading coefficients.** Divide through by $x^2$: $\dfrac{3 - 1/x}{2 + 5/x^2} \to \dfrac{3}{2}$.",
             r"**Answer:** $\tfrac{3}{2}$."],
            [r"**שלב 1 — מעלות שוות.** המונה והמכנה שניהם ממעלה $2$.",
             r"**שלב 2 — יחס מקדמים מובילים.** מחלקים ב-$x^2$: $\dfrac{3 - 1/x}{2 + 5/x^2} \to \dfrac{3}{2}$.",
             r"**תשובה:** $\tfrac{3}{2}$."]),
        num(c, meta, "hard",
            r"Compute $\lim_{x \to 0} \dfrac{1 - \cos x}{x^2}$.",
            r"חשבו את $\lim_{x \to 0} \dfrac{1 - \cos x}{x^2}$.",
            "limit((1-cos(x))/x**2, x, 0)", ["special_limit"],
            [r"**Step 1 — $\tfrac00$ form.** Direct substitution gives $\tfrac{0}{0}$.",
             r"**Step 2 — Half-angle identity.** $1 - \cos x = 2\sin^2\tfrac{x}{2}$, so the ratio is $\tfrac12\left(\dfrac{\sin(x/2)}{x/2}\right)^2$.",
             r"**Step 3 — Known limit.** $\dfrac{\sin(x/2)}{x/2}\to 1$, so the value is $\tfrac12$.",
             r"**Answer:** $\tfrac{1}{2}$."],
            [r"**שלב 1 — צורת $\tfrac00$.** הצבה ישירה נותנת $\tfrac{0}{0}$.",
             r"**שלב 2 — זהות חצי-זווית.** $1 - \cos x = 2\sin^2\tfrac{x}{2}$, ולכן היחס הוא $\tfrac12\left(\dfrac{\sin(x/2)}{x/2}\right)^2$.",
             r"**שלב 3 — גבול ידוע.** $\dfrac{\sin(x/2)}{x/2}\to 1$, ולכן הערך הוא $\tfrac12$.",
             r"**תשובה:** $\tfrac{1}{2}$."]),
        tf(c, meta, "medium",
           r"True or False: $\lim_{x \to 5} \dfrac{x^2 - 25}{x - 5} = 10$.",
           r"נכון או לא נכון: $\lim_{x \to 5} \dfrac{x^2 - 25}{x - 5} = 10$.",
           {"check": "truth", "predicate": "Eq(limit((x**2-25)/(x-5), x, 5), 10)", "claimed": "true"},
           True, ["limit_indeterminate", "factoring"],
           [r"**Factor.** $\dfrac{(x-5)(x+5)}{x-5} = x + 5$.",
            r"**Substitute.** $\lim_{x\to5}(x+5) = 10$.",
            r"**Conclusion:** **true**."],
           [r"**פירוק.** $\dfrac{(x-5)(x+5)}{x-5} = x + 5$.",
            r"**הצבה.** $\lim_{x\to5}(x+5) = 10$.",
            r"**מסקנה:** **נכון**."]),
        open_worked(c, meta, "hard",
            r"Evaluate $\lim_{x \to 0} \dfrac{\sqrt{x + 4} - 2}{x}$ by rationalizing.",
            r"חשבו את $\lim_{x \to 0} \dfrac{\sqrt{x + 4} - 2}{x}$ בעזרת הכפלה בצמוד.",
            [r"**Step 1 — $\tfrac00$ form.** Substitution gives $\tfrac{0}{0}$, so rationalize.",
             r"**Step 2 — Multiply by the conjugate.** $\dfrac{\sqrt{x+4}-2}{x}\cdot\dfrac{\sqrt{x+4}+2}{\sqrt{x+4}+2} = \dfrac{(x+4)-4}{x(\sqrt{x+4}+2)} = \dfrac{x}{x(\sqrt{x+4}+2)}$.",
             r"**Step 3 — Cancel and substitute.** $\dfrac{1}{\sqrt{x+4}+2} \to \dfrac{1}{4}$.",
             r"**Answer:** $\tfrac{1}{4}$."],
            [r"**שלב 1 — צורת $\tfrac00$.** ההצבה נותנת $\tfrac{0}{0}$, ולכן מכפילים בצמוד.",
             r"**שלב 2 — הכפלה בצמוד.** $\dfrac{\sqrt{x+4}-2}{x}\cdot\dfrac{\sqrt{x+4}+2}{\sqrt{x+4}+2} = \dfrac{x}{x(\sqrt{x+4}+2)}$.",
             r"**שלב 3 — צמצום והצבה.** $\dfrac{1}{\sqrt{x+4}+2} \to \dfrac{1}{4}$.",
             r"**תשובה:** $\tfrac{1}{4}$."],
            ["limit_indeterminate", "special_limit"],
            {"check": "value", "value": "limit((sqrt(x+4)-2)/x, x, 0)", "claimed": "1/4"}),
        mcq(c, meta, "hard",
            r"What is $\lim_{x \to \infty} \dfrac{5x + 2}{x^2 + 1}$?",
            r"מהו $\lim_{x \to \infty} \dfrac{5x + 2}{x^2 + 1}$?",
            ["0", "5", r"\infty", "1"], 0,
            {"check": "truth", "predicate": "Eq(limit((5*x+2)/(x**2+1), x, oo), 0)", "claimed": "true"},
            ["limit_at_infinity"],
            [r"**Compare degrees.** The denominator (degree $2$) grows faster than the numerator (degree $1$).",
             r"**Conclusion.** Lower-degree top over higher-degree bottom tends to $0$.",
             r"**Answer:** $0$."],
            [r"**השוואת מעלות.** המכנה (מעלה $2$) גדל מהר יותר מהמונה (מעלה $1$).",
             r"**מסקנה.** מונה ממעלה נמוכה חלקי מכנה ממעלה גבוהה שואף ל-$0$.",
             r"**תשובה:** $0$."]),
    ]
    return items


def gen_definite_integrals(meta):
    c = "definite_integrals"
    items = [
        num(c, meta, "easy",
            "Compute $\\int_1^3 2x\\,dx$.",
            "חשבו את $\\int_1^3 2x\\,dx$.",
            "integrate(2*x,(x,1,3))", ["definite_integral"],
            ["**Step 1 — Antiderivative.** $\\int 2x\\,dx = x^2$.",
             "**Step 2 — Evaluate $[x^2]_1^3$.** $9 - 1 = 8$.",
             "**Answer:** $8$."],
            ["**שלב 1 — פונקציה קדומה.** $\\int 2x\\,dx = x^2$.",
             "**שלב 2 — הצבה $[x^2]_1^3$.** $9 - 1 = 8$.",
             "**תשובה:** $8$."]),
        num(c, meta, "medium",
            "Compute $\\int_0^{\\pi} \\cos x\\,dx$.",
            "חשבו את $\\int_0^{\\pi} \\cos x\\,dx$.",
            "integrate(cos(x),(x,0,pi))", ["definite_integral"],
            ["**Step 1 — Antiderivative.** $\\int \\cos x\\,dx = \\sin x$.",
             "**Step 2 — Evaluate.** $[\\sin x]_0^{\\pi} = \\sin\\pi - \\sin 0 = 0$.",
             "**Answer:** $0$ (equal positive and negative areas)."],
            ["**שלב 1 — פונקציה קדומה.** $\\int \\cos x\\,dx = \\sin x$.",
             "**שלב 2 — הצבה.** $[\\sin x]_0^{\\pi} = 0$.",
             "**תשובה:** $0$ (שטחים חיוביים ושליליים שווים)."]),
        num(c, meta, "hard",
            "Compute $\\int_0^1 x e^{x^2}\\,dx$.",
            "חשבו את $\\int_0^1 x e^{x^2}\\,dx$.",
            "integrate(x*exp(x**2),(x,0,1))", ["u_substitution"],
            ["**Step 1 — Substitute $u = x^2$,** so $du = 2x\\,dx$ and $x\\,dx = \\tfrac12 du$.",
             "**Step 2 — Change limits.** $x=0\\Rightarrow u=0$; $x=1\\Rightarrow u=1$.",
             "**Step 3 — Integrate.** $\\tfrac12\\int_0^1 e^u\\,du = \\tfrac12(e - 1)$.",
             "**Answer:** $\\tfrac{e-1}{2} \\approx 0.859$."],
            ["**שלב 1 — הצבה $u = x^2$,** ולכן $du = 2x\\,dx$ ו-$x\\,dx = \\tfrac12 du$.",
             "**שלב 2 — שינוי גבולות.** $x=0\\Rightarrow u=0$; $x=1\\Rightarrow u=1$.",
             "**שלב 3 — אינטגרציה.** $\\tfrac12\\int_0^1 e^u\\,du = \\tfrac12(e - 1)$.",
             "**תשובה:** $\\tfrac{e-1}{2} \\approx 0.859$."]),
        mcq(c, meta, "medium",
            "By the Fundamental Theorem, if $F'(x) = f(x)$ then $\\int_a^b f(x)\\,dx$ equals:",
            "לפי המשפט היסודי, אם $F'(x) = f(x)$ אז $\\int_a^b f(x)\\,dx$ שווה ל:",
            ["F(b) - F(a)", "F(a) - F(b)", "F'(b) - F'(a)", "f(b) - f(a)"], 0,
            {"check": "truth", "predicate": "Eq(integrate(2*x,(x,1,3)), 3**2-1**2)", "claimed": "true"},
            ["fundamental_theorem"],
            ["**Fundamental Theorem of Calculus.** $\\int_a^b f = F(b) - F(a)$ where $F$ is any antiderivative.",
             "**Answer:** $F(b) - F(a)$."],
            ["**המשפט היסודי של החשבון האינטגרלי.** $\\int_a^b f = F(b) - F(a)$ כאשר $F$ פונקציה קדומה כלשהי.",
             "**תשובה:** $F(b) - F(a)$."]),
        tf(c, meta, "medium",
           "True or False: $\\int_a^b f(x)\\,dx = -\\int_b^a f(x)\\,dx$.",
           "נכון או לא נכון: $\\int_a^b f(x)\\,dx = -\\int_b^a f(x)\\,dx$.",
           {"check": "truth", "predicate": "Eq(integrate(x,(x,1,4)), -integrate(x,(x,4,1)))", "claimed": "true"},
           True, ["definite_integral"],
           ["**Orientation rule.** Swapping the limits flips the sign of a definite integral.",
            "**Conclusion:** **true**."],
           ["**כלל כיווניות.** החלפת הגבולות הופכת את סימן האינטגרל המסוים.",
            "**מסקנה:** **נכון**."]),
        num(c, meta, "easy",
            r"Compute $\int_0^2 x^2\,dx$.",
            r"חשבו את $\int_0^2 x^2\,dx$.",
            "integrate(x**2,(x,0,2))", ["definite_integral"],
            [r"**Step 1 — Antiderivative.** $\int x^2\,dx = \tfrac{x^3}{3}$.",
             r"**Step 2 — Evaluate $\left[\tfrac{x^3}{3}\right]_0^2$.** $\tfrac{8}{3} - 0 = \tfrac{8}{3}$.",
             r"**Answer:** $\tfrac{8}{3}$."],
            [r"**שלב 1 — פונקציה קדומה.** $\int x^2\,dx = \tfrac{x^3}{3}$.",
             r"**שלב 2 — הצבה $\left[\tfrac{x^3}{3}\right]_0^2$.** $\tfrac{8}{3} - 0 = \tfrac{8}{3}$.",
             r"**תשובה:** $\tfrac{8}{3}$."]),
        num(c, meta, "medium",
            r"Compute $\int_1^2 (6x^2 - 2x)\,dx$.",
            r"חשבו את $\int_1^2 (6x^2 - 2x)\,dx$.",
            "integrate(6*x**2-2*x,(x,1,2))", ["definite_integral"],
            [r"**Step 1 — Antiderivative.** $\int (6x^2 - 2x)\,dx = 2x^3 - x^2$.",
             r"**Step 2 — Evaluate.** $[2x^3 - x^2]_1^2 = (16 - 4) - (2 - 1) = 12 - 1 = 11$.",
             r"**Answer:** $11$."],
            [r"**שלב 1 — פונקציה קדומה.** $\int (6x^2 - 2x)\,dx = 2x^3 - x^2$.",
             r"**שלב 2 — הצבה.** $[2x^3 - x^2]_1^2 = 12 - 1 = 11$.",
             r"**תשובה:** $11$."]),
        num(c, meta, "medium",
            r"Compute $\int_0^{\pi/2} \sin x\,dx$.",
            r"חשבו את $\int_0^{\pi/2} \sin x\,dx$.",
            "integrate(sin(x),(x,0,pi/2))", ["definite_integral"],
            [r"**Step 1 — Antiderivative.** $\int \sin x\,dx = -\cos x$.",
             r"**Step 2 — Evaluate.** $[-\cos x]_0^{\pi/2} = -\cos\tfrac{\pi}{2} + \cos 0 = 0 + 1 = 1$.",
             r"**Answer:** $1$."],
            [r"**שלב 1 — פונקציה קדומה.** $\int \sin x\,dx = -\cos x$.",
             r"**שלב 2 — הצבה.** $[-\cos x]_0^{\pi/2} = 0 + 1 = 1$.",
             r"**תשובה:** $1$."]),
        num(c, meta, "hard",
            r"Compute $\int_1^{e} \ln x\,dx$.",
            r"חשבו את $\int_1^{e} \ln x\,dx$.",
            "integrate(log(x),(x,1,E))", ["integration_by_parts"],
            [r"**Step 1 — Integration by parts.** With $u = \ln x$, $dv = dx$: $\int \ln x\,dx = x\ln x - x$.",
             r"**Step 2 — Evaluate $[x\ln x - x]_1^{e}$.** $(e\cdot 1 - e) - (0 - 1) = 0 + 1 = 1$.",
             r"**Answer:** $1$."],
            [r"**שלב 1 — אינטגרציה בחלקים.** עם $u = \ln x$, $dv = dx$: $\int \ln x\,dx = x\ln x - x$.",
             r"**שלב 2 — הצבה $[x\ln x - x]_1^{e}$.** $(e - e) - (0 - 1) = 1$.",
             r"**תשובה:** $1$."]),
        open_worked(c, meta, "hard",
            r"Compute $\int_0^1 2x\,(x^2 + 1)^3\,dx$ using the substitution $u = x^2 + 1$.",
            r"חשבו את $\int_0^1 2x\,(x^2 + 1)^3\,dx$ בעזרת ההצבה $u = x^2 + 1$.",
            [r"**Step 1 — Substitute.** $u = x^2 + 1 \Rightarrow du = 2x\,dx$.",
             r"**Step 2 — Change limits.** $x = 0 \Rightarrow u = 1$; $x = 1 \Rightarrow u = 2$.",
             r"**Step 3 — Integrate.** $\int_1^2 u^3\,du = \left[\tfrac{u^4}{4}\right]_1^2 = \tfrac{16 - 1}{4} = \tfrac{15}{4}$.",
             r"**Answer:** $\tfrac{15}{4} = 3.75$."],
            [r"**שלב 1 — הצבה.** $u = x^2 + 1 \Rightarrow du = 2x\,dx$.",
             r"**שלב 2 — שינוי גבולות.** $x = 0 \Rightarrow u = 1$; $x = 1 \Rightarrow u = 2$.",
             r"**שלב 3 — אינטגרציה.** $\int_1^2 u^3\,du = \left[\tfrac{u^4}{4}\right]_1^2 = \tfrac{15}{4}$.",
             r"**תשובה:** $\tfrac{15}{4} = 3.75$."],
            ["u_substitution", "definite_integral"],
            {"check": "value", "value": "integrate(2*x*(x**2+1)**3,(x,0,1))", "claimed": "15/4"}),
        mcq(c, meta, "hard",
            r"The average value of $f(x) = x^2$ on $[0, 3]$ is $\tfrac{1}{3}\int_0^3 x^2\,dx$. It equals:",
            r"הערך הממוצע של $f(x) = x^2$ בקטע $[0, 3]$ הוא $\tfrac{1}{3}\int_0^3 x^2\,dx$. הוא שווה ל:",
            ["3", "9", "6", "1"], 0,
            {"check": "truth", "predicate": "Eq(integrate(x**2,(x,0,3))/3, 3)", "claimed": "true"},
            ["average_value", "definite_integral"],
            [r"**Step 1 — Integrate.** $\int_0^3 x^2\,dx = \left[\tfrac{x^3}{3}\right]_0^3 = 9$.",
             r"**Step 2 — Divide by the interval length $3$.** $\tfrac{1}{3}\cdot 9 = 3$.",
             r"**Answer:** $3$."],
            [r"**שלב 1 — אינטגרציה.** $\int_0^3 x^2\,dx = 9$.",
             r"**שלב 2 — חלוקה באורך הקטע $3$.** $\tfrac{1}{3}\cdot 9 = 3$.",
             r"**תשובה:** $3$."]),
    ]
    return items


GENERATORS = {
    "derivatives_rules": gen_derivatives_rules,
    "derivatives_trig_exp": gen_derivatives_trig_exp,
    "derivatives_applications": gen_derivatives_applications,
    "function_analysis_5pt": gen_function_analysis_5pt,
    "integrals_applications": gen_integrals_applications,
    "sequences_5pt": gen_sequences_5pt,
    "exponential_logarithmic": gen_exponential_logarithmic,
    "complex_numbers_5pt": gen_complex_numbers_5pt,
    "analytic_geometry_5pt": gen_analytic_geometry_5pt,
    "trigonometric_equations": gen_trigonometric_equations,
    "limits_5pt": gen_limits_5pt,
    "definite_integrals": gen_definite_integrals,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--lesson", help="lesson JSON to inherit subject/level/math_track from")
    ap.add_argument("--out", help="output JSON path (default: stdout)")
    args = ap.parse_args()

    if args.concept not in GENERATORS:
        raise SystemExit(f"no generator for concept '{args.concept}' (have: {', '.join(GENERATORS)})")

    meta = {"subject": "math", "level": "high_school", "math_track": ["5pt"], "points_level": "5pt"}
    if args.lesson and os.path.exists(args.lesson):
        with open(args.lesson, encoding="utf-8") as fh:
            lesson = json.load(fh)
        meta = {
            "subject": lesson.get("subject", meta["subject"]),
            "level": lesson.get("level", meta["level"]),
            "math_track": lesson.get("math_track", meta["math_track"]),
            "points_level": lesson.get("points_level") or meta["points_level"],
        }

    items = GENERATORS[args.concept](meta)
    payload = json.dumps(items, ensure_ascii=False, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")
        print(f"wrote {len(items)} items -> {args.out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
