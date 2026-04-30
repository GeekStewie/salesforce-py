"""Base class for all Connect API operation wrappers."""

from __future__ import annotations

import contextlib
import logging
from typing import Any

import httpx

from salesforce_py._retry import retry_async_http_call
from salesforce_py.connect._session import ConnectSession
from salesforce_py.exceptions import AuthError, SalesforcePyError
from salesforce_py.utils.salesforce_id import convert_to_18_char

_log = logging.getLogger(__name__)


class ConnectBaseOperations:
    """Shared HTTP dispatch layer for all Connect API operation classes.

    Subclasses receive a :class:`ConnectSession` and call the protected
    ``_get`` / ``_post`` / ``_patch`` / ``_delete`` helpers, which handle
    response validation and error surfacing uniformly.

    Args:
        session: Open :class:`ConnectSession` instance.
    """

    def __init__(
        self,
        session: ConnectSession,
        data_session: ConnectSession | None = None,
    ) -> None:
        self._session = session
        # Optional secondary session bound to ``/services/data/vXX.X/`` (no
        # ``connect/`` prefix). Chatter-root endpoints (``/chatter/...``) live
        # here, not under ``/connect/chatter/...``. When provided, calls whose
        # path starts with ``chatter/`` are routed to this session.
        self._data_session = data_session

    def _route(self, path: str) -> ConnectSession:
        """Return the session appropriate for ``path``.

        Org-scope Chatter endpoints (``chatter/...``) must be addressed under
        ``/services/data/vXX.X/chatter/...``, NOT ``/services/data/vXX.X/connect/chatter/...``.
        When a ``data_session`` has been provided and the path starts with
        ``chatter/``, we route there; otherwise we use the default Connect
        session (connect-prefixed).
        """
        if self._data_session is not None and path.startswith("chatter/"):
            return self._data_session
        return self._session

    # ------------------------------------------------------------------
    # ID normalisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_18(sf_id: str) -> str:
        """Return the 18-character form of a Salesforce ID.

        Passes through any value that is not exactly 15 characters (e.g. the
        ``"me"`` alias, fully-qualified asset names) unchanged.

        Args:
            sf_id: A 15- or 18-character Salesforce ID, or a non-ID string.

        Returns:
            18-character ID, or the original value if it is not 15 characters.
        """
        if len(sf_id) == 15:
            return convert_to_18_char(sf_id)
        return sf_id

    @staticmethod
    def _ensure_18_list(sf_ids: list[str]) -> list[str]:
        """Return a list with every 15-character ID converted to 18 characters.

        Args:
            sf_ids: List of Salesforce IDs.

        Returns:
            New list with all IDs normalised to 18 characters.
        """
        return [ConnectBaseOperations._ensure_18(i) for i in sf_ids]

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, **kwargs: object) -> dict[str, Any]:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.get(path, **kwargs))
        return self._handle(response)

    async def _get_bytes(self, path: str, **kwargs: object) -> bytes:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.get(path, **kwargs))
        self._handle_status(response)
        return response.content

    async def _post(self, path: str, **kwargs: object) -> dict[str, Any]:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.post(path, **kwargs))
        return self._handle(response)

    async def _patch(self, path: str, **kwargs: object) -> dict[str, Any]:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.patch(path, **kwargs))
        return self._handle(response)

    async def _put(self, path: str, **kwargs: object) -> dict[str, Any]:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.put(path, **kwargs))
        return self._handle(response)

    async def _delete(self, path: str, **kwargs: object) -> dict[str, Any]:
        sess = self._route(path)
        response = await retry_async_http_call(lambda: sess.delete(path, **kwargs))
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
            SalesforcePyError: On any other 4xx/5xx status.
        """
        if response.status_code == 401:
            raise AuthError(
                f"Connect API returned 401 Unauthorized. "
                f"Check that the access token is valid. URL: {response.url}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = ""
            with contextlib.suppress(Exception):
                body = response.text[:500]
            raise SalesforcePyError(f"Connect API error {response.status_code}: {body}") from exc

    @staticmethod
    def _handle(response: httpx.Response) -> dict[str, Any]:
        """Validate an httpx response and return its JSON body.

        Args:
            response: Raw httpx response.

        Returns:
            Parsed JSON dict, or ``{}`` for 204 No Content.

        Raises:
            AuthError: On 401 Unauthorized.
            SalesforcePyError: On any other 4xx/5xx status.
        """
        if response.status_code == 204:
            return {}

        ConnectBaseOperations._handle_status(response)

        if not response.content:
            return {}

        try:
            return response.json()
        except Exception as exc:
            raise SalesforcePyError(
                f"Connect API returned non-JSON response: {response.text[:500]}"
            ) from exc
