#!/usr/bin/env python3
"""Deterministic, sympy-verified generator of original question-store items.

Produces legally-clean (`license = generated-original`) composite items whose
answers are computed by sympy — so they are correct by construction and the
Node verifier can independently re-confirm them via CAS. This is the
"generate-only" tier that needs no external source materials.

Each item carries:
  - bilingual stem (math is LTR inside $...$),
  - answer_payload (learner/grader facing),
  - a `verify` spec per part (ground-truth recomputation for cas_check.py),
  - skill_atoms (mastery tracking) and difficulty.

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


def _latex(expr) -> str:
    return sp.latex(expr)


def _plain(expr) -> str:
    return str(expr)


def _item(concept, meta, *, kind, difficulty, stem_en, stem_he, answer_payload,
          explanation_en, explanation_he, skill_atoms, verify):
    """Assemble a single-part (degenerate composite) item."""
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


def _diff_short_answer(concept, meta, f, difficulty, atoms):
    """'Differentiate f(x)=...' short-answer item, answer = f'(x)."""
    fp = sp.diff(f, x)
    ans_plain = _plain(fp)
    return _item(
        concept, meta,
        kind="short_answer",
        difficulty=difficulty,
        stem_en=f"Differentiate $f(x) = {_latex(f)}$.",
        stem_he=f"גזרו את $f(x) = {_latex(f)}$.",
        answer_payload={"acceptable_answers": [ans_plain, _latex(fp)], "case_sensitive": False},
        explanation_en=f"Apply the differentiation rules: $f'(x) = {_latex(fp)}$.",
        explanation_he=f"מיישמים את כללי הגזירה: $f'(x) = {_latex(fp)}$.",
        skill_atoms=atoms,
        verify={"check": "derivative", "of": _plain(f), "var": "x", "claimed": ans_plain},
    )


def _diff_numeric_at(concept, meta, f, x0, difficulty, atoms):
    """'Given f, find f'(x0)' numeric item."""
    val = sp.diff(f, x).subs(x, x0)
    return _item(
        concept, meta,
        kind="numeric",
        difficulty=difficulty,
        stem_en=f"Given $f(x) = {_latex(f)}$, find $f'({x0})$.",
        stem_he=f"בהינתן $f(x) = {_latex(f)}$, מצאו את $f'({x0})$.",
        answer_payload={"value": float(val) if val.is_Float or val.is_Rational else int(val)},
        explanation_en=f"$f'(x) = {_latex(sp.diff(f, x))}$, so $f'({x0}) = {_latex(val)}$.",
        explanation_he=f"$f'(x) = {_latex(sp.diff(f, x))}$, ולכן $f'({x0}) = {_latex(val)}$.",
        skill_atoms=atoms,
        verify={"check": "derivative_at", "of": _plain(f), "var": "x", "at": str(x0), "claimed": _plain(val)},
    )


def _diff_mcq(concept, meta, f, distractors, difficulty, atoms):
    """'Which is the derivative of f?' MCQ item; correct = f'(x)."""
    fp = sp.diff(f, x)
    correct = _latex(fp)
    options = [correct] + [_latex(d) for d in distractors]
    return _item(
        concept, meta,
        kind="mcq",
        difficulty=difficulty,
        stem_en=f"Which of the following is the derivative of $f(x) = {_latex(f)}$?",
        stem_he=f"איזו מהאפשרויות הבאות היא הנגזרת של $f(x) = {_latex(f)}$?",
        answer_payload={
            "options_en": [f"${o}$" for o in options],
            "options_he": [f"${o}$" for o in options],
            "correct_index": 0,
        },
        explanation_en=f"By the differentiation rules, $f'(x) = {correct}$.",
        explanation_he=f"לפי כללי הגזירה, $f'(x) = {correct}$.",
        skill_atoms=atoms,
        verify={"check": "derivative", "of": _plain(f), "var": "x", "claimed": _plain(fp)},
    )


