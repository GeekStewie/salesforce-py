"""Core async subprocess runner for the `sf` CLI."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from salesforce_py.exceptions import CLIError, CLINotFoundError


async def run(args: list[str], *, timeout: float | None = 60.0) -> dict[str, Any]:
    """Run an `sf` CLI command asynchronously and return the parsed JSON output.

    Parameters
    ----------
    args:
        Arguments to pass to `sf` (do *not* include `"sf"` itself or `"--json"`).
    timeout:
        Maximum seconds to wait for the process to complete. ``None`` means no
        timeout. Defaults to 60 seconds.

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
        If the process does not complete within *timeout* seconds.
    """
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
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        raise

    stdout = raw_stdout.decode(errors="replace")
    stderr = raw_stderr.decode(errors="replace")

    if proc.returncode != 0:
        raise CLIError(returncode=proc.returncode, stdout=stdout, stderr=stderr)  # type: ignore[arg-type]

    return json.loads(stdout)  # type: ignore[no-any-return]


def run_sync(args: list[str], **kwargs: Any) -> dict[str, Any]:
    """Synchronous wrapper around :func:`run`.

    Accepts the same keyword arguments as :func:`run`.
    """
    return asyncio.run(run(args, **kwargs))
