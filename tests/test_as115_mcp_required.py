"""AS-115: required fields of every MCP tool, checked through the real FastMCP server.

For each of the 4 MCP servers (memory, graphrag, curriculum, progress) and every tool:
  * the advertised inputSchema (FastMCP list_tools) marks as required every field the
    wrapper's input model requires (pydantic, recursively for required nested models),
    plus the explicit AS-112/AS-113/AS-119 must-haves below;
  * a payload with all required fields (sample values from the advertised schema) passes
    FastMCP argument validation and reaches the backend (a fake that raises a sentinel);
  * for each required field, the same payload without it is rejected by call_tool with a
    validation error, and the backend is never reached.
Backends are fakes (no DB, no LLM, no network). Needs the real `mcp` package (installed
from the frozen uv.lock via the 4 mcp-server packages); without it the module is skipped.

AS115_CASES_OUT=<path> appends one JSON line per (server, tool, field).
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import sys
import typing
from pathlib import Path

import pytest

pytest.importorskip(
    "mcp", reason="real mcp/FastMCP not installed (uv sync the mcp-server packages)"
)

from mcp.server.fastmcp.exceptions import ToolError
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parents[1]
for _rel in (
    "packages/schemas",
    "services/memory",
    "services/graphrag",
    "services/curriculum",
    "mcp-servers/memory/src",
    "mcp-servers/graphrag/src",
    "mcp-servers/curriculum/src",
    "mcp-servers/progress/src",
):
    _p = str(_ROOT / _rel)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Must-haves from AS-112 (agent_id / messages / target_tokens) and AS-113/AS-119.
MUST_REQUIRE = {
    ("memory", "memory.write"): {"agent_id", "input", "input.learner_id", "input.content"},
    ("memory", "memory.update"): {"agent_id", "memory_id", "learner_id"},
    ("memory", "memory.delete"): {"agent_id", "memory_id", "learner_id"},
    ("memory", "memory.search"): {"agent_id", "learner_id", "query"},
    ("memory", "memory.compact_context"): {"messages", "target_tokens"},
}


class _Reached(Exception):
    pass


class _Backend:
    """Fake service/facade: every method call records itself and raises a sentinel."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError(name)

        def method(*_a, **_k):
            self.calls.append(name)
            raise _Reached(name)

        return method


def _servers(monkeypatch) -> dict[str, tuple[object, _Backend]]:
    from curriculum_mcp.server import create_server as curriculum_server
    from graphrag_mcp.server import create_server as graphrag_server
    from memory_mcp.server import create_server as memory_server
    from progress_mcp.server import create_server as progress_server

    out = {}
    b = _Backend()
    import memory_mcp.tools.memory as mem_tools

    def fake_compact(*_a, _b=b, **_k):  # module function, not on the service
        _b.calls.append("compact_context")
        raise _Reached("compact_context")

    monkeypatch.setattr(mem_tools, "compact_context", fake_compact)
    out["memory"] = (memory_server(svc=b), b)
    b = _Backend()
    out["graphrag"] = (graphrag_server(svc=b), b)
    b = _Backend()
    out["curriculum"] = (curriculum_server(svc=b), b)
    b = _Backend()
    out["progress"] = (progress_server(facade=b), b)
    return out


# ------------------------------------------------------------------ schema helpers


def _resolve(schema: dict, root: dict) -> dict:
    while "$ref" in schema:
        schema = root["$defs"][schema["$ref"].split("/")[-1]]
    return schema


def _object_branch(schema: dict, root: dict) -> dict | None:
    schema = _resolve(schema, root)
    if schema.get("type") == "object" or "properties" in schema:
        return schema
    for alt in schema.get("anyOf", []) + schema.get("allOf", []):
        alt = _resolve(alt, root)
        if alt.get("type") == "object" or "properties" in alt:
            return alt
    return None


def _advertised_required(schema: dict, root: dict, prefix: str = "") -> set[str]:
    obj = _object_branch(schema, root)
    if obj is None:
        return set()
    out = set()
    for name in obj.get("required", []):
        path = f"{prefix}{name}"
        out.add(path)
        out |= _advertised_required(obj["properties"][name], root, path + ".")
    return out