def _diff_true_false(concept, meta, f, stated_rhs, difficulty, atoms):
    """'True or False: (f)' = stated_rhs' item; value computed by sympy."""
    fp = sp.diff(f, x)
    truth = sp.simplify(fp - stated_rhs) == 0
    return _item(
        concept, meta,
        kind="true_false",
        difficulty=difficulty,
        stem_en=f"True or False: $\\left({_latex(f)}\\right)' = {_latex(stated_rhs)}$.",
        stem_he=f"נכון או לא נכון: $\\left({_latex(f)}\\right)' = {_latex(stated_rhs)}$.",
        answer_payload={"value": bool(truth)},
        explanation_en=f"The true derivative is $ {_latex(fp)} $, so the statement is {'true' if truth else 'false'}.",
        explanation_he=f"הנגזרת הנכונה היא $ {_latex(fp)} $, ולכן ההיגד {'נכון' if truth else 'לא נכון'}.",
        skill_atoms=atoms,
        verify={"check": "derivative", "of": _plain(f), "var": "x", "claimed": _plain(stated_rhs)},
    )


def _to_num(expr):
    """Convert a sympy value to a JSON-friendly int/float."""
    val = float(sp.N(expr))
    return round(val) if abs(val - round(val)) < 1e-9 else round(val, 6)


def _mk(concept, meta, *, kind, difficulty, stem_en, stem_he, answer_payload, atoms, verify,
        expl_en="", expl_he=""):
    """Generic single-part item with an explicit CAS verify spec."""
    return _item(
        concept, meta, kind=kind, difficulty=difficulty, stem_en=stem_en, stem_he=stem_he,
        answer_payload=answer_payload, explanation_en=expl_en, explanation_he=expl_he,
        skill_atoms=atoms, verify=verify,
    )


def _num(concept, meta, difficulty, stem_en, stem_he, cas_value, atoms, expl_en="", expl_he=""):
    """Numeric item whose answer is recomputed by CAS from `cas_value`."""
    value = _to_num(sp.sympify(cas_value.replace("^", "**")))
    return _mk(
        concept, meta, kind="numeric", difficulty=difficulty, stem_en=stem_en, stem_he=stem_he,
        answer_payload={"value": value}, atoms=atoms,
        verify={"check": "value", "value": cas_value, "claimed": str(value)},
        expl_en=expl_en, expl_he=expl_he,
    )


def _tf(concept, meta, difficulty, stem_en, stem_he, verify, truth, atoms):
    """True/False item whose truth value is decided by a CAS verify spec."""
    return _mk(
        concept, meta, kind="true_false", difficulty=difficulty, stem_en=stem_en, stem_he=stem_he,
        answer_payload={"value": bool(truth)}, atoms=atoms, verify=verify,
        expl_en=f"CAS check confirms the statement is {'true' if truth else 'false'}.",
        expl_he=f"בדיקת CAS מאשרת שההיגד {'נכון' if truth else 'לא נכון'}.",
    )


def _mcq(concept, meta, difficulty, stem_en, stem_he, options, correct_index, verify, atoms):
    """MCQ item; `verify` must confirm the marked option is the true answer."""
    opts = [f"${o}$" for o in options]
    return _mk(
        concept, meta, kind="mcq", difficulty=difficulty, stem_en=stem_en, stem_he=stem_he,
        answer_payload={"options_en": opts, "options_he": opts, "correct_index": correct_index},
        atoms=atoms, verify=verify,
        expl_en=f"The correct option is ${options[correct_index]}$ (CAS-verified).",
        expl_he=f"התשובה הנכונה היא ${options[correct_index]}$ (מאומת ב-CAS).",
    )


