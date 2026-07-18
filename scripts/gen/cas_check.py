#!/usr/bin/env python3
"""Deterministic CAS answer checker (sympy) for the question-store verifier.

Reads a JSON request on stdin and writes a JSON verdict on stdout. The Node
verifier (scripts/lib/cas-runner.mjs) shells out to this so the pipeline has a
real, independent ground-truth check for closed-form math answers.

Request shapes (field `check`):
  symbolic_equal      {expr, claimed}                      -> a == b symbolically
  value               {value, claimed}                     -> numeric equality
  derivative          {of, var, claimed}                   -> d/dvar(of) == claimed
  integral_definite   {of, var, lower, upper, claimed}     -> ∫ == claimed
  expr_value          {of, var, at, claimed}               -> of(at) == claimed

Verdict: {"supported": bool, "matches": bool, "computed": str, "details": str}
Never raises to the caller — parse/compute failures return supported=false.
"""
from __future__ import annotations

import json
import sys

from sympy import Abs, Eq, N, S, diff, integrate, simplify, symbols, sympify
from sympy.core.relational import Relational
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

TRANSFORMS = (*standard_transformations, implicit_multiplication_application)


def _parse(text: str):
    """Parse a human-ish math string ('3x^2-3') into a sympy expression."""
    if text is None:
        raise ValueError("empty expression")
    cleaned = str(text).replace("^", "**")
    return parse_expr(cleaned, transformations=TRANSFORMS, evaluate=True)


def _sym_equal(a, b) -> bool:
    try:
        return simplify(a - b) == 0
    except Exception:
        return bool(Eq(a, b))


def check(req: dict) -> dict:
    kind = req.get("check")
    try:
        if kind == "value":
            computed = sympify(req["value"])
            claimed = _parse(req["claimed"])
            return _ok(_num_equal(computed, claimed), computed)

        if kind == "symbolic_equal":
            computed = _parse(req["expr"])
            claimed = _parse(req["claimed"])
            return _ok(_sym_equal(computed, claimed), computed)

        if kind == "derivative":
            var = symbols(req.get("var", "x"))
            computed = diff(_parse(req["of"]), var)
            claimed = _parse(req["claimed"])
            return _ok(_sym_equal(computed, claimed), computed)

        if kind == "integral_definite":
            var = symbols(req.get("var", "x"))
            computed = integrate(_parse(req["of"]), (var, sympify(req["lower"]), sympify(req["upper"])))
            claimed = _parse(req["claimed"])
            return _ok(_num_equal(computed, claimed), computed)

        if kind == "expr_value":
            var = symbols(req.get("var", "x"))
            computed = _parse(req["of"]).subs(var, sympify(req["at"]))
            claimed = _parse(req["claimed"])
            return _ok(_num_equal(computed, claimed), computed)

        if kind == "derivative_at":
            var = symbols(req.get("var", "x"))
            computed = diff(_parse(req["of"]), var).subs(var, sympify(req["at"]))
            claimed = _parse(req["claimed"])
            return _ok(_num_equal(computed, claimed), computed)

        if kind == "second_derivative_at":
            var = symbols(req.get("var", "x"))
            computed = diff(_parse(req["of"]), var, 2).subs(var, sympify(req["at"]))
            claimed = _parse(req["claimed"])
            return _ok(_num_equal(computed, claimed), computed)

        if kind == "sign":
            # Sign of an expression (optionally at a point): claimed in {-1,0,1,+,-,0}.
            var = symbols(req.get("var", "x"))
            expr = _parse(req["of"])
            if req.get("at") is not None:
                expr = expr.subs(var, sympify(req["at"]))
            val = N(expr)
            computed_sign = 0 if abs(float(val)) < 1e-12 else (1 if float(val) > 0 else -1)
            claim_raw = str(req["claimed"]).strip()
            claim_map = {"+": 1, "positive": 1, "1": 1, "-": -1, "negative": -1, "0": 0, "zero": 0}
            claimed_sign = claim_map.get(claim_raw.lower(), None)
            if claimed_sign is None:
                claimed_sign = int(float(sympify(claim_raw)))
            return _ok(computed_sign == claimed_sign, computed_sign)

        if kind == "truth":
            # Evaluate a predicate ("3*2**2-3 > 0", "Eq(log(6)+log(5), log(30))")
            # to a bool and compare to the claimed truth value. Powers conceptual
            # true/false + mcq items. Symbolic relationals fall back to numeric.
            predicate = str(req["predicate"]).replace("^", "**")
            expr = parse_expr(predicate, transformations=TRANSFORMS)
            computed = _truth_value(expr)
            claim_raw = str(req["claimed"]).strip().lower()
            claimed = claim_raw in ("true", "1", "yes")
            return _ok(computed == claimed, computed)

        return {"supported": False, "matches": False, "computed": "", "details": f"unknown check '{kind}'"}
    except Exception as exc:  # noqa: BLE001 - report, never crash the pipeline
        return {"supported": False, "matches": False, "computed": "", "details": f"{type(exc).__name__}: {exc}"}


def _truth_value(expr) -> bool:
    """Decide the truth of a boolean/relational expr, numerically if needed."""
    if expr is S.true:
        return True
    if expr is S.false:
        return False
    if isinstance(expr, Relational):
        op = expr.rel_op
        if op in ("==", "!="):
            d = float(Abs(N(expr.lhs - expr.rhs)))
            eq = d < 1e-9
            return eq if op == "==" else (not eq)
        d = float(N(expr.lhs - expr.rhs))
        if op == "<":
            return d < 0
        if op == "<=":
            return d <= 1e-12
        if op == ">":
            return d > 0
        if op == ">=":
            return d >= -1e-12
    return bool(expr)


def _num_equal(a, b) -> bool:
    # Tolerance 1e-6 matches the generator's 6-decimal display rounding
    # (e.g. 1/9 -> 0.111111) while staying far below any distractor gap.
    try:
        return simplify(a - b) == 0 or abs(float(a) - float(b)) < 1e-6
    except Exception:
        return _sym_equal(a, b)


def _ok(matches: bool, computed) -> dict:
    return {
        "supported": True,
        "matches": bool(matches),
        "computed": str(computed),
        "details": "sympy verified" if matches else "sympy mismatch",
    }


def main() -> None:
    raw = sys.stdin.read()
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"supported": False, "matches": False, "computed": "", "details": f"bad json: {exc}"}))
        return
    print(json.dumps(check(req)))


if __name__ == "__main__":
    main()
