"""Managed async httpx session for the Connect API."""

from __future__ import annotations

from typing import Any

import httpx

from salesforce_py._defaults import DEFAULT_API_VERSION as _DEFAULT_API_VERSION
from salesforce_py._retry import DEFAULT_TIMEOUT


class ConnectSession:
    """Thin async httpx wrapper bound to one org's credentials.

    Handles base-URL construction, the Authorization header, and
    content-type defaults.  Intended to be used as an async context
    manager or kept alive for the lifetime of a :class:`ConnectClient`.

    Args:
        instance_url: Org instance URL, e.g. ``"https://myorg.my.salesforce.com"``.
        access_token: OAuth bearer token.
        api_version: Salesforce API version string, e.g. ``"62.0"``.
        timeout: Default request timeout in seconds.
        base_path: Path segment under ``/services/data/vXX.X/`` (e.g. ``"connect"``).
        http2: Negotiate HTTP/2 when the server supports it (falls back to HTTP/1.1).
            Defaults to ``True``; requires the ``h2`` package (pulled in by the
            ``connect`` extra).
    """

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        base_path: str = "connect",
        http2: bool = True,
    ) -> None:
        self._instance_url = instance_url.rstrip("/")
        self._access_token = access_token
        self._api_version = api_version
        self._timeout = timeout
        self._base_path = base_path.strip("/")
        self._http2 = http2
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> ConnectSession:
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
            suffix = f"{self._base_path}/" if self._base_path else ""
            self._client = httpx.AsyncClient(
                base_url=f"{self._instance_url}/services/data/v{self._api_version}/{suffix}",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
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
            raise RuntimeError(
                "ConnectSession is not open. Use 'async with session:' or call open()."
            )
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
