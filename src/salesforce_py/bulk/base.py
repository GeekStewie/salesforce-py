"""Base class for all Bulk API 2.0 operation wrappers."""

from __future__ import annotations

import contextlib
from typing import Any

import httpx

from salesforce_py._retry import retry_async_http_call
from salesforce_py.bulk._session import BulkSession
from salesforce_py.exceptions import AuthError, SalesforcePyError


def _drop_none(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return *params* without any keys whose value is ``None``."""
    if not params:
        return params
    return {k: v for k, v in params.items() if v is not None}


class BulkBaseOperations:
    """Shared HTTP dispatch layer for all Bulk API 2.0 operation classes.

    Subclasses receive a :class:`BulkSession` and use the protected
    ``_get`` / ``_post`` / ``_patch`` / ``_delete`` helpers for JSON
    endpoints, plus ``_put_csv`` and ``_get_csv`` for the CSV-typed
    upload/download edges.

    Args:
        session: Open :class:`BulkSession` instance.
    """

    def __init__(self, session: BulkSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # JSON helpers
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
        merged_headers = {"Content-Type": "application/json", **(headers or {})}
        kwargs: dict[str, Any] = {
            "params": _drop_none(params),
            "headers": merged_headers,
        }
        if json is not None:
            kwargs["json"] = json
        response = await retry_async_http_call(lambda: self._session.post(path, **kwargs))
        return self._handle(response)

    async def _patch(
        self,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        merged_headers = {"Content-Type": "application/json", **(headers or {})}
        kwargs: dict[str, Any] = {
            "params": _drop_none(params),
            "headers": merged_headers,
        }
        if json is not None:
            kwargs["json"] = json
        response = await retry_async_http_call(lambda: self._session.patch(path, **kwargs))
        return self._handle(response)

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = await retry_async_http_call(
            lambda: self._session.delete(path, params=_drop_none(params), headers=headers)
        )
        return self._handle(response)

    # ------------------------------------------------------------------
    # CSV helpers (ingest upload + query results)
    # ------------------------------------------------------------------

    async def _put_csv(
        self,
        path: str,
        *,
        data: bytes,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        merged_headers = {
            "Content-Type": "text/csv",
            "Accept": "application/json",
            **(headers or {}),
        }
        response = await retry_async_http_call(
            lambda: self._session.put(path, content=data, headers=merged_headers)
        )
        self._handle_status(response)
        return response

    async def _get_csv(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Fetch a CSV payload, returning the raw response so callers can
        read both the body and the ``Sforce-Locator`` / ``Sforce-NumberOfRecords``
        pagination headers.
        """
        merged_headers = {"Accept": "text/csv", **(headers or {})}
        response = await retry_async_http_call(
            lambda: self._session.get(path, params=_drop_none(params), headers=merged_headers)
        )
        self._handle_status(response)
        return response

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_status(response: httpx.Response) -> None:
        if response.status_code == 401:
            raise AuthError(
                f"Bulk API returned 401 Unauthorized. "
                f"Check that the access token is valid. URL: {response.url}"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = ""
            with contextlib.suppress(Exception):
                body = response.text[:500]
            raise SalesforcePyError(f"Bulk API error {response.status_code}: {body}") from exc

    @staticmethod
    def _handle(response: httpx.Response) -> dict[str, Any]:
        if response.status_code == 204:
            return {}
        BulkBaseOperations._handle_status(response)
        if not response.content:
            return {}
        try:
            return response.json()
        except Exception as exc:
            raise SalesforcePyError(
                f"Bulk API returned non-JSON response: {response.text[:500]}"
            ) from exc