def gen_derivatives_rules(meta):
    """Curated bank covering sum/power, product, quotient, chain rules."""
    items = []
    # Easy — power + sum rule
    items.append(_diff_short_answer("derivatives_rules", meta, 7 * x**4 - 3 * x**2 + 5, "easy", ["power_rule", "sum_rule"]))
    items.append(_diff_numeric_at("derivatives_rules", meta, x**3 + 2 * x, 2, "easy", ["power_rule", "sum_rule"]))
    items.append(_diff_mcq("derivatives_rules", meta, x**3 + 2 * x, [3 * x**2, x**2 + 2, 3 * x**3 + 2], "easy", ["power_rule"]))
    items.append(_diff_true_false("derivatives_rules", meta, x**5, 5 * x**4, "easy", ["power_rule"]))
    # Medium — product rule
    items.append(_diff_short_answer("derivatives_rules", meta, (x**2 + 1) * sp.sin(x), "medium", ["product_rule"]))
    items.append(_diff_short_answer("derivatives_rules", meta, x**2 * sp.exp(x), "medium", ["product_rule"]))
    # Medium — quotient rule
    items.append(_diff_short_answer("derivatives_rules", meta, x**2 / sp.sin(x), "medium", ["quotient_rule"]))
    # Medium/Hard — chain rule
    items.append(_diff_short_answer("derivatives_rules", meta, sp.cos(3 * x**2 - 1), "medium", ["chain_rule"]))
    items.append(_diff_short_answer("derivatives_rules", meta, (x**3 + 1) ** 10, "hard", ["chain_rule", "power_rule"]))
    # Hard — combined product + chain
    items.append(_diff_short_answer("derivatives_rules", meta, x**2 * sp.exp(sp.sin(x)), "hard", ["product_rule", "chain_rule"]))
    return items


def gen_derivatives_trig_exp(meta):
    """Derivatives of trigonometric, exponential and logarithmic functions."""
    c = "derivatives_trig_exp"
    items = [
        _diff_short_answer(c, meta, sp.sin(x), "easy", ["derivative_sin_cos"]),
        _diff_short_answer(c, meta, sp.exp(x), "easy", ["derivative_exp"]),
        _diff_short_answer(c, meta, sp.log(x), "easy", ["derivative_ln"]),
        _diff_short_answer(c, meta, sp.sin(x**2), "medium", ["chain_rule", "derivative_sin_cos"]),
        _diff_short_answer(c, meta, sp.exp(2 * x), "medium", ["chain_rule", "derivative_exp"]),
        _diff_numeric_at(c, meta, sp.exp(x), 0, "easy", ["derivative_exp"]),
        _diff_mcq(c, meta, sp.cos(x), [sp.sin(x), -sp.cos(x), sp.tan(x)], "easy", ["derivative_sin_cos"]),
        _diff_true_false(c, meta, sp.sin(x), sp.cos(x), "easy", ["derivative_sin_cos"]),
    ]
    return items


def gen_derivatives_applications(meta):
    """Critical points, tangent lines and inflection points."""
    c = "derivatives_applications"
    f = x**3 - 3 * x
    fs = _plain(f)
    items = [
        _diff_short_answer(c, meta, f, "easy", ["critical_points"]),
        _diff_numeric_at(c, meta, f, 1, "medium", ["tangent_line"]),
        _mcq(c, meta, "medium",
             "Which value is a critical point of $f(x) = x^3 - 3x$?",
             "איזה ערך הוא נקודה קריטית של $f(x) = x^3 - 3x$?",
             ["x=1", "x=0", "x=2", "x=3"], 0,
             {"check": "derivative_at", "of": fs, "var": "x", "at": "1", "claimed": "0"},
             ["critical_points"]),
        _num(c, meta, "hard",
             "Find the $x$-coordinate of the inflection point of $f(x) = x^3 - 3x$.",
             "מצאו את שיעור ה-$x$ של נקודת הפיתול של $f(x) = x^3 - 3x$.",
             "0", ["inflection_point"],
             "The inflection point is where $f''(x)=6x=0$.",
             "נקודת הפיתול היא במקום שבו $f''(x)=6x=0$."),
        _tf(c, meta, "medium",
            "True or False: $x = 1$ is a critical point of $f(x) = x^3 - 3x$.",
            "נכון או לא נכון: $x = 1$ היא נקודה קריטית של $f(x) = x^3 - 3x$.",
            {"check": "derivative_at", "of": fs, "var": "x", "at": "1", "claimed": "0"},
            True, ["critical_points"]),
    ]
    return items


