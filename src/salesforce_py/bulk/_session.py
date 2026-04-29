"""Managed async httpx session for the Salesforce Bulk API 2.0."""

from __future__ import annotations

from typing import Any

import httpx

from salesforce_py._defaults import DEFAULT_API_VERSION as _DEFAULT_API_VERSION
from salesforce_py._retry import DEFAULT_TIMEOUT


class BulkSession:
    """Thin async httpx wrapper bound to one org's Bulk API 2.0 surface.

    Builds ``/services/data/vXX.X/jobs/`` as the base URL so both
    ``ingest/`` and ``query/`` subtrees are addressable with relative paths.

    Args:
        instance_url: My Domain URL, e.g. ``"https://myorg.my.salesforce.com"``.
        access_token: OAuth bearer token for the org.
        api_version: Salesforce API version string, e.g. ``"66.0"``.
        timeout: Default request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to
            HTTP/1.1). Defaults to ``True``; requires the ``h2`` package
            (pulled in by the ``bulk`` extra).
    """

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> None:
        self._instance_url = instance_url.rstrip("/")
        self._access_token = access_token
        self._api_version = api_version
        self._timeout = timeout
        self._http2 = http2
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> BulkSession:
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        """Open the underlying httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=f"{self._instance_url}/services/data/v{self._api_version}/jobs/",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Accept": "application/json",
                },
                timeout=self._timeout,
                http2=self._http2,
            )

    async def close(self) -> None:
        """Close the underlying httpx client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def _client_or_raise(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("BulkSession is not open. Use 'async with session:' or call open().")
        return self._client

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().post(path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().patch(path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().put(path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().delete(path, **kwargs)
