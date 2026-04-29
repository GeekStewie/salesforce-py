"""Tests for salesforce_py._retry — the shared retry helpers."""

from __future__ import annotations

import subprocess
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

import salesforce_py._retry as retry_mod
from salesforce_py._retry import (
    CLI_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    HTTP_RETRY_DELAY,
    MAX_ATTEMPTS,
    RETRYABLE_STATUSES,
    is_retryable_cli_exception,
    is_retryable_http_exception,
    is_retryable_status,
    retry_async_cli,
    retry_async_http_call,
    retry_sync_cli,
)
from salesforce_py.exceptions import AuthError, CLIError, CLINotFoundError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_default_constants():
    """Shared defaults match the spec: 120s timeout, single retry, 20s HTTP / 10s CLI delay."""
    assert DEFAULT_TIMEOUT == 120.0
    assert HTTP_RETRY_DELAY == 20.0
    assert CLI_RETRY_DELAY == 10.0
    assert MAX_ATTEMPTS == 2


def test_retryable_statuses_includes_420_and_429_and_5xx():
    """420, 429, and the core 5xx family must be retried."""
    for code in (420, 429, 500, 502, 503, 504):
        assert code in RETRYABLE_STATUSES


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


class TestHttpExceptionClassification:
    def test_auth_error_not_retryable(self):
        assert is_retryable_http_exception(AuthError("401")) is False

    def test_transport_error_retryable(self):
        assert is_retryable_http_exception(httpx.ConnectError("boom")) is True
        assert is_retryable_http_exception(httpx.ReadTimeout("boom")) is True

    def test_status_error_retryable_when_in_allowlist(self):
        req = httpx.Request("GET", "https://example.com")
        for code in (420, 429, 500, 502, 503, 504):
            resp = httpx.Response(code, request=req)
            exc = httpx.HTTPStatusError("err", request=req, response=resp)
            assert is_retryable_http_exception(exc) is True

    def test_status_error_not_retryable_for_client_errors(self):
        req = httpx.Request("GET", "https://example.com")
        for code in (400, 403, 404, 422):
            resp = httpx.Response(code, request=req)
            exc = httpx.HTTPStatusError("err", request=req, response=resp)
            assert is_retryable_http_exception(exc) is False

    def test_unknown_error_not_retryable(self):
        assert is_retryable_http_exception(ValueError("nope")) is False

    def test_is_retryable_status(self):
        assert is_retryable_status(420) is True
        assert is_retryable_status(429) is True
        assert is_retryable_status(500) is True
        assert is_retryable_status(404) is False


class TestCliExceptionClassification:
    def test_timeout_retryable(self):
        assert is_retryable_cli_exception(subprocess.TimeoutExpired("sf", 1.0)) is True
        assert is_retryable_cli_exception(TimeoutError()) is True

    def test_cli_not_found_not_retryable(self):
        assert is_retryable_cli_exception(CLINotFoundError()) is False

    def test_cli_error_not_retryable(self):
        assert is_retryable_cli_exception(CLIError(1, "", "")) is False


# ---------------------------------------------------------------------------
# retry_async_http_call — exception path
# ---------------------------------------------------------------------------


async def test_async_http_retries_once_on_transport_error(monkeypatch):
    """Transport errors trigger one retry."""
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    req = httpx.Request("GET", "https://example.com")
    success = httpx.Response(200, request=req, content=b"{}")
    func = AsyncMock(side_effect=[httpx.ConnectError("nope"), success])

    result = await retry_async_http_call(func)

    assert result is success
    assert func.call_count == 2


async def test_async_http_gives_up_after_one_retry(monkeypatch):
    """Two consecutive transport errors exhaust the budget and re-raise."""
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    func = AsyncMock(side_effect=[httpx.ConnectError("first"), httpx.ConnectError("second")])

    with pytest.raises(httpx.ConnectError, match="second"):
        await retry_async_http_call(func)

    assert func.call_count == MAX_ATTEMPTS


async def test_async_http_no_retry_on_auth_error():
    """AuthError is never retried."""
    func = AsyncMock(side_effect=AuthError("401"))

    with pytest.raises(AuthError):
        await retry_async_http_call(func)

    assert func.call_count == 1


