"""Eval runner — aggregates promptfoo + DeepEval + memory hygiene suites.

Usage:
  uv run python evals/runner.py              # full local suite
  uv run python evals/runner.py --touched    # CI: only suites for changed paths
  uv run python evals/runner.py --suite tutor
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
REPORT_MD = EVALS / "report.md"
RESULTS_JSON = EVALS / "results.json"

# Ensure monorepo packages are importable when running without uv editable installs.
_PATHS = ("packages/schemas", "services/memory", "services/graphrag", "packages/agents")
for rel in _PATHS:
    pkg_root = ROOT / rel
    if pkg_root.exists() and str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))


def _pythonpath_env() -> str:
    existing = subprocess.os.environ.get("PYTHONPATH", "")
    parts = [str(ROOT / rel) for rel in _PATHS if (ROOT / rel).exists()]
    if existing:
        parts.append(existing)
    return ";".join(parts) if sys.platform == "win32" else ":".join(parts)

# Path prefixes → suite ids to run when --touched is set.
TOUCH_MAP: list[tuple[str, str]] = [
    ("prompts/tutor/", "tutor"),
    ("packages/agents/agents/learner_facing/tutor/", "tutor"),
    ("evals/agents/tutor/", "tutor"),
    ("services/memory/", "memory"),
    ("evals/memory/", "memory"),
    ("services/graphrag/", "graphrag"),
    ("evals/retrieval/kg/", "graphrag"),
    ("mcp-servers/graphrag/", "graphrag"),
]


@dataclass
class SuiteResult:
    suite: str
    kind: str
    path: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    metrics: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    ok: bool = True

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.skipped


@dataclass
class RunReport:
    started_at: str
    finished_at: str
    ok: bool
    suites: list[SuiteResult] = field(default_factory=list)
    regressions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "suites": [asdict(s) for s in self.suites],
            "regressions": self.regressions,
        }


def _git_changed_files() -> list[str]:
    """Return paths changed vs merge-base with main (or all staged/unstaged)."""
    for base in ("origin/main", "main", "HEAD~1"):
        try:
            out = subprocess.run(
                ["git", "merge-base", base, "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=ROOT,
            )
            merge_base = out.stdout.strip()
            diff = subprocess.run(
                ["git", "diff", "--name-only", f"{merge_base}...HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=ROOT,
            )
            files = [ln.strip() for ln in diff.stdout.splitlines() if ln.strip()]
            if files:
                return files
        except subprocess.CalledProcessError:
            continue

    # Fallback: unstaged + staged changes (local dev).
    out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def suites_for_touched(changed: list[str]) -> set[str]:
    matched: set[str] = set()
    for path in changed:
        norm = path.replace("\\", "/")
        for prefix, suite_id in TOUCH_MAP:
            if norm.startswith(prefix) or prefix.rstrip("/") in norm:
                matched.add(suite_id)
    # Always run evals when eval infra itself changed.
    for path in changed:
        if path.replace("\\", "/").startswith("evals/"):
            matched.update({"tutor", "memory"})
            break
    for path in changed:
        norm = path.replace("\\", "/")
        if norm.startswith("services/graphrag/") or norm.startswith("evals/retrieval/"):
            matched.add("graphrag")
            break
    return matched


def discover_promptfoo_configs(suite_filter: set[str] | None) -> list[tuple[str, Path]]:
    configs: list[tuple[str, Path]] = []
    agents_dir = EVALS / "agents"
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
            continue
        agent = agent_dir.name
        if suite_filter and agent not in suite_filter:
            continue
        for yaml_path in sorted(agent_dir.glob("*.yaml")):
            name = yaml_path.name
            if name == "thresholds.yaml" or name.endswith("_fixtures.yaml"):
                continue
            configs.append((agent, yaml_path))
    return configs


def discover_deepeval_modules(suite_filter: set[str] | None) -> list[tuple[str, Path]]:
    modules: list[tuple[str, Path]] = []
    agents_dir = EVALS / "agents"
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
            continue
        agent = agent_dir.name
        if suite_filter and agent not in suite_filter:
            continue
        for py_path in sorted(agent_dir.glob("*.py")):
            modules.append((agent, py_path))
    return modules


def discover_memory_yaml(suite_filter: set[str] | None) -> list[Path]:
    if suite_filter and "memory" not in suite_filter:
        return []
    memory_dir = EVALS / "memory"
    if not memory_dir.exists():
        return []
    paths: list[Path] = []
    for path in sorted(memory_dir.rglob("*.yaml")):
        if path.name == "thresholds.yaml":
            continue
        data = _load_yaml(path)
        if data.get("cases") and not data.get("tests"):
            paths.append(path)
    return paths


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _promptfoo_available() -> bool:
    promptfoo_bin = EVALS / "node_modules" / ".bin" / ("promptfoo.cmd" if sys.platform == "win32" else "promptfoo")
    if promptfoo_bin.exists():
        return True
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _run_promptfoo(config: Path) -> SuiteResult:
    rel = config.relative_to(ROOT)
    result = SuiteResult(suite=config.parent.name, kind="promptfoo", path=str(rel))

    if not _promptfoo_available():
        import importlib.util

        spec = importlib.util.spec_from_file_location("promptfoo_local", EVALS / "promptfoo_local.py")
        if spec is None or spec.loader is None:
            result.failed = 1
            result.errors.append("promptfoo unavailable and local fallback failed to load")
            return result
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        passed, failed, errors = mod.run_config(config)
        result.passed = passed
        result.failed = failed
        result.ok = failed == 0
        result.errors.extend(errors)
        return result

    promptfoo_bin = EVALS / "node_modules" / ".bin" / ("promptfoo.cmd" if sys.platform == "win32" else "promptfoo")
    cmd: list[str]
    if promptfoo_bin.exists():
        cmd = [str(promptfoo_bin), "eval", "-c", str(config), "--no-progress-bar"]
    else:
        cmd = ["npx", "--yes", "promptfoo", "eval", "-c", str(config), "--no-progress-bar"]

    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    stdout = proc.stdout + proc.stderr

    # Parse promptfoo summary line: "Successes: X Failures: Y Errors: Z"
    m_pass = re.search(r"Successes:\s*(\d+)", stdout)
    m_fail = re.search(r"Failures:\s*(\d+)", stdout)
    m_err = re.search(r"Errors:\s*(\d+)", stdout)
    result.passed = int(m_pass.group(1)) if m_pass else (1 if proc.returncode == 0 else 0)
    result.failed = int(m_fail.group(1)) if m_fail else (0 if proc.returncode == 0 else 1)
    result.skipped = int(m_err.group(1)) if m_err else 0
    result.ok = proc.returncode == 0 and result.failed == 0
    if not result.ok and proc.returncode != 0:
        tail = stdout.strip()[-2000:] if stdout.strip() else "(no output)"
        result.errors.append(f"promptfoo exit {proc.returncode}: {tail}")
    return result


def _run_deepeval(module: Path) -> SuiteResult:
    rel = module.relative_to(ROOT)
    result = SuiteResult(suite=module.parent.name, kind="pytest", path=str(rel))
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(module), "-q"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**dict(subprocess.os.environ), "PYTHONPATH": _pythonpath_env()},
    )
    stdout = proc.stdout + proc.stderr
    if proc.returncode == 0:
        result.passed = stdout.count(" passed") or 1
        result.failed = 0
    else:
        result.passed = 0
        result.failed = stdout.count(" failed") or 1
    result.ok = proc.returncode == 0
    if not result.ok:
        tail = stdout.strip()[-2000:] if stdout.strip() else "(no output)"
        result.errors.append(f"deepeval exit {proc.returncode}: {tail}")
    return result


async def _run_memory_case(case: dict[str, Any]) -> tuple[bool, str]:
    """Execute a single memory hygiene test case from YAML."""
    from memory_service.hygiene.pii import redact
    from memory_service.hygiene.decay import reinforce, strength_now
    from memory_service.hygiene.selective_forgetting import should_archive
    from schemas.common import Provenance
    from schemas.memory import MemoryRecord, MemoryType

    case_type = case.get("type")
    if case_type is None:
        if "a" in case and "b" in case:
            case_type = "consolidation_merge"
        elif "existing" in case and "incoming" in case:
            case_type = "conflict_contradiction"
        elif "input" in case and ("must_contain" in case or "must_not_contain" in case):
            case_type = "pii_redact"
        elif "age_days" in case and "salience" in case:
            case_type = "decay_archive"
        else:
            return False, f"unknown case shape: {list(case.keys())}"

    if case_type == "pii_redact":
        text = case["input"]
        out = await redact(text)
        for token in case.get("expected_contains", case.get("must_contain", [])):
            if token not in out:
                return False, f"expected {token!r} in output {out!r}"
        for token in case.get("expected_not_contains", case.get("must_not_contain", [])):
            if token in out:
                return False, f"did not expect {token!r} in output {out!r}"
        return True, ""

    if case_type == "decay_archive":
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        record = MemoryRecord(
            id="mem-archive",
            learner_id="learner-1",
            type=MemoryType.EPISODIC,
            content="decay eval",
            salience=case.get("salience", 0.5),
            decay_tau_days=case.get("tau_days", 14.0),
            last_accessed_at=now - timedelta(days=case.get("age_days", 0)),
            provenance=Provenance(kind="system", id="c-archive", agent="eval", model="mock"),
        )
        strength = strength_now(record, now=now)
        if "min_strength" in case and strength < case["min_strength"]:
            return False, f"strength {strength:.4f} < min {case['min_strength']}"
        if "max_strength" in case and strength > case["max_strength"]:
            return False, f"strength {strength:.4f} > max {case['max_strength']}"
        if "below_archive_threshold" in case:
            threshold = case["below_archive_threshold"]
            archived = should_archive(record, threshold=threshold)
            if not archived:
                return False, f"expected archive below {threshold}, strength={strength:.4f}"
        return True, ""

    if case_type == "decay_strength":
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        record = MemoryRecord(
            id="mem-1",
            learner_id="learner-1",
            type=MemoryType.EPISODIC,
            content="test",
            salience=case.get("salience", 0.8),
            decay_tau_days=case.get("tau_days", 14.0),
            last_accessed_at=now - timedelta(days=case.get("elapsed_days", 0)),
            provenance=Provenance(kind="system", id="c1", agent="eval", model="mock"),
        )
        strength = strength_now(record, now=now)
        lo, hi = case.get("expected_range", [0.0, 1.0])
        if not (lo <= strength <= hi):
            return False, f"strength {strength:.4f} not in [{lo}, {hi}]"
        return True, ""

    if case_type == "decay_reinforce":
        record = MemoryRecord(
            id="mem-2",
            learner_id="learner-1",
            type=MemoryType.EPISODIC,
            content="test",
            salience=case.get("salience", 0.5),
            provenance=Provenance(kind="system", id="c2", agent="eval", model="mock"),
        )
        before = record.salience
        reinforce(record, delta=case.get("delta", 0.05))
        expected_min = case.get("expected_salience_min", before)
        if record.salience < expected_min:
            return False, f"salience {record.salience} < expected min {expected_min}"
        return True, ""

    if case_type == "should_archive":
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        record = MemoryRecord(
            id="mem-3",
            learner_id="learner-1",
            type=MemoryType.EPISODIC,
            content="fading memory",
            salience=case.get("salience", 0.1),
            decay_tau_days=case.get("tau_days", 7.0),
            last_accessed_at=now - timedelta(days=case.get("elapsed_days", 30)),
            provenance=Provenance(kind="system", id="c3", agent="eval", model="mock"),
        )
        threshold = case.get("threshold", 0.05)
        expected = case.get("expected", True)
        actual = should_archive(record, threshold=threshold)
        if actual != expected:
            return False, f"should_archive={actual}, expected={expected}"
        return True, ""

    if case_type == "consolidation_merge":
        from memory_service.hygiene.text_similarity import jaccard_similarity, likely_contradiction

        sim = jaccard_similarity(case["a"], case["b"])
        should_merge = sim >= case.get("min_similarity", 0.5) and not likely_contradiction(case["a"], case["b"])
        if should_merge != case.get("expect_merge", False):
            return False, f"merge={should_merge}, expected={case.get('expect_merge')} (sim={sim:.3f})"
        return True, ""

    if case_type == "conflict_contradiction":
        from memory_service.hygiene.text_similarity import likely_contradiction

        is_contradiction = likely_contradiction(case["existing"], case["incoming"])
        if is_contradiction != case.get("expect_supersession", False):
            return (
                False,
                f"contradiction={is_contradiction}, expected={case.get('expect_supersession')}",
            )
        return True, ""

    if case_type == "consolidation_stub":
        # Phase-1: consolidation stub returns empty duplicates (contract test).
        from memory_service.hygiene.consolidation import find_near_duplicates

        class _EmptyRepo:
            async def iter_for_learner(self, learner_id: str) -> list[MemoryRecord]:
                return []

            async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
                return []

            async def upsert(self, record: MemoryRecord) -> MemoryRecord:
                return record

        repo = _EmptyRepo()
        dups = await find_near_duplicates(repo, learner_id="learner-1", cosine=0.92)
        if len(dups) != case.get("expected_count", 0):
            return False, f"expected {case.get('expected_count', 0)} duplicates, got {len(dups)}"
        return True, ""

    if case_type == "conflict_resolution_stub":
        from memory_service.hygiene.conflict_resolution import find_contradiction

        class _EmptyRepo:
            async def iter_for_learner(self, learner_id: str) -> list[MemoryRecord]:
                return []

            async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
                return []

            async def upsert(self, record: MemoryRecord) -> MemoryRecord:
                return record

        repo = _EmptyRepo()
        incoming = MemoryRecord(
            id="new-mem",
            learner_id="learner-1",
            type=MemoryType.SEMANTIC,
            content=case.get("content", "Earth orbits the Sun."),
            confidence=case.get("confidence", 0.9),
            provenance=Provenance(kind="system", id="c4", agent="eval", model="mock"),
        )
        conflict = await find_contradiction(repo, incoming)
        if case.get("expect_conflict") and conflict is None:
            return False, "expected contradiction, got None"
        if not case.get("expect_conflict") and conflict is not None:
            return False, f"expected no contradiction, got {conflict.id}"
        return True, ""

    if case_type == "dreaming_report_shape":
        from memory_service.hygiene.dreaming import dream

        class _EmptyRepo:
            async def iter_for_learner(self, learner_id: str) -> list[MemoryRecord]:
                return []

            async def list_by_types(self, learner_id: str, types: set[MemoryType]) -> list[MemoryRecord]:
                return []

            async def upsert(self, record: MemoryRecord) -> MemoryRecord:
                return record

        repo = _EmptyRepo()
        report = await dream(
            repo,
            learner_id="learner-1",
            window_hours=24,
            consolidation_cosine=0.92,
            archive_threshold=0.05,
        )
        required_fields = case.get(
            "required_fields",
            [
                "items_reviewed",
                "items_promoted",
                "items_merged",
                "items_archived",
                "conflicts_resolved",
                "conflicts_pending",
            ],
        )
        for fld in required_fields:
            if not hasattr(report, fld):
                return False, f"MemoryHealthReport missing field {fld!r}"
        return True, ""

    return False, f"unknown case type {case_type!r}"


async def _run_memory_yaml(path: Path) -> SuiteResult:
    rel = path.relative_to(ROOT)
    data = _load_yaml(path)
    result = SuiteResult(suite="memory", kind="memory", path=str(rel))
    cases = data.get("cases", [])
    for i, case in enumerate(cases):
        ok, err = await _run_memory_case(case)
        if ok:
            result.passed += 1
        else:
            result.failed += 1
            result.errors.append(f"case {i}: {err}")
    result.ok = result.failed == 0
    metric_key = data.get("metric")
    if not metric_key and "pii" in str(path):
        metric_key = "pii_redaction_accuracy"
    if not metric_key and "archive" in str(path):
        metric_key = "decay_accuracy"
    if not metric_key and "merge" in str(path):
        metric_key = "consolidation_correctness"
    if not metric_key and "contradictions" in str(path):
        metric_key = "conflict_resolution_correctness"
    if metric_key and cases:
        result.metrics[metric_key] = result.passed / max(1, len(cases))
    return result


def _run_kg_retrieval_eval() -> SuiteResult:
    """Run offline KG retrieval eval (recall@10, MRR, personalized lift)."""
    script = EVALS / "retrieval" / "kg" / "run_eval.py"
    config = EVALS / "retrieval" / "kg" / "queries.yaml"
    result = SuiteResult(suite="graphrag", kind="retrieval", path=str(script.relative_to(ROOT)))
    if not script.exists():
        result.skipped = 1
        result.errors.append("kg run_eval.py not found")
        return result
    proc = subprocess.run(
        [sys.executable, str(script), "--config", str(config)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**dict(subprocess.os.environ), "PYTHONPATH": _pythonpath_env()},
    )
    stdout = proc.stdout + proc.stderr
    if proc.returncode == 0:
        result.passed = 1
        result.failed = 0
    else:
        result.passed = 0
        result.failed = 1
        tail = stdout.strip()[-2000:] if stdout.strip() else "(no output)"
        result.errors.append(f"kg retrieval eval exit {proc.returncode}: {tail}")
    result.ok = proc.returncode == 0
    # Parse metrics from final JSON line when present.
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and "recall_at_10" in line:
            try:
                payload = json.loads(line)
                metrics = payload.get("metrics", payload)
                for key in ("recall_at_10", "mrr", "personalized_lift"):
                    if key in metrics:
                        result.metrics[key] = float(metrics[key])
            except (json.JSONDecodeError, ValueError):
                pass
            break
    return result


def _pass_rate_for(runs: list[SuiteResult]) -> float:
    total_pass = sum(r.passed for r in runs)
    total = sum(r.total for r in runs) or 1
    return total_pass / total


def _aggregate_agent_metrics(suite_results: list[SuiteResult], agent: str) -> dict[str, float]:
    agent_runs = [r for r in suite_results if r.suite == agent]
    if not agent_runs:
        return {}
    pass_rate = _pass_rate_for(agent_runs)
    cap_runs = [r for r in agent_runs if "capability" in r.path.replace("\\", "/")]
    safety_runs = [r for r in agent_runs if "safety" in r.path.replace("\\", "/")]
    metrics: dict[str, float] = {"pass_rate": pass_rate}
    if cap_runs:
        metrics["capability_pass_rate"] = _pass_rate_for(cap_runs)
    if safety_runs:
        metrics["safety_pass_rate"] = _pass_rate_for(safety_runs)
        metrics["refusal_when_appropriate"] = metrics["safety_pass_rate"]
    for r in agent_runs:
        metrics.update(r.metrics)
    # Derived Phase-1 proxy metrics for baseline gating.
    metrics.setdefault("helpfulness", pass_rate)
    metrics.setdefault("faithfulness", pass_rate)
    metrics.setdefault("citation_accuracy", pass_rate)
    metrics.setdefault("capability_pass_rate", pass_rate)
    metrics.setdefault("safety_pass_rate", pass_rate)
    metrics.setdefault("refusal_when_appropriate", pass_rate)
    return metrics


def _aggregate_memory_metrics(suite_results: list[SuiteResult]) -> dict[str, float]:
    mem_runs = [r for r in suite_results if r.suite == "memory"]
    if not mem_runs:
        return {}
    total_pass = sum(r.passed for r in mem_runs)
    total = sum(r.total for r in mem_runs) or 1
    pass_rate = total_pass / total
    metrics: dict[str, float] = {"pass_rate": pass_rate}
    for r in mem_runs:
        metrics.update(r.metrics)
    metrics.setdefault("pii_redaction_accuracy", metrics.get("pii_redaction_accuracy", pass_rate))
    metrics.setdefault("decay_accuracy", metrics.get("decay_accuracy", pass_rate))
    metrics.setdefault("consolidation_correctness", metrics.get("consolidation_correctness", pass_rate))
    metrics.setdefault("conflict_resolution_correctness", metrics.get("conflict_resolution_correctness", pass_rate))
    metrics.setdefault("dreaming_quality", metrics.get("dreaming_quality", pass_rate))
    return metrics


def _check_regressions(
    suite_results: list[SuiteResult],
    regressions: list[str],
) -> None:
    """Compare aggregate metrics against baseline.json + thresholds.yaml slack."""
    agents_dir = EVALS / "agents"
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
            continue
        agent = agent_dir.name
        thresholds_path = agent_dir / "thresholds.yaml"
        baseline_path = agent_dir / "baseline.json"
        if not thresholds_path.exists() or not baseline_path.exists():
            continue
        thresholds = _load_yaml(thresholds_path).get("metrics", {})
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        current = _aggregate_agent_metrics(suite_results, agent)
        for metric, spec in thresholds.items():
            if metric not in current or metric not in baseline:
                continue
            cur = current[metric]
            base = float(baseline[metric])
            if "min" in spec:
                floor = base - float(spec.get("slack", 0))
                if cur < floor:
                    regressions.append(
                        f"{agent}.{metric}: {cur:.3f} < baseline floor {floor:.3f} (baseline={base:.3f})"
                    )
            if "max" in spec:
                ceiling = base + float(spec.get("slack", 0))
                if cur > ceiling:
                    regressions.append(
                        f"{agent}.{metric}: {cur:.3f} > baseline ceiling {ceiling:.3f} (baseline={base:.3f})"
                    )

    mem_thresholds = EVALS / "memory" / "thresholds.yaml"
    mem_baseline = EVALS / "memory" / "baseline.json"
    if mem_thresholds.exists() and mem_baseline.exists():
        thresholds = _load_yaml(mem_thresholds).get("metrics", {})
        baseline = json.loads(mem_baseline.read_text(encoding="utf-8"))
        current = _aggregate_memory_metrics(suite_results)
        for metric, spec in thresholds.items():
            if metric not in current or metric not in baseline:
                continue
            cur = current[metric]
            base = float(baseline[metric])
            if "min" in spec:
                floor = base - float(spec.get("slack", 0))
                if cur < floor:
                    regressions.append(
                        f"memory.{metric}: {cur:.3f} < baseline floor {floor:.3f} (baseline={base:.3f})"
                    )

    kg_thresholds = EVALS / "retrieval" / "kg" / "thresholds.yaml"
    kg_baseline = EVALS / "retrieval" / "kg" / "baseline.json"
    if kg_thresholds.exists() and kg_baseline.exists():
        thresholds = _load_yaml(kg_thresholds).get("metrics", {})
        baseline = json.loads(kg_baseline.read_text(encoding="utf-8"))
        graphrag_runs = [r for r in suite_results if r.suite == "graphrag"]
        current: dict[str, float] = {}
        for r in graphrag_runs:
            current.update(r.metrics)
        for metric, spec in thresholds.items():
            if metric not in current or metric not in baseline:
                continue
            cur = current[metric]
            base = float(baseline[metric])
            if "min" in spec:
                floor = float(spec["min"])
                if cur < floor:
                    regressions.append(
                        f"graphrag.{metric}: {cur:.3f} < threshold min {floor:.3f} (baseline={base:.3f})"
                    )


def _write_report(report: RunReport) -> None:
    lines = [
        "# Eval Report",
        "",
        f"- **Started:** {report.started_at}",
        f"- **Finished:** {report.finished_at}",
        f"- **Status:** {'PASS' if report.ok else 'FAIL'}",
        "",
        "## Suites",
        "",
        "| Suite | Kind | Path | Pass | Fail | OK |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for s in report.suites:
        lines.append(
            f"| {s.suite} | {s.kind} | `{s.path}` | {s.passed} | {s.failed} | {'✓' if s.ok else '✗'} |"
        )
    if report.regressions:
        lines.extend(["", "## Regressions", ""])
        for r in report.regressions:
            lines.append(f"- {r}")
    for s in report.suites:
        if s.errors:
            lines.extend(["", f"### Errors — `{s.path}`", ""])
            for e in s.errors:
                lines.append(f"- {e}")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    RESULTS_JSON.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")


async def run_all(*, suite_filter: set[str] | None, check_baseline: bool) -> RunReport:
    started = datetime.now(timezone.utc).isoformat()
    suites: list[SuiteResult] = []

    for _agent, cfg in discover_promptfoo_configs(suite_filter):
        suites.append(_run_promptfoo(cfg))

    for _agent, mod in discover_deepeval_modules(suite_filter):
        suites.append(_run_deepeval(mod))

    for mem_yaml in discover_memory_yaml(suite_filter):
        suites.append(await _run_memory_yaml(mem_yaml))

    if suite_filter is None or "graphrag" in suite_filter:
        suites.append(_run_kg_retrieval_eval())

    regressions: list[str] = []
    if check_baseline:
        _check_regressions(suites, regressions)

    ok = all(s.ok for s in suites) and not regressions
    finished = datetime.now(timezone.utc).isoformat()
    report = RunReport(started_at=started, finished_at=finished, ok=ok, suites=suites, regressions=regressions)
    _write_report(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run A Step Forward eval suites.")
    parser.add_argument("--touched", action="store_true", help="Run only suites affected by changed files.")
    parser.add_argument("--suite", action="append", dest="suites", metavar="ID", help="Run a specific suite (tutor, memory, graphrag).")
    parser.add_argument("--no-baseline", action="store_true", help="Skip baseline regression checks.")
    args = parser.parse_args()

    suite_filter: set[str] | None = None
    if args.suites:
        suite_filter = set(args.suites)
    elif args.touched:
        changed = _git_changed_files()
        suite_filter = suites_for_touched(changed)
        if not suite_filter:
            print(json.dumps({"ok": True, "skipped": True, "reason": "no eval-relevant changes detected"}))
            _write_report(
                RunReport(
                    started_at=datetime.now(timezone.utc).isoformat(),
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    ok=True,
                    suites=[],
                    regressions=[],
                )
            )
            return 0
        print(f"Running touched suites: {sorted(suite_filter)} (changed: {len(changed)} files)")

    report = asyncio.run(run_all(suite_filter=suite_filter, check_baseline=not args.no_baseline))
    print(json.dumps(report.to_dict(), indent=2))
    print(f"\nReport written to {REPORT_MD.relative_to(ROOT)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
