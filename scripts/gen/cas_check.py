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

from sympy import Eq, diff, integrate, simplify, symbols, sympify
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

        return {"supported": False, "matches": False, "computed": "", "details": f"unknown check '{kind}'"}
    except Exception as exc:  # noqa: BLE001 - report, never crash the pipeline
        return {"supported": False, "matches": False, "computed": "", "details": f"{type(exc).__name__}: {exc}"}


def _num_equal(a, b) -> bool:
    try:
        return simplify(a - b) == 0 or abs(float(a) - float(b)) < 1e-9
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
