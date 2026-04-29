"""Tests for salesforce_py.sf._runner."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from salesforce_py.exceptions import CLIError, CLINotFoundError
from salesforce_py.sf._runner import run, run_sync

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_proc(returncode: int, stdout: bytes, stderr: bytes = b"") -> AsyncMock:
    """Build a fake asyncio.subprocess.Process mock."""
    proc = MagicMock()
    proc.returncode = returncode
    proc.communicate = AsyncMock(return_value=(stdout, stderr))
    proc.kill = MagicMock()
    return proc


# ---------------------------------------------------------------------------
# run() — argument construction
# ---------------------------------------------------------------------------


async def test_run_prepends_sf_and_json_flag():
    """run() must prepend 'sf' and append '--json' to the command."""
    payload = {"status": 0, "result": {}}
    proc = _make_proc(0, json.dumps(payload).encode())

    with patch("asyncio.create_subprocess_exec", return_value=proc) as mock_exec:
        result = await run(["org", "list"])

    called_cmd = mock_exec.call_args.args
    assert called_cmd[0] == "sf", "First argument must be 'sf'"
    assert called_cmd[1] == "org"
    assert called_cmd[2] == "list"
    assert called_cmd[-1] == "--json", "Last argument must be '--json'"
    assert result == payload


async def test_run_does_not_duplicate_json_flag():
    """run() should not add --json a second time if the caller already passed it."""
    # The contract is that _runner always appends --json; callers should not pass it.
    # This test just verifies the flag appears exactly once.
    payload = {"status": 0, "result": {}}
    proc = _make_proc(0, json.dumps(payload).encode())

    with patch("asyncio.create_subprocess_exec", return_value=proc) as mock_exec:
        await run(["org", "list"])

    cmd_args = mock_exec.call_args.args
    assert cmd_args.count("--json") == 1


# ---------------------------------------------------------------------------
# run() — error handling
# ---------------------------------------------------------------------------


async def test_run_raises_cli_not_found_error():
    """run() must raise CLINotFoundError when the sf binary is not on PATH."""
    with (
        patch(
            "asyncio.create_subprocess_exec",
            side_effect=FileNotFoundError("sf not found"),
        ),
        pytest.raises(CLINotFoundError),
    ):
        await run(["org", "list"])


async def test_run_raises_cli_error_on_nonzero_exit():
    """run() must raise CLIError when the process exits with a non-zero code."""
    stderr_msg = b"ERROR running command"
    stdout_msg = b'{"status": 1, "message": "Something went wrong"}'
    proc = _make_proc(1, stdout_msg, stderr_msg)

    with (
        patch("asyncio.create_subprocess_exec", return_value=proc),
        pytest.raises(CLIError) as exc_info,
    ):
        await run(["org", "list"])

    err = exc_info.value
    assert err.returncode == 1
    assert "Something went wrong" in err.stdout
    assert "ERROR running command" in err.stderr


async def _noop_async_sleep(_seconds: float) -> None:
    """Drop-in for ``asyncio.sleep`` that returns immediately (keeps retry tests fast)."""
    return None


async def test_run_raises_timeout_and_kills_process(monkeypatch):
    """run() must re-raise TimeoutError and kill the subprocess.

    Timeouts are retried once, so ``kill`` is called twice — once per
    attempt — before the final ``TimeoutError`` propagates.
    """
    import salesforce_py._retry as retry_mod

    monkeypatch.setattr(retry_mod, "CLI_RETRY_DELAY", 0.0)

    proc = MagicMock()
    proc.returncode = None
    proc.kill = MagicMock()
    proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError)

    with (
        patch("asyncio.create_subprocess_exec", return_value=proc),
        pytest.raises(asyncio.TimeoutError),
    ):
        await run(["org", "list"], timeout=0.001)

    # Initial attempt + 1 retry = 2 kills.
    assert proc.kill.call_count == 2


async def test_run_retries_once_on_timeout_then_succeeds(monkeypatch):
    """run() must retry once after a transient timeout and return the second attempt's result."""
    import salesforce_py._retry as retry_mod

    monkeypatch.setattr(retry_mod, "CLI_RETRY_DELAY", 0.0)

    payload = {"status": 0, "result": {"ok": True}}

    first_proc = MagicMock()
    first_proc.returncode = None
    first_proc.kill = MagicMock()
    first_proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError)

    second_proc = _make_proc(0, json.dumps(payload).encode())

    with patch(
        "asyncio.create_subprocess_exec", side_effect=[first_proc, second_proc]
    ) as mock_exec:
        result = await run(["org", "list"], timeout=0.001)

    assert result == payload
    assert mock_exec.call_count == 2
    first_proc.kill.assert_called_once()


async def test_run_does_not_retry_on_cli_error():
    """CLIError (non-zero exit) is deterministic — no retry."""
    proc = _make_proc(1, b'{"status": 1}', b"boom")

    with (
        patch("asyncio.create_subprocess_exec", return_value=proc) as mock_exec,
        pytest.raises(CLIError),
    ):
        await run(["org", "list"])

    assert mock_exec.call_count == 1


async def test_run_does_not_retry_on_cli_not_found():
    """CLINotFoundError — no retry."""
    with (
        patch(
            "asyncio.create_subprocess_exec",
            side_effect=FileNotFoundError("sf not found"),
        ) as mock_exec,
        pytest.raises(CLINotFoundError),
    ):
        await run(["org", "list"])

    assert mock_exec.call_count == 1


# ---------------------------------------------------------------------------
# run() — JSON parsing
# ---------------------------------------------------------------------------


async def test_run_parses_json_response():
    """run() must return the decoded JSON dict from stdout."""
    payload = {
        "status": 0,
        "result": {"key": "value", "count": 42},
        "warnings": [],
    }
    proc = _make_proc(0, json.dumps(payload).encode())

    with patch("asyncio.create_subprocess_exec", return_value=proc):
        result = await run(["some", "command"])

    assert result == payload
    assert result["result"]["count"] == 42


# ---------------------------------------------------------------------------
# run_sync()
# ---------------------------------------------------------------------------


def test_run_sync_returns_same_as_async():
    """run_sync() must return the same value as the underlying async run()."""
    payload = {"status": 0, "result": {"orgs": []}}
    proc = _make_proc(0, json.dumps(payload).encode())

    with patch("asyncio.create_subprocess_exec", return_value=proc):
        result = run_sync(["org", "list"])

    assert result == payload
