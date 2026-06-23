# ADR-0001 — Record architecture decisions

## Status

Accepted (2026-06-23).

## Context

Significant architecture decisions for A Step Forward will be made over many months by many sub-agents. We need a lightweight, in-repo trail so that:

- Sub-agents can read the decision history before changing structural code.
- New collaborators can understand *why*, not just *what*.
- Reversals are documented, not lost.

## Decision

Adopt [ADR](https://adr.github.io/) (Architecture Decision Records) under `docs/adr/`. One file per decision, numbered, with sections: Context, Decision, Status, Consequences.

## Consequences

- Every PR that changes architecture (new service, new node/edge type, new agent contract, schema-breaking change) must include or update an ADR.
- Reversing a decision means a new ADR that supersedes the old, with a back-link.
