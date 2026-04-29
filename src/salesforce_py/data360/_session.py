"""Managed async httpx session for the Data 360 Connect REST API."""

from __future__ import annotations

import httpx

from salesforce_py._defaults import DEFAULT_API_VERSION as _DEFAULT_API_VERSION


class Data360Session:
    """Thin async httpx wrapper bound to one Data 360 tenant's credentials.

    Handles base-URL construction (``/services/data/vXX.X/ssot/``),
    the Authorization header, and content-type defaults.

    Args:
        instance_url: Data 360 instance URL, e.g.
            ``"https://datacloud-abc.my.salesforce.com"``.
        access_token: OAuth bearer token for the tenant.
        api_version: Salesforce API version string, e.g. ``"66.0"``.
        timeout: Default request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to
            HTTP/1.1). Defaults to ``True``; requires the ``h2`` package
            (pulled in by the ``data360`` extra).
    """

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        api_version: str = _DEFAULT_API_VERSION,
        timeout: float = 30.0,
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

    async def __aenter__(self) -> Data360Session:
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
                base_url=f"{self._instance_url}/services/data/v{self._api_version}/ssot/",
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
                "Data360Session is not open. Use 'async with session:' or call open()."
            )
        return self._client

    async def get(self, path: str, **kwargs: object) -> httpx.Response:
        return await self._client_or_raise().get(path, **kwargs)

    async def post(self, path: str, **kwargs: object) -> httpx.Response:
        return await self._client_or_raise().post(path, **kwargs)

    async def patch(self, path: str, **kwargs: object) -> httpx.Response:
        return await self._client_or_raise().patch(path, **kwargs)

    async def put(self, path: str, **kwargs: object) -> httpx.Response:
        return await self._client_or_raise().put(path, **kwargs)

    async def delete(self, path: str, **kwargs: object) -> httpx.Response:
        return await self._client_or_raise().delete(path, **kwargs)
