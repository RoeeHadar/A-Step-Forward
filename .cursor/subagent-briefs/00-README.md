# Sub-agent Briefs

Each file in this directory is a **self-contained ticket** for a Cursor sub-agent
(Composer 2.5 or Auto). Each brief contains:

- **Goal** — what success looks like in one paragraph.
- **In-scope files** — exact paths the agent should touch.
- **Out-of-scope** — what to avoid.
- **Contracts** — schemas, services, rules that must not be broken.
- **Acceptance criteria** — concrete checks.
- **Required reading** — PLAN.md sections + project skills to read first.
- **Starter prompt** — copy-paste prompt to launch the sub-agent.

Briefs:

| Stream                | File                              |
| --------------------- | --------------------------------- |
| Frontend              | `01-frontend.md`                  |
| Backend / API         | `02-backend-api.md`               |
| Agents framework      | `03-agents.md`                    |
| Memory service        | `04-memory.md`                    |
| GraphRAG              | `05-graphrag.md`                  |
| MCP servers           | `06-mcp-servers.md`               |
| Curriculum / Content  | `07-curriculum.md`                |
| Evals & QA            | `08-evals-qa.md`                  |
| Infra / DevOps        | `09-infra.md`                     |
| Security / Safety     | `10-security-safety.md`           |

**Dispatching a brief.** Open a new chat, switch model to **Composer 2.5** or **Cursor Auto**, and use the starter prompt at the bottom of the brief. Background long-running streams when sensible.
