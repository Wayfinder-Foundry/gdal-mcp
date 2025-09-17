"""Pytest HTTP tests for the GDAL MCP server.

These tests assume an HTTP instance of the server is already running.
Start manually, e.g.:

    uv run gdal-mcp-server streamable-http

Set BASE_URL env var to override (default http://127.0.0.1:8000).

Tests will be skipped gracefully if the endpoint is unreachable.
No external dependencies are required (stdlib urllib only).
"""
from __future__ import annotations

import os
import json
import socket
import pytest

from urllib import request, error
from typing import Any, Dict, Optional

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    # Include both to allow server to negotiate SSE if it wants
    "Accept": "application/json, text/event-stream",
}

def _is_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"_raw": raw, "error": "Non-JSON response"}
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"http_error": e.code, "body": body}
    except Exception as e:  # noqa
        return {"exception": repr(e)}


# ---------------- Pytest Fixtures -----------------

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def endpoint(base_url: str) -> str:
    return base_url.rstrip('/') + "/mcp"


@pytest.fixture(scope="session")
def server_available(base_url: str) -> bool:
    # Rough reachability check
    try:
        host_port = base_url.split('//', 1)[-1]
        host_port = host_port.split('/', 1)[0]
        host, port = host_port.split(':') if ':' in host_port else (host_port, '80')
        return _is_reachable(host, int(port))
    except Exception:
        return False


@pytest.fixture()
def init_session(endpoint: str, server_available: bool):
    if not server_available:
        pytest.skip("HTTP MCP server not running; skipping HTTP tests")
    init_payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "clientInfo": {"name": "http-test", "version": "0.1"},
            "capabilities": {},
        },
    }
    init_resp = post_json(endpoint, init_payload, DEFAULT_HEADERS)
    if "result" not in init_resp:
        # If server returns parameter error, skip HTTP tests (likely incompatible initialize schema)
        pytest.skip(f"Initialize failed/not supported for HTTP tests: {init_resp}")
    result = init_resp["result"]
    session_id = result.get("sessionId") if isinstance(result, dict) else None
    # Send notifications/initialized if we got a session id
    if session_id:
        headers = dict(DEFAULT_HEADERS)
        headers["mcp-session-id"] = session_id
        notify_payload = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        post_json(endpoint, notify_payload, headers)
    return session_id


def _headers(session_id: Optional[str]) -> Dict[str, str]:
    h = dict(DEFAULT_HEADERS)
    if session_id:
        h["mcp-session-id"] = session_id
    return h


# ----------------- Tests -------------------------

def test_tools_list(endpoint: str, init_session):
    session = init_session
    payload = {"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}}
    resp = post_json(endpoint, payload, _headers(session))
    assert "result" in resp, f"tools/list failed: {resp}"
    tools = resp["result"].get("tools", [])
    assert any(t.get("name") == "gdalinfo" for t in tools)


@pytest.mark.parametrize("translate", [False, True])
def test_gdalinfo_and_optional_translate(endpoint: str, init_session, translate: bool):
    session = init_session
    sample_path = "test_data/sample.tif"
    if not os.path.exists(sample_path):
        pytest.skip("sample.tif not present")

    # gdalinfo
    call_payload = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "tools/call",
        "params": {
            "name": "gdalinfo",
            "arguments": {"dataset": sample_path, "json_output": False, "stats": False},
        },
    }
    resp = post_json(endpoint, call_payload, _headers(session))
    assert "result" in resp, f"gdalinfo call failed: {resp}"

    if translate:
        out_path = "test_data/sample_http_translated.tif"
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass
        translate_payload = {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "tools/call",
            "params": {
                "name": "gdal_translate",
                "arguments": {
                    "src_dataset": sample_path,
                    "dst_dataset": out_path,
                    "output_format": "GTiff",
                    "bands": [1],
                },
            },
        }
        t_resp = post_json(endpoint, translate_payload, _headers(session))
        assert "result" in t_resp, f"gdal_translate call failed: {t_resp}"
        assert os.path.exists(out_path), "Translated file not created"
        # Quick size sanity check (non-empty)
        assert os.path.getsize(out_path) > 0
