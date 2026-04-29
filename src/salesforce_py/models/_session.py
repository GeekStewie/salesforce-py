"""Managed async httpx session for the Salesforce Models REST API."""

from __future__ import annotations

from typing import Any

import httpx

from salesforce_py._retry import DEFAULT_TIMEOUT

_DEFAULT_BASE_URL = "https://api.salesforce.com/einstein/platform/v1/"
_DEFAULT_APP_CONTEXT = "EinsteinGPT"
_DEFAULT_CLIENT_FEATURE_ID = "ai-platform-models-connected-app"


class ModelsSession:
    """Thin async httpx wrapper bound to the Einstein Models REST API.

    The Models API is fronted by ``https://api.salesforce.com/einstein/platform/v1/``
    — a single regional endpoint, not the org instance URL. Every request
    must carry the ``x-sfdc-app-context`` and ``x-client-feature-id``
    headers; we set those once on the underlying client.

    Args:
        access_token: Bearer token minted from
            ``{my_domain}/services/oauth2/token`` with the
            ``sfap_api einstein_gpt_api api`` scope.
        base_url: Override the API host. Defaults to
            ``https://api.salesforce.com/einstein/platform/v1/``.
            Use the ``api_instance_url`` returned by the token endpoint when
            you need a geo-specific host.
        app_context: Value for the ``x-sfdc-app-context`` header.
        client_feature_id: Value for the ``x-client-feature-id`` header.
        timeout: Default request timeout in seconds.
        http2: Negotiate HTTP/2 when the server supports it (falls back to
            HTTP/1.1). Defaults to ``True``; requires the ``h2`` package
            (pulled in by the ``models`` extra).
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = _DEFAULT_BASE_URL,
        app_context: str = _DEFAULT_APP_CONTEXT,
        client_feature_id: str = _DEFAULT_CLIENT_FEATURE_ID,
        timeout: float = DEFAULT_TIMEOUT,
        http2: bool = True,
    ) -> None:
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self._access_token = access_token
        self._base_url = base_url
        self._app_context = app_context
        self._client_feature_id = client_feature_id
        self._timeout = timeout
        self._http2 = http2
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> ModelsSession:
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
                base_url=self._base_url,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-sfdc-app-context": self._app_context,
                    "x-client-feature-id": self._client_feature_id,
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
                "ModelsSession is not open. Use 'async with session:' or call open()."
            )
        return self._client

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client_or_raise().post(path, **kwargs)
