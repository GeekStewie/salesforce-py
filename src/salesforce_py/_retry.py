"""Shared retry defaults and helpers for salesforce-py.

All sync HTTP callouts, async HTTP callouts, and ``sf`` CLI subprocess runs
share the same retry shape: retry **once** after a short delay when the
failure looks transient (connection/timeout errors, 429s, 5xx responses,
and selected 4xx rate-limit variants such as 420). Everything else — auth
failures, client-side validation errors, non-retryable CLI failures — is
raised on the first attempt.

Values here are the single source of truth so behaviour stays consistent
across :mod:`salesforce_py.sf`, :mod:`salesforce_py.connect`,
:mod:`salesforce_py.data360`, and :mod:`salesforce_py.models`.

Built on :mod:`tenacity` (``AsyncRetrying`` / ``Retrying`` with
``wait_fixed`` + ``stop_after_attempt`` + ``retry_if_exception``).
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from collections.abc import Awaitable, Callable

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_fixed,
)

from salesforce_py.exceptions import AuthError, CLIError, CLINotFoundError

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared defaults
# ---------------------------------------------------------------------------

#: Default HTTP / subprocess timeout applied when the caller does not override.
DEFAULT_TIMEOUT: float = 120.0

#: Delay (seconds) before the single retry of an HTTP request.
HTTP_RETRY_DELAY: float = 20.0

#: Delay (seconds) before the single retry of a ``sf`` CLI subprocess run.
CLI_RETRY_DELAY: float = 10.0

#: Total attempts (first try + one retry).
MAX_ATTEMPTS: int = 2

# HTTP statuses that are always considered transient and worth one more try.
# 420 is Salesforce's "Enhance Your Calm" throttle signal; 429 is the standard
# rate-limit; 5xx responses typically indicate server-side load problems.
RETRYABLE_STATUSES: frozenset[int] = frozenset(
    {
        408,  # Request Timeout
        420,  # Enhance Your Calm (Salesforce)
        425,  # Too Early
        429,  # Too Many Requests
        500,
        502,
        503,
        504,
    }
)

# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def is_retryable_http_exception(exc: BaseException) -> bool:
    """Return True when an exception from an httpx call should be retried.

    Retries on transport-level failures (timeouts, connection errors) and
    on ``httpx.HTTPStatusError`` carrying a status in :data:`RETRYABLE_STATUSES`.
    Does NOT retry on :class:`~salesforce_py.exceptions.AuthError` (401 is
    not transient) or 4xx responses outside the allow-list.
    """
    if isinstance(exc, AuthError):
        return False
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUSES
    return isinstance(
        exc,
        (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
            httpx.ReadError,
            httpx.WriteError,
            httpx.PoolTimeout,
        ),
    )


def is_retryable_status(status_code: int) -> bool:
    """Return True when an HTTP status is transient and worth retrying."""
    return status_code in RETRYABLE_STATUSES


def is_retryable_cli_exception(exc: BaseException) -> bool:
    """Return True when a subprocess-level failure should be retried.

    Retries on timeouts. Does NOT retry on ``CLINotFoundError`` (missing
    binary is not transient) or generic ``CLIError`` (command-level failures
    are usually deterministic and retrying risks corrupting state).
    """
    if isinstance(exc, (CLINotFoundError, CLIError)):
        return False
    return isinstance(exc, (subprocess.TimeoutExpired, asyncio.TimeoutError))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _before_sleep(retry_state: RetryCallState) -> None:
    """Log a warning before tenacity sleeps between attempts."""
    outcome = retry_state.outcome
    if outcome is None:
        return
    exc = outcome.exception()
    reason = exc.__class__.__name__ if exc else "transient response"
    sleep = retry_state.next_action.sleep if retry_state.next_action else 0.0
    _log.warning(
        "Transient failure on attempt %d (%s); retrying in %.0fs.",
        retry_state.attempt_number,
        reason,
        sleep,
    )


class _TransientResponse(Exception):
    """Internal marker used to signal a retryable response inside tenacity.

    We raise this instead of an ``httpx.HTTPStatusError`` so the original
    response is preserved and handed back to the caller once retries are
    exhausted — letting the per-client ``_handle`` layer produce the right
    public exception (``AuthError`` vs ``SalesforcePyError``).
    """

    def __init__(self, response: httpx.Response) -> None:
        self.response = response


def _should_retry_http(exc: BaseException) -> bool:
    return is_retryable_http_exception(exc) or isinstance(exc, _TransientResponse)


# ---------------------------------------------------------------------------
# Execution helpers
# ---------------------------------------------------------------------------


async def retry_async_http_call(
    func: Callable[[], Awaitable[httpx.Response]],
) -> httpx.Response:
    """Run an async httpx call with the shared retry policy.

    Retries once after :data:`HTTP_RETRY_DELAY` seconds when either the call
    raises a transient error (see :func:`is_retryable_http_exception`) or
    the response carries a transient status in :data:`RETRYABLE_STATUSES`.
    After the retry budget is exhausted, returns the final response so the
    caller's response-handling layer can surface the proper public
    exception.
    """

    async def _call() -> httpx.Response:
        response = await func()
        if is_retryable_status(response.status_code):
            raise _TransientResponse(response)
        return response

    try:
        retryer = AsyncRetrying(
            stop=stop_after_attempt(MAX_ATTEMPTS),
            wait=wait_fixed(HTTP_RETRY_DELAY),
            retry=retry_if_exception(_should_retry_http),
            reraise=True,
            before_sleep=_before_sleep,
        )
        return await retryer(_call)
    except _TransientResponse as marker:
        # Retry budget exhausted while the server kept returning a transient
        # status. Return the last response so the caller's _handle() layer
        # surfaces the proper SalesforcePyError with the body attached.
        return marker.response


def retry_sync_cli[T](func: Callable[[], T]) -> T:
    """Invoke *func* with the shared sync-CLI retry policy.

    One retry after :data:`CLI_RETRY_DELAY` seconds when the call raises a
    transient error classified by :func:`is_retryable_cli_exception`.
    """
    retryer = Retrying(
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_fixed(CLI_RETRY_DELAY),
        retry=retry_if_exception(is_retryable_cli_exception),
        reraise=True,
        before_sleep=_before_sleep,
    )
    return retryer(func)


async def retry_async_cli[T](func: Callable[[], Awaitable[T]]) -> T:
    """Async variant of :func:`retry_sync_cli` for the async subprocess runner."""
    retryer = AsyncRetrying(
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_fixed(CLI_RETRY_DELAY),
        retry=retry_if_exception(is_retryable_cli_exception),
        reraise=True,
        before_sleep=_before_sleep,
    )
    return await retryer(func)
