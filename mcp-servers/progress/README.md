# progress MCP

Read/write surface over learner progress (mastery, gaps, streaks).

## Tools

| Tool                          | Purpose                                    |
| ----------------------------- | ------------------------------------------ |
| `progress.snapshot`           | Current mastery summary.                   |
| `progress.gaps`               | Identified knowledge gaps.                 |
| `progress.streak`             | Streak + cadence.                          |
| `progress.update_mastery`     | Update mastery for (learner, concept).     |

## Run

```bash
python -m progress_mcp.server
```
