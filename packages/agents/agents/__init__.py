"""Runtime AI agents.

`AGENT_REGISTRY` is the orchestrator's source of truth for available agents.
`AGENT_FACTORIES` maps agent names to callable factories for agents that have
been implemented. Sub-agent 03-agents fills in real agent classes over time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from schemas.agents import AgentManifest, AgentName, Budget, ToolRef
from schemas.memory import MemoryAccessPolicy, MemoryType

if TYPE_CHECKING:
    from agents.base.agent import Agent

AgentFactory = Callable[[], "Agent"]

def _manifest(
    name: AgentName,
    description: str,
    *,
    primary_model: str = "claude-sonnet-4-5",
    fallback_model: str | None = "gpt-5-mini",
    tools: list[ToolRef] | None = None,
    read: set[MemoryType] | None = None,
    write: set[MemoryType] | None = None,
) -> AgentManifest:
    return AgentManifest(
        name=name,
        description=description,
        prompt_version="v1",
        primary_model=primary_model,
        fallback_model=fallback_model,
        tools=tools or [],
        memory_policy=MemoryAccessPolicy(read=read or set(), write=write or set()),
        budget=Budget(),
    )


AGENT_REGISTRY: dict[AgentName, AgentManifest] = {
    AgentName.TUTOR: _manifest(
        AgentName.TUTOR,
        "Conducts adaptive Socratic lessons and worked examples.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="memory", name="memory.write"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
            ToolRef(server="curriculum", name="curriculum.get_lesson"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL, MemoryType.REFLECTIVE},
        write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
    ),
    AgentName.MENTOR: _manifest(
        AgentName.MENTOR,
        "Goal setting, motivation, study habits, accountability.",
        read={MemoryType.SEMANTIC, MemoryType.AFFECTIVE, MemoryType.PROCEDURAL},
        write={MemoryType.EPISODIC, MemoryType.SEMANTIC},
    ),
    AgentName.COACH: _manifest(
        AgentName.COACH,
        "Drills, practice, FSRS-scheduled reviews.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="memory", name="memory.write"),
            ToolRef(server="progress", name="progress.get_due_reviews"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.PROCEDURAL, MemoryType.EPISODIC},
        write={MemoryType.EPISODIC, MemoryType.PROCEDURAL},
    ),
    AgentName.QA_EXPLAINER: _manifest(
        AgentName.QA_EXPLAINER,
        "Answers ad-hoc questions with citations from KG and memory.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
            ToolRef(server="graphrag", name="kg.retrieve_chunks"),
            ToolRef(server="curriculum", name="curriculum.get_lesson"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.SOURCE},
        write={MemoryType.EPISODIC},
    ),
    AgentName.REVIEWER: _manifest(
        AgentName.REVIEWER,
        "Reviews learner submissions (code, essays, solutions) with rubric.",
        primary_model="claude-opus-4-8",
        read={MemoryType.SEMANTIC, MemoryType.EPISODIC},
        write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
    ),
    AgentName.NOTE_TAKER: _manifest(
        AgentName.NOTE_TAKER,
        "Generates lesson recaps, study notes, flashcards.",
        primary_model="claude-haiku-4-5",
        read={MemoryType.EPISODIC, MemoryType.SEMANTIC},
        write={MemoryType.EPISODIC},
    ),
    AgentName.ENGAGEMENT: _manifest(
        AgentName.ENGAGEMENT,
        "Re-engages inactive learners via personalized nudges.",
        primary_model="claude-haiku-4-5",
        read={MemoryType.EPISODIC, MemoryType.AFFECTIVE, MemoryType.PROCEDURAL},
        write={MemoryType.EPISODIC},
    ),
    AgentName.ACCESSIBILITY: _manifest(
        AgentName.ACCESSIBILITY,
        "Translation, plain-language, dyslexia-friendly, TTS/STT.",
        read={MemoryType.PROCEDURAL, MemoryType.CONTEXT},
    ),
    AgentName.ORCHESTRATOR: _manifest(
        AgentName.ORCHESTRATOR,
        "Routes user intent to the right agent(s) and composes multi-agent flows.",
        read=set(MemoryType),
        write=set(),
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="memory", name="memory.timeline"),
        ],
    ),
    AgentName.CURRICULUM_DESIGNER: _manifest(
        AgentName.CURRICULUM_DESIGNER,
        "Builds personalized learning paths.",
        primary_model="claude-opus-4-8",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="curriculum", name="curriculum.get_path"),
            ToolRef(server="curriculum", name="curriculum.update_path"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
            ToolRef(server="progress", name="progress.get_mastery"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.PROCEDURAL, MemoryType.EPISODIC},
        write={MemoryType.SEMANTIC, MemoryType.REFLECTIVE},
    ),
    AgentName.ASSESSMENT_GENERATOR: _manifest(
        AgentName.ASSESSMENT_GENERATOR,
        "Creates quizzes, exercises, projects from objectives.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="curriculum", name="curriculum.get_objectives"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
        write={MemoryType.EPISODIC},
    ),
    AgentName.GRADER: _manifest(
        AgentName.GRADER,
        "Auto-grades objective questions + LLM-judges subjective with rubric.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="curriculum", name="curriculum.get_rubric"),
            ToolRef(server="curriculum", name="curriculum.get_objectives"),
        ],
        read={MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
        write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
    ),
    AgentName.PROGRESS_ANALYZER: _manifest(
        AgentName.PROGRESS_ANALYZER,
        "Identifies knowledge gaps, predicts at-risk learners, recommends interventions.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="memory", name="memory.timeline"),
            ToolRef(server="progress", name="progress.get_mastery"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
        ],
        read={MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
        write={MemoryType.SEMANTIC, MemoryType.REFLECTIVE},
    ),
    AgentName.CONTENT_CURATOR: _manifest(
        AgentName.CONTENT_CURATOR,
        "Sources from web/library, ranks quality, attaches to concepts.",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
            ToolRef(server="graphrag", name="web.search"),
            ToolRef(server="curriculum", name="curriculum.attach_resource"),
        ],
        read={MemoryType.SEMANTIC},
        write={MemoryType.SOURCE},
    ),
    AgentName.RESEARCH: _manifest(
        AgentName.RESEARCH,
        "Deep research with web search + RAG + KG; writes citations.",
        primary_model="claude-opus-4-8",
        tools=[
            ToolRef(server="memory", name="memory.search"),
            ToolRef(server="graphrag", name="kg.retrieve_chunks"),
            ToolRef(server="graphrag", name="kg.related_concepts"),
            ToolRef(server="graphrag", name="web.search"),
        ],
        read={MemoryType.SOURCE, MemoryType.SEMANTIC},
        write={MemoryType.SOURCE, MemoryType.REFLECTIVE},
    ),
    AgentName.KG_BUILDER: _manifest(
        AgentName.KG_BUILDER,
        "Extracts entities/relations from content into the KG.",
        primary_model="claude-haiku-4-5",
        tools=[
            ToolRef(server="graphrag", name="kg.extract_entities"),
            ToolRef(server="graphrag", name="kg.write_triples"),
            ToolRef(server="memory", name="memory.search"),
        ],
        read={MemoryType.SOURCE},
        write={MemoryType.SOURCE},
    ),
    AgentName.MEMORY_STEWARD: _manifest(
        AgentName.MEMORY_STEWARD,
        "Dreaming, consolidation, decay, conflict resolution, verification.",
        read=set(MemoryType),
        write={MemoryType.SEMANTIC, MemoryType.PROCEDURAL, MemoryType.REFLECTIVE},
    ),
    AgentName.SAFETY_MODERATION: _manifest(
        AgentName.SAFETY_MODERATION,
        "Content safety, jailbreak defense, age-appropriateness, PII checks.",
        primary_model="claude-haiku-4-5",
        read={MemoryType.AFFECTIVE, MemoryType.SEMANTIC},
        write=set(),
    ),
    AgentName.EVAL_AGENT: _manifest(
        AgentName.EVAL_AGENT,
        "Runs eval suites against new prompts/agents/builds.",
        read=set(),
        write=set(),
    ),
    AgentName.ANALYTICS_INSIGHTS: _manifest(
        AgentName.ANALYTICS_INSIGHTS,
        "Aggregates learner/system analytics for educators and admins.",
        read={MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL},
        write=set(),
    ),
}


def _tutor_factory() -> Agent:
    from agents.learner_facing.tutor import TutorAgent

    return TutorAgent()


def _qa_explainer_factory() -> Agent:
    from agents.learner_facing.qa_explainer import QAExplainerAgent

    return QAExplainerAgent()


def _coach_factory() -> Agent:
    from agents.learner_facing.coach import CoachAgent

    return CoachAgent()


def _curriculum_designer_factory() -> Agent:
    from agents.system.curriculum_designer import CurriculumDesignerAgent

    return CurriculumDesignerAgent()


def _assessment_generator_factory() -> Agent:
    from agents.system.assessment_generator import AssessmentGeneratorAgent

    return AssessmentGeneratorAgent()


def _grader_factory() -> Agent:
    from agents.system.grader import GraderAgent

    return GraderAgent()


def _progress_analyzer_factory() -> Agent:
    from agents.system.progress_analyzer import ProgressAnalyzerAgent

    return ProgressAnalyzerAgent()


PHASE1_AGENTS: frozenset[AgentName] = frozenset(
    {AgentName.TUTOR, AgentName.QA_EXPLAINER, AgentName.COACH}
)

PHASE2_AGENTS: frozenset[AgentName] = frozenset(
    {
        AgentName.CURRICULUM_DESIGNER,
        AgentName.ASSESSMENT_GENERATOR,
        AgentName.GRADER,
        AgentName.PROGRESS_ANALYZER,
    }
)

IMPLEMENTED_AGENTS: frozenset[AgentName] = PHASE1_AGENTS | PHASE2_AGENTS


AGENT_FACTORIES: dict[AgentName, AgentFactory] = {
    AgentName.TUTOR: _tutor_factory,
    AgentName.QA_EXPLAINER: _qa_explainer_factory,
    AgentName.COACH: _coach_factory,
    AgentName.CURRICULUM_DESIGNER: _curriculum_designer_factory,
    AgentName.ASSESSMENT_GENERATOR: _assessment_generator_factory,
    AgentName.GRADER: _grader_factory,
    AgentName.PROGRESS_ANALYZER: _progress_analyzer_factory,
}


__all__ = [
    "AGENT_REGISTRY",
    "AGENT_FACTORIES",
    "PHASE1_AGENTS",
    "PHASE2_AGENTS",
    "IMPLEMENTED_AGENTS",
    "AgentFactory",
]
