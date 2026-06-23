# curriculum MCP

Read-side surface over the curriculum store. Sub-agent 07-curriculum implements the real backing service; this Phase-0 stub returns empty results so agents wire up cleanly.

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
