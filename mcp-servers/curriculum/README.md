# curriculum MCP

Read-side surface over the Curriculum Service (`services/curriculum`). Same tool
surface used by agents at runtime and by Cursor during development (registered
in `.cursor/mcp.json` as `curriculum-project`).

## Tools

| Tool                          | Purpose                                                |
| ----------------------------- | ------------------------------------------------------ |
| `curriculum.list_courses`     | List published courses.                                |
| `curriculum.get_course`       | Fetch a course by id.                                  |
| `curriculum.get_lesson`       | Fetch a lesson by id.                                  |
| `curriculum.find_for_concept` | Find lessons that cover a concept.                     |
| `curriculum.suggest_path`     | Suggest a personalized learning path.                  |

## Run

```bash
python -m curriculum_mcp.server
```

Uses the official Python MCP SDK (stdio transport).

## Eval

See `evals/retrieval/curriculum_mcp_list.yaml`.