def gen_function_analysis_5pt(meta):
    """Full function investigation: derivative, critical points, concavity."""
    c = "function_analysis_5pt"
    f = x**4 - 2 * x**2
    fs = _plain(f)
    items = [
        _diff_short_answer(c, meta, f, "easy", ["monotonicity"]),
        _mcq(c, meta, "medium",
             "Which value is a critical point of $f(x) = x^4 - 2x^2$?",
             "איזה ערך הוא נקודה קריטית של $f(x) = x^4 - 2x^2$?",
             ["x=1", "x=2", "x=3", "x=4"], 0,
             {"check": "derivative_at", "of": fs, "var": "x", "at": "1", "claimed": "0"},
             ["critical_points"]),
        _num(c, meta, "medium",
             "Compute $f''(0)$ for $f(x) = x^4 - 2x^2$.",
             "חשבו את $f''(0)$ עבור $f(x) = x^4 - 2x^2$.",
             "-4", ["concavity"],
             "$f''(x) = 12x^2 - 4$, so $f''(0) = -4$ (concave down at the origin).",
             "$f''(x) = 12x^2 - 4$, ולכן $f''(0) = -4$ (קעורה כלפי מטה בראשית)."),
        _diff_numeric_at(c, meta, f, 1, "medium", ["tangent_line"]),
        _tf(c, meta, "medium",
            "True or False: $x = 0$ is a critical point of $f(x) = x^4 - 2x^2$.",
            "נכון או לא נכון: $x = 0$ היא נקודה קריטית של $f(x) = x^4 - 2x^2$.",
            {"check": "derivative_at", "of": fs, "var": "x", "at": "0", "claimed": "0"},
            True, ["critical_points"]),
    ]
    return items


def gen_integrals_applications(meta):
    """Definite integrals and areas under curves."""
    c = "integrals_applications"
    items = [
        _mk(c, meta, kind="numeric", difficulty="easy",
            stem_en="Compute $\\int_0^3 2x\\,dx$.",
            stem_he="חשבו את $\\int_0^3 2x\\,dx$.",
            answer_payload={"value": 9}, atoms=["definite_integral"],
            verify={"check": "integral_definite", "of": "2*x", "var": "x", "lower": "0", "upper": "3", "claimed": "9"},
            expl_en="$\\int_0^3 2x\\,dx = [x^2]_0^3 = 9$.",
            expl_he="$\\int_0^3 2x\\,dx = [x^2]_0^3 = 9$."),
        _mk(c, meta, kind="short_answer", difficulty="easy",
            stem_en="Find an antiderivative of $f(x) = 2x$.",
            stem_he="מצאו פונקציה קדומה של $f(x) = 2x$.",
            answer_payload={"acceptable_answers": ["x**2", "x^2"], "case_sensitive": False},
            atoms=["antiderivative"],
            verify={"check": "derivative", "of": "x**2", "var": "x", "claimed": "2*x"},
            expl_en="$\\frac{d}{dx}(x^2) = 2x$.", expl_he="$\\frac{d}{dx}(x^2) = 2x$."),
        _mcq(c, meta, "medium",
             "What is the area under $f(x) = x$ from $x=0$ to $x=2$?",
             "מהו השטח מתחת ל-$f(x) = x$ בתחום $x=0$ עד $x=2$?",
             ["2", "4", "1", "8"], 0,
             {"check": "integral_definite", "of": "x", "var": "x", "lower": "0", "upper": "2", "claimed": "2"},
             ["area_under_curve"]),
        _tf(c, meta, "medium",
            "True or False: $\\int_0^1 3x^2\\,dx = 1$.",
            "נכון או לא נכון: $\\int_0^1 3x^2\\,dx = 1$.",
            {"check": "integral_definite", "of": "3*x**2", "var": "x", "lower": "0", "upper": "1", "claimed": "1"},
            True, ["definite_integral"]),
    ]
    return items


