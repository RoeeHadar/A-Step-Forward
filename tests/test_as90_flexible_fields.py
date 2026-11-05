"""AS-90: production code must not depend on the FlexibleModel model_extra fallback.

Static guard (AST, no imports of production modules, no network/DB): for every
production construction site ``X(kw=...)`` where ``X`` is imported from
``schemas.*`` and resolves to a FlexibleModel subclass (declared or produced by
``flexible_model()``), every keyword must be a declared field. A value stored
as an undeclared extra is the only way an attribute read can be served by
``FlexibleModel.__getattr__``'s model_extra fallback, so this pins it closed.
Also pins the attribute reads AS-88 confirmed at runtime (reads-r1.md).
The runtime half (any production read that reaches ``__getattr__``) lives in
the root conftest.py hook.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
from schemas._dynamic import FlexibleModel

ROOT = Path(__file__).resolve().parents[1]
PROD_DIRS = ["packages/agents", "packages/schemas", "services", "apps/api/app", "mcp-servers"]


def _is_test(p: Path) -> bool:
    parts = p.relative_to(ROOT).parts
    return "tests" in parts or p.name.startswith("test_") or p.name == "conftest.py"


def prod_files() -> list[Path]:
    out: list[Path] = []
    for d in PROD_DIRS:
        for p in sorted((ROOT / d).rglob("*.py")):
            if ".venv" in p.parts or "node_modules" in p.parts or _is_test(p):
                continue
            out.append(p)
    return out


def _resolve(mod: str, name: str):
    try:
        obj = getattr(importlib.import_module(mod), name)
    except Exception:
        return None
    return obj if isinstance(obj, type) and issubclass(obj, FlexibleModel) else None


def undeclared_kwargs() -> list[str]:
    bad: list[str] = []
    for path in prod_files():
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), str(path))
        names: dict[str, tuple[str, str]] = {}
        mods: dict[str, str] = {}
        rel_parts = path.relative_to(ROOT).parts
        if rel_parts[:2] == ("packages", "schemas"):
            # constructions inside the schemas package use the module's own classes
            own = ".".join(rel_parts[2:])[: -len(".py")]
            for top in tree.body:
                if isinstance(top, ast.ClassDef):
                    names[top.name] = (own, top.name)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.split(".")[0] == "schemas"
            ):
                for a in node.names:
                    names[a.asname or a.name] = (node.module, a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] == "schemas":
                        mods[a.asname or a.name] = a.name
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            target = None
            if isinstance(f, ast.Name) and f.id in names:
                target = names[f.id]
            elif (
                isinstance(f, ast.Attribute)
                and isinstance(f.value, ast.Name)
                and f.value.id in mods
            ):
                target = (mods[f.value.id], f.attr)
            if target is None:
                continue
            cls = _resolve(*target)
            if cls is None:
                continue
            for kw in node.keywords:
                if kw.arg is not None and kw.arg not in cls.model_fields:
                    rel = path.relative_to(ROOT)
                    bad.append(f"{cls.__name__}.{kw.arg} {rel}:{node.lineno}")
    return sorted(set(bad))


def test_no_production_construction_stores_an_undeclared_field() -> None:
    bad = undeclared_kwargs()
    assert bad == [], "undeclared FlexibleModel fields set in production:\n" + "\n".join(bad)


# Runtime-confirmed production reads from AS-88 reads-r1.md §2/§3.
READS = [
    ("schemas.agents", "AgentManifest", "primary_model"),
    ("schemas.agents", "AgentManifest", "fallback_model"),
    ("schemas.agents", "AgentManifest", "prompt_version"),
    ("schemas.agents", "AgentManifest", "memory_policy"),
    ("schemas.agents", "Budget", "max_output_tokens"),
    ("schemas.learner_model", "StudentModel", "mastery"),
    ("schemas.learner_model", "StudentModel", "weak"),
    ("schemas.learner_model", "StudentModel", "profile"),
    ("schemas.learner_model", "AdaptiveLearnerProfile", "goal"),
    ("schemas.learner_model", "AdaptiveLearnerProfile", "subjects"),
    ("schemas.learner_model", "AdaptiveLearnerProfile", "self_scores"),
    ("schemas.learner_model", "LearnerProfileInput", "goal"),
    ("schemas.learner_model", "LearnerProfileInput", "self_scores"),
    ("schemas.learning_path", "StoredQuizItem", "topic"),
    ("schemas.learning_path", "StoredQuizItem", "correct"),
    ("schemas.learning_path", "QuizAnswerItem", "item_id"),
    ("schemas.learning_path", "QuizAnswerItem", "chosen"),
    ("schemas.learners", "LearnerProfile", "child_mode"),
    ("schemas.memory", "CompactionInput", "messages"),
    ("schemas.memory", "CompactionInput", "target_tokens"),
    # AS-90 additions: request-body reads (rg body.<field> in production).
    ("schemas.learning_path", "QuizSubmitRequest", "answers"),
    ("schemas.diagnostic", "DiagnosticStartRequest", "topics"),
    ("schemas.diagnostic", "DiagnosticAnswerRequest", "item_id"),
    ("schemas.diagnostic", "DiagnosticAnswerRequest", "chosen"),
    ("schemas.curriculum_seed", "SeedBundle", "source"),
]


@pytest.mark.parametrize(("mod", "cls", "field"), READS, ids=[f"{c}.{f}" for _, c, f in READS])
def test_as88_confirmed_reads_are_declared(mod: str, cls: str, field: str) -> None:
    model = getattr(importlib.import_module(mod), cls)
    assert field in model.model_fields
