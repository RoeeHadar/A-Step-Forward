# Architecture Decision Records

We use lightweight [ADRs](https://adr.github.io/) to capture significant
architectural decisions, each with the context, the alternatives weighed, the
decision, and its consequences. Opus is the canonical author; sub-agents propose
ADRs in PRs.

## Index

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-memory-architecture.md) | Multi-layered, self-healing memory | Accepted |
| [0003](0003-security-threat-model.md) | Security threat model | Accepted |
| [0004](0004-llm-provider-groq.md) | Groq Cloud as primary LLM provider | Accepted |
| [0005](0005-embeddings-sentence-transformers.md) | Sentence-Transformers for GraphRAG embeddings | Accepted |

## Authoring a new ADR

1. Copy the file name pattern: `NNNN-<kebab-case-title>.md`. Use the next
   integer.
2. Use this minimum structure:

   ```markdown
   # ADR NNNN: <Title>

   - **Status**: Proposed | Accepted | Superseded by ADR-XXXX | Deprecated
   - **Date**: YYYY-MM-DD
   - **Deciders**: <names / "Opus + Composer">

   ## Context
   ## Decision
   ## Consequences
   ## Alternatives considered
   ```

3. Open a PR titled `docs(adr): <decision>` and request review from the relevant
   stream owner.
4. Once accepted, update this index in the same PR.

## When to write an ADR

- Cross-stream changes (e.g., switching memory backend, changing auth provider).
- Anything that locks in a vendor or storage format.
- Anything a future reader could reasonably ask "why did we do this?" about.

When in doubt, write one. ADRs are cheap; surprises are expensive.
