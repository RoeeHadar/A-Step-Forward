"""Knowledge graph ontology — node + edge kinds, constraints, and indexes.

The ontology is *the contract* of GraphRAG. New kinds require an ADR under
`docs/adr/`. Sub-agent 05 owns this directory; do not modify without
coordinating with them.
"""

from .schema import CYPHER_CONSTRAINTS, CYPHER_FULLTEXT_INDEXES, CYPHER_INDEXES

__all__ = ["CYPHER_CONSTRAINTS", "CYPHER_FULLTEXT_INDEXES", "CYPHER_INDEXES"]
