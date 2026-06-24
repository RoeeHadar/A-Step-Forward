#!/usr/bin/env python3
"""Validate production environment readiness before cutover.

Usage::

    python scripts/verify_prod_env.py

Set ``DATABASE_URL``, ``GROQ_API_KEY``, and ``CLERK_SECRET_KEY`` in the environment
(or export them in your shell). The script runs read-only checks and prints a
pass/fail checklist. Exit code 0 when every *configured* check passes; 1 otherwise.

Missing variables produce a warning and are skipped (no crash).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
POSTGRES_SCHEMES = ("postgresql://", "postgres://", "postgresql+asyncpg://")

CheckResult = tuple[str, bool | None, str]  # name, pass|fail|skip, message


def _normalize_postgres_dsn(url: str) -> str:
    for prefix in ("postgresql+asyncpg://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix) :]
    return url


def _postgres_url_format_ok(url: str) -> bool:
    return any(url.startswith(scheme) for scheme in POSTGRES_SCHEMES)


def check_database_url() -> CheckResult:
    name = "DATABASE_URL"
    url = os.environ.get(name)
    if not url:
        return name, None, "not set - skipped (export DATABASE_URL to test connectivity)"

    if not _postgres_url_format_ok(url):
        scheme = url.split("://", 1)[0] if "://" in url else "(none)"
        return name, False, f"invalid format (expected postgres URL, got {scheme}://)"

    dsn = _normalize_postgres_dsn(url)

    try:
        import asyncpg
    except ImportError:
        return name, True, "format OK (asyncpg not installed — connectivity not tested)"

    async def _ping() -> None:
        conn = await asyncpg.connect(dsn=dsn, timeout=10)
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()

    try:
        asyncio.run(_ping())
    except Exception as exc:
        return name, False, f"unreachable: {exc}"

    return name, True, "reachable (SELECT 1 ok)"


def check_groq_api_key() -> CheckResult:
    name = "GROQ_API_KEY"
    key = os.environ.get(name)
    if not key:
        return name, None, "not set - skipped (export GROQ_API_KEY to test API access)"

    req = Request(GROQ_MODELS_URL, headers={"Authorization": f"Bearer {key}"})
    try:
        with urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                return name, False, f"API returned HTTP {resp.status}"
            payload = json.loads(resp.read().decode())
            model_count = len(payload.get("data", []))
            return name, True, f"valid ({model_count} models listed)"
    except HTTPError as exc:
        if exc.code in (401, 403):
            return name, False, f"rejected (HTTP {exc.code})"
        return name, False, f"HTTP error {exc.code}: {exc.reason}"
    except URLError as exc:
        return name, False, f"unreachable: {exc.reason}"
    except Exception as exc:
        return name, False, f"check failed: {exc}"


def check_clerk_secret_key() -> CheckResult:
    name = "CLERK_SECRET_KEY"
    key = os.environ.get(name)
    if not key:
        return name, None, "not set - skipped (export CLERK_SECRET_KEY to validate format)"

    if key.startswith("sk_live_"):
        return name, True, "production key (sk_live_*)"
    if key.startswith("sk_test_"):
        return (
            name,
            False,
            "WARNING: test key (sk_test_*) — rotate to sk_live_ before cutover",
        )
    return name, False, "unrecognized format (expected sk_live_ or sk_test_ prefix)"


def _status_label(passed: bool | None) -> str:
    if passed is True:
        return "PASS"
    if passed is False:
        return "FAIL"
    return "SKIP"


def main() -> int:
    checks = (
        check_database_url(),
        check_groq_api_key(),
        check_clerk_secret_key(),
    )

    print("Production environment verification")
    print("=" * 40)

    failures = 0
    skipped = 0
    for name, passed, message in checks:
        label = _status_label(passed)
        marker = "+" if passed is True else ("x" if passed is False else "-")
        print(f"  [{marker}] {name}: {label}")
        print(f"      {message}")
        if passed is False:
            failures += 1
        elif passed is None:
            skipped += 1

    print("=" * 40)
    configured = len(checks) - skipped
    if configured == 0:
        print("No env vars set - export DATABASE_URL, GROQ_API_KEY, CLERK_SECRET_KEY.")
        return 1
    if failures:
        print(f"{failures} check(s) failed, {skipped} skipped.")
        return 1
    print(f"All {configured} configured check(s) passed ({skipped} skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
