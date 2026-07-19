# Sub-agent Briefs

Each file here is a **self-contained ticket** for a stream of work on
**A Step Forward**. Briefs are **not** auto-discovered by Cursor as subagents.

## How Cursor loads subagents

Cursor-native custom subagents live in **`.cursor/agents/`** (YAML frontmatter
+ system prompt). Those agent files tell the model to read the matching brief
in this folder plus the relevant skills under `.cursor/skills/`.

| Stream | Brief (this folder) | Cursor agent (`.cursor/agents/`) |
|--------|---------------------|----------------------------------|
| Frontend | `01-frontend.md` | `frontend.md` |
| Backend / API | `02-backend-api.md` | `backend-api.md` |
| Agents framework | `03-agents.md` | `agents-framework.md` |
| Memory | `04-memory.md` | `memory.md` |
| GraphRAG | `05-graphrag.md` | `graphrag.md` |
| MCP servers | `06-mcp-servers.md` | `mcp-servers.md` |
| Curriculum | `07-curriculum.md` | `curriculum.md` |
| Evals & QA | `08-evals-qa.md` | `evals-qa.md` |
| Infra / DevOps | `09-infra.md` | `infra.md` |
| Security / Safety | `10-security-safety.md` | `security-safety.md` |
| Architecture Steward | `24-architecture-steward.md` | `architecture-steward.md` |
| Code Reviewer | `25-code-reviewer.md` | `code-reviewer.md` |
| Coordinator | `15-coordinator-directive.md` | `coordinator.md` |

## Brief contents

Each brief typically includes goal, in/out of scope, contracts, acceptance
criteria, required reading, and a starter prompt.

**Manual dispatch:** open a new chat, or ask the parent agent to use the
matching `.cursor/agents/` subagent. Background long-running streams when sensible.
