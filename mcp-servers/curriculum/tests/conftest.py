"""Test fixtures for curriculum MCP."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "curriculum"))
sys.path.insert(0, str(ROOT / "mcp-servers" / "curriculum" / "src"))