def gen_sequences_5pt(meta):
    """Arithmetic and geometric sequences and sums."""
    c = "sequences_5pt"
    items = [
        _num(c, meta, "easy",
             "An arithmetic sequence has $a_1 = 4$ and common difference $d = 3$. Find $a_{10}$.",
             "בסדרה חשבונית $a_1 = 4$ וההפרש $d = 3$. מצאו את $a_{10}$.",
             "4+9*3", ["arithmetic_sequence"],
             "$a_{10} = a_1 + 9d = 4 + 27 = 31$.", "$a_{10} = a_1 + 9d = 4 + 27 = 31$."),
        _mcq(c, meta, "medium",
             "A geometric sequence has $a_1 = 3$ and ratio $r = 2$. What is $a_4$?",
             "בסדרה הנדסית $a_1 = 3$ והמנה $r = 2$. מהו $a_4$?",
             ["24", "48", "16", "12"], 0,
             {"check": "value", "value": "3*2**3", "claimed": "24"},
             ["geometric_sequence"]),
        _num(c, meta, "medium",
             "Find the sum of the first 5 terms of an arithmetic sequence with $a_1 = 2$, $d = 5$.",
             "מצאו את סכום 5 האיברים הראשונים בסדרה חשבונית עם $a_1 = 2$, $d = 5$.",
             "5*(2*2+4*5)/2", ["sequence_sum"],
             "$S_5 = \\frac{5}{2}(2a_1 + 4d) = \\frac{5}{2}(4+20) = 60$.",
             "$S_5 = \\frac{5}{2}(2a_1 + 4d) = \\frac{5}{2}(4+20) = 60$."),
        _tf(c, meta, "easy",
            "True or False: the 5th term of an arithmetic sequence with $a_1 = 2$, $d = 5$ is $22$.",
            "נכון או לא נכון: האיבר החמישי בסדרה חשבונית עם $a_1 = 2$, $d = 5$ הוא $22$.",
            {"check": "value", "value": "2+4*5", "claimed": "22"}, True, ["arithmetic_sequence"]),
    ]
    return items


def gen_exponential_logarithmic(meta):
    """Logarithm evaluation, exponential equations, log rules."""
    c = "exponential_logarithmic"
    items = [
        _num(c, meta, "easy", "Evaluate $\\log_2 8$.", "חשבו את $\\log_2 8$.",
             "log(8,2)", ["log_evaluation"],
             "$\\log_2 8 = 3$ because $2^3 = 8$.", "$\\log_2 8 = 3$ כי $2^3 = 8$."),
        _num(c, meta, "medium", "Evaluate $\\ln(e^5)$.", "חשבו את $\\ln(e^5)$.",
             "log(exp(5))", ["log_rules"],
             "$\\ln(e^5) = 5$.", "$\\ln(e^5) = 5$."),
        _mcq(c, meta, "medium",
             "Solve $2^x = 8$.",
             "פתרו את $2^x = 8$.",
             ["3", "2", "4", "1"], 0,
             {"check": "expr_value", "of": "2**x", "var": "x", "at": "3", "claimed": "8"},
             ["exp_equation"]),
        _tf(c, meta, "easy",
            "True or False: $\\log_3 9 = 2$.",
            "נכון או לא נכון: $\\log_3 9 = 2$.",
            {"check": "value", "value": "log(9,3)", "claimed": "2"}, True, ["log_evaluation"]),
    ]
    return items


def gen_complex_numbers_5pt(meta):
    """Modulus, arithmetic and conjugates of complex numbers."""
    c = "complex_numbers_5pt"
    items = [
        _num(c, meta, "easy", "Compute the modulus $|3 + 4i|$.", "חשבו את הערך המוחלט $|3 + 4i|$.",
             "Abs(3+4*I)", ["complex_modulus"],
             "$|3+4i| = \\sqrt{9+16} = 5$.", "$|3+4i| = \\sqrt{9+16} = 5$."),
        _num(c, meta, "medium",
             "Compute the real part of $(1 + 2i)(3 - i)$.",
             "חשבו את החלק הממשי של $(1 + 2i)(3 - i)$.",
             "re((1+2*I)*(3-I))", ["complex_arithmetic"],
             "$(1+2i)(3-i) = 5 + 5i$, real part $5$.",
             "$(1+2i)(3-i) = 5 + 5i$, החלק הממשי $5$."),
        _mcq(c, meta, "medium",
             "Compute $(2 + 3i) + (1 - i)$.",
             "חשבו את $(2 + 3i) + (1 - i)$.",
             ["3+2i", "3+4i", "1+2i", "2+3i"], 0,
             {"check": "value", "value": "(2+3*I)+(1-I)", "claimed": "3+2*I"},
             ["complex_arithmetic"]),
        _tf(c, meta, "easy",
            "True or False: $|3 + 4i| = 5$.",
            "נכון או לא נכון: $|3 + 4i| = 5$.",
            {"check": "value", "value": "Abs(3+4*I)", "claimed": "5"}, True, ["complex_modulus"]),
    ]
    return items