def _sample(schema: dict, root: dict):
    schema = _resolve(schema, root)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    if "anyOf" in schema:
        alts = [a for a in schema["anyOf"] if _resolve(a, root).get("type") != "null"]
        return _sample(alts[0], root)
    if "allOf" in schema:
        return _sample(schema["allOf"][0], root)
    t = schema.get("type")
    if isinstance(t, list):
        t = next(x for x in t if x != "null")
    if t == "object" or "properties" in schema:
        props = schema.get("properties", {})
        return {k: _sample(props[k], root) for k in schema.get("required", [])}
    if t == "array":
        n = max(1, schema.get("minItems", 1))
        item = schema.get("items", {"type": "string"})
        return [_sample(item, root) for _ in range(n)]
    if t == "string":
        if schema.get("format") == "date-time":
            return "2026-01-01T00:00:00Z"
        n = max(schema.get("minLength", 1), 1)
        return ("x" * n)[: schema.get("maxLength", n)]
    if t in ("integer", "number"):
        lo = schema.get(
            "minimum",
            schema.get("exclusiveMinimum", 0) + (1 if "exclusiveMinimum" in schema else 0),
        )
        v = (
            max(lo, 1)
            if t == "integer"
            else max(lo, 0.5 if schema.get("maximum", 1) >= 0.5 else lo)
        )
        if "maximum" in schema:
            v = min(v, schema["maximum"])
        return int(v) if t == "integer" else float(v)
    if t == "boolean":
        return False
    return "x"


def _without(payload: dict, path: str) -> dict:
    out = copy.deepcopy(payload)
    parts = path.split(".")
    node = out
    for p in parts[:-1]:
        node = node[p]
    node.pop(parts[-1], None)
    return out


# ------------------------------------------------------------------ model (source) side


def _model_required(model: type[BaseModel], prefix: str = "") -> set[str]:
    out = set()
    for name, f in model.model_fields.items():
        if not f.is_required():
            continue
        alias = f.alias or name
        out.add(f"{prefix}{alias}")
        ann = f.annotation
        for cand in (ann, *typing.get_args(ann)):
            if isinstance(cand, type) and issubclass(cand, BaseModel):
                out |= _model_required(cand, f"{prefix}{alias}.")
    return out


def _tool_model(server, tool_name: str) -> type[BaseModel]:
    tool = server._tool_manager.get_tool(tool_name)
    hints = typing.get_type_hints(tool.fn)
    return hints["inp"]


# ------------------------------------------------------------------ the test


async def _call(server, name: str, args: dict):
    try:
        await server.call_tool(name, args)
    except ToolError as exc:
        return str(exc)
    except _Reached as exc:  # pragma: no cover - FastMCP wraps tool errors in ToolError
        return f"reached {exc}"
    return "ok"


def _emit(row: dict) -> None:
    out = os.environ.get("AS115_CASES_OUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


SERVERS = ["memory", "graphrag", "curriculum", "progress"]


@pytest.mark.parametrize("server_name", SERVERS)
def test_every_required_field_is_advertised_and_enforced(monkeypatch, server_name) -> None:
    server, backend = _servers(monkeypatch)[server_name]
    tools = asyncio.run(server.list_tools())
    assert tools, server_name
    problems: list[str] = []
    n_fields = 0
    for tool in sorted(tools, key=lambda t: t.name):
        root = tool.inputSchema
        assert root.get("required") == ["inp"], (tool.name, root.get("required"))
        inp_schema = root["properties"]["inp"]
        advertised = _advertised_required(inp_schema, root)
        model_req = _model_required(_tool_model(server, tool.name))
        expected = model_req | MUST_REQUIRE.get((server_name, tool.name), set())
        payload = _sample(inp_schema, root)
        backend.calls.clear()
        full = asyncio.run(_call(server, tool.name, {"inp": payload}))
        full_ok = bool(backend.calls) and "validation error" not in full
        if not full_ok:
            problems.append(f"{tool.name}: full sample payload not accepted: {full[:200]}")
        for field in sorted(expected | advertised):
            n_fields += 1
            in_schema = field in advertised
            backend.calls.clear()
            msg = asyncio.run(_call(server, tool.name, {"inp": _without(payload, field)}))
            rejected = "validation error" in msg and not backend.calls
            ok = in_schema and rejected and full_ok and field in expected
            _emit(
                {
                    "server": server_name,
                    "tool": tool.name,
                    "field": field,
                    "in_model_required": field in model_req,
                    "in_schema_required": in_schema,
                    "call_rejected": rejected,
                    "full_payload_accepted": full_ok,
                    "result": "pass" if ok else "FAIL",
                }
            )
            if not ok:
                problems.append(
                    f"{tool.name}.{field}: in_schema={in_schema} rejected={rejected} "
                    f"expected={field in expected} msg={msg[:160]}"
                )
    assert n_fields > 0
    assert not problems, "\n".join(problems)


def test_must_haves_cover_existing_tools(monkeypatch) -> None:
    servers = _servers(monkeypatch)
    for (server_name, tool_name), fields in MUST_REQUIRE.items():
        server, _ = servers[server_name]
        names = {t.name for t in asyncio.run(server.list_tools())}
        assert tool_name in names, (server_name, tool_name)
        assert fields
