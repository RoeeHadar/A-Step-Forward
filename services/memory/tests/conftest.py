"""pytest config for memory service tests."""

# AS-99: test_smoke.py is a script (main() only, no tests; run by `make smoke`). Its
# basename is shared with services/graphrag/tests and services/orchestrator/tests, so
# collecting it from a combined run raised "import file mismatch".
collect_ignore = ["test_smoke.py"]