async def test_async_http_no_retry_on_client_4xx(monkeypatch):
    """A raised HTTPStatusError with a 404 is not retried."""
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    req = httpx.Request("GET", "https://example.com")
    resp = httpx.Response(404, request=req)
    exc = httpx.HTTPStatusError("err", request=req, response=resp)

    func = AsyncMock(side_effect=exc)

    with pytest.raises(httpx.HTTPStatusError):
        await retry_async_http_call(func)

    assert func.call_count == 1


# ---------------------------------------------------------------------------
# retry_async_http_call — response path (420 / 429 / 5xx)
# ---------------------------------------------------------------------------


async def test_async_http_retries_on_transient_response(monkeypatch):
    """Responses with transient statuses trigger a retry."""
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    req = httpx.Request("GET", "https://example.com")
    transient = httpx.Response(503, request=req, content=b"busy")
    ok = httpx.Response(200, request=req, content=b"{}")

    func = AsyncMock(side_effect=[transient, ok])

    result = await retry_async_http_call(func)

    assert result is ok
    assert func.call_count == 2


async def test_async_http_returns_final_transient_response_after_exhausting_retries(monkeypatch):
    """When both attempts return a transient status, the final response is returned.

    This lets the per-client ``_handle`` layer surface the proper
    ``SalesforcePyError`` with the body attached, instead of the caller
    seeing a raw ``RetryError`` from tenacity.
    """
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    req = httpx.Request("GET", "https://example.com")
    first = httpx.Response(503, request=req, content=b"still busy")
    second = httpx.Response(503, request=req, content=b"still busy")

    func = AsyncMock(side_effect=[first, second])

    result = await retry_async_http_call(func)

    assert result is second
    assert func.call_count == MAX_ATTEMPTS


async def test_async_http_retries_on_420_and_429(monkeypatch):
    """Salesforce-specific 420 and standard 429 both count as transient."""
    monkeypatch.setattr(retry_mod, "HTTP_RETRY_DELAY", 0.0)

    req = httpx.Request("GET", "https://example.com")

    for code in (420, 429):
        transient = httpx.Response(code, request=req, content=b"slow down")
        ok = httpx.Response(200, request=req, content=b"{}")
        func = AsyncMock(side_effect=[transient, ok])

        result = await retry_async_http_call(func)

        assert result is ok
        assert func.call_count == 2


async def test_async_http_no_retry_on_200():
    """Successful responses are returned immediately — no retry."""
    req = httpx.Request("GET", "https://example.com")
    ok = httpx.Response(200, request=req, content=b"{}")
    func = AsyncMock(return_value=ok)

    result = await retry_async_http_call(func)

    assert result is ok
    assert func.call_count == 1


# ---------------------------------------------------------------------------
# retry_sync_cli
# ---------------------------------------------------------------------------


def test_sync_cli_retries_once_on_timeout(monkeypatch):
    """Subprocess timeouts trigger one retry."""
    monkeypatch.setattr(retry_mod, "CLI_RETRY_DELAY", 0.0)

    proc = MagicMock()
    proc.returncode = 0

    func = MagicMock(side_effect=[subprocess.TimeoutExpired("sf", 1.0), proc])

    result = retry_sync_cli(func)

    assert result is proc
    assert func.call_count == 2


def test_sync_cli_no_retry_on_cli_error(monkeypatch):
    """CLIError is deterministic — no retry."""
    monkeypatch.setattr(retry_mod, "CLI_RETRY_DELAY", 0.0)

    func = MagicMock(side_effect=CLIError(1, "", ""))

    with pytest.raises(CLIError):
        retry_sync_cli(func)

    assert func.call_count == 1


# ---------------------------------------------------------------------------
# retry_async_cli
# ---------------------------------------------------------------------------


async def test_async_cli_retries_once_on_timeout(monkeypatch):
    """asyncio.TimeoutError triggers one retry."""
    monkeypatch.setattr(retry_mod, "CLI_RETRY_DELAY", 0.0)

    func = AsyncMock(side_effect=[TimeoutError(), {"ok": True}])

    result = await retry_async_cli(func)

    assert result == {"ok": True}
    assert func.call_count == 2


async def test_async_cli_no_retry_on_cli_not_found():
    """CLINotFoundError — no retry."""
    func = AsyncMock(side_effect=CLINotFoundError())

    with pytest.raises(CLINotFoundError):
        await retry_async_cli(func)

    assert func.call_count == 1
