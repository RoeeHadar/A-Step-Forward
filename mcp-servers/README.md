# MCP servers

Four MCP servers (stdio, official Python MCP SDK / FastMCP) expose the project
services to agents and to Cursor: [`memory`](memory/README.md),
[`graphrag`](graphrag/README.md), [`curriculum`](curriculum/README.md) and
[`progress`](progress/README.md). Each one is a uv workspace package
(`memory-mcp`, `graphrag-mcp`, `curriculum-mcp`, `progress-mcp`).

## Test environment

The `mcp` SDK is pinned in the root `uv.lock`, but only the four `*-mcp` packages
depend on it, so a plain root sync does not install it.

1. Main env, from the repo root, using your default uv cache:

   ```bash
   uv sync --frozen
   ```

2. Add the four MCP packages (and `mcp`) on top, without removing anything:

   ```bash
   uv sync --frozen --inexact \
     --package memory-mcp --package graphrag-mcp \
     --package curriculum-mcp --package progress-mcp
   ```

   Offline, point uv at a cache that already holds the pinned wheels and add
   `--offline`, for example:

   ```bash
   UV_CACHE_DIR=/path/to/uv-cache uv sync --frozen --offline --inexact \
     --package memory-mcp --package graphrag-mcp \
     --package curriculum-mcp --package progress-mcp
   ```

   (On the shared ASF box that cache is `/workspace/asf/cache/uv`.)

3. Check that the real SDK is there: `.venv/bin/python -c "import mcp.server.fastmcp"`.

Notes:

- A later plain `uv sync` (without `--inexact`) is exact, so it removes `mcp` and the
  MCP packages again. `tests/test_as115_mcp_required.py` then skips via
  `pytest.importorskip("mcp")` instead of running. Repeat step 2 after any plain sync.
- Never run `uv lock` or add dependencies for this; everything comes from the
  frozen `uv.lock`.
- Per-server tests: `cd mcp-servers/<name> && ../../.venv/bin/python -m pytest -o addopts= -q tests`
  (`-o addopts=` drops the coverage flags when `pytest-cov` is not installed).
