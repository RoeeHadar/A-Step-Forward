"""AS-100: cross-language drift test for the allowed Groq model ids (ADR-0004).

The TS guard (apps/web/src/lib/llm/guarded-client.ts) and the Python guard
(agents/base/llm.py) must allow exactly the same ids, and both must match
docs/adr/0004-llm-provider-groq.md (default + cheap model, lines 34-35).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from agents.base.llm import GROQ_MODEL_MAP, GROQ_NATIVE_MODELS  # noqa: E402

TS = ROOT / "apps" / "web" / "src" / "lib" / "llm" / "guarded-client.ts"
ADR = ROOT / "docs" / "adr" / "0004-llm-provider-groq.md"


def _block(src: str, start: str) -> str:
    i = src.index(start)
    return src[i : src.index(")", i)]


def ts_lists() -> tuple[set[str], dict[str, str]]:
    src = TS.read_text(encoding="utf-8")
    natives = set(re.findall(r"'([^']+)'", _block(src, "export const GROQ_NATIVE_MODELS")))
    mp = dict(re.findall(r"'([^']+)':\s*'([^']+)'", _block(src, "export const GROQ_MODEL_MAP")))
    return natives, mp


def adr_models() -> set[str]:
    text = ADR.read_text(encoding="utf-8")
    return set(re.findall(r"(?:Default|Cheap / bulk) model: `([^`]+)`", text))


def test_adr_names_exactly_two_models() -> None:
    assert adr_models() == {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"}


def test_ts_and_python_natives_match_adr() -> None:
    ts_natives, _ = ts_lists()
    assert ts_natives == set(GROQ_NATIVE_MODELS) == adr_models()


def test_ts_and_python_model_maps_match() -> None:
    _, ts_map = ts_lists()
    assert ts_map == GROQ_MODEL_MAP
    assert set(ts_map.values()) <= adr_models()
