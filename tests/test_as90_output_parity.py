"""AS-90 r1 P1-1: production JSON output must match base tree 5d1d9b63.

tests/fixtures/as90_base_output.json was produced by running
tests/as90_parity_capture.py on the base tree (items/AS-90/logs/output-parity-*).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "as90_base_output.json"


@pytest.fixture(scope="module")
def captured() -> dict:
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"GROQ_API_KEY", "LLM_API_KEY", "ALLOW_REAL_LLM", "EVAL_REAL"}
    }
    env["PYTHONHASHSEED"] = "0"  # AgentManifest set-valued fields
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "as90_parity_capture.py")],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
        check=True,
    )
    return json.loads(proc.stdout)


BASE = json.loads(FIXTURE.read_text())


def test_same_cases(captured: dict) -> None:
    assert sorted(captured) == sorted(BASE)


@pytest.mark.parametrize("case", sorted(BASE))
def test_output_matches_base(captured: dict, case: str) -> None:
    assert captured[case] == BASE[case]


def test_explicit_none_still_emitted() -> None:
    from schemas._as90_compat import dump_base_compat
    from schemas.common import Provenance
    from schemas.learning_path import QuizSubmitResponse

    assert "model" not in dump_base_compat(Provenance(kind="import", id="d"))
    assert dump_base_compat(Provenance(kind="import", id="d", model=None))["model"] is None
    out = dump_base_compat(
        QuizSubmitResponse(
            quiz_id="q",
            score=0.0,
            per_topic={},
            weak_concepts=[],
            plan_adapted=False,
            next_week_concepts=None,
        )
    )
    assert "next_week_concepts" in out and out["next_week_concepts"] is None


def test_registry_matches_declared_fields() -> None:
    import importlib

    from schemas._as90_compat import AS90_DECLARED

    assert len(AS90_DECLARED) == 58 and sum(map(len, AS90_DECLARED.values())) == 232
    for key, names in AS90_DECLARED.items():
        mod, _, cls = key.rpartition(".")
        model = getattr(importlib.import_module(mod), cls)
        for n in names:
            assert n in model.model_fields, key + "." + n
            assert model.model_fields[n].default is None, key + "." + n
