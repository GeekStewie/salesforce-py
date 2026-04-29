"""Base class for all Models REST API operation wrappers."""

from __future__ import annotations

import contextlib
import logging
from typing import Any

import httpx

from salesforce_py._retry import retry_async_http_call
from salesforce_py.exceptions import AuthError, SalesforcePyError
from salesforce_py.models._session import ModelsSession

_log = logging.getLogger(__name__)


def _drop_none(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return *params* without any keys whose value is ``None``."""
    if not params:
        return params
    return {k: v for k, v in params.items() if v is not None}


class ModelsBaseOperations:
    """Shared HTTP dispatch layer for all Models API operation classes.

    Subclasses receive a :class:`ModelsSession` and call the protected
    ``_get`` / ``_post`` helpers, which handle response validation and
    error surfacing uniformly.

    Args:
        session: Open :class:`ModelsSession` instance.
    """

    def __init__(self, session: ModelsSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = await retry_async_http_call(
            lambda: self._session.get(path, params=_drop_none(params), headers=headers)
        )
        return self._handle(response)

    async def _post(
        self,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"params": _drop_none(params), "headers": headers}
        if json is not None:
            kwargs["json"] = json
        response = await retry_async_http_call(lambda: self._session.post(path, **kwargs))
        return self._handle(response)

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_status(response: httpx.Response) -> None:
        """Raise appropriate exceptions for non-2xx responses.

        Args:
            response: Raw httpx response.

        Raises:
            AuthError: On 401 Unauthorized.
            SalesforcePyError: On any other 4xx/5xx status. Rate-limit
                responses (429) are surfaced with the body intact so callers
                can inspect the provider's error object.
        """
        if response.status_code == 401:
            raise AuthError(
                f"Models API returned 401 Unauthorized. "
                f"Check that the access token is valid and the JWT includes the "
                f"'sfap_api einstein_gpt_api api' scopes. URL: {response.url}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = ""
            with contextlib.suppress(Exception):
                body = response.text[:500]
            raise SalesforcePyError(f"Models API error {response.status_code}: {body}") from exc

    @staticmethod
    def _handle(response: httpx.Response) -> dict[str, Any]:
        """Validate an httpx response and return its JSON body.

        Args:
            response: Raw httpx response.

        Returns:
            Parsed JSON dict, or ``{}`` for 204 No Content / empty bodies.

        Raises:
            AuthError: On 401 Unauthorized.
            SalesforcePyError: On any other 4xx/5xx status or non-JSON 2xx body.
        """
        if response.status_code == 204:
            return {}

        ModelsBaseOperations._handle_status(response)

        if not response.content:
            return {}

        try:
            return response.json()
        except Exception as exc:
            raise SalesforcePyError(
                f"Models API returned non-JSON response: {response.text[:500]}"
            ) from exc
