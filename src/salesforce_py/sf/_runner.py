"""Core async subprocess runner for the `sf` CLI."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from salesforce_py._retry import DEFAULT_TIMEOUT, retry_async_cli
from salesforce_py.exceptions import CLIError, CLINotFoundError


async def _run_once(args: list[str], *, timeout: float | None) -> dict[str, Any]:
    """Execute one ``sf`` invocation and return its parsed JSON output."""
    cmd = ["sf", *args, "--json"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise CLINotFoundError from exc

    try:
        raw_stdout, raw_stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout,
        )
    except TimeoutError:
        proc.kill()
        await proc.communicate()
        raise

    stdout = raw_stdout.decode(errors="replace")
    stderr = raw_stderr.decode(errors="replace")

    returncode = proc.returncode
    if returncode is not None and returncode != 0:
        raise CLIError(returncode=returncode, stdout=stdout, stderr=stderr)

    return json.loads(stdout)  # type: ignore[no-any-return]


async def run(
    args: list[str],
    *,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Run an `sf` CLI command asynchronously and return the parsed JSON output.

    Retries once after ``CLI_RETRY_DELAY`` seconds on a subprocess-level timeout.
    Does **not** retry on :class:`CLINotFoundError` or :class:`CLIError` — those
    are deterministic failures where a retry would not change the outcome.

    Parameters
    ----------
    args:
        Arguments to pass to `sf` (do *not* include `"sf"` itself or `"--json"`).
    timeout:
        Maximum seconds to wait for the process to complete. ``None`` means no
        timeout. Defaults to :data:`salesforce_py._retry.DEFAULT_TIMEOUT`
        (120 seconds).

    Returns
    -------
    dict
        Parsed JSON response from the CLI.

    Raises
    ------
    CLINotFoundError
        If the `sf` binary is not found on PATH.
    CLIError
        If the process exits with a non-zero return code.
    asyncio.TimeoutError
        If the process does not complete within *timeout* seconds on both
        the initial attempt and the retry.
    """

    async def _attempt() -> dict[str, Any]:
        return await _run_once(args, timeout=timeout)

    return await retry_async_cli(_attempt)


def run_sync(args: list[str], **kwargs: Any) -> dict[str, Any]:
    """Synchronous wrapper around :func:`run`.

    Accepts the same keyword arguments as :func:`run`.
    """
    return asyncio.run(run(args, **kwargs))
