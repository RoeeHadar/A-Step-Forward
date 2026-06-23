"""Generate TypeScript types from Pydantic models into packages/schemas/ts/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TS_DIR = ROOT / "packages" / "schemas" / "ts"
sys.path.insert(0, str(ROOT / "packages" / "schemas"))

from schemas.agents import AgentManifest, ChatRequest, ChatChunk  # noqa: E402
from schemas.curriculum import Lesson  # noqa: E402
from schemas.learners import LearnerProfile  # noqa: E402
from schemas.memory import MemoryRecord, MemorySearchInput, MemoryWriteInput  # noqa: E402
from schemas.progress import ProgressSummary  # noqa: E402

MODELS = [
    ("ChatRequest", ChatRequest),
    ("ChatChunk", ChatChunk),
    ("AgentManifest", AgentManifest),
    ("LearnerProfile", LearnerProfile),
    ("Lesson", Lesson),
    ("ProgressSummary", ProgressSummary),
    ("MemoryRecord", MemoryRecord),
    ("MemoryWriteInput", MemoryWriteInput),
    ("MemorySearchInput", MemorySearchInput),
]


def main() -> int:
    TS_DIR.mkdir(parents=True, exist_ok=True)
    schemas: dict[str, dict] = {}
    for name, model in MODELS:
        schemas[name] = model.model_json_schema(ref_template="#/components/schemas/{model}")

    out = TS_DIR / "generated.json"
    out.write_text(json.dumps({"$schema": "http://json-schema.org/draft-07/schema#", "definitions": schemas}, indent=2))
    index = TS_DIR / "index.ts"
    index.write_text(
        "/** Auto-generated JSON Schema bundle. Import types via your codegen tool of choice. */\n"
        f"import schemas from './generated.json';\n\n"
        "export type ChatRequest = typeof schemas.definitions.ChatRequest;\n"
        "export type ChatChunk = typeof schemas.definitions.ChatChunk;\n"
        "export type AgentManifest = typeof schemas.definitions.AgentManifest;\n"
        "export type LearnerProfile = typeof schemas.definitions.LearnerProfile;\n"
        "export type Lesson = typeof schemas.definitions.Lesson;\n"
        "export type ProgressSummary = typeof schemas.definitions.ProgressSummary;\n"
        "export type MemoryRecord = typeof schemas.definitions.MemoryRecord;\n"
        "export type MemoryWriteInput = typeof schemas.definitions.MemoryWriteInput;\n"
        "export type MemorySearchInput = typeof schemas.definitions.MemorySearchInput;\n\n"
        "export default schemas;\n"
    )
    print(f"[codegen] wrote {out} and {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
