#!/usr/bin/env python3
"""Collapse over-escaped LaTeX in lesson JSON (\\\\lim -> \\lim in file -> \\lim parsed)."""
from __future__ import annotations

import json
import re
from pathlib import Path

LESSONS = Path(__file__).resolve().parents[1] / "scripts" / "seed_data" / "lessons"

# In the *parsed* string, \\cmd should be \cmd for KaTeX. Matrix row separators stay \\.
LATEX_CMD = re.compile(
    r"\\\\("
    r"lim|to|frac|dfrac|tfrac|sin|cos|tan|sec|csc|cot|log|ln|exp|sqrt|sum|prod|int|oint|"
    r"infty|pm|mp|cdot|times|div|leq|geq|neq|approx|equiv|Rightarrow|Leftarrow|Leftrightarrow|"
    r"Longleftrightarrow|quad|qquad|text|mathrm|mathbf|mathbb|mathcal|left|right|begin|end|"
    r"alpha|beta|gamma|delta|epsilon|varepsilon|theta|lambda|mu|pi|sigma|phi|omega|"
    r"Delta|Gamma|Theta|Lambda|Sigma|Phi|Omega|"
    r"le|ge|ne|subset|supset|in|notin|forall|exists|partial|nabla|"
    r"overline|underline|hat|bar|vec|dot|ddot|"
    r"sinh|cosh|tanh|"
    r"det|dim|ker|deg|gcd|lcm|min|max|sup|inf|"
    r"displaystyle|textstyle|scriptstyle|"
    r"bullet|circ|star|diamond|"
    r"ldots|cdots|vdots|ddots|"
    r"overrightarrow|overleftarrow|"
    r"not|pm|mp"
    r")"
)


def fix_parsed_latex(text: str) -> str:
    if not text or "\\\\" not in text:
        return text
    prev = None
    out = text
    # Repeat until stable (handles \\\\lim -> still no triple cases)
    while prev != out:
        prev = out
        out = LATEX_CMD.sub(r"\\\1", out)
        # Spacing commands: \\, \\; \\: \\!
        out = re.sub(r"\\\\([,;:!])", r"\\\1", out)
    return out


def walk(obj) -> int:
    n = 0
    if isinstance(obj, str):
        return 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and (
                k.endswith("_md")
                or k.endswith("_he")
                or k.endswith("_en")
                or "solution" in k
                or k in {"stem_en", "stem_he", "explanation_en", "explanation_he", "rubric_en", "rubric_he"}
            ):
                fixed = fix_parsed_latex(v)
                if fixed != v:
                    obj[k] = fixed
                    n += 1
            elif isinstance(v, list) and k.endswith("_he"):
                for i, item in enumerate(v):
                    if isinstance(item, str):
                        fixed = fix_parsed_latex(item)
                        if fixed != item:
                            v[i] = fixed
                            n += 1
            else:
                n += walk(v)
    elif isinstance(obj, list):
        for item in obj:
            n += walk(item)
    return n


def main() -> None:
    total = 0
    files = 0
    for fp in sorted(LESSONS.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
        n = walk(data)
        if n:
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            files += 1
            total += n
    print(f"Fixed {total} fields across {files} files")


if __name__ == "__main__":
    main()
