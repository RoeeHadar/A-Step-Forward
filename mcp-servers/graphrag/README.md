# graphrag MCP

Knowledge-graph retrieval surface for agents and dev tools.

## Tools

| Tool                    | Purpose                                                  |
| ----------------------- | -------------------------------------------------------- |
| `kg.search`             | Vector-local KG search by query.                         |
| `kg.walk`               | BFS walk from seeds with optional edge-type filter.      |
| `kg.hybrid`             | Vector seed + walk + rerank.                             |
| `kg.personalized`       | Hybrid biased toward a learner's subgraph.               |
| `kg.related_concepts`   | Concepts directly related to a given concept.            |
| `kg.prereqs`            | Prerequisite concepts for a given concept.               |
| `kg.next_topics`        | Next topics for a learner from a concept.                |
| `kg.explain_path`       | Shortest justified path between two nodes.               |

## Run

```bash
python -m graphrag_mcp.server
```
