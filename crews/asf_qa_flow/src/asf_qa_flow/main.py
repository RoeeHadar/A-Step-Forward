#!/usr/bin/env python
"""A Step Forward — multi-crew QA Flow (contract + optional CrewAI runtime).

This round's **runtime is Cursor Auto** (see docs/qa/rounds/current.json).
CrewAI YAML under crews/*/config is the agent/task contract.
`crewai run` against external LLMs is NOT used for the active QA round.

Flow shape (for reference / future):
  Tester crews (×5) → DeliberationCrew → Coordinator (human/Cursor) decides

Inputs (must match docs/qa/rounds/current.json):
    round_id, seed_variant, suite_focus, target_env, suites
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from crewai.flow.flow import Flow, and_, listen, router, start

from asf_qa_flow.crews.deliberation_crew.deliberation_crew import DeliberationCrew
from asf_qa_flow.crews.evals_tester_crew.evals_tester_crew import EvalsTesterCrew
from asf_qa_flow.crews.integration_tester_crew.integration_tester_crew import (
    IntegrationTesterCrew,
)
from asf_qa_flow.crews.qa_tester_crew.qa_tester_crew import QaTesterCrew
from asf_qa_flow.crews.security_tester_crew.security_tester_crew import (
    SecurityTesterCrew,
)
from asf_qa_flow.crews.ui_tester_crew.ui_tester_crew import UiTesterCrew


class QaFlowState(BaseModel):
    round_id: str = "2026-07-21-adr0010-building"
    seed_variant: str = "building"
    suite_focus: str = "pilot + ADR-0010"
    target_env: str = "local"
    suites: str = "all"
    integration_report: str = ""
    ui_report: str = ""
    qa_report: str = ""
    security_report: str = ""
    evals_report: str = ""
    deliberation_brief: str = ""
    executive_summary: str = ""


def _suite_set(suites: str) -> set[str]:
    raw = (suites or "all").strip().lower()
    if raw in {"all", "*"}:
        return {"integration", "ui", "qa", "security", "evals"}
    return {s.strip() for s in raw.split(",") if s.strip()}


def _crew_inputs(state: QaFlowState) -> dict[str, str]:
    return {
        "round_id": state.round_id,
        "seed_variant": state.seed_variant,
        "suite_focus": state.suite_focus,
        "target_env": state.target_env,
    }


class AsfQaFlow(Flow[QaFlowState]):
    """Reference Flow — prefer Cursor Auto starters in docs/qa/rounds/STARTER_PROMPTS.md."""

    @start()
    def bootstrap(self, crewai_trigger_payload: dict | None = None):
        if crewai_trigger_payload:
            for key in (
                "round_id",
                "seed_variant",
                "suite_focus",
                "target_env",
                "suites",
            ):
                if key in crewai_trigger_payload and crewai_trigger_payload[key]:
                    setattr(self.state, key, crewai_trigger_payload[key])
        print(
            f"ASF QA Flow — round={self.state.round_id!r} "
            f"variant={self.state.seed_variant!r} "
            f"focus={self.state.suite_focus!r} env={self.state.target_env!r}"
        )
        if self.state.seed_variant != "building":
            print(
                "WARNING: charter for this round expects seed_variant=building. "
                "Coordinator must update docs/qa/rounds/current.json before proceeding."
            )

    @router(bootstrap)
    def route_suites(self):
        return "run_selected"

    @listen("run_selected")
    def run_integration(self):
        if "integration" not in _suite_set(self.state.suites):
            return
        result = (
            IntegrationTesterCrew()
            .crew()
            .kickoff(inputs=_crew_inputs(self.state))
        )
        self.state.integration_report = result.raw

    @listen("run_selected")
    def run_ui(self):
        if "ui" not in _suite_set(self.state.suites):
            return
        result = UiTesterCrew().crew().kickoff(inputs=_crew_inputs(self.state))
        self.state.ui_report = result.raw

    @listen("run_selected")
    def run_qa(self):
        if "qa" not in _suite_set(self.state.suites):
            return
        result = QaTesterCrew().crew().kickoff(inputs=_crew_inputs(self.state))
        self.state.qa_report = result.raw

    @listen("run_selected")
    def run_security(self):
        if "security" not in _suite_set(self.state.suites):
            return
        result = (
            SecurityTesterCrew()
            .crew()
            .kickoff(inputs=_crew_inputs(self.state))
        )
        self.state.security_report = result.raw

    @listen("run_selected")
    def run_evals(self):
        if "evals" not in _suite_set(self.state.suites):
            return
        result = EvalsTesterCrew().crew().kickoff(inputs=_crew_inputs(self.state))
        self.state.evals_report = result.raw

    @listen(and_(run_integration, run_ui, run_qa, run_security, run_evals))
    def run_deliberation(self):
        print("→ DeliberationCrew (advocates + facilitator; no binding decision)")
        result = (
            DeliberationCrew()
            .crew()
            .kickoff(inputs=_crew_inputs(self.state))
        )
        self.state.deliberation_brief = result.raw

    @listen(run_deliberation)
    def synthesize(self):
        sections = [
            ("Integration", self.state.integration_report),
            ("UI / E2E", self.state.ui_report),
            ("Product QA", self.state.qa_report),
            ("Security", self.state.security_report),
            ("Evals", self.state.evals_report),
            ("Deliberation (non-binding)", self.state.deliberation_brief),
        ]
        lines = [
            "# ASF QA Executive Summary",
            "",
            f"- **Round:** {self.state.round_id}",
            f"- **seed_variant:** {self.state.seed_variant}",
            f"- **Focus:** {self.state.suite_focus}",
            f"- **Env:** {self.state.target_env}",
            "",
            "_Coordinator must record the binding decision in iterations/N.md._",
            "",
        ]
        for title, body in sections:
            if not body:
                continue
            lines.append(f"## {title}")
            lines.append("")
            lines.append(body.strip())
            lines.append("")

        self.state.executive_summary = "\n".join(lines)
        out = Path("output")
        out.mkdir(exist_ok=True)
        (out / "executive_summary.md").write_text(
            self.state.executive_summary, encoding="utf-8"
        )
        print("Saved output/executive_summary.md — awaiting Coordinator decision")


def kickoff():
    print(
        "NOTE: Active QA round uses Cursor Auto "
        "(docs/qa/rounds/STARTER_PROMPTS.md), not this kickoff."
    )
    AsfQaFlow().kickoff(
        inputs={
            "round_id": "2026-07-21-adr0010-building",
            "seed_variant": "building",
            "suite_focus": "pilot + ADR-0010",
            "target_env": "local",
            "suites": "all",
        }
    )


def plot():
    AsfQaFlow().plot("asf_qa_flow")


def run_with_trigger():
    import json
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: run_with_trigger '<json payload>'")
    payload = json.loads(sys.argv[1])
    AsfQaFlow().kickoff(inputs={"crewai_trigger_payload": payload})


if __name__ == "__main__":
    kickoff()
