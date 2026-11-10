"""pytest path setup for graphrag service tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "schemas"))
sys.path.insert(0, str(ROOT / "services" / "graphrag"))

# AS-99: test_smoke.py is a script (main() only, no tests; run by `make smoke`). Its
# basename is shared with services/memory/tests and services/orchestrator/tests, so
# collecting it from a combined run raised "import file mismatch".
collect_ignore = ["test_smoke.py"]