def gen_analytic_geometry_5pt(meta):
    """Slope, distance and circle equation basics."""
    c = "analytic_geometry_5pt"
    items = [
        _num(c, meta, "easy",
             "Find the distance between $(0,0)$ and $(3,4)$.",
             "מצאו את המרחק בין $(0,0)$ ל-$(3,4)$.",
             "sqrt(3**2+4**2)", ["distance_formula"],
             "$d = \\sqrt{9+16} = 5$.", "$d = \\sqrt{9+16} = 5$."),
        _num(c, meta, "easy",
             "Find the slope of the line through $(1,2)$ and $(3,8)$.",
             "מצאו את השיפוע של הישר העובר דרך $(1,2)$ ו-$(3,8)$.",
             "(8-2)/(3-1)", ["line_slope"],
             "$m = \\frac{8-2}{3-1} = 3$.", "$m = \\frac{8-2}{3-1} = 3$."),
        _mcq(c, meta, "medium",
             "What is the radius of the circle $x^2 + y^2 = 25$?",
             "מהו הרדיוס של המעגל $x^2 + y^2 = 25$?",
             ["5", "25", "10", "2.5"], 0,
             {"check": "value", "value": "sqrt(25)", "claimed": "5"},
             ["circle_equation"]),
        _tf(c, meta, "medium",
            "True or False: the distance from the origin to $(5,12)$ is $13$.",
            "נכון או לא נכון: המרחק מהראשית אל $(5,12)$ הוא $13$.",
            {"check": "value", "value": "sqrt(5**2+12**2)", "claimed": "13"}, True, ["distance_formula"]),
    ]
    return items


def gen_trigonometric_equations(meta):
    """Solving basic trigonometric equations and trig values."""
    c = "trigonometric_equations"
    items = [
        _mk(c, meta, kind="short_answer", difficulty="medium",
            stem_en="Find the principal solution of $\\sin x = \\tfrac{1}{2}$ in $[0, \\tfrac{\\pi}{2}]$.",
            stem_he="מצאו את הפתרון העיקרי של $\\sin x = \\tfrac{1}{2}$ בתחום $[0, \\tfrac{\\pi}{2}]$.",
            answer_payload={"acceptable_answers": ["pi/6", "30", "30°"], "case_sensitive": False},
            atoms=["trig_equation_solution"],
            verify={"check": "expr_value", "of": "sin(x)", "var": "x", "at": "pi/6", "claimed": "1/2"},
            expl_en="$\\sin(\\pi/6) = 1/2$.", expl_he="$\\sin(\\pi/6) = 1/2$."),
        _num(c, meta, "easy", "Evaluate $\\tan(\\tfrac{\\pi}{4})$.", "חשבו את $\\tan(\\tfrac{\\pi}{4})$.",
             "tan(pi/4)", ["trig_values"],
             "$\\tan(\\pi/4) = 1$.", "$\\tan(\\pi/4) = 1$."),
        _mcq(c, meta, "medium",
             "Which is a principal solution of $\\cos x = 0$?",
             "איזה הוא פתרון עיקרי של $\\cos x = 0$?",
             ["\\frac{\\pi}{2}", "0", "\\pi", "\\frac{\\pi}{4}"], 0,
             {"check": "expr_value", "of": "cos(x)", "var": "x", "at": "pi/2", "claimed": "0"},
             ["trig_equation_solution"]),
        _tf(c, meta, "easy",
            "True or False: $x = \\tfrac{\\pi}{6}$ satisfies $\\sin x = \\tfrac{1}{2}$.",
            "נכון או לא נכון: $x = \\tfrac{\\pi}{6}$ מקיים $\\sin x = \\tfrac{1}{2}$.",
            {"check": "expr_value", "of": "sin(x)", "var": "x", "at": "pi/6", "claimed": "1/2"},
            True, ["trig_values"]),
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
