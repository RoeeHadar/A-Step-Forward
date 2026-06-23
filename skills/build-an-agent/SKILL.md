---
name: build-an-agent
description: How to author a new runtime agent in packages/agents using the base class, typed I/O, MCP tools, versioned prompt, memory policy, budgets, and evals. Read this BEFORE creating or modifying any agent under packages/agents/.
---

# Build an Agent

## When to use
Whenever you create a new agent, modify an existing one, or refactor agent composition.

## Steps

### 1. Pick the slot
Add the agent under one of:
- `packages/agents/agents/learner_facing/<agent>/`
- `packages/agents/agents/system/<agent>/`

### 2. Files to create
```
__init__.py
agent.py        # extends Agent
input.py        # Pydantic Input
output.py       # Pydantic Output
budget.py       # token/latency/cost budget
tools.py        # MCP/function tool list
memory_policy.py
```

### 3. Versioned prompt
- Create `prompts/<agent>/v1.md` (system prompt).
- Reference it from `agent.py` via `prompt_version = "v1"`.
- Never edit a shipped `v<n>.md` — bump version instead.

### 4. Wire base class
```python
from agents.base.agent import Agent
from agents.base.memory_policy import MemoryPolicy, MemoryType
from agents.base.llm import LLM
from agents.base.tools import mcp_tool
from .input import TutorInput
from .output import TutorOutput
from .budget import BUDGET

class TutorAgent(Agent[TutorInput, TutorOutput]):
    name = "tutor"
    prompt_version = "v1"
    tools = [
        mcp_tool("memory", "memory.search"),
        mcp_tool("graphrag", "kg.related_concepts"),
        mcp_tool("curriculum", "curriculum.get_lesson"),
    ]
    memory_policy = MemoryPolicy(
        read={MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL, MemoryType.REFLECTIVE},
        write={MemoryType.EPISODIC, MemoryType.REFLECTIVE},
    )
    budget = BUDGET

    async def run(self, inp: TutorInput) -> TutorOutput:
        ...
```

### 5. Safety
- Wrap with `SafetyModeration.pre(inp)` and `SafetyModeration.post(out)` in the base class — do NOT bypass.

### 6. Register
- Add to `packages/agents/agents/__init__.AGENT_REGISTRY`.

### 7. Evals (required)
- `evals/agents/<agent>/capability.yaml` — promptfoo matrices.
- `evals/agents/<agent>/safety.yaml` — refusal + safety.
- `evals/agents/<agent>/citation.py` — DeepEval for citation accuracy where applicable.
- `evals/agents/<agent>/thresholds.yaml` — per-metric pass thresholds.

### 8. Tests
- `packages/agents/tests/test_<agent>.py` — unit tests for tool composition, schema validation, and budget enforcement.

### 9. PR
- Conventional commit: `feat(agents): add <agent>` or `feat(agents/tutor): v2 prompt`.
- PR body must paste eval summary.
- Run the `review-bugbot` skill.

## Pitfalls
- Don't instantiate Anthropic/OpenAI SDKs directly. Always go through `agents/base/llm.py`.
- Don't read/write memory tables directly. Use the Memory MCP or service.
- Don't call other agents directly. Always go through the Orchestrator.
- Don't put logic in the system prompt that belongs in code (e.g., routing).
