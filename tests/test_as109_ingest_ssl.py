"""AS-109: OPENSTAX_INSECURE_SSL must only turn off TLS verification for
scripts/ingest_content.py's own httpx client, never process-wide.

Fakes only: the script's OpenStax client is built (httpx.AsyncClient, inspected through
its SSL context) but no request is sent; ingest_book is replaced by a fake for the entry
point. No sockets, no network, no DB. Global SSL/env state is snapshotted and restored
around every test so a failing (base) run cannot leak into other tests.

Set AS109_CASES_OUT=<path> to append the measured values of each case as JSON lines.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import ssl
import sys
from pathlib import Path

import httpx
import pytest
import requests

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "ingest_content.py"
_ENV = (
    "OPENSTAX_INSECURE_SSL",
    "HF_HUB_DISABLE_SSL",
    "CURL_CA_BUNDLE",
    "REQUESTS_CA_BUNDLE",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "PYTHONHTTPSVERIFY",
)


def _global_state() -> dict:
    ctx = ssl._create_default_https_context()
    return {
        "https_ctx_factory": ssl._create_default_https_context,
        "https_ctx": (ctx.verify_mode, ctx.check_hostname),
        "create_default_context": (
            ssl.create_default_context().verify_mode,
            ssl.create_default_context().check_hostname,
        ),
        "httpx_client_init": httpx.Client.__init__,
        "httpx_async_init": httpx.AsyncClient.__init__,
        "requests_session_init": requests.Session.__init__,
        "env": {k: os.environ.get(k) for k in _ENV if k != "OPENSTAX_INSECURE_SSL"},
    }


def _verifies(ctx: ssl.SSLContext) -> bool:
    return ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname is True


def _other_clients_verify() -> bool:
    with httpx.Client() as c:
        hx = _verifies(c._transport._pool._ssl_context)
    with requests.Session() as s:
        rq = s.verify is True
    return hx and rq and _verifies(ssl._create_default_https_context())


def _default_ctx_verify() -> bool:
    return _verifies(ssl.create_default_context()) and _verifies(
        ssl._create_default_https_context()
    )


@pytest.fixture(autouse=True)
def _restore_globals():
    saved_factory = ssl._create_default_https_context
    saved_env = {k: os.environ.get(k) for k in _ENV}
    yield
    ssl._create_default_https_context = saved_factory
    for k, v in saved_env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def _load():
    spec = importlib.util.spec_from_file_location("as109_ingest_content", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses resolve their module during exec
    spec.loader.exec_module(mod)
    return mod


def _record_clients(monkeypatch):
    clients: list[httpx.AsyncClient] = []
    real = httpx.AsyncClient

    class RecordingAsyncClient(real):  # builds the real client (real SSL context), no I/O
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            clients.append(self)

    monkeypatch.setattr(httpx, "AsyncClient", RecordingAsyncClient)
    return clients


def _args(**kw):
    base = dict(books=[], dry_run=True, parse_only=False, max_pages=None, export_lessons="")
    base.update(kw)
    return argparse.Namespace(**base)


def _emit(case: str, own: bool, default: bool, other: bool, state_same: bool) -> None:
    out = os.environ.get("AS109_CASES_OUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "case": case,
                        "own_client_verify": own,
                        "default_ctx_verify": default,
                        "other_client_verify": other,
                        "global_state_unchanged": state_same,
                    }
                )
                + "\n"
            )


@pytest.mark.parametrize("value", ["1", "true", "yes"])
def test_a_flag_set_only_own_client_skips_verify(monkeypatch, value) -> None:
    before = _global_state()
    monkeypatch.setenv("OPENSTAX_INSECURE_SSL", value)
    mod = _load()
    clients = _record_clients(monkeypatch)
    asyncio.run(mod.run_ingest(_args()))
    assert len(clients) == 1
    own_ctx = clients[0]._transport._pool._ssl_context
    own = _verifies(own_ctx)
    default, other = _default_ctx_verify(), _other_clients_verify()
    monkeypatch.undo()  # drop the recording client before comparing global state
    same = _global_state() == before
    _emit(f"a:flag={value}", own, default, other, same)
    assert own_ctx.verify_mode == ssl.CERT_NONE and own_ctx.check_hostname is False
    assert default, "default SSL context no longer verifies"
    assert other, "a fresh httpx/requests/urllib client no longer verifies"
    assert same


@pytest.mark.parametrize("value", [None, "", "0", "false"])
def test_b_flag_unset_everything_verifies(monkeypatch, value) -> None:
    before = _global_state()
    if value is None:
        monkeypatch.delenv("OPENSTAX_INSECURE_SSL", raising=False)
    else:
        monkeypatch.setenv("OPENSTAX_INSECURE_SSL", value)
    mod = _load()
    clients = _record_clients(monkeypatch)
    asyncio.run(mod.run_ingest(_args()))
    own = _verifies(clients[0]._transport._pool._ssl_context)
    default, other = _default_ctx_verify(), _other_clients_verify()
    monkeypatch.undo()
    same = _global_state() == before
    _emit(f"b:flag={'unset' if value is None else repr(value)}", own, default, other, same)
    assert own and default and other and same


def test_c_import_and_entry_point_leave_no_global_ssl_change(monkeypatch, capsys) -> None:
    before = _global_state()
    monkeypatch.setenv("OPENSTAX_INSECURE_SSL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    mod = _load()
    after_import = _global_state() == before
    clients = _record_clients(monkeypatch)

    async def fake_ingest_book(client, book_slug, **kw):
        assert client is clients[0]
        return {"lessons": 0, "chunks": 0, "chunks_written": 0, "lesson_objects": []}

    monkeypatch.setattr(mod, "ingest_book", fake_ingest_book)
    monkeypatch.setattr(sys, "argv", ["ingest_content.py", "--dry-run", "--books", "fake-book"])
    rc = mod.main()
    own = _verifies(clients[0]._transport._pool._ssl_context)
    default, other = _default_ctx_verify(), _other_clients_verify()
    monkeypatch.undo()
    same = _global_state() == before
    _emit("c:import+main flag=1", own, default, other, after_import and same)
    assert rc == 0 and "Summary: books=1" in capsys.readouterr().out
    assert own is False
    assert after_import and same, "global SSL/env state changed by import or main()"
    assert default and other
